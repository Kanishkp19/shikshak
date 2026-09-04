"""Central illustrated shape with measured radial satellite callouts."""
from __future__ import annotations

import math
from typing import Iterable

from ..schemas import DiagramNode, DiagramSpec
from ..style_tokens import STYLE
from ..text_measure import measure_node
from .common import CANVAS_HEIGHT, CANVAS_WIDTH, LayoutResult, PositionedEdge, PositionedNode, assert_no_overlaps


def layout_cross_section(
    spec: DiagramSpec | None = None,
    *,
    center_asset: str | None = None,
    satellites: Iterable[DiagramNode] | None = None,
    theme: str = "light_textbook",
) -> LayoutResult:
    """Place callouts around a central node or an externally supplied SVG asset."""
    if spec is not None:
        selected_theme = spec.theme
        center_node = spec.nodes[0]
        satellite_nodes = spec.nodes[1:]
        edges = [PositionedEdge(edge.source_id, edge.target_id, edge.label) for edge in spec.edges]
    else:
        selected_theme = theme
        center_node = DiagramNode(id="center", label="Structure", node_type="concept")
        satellite_nodes = list(satellites or [])
        edges = [PositionedEdge("center", node.id) for node in satellite_nodes]
    tokens = STYLE[selected_theme]
    center_size = measure_node(center_node, tokens)
    center_width = max(250, center_size.width + 58) if center_asset else center_size.width + 44
    center_height = max(190, center_size.height + 48) if center_asset else center_size.height + 30
    center = PositionedNode(
        center_node, (CANVAS_WIDTH - center_width) / 2, (CANVAS_HEIGHT - center_height) / 2,
        center_width, center_height, center_size,
    )
    positioned = {center.node.id: center}
    count = len(satellite_nodes)
    # The ellipse gives labels more horizontal separation than a circle. For
    # dense diagrams, alternating inner/outer radii preserves no-overlap.
    for index, node in enumerate(satellite_nodes):
        size = measure_node(node, tokens)
        angle = -math.pi / 2 + 2 * math.pi * index / max(1, count)
        ring = 1 if count <= 7 or index % 2 == 0 else 0.78
        rx, ry = 465 * ring, 255 * ring
        x = CANVAS_WIDTH / 2 + rx * math.cos(angle) - size.width / 2
        y = CANVAS_HEIGHT / 2 + ry * math.sin(angle) - size.height / 2
        positioned[node.id] = PositionedNode(node, x, y, size.width, size.height, size)
    assert_no_overlaps(positioned.values())
    return LayoutResult(nodes=positioned, edges=edges, center_asset=center_asset)
