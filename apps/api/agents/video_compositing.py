"""
Shikshak AI — Video Compositing Agent.

Single responsibility: combine avatar + concept visuals (or scene sequence)
into one segment video, then optionally stitch all segments into the final lesson.
"""
from __future__ import annotations

from typing import Any
from celery_app import celery_app
from skills.video_stitching import (
    stitch_segment,
    stitch_scenes_into_segment,
    concat_segments,
)


def composite_segment(
    *,
    avatar_video_path: str,
    concept_video_path: str,
    audio_path: str | None = None,
    caption_text: str | None = None,
    language: str = "en",
) -> str:
    """Return the final per-segment video path from a single concept video."""
    return stitch_segment(
        avatar_video_path=avatar_video_path,
        concept_video_path=concept_video_path,
        audio_path=audio_path,
        caption_text=caption_text,
        language=language,
    )


def composite_scenes(
    *,
    scene_video_paths: list[str],
    audio_path: str | None = None,
    avatar_video_path: str | None = None,
    language: str = "en",
) -> str:
    """Return the final segment video composed from a sequence of rendered scenes."""
    return stitch_scenes_into_segment(
        scene_video_paths=scene_video_paths,
        audio_path=audio_path,
        avatar_video_path=avatar_video_path,
        language=language,
    )


def composite_lesson(*, segment_video_paths: list[str]) -> str:
    """Stitch all per-segment videos into one final lesson video."""
    return concat_segments(segment_video_paths)


@celery_app.task(name="agents.video_compositing.composite_segment")
def composite_segment_task(
    avatar_video_path: str,
    concept_video_path: str,
    audio_path: str | None = None,
    caption_text: str | None = None,
    language: str = "en",
) -> str:
    return composite_segment(
        avatar_video_path=avatar_video_path,
        concept_video_path=concept_video_path,
        audio_path=audio_path,
        caption_text=caption_text,
        language=language,
    )


@celery_app.task(name="agents.video_compositing.composite_scenes")
def composite_scenes_task(
    scene_video_paths: list[str],
    audio_path: str | None = None,
    avatar_video_path: str | None = None,
    language: str = "en",
) -> str:
    return composite_scenes(
        scene_video_paths=scene_video_paths,
        audio_path=audio_path,
        avatar_video_path=avatar_video_path,
        language=language,
    )


@celery_app.task(name="agents.video_compositing.composite_lesson")
def composite_lesson_task(segment_video_paths: list[str]) -> str:
    return composite_lesson(segment_video_paths=segment_video_paths)
