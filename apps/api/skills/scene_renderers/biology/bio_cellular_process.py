"""
Shikshak AI — Biology Pack: Cellular Process Scene Renderer.

Renders dynamic, high-fidelity biological and metabolic pathways:
  - Chloroplast & Photosynthesis: Thylakoid grana stacks, chlorophyll light absorption,
    water photolysis, Calvin cycle CO₂ fixation, and glucose/O₂ synthesis.
  - Mitochondria & Respiration: Dual membrane with cristae, glycolysis, Krebs cycle,
    and oxidative phosphorylation generating ATP energy.
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

    process_name = payload.process_name or "Photosynthesis"
    organelle = payload.organelle or "Chloroplast"
    equation = payload.overall_equation or "6CO₂ + 6H₂O + Sunlight → C₆H₁₂O₆ + 6O₂"
    energy_yield = payload.energy_yield or "Chemical Energy (Glucose)"
    takeaway = payload.key_takeaway or "Chlorophyll captures solar energy to convert CO₂ and water into glucose and oxygen."

    p_lower = (process_name + " " + organelle).lower()
    is_chloroplast = any(k in p_lower for k in ("chloro", "photo", "plant", "leaf", "stroma", "thylakoid", "calvin"))

    inputs = payload.inputs if payload.inputs else (
        ["Carbon Dioxide (6CO₂)", "Water (6H₂O)"] if is_chloroplast else ["Glucose (C₆H₁₂O₆)", "Oxygen (6O₂)"]
    )
    in_1 = inputs[0] if len(inputs) > 0 else "Reactant 1"
    in_2 = inputs[1] if len(inputs) > 1 else "Reactant 2"

    # Center of organelle at (360, 340)
    mx, my = 360, 340

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        pulse = 1.0 + 0.03 * math.sin(elapsed_ms * 0.01)
        in_factor = max(0.0, min(1.0, progress / 0.45))
        out_factor = max(0.0, min(1.0, (progress - 0.35) / 0.55))

        # Animated product bursts
        burst_svg = []
        if out_factor > 0.05:
            num_particles = 8
            for i in range(num_particles):
                angle = (i * (2 * math.pi / num_particles)) + (elapsed_ms * 0.002)
                dist = 60 + out_factor * 160 * ((i % 3 + 1) / 3.0)
                ax = mx + dist * math.cos(angle)
                ay = my + dist * math.sin(angle)
                alpha = min(1.0, out_factor * 1.5) * (1.0 - 0.3 * (dist / 220))
                
                if is_chloroplast:
                    label = "O₂" if i % 2 == 0 else "C₆H₁₂O₆"
                    color = "#34d399" if i % 2 == 0 else "#fbbf24"
                    burst_svg.append(
                        f'<g transform="translate({ax:.1f}, {ay:.1f})" opacity="{alpha:.2f}">'
                        f'<circle cx="0" cy="0" r="15" fill="{color}" filter="url(#glow)"/>'
                        f'<text x="0" y="4" fill="#0f172a" font-family="system-ui, sans-serif" font-size="9" font-weight="900" text-anchor="middle">{label}</text>'
                        f'</g>'
                    )
                else:
                    burst_svg.append(
                        f'<g transform="translate({ax:.1f}, {ay:.1f})" opacity="{alpha:.2f}">'
                        f'<circle cx="0" cy="0" r="14" fill="#fbbf24" filter="url(#glow)"/>'
                        f'<text x="0" y="4" fill="#0f172a" font-family="system-ui, sans-serif" font-size="10" font-weight="900" text-anchor="middle">ATP</text>'
                        f'</g>'
                    )

        if is_chloroplast:
            # Chloroplast organelle internal structures (Grana stacks and thylakoids)
            organelle_svg = f"""
            <!-- Chloroplast Outer Double Membrane -->
            <ellipse cx="0" cy="0" rx="190" ry="115" fill="url(#chloro_grad)" stroke="#10b981" stroke-width="3"/>
            <ellipse cx="0" cy="0" rx="175" ry="102" fill="none" stroke="#059669" stroke-width="1.5" stroke-dasharray="6 3"/>

            <!-- Sunlight Photon Influx Stream -->
            <g transform="translate(-160, -110)" opacity="0.9">
              <line x1="-30" y1="-30" x2="60" y2="40" stroke="#facc15" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>
              <line x1="-10" y1="-40" x2="80" y2="30" stroke="#fef08a" stroke-width="2" stroke-linecap="round"/>
              <text x="-40" y="-35" fill="#facc15" font-family="system-ui, sans-serif" font-size="12" font-weight="800">Sunlight (hν) ⚡</text>
            </g>

            <!-- Grana Thylakoid Stacks -->
            <!-- Stack 1 (Left) -->
            <g transform="translate(-80, -35)">
              <rect x="-24" y="-8" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-24" y="6" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-24" y="20" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-24" y="34" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
            </g>
            <!-- Stack 2 (Center) -->
            <g transform="translate(0, -45)">
              <rect x="-26" y="-8" width="52" height="13" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-26" y="8" width="52" height="13" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-26" y="24" width="52" height="13" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-26" y="40" width="52" height="13" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
            </g>
            <!-- Stack 3 (Right) -->
            <g transform="translate(80, -35)">
              <rect x="-24" y="-8" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-24" y="6" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-24" y="20" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
              <rect x="-24" y="34" width="48" height="12" rx="4" fill="#047857" stroke="#34d399" stroke-width="1.5"/>
            </g>
            <!-- Stroma Lamellae Links -->
            <line x1="-56" y1="-2" x2="-26" y2="-2" stroke="#10b981" stroke-width="2.5"/>
            <line x1="26" y1="14" x2="56" y2="14" stroke="#10b981" stroke-width="2.5"/>

            <text x="0" y="70" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">{escape_xml(organelle).upper()}</text>
            <text x="0" y="88" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11" font-weight="600" text-anchor="middle">({escape_xml(process_name)} Matrix)</text>
            """
        else:
            # Mitochondrion organelle with cristae
            organelle_svg = f"""
            <ellipse cx="0" cy="0" rx="180" ry="110" fill="url(#mito_grad)" stroke="#34d399" stroke-width="3"/>
            <path d="M-140 -20 Q-100 -70 -50 -30 Q0 -80 50 -30 Q100 -70 140 -20 Q110 50 50 30 Q0 70 -50 30 Q-110 60 -140 -20 Z" fill="none" stroke="#a7f3d0" stroke-width="3.5" stroke-linecap="round"/>
            <path d="M-90 -50 L-90 10 M-30 -55 L-30 20 M30 -55 L30 20 M90 -50 L90 10" stroke="#6ee7b7" stroke-width="2.5" stroke-dasharray="3 3"/>
            <text x="0" y="5" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle">{escape_xml(organelle).upper()}</text>
            <text x="0" y="24" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11" font-weight="600" text-anchor="middle">({escape_xml(process_name)} Matrix)</text>
            """

        in_str = ", ".join(inputs) if inputs else "Substrates & Reactants"
        out_str = ", ".join(payload.outputs) if payload.outputs else f"Metabolic Products ({energy_yield})"

        stage_1_title = "STAGE 1: SUBSTRATE INTAKE & BINDING"
        stage_1_sub = f"Import of {in_str} into {organelle}"
        stage_2_title = f"STAGE 2: {process_name.upper()} CATALYSIS"
        stage_2_sub = f"Biochemical transformation and energy transduction in {organelle}"
        stage_3_title = "STAGE 3: METABOLIC YIELD & PRODUCTS"
        stage_3_sub = f"Release and transport of {out_str}"

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#04121a"/>
      <stop offset="100%" stop-color="#08222c"/>
    </linearGradient>
    <radialGradient id="chloro_grad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#064e3b"/>
      <stop offset="65%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#065f46"/>
    </radialGradient>
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

  <!-- ── Cell & Organelle Stage (Left Column) ── -->
  <g transform="translate(50, 150)">
    <!-- Cytoplasm boundary frame -->
    <rect width="620" height="390" rx="20" fill="#0a221f" stroke="#047857" stroke-width="1.5"/>
    <text x="25" y="35" fill="#6ee7b7" font-family="system-ui, sans-serif" font-size="13" font-weight="700">Cellular Cytoplasm &amp; Organelle</text>

    <!-- Organelle Outer Capsule -->
    <g transform="translate({mx - 50}, {my - 150}) scale({pulse:.3f})">
      {organelle_svg}
    </g>

    <!-- Reactant Inputs Incoming -->
    <g transform="translate(30, 95)" opacity="{min(1.0, in_factor * 1.5):.2f}">
      <rect width="160" height="34" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="80" y="22" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">{escape_xml(in_1)} ↓</text>
    </g>

    <g transform="translate(30, 295)" opacity="{min(1.0, in_factor * 1.5):.2f}">
      <rect width="160" height="34" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="80" y="22" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">{escape_xml(in_2)} ↑</text>
    </g>

    <!-- Product Molecule Bursts -->
    {"".join(burst_svg)}
  </g>

  <!-- ── Biochemical Steps & Energy Accounting (Right Column) ── -->
  <g transform="translate(700, 150)">
    <!-- Stage 1 Card -->
    <g transform="translate(0, 0)">
      <rect width="530" height="85" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#38bdf8"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">1</text>
      <text x="70" y="34" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">{escape_xml(stage_1_title)}</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13" font-weight="600">{escape_xml(stage_1_sub)}</text>
    </g>

    <!-- Stage 2 Card -->
    <g transform="translate(0, 100)">
      <rect width="530" height="85" rx="14" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#10b981"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">2</text>
      <text x="70" y="34" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">{escape_xml(stage_2_title)}</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13" font-weight="600">{escape_xml(stage_2_sub)}</text>
    </g>

    <!-- Stage 3 Card -->
    <g transform="translate(0, 200)">
      <rect width="530" height="90" rx="14" fill="#1e293b" stroke="#fbbf24" stroke-width="1.8" filter="url(#glow)"/>
      <circle cx="35" cy="45" r="16" fill="#fbbf24"/>
      <text x="35" y="50" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">3</text>
      <text x="70" y="36" fill="#fde68a" font-family="system-ui, sans-serif" font-size="12" font-weight="700">{escape_xml(stage_3_title)}</text>
      <text x="70" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="19" font-weight="800">{escape_xml(stage_3_sub)}</text>
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
