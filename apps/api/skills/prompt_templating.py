"""
Shikshak AI — shared prompt templating skill.

Every LLM call that embeds user-uploaded content goes through this module
to reduce prompt-injection risk (raw string concatenation is forbidden in
agents per the TRD security checklist).
"""
from __future__ import annotations

from textwrap import dedent
from typing import Any


class PromptTemplate:
    """Simple Jinja-like template — no external dependency, escapes nothing,
    but enforces a single builder so prompt construction is auditable."""

    def __init__(self, template: str, required_vars: list[str] | None = None):
        self.template = dedent(template).strip()
        self.required_vars = required_vars or []

    def render(self, **kwargs: Any) -> str:
        missing = [v for v in self.required_vars if v not in kwargs]
        if missing:
            raise ValueError(f"PromptTemplate missing vars: {missing}")
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"PromptTemplate variable {e} not provided") from e


# ── Explicit LLM sampling parameters ──────────────────────────────────────────
TEMPERATURE_EVALUATION: float = 0.1
TEMPERATURE_RETEACH: float = 0.4


# ── Shared, reusable templates ───────────────────────────────────────────────
SYSTEM_TEACHER = PromptTemplate(
    """You are Shikshak, an experienced AI teacher.
Always produce the requested JSON exactly matching the given schema.
Never invent facts. If the source material does not contain the answer,
explicitly say "NOT_IN_SOURCE" in that field rather than guessing.
Stay in the student's requested language and level at all times.""",
)

LESSON_PLAN_TEMPLATE = PromptTemplate(
    """
Topic: {topic}
Level: {level}
Time budget: {time_budget_minutes} minutes
Language: {language}
Source material available: {has_source}
Previously weak concepts for this student: {weak_concepts}

Return a JSON object with one field "segments" — an ordered array where each
element has:
  - concept: short concept title
  - depth: "beginner" | "intermediate" | "advanced"
  - visual_type: "diagram" | "equation" | "code" | "animation" | "none"
  - has_checkpoint: boolean — true if a checkpoint question should follow

Limit segment count so total expected talking time fits the time budget at
~120 words per minute. At least one segment must have has_checkpoint=true
when time_budget_minutes >= 20.
""",
    required_vars=[
        "topic",
        "level",
        "time_budget_minutes",
        "language",
        "has_source",
        "weak_concepts",
    ],
)

NARRATION_TEMPLATE = PromptTemplate(
    """
Concept: {concept}
Depth: {level}
Language: {language}
Retrieved source chunks (use ONLY these — anything not supported here is forbidden):
{retrieved_chunks}

Write a narration script (120-160 words) that explains this concept at the
requested depth in the requested language. Do NOT add facts that aren't in
the source chunks. If the chunks are insufficient, end the script with the
literal marker "[NEEDS_MORE_SOURCE]".
""",
    required_vars=["concept", "level", "language", "retrieved_chunks"],
)

QUESTION_TEMPLATE = PromptTemplate(
    """
Concept: {concept}
Depth: {level}
Language: {language}

Generate a single checkpoint question that tests conceptual understanding
(not rote recall). Return JSON:
{{
  "type": "mcq" | "short_answer" | "conceptual",
  "prompt": "<the question>",
  "options": ["a","b","c","d"] | null,
  "correct_answer": "<answer or option letter>",
  "expected_reasoning": "<one-sentence why>"
}}
""",
    required_vars=["concept", "level", "language"],
)

MISCONCEPTION_TEMPLATE = PromptTemplate(
    """
Student answered: {student_answer}
Correct answer: {correct_answer}
Concept: {concept}
Original explanation: {original_explanation}

Diagnose the likely misconception (one short sentence), then produce a
re-explanation that uses a DIFFERENT analogy or example than the original.
Return JSON:
{{
  "misconception": "<short diagnosis>",
  "re_explanation": "<120-160 word re-teach script, different analogy>"
}}
""",
    required_vars=["student_answer", "correct_answer", "concept", "original_explanation"],
)

ASSESSMENT_REPORT_TEMPLATE = PromptTemplate(
    """
Lesson segments taught:
{segments_taught}

Student answers (one per checkpoint):
{answers_summary}

Analyze the student's performance and return JSON with ALL of these fields:
{{
  "score": <a numeric float from 0 to 100, MUST be a number not a string>,
  "strong_areas": ["list of concepts the student understood well"],
  "weak_areas": ["list of concepts the student struggled with"],
  "recommendation": "<one concrete next action for the student>"
}}

If the student had no checkpoint answers, set score to 50 and give a
general recommendation based on the lesson content.
ALL fields are REQUIRED — do NOT omit any field.
""",
    required_vars=["segments_taught", "answers_summary"],
)

LEARNING_PATH_TEMPLATE = PromptTemplate(
    """
Broad topic: {broad_topic}
Student level: {level}

Break this broad topic into an ordered list of sub-topics (5-10 items)
suitable for sequential study. Return JSON:
{{
  "items": ["sub-topic 1", "sub-topic 2", "..."]
}}
""",
    required_vars=["broad_topic", "level"],
)

CRAG_QUERY_REWRITE_TEMPLATE = PromptTemplate(
    """
Original search query: {query}

The previous search returned insufficient or low-relevance excerpts from the textbook.
Reformulate this query into a single focused, search-friendly query phrase using standard
textbook terminology, chapter keywords, and core concepts.

Return JSON:
{{
  "reformulated_query": "<focused query phrase>"
}}
""",
    required_vars=["query"],
)

CONCEPT_DEPENDENCY_GRAPH_TEMPLATE = PromptTemplate(
    """
Broad topic: {broad_topic}
Student level: {level}

Decompose this topic into 5-8 atomic, sequential sub-concepts.
For each sub-concept, specify prerequisite relationships: which earlier concepts must be mastered first?

Return JSON:
{{
  "concepts": ["Foundational Concept A", "Concept B", "Concept C", ...],
  "edges": [
    ["Foundational Concept A", "Concept B"],
    ["Concept B", "Concept C"]
  ]
}}

CRITICAL RULES:
1. Each edge is [prerequisite, dependent_concept] — meaning prerequisite must be learned before dependent_concept.
2. Every concept mentioned in "edges" MUST be included in the "concepts" list.
3. No circular dependencies or self-loops allowed.
""",
    required_vars=["broad_topic", "level"],
)
