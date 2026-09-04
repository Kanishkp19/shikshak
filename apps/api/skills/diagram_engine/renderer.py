"""SVG/CairoSVG renderer for deterministic Diagram Engine frames."""
from __future__ import annotations

import html
import os
from pathlib import Path

from .animator import animation_state
from .layout import layout_comparison, layout_cross_section, layout_cycle, layout_flowchart, layout_hierarchy
from .layout.common import LayoutResult, PositionedNode, center
from .schemas import ContentBlueprint, DiagramSpec
from .style_tokens import STYLE

os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")


def compute_layout(spec: DiagramSpec) -> LayoutResult:
    return {
        "flowchart": layout_flowchart,
        "cross_section": layout_cross_section,
        "comparison": layout_comparison,
        "hierarchy": layout_hierarchy,
        "cycle": layout_cycle,
    }[spec.layout](spec)


def _svg_text(lines: tuple[str, ...], x: float, y: float, font_size: int, color: str, anchor: str = "middle") -> str:
    line_height = font_size + 4
    return "".join(
        f'<text x="{x:.1f}" y="{y + index * line_height:.1f}" text-anchor="{anchor}" '
        f'font-size="{font_size}" fill="{color}">{html.escape(line)}</text>'
        for index, line in enumerate(lines)
    )


def _edge_svg(layout: LayoutResult, source_id: str, target_id: str, label: str | None, color: str, progress: float) -> str:
    source = layout.nodes.get(source_id)
    target = layout.nodes.get(target_id)
    if not source or not target:
        return ""
    x1, y1 = center(source)
    x2, y2 = center(target)
    end_x = x1 + (x2 - x1) * progress
    end_y = y1 + (y2 - y1) * progress
    label_svg = ""
    if label and progress > 0.75:
        label_svg = f'<text x="{(x1+x2)/2:.1f}" y="{(y1+y2)/2 - 7:.1f}" text-anchor="middle" font-size="12" fill="{color}">{html.escape(label)}</text>'
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{end_x:.1f}" y2="{end_y:.1f}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>{label_svg}'


def _node_svg(positioned: PositionedNode, tokens: dict[str, object], opacity: float, active: bool) -> str:
    border = tokens["node_border_active"] if active else tokens["node_border"]
    glow = f'filter="url(#glow)"' if active else ""
    text_x = positioned.x + positioned.width / 2
    label_y = positioned.y + 26
    label = _svg_text(positioned.size.label.lines, text_x, label_y, int(tokens["font_size_label"]), str(tokens["text_color"]))
    sublabel = ""
    if positioned.size.sublabel:
        sub_y = label_y + positioned.size.label.height + 4
        sublabel = _svg_text(positioned.size.sublabel.lines, text_x, sub_y, int(tokens["font_size_sublabel"]), str(tokens["edge_color"]))
    return (
        f'<g opacity="{opacity:.3f}" {glow}>'
        f'<rect x="{positioned.x:.1f}" y="{positioned.y:.1f}" width="{positioned.width:.1f}" height="{positioned.height:.1f}" '
        f'rx="{tokens["corner_radius"]}" fill="{tokens["node_fill"]}" stroke="{border}" stroke-width="2"/>'
        f'{label}{sublabel}</g>'
    )


def render_svg(blueprint: ContentBlueprint, at_ms: int | None = None) -> str:
    spec = blueprint.diagram_spec
    tokens = STYLE[spec.theme]
    layout = compute_layout(spec)
    at_ms = blueprint.narration_duration_estimate_ms if at_ms is None else at_ms
    state = animation_state(blueprint, at_ms)
    edge_svg = "".join(_edge_svg(layout, edge.source_id, edge.target_id, edge.label, str(tokens["edge_color"]), state.edge_progress) for edge in layout.edges)
    node_svg = "".join(_node_svg(node, tokens, state.node_opacity.get(node_id, 1), node_id in state.active_node_ids) for node_id, node in layout.nodes.items())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="{tokens["background"]}"/>
  {edge_svg}{node_svg}
</svg>'''


def render_frame(blueprint: ContentBlueprint, at_ms: int | None = None) -> bytes:
    """Return a PNG frame rendered locally through CairoSVG."""
    import cairosvg

    return cairosvg.svg2png(bytestring=render_svg(blueprint, at_ms).encode("utf-8"), output_width=1280, output_height=720)


def render_frame_to_path(blueprint: ContentBlueprint, output_path: str | Path, at_ms: int | None = None) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(render_frame(blueprint, at_ms))
    return output
