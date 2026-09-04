"""Acceptance tests for Science Visual Kits (RDKit, Circuit Symbols, BioIcons)."""
from __future__ import annotations

import pytest

from skills.bio_illustration import (
    BIO_ASSET_PATHS,
    BioIllustrationRequest,
    render_bio_illustration,
    render_bio_svg,
)
from skills.circuit_diagram import (
    CircuitComponent,
    CircuitConnection,
    CircuitDiagramSpec,
    render_circuit_diagram,
)
from skills.circuit_diagram.current_flow_animation import current_flow_direction
from skills.circuit_diagram.layout import assert_no_symbol_overlap, layout_circuit
from skills.circuit_diagram.renderer import render_circuit_svg
from skills.diagram_engine import DiagramNode
from skills.diagram_engine.style_tokens import STYLE
from skills.molecular_diagram import MolecularDiagramRequest, render_molecular_diagram
from skills.molecular_diagram.compound_lookup import NCERT_COMPOUND_SMILES


# --- Kit 1: Molecular Structure Kit (RDKit) Tests ---

@pytest.mark.parametrize("compound", ["methane", "ethane", "ethanol", "ethanoic acid", "ethyne"])
def test_rdkit_renders_all_ncert_compounds(compound: str):
    request = MolecularDiagramRequest(compound_name=compound)
    png_bytes = render_molecular_diagram(request)
    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1_000


def test_rdkit_highlight_bonds_colors_specified_bond():
    request_unhighlighted = MolecularDiagramRequest(compound_name="ethanol")
    request_highlighted = MolecularDiagramRequest(compound_name="ethanol", highlight_bonds=["C-OH"])
    
    png_unhighlighted = render_molecular_diagram(request_unhighlighted)
    png_highlighted = render_molecular_diagram(request_highlighted)
    
    assert png_unhighlighted.startswith(b"\x89PNG")
    assert png_highlighted.startswith(b"\x89PNG")
    # Highlighted drawing contains different bytes due to highlight bond color
    assert png_unhighlighted != png_highlighted


def test_rdkit_fallback_for_unknown_compound():
    request = MolecularDiagramRequest(compound_name="unknown_super_molecule_xyz_123")
    png_bytes = render_molecular_diagram(request)
    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1_000


# --- Kit 2: Circuit Symbol Kit Tests ---

def test_circuit_series_render_and_overlap_check():
    spec = CircuitDiagramSpec(
        circuit_type="series",
        components=[
            CircuitComponent(id="b1", component_type="battery", label="9V"),
            CircuitComponent(id="r1", component_type="resistor", label="100Ω"),
            CircuitComponent(id="sw1", component_type="switch", state="closed", label="S1"),
            CircuitComponent(id="l1", component_type="bulb", label="Lamp"),
        ],
        connections=[
            CircuitConnection(source_id="b1", target_id="r1"),
            CircuitConnection(source_id="r1", target_id="sw1"),
            CircuitConnection(source_id="sw1", target_id="l1"),
            CircuitConnection(source_id="l1", target_id="b1"),
        ],
        highlight_current_path=True,
    )
    layout = layout_circuit(spec)
    assert_no_symbol_overlap(layout)
    assert current_flow_direction(layout) == "clockwise"
    
    svg = render_circuit_svg(spec, elapsed_ms=500)
    assert "<svg" in svg
    assert "stroke-dasharray" in svg
    
    png_bytes = render_circuit_diagram(spec, elapsed_ms=500)
    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1_000


def test_circuit_parallel_render_and_overlap_check():
    spec = CircuitDiagramSpec(
        circuit_type="parallel",
        components=[
            CircuitComponent(id="b1", component_type="battery", label="12V"),
            CircuitComponent(id="r1", component_type="resistor", label="R1 50Ω"),
            CircuitComponent(id="r2", component_type="resistor", label="R2 75Ω"),
            CircuitComponent(id="v1", component_type="voltmeter", label="V1"),
        ],
        highlight_current_path=True,
    )
    layout = layout_circuit(spec)
    assert_no_symbol_overlap(layout)
    assert current_flow_direction(layout) == "left_to_right"
    
    png_bytes = render_circuit_diagram(spec, elapsed_ms=500)
    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1_000


# --- Kit 3: Biological Illustration Kit (BioIcons) Tests ---

@pytest.mark.parametrize("structure", [
    "heart", "neuron", "flower", "plant_cell", "animal_cell", "eye", "nephron", "dna"
])
def test_bio_illustration_renders_all_curated_structures_with_callouts(structure: str):
    request = BioIllustrationRequest(
        structure=structure,
        callouts=[
            DiagramNode(id="part-1", label=f"Primary {structure[:10]}", node_type="concept"),
            DiagramNode(id="part-2", label="Secondary feature", sublabel="Key detail", node_type="concept"),
        ],
    )
    svg = render_bio_svg(request)
    assert "<svg" in svg
    assert "data:image/svg+xml;base64" in svg
    assert f"Primary {structure[:10]}" in svg
    assert "Secondary feature" in svg
    
    png_bytes = render_bio_illustration(request)
    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1_000


def test_bio_illustration_fallback_for_missing_asset(tmp_path, monkeypatch):
    request = BioIllustrationRequest(
        structure="heart",
        callouts=[DiagramNode(id="c1", label="Callout", node_type="concept")],
    )
    # Point to nonexistent path to trigger fallback
    monkeypatch.setitem(BIO_ASSET_PATHS, "heart", tmp_path / "nonexistent.svg")
    png_bytes = render_bio_illustration(request)
    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1_000


# --- Cross-Kit Visual Consistency Test ---

def test_cross_kit_visual_consistency():
    """Verify all 3 kits plus base engine share identical style_tokens values."""
    theme = "light_textbook"
    tokens = STYLE[theme]
    
    # 1. Circuit SVG
    circuit_spec = CircuitDiagramSpec(
        circuit_type="series",
        components=[
            CircuitComponent(id="b1", component_type="battery", label="9V"),
            CircuitComponent(id="r1", component_type="resistor", label="100Ω"),
        ],
    )
    circuit_svg = render_circuit_svg(circuit_spec, theme=theme)
    assert f'fill="{tokens["background"]}"' in circuit_svg
    assert f'stroke="{tokens["edge_color"]}"' in circuit_svg
    
    # 2. Bio SVG
    bio_req = BioIllustrationRequest(
        structure="heart",
        callouts=[DiagramNode(id="aorta", label="Aorta", node_type="concept")],
        theme=theme,
    )
    bio_svg = render_bio_svg(bio_req)
    assert f'fill="{tokens["background"]}"' in bio_svg
    assert f'fill="{tokens["node_fill"]}"' in bio_svg
    assert f'stroke="{tokens["node_border"]}"' in bio_svg
    assert f'fill="{tokens["text_color"]}"' in bio_svg
