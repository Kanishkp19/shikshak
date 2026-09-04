# SKILL: Diagram Animation Engine (Shikshak AI)

## Purpose

Generate deterministic, collision-free, visually consistent diagram animations for lesson segments — replacing ad-hoc hardcoded SVG coordinate scripts. This skill owns *all* diagram-type video output; it never calls a generative video model. Generative video (LTX-Video/CogVideoX) is handled by a separate provider for non-diagram b-roll only — see Section 5.

## Why this skill exists

The previous implementation hardcoded node (x, y) positions per diagram, which produced overlapping boxes and truncated text because nothing checked bounding boxes against available space or text length. This skill fixes the actual cause: no LLM output and no hardcoded script is allowed to specify pixel coordinates. A layout algorithm computes positions; content only specifies structure.

## Input contract: `ContentBlueprint`

One LLM call (Groq Llama-3.3-70B primary, Gemini Flash fallback) produces both narration and diagram structure together, so they can never drift out of sync.

```python
class DiagramNode(BaseModel):
    id: str
    label: str                      # must be <= 28 chars; longer concepts split into label + sublabel
    sublabel: str | None = None
    node_type: Literal["concept", "input", "output", "process"]
    highlight_at_ms: int | None = None   # when this node should glow/pulse, synced to narration

class DiagramEdge(BaseModel):
    source_id: str
    target_id: str
    label: str | None = None        # e.g. "excites", "produces"

class DiagramSpec(BaseModel):
    layout: Literal["flowchart", "cross_section", "comparison", "hierarchy", "cycle"]
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]
    theme: Literal["light_textbook", "dark_focus"] = "light_textbook"

class ContentBlueprint(BaseModel):
    segment_id: str
    narration_script: str
    narration_duration_estimate_ms: int
    diagram_spec: DiagramSpec
```

No `x`, `y`, `width`, or `height` field exists anywhere in this schema. That is deliberate — the LLM is structurally prevented from causing a layout bug, because it has no coordinate field to get wrong.

## Pipeline (zero LLM calls at render time)

```
ContentBlueprint (stored in Supabase, generated once)
        │
        ▼
[1] Auto-layout pass — networkx + a layered/DAG layout algorithm (Sugiyama-style,
    e.g. via `networkx.nx_agraph` with Graphviz `dot`, or a pure-Python port such as
    `grandalf`) computes non-overlapping (x, y, width, height) for every node,
    sizing each box from actual measured text width (Pillow `ImageFont.getlength`
    or equivalent) plus fixed padding — this is what guarantees no truncation and
    no overlap, not the choice of Cairo vs. any other renderer.
        │
        ▼
[2] Style application — every node/edge is styled from the ONE locked style token
    set for the whole project (Section 4) — never per-diagram ad-hoc colors/fonts.
        │
        ▼
[3] Frame rendering — CairoSVG renders each animation keyframe (fade-in per node
    at its `highlight_at_ms`, edge-draw animation, pulse on active node) to PNG
    frames at 24fps.
        │
        ▼
[4] TTS — Edge TTS (or XTTS-v2 if voice cloning is required) renders narration_script
    to a WAV, independently, in parallel with [1]-[3] since they don't depend on
    each other.
        │
        ▼
[5] FFmpeg compositing — frames + audio -> 1280x720 H.264 MP4, faststart flag for
    web playback.
```

## Style consistency enforcement (this is the part that stops it from looking generic/different-every-time)

Define exactly one style token file, loaded by every render call — never inline colors/fonts in a diagram-generation prompt or script:

```python
# skills/diagram_engine/style_tokens.py
STYLE = {
    "light_textbook": {
        "background": "#f6f5f4",
        "node_fill": "#ffffff",
        "node_border": "#e6e6e6",
        "node_border_active": "#0075de",
        "text_color": "#000000",
        "edge_color": "#615d59",
        "highlight_glow": "#62aef0",
        "font_family": "Inter",
        "font_size_label": 18,
        "font_size_sublabel": 13,
        "corner_radius": 12,
    },
    "dark_focus": {  # reserved for specific opt-in scenes only, never the default
        "background": "#0f172a",
        "node_fill": "#1e293b",
        "node_border": "#334155",
        "node_border_active": "#38bdf8",
        "text_color": "#f1f5f9",
        "edge_color": "#64748b",
        "highlight_glow": "#38bdf8",
        "font_family": "Inter",
        "font_size_label": 18,
        "font_size_sublabel": 13,
        "corner_radius": 12,
    },
}
```

Rule: `theme` defaults to `light_textbook` for every segment in a session unless explicitly overridden — this is what makes every video in one lesson (and across different lessons) look like the same product instead of a new random palette per generation.

## Layout templates (fixed algorithms, not LLM-improvised)

- `flowchart` — Sugiyama layered layout (top-to-bottom), for process/sequence content (photosynthesis steps, algorithm steps)
- `cross_section` — central large node (e.g. the cell/leaf outline) with satellite callout nodes connected by leader lines radiating outward — for anatomy/structure content
- `comparison` — fixed two-column layout, mirrored — for pros/cons, before/after
- `hierarchy` — tree layout (Reingold-Tilford algorithm) — for taxonomies, org structures, transformer architecture stacks
- `cycle` — circular layout, nodes evenly spaced on a ring — for cycles (Calvin cycle, water cycle, circuits)

Each is a fixed, tested layout function — the LLM only picks which one fits (`diagram_spec.layout` enum), it never invents a new layout.

## Section 5 — Where generative video (LTX-Video / CogVideoX) fits, and where it explicitly does not

This skill (diagram engine) handles 100% of labeled/structural content: cross-sections, process flows, comparisons, hierarchies, cycles, chemistry apparatus, circuits — anything with text labels or precise structure.

A **separate** provider (`skills/video_generation/hf_space_provider.py`) handles only unlabeled ambient/b-roll content the Visual Selection Agent tags as `visual_type: "ambient"` — teacher intro/outro cutaways, generic classroom/nature backdrop shots. It is never invoked for anything tagged `diagram`, `equation`, or `code`. This separation is enforced in the Visual Selection Agent's routing, not left to chance per-call.

```python
# skills/video_generation/factory.py
def get_video_provider(visual_type: str) -> VideoGenerationProvider:
    if visual_type == "ambient":
        return HFSpaceProvider(primary="LTX-Video", fallback="CogVideoX-2B")
    # diagram / equation / code / cross_section / cycle / etc. never reach here —
    # they are rendered by the Diagram Animation Engine directly, not through
    # the generative-video provider interface at all.
    raise ValueError(f"visual_type '{visual_type}' must route through the diagram engine, not a video provider")
```

## Directory structure

```
skills/diagram_engine/
├── schemas.py              # ContentBlueprint, DiagramSpec, DiagramNode, DiagramEdge
├── style_tokens.py         # the one locked style dict, per theme
├── layout/
│   ├── flowchart.py
│   ├── cross_section.py
│   ├── comparison.py
│   ├── hierarchy.py
│   └── cycle.py
├── text_measure.py         # Pillow-based text measurement -> box sizing, prevents truncation
├── renderer.py             # CairoSVG frame rendering, applies style_tokens + computed layout
├── animator.py             # keyframe/timing logic synced to narration_duration_estimate_ms
└── compositor.py           # ffmpeg audio+video merge

skills/video_generation/
├── base.py
├── hf_space_provider.py    # LTX-Video primary, CogVideoX-2B fallback — ambient b-roll only
├── manim_provider.py       # reserved for actual math/physics motion, separate from diagram_engine
└── factory.py
```

## Acceptance tests for this skill

1. Render 10 diagrams with 6-12 nodes each of varying label lengths (including one deliberately long label) — assert zero bounding-box overlaps and zero truncated text via automated pixel/box-boundary check.
2. Render the same `layout` type twice with different content — assert both use identical `style_tokens` values (regression test against style drift).
3. Confirm `visual_type: "diagram"` never reaches `hf_space_provider.py` in the routing logs — assert via `agent_run_logs` that diagram segments only ever invoke `diagram_engine`.
4. Confirm narration audio duration and rendered video duration are within 500ms of each other (sync check) for at least 5 segments.
