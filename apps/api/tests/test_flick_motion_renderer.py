"""
Shikshak AI — Flick Motion Graphics & Remotion Integration Test Suite.

Acceptance criteria:
  1. Typed schema validation for MotionGraphicPayload across visual modes.
  2. Quality gate auditing and auto-repair for motion graphic scenes.
  3. Visual Router deterministic routing:
     - Chemistry -> RDKit & Reaction Lab renderers
     - Physics -> Circuit & Optics renderers
     - Biology -> BioIcons renderers
     - Mathematics -> Number line & Algebra renderers
     - Motion -> Flick / Remotion animation renderer
  4. Live Remotion execution of Photosynthesis sequence:
     Sunlight -> Chlorophyll -> Energy -> playable 1280x720 MP4.
  5. Scientific isolation: Chemistry scenes never route to Remotion.
  6. Audio-visual composition with Shikshak FFmpeg stitching pipeline.
  7. Deterministic SHA-256 caching for instant cache hits.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
import pytest

from models import (
    MotionGraphicPayload,
    validate_visual_payload,
    VISUAL_MODE_PAYLOAD_MAP,
)
from skills.quality_gate import audit_scene, audit_scenes_for_segment
from skills.scene_renderers.router import (
    ROUTER_REGISTRY,
    resolve_scene_renderer,
    route_and_render_scene,
)
from skills.scene_renderers.flick_renderer import (
    render_flick_motion,
    _compute_cache_key,
    CACHE_DIR,
)
from skills.scene_renderers.chemistry import (
    render_reaction_lab,
    render_equation_build,
)
from skills.scene_renderers.physics import render_circuit_simulation
from skills.scene_renderers.biology import render_bio_cellular_process
from skills.scene_renderers.mathematics import render_number_line_geometry
from skills.video_generation.media import require_playable_video
from skills.video_stitching import stitch_scenes_into_segment


class TestFlickMotionRenderer:
    """Test suite verifying Flick Remotion engine integration."""

    def test_01_motion_graphic_payload_validation(self):
        """Validate MotionGraphicPayload accepts structured semantic data without raw coordinates."""
        payload_data = {
            "template": "step_by_step_flow",
            "title": "Photosynthesis Light Phase",
            "subtitle": "Energy capture inside chlorophyll",
            "steps": ["Sunlight Absorption", "Water Splitting", "ATP Generation"],
            "elements": [
                {"id": "e1", "type": "badge", "content": "STEP 1"},
                {"id": "e2", "type": "text", "content": "Photons excite electrons in PSII"},
            ],
            "key_takeaway": "Light energy is converted to chemical potential energy.",
            "accent_color": "#22c55e",
            "badge": "BIOLOGY PROCESS",
        }
        validated = validate_visual_payload("motion_graphic", payload_data)
        assert isinstance(validated, MotionGraphicPayload)
        assert validated.template == "step_by_step_flow"
        assert len(validated.steps) == 3
        assert validated.accent_color == "#22c55e"

        # Check other aliases mapped to MotionGraphicPayload
        for mode in ("animated_text", "generic_motion", "step_flow", "concept_highlight", "timeline_motion"):
            assert VISUAL_MODE_PAYLOAD_MAP[mode] is MotionGraphicPayload

    def test_02_quality_gate_handles_motion_scenes(self):
        """Verify quality gate audits and repairs incomplete motion scenes."""
        raw_scene = {
            "scene_order": 1,
            "learning_objective": "Explain how sunlight powers chlorophyll",
            "narration_text": "Sunlight enters the leaf and strikes chlorophyll pigments.",
            "visual_mode": "step_flow",
            "visual_payload": {
                # Missing steps and title, should be repaired by quality gate
            },
            "on_screen_labels": ["Sunlight", "Chlorophyll", "Energy"],
            "key_takeaway": "Solar energy powers the reaction",
        }
        result = audit_scene(raw_scene, concept="Photosynthesis")
        assert result.passed is True
        repaired = result.repaired_scene
        assert repaired["visual_payload"]["title"] != ""
        assert len(repaired["visual_payload"]["steps"]) == 3
        assert repaired["visual_payload"]["steps"] == ["Sunlight", "Chlorophyll", "Energy"]

    def test_03_visual_router_enforces_domain_isolation(self):
        """Verify the central router directs each subject to its dedicated engine."""
        # Chemistry MUST route to chemistry renderers (RDKit / Reaction Lab)
        assert resolve_scene_renderer("reaction_lab") is render_reaction_lab
        assert resolve_scene_renderer("equation_build") is render_equation_build

        # Physics MUST route to circuit / optics renderers
        assert resolve_scene_renderer("circuit_simulation") is render_circuit_simulation

        # Biology MUST route to bio cellular renderer
        assert resolve_scene_renderer("bio_cellular_process") is render_bio_cellular_process

        # Mathematics MUST route to geometry / algebra renderers
        assert resolve_scene_renderer("number_line_geometry") is render_number_line_geometry

        # Motion modes MUST route to Flick Remotion renderer
        for mode in ("motion_graphic", "animated_text", "generic_motion", "step_flow", "concept_highlight", "timeline_motion"):
            assert resolve_scene_renderer(mode) is render_flick_motion

        # Chemistry is never hijacked by Flick
        assert resolve_scene_renderer("reaction_lab") is not render_flick_motion

    def test_04_photosynthesis_motion_render_end_to_end(self, tmp_path):
        """End-to-end live test: Render Photosynthesis Sunlight -> Chlorophyll -> Energy to 1280x720 MP4."""
        scene_payload = {
            "template": "step_by_step_flow",
            "title": "Photosynthesis Energy Transfer",
            "subtitle": "Conversion of solar radiation into chemical bonds",
            "steps": ["SUNLIGHT", "CHLOROPHYLL", "ENERGY"],
            "key_takeaway": "Photons drive the synthesis of high-energy chemical bonds.",
            "accent_color": "#10b981",
            "badge": "BIOLOGY FLOW",
        }
        out_file = tmp_path / "photosynthesis_test.mp4"
        rendered_path = render_flick_motion(
            payload_dict=scene_payload,
            narration_text="Sunlight provides energy to chlorophyll.",
            duration_seconds=3.0,
            out_path=out_file,
        )

        assert rendered_path.exists()
        assert rendered_path.stat().st_size > 50_000
        # Validate that video is 1280x720 playable MP4
        require_playable_video(str(rendered_path), min_width=1280, min_height=720, min_duration_seconds=1.0)

    def test_05_chemistry_scene_preserves_rdkit_reaction_lab(self, tmp_path):
        """Verify that a chemistry-specific scene still uses RDKit/Reaction Lab, NOT Remotion."""
        chem_scene = {
            "scene_order": 1,
            "learning_objective": "Precipitation reaction of sodium sulphate and barium chloride",
            "narration_text": "Sodium sulphate reacts with barium chloride to form a white precipitate.",
            "visual_mode": "reaction_lab",
            "visual_payload": {
                "reactants": [
                    {"name": "Sodium sulphate", "formula": "Na2SO4", "state": "aqueous", "color": "#38bdf8"},
                    {"name": "Barium chloride", "formula": "BaCl2", "state": "aqueous", "color": "#818cf8"},
                ],
                "products": [
                    {"name": "Barium sulphate", "formula": "BaSO4", "state": "solid", "color": "#f8fafc", "observation": "white precipitate"},
                    {"name": "Sodium chloride", "formula": "NaCl", "state": "aqueous", "color": "#38bdf8"},
                ],
                "conditions": "room temperature",
                "observation": "Insoluble white precipitate forms",
                "balanced_equation": "Na2SO4 + BaCl2 -> BaSO4 + 2NaCl",
                "atom_counts": {"Na": 2, "S": 1, "O": 4, "Ba": 1, "Cl": 2},
            },
            "on_screen_equation": "Na2SO4 + BaCl2 -> BaSO4 + 2NaCl",
            "on_screen_labels": ["Na2SO4", "BaCl2", "BaSO4 ppt"],
            "key_takeaway": "BaSO4 is insoluble and forms immediately.",
        }

        # Route through router
        renderer = resolve_scene_renderer(chem_scene["visual_mode"])
        assert renderer is render_reaction_lab
        assert renderer is not render_flick_motion

        chem_out = tmp_path / "chemistry_test.mp4"
        res = route_and_render_scene(chem_scene, duration_seconds=3.0, out_path=chem_out)
        assert res.exists()
        require_playable_video(str(res), min_width=1280, min_height=720, min_duration_seconds=1.0)

    def test_06_flick_deterministic_caching(self, tmp_path):
        """Verify deterministic SHA-256 caching avoids redundant Remotion renders."""
        payload = {
            "template": "animated_title",
            "title": "Quantum Mechanics Intro",
            "subtitle": "Wave-particle duality",
            "key_takeaway": "Light exhibits both wave and particle properties.",
            "accent_color": "#a855f7",
            "badge": "PHYSICS MOTION",
        }
        out_1 = tmp_path / "cache_test_1.mp4"
        out_2 = tmp_path / "cache_test_2.mp4"

        # First call renders & stores in cache
        p1 = render_flick_motion(payload, narration_text="Light wave", duration_seconds=2.0, out_path=out_1)
        assert p1.exists()

        # Second call with same payload should hit cache immediately
        cache_key = _compute_cache_key(payload, "Light wave", 2.0)
        assert (CACHE_DIR / f"{cache_key}.mp4").exists()

        p2 = render_flick_motion(payload, narration_text="Light wave", duration_seconds=2.0, out_path=out_2)
        assert p2.exists()
        assert p2.stat().st_size == p1.stat().st_size

    def test_07_remotion_scene_stitches_with_audio(self, tmp_path):
        """Verify a Remotion MP4 scene integrates into Shikshak FFmpeg stitching pipeline."""
        # 1. Render motion scene
        payload = {
            "template": "concept_highlight",
            "title": "Energy Conversion",
            "subtitle": "Solar to chemical ATP",
            "steps": ["Sunlight Photons", "Excitation", "ATP Synthase"],
            "key_takeaway": "Energy is neither created nor destroyed.",
        }
        scene_video = tmp_path / "scene_video.mp4"
        render_flick_motion(payload, narration_text="Energy conversion", duration_seconds=3.0, out_path=scene_video)

        # 2. Generate a 3-second silent audio track for the scene
        audio_path = tmp_path / "test_audio.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", str(audio_path)],
            capture_output=True,
            check=True,
        )

        scene_spec = {
            "scene_order": 1,
            "visual_mode": "motion_graphic",
            "narration_text": "Energy conversion",
        }

        stitched = stitch_scenes_into_segment(
            scene_video_paths=[str(scene_video)],
            audio_path=str(audio_path),
        )

        assert Path(stitched).exists()
        require_playable_video(str(stitched), min_width=1280, min_height=720, min_duration_seconds=2.0)
