"""
Shikshak AI — Personalization Agent.

Single responsibility: given a lesson plan and the student's level +
prior weak concepts, rewrite the per-segment depth tags to match
the level and inject any weak-concept remediation segments at the start.

Inputs:  plan (dict from Lesson Planning Agent), level, weak_concepts
Outputs: plan (same shape, depths adjusted, remediation segments prepended)
"""
from __future__ import annotations

from typing import Any

from celery_app import celery_app


def personalize(
    *,
    plan: dict[str, Any],
    level: str,
    weak_concepts: list[str],
) -> dict[str, Any]:
    """Rewrite segment depths to match `level`, and prepend one remediation
    segment per weak concept the student has."""
    segments = plan.get("segments", [])
    # Normalize every segment depth to the student's chosen level (the time
    # budgeting and explanation agents will diverge depth per-segment as needed).
    for s in segments:
        s["depth"] = level

    # Prepend remediation segments for previously-weak concepts.
    remediation = []
    for wc in weak_concepts[:2]:  # cap at 2 so we don't blow the time budget
        remediation.append(
            {
                "order": 0,  # will reindex below
                "concept": f"Recap: {wc}",
                "depth": level,
                "visual_type": "diagram",
                "has_checkpoint": True,
                "narration_script": "",
                "is_remediation": True,
            }
        )

    new_segments = remediation + segments
    for i, s in enumerate(new_segments):
        s["order"] = i + 1
    plan = dict(plan)
    plan["segments"] = new_segments
    return plan


@celery_app.task(name="agents.personalization.run")
def run(plan: dict[str, Any], level: str, weak_concepts: list[str]) -> dict[str, Any]:
    return personalize(plan=plan, level=level, weak_concepts=weak_concepts)
