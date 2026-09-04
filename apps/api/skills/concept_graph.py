"""
Shikshak AI — Concept Graph Builder skill.

Given a main topic and current concept, uses LLM to generate a concept map
of related topics with brief descriptions and pedagogical ordering.
Used by the frontend to show a 'Related Concepts' panel and by the backend
to generate deep-dive segments on demand.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from agents.llm import get_content_llm as get_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.prompt_templating import SYSTEM_TEACHER


class ConceptNode(BaseModel):
    concept: str
    brief: str  # 1-sentence description
    prerequisite: bool = False  # True if this should be learned before the main concept
    difficulty: str = "same"  # "easier" | "same" | "harder"


class ConceptGraph(BaseModel):
    related: list[ConceptNode] = Field(default_factory=list)


_CONCEPT_GRAPH_PROMPT = """\
Topic area: {topic}
Current concept: {current_concept}
Student level: {level}

Return a JSON object with one field "related" — an array of 4-6 related concepts
the student should explore next. Each element has:
  - concept: short concept title (2-4 words)
  - brief: one-sentence description of what this concept covers
  - prerequisite: true if this concept is a prerequisite for the current concept
  - difficulty: "easier" | "same" | "harder" relative to the current concept

Order by pedagogical sequence: prerequisites first, then same-level, then harder.
Make concepts specific and genuinely useful — not generic filler.
"""


def build_concept_graph(
    topic: str,
    current_concept: str,
    level: str = "intermediate",
) -> ConceptGraph:
    """Generate a concept map of related topics for the given concept."""
    prompt = SYSTEM_TEACHER.render() + "\n\n" + _CONCEPT_GRAPH_PROMPT.format(
        topic=topic,
        current_concept=current_concept,
        level=level,
    )
    try:
        llm = get_llm()
        graph = call_llm_with_retry(llm, prompt, ConceptGraph, model_name="concept_graph")
        return graph
    except Exception:
        # Fallback: return empty graph
        return ConceptGraph(related=[])


def get_concept_graph_dict(
    topic: str,
    current_concept: str,
    level: str = "intermediate",
) -> list[dict[str, Any]]:
    """Convenience wrapper returning a plain dict list for API responses."""
    graph = build_concept_graph(topic, current_concept, level)
    return [
        {
            "concept": node.concept,
            "brief": node.brief,
            "prerequisite": node.prerequisite,
            "difficulty": node.difficulty,
        }
        for node in graph.related
    ]
