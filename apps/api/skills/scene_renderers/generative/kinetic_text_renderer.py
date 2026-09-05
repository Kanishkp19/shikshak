"""
Shikshak AI — Kinetic Typography Scene Renderer.

Renders high-impact pedagogical typography cards, core definitions, and key
takeaway reveals using vector SVG frames piped directly to FFmpeg.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional
import uuid

from skills.scene_renderers.base import escape_xml, render_svg_frames_to_mp4

logger = logging.getLogger(__name__)


def render_kinetic_text(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Optional[Path] = None,
) -> Path:
    """Render animated typographic concept card with progressive key point illumination."""
    title = payload_dict.get("title") or "Core Principle"
    subtitle = payload_dict.get("subtitle") or narration_text[:60]
    raw_points = payload_dict.get("key_takeaways") or payload_dict.get("key_points") or []
    badge = payload_dict.get("badge") or "CORE PRINCIPLE"
    equation = payload_dict.get("equation") or ""
    highlight_word = payload_dict.get("highlight_word") or ""

    points = [str(p) for p in raw_points if str(p).strip()]
    if not points:
        points = [narration_text[:70]] if narration_text else ["Essential scientific concept"]

    def svg_generator(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Pacing:
        # 0.0 - 0.2: Badge and Title ease in
        # 0.2 - 0.8: Bullet points sequentially light up
        # 0.8 - 1.0: Full glowing takeaway state
        title_alpha = min(1.0, progress * 4.0)
        title_offset = int((1.0 - title_alpha) * 15)

        # SVG header & background
        svg_parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">',
            '  <defs>',
            '    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">',
            '      <stop offset="0%" stop-color="#0f172a"/>',
            '      <stop offset="50%" stop-color="#1e293b"/>',
            '      <stop offset="100%" stop-color="#0f172a"/>',
            '    </linearGradient>',
            '    <filter id="cardGlow" x="-10%" y="-10%" width="120%" height="120%">',
            '      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#38bdf8" flood-opacity="0.18"/>',
            '    </filter>',
            '  </defs>',
            '  <!-- Background Canvas -->',
            '  <rect width="1280" height="720" fill="url(#bgGrad)"/>',
            '  <!-- Accent Grid -->',
            '  <g stroke="#334155" stroke-width="1" opacity="0.25">',
            '    <line x1="120" y1="0" x2="120" y2="720"/>',
            '    <line x1="1160" y1="0" x2="1160" y2="720"/>',
            '    <line x1="0" y1="180" x2="1280" y2="180"/>',
            '    <line x1="0" y1="620" x2="1280" y2="620"/>',
            '  </g>',
        ]

        # Top Badge & Title Group
        svg_parts.append(
            f'  <g transform="translate(0, {title_offset})" opacity="{title_alpha:.2f}">'
        )
        # Badge Pill
        svg_parts.append(
            '    <rect x="120" y="60" width="160" height="32" rx="16" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1.5"/>'
        )
        svg_parts.append(
            f'    <text x="200" y="81" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1.5">{escape_xml(badge)}</text>'
        )

        # Main Title
        clean_title = escape_xml(title[:48])
        svg_parts.append(
            f'    <text x="120" y="130" font-family="Helvetica, Arial, sans-serif" font-size="36" font-weight="bold" fill="#f8fafc">{clean_title}</text>'
        )

        # Subtitle
        if subtitle:
            clean_sub = escape_xml(subtitle[:70])
            svg_parts.append(
                f'    <text x="120" y="162" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#94a3b8">{clean_sub}</text>'
            )
        svg_parts.append('  </g>')

        # Equation Card if present
        card_start_y = 220
        if equation:
            eq_alpha = min(1.0, max(0.0, (progress - 0.15) * 3.0))
            svg_parts.append(
                f'  <g transform="translate(120, {card_start_y})" opacity="{eq_alpha:.2f}">'
                '    <rect width="1040" height="64" rx="10" fill="#1e1b4b" stroke="#818cf8" stroke-width="1.5" filter="url(#cardGlow)"/>'
                f'    <text x="520" y="42" font-family="Helvetica, Arial, sans-serif" font-size="24" font-weight="bold" fill="#c7d2fe" text-anchor="middle" letter-spacing="1">{escape_xml(equation)}</text>'
                '  </g>'
            )
            card_start_y += 85

        # Sequential Key Takeaway Cards
        num_points = min(4, len(points))
        card_height = 68
        gap = 20
        step_window = 0.6 / max(1, num_points)

        for idx, pt in enumerate(points[:num_points]):
            trigger_progress = 0.2 + idx * step_window
            card_progress = max(0.0, min(1.0, (progress - trigger_progress) / max(0.1, step_window)))

            # Card slide & fade
            card_y = card_start_y + idx * (card_height + gap)
            card_alpha = card_progress
            card_dx = int((1.0 - card_progress) * 20)

            border_color = "#38bdf8" if card_progress > 0.8 else "#334155"
            bg_color = "#1e293b" if card_progress > 0.8 else "#172033"

            svg_parts.append(
                f'  <g transform="translate({120 + card_dx}, {card_y})" opacity="{card_alpha:.2f}">'
                f'    <rect width="1040" height="{card_height}" rx="10" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5"/>'
                f'    <circle cx="36" cy="{card_height // 2}" r="14" fill="#0284c7" fill-opacity="0.3" stroke="#38bdf8" stroke-width="1.5"/>'
                f'    <text x="36" y="{card_height // 2 + 5}" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#e0f2fe" text-anchor="middle">{idx+1}</text>'
                f'    <text x="68" y="{card_height // 2 + 6}" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#f1f5f9">{escape_xml(pt[:85])}</text>'
                '  </g>'
            )

        # Bottom subtle brand watermark
        svg_parts.append(
            '  <text x="1160" y="685" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="end">SHIKSHAK ACADEMIC STUDIO</text>'
        )
        svg_parts.append('</svg>')

        return "\n".join(svg_parts)

    return render_svg_frames_to_mp4(
        svg_generator=svg_generator,
        duration_seconds=duration_seconds,
        out_path=out_path,
        fps=24,
    )
