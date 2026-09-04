"""
Shikshak AI — Mathematics to Motion Canvas Adapter.

Translates AlgebraStepSolvePayload into structured AnimationSceneSpec
for Motion Canvas (e.g. Step-by-Step Quadratic Equation Derivation).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from models.animation_spec import (
    AnimationSceneSpec,
    SemanticObject,
    SemanticBeat,
    SemanticCameraKeyframe,
)
from skills.scene_renderers.motion_canvas_renderer import render_motion_canvas_spec


def build_math_quadratic_spec(
    payload: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 10.0,
) -> AnimationSceneSpec:
    """Build a semantic AnimationSceneSpec for step-by-step quadratic equation derivation."""
    steps = [
        ("step_1", "ax² + bx + c = 0", "Standard quadratic form"),
        ("step_2", "x² + (b/a)x + c/a = 0", "Divide entire equation by leading coefficient a"),
        ("step_3", "x² + (b/a)x = -c/a", "Subtract constant term c/a to right side"),
        ("step_4", "x² + (b/a)x + (b/2a)² = (b/2a)² - c/a", "Complete the square by adding (b/2a)²"),
        ("step_5", "(x + b/2a)² = (b² - 4ac)/(4a²)", "Factor left side into a binomial square"),
        ("step_final", "x = (-b ± √(b² - 4ac)) / (2a)", "Solve for x via square root: The Quadratic Formula"),
    ]

    objects: list[SemanticObject] = [
        SemanticObject(
            id=step_id,
            type="equation_step",
            source="latex",
            semantic_role=f"derivation_{step_id}",
            pedagogical_purpose=f"display {explanation}",
            importance=1.0,
            label=formula,
            formula=formula,
        )
        for step_id, formula, explanation in steps
    ]

    beats: list[SemanticBeat] = [
        SemanticBeat(
            at=0.0,
            duration=1.2,
            action="introduce",
            target=["step_1"],
            narrative_cue="We begin with the general quadratic equation ax² + bx + c = 0.",
        ),
        SemanticBeat(
            at=1.7,
            duration=1.0,
            action="equation_transform",
            target=["step_2"],
            narrative_cue="First, divide every term by a to make the leading coefficient one.",
        ),
        SemanticBeat(
            at=3.4,
            duration=1.0,
            action="equation_transform",
            target=["step_3"],
            narrative_cue="Next, transpose the constant term c over a to the right side.",
        ),
        SemanticBeat(
            at=5.1,
            duration=1.0,
            action="equation_transform",
            target=["step_4"],
            narrative_cue="Now complete the square by adding (b over 2a) squared to both sides.",
        ),
        SemanticBeat(
            at=6.8,
            duration=1.0,
            action="equation_transform",
            target=["step_5"],
            narrative_cue="The left side factors into a perfect binomial square.",
        ),
        SemanticBeat(
            at=8.5,
            duration=1.2,
            action="emphasize",
            target=["step_final"],
            narrative_cue="Taking the square root gives the universal quadratic formula.",
        ),
    ]

    camera: list[SemanticCameraKeyframe] = [
        SemanticCameraKeyframe(at=0.0, action="establish"),
        SemanticCameraKeyframe(at=1.7, action="focus", target=["step_2"], zoom_factor=1.15),
        SemanticCameraKeyframe(at=5.1, action="focus", target=["step_4"], zoom_factor=1.2),
        SemanticCameraKeyframe(at=8.5, action="focus", target=["step_final"], zoom_factor=1.25),
        SemanticCameraKeyframe(at=9.5, action="pullback"),
    ]

    return AnimationSceneSpec(
        scene_id="math_quadratic_derivation",
        domain="mathematics",
        duration=duration_seconds,
        fps=30,
        objects=objects,
        beats=beats,
        camera=camera,
    )


def render_mathematics_motion(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 10.0,
    out_path: Path | None = None,
) -> Path:
    """Entry point for mathematics scenes routed to Motion Canvas."""
    spec = build_math_quadratic_spec(payload_dict, narration_text, duration_seconds)
    return render_motion_canvas_spec(spec, duration_seconds=duration_seconds, out_path=out_path)
