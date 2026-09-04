"""
Shikshak AI — Physics to Motion Canvas Adapter.

Translates CircuitSimulationPayload and OpticsRayDiagramPayload into
structured AnimationSceneSpec for Motion Canvas.
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


def build_physics_circuit_spec(
    payload: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
) -> AnimationSceneSpec:
    """Build a semantic AnimationSceneSpec for an electric circuit with switch and current flow."""
    voltage = float(payload.get("voltage") or 12.0)
    resistance = float(payload.get("resistance") or 6.0)

    objects: list[SemanticObject] = [
        SemanticObject(
            id="battery",
            type="power_source",
            source="iec",
            semantic_role="battery_anode_cathode",
            pedagogical_purpose="provide electrical potential difference (12V) across terminals",
            importance=1.0,
            properties={"voltage": voltage},
        ),
        SemanticObject(
            id="switch",
            type="control_element",
            source="iec",
            semantic_role="circuit_switch",
            pedagogical_purpose="demonstrate circuit continuity: open breaks current, closed permits flow",
            importance=1.0,
            properties={"state": "open"},
        ),
        SemanticObject(
            id="resistor",
            type="load",
            source="iec",
            semantic_role="circuit_resistor",
            pedagogical_purpose="demonstrate resistance opposing charge flow and voltage drop",
            importance=1.0,
            properties={"resistance": resistance},
        ),
    ]

    beats: list[SemanticBeat] = [
        # 0.0s: Introduce circuit components in open state
        SemanticBeat(
            at=0.0,
            duration=1.2,
            action="introduce",
            target=["battery", "switch", "resistor"],
            narrative_cue="Consider a basic electric circuit with a 12-volt battery, an open switch, and a 6-ohm resistor.",
        ),
        # 2.5s: Close switch -> current flows
        SemanticBeat(
            at=2.5,
            duration=0.6,
            action="transform",
            target=["switch"],
            semantic_value="closed",
            narrative_cue="When we close the switch, the circuit loop becomes complete.",
        ),
        # 3.2s: Electron current drift begins
        SemanticBeat(
            at=3.2,
            duration=2.5,
            action="flow_particle",
            target=["battery", "switch", "resistor"],
            semantic_value={"rate": voltage / resistance},
            narrative_cue="Electrons drift through the wire, producing a 2.0-ampere current according to Ohm's Law.",
        ),
        # 4.5s: Focus on resistor
        SemanticBeat(
            at=4.5,
            duration=1.0,
            action="focus",
            target=["resistor"],
            narrative_cue="The resistor opposes electron motion, converting electrical energy into thermal energy.",
        ),
    ]

    camera: list[SemanticCameraKeyframe] = [
        SemanticCameraKeyframe(at=0.0, action="establish"),
        SemanticCameraKeyframe(at=2.4, action="focus", target=["switch"], zoom_factor=1.25),
        SemanticCameraKeyframe(at=4.5, action="focus", target=["resistor"], zoom_factor=1.3),
        SemanticCameraKeyframe(at=5.5, action="pullback"),
    ]

    return AnimationSceneSpec(
        scene_id="physics_circuit_demo",
        domain="physics",
        duration=duration_seconds,
        fps=30,
        objects=objects,
        beats=beats,
        camera=camera,
        metadata={"voltage": voltage, "resistance": resistance},
    )


def render_physics_motion(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Entry point for physics scenes routed to Motion Canvas."""
    spec = build_physics_circuit_spec(payload_dict, narration_text, duration_seconds)
    return render_motion_canvas_spec(spec, duration_seconds=duration_seconds, out_path=out_path)
