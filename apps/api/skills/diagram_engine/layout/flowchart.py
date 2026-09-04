"""Measured top-to-bottom layered (Sugiyama-style) flowchart layout."""
from __future__ import annotations

from collections import defaultdict

import networkx as nx

from ..schemas import DiagramSpec
from ..text_measure import measure_node
from .common import (
    CANVAS_WIDTH,
    GAP_X,
    GAP_Y,
    MARGIN_X,
    MARGIN_Y,
    LayoutResult,
    PositionedEdge,
    PositionedNode,
    assert_no_overlaps,
)


def _layers(spec: DiagramSpec) -> list[list[str]]:
    graph = nx.DiGraph()
    graph.add_nodes_from(node.id for node in spec.nodes)
    graph.add_edges_from((edge.source_id, edge.target_id) for edge in spec.edges)
    if not nx.is_directed_acyclic_graph(graph):
        return [[node.id] for node in spec.nodes]
    level: dict[str, int] = {}
    for node_id in nx.topological_sort(graph):
        predecessors = list(graph.predecessors(node_id))
        level[node_id] = max((level[parent] + 1 for parent in predecessors), default=0)
    grouped: dict[int, list[str]] = defaultdict(list)
    for node in spec.nodes:
        grouped[level[node.id]].append(node.id)
    return [grouped[index] for index in sorted(grouped)]


def _place_layered(spec: DiagramSpec, *, hierarchy: bool = False) -> LayoutResult:
    theme = __import__("skills.diagram_engine.style_tokens", fromlist=["STYLE"]).STYLE[spec.theme]
    node_by_id = {node.id: node for node in spec.nodes}
    sizes = {node.id: measure_node(node, theme) for node in spec.nodes}
    y = MARGIN_Y
    positioned: dict[str, PositionedNode] = {}
    for layer in _layers(spec):
        # Break overly wide layers into measured rows. This preserves the DAG
        # ordering while guaranteeing labels never overlap or clip at 1280px.
        rows: list[list[str]] = [[]]
        row_width = 0.0
        for node_id in layer:
            needed = sizes[node_id].width + (GAP_X if rows[-1] else 0)
            if rows[-1] and row_width + needed > CANVAS_WIDTH - 2 * MARGIN_X:
                rows.append([])
                row_width = 0.0
                needed = sizes[node_id].width
            rows[-1].append(node_id)
            row_width += needed
        for row in rows:
            width = sum(sizes[node_id].width for node_id in row) + GAP_X * max(0, len(row) - 1)
            row_height = max(sizes[node_id].height for node_id in row)
            x = (CANVAS_WIDTH - width) / 2
            for node_id in row:
                size = sizes[node_id]
                positioned[node_id] = PositionedNode(
                    node=node_by_id[node_id], x=x, y=y + (row_height - size.height) / 2,
                    width=size.width, height=size.height, size=size,
                )
                x += size.width + GAP_X
            y += row_height + (GAP_Y if not hierarchy else GAP_Y + 6)
        y += 8
    edges = [PositionedEdge(edge.source_id, edge.target_id, edge.label) for edge in spec.edges]
    assert_no_overlaps(positioned.values())
    return LayoutResult(nodes=positioned, edges=edges)


def layout_flowchart(spec: DiagramSpec) -> LayoutResult:
    return _place_layered(spec)
