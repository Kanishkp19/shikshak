"""
Shikshak AI — Content Ingestion Agent.

Single responsibility: take an uploaded file (PDF/DOCX/PPTX), parse it,
chunk it, embed it, and persist the chunks to `document_chunks`. For PDFs,
also runs deep structure extraction (headings, sections, formulas) so the
orchestrator can build a proper curriculum from the document's own structure.

Inputs:  document_id (from the documents table)
Outputs: {document_id, status, chunk_count, page_count, structure}
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from celery_app import celery_app
from skills import pdf_parsing, docx_parsing, pptx_parsing, chunking_embedding
from skills.pdf_structure_extraction import extract_pdf_structure
from skills.supabase_persistence import (
    get_document, set_document_status, insert_chunks,
)


def _parse(file_path: str, file_type: str) -> dict[str, Any]:
    if file_type == "pdf":
        return pdf_parsing.parse_pdf(file_path)
    if file_type == "docx":
        return docx_parsing.parse_docx(file_path)
    if file_type == "pptx":
        return pptx_parsing.parse_pptx(file_path)
    raise ValueError(f"Unsupported file_type: {file_type}")


def ingest_document(document_id: str) -> dict[str, Any]:
    """Synchronous entry point (also called from the FastAPI request handler
    when the user wants a faster response than the Celery queue can give).

    For PDFs: also runs deep structure extraction to get headings/sections
    so the orchestrator can build a curriculum from the document structure.
    """
    doc = get_document(document_id)
    if not doc:
        raise FileNotFoundError(f"Document {document_id} not found")
    if not os.path.exists(doc["storage_path"]):
        set_document_status(document_id, "failed")
        raise FileNotFoundError(f"Storage path missing: {doc['storage_path']}")

    t0 = time.time()
    try:
        parsed = _parse(doc["storage_path"], doc["file_type"])
        chunks = chunking_embedding.chunk_pages(parsed["pages"])
        embeddings = chunking_embedding.embed_texts([c["content"] for c in chunks])
        rows = [
            {
                "document_id": document_id,
                "chunk_index": c["chunk_index"],
                "content": c["content"],
                "section_label": c.get("section_label"),
                "embedding": embeddings[i] if i < len(embeddings) else None,
            }
            for i, c in enumerate(chunks)
        ]
        insert_chunks(rows)

        # Deep structural extraction for PDFs — produces headings, sections,
        # formulas. Stored in the result so the orchestrator can build a
        # proper curriculum without another disk read.
        pdf_structure: dict[str, Any] = {}
        if doc["file_type"] == "pdf":
            try:
                pdf_structure = extract_pdf_structure(doc["storage_path"])
            except Exception as struct_err:
                print(f"[content_ingestion] PDF structure extraction failed (non-fatal): {struct_err}")

        set_document_status(document_id, "ready", page_count=parsed["page_count"])
        return {
            "document_id": document_id,
            "status": "ready",
            "chunk_count": len(rows),
            "page_count": parsed["page_count"],
            "pdf_structure": pdf_structure,
            "duration_ms": int((time.time() - t0) * 1000),
        }
    except Exception as e:
        set_document_status(document_id, "failed")
        raise


@celery_app.task(name="agents.content_ingestion.run")
def run(document_id: str) -> dict[str, Any]:
    """Celery task wrapper for the Content Ingestion Agent."""
    return ingest_document(document_id)
