"""
Shikshak AI — Lesson Planning Agent (v3).

Two modes:
  document mode: uses document_curriculum skill to derive segments directly
                 from the PDF's own structure (headings, sections, formulas).
                 Segment list = [Overview] + [one per PDF heading].
  topic mode:    falls back to LLM-invented plan (unchanged from v2).

Each segment includes:
  - concept:          heading from PDF (or LLM-invented topic)
  - source_text:      actual text from the PDF section (document mode only)
  - related_concepts: adjacent headings for deep-dive navigation
  - segment_type:     "core" | "deep_dive" | "checkpoint"
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field
from typing import Literal

from celery_app import celery_app
from agents.llm import get_content_llm
from skills.json_schema_validation import call_llm_with_retry
from skills.prompt_templating import SYSTEM_TEACHER
from skills.document_curriculum import build_curriculum


class SegmentBrief(BaseModel):
    concept: str
    depth: Literal["beginner", "intermediate", "advanced"]
    visual_type: Literal["diagram", "equation", "code", "animation", "none"]
    has_checkpoint: bool = False
    related_concepts: list[str] = Field(default_factory=list)
    segment_type: Literal["core", "deep_dive", "checkpoint"] = "core"


class LessonPlan(BaseModel):
    segments: list[SegmentBrief] = Field(default_factory=list)


# LLM fallback prompt (topic-only sessions / PDF structure extraction failed)
_LESSON_PLAN_PROMPT = """\
You are Shikshak, an expert AI teacher designing a lesson plan.

Topic: {topic}
Level: {level}
Time budget: {time_budget_minutes} minutes
Language: {language}
Source material available: {has_source}
Previously weak concepts for this student: {weak_concepts}

Return a JSON object with one field "segments" — an ordered array where each
element has:
  - concept: short concept title (2-5 words, specific and unique)
  - depth: "beginner" | "intermediate" | "advanced"
  - visual_type: "diagram" | "equation" | "code" | "animation" | "none"
  - has_checkpoint: boolean — true if a checkpoint question should follow
  - related_concepts: array of 3-5 related sub-topics the student can explore next
  - segment_type: "core" for main lesson content

CRITICAL RULES:
1. Start with a brief overview segment as the very first segment.
2. Each subsequent segment MUST teach something specific and different.
3. related_concepts MUST be genuinely related sub-topics.
4. Limit segment count so total expected talking time fits the time budget at
   ~120 words per minute.
5. At least one segment must have has_checkpoint=true when time_budget_minutes >= 10.
6. The lesson should progress from foundational concepts to more complex ones.
"""


def plan_lesson(
    *,
    topic: str,
    level: str,
    time_budget_minutes: int,
    language: str,
    has_source: bool,
    weak_concepts: list[str],
    document_id: Optional[str] = None,
    pdf_structure: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Return a validated lesson plan as a dict.

    When pdf_structure is provided (document mode), uses the document_curriculum
    skill to derive the plan directly from PDF headings — no LLM invention.

    When pdf_structure is None or empty (topic mode), falls back to the LLM.
    """
    # ── Document mode: curriculum from PDF structure ──────────────────────────
    if pdf_structure and pdf_structure.get("sections"):
        try:
            curriculum = build_curriculum(
                pdf_structure,
                level=level,
                time_budget_minutes=time_budget_minutes,
                language=language,
            )
            print(
                f"[lesson_planning] Document mode: {len(curriculum['segments'])} segments "
                f"from PDF structure ({len(pdf_structure['sections'])} sections detected)"
            )
            return curriculum
        except Exception as e:
            print(f"[lesson_planning] Document curriculum failed, falling back to LLM: {e}")

    # ── Topic mode (or PDF structure fallback): LLM-invented plan ────────────
    effective_topic = topic or "the uploaded document"
    prompt = SYSTEM_TEACHER.render() + "\n\n" + _LESSON_PLAN_PROMPT.format(
        topic=effective_topic,
        level=level,
        time_budget_minutes=time_budget_minutes,
        language=language,
        has_source=has_source,
        weak_concepts=", ".join(weak_concepts) or "(none)",
    )
    llm = get_content_llm()
    plan = call_llm_with_retry(llm, prompt, LessonPlan, model_name="lesson_planning")
    segments_out = []
    for i, s in enumerate(plan.segments):
        segments_out.append(
            {
                "order": i + 1,
                "concept": s.concept,
                "depth": s.depth,
                "visual_type": s.visual_type,
                "has_checkpoint": s.has_checkpoint,
                "narration_script": "",
                "source_text": "",
                "related_concepts": s.related_concepts,
                "segment_type": s.segment_type,
            }
        )
    return {
        "segments": segments_out,
        "document_id": document_id,
        "per_segment_words": max(100, (120 * time_budget_minutes) // max(1, len(segments_out))),
        "language": language,
    }


@celery_app.task(name="agents.lesson_planning.run")
def run(
    topic: str,
    level: str,
    time_budget_minutes: int,
    language: str,
    has_source: bool,
    weak_concepts: list[str],
    document_id: Optional[str] = None,
    pdf_structure: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    return plan_lesson(
        topic=topic,
        level=level,
        time_budget_minutes=time_budget_minutes,
        language=language,
        has_source=has_source,
        weak_concepts=weak_concepts,
        document_id=document_id,
        pdf_structure=pdf_structure,
    )
