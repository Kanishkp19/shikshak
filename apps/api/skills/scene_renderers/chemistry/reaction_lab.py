"""
Shikshak AI — Reaction Lab Scene Renderer.

Renders laboratory wet-chemistry reactions:
  - Labelled reactant beakers / flasks with distinct solution colours
  - Animated pouring / ionic mixing
  - Observable reaction outcome (e.g. insoluble precipitate forming, colour change, gas bubbles)
  - Formula banner with state symbols (aq, s, g, l)
  - Atom count tags confirming element conservation
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
from models import ReactionLabPayload


def render_reaction_lab(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render a reaction_lab scene to MP4."""
    payload = ReactionLabPayload.model_validate(payload_dict)

    reactants = payload.reactants or []
    products = payload.products or []
    equation = format_subscripts(payload.balanced_equation or "")
    observation = payload.observation or "Reaction proceeds"
    conditions = payload.conditions or "Room temperature"

    r1_name = reactants[0].name if len(reactants) > 0 else "Reactant A"
    r1_form = format_subscripts(reactants[0].formula if len(reactants) > 0 else "A(aq)")
    r1_color = reactants[0].color if len(reactants) > 0 else "#38bdf8"

    r2_name = reactants[1].name if len(reactants) > 1 else "Reactant B"
    r2_form = format_subscripts(reactants[1].formula if len(reactants) > 1 else "B(aq)")
    r2_color = reactants[1].color if len(reactants) > 1 else "#818cf8"

    prod_name = products[0].name if len(products) > 0 else "Products"
    prod_form = format_subscripts(products[0].formula if len(products) > 0 else "")
    prod_color = products[0].color if len(products) > 0 else "#f8fafc"

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Phase 1 (0..0.35): Showing separate reactants
        # Phase 2 (0.35..0.70): Pouring & mixing into reaction vessel
        # Phase 3 (0.70..1.0): Product formed + precipitate / observation highlight + equation revealed
        mix_factor = max(0.0, min(1.0, (progress - 0.25) / 0.35))
        product_factor = max(0.0, min(1.0, (progress - 0.55) / 0.35))

        # Dynamic precipitate particles settling
        particles_svg = []
        if product_factor > 0.05:
            num_particles = int(18 * product_factor)
            for i in range(num_particles):
                px = 640 + 110 * math.sin(i * 1.7) * (1.0 - 0.3 * product_factor)
                settle_y = 440 + 40 * math.cos(i * 2.3) + 15 * (1.0 - product_factor)
                size = 3 + (i % 3)
                alpha = min(1.0, product_factor * 1.5)
                particles_svg.append(
                    f'<circle cx="{px:.1f}" cy="{settle_y:.1f}" r="{size}" fill="{prod_color}" opacity="{alpha:.2f}" filter="url(#glow)"/>'
                )

        # Bubbles / interaction glow
        glow_radius = int(80 + 20 * math.sin(elapsed_ms * 0.005)) if mix_factor > 0.5 else 0

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="r1_grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{r1_color}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{r1_color}" stop-opacity="0.4"/>
    </linearGradient>
    <linearGradient id="r2_grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{r2_color}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{r2_color}" stop-opacity="0.4"/>
    </linearGradient>
    <linearGradient id="flask_glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.05"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Grid overlay -->
  <path d="M0 600 L1280 600 M0 660 L1280 660" stroke="#1e293b" stroke-width="1" opacity="0.6"/>

  <!-- Top Navigation Header / Lab Badge -->
  <rect x="50" y="30" width="180" height="34" rx="17" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="70" y="52" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">🧪 REACTION LAB</text>

  <!-- Condition Badge -->
  <rect x="245" y="30" width="180" height="34" rx="17" fill="#1e293b" stroke="#64748b" stroke-width="1"/>
  <text x="260" y="52" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="13">⚡ {escape_xml(conditions)}</text>

  <!-- Main Equation Header Banner -->
  <rect x="50" y="80" width="1180" height="68" rx="14" fill="#131e32" stroke="#38bdf8" stroke-width="1.5" filter="url(#glow)"/>
  <text x="640" y="124" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="25" font-weight="700" text-anchor="middle" letter-spacing="0.5">
    {escape_xml(equation)}
  </text>

  <!-- ── Left Beaker (Reactant 1) ── -->
  <g transform="translate(180, 200)">
    <!-- Glass Beaker outline -->
    <path d="M0 20 L0 180 Q0 210 30 210 L130 210 Q160 210 160 180 L160 20 Q160 10 150 10 L10 10 Q0 10 0 20 Z" fill="url(#flask_glass)" stroke="#94a3b8" stroke-width="2.5"/>
    <path d="M-6 10 L10 10" stroke="#94a3b8" stroke-width="3"/>
    <!-- Liquid level (drains as mix_factor increases) -->
    <rect x="6" y="{80 + int(120 * mix_factor)}" width="148" height="{int(125 * (1.0 - mix_factor * 0.9))}" rx="8" fill="url(#r1_grad)"/>
    <!-- Tick marks -->
    <line x1="10" y1="80" x2="30" y2="80" stroke="#cbd5e1" stroke-width="1.5" opacity="0.6"/>
    <line x1="10" y1="120" x2="25" y2="120" stroke="#cbd5e1" stroke-width="1.5" opacity="0.6"/>
    <line x1="10" y1="160" x2="30" y2="160" stroke="#cbd5e1" stroke-width="1.5" opacity="0.6"/>
    <!-- Label -->
    <rect x="10" y="225" width="140" height="42" rx="8" fill="#1e293b" stroke="{r1_color}" stroke-width="1.5"/>
    <text x="80" y="244" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">{escape_xml(r1_form)}</text>
    <text x="80" y="260" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">{escape_xml(r1_name[:18])}</text>
  </g>

  <!-- ── Right Beaker (Reactant 2) ── -->
  <g transform="translate(940, 200)">
    <!-- Glass Beaker outline -->
    <path d="M0 20 L0 180 Q0 210 30 210 L130 210 Q160 210 160 180 L160 20 Q160 10 150 10 L10 10 Q0 10 0 20 Z" fill="url(#flask_glass)" stroke="#94a3b8" stroke-width="2.5"/>
    <path d="M166 10 L150 10" stroke="#94a3b8" stroke-width="3"/>
    <!-- Liquid level -->
    <rect x="6" y="{80 + int(120 * mix_factor)}" width="148" height="{int(125 * (1.0 - mix_factor * 0.9))}" rx="8" fill="url(#r2_grad)"/>
    <!-- Tick marks -->
    <line x1="130" y1="80" x2="150" y2="80" stroke="#cbd5e1" stroke-width="1.5" opacity="0.6"/>
    <line x1="135" y1="120" x2="150" y2="120" stroke="#cbd5e1" stroke-width="1.5" opacity="0.6"/>
    <line x1="130" y1="160" x2="150" y2="160" stroke="#cbd5e1" stroke-width="1.5" opacity="0.6"/>
    <!-- Label -->
    <rect x="10" y="225" width="140" height="42" rx="8" fill="#1e293b" stroke="{r2_color}" stroke-width="1.5"/>
    <text x="80" y="244" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">{escape_xml(r2_form)}</text>
    <text x="80" y="260" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">{escape_xml(r2_name[:18])}</text>
  </g>

  <!-- ── Center Reaction Vessel (Conical Flask / Beaker) ── -->
  <g transform="translate(520, 200)">
    <!-- Reaction Flask Body -->
    <path d="M70 0 L170 0 L170 40 L220 180 Q240 220 200 220 L40 220 Q0 220 20 180 L70 40 Z" fill="url(#flask_glass)" stroke="#e2e8f0" stroke-width="2.5"/>
    
    <!-- Mixed Liquid (grows as mix_factor increases) -->
    <path d="M{45 - int(20*mix_factor)} {220 - int(110*mix_factor)} L{195 + int(20*mix_factor)} {220 - int(110*mix_factor)} L215 200 Q225 218 195 218 L45 218 Q15 218 25 200 Z" fill="url(#r1_grad)" opacity="{min(1.0, mix_factor * 1.2)}"/>

    <!-- Precipitate Layer at bottom -->
    <rect x="35" y="{205 - int(20*product_factor)}" width="170" height="{int(20*product_factor)}" rx="5" fill="{prod_color}" opacity="{product_factor*0.95}"/>

    <!-- Precipitate particles -->
    {"".join(particles_svg)}

    <!-- Flask Neck Lip -->
    <rect x="65" y="0" width="110" height="8" rx="4" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>

    <!-- Reaction Label -->
    <rect x="30" y="235" width="180" height="42" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="120" y="254" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">{escape_xml(prod_form or 'Reaction Chamber')}</text>
    <text x="120" y="270" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">{escape_xml(prod_name[:22])}</text>
  </g>

  <!-- ── Observable Outcome Banner ── -->
  <g transform="translate(180, 520)">
    <rect width="920" height="52" rx="12" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
    <circle cx="30" cy="26" r="10" fill="#f59e0b"/>
    <text x="30" y="30" fill="#0f172a" font-size="12" font-weight="900" text-anchor="middle">!</text>
    <text x="55" y="32" fill="#fde68a" font-family="system-ui, sans-serif" font-size="15" font-weight="700">
      OBSERVATION: <tspan fill="#ffffff" font-weight="500">{escape_xml(observation)}</tspan>
    </text>
  </g>

  <!-- ── Element conservation badge footer ── -->
  <g transform="translate(180, 590)">
    <text x="0" y="22" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13" font-weight="600">ATOM BALANCE:</text>
    {"".join(
        f'<rect x="{125 + idx*110}" y="2" width="100" height="28" rx="6" fill="#132038" stroke="#38bdf8" stroke-width="1"/>'
        f'<text x="{175 + idx*110}" y="20" fill="#38bdf8" font-family="monospace" font-size="13" font-weight="700" text-anchor="middle">{elem}: {count}</text>'
        for idx, (elem, count) in enumerate(payload.atom_counts.items())
    )}
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
