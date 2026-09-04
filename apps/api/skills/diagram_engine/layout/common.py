"""Shared computed geometry; never part of LLM-facing schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ..schemas import DiagramNode
from ..text_measure import NodeBoxSize

CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720
MARGIN_X = 52
MARGIN_Y = 54
GAP_X = 28
GAP_Y = 28


@dataclass(frozen=True)
class PositionedNode:
    node: DiagramNode
    x: float
    y: float
    width: float
    height: float
    size: NodeBoxSize

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass(frozen=True)
class PositionedEdge:
    source_id: str
    target_id: str
    label: str | None = None
    points: tuple[tuple[float, float], ...] = ()


@dataclass
class LayoutResult:
    nodes: dict[str, PositionedNode]
    edges: list[PositionedEdge] = field(default_factory=list)
    center_asset: str | None = None


def boxes_overlap(left: PositionedNode, right: PositionedNode, padding: float = 0) -> bool:
    ax1, ay1, ax2, ay2 = left.bounds
    bx1, by1, bx2, by2 = right.bounds
    return not (ax2 + padding <= bx1 or bx2 + padding <= ax1 or ay2 + padding <= by1 or by2 + padding <= ay1)


def assert_no_overlaps(nodes: Iterable[PositionedNode]) -> None:
    positioned = list(nodes)
    for index, node in enumerate(positioned):
        for other in positioned[index + 1 :]:
            if boxes_overlap(node, other):
                raise ValueError(f"Layout overlap: {node.node.id} and {other.node.id}")


def center(node: PositionedNode) -> tuple[float, float]:
    return (node.x + node.width / 2, node.y + node.height / 2)
