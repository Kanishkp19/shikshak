"""
Shikshak AI — Execution Plan builder.

Given a CreateSessionRequest, returns the ordered sequence of agent calls
(both sequential via celery.chain and parallel via celery.group) that
need to run to turn the request into a session with segments + checkpoints.

This module is pure — it returns DAG descriptors; the actual execution is
done by orchestrator/router.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class Step:
    """One step of the execution DAG."""
    agent: str
    args: dict[str, Any]
    depends_on: list[str] = field(default_factory=list)  # names of upstream steps
    parallel_group: Optional[str] = None  # set if part of a parallel batch


def build_execution_plan(
    *,
    session_id: str,
    student_id: str,
    source_type: str,
    document_id: Optional[str],
    topic: Optional[str],
    level: str,
    language: str,
    time_budget_minutes: int,
    weak_concepts: list[str],
) -> list[Step]:
    """Return the ordered list of Steps for the orchestrator to dispatch.

    The DAG (per AI-TEACHER-AGENT-ARCHITECTURE.md Section 5) is:

      1. (document only) content_ingestion
      2. knowledge_retrieval        (depends on 1)
      3. lesson_planning            (depends on 2)
      4. personalization            (depends on 3)
      5. time_budgeting              (depends on 4)
      6. visual_selection           (depends on 5)
      7. language                    (depends on 6, only if language != 'en')
      8. explanation                 (depends on 7) — parallel per segment
      9. qa_grounding_guard         (depends on 8, document-only) — parallel per segment
     10. interaction                (depends on 9) — parallel per checkpoint segment
     11. (later) voice/avatar/animation/compositing — triggered by /segments/{id}/render
    """
    steps: list[Step] = []
    has_source = source_type == "document" and bool(document_id)

    if has_source:
        steps.append(Step(
            agent="content_ingestion",
            args={"document_id": document_id},
        ))

    steps.append(Step(
        agent="knowledge_retrieval",
        args={
            "query": topic or "main topics and key concepts",
            "document_id": document_id if has_source else None,
        },
        depends_on=["content_ingestion"] if has_source else [],
    ))

    steps.append(Step(
        agent="lesson_planning",
        args={
            "topic": topic or "",
            "level": level,
            "time_budget_minutes": time_budget_minutes,
            "language": language,
            "has_source": has_source,
            "weak_concepts": weak_concepts,
            "document_id": document_id if has_source else None,
        },
        depends_on=["knowledge_retrieval"],
    ))

    steps.append(Step(
        agent="personalization",
        args={"level": level, "weak_concepts": weak_concepts},
        depends_on=["lesson_planning"],
    ))

    steps.append(Step(
        agent="time_budgeting",
        args={"time_budget_minutes": time_budget_minutes},
        depends_on=["personalization"],
    ))

    steps.append(Step(
        agent="visual_selection",
        args={},
        depends_on=["time_budgeting"],
    ))

    if language and language != "en":
        steps.append(Step(
            agent="language",
            args={"target_language": language, "current_language": "en"},
            depends_on=["visual_selection"],
        ))
        explanation_dep = "language"
    else:
        explanation_dep = "visual_selection"

    # Per-segment explanation (parallel across segments)
    steps.append(Step(
        agent="explanation",
        args={"parallel_per": "segment"},
        depends_on=[explanation_dep],
        parallel_group="explanation",
    ))

    if has_source:
        steps.append(Step(
            agent="qa_grounding_guard",
            args={"parallel_per": "segment"},
            depends_on=["explanation"],
            parallel_group="qa_guard",
        ))
        interaction_dep = "qa_grounding_guard"
    else:
        interaction_dep = "explanation"

    # Per-checkpoint question generation (parallel across checkpoint segments)
    steps.append(Step(
        agent="interaction",
        args={"parallel_per": "checkpoint_segment"},
        depends_on=[interaction_dep],
        parallel_group="interaction",
    ))

    return steps
