"""
Shikshak AI — misconception analogy bank.

Curated analogies for the most common STEM misconceptions. Used as a fallback
when the LLM-driven Misconception Detection Agent is unavailable, and as a
sanity check on LLM-generated re-explanations (the agent should always choose
a different analogy than the one used in the original explanation).
"""
from __future__ import annotations

from typing import Optional
from skills.prompt_templating import PromptTemplate


# ── Reteach Ladder Prompt Templates ──────────────────────────────────────────
# Strategy 1 (attempt 1): Simplify vocabulary, step-by-step, zero jargon
RETEACH_SIMPLIFY_TEMPLATE = PromptTemplate(
    """
Concept: {concept}
Original explanation: {original_explanation}
Student wrong answer: {student_wrong_answer}
Prior analogies used (STRICTLY FORBIDDEN TO REUSE): {prior_analogies_used}

You are executing Reteach Strategy: "simplify".
1. Strip away all academic jargon and complex vocabulary.
2. Break the explanation down into intuitive, plain-language sentences that a 10-year-old would understand.
3. DO NOT repeat or reuse any analogy, metaphor, or phrasing from "Prior analogies used" or "Original explanation".
4. Provide a clear follow-up check question to verify comprehension.

Return valid JSON:
{{
  "strategy": "simplify",
  "explanation": "<100-140 words simple, jargon-free re-explanation>",
  "new_example": "<short intuitive analogy or null>",
  "follow_up_question": "<a simple conceptual check question>"
}}
""",
    required_vars=["concept", "original_explanation", "student_wrong_answer", "prior_analogies_used"],
)

# Strategy 2 (attempt 2): Real-world concrete example, naming the misconception
RETEACH_CONCRETE_EXAMPLE_TEMPLATE = PromptTemplate(
    """
Concept: {concept}
Original explanation: {original_explanation}
Student wrong answer: {student_wrong_answer}
Prior analogies used (STRICTLY FORBIDDEN TO REUSE): {prior_analogies_used}

You are executing Reteach Strategy: "concrete_example".
1. Explicitly name the misconception that led to the student's answer: "{student_wrong_answer}".
2. Ground the concept in a tangible, physical real-world scenario (e.g., everyday objects, sports, kitchen science).
3. DO NOT repeat or reuse any analogy or example from "Prior analogies used" or "Original explanation".
4. Provide a fresh follow-up check question that tests this concrete scenario.

Return valid JSON:
{{
  "strategy": "concrete_example",
  "explanation": "<120-160 words naming misconception and explaining via new concrete scenario>",
  "new_example": "<the concrete real-world scenario>",
  "follow_up_question": "<a follow-up question based on this concrete example>"
}}
""",
    required_vars=["concept", "original_explanation", "student_wrong_answer", "prior_analogies_used"],
)

# Strategy 3 (attempt 3+): Decompose into atomic sub-concepts, numbered, zero prior knowledge
RETEACH_ATOMIC_STEPS_TEMPLATE = PromptTemplate(
    """
Concept: {concept}
Original explanation: {original_explanation}
Student wrong answer: {student_wrong_answer}
Prior analogies used (STRICTLY FORBIDDEN TO REUSE): {prior_analogies_used}

You are executing Reteach Strategy: "atomic_steps".
1. The student has struggled across multiple attempts. Assume zero prior knowledge.
2. Decompose the concept into 3-4 numbered atomic micro-steps (Step 1, Step 2, Step 3...).
3. Build up the mechanism step-by-step so failure at intermediate reasoning is impossible.
4. DO NOT reuse any analogy from "Prior analogies used" or "Original explanation".
5. Provide a simple follow-up question testing Step 1 and Step 2.

Return valid JSON:
{{
  "strategy": "atomic_steps",
  "explanation": "<Numbered atomic steps: Step 1: ..., Step 2: ..., Step 3: ...>",
  "new_example": "<micro-analogy for step 1 or null>",
  "follow_up_question": "<targeted question on the fundamental step>"
}}
""",
    required_vars=["concept", "original_explanation", "student_wrong_answer", "prior_analogies_used"],
)


def get_strategy_template(strategy: str) -> PromptTemplate:
    """Return the corresponding PromptTemplate for the chosen reteach strategy."""
    if strategy == "simplify":
        return RETEACH_SIMPLIFY_TEMPLATE
    elif strategy == "concrete_example":
        return RETEACH_CONCRETE_EXAMPLE_TEMPLATE
    elif strategy == "atomic_steps":
        return RETEACH_ATOMIC_STEPS_TEMPLATE
    raise ValueError(f"Unknown reteach strategy: {strategy}")



# Keyword → list of alternative analogies. The Misconception Detection Agent
# picks one of these as a seed when generating a re-explanation.
ANALOGY_BANK: dict[str, list[str]] = {
    # Physics
    "newton": [
        "Pushing a heavy shopping cart vs an empty one — same force, different acceleration",
        "Slamming the brakes in a car — your body wants to keep moving",
        "A hockey puck on ice — friction is the only thing slowing it down",
    ],
    "gravity": [
        "A stretched trampoline with marbles on it — they roll toward the heavy ball in the middle",
        "A bowling ball on a mattress — the mattress sags and pulls other objects toward it",
        "Two magnets of different sizes — the bigger one pulls harder, just like more mass",
    ],
    # Math
    "fraction": [
        "Cutting a pizza into slices — each slice is part of the whole pizza",
        "Pouring water into identical cups — each cup holds an equal fraction of the jug",
        "Sharing a chocolate bar among friends — each friend gets a fraction",
    ],
    "derivative": [
        "Speedometer in a car — it's the rate of change of position at this exact instant",
        "Zooming into a curve until it looks straight — the slope at that point is the derivative",
        "Tracking your bank balance — the derivative is how fast it's changing right now",
    ],
    # Biology
    "photosynthesis": [
        "A solar-powered kitchen — leaves catch sunlight and use it to cook sugar out of water and air",
        "A factory that takes in raw materials (CO2 + water) and ships out sugar + oxygen",
        "A rechargeable battery — sunlight recharges the plant's energy storage (sugar)",
    ],
    # CS
    "recursion": [
        "Russian nesting dolls — each doll opens to reveal a smaller one until the tiniest",
        "Looking at yourself in a mirror that reflects a mirror — base case is when there's no more reflection",
        "Telling a story where the hero tells the same story — only stops when there's no hero left to tell it",
    ],
    "variable": [
        "A labeled box — you put something in, take something out, but the label stays the same",
        "A locker — same number, different contents today vs tomorrow",
        "A parking spot — same spot, different car each day",
    ],
    "loop": [
        "Doing push-ups until your timer rings — repeat until the end condition",
        "Flipping pages of a book — one at a time, until the last page",
        "Walking up stairs — same motion, one step at a time, until you reach the floor",
    ],
}

DEFAULT_ANALOGIES = [
    "Try explaining it backwards — start from the result and trace the steps back to the cause",
    "Use a real-life example the student sees every day, like cooking or sports",
    "Draw it on paper first, then re-explain using the picture",
    "Compare it to something the student already understood in an earlier segment",
]


def pick_alternative_analogies(
    concept: str,
    original_analogy: Optional[str] = None,
    prior_analogies: Optional[list[str]] = None,
) -> list[str]:
    """Return 2-3 alternative analogies for `concept`, excluding the original and prior used analogies."""
    key = _keyword_match(concept)
    pool = list(ANALOGY_BANK.get(key, DEFAULT_ANALOGIES))
    exclusions = []
    if original_analogy:
        exclusions.append(original_analogy.lower())
    if prior_analogies:
        exclusions.extend(a.lower() for a in prior_analogies if a)

    if exclusions:
        filtered = [
            a for a in pool
            if not any(ex in a.lower() or a.lower() in ex for ex in exclusions)
        ]
        # If all filtered out, fall back to default analogies not yet in exclusions
        if not filtered:
            filtered = [
                a for a in DEFAULT_ANALOGIES
                if not any(ex in a.lower() or a.lower() in ex for ex in exclusions)
            ]
        pool = filtered or pool

    return pool[:3]


def _keyword_match(concept: str) -> Optional[str]:
    concept_lower = concept.lower()
    for key in ANALOGY_BANK:
        if key in concept_lower:
            return key
    return None
