"""
Shikshak AI — Split Screen Dual-Pane Scene Renderer.

Renders side-by-side educational compositions:
  - Left pane: Visual illustration / schematic apparatus with subtle Ken Burns push-in
  - Right pane: Glassmorphic pedagogical takeaways, formulas, and progressive bullet points
"""
from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Optional
import uuid

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

    # 1. Detect domain for Left Classroom Schematic
    c_lower = (left_title + " " + narration_text + " " + right_title).lower()
    is_optics = any(k in c_lower for k in ("light", "reflect", "vision", "ray", "mirror", "optics", "lens"))
    is_bio = any(k in c_lower for k in ("photo", "chloro", "cell", "plant", "leaf", "organelle"))
    is_circuit = any(k in c_lower for k in ("circuit", "resistor", "ohm", "current", "battery", "voltage"))

    # 2. Render dual-pane classroom blackboard frames using pure vector SVG
    def svg_generator(progress: float, elapsed_ms: int, total_ms: int) -> str:
        pulse = 0.5 + 0.5 * math.sin(elapsed_ms * 0.003)
        ray_anim = min(1.0, progress * 1.5)
        right_alpha = min(1.0, progress * 3.0)

        svg_parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">',
            '  <defs>',
            '    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">',
            '      <stop offset="0%" stop-color="#0b1320"/>',
            '      <stop offset="100%" stop-color="#0f1d30"/>',
            '    </linearGradient>',
            '    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
            '      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#16253b" stroke-width="0.75"/>',
            '    </pattern>',
            '    <filter id="cardGlow">',
            '      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#38bdf8" flood-opacity="0.3"/>',
            '    </filter>',
            '    <filter id="amberGlow">',
            '      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#f59e0b" flood-opacity="0.4"/>',
            '    </filter>',
            '  </defs>',
            '  <!-- Background Canvas -->',
            '  <rect width="1280" height="720" fill="url(#bgGrad)"/>',
            '  <rect width="1280" height="720" fill="url(#grid)"/>',
            '  <!-- Classroom Frame -->',
            '  <rect x="20" y="20" width="1240" height="680" rx="12" fill="none" stroke="#2a3c54" stroke-width="2"/>',
            '  <!-- Center Divider Line -->',
            '  <line x1="640" y1="40" x2="640" y2="600" stroke="#38bdf8" stroke-width="2" stroke-opacity="0.3" stroke-dasharray="6,6"/>',
        ]

        # ── Left Pane: Vector Classroom Schematic ──
        svg_parts.append('  <!-- Left Pane: Classroom Vector Schematic Stage -->')
        svg_parts.append('  <g transform="translate(40, 40)">')
        svg_parts.append('    <rect width="560" height="560" rx="12" fill="#0c1524" stroke="#253549" stroke-width="1.5"/>')
        svg_parts.append('    <rect x="20" y="20" width="200" height="26" rx="13" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>')
        svg_parts.append('    <text x="120" y="37" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1">CLASSROOM SCHEMA</text>')
        svg_parts.append(f'    <text x="20" y="78" font-family="Helvetica, Arial, sans-serif" font-size="22" font-weight="bold" fill="#f8fafc">{escape_xml(left_title[:32])}</text>')

        if is_optics:
            surf_y = 360
            norm_x = 280
            # Plane Mirror
            svg_parts.append(f'    <line x1="60" y1="{surf_y}" x2="500" y2="{surf_y}" stroke="#94a3b8" stroke-width="4"/>')
            for hx in range(70, 490, 25):
                svg_parts.append(f'    <line x1="{hx}" y1="{surf_y}" x2="{hx - 12}" y2="{surf_y + 16}" stroke="#475569" stroke-width="1.5"/>')
            svg_parts.append(f'    <text x="400" y="{surf_y + 35}" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#94a3b8">Reflecting Surface</text>')

            # Normal line
            svg_parts.append(f'    <line x1="{norm_x}" y1="180" x2="{norm_x}" y2="{surf_y}" stroke="#64748b" stroke-width="2" stroke-dasharray="6,6"/>')
            svg_parts.append(f'    <text x="{norm_x - 10}" y="170" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#94a3b8">Normal (N)</text>')

            # Incident Ray
            cur_inc_x = 100 + (norm_x - 100) * min(1.0, ray_anim * 1.5)
            cur_inc_y = 210 + (surf_y - 210) * min(1.0, ray_anim * 1.5)
            svg_parts.append(f'    <line x1="100" y1="210" x2="{cur_inc_x}" y2="{cur_inc_y}" stroke="#fbbf24" stroke-width="3" filter="url(#amberGlow)"/>')
            svg_parts.append(f'    <circle cx="100" cy="210" r="5" fill="#f59e0b"/>')
            svg_parts.append(f'    <text x="80" y="195" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#fbbf24">Incident Ray</text>')

            # Reflected Ray
            if ray_anim > 0.5:
                ref_prog = (ray_anim - 0.5) * 2.0
                cur_ref_x = norm_x + (460 - norm_x) * ref_prog
                cur_ref_y = surf_y + (210 - surf_y) * ref_prog
                svg_parts.append(f'    <line x1="{norm_x}" y1="{surf_y}" x2="{cur_ref_x}" y2="{cur_ref_y}" stroke="#38bdf8" stroke-width="3" filter="url(#cardGlow)"/>')
                svg_parts.append(f'    <circle cx="{norm_x}" cy="{surf_y}" r="6" fill="#38bdf8"/>')
                svg_parts.append(f'    <text x="400" y="195" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">Reflected Ray</text>')
                svg_parts.append(f'    <text x="{norm_x - 45}" y="310" font-family="Helvetica, Arial, sans-serif" font-size="16" font-weight="bold" fill="#fbbf24">∠i</text>')
                svg_parts.append(f'    <text x="{norm_x + 30}" y="310" font-family="Helvetica, Arial, sans-serif" font-size="16" font-weight="bold" fill="#38bdf8">∠r</text>')
                svg_parts.append(f'    <text x="280" y="450" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#34d399" text-anchor="middle">Law Confirmed: ∠i = ∠r</text>')

        elif is_bio:
            cx, cy = 280, 310
            svg_parts.append(f'    <ellipse cx="{cx}" cy="{cy}" rx="180" ry="110" fill="#064e3b" fill-opacity="0.3" stroke="#10b981" stroke-width="2.5" stroke-dasharray="8,4"/>')
            svg_parts.append(f'    <text x="{cx}" y="{cy - 75}" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#34d399" text-anchor="middle">Chloroplast Organelle</text>')
            for gx in (cx - 80, cx, cx + 80):
                for ty in (cy - 25, cy, cy + 25):
                    svg_parts.append(f'    <rect x="{gx - 22}" y="{ty - 7}" width="44" height="14" rx="5" fill="#059669" stroke="#34d399" stroke-width="1.2"/>')
            svg_parts.append(f'    <text x="{cx}" y="{cy + 75}" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#a7f3d0" text-anchor="middle">Thylakoid Grana Stacks</text>')
            svg_parts.append(f'    <text x="70" y="470" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">Light + H₂O + CO₂</text>')
            svg_parts.append(f'    <text x="350" y="470" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#fbbf24">⟶ Glucose + O₂</text>')

        elif is_circuit:
            cx, cy = 280, 310
            svg_parts.append(f'    <rect x="120" y="200" width="320" height="220" rx="10" fill="none" stroke="#38bdf8" stroke-width="3"/>')
            svg_parts.append(f'    <rect x="250" y="185" width="60" height="30" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>')
            svg_parts.append(f'    <text x="280" y="205" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#fbbf24" text-anchor="middle">100Ω</text>')
            svg_parts.append(f'    <line x1="260" y1="420" x2="260" y2="440" stroke="#f87171" stroke-width="4"/>')
            svg_parts.append(f'    <line x1="280" y1="410" x2="280" y2="450" stroke="#38bdf8" stroke-width="4"/>')
            svg_parts.append(f'    <text x="280" y="480" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#e0f2fe" text-anchor="middle">Battery 12V</text>')

        else:
            cx, cy = 280, 310
            nodes = [(cx, cy - 80, "Initial State"), (cx - 110, cy + 60, "Reaction Process"), (cx + 110, cy + 60, "Equilibrium")]
            svg_parts.append(f'    <line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[1][0]}" y2="{nodes[1][1]}" stroke="#38bdf8" stroke-width="2"/>')
            svg_parts.append(f'    <line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[2][0]}" y2="{nodes[2][1]}" stroke="#38bdf8" stroke-width="2"/>')
            svg_parts.append(f'    <line x1="{nodes[1][0]}" y1="{nodes[1][1]}" x2="{nodes[2][0]}" y2="{nodes[2][1]}" stroke="#34d399" stroke-width="2" stroke-dasharray="6,4"/>')
            for nx, ny, nlbl in nodes:
                svg_parts.append(f'    <circle cx="{nx}" cy="{ny}" r="34" fill="#1e293b" stroke="#38bdf8" stroke-width="2" filter="url(#cardGlow)"/>')
                svg_parts.append(f'    <circle cx="{nx}" cy="{ny}" r="{16 + 4 * pulse:.1f}" fill="#0284c7" fill-opacity="0.3"/>')
                svg_parts.append(f'    <text x="{nx}" y="{ny + 4}" font-family="Helvetica, Arial, sans-serif" font-size="10" font-weight="bold" fill="#f8fafc" text-anchor="middle">{escape_xml(nlbl)}</text>')

        svg_parts.append('  </g>')

        # ── Right Pane: Structured Pedagogical Principles ──
        svg_parts.append(f'  <g transform="translate(680, 0)" opacity="{right_alpha:.2f}">')
        svg_parts.append(
            '    <rect x="0" y="40" width="140" height="28" rx="14" fill="#0369a1" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1.2"/>'
        )
        svg_parts.append(
            '    <text x="70" y="58" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1">KEY PRINCIPLES</text>'
        )
        svg_parts.append(
            f'    <text x="0" y="105" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="bold" fill="#f8fafc">{escape_xml(right_title[:38])}</text>'
        )

        current_y = 135
        if formula:
            svg_parts.append(
                f'    <rect x="0" y="{current_y}" width="560" height="54" rx="8" fill="#111c2e" stroke="#818cf8" stroke-width="1.5" filter="url(#cardGlow)"/>'
                f'    <text x="280" y="{current_y + 35}" font-family="Courier New, monospace, sans-serif" font-size="20" font-weight="bold" fill="#c7d2fe" text-anchor="middle">{escape_xml(formula)}</text>'
            )
            current_y += 72
            point_h = 64
            point_gap = 16
        else:
            current_y = 145
            point_h = 76
            point_gap = 22

        num_points = min(3, len(points))
        step_window = 0.5 / max(1, num_points)

        for idx, pt in enumerate(points[:num_points]):
            trig = 0.2 + idx * step_window
            pt_prog = max(0.0, min(1.0, (progress - trig) / max(0.1, step_window)))
            pt_alpha = pt_prog
            pt_border = "#38bdf8" if pt_prog > 0.8 else "#1e293b"
            pt_bg = "#111c2e" if pt_prog > 0.8 else "#0c1524"

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

        # Bottom Full-Width Bar
        svg_parts.append(
            '  <rect x="40" y="630" width="1200" height="50" rx="10" fill="#0f1d30" stroke="#1e3a5f" stroke-width="1.5"/>'
        )
        bar_text = key_takeaway or f"Mastering {left_title}: Critical pedagogical relationships"
        svg_parts.append(
            f'  <text x="60" y="661" font-family="Helvetica, Arial, sans-serif" font-size="15" fill="#38bdf8" font-weight="500">{escape_xml(bar_text[:95])}</text>'
        )
        svg_parts.append('</svg>')

        return "\n".join(svg_parts)

    # Render directly to MP4 using pure vector SVG engine (zero stock photos)
    render_svg_frames_to_mp4(
        svg_generator=svg_generator,
        duration_seconds=duration_s,
        out_path=target_path,
        fps=24,
    )

    require_playable_video(str(target_path), min_width=640, min_height=360, min_duration_seconds=1.0)
    return target_path
