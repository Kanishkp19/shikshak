"""
Shikshak AI — Biology Pack: Cellular Process Scene Renderer.

Renders cellular respiration, photosynthesis, and bio-energetics:
  - Cellular membrane, cytoplasm, and detailed mitochondrion organelle with cristae
  - Reactant molecules (Glucose C₆H₁₂O₆ + 6O₂) entering organelle
  - Dynamic metabolic breakdown & glowing ATP energy molecule bursts
  - Complete biochemical equation banner
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)
from models import BioCellularProcessPayload


def render_bio_cellular_process(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render a bio_cellular_process scene to MP4."""
    payload = BioCellularProcessPayload.model_validate(payload_dict)

    process_name = payload.process_name or "Cellular Respiration"
    organelle = payload.organelle or "Mitochondria"
    equation = payload.overall_equation or "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy (38 ATP)"
    energy_yield = payload.energy_yield or "38 ATP Energy"
    takeaway = payload.key_takeaway or "Glucose breakdown in mitochondria releases cellular ATP energy."

    # Center of mitochondrion organelle at (360, 340)
    mx, my = 360, 340

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Breathing pulse of mitochondria
        pulse = 1.0 + 0.03 * math.sin(elapsed_ms * 0.01)
        
        # Influx progress for reactants (Glucose + O2)
        in_factor = max(0.0, min(1.0, progress / 0.45))
        # Release progress for ATP energy and CO2
        out_factor = max(0.0, min(1.0, (progress - 0.35) / 0.55))

        # Animated ATP energy bursts
        atp_svg = []
        if out_factor > 0.05:
            for i in range(10):
                angle = (i * 0.628) + (elapsed_ms * 0.002)
                dist = 60 + out_factor * 160 * ((i % 3 + 1) / 3.0)
                ax = mx + dist * math.cos(angle)
                ay = my + dist * math.sin(angle)
                alpha = min(1.0, out_factor * 1.5) * (1.0 - 0.3 * (dist / 220))
                atp_svg.append(
                    f'<g transform="translate({ax:.1f}, {ay:.1f})" opacity="{alpha:.2f}">'
                    f'<circle cx="0" cy="0" r="14" fill="#fbbf24" filter="url(#glow)"/>'
                    f'<text x="0" y="4" fill="#0f172a" font-family="system-ui, sans-serif" font-size="10" font-weight="900" text-anchor="middle">ATP</text>'
                    f'</g>'
                )

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#06121e"/>
      <stop offset="100%" stop-color="#0b1e2d"/>
    </linearGradient>
    <radialGradient id="mito_grad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#065f46"/>
      <stop offset="70%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#064e3b"/>
    </radialGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Top Badge -->
  <rect x="50" y="30" width="220" height="34" rx="17" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
  <text x="70" y="52" fill="#10b981" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">🧬 BIOLOGY &amp; LIFE PROCESSES</text>

  <!-- Biochemical Equation Header -->
  <rect x="50" y="76" width="1180" height="54" rx="12" fill="#0f2922" stroke="#10b981" stroke-width="1.5" filter="url(#glow)"/>
  <text x="640" y="111" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="700" text-anchor="middle">
    {escape_xml(process_name).upper()}: <tspan fill="#34d399">{escape_xml(equation)}</tspan>
  </text>

  <!-- ── Cell & Mitochondrion Stage (Left Column) ── -->
  <g transform="translate(50, 150)">
    <!-- Cytoplasm boundary frame -->
    <rect width="620" height="390" rx="20" fill="#0a221f" stroke="#047857" stroke-width="1.5"/>
    <text x="25" y="35" fill="#6ee7b7" font-family="system-ui, sans-serif" font-size="13" font-weight="700">Cell Cytoplasm Matrix</text>

    <!-- Mitochondrion Organelle Outer Capsule -->
    <g transform="translate({mx - 50}, {my - 150}) scale({pulse:.3f})">
      <!-- Outer Membrane -->
      <ellipse cx="0" cy="0" rx="180" ry="110" fill="url(#mito_grad)" stroke="#34d399" stroke-width="3"/>
      <!-- Inner Membrane & Cristae Folds -->
      <path d="M-140 -20 Q-100 -70 -50 -30 Q0 -80 50 -30 Q100 -70 140 -20 Q110 50 50 30 Q0 70 -50 30 Q-110 60 -140 -20 Z" fill="none" stroke="#a7f3d0" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M-90 -50 L-90 10 M-30 -55 L-30 20 M30 -55 L30 20 M90 -50 L90 10" stroke="#6ee7b7" stroke-width="2.5" stroke-dasharray="3 3"/>
      
      <!-- Label -->
      <text x="0" y="5" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle">MITOCHONDRIA</text>
      <text x="0" y="24" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11" font-weight="600" text-anchor="middle">(Powerhouse of the Cell)</text>
    </g>

    <!-- Reactant Inputs (Glucose + Oxygen) Incoming -->
    <g transform="translate(40, 100)" opacity="{min(1.0, in_factor * 1.5):.2f}">
      <rect width="140" height="34" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="70" y="22" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">Glucose (C₆H₁₂O₆) ↓</text>
    </g>

    <g transform="translate(40, 290)" opacity="{min(1.0, in_factor * 1.5):.2f}">
      <rect width="140" height="34" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="70" y="22" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">Oxygen (6O₂) ↑</text>
    </g>

    <!-- ATP Energy Molecule Bursts -->
    {"".join(atp_svg)}
  </g>

  <!-- ── Biochemical Steps & Energy Accounting (Right Column) ── -->
  <g transform="translate(700, 150)">
    <!-- Stage 1: Glycolysis Card -->
    <g transform="translate(0, 0)">
      <rect width="530" height="85" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#38bdf8"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">1</text>
      <text x="70" y="34" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">STAGE 1: GLYCOLYSIS (CYTOPLASM)</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Glucose (6-Carbon) → 2 Pyruvate (3-Carbon) + 2 ATP</text>
    </g>

    <!-- Stage 2: Krebs Cycle Card -->
    <g transform="translate(0, 100)">
      <rect width="530" height="85" rx="14" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#10b981"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">2</text>
      <text x="70" y="34" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">STAGE 2: KREBS CYCLE (MITOCHONDRIAL MATRIX)</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Pyruvate breakdown in presence of O₂ → CO₂ + 2 ATP</text>
    </g>

    <!-- Stage 3: Oxidative Phosphorylation & ATP Yield -->
    <g transform="translate(0, 200)">
      <rect width="530" height="90" rx="14" fill="#1e293b" stroke="#fbbf24" stroke-width="1.8" filter="url(#glow)"/>
      <circle cx="35" cy="45" r="16" fill="#fbbf24"/>
      <text x="35" y="50" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">3</text>
      <text x="70" y="36" fill="#fde68a" font-family="system-ui, sans-serif" font-size="12" font-weight="700">TOTAL ENERGY YIELD:</text>
      <text x="70" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="20" font-weight="800">38 ATP Molecules Produced</text>
    </g>
  </g>

  <!-- ── Conclusion / Biological Principle Banner ── -->
  <g transform="translate(50, 560)">
    <rect width="1180" height="90" rx="14" fill="#0b241c" stroke="#10b981" stroke-width="1.8" filter="url(#glow)"/>
    <circle cx="45" cy="45" r="18" fill="#10b981"/>
    <text x="45" y="51" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="900" text-anchor="middle">🌱</text>
    <text x="80" y="36" fill="#34d399" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="0.5">BIOLOGICAL TAKEAWAY</text>
    <text x="80" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="17" font-weight="600">
      {escape_xml(takeaway)}
    </text>
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
