"""RDKit 2D structure renderer using Diagram Engine style tokens."""
from __future__ import annotations

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

from skills.diagram_engine import ContentBlueprint, DiagramNode, DiagramSpec
from skills.diagram_engine.renderer import render_frame
from skills.diagram_engine.style_tokens import STYLE

from .bond_highlight import resolve_bond_indices
from .compound_lookup import NCERT_COMPOUND_SMILES
from .schemas import MolecularDiagramRequest


def _rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))


def _generic_fallback(request: MolecularDiagramRequest) -> bytes:
    """Plain labeled box fallback for unknown compounds, never a network call."""
    blueprint = ContentBlueprint(
        segment_id="molecular-fallback",
        narration_script=request.compound_name,
        narration_duration_estimate_ms=1_000,
        diagram_spec=DiagramSpec(
            layout="flowchart",
            theme=request.theme,
            nodes=[DiagramNode(id="compound", label=request.compound_name[:28] or "Unknown compound", node_type="concept")],
        ),
    )
    return render_frame(blueprint)


def render_molecular_diagram(request: MolecularDiagramRequest) -> bytes:
    smiles = request.smiles or NCERT_COMPOUND_SMILES.get(request.compound_name.lower())
    if not smiles:
        return _generic_fallback(request)
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return _generic_fallback(request)
    tokens = STYLE[request.theme]
    drawer = rdMolDraw2D.MolDraw2DCairo(800, 600)
    options = drawer.drawOptions()
    options.bondLineWidth = 3
    options.setBackgroundColour(_rgb(str(tokens["background"])))
    options.setAtomPalette({6: _rgb(str(tokens["text_color"])), 7: _rgb(str(tokens["text_color"])), 8: _rgb(str(tokens["text_color"]))})
    highlighted = resolve_bond_indices(mol, request.highlight_bonds)
    drawer.DrawMolecule(
        mol,
        highlightAtoms=[],
        highlightBonds=highlighted,
        highlightBondColors={index: _rgb(str(tokens["highlight_glow"])) for index in highlighted},
    )
    drawer.FinishDrawing()
    return drawer.GetDrawingText()
