"""
Shikshak AI — Knowledge Retrieval Agent.

Single responsibility: given a topic/concept + (optional) document_id,
return the top-k retrieved source chunks gated by Corrective RAG (CRAG-lite).

After pgvector similarity search, chunks are scored using combined_score()
(cosine similarity + lexical overlap) and passed through gate():
- "proceed": chunks returned directly.
- "reformulate_retry": query reformulated once via LLM, re-queried and re-gated.
- "decline": explicit not_covered=True flag returned, preventing hallucinated generation.

Sits strictly before QA Grounding Guard.
"""
from __future__ import annotations

import logging
from typing import Any, Optional
from pydantic import BaseModel

from celery_app import celery_app
from agents.llm import get_content_llm as get_llm
from skills import vector_search
from skills.crag_relevance_gate import (
    CragResult,
    combined_score,
    gate,
)
from skills.json_schema_validation import call_llm_with_retry
from skills.prompt_templating import CRAG_QUERY_REWRITE_TEMPLATE
from skills.supabase_persistence import log_agent_run

logger = logging.getLogger(__name__)


class QueryRewrite(BaseModel):
    reformulated_query: str


class RetrievalChunkList(list):
    """Subclass of list that carries CRAG gating metadata while behaving as a plain list."""
    def __init__(self, items: list[dict[str, Any]], not_covered: bool = False, crag_action: str = "proceed"):
        super().__init__(items)
        self.not_covered = not_covered
        self.crag_action = crag_action


def _score_chunks(chunks: list[dict[str, Any]], query: str) -> list[tuple[dict[str, Any], float]]:
    """Compute combined similarity + lexical overlap score for each chunk."""
    scored = []
    for c in chunks:
        sim = float(c.get("similarity", 0.0) or c.get("score", 0.0))
        content = c.get("content", "")
        s = combined_score(sim, query, content)
        scored.append((c, s))
    return scored


def _reformulate_query(query: str) -> str:
    """Rewrite query using textbook-focused terminology to rescue partial matches."""
    try:
        llm = get_llm()
        prompt = CRAG_QUERY_REWRITE_TEMPLATE.render(query=query)
        res = call_llm_with_retry(llm, prompt, QueryRewrite, model_name="crag_rewrite")
        return res.reformulated_query.strip() or query
    except Exception as e:
        logger.warning("[knowledge_retrieval] Query reformulation failed (%s); using original", e)
        return query


def retrieve_with_crag(
    *,
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5,
    threshold: float = 0.25,
    session_id: Optional[str] = None,
) -> CragResult:
    """Execute CRAG-gated retrieval returning a structured CragResult."""
    if not document_id:
        # Topic-only session: no RAG grounding needed
        return CragResult(action="proceed", chunks=[], not_covered=False)

    # 1. Initial pgvector similarity query
    raw_chunks = vector_search.vector_search(
        document_id=document_id,
        query=query,
        top_k=top_k,
        similarity_threshold=0.0,  # capture candidates for gate scoring
    )

    if not raw_chunks:
        try:
            log_agent_run(
                session_id=session_id,
                agent_name="knowledge_retrieval",
                input_summary={"query": query, "document_id": document_id},
                output_summary={"crag_action": "decline", "reason": "no_raw_chunks_found"},
                status="success",
            )
        except Exception:
            pass
        return CragResult(action="decline", chunks=[], not_covered=True)

    # 2. Score candidate chunks
    scored_chunks = _score_chunks(raw_chunks, query)
    crag_res = gate(scored_chunks, threshold=threshold)

    # 3. If reformulate_retry: rewrite query once and re-gate
    if crag_res.action == "reformulate_retry":
        rewritten = _reformulate_query(query)
        retry_raw = vector_search.vector_search(
            document_id=document_id,
            query=rewritten,
            top_k=top_k,
            similarity_threshold=0.0,
        )
        if retry_raw:
            retry_scored = _score_chunks(retry_raw, rewritten)
            crag_res = gate(retry_scored, threshold=threshold)
        else:
            crag_res = CragResult(action="decline", chunks=[], not_covered=True)

    # 4. Log CRAG decision point to agent_run_logs
    try:
        log_agent_run(
            session_id=session_id,
            agent_name="knowledge_retrieval",
            input_summary={"query": query, "document_id": document_id, "top_k": top_k},
            output_summary={
                "crag_action": crag_res.action,
                "passing_chunks_count": len(crag_res.chunks),
                "not_covered": crag_res.not_covered,
            },
            status="success",
        )
    except Exception:
        pass

    return crag_res


def retrieve(
    *,
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5,
    session_id: Optional[str] = None,
) -> RetrievalChunkList:
    """Return top_k chunks for the query, filtered by CRAG relevance gate."""
    res = retrieve_with_crag(
        query=query,
        document_id=document_id,
        top_k=top_k,
        session_id=session_id,
    )
    return RetrievalChunkList(
        res.chunks,
        not_covered=res.not_covered,
        crag_action=res.action,
    )


@celery_app.task(name="agents.knowledge_retrieval.run")
def run(
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5,
    session_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    return list(retrieve(query=query, document_id=document_id, top_k=top_k, session_id=session_id))
