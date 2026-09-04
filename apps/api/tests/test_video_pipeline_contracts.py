"""Regression tests for the diagram-first video pipeline contracts."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import agents.concept_animation as concept_animation
import skills.video_generation.factory as factory
import skills.video_generation.svg_templates.universal_diagram as diagram_engine
from skills.video_generation.base import VideoGenerationProvider, VisualBrief
from skills.video_generation.media import MediaValidationError
from skills.video_stitching import stitch_segment


class _BrokenProvider(VideoGenerationProvider):
    name = "broken"

    def generate(self, brief: VisualBrief, out_path: Path) -> str:
        out_path.write_bytes(b"partial render")
        return str(out_path)


class _WorkingProvider(VideoGenerationProvider):
    name = "working"

    def generate(self, brief: VisualBrief, out_path: Path) -> str:
        out_path.write_bytes(b"completed render")
        return str(out_path)


def test_factory_rejects_invalid_provider_output_before_fallback(monkeypatch, tmp_path):
    """A returned path is not success until its media stream is validated."""
    monkeypatch.setattr(factory, "_fallback_chain", lambda _: [_BrokenProvider(), _WorkingProvider()])

    def validate(path, **_kwargs):
        if Path(path).read_bytes() == b"partial render":
            raise MediaValidationError("invalid partial video")

    monkeypatch.setattr(factory, "require_playable_video", validate)
    path, provider = factory.generate_with_fallback(
        VisualBrief("Cell Cycle", "diagram", "A cell progresses through ordered phases."),
        tmp_path / "visual.mp4",
    )

    assert provider == "working"
    assert Path(path).read_bytes() == b"completed render"


def test_concept_animation_uses_audio_matched_duration(monkeypatch):
    """The planned visual should cover the spoken narration, not a fixed 15s."""
    captured: dict[str, VisualBrief] = {}

    def generate(brief, _out_path):
        captured["brief"] = brief
        return "/tmp/concept.mp4", "diagram"

    monkeypatch.setattr(concept_animation, "generate_with_fallback", generate)
    result = concept_animation.animate_segment(
        concept="Water Cycle",
        visual_type="diagram",
        narration_script="Evaporation, condensation, and precipitation form a cycle.",
        duration_seconds=27.4,
    )

    assert result["provider"] == "diagram"
    assert captured["brief"].duration_seconds == 27


def test_diagram_planning_is_immediate_without_a_configured_llm(monkeypatch):
    """Offline rendering retains a real deterministic diagram, not a blank clip."""
    monkeypatch.setattr(
        diagram_engine,
        "settings",
        SimpleNamespace(gemini_api_key="", groq_api_key="", diagram_plan_timeout_seconds=1),
    )
    spec = diagram_engine.plan_diagram("Offline Visual Contract", "A clear process with connected steps.")

    assert len(spec.nodes) >= 2
    assert spec.edges


def test_compositor_never_replaces_a_missing_diagram_with_the_avatar(tmp_path):
    """The original regression: an invalid diagram must fail visibly."""
    avatar = tmp_path / "avatar.mp4"
    avatar.write_bytes(b"not a real video")

    with pytest.raises(MediaValidationError, match="Media file is missing or empty"):
        stitch_segment(
            avatar_video_path=str(avatar),
            concept_video_path=str(tmp_path / "missing-diagram.mp4"),
            audio_path=str(tmp_path / "missing-audio.wav"),
        )
