"""
Shikshak AI — Language Agent.

Single responsibility: ensure the narration scripts in the plan are in the
requested language. Used in two flows:
  - at session start, when language is set up-front
  - mid-session, when the student switches language (regenerates only the
    not-yet-played segments)
"""
from __future__ import annotations

from typing import Any

from celery_app import celery_app
from skills.translation import translate_text


def apply_language(
    *,
    plan: dict[str, Any],
    target_language: str,
    current_language: str = "en",
    regenerate_from_order: int = 1,
) -> dict[str, Any]:
    """Translate narration scripts in the plan from `current_language` to
    `target_language`. If `regenerate_from_order` is set, only segments with
    order >= that value are translated (used for mid-session switches)."""
    if target_language == current_language:
        return plan

    new_plan = dict(plan)
    new_segments = []
    for s in plan.get("segments", []):
        if s.get("order", 0) < regenerate_from_order:
            new_segments.append(s)
            continue
        new_s = dict(s)
        if new_s.get("narration_script"):
            new_s["narration_script"] = translate_text(
                new_s["narration_script"],
                target_language=target_language,
                source_language=current_language,
            )
        new_segments.append(new_s)
    new_plan["segments"] = new_segments
    new_plan["language"] = target_language
    return new_plan


@celery_app.task(name="agents.language.run")
def run(
    plan: dict[str, Any],
    target_language: str,
    current_language: str = "en",
    regenerate_from_order: int = 1,
) -> dict[str, Any]:
    return apply_language(
        plan=plan,
        target_language=target_language,
        current_language=current_language,
        regenerate_from_order=regenerate_from_order,
    )
