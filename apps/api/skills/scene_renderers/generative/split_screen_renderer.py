"""
Shikshak AI — Split Screen Dual-Pane Scene Renderer.

Renders side-by-side educational compositions:
  - Left pane: Visual illustration / schematic apparatus with subtle Ken Burns push-in
  - Right pane: Glassmorphic pedagogical takeaways, formulas, and progressive bullet points
"""
from __future__ import annotations

import logging
from pathlib import Path
import subprocess
from typing import Any, Optional
import uuid

from PIL import Image, ImageDraw, ImageFont

from skills.image_generation.generator import generate_educational_image
from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
    require_playable_video,
    sanitize_display_text,
)

logger = logging.getLogger(__name__)


def render_split_screen(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Optional[Path] = None,
) -> Path:
    """Render dual-pane side-by-side visual and structured takeaway composition."""
    duration_s = max(2.0, min(90.0, float(duration_seconds)))
    if out_path is None:
        target_path = Path("/tmp/shikshak_scenes") / f"split_{uuid.uuid4().hex}.mp4"
    else:
        target_path = Path(out_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    left_title = sanitize_display_text(payload_dict.get("left_title")) or "Visual Representation"
    right_title = sanitize_display_text(payload_dict.get("right_title")) or "Key Principles"
    raw_points = payload_dict.get("right_points") or []
    formula = sanitize_display_text(payload_dict.get("formula"))
    key_takeaway = sanitize_display_text(payload_dict.get("key_takeaway"))

    points = [sanitize_display_text(p) for p in raw_points if sanitize_display_text(p)]
    if not points:
        fallback_pt = sanitize_display_text(narration_text[:65])
        points = [fallback_pt] if fallback_pt else ["Essential takeaway"]

    # 1. Obtain or generate left image asset
    img_path_str = payload_dict.get("left_image_path")
    left_img_path = Path(img_path_str) if img_path_str else None

    if left_img_path is None or not left_img_path.is_file() or left_img_path.stat().st_size < 1000:
        left_prompt = payload_dict.get("left_image_prompt") or f"Educational illustration of {left_title}"
        img_temp = Path("/tmp/shikshak_concept_images") / f"split_img_{uuid.uuid4().hex}.png"
        left_img_path = generate_educational_image(
            concept=left_title,
            visual_objective=left_prompt,
            narration_span=narration_text,
            out_path=img_temp,
            width=640,
            height=640,
        )

    # 2. Render right-pane overlay frames using SVG
    def svg_generator(progress: float, elapsed_ms: int, total_ms: int) -> str:
        right_alpha = min(1.0, progress * 3.0)
        svg_parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">',
            '  <defs>',
            '    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">',
            '      <stop offset="0%" stop-color="#0b0f19"/>',
            '      <stop offset="100%" stop-color="#1e293b"/>',
            '    </linearGradient>',
            '    <filter id="cardGlow">',
            '      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#38bdf8" flood-opacity="0.15"/>',
            '    </filter>',
            '  </defs>',
            '  <!-- Background Canvas -->',
            '  <rect width="1280" height="720" fill="url(#bgGrad)"/>',
            '  <!-- Left Pane Image Frame Placeholder (Composite will blend or frame it) -->',
            '  <rect x="40" y="40" width="560" height="560" rx="16" fill="#111827" stroke="#334155" stroke-width="2"/>',
            '  <!-- Center Divider Line -->',
            '  <line x1="640" y1="40" x2="640" y2="600" stroke="#38bdf8" stroke-width="2" stroke-opacity="0.4" stroke-dasharray="6,6"/>',
        ]

        # Right Pane Content
        svg_parts.append(f'  <g transform="translate(680, 0)" opacity="{right_alpha:.2f}">')
        # Section Header
        svg_parts.append(
            '    <rect x="0" y="40" width="140" height="28" rx="14" fill="#0369a1" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1.2"/>'
        )
        svg_parts.append(
            '    <text x="70" y="58" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1">KEY PRINCIPLES</text>'
        )
        svg_parts.append(
            f'    <text x="0" y="105" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="bold" fill="#f8fafc">{escape_xml(right_title[:38])}</text>'
        )

        # Formula box if present (sanitized)
        current_y = 135
        if formula:
            svg_parts.append(
                f'    <rect x="0" y="{current_y}" width="560" height="54" rx="8" fill="#1e1b4b" stroke="#818cf8" stroke-width="1.5" filter="url(#cardGlow)"/>'
                f'    <text x="280" y="{current_y + 35}" font-family="Helvetica, Arial, sans-serif" font-size="20" font-weight="bold" fill="#c7d2fe" text-anchor="middle">{escape_xml(formula)}</text>'
            )
            current_y += 72
            point_h = 64
            point_gap = 16
        else:
            current_y = 145
            point_h = 76
            point_gap = 22

        # Sequential Takeaway bullet points
        num_points = min(3, len(points))
        step_window = 0.5 / max(1, num_points)

        for idx, pt in enumerate(points[:num_points]):
            trig = 0.2 + idx * step_window
            pt_prog = max(0.0, min(1.0, (progress - trig) / max(0.1, step_window)))
            pt_alpha = pt_prog
            pt_border = "#38bdf8" if pt_prog > 0.8 else "#334155"
            pt_bg = "#1e293b" if pt_prog > 0.8 else "#172033"

            svg_parts.append(
                f'    <g transform="translate(0, {current_y})" opacity="{pt_alpha:.2f}">'
                f'      <rect width="560" height="{point_h}" rx="8" fill="{pt_bg}" stroke="{pt_border}" stroke-width="1.2"/>'
                f'      <circle cx="28" cy="{point_h // 2}" r="12" fill="#0284c7" fill-opacity="0.3" stroke="#38bdf8" stroke-width="1.2"/>'
                f'      <text x="28" y="{point_h // 2 + 4}" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#e0f2fe" text-anchor="middle">{idx+1}</text>'
                f'      <text x="54" y="{point_h // 2 + 5}" font-family="Helvetica, Arial, sans-serif" font-size="16" fill="#f1f5f9">{escape_xml(pt[:55])}</text>'
                '    </g>'
            )
            current_y += point_h + point_gap

        svg_parts.append('  </g>')

        # Bottom Bar
        svg_parts.append(
            '  <rect x="40" y="630" width="1200" height="50" rx="10" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>'
        )
        bar_text = key_takeaway or f"Mastering {left_title}: Critical pedagogical relationships"
        svg_parts.append(
            f'  <text x="60" y="661" font-family="Helvetica, Arial, sans-serif" font-size="15" fill="#38bdf8" font-weight="500">{escape_xml(bar_text[:95])}</text>'
        )
        svg_parts.append('</svg>')

        return "\n".join(svg_parts)

    # 3. Render graphic overlay video
    overlay_video = Path("/tmp/shikshak_scenes") / f"split_overlay_{uuid.uuid4().hex}.mp4"
    render_svg_frames_to_mp4(
        svg_generator=svg_generator,
        duration_seconds=duration_s,
        out_path=overlay_video,
        fps=24,
    )

    # 4. Composite Left Image into the left frame via FFmpeg
    # Left frame coordinates: x=50, y=50, width=540, height=540
    fps = 24
    total_frames = max(24, int(round(duration_s * fps)))
    zoom_step = 0.08 / total_frames

    # Ken Burns push-in on left image + overlay on right
    comp_cmd = [
        "ffmpeg", "-y",
        "-i", str(overlay_video),
        "-loop", "1", "-i", str(left_img_path),
        "-filter_complex",
        f"[1:v]scale=1080:1080,zoompan=z='min(zoom+{zoom_step:.6f},1.08)':d={total_frames}:fps=24:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=540x540[left_zoom];"
        "[0:v][left_zoom]overlay=x=50:y=50:shortest=1[outv]",
        "-map", "[outv]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-t", f"{duration_s:.2f}",
        "-preset", "veryfast",
        str(target_path),
    ]

    try:
        subprocess.run(comp_cmd, check=True, timeout=120, capture_output=True)
    except subprocess.CalledProcessError as exc:
        logger.warning("[SplitScreenRenderer] FFmpeg composite failed: %s; using overlay video", exc)
        import shutil
        shutil.copyfile(str(overlay_video), str(target_path))
    finally:
        overlay_video.unlink(missing_ok=True)

    require_playable_video(str(target_path), min_width=640, min_height=360, min_duration_seconds=1.0)
    return target_path
