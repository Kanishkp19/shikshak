"""Compose sourced IEC SVG symbols into deterministic circuit layouts."""
from __future__ import annotations

import base64
import html
import os
from pathlib import Path

from skills.diagram_engine import ContentBlueprint, DiagramNode, DiagramSpec
from skills.diagram_engine.renderer import render_frame
from skills.diagram_engine.style_tokens import STYLE

from .current_flow_animation import current_flow_dash_offset
from .layout import CircuitLayout, layout_circuit
from .schemas import CircuitDiagramSpec

os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")
ASSET_ROOT = Path(__file__).resolve().parents[4] / "assets" / "circuit_symbols"


def _symbol_filename(component_type: str, state: str | None) -> str:
    if component_type == "switch":
        return f"switch_{state or 'open'}.svg"
    return f"{component_type}.svg"


def _asset_uri(path: Path) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _fallback(spec: CircuitDiagramSpec) -> bytes:
    return render_frame(ContentBlueprint(
        segment_id="circuit-fallback", narration_script="Circuit components", narration_duration_estimate_ms=1_000,
        diagram_spec=DiagramSpec(
            layout="flowchart",
            nodes=[DiagramNode(id=item.id, label=(item.label or item.component_type)[:28], node_type="process") for item in spec.components],
        ),
    ))


def render_circuit_svg(spec: CircuitDiagramSpec, elapsed_ms: int = 0, theme: str = "light_textbook") -> str:
    layout = layout_circuit(spec)
    tokens = STYLE[theme]
    component_by_id = {item.id: item for item in spec.components}
    asset_paths = {item.id: ASSET_ROOT / _symbol_filename(item.component_type, item.state) for item in spec.components}
    if any(not path.is_file() for path in asset_paths.values()):
        return ""
    wires = "".join(
        f'<polyline points="{" ".join(f"{x},{y}" for x, y in path)}" fill="none" stroke="{tokens["edge_color"]}" stroke-width="4" '
        f'{"stroke-dasharray=\"12 9\" stroke-dashoffset=\"" + str(current_flow_dash_offset(elapsed_ms)) + "\"" if spec.highlight_current_path else ""}/>'
        for path in layout.wire_paths
    )
    symbols = ""
    for component_id, position in layout.positions.items():
        component = component_by_id[component_id]
        symbols += f'<image href="{_asset_uri(asset_paths[component_id])}" x="{position.x - 48}" y="{position.y - 36}" width="96" height="72"/>'
        if component.label:
            symbols += f'<text x="{position.label_x}" y="{position.label_y}" text-anchor="middle" font-size="{tokens["font_size_label"]}" fill="{tokens["text_color"]}">{html.escape(component.label)}</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><rect width="1280" height="720" fill="{tokens["background"]}"/>{wires}{symbols}</svg>'


def render_circuit_diagram(spec: CircuitDiagramSpec, elapsed_ms: int = 0, theme: str = "light_textbook") -> bytes:
    svg = render_circuit_svg(spec, elapsed_ms, theme)
    if not svg:
        return _fallback(spec)
    import cairosvg

    return cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=1280, output_height=720)
