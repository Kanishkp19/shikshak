"""
Shikshak AI — Semantic Animation Intermediate Representation (IR).

Non-negotiable architectural guarantee:
The LLM and scene planner express pedagogical intent ONLY.
They MUST NOT generate:
- x, y, width, height
- pixel coordinates
- CSS layout
- arbitrary SVG paths
- arbitrary HTML/React/Motion Canvas code

The Motion Canvas engine resolves all geometry, layout, camera transforms,
and kinetic realization from this semantic specification.
"""
from __future__ import annotations

import re
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


def _cam(snake: str) -> str:
    """snake_case -> camelCase"""
    head, *tail = snake.split("_")
    return head + "".join(t.title() for t in tail)


class SpecBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_cam,
        populate_by_name=True,
        from_attributes=True,
    )


# ── Forbidden coordinate & raw-drawing patterns ──────────────────────────────
FORBIDDEN_COORDINATE_KEYS = {
    "x", "y", "z", "w", "h", "width", "height", "dx", "dy",
    "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2",
    "top", "left", "right", "bottom", "pos_x", "pos_y",
    "coord_x", "coord_y", "pixel_x", "pixel_y",
    "svg_path", "raw_svg", "raw_html", "raw_code", "css",
}


def _check_for_forbidden_coordinates(data: dict[str, Any], path: str = "") -> None:
    for key, val in data.items():
        k_clean = key.lower().strip()
        current_path = f"{path}.{key}" if path else key
        if k_clean in FORBIDDEN_COORDINATE_KEYS:
            raise ValueError(
                f"Coordinate Invariance Violation: Forbidden layout/drawing field '{current_path}' detected. "
                "The LLM/planner must express semantic intent only, never geometry or pixel positions."
            )
        if isinstance(val, dict):
            _check_for_forbidden_coordinates(val, current_path)


# ── Semantic Object ──────────────────────────────────────────────────────────
class SemanticObject(SpecBaseModel):
    """A scientifically verified pedagogical object within an animation scene."""
    id: str
    type: str  # atom, molecule, bond, particle, wire, switch, resistor, membrane, organelle, equation, term, etc.
    source: str = "scientific_engine"  # rdkit, iec, bio_icons, latex, system
    semantic_role: str  # e.g. "reactant_iron", "current_drift", "chlorophyll_hub"
    pedagogical_purpose: str  # e.g. "count reactant iron atoms", "show electron flow"
    importance: float = 1.0  # 0.0 to 1.0
    label: Optional[str] = None
    formula: Optional[str] = None
    count: Optional[int] = None
    properties: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def validate_no_coordinates(cls, values: Any) -> Any:
        if isinstance(values, dict):
            _check_for_forbidden_coordinates(values)
        return values


# ── Semantic Animation Beat ──────────────────────────────────────────────────
SemanticAction = Literal[
    "introduce", "reveal", "highlight", "focus", "dim", "emphasize", "pulse",
    "trace", "draw", "move", "transform", "morph", "duplicate", "split", "merge",
    "count", "compare", "follow", "zoom", "pan", "camera_focus", "camera_pullback",
    "group", "fade", "equation_transform", "coefficient_insert", "object_compare",
    "flow_particle", "process_step", "cause_effect", "progressive_build", "remove", "reorder"
]


class SemanticBeat(SpecBaseModel):
    """An educational animation event scheduled on the scene timeline."""
    at: float  # Start time in seconds relative to scene start
    duration: float = 0.5  # Duration of the animation action
    action: str  # SemanticAction or domain-specific semantic action
    target: list[str] = Field(default_factory=list)  # Target object IDs
    semantic_value: Optional[Any] = None  # e.g. new coefficient (3), state change ("closed")
    narrative_cue: Optional[str] = None  # Synchronized voice-over snippet
    easing: str = "ease_in_out"

    @model_validator(mode="before")
    @classmethod
    def validate_no_coordinates(cls, values: Any) -> Any:
        if isinstance(values, dict):
            _check_for_forbidden_coordinates(values)
        return values


# ── Semantic Camera Keyframe ─────────────────────────────────────────────────
CameraAction = Literal[
    "establish", "focus", "follow", "zoom_in", "zoom_out", "pan", "pullback"
]


class SemanticCameraKeyframe(SpecBaseModel):
    """A semantic camera instruction targeting educational regions or objects."""
    at: float  # Time in seconds
    action: CameraAction = "focus"
    target: list[str] = Field(default_factory=list)  # Target object IDs to frame
    zoom_factor: float = 1.0  # Normalized zoom level (1.0 = normal, 1.5 = close-up)
    transition_duration: float = 0.8

    @model_validator(mode="before")
    @classmethod
    def validate_no_coordinates(cls, values: Any) -> Any:
        if isinstance(values, dict):
            _check_for_forbidden_coordinates(values)
        return values


# ── Narrative Timing Marker ──────────────────────────────────────────────────
class NarrativeMarker(SpecBaseModel):
    time_seconds: float
    word_cue: str


# ── Complete Animation Scene Specification ───────────────────────────────────
class AnimationSceneSpec(SpecBaseModel):
    """Root specification passed from scientific adapters to Motion Canvas."""
    scene_id: str
    domain: Literal["chemistry", "physics", "biology", "mathematics", "general"] = "general"
    duration: float = 6.0
    fps: int = 30
    width: int = 1280
    height: int = 720
    objects: list[SemanticObject] = Field(default_factory=list)
    beats: list[SemanticBeat] = Field(default_factory=list)
    camera: list[SemanticCameraKeyframe] = Field(default_factory=list)
    narrative_sync: list[NarrativeMarker] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def validate_spec(cls, values: Any) -> Any:
        if isinstance(values, dict):
            _check_for_forbidden_coordinates(values)
        return values
