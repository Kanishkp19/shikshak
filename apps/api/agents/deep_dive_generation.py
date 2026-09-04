"""
Shikshak AI — Deep Dive Generation Agent.

Single responsibility: when the user clicks "Next" and selects (or auto-picks)
a related concept, generate a fresh segment for that concept on demand.

This agent:
  1. Takes the selected concept + session context
  2. Generates a narration script via the Explanation agent
  3. Returns the segment data ready for rendering
"""
from __future__ import annotations

from typing import Any, Optional

from celery_app import celery_app
from agents import explanation as a_expl
from skills.supabase_persistence import insert_segments, list_segments


def generate_deep_dive(
    *,
    session_id: str,
    concept: str,
    level: str,
    language: str,
    parent_segment_order: int,
) -> dict[str, Any]:
    """Generate a deep-dive segment for the given concept.

    Returns a segment dict with narration_script populated, ready for rendering.
    """
    # Determine the next order number
    existing = list_segments(session_id)
    next_order = max((s["segment_order"] for s in existing), default=0) + 1

    # Generate narration for the deep-dive concept
    narration = a_expl.explain_segment(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=None,  # Deep dives use LLM knowledge, not source docs
        per_segment_words=200,
    )

    # Build segment data
    segment_data = {
        "session_id": session_id,
        "segment_order": next_order,
        "concept": concept,
        "depth": level,
        "visual_type": "diagram",  # Default to diagram for deep dives
        "narration_script": narration,
        "has_checkpoint": False,
        "status": "pending",
    }

    # Persist to database
    inserted = insert_segments([segment_data])
    db_id = inserted[0]["id"] if inserted else None

    return {
        "id": db_id,
        "order": next_order,
        "concept": concept,
        "depth": level,
        "visual_type": "diagram",
        "narration_script": narration,
        "has_checkpoint": False,
        "segment_type": "deep_dive",
        "related_concepts": [],  # Could be populated by another LLM call
        "status": "pending",
    }


@celery_app.task(name="agents.deep_dive_generation.run")
def run(
    session_id: str,
    concept: str,
    level: str,
    language: str,
    parent_segment_order: int,
) -> dict[str, Any]:
    return generate_deep_dive(
        session_id=session_id,
        concept=concept,
        level=level,
        language=language,
        parent_segment_order=parent_segment_order,
    )
