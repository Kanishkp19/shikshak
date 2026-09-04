"""
Shikshak AI — Corrective RAG (CRAG-lite) Relevance Gate skill.

Single responsibility: deterministic, offline scoring of retrieved chunks
against a query to prevent ungrounded generation or hallucinations.
Decides whether to proceed, reformulate the query once, or explicitly decline.
"""
from __future__ import annotations

import re
from typing import Any, Literal
from pydantic import BaseModel, Field

_STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "is",
    "are", "was", "were", "what", "how", "why", "who", "which", "this", "that",
    "from", "by", "with", "about", "into", "through", "during", "before", "after",
}


class CragResult(BaseModel):
    action: Literal["proceed", "reformulate_retry", "decline"]
    chunks: list[dict[str, Any]] = Field(default_factory=list)
    not_covered: bool = False


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase alphanumeric words."""
    words = re.findall(r"\b[a-z0-9_]+\b", (text or "").lower())
    filtered = {w for w in words if len(w) > 1 and w not in _STOPWORDS}
    return filtered or set(words)


def keyword_overlap_score(query: str, chunk_text: str) -> float:
    """Calculate token-overlap ratio between query and chunk content."""
    q_tokens = _tokenize(query)
    if not q_tokens:
        return 0.0
    c_tokens = set(re.findall(r"\b[a-z0-9_]+\b", (chunk_text or "").lower()))
    overlap = len(q_tokens & c_tokens)
    return round(overlap / len(q_tokens), 4)


def combined_score(cosine_sim: float, query: str, chunk_text: str) -> float:
    """Combine vector cosine similarity with lexical keyword overlap.

    Returns a composite score: cosine_sim + keyword_overlap.
    """
    kw_score = keyword_overlap_score(query, chunk_text)
    return round(float(cosine_sim) + kw_score, 4)


def gate(
    chunks_with_scores: list[tuple[dict[str, Any], float]],
    threshold: float = 0.25,
) -> CragResult:
    """Determine CRAG action based on chunk scores against threshold.

    - If no chunks pass threshold: action="decline"
    - If < 50% of candidate chunks pass: action="reformulate_retry" (only passing returned)
    - If >= 50% of candidate chunks pass: action="proceed"
    """
    if not chunks_with_scores:
        return CragResult(action="decline", chunks=[], not_covered=True)

    passing = [c for c, s in chunks_with_scores if s >= threshold]
    if not passing:
        return CragResult(action="decline", chunks=[], not_covered=True)

    if len(passing) < len(chunks_with_scores) * 0.5:
        return CragResult(action="reformulate_retry", chunks=passing, not_covered=False)

    return CragResult(action="proceed", chunks=passing, not_covered=False)
