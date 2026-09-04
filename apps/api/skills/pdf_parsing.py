"""
Shikshak AI — PDF parsing skill.

Wraps PyMuPDF (fitz) with a single function returning page-level chunks
suitable for the chunking+embedding skill.

Pure function — no Supabase or LLM calls — so it's unit-testable in isolation.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any


def _sanitize_page_text(text: str) -> str:
    """Strip non-printable and garbled Unicode from page text."""
    if not text:
        return ""
    # Remove null bytes
    text = text.replace("\x00", "").replace("\u0000", "")
    # Remove replacement character
    text = text.replace("\ufffd", "")
    # Strip Private Use Area characters (font-specific glyphs)
    text = re.sub(r"[\ue000-\uf8ff]", "", text)
    # Strip control characters except newline/tab/space
    cleaned = []
    for ch in text:
        if ch in ("\n", "\t", " "):
            cleaned.append(ch)
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("C"):
            continue
        cleaned.append(ch)
    return "".join(cleaned).strip()


def parse_pdf(file_path: str | Path) -> dict[str, Any]:
    """Parse a PDF file into pages of plain text.

    Returns:
        {
            "page_count": int,
            "pages": [{"page": int, "text": str}]
        }
    """
    try:
        import fitz  # type: ignore  # PyMuPDF
    except ImportError as e:
        raise RuntimeError(
            "PyMuPDF (pymupdf) not installed — pip install pymupdf"
        ) from e

    doc = fitz.open(str(file_path))
    pages: list[dict] = []
    for i, page in enumerate(doc, start=1):
        text = _sanitize_page_text(page.get_text("text") or "")
        pages.append({"page": i, "text": text})
    doc.close()
    return {"page_count": len(pages), "pages": pages}
