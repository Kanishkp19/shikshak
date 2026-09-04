"""
Shikshak AI — Interaction Agent.

Single responsibility: generate checkpoint questions for segments flagged
with has_checkpoint=true. When a segment covers multiple candidate concepts,
uses weakness_priority() from mastery_scoring to prioritize the concept
with the highest remediation need.
"""
from __future__ import annotations

import logging
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

from celery_app import celery_app
from agents.llm import get_content_llm as get_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.mastery_scoring import weakness_priority
from skills.prompt_templating import QUESTION_TEMPLATE, SYSTEM_TEACHER
from skills.supabase_persistence import (
    get_concept_mastery,
    insert_checkpoint,
    log_agent_run,
)

logger = logging.getLogger(__name__)


class QuestionObject(BaseModel):
    type: Literal["mcq", "short_answer", "conceptual"]
    prompt: str
    options: Optional[list[str]] = None
    correct_answer: str
    expected_reasoning: str = Field(default="")


def select_checkpoint_concept(
    concept: str,
    candidate_concepts: Optional[list[str]] = None,
    student_id: Optional[str] = None,
) -> str:
    """Decide which concept to test using weakness_priority when multiple candidates exist."""
    candidates = list(candidate_concepts or [])
    if not candidates:
        if "," in concept:
            candidates = [c.strip() for c in concept.split(",") if c.strip()]
        elif ";" in concept:
            candidates = [c.strip() for c in concept.split(";") if c.strip()]
        else:
            candidates = [concept.strip()]

    if len(candidates) <= 1:
        return candidates[0] if candidates else concept

    best_concept = candidates[0]
    best_priority = -999.0

    for c in candidates:
        score = 0.5
        attempts = 0
        if student_id:
            try:
                record = get_concept_mastery(student_id, c)
                if record:
                    score = float(record.get("score", 0.5))
                    attempts = int(record.get("attempts", 0))
            except Exception:
                pass
        p = weakness_priority(score, attempts)
        if p > best_priority:
            best_priority = p
            best_concept = c

    return best_concept


def generate_checkpoint(
    *,
    segment_id: str,
    concept: str,
    level: str,
    language: str,
    candidate_concepts: Optional[list[str]] = None,
    student_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    """Return a persisted checkpoint row for the segment."""
    target_concept = select_checkpoint_concept(
        concept=concept,
        candidate_concepts=candidate_concepts,
        student_id=student_id,
    )

    prompt = SYSTEM_TEACHER.render() + "\n\n" + QUESTION_TEMPLATE.render(
        concept=target_concept, level=level, language=language
    )
    llm = get_llm()
    try:
        q = call_llm_with_retry(llm, prompt, QuestionObject, model_name="interaction")
    except Exception as e:
        logger.warning("[interaction] LLM call failed (%s); using fallback question", e)
        q = QuestionObject(
            type="conceptual",
            prompt=f"In your own words, summarize the main mechanism or significance of {target_concept}.",
            correct_answer=f"An accurate explanation identifies the key concepts and mechanisms of {target_concept}.",
            expected_reasoning=f"Verifies conceptual understanding of {target_concept}.",
        )

    row = insert_checkpoint(
        segment_id=segment_id,
        question_type=q.type,
        prompt=q.prompt,
        options=q.options,
        correct_answer=q.correct_answer,
    )

    try:
        log_agent_run(
            session_id=session_id,
            agent_name="interaction",
            input_summary={
                "segment_id": segment_id,
                "input_concept": concept,
                "target_concept": target_concept,
            },
            output_summary={
                "question_type": q.type,
                "prompt_preview": q.prompt[:80],
            },
            status="success",
        )
    except Exception as e:
        logger.warning("[interaction] Could not log agent run: %s", e)

    return row


@celery_app.task(name="agents.interaction.run")
def run(
    segment_id: str,
    concept: str,
    level: str,
    language: str,
    candidate_concepts: Optional[list[str]] = None,
    student_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    return generate_checkpoint(
        segment_id=segment_id,
        concept=concept,
        level=level,
        language=language,
        candidate_concepts=candidate_concepts,
        student_id=student_id,
        session_id=session_id,
    )
