"""
Shikshak AI — Time Budgeting Agent.

Single responsibility: ensure the lesson plan fits the student's time budget.
Truncates or expands segments to stay within the budget at ~120 wpm narration.
For 5-min budgets it returns 1-2 segments; for 20-min it returns 4-6; for 60-min
it returns 10-15 with assessment checkpoints; for 7-day plans it kicks off a
learning path instead (handled by a different agent — here we just truncate to
a single overview segment).
"""
from __future__ import annotations

from typing import Any

from celery_app import celery_app


# Roughly: target_narration_words = time_budget_minutes * 120
# Segment count = total_words / per_segment_words (where per_segment ≈ 200 words)
def budget_segments(
    *,
    plan: dict[str, Any],
    time_budget_minutes: int,
) -> dict[str, Any]:
    segments = plan.get("segments", [])
    if not segments:
        return plan

    # 7-day "plan mode" — collapse to a single overview segment
    if time_budget_minutes > 60 * 24 * 6:  # ~6 days
        overview = segments[0]
        overview["concept"] = f"Overview of {plan.get('topic', 'this topic')}"
        overview["depth"] = plan.get("level", "intermediate")
        overview["has_checkpoint"] = False
        plan = dict(plan)
        plan["segments"] = [overview]
        plan["is_path_mode"] = True
        return plan

    # For document mode: DO NOT truncate the chapter's topics!
    # When a student uploads a PDF, every concept extracted from the textbook
    # must be available in the chapter curriculum roadmap.
    is_doc = bool(
        plan.get("document_id")
        or plan.get("is_document_mode")
        or any(s.get("source_text") for s in segments)
    )
    if is_doc:
        # Scale word budget per segment based on time budget, but keep ALL topics
        per_seg_words = max(160, min(280, (time_budget_minutes * 120) // max(1, len(segments))))
        plan = dict(plan)
        plan["per_segment_words"] = per_seg_words
        return plan

    # Per-segment target word count (for topic-only mode)
    if time_budget_minutes <= 5:
        per_seg_words = 80
        max_segments = 2
    elif time_budget_minutes <= 20:
        per_seg_words = 200
        max_segments = 6
    elif time_budget_minutes <= 60:
        per_seg_words = 220
        max_segments = 15
    else:
        per_seg_words = 250
        max_segments = 20

    total_budget_words = time_budget_minutes * 120
    n_segments = max(1, min(max_segments, total_budget_words // per_seg_words))

    # Truncate (preserve at least one checkpoint if any was set)
    if len(segments) > n_segments:
        truncated = segments[:n_segments]
        # Ensure last segment keeps a checkpoint flag if original had any
        if any(s.get("has_checkpoint") for s in segments):
            truncated[-1]["has_checkpoint"] = True
        segments = truncated

    plan = dict(plan)
    plan["segments"] = segments
    plan["per_segment_words"] = per_seg_words
    return plan


@celery_app.task(name="agents.time_budgeting.run")
def run(plan: dict[str, Any], time_budget_minutes: int) -> dict[str, Any]:
    return budget_segments(plan=plan, time_budget_minutes=time_budget_minutes)
