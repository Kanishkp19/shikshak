"""
Shikshak AI — Concept Animation Agent.

Single responsibility: take a segment's concept + visual_type and produce
a concept animation video clip. Always goes through
`skills.video_generation.factory.generate_with_fallback` — never calls a
provider's SDK directly (per 00-MASTER-PROMPT.md agent operating rules).

Now accepts an optional pre-computed diagram_spec from the content_scriptwriter.
When provided, the diagram provider skips LLM planning entirely — making
the animation render fully deterministic with zero network calls.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
import uuid

from celery_app import celery_app
from skills.video_generation.base import VideoGenerationRequest
from skills.video_generation.factory import generate_with_fallback


def animate_segment(
    *,
    concept: str,
    visual_type: str,
    narration_script: str,
    language: str = "en",
    depth: str = "beginner",
    segment_id: str = "",
    duration_seconds: float | None = None,
    diagram_spec: dict[str, Any] | None = None,
    scenes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return {video_path, video_url, provider, cache_hit, video_cache_id}.

    Args:
        concept: The topic being animated.
        visual_type: 'diagram' | 'equation' | 'code' | 'animation' | 'none'
        narration_script: The teacher's narration for this segment.
        language: BCP-47 language code.
        depth: 'beginner' | 'intermediate' | 'advanced'
        segment_id: ID of the lesson segment being animated.
        duration_seconds: How long the animation should last.
        diagram_spec: Pre-computed DiagramSpec from content_scriptwriter.
            When provided, eliminates all LLM calls from the render path.
        scenes: Per-scene breakdown for multi-scene animation (future use).
    """
    out_path = Path("/tmp/shikshak_concept") / f"concept_{uuid.uuid4().hex}.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    request = VideoGenerationRequest(
        segment_id=segment_id,
        concept=concept,
        narration_script=narration_script,
        visual_type=visual_type,
        depth=depth,
        language=language,
        duration_seconds=max(5.0, min(90.0, float(round(duration_seconds or 15)))),
        diagram_spec=diagram_spec,
        scenes=scenes,
        out_path=out_path,
        extra_params={
            "duration_seconds": duration_seconds,
            "diagram_spec": diagram_spec,
            "scenes": scenes,
        },
    )

    result = generate_with_fallback(request, out_path)
    if isinstance(result, tuple):
        video_path, provider = result
        return {
            "video_path": str(video_path),
            "video_url": str(video_path),
            "provider": str(provider),
            "cache_hit": False,
            "video_cache_id": None,
        }

    return {
        "video_path": result.video_url,
        "video_url": result.video_url,
        "provider": result.provider,
        "cache_hit": result.cache_hit,
        "video_cache_id": result.video_cache_id,
    }


@celery_app.task(name="agents.concept_animation.run")
def run(
    concept: str,
    visual_type: str,
    narration_script: str,
    language: str = "en",
    depth: str = "beginner",
    segment_id: str = "",
    duration_seconds: float | None = None,
    diagram_spec: dict[str, Any] | None = None,
    scenes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return animate_segment(
        concept=concept,
        visual_type=visual_type,
        narration_script=narration_script,
        language=language,
        depth=depth,
        segment_id=segment_id,
        duration_seconds=duration_seconds,
        diagram_spec=diagram_spec,
        scenes=scenes,
    )
