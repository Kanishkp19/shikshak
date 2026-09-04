"""
Shikshak AI — DOCX parsing skill.

Wraps python-docx with a single function returning paragraph chunks.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_docx(file_path: str | Path) -> dict[str, Any]:
    """Parse a DOCX file into paragraphs grouped by heading.

    Returns:
        {
            "page_count": <count of top-level sections>,
            "pages": [{"page": int, "text": str, "section_label": str}]
        }
    """
    try:
        from docx import Document  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "python-docx not installed — pip install python-docx"
        ) from e

    doc = Document(str(file_path))
    pages: list[dict] = []
    current_section = "Document"
    current_buf: list[str] = []
    section_idx = 0

    def flush() -> None:
        nonlocal section_idx, current_buf
        if current_buf:
            section_idx += 1
            pages.append(
                {
                    "page": section_idx,
                    "section_label": current_section,
                    "text": "\n".join(current_buf).strip(),
                }
            )
            current_buf = []

    for para in doc.paragraphs:
        text = (para.text or "").replace("\x00", "").replace("\u0000", "").strip()
        if not text:
            continue
        style = (para.style.name or "").lower()
        if "heading" in style:
            flush()
            current_section = text
        else:
            current_buf.append(text)
    flush()
    return {"page_count": len(pages), "pages": pages}
