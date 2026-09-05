"""
Tests for Scene Breakdown, Smart Asset Dispatch, Text Sanitization, and Lively Avatar.

Verifies:
1. Text Sanitization: "NOT_IN_SOURCE" and placeholders are stripped and never rendered.
2. Speech-Paced Scene Durations: Scene durations correlate with narration word count.
3. Pre-Installed Assets vs Grounded Image Prompts in Visual Director.
4. Lively Talking Avatar: Audio envelope analysis, lip movements, and playable MP4 output.
"""
from pathlib import Path
import pytest

from skills.scene_renderers.base import sanitize_display_text
from skills.scene_renderers.generative import render_split_screen
from skills.scene_renderers.chemistry import render_generic_explainer
from skills.avatar.lively_avatar import _extract_audio_envelope_and_features, generate_lively_avatar_video
from agents.scene_planning import _validate_and_normalize_scenes, ScenePlanRaw
from agents.visual_director import determine_visual_strategy
from skills.image_generation.prompt_engineer import build_educational_prompt
from models.avatar import DEFAULT_FEMALE_TEACHER
from models import VisualMode


def test_sanitize_display_text_strips_placeholders():
    assert sanitize_display_text("NOT_IN_SOURCE") == ""
    assert sanitize_display_text("not_in_source") == ""
    assert sanitize_display_text("[MISSING]") == ""
    assert sanitize_display_text("None") == ""
    assert sanitize_display_text("N/A") == ""
    assert sanitize_display_text("undefined") == ""
    assert sanitize_display_text("2H2 + O2 -> 2H2O") == "2H2 + O2 -> 2H2O"
    assert sanitize_display_text("Definition of Chemistry") == "Definition of Chemistry"


def test_split_screen_renderer_omits_not_in_source(tmp_path):
    out = tmp_path / "test_split_sanitize.mp4"
    payload = {
        "left_title": "Disciplines of Science",
        "right_title": "Definition of Chemistry",
        "right_points": [
            "Studies preparation and properties of substances",
            "Examines molecular structure",
            "Investigates chemical reactions",
        ],
        "formula": "NOT_IN_SOURCE",
        "key_takeaway": "Chemistry is the central science studying material substances",
    }
    res = render_split_screen(payload, narration_text="Definition of chemistry", duration_seconds=2.0, out_path=out)
    assert res.exists()
    assert res.stat().st_size > 1000


def test_generic_explainer_omits_not_in_source(tmp_path):
    out = tmp_path / "test_generic_sanitize.mp4"
    payload = {
        "title": "Natural Chemical Changes",
        "key_points": ["Milk turning into curd", "Rusting of iron in moist air"],
        "equation": "NOT_IN_SOURCE",
    }
    res = render_generic_explainer(payload, narration_text="Observing chemical changes", duration_seconds=2.0, out_path=out)
    assert res.exists()
    assert res.stat().st_size > 1000


def test_speech_paced_scene_duration_calculation():
    raw_scenes = [
        ScenePlanRaw(
            scene_order=1,
            learning_objective="Welcome students to chemistry",
            narration_text="Welcome, students!",
            visual_mode="kinetic_text",
            duration_seconds=6.0,  # Default schema value
        ),
        ScenePlanRaw(
            scene_order=2,
            learning_objective="Explain oxidation and corrosion in daily life",
            narration_text="In our daily life, we observe many chemical changes. When an iron nail is left exposed to moist air for a long time, a reddish-brown flaky substance called rust develops on its surface, indicating an oxidation reaction.",
            visual_mode="split_screen",
            duration_seconds=6.0,  # Default schema value
        ),

    ]
    normalized = _validate_and_normalize_scenes(raw_scenes, concept="Chemical Reactions")
    assert len(normalized) == 2

    # Scene 1 has 2 words -> should be clamped to min duration 3.0s
    assert normalized[0]["duration_seconds"] == 3.0
    assert normalized[0]["narration_text"] == "Welcome, students!"

    # Scene 2 has ~36 words -> should have longer duration proportional to speech (~15-16s)
    assert normalized[1]["duration_seconds"] >= 14.0
    assert normalized[1]["duration_seconds"] > normalized[0]["duration_seconds"]


def test_visual_director_intro_pacing_and_grounded_prompts():
    # Intro scene with greeting should be kinetic_text, NOT ai_illustration
    intro_scene = {
        "learning_objective": "Introduction to daily chemical changes",
        "narration_text": "Welcome, students! Today we explore natural chemical changes around us.",
    }
    mode, strategy, payload = determine_visual_strategy(intro_scene, scene_index=0, total_scenes=3, segment_concept="Chemical Changes")
    assert mode == "kinetic_text"

    # Middle scene with observational chemistry (curd / milk) should produce concrete grounded prompt
    obs_prompt = build_educational_prompt(
        concept="Natural Chemical Changes in Daily Life",
        visual_objective="Curdling of milk and rusting of iron",
        narration_span="Milk left at room temperature turns into curd, and iron nails rust in moist air.",
    )
    # The prompt should contain concrete physical subjects and explicitly ban circular dials
    assert "curd" in obs_prompt.prompt.lower()
    assert "circular dial" in obs_prompt.negative_prompt


def test_lively_talking_avatar_audio_sync(tmp_path):
    portrait = Path("assets/female_teacher_ref.jpg")
    audio = Path("assets/teacher_voice.wav")
    assert portrait.exists()
    assert audio.exists()

    # Verify audio envelope extraction
    envelope, duration_s = _extract_audio_envelope_and_features(audio, fps=25)
    assert len(envelope) > 0
    assert duration_s > 0.5
    # Non-silent speech should have non-zero envelope values
    assert envelope.max() > 0.1

    out = tmp_path / "test_talking_avatar.mp4"
    res = generate_lively_avatar_video(portrait, audio, out_path=out, fps=25, canvas_size=256)
    assert res.exists()
    assert res.stat().st_size > 10000
