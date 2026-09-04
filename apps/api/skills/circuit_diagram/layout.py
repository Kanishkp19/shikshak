"""Circuit-specific loop and branch topology; never a generic flowchart."""
from __future__ import annotations

from dataclasses import dataclass

from skills.diagram_engine.style_tokens import STYLE
from skills.diagram_engine.text_measure import get_font

from .schemas import CircuitDiagramSpec


@dataclass(frozen=True)
class CircuitPosition:
    component_id: str
    x: float
    y: float
    width: float = 96
    height: float = 72
    label_x: float = 0
    label_y: float = 0

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return (self.x - self.width / 2, self.y - self.height / 2, self.x + self.width / 2, self.y + self.height / 2)


@dataclass(frozen=True)
class CircuitLayout:
    positions: dict[str, CircuitPosition]
    wire_paths: tuple[tuple[tuple[float, float], ...], ...]


def _label_position(x: float, y: float, index: int) -> tuple[float, float]:
    # Alternating below/above prevents adjacent component labels from colliding.
    return (x, y + (58 if index % 2 == 0 else -50))


def layout_series_circuit(spec: CircuitDiagramSpec) -> CircuitLayout:
    """Place components evenly around a closed rectangular current loop."""
    anchors = [(225, 360), (640, 180), (1055, 360), (640, 540)]
    positions: dict[str, CircuitPosition] = {}
    for index, component in enumerate(spec.components):
        x, y = anchors[index % len(anchors)]
        label_x, label_y = _label_position(x, y, index)
        positions[component.id] = CircuitPosition(component.id, x, y, label_x=label_x, label_y=label_y)
    wires = (((225, 180), (1055, 180), (1055, 540), (225, 540), (225, 180)),)
    return CircuitLayout(positions=positions, wire_paths=wires)


def layout_parallel_circuit(spec: CircuitDiagramSpec) -> CircuitLayout:
    """Use two vertical rails and horizontal branches for a parallel circuit."""
    positions: dict[str, CircuitPosition] = {}
    battery = next((component for component in spec.components if component.component_type == "battery"), spec.components[0])
    positions[battery.id] = CircuitPosition(battery.id, 210, 360, label_x=210, label_y=430)
    branches = [component for component in spec.components if component.id != battery.id]
    branch_y = [190, 360, 530]
    for index, component in enumerate(branches):
        x = 610 if index % 2 == 0 else 920
        y = branch_y[index % len(branch_y)]
        label_x, label_y = _label_position(x, y, index)
        positions[component.id] = CircuitPosition(component.id, x, y, label_x=label_x, label_y=label_y)
    wires: list[tuple[tuple[float, float], ...]] = [((320, 130), (320, 590)), ((1110, 130), (1110, 590))]
    for y in branch_y[:max(1, len(branches))]:
        wires.append(((320, y), (1110, y)))
    return CircuitLayout(positions=positions, wire_paths=tuple(wires))


def assert_no_symbol_overlap(layout: CircuitLayout) -> None:
    positions = list(layout.positions.values())
    for index, current in enumerate(positions):
        ax1, ay1, ax2, ay2 = current.bounds
        for other in positions[index + 1 :]:
            bx1, by1, bx2, by2 = other.bounds
            if not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1):
                raise ValueError(f"Circuit symbol overlap: {current.component_id}, {other.component_id}")


def layout_circuit(spec: CircuitDiagramSpec) -> CircuitLayout:
    layout = layout_series_circuit(spec) if spec.circuit_type == "series" else layout_parallel_circuit(spec)
    assert_no_symbol_overlap(layout)
    return layout
