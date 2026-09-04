"""
Shikshak AI — Universal LLM-Driven SVG Diagram Engine.

Replaces all hardcoded topic-specific SVG templates (photosynthesis, physics, etc.)
with a single engine that works for ANY topic — from microorganisms to transformer
architectures, Class 1 to PhD level.

Pipeline:
  1. LLM (Gemini Flash) generates a structured DiagramSpec (JSON) from concept + narration
  2. Renderer converts DiagramSpec → animated SVG frames at time t
  3. Supports 6 layout algorithms: flowchart, cycle, hierarchy, comparison, timeline, radial
"""
from __future__ import annotations

import json
import math
import hashlib
import multiprocessing as mp
import queue
from typing import Any

from agents.llm import gemini_llm, groq_llm, get_animation_llm
from config import settings
from skills.json_schema_validation import call_llm_with_retry
from pydantic import BaseModel, Field


# ── Diagram Spec Schema ──────────────────────────────────────────────────────

class DiagramNode(BaseModel):
    id: str
    label: str
    icon: str = "📌"
    color: str = "#38bdf8"
    detail: str = ""


class DiagramEdge(BaseModel):
    source: str = Field(alias="from", default="")
    target: str = Field(alias="to", default="")
    label: str = ""
    animated: bool = True

    model_config = {"populate_by_name": True}


class DiagramSpec(BaseModel):
    layout: str = "flowchart"  # flowchart | cycle | hierarchy | comparison | timeline | radial
    nodes: list[DiagramNode] = Field(default_factory=list)
    edges: list[DiagramEdge] = Field(default_factory=list)
    title: str = "Concept Overview"
    formula: str = ""  # optional formula/equation
    key_insight: str = ""  # single-line takeaway


# ── LLM Diagram Planner ─────────────────────────────────────────────────────

_DIAGRAM_PLAN_PROMPT = """You are an expert educational diagram designer. Given a concept and narration,
produce a structured JSON diagram specification.

Concept: {concept}
Narration Context: {narration}
Difficulty Level: {level}

Return ONLY valid JSON matching this schema:
{{
  "layout": "flowchart" | "cycle" | "hierarchy" | "comparison" | "timeline" | "radial",
  "nodes": [
    {{"id": "n1", "label": "Short Label", "icon": "emoji", "color": "#hexcolor", "detail": "One-line explanation"}},
    ...
  ],
  "edges": [
    {{"from": "n1", "to": "n2", "label": "relationship verb", "animated": true}},
    ...
  ],
  "title": "Diagram Title",
  "formula": "optional equation like E=mc²",
  "key_insight": "Single sentence key takeaway"
}}

Rules:
- Use 4-7 nodes (not too few, not too many)
- Choose layout based on concept: cycles for biological processes, flowcharts for step-by-step,
  hierarchy for classification, comparison for pros/cons, timeline for historical, radial for central concept
- Use relevant emojis as icons (🧬 for DNA, ⚡ for energy, 🔄 for cycles, etc.)
- Use distinct, harmonious colors from this palette: #38bdf8 #818cf8 #34d399 #f472b6 #fbbf24 #fb923c #a78bfa #22d3ee
- Keep labels short (2-4 words max)
- Edges describe relationships (produces, requires, leads to, contains, etc.)
- formula field is optional — use only when a key equation is relevant
"""

# Cache to avoid re-planning identical concepts
_plan_cache: dict[str, DiagramSpec] = {}


def _diagram_plan_worker(
    result_queue: Any,
    prompt: str,
    use_gemini: bool,
    per_attempt_timeout: float,
) -> None:
    """Execute remote planning in an isolated process that can be cancelled."""
    try:
        if use_gemini:
            def llm(candidate_prompt: str) -> str:
                return gemini_llm(
                    candidate_prompt,
                    timeout_seconds=per_attempt_timeout,
                    try_backup_models=False,
                    fallback_to_groq=False,
                )
        else:
            def llm(candidate_prompt: str) -> str:
                return groq_llm(candidate_prompt, timeout_seconds=per_attempt_timeout)
        spec = call_llm_with_retry(llm, prompt, DiagramSpec, model_name="diagram_planner")
        result_queue.put(("ok", spec.model_dump(mode="json")))
    except Exception as exc:  # noqa: BLE001
        result_queue.put(("error", str(exc)))


def _plan_remote_diagram(
    *,
    prompt: str,
    use_gemini: bool,
    timeout_seconds: float,
) -> DiagramSpec:
    """Run remote planning with a hard deadline and no orphaned request work."""
    context = mp.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_diagram_plan_worker,
        args=(result_queue, prompt, use_gemini, max(1, timeout_seconds / 2)),
    )
    process.start()
    try:
        process.join(timeout=max(1, timeout_seconds))
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
            raise TimeoutError("Diagram planner exceeded its render-time budget")
        try:
            status, payload = result_queue.get(timeout=0.5)
        except queue.Empty as exc:
            raise RuntimeError("Diagram planner exited without a result") from exc
        if status != "ok":
            raise RuntimeError(f"Diagram planner failed: {payload}")
        return DiagramSpec.model_validate(payload)
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
        result_queue.close()
        result_queue.join_thread()


def plan_diagram(concept: str, narration_script: str, level: str = "intermediate") -> DiagramSpec:
    """Use LLM to generate a DiagramSpec for the given concept."""
    cache_key = hashlib.md5(f"{concept}|{narration_script[:100]}|{level}".encode()).hexdigest()
    if cache_key in _plan_cache:
        return _plan_cache[cache_key]

    prompt = _DIAGRAM_PLAN_PROMPT.format(
        concept=concept,
        narration=narration_script[:300],
        level=level,
    )

    try:
        # Without a configured LLM key, avoid a network retry on the render
        # request path. The deterministic fallback still produces a diagram
        # immediately and keeps the video pipeline responsive offline.
        if not (settings.gemini_api_key or settings.groq_api_key):
            raise RuntimeError("No LLM key configured for diagram planning")
        # Diagram generation is on the segment-render critical path. Remote
        # planning runs in a separate process so it can be stopped cleanly;
        # an unavailable model never leaves background work or blocks video.
        spec = _plan_remote_diagram(
            prompt=prompt,
            use_gemini=bool(settings.gemini_api_key),
            timeout_seconds=settings.diagram_plan_timeout_seconds,
        )
        # Ensure at least 2 nodes
        if len(spec.nodes) < 2:
            spec = _fallback_spec(concept, narration_script)
    except Exception:
        spec = _fallback_spec(concept, narration_script)

    _plan_cache[cache_key] = spec
    return spec


def _fallback_spec(concept: str, narration: str) -> DiagramSpec:
    """Create a reasonable fallback diagram when LLM fails."""
    # Extract key phrases from narration for node labels
    words = narration.split()
    chunks = []
    for i in range(0, min(len(words), 20), 5):
        chunk = " ".join(words[i:i+4])
        if chunk:
            chunks.append(chunk)

    nodes = [
        DiagramNode(id="n1", label=concept[:25], icon="💡", color="#38bdf8", detail="Core concept"),
        DiagramNode(id="n2", label="Key Process", icon="⚙️", color="#818cf8", detail="How it works"),
        DiagramNode(id="n3", label="Key Outcome", icon="🎯", color="#34d399", detail="What results"),
    ]
    if len(chunks) > 0:
        nodes[1].label = chunks[0][:25]
    if len(chunks) > 1:
        nodes[2].label = chunks[1][:25]

    edges = [
        DiagramEdge(**{"from": "n1", "to": "n2", "label": "drives", "animated": True}),
        DiagramEdge(**{"from": "n2", "to": "n3", "label": "produces", "animated": True}),
    ]
    return DiagramSpec(
        layout="flowchart",
        nodes=nodes,
        edges=edges,
        title=concept[:50],
        key_insight=f"Understanding {concept} step by step.",
    )


# ── SVG Renderer ─────────────────────────────────────────────────────────────

# Color palette for dark mode backgrounds
_BG_COLOR = "#0f172a"
_CARD_BG = "#1e293b"
_BORDER_SUBTLE = "#334155"
_TEXT_PRIMARY = "#ffffff"
_TEXT_SECONDARY = "#94a3b8"
_TEXT_MUTED = "#64748b"

# Layout calculators — return (x, y) positions for each node
def _layout_positions(spec: DiagramSpec, canvas_w: int = 1280, canvas_h: int = 720) -> list[tuple[float, float]]:
    """Calculate node positions based on layout type."""
    n = len(spec.nodes)
    if n == 0:
        return []

    # Usable area (accounting for header + footer)
    margin_top = 120
    margin_bottom = 80
    margin_x = 80
    usable_w = canvas_w - 2 * margin_x
    usable_h = canvas_h - margin_top - margin_bottom
    cx = canvas_w / 2
    cy = margin_top + usable_h / 2

    layout = spec.layout.lower()

    if layout == "cycle":
        # Circular arrangement
        r = min(usable_w, usable_h) * 0.35
        return [
            (cx + r * math.cos(2 * math.pi * i / n - math.pi / 2),
             cy + r * math.sin(2 * math.pi * i / n - math.pi / 2))
            for i in range(n)
        ]

    elif layout == "radial":
        # Central node + surrounding nodes
        positions = [(cx, cy)]
        r = min(usable_w, usable_h) * 0.33
        for i in range(1, n):
            angle = 2 * math.pi * (i - 1) / (n - 1) - math.pi / 2
            positions.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return positions

    elif layout == "hierarchy":
        # Top-down tree layout
        levels = max(1, int(math.ceil(math.log2(n + 1))))
        positions = []
        idx = 0
        for level in range(levels):
            nodes_in_level = min(2 ** level, n - idx)
            if nodes_in_level <= 0:
                break
            y = margin_top + (usable_h / (levels + 1)) * (level + 1)
            for j in range(nodes_in_level):
                x = margin_x + usable_w * (j + 0.5) / nodes_in_level
                positions.append((x, y))
                idx += 1
                if idx >= n:
                    break
        return positions

    elif layout == "comparison":
        # Two columns
        left_n = (n + 1) // 2
        right_n = n - left_n
        positions = []
        for i in range(left_n):
            y = margin_top + usable_h * (i + 0.5) / left_n
            positions.append((margin_x + usable_w * 0.25, y))
        for i in range(right_n):
            y = margin_top + usable_h * (i + 0.5) / right_n
            positions.append((margin_x + usable_w * 0.75, y))
        return positions

    elif layout == "timeline":
        # Horizontal timeline
        positions = []
        for i in range(n):
            x = margin_x + usable_w * (i + 0.5) / n
            y = cy + (30 if i % 2 == 0 else -30)  # zigzag for visual interest
            positions.append((x, y))
        return positions

    else:  # flowchart (default) — left to right with wrapping
        cols = min(n, 4)
        rows = math.ceil(n / cols)
        positions = []
        for i in range(n):
            row = i // cols
            col = i % cols
            x = margin_x + usable_w * (col + 0.5) / cols
            y = margin_top + usable_h * (row + 0.5) / rows
            positions.append((x, y))
        return positions


def _ease_in_out(t: float) -> float:
    """Smooth easing function for animations."""
    return t * t * (3 - 2 * t)


def _wrap_card_label(label: str, max_chars: int = 18) -> list[str]:
    """Return at most two readable title lines for a diagram card."""
    words = (label or "Concept").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
            if len(lines) == 2:
                break
        else:
            current = candidate
    if current and len(lines) < 2:
        lines.append(current)
    if len(lines) == 2 and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = f"{lines[-1][:max_chars - 1].rstrip()}…"
    return lines or ["Concept"]


def _node_card_svg(node: DiagramNode, x: float, y: float, opacity: float, pulse: float, card_w: int = 260, card_h: int = 120) -> str:
    """Render a single node card as SVG."""
    color = node.color or "#38bdf8"
    label = (node.label or "").replace("<", "&lt;").replace(">", "&gt;")[:30]
    detail = (node.detail or "").replace("<", "&lt;").replace(">", "&gt;")[:50]
    half_w = card_w / 2
    half_h = card_h / 2
    # Cairo does not reliably bundle color-emoji fonts. A deterministic letter
    # badge reads cleanly everywhere and avoids tofu-box glyphs in exported MP4s.
    icon = next((char.upper() for char in label if char.isascii() and char.isalnum()), "•")
    label_lines = _wrap_card_label(label)
    if len(label_lines) == 1:
        label_svg = f'''<text x="{-half_w + 68}" y="{-half_h + 42}" font-size="17" font-weight="bold"
            fill="{_TEXT_PRIMARY}" dominant-baseline="middle">{label_lines[0]}</text>'''
    else:
        label_svg = f'''<text x="{-half_w + 68}" y="{-half_h + 32}" font-size="15" font-weight="bold"
            fill="{_TEXT_PRIMARY}">{label_lines[0]}</text>
      <text x="{-half_w + 68}" y="{-half_h + 52}" font-size="15" font-weight="bold"
            fill="{_TEXT_PRIMARY}">{label_lines[1]}</text>'''
    return f"""
    <g transform="translate({x}, {y})" opacity="{opacity:.2f}">
      <rect x="{-half_w}" y="{-half_h}" width="{card_w}" height="{card_h}" rx="16"
            fill="{_CARD_BG}" stroke="{color}" stroke-width="2.5"/>
      <rect x="{-half_w + 16}" y="{-half_h + 16}" width="40" height="40" rx="10"
            fill="{color}" opacity="0.2"/>
      <text x="{-half_w + 36}" y="{-half_h + 42}" font-size="20" text-anchor="middle"
            fill="{_TEXT_PRIMARY}" dominant-baseline="middle">{icon}</text>
      {label_svg}
      <line x1="{-half_w + 16}" y1="{-half_h + 64}" x2="{half_w - 16}" y2="{-half_h + 64}"
            stroke="{_BORDER_SUBTLE}" stroke-width="1"/>
      <text x="{-half_w + 20}" y="{-half_h + 90}" font-size="13" fill="{_TEXT_SECONDARY}">{detail}</text>
      <circle cx="{half_w - 20}" cy="{-half_h + 38}" r="{6 * pulse}" fill="{color}" opacity="0.4"/>
    </g>"""


def _edge_svg(x1: float, y1: float, x2: float, y2: float, label: str, opacity: float, t: float, animated: bool = True) -> str:
    """Render an edge (connection) between two nodes."""
    label = (label or "").replace("<", "&lt;").replace(">", "&gt;")[:20]
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2

    # Animated dash offset
    dash_offset = (t * 30) % 20 if animated else 0

    # Calculate arrowhead
    dx = x2 - x1
    dy = y2 - y1
    length = max(1, math.sqrt(dx * dx + dy * dy))
    ux = dx / length
    uy = dy / length

    # Shorten line to not overlap node cards
    shorten = 70
    sx1 = x1 + ux * shorten
    sy1 = y1 + uy * shorten
    sx2 = x2 - ux * shorten
    sy2 = y2 - uy * shorten

    # Arrow points
    arrow_size = 10
    ax = sx2 - ux * arrow_size
    ay = sy2 - uy * arrow_size
    px = -uy * arrow_size * 0.5
    py = ux * arrow_size * 0.5

    return f"""
    <g opacity="{opacity:.2f}">
      <line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}"
            stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8,5"
            stroke-dashoffset="{dash_offset}" stroke-linecap="round"/>
      <polygon points="{sx2},{sy2} {ax + px},{ay + py} {ax - px},{ay - py}"
               fill="#38bdf8"/>
      <rect x="{mid_x - len(label) * 4}" y="{mid_y - 12}" width="{max(40, len(label) * 8)}" height="22"
            rx="6" fill="{_BG_COLOR}" stroke="{_BORDER_SUBTLE}" stroke-width="1"/>
      <text x="{mid_x}" y="{mid_y + 3}" font-size="11" fill="{_TEXT_MUTED}"
            text-anchor="middle">{label}</text>
    </g>"""


def render_universal_diagram_svg(
    t: float,
    total_duration: float,
    spec: DiagramSpec,
) -> str:
    """Render a complete animated SVG frame at time t (seconds).

    Features:
    - Progressive node reveal (staggered fade-in)
    - Animated edge paths with flowing dashes
    - Pulsing highlight on currently-revealed node
    - Professional dark-mode gradient background
    - Title banner + optional formula footer
    """
    p = min(1.0, max(0.0, t / max(1.0, total_duration)))
    n = len(spec.nodes)
    if n == 0:
        return _empty_frame_svg(spec.title)

    positions = _layout_positions(spec)
    pulse = 1.0 + 0.06 * math.sin(t * 3.5)

    # Stagger reveal: each node fades in over 1.5s, staggered by 1.0s
    reveal_interval = max(0.5, min(2.0, (total_duration * 0.6) / max(1, n)))
    node_opacities = []
    for i in range(n):
        start_t = 0.8 + i * reveal_interval
        node_opacity = min(1.0, max(0.0, (t - start_t) / 1.0))
        node_opacities.append(_ease_in_out(node_opacity))

    # Edges appear after both connected nodes are visible
    id_to_idx = {node.id: i for i, node in enumerate(spec.nodes)}

    # Clean title
    clean_title = (spec.title or "Concept Overview").replace("<", "&lt;").replace(">", "&gt;")[:60]
    clean_formula = (spec.formula or "").replace("<", "&lt;").replace(">", "&gt;")
    clean_insight = (spec.key_insight or "").replace("<", "&lt;").replace(">", "&gt;")[:80]

    # Build SVG
    svg_parts = [f'''<svg width="1280" height="720" viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg"
     style="background:{_BG_COLOR}; font-family: 'Helvetica Neue', Arial, sans-serif;">
  <defs>
    <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1a1f36"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1280" height="720" fill="url(#bgGrad)"/>

  <!-- Subtle grid dots -->''']

    # Add subtle background grid
    for gx in range(0, 1280, 60):
        for gy in range(0, 720, 60):
            svg_parts.append(f'  <circle cx="{gx}" cy="{gy}" r="0.8" fill="#1e293b" opacity="0.5"/>')

    # Header banner
    svg_parts.append(f'''
  <!-- Header Banner -->
  <g transform="translate(640, 50)">
    <rect x="-380" y="-28" width="760" height="56" rx="28" fill="{_CARD_BG}"
          stroke="url(#headerGrad)" stroke-width="2"/>
    <text x="0" y="7" font-size="24" font-weight="bold" fill="{_TEXT_PRIMARY}"
          text-anchor="middle" letter-spacing="0.5">{clean_title}</text>
  </g>''')

    # Render edges first (below nodes)
    for edge in spec.edges:
        src_idx = id_to_idx.get(edge.source, id_to_idx.get(edge.target, 0))
        tgt_idx = id_to_idx.get(edge.target, id_to_idx.get(edge.source, 0))
        if src_idx < len(positions) and tgt_idx < len(positions):
            edge_opacity = min(node_opacities[src_idx], node_opacities[tgt_idx]) * 0.8
            x1, y1 = positions[src_idx]
            x2, y2 = positions[tgt_idx]
            svg_parts.append(_edge_svg(x1, y1, x2, y2, edge.label, edge_opacity, t, edge.animated))

    # Render nodes
    for i, node in enumerate(spec.nodes):
        if i < len(positions):
            x, y = positions[i]
            svg_parts.append(_node_card_svg(node, x, y, node_opacities[i], pulse))

    # Footer — formula or insight
    footer_text = clean_formula or clean_insight or "Shikshak AI · Universal Concept Engine"
    footer_opacity = min(1.0, max(0.0, (t - 1.0) / 1.0))
    svg_parts.append(f'''
  <!-- Footer -->
  <g transform="translate(640, 680)" opacity="{footer_opacity:.2f}">
    <rect x="-440" y="-20" width="880" height="40" rx="10" fill="{_CARD_BG}"
          stroke="{_BORDER_SUBTLE}" stroke-width="1"/>
    <text x="0" y="5" font-size="15" font-weight="500" fill="{_TEXT_SECONDARY}"
          text-anchor="middle">{footer_text}</text>
  </g>

</svg>''')

    return "\n".join(svg_parts)


def _empty_frame_svg(title: str) -> str:
    """Fallback SVG when no nodes are available."""
    clean = (title or "Loading…").replace("<", "&lt;").replace(">", "&gt;")
    return f'''<svg width="1280" height="720" viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg"
     style="background:{_BG_COLOR}; font-family: 'Helvetica Neue', Arial, sans-serif;">
  <rect width="1280" height="720" fill="{_BG_COLOR}"/>
  <text x="640" y="360" font-size="28" font-weight="bold" fill="{_TEXT_PRIMARY}"
        text-anchor="middle">{clean}</text>
</svg>'''
