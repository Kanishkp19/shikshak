"""
Shikshak AI — Talking Educator Avatar Rendering Skill.

Dispatches speech audio and educator portrait to the MuseTalk v1.5 renderer
(with deterministic local breathing & audio synchronization fallback).
Zero external neural weights / sub-repos required.
"""
from __future__ import annotations

import logging
from pathlib import Path
import uuid

from config import settings
from models.avatar import DEFAULT_FEMALE_TEACHER
from skills.avatar.musetalk_client import MuseTalkMacRenderer

logger = logging.getLogger(__name__)


def render_lip_sync(audio_path: str) -> str:
    """Render a talking educator avatar video using Wav2Lip / MuseTalk / local fallback."""
    out_dir = Path("/tmp/shikshak_avatar")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"avatar_{uuid.uuid4().hex}.mp4"

    audio = Path(audio_path).resolve()

    # 1. Primary Neural Renderer: Wav2Lip
    if settings.avatar_provider == "wav2lip":
        try:
            from skills.avatar.wav2lip_renderer import Wav2LipRenderer
            renderer = Wav2LipRenderer()
            result_path = renderer.render_speech(
                audio_path=audio,
                profile=DEFAULT_FEMALE_TEACHER,
                out_path=out_path,
            )
            return str(result_path)
        except Exception as e:
            logger.warning("[LipSync] Wav2Lip rendering failed (%s). Attempting secondary renderer.", e)

    # 2. Secondary Renderer: MuseTalk-Mac service
    if settings.avatar_provider in ("musetalk", "wav2lip"):
        try:
            renderer = MuseTalkMacRenderer()
            result_path = renderer.render_speech(
                audio_path=audio,
                profile=DEFAULT_FEMALE_TEACHER,
                out_path=out_path,
            )
            return str(result_path)
        except Exception as e:
            logger.warning("[LipSync] MuseTalk rendering failed (%s). Engaging clean local fallback.", e)

    # 3. Graceful Local Fallback (Guaranteed Playable Video)
    from skills.avatar.musetalk_client import render_local_animated_teacher
    return str(render_local_animated_teacher(audio, DEFAULT_FEMALE_TEACHER, out_path))


def resolve_reference_image() -> str:
    """Resolve educator reference portrait with neutral background."""
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

    # Fallback default
    return str((api_dir / "assets" / "female_teacher_ref.jpg").resolve())
