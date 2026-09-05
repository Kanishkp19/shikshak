"""
Shikshak AI — Mandatory 4-Subject Acceptance Demos Test Suite.

Renders and validates all 4 acceptance demos mandated by architecture specifications:
  1. DEMO 1 — CHEMISTRY: Balancing Fe + H2O -> Fe3O4 + H2 (No seesaw, atom inventory, coefficient insertion)
  2. DEMO 2 — PHYSICS: Simple electric circuit (Battery, switch closure, electron drift, resistor drop)
  3. DEMO 3 — BIOLOGY: Photosynthesis light reaction (Thylakoid membrane, photolysis, proton gradient, ATP synthase)
  4. DEMO 4 — MATHEMATICS: Step-by-step quadratic equation derivation (Term continuity, camera focus)
"""
from pathlib import Path
import pytest

from skills.scene_renderers.chemistry.motion_adapter import render_chemistry_motion
from skills.scene_renderers.physics.motion_adapter import render_physics_motion
from skills.scene_renderers.biology.motion_adapter import render_biology_motion
from skills.scene_renderers.mathematics.motion_adapter import render_mathematics_motion
from skills.video_generation.media import require_playable_video

# Save to project workspace demos/ for convenient viewing in IDE file explorer
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEMO_OUTPUT_DIR = WORKSPACE_ROOT / "demos"


@pytest.fixture(scope="session", autouse=True)
def setup_demo_dir():
    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_demo_1_chemistry_balancing_iron_steam():
    out_path = DEMO_OUTPUT_DIR / "demo_1_chemistry_fe_balancing.mp4"
    payload = {
        "unbalanced_equation": "Fe + H2O -> Fe3O4 + H2",
        "balanced_equation": "3Fe + 4H2O -> Fe3O4 + 4H2",
        "atom_inventory": {"Fe": [1, 3], "H": [2, 2], "O": [1, 4]},
    }
    narration = (
        "Let's balance the reaction between iron and steam. Notice we have one iron on the left, "
        "but three on the right. We insert coefficient three before iron, then four before water, "
        "and four before hydrogen, balancing all atoms without any guessing."
    )

    result = render_chemistry_motion(
        payload_dict=payload,
        narration_text=narration,
        duration_seconds=5.0,
        out_path=out_path,
    )

    assert result.exists()
    assert result.stat().st_size > 10000
    require_playable_video(str(result), min_width=1280, min_height=720, min_duration_seconds=4.5)


def test_demo_2_physics_electric_circuit():
    out_path = DEMO_OUTPUT_DIR / "demo_2_physics_circuit.mp4"
    payload = {
        "circuit_type": "series",
        "voltage": 12.0,
        "resistance": 6.0,
    }
    narration = (
        "Here is a simple DC circuit. When the switch closes, potential difference from the battery "
        "drives a two-ampere electron current through the six-ohm resistor."
    )

    result = render_physics_motion(
        payload_dict=payload,
        narration_text=narration,
        duration_seconds=4.0,
        out_path=out_path,
    )

    assert result.exists()
    assert result.stat().st_size > 10000
    require_playable_video(str(result), min_width=1280, min_height=720, min_duration_seconds=3.5)


def test_demo_3_biology_photosynthesis_light_reaction():
    out_path = DEMO_OUTPUT_DIR / "demo_3_biology_photosynthesis.mp4"
    payload = {
        "process": "light_dependent_reaction",
        "membrane": "thylakoid",
    }
    narration = (
        "Inside the thylakoid membrane, chlorophyll absorbs sunlight photons, splitting water molecules. "
        "The accumulated proton gradient powers ATP Synthase to manufacture cellular energy."
    )

    result = render_biology_motion(
        payload_dict=payload,
        narration_text=narration,
        duration_seconds=4.0,
        out_path=out_path,
    )

    assert result.exists()
    assert result.stat().st_size > 10000
    require_playable_video(str(result), min_width=1280, min_height=720, min_duration_seconds=3.5)


def test_demo_4_mathematics_quadratic_derivation():
    out_path = DEMO_OUTPUT_DIR / "demo_4_mathematics_quadratic.mp4"
    payload = {
        "equation": "ax^2 + bx + c = 0",
        "method": "completing_the_square",
    }
    narration = (
        "We start with the general quadratic equation. Dividing by a and completing the square "
        "yields the famous quadratic formula, providing the exact roots for any parabola."
    )

    result = render_mathematics_motion(
        payload_dict=payload,
        narration_text=narration,
        duration_seconds=5.0,
        out_path=out_path,
    )

    assert result.exists()
    assert result.stat().st_size > 10000
    require_playable_video(str(result), min_width=1280, min_height=720, min_duration_seconds=4.5)


def test_demo_5_daily_life_chemical_changes_with_talking_avatar():
    out_path = DEMO_OUTPUT_DIR / "demo_5_daily_life_chemical_changes.mp4"
    from skills.scene_renderers.generative import render_split_screen
    from skills.video_stitching import stitch_segment
    from skills.lip_sync_rendering import render_lip_sync
    from models.avatar import AvatarPresenterMode

    payload = {
        "left_title": "Daily Life Chemical Changes",
        "right_title": "Observable Phenomena",
        "right_points": [
            "Milk left in warm conditions forms thick curd",
            "Iron nails develop reddish-brown flaky rust",
            "Grapes and sugarcane juice undergo fermentation",
        ],
        "formula": "NOT_IN_SOURCE",
        "key_takeaway": "Chemical reactions alter initial identity and produce new substances",
    }
    narration = (
        "In our daily life, we observe many chemical changes: milk turning into curd, "
        "an iron nail rusting when exposed to moist air, and fermentation of juices."
    )

    concept_clip = DEMO_OUTPUT_DIR / "demo_5_concept_clip.mp4"
    concept_res = render_split_screen(
        payload_dict=payload,
        narration_text=narration,
        duration_seconds=5.0,
        out_path=concept_clip,
    )
    assert concept_res.exists()

    # Generate audio-synced talking avatar
    audio_file = Path("assets/teacher_voice.wav")
    assert audio_file.exists()
    avatar_video = render_lip_sync(str(audio_file))
    assert Path(avatar_video).exists()

    # Stitch into final lesson segment with Picture-in-Picture talking teacher
    final_video = stitch_segment(
        avatar_video_path=avatar_video,
        concept_video_path=str(concept_res),
        audio_path=str(audio_file),
        presenter_mode=AvatarPresenterMode.TEACHER_EXPLAIN,
    )
    import shutil
    shutil.copy(final_video, str(out_path))

    assert out_path.exists()
    assert out_path.stat().st_size > 50000
    require_playable_video(str(out_path), min_width=1280, min_height=720, min_duration_seconds=4.0)

