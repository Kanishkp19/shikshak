"""
Shikshak AI — Mathematics Pack: Number Line Geometry Scene Renderer.

Renders real number lines, coordinate geometry, and geometric constructions:
  - High-precision continuous real number line (integers, fractions, irrationals)
  - Geometric representation of √2, √3 via Pythagorean right triangle construction
  - Animated compass arc dropping hypotenuse onto number line at 1.414...
  - Mathematical completeness theorem
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)
from models import NumberLineGeometryPayload


def render_number_line_geometry(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render a number_line_geometry scene to MP4."""
    payload = NumberLineGeometryPayload.model_validate(payload_dict)

    title = payload.title or "Representation of Real Numbers on Number Line"
    theorem = payload.theorem or "Every real number is represented by a unique point on the number line."
    construction = payload.construction_step or "Right triangle: base=1, height=1 → Hypotenuse OB = √2 ≈ 1.414"

    # Number line coordinate system: Origin O at (380, 420), unit scale = 140 pixels per unit
    ox, oy = 380, 420
    u_px = 140

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Phase 1: Base right triangle OA on number line (progress 0.0 -> 0.3)
        # Phase 2: Perpendicular AB = 1 unit constructed (progress 0.3 -> 0.5)
        # Phase 3: Hypotenuse OB = √2 connected (progress 0.5 -> 0.7)
        # Phase 4: Compass arc from B swings down to intercept number line at P (progress 0.7 -> 1.0)
        tri_progress = max(0.0, min(1.0, (progress - 0.1) / 0.3))
        perp_progress = max(0.0, min(1.0, (progress - 0.3) / 0.25))
        hyp_progress = max(0.0, min(1.0, (progress - 0.5) / 0.25))
        arc_progress = max(0.0, min(1.0, (progress - 0.7) / 0.3))

        # Triangle vertices:
        # O = (ox, oy)
        # A = (ox + u_px, oy) [x = 1]
        # B = (ox + u_px, oy - u_px) [x = 1, y = 1]
        # P = (ox + int(u_px * 1.4142), oy) [x = √2 ≈ 1.414]
        ax, ay = ox + u_px, oy
        bx, by = ox + u_px, oy - u_px
        px = ox + int(u_px * 1.4142)

        # Current perpendicular tip
        curr_by = oy - (u_px * perp_progress)
        # Current hypotenuse tip
        curr_hx = ox + (u_px * hyp_progress)
        curr_hy = oy - (u_px * hyp_progress)

        # Arc sweep angle from 45 deg (-u_px, -u_px relative to O) down to 0 deg (on x-axis)
        curr_angle = (math.pi / 4.0) * (1.0 - arc_progress)
        arc_x = ox + (u_px * 1.4142) * math.cos(curr_angle)
        arc_y = oy - (u_px * 1.4142) * math.sin(curr_angle)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#080e1a"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bg)"/>

  <!-- Top Badge -->
  <rect x="50" y="30" width="220" height="34" rx="17" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="70" y="52" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">📐 REAL NUMBERS &amp; MATH</text>

  <!-- Title Banner -->
  <rect x="50" y="76" width="1180" height="54" rx="12" fill="#131e32" stroke="#38bdf8" stroke-width="1.5" filter="url(#glow)"/>
  <text x="640" y="111" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="700" text-anchor="middle">
    {escape_xml(title).upper()}
  </text>

  <!-- ── Number Line Stage (Left Column) ── -->
  <g transform="translate(0, 0)">
    <!-- Stage Frame Card -->
    <rect x="50" y="150" width="760" height="390" rx="18" fill="#111c2e" stroke="#334155" stroke-width="1.5"/>

    <!-- Horizontal Number Line -->
    <line x1="100" y1="{oy}" x2="760" y2="{oy}" stroke="#94a3b8" stroke-width="3"/>
    <!-- Left/Right Arrowheads -->
    <polygon points="95,{oy} 105,{oy-6} 105,{oy+6}" fill="#94a3b8"/>
    <polygon points="765,{oy} 755,{oy-6} 755,{oy+6}" fill="#94a3b8"/>

    <!-- Integer Unit Ticks & Labels -->
    <!-- -1 -->
    <line x1="{ox - u_px}" y1="{oy - 8}" x2="{ox - u_px}" y2="{oy + 8}" stroke="#64748b" stroke-width="2"/>
    <text x="{ox - u_px}" y="{oy + 28}" fill="#64748b" font-family="system-ui, sans-serif" font-size="16" font-weight="700" text-anchor="middle">-1</text>
    <!-- 0 (Origin O) -->
    <line x1="{ox}" y1="{oy - 10}" x2="{ox}" y2="{oy + 10}" stroke="#38bdf8" stroke-width="3"/>
    <circle cx="{ox}" cy="{oy}" r="5" fill="#38bdf8"/>
    <text x="{ox}" y="{oy + 28}" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">0 (O)</text>
    <!-- 1 (Point A) -->
    <line x1="{ox + u_px}" y1="{oy - 10}" x2="{ox + u_px}" y2="{oy + 10}" stroke="#38bdf8" stroke-width="3"/>
    <circle cx="{ax}" cy="{ay}" r="5" fill="#38bdf8"/>
    <text x="{ox + u_px}" y="{oy + 28}" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">1 (A)</text>
    <!-- 2 -->
    <line x1="{ox + 2*u_px}" y1="{oy - 8}" x2="{ox + 2*u_px}" y2="{oy + 8}" stroke="#64748b" stroke-width="2"/>
    <text x="{ox + 2*u_px}" y="{oy + 28}" fill="#64748b" font-family="system-ui, sans-serif" font-size="16" font-weight="700" text-anchor="middle">2</text>

    <!-- ── Geometric Pythagorean Triangle Construction ── -->
    <!-- 1. Base OA = 1 unit -->
    <line x1="{ox}" y1="{oy}" x2="{ax}" y2="{ay}" stroke="#38bdf8" stroke-width="4"/>
    <text x="{ox + u_px/2}" y="{oy - 8}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">1 Unit</text>

    <!-- 2. Perpendicular AB = 1 unit -->
    {f'''<line x1="{ax}" y1="{ay}" x2="{ax}" y2="{curr_by:.1f}" stroke="#f59e0b" stroke-width="4"/>
    <rect x="{ax - 14}" y="{ay - 14}" width="14" height="14" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <circle cx="{ax}" cy="{by}" r="5" fill="#f59e0b"/>
    <text x="{ax + 18}" y="{oy - u_px/2}" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="12" font-weight="700">1 Unit (AB)</text>
    <text x="{ax + 14}" y="{by}" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="14" font-weight="900">B</text>''' if perp_progress > 0.0 else ""}

    <!-- 3. Hypotenuse OB = √2 -->
    {f'''<line x1="{ox}" y1="{oy}" x2="{curr_hx:.1f}" y2="{curr_hy:.1f}" stroke="#10b981" stroke-width="4" filter="url(#glow)"/>
    <text x="{ox + u_px/2 - 16}" y="{oy - u_px/2 - 12}" fill="#34d399" font-family="system-ui, sans-serif" font-size="15" font-weight="900">√2 ≈ 1.414</text>''' if hyp_progress > 0.0 else ""}

    <!-- 4. Compass Arc swinging to Number Line Point P -->
    {f'''<path d="M{bx} {by} A{u_px * 1.4142:.1f} {u_px * 1.4142:.1f} 0 0 1 {arc_x:.1f} {arc_y:.1f}" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="5 4"/>
    <circle cx="{arc_x:.1f}" cy="{arc_y:.1f}" r="4" fill="#fbbf24" filter="url(#glow)"/>''' if arc_progress > 0.0 else ""}

    <!-- Point P (√2 on Number Line) -->
    {f'''<g transform="translate({px}, {oy})">
      <line x1="0" y1="-14" x2="0" y2="14" stroke="#fbbf24" stroke-width="3"/>
      <circle cx="0" cy="0" r="6" fill="#fbbf24" filter="url(#glow)"/>
      <text x="0" y="-22" fill="#fbbf24" font-family="system-ui, sans-serif" font-size="16" font-weight="900" text-anchor="middle">P (√2)</text>
      <text x="0" y="48" fill="#fde68a" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">Point √2 = 1.414...</text>
    </g>''' if arc_progress > 0.8 else ""}
  </g>

  <!-- ── Mathematical Proof & Sets (Right Column) ── -->
  <g transform="translate(840, 150)">
    <!-- Pythagorean Calculation Card -->
    <rect width="390" height="115" rx="14" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
    <text x="20" y="32" fill="#10b981" font-family="system-ui, sans-serif" font-size="12" font-weight="700">PYTHAGORAS THEOREM PROOF:</text>
    <text x="20" y="60" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="700">OB² = OA² + AB²</text>
    <text x="20" y="85" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="15">OB² = 1² + 1² = 2 ⇒ <tspan fill="#34d399" font-weight="800">OB = √2</tspan></text>

    <!-- Number Sets Classification Card -->
    <rect y="130" width="390" height="120" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.2"/>
    <text x="20" y="156" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700">REAL NUMBER SYSTEM (ℝ):</text>
    <text x="20" y="180" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13">Rational Numbers (ℚ): Terminating / Repeating</text>
    <text x="20" y="204" fill="#fde68a" font-family="system-ui, sans-serif" font-size="13">Irrational Numbers: Non-terminating (√2, π)</text>
    <text x="20" y="228" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13">Real Numbers ℝ = ℚ ∪ Irrationals</text>

    <!-- Construction Step Card -->
    <rect y="265" width="390" height="110" rx="14" fill="#1e293b" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="20" y="292" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="12" font-weight="700">CONSTRUCTION PRINCIPLE:</text>
    <text x="20" y="320" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13">{escape_xml(construction)}</text>
  </g>

  <!-- ── Bottom Summary Banner ── -->
  <g transform="translate(50, 560)">
    <rect width="1180" height="90" rx="14" fill="#102538" stroke="#38bdf8" stroke-width="1.8" filter="url(#glow)"/>
    <circle cx="45" cy="45" r="18" fill="#38bdf8"/>
    <text x="45" y="51" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="900" text-anchor="middle">✓</text>
    <text x="80" y="36" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="0.5">DEDEKIND-CANTOR THEOREM</text>
    <text x="80" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="17" font-weight="600">
      {escape_xml(theorem)}
    </text>
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
