"""
Shikshak AI — Learner Profile Agent.

Single responsibility: read and update the learner_profiles table. Called at
session start (to inject prior weak concepts into the lesson plan) and at
session end (to write back new weak/strong concepts from the assessment).
"""
from __future__ import annotations

from typing import Any

from celery_app import celery_app
from skills.supabase_persistence import (
    get_learner_profile,
    upsert_learner_profile,
    patch_learner_profile,
)


def read_profile(student_id: str) -> dict[str, Any]:
    """Return the student's profile, creating an empty one if absent."""
    existing = get_learner_profile(student_id)
    if existing:
        return existing
    # Create empty profile
    row = upsert_learner_profile(
        id=student_id,
        display_name=None,
        default_level="beginner",
        default_language="en",
        topics_studied=[],
        weak_concepts=[],
        strong_concepts=[],
        average_score=0,
    )
    return row


def update_profile_from_report(
    *,
    student_id: str,
    topic: str,
    score: float,
    strong_areas: list[str],
    weak_areas: list[str],
) -> dict[str, Any]:
    """At session end, merge the report's strong/weak areas into the profile,
    add the topic to topics_studied, and recompute average_score."""
    profile = read_profile(student_id)
    topics = list(profile.get("topics_studied") or [])
    if topic and topic not in topics:
        topics.append(topic)

    strong = list(profile.get("strong_concepts") or [])
    weak = list(profile.get("weak_concepts") or [])
    for s in strong_areas:
        if s not in strong:
            strong.append(s)
        if s in weak:
            weak.remove(s)
    for w in weak_areas:
        if w not in weak:
            weak.append(w)
        if w in strong:
            strong.remove(w)

    # Also sync derived views from concept_mastery table
    try:
        from skills.supabase_persistence import list_concept_mastery
        mastery_list = list_concept_mastery(student_id)
        if mastery_list:
            for m in mastery_list:
                c = m.get("concept")
                st = m.get("status")
                if not c:
                    continue
                if st == "strong":
                    if c not in strong:
                        strong.append(c)
                    if c in weak:
                        weak.remove(c)
                elif st == "weak":
                    if c not in weak:
                        weak.append(c)
                    if c in strong:
                        strong.remove(c)
    except Exception:
        pass

    # Recompute average score as a running mean
    prev_avg = float(profile.get("average_score") or 0)
    n = len(topics) or 1
    new_avg = round(((prev_avg * (n - 1)) + score) / n, 2)

    return patch_learner_profile(
        student_id,
        {
            "topics_studied": topics,
            "strong_concepts": strong,
            "weak_concepts": weak,
            "average_score": new_avg,
        },
    )



@celery_app.task(name="agents.learner_profile.read")
def read_task(student_id: str) -> dict[str, Any]:
    return read_profile(student_id)


@celery_app.task(name="agents.learner_profile.update_from_report")
def update_task(
    student_id: str,
    topic: str,
    score: float,
    strong_areas: list[str],
    weak_areas: list[str],
) -> dict[str, Any]:
    return update_profile_from_report(
        student_id=student_id,
        topic=topic,
        score=score,
        strong_areas=strong_areas,
        weak_areas=weak_areas,
    )
