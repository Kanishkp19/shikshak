"""Deterministic current-flow timing for circuit SVG frames."""
from __future__ import annotations

from .layout import CircuitLayout


def current_flow_dash_offset(elapsed_ms: int, pixels_per_second: float = 90.0) -> float:
    """Negative offset moves dashed current clockwise along each stored wire path."""
    return -(elapsed_ms / 1000) * pixels_per_second


def current_flow_direction(layout: CircuitLayout) -> str:
    """Layouts encode wires clockwise/left-to-right, the convention used in render."""
    return "clockwise" if len(layout.wire_paths) == 1 else "left_to_right"
