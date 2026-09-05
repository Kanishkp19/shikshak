"""
Shikshak AI — Classroom Whiteboard Generic Explainer Scene Renderer.

Renders high-contrast, illustrated whiteboard classroom animations:
  - Clean, warm classroom whiteboard aesthetic (#fdfbf7 with subtle grid dots)
  - Automatic routing to specialized multi-domain kits (Physics, Chemistry, Biology, ML, Math)
  - Two-Column Educational Stage:
    * Left: Large, interactive concept illustration stage with active orbital particle aura
    * Right: Progressive whiteboard observation cards with active marker highlights
  - Native studio stage resolution support (980x720 / 1280x720)
"""
from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    format_subscripts,
    render_svg_frames_to_mp4,
    sanitize_display_text,
)
from skills.scene_renderers.icon_library import (
    ICONS,
    render_icon_element,
    resolve_semantic_icon,
)
from skills.scene_renderers.multi_domain_kits import (
    WHITEBOARD_DEFS,
    detect_multi_domain_scene,
)
from models import GenericExplainerPayload


# Curated palette for observation badges and highlights
MARKER_THEMES = [
    {"stroke": "#2563eb", "badge_bg": "#eff6ff", "badge_text": "#1d4ed8", "tag": "OBSERVATION 01"},
    {"stroke": "#d97706", "badge_bg": "#fffbeb", "badge_text": "#b45309", "tag": "OBSERVATION 02"},
    {"stroke": "#7c3aed", "badge_bg": "#faf5ff", "badge_text": "#6d28d9", "tag": "OBSERVATION 03"},
    {"stroke": "#059669", "badge_bg": "#f0fdf4", "badge_text": "#047857", "tag": "OBSERVATION 04"},
]


def render_generic_explainer(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render an illustrated, whiteboard-classroom explainer scene to MP4."""
    payload = GenericExplainerPayload.model_validate(payload_dict)

    title = sanitize_display_text(payload.title) or "Key Concept Overview"
    raw_points = [sanitize_display_text(pt) for pt in (payload.key_points or []) if sanitize_display_text(pt)]
    key_points = raw_points or ["Core pedagogical takeaway for this concept."]
    raw_eq = sanitize_display_text(payload.equation)
    equation = format_subscripts(raw_eq) if raw_eq else ""

    # Check if this scene matches a dedicated multi-domain ready-made kit
    specialized_kit = detect_multi_domain_scene(
        concept=title,
        narration=narration_text,
        key_points=key_points,
    )
    if specialized_kit is not None:
        return specialized_kit(
            concept=title,
            narration_text=narration_text,
            duration_seconds=duration_seconds,
            out_path=out_path,
            width=width,
            height=height,
        )

    # Primary concept illustration icon
    primary_icon = resolve_semantic_icon(f"{title} {' '.join(key_points)} {narration_text}")

    # Resolve vector iconography for each observation point
    resolved_cards = []
    for idx, pt in enumerate(key_points[:3]):
        icon_info = resolve_semantic_icon(pt)
        theme = MARKER_THEMES[idx % len(MARKER_THEMES)]
        
        pt_clean = pt.strip()
        parts = pt_clean.split(" - ") if " - " in pt_clean else pt_clean.split(": ")
        main_text = parts[0].strip()
        sub_text = parts[1].strip() if len(parts) > 1 else ""

        resolved_cards.append({
            "idx": idx,
            "main_text": main_text,
            "sub_text": sub_text,
            "icon": icon_info,
            "theme": theme,
        })

    # Stage Geometry: Left Illustration Stage & Right Observation Column
    left_w = 460
    right_x = 540
    right_w = width - right_x - 50

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        num_cards = max(1, len(resolved_cards))
        active_card_idx = min(num_cards - 1, int(progress * num_cards))

        # Dynamic orbital particles around left illustration
        aura_r = 135 + 8 * math.sin(elapsed_ms * 0.006)
        orbit_ang = elapsed_ms * 0.0025
        p1_x = 230 + aura_r * math.cos(orbit_ang)
        p1_y = 190 + aura_r * math.sin(orbit_ang)
        p2_x = 230 + aura_r * math.cos(orbit_ang + math.pi)
        p2_y = 190 + aura_r * math.sin(orbit_ang + math.pi)

        # Right-side observation cards
        cards_svg = []
        card_start_y = 150 if not equation else 205
        card_gap = 145 if len(resolved_cards) <= 2 else 115

        for card in resolved_cards:
            idx = card["idx"]
            theme = card["theme"]
            icon = card["icon"]
            
            card_thresh = idx * (0.85 / num_cards)
            card_progress = max(0.0, min(1.0, (progress - card_thresh) / 0.15))
            
            offset_y = (1.0 - card_progress) * 16
            opacity = min(1.0, card_progress * 1.25)
            
            is_active = (idx == active_card_idx)
            border_color = theme["stroke"] if is_active else "#e2e8f0"
            border_width = "2.5" if is_active else "1.5"
            card_bg = "#ffffff"

            cy = card_start_y + idx * card_gap + offset_y
            category_label = card["sub_text"] or icon["label"]

            cards_svg.append(f"""
    <!-- Observation Card {idx+1} -->
    <g transform="translate({right_x}, {cy:.1f})" opacity="{opacity:.2f}" filter="url(#card-shadow)">
      <rect width="{right_w}" height="102" rx="16" fill="{card_bg}" stroke="{border_color}" stroke-width="{border_width}"/>
      
      <!-- Left Icon Circle Badge -->
      <circle cx="52" cy="51" r="30" fill="{icon['bg_tint']}" stroke="{icon['color']}" stroke-width="1.8"/>
      {render_icon_element(icon, 52, 51, size=34, color=icon['color'])}
      
      <!-- Step Tag Badge -->
      <rect x="96" y="20" width="120" height="22" rx="11" fill="{theme['badge_bg']}"/>
      <text x="156" y="35" fill="{theme['badge_text']}" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">
        {theme['tag']}
      </text>

      <!-- Category Label Pill (Right) -->
      <rect x="{right_w - 170}" y="20" width="150" height="22" rx="11" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
      <text x="{right_w - 95}" y="35" fill="#475569" font-family="system-ui, sans-serif" font-size="11" font-weight="700" text-anchor="middle">
        {escape_xml(category_label[:20])}
      </text>

      <!-- Main Concept Text -->
      <text x="98" y="72" fill="#0f172a" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="700">
        {escape_xml(card['main_text'][:48])}
      </text>
    </g>
""")

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Whiteboard Header -->
  <g transform="translate(50, 36)">
    <rect width="250" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="800" letter-spacing="1">📝 CLASSROOM OBSERVATION</text>
    
    <text x="0" y="72" fill="#0f172a" font-family="system-ui, -apple-system, sans-serif" font-size="28" font-weight="800">
      {escape_xml(title)}
    </text>
    <text x="0" y="100" fill="#475569" font-family="system-ui, sans-serif" font-size="15" font-weight="500">
      Key pedagogical observations and conceptual takeaways for this lesson.
    </text>
  </g>

  <!-- Optional Formula Banner (if present) -->
  {"".join([
      f'''<g transform="translate({right_x}, 145)">
        <rect width="{right_w}" height="48" rx="12" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" filter="url(#card-shadow)"/>
        <text x="{right_w // 2}" y="31" fill="#1d4ed8" font-family="system-ui, monospace" font-size="18" font-weight="800" text-anchor="middle">
          {escape_xml(equation)}
        </text>
      </g>'''
      if equation else ""
  ])}

  <!-- ── Left Column: Prominent Animated Concept Illustration Stage ── -->
  <g transform="translate(50, 150)">
    <rect width="{left_w}" height="480" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <!-- Stage Header Badge -->
    <rect x="25" y="20" width="180" height="26" rx="13" fill="{primary_icon['bg_tint']}"/>
    <text x="115" y="37" fill="{primary_icon['color']}" font-family="system-ui, sans-serif" font-size="12" font-weight="800" text-anchor="middle">
      VISUAL DEMONSTRATION
    </text>

    <!-- Concentric Orbital Glow Rings -->
    <circle cx="230" cy="190" r="{aura_r:.1f}" fill="none" stroke="{primary_icon['color']}" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.45"/>
    <circle cx="230" cy="190" r="160" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 3" opacity="0.4"/>
    
    <!-- Orbiting Energy Dots -->
    <circle cx="{p1_x:.1f}" cy="{p1_y:.1f}" r="5" fill="{primary_icon['color']}"/>
    <circle cx="{p2_x:.1f}" cy="{p2_y:.1f}" r="4" fill="#64748b"/>

    <!-- Central Illustrated Visual Badge -->
    <circle cx="230" cy="190" r="75" fill="{primary_icon['bg_tint']}" stroke="{primary_icon['color']}" stroke-width="2.5" filter="url(#card-shadow)"/>
    {render_icon_element(primary_icon, 230, 190, size=84, color=primary_icon['color'])}

    <!-- Bottom Illustration Title & Takeaway Badge -->
    <g transform="translate(25, 335)">
      <rect width="{left_w - 50}" height="115" rx="14" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>
      <text x="{(left_w - 50) // 2}" y="36" fill="#0f172a" font-family="system-ui, sans-serif" font-size="17" font-weight="800" text-anchor="middle">
        {escape_xml(primary_icon['label'].upper())}
      </text>
      <text x="{(left_w - 50) // 2}" y="65" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="600" text-anchor="middle">
        Active pedagogical focus for this concept
      </text>
      <text x="{(left_w - 50) // 2}" y="92" fill="#2563eb" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">
        Interactive Whiteboard Demonstration
      </text>
    </g>
  </g>

  <!-- ── Right Column: Observation Cards ── -->
  {"".join(cards_svg)}

  <!-- Bottom Classroom Footer Badge -->
  <g transform="translate(50, 665)">
    <line x1="0" y1="0" x2="{width - 100}" y2="0" stroke="#e2e8f0" stroke-width="1.5"/>
    <text x="0" y="22" fill="#64748b" font-family="system-ui, sans-serif" font-size="12" font-weight="600">
      SHIKSHAK AI • INTERACTIVE WHITEBOARD LESSON
    </text>
    <text x="{width - 100}" y="22" fill="#2563eb" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="end">
      STEP-BY-STEP CONCEPTUAL BREAKDOWN
    </text>
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
        width=width,
        height=height,
    )
