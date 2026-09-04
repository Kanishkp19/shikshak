"""
Unit tests for the new video generation pipeline components:
- Universal Diagram Engine
- Edge TTS synthesis
- Concept Graph & Deep Dive Generation
"""
from pathlib import Path
import pytest
from skills.video_generation.svg_templates.universal_diagram import (
    plan_diagram,
    render_universal_diagram_svg,
    DiagramSpec,
    DiagramNode,
    DiagramEdge,
)
from skills.video_generation.diagram_provider import DiagramProvider
from skills.video_generation.base import VisualBrief
from skills.concept_graph import build_concept_graph, get_concept_graph_dict
from skills.tts_synthesis import synthesize_speech


def test_universal_diagram_plan_fallback():
    """Verify fallback spec generates valid nodes and edges for arbitrary topic."""
    spec = plan_diagram("Quantum Teleportation", "Information transfer using entangled photons", "advanced")
    assert len(spec.nodes) >= 2
    assert spec.title
    svg = render_universal_diagram_svg(1.0, 10.0, spec)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "1280" in svg
    assert "720" in svg


def test_universal_diagram_layouts():
    """Verify all layout algorithms render valid SVGs."""
    for layout in ["flowchart", "cycle", "hierarchy", "comparison", "timeline", "radial"]:
        spec = DiagramSpec(
            layout=layout,
            nodes=[
                DiagramNode(id="1", label="Node A", icon="A", color="#38bdf8", detail="Detail A"),
                DiagramNode(id="2", label="Node B", icon="B", color="#818cf8", detail="Detail B"),
                DiagramNode(id="3", label="Node C", icon="C", color="#34d399", detail="Detail C"),
            ],
            edges=[
                DiagramEdge(**{"from": "1", "to": "2", "label": "step 1"}),
                DiagramEdge(**{"from": "2", "to": "3", "label": "step 2"}),
            ],
            title=f"Test {layout}",
        )
        svg = render_universal_diagram_svg(2.0, 10.0, spec)
        assert "<svg" in svg
        assert f"Test {layout}" in svg


def test_edge_tts_synthesis(tmp_path):
    """Verify Edge TTS synthesizes a real playable wav file."""
    wav_path = synthesize_speech("Photosynthesis is how plants make food.", language="en")
    assert wav_path
    p = Path(wav_path)
    assert p.exists()
    assert p.stat().st_size > 1000  # Non-trivial audio file


def test_concept_graph():
    """Verify concept graph generates related concepts."""
    graph = build_concept_graph("Biology", "Cell Division", "intermediate")
    assert isinstance(graph.related, list)
    dict_list = get_concept_graph_dict("Biology", "Cell Division", "intermediate")
    assert isinstance(dict_list, list)
