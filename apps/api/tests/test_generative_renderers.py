"""
Unit & integration tests for generative scene renderers and transition stitching.
"""
from pathlib import Path
import tempfile
import pytest

from skills.scene_renderers import (
    get_scene_renderer,
    render_ai_illustration,
    render_kinetic_text,
    render_split_screen,
)
from skills.video_generation.media import require_playable_video
from skills.video_stitching import concat_segments_with_transitions


def test_resolve_scene_renderers_new_modes():
    assert get_scene_renderer("ai_illustration") is render_ai_illustration
    assert get_scene_renderer("kinetic_text") is render_kinetic_text
    assert get_scene_renderer("split_screen") is render_split_screen


def test_render_kinetic_text():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "kinetic_test.mp4"
        payload = {
            "title": "Conservation of Energy",
            "subtitle": "Total energy remains constant in an isolated system",
            "key_takeaways": [
                "Energy transforms between kinetic and potential forms",
                "Work done equals change in kinetic energy",
            ],
            "badge": "PHYSICAL PRINCIPLE",
            "equation": "E_total = K + U = constant",
        }

        rendered = render_kinetic_text(
            payload_dict=payload,
            narration_text="Energy can neither be created nor destroyed.",
            duration_seconds=2.0,
            out_path=out_file,
        )

        assert rendered.exists()
        require_playable_video(rendered, min_width=640, min_height=360, min_duration_seconds=1.0)


def test_render_split_screen():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "split_test.mp4"
        payload = {
            "left_title": "Ohm's Law Circuit Setup",
            "left_type": "image",
            "right_title": "Mathematical Relationship",
            "right_points": [
                "Potential difference is proportional to current",
                "Resistance represents opposition to charge flow",
            ],
            "formula": "V = I × R",
            "key_takeaway": "Current increases linearly with applied voltage",
        }

        rendered = render_split_screen(
            payload_dict=payload,
            narration_text="In this circuit, current is measured as voltage varies.",
            duration_seconds=2.0,
            out_path=out_file,
        )

        assert rendered.exists()
        require_playable_video(rendered, min_width=640, min_height=360, min_duration_seconds=1.0)


def test_render_ai_illustration():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "ai_illus_test.mp4"
        payload = {
            "title": "Structure of Mitochondria",
            "caption": "Outer membrane, cristae, and matrix producing ATP",
            "entities": ["Outer Membrane", "Cristae", "Matrix", "ATP Synthase"],
            "style": "educational_illustration",
            "key_takeaway": "Folded cristae maximize surface area for respiration",
        }

        rendered = render_ai_illustration(
            payload_dict=payload,
            narration_text="Mitochondria are the powerhouse organelles of the cell.",
            duration_seconds=2.0,
            out_path=out_file,
        )

        assert rendered.exists()
        require_playable_video(rendered, min_width=640, min_height=360, min_duration_seconds=1.0)


def test_concat_segments_with_transitions():
    with tempfile.TemporaryDirectory() as tmpdir:
        clip1 = Path(tmpdir) / "clip1.mp4"
        clip2 = Path(tmpdir) / "clip2.mp4"
        out_stitched = Path(tmpdir) / "stitched.mp4"

        # Render 2 short clips
        render_kinetic_text(
            payload_dict={"title": "Clip 1", "key_takeaways": ["Point 1"]},
            duration_seconds=2.0,
            out_path=clip1,
        )
        render_kinetic_text(
            payload_dict={"title": "Clip 2", "key_takeaways": ["Point 2"]},
            duration_seconds=2.0,
            out_path=clip2,
        )

        result_path = concat_segments_with_transitions(
            segment_paths=[str(clip1), str(clip2)],
            transition="fade",
            transition_duration=0.3,
            out_path=out_stitched,
        )

        assert Path(result_path).exists()
        require_playable_video(Path(result_path), min_width=640, min_height=360, min_duration_seconds=2.0)
