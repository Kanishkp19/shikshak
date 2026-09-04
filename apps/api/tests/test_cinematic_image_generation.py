"""
Shikshak AI — Test Suite: Transcript-Timed Cinematic Image Generation & Quality Gate.

Validates:
  1. Transcript-timed scene contract on SceneIn / SceneOut models.
  2. Scene planning agent dynamic duration calculation and transcript grounding.
  3. Continuous kinetic camera motion over 100% of scene duration (no 8s freeze).
  4. Visual quality gate audit: timing drift, static interval detection, blank canvas rejection,
     and negative visual vocabulary filtering.
"""
from pathlib import Path
import subprocess
import tempfile
import pytest
from PIL import Image

from models import SceneIn, SceneOut
from agents.scene_planning import _fallback_scenes
from skills.video_generation.cinematic_provider import CinematicProvider
from skills.quality_gate import audit_cinematic_video, NEGATIVE_VISUAL_VOCABULARY


def test_transcript_timed_scene_contract_model():
    """Verify SceneIn and SceneOut include all required transcript-timed fields."""
    scene = SceneIn(
        scene_order=1,
        learning_objective="Show outer and inner membranes of mitochondrion with cristae folds",
        narration_text="The mitochondria is the powerhouse of the cell, generating adenosine triphosphate.",
        visual_mode="cinematic",
        visual_payload={"title": "Mitochondria", "takeaway": "Powerhouse of the cell"},
        narration_span="The mitochondria is the powerhouse of the cell, generating adenosine triphosphate.",
        duration_seconds=7.5,
        visual_objective="Show outer and inner membranes of mitochondrion with cristae folds",
        entities=["outer membrane", "inner membrane", "cristae", "ATP synthase"],
        forbidden_terms=["cartoon battery", "generic lightning bolt"],
        motion_beats=[{"time_offset": 0.0, "camera_motion": "slow_zoom_in"}],
        asset_strategy="cinematic_concept",
    )

    data = scene.model_dump()
    assert data["narration_span"].startswith("The mitochondria")
    assert data["duration_seconds"] == 7.5
    assert len(data["entities"]) == 4
    assert "cartoon battery" in data["forbidden_terms"]

    out = SceneOut(
        id="scene_test_123",
        segment_id="seg_test_456",
        scene_order=scene.scene_order,
        learning_objective=scene.learning_objective,
        narration_text=scene.narration_text,
        visual_mode=scene.visual_mode,
        visual_payload=scene.visual_payload,
        duration_seconds=scene.duration_seconds,
        narration_span=scene.narration_span,
        entities=scene.entities,
    )
    assert out.duration_seconds == 7.5
    assert out.narration_span == scene.narration_span
    assert len(out.entities) == 4


def test_scene_planning_fallback_transcript_grounded():
    """Verify fallback scene planning grounds duration and content in narration text."""
    narration = (
        "Welcome to our study of thermodynamics. In this first segment, we will examine the first law "
        "of thermodynamics which states that energy cannot be created or destroyed, only transformed "
        "from one state to another."
    )
    scenes = _fallback_scenes("First Law of Thermodynamics", "intermediate", "en", narration)

    assert len(scenes) >= 1
    first_scene = scenes[0]
    # Duration calculated dynamically (~12.6s for ~29 words)
    dur = first_scene.get("duration_seconds") or first_scene.get("durationSeconds", 0)
    assert dur >= 6.0
    narration_span = first_scene.get("narration_span") or first_scene.get("narrationSpan", "")
    assert "thermodynamics" in narration_span.lower()
    entities = first_scene.get("entities", [])
    assert len(entities) > 0


def test_cinematic_fallback_canvas_and_rendering():
    """Verify CinematicProvider creates a high-contrast pedagogical schema and renders continuous motion."""
    provider = CinematicProvider()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        img_path = tmp_path / "test_schema.jpg"
        vid_path = tmp_path / "test_motion.mp4"

        # 1. Create fallback canvas
        provider._create_fallback_canvas(
            img_path=img_path,
            concept="Bernoulli's Principle",
            entities=["Venturi tube", "Static pressure", "Fluid velocity"],
            objective="Illustrate pressure differential across a fluid constriction",
        )
        assert img_path.exists()
        assert img_path.stat().st_size > 5000

        # Verify image dimensions
        with Image.open(img_path) as img:
            assert img.size == (1280, 720)

        # 2. Render a 10-second clip (longer than old 8-second freeze limit)
        test_duration = 10.0
        provider._render_cinematic_video(
            img_path=img_path,
            concept="Bernoulli's Principle",
            entities=["Venturi tube", "Static pressure"],
            duration=test_duration,
            out_path=vid_path,
        )

        assert vid_path.exists()
        assert vid_path.stat().st_size > 20000

        # 3. Probe duration via ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(vid_path),
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        probed_duration = float(res.stdout.strip())
        assert abs(probed_duration - test_duration) < 0.5

        # 4. Verify continuous kinetic motion across the 10-second span (specifically frame 4s to 9s)
        # Old code froze after 8.0s (frame 200). New code must have distinct frames.
        frame_4s_cmd = [
            "ffmpeg", "-y", "-ss", "4.0", "-i", str(vid_path),
            "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "-"
        ]
        p4 = subprocess.run(frame_4s_cmd, capture_output=True, check=True)

        frame_9s_cmd = [
            "ffmpeg", "-y", "-ss", "9.0", "-i", str(vid_path),
            "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "-"
        ]
        p9 = subprocess.run(frame_9s_cmd, capture_output=True, check=True)

        import io
        img_4 = Image.open(io.BytesIO(p4.stdout)).convert("RGB").resize((160, 90))
        img_9 = Image.open(io.BytesIO(p9.stdout)).convert("RGB").resize((160, 90))

        pixels_4 = list(getattr(img_4, "get_flattened_data", img_4.getdata)())
        pixels_9 = list(getattr(img_9, "get_flattened_data", img_9.getdata)())

        mad = sum(abs(c1 - c2) for px1, px2 in zip(pixels_4, pixels_9) for c1, c2 in zip(px1, px2)) / (len(pixels_4) * 3)
        # Continuous pan & zoom ensures measurable frame change between 4s and 9s
        assert mad > 0.8, f"Frame change between 4s and 9s too low ({mad:.2f}), camera motion froze!"


def test_visual_quality_gate_cinematic_audit():
    """Verify audit_cinematic_video detects valid motion, static slides, and negative vocabulary."""
    provider = CinematicProvider()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        img_path = tmp_path / "valid_schema.jpg"
        vid_path = tmp_path / "valid_clip.mp4"

        provider._create_fallback_canvas(
            img_path=img_path,
            concept="Wave-Particle Duality",
            entities=["Photon packet", "Interference fringe", "Detector screen"],
            objective="Demonstrate diffraction pattern formation",
        )

        provider._render_cinematic_video(
            img_path=img_path,
            concept="Wave-Particle Duality",
            entities=["Photon packet", "Interference fringe"],
            duration=6.0,
            out_path=vid_path,
        )

        # 1. Valid video passes audit
        res_pass = audit_cinematic_video(
            vid_path,
            expected_duration=6.0,
            concept="Wave-Particle Duality",
            entities=["Photon packet", "Interference fringe"],
        )
        assert res_pass.passed is True
        assert len(res_pass.issues) == 0

        # 2. Negative vocabulary in entities or prompt triggers quality gate error
        res_neg = audit_cinematic_video(
            vid_path,
            expected_duration=6.0,
            concept="Balancing Chemical Equations",
            entities=["seesaw balance scale", "weight pan"],
            prompt="cartoon balance scale tipping over",
        )
        assert res_neg.passed is False
        assert any(i.check_name == "negative_vocabulary_violation" for i in res_neg.issues)

        # 3. Blank / solid color canvas rejection
        blank_img_path = tmp_path / "solid_black.jpg"
        blank_vid_path = tmp_path / "solid_black.mp4"
        blank_img = Image.new("RGB", (1280, 720), color=(0, 0, 0))
        blank_img.save(blank_img_path)

        cmd_blank = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(blank_img_path),
            "-c:v", "libx264", "-t", "5.0", "-pix_fmt", "yuv420p",
            str(blank_vid_path)
        ]
        subprocess.run(cmd_blank, capture_output=True, check=True)

        res_blank = audit_cinematic_video(
            blank_vid_path,
            expected_duration=5.0,
            concept="Empty Test",
            entities=[],
        )
        assert res_blank.passed is False
        assert any(i.check_name in ("blank_canvas_rejection", "static_interval") for i in res_blank.issues)
