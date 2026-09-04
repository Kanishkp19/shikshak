"""
Test suite for Content Scriptwriter agent and the Dual-Output Video Pipeline.

Verifies:
1. Content generation & script generation for the video (Output 1: Narration Script)
2. Matching animation definition (Output 2: DiagramSpec / Animation Video)
3. Both outputs are generated together and aligned on topic
4. Render pipeline works deterministically with pre-computed diagram_spec (0 LLM calls)
5. Generated video is playable, 1280x720, with correct duration
"""
import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.content_scriptwriter import (
    generate_content_blueprint,
    ContentBlueprint,
    _fallback_blueprint,
)
from agents.explanation import explain_segment_with_blueprint, explain_segment
from skills.video_generation.base import VisualBrief
from skills.video_generation.diagram_provider import DiagramProvider
from skills.video_generation.media import require_playable_video, require_playable_audio
from skills.tts_synthesis import synthesize_speech


def test_fallback_blueprint_structure():
    """Verify fallback blueprint generates aligned narration and diagram spec."""
    bp = _fallback_blueprint("Quantum Entanglement", "intermediate", "en")
    assert isinstance(bp, ContentBlueprint)
    assert bp.concept == "Quantum Entanglement"
    assert "Quantum Entanglement" in bp.full_narration_script
    assert len(bp.scenes) >= 2
    assert len(bp.diagram_spec.nodes) >= 2
    assert len(bp.diagram_spec.edges) >= 1
    # Check that diagram title matches concept
    assert "Quantum Entanglement" in bp.diagram_spec.title


def test_explain_segment_with_blueprint():
    """Verify explain_segment_with_blueprint returns dual outputs."""
    result = explain_segment_with_blueprint(
        concept="Photosynthesis Light Reactions",
        level="beginner",
        language="en",
        retrieved_chunks=None,
        per_segment_words=150,
    )
    assert "narration_script" in result
    assert "diagram_spec" in result
    assert "scenes" in result
    assert len(result["narration_script"]) > 20
    assert len(result["diagram_spec"]["nodes"]) >= 2


def test_explain_segment_backward_compat():
    """Verify legacy explain_segment returns str narration."""
    script = explain_segment(
        concept="Black Holes and Event Horizons",
        level="intermediate",
        language="en",
        retrieved_chunks=None,
    )
    assert isinstance(script, str)
    assert len(script) > 20


def test_deterministic_diagram_render_with_precomputed_spec(tmp_path):
    """Verify DiagramProvider renders video directly from pre-computed spec (no LLM)."""
    # 1. Generate blueprint
    bp = _fallback_blueprint("Plate Tectonics", "intermediate", "en")

    # 2. Package into VisualBrief with pre-computed diagram_spec
    brief = VisualBrief(
        concept=bp.concept,
        visual_type="diagram",
        narration_script=bp.full_narration_script,
        duration_seconds=5,
        diagram_spec=bp.diagram_spec.model_dump(mode="json"),
        scenes=[s.model_dump(mode="json") for s in bp.scenes],
    )

    # 3. Render directly using DiagramProvider
    out_mp4 = tmp_path / "test_diagram.mp4"
    provider = DiagramProvider()
    rendered_path = provider.generate(brief, out_mp4)

    assert Path(rendered_path).exists()
    assert Path(rendered_path).stat().st_size > 5000

    # 4. Probe video quality & playable stream
    info = require_playable_video(rendered_path, min_width=1280, min_height=720, min_duration_seconds=1.0)
    assert info.has_video is True
    assert info.width == 1280
    assert info.height == 720
    assert info.duration_seconds >= 4.0


def test_dual_output_narration_and_audio():
    """Verify narration script can be synthesized to audio (Output 1 pipeline)."""
    bp = _fallback_blueprint("Cell Mitosis", "beginner", "en")
    narration = bp.full_narration_script
    assert len(narration) > 0

    # Synthesize audio
    audio_path = synthesize_speech(narration[:100], language="en")
    assert Path(audio_path).exists()
    audio_info = require_playable_audio(audio_path)
    assert audio_info.has_audio is True
    assert audio_info.duration_seconds > 0.5
