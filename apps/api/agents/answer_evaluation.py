"""
Shikshak AI — Answer Evaluation Agent.

Single responsibility: given a checkpoint row + the student's submitted
answer, return {is_correct, misconception_seed} and update the student's
continuous concept mastery score in concept_mastery via blend_score (alpha=0.4).

Grades at explicit temperature=0.1 (TEMPERATURE_EVALUATION) for maximum consistency.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from celery_app import celery_app
from agents.llm import get_content_llm as get_llm
from config import settings
from skills.mastery_scoring import update_mastery_record
from skills.prompt_templating import TEMPERATURE_EVALUATION
from skills.supabase_persistence import (
    get_checkpoint,
    get_client,
    get_concept_mastery,
    log_agent_run,
    update_checkpoint,
    upsert_concept_mastery,
)

logger = logging.getLogger(__name__)


def evaluate_answer(
    *,
    checkpoint_id: str,
    student_answer: str,
    student_id: Optional[str] = None,
) -> dict[str, Any]:
    """Grade a student's answer against the checkpoint's correct answer and update concept mastery."""
    cp = get_checkpoint(checkpoint_id)
    if not cp:
        raise ValueError(f"Checkpoint {checkpoint_id} not found")

    is_correct = _grade(cp, student_answer)

    # Persist student answer and evaluation to checkpoint
    update_checkpoint(
        checkpoint_id,
        {
            "student_answer": student_answer,
            "is_correct": is_correct,
        },
    )

    # Resolve concept, session_id, and student_id
    concept = cp.get("concept") or ""
    resolved_student_id = student_id
    session_id = None

    if cp.get("segment_id"):
        try:
            client = get_client()
            seg_res = client.table("lesson_segments").select("concept, session_id").eq("id", cp["segment_id"]).execute()
            if seg_res.data:
                seg = seg_res.data[0]
                if not concept:
                    concept = seg.get("concept") or ""
                session_id = seg.get("session_id")
                if not resolved_student_id and session_id:
                    sess_res = client.table("sessions").select("student_id").eq("id", session_id).execute()
                    if sess_res.data:
                        resolved_student_id = sess_res.data[0].get("student_id")
        except Exception as e:
            logger.warning("[answer_evaluation] Could not resolve segment/session/student context: %s", e)

    # Continuous Mastery Scoring UPSERT
    mastery_info = None
    if resolved_student_id and concept:
        try:
            current_score = 1.0 if is_correct else 0.0
            existing_record = get_concept_mastery(resolved_student_id, concept)
            old_score = float(existing_record["score"]) if existing_record and "score" in existing_record else 0.0
            old_attempts = int(existing_record["attempts"]) if existing_record and "attempts" in existing_record else 0
            old_consecutive = int(existing_record["consecutive_strong"]) if existing_record and "consecutive_strong" in existing_record else 0

            updated = update_mastery_record(
                old_score=old_score,
                new_grade=current_score,
                old_attempts=old_attempts,
                old_consecutive_strong=old_consecutive,
                alpha=0.4,
            )
            upsert_concept_mastery(
                student_id=resolved_student_id,
                concept=concept,
                score=float(updated["score"]),
                status=str(updated["status"]),
                attempts=int(updated["attempts"]),
                consecutive_strong=int(updated["consecutive_strong"]),
            )
            mastery_info = updated
        except Exception as e:
            logger.warning("[answer_evaluation] Failed to update concept_mastery for (%s, %s): %s", resolved_student_id, concept, e)

    # Log to agent_run_logs
    try:
        log_agent_run(
            session_id=session_id,
            agent_name="answer_evaluation",
            input_summary={
                "checkpoint_id": checkpoint_id,
                "student_answer": student_answer,
                "concept": concept,
            },
            output_summary={
                "is_correct": is_correct,
                "mastery_score": mastery_info["score"] if mastery_info else None,
                "mastery_status": mastery_info["status"] if mastery_info else None,
            },
            status="success",
        )
    except Exception as e:
        logger.warning("[answer_evaluation] Could not write agent_run_log: %s", e)

    return {
        "checkpoint_id": checkpoint_id,
        "is_correct": is_correct,
        "correct_answer": cp["correct_answer"],
        "student_answer": student_answer,
        "concept": concept,
        "segment_id": cp["segment_id"],
        "mastery": mastery_info,
    }


def _grade(checkpoint: dict, student_answer: str) -> bool:
    """Heuristic grader: case-insensitive match for MCQ (letter or value)
    and substring match for short-answer. For complex cases, ask the LLM at temperature=0.1."""
    correct = (checkpoint.get("correct_answer") or "").strip().lower()
    answer = student_answer.strip().lower()
    if not correct or not answer:
        return False
    # Exact match
    if correct == answer:
        return True
    # MCQ letter match (e.g. correct='a' and student='a' or 'a) The first option'
    if checkpoint.get("question_type") == "mcq":
        options = checkpoint.get("options") or []
        try:
            idx = ord(answer[0]) - ord("a")
            if 0 <= idx < len(options) and options[idx].strip().lower() == correct:
                return True
            # If the student picked the full correct option text
            if options and answer == correct:
                return True
        except Exception:
            pass
    # Short-answer / conceptual — let the LLM grade if available at explicit temperature=0.1
    if settings.gemini_api_key or settings.groq_api_key:
        try:
            llm = get_llm(temperature=TEMPERATURE_EVALUATION)
            prompt = (
                f"Grade the student's answer. Correct answer: '{checkpoint['correct_answer']}'. "
                f"Student answer: '{student_answer}'. "
                "Return JSON: {\"is_correct\": true|false}. Be strict about factual correctness."
            )
            verdict = llm(prompt)
            data = json.loads(verdict.strip())
            return bool(data.get("is_correct", False))
        except Exception:
            pass
    # Fallback: substring match in either direction
    return correct in answer or answer in correct


@celery_app.task(name="agents.answer_evaluation.run")
def run(
    checkpoint_id: str,
    student_answer: str,
    student_id: Optional[str] = None,
) -> dict[str, Any]:
    return evaluate_answer(
        checkpoint_id=checkpoint_id,
        student_answer=student_answer,
        student_id=student_id,
    )
