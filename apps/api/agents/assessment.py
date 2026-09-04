"""
Shikshak AI — Assessment Agent.

Single responsibility: at the end of a session, compute a score from the
student's checkpoint answers, derive strong/weak areas from which concepts
had correct vs. incorrect answers, generate a recommendation, and upsert
the report to the `assessment_reports` table.

Orders weak_areas descending by weakness_priority() so recommendations
focus on the highest-urgency remediation needs first.
"""
from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel, Field

from celery_app import celery_app
from agents.llm import get_content_llm as get_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.mastery_scoring import weakness_priority
from skills.prompt_templating import ASSESSMENT_REPORT_TEMPLATE, SYSTEM_TEACHER
from skills.supabase_persistence import (
    get_client,
    get_concept_mastery,
    list_checkpoints_for_session,
    list_segments,
    log_agent_run,
    upsert_report,
)

logger = logging.getLogger(__name__)


class AssessmentPlan(BaseModel):
    score: float = 0.0
    strong_areas: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    recommendation: str = "Review the lesson material and try again."


def order_weak_areas_by_priority(
    weak_areas: list[str],
    checkpoints: list[dict],
    student_id: str | None = None,
) -> list[str]:
    """Sort weak_areas descending by weakness_priority (highest remediation need first)."""
    if not weak_areas:
        return []

    # Map checkpoints by concept
    cp_by_concept: dict[str, list[dict]] = {}
    for c in checkpoints:
        concept_name = (c.get("concept") or "").strip().lower()
        if concept_name:
            cp_by_concept.setdefault(concept_name, []).append(c)

    scored_areas: list[tuple[str, float]] = []
    for area in weak_areas:
        area_clean = area.strip()
        area_lower = area_clean.lower()
        score = 0.3
        attempts = 1

        # Check if mastery table has historical stats
        if student_id:
            try:
                rec = get_concept_mastery(student_id, area_clean)
                if rec:
                    score = float(rec.get("score", 0.3))
                    attempts = int(rec.get("attempts", 1))
            except Exception:
                pass
        # If not found in mastery table, derive from current session checkpoints
        if area_lower in cp_by_concept:
            matching_cps = cp_by_concept[area_lower]
            wrong_count = sum(1 for cp in matching_cps if not cp.get("is_correct"))
            total_count = len(matching_cps)
            score = (total_count - wrong_count) / max(1, total_count)
            attempts = max(attempts, wrong_count)

        p = weakness_priority(score, attempts)
        scored_areas.append((area_clean, p))

    # Sort descending by priority score
    scored_areas.sort(key=lambda x: x[1], reverse=True)
    return [area for area, _ in scored_areas]


def assess_session(*, session_id: str) -> dict[str, Any]:
    """Produce and persist the assessment report for `session_id`."""
    segments = list_segments(session_id)
    checkpoints = list_checkpoints_for_session(session_id)

    # Resolve student_id for mastery prioritization
    student_id = None
    try:
        sess_res = get_client().table("sessions").select("student_id").eq("id", session_id).execute()
        if sess_res.data:
            student_id = sess_res.data[0].get("student_id")
    except Exception as e:
        logger.warning("[assessment] Could not resolve student_id for session %s: %s", session_id, e)

    # Heuristic score: % of checkpoints with is_correct=True
    n_total = len(checkpoints)
    n_correct = sum(1 for c in checkpoints if c.get("is_correct"))
    heuristic_score = (n_correct / n_total * 100.0) if n_total else 0.0

    # Build a textual summary for the LLM
    segments_taught = "\n".join(
        f"- Segment {s['segment_order']}: {s.get('concept', '')}"
        for s in segments
    )
    answers_summary = "\n".join(
        f"- Q: {(c.get('prompt') or '')[:120]} | student: {(c.get('student_answer') or '')[:120]} | "
        f"correct: {c.get('is_correct')}"
        for c in checkpoints
    )

    prompt = SYSTEM_TEACHER.render() + "\n\n" + ASSESSMENT_REPORT_TEMPLATE.render(
        segments_taught=segments_taught or "(none)",
        answers_summary=answers_summary or "(none)",
    )
    llm = get_llm()

    # Graceful fallback: if the LLM fails schema validation, use heuristic score
    try:
        plan = call_llm_with_retry(llm, prompt, AssessmentPlan, model_name="assessment")
    except ValueError as e:
        logger.warning("[assessment] LLM failed, falling back to heuristic: %s", e)
        plan = AssessmentPlan(
            score=heuristic_score,
            strong_areas=[],
            weak_areas=[s.get("concept", "") for s in segments if s.get("concept")][:3],
            recommendation="The AI assessment could not be generated. Score is based on checkpoint answers only.",
        )

    # Blend heuristic score with LLM score (50/50)
    final_score = round((plan.score + heuristic_score) / 2, 2)

    # Order weak areas by weakness_priority descending
    ordered_weak_areas = order_weak_areas_by_priority(
        weak_areas=plan.weak_areas,
        checkpoints=checkpoints,
        student_id=student_id,
    )

    row = upsert_report(
        session_id=session_id,
        score=final_score,
        strong_areas=plan.strong_areas,
        weak_areas=ordered_weak_areas,
        recommendation=plan.recommendation,
    )

    try:
        log_agent_run(
            session_id=session_id,
            agent_name="assessment",
            input_summary={
                "checkpoints_count": n_total,
                "correct_count": n_correct,
            },
            output_summary={
                "final_score": final_score,
                "ordered_weak_areas": ordered_weak_areas,
                "strong_areas_count": len(plan.strong_areas),
            },
            status="success",
        )
    except Exception as e:
        logger.warning("[assessment] Could not write agent_run_log: %s", e)

    return row


@celery_app.task(name="agents.assessment.run")
def run(session_id: str) -> dict[str, Any]:
    return assess_session(session_id=session_id)
