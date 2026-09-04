"""
Shikshak AI — chunking + embedding skill.

Sentence-window chunker with optional overlap, plus an embedding call that
prefers Gemini's text-embedding-004 and falls back to a local sentence-transformers
model (per 02-TRD.md). Every chunk keeps a section_label so the explanation
agent can cite where a fact came from.
"""
from __future__ import annotations

from typing import Any
import hashlib
import os
import re


def _sentence_split(text: str) -> list[str]:
    """Cheap sentence splitter — handles Latin + Devanagari sentence enders."""
    parts = re.split(r"(?<=[.!?।])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_pages(
    pages: list[dict],
    target_words: int = 200,
    overlap_sentences: int = 2,
) -> list[dict]:
    """Sentence-window chunker.

    Args:
        pages: list of {"page": int, "section_label"?: str, "text": str}
        target_words: aim for chunks of approximately this many words.
        overlap_sentences: carry this many trailing sentences into the next chunk.

    Returns:
        list of {
            "chunk_index": int,
            "content": str,
            "section_label": str,
            "page": int,
        }
    """
    out: list[dict] = []
    idx = 0
    carry: list[str] = []
    for page in pages:
        section_label = page.get("section_label") or f"Page {page.get('page', '?')}"
        page_num = page.get("page")
        sentences = _sentence_split(page.get("text", ""))
        if carry:
            sentences = carry + sentences
            carry = []
        buf: list[str] = []
        buf_words = 0
        for s in sentences:
            buf.append(s)
            buf_words += len(s.split())
            if buf_words >= target_words:
                out.append(
                    {
                        "chunk_index": idx,
                        "content": " ".join(buf),
                        "section_label": section_label,
                        "page": page_num,
                    }
                )
                idx += 1
                carry = buf[-overlap_sentences:] if overlap_sentences > 0 else []
                buf = []
                buf_words = 0
        # remaining buffer stays as carry-forward to next page
        if buf:
            carry.extend(buf)
    if carry:
        out.append(
            {
                "chunk_index": idx,
                "content": " ".join(carry),
                "section_label": "Tail",
                "page": pages[-1].get("page") if pages else None,
            }
        )
    return out


# ── Embeddings ───────────────────────────────────────────────────────────────
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings using Gemini text-embedding-004, or fall back
    to sentence-transformers bge-small-en if Gemini is unavailable.

    Returns one 768-d (or 384-d for bge) vector per input text.
    """
    from config import settings

    if settings.gemini_api_key:
        try:
            return _embed_gemini(texts)
        except Exception:
            pass  # fall through to local

    return _embed_local(texts)


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    import google.generativeai as genai  # type: ignore
    from config import settings

    genai.configure(api_key=settings.gemini_api_key)
    model = "models/gemini-embedding-001"
    out: list[list[float]] = []
    # batched to keep under per-request limits
    batch = 64
    for i in range(0, len(texts), batch):
        slice_ = texts[i : i + batch]
        res = genai.embed_content(
            model=model,
            content=slice_,
            output_dimensionality=768,
        )
        out.extend([list(v) for v in res["embedding"]])
    return out


def _embed_local(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer  # type: ignore

    model = SentenceTransformer("BAAI/bge-small-en")
    raw_vecs = model.encode(texts, normalize_embeddings=True).tolist()
    # Pad to 768 dimensions if needed so pgvector vector(768) constraint never fails
    return [v + [0.0] * (768 - len(v)) if len(v) < 768 else v[:768] for v in raw_vecs]


def embed_query(text: str) -> list[float]:
    """Embed a single query string (used by the knowledge_retrieval agent)."""
    return embed_texts([text])[0]
