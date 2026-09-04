"""Unit tests for agents/visual_selection.py."""
from agents.visual_selection import _infer_visual_type, select_visuals


def test_infer_equation_from_concept_name():
    assert _infer_visual_type("Solving a quadratic equation") == "equation"
    assert _infer_visual_type("Derivative of a function") == "equation"


def test_infer_code_from_concept_name():
    assert _infer_visual_type("Writing a for loop in Python") == "code"
    assert _infer_visual_type("Recursion explained") == "code"


def test_infer_diagram():
    assert _infer_visual_type("The water cycle diagram") == "diagram"
    assert _infer_visual_type("Cell structure overview") == "diagram"


def test_infer_animation():
    assert _infer_visual_type("Wave motion in physics") == "animation"


def test_infer_none_for_unknown():
    assert _infer_visual_type("Some abstract history topic") == "none"


def test_select_visuals_upgrades_none_to_better_type():
    plan = {
        "segments": [
            {"concept": "Quadratic equation", "visual_type": "none"},
            {"concept": "Recursion", "visual_type": "diagram"},  # explicit, leave alone
        ]
    }
    out = select_visuals(plan)
    assert out["segments"][0]["visual_type"] == "equation"
    assert out["segments"][1]["visual_type"] == "diagram"
