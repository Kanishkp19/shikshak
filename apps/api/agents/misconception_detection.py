"""
Shikshak AI — Misconception Detection Agent.

Single responsibility: when an answer is wrong, diagnose the likely misconception
and produce an escalating re-explanation using an attempt-count adaptive ladder:
- attempt 1 -> "simplify" (simpler vocabulary, step-by-step, zero jargon)
- attempt 2 -> "concrete_example" (tangible real-world example, explicitly naming misconception)
- attempt 3+ -> "atomic_steps" (numbered micro-steps, zero prior knowledge assumed)

Guarantees divergence across attempts by excluding prior analogies accumulated on the checkpoint.
Validates all LLM outputs against ReteachContent before persisting or returning.
"""
from __future__ import annotations

import logging
from typing import Any, Literal, Optional
from pydantic import BaseModel

from celery_app import celery_app
from agents.llm import get_content_llm as get_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.misconception_analogy_bank import (
    get_strategy_template,
    pick_alternative_analogies,
)
from skills.prompt_templating import SYSTEM_TEACHER, TEMPERATURE_RETEACH
from skills.supabase_persistence import (
    get_checkpoint,
    log_agent_run,
    update_checkpoint,
)

logger = logging.getLogger(__name__)

ReteachStrategy = Literal["simplify", "concrete_example", "atomic_steps"]


class ReteachContent(BaseModel):
    strategy: ReteachStrategy
    explanation: str
    new_example: Optional[str] = None
    follow_up_question: str


# Backward compatibility alias
ReExplanation = ReteachContent


def select_reteach_strategy(attempt_number: int) -> ReteachStrategy:
    """Pure deterministic lookup mapping attempt count to reteach ladder strategy."""
    if attempt_number <= 1:
        return "simplify"
    elif attempt_number == 2:
        return "concrete_example"
    else:
        return "atomic_steps"


def diagnose_and_reteach(
    *,
    checkpoint_id: str,
    concept: str,
    student_answer: str,
    correct_answer: str,
    original_explanation: str,
    language: str = "en",
    attempt_number: int = 1,
    strategy: Optional[str] = None,
    prior_analogies_used: Optional[list[str]] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    """Produce an escalated re-teach segment validated against ReteachContent."""
    chosen_strategy = strategy or select_reteach_strategy(attempt_number)
    if chosen_strategy not in ("simplify", "concrete_example", "atomic_steps"):
        chosen_strategy = select_reteach_strategy(attempt_number)

    # 1. Resolve prior analogies to enforce distinct re-explanations
    accumulated_analogies: list[str] = list(prior_analogies_used or [])
    if checkpoint_id and checkpoint_id != "fake" and not accumulated_analogies:
        try:
            cp_row = get_checkpoint(checkpoint_id)
            if cp_row and cp_row.get("prior_analogies_used"):
                accumulated_analogies = list(cp_row["prior_analogies_used"])
        except Exception as e:
            logger.warning("[misconception_detection] Could not read checkpoint prior analogies: %s", e)

    # 2. Pick alternative seed analogies from curated bank
    seed_analogies = pick_alternative_analogies(
        concept,
        original_analogy=original_explanation,
        prior_analogies=accumulated_analogies,
    )
    seed_block = ""
    if seed_analogies:
        seed_block = (
            f"\n\nFresh analogies to consider for {chosen_strategy} (do NOT reuse prior ones):\n"
            + "\n".join(f"- {a}" for a in seed_analogies)
        )

    # 3. Render strategy-specific prompt
    tpl = get_strategy_template(chosen_strategy)
    system_instruction = (
        "You are Shikshak, an expert AI tutor helping a student overcome a misconception. "
        "Provide an engaging, pedagogically sound re-explanation matching the requested strategy and schema."
    )
    prompt = (
        system_instruction
        + "\n\n"
        + tpl.render(
            concept=concept,
            original_explanation=original_explanation or "(none)",
            student_wrong_answer=student_answer or "(none)",
            prior_analogies_used=", ".join(accumulated_analogies) or "(none)",
        )
        + seed_block
    )

    # 4. Invoke LLM with validated ReteachContent schema & TEMPERATURE_RETEACH
    llm = get_llm(temperature=TEMPERATURE_RETEACH)
    try:
        reteach = call_llm_with_retry(
            llm,
            prompt,
            ReteachContent,
            model_name="misconception_detection",
        )
    except Exception as e:
        logger.warning(
            "[misconception_detection] LLM call failed (%s); using deterministic fallback for %s",
            e, chosen_strategy,
        )
        reteach = _deterministic_reteach_fallback(
            strategy=chosen_strategy,
            concept=concept,
            student_answer=student_answer,
            seed_analogies=seed_analogies,
        )

    # 5. Record newly used example/analogy into accumulated list
    if reteach.new_example and reteach.new_example not in accumulated_analogies:
        accumulated_analogies.append(reteach.new_example)

    # 6. Persist state to question_checkpoints
    try:
        if checkpoint_id and checkpoint_id != "fake":
            update_checkpoint(
                checkpoint_id,
                {
                    "attempt_number": attempt_number,
                    "reteach_strategy": chosen_strategy,
                    "misconception": f"[{chosen_strategy}] {reteach.explanation[:120]}",
                    "prior_analogies_used": accumulated_analogies,
                },
            )
    except Exception as e:
        logger.warning("[diagnose_and_reteach] Could not update checkpoint %s: %s", checkpoint_id, e)

    # 7. Log decision point to agent_run_logs
    try:
        log_agent_run(
            session_id=session_id,
            agent_name="misconception_detection",
            input_summary={
                "checkpoint_id": checkpoint_id,
                "attempt_number": attempt_number,
                "strategy": chosen_strategy,
                "prior_analogies_count": len(accumulated_analogies),
            },
            output_summary={
                "strategy": chosen_strategy,
                "explanation_length": len(reteach.explanation),
                "has_new_example": bool(reteach.new_example),
                "follow_up_question": reteach.follow_up_question,
            },
            status="success",
        )
    except Exception as e:
        logger.warning("[diagnose_and_reteach] Could not write agent_run_log: %s", e)

    return {
        "concept": f"Re-teach ({chosen_strategy.replace('_', ' ')}): {concept}",
        "narration_script": reteach.explanation,
        "depth": "beginner",
        "visual_type": "diagram",
        "is_remediation": True,
        "misconception": f"[{chosen_strategy}] {reteach.explanation[:120]}",
        "strategy": chosen_strategy,
        "attempt_number": attempt_number,
        "new_example": reteach.new_example,
        "follow_up_question": reteach.follow_up_question,
        "prior_analogies_used": accumulated_analogies,
        "reteach_content": reteach.model_dump(),
    }


def _deterministic_reteach_fallback(
    strategy: ReteachStrategy,
    concept: str,
    student_answer: str,
    seed_analogies: list[str],
) -> ReteachContent:
    """Safe, deterministic fallback ensuring no request crashes."""
    example = seed_analogies[0] if seed_analogies else None

    if strategy == "simplify":
        return ReteachContent(
            strategy="simplify",
            explanation=(
                f"Let us explain {concept} using simple everyday words without jargon. "
                f"When {concept} happens, one direct action causes the next reaction in a plain sequence, "
                f"just like dominoes falling in a row."
            ),
            new_example=example or "Dominoes knocking each other down in a neat row",
            follow_up_question=f"In simple words, what starts the sequence in {concept}?",
        )
    elif strategy == "concrete_example":
        return ReteachContent(
            strategy="concrete_example",
            explanation=(
                f"The misconception behind answering '{student_answer}' is confusing the net effect with the cause. "
                f"In the physical world: {example or 'pushing a grocery cart on level ground versus a steep ramp'}. "
                f"This real situation demonstrates why {concept} behaves the way it does."
            ),
            new_example=example or "Pushing a grocery cart up a steep ramp versus flat ground",
            follow_up_question=f"How does the real-world scenario disprove '{student_answer}'?",
        )
    else:  # atomic_steps
        return ReteachContent(
            strategy="atomic_steps",
            explanation=(
                f"Let us break {concept} into atomic numbered steps with zero assumptions:\n"
                f"Step 1: Identify the starting state and initial conditions.\n"
                f"Step 2: Identify the single force or rule acting upon it.\n"
                f"Step 3: Track the direct result of that rule on the system.\n"
                f"Step 4: Confirm that the final state matches conservation laws."
            ),
            new_example=example or "A step-by-step checklist where every step must pass before the next",
            follow_up_question="What must be confirmed in Step 1 before applying Step 2?",
        )


@celery_app.task(name="agents.misconception_detection.run")
def run(
    checkpoint_id: str,
    concept: str,
    student_answer: str,
    correct_answer: str,
    original_explanation: str,
    language: str = "en",
    attempt_number: int = 1,
    strategy: Optional[str] = None,
    prior_analogies_used: Optional[list[str]] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    return diagnose_and_reteach(
        checkpoint_id=checkpoint_id,
        concept=concept,
        student_answer=student_answer,
        correct_answer=correct_answer,
        original_explanation=original_explanation,
        language=language,
        attempt_number=attempt_number,
        strategy=strategy,
        prior_analogies_used=prior_analogies_used,
        session_id=session_id,
    )
