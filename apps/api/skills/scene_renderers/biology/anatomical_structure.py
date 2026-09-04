"""
Shikshak AI — Biology Pack: Anatomical Structure Scene Renderer.

Renders anatomical organ systems & biological cross-sections:
  - Labeled anatomical organ diagrams (Heart, Nephron, Neuron, Leaf Stomata)
  - Animated blood/nutrient circulation pulse
  - Multi-part callouts with physiological functions
  - Biological principle summary
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)
from models import AnatomicalStructurePayload


def render_anatomical_structure(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render an anatomical_structure scene to MP4."""
    payload = AnatomicalStructurePayload.model_validate(payload_dict)

    name = payload.structure_name or "Human Heart & Double Circulation"
    takeaway = payload.takeaway or "Double circulation separates oxygenated and deoxygenated blood for optimal efficiency."

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Heart beat pulse animation (72 bpm ~ 833ms period)
        heart_beat = 1.0 + 0.05 * math.sin(elapsed_ms * 0.0075)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#080e18"/>
      <stop offset="100%" stop-color="#141824"/>
    </linearGradient>
    <radialGradient id="blood_oxy" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ef4444"/>
      <stop offset="100%" stop-color="#991b1b"/>
    </radialGradient>
    <radialGradient id="blood_deoxy" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#1e3a8a"/>
    </radialGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Top Badge -->
  <rect x="50" y="30" width="220" height="34" rx="17" fill="#1e293b" stroke="#ef4444" stroke-width="1.5"/>
  <text x="70" y="52" fill="#ef4444" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">🫀 ANATOMY &amp; PHYSIOLOGY</text>

  <!-- Structure Title Banner -->
  <rect x="50" y="76" width="1180" height="54" rx="12" fill="#1e1b2e" stroke="#ef4444" stroke-width="1.5" filter="url(#glow)"/>
  <text x="640" y="111" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="700" text-anchor="middle">
    {escape_xml(name).upper()}
  </text>

  <!-- ── Heart Diagram Chamber (Left Column) ── -->
  <g transform="translate(50, 150)">
    <rect width="600" height="390" rx="20" fill="#141624" stroke="#334155" stroke-width="1.5"/>

    <!-- Heart Main Muscle Container with pulsing scale -->
    <g transform="translate(300, 200) scale({heart_beat:.3f})">
      <!-- Right Atrium / Ventricle (Deoxygenated - Blue) -->
      <path d="M-130 -60 Q-40 -120 0 -50 L0 100 Q-80 120 -130 30 Z" fill="url(#blood_deoxy)" stroke="#60a5fa" stroke-width="2.5"/>
      <text x="-60" y="-15" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">RIGHT ATRIUM</text>
      <text x="-60" y="45" fill="#93c5fd" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">RIGHT VENTRICLE</text>

      <!-- Left Atrium / Ventricle (Oxygenated - Red) -->
      <path d="M130 -60 Q40 -120 0 -50 L0 100 Q80 120 130 30 Z" fill="url(#blood_oxy)" stroke="#f87171" stroke-width="2.5"/>
      <text x="60" y="-15" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">LEFT ATRIUM</text>
      <text x="60" y="45" fill="#fca5a5" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">LEFT VENTRICLE</text>

      <!-- Central Septum Dividing Wall -->
      <line x1="0" y1="-50" x2="0" y2="100" stroke="#f1f5f9" stroke-width="5"/>
      <text x="0" y="125" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11" font-weight="700" text-anchor="middle">Septum (Separates Oxygenated &amp; Deoxygenated)</text>
    </g>
  </g>

  <!-- ── Chamber Callout Descriptions (Right Column) ── -->
  <g transform="translate(680, 150)">
    <!-- Right Ventricle -> Lungs -->
    <g transform="translate(0, 0)">
      <rect width="550" height="85" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#38bdf8"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="900" text-anchor="middle">1</text>
      <text x="70" y="34" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">PULMONARY ARTERY (DEOXYGENATED BLOOD):</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Pumps deoxygenated blood from Right Ventricle to Lungs for O₂.</text>
    </g>

    <!-- Left Ventricle -> Body -->
    <g transform="translate(0, 100)">
      <rect width="550" height="85" rx="14" fill="#1e293b" stroke="#ef4444" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#ef4444"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="900" text-anchor="middle">2</text>
      <text x="70" y="34" fill="#f87171" font-family="system-ui, sans-serif" font-size="12" font-weight="700">AORTA (OXYGENATED BLOOD):</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Thick left ventricle walls pump oxygen-rich blood to entire body.</text>
    </g>

    <!-- Valves -->
    <g transform="translate(0, 200)">
      <rect width="550" height="85" rx="14" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
      <circle cx="35" cy="42" r="16" fill="#f59e0b"/>
      <text x="35" y="47" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="900" text-anchor="middle">3</text>
      <text x="70" y="34" fill="#fde68a" font-family="system-ui, sans-serif" font-size="12" font-weight="700">HEART VALVES (TRICUSPID &amp; BICUSPID):</text>
      <text x="70" y="60" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Prevent backflow of blood when ventricles contract.</text>
    </g>
  </g>

  <!-- ── Bottom Summary ── -->
  <g transform="translate(50, 560)">
    <rect width="1180" height="90" rx="14" fill="#1c121e" stroke="#ef4444" stroke-width="1.8" filter="url(#glow)"/>
    <circle cx="45" cy="45" r="18" fill="#ef4444"/>
    <text x="45" y="51" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="900" text-anchor="middle">❤️</text>
    <text x="80" y="36" fill="#f87171" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="0.5">PHYSIOLOGICAL PRINCIPLE</text>
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
