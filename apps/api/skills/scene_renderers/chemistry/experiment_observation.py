"""
Shikshak AI — Experiment Observation Scene Renderer.

Renders scientific laboratory demonstrations and observations:
  - Lab apparatus setup (e.g. china dish, burner with dynamic flame, reaction sample)
  - Physical/chemical transformations with localized, perfectly aligned particle physics
  - Action → Observable outcome progression with dynamic phase badges
  - High-contrast conclusion banner
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
from models import ExperimentObservationPayload


def render_experiment_observation(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render an experiment_observation scene to MP4."""
    payload = ExperimentObservationPayload.model_validate(payload_dict)

    setup_desc = payload.setup_description or "Laboratory Demonstration"
    steps = payload.steps or []
    conclusion = payload.conclusion or "Transformation complete"

    active_step = steps[0] if steps else None
    step_action = active_step.action if active_step else "Apply heat / condition"
    step_obs = active_step.observation if active_step else "Reaction proceeds"
    step_cue = active_step.visual_cue if active_step and active_step.visual_cue else step_obs

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Dynamic animated flame
        flame_h = 48 + 12 * math.sin(elapsed_ms * 0.016)
        flame_w = 26 + 5 * math.cos(elapsed_ms * 0.013)

        # Transformation progress (e.g. heating effect turns copper brown -> black or sample reacts)
        transform_factor = max(0.0, min(1.0, (progress - 0.15) / 0.65))

        # Dynamic sample color transition
        # Interpolates from vibrant reactant tone to reacted product tone
        r = int(185 * (1.0 - transform_factor) + 24 * transform_factor)
        g = int(95 * (1.0 - transform_factor) + 28 * transform_factor)
        b = int(20 * (1.0 - transform_factor) + 42 * transform_factor)
        sample_color = f"rgb({r},{g},{b})"

        # Dynamic phase badge based on actual step observation
        if transform_factor < 0.25:
            phase_badge_text = "Initial Setup: Reactants Ready"
            phase_badge_color = "#38bdf8"
        elif transform_factor < 0.75:
            phase_badge_text = f"Reaction: {step_action[:26]}"
            phase_badge_color = "#f59e0b"
        else:
            phase_badge_text = f"Result: {step_cue[:26]}"
            phase_badge_color = "#10b981"

        # Inward reactant particles (e.g. atmospheric oxygen O2 moving directly into the heated dish)
        # Stage coordinates: width 480, height 360. Dish center is exactly at (x=240, y=176).
        particles_svg = []
        if transform_factor > 0.05:
            for i in range(12):
                p_progress = (progress * 2.2 + i * 0.16) % 1.0
                radius_x = 25 + (1.0 - p_progress) * 170
                radius_y = 15 + (1.0 - p_progress) * 110
                angle = (i * 0.52) + (elapsed_ms * 0.001)
                ox = 240 + radius_x * math.cos(angle)
                oy = 176 + radius_y * math.sin(angle)
                
                # Render only inside the stage card boundaries
                if 25 <= ox <= 455 and 45 <= oy <= 340:
                    alpha = min(0.95, transform_factor * 1.5) * (1.0 - 0.3 * (1.0 - p_progress))
                    particles_svg.append(
                        f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="4" fill="#38bdf8" opacity="{alpha:.2f}" filter="url(#glow)"/>'
                        f'<text x="{ox+6:.1f}" y="{oy+4:.1f}" fill="#93c5fd" font-size="10" font-family="system-ui, sans-serif" font-weight="700" opacity="{alpha:.2f}">O₂</text>'
                    )

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#080e18"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <radialGradient id="flame_outer" cx="50%" cy="80%" r="65%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="35%" stop-color="#f97316"/>
      <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="flame_inner" cx="50%" cy="80%" r="45%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="65%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Top Navigation Header / Lab Badge -->
  <rect x="50" y="30" width="220" height="34" rx="17" fill="#1e293b" stroke="#f97316" stroke-width="1.5"/>
  <text x="70" y="52" fill="#f97316" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">🔬 EXPERIMENT LAB</text>

  <!-- Setup Description Title Banner -->
  <rect x="50" y="78" width="1180" height="52" rx="12" fill="#131e32" stroke="#334155" stroke-width="1.2"/>
  <text x="75" y="110" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="17" font-weight="600">
    Setup: <tspan fill="#38bdf8">{escape_xml(setup_desc)}</tspan>
  </text>

  <!-- ── Visual Demonstration Stage (Left Column) ── -->
  <g transform="translate(60, 150)">
    <!-- Stage Card Frame -->
    <rect width="520" height="380" rx="18" fill="#111c2e" stroke="#38bdf8" stroke-width="1.5"/>

    <!-- Bunsen Burner Apparatus -->
    <rect x="225" y="295" width="70" height="15" rx="3" fill="#64748b" stroke="#334155"/>
    <rect x="252" y="230" width="16" height="65" fill="#94a3b8"/>
    <rect x="242" y="220" width="36" height="10" rx="2" fill="#cbd5e1"/>

    <!-- Tripod & Gauze Stand -->
    <line x1="165" y1="200" x2="355" y2="200" stroke="#cbd5e1" stroke-width="4"/>
    <line x1="180" y1="200" x2="145" y2="330" stroke="#64748b" stroke-width="3"/>
    <line x1="340" y1="200" x2="375" y2="330" stroke="#64748b" stroke-width="3"/>

    <!-- Dynamic Animated Burner Flame -->
    <ellipse cx="260" cy="{215 - flame_h/2}" rx="{flame_w}" ry="{flame_h}" fill="url(#flame_outer)" filter="url(#glow)"/>
    <ellipse cx="260" cy="{215 - flame_h/3}" rx="{flame_w*0.5}" ry="{flame_h*0.6}" fill="url(#flame_inner)"/>

    <!-- China Dish / Reaction Sample on Gauze -->
    <path d="M190 196 Q260 234 330 196 Z" fill="#f8fafc" stroke="#94a3b8" stroke-width="2.5"/>
    <!-- Reacting Sample with smooth color transition -->
    <path d="M202 198 Q260 224 318 198 Z" fill="{sample_color}" stroke="{sample_color}" stroke-width="2"/>

    <!-- Localized Inward Oxygen (O2) Molecules -->
    {"".join(particles_svg)}

    <!-- Dynamic State Badge -->
    <rect x="25" y="20" width="280" height="34" rx="8" fill="#1e293b" stroke="{phase_badge_color}" stroke-width="1.5"/>
    <circle cx="42" cy="37" r="5" fill="{phase_badge_color}"/>
    <text x="56" y="42" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="12" font-weight="700">
      {escape_xml(phase_badge_text)}
    </text>
  </g>

  <!-- ── Step-by-Step Observation Cards (Right Column) ── -->
  <g transform="translate(610, 150)">
    {"".join(
        f'''<g transform="translate(0, {idx * 125})">
          <rect width="610" height="110" rx="16" fill="#1e293b" stroke="{"#38bdf8" if progress > (idx*0.35) else "#334155"}" stroke-width="1.5"/>
          <circle cx="35" cy="35" r="15" fill="#38bdf8"/>
          <text x="35" y="40" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">{idx+1}</text>
          
          <text x="68" y="36" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">ACTION:</text>
          <text x="135" y="36" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="15" font-weight="600">{escape_xml(s.action)}</text>
          
          <text x="68" y="74" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="12" font-weight="700">OBSERVATION:</text>
          <text x="180" y="74" fill="#fde68a" font-family="system-ui, sans-serif" font-size="15" font-weight="600">{escape_xml(s.observation)}</text>
        </g>'''
        for idx, s in enumerate(steps[:2])
    )}
  </g>

  <!-- ── Conclusion Banner (Bottom Full-Width) ── -->
  <g transform="translate(50, 560)">
    <rect width="1180" height="92" rx="16" fill="#112438" stroke="#10b981" stroke-width="2" filter="url(#glow)"/>
    <circle cx="48" cy="46" r="18" fill="#10b981"/>
    <text x="48" y="52" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="900" text-anchor="middle">✓</text>
    <text x="85" y="38" fill="#6ee7b7" font-family="system-ui, sans-serif" font-size="14" font-weight="700" letter-spacing="0.5">CONCLUSION / SCIENTIFIC PRINCIPLE</text>
    <text x="85" y="68" fill="#ffffff" font-family="system-ui, sans-serif" font-size="18" font-weight="600">
      {escape_xml(conclusion)}
    </text>
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
