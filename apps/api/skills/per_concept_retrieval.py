"""
Shikshak AI — Per-Concept Retrieval Skill.

Single responsibility: given a concept name + document_id, retrieve the
most relevant chunks from the document specifically for that concept.

This is different from the bulk knowledge_retrieval agent (which does one
query for the whole session). This skill is called once per segment so
each segment's explanation is grounded in the *right part* of the source
document — not a one-size-fits-all set of chunks.

Usage:
    from skills.per_concept_retrieval import retrieve_for_concept

    chunks = retrieve_for_concept(
        concept="Chemical Equations",
        document_id="doc-uuid",
        source_text="optional hint text from pdf structure",
        top_k=5,
    )
"""
from __future__ import annotations

from typing import Any, Optional

from skills.chunking_embedding import embed_query
from skills.supabase_persistence import get_client


def retrieve_for_concept(
    *,
    concept: str,
    document_id: str,
    source_text: Optional[str] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.25,
) -> list[dict[str, Any]]:
    """Retrieve chunks most relevant to `concept` from `document_id`.

    Args:
        concept: The segment's concept title (e.g. "Chemical Equations")
        document_id: UUID of the ingested document
        source_text: Optional text hint from pdf_structure_extraction
                     (used to build a richer query embedding)
        top_k: Number of chunks to return
        similarity_threshold: Min cosine similarity to include

    Returns:
        List of chunk dicts: {id, document_id, chunk_index, content,
                              section_label, similarity}

    Falls back to empty list (never raises) so the explanation agent
    can degrade gracefully to a generic-but-marked explanation.
    """
    if not document_id:
        return []

    try:
        # Build a rich query: concept title + first sentence of source_text
        query = _build_query(concept, source_text)
        query_embedding = embed_query(query)

        client = get_client()
        res = client.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_embedding,
                "filter_doc_id": document_id,
                "match_count": top_k,
                "threshold": similarity_threshold,
            },
        ).execute()
        return res.data or []

    except Exception as e:
        print(f"[per_concept_retrieval] Failed for concept '{concept}': {e}")
        return []


def retrieve_for_concept_with_fallback(
    *,
    concept: str,
    document_id: Optional[str],
    source_text: Optional[str] = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Same as retrieve_for_concept but handles missing document_id gracefully.

    Use this in the explanation step of the orchestrator — it safely returns
    [] when there's no document (topic-only session).
    """
    if not document_id:
        return []
    return retrieve_for_concept(
        concept=concept,
        document_id=document_id,
        source_text=source_text,
        top_k=top_k,
    )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_query(concept: str, source_text: Optional[str]) -> str:
    """Compose a rich query string for better embedding similarity."""
    if not source_text:
        return concept

    # Take first ~150 chars of source_text as a query hint
    hint = source_text.strip()[:150].rsplit(" ", 1)[0]  # don't cut mid-word
    return f"{concept}: {hint}"
