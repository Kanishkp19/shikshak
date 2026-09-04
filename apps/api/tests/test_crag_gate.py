"""
Unit tests for Work Stream 3: Corrective RAG (CRAG-lite) Relevance Gate.
"""
from unittest.mock import MagicMock, patch

from agents.knowledge_retrieval import (
    RetrievalChunkList,
    retrieve,
    retrieve_with_crag,
)
from skills.crag_relevance_gate import (
    CragResult,
    combined_score,
    gate,
    keyword_overlap_score,
)


def test_keyword_overlap_score():
    """Verify lexical token overlap calculation."""
    query = "photosynthesis in green plants"
    # Chunk with high overlap
    chunk_high = "Photosynthesis occurs in green plant cells containing chloroplasts."
    score_high = keyword_overlap_score(query, chunk_high)
    assert score_high > 0.5

    # Chunk with zero overlap
    chunk_zero = "Quantum mechanics governs particle spin and wavefunction collapse."
    score_zero = keyword_overlap_score(query, chunk_zero)
    assert score_zero == 0.0


def test_combined_score():
    """Verify composite cosine_sim + keyword_overlap scoring."""
    query = "Newton second law acceleration"
    chunk = "Newton's second law relates force, mass, and acceleration."
    kw_score = keyword_overlap_score(query, chunk)
    cosine_sim = 0.65
    comb = combined_score(cosine_sim, query, chunk)
    assert comb == round(cosine_sim + kw_score, 4)


def test_gate_pure_offline_actions():
    """Verify the gate function with synthetic chunks:
    - all-high-score -> proceed
    - all-low-score -> decline
    - mixed (<50% passing) -> reformulate_retry
    Runs 100% offline with zero network calls."""
    chunk_a = {"id": "1", "content": "Relevant content A"}
    chunk_b = {"id": "2", "content": "Relevant content B"}
    chunk_c = {"id": "3", "content": "Irrelevant noise C"}
    chunk_d = {"id": "4", "content": "Irrelevant noise D"}

    # 1. All high scores (>= 0.25) -> proceed
    high_scored = [(chunk_a, 0.85), (chunk_b, 0.72)]
    res_proceed = gate(high_scored, threshold=0.25)
    assert res_proceed.action == "proceed"
    assert len(res_proceed.chunks) == 2
    assert res_proceed.not_covered is False

    # 2. All low scores (< 0.25) -> decline
    low_scored = [(chunk_c, 0.12), (chunk_d, 0.05)]
    res_decline = gate(low_scored, threshold=0.25)
    assert res_decline.action == "decline"
    assert len(res_decline.chunks) == 0
    assert res_decline.not_covered is True

    # 3. Mixed scores (< 50% passing, e.g. 1 passing out of 4) -> reformulate_retry
    mixed_scored = [(chunk_a, 0.60), (chunk_b, 0.10), (chunk_c, 0.08), (chunk_d, 0.12)]
    res_retry = gate(mixed_scored, threshold=0.25)
    assert res_retry.action == "reformulate_retry"
    assert len(res_retry.chunks) == 1
    assert res_retry.chunks[0]["id"] == "1"


def test_crag_retrieval_flow_decline_and_proceed():
    """Verify retrieve_with_crag with mocked vector_search to confirm gate wiring."""
    doc_id = "doc-test-456"

    # Test case 1: Vector search returns low score chunks -> decline
    low_chunks = [
        {"id": "c1", "similarity": 0.05, "content": "Unrelated chapter on geology"},
        {"id": "c2", "similarity": 0.02, "content": "Glossary index table"},
    ]
    with patch("skills.vector_search.vector_search", return_value=low_chunks), \
         patch("agents.knowledge_retrieval.log_agent_run") as mock_log:

        res = retrieve_with_crag(
            query="quantum entanglement EPR paradox",
            document_id=doc_id,
            threshold=0.25,
        )
        assert res.action == "decline"
        assert res.not_covered is True
        assert len(res.chunks) == 0

    # Test case 2: Vector search returns high score chunks -> proceed
    high_chunks = [
        {"id": "c3", "similarity": 0.75, "content": "Quantum entanglement and the EPR paradox explanation."},
        {"id": "c4", "similarity": 0.80, "content": "Bell test experiments verifying entanglement."},
    ]
    with patch("skills.vector_search.vector_search", return_value=high_chunks), \
         patch("agents.knowledge_retrieval.log_agent_run") as mock_log:

        res = retrieve_with_crag(
            query="quantum entanglement EPR paradox",
            document_id=doc_id,
            threshold=0.25,
        )
        assert res.action == "proceed"
        assert res.not_covered is False
        assert len(res.chunks) == 2


def test_retrieval_chunk_list_subclass():
    """Verify RetrievalChunkList maintains list behavior while preserving CRAG metadata."""
    items = [{"id": "1"}, {"id": "2"}]
    chunk_list = RetrievalChunkList(items, not_covered=False, crag_action="proceed")

    assert len(chunk_list) == 2
    assert chunk_list[0] == {"id": "1"}
    assert chunk_list.not_covered is False
    assert chunk_list.crag_action == "proceed"
    assert isinstance(chunk_list, list)
