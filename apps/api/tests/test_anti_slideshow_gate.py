"""
Tests for Anti-Slideshow Quality Gate & Lively Educational Animations.
"""
from pathlib import Path
import pytest

from skills.quality_gate import audit_scene
from skills.scene_renderers.physics.spherical_mirror import render_spherical_mirror_optics
from skills.scene_renderers.physics.optics_ray_diagram import render_optics_ray_diagram
from skills.video_generation.media import require_playable_video


def test_anti_slideshow_gate_intercepts_bulleted_formulas():
    """Verify that a PowerPoint-style bulleted formula scene is intercepted and repaired into an active simulation."""
    slideshow_scene = {
        "scene_order": 2,
        "visual_mode": "concept_highlight",
        "learning_objective": "Spherical mirror equations and geometry",
        "narration_text": "Focal length is half the radius of curvature, linked via the mirror formula.",
        "on_screen_equation": "1/v + 1/u = 1/f",
        "visual_payload": {
            "template": "concept_highlight",
            "title": "Mirror Equations & Geometry",
            "subtitle": "Fundamental relations for spherical mirrors",
            "steps": [
                "f = R / 2",
                "1/v + 1/u = 1/f",
                "Apply Sign Conventions",
            ],
            "key_takeaway": "Focal length is half the radius of curvature, linked via the mirror formula.",
        },
    }

    result = audit_scene(slideshow_scene, concept="Spherical Mirrors")
    assert result.passed is True
    assert result.visual_mode == "spherical_mirror"
    assert result.repaired_scene["visual_mode"] == "spherical_mirror"
    assert result.repaired_scene["visual_payload"]["formula"] == "1/v + 1/u = 1/f"
    assert any(i.check_name == "anti_slideshow_gate" for i in result.issues)


def test_anti_slideshow_gate_intercepts_lens_formula_slide():
    """Verify that a static bulleted lens formula slide is converted into an animated ray diagram."""
    lens_slide = {
        "scene_order": 1,
        "visual_mode": "concept_highlight",
        "learning_objective": "Lens formula and magnification",
        "narration_text": "Rays parallel to principal axis refract through principal focus F2 according to the lens formula.",
        "visual_payload": {
            "template": "concept_highlight",
            "title": "Lens Formula",
            "steps": [
                "1/f = 1/v - 1/u",
                "m = v / u",
            ],
        },
    }

    result = audit_scene(lens_slide, concept="Refraction through Lenses")
    assert result.passed is True
    assert result.visual_mode == "optics_ray_diagram"
    assert result.repaired_scene["visual_mode"] == "optics_ray_diagram"


def test_spherical_mirror_renderer_creates_playable_mp4(tmp_path: Path):
    """Verify that the spherical mirror animation produces a valid playable video."""
    out_file = tmp_path / "test_spherical_mirror_unit.mp4"
    render_spherical_mirror_optics(
        {
            "title": "Spherical Mirror Geometry & Formula",
            "formula": "1/v + 1/u = 1/f",
            "radius": "20 cm",
            "focal_length": "10 cm",
        },
        duration_seconds=2.0,
        out_path=out_file,
    )

    assert out_file.exists()
    assert out_file.stat().st_size > 10_000
    require_playable_video(str(out_file), min_duration_seconds=1.5)


def test_optics_ray_diagram_renderer_creates_playable_mp4(tmp_path: Path):
    """Verify that the optics ray diagram produces a valid playable video."""
    out_file = tmp_path / "test_optics_ray_unit.mp4"
    render_optics_ray_diagram(
        {
            "optical_element": "convex_lens",
            "focal_length": 10.0,
            "object_distance": 20.0,
            "object_height": 5.0,
            "image_distance": 20.0,
            "image_height": -5.0,
            "image_nature": "Real, Inverted, Same Size",
            "formula": "1/f = 1/v - 1/u",
            "key_observation": "Rays parallel to principal axis refract through principal focus F2",
        },
        duration_seconds=2.0,
        out_path=out_file,
    )

    assert out_file.exists()
    assert out_file.stat().st_size > 10_000
    require_playable_video(str(out_file), min_duration_seconds=1.5)
