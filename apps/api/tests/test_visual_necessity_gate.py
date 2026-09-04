"""
Tests for Visual Necessity Quality Gate & Anti-Pattern Prevention.

Enforces:
1. Every rendered visual must have a justified pedagogical purpose.
2. Decorative metaphors (e.g. balance scale for chemical balancing,
   water pipe for electric current, lightning for biological energy)
   are strictly forbidden unless explicitly introduced in narration.
3. Deterministic VisualNecessityScore correctly penalizes decorative elements.
"""
import pytest
from skills.quality_gate import (
    audit_scene,
    compute_visual_necessity_score,
    NEGATIVE_VISUAL_VOCABULARY,
)


def test_rejects_unjustified_balancing_scale_metaphor():
    # Fe + H2O -> Fe3O4 + H2 with an automatic decorative scale
    scene = {
        "scene_order": 1,
        "learning_objective": "Balance chemical reaction between iron and steam",
        "visual_mode": "balancing_exercise",
        "narration_text": "We start with iron and water reacting to form iron oxide and hydrogen gas.",
        "visual_payload": {
            "unbalanced_equation": "Fe + H2O -> Fe3O4 + H2",
            "balanced_equation": "3Fe + 4H2O -> Fe3O4 + 4H2",
            "atom_inventory": {"Fe": [3, 3], "H": [8, 8], "O": [4, 4]},
            "scale_pan": "left_pan",
            "show_scale": True,
        },
    }

    score, issues = compute_visual_necessity_score(scene, narration_text=scene["narration_text"])
    assert score < 0.7
    issue_names = [i.check_name for i in issues]
    assert "anti_pattern_metaphor" in issue_names or "balancing_scale_metaphor" in issue_names

    # Run full audit_scene: verify auto-repair strips the decorative scale
    result = audit_scene(scene)
    assert result.repaired_scene is not None
    repaired_payload = result.repaired_scene.get("visual_payload")
    assert repaired_payload.get("show_scale") is False
    assert repaired_payload.get("comparison_mode") == "atom_inventory"


def test_allows_metaphor_when_explicitly_justified_in_narration():
    # When narration explicitly introduces the balance scale analogy
    scene = {
        "scene_order": 1,
        "learning_objective": "Understand mass conservation with balance scale analogy",
        "visual_mode": "balancing_exercise",
        "narration_text": "Think of this like a physical balance scale where reactant mass must balance product mass.",
        "visual_payload": {
            "unbalanced_equation": "Fe + H2O -> Fe3O4 + H2",
            "balanced_equation": "3Fe + 4H2O -> Fe3O4 + 4H2",
            "atom_inventory": {"Fe": [3, 3], "H": [8, 8], "O": [4, 4]},
            "show_scale": True,
        },
    }

    score, issues = compute_visual_necessity_score(scene, narration_text=scene["narration_text"])
    # No error issues because narration explicitly introduced the analogy
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 0
    assert score >= 0.9


def test_detects_water_pipe_metaphor_in_circuit():
    scene = {
        "scene_order": 1,
        "learning_objective": "Electric current in conductors",
        "visual_mode": "circuit_simulation",
        "narration_text": "The battery creates a potential difference across the circuit.",
        "visual_payload": {
            "circuit_type": "series",
            "water_pipe": True,
            "voltage": 12.0,
            "current": 2.0,
        },
    }

    score, issues = compute_visual_necessity_score(scene, narration_text=scene["narration_text"])
    assert score < 0.8
    assert any(i.check_name == "anti_pattern_metaphor" for i in issues)


def test_detects_lightning_icon_in_cellular_biology():
    scene = {
        "scene_order": 2,
        "learning_objective": "Cellular respiration ATP yield",
        "visual_mode": "bio_cellular_process",
        "narration_text": "Mitochondria produce cellular energy through oxidative phosphorylation.",
        "visual_payload": {
            "process_name": "Cellular Respiration",
            "organelle": "Mitochondria",
            "lightning_bolt": True,
        },
    }

    score, issues = compute_visual_necessity_score(scene, narration_text=scene["narration_text"])
    assert score < 0.8
    assert any(i.check_name == "anti_pattern_metaphor" for i in issues)


def test_penalizes_objects_without_pedagogical_purpose():
    scene = {
        "scene_order": 1,
        "learning_objective": "Atom counting",
        "visual_mode": "reaction_lab",
        "narration_text": "Iron reacts with oxygen.",
        "visual_payload": {
            "objects": [
                {"id": "fe_1", "type": "atom", "pedagogical_purpose": ""},
                {"id": "fe_2", "type": "atom"},
            ]
        },
    }

    score, issues = compute_visual_necessity_score(scene, narration_text=scene["narration_text"])
    assert score < 1.0
    assert any(i.check_name == "pedagogical_justification" for i in issues)
