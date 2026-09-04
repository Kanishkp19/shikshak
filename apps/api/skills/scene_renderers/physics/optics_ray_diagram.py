"""
Shikshak AI — Physics Pack: Optics Ray Diagram Scene Renderer.

Renders geometric optics and ray tracing:
  - Convex & concave lenses / mirrors with optical center O, principal focus F₁, F₂, and 2F
  - Object arrow AB and real/virtual inverted image arrow A'B'
  - Animated incident and refracted light rays with directional attention cues
  - Clean Lens formula (1/f = 1/v - 1/u) & magnification banner
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)
from models import OpticsRayDiagramPayload


def render_optics_ray_diagram(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render an optics_ray_diagram scene to MP4."""
    payload = OpticsRayDiagramPayload.model_validate(payload_dict)

    element = payload.optical_element or "convex_lens"
    image_nature = payload.image_nature or "Real, Inverted, Same Size"
    formula = "1/f = 1/v - 1/u"
    obs = payload.key_observation or "Rays parallel to principal axis refract through principal focus F₂"

    # Coordinates for optical system: Optical center O at (460, 330)
    ox, oy = 460, 330
    f_px = 120   # 1 focal length = 120 pixels
    obj_x = ox - int(2 * f_px)  # Object at 2F₁ (220, 330)
    obj_h = 90                  # Height of object arrow
    img_x = ox + int(2 * f_px)  # Image formed at 2F₂ (700, 330)
    img_h = 90                  # Height of image arrow (inverted, tip at 700, 420)

    # Destination past image plane for full ray trajectory
    x_end = img_x + 60          # 760 px
    # Ray 1: slope = 90 / 120 = 0.75 -> y_end = 420 + 60 * 0.75 = 465
    ray1_dest_y = (oy + img_h) + int(60 * (img_h / f_px))
    # Ray 2: slope = 90 / 240 = 0.375 -> y_end = 420 + 60 * 0.375 = 442.5
    ray2_dest_y = (oy + img_h) + (60 * (obj_h / (2 * f_px)))

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        ray1_progress = max(0.0, min(1.0, (progress - 0.12) / 0.45))
        ray2_progress = max(0.0, min(1.0, (progress - 0.30) / 0.45))
        img_reveal = max(0.0, min(1.0, (progress - 0.65) / 0.30))

        # Ray 1: (obj_x, oy - obj_h) -> (ox, oy - obj_h) -> passes strictly through F2 (ox+f_px, oy) -> A' (img_x, oy+img_h)
        seg1_x = obj_x + (ox - obj_x) * min(1.0, ray1_progress * 2.0)
        seg1_y = oy - obj_h
        seg2_progress = max(0.0, (ray1_progress - 0.5) * 2.0)
        seg2_x = ox + (x_end - ox) * seg2_progress
        seg2_y = (oy - obj_h) + (ray1_dest_y - (oy - obj_h)) * seg2_progress

        # Ray 2: straight from A (obj_x, oy - obj_h) through O (ox, oy) to A' (img_x, oy+img_h)
        curr_r2_x = obj_x + (x_end - obj_x) * ray2_progress
        curr_r2_y = (oy - obj_h) + (ray2_dest_y - (oy - obj_h)) * ray2_progress

        # Dynamic Diagram Attention Glow
        pulse_r = int(12 + 3 * math.sin(elapsed_ms * 0.01))
        active_focus_svg = ""
        if ray1_progress < 0.5:
            active_focus_svg = f'<circle cx="{obj_x}" cy="{oy - obj_h}" r="{pulse_r}" fill="none" stroke="#f59e0b" stroke-width="2" filter="url(#glow)"/>'
        elif ray1_progress < 0.95:
            active_focus_svg = f'<circle cx="{ox + f_px}" cy="{oy}" r="{pulse_r}" fill="none" stroke="#38bdf8" stroke-width="2" filter="url(#glow)"/>'
        elif img_reveal > 0.1:
            active_focus_svg = f'<circle cx="{img_x}" cy="{oy + img_h}" r="{pulse_r}" fill="none" stroke="#10b981" stroke-width="2" filter="url(#glow)"/>'

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#080e1a"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="lens_glass" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.35"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.35"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Top Badge -->
  <rect x="50" y="24" width="190" height="32" rx="16" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="68" y="45" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="800" letter-spacing="1">LIGHT &amp; OPTICS</text>

  <!-- ── Distinct Non-Overlapping Formula Headers ── -->
  <!-- Left Header Pill: Lens Formula -->
  <g transform="translate(50, 68)">
    <rect width="550" height="52" rx="12" fill="#131e32" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">LENS FORMULA:</text>
    <text x="175" y="34" fill="#38bdf8" font-family="system-ui, monospace, sans-serif" font-size="20" font-weight="800">1/f = 1/v − 1/u</text>
  </g>

  <!-- Right Header Pill: Magnification Formula -->
  <g transform="translate(620, 68)">
    <rect width="610" height="52" rx="12" fill="#131e32" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">MAGNIFICATION:</text>
    <text x="180" y="34" fill="#fde68a" font-family="system-ui, monospace, sans-serif" font-size="20" font-weight="800">m = v / u = h&apos; / h</text>
  </g>

  <!-- ── Main Optical Bench Stage Frame (Left 890px) ── -->
  <g transform="translate(50, 140)">
    <rect width="880" height="400" rx="18" fill="#10192b" stroke="#334155" stroke-width="1.5"/>

    <!-- Principal Axis (Horizontal Line) -->
    <line x1="30" y1="{oy - 140}" x2="850" y2="{oy - 140}" stroke="#64748b" stroke-width="2" stroke-dasharray="6 4"/>
    <text x="840" y="{oy - 148}" fill="#64748b" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Principal Axis</text>

    <!-- Focal Points & Marks on Principal Axis -->
    <!-- 2F1 -->
    <line x1="{ox - 50 - 2*f_px}" y1="{oy - 140 - 8}" x2="{ox - 50 - 2*f_px}" y2="{oy - 140 + 8}" stroke="#38bdf8" stroke-width="2"/>
    <text x="{ox - 50 - 2*f_px}" y="{oy - 140 + 24}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">2F₁</text>
    <!-- F1 -->
    <line x1="{ox - 50 - f_px}" y1="{oy - 140 - 8}" x2="{ox - 50 - f_px}" y2="{oy - 140 + 8}" stroke="#38bdf8" stroke-width="2"/>
    <text x="{ox - 50 - f_px}" y="{oy - 140 + 24}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">F₁</text>
    <!-- Optical Center O -->
    <circle cx="{ox - 50}" cy="{oy - 140}" r="4" fill="#ffffff"/>
    <text x="{ox - 50 - 10}" y="{oy - 140 + 24}" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="800">O</text>
    <!-- F2 -->
    <line x1="{ox - 50 + f_px}" y1="{oy - 140 - 8}" x2="{ox - 50 + f_px}" y2="{oy - 140 + 8}" stroke="#38bdf8" stroke-width="2"/>
    <text x="{ox - 50 + f_px}" y="{oy - 140 + 24}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">F₂</text>
    <!-- 2F2 -->
    <line x1="{ox - 50 + 2*f_px}" y1="{oy - 140 - 8}" x2="{ox - 50 + 2*f_px}" y2="{oy - 140 + 8}" stroke="#38bdf8" stroke-width="2"/>
    <text x="{ox - 50 + 2*f_px}" y="{oy - 140 + 24}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">2F₂</text>

    <!-- Double Convex Lens Body -->
    <path d="M{ox - 50} {oy - 140 - 150} Q{ox - 50 - 28} {oy - 140} {ox - 50} {oy - 140 + 150} Q{ox - 50 + 28} {oy - 140} {ox - 50} {oy - 140 - 150} Z" fill="url(#lens_glass)" stroke="#38bdf8" stroke-width="2"/>
    <line x1="{ox - 50}" y1="{oy - 140 - 150}" x2="{ox - 50}" y2="{oy - 140 + 150}" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="4 4" opacity="0.7"/>

    <!-- ── 1. Object Arrow AB (At 2F₁) ── -->
    <g transform="translate({obj_x - 50}, {oy - 140})">
      <line x1="0" y1="0" x2="0" y2="{-obj_h}" stroke="#f59e0b" stroke-width="4"/>
      <polygon points="0,{-obj_h - 4} -6,{-obj_h + 10} 6,{-obj_h + 10}" fill="#f59e0b"/>
      <text x="-14" y="{-obj_h}" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="14" font-weight="900">A</text>
      <text x="-14" y="16" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="14" font-weight="900">B</text>
      <text x="0" y="{-obj_h - 12}" fill="#fde68a" font-family="system-ui, sans-serif" font-size="12" font-weight="800" text-anchor="middle">Object (h)</text>
    </g>

    <!-- ── 2. Light Ray 1 (Incident Parallel -> Refracts through F₂) ── -->
    {f'''<line x1="{obj_x - 50}" y1="{oy - 140 - obj_h}" x2="{seg1_x - 50:.1f}" y2="{seg1_y - 140:.1f}" stroke="#fbbf24" stroke-width="2.5" filter="url(#glow)"/>''' if ray1_progress > 0.0 else ""}
    {f'''<line x1="{ox - 50}" y1="{oy - 140 - obj_h}" x2="{seg2_x - 50:.1f}" y2="{seg2_y - 140:.1f}" stroke="#fbbf24" stroke-width="2.5" filter="url(#glow)"/>''' if ray1_progress > 0.5 else ""}

    <!-- ── 3. Light Ray 2 (Through Optical Center O) ── -->
    {f'''<line x1="{obj_x - 50}" y1="{oy - 140 - obj_h}" x2="{curr_r2_x - 50:.1f}" y2="{curr_r2_y - 140:.1f}" stroke="#f472b6" stroke-width="2.5" filter="url(#glow)"/>''' if ray2_progress > 0.0 else ""}

    <!-- ── 4. Image Arrow A'B' (Formed at 2F₂, tip at 700, 420) ── -->
    {f'''<g transform="translate({img_x - 50}, {oy - 140})" opacity="{img_reveal:.2f}">
      <line x1="0" y1="0" x2="0" y2="{img_h}" stroke="#10b981" stroke-width="4"/>
      <polygon points="0,{img_h + 4} -6,{img_h - 10} 6,{img_h - 10}" fill="#10b981"/>
      <text x="14" y="{img_h + 2}" fill="#10b981" font-family="system-ui, sans-serif" font-size="14" font-weight="900">A&apos;</text>
      <text x="14" y="-8" fill="#10b981" font-family="system-ui, sans-serif" font-size="14" font-weight="900">B&apos;</text>
      <text x="0" y="{img_h + 24}" fill="#6ee7b7" font-family="system-ui, sans-serif" font-size="12" font-weight="800" text-anchor="middle">Image (h&apos;)</text>
    </g>''' if img_reveal > 0.05 else ""}

    <!-- Dynamic Attention Focus Ring -->
    {active_focus_svg}

    <!-- ── In-Stage Sign Conventions Pill (Protected from PIP Occlusion) ── -->
    <g transform="translate(24, 348)">
      <rect width="470" height="34" rx="8" fill="#132038" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="14" y="22" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11" font-weight="800">SIGN CONVENTIONS:</text>
      <text x="145" y="22" fill="#ffffff" font-family="system-ui, monospace, sans-serif" font-size="11" font-weight="700">u = -20cm | v = +20cm | f = +10cm</text>
    </g>
  </g>

  <!-- ── Right Column Cards (Arranged purely in Top Half y < 390 to prevent PIP occlusion) ── -->
  <!-- Card 1: Image Characteristics -->
  <g transform="translate(950, 140)">
    <rect width="280" height="108" rx="14" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
    <text x="20" y="30" fill="#10b981" font-family="system-ui, sans-serif" font-size="11" font-weight="800" letter-spacing="0.5">IMAGE CHARACTERISTICS:</text>
    <text x="20" y="58" fill="#ffffff" font-family="system-ui, sans-serif" font-size="15" font-weight="800">{escape_xml(image_nature)}</text>
    <text x="20" y="85" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">Position: Formed at 2F₂</text>
  </g>

  <!-- Card 2: Ray Rules (with SVG vector arrows, preventing missing font glyph boxes) -->
  <g transform="translate(950, 262)">
    <rect width="280" height="120" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.2"/>
    <text x="20" y="28" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11" font-weight="800" letter-spacing="0.5">RAY RULES:</text>
    <g transform="translate(20, 48)">
      <polygon points="0,0 6,4 0,8" fill="#fbbf24"/>
      <text x="14" y="7" fill="#fbbf24" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Parallel ray passes through F₂</text>
    </g>
    <g transform="translate(20, 72)">
      <polygon points="0,0 6,4 0,8" fill="#f472b6"/>
      <text x="14" y="7" fill="#f472b6" font-family="system-ui, sans-serif" font-size="11" font-weight="700">Ray through O continues straight</text>
    </g>
    <text x="20" y="104" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="600">Intersection forms image tip A&apos;</text>
  </g>

  <!-- ── Bottom Observation Banner (Left Aligned, Leaves Bottom-Right Free for PIP) ── -->
  <g transform="translate(50, 560)">
    <rect width="880" height="92" rx="14" fill="#102338" stroke="#38bdf8" stroke-width="1.5" filter="url(#glow)"/>
    <circle cx="45" cy="46" r="18" fill="#38bdf8"/>
    <text x="45" y="52" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">👁</text>
    <text x="80" y="36" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="800" letter-spacing="0.5">OPTICAL OBSERVATION</text>
    <text x="80" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="15" font-weight="600">
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
