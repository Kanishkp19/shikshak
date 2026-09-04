"""
Shikshak AI — Mathematics Pack: Algebra Step Solve Scene Renderer.

Renders stepwise algebraic problem solving:
  - Problem statement & given equation
  - Progressive step-by-step mathematical transformations
  - Formula rules & algebraic theorems applied
  - Final highlighted solution box
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
)
from models import AlgebraStepSolvePayload


def render_algebra_step_solve(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Render an algebra_step_solve scene to MP4."""
    payload = AlgebraStepSolvePayload.model_validate(payload_dict)

    title = payload.title or "Step-by-Step Algebraic Solution"
    initial_expr = payload.initial_expression or "ax² + bx + c = 0"
    steps = payload.steps or [
        "Divide by a: x² + (b/a)x + (c/a) = 0",
        "Complete the square: (x + b/2a)² = (b² - 4ac) / 4a²",
        "Take square root: x + b/2a = ±√(b² - 4ac) / 2a",
    ]
    final_sol = payload.final_solution or "x = (-b ± √(b² - 4ac)) / 2a"
    rule = payload.rule_used or "Quadratic Formula / Completing the Square"

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
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
  <text x="70" y="52" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="1">🔢 ALGEBRA &amp; EQUATIONS</text>

  <!-- Title Banner -->
  <rect x="50" y="76" width="1180" height="54" rx="12" fill="#131e32" stroke="#38bdf8" stroke-width="1.5" filter="url(#glow)"/>
  <text x="640" y="111" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="700" text-anchor="middle">
    {escape_xml(title).upper()}
  </text>

  <!-- ── Step-by-Step Derivation Column (Left Main) ── -->
  <g transform="translate(50, 150)">
    <!-- Initial Equation Header Card -->
    <rect width="780" height="65" rx="14" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="25" y="40" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="14" font-weight="700">GIVEN EQUATION:</text>
    <text x="180" y="42" fill="#38bdf8" font-family="monospace, sans-serif" font-size="20" font-weight="700">{escape_xml(initial_expr)}</text>

    <!-- Derivation Steps Progression -->
    {"".join(
        f'''<g transform="translate(0, {80 + idx * 75})">
          <rect width="780" height="62" rx="12" fill="#162032" stroke="{"#38bdf8" if progress > (idx*0.25) else "#334155"}" stroke-width="1.2"/>
          <circle cx="30" cy="31" r="14" fill="#38bdf8"/>
          <text x="30" y="36" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="900" text-anchor="middle">{idx+1}</text>
          <text x="65" y="38" fill="{"#ffffff" if progress > (idx*0.25) else "#94a3b8"}" font-family="monospace, sans-serif" font-size="16" font-weight="600">{escape_xml(step)}</text>
        </g>'''
        for idx, step in enumerate(steps[:4])
    )}
  </g>

  <!-- ── Right Column: Solution & Rule Cards ── -->
  <g transform="translate(860, 150)">
    <!-- Final Solution Box -->
    <rect width="370" height="150" rx="16" fill="#112438" stroke="#10b981" stroke-width="2" filter="url(#glow)"/>
    <text x="25" y="38" fill="#10b981" font-family="system-ui, sans-serif" font-size="13" font-weight="700">FINAL SOLUTION:</text>
    <text x="25" y="85" fill="#34d399" font-family="monospace, sans-serif" font-size="18" font-weight="800">{escape_xml(final_sol)}</text>
    <text x="25" y="125" fill="#6ee7b7" font-family="system-ui, sans-serif" font-size="12">✓ Verified Roots / Exact Formula</text>

    <!-- Formula Rule Card -->
    <rect y="170" width="370" height="140" rx="14" fill="#1e293b" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="25" y="200" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="12" font-weight="700">ALGEBRAIC THEOREM / RULE:</text>
    <text x="25" y="235" fill="#ffffff" font-family="system-ui, sans-serif" font-size="15" font-weight="700">{escape_xml(rule)}</text>
    <text x="25" y="270" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">Discriminant: D = b² - 4ac determines real roots.</text>
  </g>

  <!-- ── Bottom Summary Banner ── -->
  <g transform="translate(50, 560)">
    <rect width="1180" height="90" rx="14" fill="#102538" stroke="#38bdf8" stroke-width="1.8" filter="url(#glow)"/>
    <circle cx="45" cy="45" r="18" fill="#38bdf8"/>
    <text x="45" y="51" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="900" text-anchor="middle">✓</text>
    <text x="80" y="36" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="0.5">MATHEMATICAL PRINCIPLE</text>
    <text x="80" y="66" fill="#ffffff" font-family="system-ui, sans-serif" font-size="17" font-weight="600">
      Every quadratic equation has at most two solutions in the complex plane, determined by the quadratic formula.
    </text>
  </g>
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
