"""Evenly spaced measured ring layout for cyclical processes."""
from __future__ import annotations

import math

from ..schemas import DiagramSpec
from ..style_tokens import STYLE
from ..text_measure import measure_node
from .common import CANVAS_HEIGHT, CANVAS_WIDTH, LayoutResult, PositionedEdge, PositionedNode, assert_no_overlaps


def layout_cycle(spec: DiagramSpec) -> LayoutResult:
    tokens = STYLE[spec.theme]
    count = len(spec.nodes)
    positioned: dict[str, PositionedNode] = {}
    # A 12-node cycle needs two concentric rings at this fixed lesson-frame
    # size; each ring remains evenly spaced and keeps text boxes collision-free.
    outer_count = count if count <= 8 else (count + 1) // 2
    for index, node in enumerate(spec.nodes):
        size = measure_node(node, tokens)
        outer = index < outer_count
        local_index = index if outer else index - outer_count
        local_count = outer_count if outer else count - outer_count
        angle = -math.pi / 2 + 2 * math.pi * local_index / max(1, local_count)
        rx, ry = (460, 250) if outer else (285, 160)
        x = CANVAS_WIDTH / 2 + rx * math.cos(angle) - size.width / 2
        y = CANVAS_HEIGHT / 2 + ry * math.sin(angle) - size.height / 2
        positioned[node.id] = PositionedNode(node, x, y, size.width, size.height, size)
    assert_no_overlaps(positioned.values())
    return LayoutResult(
        nodes=positioned,
        edges=[PositionedEdge(edge.source_id, edge.target_id, edge.label) for edge in spec.edges],
    )
