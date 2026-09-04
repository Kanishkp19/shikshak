"""Local ffmpeg compositor for diagram frames plus already-rendered TTS audio."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from .animator import keyframe_times
from .renderer import render_frame_to_path
from .schemas import ContentBlueprint


def audio_duration_ms(audio_path: str | Path) -> int:
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)],
        check=True, capture_output=True, text=True, timeout=15,
    )
    return round(float(json.loads(completed.stdout)["format"]["duration"]) * 1000)


def compose_video(blueprint: ContentBlueprint, audio_path: str | Path, output_path: str | Path, *, fps: int = 24) -> Path:
    """Render local frames and mux the supplied narration into a faststart MP4."""
    audio = Path(audio_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    duration_ms = audio_duration_ms(audio)
    synced = blueprint.model_copy(update={"narration_duration_estimate_ms": duration_ms})
    with tempfile.TemporaryDirectory(prefix="shikshak_diagram_frames_") as frame_dir:
        frame_root = Path(frame_dir)
        for index, at_ms in enumerate(keyframe_times(synced, fps), start=1):
            render_frame_to_path(synced, frame_root / f"frame_{index:05d}.png", at_ms)
        subprocess.run(
            [
                "ffmpeg", "-y", "-framerate", str(fps), "-i", str(frame_root / "frame_%05d.png"),
                "-i", str(audio), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "-shortest", str(output),
            ],
            check=True, capture_output=True, timeout=240,
        )
    return output
