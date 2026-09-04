"""
Unit tests for Work Stream 2: Continuous Mastery Scoring.
"""
from agents.assessment import order_weak_areas_by_priority
from agents.interaction import select_checkpoint_concept
from skills.mastery_scoring import (
    blend_score,
    classify,
    update_mastery_record,
    weakness_priority,
)


def test_blend_score_known_values():
    """Assert blend_score with default alpha=0.4:
    0.4 * 0.85 + 0.6 * 0.40 = 0.34 + 0.24 = 0.58"""
    assert blend_score(0.40, 0.85) == 0.58
    assert blend_score(0.0, 1.0) == 0.40
    assert blend_score(0.80, 0.80) == 0.80


def test_classify_tiers():
    """Verify discrete mastery tier classifications."""
    # Under 0.58, still classified "weak"
    assert classify(0.58) == "weak"
    assert classify(0.0) == "weak"
    assert classify(0.5999) == "weak"

    # Moderate: 0.60 to < 0.80
    assert classify(0.60) == "moderate"
    assert classify(0.75) == "moderate"
    assert classify(0.799) == "moderate"

    # Strong: >= 0.80
    assert classify(0.80) == "strong"
    assert classify(0.95) == "strong"
    assert classify(1.0) == "strong"


def test_weakness_priority_formula():
    """Verify weakness_priority = (0.6 - score) + min(attempts * 0.1, 0.5)."""
    # score=0.4, attempts=2: (0.6 - 0.4) + 0.2 = 0.4
    assert round(weakness_priority(0.4, 2), 2) == 0.40

    # score=0.2, attempts=5: (0.6 - 0.2) + 0.5 = 0.9 (capped attempt weight)
    assert round(weakness_priority(0.2, 5), 2) == 0.90
    assert round(weakness_priority(0.2, 8), 2) == 0.90  # capped at +0.5

    # score=0.9, attempts=1: (0.6 - 0.9) + 0.1 = -0.2
    assert round(weakness_priority(0.9, 1), 2) == -0.20


def test_update_mastery_record_transitions():
    """Verify record updates, attempt counts, and consecutive_strong tracking."""
    # 1. First wrong attempt
    r1 = update_mastery_record(
        old_score=0.0,
        new_grade=0.0,
        old_attempts=0,
        old_consecutive_strong=0,
    )
    assert r1["score"] == 0.0
    assert r1["status"] == "weak"
    assert r1["attempts"] == 1
    assert r1["consecutive_strong"] == 0

    # 2. Perfect answer after 1 wrong attempt: blend_score(0.0, 1.0) -> 0.4
    r2 = update_mastery_record(
        old_score=float(r1["score"]),
        new_grade=1.0,
        old_attempts=int(r1["attempts"]),
        old_consecutive_strong=int(r1["consecutive_strong"]),
    )
    assert r2["score"] == 0.4
    assert r2["status"] == "weak"
    assert r2["attempts"] == 2
    assert r2["consecutive_strong"] == 0

    # 3. Second perfect answer: blend_score(0.4, 1.0) -> 0.64 (moderate)
    r3 = update_mastery_record(
        old_score=float(r2["score"]),
        new_grade=1.0,
        old_attempts=int(r2["attempts"]),
        old_consecutive_strong=int(r2["consecutive_strong"]),
    )
    assert r3["score"] == 0.64
    assert r3["status"] == "moderate"
    assert r3["attempts"] == 3
    assert r3["consecutive_strong"] == 0

    # 4. Third perfect answer: blend_score(0.64, 1.0) -> 0.784 (moderate)
    r4 = update_mastery_record(
        old_score=float(r3["score"]),
        new_grade=1.0,
        old_attempts=int(r3["attempts"]),
        old_consecutive_strong=int(r3["consecutive_strong"]),
    )
    assert r4["score"] == 0.784
    assert r4["status"] == "moderate"

    # 5. Fourth perfect answer: blend_score(0.784, 1.0) -> 0.8704 (strong!)
    r5 = update_mastery_record(
        old_score=float(r4["score"]),
        new_grade=1.0,
        old_attempts=int(r4["attempts"]),
        old_consecutive_strong=int(r4["consecutive_strong"]),
    )
    assert r5["score"] == 0.8704
    assert r5["status"] == "strong"
    assert r5["attempts"] == 5
    assert r5["consecutive_strong"] == 1

    # 6. Fifth perfect answer -> consecutive_strong increments to 2
    r6 = update_mastery_record(
        old_score=float(r5["score"]),
        new_grade=1.0,
        old_attempts=int(r5["attempts"]),
        old_consecutive_strong=int(r5["consecutive_strong"]),
    )
    assert r6["consecutive_strong"] == 2

    # 7. Followed by an incorrect answer -> consecutive_strong resets to 0
    r7 = update_mastery_record(
        old_score=float(r6["score"]),
        new_grade=0.0,
        old_attempts=int(r6["attempts"]),
        old_consecutive_strong=int(r6["consecutive_strong"]),
    )
    assert r7["consecutive_strong"] == 0


def test_order_weak_areas_by_priority():
    """Verify that assessment weak areas are ordered by highest remediation urgency first."""
    checkpoints = [
        # Concept A: 3 attempts, all wrong (urgency = (0.6 - 0) + 0.3 = 0.9)
        {"concept": "Concept A", "is_correct": False, "attempt_number": 3},
        {"concept": "Concept A", "is_correct": False, "attempt_number": 2},
        {"concept": "Concept A", "is_correct": False, "attempt_number": 1},
        # Concept B: 1 attempt, 1 correct (urgency = (0.6 - 1.0) + 0 = -0.4)
        {"concept": "Concept B", "is_correct": True, "attempt_number": 1},
        # Concept C: 1 attempt, wrong (urgency = (0.6 - 0) + 0.1 = 0.7)
        {"concept": "Concept C", "is_correct": False, "attempt_number": 1},
    ]

    ordered = order_weak_areas_by_priority(
        weak_areas=["Concept B", "Concept C", "Concept A"],
        checkpoints=checkpoints,
    )
    assert ordered == ["Concept A", "Concept C", "Concept B"]


def test_select_checkpoint_concept():
    """Verify interaction agent picks the concept with highest priority."""
    # Single concept
    assert select_checkpoint_concept("Photosynthesis") == "Photosynthesis"

    # Multi-concept string
    candidates = ["Calculus Integration", "Derivatives Basics"]
    # With equal baseline, first or higher priority selected deterministically
    chosen = select_checkpoint_concept("Calculus Integration, Derivatives Basics")
    assert chosen in candidates
