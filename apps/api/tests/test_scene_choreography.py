"""Regression tests for transcript-driven visual choreography."""
from __future__ import annotations

import pytest

from skills.scene_choreography import choreograph_scenes


def test_choreography_allocates_the_full_audio_duration_by_transcript_weight():
    """Every rendered scene receives a contiguous, word-weighted audio window."""
    narration = (
        "Scientific notation makes extremely large values compact. "
        "Move the decimal point until only one nonzero digit remains to its left. "
        "The number of moves becomes the exponent of ten."
    )
    scenes = choreograph_scenes(
        concept="Scientific notation",
        narration_script=narration,
        planned_scenes=[],
        total_duration_seconds=18.0,
    )

    assert len(scenes) == 3
    assert scenes[0]["start_time_ms"] == 0
    assert scenes[-1]["end_time_ms"] == 18_000
    assert all(scene["end_time_ms"] > scene["start_time_ms"] for scene in scenes)
    assert sum(scene["duration_seconds"] for scene in scenes) == pytest.approx(18.0)
    assert scenes[1]["duration_seconds"] > scenes[0]["duration_seconds"]


def test_choreography_replaces_an_unrelated_specialized_scene_with_transcript_visual():
    """A scene about unit conversion must never render a chemistry balance demo."""
    narration = (
        "To convert one day into seconds, first multiply by twenty-four hours per day. "
        "Then multiply by three thousand six hundred seconds per hour."
    )
    planned_scenes = [
        {
            "scene_order": 1,
            "narration_text": "Hydrogen and oxygen form water.",
            "narration_span": "Hydrogen and oxygen form water.",
            "learning_objective": "Balance a chemical equation",
            "visual_mode": "balancing_exercise",
            "visual_payload": {"unbalanced_equation": "H2 + O2 -> H2O"},
        }
    ]

    scenes = choreograph_scenes(
        concept="Unit conversion",
        narration_script=narration,
        planned_scenes=planned_scenes,
        total_duration_seconds=12.0,
    )

    assert all(scene["visual_mode"] == "generic_explainer" for scene in scenes)
    assert all(scene["asset_strategy"] == "transcript_diagram" for scene in scenes)
    assert all("hydrogen" not in scene["narration_span"].lower() for scene in scenes)
    assert all("day" in " ".join(scene["entities"]).lower() or "seconds" in " ".join(scene["entities"]).lower() for scene in scenes)


def test_choreography_preserves_a_matching_specialized_scene_and_its_payload():
    """A valid domain kit remains selected only when its narration is relevant."""
    narration = "Close the switch so electrons flow around the circuit through the resistor."
    planned_scenes = [
        {
            "scene_order": 1,
            "narration_text": narration,
            "narration_span": narration,
            "learning_objective": "Show current in a closed circuit",
            "visual_mode": "circuit_simulation",
            "visual_payload": {
                "circuit_type": "series",
                "voltage": 12.0,
                "resistance": 6.0,
                "current": 2.0,
                "formula": "V = I × R",
                "observation": "Electrons flow through the resistor.",
            },
            "entities": ["switch", "electrons", "resistor"],
        }
    ]

    scenes = choreograph_scenes(
        concept="Electric circuits",
        narration_script=narration,
        planned_scenes=planned_scenes,
        total_duration_seconds=8.0,
    )

    assert len(scenes) == 1
    assert scenes[0]["visual_mode"] == "circuit_simulation"
    assert scenes[0]["visual_payload"]["voltage"] == 12.0
    assert scenes[0]["asset_strategy"] == "existing_domain_kit"
    assert len(scenes[0]["motion_beats"]) >= 3
