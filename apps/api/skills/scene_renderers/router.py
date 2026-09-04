"""
Shikshak AI — Centralized Visual Renderer Router.

Enforces deterministic dispatch between visual modes and rendering engines:
  - Chemistry Pack → RDKit & Reaction Lab Vector Engines
  - Physics Pack → IEC 60617 Circuit & Optics Vector Engines
  - Biology Pack → BioIcons Cellular & Anatomical Vector Engines
  - Mathematics Pack → Coordinate Geometry & Algebraic Step Solvers
  - Motion Graphics Pack → Flick / Remotion Deterministic Animation Engine
  - Universal Fallback → CairoSVG Illustrated Explainer

Controlled strictly by the VisualMode schema — no arbitrary renderer selection permitted.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from skills.scene_renderers.chemistry import (
    render_reaction_lab,
    render_equation_build,
    render_experiment_observation,
    render_balancing_exercise,
    render_generic_explainer,
)
from skills.scene_renderers.physics import (
    render_circuit_simulation,
    render_optics_ray_diagram,
    render_spherical_mirror_optics,
)
from skills.scene_renderers.biology import (
    render_bio_cellular_process,
    render_anatomical_structure,
)
from skills.scene_renderers.mathematics import (
    render_number_line_geometry,
    render_algebra_step_solve,
)
from skills.scene_renderers.chemistry.motion_adapter import render_chemistry_motion
from skills.scene_renderers.physics.motion_adapter import render_physics_motion
from skills.scene_renderers.biology.motion_adapter import render_biology_motion
from skills.scene_renderers.mathematics.motion_adapter import render_mathematics_motion
from skills.scene_renderers.flick_renderer import render_flick_motion

logger = logging.getLogger(__name__)


def render_generic_motion_canvas(
    payload_dict: dict[str, Any],
    narration_text: str = "",
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
) -> Path:
    """Primary Motion Canvas renderer for multi-subject motion graphics."""
    try:
        from models.animation_spec import AnimationSceneSpec, SemanticObject, SemanticBeat
        from skills.scene_renderers.motion_canvas_renderer import render_motion_canvas_spec

        title = payload_dict.get("title") or "Lesson Concept"
        steps = payload_dict.get("steps") or []
        objects = [
            SemanticObject(
                id=f"step_{idx+1}",
                type="process_step",
                source="system",
                semantic_role=f"step_{idx+1}",
                pedagogical_purpose=f"explain step: {s}",
                importance=1.0,
                label=s,
            )
            for idx, s in enumerate(steps)
        ] or [
            SemanticObject(
                id="main_concept",
                type="concept",
                source="system",
                semantic_role="core_topic",
                pedagogical_purpose=title,
                importance=1.0,
                label=title,
            )
        ]
        step_interval = duration_seconds / max(1, len(objects))
        beats = [
            SemanticBeat(
                at=idx * step_interval,
                duration=min(1.0, step_interval * 0.8),
                action="introduce",
                target=[obj.id],
            )
            for idx, obj in enumerate(objects)
        ]
        spec = AnimationSceneSpec(
            scene_id=f"motion_{title[:20]}",
            domain="general",
            duration=duration_seconds,
            objects=objects,
            beats=beats,
        )
        return render_motion_canvas_spec(spec, duration_seconds=duration_seconds, out_path=out_path)
    except Exception as exc:
        logger.warning("[Router] Motion Canvas generic dispatch failed: %s; falling back to Flick", exc)
        return render_flick_motion(payload_dict, narration_text, duration_seconds, out_path)


# Single source of truth mapping controlled visual_mode → renderer function
ROUTER_REGISTRY: dict[str, Callable[..., Path]] = {
    # ── Chemistry Pack ──────────────────────────────────────────────
    "reaction_lab":           render_reaction_lab,
    "equation_build":         render_equation_build,
    "experiment_observation":  render_experiment_observation,
    "balancing_exercise":     render_chemistry_motion,

    # ── Physics Pack ────────────────────────────────────────────────
    "circuit_simulation":     render_circuit_simulation,
    "optics_ray_diagram":     render_optics_ray_diagram,
    "spherical_mirror":       render_spherical_mirror_optics,

    # ── Biology Pack ────────────────────────────────────────────────
    "bio_cellular_process":   render_bio_cellular_process,
    "anatomical_structure":   render_anatomical_structure,

    # ── Mathematics Pack ────────────────────────────────────────────
    "number_line_geometry":   render_number_line_geometry,
    "algebra_step_solve":     render_algebra_step_solve,

    # ── Flick / Remotion Motion Graphics Pack (Legacy Multi-Subject) ─
    "motion_graphic":         render_flick_motion,
    "animated_text":          render_flick_motion,
    "generic_motion":         render_flick_motion,
    "step_flow":              render_flick_motion,
    "concept_highlight":      render_flick_motion,
    "timeline_motion":        render_flick_motion,

    # ── Motion Canvas Primary Dedicated Modes ───────────────────────
    "chemistry_motion":       render_chemistry_motion,
    "physics_motion":         render_physics_motion,
    "biology_motion":         render_biology_motion,
    "mathematics_motion":     render_mathematics_motion,
    "motion_canvas":          render_generic_motion_canvas,

    # ── Universal Illustrated Fallback ──────────────────────────────
    "generic_explainer":      render_generic_explainer,
}

# Dedicated Motion Canvas Registry (Next-Gen Educational Explainer Layer)
MOTION_CANVAS_REGISTRY: dict[str, Callable[..., Path]] = {
    "reaction_lab":           render_chemistry_motion,
    "equation_build":         render_chemistry_motion,
    "balancing_exercise":     render_chemistry_motion,
    "circuit_simulation":     render_physics_motion,
    "optics_ray_diagram":     render_physics_motion,
    "spherical_mirror":       render_spherical_mirror_optics,
    "bio_cellular_process":   render_biology_motion,
    "anatomical_structure":   render_biology_motion,
    "number_line_geometry":   render_mathematics_motion,
    "algebra_step_solve":     render_mathematics_motion,
    "motion_graphic":         render_generic_motion_canvas,
    "animated_text":          render_generic_motion_canvas,
    "generic_motion":         render_generic_motion_canvas,
    "step_flow":              render_generic_motion_canvas,
    "concept_highlight":      render_generic_motion_canvas,
    "timeline_motion":        render_generic_motion_canvas,
}


def resolve_scene_renderer(visual_mode: str, engine: str = "default") -> Callable[..., Path]:
    """Retrieve the deterministic renderer for a given visual mode.

    Guarantees scientific isolation: Chemistry, Physics, Biology, and Math
    modes resolve to their dedicated vector kits or Motion Canvas adapters.
    """
    if engine == "motion_canvas":
        mc_renderer = MOTION_CANVAS_REGISTRY.get(visual_mode)
        if mc_renderer is not None:
            return mc_renderer

    renderer = ROUTER_REGISTRY.get(visual_mode)
    if renderer is None:
        logger.info("[Router] Unknown visual_mode %r, resolving to generic_explainer fallback", visual_mode)
        return render_generic_explainer
    return renderer


def route_and_render_scene(
    scene: dict[str, Any],
    duration_seconds: float = 6.0,
    out_path: Path | None = None,
    engine: str = "default",
) -> Path:
    """Validate visual mode and execute rendering via the resolved backend."""
    mode = scene.get("visual_mode", "generic_explainer")
    selected_engine = scene.get("animation_engine") or scene.get("engine") or engine
    renderer = resolve_scene_renderer(mode, engine=selected_engine)
    payload = scene.get("visual_payload") or {}
    narration = scene.get("narration_text") or ""
    return renderer(
        payload_dict=payload,
        narration_text=narration,
        duration_seconds=duration_seconds,
        out_path=out_path,
    )
