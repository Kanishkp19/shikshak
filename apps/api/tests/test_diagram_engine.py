"""Acceptance coverage for the deterministic Diagram Animation Engine."""
from __future__ import annotations

import inspect
import subprocess

import pytest

from skills.diagram_engine import ContentBlueprint, DiagramEdge, DiagramNode, DiagramSpec
from skills.diagram_engine.compositor import audio_duration_ms, compose_video
from skills.diagram_engine.layout.common import assert_no_overlaps
from skills.diagram_engine.renderer import compute_layout, render_frame, render_svg
from skills.diagram_engine.style_tokens import STYLE


def _blueprint(layout: str, count: int, segment_id: str = "segment") -> ContentBlueprint:
    nodes = [
        DiagramNode(
            id=f"node-{index}",
            label="Deliberately long label" if index == 0 else f"Measured node {index}",
            sublabel="Supporting explanation" if index % 2 else None,
            node_type="process",
            highlight_at_ms=index * 100,
        )
        for index in range(count)
    ]
    edges = [DiagramEdge(source_id=nodes[index].id, target_id=nodes[index + 1].id, label="leads to") for index in range(count - 1)]
    return ContentBlueprint(
        segment_id=segment_id,
        narration_script="A deterministic explanation.",
        narration_duration_estimate_ms=700,
        diagram_spec=DiagramSpec(layout=layout, nodes=nodes, edges=edges),
    )


@pytest.mark.parametrize("layout,count", [
    ("flowchart", 12), ("hierarchy", 10), ("comparison", 10), ("cross_section", 6), ("cycle", 6),
    ("flowchart", 8), ("hierarchy", 7), ("comparison", 6), ("cross_section", 7), ("cycle", 7),
])
def test_measured_layouts_have_no_overlap_or_truncated_labels(layout, count):
    blueprint = _blueprint(layout, count)
    computed = compute_layout(blueprint.diagram_spec)
    assert_no_overlaps(computed.nodes.values())
    for positioned in computed.nodes.values():
        measured = positioned.size
        # The text-measurement utility wraps rather than truncates labels.
        assert " ".join(measured.label.lines) == positioned.node.label
        assert measured.label.width <= positioned.width - 2 * 24 + 0.01
        if measured.sublabel:
            assert measured.sublabel.width <= positioned.width - 2 * 24 + 0.01
    png = render_frame(blueprint)
    assert png.startswith(b"\x89PNG")
    assert len(png) > 1_000


def test_same_layout_uses_locked_style_tokens_for_different_content():
    first = _blueprint("flowchart", 6, "first")
    second = _blueprint("flowchart", 7, "second")
    first_svg = render_svg(first)
    second_svg = render_svg(second)
    tokens = STYLE["light_textbook"]
    for value in (tokens["background"], tokens["node_fill"], tokens["node_border"], tokens["text_color"]):
        assert value in first_svg
        assert value in second_svg


def test_diagram_engine_has_no_generative_video_provider_dependency():
    import skills.diagram_engine.animator as animator
    import skills.diagram_engine.compositor as compositor
    import skills.diagram_engine.renderer as renderer

    source = "\n".join(inspect.getsource(module) for module in (animator, compositor, renderer))
    assert "skills.video_generation" not in source
    assert "hf_space_provider" not in source


@pytest.mark.parametrize("index", range(5))
def test_video_duration_matches_tts_audio_within_500ms(tmp_path, index):
    audio = tmp_path / f"narration-{index}.wav"
    output = tmp_path / f"diagram-{index}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "0.55", str(audio)],
        check=True, capture_output=True,
    )
    compose_video(_blueprint("flowchart", 6, f"sync-{index}"), audio, output)
    assert output.exists() and output.stat().st_size > 1_000
    assert abs(audio_duration_ms(audio) - audio_duration_ms(output)) <= 500
