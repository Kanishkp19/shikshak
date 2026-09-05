"""
Shikshak AI — Interactive Equation & Chemical Formula Studio Scene Renderer.

Renders high-impact, pedagogical whiteboard classroom animations:
  - Mode 1: Chemical Formula Building & Criss-Cross Valency Animation
    * 3D-shaded atom/ion spheres (CPK color-coded)
    * Animated curved swooping criss-cross arrows transferring valencies
    * Polyatomic ion brackets with charge callouts: [ SO₄ ]²⁻
    * Electrical charge cancellation check: (+2) + 2(-1) = 0 (Neutral)
  - Mode 2: Progressive Chemical Reaction & Molecular Assembly
    * Term-by-term progressive equation construction
    * Molecular structure / atom cluster visualization below formulas
    * Flowing reaction particles across the yield arrow (→)
    * Element conservation inventory badges with live balance checks
  - Mode 3: Stepwise Scientific & Mathematical Formula Derivation
  - Clean, warm whiteboard classroom aesthetic (#fdfbf7 with dot-matrix grid)
"""
from __future__ import annotations

import html
import math
import re
from pathlib import Path
from typing import Any, Tuple

from skills.scene_renderers.base import (
    escape_xml,
    format_subscripts,
    render_svg_frames_to_mp4,
)
from skills.scene_renderers.icon_library import (
    ICONS,
    render_icon_element,
    resolve_semantic_icon,
)
from skills.scene_renderers.multi_domain_kits import WHITEBOARD_DEFS
from models import EquationBuildPayload


# ── Curated CPK Color Palette for 3D Atom Spheres ────────────────────────────
CPK_PALETTE: dict[str, dict[str, str]] = {
    "H":  {"name": "Hydrogen", "grad": "sphere-white",    "text": "#0f172a", "accent": "#94a3b8", "r": 20},
    "C":  {"name": "Carbon",   "grad": "sphere-charcoal", "text": "#ffffff", "accent": "#334155", "r": 28},
    "O":  {"name": "Oxygen",   "grad": "sphere-red",      "text": "#ffffff", "accent": "#ef4444", "r": 24},
    "N":  {"name": "Nitrogen", "grad": "sphere-blue",     "text": "#ffffff", "accent": "#2563eb", "r": 26},
    "Cl": {"name": "Chlorine", "grad": "sphere-emerald",  "text": "#ffffff", "accent": "#10b981", "r": 30},
    "Na": {"name": "Sodium",   "grad": "sphere-purple",   "text": "#ffffff", "accent": "#8b5cf6", "r": 30},
    "Mg": {"name": "Magnesium","grad": "sphere-teal",     "text": "#ffffff", "accent": "#0d9488", "r": 32},
    "Al": {"name": "Aluminum", "grad": "sphere-slate",    "text": "#ffffff", "accent": "#64748b", "r": 30},
    "Ca": {"name": "Calcium",  "grad": "sphere-cyan",     "text": "#ffffff", "accent": "#06b6d4", "r": 32},
    "S":  {"name": "Sulfur",   "grad": "sphere-gold",     "text": "#0f172a", "accent": "#eab308", "r": 28},
    "Fe": {"name": "Iron",     "grad": "sphere-amber",    "text": "#ffffff", "accent": "#d97706", "r": 32},
    "Cu": {"name": "Copper",   "grad": "sphere-bronze",   "text": "#ffffff", "accent": "#b45309", "r": 32},
    "Ba": {"name": "Barium",   "grad": "sphere-teal",     "text": "#ffffff", "accent": "#0f766e", "r": 34},
}

DEFAULT_ATOM = {"name": "Atom", "grad": "sphere-blue", "text": "#ffffff", "accent": "#2563eb", "r": 28}


def _get_atom_info(symbol: str) -> dict[str, Any]:
    """Return visual rendering attributes for an element symbol."""
    clean = re.sub(r"[^A-Za-z]", "", symbol)
    return CPK_PALETTE.get(clean, DEFAULT_ATOM)


# ── 3D Sphere SVG Gradient Definitions ───────────────────────────────────────
SPHERE_DEFS = """
    <!-- 3D Atom Sphere Shading Gradients -->
    <radialGradient id="sphere-white" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="65%" stop-color="#e2e8f0"/>
      <stop offset="100%" stop-color="#94a3b8"/>
    </radialGradient>
    <radialGradient id="sphere-charcoal" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#64748b"/>
      <stop offset="60%" stop-color="#334155"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </radialGradient>
    <radialGradient id="sphere-red" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#fca5a5"/>
      <stop offset="55%" stop-color="#ef4444"/>
      <stop offset="100%" stop-color="#991b1b"/>
    </radialGradient>
    <radialGradient id="sphere-blue" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#93c5fd"/>
      <stop offset="55%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1e3a8a"/>
    </radialGradient>
    <radialGradient id="sphere-emerald" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#86efac"/>
      <stop offset="55%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#064e3b"/>
    </radialGradient>
    <radialGradient id="sphere-teal" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#5eead4"/>
      <stop offset="55%" stop-color="#0d9488"/>
      <stop offset="100%" stop-color="#115e59"/>
    </radialGradient>
    <radialGradient id="sphere-cyan" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#67e8f9"/>
      <stop offset="55%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#155e75"/>
    </radialGradient>
    <radialGradient id="sphere-purple" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#d8b4fe"/>
      <stop offset="55%" stop-color="#8b5cf6"/>
      <stop offset="100%" stop-color="#581c87"/>
    </radialGradient>
    <radialGradient id="sphere-gold" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="55%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#854d0e"/>
    </radialGradient>
    <radialGradient id="sphere-amber" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#fdba74"/>
      <stop offset="55%" stop-color="#f97316"/>
      <stop offset="100%" stop-color="#9a3412"/>
    </radialGradient>
    <radialGradient id="sphere-bronze" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#fed7aa"/>
      <stop offset="55%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#78350f"/>
    </radialGradient>
    <radialGradient id="sphere-slate" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#cbd5e1"/>
      <stop offset="55%" stop-color="#64748b"/>
      <stop offset="100%" stop-color="#334155"/>
    </radialGradient>
    
    <!-- Arrowhead markers -->
    <marker id="arrow-criss-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <marker id="arrow-criss-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
"""


def _detect_formula_crisscross(
    steps: list[str],
    final_equation: str,
    narration: str,
) -> bool:
    """Determine whether the scene is demonstrating the criss-cross method or formula writing."""
    combined = f"{' '.join(steps)} {final_equation} {narration}".lower()
    keywords = [
        "criss-cross", "criss cross", "valency", "valence", "polyatomic",
        "bracket", "charges balance", "neutrality", "chemical formula",
        "formula writing", "combining capacity", "cross-multiply", "ionic formula",
    ]
    if any(kw in combined for kw in keywords):
        return True

    # Check if steps look like ions or formula progression (e.g. X(+2) Y(-1))
    if any(re.search(r"\b[A-Z][a-z]?[\+\-\d\(\)]+", s) for s in steps):
        if not any("->" in s or "→" in s for s in steps):
            return True

    return False


def _extract_ions_from_context(
    steps: list[str],
    final_equation: str,
    narration: str,
) -> Tuple[dict[str, Any], dict[str, Any], str]:
    """Extract cation and anion details dynamically from text and chemical symbols."""
    combined = f"{' '.join(steps)} {final_equation} {narration}".lower()

    # Standard general chemical ions lookup
    ION_REGISTRY = {
        "aluminum": ({"symbol": "Al", "charge": "+3", "valency": 3, "name": "Aluminum", "grad": "sphere-slate", "color": "#64748b"}, 3),
        "alumin": ({"symbol": "Al", "charge": "+3", "valency": 3, "name": "Aluminum", "grad": "sphere-slate", "color": "#64748b"}, 3),
        "sodium": ({"symbol": "Na", "charge": "+1", "valency": 1, "name": "Sodium", "grad": "sphere-purple", "color": "#8b5cf6"}, 1),
        "calcium": ({"symbol": "Ca", "charge": "+2", "valency": 2, "name": "Calcium", "grad": "sphere-cyan", "color": "#06b6d4"}, 2),
        "magnesium": ({"symbol": "Mg", "charge": "+2", "valency": 2, "name": "Magnesium", "grad": "sphere-teal", "color": "#0d9488"}, 2),
        "potassium": ({"symbol": "K", "charge": "+1", "valency": 1, "name": "Potassium", "grad": "sphere-purple", "color": "#8b5cf6"}, 1),
        "iron": ({"symbol": "Fe", "charge": "+3", "valency": 3, "name": "Iron(III)", "grad": "sphere-amber", "color": "#d97706"}, 3),
        "copper": ({"symbol": "Cu", "charge": "+2", "valency": 2, "name": "Copper(II)", "grad": "sphere-cyan", "color": "#0284c7"}, 2),
        "zinc": ({"symbol": "Zn", "charge": "+2", "valency": 2, "name": "Zinc", "grad": "sphere-slate", "color": "#94a3b8"}, 2),
    }

    ANION_REGISTRY = {
        "sulfate": ({"symbol": "SO₄", "charge": "-2", "valency": 2, "name": "Sulfate", "grad": "sphere-gold", "color": "#d97706", "is_polyatomic": True}, 2),
        "chloride": ({"symbol": "Cl", "charge": "-1", "valency": 1, "name": "Chloride", "grad": "sphere-emerald", "color": "#10b981"}, 1),
        "hydroxide": ({"symbol": "OH", "charge": "-1", "valency": 1, "name": "Hydroxide", "grad": "sphere-teal", "color": "#0d9488", "is_polyatomic": True}, 1),
        "oxide": ({"symbol": "O", "charge": "-2", "valency": 2, "name": "Oxide", "grad": "sphere-red", "color": "#ef4444"}, 2),
        "nitrate": ({"symbol": "NO₃", "charge": "-1", "valency": 1, "name": "Nitrate", "grad": "sphere-blue", "color": "#3b82f6", "is_polyatomic": True}, 1),
        "carbonate": ({"symbol": "CO₃", "charge": "-2", "valency": 2, "name": "Carbonate", "grad": "sphere-amber", "color": "#f59e0b", "is_polyatomic": True}, 2),
    }

    detected_cation = None
    c_val = 2
    for k, (cat_info, v) in ION_REGISTRY.items():
        if k in combined or cat_info["symbol"].lower() in combined:
            detected_cation = cat_info
            c_val = v
            break

    detected_anion = None
    a_val = 1
    for k, (ani_info, v) in ANION_REGISTRY.items():
        if k in combined or ani_info["symbol"].lower() in combined:
            detected_anion = ani_info
            a_val = v
            break

    cation = detected_cation or {"symbol": "M", "charge": "+2", "valency": 2, "name": "Metal Cation", "grad": "sphere-teal", "color": "#0d9488"}
    anion = detected_anion or {"symbol": "X", "charge": "-1", "valency": 1, "name": "Anion", "grad": "sphere-emerald", "color": "#10b981"}

    # Dynamically compute formula from valencies
    if c_val == a_val:
        formula = f"{cation['symbol']}{anion['symbol']}"
    else:
        # Cross valencies
        c_sub = f"_{a_val}" if a_val > 1 else ""
        if anion.get("is_polyatomic") and c_val > 1:
            a_sub = f"({anion['symbol']})_{c_val}"
        else:
            a_sub = f"{anion['symbol']}_{c_val}" if c_val > 1 else anion["symbol"]
        formula = format_subscripts(f"{cation['symbol']}{c_sub}{a_sub}")

    return cation, anion, formula


def render_equation_build(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic, whiteboard-classroom formula/equation building animation to MP4."""
    payload = EquationBuildPayload.model_validate(payload_dict)

    steps = [format_subscripts(s) for s in (payload.steps or [payload.final_equation])]
    final_eq = format_subscripts(payload.final_equation or (steps[-1] if steps else ""))
    highlights = payload.atom_highlight or []
    num_steps = max(1, len(steps))

    # Detect whether this scene is teaching chemical formula building / criss-cross method
    is_crisscross = _detect_formula_crisscross(steps, final_eq, narration_text)

    if is_crisscross:
        return _render_crisscross_formula_scene(
            steps=steps,
            final_equation=final_eq,
            narration_text=narration_text,
            duration_seconds=duration_seconds,
            out_path=out_path,
            width=width,
            height=height,
        )
    else:
        return _render_reaction_equation_scene(
            steps=steps,
            final_equation=final_eq,
            highlights=highlights,
            narration_text=narration_text,
            duration_seconds=duration_seconds,
            out_path=out_path,
            width=width,
            height=height,
        )


# ── Mode 1: Criss-Cross Chemical Formula Builder ─────────────────────────────

def _render_crisscross_formula_scene(
    steps: list[str],
    final_equation: str,
    narration_text: str,
    duration_seconds: float,
    out_path: Path | None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render the Criss-Cross valency swap and charge balancing whiteboard animation."""
    cation, anion, compound_formula = _extract_ions_from_context(steps, final_equation, narration_text)
    
    cat_val = cation.get("valency", 2)
    ani_val = anion.get("valency", 1)
    is_polyatomic = anion.get("is_polyatomic", False) or "polyatomic" in narration_text.lower() or "bracket" in narration_text.lower()

    # Geometry coordinates centered on whiteboard stage
    cx = width // 2
    cat_x = cx - 210
    ani_x = cx + 210
    ions_y = 260
    assembled_y = 540

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # 3 Pedagogical Phases:
        # Phase 1 (0.0..0.35): Ions & valency charges introduced
        # Phase 2 (0.35..0.70): Criss-cross valency arrows swap positions
        # Phase 3 (0.70..1.0): Final compound formula assembled with charge cancellation check
        phase1_prog = max(0.0, min(1.0, progress / 0.35))
        cross_prog = max(0.0, min(1.0, (progress - 0.30) / 0.38))
        reveal_prog = max(0.0, min(1.0, (progress - 0.65) / 0.35))

        # Dynamic floating pulse
        pulse = 0.5 + 0.5 * math.sin(elapsed_ms * 0.007)
        dash_offset = (elapsed_ms * 0.04) % 30

        # Arrow 1: from Cation Valency (cat_x + 40, ions_y - 30) down-right to Anion Subscript (ani_x + 35, ions_y + 80)
        # Arrow 2: from Anion Valency (ani_x - 40, ions_y - 30) down-left to Cation Subscript (cat_x - 35, ions_y + 80)
        p1_x, p1_y = cat_x + 45, ions_y - 35
        d1_x, d1_y = ani_x + 40, ions_y + 90
        p2_x, p2_y = ani_x - 45, ions_y - 35
        d2_x, d2_y = cat_x - 40, ions_y + 90

        # Curved path coordinates
        curve1_ctrl_x, curve1_ctrl_y = cx + 20, ions_y + 10
        curve2_ctrl_x, curve2_ctrl_y = cx - 20, ions_y + 10

        # Interpolated arrow tip positions for active drawing
        arrow1_curr_x = (1 - cross_prog)**2 * p1_x + 2 * (1 - cross_prog) * cross_prog * curve1_ctrl_x + cross_prog**2 * d1_x
        arrow1_curr_y = (1 - cross_prog)**2 * p1_y + 2 * (1 - cross_prog) * cross_prog * curve1_ctrl_y + cross_prog**2 * d1_y

        arrow2_curr_x = (1 - cross_prog)**2 * p2_x + 2 * (1 - cross_prog) * cross_prog * curve2_ctrl_x + cross_prog**2 * d2_x
        arrow2_curr_y = (1 - cross_prog)**2 * p2_y + 2 * (1 - cross_prog) * cross_prog * curve2_ctrl_x + cross_prog**2 * d2_y

        # Animated valency number transfer
        val_cat_x = p1_x + (d1_x - p1_x) * cross_prog
        val_cat_y = p1_y + (d1_y - p1_y) * cross_prog

        val_ani_x = p2_x + (d2_x - p2_x) * cross_prog
        val_ani_y = p2_y + (d2_y - p2_y) * cross_prog

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  {SPHERE_DEFS}
  
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 36)">
    <rect width="270" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="800" letter-spacing="1">📐 CRISS-CROSS METHOD</text>
    
    <text x="0" y="72" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Writing Chemical Formulas: Combining Valencies
    </text>
    <text x="0" y="100" fill="#475569" font-family="system-ui, sans-serif" font-size="15" font-weight="500">
      Cross-multiplying ionic valencies guarantees that positive and negative charges balance to zero.
    </text>
  </g>

  <!-- Step Tracker Indicator -->
  <g transform="translate({width - 340}, 42)">
    <rect width="290" height="36" rx="18" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#card-shadow)"/>
    <circle cx="28" cy="18" r="8" fill="{"#2563eb" if phase1_prog > 0.2 else "#cbd5e1"}"/>
    <circle cx="98" cy="18" r="8" fill="{"#2563eb" if cross_prog > 0.2 else "#cbd5e1"}"/>
    <circle cx="168" cy="18" r="8" fill="{"#059669" if reveal_prog > 0.2 else "#cbd5e1"}"/>
    <text x="215" y="23" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="700">
      {"Step 1: Ions" if cross_prog < 0.2 else ("Step 2: Cross" if reveal_prog < 0.2 else "Step 3: Formula")}
    </text>
  </g>

  <!-- ── Main Visual Formula Arena Card ── -->
  <g transform="translate(50, 155)">
    <rect width="{width - 100}" height="320" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <!-- Arena Subtitle Pill -->
    <rect x="25" y="20" width="220" height="26" rx="13" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="135" y="37" fill="#475569" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">
      IONIC COMBINING CAPACITY
    </text>

    <!-- ── Left: Cation Node (e.g. Mg²⁺) ── -->
    <g transform="translate({cat_x - 50}, 120)">
      <!-- Outer glowing focus ring -->
      <circle cx="0" cy="0" r="54" fill="none" stroke="{cation.get('color', '#0d9488')}" stroke-width="2" stroke-dasharray="6 4" opacity="0.6"/>
      
      <!-- 3D Atom Sphere -->
      <circle cx="0" cy="0" r="46" fill="url(#{cation.get('grad', 'sphere-teal')})"/>
      
      <!-- Symbol Text -->
      <text x="0" y="10" fill="#ffffff" font-family="system-ui, sans-serif" font-size="28" font-weight="800" text-anchor="middle">
        {cation['symbol']}
      </text>
      
      <!-- Valency Superscript Badge (Top Right) -->
      <g transform="translate(36, -30)">
        <circle cx="0" cy="0" r="19" fill="#ffffff" stroke="#2563eb" stroke-width="2.2" filter="url(#badge-shadow)"/>
        <text x="0" y="6" fill="#2563eb" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle">
          {cation['charge']}
        </text>
      </g>

      <!-- Label -->
      <text x="0" y="75" fill="#0f172a" font-family="system-ui, sans-serif" font-size="15" font-weight="700" text-anchor="middle">
        {cation['name']}
      </text>
      <text x="0" y="95" fill="#2563eb" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">
        Valency = {cat_val}
      </text>
    </g>

    <!-- ── Right: Anion Node (e.g. Cl⁻ or [SO₄]²⁻) ── -->
    <g transform="translate({ani_x - 50}, 120)">
      <!-- Polyatomic ion bracket indicator if applicable -->
      {"".join([
          f'''<path d="M -58 -52 L -72 -52 L -72 52 L -58 52 M 58 -52 L 72 -52 L 72 52 L 58 52" 
                    fill="none" stroke="#7c3aed" stroke-width="3" stroke-linecap="round"/>'''
          if is_polyatomic else ""
      ])}

      <!-- Outer glowing focus ring -->
      <circle cx="0" cy="0" r="54" fill="none" stroke="{anion.get('color', '#10b981')}" stroke-width="2" stroke-dasharray="6 4" opacity="0.6"/>
      
      <!-- 3D Atom Sphere -->
      <circle cx="0" cy="0" r="46" fill="url(#{anion.get('grad', 'sphere-emerald')})"/>
      
      <!-- Symbol Text -->
      <text x="0" y="10" fill="#ffffff" font-family="system-ui, sans-serif" font-size="{24 if len(anion['symbol']) > 2 else 28}" font-weight="800" text-anchor="middle">
        {anion['symbol']}
      </text>
      
      <!-- Valency Superscript Badge (Top Right) -->
      <g transform="translate(36, -30)">
        <circle cx="0" cy="0" r="19" fill="#ffffff" stroke="#7c3aed" stroke-width="2.2" filter="url(#badge-shadow)"/>
        <text x="0" y="6" fill="#7c3aed" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle">
          {anion['charge']}
        </text>
      </g>

      <!-- Label -->
      <text x="0" y="75" fill="#0f172a" font-family="system-ui, sans-serif" font-size="15" font-weight="700" text-anchor="middle">
        {anion['name']}
      </text>
      <text x="0" y="95" fill="#7c3aed" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">
        Valency = {ani_val}
      </text>
    </g>

    <!-- ── Center: Dynamic Animated Criss-Cross Arrows ── -->
    {"".join([
        f'''
        <!-- Arrow 1: Cation valency -> Anion subscript -->
        <path d="M {cat_x + 10} 95 Q {cx - 50} 135 {ani_x - 15} 155" 
              fill="none" stroke="#2563eb" stroke-width="3" stroke-dasharray="8 5" 
              stroke-dashoffset="{dash_offset}" marker-end="url(#arrow-criss-blue)" opacity="{min(1.0, cross_prog * 1.5):.2f}"/>
              
        <!-- Arrow 2: Anion valency -> Cation subscript -->
        <path d="M {ani_x - 30} 95 Q {cx - 50} 135 {cat_x - 15} 155" 
              fill="none" stroke="#7c3aed" stroke-width="3" stroke-dasharray="8 5" 
              stroke-dashoffset="{-dash_offset}" marker-end="url(#arrow-criss-purple)" opacity="{min(1.0, cross_prog * 1.5):.2f}"/>
              
        <!-- Center Action Pill -->
        <rect x="{cx - 120}" y="120" width="140" height="32" rx="16" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
        <text x="{cx - 50}" y="141" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">
          CROSS VALENCY
        </text>
        '''
        if cross_prog > 0.05 else ""
    ])}
  </g>

  <!-- ── Bottom Section: Final Assembled Formula & Charge Balancing Check ── -->
  <g transform="translate(50, 495)">
    <!-- Main Result Container Card -->
    <rect width="{width - 100}" height="195" rx="18" fill="#ffffff" stroke="{"#059669" if reveal_prog > 0.4 else "#e2e8f0"}" stroke-width="2" filter="url(#card-shadow)"/>
    
    <!-- Left: Assembled Formula Callout -->
    <g transform="translate(40, 25)">
      <rect width="360" height="145" rx="14" fill="#f0fdf4" stroke="#059669" stroke-width="1.8"/>
      <text x="180" y="34" fill="#047857" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle" letter-spacing="1">
        FINAL BALANCED CHEMICAL FORMULA
      </text>
      
      <!-- Formula Display -->
      <text x="180" y="95" fill="#0f172a" font-family="system-ui, sans-serif" font-size="44" font-weight="800" text-anchor="middle" opacity="{reveal_prog:.2f}">
        {escape_xml(compound_formula)}
      </text>

      <text x="180" y="128" fill="#059669" font-family="system-ui, sans-serif" font-size="14" font-weight="700" text-anchor="middle">
        {"Electrically Neutral Compound ✓" if reveal_prog > 0.5 else "Subscripts represent combining ratio"}
      </text>
    </g>

    <!-- Right: Charge Balance Verification Math Card -->
    <g transform="translate(430, 25)">
      <rect width="{width - 570}" height="145" rx="14" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.5"/>
      <text x="30" y="34" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="800">
        ELECTRICAL NEUTRALITY VERIFICATION:
      </text>
      
      <!-- Balance Equation Line -->
      <text x="30" y="70" fill="#0f172a" font-family="system-ui, monospace" font-size="19" font-weight="700">
        Total (+) Charge: 1 × ({cation['charge']}) = +{cat_val}
      </text>
      <text x="30" y="98" fill="#0f172a" font-family="system-ui, monospace" font-size="19" font-weight="700">
        Total (-) Charge: {cat_val} × ({anion['charge']}) = -{cat_val}
      </text>
      
      <!-- Neutral outcome badge -->
      <g transform="translate(30, 114)">
        <rect width="360" height="24" rx="12" fill="#ecfdf5"/>
        <text x="10" y="17" fill="#059669" font-family="system-ui, sans-serif" font-size="12" font-weight="800">
          (+{cat_val}) + (-{cat_val}) = 0 Net Charge (Balanced &amp; Stable)
        </text>
      </g>
    </g>
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


# ── Mode 2: Progressive Chemical Reaction Equation & Molecule Assembler ─────

def _render_reaction_equation_scene(
    steps: list[str],
    final_equation: str,
    highlights: list[str],
    narration_text: str,
    duration_seconds: float,
    out_path: Path | None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render progressive chemical equation construction with molecular atom models."""
    num_steps = max(1, len(steps))

    # Parse primary elements for molecular model display
    detected_elements = [h for h in highlights if h in CPK_PALETTE]
    if not detected_elements:
        for symbol in ["Fe", "Cu", "Ba", "Na", "Cl", "S", "N", "Ca", "Mg", "Al", "C", "H", "O"]:
            # Match element symbol as whole token or followed by subscript/digit
            if re.search(r"\b" + symbol + r"(?:[\d₀-₉]|\b)", final_equation):
                detected_elements.append(symbol)

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        step_idx = min(num_steps - 1, int(progress * num_steps))
        current_eq = steps[step_idx]
        step_progress = (progress * num_steps) - step_idx
        reveal_alpha = min(1.0, step_progress * 2.5)

        # Draw atom sphere cluster tokens for the highlighted elements
        atoms_svg = []
        start_atom_x = 90
        for a_idx, elem in enumerate(detected_elements[:5]):
            ainfo = _get_atom_info(elem)
            ax = start_atom_x + a_idx * 180
            ay = 90

            atoms_svg.append(f"""
    <!-- Element Token {elem} -->
    <g transform="translate({ax}, {ay})">
      <!-- 3D Atom Sphere -->
      <circle cx="0" cy="0" r="30" fill="url(#{ainfo['grad']})" filter="url(#card-shadow)"/>
      <text x="0" y="8" fill="{ainfo['text']}" font-family="system-ui, sans-serif" font-size="20" font-weight="800" text-anchor="middle">
        {elem}
      </text>

      <text x="0" y="48" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">
        {ainfo['name']}
      </text>
      <rect x="-48" y="58" width="96" height="20" rx="10" fill="#ecfdf5" stroke="#a7f3d0" stroke-width="1"/>
      <text x="0" y="72" fill="#059669" font-family="system-ui, monospace" font-size="11" font-weight="800" text-anchor="middle">
        CONSERVED
      </text>
    </g>
""")

        has_bottom_stage = len(atoms_svg) > 0
        board_height = 300 if has_bottom_stage else 490
        board_eq_y = 140 if has_bottom_stage else 230
        desc_y = 235 if has_bottom_stage else 340

        bottom_svg = f"""
  <!-- ── Bottom Molecular Atom Inventory Stage ── -->
  <g transform="translate(50, 480)">
    <rect width="{width - 100}" height="205" rx="18" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#card-shadow)"/>
    
    <!-- Stage Header -->
    <text x="30" y="32" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="0.5">
      ATOMIC CONSTITUENTS &amp; CONSERVATION CONFIRMATION:
    </text>

    <!-- Atom Sphere Models -->
    {"".join(atoms_svg)}
  </g>
""" if has_bottom_stage else ""

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  {SPHERE_DEFS}

  <!-- Clean Canvas Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 36)">
    <rect width="260" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="800" letter-spacing="1">EQUATION BUILDER</text>
    
    <text x="0" y="72" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Chemical Equation Construction &amp; Balancing
    </text>
    <text x="0" y="100" fill="#475569" font-family="system-ui, sans-serif" font-size="15" font-weight="500">
      Progressive step-by-step assembly conforming to the Law of Conservation of Mass.
    </text>
  </g>

  <!-- Step Tracker Indicator -->
  <g transform="translate({width - 340}, 42)">
    <rect width="290" height="36" rx="18" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#card-shadow)"/>
    {"".join(
        f'<circle cx="{28 + i*30}" cy="18" r="7" fill="{"#2563eb" if i <= step_idx else "#cbd5e1"}"/>'
        for i in range(num_steps)
    )}
    <text x="{num_steps*30 + 38}" y="23" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="700">
      Step {step_idx + 1} of {num_steps}
    </text>
  </g>

  <!-- ── Main Equation Construction Board ── -->
  <g transform="translate(50, 155)">
    <rect width="{width - 100}" height="{board_height}" rx="20" fill="#ffffff" stroke="#2563eb" stroke-width="2" filter="url(#card-shadow)"/>

    <!-- Current Step Equation Text (Large, High Contrast, Centered) -->
    <g transform="translate({(width - 100) // 2}, {board_eq_y})" opacity="{reveal_alpha:.2f}">
      <rect x="-420" y="-55" width="840" height="95" rx="16" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="0" y="8" fill="#0f172a" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="800" text-anchor="middle" letter-spacing="0.8">
        {escape_xml(current_eq)}
      </text>
    </g>

    <!-- Subtitle descriptor banner -->
    <text x="{(width - 100) // 2}" y="{desc_y}" fill="#2563eb" font-family="system-ui, sans-serif" font-size="16" font-weight="700" text-anchor="middle" opacity="{reveal_alpha:.2f}">
      {"1. Identifying Reactants &amp; State Symbols" if step_idx == 0 else ("2. Specifying Reaction Conditions &amp; Intermediate Species" if step_idx == 1 and num_steps > 2 else "3. Final Balanced Equation (Mass &amp; Charge Conserved)")}
    </text>
  </g>
  {bottom_svg}
</svg>"""
        return svg

    return render_svg_frames_to_mp4(
        svg_generator=frame_gen,
        duration_seconds=duration_seconds,
        out_path=out_path,
        width=width,
        height=height,
    )
