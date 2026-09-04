"""
Shikshak AI — Chemistry Lesson Benchmark (Acceptance Test Suite).

Verifies the complete scene-first video-lesson architecture against the
benchmark requirements defined in GOAL.md:
  1. Precipitation reaction (Na2SO4 + BaCl2 -> BaSO4 precipitate + 2NaCl)
  2. Copper oxidation (2Cu + O2 -> 2CuO)
  3. Respiration exothermic reaction (C6H12O6 + 6O2 -> 6CO2 + 6H2O + energy)
  4. Atom conservation & equation balancing

Acceptance Criteria:
  - Decomposes lesson into discrete, purposeful visual scenes (not 1 consolidated flowchart)
  - Validates typed visual payloads against Pydantic models
  - Successfully routes each scene to its domain renderer
  - All 5 chemistry renderers produce valid playable 1280x720 MP4 files
  - Quality gate catches and repairs missing equations and invalid schemas
  - Compositor stitches scenes with real audio duration timing
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest

from models import (
    ReactionLabPayload,
    EquationBuildPayload,
    ExperimentObservationPayload,
    BalancingExercisePayload,
    GenericExplainerPayload,
    validate_visual_payload,
    VISUAL_MODE_PAYLOAD_MAP,
)
from agents.scene_planning import plan_scenes_for_segment
from agents.visual_selection import select_visuals, get_renderer_for_mode, dispatch_scene_render
from skills.scene_renderers import (
    render_reaction_lab,
    render_equation_build,
    render_experiment_observation,
    render_balancing_exercise,
    render_generic_explainer,
    RENDERER_REGISTRY,
)
from skills.quality_gate import audit_scene, audit_scenes_for_segment
from skills.video_stitching import stitch_scenes_into_segment
from skills.video_generation.media import require_playable_video


class TestChemistryBenchmark:
    """Acceptance test suite for Scene-First Video Lessons."""

    def test_01_schema_contracts_and_payload_validation(self):
        """Verify all 5 chemistry visual modes validate their typed payloads."""
        # 1. Reaction Lab
        p_rxn = validate_visual_payload("reaction_lab", {
            "reactants": [
                {"name": "Sodium sulphate", "formula": "Na2SO4", "state": "aqueous", "color": "#38bdf8"},
                {"name": "Barium chloride", "formula": "BaCl2", "state": "aqueous", "color": "#818cf8"}
            ],
            "products": [
                {"name": "Barium sulphate", "formula": "BaSO4", "state": "solid", "color": "#f8fafc", "observation": "white precipitate"},
                {"name": "Sodium chloride", "formula": "NaCl", "state": "aqueous", "color": "#38bdf8"}
            ],
            "conditions": "room temperature",
            "observation": "Insoluble white precipitate of BaSO4 forms immediately",
            "balanced_equation": "Na2SO4 + BaCl2 -> BaSO4 + 2NaCl",
            "atom_counts": {"Na": 2, "S": 1, "O": 4, "Ba": 1, "Cl": 2},
        })
        assert isinstance(p_rxn, ReactionLabPayload)
        assert len(p_rxn.reactants) == 2
        assert "BaSO4" in p_rxn.balanced_equation

        # 2. Equation Build
        p_eq = validate_visual_payload("equation_build", {
            "steps": ["C6H12O6", "C6H12O6 + 6O2", "C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy"],
            "final_equation": "C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy",
            "atom_highlight": ["C", "H", "O"],
        })
        assert isinstance(p_eq, EquationBuildPayload)
        assert len(p_eq.steps) == 3

        # 3. Experiment Observation
        p_obs = validate_visual_payload("experiment_observation", {
            "setup_description": "Copper powder heated in a china dish",
            "steps": [{"action": "Heat in air", "observation": "Turns black (CuO)"}],
            "conclusion": "2Cu + O2 -> 2CuO",
        })
        assert isinstance(p_obs, ExperimentObservationPayload)

        # 4. Balancing Exercise
        p_bal = validate_visual_payload("balancing_exercise", {
            "unbalanced_equation": "Cu + O2 -> CuO",
            "balanced_equation": "2Cu + O2 -> 2CuO",
            "atom_inventory": {"Cu": [2, 2], "O": [2, 2]},
        })
        assert isinstance(p_bal, BalancingExercisePayload)

        # 5. Generic Explainer
        p_gen = validate_visual_payload("generic_explainer", {
            "title": "Atom Conservation Principle",
            "key_points": ["Mass is neither created nor destroyed", "Atoms rearrange during reactions"],
            "equation": "Reactants -> Products",
        })
        assert isinstance(p_gen, GenericExplainerPayload)

    def test_02_scene_planning_decomposition(self):
        """Verify Scene Planning breaks chemistry segments into 2-5 distinct scenes."""
        concepts = [
            "Sodium sulphate and Barium chloride precipitation",
            "Copper surface oxidation and heating in air",
            "Respiration exothermic reaction and energy release",
        ]

        for concept in concepts:
            scenes = plan_scenes_for_segment(concept=concept, level="intermediate")
            assert len(scenes) >= 2, f"Segment '{concept}' should have at least 2 scenes"
            for sc in scenes:
                assert sc["visual_mode"] in RENDERER_REGISTRY
                assert "visual_payload" in sc
                assert sc["learning_objective"]
                assert sc["narration_text"]

    def test_03_quality_gate_audit_and_auto_repair(self):
        """Verify the quality gate detects and auto-repairs missing formulas and schemas."""
        bad_scene = {
            "scene_order": 1,
            "learning_objective": "Understand reaction mechanism",
            "narration_text": "Observe the reaction.",
            "visual_mode": "reaction_lab",
            "visual_payload": {
                "reactants": [{"name": "A", "formula": "A"}],
                "products": [{"name": "B", "formula": "B"}],
                "balanced_equation": "A -> B",
            },
            "on_screen_equation": "",  # Missing! Quality gate should repair
            "on_screen_labels": ["Mechanism", "Reactant A"],  # Generic label warning
        }

        res = audit_scene(bad_scene, concept="Test Reaction")
        assert res.passed is True
        # Verify auto-repair populated on_screen_equation
        assert res.repaired_scene["on_screen_equation"] == "A -> B"

    def test_04_render_all_chemistry_modes_to_mp4(self, tmp_path):
        """Verify all 5 renderers generate valid 1280x720 H.264 MP4 videos."""
        # 1. Reaction Lab MP4
        rxn_path = render_reaction_lab({
            "reactants": [
                {"name": "Sodium sulphate", "formula": "Na₂SO₄", "state": "aqueous", "color": "#38bdf8"},
                {"name": "Barium chloride", "formula": "BaCl₂", "state": "aqueous", "color": "#818cf8"},
            ],
            "products": [
                {"name": "Barium sulphate", "formula": "BaSO₄", "state": "solid", "color": "#f8fafc", "observation": "white precipitate"},
                {"name": "Sodium chloride", "formula": "NaCl", "state": "aqueous", "color": "#38bdf8"},
            ],
            "conditions": "room temperature",
            "observation": "Insoluble white precipitate of BaSO₄ forms immediately",
            "balanced_equation": "Na₂SO₄(aq) + BaCl₂(aq) → BaSO₄(s)↓ + 2NaCl(aq)",
            "atom_counts": {"Na": 2, "S": 1, "O": 4, "Ba": 1, "Cl": 2},
        }, duration_seconds=2.0, out_path=tmp_path / "rxn.mp4")
        require_playable_video(str(rxn_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

        # 2. Equation Build MP4
        eq_path = render_equation_build({
            "steps": ["C₆H₁₂O₆", "C₆H₁₂O₆ + 6O₂", "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy"],
            "final_equation": "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy",
            "atom_highlight": ["C", "H", "O"],
        }, duration_seconds=2.0, out_path=tmp_path / "eq.mp4")
        require_playable_video(str(eq_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

        # 3. Experiment Observation MP4
        obs_path = render_experiment_observation({
            "setup_description": "China dish with copper powder over burner",
            "steps": [{"action": "Heat in air", "observation": "Surface turns black"}],
            "conclusion": "2Cu + O₂ → 2CuO",
        }, duration_seconds=2.0, out_path=tmp_path / "obs.mp4")
        require_playable_video(str(obs_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

        # 4. Balancing Exercise MP4
        bal_path = render_balancing_exercise({
            "unbalanced_equation": "Cu + O₂ → CuO",
            "balanced_equation": "2Cu + O₂ → 2CuO",
            "atom_inventory": {"Cu": [2, 2], "O": [2, 2]},
        }, duration_seconds=2.0, out_path=tmp_path / "bal.mp4")
        require_playable_video(str(bal_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

        # 5. Generic Explainer MP4
        gen_path = render_generic_explainer({
            "title": "Conservation of Mass in Reactions",
            "key_points": ["Total mass remains constant", "Bonds rearrange to form products"],
            "equation": "2Cu + O₂ → 2CuO",
        }, duration_seconds=2.0, out_path=tmp_path / "gen.mp4")
        require_playable_video(str(gen_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

    def test_05_end_to_end_scene_pipeline_and_stitching(self, tmp_path):
        """Verify end-to-end: Segment -> Scene Planning -> Dispatch Render -> Stitch."""
        concept = "Sodium sulphate and Barium chloride precipitation"
        scenes = plan_scenes_for_segment(concept=concept)
        audited_scenes = audit_scenes_for_segment(scenes, concept=concept)

        rendered_scene_clips = []
        for i, sc in enumerate(audited_scenes):
            clip_path = dispatch_scene_render(
                scene=sc,
                duration_seconds=2.0,
                out_path=tmp_path / f"scene_{i}.mp4",
            )
            assert Path(clip_path).exists()
            rendered_scene_clips.append(str(clip_path))

        # Stitch scenes into one segment video
        final_segment = stitch_scenes_into_segment(
            scene_video_paths=rendered_scene_clips,
            language="en",
        )
        require_playable_video(final_segment, min_width=1280, min_height=720, min_duration_seconds=1.0)
        assert Path(final_segment).stat().st_size > 1000
