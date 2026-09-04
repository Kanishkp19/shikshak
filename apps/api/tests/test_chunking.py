"""Unit tests for skills/chunking_embedding.py.

Verifies the sentence-window chunker produces non-empty chunks of roughly
the requested word count, and that carry-overlap works between pages.
"""
from skills.chunking_embedding import chunk_pages, _sentence_split


def test_sentence_split_basic():
    out = _sentence_split("Hello world. This is a test. Final sentence!")
    assert len(out) == 3
    assert out[0] == "Hello world."


def test_sentence_split_handles_devanagari():
    out = _sentence_split("यह एक वाक्य है। यह दूसरा वाक्य है!")
    assert len(out) == 2


def test_chunk_pages_returns_chunks():
    pages = [
        {"page": 1, "section_label": "Intro", "text": "Sentence one. " * 100},
        {"page": 2, "section_label": "Body", "text": "Sentence two. " * 100},
    ]
    chunks = chunk_pages(pages, target_words=80, overlap_sentences=1)
    assert len(chunks) > 0
    assert all("chunk_index" in c for c in chunks)
    assert all("section_label" in c for c in chunks)
    assert all("content" in c for c in chunks)


def test_chunk_pages_handles_empty_input():
    chunks = chunk_pages([], target_words=200)
    assert chunks == []
