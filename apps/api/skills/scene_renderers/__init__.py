"""
Shikshak AI — Universal Scene Renderers Package.

Registry of all domain-specific STEM, Humanities, and Motion scene renderers:
  - Chemistry Pack: reaction_lab, equation_build, experiment_observation, balancing_exercise
  - Physics Pack: circuit_simulation, optics_ray_diagram, spherical_mirror
  - Biology Pack: bio_cellular_process, anatomical_structure
  - Mathematics Pack: number_line_geometry, algebra_step_solve
  - Motion Graphics Pack: motion_graphic, animated_text, generic_motion, step_flow, concept_highlight, timeline_motion
  - Universal Explainer: generic_explainer
"""
from typing import Callable, Any
from pathlib import Path

from skills.scene_renderers.base import SceneRenderer, render_svg_frames_to_mp4
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
from skills.scene_renderers.generative import (
    render_ai_illustration,
    render_kinetic_text,
    render_split_screen,
)
from skills.scene_renderers.router import (
    ROUTER_REGISTRY,
    MOTION_CANVAS_REGISTRY,
    render_generic_motion_canvas,
    resolve_scene_renderer,
    route_and_render_scene,
)

RENDERER_REGISTRY: dict[str, Callable[..., Path]] = ROUTER_REGISTRY


def get_scene_renderer(visual_mode: str) -> Callable[..., Path]:
    """Retrieve the renderer function for a given visual mode."""
    return resolve_scene_renderer(visual_mode)


__all__ = [
    "SceneRenderer",
    "render_svg_frames_to_mp4",
    "RENDERER_REGISTRY",
    "ROUTER_REGISTRY",
    "MOTION_CANVAS_REGISTRY",
    "get_scene_renderer",
    "resolve_scene_renderer",
    "route_and_render_scene",
    "render_reaction_lab",
    "render_equation_build",
    "render_experiment_observation",
    "render_balancing_exercise",
    "render_circuit_simulation",
    "render_optics_ray_diagram",
    "render_spherical_mirror_optics",
    "render_bio_cellular_process",
    "render_anatomical_structure",
    "render_number_line_geometry",
    "render_algebra_step_solve",
    "render_generic_explainer",
    "render_chemistry_motion",
    "render_physics_motion",
    "render_biology_motion",
    "render_mathematics_motion",
    "render_generic_motion_canvas",
    "render_ai_illustration",
    "render_kinetic_text",
    "render_split_screen",
]
