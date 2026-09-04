"""
Shikshak AI — Physics Pack: Circuit Simulation Scene Renderer.

Renders interactive electric circuits:
  - Battery, resistors, switch, lamp, ammeter, and voltmeter components
  - Dynamic flowing electron current particles animated along wire paths
  - Real-time Ohm's Law calculation banner (V = I × R)
  - Voltage, Resistance, and Current metrics
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)
from models import CircuitSimulationPayload


def render_circuit_simulation(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render a circuit_simulation scene to MP4."""
    payload = CircuitSimulationPayload.model_validate(payload_dict)

    voltage = payload.voltage or 12.0
    resistance = payload.resistance or 6.0
    current = payload.current or (voltage / max(0.1, resistance))
    formula = payload.formula or "V = I × R"
    obs = payload.observation or "Current flows clockwise through the closed loop"

    # Circuit loop dimensions: x from 120 to 680, y from 170 to 490
    loop_w = 560
    loop_h = 320
    perimeter = 2 * (loop_w + loop_h)

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Electron speed proportional to current
        speed_factor = max(0.5, min(4.0, current * 0.8))
        base_offset = (elapsed_ms * 0.0006 * speed_factor) % 1.0

        # Animated flowing electron dots around loop
        num_electrons = 16
        electrons_svg = []
        for i in range(num_electrons):
            pos_ratio = (base_offset + i / num_electrons) % 1.0
            dist = pos_ratio * perimeter
            
            # Top wire: (120, 170) -> (680, 170)
            if dist < loop_w:
                ex = 120 + dist
                ey = 170
            # Right wire: (680, 170) -> (680, 490)
            elif dist < loop_w + loop_h:
                ex = 680
                ey = 170 + (dist - loop_w)
            # Bottom wire: (680, 490) -> (120, 490)
            elif dist < 2 * loop_w + loop_h:
                ex = 680 - (dist - (loop_w + loop_h))
                ey = 490
            # Left wire: (120, 490) -> (120, 170)
            else:
                ex = 120
                ey = 490 - (dist - (2 * loop_w + loop_h))

            electrons_svg.append(
                f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="#38bdf8" filter="url(#glow)"/>'
            )

        # Bulb glow pulsing
        bulb_glow_r = int(22 + 6 * math.sin(elapsed_ms * 0.008))

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070d18"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <radialGradient id="bulb_glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="40%" stop-color="#facc15" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#eab308" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Top Badge -->
  <rect x="50" y="30" width="230" height="34" rx="17" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="70" y="52" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">⚡ ELECTRICITY &amp; CIRCUITS</text>

  <!-- Formula Banner Header -->
  <rect x="50" y="76" width="1180" height="54" rx="12" fill="#131e32" stroke="#38bdf8" stroke-width="1.5" filter="url(#glow)"/>
  <text x="640" y="111" fill="#ffffff" font-family="system-ui, sans-serif" font-size="24" font-weight="700" text-anchor="middle" letter-spacing="1">
    OHM&apos;S LAW: <tspan fill="#38bdf8">{escape_xml(formula)}</tspan> (<tspan fill="#fde68a">{voltage}V = {current:.2f}A × {resistance}Ω</tspan>)
  </text>

  <!-- ── Circuit Stage Box (Left Column) ── -->
  <g transform="translate(0, 0)">
    <!-- Main Circuit Loop Wires -->
    <rect x="120" y="170" width="560" height="320" rx="20" fill="none" stroke="#475569" stroke-width="4"/>
    
    <!-- Flowing Current Particles (Electrons) -->
    {"".join(electrons_svg)}

    <!-- 1. Left: Battery / DC Voltage Source -->
    <g transform="translate(120, 330)">
      <rect x="-24" y="-35" width="48" height="70" fill="#0f172a" stroke="#0f172a"/>
      <!-- Long positive plate -->
      <line x1="-12" y1="-22" x2="12" y2="-22" stroke="#38bdf8" stroke-width="4"/>
      <text x="18" y="-18" fill="#38bdf8" font-size="14" font-weight="900">+</text>
      <!-- Short thick negative plate -->
      <line x1="-7" y1="-10" x2="7" y2="-10" stroke="#94a3b8" stroke-width="5"/>
      <text x="18" y="-6" fill="#94a3b8" font-size="14" font-weight="900">-</text>
      <!-- Second pair -->
      <line x1="-12" y1="6" x2="12" y2="6" stroke="#38bdf8" stroke-width="4"/>
      <line x1="-7" y1="18" x2="7" y2="18" stroke="#94a3b8" stroke-width="5"/>
      <text x="-35" y="5" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="end">{voltage}V Battery</text>
    </g>

    <!-- 2. Top: Resistor R -->
    <g transform="translate(400, 170)">
      <rect x="-50" y="-18" width="100" height="36" fill="#0f172a"/>
      <!-- Resistor Zigzag -->
      <path d="M-45 0 L-35 -14 L-20 14 L-5 -14 L10 14 L25 -14 L35 14 L45 0" fill="none" stroke="#f59e0b" stroke-width="3.5"/>
      <text x="0" y="-24" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Resistor R ({resistance}Ω)</text>
    </g>

    <!-- 3. Right: Ammeter & Switch -->
    <g transform="translate(680, 270)">
      <circle cx="0" cy="0" r="22" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
      <text x="0" y="6" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">A</text>
      <text x="32" y="5" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700">{current:.2f} A</text>
    </g>

    <g transform="translate(680, 410)">
      <rect x="-15" y="-20" width="30" height="40" fill="#0f172a"/>
      <!-- Closed Switch contact -->
      <circle cx="0" cy="-14" r="4" fill="#10b981"/>
      <circle cx="0" cy="14" r="4" fill="#10b981"/>
      <line x1="0" y1="-14" x2="0" y2="14" stroke="#10b981" stroke-width="3.5"/>
      <text x="30" y="5" fill="#10b981" font-family="system-ui, sans-serif" font-size="12" font-weight="700">Switch: Closed</text>
    </g>

    <!-- 4. Bottom: Light Bulb -->
    <g transform="translate(400, 490)">
      <!-- Glow halo -->
      <circle cx="0" cy="0" r="{bulb_glow_r}" fill="url(#bulb_glow)"/>
      <circle cx="0" cy="0" r="18" fill="#1e293b" stroke="#eab308" stroke-width="2.5"/>
      <!-- Filament X -->
      <line x1="-10" y1="-10" x2="10" y2="10" stroke="#facc15" stroke-width="2.5"/>
      <line x1="-10" y1="10" x2="10" y2="-10" stroke="#facc15" stroke-width="2.5"/>
      <text x="0" y="36" fill="#facc15" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Lamp / Load</text>
    </g>
  </g>

  <!-- ── Quantitative Meter Cards (Right Column) ── -->
  <g transform="translate(760, 160)">
    <!-- Voltage Card -->
    <g transform="translate(0, 0)">
      <rect width="470" height="95" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="35" cy="47" r="18" fill="#38bdf8"/>
      <text x="35" y="53" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">V</text>
      <text x="70" y="38" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">POTENTIAL DIFFERENCE (VOLTAGE):</text>
      <text x="70" y="68" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="700">{voltage} Volts (V)</text>
    </g>

    <!-- Current Card -->
    <g transform="translate(0, 115)">
      <rect width="470" height="95" rx="14" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
      <circle cx="35" cy="47" r="18" fill="#10b981"/>
      <text x="35" y="53" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">I</text>
      <text x="70" y="38" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">ELECTRIC CURRENT (AMPERES):</text>
      <text x="70" y="68" fill="#34d399" font-family="system-ui, sans-serif" font-size="22" font-weight="700">{current:.2f} Amperes (A = V/R)</text>
    </g>

    <!-- Resistance Card -->
    <g transform="translate(0, 230)">
      <rect width="470" height="95" rx="14" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
      <circle cx="35" cy="47" r="18" fill="#f59e0b"/>
      <text x="35" y="53" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">R</text>
      <text x="70" y="38" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">ELECTRICAL RESISTANCE (OHMS):</text>
      <text x="70" y="68" fill="#fde68a" font-family="system-ui, sans-serif" font-size="22" font-weight="700">{resistance} Ohms (Ω)</text>
    </g>
  </g>

  <!-- ── Observation Takeaway Footer ── -->
  <g transform="translate(50, 565)">
    <rect width="1180" height="85" rx="14" fill="#102538" stroke="#38bdf8" stroke-width="1.8" filter="url(#glow)"/>
    <circle cx="45" cy="42" r="18" fill="#38bdf8"/>
    <text x="45" y="48" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="900" text-anchor="middle">⚡</text>
    <text x="80" y="34" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="0.5">OBSERVATION &amp; TAKEAWAY</text>
    <text x="80" y="62" fill="#ffffff" font-family="system-ui, sans-serif" font-size="17" font-weight="600">
      {escape_xml(obs)}
    </text>
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
