# SKILL: Science Visual Kits (RDKit + Circuit Symbols + BioIcons)

Three new asset/rendering kits that plug into the existing Diagram Animation Engine (`skills/diagram_engine/`) via the same `layout` + `theme` pattern already established — none of these are a new video-generation path, they're new node/content *types* the existing renderer and Visual Selection Agent can route to.

---

## Kit 1 — Molecular Structure Kit (RDKit)

### Purpose
Render scientifically accurate 2D molecular structure diagrams (Carbon Compounds chapter, ionic structures in Metals/Non-metals) directly from a chemical identifier — never from an LLM's freehand drawing attempt.

### Input contract
```python
class MolecularDiagramRequest(BaseModel):
    compound_name: str            # e.g. "ethanol", "methane"
    smiles: str | None = None     # if known; otherwise resolved from compound_name
    highlight_bonds: list[str] = []   # e.g. ["C-OH"] to highlight the functional group being taught
    theme: Literal["light_textbook", "dark_focus"] = "light_textbook"
```

### Pipeline
1. If `smiles` isn't provided, resolve `compound_name` -> SMILES via a small locked lookup table of NCERT-syllabus compounds (methane, ethane, ethanol, ethanoic acid, etc.) — do not call an external name-resolution API at render time; this table is built once and versioned, so results never drift between sessions.
2. RDKit (`Chem.MolFromSmiles` + `Draw.MolToImage` / `rdMolDraw2D.MolDraw2DCairo`) renders the 2D structure to PNG, using the same `style_tokens.py` color values (bond color, background, font) as the rest of the diagram engine, so it visually matches every other diagram in the lesson.
3. If `highlight_bonds` is set, use RDKit's `highlightBonds` parameter to color that specific bond — this is what lets the teacher say "notice this hydroxyl group" and have it actually glow in the rendered structure.
4. Output PNG is composited into the same Remotion/ffmpeg pipeline as every other diagram frame — no special-cased video path.

### Skill file
```python
# skills/molecular_diagram/rdkit_renderer.py
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from .compound_lookup import NCERT_COMPOUND_SMILES   # locked lookup table, versioned in repo

def render_molecular_diagram(request: MolecularDiagramRequest) -> bytes:
    smiles = request.smiles or NCERT_COMPOUND_SMILES.get(request.compound_name.lower())
    if smiles is None:
        raise ValueError(f"No known SMILES for '{request.compound_name}' — add it to compound_lookup.py")

    mol = Chem.MolFromSmiles(smiles)
    drawer = rdMolDraw2D.MolDraw2DCairo(800, 600)
    drawer.drawOptions().bondLineWidth = 3
    # apply style_tokens background/text colors here via drawOptions().setBackgroundColour etc.
    highlight_bond_idxs = _resolve_bond_indices(mol, request.highlight_bonds)
    drawer.DrawMolecule(mol, highlightBonds=highlight_bond_idxs)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()  # PNG bytes
```

### Directory
```
skills/molecular_diagram/
├── schemas.py              # MolecularDiagramRequest
├── compound_lookup.py      # locked NCERT compound -> SMILES table
├── rdkit_renderer.py       # rendering function above
└── bond_highlight.py       # resolves human-readable bond names -> RDKit bond indices
```

### Routing
Visual Selection Agent tags a segment `visual_type: "molecular_structure"` whenever the lesson content is Carbon Compounds or discusses ionic/molecular bonding — this routes to this kit, never to the generic flowchart engine and never to generative video.

---

## Kit 2 — Circuit Symbol Kit (Electricity chapter)

### Purpose
Render standard, textbook-correct circuit diagrams (battery, resistor, bulb, switch, ammeter, voltmeter, wires) for series/parallel circuits and Ohm's Law demonstrations.

### Sourcing (not drawn from scratch)
Pull the standard IEC 60617 circuit symbol set from Wikimedia Commons — these are public domain / CC-licensed vector symbols already used in textbooks worldwide, so "looks correct to a physics teacher" is guaranteed by using the actual standard, not an approximation.

```
assets/circuit_symbols/
├── battery.svg
├── resistor.svg
├── bulb.svg
├── switch_open.svg
├── switch_closed.svg
├── ammeter.svg
├── voltmeter.svg
└── wire_corner.svg
```

### Input contract
```python
class CircuitComponent(BaseModel):
    id: str
    component_type: Literal["battery", "resistor", "bulb", "switch", "ammeter", "voltmeter"]
    label: str | None = None       # e.g. "R1", "5Ω"
    state: Literal["open", "closed"] | None = None   # for switches

class CircuitConnection(BaseModel):
    source_id: str
    target_id: str

class CircuitDiagramSpec(BaseModel):
    circuit_type: Literal["series", "parallel"]
    components: list[CircuitComponent]
    connections: list[CircuitConnection]
    highlight_current_path: bool = False   # animates a flowing-current effect along wires
```

### Pipeline
1. `circuit_type` determines the layout algorithm: `series` lays components on a single loop path; `parallel` computes branch positions (a small dedicated layout function, not the general Sugiyama layout used for flowcharts, since circuits have their own topological convention — components in a loop, branches drawn as parallel rails).
2. Each component renders as its corresponding SVG from `assets/circuit_symbols/`, positioned along the computed path, with `label` text placed adjacent using the same text-measurement logic from the diagram engine (prevents label overlap here too).
3. If `highlight_current_path` is true, an animated dashed-line/particle-flow effect travels along the wires in Remotion — this is a legitimate, accurate way to show current flow without needing generative video.

### Skill file
```python
# skills/circuit_diagram/layout.py
def layout_series_circuit(spec: CircuitDiagramSpec) -> dict[str, tuple[float, float]]:
    """Places components evenly around a rectangular loop path."""
    ...

def layout_parallel_circuit(spec: CircuitDiagramSpec) -> dict[str, tuple[float, float]]:
    """Places the main loop plus branch rails for parallel components."""
    ...
```

### Directory
```
skills/circuit_diagram/
├── schemas.py
├── layout.py                # series/parallel layout functions above
├── renderer.py               # composites the SVG symbols at computed positions
└── current_flow_animation.py # Remotion timing for the flowing-current effect
assets/circuit_symbols/        # the 8 sourced IEC symbol SVGs
```

### Routing
Visual Selection Agent tags Electricity-chapter segments `visual_type: "circuit_diagram"`. Falls back to the generic `flowchart` layout (plain labeled boxes) automatically if a requested `component_type` isn't in the sourced symbol set yet — never a broken render.

---

## Kit 3 — Biological Illustration Kit (BioIcons)

### Purpose
Provide real, curated, scientifically-styled illustrations (not colored rectangles) for the 7 recurring NCERT biology structures: heart, neuron, flower, cell, eye, nephron, DNA.

### Sourcing
Download once from bioicons.com (CC-licensed scientific illustration sets), store locally — never re-fetch at render time, and never attempt to generate a new biological illustration on the fly (this is the exact hallucination risk flagged earlier).

```
assets/bio_icons/
├── heart_cross_section.svg
├── neuron_structure.svg
├── flower_cross_section.svg
├── plant_cell.svg
├── animal_cell.svg
├── eye_cross_section.svg
├── nephron.svg
└── dna_double_helix.svg
```

### Input contract
```python
class BioIllustrationRequest(BaseModel):
    structure: Literal["heart", "neuron", "flower", "plant_cell", "animal_cell", "eye", "nephron", "dna"]
    callouts: list[DiagramNode] = []   # reuses the existing DiagramNode schema from the diagram engine
    theme: Literal["light_textbook", "dark_focus"] = "light_textbook"
```

### Pipeline
1. Load the fixed base SVG for the requested `structure` from `assets/bio_icons/`.
2. Each entry in `callouts` gets a leader-line + label box positioned automatically — this reuses the exact `cross_section` layout function already built for the generic diagram engine (satellite nodes radiating from a central shape), just pointed at a real illustrated base image instead of a plain colored center node.
3. Style tokens (font, label box color) apply identically to every other diagram in the lesson, keeping visual consistency across subjects.

### Skill file
```python
# skills/bio_illustration/renderer.py
from diagram_engine.layout.cross_section import layout_cross_section
from diagram_engine.style_tokens import STYLE

BIO_ASSET_PATHS = {
    "heart": "assets/bio_icons/heart_cross_section.svg",
    "neuron": "assets/bio_icons/neuron_structure.svg",
    "flower": "assets/bio_icons/flower_cross_section.svg",
    "plant_cell": "assets/bio_icons/plant_cell.svg",
    "animal_cell": "assets/bio_icons/animal_cell.svg",
    "eye": "assets/bio_icons/eye_cross_section.svg",
    "nephron": "assets/bio_icons/nephron.svg",
    "dna": "assets/bio_icons/dna_double_helix.svg",
}

def render_bio_illustration(request: BioIllustrationRequest) -> bytes:
    base_svg_path = BIO_ASSET_PATHS[request.structure]
    positions = layout_cross_section(center_asset=base_svg_path, satellites=request.callouts)
    return compose_svg_with_callouts(base_svg_path, request.callouts, positions, STYLE[request.theme])
```

### Directory
```
skills/bio_illustration/
├── schemas.py
├── renderer.py
└── asset_manifest.py    # BIO_ASSET_PATHS lookup above, versioned with license attribution comment
assets/bio_icons/          # the 8 sourced BioIcons SVGs + a LICENSE_ATTRIBUTION.txt per source's CC terms
```

### Routing
Visual Selection Agent tags biology structural content `visual_type: "bio_illustration"` with a `structure` value from the fixed list above. Any biology concept **outside** this curated 8-item set falls back to the generic `flowchart`/`cross_section` layout with plain labeled boxes — explicitly, rather than attempting to generate a new illustration and risking inaccuracy.

---

## Updated Visual Selection Agent routing table (supersedes the earlier 4-row table)

| `visual_type` tag | Engine | Kit |
|---|---|---|
| `equation` / physics motion (light rays, fields, forces) | Manim | — |
| `molecular_structure` | RDKit | Kit 1 |
| `circuit_diagram` | Circuit layout + IEC symbols | Kit 2 |
| `bio_illustration` (structure in curated list) | BioIcons + cross_section layout | Kit 3 |
| `diagram` / `flowchart` / anything above's fallback | Existing generic diagram engine | — |
| `ambient` (b-roll only, never labeled content) | HF Space (LTX-Video primary, CogVideoX-2B fallback) | — |

## Acceptance tests

1. RDKit: render all NCERT-syllabus compounds in `compound_lookup.py` (methane, ethane, ethanol, ethanoic acid, ethyne — minimum set) without error, and verify `highlight_bonds` correctly colors the specified bond.
2. Circuit: render one series and one parallel circuit with 4 components each, verify zero symbol overlap and correct current-flow animation direction.
3. BioIcons: render all 8 curated structures with at least 2 callouts each, verify callout leader-lines don't cross through the base illustration.
4. Cross-kit consistency: render one segment from each kit in the same session and verify all three use identical `style_tokens` font/background values (regression test against visual drift across subjects).
