"""
Unit tests for the educational image generation engine.
"""
from pathlib import Path
import tempfile
from PIL import Image
import pytest

from skills.image_generation.cache import ImageCache, compute_cache_key
from skills.image_generation.prompt_engineer import build_educational_prompt
from skills.image_generation.generator import (
    create_fallback_chalkboard_canvas,
    generate_educational_image,
)


def test_prompt_engineer_filters_forbidden_vocabulary():
    prompt_res = build_educational_prompt(
        concept="Chemical Equilibrium and Le Chatelier Principle",
        visual_objective="Demonstrate dynamic equilibrium",
        entities=["balance_scale", "reactants", "products", "weighing scale"],
        forbidden_terms=["balance_scale", "weighing_scale"],
        style="educational_illustration",
    )
    # The forbidden terms must not appear in the entities list
    for ent in prompt_res.entities:
        assert "balance_scale" not in ent.lower()
        assert "weighing scale" not in ent.lower()

    assert "reactants" in prompt_res.entities
    assert "products" in prompt_res.entities
    assert prompt_res.seed is not None
    assert "no decorative balance scales" in prompt_res.prompt.lower()


def test_prompt_engineer_styles():
    for style in ["realistic_photo", "schematic_diagram", "infographic", "educational_illustration"]:
        res = build_educational_prompt(
            concept="Tectonic Plate Boundaries",
            visual_objective="Subduction zone mechanics",
            entities=["Lithosphere", "Asthenosphere", "Oceanic Trench"],
            style=style,  # type: ignore
        )
        assert res.style == style
        assert len(res.prompt) > 50


def test_image_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ImageCache(cache_dir=Path(tmpdir))
        key = compute_cache_key("test prompt", seed=42)

        # Initially empty
        assert cache.get(key) is None

        # Store dummy png bytes (> 500 bytes)
        fake_png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 600
        stored_path = cache.store(key, fake_png_data)
        assert stored_path.exists()

        # Cache hit
        cached = cache.get(key)
        assert cached is not None
        assert cached.read_bytes() == fake_png_data


def test_fallback_chalkboard_canvas_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_chalkboard.png"
        create_fallback_chalkboard_canvas(
            img_path=out_path,
            concept="Newton's Law of Universal Gravitation",
            entities=["Mass m1", "Mass m2", "Distance r", "Gravitational Constant G"],
            objective="Analyze gravitational attraction between point masses",
            width=1280,
            height=720,
        )

        assert out_path.exists()
        assert out_path.stat().st_size > 5000

        with Image.open(out_path) as im:
            assert im.size == (1280, 720)
            assert im.format == "PNG"


def test_generate_educational_image_offline_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "generated.png"
        cache = ImageCache(cache_dir=Path(tmpdir) / "cache")

        # Calling with invalid / offline-safe parameters
        result_path = generate_educational_image(
            concept="Photosynthesis Light Reactions",
            visual_objective="Photon excitation in Chlorophyll",
            entities=["Thylakoid", "Photon", "ATP Synthase"],
            out_path=out_path,
            cache=cache,
        )

        assert result_path.exists()
        assert result_path.stat().st_size > 1000
        with Image.open(result_path) as im:
            assert im.size == (1280, 720)
