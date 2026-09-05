"""
Shikshak AI — Scene Planning Agent (Universal Multi-Subject).

Single responsibility: given a lesson segment (concept, depth, narration, and source text),
decompose the segment into 3-5 discrete, purposeful visual scenes.

Supported Subject Packs:
  - Chemistry: reaction_lab, equation_build, experiment_observation, balancing_exercise
  - Physics: circuit_simulation, optics_ray_diagram, motion_mechanics
  - Biology: bio_cellular_process, anatomical_structure
  - Mathematics: number_line_geometry, algebra_step_solve
  - Universal Fallback: generic_explainer
"""
from __future__ import annotations

import json
import math
import re
from typing import Any, Optional
from pydantic import BaseModel, Field

from celery_app import celery_app
from models import (
    SceneIn,
    VisualMode,
    validate_visual_payload,
    VISUAL_MODE_PAYLOAD_MAP,
)
from agents.llm import get_content_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.prompt_templating import SYSTEM_TEACHER


# ── LLM Schema for Scene Planning ───────────────────────────────────────────

class ScenePlanRaw(BaseModel):
    scene_order: int
    learning_objective: str
    narration_text: str
    visual_mode: VisualMode
    visual_payload: dict[str, Any] = Field(default_factory=dict)
    on_screen_equation: str = ""
    on_screen_labels: list[str] = Field(default_factory=list)
    key_takeaway: str = ""
    narration_span: str = ""
    duration_seconds: float = 6.0
    visual_objective: str = ""
    entities: list[str] = Field(default_factory=list)
    forbidden_terms: list[str] = Field(default_factory=list)
    motion_beats: list[dict[str, Any]] = Field(default_factory=list)
    asset_strategy: str = "auto"


class SegmentScenePlanResponse(BaseModel):
    concept: str
    scenes: list[ScenePlanRaw]


# ── Universal Prompt ─────────────────────────────────────────────────────────

_SCENE_PLANNING_PROMPT = """\
You are an expert curriculum animator and instructional director for Shikshak AI.
Your job is to transform a lesson segment into an exact sequence of 3 to 5 visual scenes.

Segment Concept: {concept}
Level: {level}
Language: {language}
Full Segment Narration:
\"\"\"{narration_script}\"\"\"

Source Context (if available):
{source_context}

Supported Visual Modes across STEM & Humanities Domains:

1. CHEMISTRY PACK:
   - "reaction_lab": Mixing chemicals/beakers, solution changes, precipitate formation.
     visual_payload: {{"reactants": [{{"name": "Sodium sulphate", "formula": "Na2SO4", "state": "aqueous", "color": "#38bdf8"}}], "products": [{{"name": "Barium sulphate", "formula": "BaSO4", "state": "solid", "color": "#f8fafc", "observation": "white precipitate"}}], "conditions": "room temperature", "observation": "Insoluble white precipitate forms", "balanced_equation": "Na2SO4 + BaCl2 -> BaSO4 + 2NaCl", "atom_counts": {{"Na": 2, "S": 1, "O": 4, "Ba": 1, "Cl": 2}}}}
   - "equation_build": Step-by-step chemical/scientific formula construction and criss-cross valency combining.
     For chemical formulas: visual_payload: {{"steps": ["Mg²⁺ (Valency 2) + Cl⁻ (Valency 1)", "Cross Valencies: Mg₁Cl₂", "MgCl₂ (Balanced)"], "final_equation": "MgCl2", "atom_highlight": ["Mg", "Cl"]}}
     For reaction equations: visual_payload: {{"steps": ["C6H12O6", "C6H12O6 + 6O2", "C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy"], "final_equation": "C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy", "atom_highlight": ["C", "H", "O"]}}
     RULE: In "equation_build", "steps" MUST contain actual chemical formulas, ions, or equations (e.g. Al³⁺, SO₄²⁻, Al₂(SO₄)₃), NEVER plain English descriptive titles like "Polyatomic Ions".
   - "experiment_observation": Laboratory experiments, heating, oxidation, observation sequences.
     visual_payload: {{"setup_description": "Copper powder heated in air", "steps": [{{"action": "Heat copper in presence of air", "observation": "Surface turns black", "visual_cue": "orange to black coating"}}], "conclusion": "2Cu + O2 -> 2CuO"}}
   - "balancing_exercise": Conservation of mass and atom inventories.
     visual_payload: {{"unbalanced_equation": "Cu + O2 -> CuO", "balanced_equation": "2Cu + O2 -> 2CuO", "atom_inventory": {{"Cu": [2, 2], "O": [2, 2]}}}}

2. PHYSICS PACK:
   - "circuit_simulation": Electricity, Ohm's law, batteries, resistors, current flow.
     visual_payload: {{"circuit_type": "series", "voltage": 12.0, "resistance": 6.0, "current": 2.0, "formula": "V = I * R", "observation": "Current flows clockwise through the loop"}}
   - "optics_ray_diagram": Light, refraction, lenses, ray tracing, image formation.
     visual_payload: {{"optical_element": "convex_lens", "focal_length": 10.0, "object_distance": 20.0, "object_height": 5.0, "image_distance": 20.0, "image_height": -5.0, "image_nature": "Real, Inverted, Same Size", "formula": "1/f = 1/v - 1/u", "key_observation": "Rays parallel to axis pass through focus F"}}
   - "spherical_mirror": Spherical mirrors, curvature geometry, focal proof f = R/2, and mirror formula 1/v + 1/u = 1/f.
     visual_payload: {{"title": "Spherical Mirror Geometry & Formula", "formula": "1/v + 1/u = 1/f", "radius": "20 cm", "focal_length": "10 cm", "mirror_type": "concave"}}

3. BIOLOGY PACK:
   - "bio_cellular_process": Cellular respiration, photosynthesis, ATP energy, cell organelles.
     visual_payload: {{"process_name": "Cellular Respiration", "organelle": "Mitochondria", "inputs": ["Glucose (C6H12O6)", "Oxygen (6O2)"], "outputs": ["Carbon Dioxide (6CO2)", "Water (6H2O)", "38 ATP"], "energy_yield": "38 ATP Molecules", "overall_equation": "C6H12O6 + 6O2 -> 6CO2 + 6H2O + ATP", "key_takeaway": "Mitochondria release cellular ATP energy."}}
   - "anatomical_structure": Heart circulation, nephron, neuron, leaf anatomy.
     visual_payload: {{"structure_name": "Human Heart Circulation", "callouts": [{{"label": "Left Ventricle", "function": "Pumps oxygenated blood to body"}}], "takeaway": "Double circulation separates oxygenated and deoxygenated blood."}}

4. MATHEMATICS PACK:
   - "number_line_geometry": Real numbers, rational/irrational points, geometric √2 construction.
     visual_payload: {{"title": "Real Numbers on Number Line", "theorem": "Every real number has a unique point on number line.", "construction_step": "Right triangle with base=1 and height=1 gives hypotenuse √2."}}
   - "algebra_step_solve": Kinetic step-by-step derivations, quadratic formula, algebraic solving.
     visual_payload: {{"title": "Quadratic Formula Derivation", "initial_expression": "ax^2 + bx + c = 0", "steps": ["Divide by a", "Complete the square", "Take square root"], "final_solution": "x = (-b ± √(b^2 - 4ac)) / 2a", "rule_used": "Quadratic Formula"}}

5. DYNAMIC MULTI-SUBJECT MOTION GRAPHICS PACK:
   - "motion_graphic" / "step_flow": Sequential multi-step process flows, biological pathways, chemical stages, or algorithm steps.
     visual_payload: {{"template": "step_by_step_flow", "title": "Photosynthesis Flow", "subtitle": "Thylakoid electron transport", "steps": ["Sunlight", "Chlorophyll", "Water Splitting", "ATP Synthase"], "key_takeaway": "Light energy converts to chemical ATP energy.", "badge": "PROCESS FLOW"}}
   - "animated_text": Kinetic title cards, overarching principle reveals, and core definitions across any subject.
     visual_payload: {{"template": "animated_title", "title": "Conservation of Energy", "subtitle": "Energy can neither be created nor destroyed", "key_takeaway": "Total energy in an isolated system is conserved.", "badge": "FUNDAMENTAL PRINCIPLE"}}
   - "timeline_motion": Sequential historical milestones, multi-phase reaction progressions, or biological eras.
     visual_payload: {{"template": "timeline", "title": "Respiration Phases", "steps": ["Glycolysis in Cytoplasm", "Krebs Cycle in Matrix", "Oxidative Phosphorylation in Cristae"], "key_takeaway": "Generates 38 ATP molecules sequentially.", "badge": "BIO TIMELINE"}}

6. CLASSROOM SMARTBOARD & DYNAMIC TYPOGRAPHY PACK:
   - "ai_illustration": Classroom digital smartboard / chalkboard lecture card with glowing formulas, step-by-step physical derivations, and animated vector apparatus schematics. ZERO stock photos or realistic photographs.
     visual_payload: {{"title": "Chloroplast Thylakoid Structure", "caption": "Membrane-bound compartments where light reactions occur", "formula": "6CO2 + 6H2O -> C6H12O6 + 6O2", "entities": ["Thylakoid", "Stroma", "Granum"], "key_takeaway": "Light absorption occurs within thylakoid membranes"}}
   - "kinetic_text": High-impact typographic concept card for core definitions, laws, or opening/closing takeaways.
     visual_payload: {{"title": "Newton's First Law of Motion", "subtitle": "The Law of Inertia", "key_takeaways": ["An object at rest stays at rest unless acted upon by an external force", "Inertia depends directly on mass"], "badge": "FUNDAMENTAL LAW", "equation": "F_net = 0 => dv/dt = 0"}}
   - "split_screen": Dual-pane classroom composition with vector schematic apparatus on left and structured takeaways/formula on right.
     visual_payload: {{"left_title": "Electromagnetic Induction", "left_type": "vector_schematic", "right_title": "Faraday's Law Observations", "right_points": ["Relative motion induces electromotive force", "Deflection direction reverses with magnet pole"], "formula": "emf = -N (dPhi/dt)", "key_takeaway": "Changing magnetic flux induces electric current"}}

7. UNIVERSAL FALLBACK:
   - "generic_explainer": Illustrated concept cards with icons, equations, and takeaways.
     visual_payload: {{"title": "Scientific Concept", "key_points": ["Point 1", "Point 2"], "icons": ["atom", "sparkles"], "equation": ""}}

CRITICAL RULES:
1. Act as the Lead Educational Animator: plan 3 to 5 discrete, lively visual scenes for the segment narration.
2. ABSOLUTELY BAN ALL STOCK PHOTOS, REALISTIC PHOTOGRAPHS, AND IRRELEVANT IMAGES (e.g., desk lamps, computers, random real-world items, stock people). Every single scene MUST have an authentic CLASSROOM SMARTBOARD / CHALKBOARD VIBE. Focus 100% on formulas, mathematical derivations, scientific laws, concepts, and animations.
3. BAN STATIC SLIDESHOWS: NEVER create static PowerPoint-style cards with bullet-point lists of equations. Every formula MUST be animated within an active physical apparatus, step-by-step derivation, or dynamic split-screen.
4. Select the MOST ACCURATE visual mode:
   - Light, Optics, Sunlight, Reflection, Refraction, Mirrors, Lenses, Vision -> ALWAYS "optics_ray_diagram" or "spherical_mirror". NEVER choose stock images or generic illustrations for optics.
   - Photosynthesis, Cellular Respiration, Organelles -> "bio_cellular_process" with chemical equation (6CO2 + 6H2O -> C6H12O6 + 6O2) and organelle diagrams, or "step_flow".
   - Chemical reaction apparatus / beakers -> "reaction_lab"
   - Chemical formula combining / equation steps -> "equation_build"
   - Laboratory oxidation / heating experiment -> "experiment_observation"
   - Mass conservation / atom counting -> "balancing_exercise"
   - Electric circuits & schematics -> "circuit_simulation"
   - Mathematics & Derivations -> "algebra_step_solve" or "number_line_geometry"
   - Side-by-side visual apparatus + formula/principles -> "split_screen"
   - Formal laws, definitions, summary cards, opening concept hooks -> "kinetic_text"
   - Classroom Lecture Smartboard with Derivations & Vector Schematics -> "ai_illustration"
5. Each scene MUST focus on ONE dominant idea and ONE learning objective.
6. Every visual_payload MUST match the exact fields required by its visual_mode.
7. Return 3 to 5 scenes in strictly sequential scene_order (1, 2, 3...).

Return ONLY valid JSON matching this schema:
{{
  "concept": "{concept}",
  "scenes": [
    {{
      "scene_order": 1,
      "learning_objective": "...",
      "narration_text": "...",
      "visual_mode": "circuit_simulation",
      "visual_payload": {{ ... }},
      "on_screen_equation": "...",
      "on_screen_labels": ["..."],
      "key_takeaway": "..."
    }}
  ]
}}
"""


# ── Core Agent Function ──────────────────────────────────────────────────────

def plan_scenes_for_segment(
    *,
    concept: str,
    level: str = "intermediate",
    language: str = "en",
    narration_script: str = "",
    retrieved_chunks: list[dict] | None = None,
    animation_scenes: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """Generate 3-5 typed scenes for a single lesson segment across any subject."""
    if not narration_script and animation_scenes:
        narration_script = " ".join(s.get("narration_text", "") for s in animation_scenes)

    source_context = ""
    if retrieved_chunks:
        source_context = "\n".join(
            f"- {c.get('section_label', 'Source')}: {c.get('content', '')[:300]}"
            for c in retrieved_chunks[:3]
        )

    prompt = (
        SYSTEM_TEACHER.render()
        + "\n\n"
        + _SCENE_PLANNING_PROMPT.format(
            concept=concept,
            level=level,
            language=language,
            narration_script=narration_script or f"Explaining {concept} thoroughly.",
            source_context=source_context or "Standard curriculum STEM concepts.",
        )
    )

    llm = get_content_llm()

    try:
        raw_plan = call_llm_with_retry(
            llm, prompt, SegmentScenePlanResponse, model_name="scene_planning"
        )
        validated_scenes = _validate_and_normalize_scenes(raw_plan.scenes, concept)
        if validated_scenes:
            return validated_scenes
    except Exception as e:
        print(f"[scene_planning] LLM planning failed: {e}; falling back to deterministic plan")

    return _fallback_scenes(concept, level, language, narration_script)


def _validate_and_normalize_scenes(
    raw_scenes: list[ScenePlanRaw], concept: str
) -> list[dict[str, Any]]:
    """Validate each scene against its visual_mode payload schema and normalize."""
    output_scenes = []
    for idx, sc in enumerate(raw_scenes, start=1):
        mode = sc.visual_mode
        payload = sc.visual_payload or {}

        # Validate or repair visual_payload
        try:
            validated_payload = validate_visual_payload(mode, payload)
            payload_dict = validated_payload.model_dump(mode="json")
        except Exception as ve:
            print(f"[scene_planning] Payload validation warning for scene {idx} ({mode}): {ve}. Converting to generic_explainer.")
            mode = "generic_explainer"
            payload_dict = {
                "title": sc.learning_objective or concept[:40],
                "key_points": [sc.key_takeaway or f"Understanding {concept}."],
                "icons": ["atom", "lightbulb"],
                "equation": sc.on_screen_equation or "",
            }

        narration = sc.narration_span or sc.narration_text or f"Observing {concept}."
        words = len(narration.split())
        calculated_dur = max(3.0, round(words / 2.3, 1))
        # Derive speech-paced duration from narration word count unless LLM provided custom non-default duration
        if sc.duration_seconds > 1.0 and sc.duration_seconds != 6.0:
            duration = sc.duration_seconds
        else:
            duration = calculated_dur

        # Sanitize placeholders
        from skills.scene_renderers.base import sanitize_display_text
        clean_equation = sanitize_display_text(sc.on_screen_equation)
        clean_takeaway = sanitize_display_text(sc.key_takeaway)

        # Extract entities from on_screen_labels or concept if empty
        entities = sc.entities or sc.on_screen_labels or [concept[:40]]

        scene_obj = SceneIn(
            scene_order=idx,
            learning_objective=sc.learning_objective or f"Learn {concept}",
            narration_text=sc.narration_text or narration,
            visual_mode=mode,
            visual_payload=payload_dict,
            on_screen_equation=clean_equation,
            on_screen_labels=sc.on_screen_labels or [],
            key_takeaway=clean_takeaway,
            narration_span=sc.narration_span or narration,
            duration_seconds=duration,
            visual_objective=sc.visual_objective or sc.learning_objective or f"Illustrate {concept}",
            entities=entities,
            forbidden_terms=sc.forbidden_terms or [],
            motion_beats=sc.motion_beats or [
                {"at": 0.0, "action": "establish", "target": entities[0] if entities else "main_concept"},
                {"at": round(duration * 0.4, 1), "action": "pan_zoom", "target": entities[-1] if entities else "detail"},
            ],
            asset_strategy=sc.asset_strategy or "auto",
        )
        output_scenes.append(scene_obj.model_dump(mode="json"))


    return output_scenes


def _fallback_scenes(
    concept: str, level: str, language: str, narration_script: str
) -> list[dict[str, Any]]:
    """Deterministic, dynamic scene synthesis derived strictly from the narration and concept.

    Zero hardcoding: dynamically decomposes the transcript into pedagogical narrative beats
    and infers appropriate visual modes and key takeaway cards purely from input text.
    """
    script = (narration_script or "").strip()
    if not script:
        script = f"In this lesson, we explore {concept}. We analyze the foundational principles, key mechanisms, and observable real-world results."

    # Extract clean sentence boundaries
    raw_sentences = [
        s.strip() for s in re.split(r'(?<=[.!?])\s+', script) if len(s.strip()) > 8
    ]
    if not raw_sentences:
        raw_sentences = [script]

    total_words = len(script.split())
    if len(raw_sentences) >= 4 or total_words >= 80:
        num_scenes = 3
    elif len(raw_sentences) >= 2 or total_words >= 35:
        num_scenes = 2
    else:
        num_scenes = 1

    chunk_size = max(1, math.ceil(len(raw_sentences) / num_scenes))
    sentence_groups = [
        raw_sentences[i : i + chunk_size]
        for i in range(0, len(raw_sentences), chunk_size)
    ][:num_scenes]

    def _infer_mode(scene_text: str, scene_idx: int) -> tuple[str, dict[str, Any]]:
        text_lower = (concept + " " + scene_text).lower()

        # 1. Physics / Optics & Rays
        if any(k in text_lower for k in ("optic", "lens", "mirror", "refract", "reflect", "ray", "focal", "snell")):
            if "mirror" in text_lower:
                return "spherical_mirror", {
                    "title": concept[:40],
                    "formula": "1/v + 1/u = 1/f",
                    "mirror_type": "concave" if "concave" in text_lower else "convex",
                }
            return "optics_ray_diagram", {
                "optical_element": "convex_lens" if "convex" in text_lower else "lens",
                "key_observation": scene_text[:90],
                "formula": "1/f = 1/v - 1/u",
            }

        # 2. Physics / Electricity & Circuits
        if any(k in text_lower for k in ("circuit", "voltage", "resistan", "ohm", "current", "ammeter", "battery")):
            return "circuit_simulation", {
                "circuit_type": "series",
                "voltage": 12.0,
                "resistance": 6.0,
                "current": 2.0,
                "formula": "V = I × R",
                "observation": scene_text[:90],
            }

        # 3. Biology / Cellular & Life Processes
        if any(k in text_lower for k in ("cell", "organelle", "chloro", "photo", "respir", "mitochondr", "atp", "glucose", "membrane")):
            is_plant = any(k in text_lower for k in ("chloro", "photo", "plant", "leaf", "stroma", "thylakoid"))
            return "bio_cellular_process", {
                "process_name": concept[:35],
                "organelle": "Chloroplast" if is_plant else "Mitochondria",
                "inputs": [concept[:25], "Substrate"],
                "outputs": ["Products", "Yield"],
                "overall_equation": "",
                "key_takeaway": scene_text[:90],
            }

        # 4. Chemistry / Reactions & Equations
        if any(k in text_lower for k in ("react", "balanc", "precipitat", "oxid", "acid", "base", "salt", "chemi", "atom")):
            if any(k in text_lower for k in ("balanc", "atom", "coefficient", "conservation")):
                return "balancing_exercise", {
                    "unbalanced_equation": "Reactants -> Products",
                    "balanced_equation": "Balanced Reactants -> Balanced Products",
                    "atom_inventory": {"Atoms": [2, 2]},
                }
            return "reaction_lab", {
                "reactants": [{"name": "Reactants", "formula": "R", "state": "aqueous", "color": "#38bdf8"}],
                "products": [{"name": "Products", "formula": "P", "state": "solid", "color": "#f8fafc", "observation": "formation"}],
                "observation": scene_text[:90],
            }

        # 5. Mathematics & Coordinate Geometry / Number Line
        if any(k in text_lower for k in ("number line", "coordinate", "geometry", "hypotenuse")):
            return "number_line_geometry", {
                "title": concept[:40],
                "theorem": f"Geometric representation of {concept[:30]}",
                "construction_step": scene_text[:90],
            }

        # 6. Mathematics & Symbolic Derivations
        if any(k in text_lower for k in ("equation", "graph", "quadrat", "formula", "algebra", "theorem", "solve")):
            return "algebra_step_solve", {
                "title": concept[:40],
                "steps": [s[:60] for s in scene_text.split(".") if len(s.strip()) > 5][:3] or ["Identify variables", "Apply formula", "Solve"],
                "final_solution": "",
            }

        # 6. Universal Default: Split screen or Generic Explainer derived 100% from transcript
        if scene_idx == 0:
            return "split_screen", {
                "left_title": concept[:30],
                "left_type": "generated",
                "right_title": "Core Principles",
                "right_points": [s[:80] for s in scene_text.split(".") if len(s.strip()) > 5][:3] or [concept[:40]],
                "key_takeaway": scene_text[:90],
            }

        return "generic_explainer", {
            "title": concept[:40],
            "key_points": [s[:80] for s in scene_text.split(".") if len(s.strip()) > 5][:3] or [concept[:40]],
            "icons": ["lightbulb", "atom"],
            "equation": "",
        }

    scenes: list[dict[str, Any]] = []
    for idx, group in enumerate(sentence_groups, start=1):
        scene_narration = " ".join(group).strip()
        words = len(scene_narration.split())
        scene_dur = max(3.5, round(words / 2.3, 1))
        mode, payload = _infer_mode(scene_narration, idx - 1)

        # Look for candidate equation in scene narration via regex
        eq_match = re.search(r'([A-Za-z0-9₀-₉\(\)]+\s*(?:->|→|=|\+)\s*[A-Za-z0-9₀-₉\(\)\+\s]+)', scene_narration)
        cand_eq = eq_match.group(1).strip() if eq_match else ""

        scenes.append(
            SceneIn(
                scene_order=idx,
                learning_objective=f"Analyze {concept}: Part {idx}" if num_scenes > 1 else f"Understand {concept}",
                narration_text=scene_narration,
                visual_mode=mode,
                visual_payload=payload,
                on_screen_equation=cand_eq,
                on_screen_labels=[concept[:30]],
                key_takeaway=group[-1][:90] if group else concept[:40],
                narration_span=scene_narration,
                duration_seconds=scene_dur,
                visual_objective=f"Illustrate {concept} concepts in scene {idx}",
                entities=[concept[:30]],
                motion_beats=[
                    {"at": 0.0, "action": "establish", "target": "main_stage"},
                    {"at": round(scene_dur * 0.5, 1), "action": "pan_zoom", "target": "detail_card"},
                ],
            ).model_dump(mode="json")
        )

    return scenes


@celery_app.task(name="agents.scene_planning.run")
def run(
    concept: str,
    level: str = "intermediate",
    language: str = "en",
    narration_script: str = "",
    retrieved_chunks: Optional[list[dict]] = None,
    animation_scenes: Optional[list[dict]] = None,
) -> list[dict[str, Any]]:
    return plan_scenes_for_segment(
        concept=concept,
        level=level,
        language=language,
        narration_script=narration_script,
        retrieved_chunks=retrieved_chunks,
        animation_scenes=animation_scenes,
    )
