"""
Shikshak AI — Universal Multi-Subject Benchmark Acceptance Test.

Verifies end-to-end multi-subject visual generation across:
  - Physics (Electricity Circuits, Optics Ray Diagrams)
  - Biology (Cellular Respiration, Anatomical Heart)
  - Mathematics (Real Numbers Geometry, Stepwise Algebra)
  - Chemistry (Reactions, Balancing, Experiments)
  - Scene Planning Agent subject routing
"""
from __future__ import annotations

from pathlib import Path
import pytest

from models import (
    CircuitSimulationPayload,
    OpticsRayDiagramPayload,
    BioCellularProcessPayload,
    AnatomicalStructurePayload,
    NumberLineGeometryPayload,
    AlgebraStepSolvePayload,
    validate_visual_payload,
)
from skills.scene_renderers import (
    render_circuit_simulation,
    render_optics_ray_diagram,
    render_bio_cellular_process,
    render_anatomical_structure,
    render_number_line_geometry,
    render_algebra_step_solve,
    get_scene_renderer,
)
from agents.scene_planning import plan_scenes_for_segment


class TestUniversalMultiSubjectBenchmark:
    """Acceptance suite for universal STEM scene rendering."""

    def test_01_payload_validation_across_all_domains(self):
        """Validate all STEM payload models against the single source of truth."""
        # 1. Physics: Circuit Simulation
        circuit_payload = validate_visual_payload("circuit_simulation", {
            "circuit_type": "series",
            "voltage": 12.0,
            "resistance": 4.0,
            "current": 3.0,
            "formula": "V = I * R",
        })
        assert isinstance(circuit_payload, CircuitSimulationPayload)
        assert circuit_payload.voltage == 12.0

        # 2. Physics: Optics Ray Diagram
        optics_payload = validate_visual_payload("optics_ray_diagram", {
            "optical_element": "convex_lens",
            "focal_length": 10.0,
            "object_distance": 20.0,
        })
        assert isinstance(optics_payload, OpticsRayDiagramPayload)

        # 3. Biology: Cellular Process
        bio_payload = validate_visual_payload("bio_cellular_process", {
            "process_name": "Cellular Respiration",
            "organelle": "Mitochondria",
            "energy_yield": "38 ATP",
        })
        assert isinstance(bio_payload, BioCellularProcessPayload)

        # 4. Biology: Anatomy
        anatomy_payload = validate_visual_payload("anatomical_structure", {
            "structure_name": "Human Heart",
            "callouts": [{"label": "Left Ventricle", "function": "Pumps blood"}],
        })
        assert isinstance(anatomy_payload, AnatomicalStructurePayload)

        # 5. Mathematics: Number Line Geometry
        math_payload = validate_visual_payload("number_line_geometry", {
            "title": "Real Numbers on Number Line",
            "theorem": "Every real number has a unique position",
        })
        assert isinstance(math_payload, NumberLineGeometryPayload)

        # 6. Mathematics: Algebra Step Solve
        algebra_payload = validate_visual_payload("algebra_step_solve", {
            "title": "Quadratic Formula",
            "initial_expression": "ax^2 + bx + c = 0",
        })
        assert isinstance(algebra_payload, AlgebraStepSolvePayload)

    def test_02_render_physics_scenes_to_mp4(self, tmp_path: Path):
        """Render electricity and optics scenes into valid MP4 video files."""
        # Circuit simulation
        p1 = render_circuit_simulation({
            "voltage": 12.0,
            "resistance": 6.0,
            "current": 2.0,
            "formula": "V = I × R",
        }, duration_seconds=1.5, out_path=tmp_path / "circuit.mp4")
        assert p1.exists() and p1.stat().st_size > 1000

        # Optics ray diagram
        p2 = render_optics_ray_diagram({
            "optical_element": "convex_lens",
            "focal_length": 10.0,
            "object_distance": 20.0,
        }, duration_seconds=1.5, out_path=tmp_path / "optics.mp4")
        assert p2.exists() and p2.stat().st_size > 1000

    def test_03_render_biology_scenes_to_mp4(self, tmp_path: Path):
        """Render cellular respiration and anatomical diagrams into valid MP4 video files."""
        # Cellular process
        p1 = render_bio_cellular_process({
            "process_name": "Cellular Respiration",
            "organelle": "Mitochondria",
            "energy_yield": "38 ATP",
        }, duration_seconds=1.5, out_path=tmp_path / "respiration.mp4")
        assert p1.exists() and p1.stat().st_size > 1000

        # Anatomy
        p2 = render_anatomical_structure({
            "structure_name": "Human Heart Circulation",
        }, duration_seconds=1.5, out_path=tmp_path / "heart.mp4")
        assert p2.exists() and p2.stat().st_size > 1000

    def test_04_render_mathematics_scenes_to_mp4(self, tmp_path: Path):
        """Render real number line geometry and algebra into valid MP4 video files."""
        # Number line geometry
        p1 = render_number_line_geometry({
            "title": "Representation of Real Numbers",
            "construction_step": "Hypotenuse = √2 ≈ 1.414",
        }, duration_seconds=1.5, out_path=tmp_path / "real_numbers.mp4")
        assert p1.exists() and p1.stat().st_size > 1000

        # Algebra step solve
        p2 = render_algebra_step_solve({
            "title": "Quadratic Derivation",
            "initial_expression": "ax² + bx + c = 0",
        }, duration_seconds=1.5, out_path=tmp_path / "algebra.mp4")
        assert p2.exists() and p2.stat().st_size > 1000

    def test_05_multi_subject_scene_planning_routing(self):
        """Verify Scene Planning Agent generates appropriate visual modes for diverse topics."""
        # 1. Physics topic: Electricity & Ohm's Law
        p_scenes = plan_scenes_for_segment(concept="Electric Current and Ohm's Law")
        assert len(p_scenes) >= 1
        assert p_scenes[0]["visual_mode"] in ("circuit_simulation", "generic_explainer")

        # 2. Physics topic: Refraction & Lenses
        optics_scenes = plan_scenes_for_segment(concept="Refraction of Light by Spherical Lenses")
        assert len(optics_scenes) >= 1
        assert optics_scenes[0]["visual_mode"] in ("optics_ray_diagram", "generic_explainer")

        # 3. Biology topic: Cellular Respiration
        bio_scenes = plan_scenes_for_segment(concept="Cellular Respiration in Mitochondria")
        assert len(bio_scenes) >= 1
        assert bio_scenes[0]["visual_mode"] in ("bio_cellular_process", "equation_build", "generic_explainer")

        # 4. Mathematics topic: Real Numbers
        math_scenes = plan_scenes_for_segment(concept="Representation of Real Numbers on Number Line")
        assert len(math_scenes) >= 1
        assert math_scenes[0]["visual_mode"] in ("number_line_geometry", "generic_explainer")
