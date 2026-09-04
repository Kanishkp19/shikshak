"""
Shikshak AI — Biology to Motion Canvas Adapter.

Translates BioCellularProcessPayload into structured AnimationSceneSpec
for Motion Canvas (e.g. Photosynthesis Light Reaction on Thylakoid Membrane).
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


def build_biology_photosynthesis_spec(
    payload: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 7.0,
) -> AnimationSceneSpec:
    """Build a semantic AnimationSceneSpec for photosynthesis light-dependent reaction."""
    objects: list[SemanticObject] = [
        SemanticObject(
            id="photosystem_ii",
            type="protein_complex",
            source="bio_icons",
            semantic_role="chlorophyll_light_harvester",
            pedagogical_purpose="absorb photon energy to excite electrons and split water",
            importance=1.0,
            label="Photosystem II",
        ),
        SemanticObject(
            id="water_splitting_site",
            type="catalytic_center",
            source="bio_icons",
            semantic_role="water_oxidation_catalyst",
            pedagogical_purpose="split 2 H2O into 4 protons, oxygen, and 4 electrons",
            importance=1.0,
            label="Water Splitting (2H₂O ⟶ 4H⁺ + O₂ + 4e⁻)",
        ),
        SemanticObject(
            id="atp_synthase",
            type="molecular_motor",
            source="bio_icons",
            semantic_role="chemiosmotic_atp_generator",
            pedagogical_purpose="use proton motive force to synthesize ATP from ADP and phosphate",
            importance=1.0,
            label="ATP Synthase",
        ),
    ]

    beats: list[SemanticBeat] = [
        # 0.0s: Introduce thylakoid membrane architecture
        SemanticBeat(
            at=0.0,
            duration=1.2,
            action="introduce",
            target=["photosystem_ii", "atp_synthase"],
            narrative_cue="Inside the chloroplast, the thylakoid membrane hosts the light-dependent reactions.",
        ),
        # 1.5s: Photons strike Photosystem II
        SemanticBeat(
            at=1.5,
            duration=1.0,
            action="highlight",
            target=["photosystem_ii"],
            narrative_cue="Chlorophyll absorbs incoming photon energy, exciting electrons.",
        ),
        # 2.8s: Water photolysis
        SemanticBeat(
            at=2.8,
            duration=1.2,
            action="split",
            target=["water_splitting_site"],
            narrative_cue="Water molecules are split, releasing oxygen and pumping protons into the thylakoid lumen.",
        ),
        # 4.5s: Proton gradient drives ATP Synthase rotor
        SemanticBeat(
            at=4.5,
            duration=2.0,
            action="transform",
            target=["atp_synthase"],
            semantic_value="synthesizing_atp",
            narrative_cue="The resulting electrochemical proton gradient drives ATP Synthase to generate cellular ATP.",
        ),
    ]

    camera: list[SemanticCameraKeyframe] = [
        SemanticCameraKeyframe(at=0.0, action="establish"),
        SemanticCameraKeyframe(at=1.5, action="focus", target=["photosystem_ii"], zoom_factor=1.25),
        SemanticCameraKeyframe(at=4.5, action="focus", target=["atp_synthase"], zoom_factor=1.3),
        SemanticCameraKeyframe(at=6.2, action="pullback"),
    ]

    return AnimationSceneSpec(
        scene_id="bio_photosynthesis_light_reaction",
        domain="biology",
        duration=duration_seconds,
        fps=30,
        objects=objects,
        beats=beats,
        camera=camera,
    )


def render_biology_motion(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 7.0,
    out_path: Path | None = None,
) -> Path:
    """Entry point for biology scenes routed to Motion Canvas."""
    spec = build_biology_photosynthesis_spec(payload_dict, narration_text, duration_seconds)
    return render_motion_canvas_spec(spec, duration_seconds=duration_seconds, out_path=out_path)
