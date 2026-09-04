"""
Tests for AnimationSceneSpec and Coordinate Invariance.

Ensures that the LLM-facing schemas cannot receive coordinate,
dimension, or drawing instructions, preserving the separation of concerns:
LLM = Semantic Pedagogical Intent
Motion Canvas = Geometry, Layout, and Motion.
"""
import pytest
from pydantic import ValidationError

from models.animation_spec import (
    AnimationSceneSpec,
    SemanticObject,
    SemanticBeat,
    SemanticCameraKeyframe,
)


def test_valid_animation_scene_spec():
    spec = AnimationSceneSpec(
        scene_id="chem_balance_01",
        domain="chemistry",
        duration=8.5,
        objects=[
            SemanticObject(
                id="fe_reactant",
                type="atom",
                source="rdkit",
                semantic_role="reactant_iron",
                pedagogical_purpose="show single iron atom on reactant side",
                importance=1.0,
                properties={"element": "Fe", "count": 1},
            ),
            SemanticObject(
                id="fe_product",
                type="atom",
                source="rdkit",
                semantic_role="product_iron",
                pedagogical_purpose="show three iron atoms in magnetite",
                importance=1.0,
                properties={"element": "Fe", "count": 3},
            ),
        ],
        beats=[
            SemanticBeat(
                at=0.0,
                action="introduce",
                target=["fe_reactant"],
                narrative_cue="We begin with one iron atom.",
            ),
            SemanticBeat(
                at=2.0,
                action="compare",
                target=["fe_reactant", "fe_product"],
                narrative_cue="Notice we have three on the product side.",
            ),
            SemanticBeat(
                at=4.0,
                action="coefficient_insert",
                target=["fe_reactant"],
                semantic_value=3,
                narrative_cue="So we add a coefficient of three.",
            ),
        ],
        camera=[
            SemanticCameraKeyframe(
                at=0.0,
                action="establish",
            ),
            SemanticCameraKeyframe(
                at=2.0,
                action="focus",
                target=["fe_reactant", "fe_product"],
                zoom_factor=1.2,
            ),
        ],
    )

    data = spec.model_dump(by_alias=True)
    assert data["sceneId"] == "chem_balance_01"
    assert data["domain"] == "chemistry"
    assert len(data["objects"]) == 2
    assert data["beats"][2]["action"] == "coefficient_insert"
    assert data["beats"][2]["semanticValue"] == 3


@pytest.mark.parametrize("forbidden_field", [
    "x", "y", "width", "height", "top", "left", "pixel_x", "svg_path", "css", "raw_html"
])
def test_rejects_coordinate_fields_in_object(forbidden_field):
    with pytest.raises(ValidationError) as exc_info:
        SemanticObject(
            id="obj_1",
            type="atom",
            semantic_role="test",
            pedagogical_purpose="test purpose",
            properties={forbidden_field: 100},
        )
    assert "Coordinate Invariance Violation" in str(exc_info.value)


@pytest.mark.parametrize("forbidden_field", [
    "x", "y", "width", "height", "dx", "dy", "coord_x"
])
def test_rejects_coordinate_fields_in_beat(forbidden_field):
    with pytest.raises(ValidationError) as exc_info:
        SemanticBeat.model_validate({
            "at": 1.0,
            "action": "move",
            "target": ["obj_1"],
            forbidden_field: 250,
        })
    assert "Coordinate Invariance Violation" in str(exc_info.value)
