"""Biological illustration renderer combining BioIcons vector assets with cross-section layout."""
from __future__ import annotations

import base64
import html
import os
from pathlib import Path

from skills.diagram_engine import ContentBlueprint, DiagramNode, DiagramSpec
from skills.diagram_engine.layout.common import PositionedNode, center
from skills.diagram_engine.layout.cross_section import layout_cross_section
from skills.diagram_engine.renderer import render_frame
from skills.diagram_engine.style_tokens import STYLE

from .asset_manifest import BIO_ASSET_PATHS
from .schemas import BioIllustrationRequest

os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")


def _asset_uri(path: Path) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _generic_fallback(request: BioIllustrationRequest) -> bytes:
    """Fallback to generic cross_section layout with plain labeled boxes."""
    nodes = [DiagramNode(id="center", label=request.structure.replace("_", " ").title()[:28], node_type="concept")]
    nodes.extend(request.callouts)
    blueprint = ContentBlueprint(
        segment_id="bio-fallback",
        narration_script=f"Structure of {request.structure}",
        narration_duration_estimate_ms=1_000,
        diagram_spec=DiagramSpec(
            layout="cross_section",
            theme=request.theme,
            nodes=nodes,
        ),
    )
    return render_frame(blueprint)


def _svg_text(lines: tuple[str, ...], x: float, y: float, font_size: int, color: str, anchor: str = "middle") -> str:
    line_height = font_size + 4
    return "".join(
        f'<text x="{x:.1f}" y="{y + index * line_height:.1f}" text-anchor="{anchor}" '
        f'font-size="{font_size}" fill="{color}">{html.escape(line)}</text>'
        for index, line in enumerate(lines)
    )


def _callout_node_svg(positioned: PositionedNode, tokens: dict[str, object]) -> str:
    text_x = positioned.x + positioned.width / 2
    label_y = positioned.y + 26
    label = _svg_text(positioned.size.label.lines, text_x, label_y, int(tokens["font_size_label"]), str(tokens["text_color"]))
    sublabel = ""
    if positioned.size.sublabel:
        sub_y = label_y + positioned.size.label.height + 4
        sublabel = _svg_text(positioned.size.sublabel.lines, text_x, sub_y, int(tokens["font_size_sublabel"]), str(tokens["edge_color"]))
    return (
        f'<g>'
        f'<rect x="{positioned.x:.1f}" y="{positioned.y:.1f}" width="{positioned.width:.1f}" height="{positioned.height:.1f}" '
        f'rx="{tokens["corner_radius"]}" fill="{tokens["node_fill"]}" stroke="{tokens["node_border"]}" stroke-width="2"/>'
        f'{label}{sublabel}</g>'
    )


def render_bio_svg(request: BioIllustrationRequest) -> str:
    base_svg_path = BIO_ASSET_PATHS.get(request.structure)
    if not base_svg_path or not base_svg_path.is_file():
        return ""

    tokens = STYLE[request.theme]
    layout = layout_cross_section(center_asset=str(base_svg_path), satellites=request.callouts, theme=request.theme)
    center_pos = layout.nodes["center"]
    cx, cy = center(center_pos)

    # Base illustration at the center
    img_w, img_h = 360, 270
    img_x = cx - img_w / 2
    img_y = cy - img_h / 2
    center_img_svg = f'<image href="{_asset_uri(base_svg_path)}" x="{img_x:.1f}" y="{img_y:.1f}" width="{img_w}" height="{img_h}" preserveAspectRatio="xMidYMid meet"/>'

    # Leader lines from center to each satellite
    leader_lines = []
    callout_boxes = []
    for node_id, pos in layout.nodes.items():
        if node_id == "center":
            continue
        sx, sy = center(pos)
        # Leader line from center edge towards satellite center
        leader_lines.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
            f'stroke="{tokens["edge_color"]}" stroke-width="2" stroke-dasharray="4 3"/>'
        )
        callout_boxes.append(_callout_node_svg(pos, tokens))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="{tokens["background"]}"/>
  {"".join(leader_lines)}
  {center_img_svg}
  {"".join(callout_boxes)}
</svg>'''


def render_bio_illustration(request: BioIllustrationRequest) -> bytes:
    """Render a biological illustration with satellite callouts to PNG bytes."""
    svg = render_bio_svg(request)
    if not svg:
        return _generic_fallback(request)
    import cairosvg

    return cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=1280, output_height=720)
