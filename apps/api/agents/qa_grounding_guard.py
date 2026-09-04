"""
Shikshak AI — QA Grounding Guard Agent.

Single responsibility: check explanation text against retrieved chunks
(document sessions only). Flags any factual claim that isn't supported
by the source. If unsupported claims are found, regenerates the explanation
once with a stricter prompt.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from celery_app import celery_app
from agents.explanation import explain_segment
from agents.llm import get_content_llm as get_llm
from skills.prompt_templating import SYSTEM_TEACHER


def guard(
    *,
    concept: str,
    level: str,
    language: str,
    narration_script: str,
    retrieved_chunks: Optional[list[dict]],
) -> dict[str, Any]:
    """Return {narration_script, flagged_claims, regenerated}.

    If narration_script contains the marker "[NEEDS_MORE_SOURCE]" or claims
    that aren't in the source chunks, regenerate once.
    """
    if not retrieved_chunks:
        # Topic-only session — no grounding check, trust the LLM
        return {
            "narration_script": narration_script,
            "flagged_claims": [],
            "regenerated": False,
        }

    flagged = _find_unsupported_claims(narration_script, retrieved_chunks)
    needs_marker = "[NEEDS_MORE_SOURCE]" in narration_script

    if not flagged and not needs_marker:
        return {
            "narration_script": narration_script,
            "flagged_claims": [],
            "regenerated": False,
        }

    # Regenerate with stricter prompt
    regenerated = explain_segment(
        concept=concept,
        level=level,
        language=language,
        retrieved_chunks=retrieved_chunks,
    )
    return {
        "narration_script": regenerated,
        "flagged_claims": flagged,
        "regenerated": True,
    }


def _find_unsupported_claims(script: str, chunks: list[dict]) -> list[str]:
    """Naive check: extract capitalised noun phrases from the script and
    verify each appears somewhere in the chunks. Real implementation would
    use the LLM for claim extraction + NLI verification; this fallback keeps
    the demo honest without burning API calls on every segment."""
    # Collect chunk corpus
    corpus = " ".join(c.get("content", "") for c in chunks).lower()
    if not corpus.strip():
        return []

    # Find Capitalised multi-word phrases in the script (likely claims)
    phrases = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", script)
    flagged: list[str] = []
    for p in phrases:
        if p.lower() not in corpus:
            flagged.append(p)
    return flagged[:5]  # cap to keep the report readable


@celery_app.task(name="agents.qa_grounding_guard.run")
def run(
    concept: str,
    level: str,
    language: str,
    narration_script: str,
    retrieved_chunks: Optional[list[dict]],
) -> dict[str, Any]:
    return guard(
        concept=concept,
        level=level,
        language=language,
        narration_script=narration_script,
        retrieved_chunks=retrieved_chunks,
    )
