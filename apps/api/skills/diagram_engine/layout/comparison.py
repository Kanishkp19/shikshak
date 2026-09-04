"""Fixed two-column, mirrored comparison layout."""
from __future__ import annotations

from ..schemas import DiagramSpec
from ..text_measure import measure_node
from .common import CANVAS_WIDTH, GAP_Y, MARGIN_X, MARGIN_Y, LayoutResult, PositionedEdge, PositionedNode, assert_no_overlaps
from ..style_tokens import STYLE


def layout_comparison(spec: DiagramSpec) -> LayoutResult:
    theme = STYLE[spec.theme]
    split = (len(spec.nodes) + 1) // 2
    columns = (spec.nodes[:split], spec.nodes[split:])
    x_positions = (MARGIN_X + 20, CANVAS_WIDTH / 2 + 30)
    positioned: dict[str, PositionedNode] = {}
    for column, x in zip(columns, x_positions):
        y = MARGIN_Y + 58
        for node in column:
            size = measure_node(node, theme)
            positioned[node.id] = PositionedNode(node, x, y, size.width, size.height, size)
            y += size.height + GAP_Y
    assert_no_overlaps(positioned.values())
    return LayoutResult(
        nodes=positioned,
        edges=[PositionedEdge(edge.source_id, edge.target_id, edge.label) for edge in spec.edges],
    )
