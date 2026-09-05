"""
Shikshak AI — Scene Renderers Base Module.

Provides standard 1280x720 SVG canvas helpers, animation frame generators,
and high-speed CairoSVG + FFmpeg encoding pipe.
"""
from __future__ import annotations

import html
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, Callable, Protocol

# Ensure Cairo libraries are found on macOS
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")

import cairosvg
from skills.video_generation.media import require_playable_video


class SceneRenderer(Protocol):
    """Protocol for all scene renderers."""
    def render(
        self,
        payload: dict[str, Any],
        narration_text: str = "",
        duration_seconds: float = 6.0,
        out_path: Path | None = None,
    ) -> Path:
        ...


_ALLOWED_XML_ENTITIES = {"&amp;", "&lt;", "&gt;", "&quot;", "&apos;"}


def sanitize_svg_entities(svg_str: str) -> str:
    """Ensure SVG XML string does not contain HTML-only entities that break expat XML parser."""
    def _replace_entity(m: re.Match) -> str:
        entity = m.group(0)
        if entity in _ALLOWED_XML_ENTITIES or entity.startswith("&#"):
            return entity
        decoded = html.unescape(entity)
        if decoded != entity:
            return escape_xml(decoded) if decoded in ("&", "<", ">", '"', "'") else decoded
        return " "

    return re.sub(r"&[A-Za-z0-9_#]+;", _replace_entity, svg_str)


def render_svg_frames_to_mp4(
    svg_generator: Callable[[float, int, int], str],
    duration_seconds: float,
    out_path: Path | None = None,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic SVG frame generator to an H.264 MP4 video.

    svg_generator receives: (progress: 0.0..1.0, elapsed_ms: int, total_ms: int) -> svg_xml_str.
    Pipes PNG frames into FFmpeg via image2pipe for zero disk I/O overhead.
    """
    duration_seconds = max(2.0, min(90.0, float(duration_seconds)))
    total_frames = max(1, int(round(duration_seconds * fps)))
    total_ms = int(duration_seconds * 1000)

    if out_path is None:
        target_path = Path("/tmp/shikshak_scenes") / f"scene_{uuid.uuid4().hex}.mp4"
    else:
        target_path = Path(out_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe",
        "-vcodec", "png",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "ultrafast",
        "-crf", "18",
        str(target_path),
    ]

    proc = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        for frame_idx in range(total_frames):
            progress = min(1.0, frame_idx / max(1, total_frames - 1))
            elapsed_ms = int((frame_idx / fps) * 1000)
            svg_content = svg_generator(progress, elapsed_ms, total_ms)
            clean_svg = sanitize_svg_entities(svg_content)
            png_bytes = cairosvg.svg2png(
                bytestring=clean_svg.encode("utf-8"),
                output_width=width,
                output_height=height,
            )
            proc.stdin.write(png_bytes)

        proc.stdin.close()
        stderr = proc.stderr.read()
        proc.wait(timeout=120)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed with code {proc.returncode}: {stderr.decode('utf-8', errors='ignore')}")

        require_playable_video(str(target_path), min_width=640, min_height=360, min_duration_seconds=1.0)
        return target_path
    except Exception as e:
        if proc.poll() is None:
            proc.kill()
        target_path.unlink(missing_ok=True)
        raise RuntimeError(f"Scene frame rendering failed: {e}") from e


def escape_xml(text: str) -> str:
    """Escape XML characters for safe inclusion in SVG text elements."""
    if text is None:
        return ""
    s = html.unescape(str(text))
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def format_subscripts(formula: str) -> str:
    """Helper to convert standard numbers in chemical formulas to unicode subscripts if needed."""
    subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    # Convert reaction arrows to clean unicode arrow
    formula = formula.replace("->", " ⟶ ").replace("→", " ⟶ ").replace("&#8594;", " ⟶ ")
    # Only convert numbers immediately following letters or closing brackets/parentheses into subscripts
    import re
    return re.sub(r"([A-Za-z\)\]])(\d+)", lambda m: m.group(1) + m.group(2).translate(subscripts), formula)


FORBIDDEN_TEXT_PLACEHOLDERS = {
    "not_in_source",
    "none",
    "n/a",
    "na",
    "undefined",
    "[missing]",
    "null",
    "not available",
    "unknown",
}


def sanitize_display_text(text: Any) -> str:
    """Sanitize educational text, preventing LLM placeholders (e.g. NOT_IN_SOURCE) from rendering."""
    if text is None:
        return ""
    cleaned = str(text).strip()
    if cleaned.lower() in FORBIDDEN_TEXT_PLACEHOLDERS or "not_in_source" in cleaned.lower():
        return ""
    return cleaned



