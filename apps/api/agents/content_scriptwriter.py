"""
Shikshak AI — Content Scriptwriter Agent (v3).

Generates a **single unified ContentBlueprint** that contains BOTH:
  1. The teacher's narration script (rich, grounded spoken words)
  2. The matching animation specification (diagram nodes/edges/layout)

Both outputs are generated in a single LLM call so they are inherently
aligned — the diagram always illustrates exactly what the teacher is saying.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from pydantic import BaseModel, Field
from typing import Literal

from agents.llm import get_content_llm, get_animation_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.prompt_templating import SYSTEM_TEACHER


# ── Schema ───────────────────────────────────────────────────────────────────

class VisualNode(BaseModel):
    id: str
    label: str
    detail: str = ""
    color: str = "#38bdf8"


class VisualEdge(BaseModel):
    source: str = Field(alias="from", default="")
    target: str = Field(alias="to", default="")
    label: str = ""

    model_config = {"populate_by_name": True}


class SceneSpec(BaseModel):
    """One scene within a segment's animation."""
    scene_number: int = 1
    narration_text: str = ""
    scene_title: str = ""
    visual_nodes: list[VisualNode] = Field(default_factory=list)
    visual_edges: list[VisualEdge] = Field(default_factory=list)
    layout: str = "flowchart"
    duration_hint_seconds: float = 6.0


class DiagramSpecBlueprint(BaseModel):
    """The pre-computed DiagramSpec, matching the narration exactly."""
    layout: str = "flowchart"
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    title: str = "Concept Overview"
    formula: str = ""
    key_insight: str = ""


class ContentBlueprint(BaseModel):
    """The unified contract between narration and animation.

    Generated in a single LLM call to ensure alignment.
    """
    concept: str = ""
    full_narration_script: str = ""
    scenes: list[SceneSpec] = Field(default_factory=list)
    diagram_spec: DiagramSpecBlueprint = Field(default_factory=DiagramSpecBlueprint)


# ── Prompt ───────────────────────────────────────────────────────────────────

_SCENE_BLUEPRINT_PROMPT = """\
You are Shikshak, an elite, passionate master teacher explaining a lesson segment.
Your mission is to deliver an IN-DEPTH, highly pedagogical explanation that teaches
the student deeply and clearly, while coordinating matching animation visuals.

Concept to Teach: {concept}
Target Level: {level}
Language: {language}

Source Material (Textbook / Chapter Extracts for THIS topic):
{retrieved_chunks}

Generate a complete content blueprint with these requirements:

1. full_narration_script: The COMPLETE, thorough teaching narration spoken by the teacher ({target_words} words, ~180-260 words).
   - Speak with the clarity, enthusiasm, and precision of a world-class educator.
   - If this is an OVERVIEW or ROADMAP segment: Introduce the chapter's importance and clearly list the syllabus/topics we will study step by step.
   - If this is a SPECIFIC TOPIC segment: You MUST focus EXCLUSIVELY on "{concept}". Explain its definition, mechanisms, specific experimental observations (e.g. colour changes, gas evolution, precipitate, temperature shifts), and the exact formulas or equations found in the source material for THIS concept.
   - Ground your explanation strictly in the facts and equations of the source material provided above. DO NOT repeat unrelated examples from other topics.

2. scenes: Break this narration into 3-4 cohesive scenes (40-70 words per scene). For EACH scene:
   - narration_text: What the teacher says in this scene
   - scene_title: Clear title shown on screen (2-5 words)
   - visual_nodes: 2-4 diagram nodes that DIRECTLY illustrate what the narration describes.
     Each node has: id (n1, n2...), label (2-4 words), detail (one-line explanation), color (hex)
   - visual_edges: Directed connections showing causes, products, steps, or relationships (e.g. "reacts to form", "decomposes into", "releases", "causes")
   - layout: "flowchart" | "cycle" | "hierarchy" | "radial" | "timeline" | "comparison"

3. diagram_spec: A clean, consolidated diagram combining all key nodes and edges:
   - layout: best overall layout for this concept
   - nodes: array of unique nodes (id, label, icon emoji, color, detail)
   - edges: array of animated edges (from, to, label, animated=true)
   - title: diagram title (2-6 words)
   - formula: the primary equation or formula for THIS concept from the source material (e.g. "2FeSO₄ → Fe₂O₃ + SO₂ + SO₃", or "" if none)
   - key_insight: single-sentence high-yield takeaway for this concept

CRITICAL TEACHING RULES:
- Teach the SPECIFIC science of "{concept}": specific reactants, products, states, observations, and equations from the provided source text.
- The visual_nodes MUST directly correspond to the narration of this concept.
- Use vibrant, distinct colors: #38bdf8 (sky), #818cf8 (indigo), #34d399 (emerald), #f472b6 (pink), #fbbf24 (amber), #fb923c (orange), #a78bfa (violet), #22d3ee (cyan).
- Use relevant emoji icons: 🧪 chemistry, ⚡ energy, 🔄 reaction, 🔥 heat, 💡 insight, ⚖️ balance, 🧬 bio, 📐 math, 🛡️ protection.

Return ONLY valid JSON matching this schema:
{{
  "concept": "{concept}",
  "full_narration_script": "...",
  "scenes": [
    {{
      "scene_number": 1,
      "narration_text": "...",
      "scene_title": "...",
      "visual_nodes": [{{"id": "n1", "label": "...", "detail": "...", "color": "#38bdf8"}}],
      "visual_edges": [{{"from": "n1", "to": "n2", "label": "..."}}],
      "layout": "flowchart",
      "duration_hint_seconds": 6.0
    }}
  ],
  "diagram_spec": {{
    "layout": "flowchart",
    "nodes": [{{"id": "n1", "label": "...", "icon": "💡", "color": "#38bdf8", "detail": "..."}}],
    "edges": [{{"from": "n1", "to": "n2", "label": "...", "animated": true}}],
    "title": "...",
    "formula": "",
    "key_insight": "..."
  }}
}}
"""


# ── Generator ────────────────────────────────────────────────────────────────

def generate_content_blueprint(
    *,
    concept: str,
    level: str,
    language: str,
    retrieved_chunks: str,
    per_segment_words: int = 220,
) -> ContentBlueprint:
    """Generate a unified content blueprint for one segment.

    Returns both the narration script AND the matching diagram spec,
    generated together in a single LLM call for perfect alignment.
    """
    target_words = max(180, min(280, per_segment_words))
    prompt = SYSTEM_TEACHER.render() + "\n\n" + _SCENE_BLUEPRINT_PROMPT.format(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=retrieved_chunks,
        target_words=target_words,
    )

    llm = get_content_llm()

    try:
        blueprint = call_llm_with_retry(
            llm, prompt, ContentBlueprint, model_name="content_scriptwriter"
        )

        # Validate: ensure we got meaningful content
        if not blueprint.full_narration_script or len(blueprint.full_narration_script.strip()) < 20:
            blueprint.full_narration_script = _extract_narration_from_scenes(blueprint)

        # Validate: ensure diagram_spec has nodes
        if len(blueprint.diagram_spec.nodes) < 2:
            blueprint.diagram_spec = _build_diagram_from_scenes(blueprint, concept)

        # Ensure concept is set
        if not blueprint.concept:
            blueprint.concept = concept

        return blueprint

    except Exception as e:
        print(f"[content_scriptwriter] Blueprint generation failed: {e}; using fallback")
        return _fallback_blueprint(concept, level, language)


def _extract_narration_from_scenes(blueprint: ContentBlueprint) -> str:
    """Extract full narration from scene-level narration_text fields."""
    parts = [s.narration_text for s in blueprint.scenes if s.narration_text]
    if parts:
        return " ".join(parts)
    return blueprint.full_narration_script or ""


def _build_diagram_from_scenes(blueprint: ContentBlueprint, concept: str) -> DiagramSpecBlueprint:
    """Build a DiagramSpec by merging all visual_nodes/edges from scenes."""
    all_nodes: list[dict[str, Any]] = []
    all_edges: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    colors = ["#38bdf8", "#818cf8", "#34d399", "#f472b6", "#fbbf24", "#fb923c"]

    for scene in blueprint.scenes:
        for node in scene.visual_nodes:
            if node.id not in seen_ids:
                seen_ids.add(node.id)
                icon = next((c.upper() for c in node.label if c.isascii() and c.isalnum()), "•")
                all_nodes.append({
                    "id": node.id,
                    "label": node.label[:30],
                    "icon": icon,
                    "color": node.color or colors[len(all_nodes) % len(colors)],
                    "detail": node.detail[:60],
                })
        for edge in scene.visual_edges:
            all_edges.append({
                "from": edge.source,
                "to": edge.target,
                "label": edge.label,
                "animated": True,
            })

    if len(all_nodes) < 2:
        all_nodes = [
            {"id": "n1", "label": concept[:30], "icon": "💡", "color": "#38bdf8", "detail": "Core concept"},
            {"id": "n2", "label": "Mechanism", "icon": "⚙️", "color": "#818cf8", "detail": "How it works"},
            {"id": "n3", "label": "Applications", "icon": "🎯", "color": "#34d399", "detail": "Real-world observations"},
        ]
        all_edges = [
            {"from": "n1", "to": "n2", "label": "drives", "animated": True},
            {"from": "n2", "to": "n3", "label": "produces", "animated": True},
        ]

    return DiagramSpecBlueprint(
        layout=blueprint.scenes[0].layout if blueprint.scenes else "flowchart",
        nodes=all_nodes,
        edges=all_edges,
        title=concept[:50],
        key_insight=f"Mastering {concept} step by step.",
    )


def _fallback_blueprint(concept: str, level: str, language: str) -> ContentBlueprint:
    """Deterministic fallback when the LLM is completely unavailable."""
    narration = (
        f"Let us explore {concept} in detail. "
        f"In chemistry and science, understanding {concept} reveals the fundamental interactions "
        f"between substances and energy changes. "
        f"We will examine the reactants, the chemical equations, and the observable changes such as "
        f"precipitate formation, temperature evolution, and state transformations. "
        f"Let us break down each key component systematically."
    )

    scenes = [
        SceneSpec(
            scene_number=1,
            narration_text=f"Let us examine the core principles of {concept}.",
            scene_title=concept[:25],
            visual_nodes=[
                VisualNode(id="n1", label=concept[:25], detail="Core concept", color="#38bdf8"),
                VisualNode(id="n2", label="Reactants & Conditions", detail="Initial state", color="#818cf8"),
            ],
            visual_edges=[VisualEdge(**{"from": "n1", "to": "n2", "label": "involves"})],
            layout="flowchart",
            duration_hint_seconds=6.0,
        ),
        SceneSpec(
            scene_number=2,
            narration_text=f"Observe how chemical bonds rearrange to produce distinct products and observable energy changes.",
            scene_title="Reaction & Products",
            visual_nodes=[
                VisualNode(id="n3", label="Products & Energy", detail="Final transformed state", color="#34d399"),
            ],
            visual_edges=[VisualEdge(**{"from": "n2", "to": "n3", "label": "transforms into"})],
            layout="flowchart",
            duration_hint_seconds=6.0,
        ),
    ]

    diagram_spec = DiagramSpecBlueprint(
        layout="flowchart",
        nodes=[
            {"id": "n1", "label": concept[:30], "icon": "💡", "color": "#38bdf8", "detail": "Core concept"},
            {"id": "n2", "label": "Reactants", "icon": "🧪", "color": "#818cf8", "detail": "Initial substances"},
            {"id": "n3", "label": "Products & Energy", "icon": "⚡", "color": "#34d399", "detail": "Resulting substances"},
        ],
        edges=[
            {"from": "n1", "to": "n2", "label": "involves", "animated": True},
            {"from": "n2", "to": "n3", "label": "transforms into", "animated": True},
        ],
        title=concept[:50],
        key_insight=f"Understanding {concept} step by step.",
    )

    return ContentBlueprint(
        concept=concept,
        full_narration_script=narration,
        scenes=scenes,
        diagram_spec=diagram_spec,
    )
