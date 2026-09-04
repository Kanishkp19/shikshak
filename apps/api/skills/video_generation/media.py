"""Small, strict media probes used at each video-pipeline boundary.

The pipeline must never treat a path as a successful render merely because a
provider returned it.  `ffprobe` is deliberately used here instead of file
size alone: an interrupted ffmpeg process can leave behind a non-empty but
unplayable MP4, which previously caused the compositor to discard the planned
diagram and fall back to the presenter video.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


class MediaValidationError(RuntimeError):
    """Raised when an expected media asset is absent or not decodable."""


@dataclass(frozen=True)
class MediaInfo:
    duration_seconds: float
    has_video: bool
    has_audio: bool
    width: int | None = None
    height: int | None = None


def probe_media(path: str | Path) -> MediaInfo:
    """Return decoded stream metadata, or raise when ffprobe rejects `path`."""
    media_path = Path(path)
    if not media_path.is_file() or media_path.stat().st_size == 0:
        raise MediaValidationError(f"Media file is missing or empty: {media_path}")

    try:
        completed = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration:stream=codec_type,width,height",
                "-of", "json", str(media_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        data = json.loads(completed.stdout)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise MediaValidationError(f"Unable to inspect media file: {media_path}") from exc

    streams = data.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    try:
        duration = float(data.get("format", {}).get("duration", 0) or 0)
    except (TypeError, ValueError):
        duration = 0.0

    return MediaInfo(
        duration_seconds=duration,
        has_video=video_stream is not None,
        has_audio=has_audio,
        width=int(video_stream["width"]) if video_stream and video_stream.get("width") else None,
        height=int(video_stream["height"]) if video_stream and video_stream.get("height") else None,
    )


def require_playable_video(
    path: str | Path,
    *,
    min_width: int = 64,
    min_height: int = 64,
    min_duration_seconds: float = 0.25,
) -> MediaInfo:
    """Validate that a file is a decodable, non-trivial video clip."""
    info = probe_media(path)
    if not info.has_video:
        raise MediaValidationError(f"Expected a video stream: {path}")
    if (info.width or 0) < min_width or (info.height or 0) < min_height:
        raise MediaValidationError(f"Video resolution is too small: {path}")
    if info.duration_seconds < min_duration_seconds:
        raise MediaValidationError(f"Video duration is too short: {path}")
    return info


def require_playable_audio(path: str | Path) -> MediaInfo:
    """Validate that a file carries a decodable audio stream."""
    info = probe_media(path)
    if not info.has_audio or info.duration_seconds <= 0:
        raise MediaValidationError(f"Expected a non-empty audio stream: {path}")
    return info
