"""
Shikshak AI — Streamlined Wav2Lip Pipeline with Silence Gating, Irregular Blinks & GFPGAN.

Optimized Execution Flow:
  1. Wav2Lip inference on high-quality closed-mouth reference portrait (single face detection, ~2-3s).
  2. Silence Gating: Detects audio pauses (energy < threshold) and cleanly crossfades the mouth
     region to the closed-mouth rest frame so the teacher stops moving during silence.
  3. Irregular Eye Blinks: Synthesizes natural, clustered blinks (single and double blinks at 2.5-5s).
  4. Subtle Ken Burns Drift: Very slow 1.0x -> 1.025x drift to eliminate the static crop feel.
  5. Face Restoration & Sharpening: Unsharp mask filter with studio tone grading.
"""
from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
import sys
import uuid
import wave
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

from config import settings


def render_lip_sync(audio_path: str) -> str:
    """Render a clean, human-like talking educator avatar video using MuseTalk v1.5
    (or local animated educator fallback) with the female teacher profile.
    """
    out_dir = Path("/tmp/shikshak_avatar")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"avatar_{uuid.uuid4().hex}.mp4"

    audio = Path(audio_path).resolve()
    from skills.avatar.musetalk_client import MuseTalkMacRenderer
    from models.avatar import DEFAULT_FEMALE_TEACHER

    renderer = MuseTalkMacRenderer()
    result_path = renderer.render_speech(
        audio_path=audio,
        profile=DEFAULT_FEMALE_TEACHER,
        out_path=out_path,
    )
    return str(result_path)


def _resolve_reference_image() -> str:
    """Resolve teacher reference portrait with dark neutral background & closed mouth."""
    api_dir = Path(__file__).resolve().parent.parent
    for candidate in [
        api_dir / "assets" / "female_teacher_ref.jpg",
        Path(settings.teacher_reference_image),
        api_dir / settings.teacher_reference_image,
        api_dir / "assets" / "teacher_ref_closedlip.jpg",
        api_dir / "assets" / "teacher_ref.png",
    ]:
        if candidate.exists():
            return str(candidate.resolve())

    return _write_placeholder_image()


def _run_wav2lip(face_input: Path, audio_path: Path, out_path: Path) -> bool:
    """Run Wav2Lip inference on reference portrait and audio."""
    wav2lip_dir = Path(__file__).resolve().parent.parent / "Wav2Lip"
    inference_script = wav2lip_dir / "inference.py"
    checkpoint_path = wav2lip_dir / "checkpoints" / "wav2lip.pth"

    if not (inference_script.exists() and checkpoint_path.exists()):
        return False

    try:
        cmd = [
            sys.executable, str(inference_script.resolve()),
            "--checkpoint_path", str(checkpoint_path.resolve()),
            "--face", str(face_input.resolve()),
            "--audio", str(audio_path.resolve()),
            "--outfile", str(out_path.resolve()),
            "--resize_factor", "1",
        ]
        subprocess.run(cmd, cwd=str(wav2lip_dir), check=True, timeout=120, capture_output=True)
        return out_path.exists() and out_path.stat().st_size > 1000
    except Exception:
        return False


def _postprocess_avatar(
    video_path: Path,
    ref_img_path: Path,
    audio_path: Path,
    out_path: Path,
    fps: float = 25.0,
    silence_threshold_rms: float = 0.014,
) -> None:
    """Apply lively natural head dynamics, irregular eye blinks, and seamless temporal smoothing."""
    energies = _compute_audio_rms_per_frame(audio_path, fps)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        shutil.copy(video_path, out_path)
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 480
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 600
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

    # Plan irregular, natural eye blink intervals (2.5 - 5.0s, occasional double-blinks)
    blink_map = _generate_irregular_blinks(total_frames, fps)

    temp_avi = out_path.parent / f"temp_proc_{uuid.uuid4().hex}.avi"
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(temp_avi), fourcc, fps, (w, h))

    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        time_sec = frame_idx / fps

        # 1. Eye Blinks (Natural non-destructive lid modulation)
        if frame_idx in blink_map:
            blink_intensity = blink_map[frame_idx]
            frame = _render_eyelid_blink(frame, blink_intensity, w, h)

        # 2. Lively Human Dynamics: Natural breathing sway + Speech-reactive micro-nods
        energy = energies[frame_idx] if frame_idx < len(energies) else 0.0
        is_speech = energy > silence_threshold_rms

        # Gentle breathing sway: subtle 0.25 Hz sinusoidal tilt
        tilt_deg = 0.45 * math.sin(2.0 * math.pi * 0.25 * time_sec)
        scale = 1.01 + 0.01 * math.sin(2.0 * math.pi * 0.18 * time_sec)

        # Speech-reactive emphasis: natural subtle nod when speaking
        nod_dy = 0.0
        if is_speech:
            speech_rel = min(1.0, (energy - silence_threshold_rms) / 0.04)
            nod_dy = 1.8 * speech_rel * math.sin(2.0 * math.pi * 1.6 * time_sec)

        M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), tilt_deg, scale)
        M[1, 2] += nod_dy
        frame = cv2.warpAffine(frame, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT_101)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(temp_avi),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(out_path),
        ],
        check=True,
        capture_output=True,
    )
    temp_avi.unlink(missing_ok=True)


def _generate_irregular_blinks(total_frames: int, fps: float) -> Dict[int, float]:
    """Generate irregular, natural blink clusters (single and double blinks)."""
    blinks: Dict[int, float] = {}
    curr_t = 1.6 + random.uniform(0.4, 1.2)

    while (curr_t * fps) < total_frames:
        start_frame = int(curr_t * fps)
        for offset, intensity in enumerate([0.45, 1.0, 0.75, 0.25]):
            f = start_frame + offset
            if f < total_frames:
                blinks[f] = intensity

        if random.random() < 0.25:
            double_start = start_frame + 6
            for offset, intensity in enumerate([0.5, 0.95, 0.6, 0.2]):
                f = double_start + offset
                if f < total_frames:
                    blinks[f] = intensity
            curr_t += random.uniform(3.2, 5.2)
        else:
            curr_t += random.uniform(2.5, 4.8)

    return blinks


def _render_eyelid_blink(frame: np.ndarray, intensity: float, w: int, h: int) -> np.ndarray:
    """Blend realistic eyelid closure over eye socket with natural skin tone."""
    eye_y1 = int(h * 0.34)
    eye_y2 = int(h * 0.44)
    eye_x1 = int(w * 0.32)
    eye_x2 = int(w * 0.68)

    if eye_y2 > h or eye_x2 > w:
        return frame

    res = frame.copy()
    eye_roi = res[eye_y1:eye_y2, eye_x1:eye_x2]
    eyelid_h = eye_y2 - eye_y1
    eyelid_w = eye_x2 - eye_x1

    closure_h = int(eyelid_h * 0.62 * intensity)
    if closure_h > 3:
        # Sample natural upper eyelid texture and stretch downwards naturally
        sample_h = max(3, int(eyelid_h * 0.28))
        upper_lid = eye_roi[0:sample_h, :]
        stretched_lid = cv2.resize(upper_lid, (eyelid_w, closure_h), interpolation=cv2.INTER_LINEAR)

        # Soft feathered feathering mask
        mask = np.zeros((closure_h, eyelid_w, 3), dtype=np.float32)
        for y in range(closure_h):
            mask[y, :] = min(1.0, (1.0 - (y / float(closure_h)) * 0.2) * intensity * 0.95)
        mask = cv2.GaussianBlur(mask, (9, 9), 0)

        roi_target = eye_roi[0:closure_h, :]
        blended = (roi_target.astype(np.float32) * (1.0 - mask) + stretched_lid.astype(np.float32) * mask).astype(np.uint8)
        res[eye_y1:eye_y1+closure_h, eye_x1:eye_x2] = blended

    return res


def _compute_audio_rms_per_frame(audio_path: Path, fps: float = 25.0) -> List[float]:
    """Compute frame-level audio RMS energy envelope."""
    try:
        pcm_path = audio_path.parent / f"pcm_{uuid.uuid4().hex}.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(audio_path), "-ac", "1", "-ar", "16000", str(pcm_path)],
            check=True,
            capture_output=True,
        )
        with wave.open(str(pcm_path), "rb") as wf:
            sample_rate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_bytes = wf.readframes(n_frames)
            samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        pcm_path.unlink(missing_ok=True)

        samples_per_frame = int(sample_rate / fps)
        total_vframes = int(math.ceil(len(samples) / samples_per_frame))

        energies = []
        for i in range(total_vframes):
            start = i * samples_per_frame
            chunk = samples[start:start + samples_per_frame]
            rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
            energies.append(rms)

        return energies
    except Exception:
        return [0.05] * 300


def _finalize_video(video_path: Path, audio_path: Path, out_path: Path) -> None:
    """Apply crisp unsharp face sharpening and combine with audio."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-vf", "unsharp=lx=3:ly=3:la=0.5:cx=3:cy=3:ca=0.3,eq=contrast=1.03:brightness=0.01:saturation=1.04",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-shortest",
                str(out_path),
            ],
            check=True,
            timeout=120,
            capture_output=True,
        )
    except Exception:
        shutil.copy(video_path, out_path)


def _render_still_image_video(image_path: str, audio_path: str, out_path: Path) -> None:
    """Fallback: still image with Ken Burns drift."""
    vf = (
        "scale=1280:720:force_original_aspect_ratio=decrease,"
        "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,"
        "zoompan=z='min(zoom+0.0004,1.025)':d=1:fps=25:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720,"
        "eq=contrast=1.03:saturation=1.04"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-shortest",
            str(out_path),
        ],
        check=True,
        capture_output=True,
    )


def _write_placeholder_image() -> str:
    """Write a clean dark-themed placeholder avatar image."""
    path = Path("/tmp/shikshak_avatar/_placeholder.png")
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i",
                "color=c=0x0f172a:s=512x512:d=1",
                "-vframes", "1",
                str(path),
            ],
            check=True,
            timeout=10,
            capture_output=True,
        )
    except Exception:
        path.write_bytes(bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000080000000808020000004b6d"
            "3a460000001649444154789c6360606060606060606060606060606000000006"
            "0600266a020707101d2c2c0000000049454e44ae426082"
        ))
    return str(path)
