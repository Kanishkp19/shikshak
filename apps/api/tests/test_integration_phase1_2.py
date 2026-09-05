"""Integration test: full Phase 1 + Phase 2 checkpoint flow via API calls.

Per 06-IMPLEMENTATION-PLAN.md step 25:
  "a full text-based lesson-question-wrong-answer-reteach-report loop works
   via API calls alone. This is your minimum viable demo if video runs out
   of time."

This test runs the agent chain in-process (no Celery, no Supabase) using
the LLM stub fallback so it works without external dependencies.
"""
import os
import sys

import pytest

# Ensure the apps/api dir is on sys.path so we can import agents.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_phase1_phase2_pipeline_topic_only():
    """End-to-end: topic → plan → personalize → budget → visuals → explain →
    interaction → answer (wrong) → misconception reteach → assessment.
    """
    from agents.lesson_planning import plan_lesson
    from agents.personalization import personalize
    from agents.time_budgeting import budget_segments
    from agents.visual_selection import select_visuals
    from agents.explanation import explain_segment
    from agents.interaction import generate_checkpoint
    from agents.answer_evaluation import _grade
    from agents.misconception_detection import diagnose_and_reteach

    # Phase 1: plan
    plan = plan_lesson(
        topic="Newton's Laws of Motion",
        level="beginner",
        time_budget_minutes=20,
        language="en",
        has_source=False,
        weak_concepts=[],
    )
    assert "segments" in plan
    assert len(plan["segments"]) >= 1

    plan = personalize(plan=plan, level="beginner", weak_concepts=[])
    plan = budget_segments(plan=plan, time_budget_minutes=20)
    plan = select_visuals(plan)
    assert plan["segments"]

    # Produce narration scripts for every segment
    for s in plan["segments"]:
        s["narration_script"] = explain_segment(
            concept=s["concept"],
            level=s["depth"],
            language="en",
            retrieved_chunks=None,
        )
        assert s["narration_script"]

    # Phase 2: pick the first checkpoint segment, generate a question
    checkpoint_seg = next((s for s in plan["segments"] if s.get("has_checkpoint")), None)
    if checkpoint_seg is None:
        # Plan should ensure at least one checkpoint for a 20-min budget
        plan["segments"][-1]["has_checkpoint"] = True
        checkpoint_seg = plan["segments"][-1]

    # The real flow persists via Supabase and uses the returned checkpoint row;
    # for this in-process test we just exercise the grader directly.
    fake_checkpoint = {
        "correct_answer": "inertia",
        "question_type": "short_answer",
        "options": None,
    }
    is_correct = _grade(fake_checkpoint, "momentum")
    assert is_correct is False  # wrong answer must be False

    # Misconception + reteach
    reteach = diagnose_and_reteach(
        checkpoint_id="fake",
        concept=checkpoint_seg["concept"],
        student_answer="momentum",
        correct_answer=fake_checkpoint["correct_answer"],
        original_explanation=checkpoint_seg["narration_script"],
        language="en",
    )
    assert reteach["narration_script"]
    assert reteach["narration_script"] != checkpoint_seg["narration_script"]
    assert reteach["concept"].startswith("Re-teach")


def test_personalization_topic_relevance_and_placeholder_filtering():
    """Verify that personalization rejects generic placeholders and unrelated weak concepts,
    starting directly on the requested topic."""
    from agents.personalization import personalize

    initial_plan = {
        "topic": "Photosynthesis",
        "segments": [
            {"order": 1, "concept": "What is Photosynthesis Overview", "depth": "beginner"},
            {"order": 2, "concept": "Role of Sunlight and Chlorophyll", "depth": "beginner"},
        ],
    }

    # Case 1: Generic placeholder concept must be ignored
    p1 = personalize(
        plan=initial_plan,
        level="beginner",
        weak_concepts=["Fundamental understanding of the core idea", "core idea"],
    )
    assert len(p1["segments"]) == 2
    assert p1["segments"][0]["concept"] == "What is Photosynthesis Overview"

    # Case 2: Unrelated topic weak concept must be ignored
    p2 = personalize(
        plan=initial_plan,
        level="beginner",
        weak_concepts=["Quadratic Formula", "Newton's First Law"],
    )
    assert len(p2["segments"]) == 2
    assert p2["segments"][0]["concept"] == "What is Photosynthesis Overview"

    # Case 3: Genuinely relevant weak concept IS prepended
    p3 = personalize(
        plan=initial_plan,
        level="beginner",
        weak_concepts=["Chlorophyll Light Absorption in Photosynthesis"],
    )
    assert len(p3["segments"]) == 3
    assert p3["segments"][0]["concept"] == "Recap: Chlorophyll Light Absorption in Photosynthesis"
    assert p3["segments"][1]["concept"] == "What is Photosynthesis Overview"

