"""
Shikshak AI — Native Wav2Lip Neural Lip Synchronization Renderer.

Produces guaranteed, high-fidelity neural lip-synchronized educator videos
directly on Apple Silicon (MPS) or CPU:
  1. Mel-spectrogram chunk extraction (80 mels at 16kHz via librosa)
  2. Neural mouth viseme synthesis via Wav2Lip GAN generator
  3. Seamless feathered boundary blending preserving facial identity and sharp hair/eyes
  4. Streamed direct to FFmpeg for high-speed H.264 MP4 export.
"""
from __future__ import annotations

import logging
import math
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import torch

from models.avatar import AvatarProfile, DEFAULT_FEMALE_TEACHER
from skills.avatar.wav2lip.audio import get_mel_chunks_for_frames
from skills.avatar.wav2lip.model import Wav2Lip
from skills.video_generation.media import require_playable_video

logger = logging.getLogger(__name__)

DEFAULT_CHECKPOINT = Path(__file__).resolve().parent.parent.parent / "models" / "wav2lip" / "wav2lip_gan.pth"


class Wav2LipRenderer:
    """Neural lip-sync renderer powered by pre-trained Wav2Lip GAN."""

    _model_instance: Optional[Wav2Lip] = None
    _device_cached: Optional[str] = None

    def __init__(
        self,
        checkpoint_path: Optional[Path] = None,
        device: Optional[str] = None,
    ):
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else DEFAULT_CHECKPOINT
        if device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = device

    def ensure_model(self) -> Wav2Lip:
        """Load and cache Wav2Lip generator model."""
        if Wav2LipRenderer._model_instance is not None and Wav2LipRenderer._device_cached == self.device:
            return Wav2LipRenderer._model_instance

        if not self.checkpoint_path.exists():
            logger.info("[Wav2Lip] Checkpoint not found at %s. Downloading from Hugging Face...", self.checkpoint_path)
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                from huggingface_hub import hf_hub_download
                downloaded = hf_hub_download(
                    repo_id="Nekochu/Wav2Lip",
                    filename="wav2lip_gan.pth",
                    local_dir=str(self.checkpoint_path.parent),
                )
                self.checkpoint_path = Path(downloaded)
            except Exception as e:
                logger.error("[Wav2Lip] Auto-download failed: %s", e)
                raise FileNotFoundError(f"Wav2Lip checkpoint missing at {self.checkpoint_path}") from e

        logger.info("[Wav2Lip] Loading weights from %s on device=%s", self.checkpoint_path, self.device)
        model = Wav2Lip().to(self.device)
        checkpoint = torch.load(str(self.checkpoint_path), map_location=self.device)
        sd = checkpoint.get("state_dict", checkpoint)
        new_sd = {k.replace("module.", ""): v for k, v in sd.items()}
        model.load_state_dict(new_sd, strict=False)
        model.eval()

        Wav2LipRenderer._model_instance = model
        Wav2LipRenderer._device_cached = self.device
        return model

    def render_speech(
        self,
        audio_path: Path,
        profile: AvatarProfile = DEFAULT_FEMALE_TEACHER,
        out_path: Optional[Path] = None,
        fps: int = 25,
        canvas_size: int = 512,
        batch_size: int = 16,
    ) -> Path:
        """Render synchronized neural lip-talking educator video."""
        portrait_path = profile.get_absolute_portrait_path()
        if not portrait_path.exists():
            alt = Path(__file__).resolve().parent.parent.parent / "assets" / "female_teacher_ref.jpg"
            if alt.exists():
                portrait_path = alt
            else:
                raise FileNotFoundError(f"Educator portrait not found: {portrait_path}")

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if out_path is None:
            target_path = Path("/tmp/shikshak_avatar") / f"wav2lip_{uuid.uuid4().hex}.mp4"
        else:
            target_path = Path(out_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Load and prepare educator portrait
        base_bgr = cv2.imread(str(portrait_path))
        if base_bgr is None:
            raise ValueError(f"Failed to read image: {portrait_path}")
        base_bgr = cv2.resize(base_bgr, (canvas_size, canvas_size), interpolation=cv2.INTER_AREA)

        # Ground truth face bounding box on calibrated 512x512 portrait
        # Teacher face box: y: 95..245, x: 181..331 (height 150, width 150)
        # Positions eyes at row 37, nose at row 54, and mouth at row 70 (lower half)
        fy1, fy2 = 95, 245
        fx1, fx2 = 181, 331
        face_w = fx2 - fx1
        face_h = fy2 - fy1

        face_crop = base_bgr[fy1:fy2, fx1:fx2]
        face_resized = cv2.resize(face_crop, (96, 96))
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

        # Mask lower half for Wav2Lip condition (rows 48-96, covering nose base to chin)
        masked_face = face_rgb.copy()
        masked_face[48:, :] = 0.0

        # 6-channel static face tensor (6, 96, 96)
        face_tensor_np = np.concatenate([masked_face, face_rgb], axis=2).transpose(2, 0, 1)
        base_face_tensor = torch.FloatTensor(face_tensor_np)

        # 2. Extract audio mel-spectrogram chunks
        mel_chunks, total_frames = get_mel_chunks_for_frames(str(audio_path), fps=fps)
        if not mel_chunks:
            raise ValueError(f"No audio data extracted from: {audio_path}")

        # 3. Initialize model
        model = self.ensure_model()

        # 4. Setup FFmpeg pipe
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{canvas_size}x{canvas_size}",
            "-pix_fmt", "bgr24",
            "-r", str(fps),
            "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(target_path),
        ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        # Build feather mask for seamless mouth integration
        # Only blend y > 58% of the face box (mouth & chin, below nose tip at ~y=180)
        blend_mask = np.zeros((face_h, face_w), dtype=np.float32)
        split_y = int(face_h * 0.58)
        blend_mask[split_y:, :] = 1.0
        # Feather border boundaries so there are no square seams on cheeks or chin
        blend_mask[:, :12] = 0.0
        blend_mask[:, -12:] = 0.0
        blend_mask[-8:, :] = 0.0
        blend_mask = cv2.GaussianBlur(blend_mask, (21, 21), 0)
        blend_mask_3c = np.repeat(blend_mask[:, :, np.newaxis], 3, axis=2)

        # Pre-compute natural eye blinks (every ~3.8s for 2 frames)
        blink_frames = set()
        blink_interval = int(fps * 3.8)
        for bf in range(blink_interval, total_frames, blink_interval):
            blink_frames.add(bf)
            blink_frames.add(bf + 1)

        eye_l_center = (230, 153)
        eye_r_center = (282, 153)
        eye_rx, eye_ry = 12, 7
        cheek_skin = base_bgr[170:180, 205:215].mean(axis=(0, 1)).astype(np.uint8)

        try:
            # 5. Process in batches for high throughput
            for b_start in range(0, total_frames, batch_size):
                b_end = min(total_frames, b_start + batch_size)
                cur_batch_size = b_end - b_start

                mels_batch = torch.FloatTensor(np.array([
                    mel_chunks[idx] for idx in range(b_start, b_end)
                ])).unsqueeze(1).to(self.device)  # (B, 1, 80, 16)

                faces_batch = base_face_tensor.unsqueeze(0).repeat(cur_batch_size, 1, 1, 1).to(self.device)

                with torch.no_grad():
                    preds = model(mels_batch, faces_batch)

                preds_np = preds.permute(0, 2, 3, 1).cpu().numpy()  # (B, 96, 96, 3) in RGB

                for b_idx in range(cur_batch_size):
                    frame_idx = b_start + b_idx
                    frame = base_bgr.copy()

                    pred_rgb = (preds_np[b_idx] * 255).clip(0, 255).astype(np.uint8)
                    pred_bgr = cv2.cvtColor(pred_rgb, cv2.COLOR_RGB2BGR)

                    # Upscale neural face patch to original crop dimensions
                    pred_upscaled = cv2.resize(pred_bgr, (face_w, face_h), interpolation=cv2.INTER_LANCZOS4)

                    # Seamless alpha blend into base portrait
                    original_face = frame[fy1:fy2, fx1:fx2].astype(np.float32)
                    morphed_face = (
                        pred_upscaled.astype(np.float32) * blend_mask_3c
                        + original_face * (1.0 - blend_mask_3c)
                    ).clip(0, 255).astype(np.uint8)

                    frame[fy1:fy2, fx1:fx2] = morphed_face

                    # Natural eye blink overlay
                    if frame_idx in blink_frames:
                        for eye_c in (eye_l_center, eye_r_center):
                            cv2.ellipse(
                                frame,
                                (eye_c[0], eye_c[1]),
                                (eye_rx, eye_ry),
                                0, 0, 360,
                                (int(cheek_skin[0]), int(cheek_skin[1]), int(cheek_skin[2])),
                                -1,
                                cv2.LINE_AA,
                            )
                            cv2.line(
                                frame,
                                (eye_c[0] - eye_rx + 1, eye_c[1]),
                                (eye_c[0] + eye_rx - 1, eye_c[1]),
                                (75, 55, 50),
                                1,
                                cv2.LINE_AA,
                            )

                    # Subtle breathing micro-motion
                    t_sec = frame_idx / float(fps)
                    drift_x = 0.5 * math.sin(t_sec * 1.5)
                    drift_y = 0.4 * math.cos(t_sec * 1.8)
                    warp_mat = np.float32([[1.0, 0.0, drift_x], [0.0, 1.0, drift_y]])
                    frame = cv2.warpAffine(frame, warp_mat, (canvas_size, canvas_size), borderMode=cv2.BORDER_REFLECT)

                    proc.stdin.write(frame.tobytes())

            proc.stdin.close()
            proc.wait(timeout=45)
            if proc.returncode != 0:
                stderr = proc.stderr.read().decode()
                raise RuntimeError(f"FFmpeg encoding failed: {stderr}")

            require_playable_video(str(target_path), min_duration_seconds=0.2)
            logger.info("[Wav2Lip] Successfully synthesized talking educator: %s", target_path)
            return target_path

        except Exception as e:
            if proc.poll() is None:
                proc.kill()
            raise e
