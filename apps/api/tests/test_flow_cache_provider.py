"""
Unit and integration tests for Flow Cache video generation provider and fallback chain.
"""
from __future__ import annotations

import inspect
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import agents.concept_animation as concept_animation
from scripts.populate_video_cache import populate_video_cache
from skills.caching import build_cache_prompt, hash_prompt
from skills.video_generation import (
    FlowCacheProvider,
    ManimProvider,
    VideoGenerationError,
    VideoGenerationRequest,
    VideoGenerationResult,
    VisualBrief,
    generate_with_fallback,
)
from skills.video_generation.factory import _build_chain


class MockSupabaseClient:
    def __init__(self):
        self.rows: dict[str, dict] = {}
        self.storage_files: dict[str, bytes] = {}
        self.storage_mock = SimpleNamespace(
            from_=self._from_bucket
        )
        self.storage = self.storage_mock

    def _from_bucket(self, bucket: str):
        outer = self

        class BucketMock:
            def upload(self, path: str, file: bytes, file_options: dict = None):
                outer.storage_files[f"{bucket}/{path}"] = file
                return {"path": path}

            def get_public_url(self, path: str) -> str:
                return f"https://example.supabase.co/storage/v1/object/public/{bucket}/{path}"

        return BucketMock()

    def table(self, table_name: str):
        outer = self

        class TableMock:
            def __init__(self):
                self.selected = "*"
                self.filters = {}
                self._limit = None

            def select(self, fields: str):
                self.selected = fields
                return self

            def eq(self, col: str, val: Any):
                self.filters[col] = val
                return self

            def limit(self, count: int):
                self._limit = count
                return self

            def execute(self):
                data = []
                for row in outer.rows.values():
                    match = True
                    for col, val in self.filters.items():
                        if row.get(col) != val:
                            match = False
                            break
                    if match:
                        data.append(row)
                if self._limit is not None:
                    data = data[: self._limit]
                return SimpleNamespace(data=data)

            def upsert(self, row: dict, on_conflict: str = None):
                key = row.get(on_conflict) if on_conflict else row.get("id")
                outer.rows[key] = row

                class ExecMock:
                    def execute(self):
                        return SimpleNamespace(data=[row])

                return ExecMock()

        return TableMock()


def test_hash_prompt_determinism_and_uniqueness():
    """Verify hash_prompt returns stable, normalized SHA-256 hashes."""
    h1 = hash_prompt("Photosynthesis", "animation", "beginner", "en")
    h2 = hash_prompt("  photosynthesis ", "ANIMATION", "Beginner", "EN")
    assert h1 == h2
    assert len(h1) == 64

    h_diff_concept = hash_prompt("Respiration", "animation", "beginner", "en")
    assert h_diff_concept != h1

    h_diff_type = hash_prompt("Photosynthesis", "diagram", "beginner", "en")
    assert h_diff_type != h1

    h_diff_depth = hash_prompt("Photosynthesis", "animation", "advanced", "en")
    assert h_diff_depth != h1

    h_diff_lang = hash_prompt("Photosynthesis", "animation", "beginner", "hi")
    assert h_diff_lang != h1


def test_flow_cache_provider_miss_raises_typed_error():
    """Calling FlowCacheProvider.generate for an unregistered concept raises VideoGenerationError."""
    mock_client = MockSupabaseClient()
    provider = FlowCacheProvider(client=mock_client)

    request = VideoGenerationRequest(
        segment_id="seg-1",
        concept="Unregistered Concept",
        visual_type="animation",
        depth="beginner",
        language="en",
    )

    with pytest.raises(VideoGenerationError) as exc_info:
        provider.generate(request)

    assert exc_info.value.provider == "flow_cache"
    assert "Unregistered Concept" in exc_info.value.reason
    assert "populate_video_cache.py" in exc_info.value.reason


def test_flow_cache_provider_hit_returns_result():
    """Calling FlowCacheProvider.generate for a registered concept returns a valid VideoGenerationResult."""
    mock_client = MockSupabaseClient()
    prompt_hash = hash_prompt("Photosynthesis", "animation", "beginner", "en")
    mock_client.rows[prompt_hash] = {
        "id": "uuid-1234",
        "prompt_hash": prompt_hash,
        "provider": "flow_cache",
        "storage_path": f"flow_cache/{prompt_hash}.mp4",
    }

    provider = FlowCacheProvider(client=mock_client)
    request = VideoGenerationRequest(
        segment_id="seg-1",
        concept="Photosynthesis",
        visual_type="animation",
        depth="beginner",
        language="en",
    )

    result = provider.generate(request)
    assert isinstance(result, VideoGenerationResult)
    assert result.cache_hit is True
    assert result.provider == "flow_cache"
    assert result.video_cache_id == "uuid-1234"
    assert "flow_cache/" in result.video_url


def test_populate_video_cache_updates_row_without_duplicate(tmp_path):
    """Running populate_video_cache twice updates existing prompt_hash row."""
    mock_client = MockSupabaseClient()
    video_file_1 = tmp_path / "clip1.mp4"
    video_file_1.write_bytes(b"dummy mp4 content 1")

    video_file_2 = tmp_path / "clip2.mp4"
    video_file_2.write_bytes(b"dummy mp4 content 2 updated")

    res1 = populate_video_cache(
        file_path=video_file_1,
        concept="Cell Division",
        visual_type="diagram",
        depth="intermediate",
        language="en",
        client=mock_client,
    )
    prompt_hash = res1["prompt_hash"]
    assert len(mock_client.rows) == 1
    assert prompt_hash in mock_client.rows

    # Register updated clip for same concept
    res2 = populate_video_cache(
        file_path=video_file_2,
        concept="Cell Division",
        visual_type="diagram",
        depth="intermediate",
        language="en",
        client=mock_client,
    )
    assert res2["prompt_hash"] == prompt_hash
    # Row count remains 1 (updated, not duplicated)
    assert len(mock_client.rows) == 1
    # Storage content was updated
    storage_key = f"videos/{res2['storage_path']}"
    assert mock_client.storage_files[storage_key] == b"dummy mp4 content 2 updated"


def test_generate_with_fallback_cache_hit_bypasses_manim(monkeypatch):
    """When a cache hit occurs, generate_with_fallback returns cache hit immediately."""
    mock_client = MockSupabaseClient()
    prompt_hash = hash_prompt("Cell Division", "diagram", "intermediate", "en")
    mock_client.rows[prompt_hash] = {
        "id": "uuid-5678",
        "prompt_hash": prompt_hash,
        "provider": "flow_cache",
        "storage_path": f"flow_cache/{prompt_hash}.mp4",
    }

    flow_provider = FlowCacheProvider(client=mock_client)
    manim_mock = MagicMock(spec=ManimProvider)
    manim_mock.name = "manim"
    manim_mock.is_available.return_value = True

    monkeypatch.setattr(
        "skills.video_generation.factory._build_chain",
        lambda: [flow_provider, manim_mock],
    )

    request = VideoGenerationRequest(
        segment_id="seg-1",
        concept="Cell Division",
        visual_type="diagram",
        depth="intermediate",
        language="en",
    )

    result = generate_with_fallback(request)
    assert result.cache_hit is True
    assert result.provider == "flow_cache"
    manim_mock.generate.assert_not_called()


def test_generate_with_fallback_miss_falls_through_to_manim(monkeypatch, tmp_path):
    """When flow_cache misses, generate_with_fallback falls through to ManimProvider without failing."""
    mock_client = MockSupabaseClient()  # Empty cache
    flow_provider = FlowCacheProvider(client=mock_client)

    manim_provider = ManimProvider()
    monkeypatch.setattr(
        "skills.video_generation.factory._build_chain",
        lambda: [flow_provider, manim_provider],
    )

    out_file = tmp_path / "fallback_manim.mp4"
    request = VideoGenerationRequest(
        segment_id="seg-1",
        concept="Gravity",
        visual_type="animation",
        depth="beginner",
        language="en",
        out_path=out_file,
    )

    result = generate_with_fallback(request, out_path=out_file)
    assert result.provider == "manim"
    assert result.cache_hit is False
    assert Path(result.video_url).exists()


def test_enable_flow_cache_env_flag(monkeypatch):
    """Setting ENABLE_FLOW_CACHE=false causes _build_chain to omit FlowCacheProvider."""
    monkeypatch.setenv("ENABLE_FLOW_CACHE", "false")
    monkeypatch.setenv("VIDEO_PROVIDER", "manim")

    chain = _build_chain()
    provider_names = [p.name for p in chain]
    assert "flow_cache" not in provider_names
    assert provider_names == ["manim"]


def test_no_browser_automation_imports():
    """Verify that none of the video generation modules import browser automation tools."""
    forbidden = ["selenium", "playwright", "cdp", "puppeteer", "browser_subagent"]
    module_paths = [
        Path("skills/caching.py"),
        Path("skills/video_generation/base.py"),
        Path("skills/video_generation/flow_cache_provider.py"),
        Path("skills/video_generation/factory.py"),
        Path("scripts/populate_video_cache.py"),
        Path("agents/concept_animation.py"),
    ]

    for p in module_paths:
        full_path = Path(__file__).parent.parent / p
        content = full_path.read_text(encoding="utf-8").lower()
        for f in forbidden:
            assert f not in content, f"Forbidden browser automation keyword '{f}' found in {p}"


def test_concept_animation_agent_uses_factory_without_concrete_provider_imports():
    """Verify concept_animation.py does not import concrete providers directly."""
    agent_source = Path(__file__).parent.parent / "agents/concept_animation.py"
    source = agent_source.read_text(encoding="utf-8")
    assert "FlowCacheProvider" not in source
    assert "ManimProvider" not in source
    assert "DiagramProvider" not in source
    assert "CinematicProvider" not in source
    assert "generate_with_fallback" in source
