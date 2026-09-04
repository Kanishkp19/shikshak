"""
Shikshak AI — Physics Pack: Spherical Mirror Curvature & Formula Explainer.

Lively, dynamic educational animation replacing static bullet-point slides:
  - Animated optical bench with glowing concave mirror curvature arc
  - Sweeping radius of curvature R from center C to pole P
  - Dynamic dimension caliper bisecting R into two equal halves demonstrating f = R / 2
  - Active light ray reflection striking curved reflective surface and focusing at F
  - Color-coded physical dimension brackets (u in amber, v in emerald, f in cyan)
    kinetically linked to the Mirror Formula (1/v + 1/u = 1/f)
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)


def render_spherical_mirror_optics(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic, lively spherical mirror curvature and formula animation to MP4."""
    title = payload_dict.get("title") or "Spherical Mirror Geometry & Formula"
    formula = payload_dict.get("formula") or "1/v + 1/u = 1/f"
    radius_val = payload_dict.get("radius", "20 cm")
    focal_val = payload_dict.get("focal_length", "10 cm")
    mirror_type = payload_dict.get("mirror_type", "concave")

    # Bench coordinates
    # Pole P at (780, 320), Center of Curvature C at (380, 320), Focus F at (580, 320)
    px, py = 780, 320
    cx, cy = 380, 320
    fx, fy = 580, 320
    r_len = px - cx  # 400 px
    f_len = px - fx  # 200 px

    # Object at x = 260 (beyond C), Image formed at x = 460 (between C and F)
    obj_x = 240
    obj_h = 85
    img_x = 480
    img_h = 50

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Animation timeline phases:
        # Phase 1: Curvature & Radius sweep (0.00 -> 0.35)
        # Phase 2: Caliper bisection proving f = R/2 (0.30 -> 0.65)
        # Phase 3: Active ray reflection & formula linking (0.60 -> 1.00)
        t_curv = max(0.0, min(1.0, progress / 0.32))
        t_caliper = max(0.0, min(1.0, (progress - 0.28) / 0.34))
        t_ray = max(0.0, min(1.0, (progress - 0.55) / 0.40))
        t_formula = max(0.0, min(1.0, (progress - 0.70) / 0.28))

        # 1. Radius arc sweep: angle sweeps from 0 to 45 degrees
        arc_angle_deg = 42.0 * t_curv
        rad_sweep_x = cx + r_len * math.cos(math.radians(-arc_angle_deg * 0.7))
        rad_sweep_y = cy + r_len * math.sin(math.radians(-arc_angle_deg * 0.7))

        # 2. Dynamic caliper bisection (glides from C to F and reveals midpoint)
        caliper_x = cx + (fx - cx) * t_caliper
        caliper_pulse = int(12 + 3 * math.sin(elapsed_ms * 0.012))

        # 3. Ray path:
        # Parallel ray from Object tip (240, 320 - 85 = 235) to Mirror surface (760, 235)
        # Mirror arc at y=235 has x approx 762
        mirror_hit_x = 762
        mirror_hit_y = 235

        ray_p1 = min(1.0, t_ray * 2.0)
        curr_ray1_x = obj_x + (mirror_hit_x - obj_x) * ray_p1
        curr_ray1_y = mirror_hit_y

        # Reflected ray: from (762, 235) passing through F (580, 320) to (img_x, py + img_h)
        # Slope = (320 - 235) / (580 - 762) = 85 / -182 = -0.467
        ray_p2 = max(0.0, (t_ray - 0.5) * 2.0)
        refl_end_x = 420
        refl_end_y = 235 + int((refl_end_x - mirror_hit_x) * -0.467)
        curr_refl_x = mirror_hit_x + (refl_end_x - mirror_hit_x) * ray_p2
        curr_refl_y = mirror_hit_y + (refl_end_y - mirror_hit_y) * ray_p2

        # Glowing traveling photon pulse along ray
        photon_phase = (elapsed_ms * 0.003) % 1.0
        photon_x = curr_ray1_x if ray_p1 < 1.0 else curr_refl_x
        photon_y = curr_ray1_y if ray_p1 < 1.0 else curr_refl_y

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="deep_bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070d18"/>
      <stop offset="60%" stop-color="#0b1528"/>
      <stop offset="100%" stop-color="#0f1f38"/>
    </linearGradient>
    <linearGradient id="mirror_silver" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.8"/>
      <stop offset="35%" stop-color="#e2e8f0" stop-opacity="0.95"/>
      <stop offset="70%" stop-color="#94a3b8" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.7"/>
    </linearGradient>
    <linearGradient id="caliper_glow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#67e8f9"/>
      <stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
    <filter id="aura" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Deep Academic Canvas Background -->
  <rect width="{width}" height="{height}" fill="url(#deep_bg)"/>

  <!-- Top Pedagogical Badge -->
  <rect x="50" y="24" width="220" height="32" rx="16" fill="#13233c" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="70" y="45" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="800" letter-spacing="1">GEOMETRIC OPTICS</text>

  <!-- ── Dynamic Dual Formula Badges ── -->
  <!-- Left Pill: Radius / Focal Proof f = R / 2 -->
  <g transform="translate(50, 66)">
    <rect width="550" height="52" rx="12" fill="#101d32" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="0.8">FOCAL RELATION:</text>
    <text x="175" y="34" fill="#38bdf8" font-family="system-ui, monospace, sans-serif" font-size="21" font-weight="900">f = R / 2</text>
    <rect x="300" y="14" width="225" height="24" rx="12" fill="#082f49"/>
    <text x="315" y="31" fill="#7dd3fc" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Focal length is exactly half radius</text>
  </g>

  <!-- Right Pill: Spherical Mirror Formula -->
  <g transform="translate(620, 66)">
    <rect width="610" height="52" rx="12" fill="#101d32" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="0.8">MIRROR FORMULA:</text>
    <text x="185" y="34" fill="#fde68a" font-family="system-ui, monospace, sans-serif" font-size="21" font-weight="900">1/v + 1/u = 1/f</text>
    <circle cx="430" cy="26" r="4" fill="#10b981"/>
    <text x="444" y="30" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Cartesian Sign Conventions Apply</text>
  </g>

  <!-- ── Main Optical Bench Simulation Card (Leaves Bottom-Right Clear for PIP) ── -->
  <g transform="translate(50, 136)">
    <rect width="890" height="408" rx="18" fill="#0b172a" stroke="#1e293b" stroke-width="1.8"/>

    <!-- Optical Axis -->
    <line x1="40" y1="{py - 136}" x2="840" y2="{py - 136}" stroke="#475569" stroke-width="2" stroke-dasharray="6 4"/>
    <text x="40" y="{py - 146}" fill="#64748b" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Principal Axis</text>

    <!-- Center of Curvature C -->
    <circle cx="{cx}" cy="{py - 136}" r="6" fill="#38bdf8"/>
    <text x="{cx}" y="{py - 136 - 16}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">C</text>
    <text x="{cx}" y="{py - 136 + 22}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10" font-weight="700" text-anchor="middle">(Center)</text>

    <!-- Principal Focus F -->
    <circle cx="{fx}" cy="{py - 136}" r="6" fill="#67e8f9" filter="url(#aura)"/>
    <text x="{fx}" y="{py - 136 - 16}" fill="#67e8f9" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">F</text>
    <text x="{fx}" y="{py - 136 + 22}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10" font-weight="700" text-anchor="middle">(Focus)</text>

    <!-- Pole P -->
    <circle cx="{px}" cy="{py - 136}" r="6" fill="#f8fafc"/>
    <text x="{px - 14}" y="{py - 136 - 16}" fill="#ffffff" font-family="system-ui, sans-serif" font-size="14" font-weight="900">P</text>

    <!-- ── Concave Spherical Mirror Reflective Arc ── -->
    <!-- Arc centered at C(380) with radius R=400 to P(780) -->
    <path d="M 720 {py - 136 - 150} A 400 400 0 0 1 780 {py - 136} A 400 400 0 0 1 720 {py - 136 + 150}"
          fill="none" stroke="url(#mirror_silver)" stroke-width="8" stroke-linecap="round" filter="url(#aura)"/>
    <!-- Opaque back coating hatch lines -->
    {"".join(f'<line x1="{720 + i*3}" y1="{py - 136 - 150 + i*16}" x2="{732 + i*3}" y2="{py - 136 - 144 + i*16}" stroke="#64748b" stroke-width="1.5"/>' for i in range(19))}

    <!-- ── Sweeping Radius Indicator R (Confined strictly to Mirror Aperture) ── -->
    <line x1="{cx}" y1="{py - 136}" x2="{cx + r_len * t_curv}" y2="{py - 136}" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="4 2"/>
    <!-- Animated Radius Arc Sector (clamped within mirror aperture) -->
    <path d="M {cx} {py - 136} L {min(770, rad_sweep_x)} {max(py - 136 - 130, rad_sweep_y - 136)}" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3 3" opacity="0.6"/>

    <!-- ── Dynamic Dimension Caliper (Bisects R to prove f = R/2) ── -->
    <!-- Bracket for R (Bottom of axis, clearly spaced below (Focus)) -->
    <g transform="translate(0, {py - 136 + 65})" opacity="{t_curv:.2f}">
      <line x1="{cx}" y1="0" x2="{px}" y2="0" stroke="#38bdf8" stroke-width="1.8"/>
      <line x1="{cx}" y1="-6" x2="{cx}" y2="6" stroke="#38bdf8" stroke-width="1.8"/>
      <line x1="{px}" y1="-6" x2="{px}" y2="6" stroke="#38bdf8" stroke-width="1.8"/>
      <text x="{(cx + px) // 2}" y="-8" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="800" text-anchor="middle">
        Radius of Curvature R = {radius_val}
      </text>
    </g>

    <!-- Caliper showing f = R/2 (Under focus F) -->
    <g transform="translate(0, {py - 136 + 105})" opacity="{t_caliper:.2f}">
      <rect x="{fx - 90}" y="-16" width="180" height="32" rx="16" fill="#082f49" stroke="#67e8f9" stroke-width="1.5"/>
      <text x="{fx}" y="5" fill="#67e8f9" font-family="system-ui, sans-serif" font-size="12" font-weight="900" text-anchor="middle">
        Midpoint: f = R / 2 ({focal_val})
      </text>
      <!-- Connecting dashed ticks -->
      <line x1="{fx}" y1="-16" x2="{fx}" y2="-38" stroke="#67e8f9" stroke-width="1.5" stroke-dasharray="2 2"/>
    </g>

    <!-- ── Object Arrow (Placed beyond C at x=240) ── -->
    <g transform="translate({obj_x}, {py - 136})">
      <line x1="0" y1="0" x2="0" y2="{-obj_h}" stroke="#f59e0b" stroke-width="4"/>
      <polygon points="0,{-obj_h - 4} -6,{-obj_h + 10} 6,{-obj_h + 10}" fill="#f59e0b"/>
      <text x="0" y="{-obj_h - 10}" fill="#fde68a" font-family="system-ui, sans-serif" font-size="12" font-weight="800" text-anchor="middle">Object (h)</text>
      <!-- Distance label u -->
      <text x="0" y="18" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">u = -30cm</text>
    </g>

    <!-- ── Active Incident Ray (Parallel to axis -> strikes mirror) ── -->
    {f'''<line x1="{obj_x}" y1="{mirror_hit_y - 136}" x2="{curr_ray1_x}" y2="{mirror_hit_y - 136}" stroke="#fbbf24" stroke-width="2.5" filter="url(#aura)"/>''' if ray_p1 > 0.0 else ""}

    <!-- ── Active Reflected Ray (Reflects through Focus F) ── -->
    {f'''<line x1="{mirror_hit_x}" y1="{mirror_hit_y - 136}" x2="{curr_refl_x}" y2="{curr_refl_y - 136}" stroke="#f472b6" stroke-width="2.5" filter="url(#aura)"/>''' if ray_p2 > 0.0 else ""}

    <!-- Photon attention pulse -->
    {f'''<circle cx="{photon_x}" cy="{photon_y - 136}" r="5" fill="#ffffff" filter="url(#aura)"/>''' if t_ray > 0.1 else ""}

    <!-- In-Stage Dimension Linking Pill -->
    <g transform="translate(24, 350)" opacity="{t_formula:.2f}">
      <rect width="520" height="36" rx="10" fill="#112240" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="14" y="23" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11" font-weight="800">VARIABLE ANCHORS:</text>
      <text x="150" y="23" fill="#fde68a" font-family="system-ui, sans-serif" font-size="11" font-weight="700">u (Object Dist)</text>
      <text x="265" y="23" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11" font-weight="700">v (Image Dist)</text>
      <text x="380" y="23" fill="#7dd3fc" font-family="system-ui, sans-serif" font-size="11" font-weight="700">f = R/2 (Focal Len)</text>
    </g>
  </g>

  <!-- ── Right Column Pedagogical Insight Cards (Top Half y < 390 to preserve PIP) ── -->
  <!-- Card 1: Curvature Law Proof -->
  <g transform="translate(960, 136)">
    <rect width="270" height="110" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="18" y="28" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11" font-weight="800" letter-spacing="0.5">GEOMETRIC PROOF:</text>
    <text x="18" y="54" fill="#ffffff" font-family="system-ui, sans-serif" font-size="15" font-weight="800">f = R / 2</text>
    <text x="18" y="78" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">Focal point bisects radius of</text>
    <text x="18" y="96" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">curvature for paraxial rays.</text>
  </g>

  <!-- Card 2: Reflection Principle -->
  <g transform="translate(960, 260)">
    <rect width="270" height="125" rx="14" fill="#1e293b" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="18" y="26" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="11" font-weight="800" letter-spacing="0.5">REFLECTION RULE:</text>
    <g transform="translate(18, 44)">
      <polygon points="0,0 6,4 0,8" fill="#fbbf24"/>
      <text x="14" y="7" fill="#fbbf24" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Parallel rays reflect to F</text>
    </g>
    <g transform="translate(18, 68)">
      <polygon points="0,0 6,4 0,8" fill="#38bdf8"/>
      <text x="14" y="7" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Angle i = Angle r at mirror arc</text>
    </g>
    <text x="18" y="108" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="600">Links focal geometry to 1/v + 1/u = 1/f</text>
  </g>

  <!-- ── Bottom Educational Insight Banner (Left 890px, Leaves Bottom-Right Free for PIP) ── -->
  <g transform="translate(50, 560)">
    <rect width="890" height="92" rx="14" fill="#0f223a" stroke="#38bdf8" stroke-width="1.5" filter="url(#aura)"/>
    <circle cx="45" cy="46" r="18" fill="#38bdf8"/>
    <text x="45" y="52" fill="#071224" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">💡</text>
    <text x="80" y="36" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="800" letter-spacing="0.5">CORE SCIENTIFIC INSIGHT</text>
    <text x="80" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="15" font-weight="600">
      Spherical mirrors curve paraxial light to focal point F = R/2, connecting physical distances to 1/v + 1/u = 1/f.
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
