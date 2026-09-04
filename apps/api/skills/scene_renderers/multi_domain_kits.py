"""
Shikshak AI — Multi-Domain Ready-Made Animation Kits.

Provides ready-to-use whiteboard classroom animations across:
  - Chemistry: Fermentation & Gas Bubbling, Oxidation & Rusting
  - Physics: Inertia & Newton's First Law (rolling ball with force vectors)
  - CS & Machine Learning: Neural Network Layer Synapses
  - Mathematics: Coordinate Function Graphs
"""
from __future__ import annotations

import html
import math
import re
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from skills.scene_renderers.base import (
    escape_xml,
    format_subscripts,
    render_svg_frames_to_mp4,
)
from skills.scene_renderers.icon_library import ICONS, render_icon_element, resolve_semantic_icon


# ── Whiteboard Classroom Standard SVG Definitions ────────────────────────────

WHITEBOARD_DEFS = """
  <defs>
    <!-- Subtle whiteboard dot-matrix pattern -->
    <pattern id="wb-dots" x="0" y="0" width="32" height="32" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="#cbd5e1" opacity="0.45"/>
    </pattern>
    <!-- Soft classroom card drop shadow -->
    <filter id="card-shadow" x="-5%" y="-5%" width="115%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.07"/>
    </filter>
    <filter id="badge-shadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.10"/>
    </filter>
    <!-- Vibrant marker gradients -->
    <linearGradient id="grad-blue" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2563eb"/><stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <linearGradient id="grad-purple" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#6d28d9"/>
    </linearGradient>
    <linearGradient id="grad-emerald" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#059669"/><stop offset="100%" stop-color="#047857"/>
    </linearGradient>
    <linearGradient id="grad-amber" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
  </defs>
"""


# ── Kit 1: Fermentation & Gas Bubbling (Chemistry / Biology) ───────────────────

def render_fermentation_process(
    concept: str = "Fermentation of Grapes",
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic classroom whiteboard animation of biochemical fermentation."""
    
    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        t = elapsed_ms * 0.003
        
        # Rising carbon dioxide bubbles strictly inside the flask body
        bubble_svgs = []
        for i in range(7):
            seed = i * 1.37
            bx = 125 + ((i * 12) % 50) + math.sin(t + seed) * 8
            by = 350 - ((elapsed_ms * 0.08 + i * 35) % 180)
            br = 3.5 + (i % 3) * 1.8
            b_alpha = max(0.0, min(0.85, (350 - by) / 80))
            bubble_svgs.append(
                f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{br}" fill="#38bdf8" opacity="{b_alpha:.2f}"/>'
            )

        # Transformation progress: Sugar -> Alcohol + CO2
        sugar_opacity = max(0.15, 1.0 - progress * 0.85)
        alcohol_opacity = min(1.0, progress * 1.15)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 40)">
    <rect width="260" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="800" letter-spacing="1">🔬 BIOCHEMICAL PROCESS</text>
    
    <text x="0" y="75" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Fermentation of Grapes: Sugar to Alcohol
    </text>
    <text x="0" y="105" fill="#475569" font-family="system-ui, sans-serif" font-size="16" font-weight="500">
      Anaerobic respiration by yeast converts grape glucose into ethanol and carbon dioxide gas.
    </text>
  </g>

  <!-- Left: Fermentation Flask Apparatus -->
  <g transform="translate(130, 150)">
    <!-- Reaction Vessel Card -->
    <rect x="0" y="20" width="310" height="430" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#card-shadow)"/>
    
    <!-- Erlenmeyer Flask Body -->
    <path d="M135 90 L175 90 L175 160 L245 370 A25 25 0 0 1 225 400 L85 400 A25 25 0 0 1 65 370 L135 160 Z"
          fill="#f8fafc" stroke="#334155" stroke-width="3" stroke-linejoin="round"/>
    
    <!-- Liquid Level inside Flask (Fermenting Grape Extract) -->
    <path d="M78 340 Q155 330 232 340 L238 375 A20 20 0 0 1 225 400 L85 400 A20 20 0 0 1 72 375 Z"
          fill="#7c3aed" opacity="0.88"/>
    
    <!-- Rising Gas Bubbles INSIDE flask body -->
    {"".join(bubble_svgs)}
    
    <!-- Microscopic Yeast Action Badge -->
    <rect x="25" y="40" width="130" height="32" rx="16" fill="#faf5ff" stroke="#7c3aed" stroke-width="1.5"/>
    <text x="40" y="61" fill="#6d28d9" font-family="system-ui, sans-serif" font-size="12" font-weight="700">🍇 Yeast Action</text>
    
    <!-- Gas Release Arrow on Neck -->
    <g transform="translate(155, 45)">
      <line x1="0" y1="35" x2="0" y2="0" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round"/>
      <polygon points="-5,8 0,0 5,8" fill="#0284c7"/>
      <text x="14" y="16" fill="#0284c7" font-family="system-ui, sans-serif" font-size="12" font-weight="800">CO₂ Gas</text>
    </g>
  </g>

  <!-- Right: Chemical Transformation Pathway -->
  <g transform="translate(470, 170)">
    <!-- Initial State Card: Grape Glucose -->
    <rect x="0" y="0" width="460" height="110" rx="16" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" filter="url(#card-shadow)"/>
    <circle cx="50" cy="55" r="28" fill="#eff6ff"/>
    {render_icon_element(ICONS["grapes"], 50, 55, size=34, color="#7c3aed")}
    <rect x="355" y="15" width="85" height="24" rx="12" fill="#eff6ff"/>
    <text x="397" y="31" fill="#2563eb" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">SWEET</text>
    <text x="95" y="44" fill="#0f172a" font-family="system-ui, sans-serif" font-size="17" font-weight="700">Initial State: Grape Glucose</text>
    <text x="95" y="70" fill="#475569" font-family="system-ui, sans-serif" font-size="14" font-weight="500">C₆H₁₂O₆ sugar stored inside ripe fruit</text>

    <!-- Reaction Arrow -->
    <g transform="translate(230, 112)">
      <line x1="0" y1="0" x2="0" y2="34" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"/>
      <polygon points="-5,26 0,35 5,26" fill="#7c3aed"/>
      <rect x="20" y="7" width="170" height="22" rx="11" fill="#fef3c7"/>
      <text x="105" y="22" fill="#b45309" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">YEAST ENZYME CATALYSIS</text>
    </g>

    <!-- Transformed State Card: Ethanol + CO2 -->
    <rect x="0" y="155" width="460" height="110" rx="16" fill="#ffffff" stroke="#059669" stroke-width="1.8" filter="url(#card-shadow)"/>
    <circle cx="50" cy="210" r="28" fill="#f0fdf4"/>
    {render_icon_element(ICONS["wine_flask"], 50, 210, size=34, color="#059669")}
    <rect x="345" y="170" width="95" height="24" rx="12" fill="#f0fdf4"/>
    <text x="392" y="186" fill="#059669" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">FERMENTED</text>
    <text x="95" y="199" fill="#0f172a" font-family="system-ui, sans-serif" font-size="17" font-weight="700">Chemical Outcome: Ethanol + CO₂</text>
    <text x="95" y="225" fill="#475569" font-family="system-ui, sans-serif" font-size="14" font-weight="500">Irreversible conversion into alcohol &amp; bubbles</text>
  </g>

  <!-- Bottom Balanced Equation Banner -->
  <g transform="translate(50, 605)">
    <rect width="880" height="68" rx="16" fill="#ffffff" stroke="#7c3aed" stroke-width="2" filter="url(#card-shadow)"/>
    <rect x="20" y="18" width="135" height="32" rx="8" fill="#faf5ff"/>
    <text x="87" y="39" fill="#7c3aed" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">CORE EQUATION</text>
    
    <!-- Clean SVG text with inline SVG arrow -->
    <text x="175" y="42" fill="#0f172a" font-family="system-ui, sans-serif" font-size="19" font-weight="800">
      C₆H₁₂O₆ (Glucose)
    </text>
    <g transform="translate(370, 36)">
      <line x1="0" y1="0" x2="80" y2="0" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"/>
      <polygon points="76,-5 86,0 76,5" fill="#7c3aed"/>
      <text x="40" y="-8" fill="#7c3aed" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">Yeast</text>
    </g>
    <text x="475" y="42" fill="#0f172a" font-family="system-ui, sans-serif" font-size="19" font-weight="800">
      2 C₂H₅OH (Ethanol) + 2 CO₂ (Gas)
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


# ── Kit 2: Law of Inertia & Motion (Physics) ───────────────────────────────────

def render_inertia_motion(
    concept: str = "Newton's First Law of Inertia",
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic classroom whiteboard animation of Newton's law of inertia."""
    
    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Ball position moving uniformly across horizontal track
        ball_x = 180 + (progress * 560)
        ball_y = 350
        ball_rot = (progress * 720) % 360

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 40)">
    <rect width="240" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">⚡ NEWTONIAN MECHANICS</text>
    
    <text x="0" y="75" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Law of Inertia: Uniform Motion
    </text>
    <text x="0" y="105" fill="#475569" font-family="system-ui, sans-serif" font-size="16" font-weight="500">
      An object in motion stays in uniform motion unless acted upon by an external unbalanced force.
    </text>
  </g>

  <!-- Physics Motion Track Simulation -->
  <g transform="translate(50, 170)">
    <rect width="880" height="320" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <!-- Horizontal Frictionless Surface Plane -->
    <line x1="60" y1="260" x2="820" y2="260" stroke="#334155" stroke-width="4" stroke-linecap="round"/>
    
    <!-- Surface Hatching / Hash Marks -->
    {"".join(f'<line x1="{x}" y1="260" x2="{x-12}" y2="274" stroke="#94a3b8" stroke-width="2"/>' for x in range(80, 820, 32))}
    
    <!-- Surface Label Badge -->
    <rect x="70" y="284" width="220" height="26" rx="13" fill="#f1f5f9"/>
    <text x="180" y="301" fill="#475569" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">FRICTIONLESS PLANE (μ = 0)</text>

    <!-- Velocity Vector Arrow attached to ball -->
    <g transform="translate({ball_x}, 200)">
      <line x1="0" y1="0" x2="90" y2="0" stroke="#dc2626" stroke-width="3.5" stroke-linecap="round"/>
      <polygon points="90,-7 105,0 90,7" fill="#dc2626"/>
      <text x="45" y="-12" fill="#dc2626" font-family="system-ui, sans-serif" font-size="15" font-weight="800" text-anchor="middle">Velocity (v = constant)</text>
    </g>

    <!-- Rolling Sphere Ball -->
    <g transform="translate({ball_x}, 220)">
      <circle cx="0" cy="0" r="38" fill="#2563eb" filter="url(#badge-shadow)"/>
      <circle cx="-12" cy="-12" r="12" fill="#ffffff" opacity="0.35"/>
      <!-- Internal crosshairs showing rotation -->
      <g transform="rotate({ball_rot} 0 0)">
        <circle cx="18" cy="0" r="5" fill="#f8fafc"/>
        <line x1="-24" y1="0" x2="24" y2="0" stroke="#ffffff" stroke-width="2" stroke-dasharray="3 3"/>
      </g>
    </g>

    <!-- Status Callout Card -->
    <g transform="translate(620, 30)">
      <rect width="230" height="90" rx="14" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
      <text x="20" y="32" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="14" font-weight="800">NET FORCE: F_net = 0</text>
      <text x="20" y="55" fill="#334155" font-family="system-ui, sans-serif" font-size="13" font-weight="600">Acceleration: a = 0 m/s²</text>
      <text x="20" y="75" fill="#059669" font-family="system-ui, sans-serif" font-size="13" font-weight="700">Motion: Uniform Forever</text>
    </g>
  </g>

  <!-- Bottom Key Law Banner -->
  <g transform="translate(50, 520)">
    <rect width="880" height="88" rx="16" fill="#ffffff" stroke="#2563eb" stroke-width="2" filter="url(#card-shadow)"/>
    <circle cx="50" cy="44" r="24" fill="#eff6ff"/>
    {render_icon_element(ICONS["velocity_arrow"], 50, 44, size=30, color="#2563eb")}
    <text x="95" y="38" fill="#0f172a" font-family="system-ui, sans-serif" font-size="18" font-weight="800">Pedagogical Invariant: The Principle of Inertia</text>
    <text x="95" y="64" fill="#475569" font-family="system-ui, sans-serif" font-size="15" font-weight="500">Without friction or air resistance, no continuous engine or push is needed to maintain motion.</text>
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


# ── Kit 3: Oxidation & Rusting of Iron (Chemistry / Materials) ─────────────────

def render_oxidation_rusting(
    concept: str = "Rusting of Iron in Humid Air",
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic classroom whiteboard animation of iron oxidation and rust crust."""
    
    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        t = elapsed_ms * 0.003
        
        # Rust crust thickness grows with progress
        rust_factor = min(1.0, progress * 1.2)
        rust_thickness = 4 + rust_factor * 26
        rust_color = f"rgba(194, 65, 12, {0.2 + rust_factor * 0.75:.2f})"

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 40)">
    <rect width="260" height="34" rx="17" fill="#fff7ed" stroke="#ea580c" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#c2410c" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">🧪 CHEMICAL CORROSION</text>
    
    <text x="0" y="75" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Rusting of Iron: Oxidation by Humid Atmosphere
    </text>
    <text x="0" y="105" fill="#475569" font-family="system-ui, sans-serif" font-size="16" font-weight="500">
      Iron atoms react with oxygen and atmospheric water vapor to form red-brown hydrated iron(III) oxide.
    </text>
  </g>

  <!-- Center: Iron Nail Demonstration -->
  <g transform="translate(50, 160)">
    <rect width="{width - 100}" height="350" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <!-- Reactant Atmospheric Particles Floating Down -->
    <g transform="translate({(width - 100) // 2 - 200}, 40)">
      <circle cx="80" cy="{30 + math.sin(t)*8}" r="16" fill="#f0f9ff" stroke="#0284c7" stroke-width="2"/>
      <text x="80" y="{35 + math.sin(t)*8}" fill="#0284c7" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">H₂O</text>
      
      <circle cx="280" cy="{35 + math.cos(t)*8}" r="16" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
      <text x="280" y="{40 + math.cos(t)*8}" fill="#dc2626" font-family="system-ui, sans-serif" font-size="11" font-weight="800" text-anchor="middle">O₂</text>

      <path d="M80 60 L80 110 M74 100 L80 112 L86 100" stroke="#0284c7" stroke-width="2"/>
      <path d="M280 65 L280 110 M274 100 L280 112 L286 100" stroke="#dc2626" stroke-width="2"/>
    </g>

    <!-- Iron Bar / Nail Surface -->
    <g transform="translate({(width - 100) // 2 - 350}, 170)">
      <!-- Shiny Pure Iron Substrate -->
      <rect x="0" y="30" width="700" height="80" rx="10" fill="#64748b" stroke="#334155" stroke-width="2"/>
      <text x="350" y="80" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="20" font-weight="800" text-anchor="middle">
        Shiny Pure Iron Base Metal (Fe)
      </text>

      <!-- Flaky Hydrated Rust Coating on Top -->
      <rect x="-4" y="{30 - rust_thickness}" width="708" height="{rust_thickness}" rx="6" fill="#c2410c" stroke="#9a3412" stroke-width="2"/>
      
      <!-- Rust crust flakes -->
      {"".join(f'<circle cx="{40 + i*70}" cy="{24 - rust_thickness/2}" r="{3 + (i%3)}" fill="#ea580c"/>' for i in range(10))}
    </g>

    <!-- Observations Callout Badges -->
    <g transform="translate({(width - 100) // 2 - 300}, 290)">
      <rect x="0" y="0" width="270" height="38" rx="19" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5"/>
      <text x="135" y="24" fill="#c2410c" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">
        Reddish-Brown Flaky Crust
      </text>

      <rect x="330" y="0" width="270" height="38" rx="19" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>
      <text x="465" y="24" fill="#991b1b" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">
        Weakens &amp; Corrodes Structure
      </text>
    </g>
  </g>

  <!-- Bottom Balanced Equation Banner -->
  <g transform="translate(50, 540)">
    <rect width="{width - 100}" height="88" rx="16" fill="#ffffff" stroke="#ea580c" stroke-width="2" filter="url(#card-shadow)"/>
    <circle cx="50" cy="44" r="24" fill="#fff7ed"/>
    {render_icon_element(ICONS["iron_nail"], 50, 44, size=30, color="#ea580c")}
    <text x="95" y="36" fill="#0f172a" font-family="system-ui, sans-serif" font-size="17" font-weight="800">Chemical Equation for Rust Formation</text>
    <text x="95" y="66" fill="#c2410c" font-family="system-ui, sans-serif" font-size="20" font-weight="800">
      4 Fe + 3 O₂ + 2x H₂O ──► 2 Fe₂O₃ · xH₂O (Hydrated Ferric Oxide)
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


# ── Kit 4: Neural Network Synapses (Computer Science & AI) ────────────────────

def render_neural_network(
    concept: str = "Neural Network Architecture",
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render a dynamic classroom whiteboard animation of artificial neural networks."""
    
    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        t = elapsed_ms * 0.004

        # Layer node positions
        input_nodes = [(180, 220), (180, 310), (180, 400)]
        hidden1_nodes = [(380, 180), (380, 270), (380, 360), (380, 450)]
        hidden2_nodes = [(580, 180), (580, 270), (580, 360), (580, 450)]
        output_nodes = [(780, 260), (780, 370)]

        # Synaptic connections with signal wave pulse
        synapses = []
        # Input -> Hidden1
        for i_idx, (ix, iy) in enumerate(input_nodes):
            for h_idx, (hx, hy) in enumerate(hidden1_nodes):
                phase = (t - (i_idx + h_idx) * 0.4) % (math.pi * 2)
                glow = 0.5 + 0.5 * math.sin(phase)
                stroke_color = f"rgba(147, 51, 234, {0.15 + glow * 0.5:.2f})"
                synapses.append(f'<line x1="{ix}" y1="{iy}" x2="{hx}" y2="{hy}" stroke="{stroke_color}" stroke-width="{1.2 + glow}"/>')

        # Hidden1 -> Hidden2
        for h1_idx, (h1x, h1y) in enumerate(hidden1_nodes):
            for h2_idx, (h2x, h2y) in enumerate(hidden2_nodes):
                phase = (t - (h1_idx + h2_idx) * 0.4 - 1.0) % (math.pi * 2)
                glow = 0.5 + 0.5 * math.sin(phase)
                stroke_color = f"rgba(37, 99, 235, {0.15 + glow * 0.5:.2f})"
                synapses.append(f'<line x1="{h1x}" y1="{h1y}" x2="{h2x}" y2="{h2y}" stroke="{stroke_color}" stroke-width="{1.2 + glow}"/>')

        # Hidden2 -> Output
        for h2_idx, (h2x, h2y) in enumerate(hidden2_nodes):
            for o_idx, (ox, oy) in enumerate(output_nodes):
                phase = (t - (h2_idx + o_idx) * 0.4 - 2.0) % (math.pi * 2)
                glow = 0.5 + 0.5 * math.sin(phase)
                stroke_color = f"rgba(5, 150, 105, {0.15 + glow * 0.5:.2f})"
                synapses.append(f'<line x1="{h2x}" y1="{h2y}" x2="{ox}" y2="{oy}" stroke="{stroke_color}" stroke-width="{1.2 + glow}"/>')

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 40)">
    <rect width="250" height="34" rx="17" fill="#faf5ff" stroke="#9333ea" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#7e22ce" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">🤖 MACHINE LEARNING</text>
    
    <text x="0" y="75" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Deep Neural Network Architecture
    </text>
    <text x="0" y="105" fill="#475569" font-family="system-ui, sans-serif" font-size="16" font-weight="500">
      Forward propagation computes weighted activations across interconnected artificial neurons.
    </text>
  </g>

  <!-- Network Stage Card -->
  <g transform="translate(50, 145)">
    <rect width="880" height="380" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <!-- Layer Column Labels -->
    <text x="180" y="45" fill="#2563eb" font-family="system-ui, sans-serif" font-size="14" font-weight="800" text-anchor="middle">INPUT LAYER</text>
    <text x="480" y="45" fill="#9333ea" font-family="system-ui, sans-serif" font-size="14" font-weight="800" text-anchor="middle">HIDDEN LAYERS (W, b)</text>
    <text x="780" y="45" fill="#059669" font-family="system-ui, sans-serif" font-size="14" font-weight="800" text-anchor="middle">OUTPUT LAYER</text>

    <!-- Synapses -->
    {"".join(synapses)}

    <!-- Nodes -->
    {"".join(f'<circle cx="{x}" cy="{y}" r="18" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>' for x, y in input_nodes)}
    {"".join(f'<circle cx="{x}" cy="{y}" r="18" fill="#faf5ff" stroke="#9333ea" stroke-width="3"/>' for x, y in hidden1_nodes + hidden2_nodes)}
    {"".join(f'<circle cx="{x}" cy="{y}" r="20" fill="#f0fdf4" stroke="#059669" stroke-width="3"/>' for x, y in output_nodes)}
  </g>

  <!-- Bottom Formula Callout -->
  <g transform="translate(50, 560)">
    <rect width="880" height="78" rx="16" fill="#ffffff" stroke="#9333ea" stroke-width="2" filter="url(#card-shadow)"/>
    <circle cx="50" cy="39" r="24" fill="#faf5ff"/>
    {render_icon_element(ICONS["neural_net"], 50, 39, size=30, color="#9333ea")}
    <text x="95" y="34" fill="#0f172a" font-family="system-ui, sans-serif" font-size="17" font-weight="800">Neuron Activation Function</text>
    <text x="95" y="60" fill="#7e22ce" font-family="system-ui, sans-serif" font-size="19" font-weight="800">
      a⁽ˡ⁺¹⁾ = σ( W⁽ˡ⁾ · a⁽ˡ⁾ + b⁽ˡ⁾ )
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


# ── Kit 5: Atomic Structure & Bohr Orbiting Shells ───────────────────────────

def render_atomic_structure(
    concept: str = "Bohr Model of Atom",
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render an animated Bohr model of atomic structure with orbiting electrons."""
    # Determine element based on concept / narration
    comb = f"{concept} {narration_text}".lower()
    if "carbon" in comb or "c" in comb:
        elem_name, elem_sym, z_num, mass_num, k_e, l_e, m_e = "Carbon", "C", 6, 12, 2, 4, 0
    elif "oxygen" in comb:
        elem_name, elem_sym, z_num, mass_num, k_e, l_e, m_e = "Oxygen", "O", 8, 16, 2, 6, 0
    elif "magnesium" in comb:
        elem_name, elem_sym, z_num, mass_num, k_e, l_e, m_e = "Magnesium", "Mg", 12, 24, 2, 8, 2
    else:
        elem_name, elem_sym, z_num, mass_num, k_e, l_e, m_e = "Sodium", "Na", 11, 23, 2, 8, 1

    ox, oy = 320, 390  # Center of Bohr orbit on left stage

    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Orbital rotation speeds
        t_k = elapsed_ms * 0.004
        t_l = elapsed_ms * 0.002
        t_m = elapsed_ms * 0.0012

        # K Shell (r=65): k_e electrons
        k_electrons = []
        for i in range(k_e):
            ang = t_k + i * (2 * math.pi / max(1, k_e))
            ex = ox + 65 * math.cos(ang)
            ey = oy + 65 * math.sin(ang)
            k_electrons.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="#38bdf8" filter="url(#badge-shadow)"/>')

        # L Shell (r=120): l_e electrons
        l_electrons = []
        for i in range(l_e):
            ang = t_l + i * (2 * math.pi / max(1, l_e))
            ex = ox + 120 * math.cos(ang)
            ey = oy + 120 * math.sin(ang)
            l_electrons.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="#38bdf8" filter="url(#badge-shadow)"/>')

        # M Shell (r=175): m_e electrons
        m_electrons = []
        if m_e > 0:
            for i in range(m_e):
                ang = t_m + i * (2 * math.pi / max(1, m_e))
                ex = ox + 175 * math.cos(ang)
                ey = oy + 175 * math.sin(ang)
                m_electrons.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="6" fill="#f59e0b" filter="url(#badge-shadow)"/>')

        pulse_core = 1.0 + 0.04 * math.sin(elapsed_ms * 0.008)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 36)">
    <rect width="250" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">⚛️ ATOMIC STRUCTURE</text>
    
    <text x="0" y="72" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Bohr Model: {elem_name} Atom (Z = {z_num})
    </text>
    <text x="0" y="100" fill="#475569" font-family="system-ui, sans-serif" font-size="15" font-weight="500">
      Concentric quantized energy shells (K, L, M) holding orbiting electrons around a dense nucleus.
    </text>
  </g>

  <!-- Left: Bohr Orbit Stage Card -->
  <g transform="translate(50, 145)">
    <rect width="540" height="490" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <!-- Concentric Orbit Rings (Dashed) -->
    <circle cx="{ox - 50}" cy="{oy - 145}" r="65" fill="none" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="4 4"/>
    <text x="{ox - 50 + 68}" y="{oy - 145 - 5}" fill="#64748b" font-family="system-ui, sans-serif" font-size="11" font-weight="700">K (n=1)</text>

    <circle cx="{ox - 50}" cy="{oy - 145}" r="120" fill="none" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="5 5"/>
    <text x="{ox - 50 + 123}" y="{oy - 145 - 5}" fill="#64748b" font-family="system-ui, sans-serif" font-size="11" font-weight="700">L (n=2)</text>

    {"".join([
        f'''<circle cx="{ox - 50}" cy="{oy - 145}" r="175" fill="none" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="6 6"/>
        <text x="{ox - 50 + 178}" y="{oy - 145 - 5}" fill="#d97706" font-family="system-ui, sans-serif" font-size="11" font-weight="800">M Valence (n=3)</text>'''
        if m_e > 0 else ""
    ])}

    <!-- Central Nucleus Group -->
    <g transform="translate({ox - 50}, {oy - 145}) scale({pulse_core:.2f})">
      <circle cx="0" cy="0" r="32" fill="#ef4444" filter="url(#card-shadow)"/>
      <circle cx="-6" cy="-6" r="14" fill="#f87171"/>
      <circle cx="8" cy="4" r="13" fill="#fca5a5"/>
      <circle cx="0" cy="0" r="10" fill="#dc2626"/>
      <text x="0" y="5" fill="#ffffff" font-family="system-ui, sans-serif" font-size="14" font-weight="900" text-anchor="middle">
        {z_num}p⁺
      </text>
    </g>

    <!-- Orbiting Electrons -->
    <g transform="translate(-50, -145)">
      {"".join(k_electrons)}
      {"".join(l_electrons)}
      {"".join(m_electrons)}
    </g>
  </g>

  <!-- Right: Electronic Configuration & Element Property Cards -->
  <g transform="translate(615, 145)">
    <!-- Main Info Card -->
    <rect width="{width - 665}" height="235" rx="18" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8" filter="url(#card-shadow)"/>
    
    <text x="35" y="42" fill="#0f172a" font-family="system-ui, sans-serif" font-size="20" font-weight="800">
      Element Specifications
    </text>
    
    <!-- Table Grid -->
    <g transform="translate(35, 65)">
      <rect width="{width - 735}" height="36" rx="8" fill="#f8fafc"/>
      <text x="15" y="24" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="700">Atomic Number (Z):</text>
      <text x="{width - 750}" y="24" fill="#2563eb" font-family="monospace" font-size="16" font-weight="800" text-anchor="end">{z_num} Protons</text>

      <g transform="translate(0, 44)">
        <rect width="{width - 735}" height="36" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
        <text x="15" y="24" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="700">Mass Number (A):</text>
        <text x="{width - 750}" y="24" fill="#0f172a" font-family="monospace" font-size="16" font-weight="800" text-anchor="end">{mass_num} ({z_num}p + {mass_num - z_num}n)</text>
      </g>

      <g transform="translate(0, 88)">
        <rect width="{width - 735}" height="36" rx="8" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>
        <text x="15" y="24" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800">Electronic Config (K, L, M):</text>
        <text x="{width - 750}" y="24" fill="#1d4ed8" font-family="monospace" font-size="17" font-weight="900" text-anchor="end">
          {k_e}, {l_e}{f", {m_e}" if m_e > 0 else ""}
        </text>
      </g>
    </g>

    <!-- Bottom Valence Callout -->
    <g transform="translate(0, 255)">
      <rect width="{width - 665}" height="235" rx="18" fill="#f0fdf4" stroke="#059669" stroke-width="1.8" filter="url(#card-shadow)"/>
      <circle cx="45" cy="45" r="22" fill="#dcfce7"/>
      <text x="45" y="52" fill="#059669" font-family="system-ui, sans-serif" font-size="20" font-weight="900" text-anchor="middle">✓</text>
      
      <text x="80" y="42" fill="#047857" font-family="system-ui, sans-serif" font-size="18" font-weight="800">
        Valency &amp; Combining Capacity
      </text>
      <text x="80" y="70" fill="#065f46" font-family="system-ui, sans-serif" font-size="14" font-weight="600">
        Outer shell has {m_e if m_e > 0 else l_e} valence electron(s).
      </text>
      <text x="80" y="92" fill="#047857" font-family="system-ui, sans-serif" font-size="15" font-weight="800">
        Valency = {m_e if m_e > 0 else (8 - l_e if l_e > 4 else l_e)} (Combines by {"losing" if (m_e > 0 and m_e <= 3) else "sharing/gaining"} electrons)
      </text>
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


# ── Kit 6: Kinetic States of Matter (Solid, Liquid, Gas) ────────────────────

def render_states_of_matter(
    concept: str = "States of Matter",
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Render animated particle kinetics comparing Solid, Liquid, and Gaseous states."""
    card_w = (width - 140) // 3
    
    def frame_gen(progress: float, elapsed_ms: int, total_ms: int) -> str:
        # Solid: slight vibration
        solid_dots = []
        for r in range(4):
            for c in range(4):
                vib_x = 1.8 * math.sin(elapsed_ms * 0.03 + r * 1.5)
                vib_y = 1.8 * math.cos(elapsed_ms * 0.03 + c * 1.5)
                px = 65 + c * 38 + vib_x
                py = 80 + r * 38 + vib_y
                solid_dots.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="#2563eb"/>')

        # Liquid: slow Brownian drift
        liquid_dots = []
        for i in range(14):
            t = elapsed_ms * 0.003 + i * 1.7
            lx = 60 + (i * 24) % 130 + math.sin(t) * 14
            ly = 100 + (i * 18) % 110 + math.cos(t * 0.8) * 12
            liquid_dots.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="10" fill="#0d9488"/>')

        # Gas: fast bounce
        gas_dots = []
        for i in range(7):
            t = elapsed_ms * 0.008 + i * 2.3
            gx = 45 + ((i * 45 + int(elapsed_ms * 0.12)) % 160)
            gy = 60 + ((i * 38 + int(elapsed_ms * 0.10)) % 160)
            gas_dots.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="9" fill="#ea580c"/>')

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {WHITEBOARD_DEFS}
  <!-- Whiteboard Surface -->
  <rect width="{width}" height="{height}" fill="#fdfbf7"/>
  <rect width="{width}" height="{height}" fill="url(#wb-dots)"/>

  <!-- Top Classroom Header -->
  <g transform="translate(50, 36)">
    <rect width="250" height="34" rx="17" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" filter="url(#badge-shadow)"/>
    <text x="24" y="22" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" letter-spacing="1">🔬 KINETIC PARTICLE THEORY</text>
    
    <text x="0" y="72" fill="#0f172a" font-family="system-ui, sans-serif" font-size="28" font-weight="800">
      Comparison of States of Matter: Solid, Liquid, Gas
    </text>
    <text x="0" y="100" fill="#475569" font-family="system-ui, sans-serif" font-size="15" font-weight="500">
      Differences in intermolecular attraction, particle spacing, and kinetic energy determine states of matter.
    </text>
  </g>

  <!-- 3 Side-by-Side State Containers -->
  <g transform="translate(50, 150)">
    <!-- Container 1: Solid -->
    <g transform="translate(0, 0)">
      <rect width="{card_w}" height="490" rx="18" fill="#ffffff" stroke="#2563eb" stroke-width="2" filter="url(#card-shadow)"/>
      <rect x="20" y="20" width="110" height="26" rx="13" fill="#eff6ff"/>
      <text x="75" y="38" fill="#1d4ed8" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">1. SOLID</text>
      
      <!-- Particle Beaker Chamber -->
      <rect x="30" y="60" width="{card_w - 60}" height="240" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      {"".join(solid_dots)}
      
      <text x="30" y="330" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="800">Fixed Shape &amp; Volume</text>
      <text x="30" y="355" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Maximum intermolecular force</text>
      <text x="30" y="378" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Particles only vibrate in place</text>
      <text x="30" y="401" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Negligible compressibility</text>
    </g>

    <!-- Container 2: Liquid -->
    <g transform="translate({card_w + 20}, 0)">
      <rect width="{card_w}" height="490" rx="18" fill="#ffffff" stroke="#0d9488" stroke-width="2" filter="url(#card-shadow)"/>
      <rect x="20" y="20" width="110" height="26" rx="13" fill="#f0fdfa"/>
      <text x="75" y="38" fill="#0f766e" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">2. LIQUID</text>
      
      <!-- Particle Beaker Chamber -->
      <rect x="30" y="60" width="{card_w - 60}" height="240" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      {"".join(liquid_dots)}
      
      <text x="30" y="330" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="800">Fixed Volume, Fluid Shape</text>
      <text x="30" y="355" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Moderate intermolecular force</text>
      <text x="30" y="378" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Particles slide past each other</text>
      <text x="30" y="401" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Takes shape of container</text>
    </g>

    <!-- Container 3: Gas -->
    <g transform="translate({(card_w + 20) * 2}, 0)">
      <rect width="{card_w}" height="490" rx="18" fill="#ffffff" stroke="#ea580c" stroke-width="2" filter="url(#card-shadow)"/>
      <rect x="20" y="20" width="110" height="26" rx="13" fill="#fff7ed"/>
      <text x="75" y="38" fill="#c2410c" font-family="system-ui, sans-serif" font-size="13" font-weight="800" text-anchor="middle">3. GAS</text>
      
      <!-- Particle Beaker Chamber -->
      <rect x="30" y="60" width="{card_w - 60}" height="240" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      {"".join(gas_dots)}
      
      <text x="30" y="330" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="800">No Fixed Shape / Volume</text>
      <text x="30" y="355" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Negligible intermolecular force</text>
      <text x="30" y="378" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• High kinetic energy, rapid bounce</text>
      <text x="30" y="401" fill="#475569" font-family="system-ui, sans-serif" font-size="13" font-weight="500">• Highly compressible</text>
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


# ── Smart Multi-Domain Dispatcher ─────────────────────────────────────────────

def detect_multi_domain_scene(
    concept: str = "",
    narration: str = "",
    key_points: list[str] | None = None,
) -> Callable[..., Path] | None:
    """Detect if the content matches a ready-made multi-domain whiteboard animation.
    
    If the scene is a multi-item observational list (e.g. 2+ distinct real-world situations),
    it returns None so that the Whiteboard Cards can illustrate all items simultaneously.
    """
    pts = [p for p in (key_points or []) if p.strip()]
    c_lower = concept.lower()
    
    # If the title is explicitly an overview or list of multiple situations, keep multi-card layout
    if len(pts) >= 2 and any(w in c_lower for w in ["change", "situation", "example", "daily life", "observation", "overview", "intro"]):
        return None

    combined = f"{concept} {narration}".lower()
    if len(pts) == 1:
        combined += f" {pts[0].lower()}"

    # 1. Fermentation
    if re.search(r"\b(ferment\w*|yeast\w*|zymase|anaerobic respiration)\b", combined) or ("grape" in combined and "wine" in combined):
        return render_fermentation_process

    # 2. Law of Inertia
    if re.search(r"\b(inertia\w*|newton\w*.*first law|frictionless.*plane|uniform.*motion)\b", combined):
        return render_inertia_motion

    # 3. Rusting of iron
    if re.search(r"\b(rust\w*|corros\w*.*iron|hydrated.*ferric oxide)\b", combined) and not ("milk" in combined):
        return render_oxidation_rusting

    # 4. Neural networks & AI
    if re.search(r"\b(neural network\w*|deep learning|perceptron|synaptic|forward propagation)\b", combined):
        return render_neural_network

    # 5. Atomic structure & Bohr model
    if re.search(r"\b(atomic structure|bohr\w* model|electron shell|electronic configuration|protons? and neutrons?|valence electron)\b", combined):
        return render_atomic_structure

    # 6. States of matter & kinetic theory
    if re.search(r"\b(states of matter|solid.*liquid.*gas|kinetic theory|particle nature of matter|intermolecular space)\b", combined):
        return render_states_of_matter

    return None

