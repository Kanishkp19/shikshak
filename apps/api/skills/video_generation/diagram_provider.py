"""
Shikshak AI — Deterministic Diagram Animation Provider.

Renders high-quality, collision-free educational diagrams and science visual kits.
Eliminates coordinate-guessing and text-overlapping by computing all geometry from
measured text length (Pillow) and topology algorithms.

Routes to:
  1. Bio Illustration Kit (BioIcons + radial cross-section callouts)
  2. Circuit Diagram Kit (IEC symbols + animated flowing current)
  3. Molecular Diagram Kit (RDKit 2D structures with bond highlights)
  4. Base Diagram Engine (flowchart, cycle, cross_section, comparison, hierarchy)
"""
from __future__ import annotations

import html
import os
import re
import subprocess
from pathlib import Path
from typing import Any

# Ensure Cairo native libraries are discoverable on macOS Homebrew
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")

import cairosvg

from skills.bio_illustration import (
    BIO_ASSET_PATHS,
    BioIllustrationRequest,
    render_bio_svg,
)
from skills.circuit_diagram import (
    CircuitComponent,
    CircuitConnection,
    CircuitDiagramSpec,
)
from skills.circuit_diagram.renderer import render_circuit_svg
from skills.diagram_engine.animator import animation_state
from skills.diagram_engine.layout import (
    layout_comparison,
    layout_cross_section,
    layout_cycle,
    layout_flowchart,
    layout_hierarchy,
)
from skills.diagram_engine.layout.common import LayoutResult, PositionedNode, center
from skills.diagram_engine.schemas import (
    ContentBlueprint,
    DiagramEdge,
    DiagramNode,
    DiagramSpec,
)
from skills.diagram_engine.style_tokens import STYLE
from skills.molecular_diagram import MolecularDiagramRequest, render_molecular_diagram
from skills.molecular_diagram.compound_lookup import NCERT_COMPOUND_SMILES
from skills.video_generation.base import (
    VideoGenerationProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
)
from skills.video_generation.media import require_playable_video
import uuid


def _detect_bio_structure(concept: str) -> str | None:
    c = concept.lower()
    if re.search(r"\b(chloroplast|photosynthesis|plant cell|thylakoid|stroma|grana|cell wall)\b", c):
        return "plant_cell"
    if re.search(r"\b(heart|cardiac|circulation|ventricle|atrium|aorta)\b", c):
        return "heart"
    if re.search(r"\b(neuron|nerve|synapse|axon|dendrite|myelin)\b", c):
        return "neuron"
    if re.search(r"\b(flower|petal|stamen|carpel|pistil|sepal|anther)\b", c):
        return "flower"
    if re.search(r"\b(animal cell|mitochondria|eukaryot|nucleus)\b", c):
        return "animal_cell"
    if re.search(r"\b(eye|vision|cornea|retina|lens|pupil|iris)\b", c):
        return "eye"
    if re.search(r"\b(nephron|kidney|glomerulus|bowman|renal)\b", c):
        return "nephron"
    if re.search(r"\b(dna|double helix|gene|nucleotide|chromosome)\b", c):
        return "dna"
    return None


def _detect_compound(concept: str) -> str | None:
    c = concept.lower()
    for name in NCERT_COMPOUND_SMILES:
        if name in c:
            return name
    return None


def _extract_nodes_from_brief(brief: VisualBrief, duration_ms: int) -> list[DiagramNode]:
    """Derive clean, measured DiagramNodes from concept and narration."""
    concept = brief.concept.strip()
    narration = brief.narration_script.strip()
    
    # Split sentences or key phrases
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", narration) if len(s.strip()) > 8]
    if not sentences:
        sentences = [concept]

    raw_labels: list[tuple[str, str | None]] = []
    # Primary node
    primary_label = concept[:28]
    raw_labels.append((primary_label, "Core Concept"))

    # Extract 3-5 process steps or aspects
    for s in sentences[:4]:
        words = s.split()
        if len(words) >= 2:
            lbl = " ".join(words[:3])[:28]
            sub = " ".join(words[3:8])[:35] if len(words) > 3 else None
            raw_labels.append((lbl, sub))

    nodes: list[DiagramNode] = []
    step = duration_ms / max(1, len(raw_labels))
    for idx, (lbl, sub) in enumerate(raw_labels):
        nodes.append(
            DiagramNode(
                id=f"node_{idx+1}",
                label=lbl or f"Step {idx+1}",
                sublabel=sub,
                node_type="concept" if idx == 0 else "process",
                highlight_at_ms=int(idx * step),
            )
        )
    return nodes


def _brief_to_blueprint(brief: VisualBrief, duration_ms: int) -> ContentBlueprint:
    spec_data = brief.diagram_spec or {}
    raw_nodes = spec_data.get("nodes", [])
    raw_edges = spec_data.get("edges", [])
    
    layout_name = spec_data.get("layout", "flowchart")
    if layout_name not in {"flowchart", "cross_section", "comparison", "hierarchy", "cycle"}:
        c_lower = brief.concept.lower()
        if any(k in c_lower for k in ("cycle", "calvin", "krebs", "water cycle", "circulation", "recycle")):
            layout_name = "cycle"
        elif any(k in c_lower for k in ("structure", "cross section", "anatomy", "parts")):
            layout_name = "cross_section"
        elif any(k in c_lower for k in ("versus", " vs ", "difference", "comparison", "compare")):
            layout_name = "comparison"
        elif any(k in c_lower for k in ("hierarchy", "classification", "types of", "taxonomy")):
            layout_name = "hierarchy"
        else:
            layout_name = "flowchart"

    nodes: list[DiagramNode] = []
    if raw_nodes:
        node_step = duration_ms / max(1, len(raw_nodes))
        for idx, n in enumerate(raw_nodes):
            nid = str(n.get("id") or f"node_{idx+1}")
            lbl = str(n.get("label") or f"Concept {idx+1}")
            sublbl = n.get("sublabel") or n.get("detail")
            if len(lbl) > 28:
                parts = lbl.split(" ")
                lbl = " ".join(parts[:3])[:28]
                if len(parts) > 3 and not sublbl:
                    sublbl = " ".join(parts[3:])[:35]
            if sublbl:
                sublbl = str(sublbl)[:38]

            node_type = n.get("node_type")
            if node_type not in {"concept", "input", "output", "process"}:
                node_type = "concept" if idx == 0 else "process"

            highlight = n.get("highlight_at_ms")
            if highlight is None:
                highlight = int(idx * node_step)

            nodes.append(
                DiagramNode(
                    id=nid,
                    label=lbl,
                    sublabel=sublbl,
                    node_type=node_type,
                    highlight_at_ms=highlight,
                )
            )
    else:
        nodes = _extract_nodes_from_brief(brief, duration_ms)

    edges: list[DiagramEdge] = []
    for e in raw_edges:
        src = e.get("source_id") or e.get("source") or e.get("from")
        tgt = e.get("target_id") or e.get("target") or e.get("to")
        if src and tgt:
            edges.append(DiagramEdge(source_id=str(src), target_id=str(tgt), label=e.get("label")))

    if not edges and len(nodes) > 1:
        if layout_name == "cross_section":
            for n in nodes[1:]:
                edges.append(DiagramEdge(source_id=nodes[0].id, target_id=n.id))
        elif layout_name == "cycle":
            for i in range(len(nodes)):
                edges.append(DiagramEdge(source_id=nodes[i].id, target_id=nodes[(i + 1) % len(nodes)].id))
        else:
            for i in range(len(nodes) - 1):
                edges.append(DiagramEdge(source_id=nodes[i].id, target_id=nodes[i + 1].id))

    return ContentBlueprint(
        segment_id="render-segment",
        narration_script=brief.narration_script or brief.concept,
        narration_duration_estimate_ms=duration_ms,
        diagram_spec=DiagramSpec(
            layout=layout_name,
            nodes=nodes,
            edges=edges,
            theme="light_textbook",
        ),
    )


def _svg_text(lines: tuple[str, ...], x: float, y: float, font_size: int, color: str, anchor: str = "middle") -> str:
    line_height = font_size + 4
    return "".join(
        f'<text x="{x:.1f}" y="{y + index * line_height:.1f}" text-anchor="{anchor}" '
        f'font-size="{font_size}" fill="{color}">{html.escape(line)}</text>'
        for index, line in enumerate(lines)
    )


def _render_edge(layout: LayoutResult, source_id: str, target_id: str, label: str | None, color: str, progress: float) -> str:
    source = layout.nodes.get(source_id)
    target = layout.nodes.get(target_id)
    if not source or not target:
        return ""
    x1, y1 = center(source)
    x2, y2 = center(target)
    end_x = x1 + (x2 - x1) * progress
    end_y = y1 + (y2 - y1) * progress
    label_svg = ""
    if label and progress > 0.75:
        label_svg = f'<text x="{(x1+x2)/2:.1f}" y="{(y1+y2)/2 - 7:.1f}" text-anchor="middle" font-size="12" fill="{color}">{html.escape(label)}</text>'
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{end_x:.1f}" y2="{end_y:.1f}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>{label_svg}'


def _render_node(positioned: PositionedNode, tokens: dict[str, object], opacity: float, active: bool) -> str:
    border = tokens["node_border_active"] if active else tokens["node_border"]
    glow = 'filter="url(#glow)"' if active else ""
    text_x = positioned.x + positioned.width / 2
    label_y = positioned.y + 26
    label = _svg_text(positioned.size.label.lines, text_x, label_y, int(tokens["font_size_label"]), str(tokens["text_color"]))
    sublabel = ""
    if positioned.size.sublabel:
        sub_y = label_y + positioned.size.label.height + 4
        sublabel = _svg_text(positioned.size.sublabel.lines, text_x, sub_y, int(tokens["font_size_sublabel"]), str(tokens["edge_color"]))
    return (
        f'<g opacity="{opacity:.3f}" {glow}>'
        f'<rect x="{positioned.x:.1f}" y="{positioned.y:.1f}" width="{positioned.width:.1f}" height="{positioned.height:.1f}" '
        f'rx="{tokens["corner_radius"]}" fill="{tokens["node_fill"]}" stroke="{border}" stroke-width="2"/>'
        f'{label}{sublabel}</g>'
    )


def _compute_layout_cached(spec: DiagramSpec) -> LayoutResult:
    layout_funcs = {
        "flowchart": layout_flowchart,
        "cross_section": layout_cross_section,
        "comparison": layout_comparison,
        "hierarchy": layout_hierarchy,
        "cycle": layout_cycle,
    }
    return layout_funcs[spec.layout](spec)


class DiagramProvider(VideoGenerationProvider):
    """Deterministic, collision-free diagram animation engine."""

    name: str = "diagram"

    def is_available(self) -> bool:
        return True

    def generate(
        self, request: VideoGenerationRequest | VisualBrief, out_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        if isinstance(request, VisualBrief):
            brief = request
        else:
            brief = VisualBrief(
                concept=request.concept,
                visual_type=request.visual_type,
                narration_script=request.narration_script,
                language=request.language,
                duration_seconds=int(round(getattr(request, "duration_seconds", 30.0) or 30)),
                diagram_spec=getattr(request, "diagram_spec", None),
                scenes=getattr(request, "scenes", None),
                depth=request.depth,
                segment_id=request.segment_id,
            )

        target_path = out_path or getattr(request, "out_path", None)
        if target_path is None:
            target_path = Path("/tmp/shikshak_concept") / f"diagram_{uuid.uuid4().hex}.mp4"
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        duration_seconds = max(3, int(round(brief.duration_seconds or 15)))
        duration_ms = duration_seconds * 1000

        source_fps = 24
        output_fps = 24
        total_frames = int(duration_seconds * source_fps)

        # ── Check for Science Visual Kits ────────────────────────────────────
        bio_structure = _detect_bio_structure(brief.concept) if brief.visual_type in ("bio_illustration", "diagram", "none") else None
        compound_name = _detect_compound(brief.concept) if brief.visual_type in ("molecular_structure", "diagram", "none") else None
        is_circuit = (
            brief.visual_type == "circuit_diagram"
            or bool(re.search(r"\b(circuit|resistor|ohm's law|ammeter|voltmeter)\b", brief.concept.lower()))
        )

        # ── Scene-First Architecture (Chemistry pack & domain scene renderers) ──
        scenes_list: list[dict[str, Any]] = []
        if brief.segment_id:
            try:
                from skills.supabase_persistence import list_scenes
                scenes_list = list_scenes(brief.segment_id)
            except Exception:
                pass

        if not scenes_list and brief.scenes and isinstance(brief.scenes, list) and len(brief.scenes) > 0:
            if isinstance(brief.scenes[0], dict) and brief.scenes[0].get("visual_mode"):
                scenes_list = brief.scenes

        if not scenes_list and brief.narration_script and not bio_structure and not is_circuit and not compound_name:
            try:
                from agents.scene_planning import plan_scenes_for_segment
                from skills.quality_gate import audit_scenes_for_segment
                raw = plan_scenes_for_segment(
                    concept=brief.concept,
                    level=brief.depth,
                    language=brief.language,
                    narration_script=brief.narration_script,
                )
                scenes_list = audit_scenes_for_segment(raw, concept=brief.concept)
            except Exception as e:
                print(f"[DiagramProvider] Scene planning fallback: {e}")

        if scenes_list and not bio_structure and not is_circuit and not compound_name:
            import shutil
            from agents.visual_selection import dispatch_scene_render
            from skills.video_stitching import concat_segments_with_transitions

            scene_paths: list[str] = []
            # Calculate speech-paced duration for each scene based on narration text
            scene_word_counts = [
                max(1, len((sc.get("narration_text") or sc.get("narration_span") or "").split()))
                for sc in scenes_list
            ]
            total_words = sum(scene_word_counts)
            total_dur = max(float(duration_seconds), float(len(scenes_list) * 3.0))

            for s_idx, sc in enumerate(scenes_list):
                # If explicit scene duration provided and reasonable, use it; otherwise distribute proportionally
                explicit_dur = float(sc.get("duration_seconds", 0))
                if explicit_dur >= 2.5:
                    sc_dur = explicit_dur
                elif total_words > 0:
                    sc_dur = max(3.0, round((scene_word_counts[s_idx] / total_words) * total_dur, 1))
                else:
                    sc_dur = max(3.0, total_dur / len(scenes_list))

                sc_out = Path("/tmp/shikshak_concept") / f"scene_{uuid.uuid4().hex}.mp4"
                rendered = dispatch_scene_render(sc, duration_seconds=sc_dur, out_path=sc_out)
                scene_paths.append(str(rendered))


            if len(scene_paths) == 1:
                shutil.copy(scene_paths[0], str(target_path))
            else:
                combined = concat_segments_with_transitions(scene_paths, transition="fade", transition_duration=0.4)
                shutil.copy(combined, str(target_path))

            require_playable_video(target_path, min_width=1280, min_height=720, min_duration_seconds=1.0)
            return VideoGenerationResult(
                video_url=str(target_path),
                provider=self.name,
                cache_hit=False,
            )


        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "image2pipe",
            "-vcodec", "png",
            "-framerate", str(source_fps),
            "-i", "-",
            "-r", str(output_fps),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "16",
            "-preset", "veryfast",
            "-movflags", "+faststart",
            "-t", str(duration_seconds),
            str(target_path),
        ]

        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        try:
            if bio_structure and BIO_ASSET_PATHS.get(bio_structure, Path()).is_file():
                # ── Bio Illustration Mode ──
                callout_nodes = _extract_nodes_from_brief(brief, duration_ms)
                req = BioIllustrationRequest(
                    structure=bio_structure,  # type: ignore
                    callouts=callout_nodes[1:6] if len(callout_nodes) > 1 else callout_nodes,
                    theme="light_textbook",
                )
                svg_str = render_bio_svg(req)
                png_bytes = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"), output_width=1280, output_height=720)
                for _ in range(total_frames):
                    proc.stdin.write(png_bytes)

            elif is_circuit:
                # ── Circuit Diagram Mode with Animated Current ──
                circuit_spec = CircuitDiagramSpec(
                    circuit_type="series",
                    components=[
                        CircuitComponent(id="b1", component_type="battery", label="12V Battery"),
                        CircuitComponent(id="r1", component_type="resistor", label="Resistor 100Ω"),
                        CircuitComponent(id="sw1", component_type="switch", state="closed", label="Switch"),
                        CircuitComponent(id="l1", component_type="bulb", label="Lamp"),
                    ],
                    connections=[
                        CircuitConnection(source_id="b1", target_id="r1"),
                        CircuitConnection(source_id="r1", target_id="sw1"),
                        CircuitConnection(source_id="sw1", target_id="l1"),
                        CircuitConnection(source_id="l1", target_id="b1"),
                    ],
                    highlight_current_path=True,
                )
                for frame_idx in range(total_frames):
                    elapsed_ms = int(frame_idx / source_fps * 1000)
                    svg_str = render_circuit_svg(circuit_spec, elapsed_ms=elapsed_ms, theme="light_textbook")
                    png_bytes = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"), output_width=1280, output_height=720)
                    proc.stdin.write(png_bytes)

            elif compound_name:
                # ── Molecular Structure Mode ──
                mol_req = MolecularDiagramRequest(compound_name=compound_name, theme="light_textbook")
                png_bytes = render_molecular_diagram(mol_req)
                for _ in range(total_frames):
                    proc.stdin.write(png_bytes)

            else:
                # ── Base Diagram Engine Mode (Collision-Free Auto-Layout) ──
                blueprint = _brief_to_blueprint(brief, duration_ms)
                tokens = STYLE[blueprint.diagram_spec.theme]
                layout = _compute_layout_cached(blueprint.diagram_spec)

                for frame_idx in range(total_frames):
                    at_ms = int(frame_idx / source_fps * 1000)
                    state = animation_state(blueprint, at_ms)
                    edge_svg = "".join(
                        _render_edge(layout, edge.source_id, edge.target_id, edge.label, str(tokens["edge_color"]), state.edge_progress)
                        for edge in layout.edges
                    )
                    node_svg = "".join(
                        _render_node(node, tokens, state.node_opacity.get(node_id, 1), node_id in state.active_node_ids)
                        for node_id, node in layout.nodes.items()
                    )
                    frame_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="{tokens["background"]}"/>
  {edge_svg}{node_svg}
</svg>'''
                    png_bytes = cairosvg.svg2png(bytestring=frame_svg.encode("utf-8"), output_width=1280, output_height=720)
                    proc.stdin.write(png_bytes)

            if proc.stdin is not None:
                proc.stdin.close()
            stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
            return_code = proc.wait(timeout=120)
            if return_code != 0:
                raise RuntimeError(f"Diagram ffmpeg encoding failed: {stderr[-500:]}")

        except Exception:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)
            target_path.unlink(missing_ok=True)
            raise

        require_playable_video(target_path, min_width=1280, min_height=720, min_duration_seconds=1.0)
        return VideoGenerationResult(
            video_url=str(target_path),
            provider=self.name,
            cache_hit=False,
        )
