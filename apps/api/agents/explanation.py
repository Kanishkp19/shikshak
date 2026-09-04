"""
Shikshak AI — Explanation Agent (v2).

Uses the unified ContentBlueprint from content_scriptwriter to generate
BOTH narration AND animation spec in a single LLM call.

Single responsibility: given a segment brief + retrieved source chunks,
produce the final narration script (text only) AND the matching DiagramSpec.
"""
from __future__ import annotations

from typing import Any, Optional

from celery_app import celery_app
from agents.content_scriptwriter import generate_content_blueprint, ContentBlueprint


def explain_segment_with_blueprint(
    *,
    concept: str,
    level: str,
    language: str,
    retrieved_chunks: list[dict] | None,
    per_segment_words: int = 200,
) -> dict[str, Any]:
    """Return narration script AND diagram spec for one segment.

    Returns:
        dict with keys:
          - narration_script: str — the teacher's spoken words
          - diagram_spec: dict — the pre-computed DiagramSpec for animation
          - scenes: list[dict] — per-scene breakdown
    """
    chunks_text = _format_chunks(retrieved_chunks)

    # Generate unified blueprint (narration + animation together)
    blueprint = generate_content_blueprint(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=chunks_text,
        per_segment_words=per_segment_words,
    )

    narration = blueprint.full_narration_script
    narration = _truncate_to_word_target(narration, per_segment_words)

    # Convert diagram_spec to dict for storage
    diagram_spec = blueprint.diagram_spec.model_dump(mode="json")
    scenes = [s.model_dump(mode="json") for s in blueprint.scenes]

    return {
        "narration_script": narration,
        "diagram_spec": diagram_spec,
        "scenes": scenes,
    }


def explain_segment(
    *,
    concept: str,
    level: str,
    language: str,
    retrieved_chunks: list[dict] | None,
    per_segment_words: int = 200,
) -> str:
    """Return narration script string for backward compatibility.

    Used by callers that expect a string response (tests, qa guard, etc.).
    Internally uses the unified blueprint for quality.
    """
    result = explain_segment_with_blueprint(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=retrieved_chunks,
        per_segment_words=per_segment_words,
    )
    return result["narration_script"]


def explain_segment_narration_only(
    *,
    concept: str,
    level: str,
    language: str,
    retrieved_chunks: list[dict] | None,
    per_segment_words: int = 200,
) -> str:
    """Alias for explain_segment."""
    return explain_segment(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=retrieved_chunks,
        per_segment_words=per_segment_words,
    )


def _format_chunks(chunks: list[dict] | None) -> str:
    if not chunks:
        return (
            "[NO SOURCE MATERIAL AVAILABLE — produce a generic, well-known "
            "explanation of the concept and DO NOT cite any specific source.]"
        )
    out = []
    for i, c in enumerate(chunks, start=1):
        section = c.get("section_label") or c.get("page") or "?"
        out.append(f"[Source {i}, {section}]\n{c.get('content', '')}")
    return "\n\n".join(out)


def _truncate_to_word_target(text: str, target: int) -> str:
    words = text.split()
    if len(words) <= target * 1.2:
        return text.strip()
    return " ".join(words[:target]) + "..."


@celery_app.task(name="agents.explanation.run")
def run(
    concept: str,
    level: str,
    language: str,
    retrieved_chunks: Optional[list[dict]] = None,
    per_segment_words: int = 200,
) -> str:
    """Celery task — returns narration script only for backward compat."""
    return explain_segment(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=retrieved_chunks,
        per_segment_words=per_segment_words,
    )
