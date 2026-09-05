"""
Shikshak AI — Pydantic schemas (request/response).

Mirrors the TypeScript interfaces in 02-TRD.md exactly — every field name
and type is identical after JSON casing conversion (camelCase on the wire,
snake_case in Python via Pydantic's alias generator).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Shared enums ────────────────────────────────────────────────────────────
Level = Literal["beginner", "intermediate", "advanced"]
VisualType = Literal["diagram", "equation", "code", "animation", "none"]
SourceType = Literal["document", "topic"]
SessionStatus = Literal["planning", "in_progress", "completed", "failed"]
SegmentStatus = Literal["pending", "rendering", "ready", "failed"]
QuestionType = Literal["mcq", "short_answer", "conceptual"]

# ── Scene-first architecture enums ───────────────────────────────────────────
ChemistryVisualMode = Literal[
    "reaction_lab",           # two beakers mix → product forms with observation
    "equation_build",         # equation constructed step-by-step on screen
    "experiment_observation", # setup → action → observable change sequence
    "balancing_exercise",     # atom counters confirm conservation
]

PhysicsVisualMode = Literal[
    "circuit_simulation",     # dynamic circuit with current flow & Ohm's law
    "optics_ray_diagram",     # ray tracing with lenses/mirrors & focal points
    "spherical_mirror",       # curvature geometry, focal proof f = R/2, mirror formula
    "motion_mechanics",       # vectors, free-body diagrams, and kinematics graphs
]

BiologyVisualMode = Literal[
    "bio_cellular_process",   # respiration, photosynthesis, ATP energy & organelle flows
    "anatomical_structure",   # anatomical cross-sections & labeled system callouts
]

MathVisualMode = Literal[
    "number_line_geometry",   # real numbers, intervals, square root spiral & coordinate points
    "algebra_step_solve",     # step-by-step mathematical derivations with LaTeX styling
]

MotionGraphicVisualMode = Literal[
    "motion_graphic",         # universal Remotion motion graphics
    "animated_text",          # kinetic typography & definition cards
    "generic_motion",         # universal motion scene
    "step_flow",              # sequential multi-step animated process
    "concept_highlight",      # spotlight on a core scientific/pedagogical law
    "timeline_motion",        # milestone timeline progression
]

# Universal Visual Mode (Union across all STEM, Humanities & Motion domains)
VisualMode = Literal[
    ChemistryVisualMode,
    PhysicsVisualMode,
    BiologyVisualMode,
    MathVisualMode,
    MotionGraphicVisualMode,
    "generic_explainer",      # illustrated fallback — icons + equations + highlights
    "cinematic",              # transcript-grounded cinematic concept animation
    "ai_illustration",        # synthesized pedagogical artwork & Ken Burns animation
    "kinetic_text",           # typographic animated key concepts, definitions & takeaways
    "split_screen",           # dual visual layout: illustration/diagram + structured takeaway card
]

SceneRenderStatus = Literal["pending", "rendering", "ready", "failed"]


def _cam(snake: str) -> str:
    """snake_case → camelCase"""
    head, *tail = snake.split("_")
    return head + "".join(t.title() for t in tail)


class CamelModel(BaseModel):
    """Force camelCase JSON output so the frontend never has to translate."""

    model_config = ConfigDict(
        alias_generator=_cam,
        populate_by_name=True,
        from_attributes=True,
    )


# ── Lesson segment ───────────────────────────────────────────────────────────
class LessonSegment(CamelModel):
    id: str
    order: int
    concept: str
    depth: Level
    visual_type: VisualType
    narration_script: str
    video_url: Optional[str] = None
    has_checkpoint: bool = False
    related_concepts: list[str] = Field(default_factory=list)


class LessonSegmentIn(CamelModel):
    """Internal plan shape (used between agents, not exposed to FE)."""

    order: int
    concept: str
    depth: Level
    visual_type: VisualType
    narration_script: str = ""
    has_checkpoint: bool = False
    related_concepts: list[str] = Field(default_factory=list)


# ── Session ──────────────────────────────────────────────────────────────────
class CreateSessionRequest(CamelModel):
    source_type: SourceType
    document_id: Optional[str] = None
    topic: Optional[str] = None
    level: Level
    language: str = "en"
    time_budget_minutes: int = Field(gt=0)


class Session(CamelModel):
    id: str
    student_id: str
    source_type: SourceType
    document_id: Optional[str] = None
    topic: Optional[str] = None
    level: Level
    language: str
    time_budget_minutes: int
    status: SessionStatus
    segments: list[LessonSegment] = Field(default_factory=list)
    created_at: datetime


class SessionStatusOut(CamelModel):
    status: SessionStatus


# ── Checkpoints ──────────────────────────────────────────────────────────────
# ── Checkpoints & Reteach Ladder ──────────────────────────────────────────
ReteachStrategy = Literal["simplify", "concrete_example", "atomic_steps"]


class ReteachContent(CamelModel):
    strategy: ReteachStrategy
    explanation: str
    new_example: Optional[str] = None
    follow_up_question: str


class QuestionCheckpoint(CamelModel):
    id: str
    segment_id: str
    type: QuestionType
    prompt: str
    options: Optional[list[str]] = None
    student_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    misconception: Optional[str] = None
    attempt_number: int = 1
    reteach_strategy: Optional[ReteachStrategy] = None
    prior_analogies_used: list[str] = Field(default_factory=list)


class SubmitAnswerRequest(CamelModel):
    checkpoint_id: str
    answer: str


class SubmitAnswerResponse(CamelModel):
    is_correct: bool
    misconception: Optional[str] = None
    next_segment_id: Optional[str] = None
    attempt_number: Optional[int] = None
    reteach_strategy: Optional[ReteachStrategy] = None


# ── Concept Mastery ──────────────────────────────────────────────────────────
MasteryTier = Literal["weak", "moderate", "strong"]


class ConceptMasteryOut(CamelModel):
    id: str
    student_id: str
    concept: str
    score: float
    status: MasteryTier
    attempts: int = 0
    consecutive_strong: int = 0
    last_updated: Optional[datetime] = None



# ── Assessment ───────────────────────────────────────────────────────────────
class AssessmentReportOut(CamelModel):
    session_id: str
    score: float
    strong_areas: list[str]
    weak_areas: list[str]
    recommendation: str


# ── Learner profile ──────────────────────────────────────────────────────────
class LearnerProfileOut(CamelModel):
    student_id: str
    topics_studied: list[str]
    weak_concepts: list[str]
    strong_concepts: list[str]
    average_score: float


class PatchLearnerProfileRequest(CamelModel):
    default_level: Optional[Level] = None
    default_language: Optional[str] = None


# ── Learning path ─────────────────────────────────────────────────────────────
class LearningPathItemOut(CamelModel):
    id: str
    item_order: int
    sub_topic: str
    status: Literal["locked", "unlocked", "completed"] = "locked"
    related_session_id: Optional[str] = None


class LearningPathOut(CamelModel):
    id: str
    broad_topic: str
    items: list[LearningPathItemOut]


class CreateLearningPathRequest(CamelModel):
    student_id: str
    broad_topic: str


class ConceptGraphModel(CamelModel):
    concepts: list[str] = Field(default_factory=list)
    edges: list[tuple[str, str]] = Field(default_factory=list)


# ── Corrective RAG (CRAG) ──────────────────────────────────────────────────
CragAction = Literal["proceed", "reformulate_retry", "decline"]


class CragResult(CamelModel):
    action: CragAction
    chunks: list[dict[str, Any]] = Field(default_factory=list)
    not_covered: bool = False



# ── Documents ───────────────────────────────────────────────────────────────
class DocumentOut(CamelModel):
    id: str
    file_name: str
    file_type: Literal["pdf", "docx", "pptx"]
    page_count: Optional[int] = None
    status: Literal["processing", "ready", "failed"]


# ── Language switch ──────────────────────────────────────────────────────────
class LanguageSwitchRequest(CamelModel):
    language: str


# ── Errors ───────────────────────────────────────────────────────────────────
class AgentError(CamelModel):
    error: str
    agent: str
    retryable: bool = False


# ── Scene-first architecture — typed visual payloads ─────────────────────────
# Each visual_mode has exactly one matching payload class.
# The Scene Planning Agent validates LLM output against this schema.
# The renderer dispatch resolves the payload class from the visual_mode string.

class _ChemSpecies(CamelModel):
    """One chemical species (reactant or product) in a reaction scene."""
    name: str = ""
    formula: str
    state: Literal["solid", "liquid", "gas", "aqueous"] = "aqueous"
    color: str = "#38bdf8"         # SVG fill color for the beaker / flask

    @field_validator("name", mode="before")
    @classmethod
    def _coerce_name(cls, v: Any) -> str:
        return str(v) if v else ""

    @field_validator("state", mode="before")
    @classmethod
    def _coerce_state(cls, v: Any) -> str:
        if not v:
            return "aqueous"
        s = str(v).lower().strip()
        if s in ("aq", "aqueous", "solution", "dissolved"):
            return "aqueous"
        if s in ("s", "solid", "precipitate", "powder"):
            return "solid"
        if s in ("l", "liquid"):
            return "liquid"
        if s in ("g", "gas", "vapor", "vapour"):
            return "gas"
        return "aqueous"


class _ObservationStep(CamelModel):
    """One step in an experiment observation sequence."""
    action: str                    # e.g. "heat the copper strip"
    observation: str               # e.g. "turns black"
    visual_cue: str = ""           # e.g. "orange→black gradient"


class ReactionLabPayload(CamelModel):
    """Visual payload for reaction_lab mode.

    Describes a wet-chemistry reaction: two species mix in labelled apparatus,
    an observable change occurs, and the balanced equation is displayed.
    """
    reactants: list[_ChemSpecies]
    products: list[_ChemSpecies]
    conditions: str = ""           # "heat" | "room temperature" | "catalyst: MnO₂"
    observation: str = ""          # "white BaSO₄ precipitate forms"
    balanced_equation: str = ""    # "Na₂SO₄ + BaCl₂ → BaSO₄↓ + 2NaCl"
    atom_counts: dict[str, int] = Field(default_factory=dict)
                                   # {"Na": 2, "S": 1, "O": 4, "Ba": 1, "Cl": 2}


class EquationBuildPayload(CamelModel):
    """Visual payload for equation_build mode.

    The equation is revealed one step at a time, left-to-right.
    Each step string is the full equation text so far (the renderer
    diffs adjacent steps to know which tokens are new).
    """
    steps: list[str]               # ["C₆H₁₂O₆", "C₆H₁₂O₆ + 6O₂", "C₆H₁₂O₆ + 6O₂ →", ...]
    final_equation: str            # "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + energy"
    atom_highlight: list[str] = Field(default_factory=list)
                                   # atom symbols to ring-highlight for conservation


class ExperimentObservationPayload(CamelModel):
    """Visual payload for experiment_observation mode.

    Shows a lab sequence: apparatus setup → each action → visible change.
    """
    setup_description: str         # "A copper strip held in tongs over a Bunsen burner"
    steps: list[_ObservationStep]
    conclusion: str = ""           # "Copper reacts with oxygen to form copper(II) oxide"


class BalancingExercisePayload(CamelModel):
    """Visual payload for balancing_exercise mode.

    Shows atom-count inventories for the unbalanced equation, then
    animates coefficient adjustments until both sides match.
    """
    unbalanced_equation: str       # "Cu + O₂ → CuO"
    balanced_equation: str         # "2Cu + O₂ → 2CuO"
    # atom_inventory: maps each element to [left_count, right_count] per step
    atom_inventory: dict[str, list[int]] = Field(default_factory=dict)
                                   # {"Cu": [1, 1], "O": [2, 1]} (unbalanced)
    show_scale: bool = False       # Physical balance scale metaphor: default FALSE per pedagogical policy
    comparison_mode: str = "atom_inventory"  # "atom_inventory" | "molecular_structure"

    @field_validator("atom_inventory", mode="before")
    @classmethod
    def _coerce_inventory(cls, v: Any) -> dict[str, list[int]]:
        if not isinstance(v, dict):
            return {}
        cleaned: dict[str, list[int]] = {}
        for elem, val in v.items():
            elem_str = str(elem).strip()
            if elem_str.lower() in ("atoms", "status", "conservation", "note", "state"):
                continue
            if isinstance(val, (int, float)):
                cleaned[elem_str] = [int(val), int(val)]
            elif isinstance(val, list):
                num_list = []
                for x in val:
                    try:
                        num_list.append(int(x))
                    except (ValueError, TypeError):
                        num_list.append(1)
                while len(num_list) < 2:
                    num_list.append(num_list[0] if num_list else 1)
                cleaned[elem_str] = num_list[:2]
            elif isinstance(val, str):
                import re
                nums = [int(n) for n in re.findall(r"\d+", val)]
                if nums:
                    cleaned[elem_str] = [nums[0], nums[1] if len(nums) > 1 else nums[0]]
                else:
                    cleaned[elem_str] = [1, 1]
        return cleaned



class GenericExplainerPayload(CamelModel):
    """Visual payload for generic_explainer — the meaningful fallback.

    A well-composed illustrated explainer with icons, equations, and
    progressive highlights. NOT generic cards — every field should be
    concept-specific (quality gate rejects 'Mechanism' / 'Applications').
    """
    title: str                     # specific, not generic: "Atom Conservation in Reactions"
    key_points: list[str]          # 2-4 concept-specific points, no filler
    icons: list[str] = Field(default_factory=list)   # emoji or icon names
    equation: str = ""             # primary equation for the scene
    source_figure_ref: str = ""    # PDF figure reference if from source material


# ── Physics Pack Payloads ───────────────────────────────────────────────────

class CircuitComponent(CamelModel):
    id: str
    type: str                      # "battery" | "resistor" | "bulb" | "switch" | "ammeter" | "voltmeter"
    label: str = ""                # "12V Battery", "Resistor R1 (10Ω)"
    value: float = 0.0
    unit: str = ""                 # "V", "Ω", "A"
    state: str = "closed"          # "open" | "closed"


class CircuitSimulationPayload(CamelModel):
    """Visual payload for circuit_simulation mode (Electricity)."""
    circuit_type: str = "series"   # "series" | "parallel" | "ohms_law"
    voltage: float = 12.0
    resistance: float = 6.0
    current: float = 2.0           # I = V / R
    components: list[CircuitComponent] = Field(default_factory=list)
    formula: str = "V = I × R"
    observation: str = "Current flows clockwise through the closed loop"


class OpticsRayDiagramPayload(CamelModel):
    """Visual payload for optics_ray_diagram mode (Light & Optics)."""
    optical_element: str = "convex_lens"  # "convex_lens" | "concave_lens" | "concave_mirror" | "convex_mirror" | "prism"
    focal_length: float = 10.0
    object_distance: float = 20.0
    object_height: float = 5.0
    image_distance: float = 20.0
    image_height: float = -5.0
    image_nature: str = "Real, Inverted, Same Size"
    formula: str = "1/f = 1/v - 1/u"
    key_observation: str = "Rays parallel to principal axis pass through principal focus F"


class SphericalMirrorPayload(CamelModel):
    """Visual payload for spherical_mirror mode (Curvature & Mirror Formula)."""
    title: str = "Spherical Mirror Geometry & Formula"
    formula: str = "1/v + 1/u = 1/f"
    radius: str = "20 cm"
    focal_length: str = "10 cm"
    mirror_type: str = "concave"


class MotionMechanicsPayload(CamelModel):
    """Visual payload for motion_mechanics mode (Physics Forces & Motion)."""
    scenario: str = "kinematics"   # "kinematics" | "free_body" | "projectile"
    title: str = "Uniform Acceleration"
    equations: list[str] = Field(default_factory=lambda: ["v = u + at", "s = ut + ½at²"])
    vectors: list[dict[str, Any]] = Field(default_factory=list)
    takeaway: str = "Acceleration represents rate of change of velocity."


# ── Biology Pack Payloads ────────────────────────────────────────────────────

class BioCellularProcessPayload(CamelModel):
    """Visual payload for bio_cellular_process mode (Respiration, Photosynthesis, Cells)."""
    process_name: str = "Cellular Respiration"  # "Cellular Respiration" | "Photosynthesis" | "Fermentation"
    organelle: str = "Mitochondria"
    inputs: list[str] = Field(default_factory=lambda: ["Glucose (C₆H₁₂O₆)", "Oxygen (6O₂)"])
    outputs: list[str] = Field(default_factory=lambda: ["Carbon Dioxide (6CO₂)", "Water (6H₂O)", "38 ATP Energy"])
    energy_yield: str = "38 ATP Molecules"
    overall_equation: str = "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy (ATP)"
    key_takeaway: str = "Exothermic breakdown of glucose releasing energy in cellular mitochondria."


class AnatomicalStructurePayload(CamelModel):
    """Visual payload for anatomical_structure mode (Heart, Nephron, Neuron, Leaf)."""
    structure_name: str = "Human Heart Circulation"
    callouts: list[dict[str, str]] = Field(default_factory=list)  # [{"label": "Left Ventricle", "function": "Pumps oxygenated blood"}]
    functional_flow: list[str] = Field(default_factory=list)
    takeaway: str = "Double circulation ensures oxygenated and deoxygenated blood remain separated."


# ── Mathematics Pack Payloads ───────────────────────────────────────────────

class NumberLineGeometryPayload(CamelModel):
    """Visual payload for number_line_geometry mode (Real Numbers & Coordinate Geometry)."""
    title: str = "Representation of Real Numbers on Number Line"
    marked_points: list[dict[str, Any]] = Field(default_factory=lambda: [{"label": "√2", "value": 1.414, "color": "#38bdf8"}])
    intervals: list[dict[str, Any]] = Field(default_factory=list)
    theorem: str = "Every real number corresponds to a unique point on the number line."
    construction_step: str = "Construct right triangle with base=1 and height=1; hypotenuse is √2."


class AlgebraStepSolvePayload(CamelModel):
    """Visual payload for algebra_step_solve mode (Equations, Proofs, Polynomials)."""
    title: str = "Step-by-Step Algebraic Solution"
    initial_expression: str = "ax² + bx + c = 0"
    steps: list[str] = Field(default_factory=list)
    final_solution: str = "x = (-b ± √(b² - 4ac)) / (2a)"
    rule_used: str = "Quadratic Formula / Completing the Square"


class MotionGraphicElement(CamelModel):
    id: str = ""
    type: Literal["text", "arrow", "badge", "icon", "highlight", "card", "metric"] = "text"
    content: str = ""
    subtitle: str = ""
    icon: str = ""
    color: str = ""


class MotionGraphicPayload(CamelModel):
    """Visual payload for multi-subject motion graphics scenes.

    Strictly semantic: defines structure, step items, and visual cues.
    Preserves Coordinate Invariant: NO raw x, y, width, height, or arbitrary code.
    """
    template: Literal[
        "step_by_step_flow",
        "animated_title",
        "concept_highlight",
        "text_reveal",
        "comparison",
        "timeline",
        "diagram_build",
    ] = "step_by_step_flow"
    title: str = "Lesson Scene"
    subtitle: str = ""
    steps: list[str] = Field(default_factory=list)
    elements: list[MotionGraphicElement] = Field(default_factory=list)
    key_takeaway: str = ""
    accent_color: str = "#38bdf8"
    badge: str = "LESSON SCENE"


# ── Generative Visual Payloads ─────────────────────────────────────────────

class AiIllustrationPayload(CamelModel):
    """Visual payload for ai_illustration mode — synthesized pedagogical artwork."""
    prompt: str = ""
    style: str = "educational_illustration"
    title: str = ""
    caption: str = ""
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    entities: list[str] = Field(default_factory=list)
    key_takeaway: str = ""


class KineticTextPayload(CamelModel):
    """Visual payload for kinetic_text mode — dynamic typography & key concepts."""
    title: str = "Core Concept"
    subtitle: str = ""
    key_takeaways: list[str] = Field(default_factory=list)
    badge: str = "KEY PRINCIPLE"
    equation: str = ""
    highlight_word: str = ""


class SplitScreenPayload(CamelModel):
    """Visual payload for split_screen mode — side-by-side illustration + key takeaways."""
    left_title: str = ""
    left_type: str = "image"
    left_image_prompt: str = ""
    left_image_url: Optional[str] = None
    left_image_path: Optional[str] = None
    right_title: str = "Key Principles"
    right_points: list[str] = Field(default_factory=list)
    formula: str = ""
    key_takeaway: str = ""


# Union of all payload models — used by the renderer dispatch
VisualPayload = (
    ReactionLabPayload
    | EquationBuildPayload
    | ExperimentObservationPayload
    | BalancingExercisePayload
    | CircuitSimulationPayload
    | OpticsRayDiagramPayload
    | SphericalMirrorPayload
    | MotionMechanicsPayload
    | BioCellularProcessPayload
    | AnatomicalStructurePayload
    | NumberLineGeometryPayload
    | AlgebraStepSolvePayload
    | MotionGraphicPayload
    | GenericExplainerPayload
    | AiIllustrationPayload
    | KineticTextPayload
    | SplitScreenPayload
)

# Map from visual_mode string → payload Pydantic class (single source of truth)
VISUAL_MODE_PAYLOAD_MAP: dict[str, type] = {
    # Chemistry Pack
    "reaction_lab":           ReactionLabPayload,
    "equation_build":         EquationBuildPayload,
    "experiment_observation":  ExperimentObservationPayload,
    "balancing_exercise":     BalancingExercisePayload,
    # Physics Pack
    "circuit_simulation":     CircuitSimulationPayload,
    "optics_ray_diagram":     OpticsRayDiagramPayload,
    "spherical_mirror":       SphericalMirrorPayload,
    "motion_mechanics":       MotionMechanicsPayload,
    # Biology Pack
    "bio_cellular_process":   BioCellularProcessPayload,
    "anatomical_structure":   AnatomicalStructurePayload,
    # Mathematics Pack
    "number_line_geometry":   NumberLineGeometryPayload,
    "algebra_step_solve":     AlgebraStepSolvePayload,
    # Multi-Subject Motion Pack
    "motion_graphic":         MotionGraphicPayload,
    "animated_text":          MotionGraphicPayload,
    "generic_motion":         MotionGraphicPayload,
    "step_flow":              MotionGraphicPayload,
    "concept_highlight":      MotionGraphicPayload,
    "timeline_motion":        MotionGraphicPayload,
    # Generative AI & Typographic Pack
    "ai_illustration":        AiIllustrationPayload,
    "kinetic_text":           KineticTextPayload,
    "split_screen":           SplitScreenPayload,
    # Fallback & Cinematic
    "generic_explainer":      GenericExplainerPayload,
    "cinematic":              GenericExplainerPayload,
}


def validate_visual_payload(visual_mode: str, raw: dict) -> "VisualPayload":
    """Parse and validate a visual_payload dict against the correct schema.

    Raises ValueError if visual_mode is unknown or payload fails validation.
    This is the sole entry point used by the Scene Planning Agent and renderer
    dispatch — never validate raw payloads manually elsewhere.
    """
    cls = VISUAL_MODE_PAYLOAD_MAP.get(visual_mode)
    if cls is None:
        raise ValueError(
            f"Unknown visual_mode {visual_mode!r}. "
            f"Valid modes: {list(VISUAL_MODE_PAYLOAD_MAP)}"
        )
    try:
        return cls.model_validate(raw)
    except Exception as exc:
        raise ValueError(
            f"visual_payload for mode {visual_mode!r} failed validation: {exc}"
        ) from exc


# ── Scene (scene-first render unit) ──────────────────────────────────────────

class SceneIn(CamelModel):
    """Internal scene contract produced by the Scene Planning Agent.

    Not exposed to the frontend — used between agents and the DB layer.
    """
    scene_order: int
    learning_objective: str
    narration_text: str
    visual_mode: VisualMode
    visual_payload: dict = Field(default_factory=dict)   # validated via validate_visual_payload
    on_screen_equation: str = ""
    on_screen_labels: list[str] = Field(default_factory=list)
    key_takeaway: str = ""
    interaction_cue: Optional[dict] = None

    # Transcript-timed scene contract fields
    narration_span: str = ""
    duration_seconds: float = 6.0
    visual_objective: str = ""
    entities: list[str] = Field(default_factory=list)
    forbidden_terms: list[str] = Field(default_factory=list)
    motion_beats: list[dict[str, Any]] = Field(default_factory=list)
    asset_strategy: str = "auto"


class SceneOut(CamelModel):
    """Scene as returned to the frontend via GET /sessions/{id}/segments/{id}/scenes."""
    id: str
    segment_id: str
    scene_order: int
    learning_objective: str
    narration_text: str
    visual_mode: str
    visual_payload: dict
    on_screen_equation: str = ""
    key_takeaway: str = ""
    start_time_ms: Optional[int] = None
    end_time_ms: Optional[int] = None
    duration_seconds: Optional[float] = None
    narration_span: Optional[str] = None
    entities: list[str] = Field(default_factory=list)
    render_status: SceneRenderStatus = "pending"
    rendered_clip_url: Optional[str] = None


# ── Semantic Animation IR (Motion Canvas) ──────────────────────────────────
from models.animation_spec import (
    AnimationSceneSpec,
    SemanticObject,
    SemanticBeat,
    SemanticCameraKeyframe,
    NarrativeMarker,
    FORBIDDEN_COORDINATE_KEYS,
)

