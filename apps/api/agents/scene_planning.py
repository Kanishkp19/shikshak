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

6. UNIVERSAL FALLBACK:
   - "generic_explainer": Illustrated concept cards with icons, equations, and takeaways.
     visual_payload: {{"title": "Scientific Concept", "key_points": ["Point 1", "Point 2"], "icons": ["atom", "sparkles"], "equation": ""}}

CRITICAL RULES:
1. Act as the Lead Educational Animator: plan 3 to 5 discrete, lively visual scenes for the segment narration.
2. BAN STATIC SLIDESHOWS: NEVER create static PowerPoint-style cards with bullet-point lists of equations (e.g. lists like "• f = R/2", "• 1/v + 1/u = 1/f"). Every formula MUST be animated within an active physical apparatus or step-by-step derivation:
   - Optical mirrors/curvature -> "spherical_mirror"
   - Lenses / Ray refraction -> "optics_ray_diagram"
   - Electric circuits & Ohm's law -> "circuit_simulation"
   - Chemical reactions & beakers -> "reaction_lab"
   - Chemical formula combining -> "equation_build"
   - Algebraic & mathematical derivations -> "algebra_step_solve"
3. Select the MOST ACCURATE visual mode:
   - Chemical reaction apparatus / beakers -> "reaction_lab"
   - Chemical formula combining / equation steps -> "equation_build"
   - Laboratory oxidation / heating experiment -> "experiment_observation"
   - Mass conservation / atom counting -> "balancing_exercise"
   - Electric circuits & schematics -> "circuit_simulation"
   - Ray optics / refraction / reflection -> "optics_ray_diagram"
   - Spherical mirror curvature & focal relations -> "spherical_mirror"
   - Cell organelles & anatomy -> "bio_cellular_process" or "anatomical_structure"
   - Number line & coordinate geometry -> "number_line_geometry"
   - Dynamic pedagogical flows & kinetic pathways -> "motion_graphic", "step_flow", or "timeline_motion"
4. Each scene MUST focus on ONE dominant idea and ONE learning objective.
5. Every visual_payload MUST match the exact fields required by its visual_mode.
6. Return 3 to 5 scenes in strictly sequential scene_order (1, 2, 3...).

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
        duration = sc.duration_seconds if sc.duration_seconds > 1.0 else calculated_dur

        # Extract entities from on_screen_labels or concept if empty
        entities = sc.entities or sc.on_screen_labels or [concept[:40]]

        scene_obj = SceneIn(
            scene_order=idx,
            learning_objective=sc.learning_objective or f"Learn {concept}",
            narration_text=sc.narration_text or narration,
            visual_mode=mode,
            visual_payload=payload_dict,
            on_screen_equation=sc.on_screen_equation or "",
            on_screen_labels=sc.on_screen_labels or [],
            key_takeaway=sc.key_takeaway or "",
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
    """Deterministic fallback across Physics, Biology, Mathematics, and Chemistry."""
    c_lower = concept.lower()

    script = (narration_script or "").strip()
    dur = max(4.0, round(len(script.split()) / 2.3, 1)) if script else 6.0

    # 1. Physics: Electricity & Circuits
    if any(k in c_lower for k in ("electric", "circuit", "ohm", "current", "voltage", "resistan", "potenti")):
        text = "In a closed electric circuit, potential difference from a battery drives a continuous flow of electric charge through the resistor."
        return [
            SceneIn(
                scene_order=1,
                learning_objective="Understand electric circuit components and current flow",
                narration_text=script or text,
                visual_mode="circuit_simulation",
                visual_payload={
                    "circuit_type": "series",
                    "voltage": 12.0,
                    "resistance": 6.0,
                    "current": 2.0,
                    "formula": "V = I × R",
                    "observation": "Current of 2.0 Amperes flows steadily through the 6Ω load under 12V potential.",
                },
                on_screen_equation="V = I × R ⇒ I = V / R = 12V / 6Ω = 2A",
                on_screen_labels=["12V DC Battery", "6Ω Resistor", "Ammeter (2A)", "Closed Switch"],
                key_takeaway="Ohm's Law states current is directly proportional to voltage across a conductor.",
                narration_span=script or text,
                duration_seconds=dur,
                visual_objective="Simulate current flow and Ohm's law in closed DC circuit",
                entities=["Battery", "Resistor", "Current Flow", "Ammeter"],
                motion_beats=[{"at": 0.0, "action": "establish", "target": "circuit"}, {"at": round(dur * 0.5, 1), "action": "pan_zoom", "target": "resistor"}],
            ).model_dump(mode="json"),
        ]

    # 2. Physics: Optics & Light
    if any(k in c_lower for k in ("light", "optic", "lens", "mirror", "reflect", "refract", "ray", "focal")):
        text = "When an object is placed at 2F₁ in front of a convex lens, refracted rays intersect at 2F₂ to produce a real, inverted image of the same size."
        return [
            SceneIn(
                scene_order=1,
                learning_objective="Ray tracing and real image formation by a convex lens",
                narration_text=script or text,
                visual_mode="optics_ray_diagram",
                visual_payload={
                    "optical_element": "convex_lens",
                    "focal_length": 10.0,
                    "object_distance": 20.0,
                    "object_height": 5.0,
                    "image_distance": 20.0,
                    "image_height": -5.0,
                    "image_nature": "Real, Inverted, Same Size",
                    "formula": "1/f = 1/v - 1/u",
                    "key_observation": "Parallel rays converge through principal focus F₂.",
                },
                on_screen_equation="1/f = 1/v - 1/u",
                on_screen_labels=["Convex Lens", "Principal Focus (F)", "Object at 2F₁", "Inverted Image at 2F₂"],
                key_takeaway="Convex lenses converge light rays to form real, inverted images at conjugate focal distances.",
                narration_span=script or text,
                duration_seconds=dur,
                visual_objective="Trace refraction and conjugate real image formation",
                entities=["Convex Lens", "Principal Axis", "Focal Point F", "Refracted Rays"],
                motion_beats=[{"at": 0.0, "action": "establish", "target": "lens_axis"}, {"at": round(dur * 0.5, 1), "action": "pan_zoom", "target": "image_plane"}],
            ).model_dump(mode="json"),
        ]

    # 3. Biology: Cellular Respiration & Life Processes
    if any(k in c_lower for k in ("respirat", "glucose", "mitochondr", "atp", "cellular", "photosynth")):
        text = "Inside cellular mitochondria, glucose combines with oxygen through metabolic stages, yielding 38 ATP energy molecules along with carbon dioxide and water."
        return [
            SceneIn(
                scene_order=1,
                learning_objective="Biochemical pathway of cellular respiration in mitochondria",
                narration_text=script or text,
                visual_mode="bio_cellular_process",
                visual_payload={
                    "process_name": "Cellular Respiration",
                    "organelle": "Mitochondria",
                    "inputs": ["Glucose (C₆H₁₂O₆)", "Oxygen (6O₂)"],
                    "outputs": ["Carbon Dioxide (6CO₂)", "Water (6H₂O)", "38 ATP Energy"],
                    "energy_yield": "38 ATP Molecules",
                    "overall_equation": "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy (38 ATP)",
                    "key_takeaway": "Cellular respiration breaks down glucose to generate vital ATP energy in mitochondria.",
                },
                on_screen_equation="C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + 38 ATP",
                on_screen_labels=["Mitochondrion Cristae", "Glucose (C₆H₁₂O₆)", "Oxygen (6O₂)", "ATP Energy release"],
                key_takeaway="Respiration is the essential biological process powering cellular life.",
                narration_span=script or text,
                duration_seconds=dur,
                visual_objective="Illustrate mitochondrial ATP release from glucose oxidation",
                entities=["Mitochondria", "Glucose", "Oxygen", "ATP Energy"],
                motion_beats=[{"at": 0.0, "action": "establish", "target": "mitochondrion"}, {"at": round(dur * 0.5, 1), "action": "pan_zoom", "target": "cristae_atp"}],
            ).model_dump(mode="json"),
        ]

    # 4. Mathematics: Real Numbers & Geometry
    if any(k in c_lower for k in ("real number", "number line", "rational", "irrational", "sqrt", "pythagor", "root")):
        text = "By constructing a right-angled triangle of base 1 unit and height 1 unit, Pythagoras' theorem gives a hypotenuse of √2, which we project directly onto the real number line."
        return [
            SceneIn(
                scene_order=1,
                learning_objective="Representation of irrational numbers on the real number line",
                narration_text=script or text,
                visual_mode="number_line_geometry",
                visual_payload={
                    "title": "Representation of Real Numbers on Number Line",
                    "marked_points": [{"label": "√2", "value": 1.414, "color": "#38bdf8"}],
                    "intervals": [],
                    "theorem": "Every real number corresponds to a unique point on the number line.",
                    "construction_step": "Right triangle with base=1 and height=1 yields hypotenuse OB = √2 ≈ 1.414",
                },
                on_screen_equation="OB² = 1² + 1² = 2 ⇒ OB = √2 ≈ 1.414...",
                on_screen_labels=["Origin 0 (O)", "Unit Base 1 (A)", "Perpendicular 1 (B)", "Point P (√2)"],
                key_takeaway="Every real number (rational and irrational) has a unique geometric position on the continuous real number line.",
                narration_span=script or text,
                duration_seconds=dur,
                visual_objective="Geometric Pythagoras construction of root 2 on number line",
                entities=["Number Line", "Right Triangle", "Hypotenuse √2", "Projected Point P"],
                motion_beats=[{"at": 0.0, "action": "establish", "target": "number_line"}, {"at": round(dur * 0.5, 1), "action": "pan_zoom", "target": "root_2_point"}],
            ).model_dump(mode="json"),
        ]

    # 5. Chemistry: Reactions & Lab
    if any(k in c_lower for k in ("react", "precipitat", "oxid", "acid", "base", "salt", "chemi")):
        text = "Chemical reactions involve rearrangement of atoms and formation of new bonds, accompanied by characteristic observations."
        return [
            SceneIn(
                scene_order=1,
                learning_objective="Observation and chemistry of chemical reactions",
                narration_text=script or text,
                visual_mode="experiment_observation",
                visual_payload={
                    "setup_description": f"Experimental study of {concept}",
                    "steps": [
                        {"action": "Initiate reaction conditions", "observation": "Transformation occurs with observable change", "visual_cue": "reactant to product"}
                    ],
                    "conclusion": f"Reaction completes confirming principles of {concept}.",
                },
                on_screen_equation="Reactants → Products + Energy",
                on_screen_labels=["Reactants", "Reaction Vessel", "Products"],
                key_takeaway="Chemical equations describe the conservation of mass and transformation of substances.",
                narration_span=script or text,
                duration_seconds=dur,
                visual_objective=f"Experimental laboratory observation of {concept}",
                entities=["Reactants", "Reaction Flask", "Products", "Observation"],
                motion_beats=[{"at": 0.0, "action": "establish", "target": "reaction_flask"}, {"at": round(dur * 0.5, 1), "action": "pan_zoom", "target": "product_transformation"}],
            ).model_dump(mode="json"),
        ]

    # Default Universal Explainer
    default_text = script or f"Let us examine the foundational concepts governing {concept}."
    return [
        SceneIn(
            scene_order=1,
            learning_objective=f"Fundamental principles of {concept}",
            narration_text=default_text,
            visual_mode="generic_explainer",
            visual_payload={
                "title": concept[:40],
                "key_points": [
                    f"Core principles and definition of {concept}",
                    "Key relationships and governing laws",
                ],
                "icons": ["lightbulb", "atom"],
                "equation": "",
            },
            on_screen_equation="",
            on_screen_labels=[concept[:30], "Core Principle"],
            key_takeaway=f"Core understanding of {concept}.",
            narration_span=default_text,
            duration_seconds=dur,
            visual_objective=f"Explain core principles of {concept}",
            entities=[concept[:30], "Concept Principles"],
            motion_beats=[{"at": 0.0, "action": "establish", "target": "concept_overview"}, {"at": round(dur * 0.5, 1), "action": "pan_zoom", "target": "principles"}],
        ).model_dump(mode="json"),
    ]


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
