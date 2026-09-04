"""
Shikshak AI — Video Stitching & Studio Compositor Skill.

Concatenates scene sequences into complete segment lessons, overlays a
redesigned instructor card with a thin accent border and a simple audio-reactive bar
on the side-rail, and stitches segments into final downloadable lessons.
"""
from __future__ import annotations

import subprocess
import uuid
from pathlib import Path
from typing import Any

from models.avatar import AvatarPresenterMode
from skills.video_generation.media import (
    MediaValidationError,
    require_playable_audio,
    require_playable_video,
)


def stitch_segment(
    *,
    avatar_video_path: str = "",
    concept_video_path: str,
    audio_path: str | None = None,
    caption_text: str | None = None,
    language: str = "en",
    presenter_mode: AvatarPresenterMode | str = AvatarPresenterMode.TEACHER_EXPLAIN,
    **kwargs: Any,
) -> str:
    """Create an educational lesson segment composited according to pedagogical intent.

    Supported Presenter Modes:
      - TEACHER_OFF_SCREEN: 100% full-canvas visualization, teacher hidden.
      - TEACHER_EXPLAIN: Full-canvas visualization with sleek picture-in-picture (PIP)
        instructor overlay in the corner.
      - TEACHER_INTRO: Prominent educator framing for lesson introduction.
      - TEACHER_EMPHASIZE / TEACHER_RECAP: Balanced pedagogical focus.
    """
    out_dir = Path("/tmp/shikshak_final")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"segment_{uuid.uuid4().hex}.mp4"

    if isinstance(presenter_mode, str):
        try:
            p_mode = AvatarPresenterMode(presenter_mode)
        except ValueError:
            p_mode = AvatarPresenterMode.TEACHER_EXPLAIN
    else:
        p_mode = presenter_mode

    concept = Path(concept_video_path)
    require_playable_video(concept, min_width=640, min_height=360, min_duration_seconds=1.0)

    avatar = Path(avatar_video_path) if avatar_video_path else None
    avatar_is_usable = False
    if avatar and avatar.exists() and p_mode != AvatarPresenterMode.TEACHER_OFF_SCREEN:
        try:
            require_playable_video(avatar, min_width=64, min_height=64, min_duration_seconds=0.25)
            avatar_is_usable = True
        except MediaValidationError:
            avatar_is_usable = False

    # Audio verification
    audio_is_usable = False
    audio_source: Path | None = None
    if audio_path and Path(audio_path).exists():
        try:
            require_playable_audio(Path(audio_path))
            audio_source = Path(audio_path)
            audio_is_usable = True
        except MediaValidationError:
            pass
    elif avatar_is_usable and avatar:
        try:
            require_playable_audio(avatar)
            audio_source = avatar
            audio_is_usable = True
        except MediaValidationError:
            pass

    cmd = ["ffmpeg", "-y", "-i", str(concept)]

    if audio_is_usable and audio_source:
        cmd += ["-i", str(audio_source)]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]

    if avatar_is_usable and avatar:
        cmd += ["-i", str(avatar)]

        if p_mode in (AvatarPresenterMode.TEACHER_INTRO, AvatarPresenterMode.TEACHER_RECAP):
            # ── Prominent Teacher Intro / Recap Stage ──
            filter_parts = [
                "color=c=0x0b1329:s=1280x720[bg]",
                "[2:v]scale=520:580:force_original_aspect_ratio=increase:flags=lanczos,"
                "crop=520:580,"
                "pad=524:584:2:2:color=0x38bdf8@0.9,setsar=1[presenter]",
                "[0:v]scale=360:202:force_original_aspect_ratio=decrease:flags=lanczos,"
                "pad=364:206:2:2:color=0x2563eb@0.85,setsar=1[preview]",
                "[1:a]showwaves=s=524x20:mode=line:colors=0x38bdf8@0.95:scale=sqrt,setsar=1[waves]",
                "[bg][presenter]overlay=(W-w)/2:50[stage_with_p]",
                "[stage_with_p][waves]overlay=(W-w)/2:640[stage_with_w]",
                "[stage_with_w][preview]overlay=60:460[v]",
            ]
        else:
            # ── TEACHER_EXPLAIN: Sleek Picture-in-Picture (PIP) ──
            # 100% full 1280x720 canvas for scientific visualization,
            # floating presenter card in bottom-right corner with 2px cyan border
            filter_parts = [
                "[0:v]scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,"
                "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0b1329,setsar=1[stage]",
                "[2:v]scale=220:250:force_original_aspect_ratio=increase:flags=lanczos,"
                "crop=220:250,"
                "pad=224:254:2:2:color=0x38bdf8@0.9,setsar=1[pip]",
                "[1:a]showwaves=s=224x16:mode=line:colors=0x38bdf8@0.95:scale=sqrt,setsar=1[waves]",
                "[stage][pip]overlay=1020:416[stage_with_pip]",
                "[stage_with_pip][waves]overlay=1020:674[v]",
            ]
    else:
        # ── TEACHER_OFF_SCREEN or Pure Concept View ──
        filter_parts = [
            "[0:v]scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,"
            "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0b1329,setsar=1[v]"
        ]

    cmd += [
        "-filter_complex", ";".join(filter_parts),
        "-map", "[v]",
        "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest", str(out_path),
    ]

    try:
        subprocess.run(cmd, check=True, timeout=180, capture_output=True, text=True)
        require_playable_video(out_path, min_width=1280, min_height=720, min_duration_seconds=1.0)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired, MediaValidationError) as exc:
        out_path.unlink(missing_ok=True)
        raise RuntimeError("Unable to compose the animated teaching visual") from exc

    return str(out_path)


def stitch_scenes_into_segment(
    *,
    scene_video_paths: list[str],
    audio_path: str | None = None,
    avatar_video_path: str | None = None,
    language: str = "en",
) -> str:
    """Stitch a sequence of rendered scene MP4s into a single combined segment video."""
    if not scene_video_paths:
        raise ValueError("No scene videos provided for stitching")

    out_dir = Path("/tmp/shikshak_final")
    out_dir.mkdir(parents=True, exist_ok=True)

    if len(scene_video_paths) == 1:
        concept_combined = scene_video_paths[0]
    else:
        concept_combined = concat_segments(scene_video_paths)

    return stitch_segment(
        avatar_video_path=avatar_video_path or "",
        concept_video_path=concept_combined,
        audio_path=audio_path,
        language=language,
    )


def concat_segments(segment_paths: list[str]) -> str:
    """Concatenate per-segment videos into one final lesson video."""
    if not segment_paths:
        return ""

    out_dir = Path("/tmp/shikshak_final")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"lesson_{uuid.uuid4().hex}.mp4"

    valid_paths = [Path(p) for p in segment_paths if p and Path(p).exists()]
    for path in valid_paths:
        require_playable_video(path, min_width=640, min_height=360, min_duration_seconds=1.0)

    list_path = out_dir / f"concat_{uuid.uuid4().hex}.txt"
    lines = [f"file '{path}'" for path in valid_paths]
    list_path.write_text("\n".join(lines), encoding="utf-8")

    if not lines:
        out_path.write_bytes(b"")
        return str(out_path)

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                "-movflags", "+faststart",
                str(out_path),
            ],
            check=True,
            timeout=180,
            capture_output=True,
        )
        require_playable_video(out_path, min_width=640, min_height=360, min_duration_seconds=1.0)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired, MediaValidationError) as exc:
        out_path.unlink(missing_ok=True)
        raise RuntimeError("Unable to concatenate all completed lesson segments") from exc

    return str(out_path)
