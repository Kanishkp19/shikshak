"""
Shikshak AI — Chemistry to Motion Canvas Adapter.

Translates Chemistry payloads (BalancingExercisePayload, ReactionLabPayload, EquationBuildPayload)
into a structured AnimationSceneSpec for Motion Canvas.

Non-negotiable rule:
Mass conservation must be visualized using atomic counts, molecular structures,
and coefficient animation — NEVER decorative balance scales or seesaws.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from models.animation_spec import (
    AnimationSceneSpec,
    SemanticObject,
    SemanticBeat,
    SemanticCameraKeyframe,
    NarrativeMarker,
)
from skills.scene_renderers.motion_canvas_renderer import render_motion_canvas_spec


def build_chemistry_balancing_spec(
    payload: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 8.5,
) -> AnimationSceneSpec:
    """Build a semantic AnimationSceneSpec for equation balancing (e.g. Fe + H2O -> Fe3O4 + H2)."""
    unbalanced = payload.get("unbalanced_equation") or "Fe + H2O -> Fe3O4 + H2"
    balanced = payload.get("balanced_equation") or "3Fe + 4H2O -> Fe3O4 + 4H2"

    objects: list[SemanticObject] = [
        SemanticObject(
            id="fe_reactant",
            type="atom",
            source="rdkit",
            semantic_role="reactant_iron",
            pedagogical_purpose="display iron atom on reactant side for counting and coefficient addition",
            importance=1.0,
            label="Fe",
            formula="Fe",
            count=1,
            properties={"element": "Fe", "side": "reactant"},
        ),
        SemanticObject(
            id="h2o_reactant",
            type="molecule",
            source="rdkit",
            semantic_role="reactant_water",
            pedagogical_purpose="display water molecule on reactant side for oxygen and hydrogen counting",
            importance=1.0,
            label="H₂O",
            formula="H2O",
            count=1,
            properties={"element": "H2O", "side": "reactant"},
        ),
        SemanticObject(
            id="fe3o4_product",
            type="molecule",
            source="rdkit",
            semantic_role="product_magnetite",
            pedagogical_purpose="display iron oxide product showing 3 Fe and 4 O atoms",
            importance=1.0,
            label="Fe₃O₄",
            formula="Fe3O4",
            count=1,
            properties={"element": "Fe3O4", "side": "product"},
        ),
        SemanticObject(
            id="h2_product",
            type="molecule",
            source="rdkit",
            semantic_role="product_hydrogen",
            pedagogical_purpose="display hydrogen gas product for hydrogen balancing",
            importance=1.0,
            label="H₂",
            formula="H2",
            count=1,
            properties={"element": "H2", "side": "product"},
        ),
    ]

    beats: list[SemanticBeat] = [
        # 0.0s: Introduce unbalanced equation
        SemanticBeat(
            at=0.0,
            duration=1.2,
            action="introduce",
            target=["fe_reactant", "h2o_reactant", "fe3o4_product", "h2_product"],
            narrative_cue="Let's balance this equation.",
        ),
        # 2.0s: Highlight and compare Fe on both sides (1 vs 3)
        SemanticBeat(
            at=2.0,
            duration=1.0,
            action="compare",
            target=["fe_reactant", "fe3o4_product"],
            narrative_cue="We have one iron atom on the left, but three on the right.",
        ),
        # 4.5s: Insert coefficient 3 into Fe reactant
        SemanticBeat(
            at=4.5,
            duration=0.8,
            action="coefficient_insert",
            target=["fe_reactant"],
            semantic_value=3,
            narrative_cue="So we add a coefficient of three before iron.",
        ),
        # 6.5s: Compare Oxygen counts (1 vs 4)
        SemanticBeat(
            at=6.5,
            duration=1.0,
            action="compare",
            target=["h2o_reactant", "fe3o4_product"],
            narrative_cue="Next look at oxygen: four on the right, so we need four waters on the left.",
        ),
        # 7.8s: Insert coefficient 4 into H2O
        SemanticBeat(
            at=7.8,
            duration=0.8,
            action="coefficient_insert",
            target=["h2o_reactant"],
            semantic_value=4,
            narrative_cue="Adding four before water gives eight hydrogens.",
        ),
        # 9.5s: Insert coefficient 4 into H2
        SemanticBeat(
            at=9.5,
            duration=0.8,
            action="coefficient_insert",
            target=["h2_product"],
            semantic_value=4,
            narrative_cue="Finally, placing four before hydrogen balances the equation completely.",
        ),
    ]

    camera: list[SemanticCameraKeyframe] = [
        SemanticCameraKeyframe(at=0.0, action="establish"),
        SemanticCameraKeyframe(at=2.0, action="focus", target=["fe_reactant", "fe3o4_product"], zoom_factor=1.2),
        SemanticCameraKeyframe(at=4.5, action="focus", target=["fe_reactant"], zoom_factor=1.35),
        SemanticCameraKeyframe(at=6.5, action="focus", target=["h2o_reactant", "fe3o4_product"], zoom_factor=1.2),
        SemanticCameraKeyframe(at=9.0, action="pullback"),
    ]

    return AnimationSceneSpec(
        scene_id="chem_balancing_fe_h2o",
        domain="chemistry",
        duration=duration_seconds,
        fps=30,
        objects=objects,
        beats=beats,
        camera=camera,
        metadata={
            "unbalanced_equation": unbalanced,
            "balanced_equation": balanced,
        },
    )


def render_chemistry_motion(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 8.5,
    out_path: Path | None = None,
) -> Path:
    """Entry point for chemistry scenes routed to Motion Canvas."""
    spec = build_chemistry_balancing_spec(payload_dict, narration_text, duration_seconds)
    return render_motion_canvas_spec(spec, duration_seconds=duration_seconds, out_path=out_path)
