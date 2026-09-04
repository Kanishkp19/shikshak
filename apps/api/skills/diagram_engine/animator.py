"""Deterministic node/edge animation timing synced to narration duration."""
from __future__ import annotations

from dataclasses import dataclass

from .schemas import ContentBlueprint


@dataclass(frozen=True)
class AnimationState:
    node_opacity: dict[str, float]
    active_node_ids: frozenset[str]
    edge_progress: float


def animation_state(blueprint: ContentBlueprint, at_ms: int) -> AnimationState:
    spec = blueprint.diagram_spec
    duration = max(1, blueprint.narration_duration_estimate_ms)
    fallback_step = duration / max(1, len(spec.nodes))
    opacities: dict[str, float] = {}
    active: set[str] = set()
    for index, node in enumerate(spec.nodes):
        start = node.highlight_at_ms if node.highlight_at_ms is not None else int(index * fallback_step)
        fade = min(1.0, max(0.0, (at_ms - start) / 280))
        opacities[node.id] = fade
        if 0 < at_ms - start < 700:
            active.add(node.id)
    return AnimationState(
        node_opacity=opacities,
        active_node_ids=frozenset(active),
        edge_progress=min(1.0, max(0.0, at_ms / duration)),
    )


def keyframe_times(blueprint: ContentBlueprint, fps: int = 24) -> list[int]:
    duration = blueprint.narration_duration_estimate_ms
    frames = max(1, round(duration / 1000 * fps))
    return [round(index * duration / frames) for index in range(frames)]
