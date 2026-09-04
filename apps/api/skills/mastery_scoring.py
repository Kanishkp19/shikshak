"""
Shikshak AI — Continuous Mastery Scoring skill.

Zero-cost, pure-Python calculation module for tracking a student's evolving
mastery of concepts across question checkpoints.
"""
from __future__ import annotations

from typing import Literal

MasteryStatus = Literal["weak", "moderate", "strong"]


def blend_score(old: float, new: float, alpha: float = 0.4) -> float:
    """Compute exponential moving average between historical and newly observed score.

    Default alpha=0.4 gives 40% weight to the latest attempt and 60% to prior history.
    Example: blend_score(0.40, 0.85) -> 0.58
    """
    return round(alpha * float(new) + (1.0 - alpha) * float(old), 4)


def classify(score: float) -> MasteryStatus:
    """Classify numeric score into discrete pedagogical mastery tiers:
    - < 0.6: weak
    - 0.6 to < 0.8: moderate
    - >= 0.8: strong
    """
    if score < 0.6:
        return "weak"
    if score < 0.8:
        return "moderate"
    return "strong"


def weakness_priority(score: float, attempts: int) -> float:
    """Calculate the urgency of re-testing or reviewing a concept.

    Combines the gap from mastery threshold (0.6 - score) with repeated attempt
    struggles (capped at +0.5). Higher value means higher priority for remediation.
    """
    return round((0.6 - float(score)) + min(int(attempts) * 0.1, 0.5), 4)


def update_mastery_record(
    *,
    old_score: float,
    new_grade: float,
    old_attempts: int,
    old_consecutive_strong: int,
    alpha: float = 0.4,
) -> dict[str, float | str | int]:
    """Calculate the updated mastery tuple after a graded answer submission."""
    new_score = blend_score(old_score, new_grade, alpha=alpha)
    status = classify(new_score)
    attempts = old_attempts + 1
    consecutive_strong = (old_consecutive_strong + 1) if status == "strong" else 0

    return {
        "score": new_score,
        "status": status,
        "attempts": attempts,
        "consecutive_strong": consecutive_strong,
    }
