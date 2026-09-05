"""
Shikshak AI — Classroom Smartboard Animated Lecture Scene Renderer.

Renders high-grade university classroom smartboard / chalkboard animations:
  - Deep slate blackboard canvas with coordinate grid and academic borders
  - Dedicated Formula & Governing Law Card with glowing chalk accents
  - Kinetic step-by-step concept derivations (revealed progressively across speech)
  - Animated vector pedagogical schematics (optics ray reflection, chloroplast pathways, circuits)
  - 100% Vector SVG-to-MP4 animation with ZERO stock photos or external images.
"""
from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Optional
import uuid

from skills.scene_renderers.base import (
    escape_xml,
    render_svg_frames_to_mp4,
    require_playable_video,
    sanitize_display_text,
)

logger = logging.getLogger(__name__)


def _detect_canonical_formula(concept: str, narration: str, explicit_formula: str = "") -> str:
    """Infer or format canonical scientific formula for the lesson topic."""
    if explicit_formula and explicit_formula.upper() != "NOT_IN_SOURCE":
        return explicit_formula
    c = (concept + " " + narration).lower()
    if any(k in c for k in ("reflection", "mirror", "angle of incidence", "vision", "sunlight")):
        return "∠i = ∠r  (Law of Reflection)  •  1/f = 1/v + 1/u"
    if any(k in c for k in ("refraction", "snell", "index")):
        return "n = sin(i) / sin(r)  (Snell's Law)  •  v = c / n"
    if any(k in c for k in ("lens", "focal length", "magnification")):
        return "1/f = 1/v - 1/u  (Lens Formula)  •  m = v / u"
    if any(k in c for k in ("photosynthesis", "chloroplast", "chlorophyll")):
        return "6CO₂ + 6H₂O + Sunlight ⟶ C₆H₁₂O₆ + 6O₂"
    if any(k in c for k in ("respiration", "mitochondria", "atp")):
        return "C₆H₁₂O₆ + 6O₂ ⟶ 6CO₂ + 6H₂O + 38 ATP"
    if any(k in c for k in ("circuit", "ohm", "resistance", "resistor")):
        return "V = I · R  (Ohm's Law)  •  P = V · I = I²R"
    if any(k in c for k in ("newton", "force", "acceleration")):
        return "F_net = m · a  •  p = m · v  •  F_AB = -F_BA"
    if any(k in c for k in ("gravity", "gravitation", "orbit")):
        return "F = G · (m₁ · m₂) / r²  •  g = 9.8 m/s²"
    if any(k in c for k in ("energy", "kinetic", "potential")):
        return "E_k = ½ m·v²  •  E_p = m·g·h  •  E_total = const"
    return "Principle: Baseline Governing Law & State Equation"


def render_ai_illustration(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Optional[Path] = None,
) -> Path:
    """Render a pure Classroom Smartboard lecture scene with formulas, text, and vector animations."""
    duration_s = max(2.0, min(90.0, float(duration_seconds)))
    if out_path is None:
        target_path = Path("/tmp/shikshak_scenes") / f"classroom_board_{uuid.uuid4().hex}.mp4"
    else:
        target_path = Path(out_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    title = sanitize_display_text(payload_dict.get("title")) or "Core Principles & Laws"
    caption = sanitize_display_text(payload_dict.get("caption")) or narration_text[:85]
    entities = payload_dict.get("entities") or []
    explicit_formula = sanitize_display_text(payload_dict.get("formula"))
    formula = _detect_canonical_formula(title, narration_text, explicit_formula)
    takeaway = sanitize_display_text(payload_dict.get("key_takeaway")) or f"Essential mastery of {title[:40]}"

    # Extract 3 progressive pedagogical points
    raw_points = payload_dict.get("key_points") or entities
    points = [sanitize_display_text(p) for p in raw_points if sanitize_display_text(p)]
    if len(points) < 3:
        sentences = [s.strip() for s in narration_text.split(".") if len(s.strip()) > 10]
        for s in sentences:
            if len(points) < 3 and s not in points:
                points.append(s[:58])
    while len(points) < 3:
        points.append(f"Step {len(points)+1}: Systematic physical observation")
    points = points[:3]

    is_optics = any(k in (title + " " + narration_text).lower() for k in ("light", "reflect", "vision", "ray", "mirror", "optics"))
    is_bio = any(k in (title + " " + narration_text).lower() for k in ("photo", "chloro", "cell", "plant", "leaf"))

    def svg_generator(progress: float, elapsed_ms: int, total_ms: int) -> str:
        pulse = 0.5 + 0.5 * math.sin(elapsed_ms * 0.003)
        ray_anim = min(1.0, progress * 1.6)

        svg = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">',
            '  <defs>',
            '    <linearGradient id="chalkboardBg" x1="0" y1="0" x2="0" y2="1">',
            '      <stop offset="0%" stop-color="#0b1320"/>',
            '      <stop offset="100%" stop-color="#0f1d30"/>',
            '    </linearGradient>',
            '    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
            '      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#16253b" stroke-width="0.75"/>',
            '    </pattern>',
            '    <filter id="glow">',
            '      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#38bdf8" flood-opacity="0.4"/>',
            '    </filter>',
            '    <filter id="amberGlow">',
            '      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#f59e0b" flood-opacity="0.5"/>',
            '    </filter>',
            '  </defs>',
            '  <!-- Blackboard Base Canvas -->',
            '  <rect width="1280" height="720" fill="url(#chalkboardBg)"/>',
            '  <rect width="1280" height="720" fill="url(#grid)"/>',
            '  <!-- Classroom Chalk Frame -->',
            '  <rect x="20" y="20" width="1240" height="680" rx="12" fill="none" stroke="#2a3c54" stroke-width="2"/>',
            '  <rect x="24" y="24" width="1232" height="672" rx="10" fill="none" stroke="#162232" stroke-width="1"/>',
            '  <!-- Top Lecture Banner -->',
            '  <rect x="40" y="38" width="190" height="28" rx="14" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5" filter="url(#amberGlow)"/>',
            '  <circle cx="56" cy="52" r="4" fill="#f59e0b"/>',
            '  <text x="68" y="56" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#fbbf24" letter-spacing="1">CLASSROOM LECTURE</text>',
            '  <text x="248" y="56" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="600" fill="#94a3b8">PROFESSOR\'S SMARTBOARD · CORE PRINCIPLES</text>',
            f'  <!-- Topic Title -->',
            f'  <text x="40" y="106" font-family="Helvetica, Arial, sans-serif" font-size="30" font-weight="bold" fill="#f8fafc">{escape_xml(title[:45])}</text>',
            f'  <!-- Formula & Governing Law Card -->',
            f'  <rect x="40" y="126" width="620" height="60" rx="8" fill="#111c2e" stroke="#38bdf8" stroke-width="1.8" filter="url(#glow)"/>',
            f'  <text x="56" y="146" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" letter-spacing="1">GOVERNING LAW / EQUATION</text>',
            f'  <text x="56" y="172" font-family="Courier New, monospace, sans-serif" font-size="19" font-weight="bold" fill="#e0f2fe">{escape_xml(formula)}</text>',
        ]

        # Left Column: Progressive Derivation Steps
        step_y = 208
        card_h = 66
        card_gap = 14
        step_times = [0.12, 0.40, 0.68]

        for idx, (pt, trig) in enumerate(zip(points, step_times)):
            pt_prog = max(0.0, min(1.0, (progress - trig) / 0.22))
            alpha = pt_prog
            card_border = "#38bdf8" if pt_prog > 0.8 else "#1e293b"
            card_bg = "#111c2e" if pt_prog > 0.8 else "#0c1524"

            svg.append(f'  <g opacity="{alpha:.2f}">')
            svg.append(f'    <rect x="40" y="{step_y}" width="620" height="{card_h}" rx="8" fill="{card_bg}" stroke="{card_border}" stroke-width="1.2"/>')
            svg.append(f'    <rect x="52" y="{step_y + 16}" width="34" height="34" rx="6" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1.2"/>')
            svg.append(f'    <text x="69" y="{step_y + 38}" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8" text-anchor="middle">0{idx+1}</text>')
            svg.append(f'    <text x="100" y="{step_y + 38}" font-family="Helvetica, Arial, sans-serif" font-size="16" font-weight="500" fill="#f1f5f9">{escape_xml(pt[:56])}</text>')
            svg.append('  </g>')
            step_y += card_h + card_gap

        # Right Column: Animated Vector Classroom Schematic
        schematic_x = 690
        schematic_y = 126
        schematic_w = 550
        schematic_h = 390

        svg.append(f'  <!-- Interactive Classroom Diagram Stage -->')
        svg.append(f'  <rect x="{schematic_x}" y="{schematic_y}" width="{schematic_w}" height="{schematic_h}" rx="10" fill="#0c1524" stroke="#253549" stroke-width="1.5"/>')
        svg.append(f'  <rect x="{schematic_x + 16}" y="{schematic_y + 14}" width="160" height="24" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>')
        svg.append(f'  <text x="{schematic_x + 96}" y="{schematic_y + 30}" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1">VECTOR SCHEMA</text>')

        if is_optics:
            surf_y = 350
            norm_x = schematic_x + schematic_w // 2
            svg.append(f'  <line x1="{schematic_x + 40}" y1="{surf_y}" x2="{schematic_x + schematic_w - 40}" y2="{surf_y}" stroke="#94a3b8" stroke-width="4"/>')
            for hx in range(schematic_x + 45, schematic_x + schematic_w - 40, 20):
                svg.append(f'  <line x1="{hx}" y1="{surf_y}" x2="{hx - 10}" y2="{surf_y + 15}" stroke="#475569" stroke-width="1.5"/>')
            svg.append(f'  <text x="{schematic_x + schematic_w - 90}" y="{surf_y + 30}" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#94a3b8">Plane Mirror</text>')

            # Normal line
            svg.append(f'  <line x1="{norm_x}" y1="{surf_y - 180}" x2="{norm_x}" y2="{surf_y}" stroke="#64748b" stroke-width="1.8" stroke-dasharray="6,6"/>')
            svg.append(f'  <text x="{norm_x - 10}" y="{surf_y - 190}" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#94a3b8">Normal (N)</text>')

            # Incident Ray
            inc_start_x = schematic_x + 70
            inc_start_y = surf_y - 150
            cur_inc_x = inc_start_x + (norm_x - inc_start_x) * min(1.0, ray_anim * 1.5)
            cur_inc_y = inc_start_y + (surf_y - inc_start_y) * min(1.0, ray_anim * 1.5)

            svg.append(f'  <line x1="{inc_start_x}" y1="{inc_start_y}" x2="{cur_inc_x}" y2="{cur_inc_y}" stroke="#fbbf24" stroke-width="3" filter="url(#amberGlow)"/>')
            svg.append(f'  <circle cx="{inc_start_x}" cy="{inc_start_y}" r="5" fill="#f59e0b"/>')
            svg.append(f'  <text x="{inc_start_x - 20}" y="{inc_start_y - 12}" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#fbbf24">Incident Ray</text>')

            # Reflected Ray
            if ray_anim > 0.5:
                ref_prog = (ray_anim - 0.5) * 2.0
                ref_end_x = schematic_x + schematic_w - 70
                ref_end_y = surf_y - 150
                cur_ref_x = norm_x + (ref_end_x - norm_x) * ref_prog
                cur_ref_y = surf_y + (ref_end_y - surf_y) * ref_prog

                svg.append(f'  <line x1="{norm_x}" y1="{surf_y}" x2="{cur_ref_x}" y2="{cur_ref_y}" stroke="#38bdf8" stroke-width="3" filter="url(#glow)"/>')
                svg.append(f'  <circle cx="{norm_x}" cy="{surf_y}" r="6" fill="#38bdf8"/>')
                svg.append(f'  <text x="{ref_end_x - 30}" y="{ref_end_y - 12}" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">Reflected Ray</text>')
                svg.append(f'  <text x="{norm_x - 50}" y="{surf_y - 50}" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#fbbf24">∠i</text>')
                svg.append(f'  <text x="{norm_x + 35}" y="{surf_y - 50}" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#38bdf8">∠r</text>')
                svg.append(f'  <text x="{schematic_x + schematic_w//2}" y="{schematic_y + schematic_h - 20}" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#34d399" text-anchor="middle">Law Confirmed: ∠i = ∠r</text>')

        elif is_bio:
            cx = schematic_x + schematic_w // 2
            cy = schematic_y + schematic_h // 2 + 10
            svg.append(f'  <ellipse cx="{cx}" cy="{cy}" rx="190" ry="115" fill="#064e3b" fill-opacity="0.3" stroke="#10b981" stroke-width="2.5" stroke-dasharray="8,4"/>')
            svg.append(f'  <text x="{cx}" y="{cy - 85}" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#34d399" text-anchor="middle">Chloroplast Double Membrane</text>')
            for gx in (cx - 90, cx, cx + 90):
                for ty in (cy - 30, cy, cy + 30):
                    svg.append(f'  <rect x="{gx - 25}" y="{ty - 8}" width="50" height="16" rx="6" fill="#059669" stroke="#34d399" stroke-width="1.2"/>')
            svg.append(f'  <text x="{cx}" y="{cy + 75}" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#a7f3d0" text-anchor="middle">Thylakoid Grana (Light Reaction Site)</text>')
            svg.append(f'  <text x="{schematic_x + 40}" y="{cy - 50}" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">H₂O + CO₂ ⟶</text>')
            svg.append(f'  <text x="{schematic_x + schematic_w - 130}" y="{cy - 50}" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#fbbf24">⟶ C₆H₁₂O₆ + O₂</text>')

        else:
            cx = schematic_x + schematic_w // 2
            cy = schematic_y + schematic_h // 2
            nodes = [
                (cx, cy - 90, "Baseline Input"),
                (cx - 140, cy + 60, "Transform Step"),
                (cx + 140, cy + 60, "Output Result"),
            ]
            svg.append(f'  <line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[1][0]}" y2="{nodes[1][1]}" stroke="#38bdf8" stroke-width="2"/>')
            svg.append(f'  <line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[2][0]}" y2="{nodes[2][1]}" stroke="#38bdf8" stroke-width="2"/>')
            svg.append(f'  <line x1="{nodes[1][0]}" y1="{nodes[1][1]}" x2="{nodes[2][0]}" y2="{nodes[2][1]}" stroke="#34d399" stroke-width="2" stroke-dasharray="6,4"/>')

            for nx, ny, nlbl in nodes:
                svg.append(f'  <circle cx="{nx}" cy="{ny}" r="38" fill="#1e293b" stroke="#38bdf8" stroke-width="2" filter="url(#glow)"/>')
                svg.append(f'  <circle cx="{nx}" cy="{ny}" r="{18 + 4 * pulse:.1f}" fill="#0284c7" fill-opacity="0.3"/>')
                svg.append(f'  <text x="{nx}" y="{ny + 5}" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#f8fafc" text-anchor="middle">{escape_xml(nlbl)}</text>')

        # Bottom Full-Width Takeaway Banner
        bar_y = 628
        svg.append(f'  <rect x="40" y="{bar_y}" width="1200" height="52" rx="8" fill="#0f1d30" stroke="#1e3a5f" stroke-width="1.5"/>')
        svg.append(f'  <rect x="52" y="{bar_y + 12}" width="110" height="28" rx="6" fill="#0369a1" fill-opacity="0.3" stroke="#38bdf8" stroke-width="1"/>')
        svg.append(f'  <text x="107" y="{bar_y + 30}" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle">KEY TAKEAWAY</text>')
        svg.append(f'  <text x="175" y="{bar_y + 32}" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="500" fill="#e0f2fe">{escape_xml(takeaway[:95])}</text>')

        svg.append('</svg>')
        return "\n".join(svg)

    render_svg_frames_to_mp4(
        svg_generator=svg_generator,
        duration_seconds=duration_s,
        out_path=target_path,
        fps=24,
    )

    require_playable_video(str(target_path), min_width=640, min_height=360, min_duration_seconds=1.0)
    return target_path
