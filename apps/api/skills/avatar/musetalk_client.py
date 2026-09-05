"""
Shikshak AI — MuseTalk v1.5 Apple Silicon Avatar Renderer.

Communicates with the local or remote MuseTalk-Mac service:
  https://github.com/barnent1/musetalk-mac
Running on Apple Silicon (M4/M3/M2/M1) via Metal Performance Shaders (MPS).

Endpoints consumed:
  GET  /health           -> Check MPS device readiness & cached avatar keys
  POST /warmup           -> Pre-compute & cache avatar face latents / landmarks
  POST /lipsync_stream   -> Streamed raw MP4 generation from cached avatar + audio
  POST /                 -> Synchronous lip-sync generation (video_b64 + audio_b64)
  POST /speak            -> Direct TTS-to-video if supported

Includes automatic, high-fidelity local fallback (animated portrait with natural breathing)
if the MuseTalk service is offline or initializing.
"""
from __future__ import annotations

import base64
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx

from models.avatar import AvatarProfile, DEFAULT_FEMALE_TEACHER
from skills.avatar.base import AvatarRenderer
from skills.video_generation.media import require_playable_video

logger = logging.getLogger(__name__)

DEFAULT_MUSETALK_ENDPOINT = os.getenv("MUSETALK_ENDPOINT", "http://127.0.0.1:8001")


class MuseTalkMacRenderer(AvatarRenderer):
    """MuseTalk v1.5 client tailored for Apple Silicon MPS inference."""

    def __init__(self, endpoint: str = DEFAULT_MUSETALK_ENDPOINT, timeout_seconds: float = 60.0):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout_seconds
        self._cached_avatars: set[str] = set()

    def health_check(self) -> dict[str, Any]:
        """Query MuseTalk-Mac server health and MPS device readiness."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.endpoint}/health")
                if res.status_code == 200:
                    data = res.json()
                    # Verify this is actually a MuseTalk service and not another local API
                    if "cached_avatars" in data or data.get("device") in ("mps", "cuda", "cpu"):
                        cached = data.get("cached_avatars", [])
                        if isinstance(cached, list):
                            self._cached_avatars.update(cached)
                        return {"ok": True, "device": data.get("device", "mps"), "cached_avatars": cached}
                return {"ok": False, "status_code": res.status_code, "error": "Not a MuseTalk endpoint"}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "endpoint": self.endpoint}

    def prepare_avatar(self, profile: AvatarProfile) -> str:
        """Pre-cache avatar facial latents on the MuseTalk-Mac server."""
        avatar_key = profile.prepared_avatar_key or profile.avatar_id

        # Check if already cached on server
        health = self.health_check()
        if health.get("ok") and avatar_key in health.get("cached_avatars", []):
            self._cached_avatars.add(avatar_key)
            return avatar_key

        portrait_path = profile.get_absolute_portrait_path()
        if not portrait_path.exists():
            raise FileNotFoundError(f"Avatar reference portrait not found: {portrait_path}")

        image_bytes = portrait_path.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                payload = {
                    "video_b64": image_b64,
                    "avatar_key": avatar_key,
                }
                res = client.post(f"{self.endpoint}/warmup", json=payload)
                if res.status_code in (200, 201):
                    self._cached_avatars.add(avatar_key)
                    logger.info("[MuseTalk] Successfully warmed up avatar key: %s", avatar_key)
                    return avatar_key
                else:
                    logger.warning(
                        "[MuseTalk] Warmup returned status %d: %s. Continuing with key.",
                        res.status_code,
                        res.text,
                    )
                    return avatar_key
        except Exception as exc:
            logger.warning("[MuseTalk] Warmup failed (%s). Continuing with avatar key.", exc)
            return avatar_key

    def render_speech(
        self,
        audio_path: Path,
        profile: AvatarProfile = DEFAULT_FEMALE_TEACHER,
        out_path: Optional[Path] = None,
    ) -> Path:
        """Render talking-head video synced to narration audio.

        If MuseTalk service is active, queries MPS inference.
        If unavailable, engages local animated teacher fallback.
        """
        if out_path is None:
            target_path = Path("/tmp/shikshak_scenes") / f"avatar_{uuid.uuid4().hex}.mp4"
        else:
            target_path = Path(out_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Attempt MuseTalk-Mac service call
        health = self.health_check()
        if health.get("ok"):
            try:
                avatar_key = profile.prepared_avatar_key or profile.avatar_id
                audio_bytes = audio_path.read_bytes()
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

                with httpx.Client(timeout=self.timeout) as client:
                    logger.info(
                        "[MuseTalk] Requesting lip-sync for avatar=%s, audio=%s (%d bytes)",
                        avatar_key,
                        audio_path.name,
                        len(audio_bytes),
                    )
                    # Try /lipsync_stream endpoint first
                    res = client.post(
                        f"{self.endpoint}/lipsync_stream",
                        json={"avatar_key": avatar_key, "audio_b64": audio_b64},
                    )

                    if res.status_code == 200 and len(res.content) > 1000:
                        target_path.write_bytes(res.content)
                        require_playable_video(str(target_path), min_duration_seconds=0.5)
                        logger.info("[MuseTalk] Stream render successful: %s", target_path)
                        return target_path

                    # Fallback to standard POST /
                    portrait_bytes = profile.get_absolute_portrait_path().read_bytes()
                    portrait_b64 = base64.b64encode(portrait_bytes).decode("utf-8")
                    res2 = client.post(
                        f"{self.endpoint}/",
                        json={
                            "video_b64": portrait_b64,
                            "audio_b64": audio_b64,
                            "avatar_key": avatar_key,
                        },
                    )
                    if res2.status_code == 200:
                        data = res2.json()
                        video_b64 = data.get("video_b64")
                        if video_b64:
                            video_bytes = base64.b64decode(video_b64)
                            target_path.write_bytes(video_bytes)
                            require_playable_video(str(target_path), min_duration_seconds=0.5)
                            logger.info("[MuseTalk] Standard render successful: %s", target_path)
                            return target_path

            except Exception as exc:
                logger.warning(
                    "[MuseTalk] Service invocation failed (%s). Engaging local animated fallback.",
                    exc,
                )

        # Local Animated Teacher Fallback (Graceful Degradation Guarantee)
        logger.info("[MuseTalk] Using high-fidelity local animated teacher renderer.")
        return render_local_animated_teacher(audio_path, profile, target_path)


def render_local_animated_teacher(
    audio_path: Path,
    profile: AvatarProfile,
    out_path: Path,
) -> Path:
    """Deterministic, audio-driven local avatar renderer.

    Generates synchronized talking educator video with active mouth opening,
    visemes, natural blinking, and subtle micro-movements.
    """
    portrait_path = profile.get_absolute_portrait_path()
    if not portrait_path.exists():
        logger.warning("[Avatar] Portrait missing at %s; checking assets/female_teacher_ref.jpg", portrait_path)
        alt = Path(__file__).resolve().parent.parent.parent / "assets" / "female_teacher_ref.jpg"
        if alt.exists():
            portrait_path = alt

    # 1. Try high-fidelity audio-driven lively avatar generator
    try:
        from skills.avatar.lively_avatar import generate_lively_avatar_video
        return generate_lively_avatar_video(
            portrait_path=portrait_path,
            audio_path=audio_path,
            out_path=out_path,
            fps=25,
            canvas_size=512,
        )
    except Exception as exc:
        logger.warning("[Avatar] LivelyTalkingAvatar failed (%s); falling back to breathing zoom filter.", exc)

    # 2. Resilient fallback: Subtle Breathing Animation with Audio Sync
    if not portrait_path.exists():
        portrait_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x1e293b:s=512x512",
            "-frames:v", "1", str(portrait_path)
        ], check=True, capture_output=True)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(portrait_path),
        "-i", str(audio_path),
        "-filter_complex",
        (
            "[0:v]scale=540:540,"
            "zoompan=z='1.0+0.015*sin(2*PI*it/3.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            "d=1:s=512x512:fps=25[v]"
        ),
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(out_path),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"Local animated teacher render failed: {proc.stderr}")

    require_playable_video(str(out_path), min_duration_seconds=0.2)
    return out_path

