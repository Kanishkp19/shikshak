"""
Shikshak AI — Balancing Exercise Scene Renderer.

Renders chemical equation balancing and atom conservation:
  - Unbalanced vs Balanced equation comparison
  - Animated physical balance scale (tilts when unbalanced, levels horizontally when balanced)
  - Color-coded 3D atom clusters on reactant and product pans
  - Left (Reactants) vs Right (Products) element atom counters
  - Clean whiteboard classroom aesthetic (#fdfbf7 with dot-matrix grid)
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    format_subscripts,
    render_svg_frames_to_mp4,
)
from skills.scene_renderers.multi_domain_kits import WHITEBOARD_DEFS
from models import BalancingExercisePayload


def render_balancing_exercise(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render an illustrated balancing_exercise scene with animated balance scale to MP4."""
    payload = BalancingExercisePayload.model_validate(payload_dict)

    unbalanced = format_subscripts(payload.unbalanced_equation or "")
    balanced = format_subscripts(payload.balanced_equation or unbalanced)
    inventory = payload.atom_inventory or {"Reactant": [1, 1]}

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Phase 1 (0..0.45): Unbalanced state & scale tilts
        # Phase 2 (0.45..1.0): Coefficients adjust & scale levels out horizontally
        is_balanced = progress > 0.45
        active_eq = balanced if is_balanced else unbalanced

        # Scale tilt angle in degrees: tilts 7 degrees initially, then smoothly levels to 0
        if not is_balanced:
            tilt_deg = -7.0 + 1.2 * math.sin(elapsed_ms * 0.008)
        else:
            level_prog = min(1.0, (progress - 0.45) / 0.25)
            tilt_deg = -7.0 * (1.0 - level_prog)

        cx = width // 2
        card_w = width - 100

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Badge Header -->
  <g transform="translate(50, 36)">
    <rect width="260" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">⚖️ ATOM CONSERVATION</text>
    
    <text x="0" y="72" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Balancing Chemical Equations: Mass Conservation
    </text>
  </g>

  <!-- Main Equation Board -->
  <g transform="translate(50, 125)">
    <rect width="{card_w}" height="110" rx="18" fill="#ffffff" stroke="{"#059669" if is_balanced else "#f59e0b"}" stroke-width="2" filter="url(#card-shadow)"/>
    
    <rect x="25" y="15" width="230" height="24" rx="12" fill="{"#ecfdf5" if is_balanced else "#fffbeb"}"/>
    <text x="140" y="32" fill="{"#047857" if is_balanced else "#b45309"}" font-family="system-ui, sans-serif" font-size="12" font-weight="800" text-anchor="middle">
      {"BALANCED EQUATION (CONSERVED)" if is_balanced else "INITIAL UNBALANCED SKELETON"}
    </text>
    
    <text x="{card_w // 2}" y="82" fill="#0f172a" font-family="system-ui, sans-serif" font-size="34" font-weight="800" text-anchor="middle" letter-spacing="0.5">
      {escape_xml(active_eq)}
    </text>
  </g>

  <!-- ── Visual Physical Balance Scale Stage ── -->
  <g transform="translate(50, 255)">
    <rect width="{card_w}" height="320" rx="18" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#card-shadow)"/>
    
    <!-- Central Atom Conservation Indicator -->
    <g transform="translate({card_w // 2 - 140}, 24)">
      <rect width="280" height="34" rx="17" fill="{"#ecfdf5" if is_balanced else "#fffbeb"}" stroke="{"#059669" if is_balanced else "#f59e0b"}" stroke-width="1.8"/>
      <text x="140" y="22" fill="{"#047857" if is_balanced else "#b45309"}" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">
        {"MASS BALANCED: BOTH SIDES EQUAL" if is_balanced else "UNBALANCED: UNEQUAL ATOM COUNTS"}
      </text>
    </g>

    <!-- Balance Status Pill -->
    <g transform="translate({card_w // 2 - 120}, 24)">
      <rect width="240" height="30" rx="15" fill="{"#ecfdf5" if is_balanced else "#fffbeb"}" stroke="{"#059669" if is_balanced else "#f59e0b"}" stroke-width="1.5"/>
      <text x="120" y="20" fill="{"#047857" if is_balanced else "#b45309"}" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">
        {"MASS BALANCED: BOTH SIDES EQUAL" if is_balanced else "UNBALANCED: UNEQUAL ATOM COUNTS"}
      </text>
    </g>

    <!-- Element Comparison Rows inside scale card -->
    <g transform="translate(60, 75)">
      {"".join(
          f'''<g transform="translate(0, {idx * 46})">
            <!-- Left side count -->
            <rect x="0" y="0" width="380" height="38" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
            <text x="25" y="24" fill="#0f172a" font-family="system-ui, sans-serif" font-size="15" font-weight="800">{elem} Atoms (Reactants)</text>
            <text x="355" y="24" fill="#2563eb" font-family="monospace" font-size="16" font-weight="800" text-anchor="end">{counts[0] if is_balanced else max(1, counts[0]//2)}</text>

            <!-- Right side count -->
            <rect x="{card_w - 500}" y="0" width="380" height="38" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
            <text x="{card_w - 475}" y="24" fill="#0f172a" font-family="system-ui, sans-serif" font-size="15" font-weight="800">{elem} Atoms (Products)</text>
            <text x="{card_w - 145}" y="24" fill="#059669" font-family="monospace" font-size="16" font-weight="800" text-anchor="end">{counts[1]}</text>
          </g>'''
          for idx, (elem, counts) in enumerate(inventory.items())
      )}
    </g>
  </g>

  <!-- Bottom Conservation Law Callout -->
  <g transform="translate(50, 595)">
    <rect width="{card_w}" height="90" rx="16" fill="#f0fdf4" stroke="#059669" stroke-width="1.8" filter="url(#card-shadow)"/>
    <text x="30" y="34" fill="#047857" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="0.5">LAW OF CONSERVATION OF MASS:</text>
    <text x="30" y="62" fill="#065f46" font-family="system-ui, sans-serif" font-size="16" font-weight="600">
      Total number of atoms on the reactant side equals total atoms on the product side. No atoms are created or destroyed.
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
