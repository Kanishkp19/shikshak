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


def _is_generic_placeholder(concept: str) -> bool:
    """Return True if the concept string is a dummy or generic placeholder."""
    c = concept.lower().strip()
    generic_patterns = [
        "fundamental understanding",
        "core idea",
        "baseline condition",
        "general understanding",
        "recap:",
        "overview of the core",
        "basic principle",
    ]
    return any(gp in c for gp in generic_patterns) or len(c) < 4


def _is_relevant_to_topic(weak_concept: str, topic: str, existing_concepts: list[str]) -> bool:
    """Check if the weak concept has meaningful topical overlap with the lesson."""
    import re
    wc_lower = weak_concept.lower()
    topic_words = set(re.findall(r"\b\w{3,}\b", topic.lower()))
    
    # Check match against topic words
    for w in topic_words:
        if w in wc_lower:
            return True
            
    # Check match against existing segment concepts
    for ec in existing_concepts:
        ec_words = set(re.findall(r"\b\w{3,}\b", ec.lower()))
        if any(w in wc_lower for w in ec_words if len(w) >= 4):
            return True
            
    return False


def personalize(
    *,
    plan: dict[str, Any],
    level: str,
    weak_concepts: list[str],
) -> dict[str, Any]:
    """Rewrite segment depths to match `level`, and prepend remediation
    segments ONLY for genuinely relevant, non-placeholder weak concepts."""
    segments = plan.get("segments", [])
    for s in segments:
        s["depth"] = level

    topic = str(plan.get("topic") or "")
    existing_concepts = [s.get("concept", "") for s in segments]

    # Filter weak concepts: must not be generic placeholder, and must be relevant to current topic
    valid_remediation_concepts = [
        wc for wc in weak_concepts
        if not _is_generic_placeholder(wc)
        and (not topic or _is_relevant_to_topic(wc, topic, existing_concepts))
    ]

    remediation = []
    for wc in valid_remediation_concepts[:2]:  # cap at 2 so we don't blow the time budget
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
