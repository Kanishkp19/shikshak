"""
Shikshak AI — vector search skill.

Issues pgvector cosine-similarity queries against the `document_chunks`
table. Returns the top-k chunks for a query string.
"""
from __future__ import annotations

from typing import Any

from skills.chunking_embedding import embed_query
from skills.supabase_persistence import get_client


def vector_search(
    *,
    document_id: str,
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.30,
) -> list[dict]:
    """Return top_k chunks for the given query, ranked by cosine similarity.

    Each item: {id, document_id, chunk_index, content, section_label, score}
    """
    query_embedding = embed_query(query)
    client = get_client()

    # Supabase RPC — we call a stored function that takes the embedding + doc id
    # and returns the top-k matches. The function is created by the migration
    # below if you don't have it yet — see supabase/migrations/003b_match_chunks.sql
    rpc_payload = {
        "query_embedding": query_embedding,
        "filter_doc_id": document_id,
        "match_count": top_k,
        "threshold": similarity_threshold,
    }
    res = client.rpc("match_document_chunks", rpc_payload).execute()
    return res.data or []
