"""
Unit tests for the Visual Director Agent.
"""
import pytest
from agents.visual_director import (
    determine_visual_strategy,
    direct_scenes_for_segment,
    enrich_segment_with_visual_assets,
)
from models import validate_visual_payload


def test_determine_visual_strategy_chemistry():
    scene = {
        "learning_objective": "Acid-Base neutralization reaction in beakers",
        "narration_text": "When hydrochloric acid mixes with sodium hydroxide, a chemical reaction produces salt and water with heat release.",
        "key_takeaway": "Acid + Base -> Salt + Water",
    }
    mode, strategy, payload = determine_visual_strategy(
        scene, scene_index=1, total_scenes=3, segment_concept="Acids and Bases"
    )
    assert mode in ("reaction_lab", "equation_build", "experiment_observation")
    assert strategy == "vector_diagram"
    # Ensure payload validates against Pydantic schema
    val = validate_visual_payload(mode, payload)
    assert val is not None


def test_determine_visual_strategy_physics_circuit():
    scene = {
        "learning_objective": "Ohm's law in closed circuit",
        "narration_text": "Electric current flows through the resistor driven by the battery voltage according to V = I * R.",
        "key_takeaway": "Current is proportional to voltage",
    }
    mode, strategy, payload = determine_visual_strategy(
        scene, scene_index=1, total_scenes=3, segment_concept="Current Electricity"
    )
    assert mode == "circuit_simulation"
    assert strategy == "vector_diagram"
    val = validate_visual_payload(mode, payload)
    assert val is not None


def test_determine_visual_strategy_biology_cellular():
    scene = {
        "learning_objective": "Cellular respiration in mitochondria",
        "narration_text": "Glucose and oxygen react within mitochondria to produce 38 ATP molecules during cellular respiration.",
        "key_takeaway": "Mitochondria produce ATP energy",
    }
    mode, strategy, payload = determine_visual_strategy(
        scene, scene_index=1, total_scenes=3, segment_concept="Life Processes"
    )
    assert mode == "bio_cellular_process"
    assert strategy == "vector_diagram"
    val = validate_visual_payload(mode, payload)
    assert val is not None


def test_determine_visual_strategy_intro_kinetic_text():
    scene = {
        "learning_objective": "Fundamental law of conservation of energy",
        "narration_text": "Energy can neither be created nor destroyed; it can only transform from one form to another.",
        "key_takeaway": "Total energy is conserved",
    }
    mode, strategy, payload = determine_visual_strategy(
        scene, scene_index=0, total_scenes=4, segment_concept="Work and Energy"
    )
    assert mode == "kinetic_text"
    assert strategy == "kinetic_text"
    val = validate_visual_payload(mode, payload)
    assert val is not None


def test_determine_visual_strategy_general_pdf_illustration():
    # Non-STEM historical / environmental topic from a PDF
    scene = {
        "learning_objective": "Impact of the Industrial Revolution on urban steam machinery",
        "narration_text": "The advent of coal-powered steam engines transformed textile factories and locomotive transport.",
        "entities": ["Steam Engine", "Coal Boiler", "Locomotive"],
    }
    mode, strategy, payload = determine_visual_strategy(
        scene, scene_index=1, total_scenes=4, segment_concept="The Industrial Revolution"
    )
    assert mode in ("ai_illustration", "split_screen")
    assert strategy in ("generate_ai_image", "split_screen")
    val = validate_visual_payload(mode, payload)
    assert val is not None


def test_direct_scenes_for_segment_variety():
    raw_scenes = [
        {
            "scene_order": 1,
            "learning_objective": "Definition and principle of atmospheric greenhouse effect",
            "narration_text": "The greenhouse effect is defined as the warming of Earth's surface caused by atmospheric gases trapping infrared radiation.",
            "visual_mode": "generic_explainer",
            "visual_payload": {},
            "key_takeaway": "Greenhouse gases trap heat in atmosphere",
        },
        {
            "scene_order": 2,
            "learning_objective": "Greenhouse gases absorbing infrared solar radiation",
            "narration_text": "Incoming solar ultraviolet rays penetrate the atmosphere, while outgoing infrared thermal radiation is absorbed by CO2 and methane.",
            "visual_mode": "generic_explainer",
            "entities": ["Solar Radiation", "Infrared Radiation", "Carbon Dioxide", "Atmosphere"],
            "visual_payload": {},
        },
        {
            "scene_order": 3,
            "learning_objective": "Global temperature progression over decades",
            "narration_text": "First industrial emissions rise, second heat retention increases, finally global temperature curves steepen.",
            "visual_mode": "generic_explainer",
            "visual_payload": {},
            "key_takeaway": "Global climate equilibrium shifts",
        },
        {
            "scene_order": 4,
            "learning_objective": "Summary of anthropogenic impacts and mitigation",
            "narration_text": "In summary, renewable energy transition and carbon reduction are essential for stabilization.",
            "visual_mode": "generic_explainer",
            "visual_payload": {},
            "key_takeaway": "Sustainable energy stabilizes the biosphere",
        },
    ]

    directed = direct_scenes_for_segment(
        raw_scenes,
        concept="Climate Dynamics & Greenhouse Effect",
        depth="intermediate",
        generate_images=False,
    )

    assert len(directed) == 4
    # Ensure NO scenes were left on generic_explainer
    modes = [s["visual_mode"] for s in directed]
    assert "generic_explainer" not in modes

    # Ensure visual variety across scenes
    assert len(set(modes)) >= 2, f"Expected diverse visual modes, got {modes}"

    # Ensure every scene's payload is valid
    for s in directed:
        val = validate_visual_payload(s["visual_mode"], s["visual_payload"])
        assert val is not None


def test_enrich_segment_with_visual_assets():
    segment = {
        "concept": "Optics and Refraction of Light",
        "depth": "beginner",
        "scenes": [
            {
                "scene_order": 1,
                "learning_objective": "Convex lens focal point and ray tracing",
                "narration_text": "Convex lens refracts parallel rays through principal focus F with real inverted image.",
                "visual_mode": "generic_explainer",
            }
        ],
    }

    enriched = enrich_segment_with_visual_assets(segment, generate_images=False)
    assert enriched["scenes"][0]["visual_mode"] == "optics_ray_diagram"
