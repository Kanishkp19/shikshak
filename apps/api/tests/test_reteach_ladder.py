"""
Unit tests for Work Stream 1: Attempt-Count Adaptive Reteach Ladder.
"""
from unittest.mock import patch

from agents.misconception_detection import (
    ReteachContent,
    diagnose_and_reteach,
    select_reteach_strategy,
)
from skills.misconception_analogy_bank import (
    RETEACH_ATOMIC_STEPS_TEMPLATE,
    RETEACH_CONCRETE_EXAMPLE_TEMPLATE,
    RETEACH_SIMPLIFY_TEMPLATE,
    get_strategy_template,
)


def test_select_reteach_strategy_ladder():
    """Assert deterministic strategy selection progression: simplify -> concrete_example -> atomic_steps."""
    assert select_reteach_strategy(1) == "simplify"
    assert select_reteach_strategy(2) == "concrete_example"
    assert select_reteach_strategy(3) == "atomic_steps"
    assert select_reteach_strategy(4) == "atomic_steps"
    assert select_reteach_strategy(10) == "atomic_steps"


def test_strategy_templates_loaded():
    """Verify templates exist and require the expected parameters."""
    t1 = get_strategy_template("simplify")
    t2 = get_strategy_template("concrete_example")
    t3 = get_strategy_template("atomic_steps")

    assert t1 is RETEACH_SIMPLIFY_TEMPLATE
    assert t2 is RETEACH_CONCRETE_EXAMPLE_TEMPLATE
    assert t3 is RETEACH_ATOMIC_STEPS_TEMPLATE

    for t in (t1, t2, t3):
        rendered = t.render(
            concept="Photosynthesis",
            original_explanation="Plants convert sunlight into chemical energy.",
            student_wrong_answer="Plants eat dirt to grow.",
            prior_analogies_used="Solar panel factory",
        )
        assert "Photosynthesis" in rendered
        assert "Plants eat dirt to grow" in rendered


def test_reteach_content_pydantic_schema():
    """Verify validation of ReteachContent schema."""
    content = ReteachContent(
        strategy="simplify",
        explanation="Plants use light from the sun and air to make sweet food for themselves.",
        new_example="Baking a cake using sunlight as the oven.",
        follow_up_question="What does the plant use for energy?",
    )
    assert content.strategy == "simplify"
    assert content.new_example is not None


def _lexical_overlap_ratio(text1: str, text2: str) -> float:
    """Calculate token overlap Jaccard ratio between two explanation texts."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)


def test_three_consecutive_wrong_answers_escalate_and_diverge():
    """Mock 3 consecutive wrong answers on one checkpoint and assert strategy progression:
    simplify -> concrete_example -> atomic_steps, and that explanations diverge lexically."""
    checkpoint_id = "test-cp-123"
    concept = "Newton's Second Law"
    correct_answer = "Force equals mass times acceleration (F=ma)"
    student_answers = [
        "Heavier things always fall faster because they are heavier",
        "More force means the object travels for longer time",
        "Mass doesn't matter if you push hard enough",
    ]
    original_explanation = "Force is the product of mass and acceleration."

    mock_llm_responses = [
        # Attempt 1: Simplify
        ReteachContent(
            strategy="simplify",
            explanation="In simple words: heavy things need more push to get moving. If you gently push a toy car, it rolls easily. If you push a full supermarket trolley with the same gentle push, it barely moves.",
            new_example="Pushing a toy car versus a heavy grocery trolley",
            follow_up_question="Which one needs a bigger push to speed up quickly?",
        ),
        # Attempt 2: Concrete Example
        ReteachContent(
            strategy="concrete_example",
            explanation="The common misconception is thinking force dictates duration instead of acceleration. Consider a bowler bowling a cricket ball: the force from the arm only accelerates the ball while touching it, not for the entire flight.",
            new_example="A bowler releasing a cricket ball",
            follow_up_question="Does the bowler apply force after releasing the ball?",
        ),
        # Attempt 3: Atomic Steps
        ReteachContent(
            strategy="atomic_steps",
            explanation="Step 1: Notice the mass of the object in kilograms.\nStep 2: Measure the net unbalanced force acting on it.\nStep 3: Divide net force by mass to determine instantaneous acceleration.\nStep 4: The object changes speed at exactly that acceleration rate.",
            new_example="Numbered calculation steps",
            follow_up_question="What is the result of Step 3?",
        ),
    ]

    strategies_observed = []
    explanations = []
    accumulated_prior = []

    for attempt_idx in range(1, 4):
        strategy = select_reteach_strategy(attempt_idx)
        strategies_observed.append(strategy)

        with patch("agents.misconception_detection.call_llm_with_retry") as mock_call, \
             patch("agents.misconception_detection.update_checkpoint") as mock_update, \
             patch("agents.misconception_detection.log_agent_run") as mock_log:

            mock_call.return_value = mock_llm_responses[attempt_idx - 1]

            result = diagnose_and_reteach(
                checkpoint_id=checkpoint_id,
                concept=concept,
                student_answer=student_answers[attempt_idx - 1],
                correct_answer=correct_answer,
                original_explanation=original_explanation,
                attempt_number=attempt_idx,
                strategy=strategy,
                prior_analogies_used=accumulated_prior,
            )

            assert result["strategy"] == strategy
            assert result["attempt_number"] == attempt_idx
            assert result["is_remediation"] is True
            assert len(result["narration_script"]) > 20

            explanations.append(result["narration_script"])
            if result.get("new_example"):
                accumulated_prior.append(result["new_example"])

            mock_update.assert_called_once()
            call_args = mock_update.call_args[0]
            assert call_args[0] == checkpoint_id
            assert call_args[1]["attempt_number"] == attempt_idx
            assert call_args[1]["reteach_strategy"] == strategy

    # 1. Assert strategy progression is exactly simplify -> concrete_example -> atomic_steps
    assert strategies_observed == ["simplify", "concrete_example", "atomic_steps"]

    # 2. Assert non-trivial lexical divergence across attempts (Jaccard overlap < 0.35)
    overlap_1_2 = _lexical_overlap_ratio(explanations[0], explanations[1])
    overlap_2_3 = _lexical_overlap_ratio(explanations[1], explanations[2])
    overlap_1_3 = _lexical_overlap_ratio(explanations[0], explanations[2])

    assert overlap_1_2 < 0.35, f"Explanations 1 & 2 overlap too much: {overlap_1_2}"
    assert overlap_2_3 < 0.35, f"Explanations 2 & 3 overlap too much: {overlap_2_3}"
    assert overlap_1_3 < 0.35, f"Explanations 1 & 3 overlap too much: {overlap_1_3}"
