"""
Shikshak AI — PDF Structure Extraction Skill (v3).

Extracts deep, clean structural curriculum metadata from educational PDFs:
  - Chapter/Document Title (cleaned of noise and headers)
  - Table of contents (if present in PDF metadata)
  - Major educational sections & topics (filtered of callouts, activity boxes,
    figure captions, caution warnings, exercises, and shadow-text duplicates)
  - Full section text content, page ranges, and detected formulas

Works robustly on complex textbook layouts including NCERT, CBSE, university
handbooks, research papers, and standard PDF documents.

Usage:
    from skills.pdf_structure_extraction import extract_pdf_structure
    structure = extract_pdf_structure("/path/to/file.pdf")
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any


# ── Constants ────────────────────────────────────────────────────────────────

# Minimum words for a section to be kept standalone
_MIN_SECTION_WORDS_TO_KEEP = 20

# Math-ish patterns to detect formula lines
_MATH_RE = re.compile(r"[=→⟶⇌±Δ∑∏√∫≈≠≤≥²³⁴⁰¹⁺⁻⁼]|[A-Z][a-z]?\d+|→|⇌")

# Headings that are noise (callouts, activities, captions, questions, exercises)
_NOISE_HEADING_RE = re.compile(
    r"^(?:"
    r"activity\s*\d.*|"
    r"figure\s*\d.*|"
    r"fig\.\s*\d.*|"
    r"caution\s*:?.*|"
    r"table\s*\d.*|"
    r"do you know\??.*|"
    r"questions?\s*$|"
    r"what you have learnt.*|"
    r"think it over.*|"
    r"group\s+activity.*|"
    r"exercises?\s*$|"
    r"summary\s*$|"
    r"note\s*:?.*|"
    r"box\s*\d.*|"
    r"sidebar.*|"
    r"glossary.*|"
    r"index\s*$|"
    r"appendix.*|"
    r"solutions?\s*$|"
    r"answer\s*key.*|"
    r"\d+$|"
    r"\?+$|"
    r"[+=→/\\-]\s*\d+.*"
    r")$",
    re.IGNORECASE,
)

# Numbered section header pattern: "1.1 ...", "1.2.1 ...", "Chapter 2 ..."
_NUMBERED_SEC_RE = re.compile(
    r"^(?:(?:chapter|unit|section|part)\s*\d+[\s:.-]+)?(\d+\.\d+(?:\.\d+)?)\s*(.*)$",
    re.IGNORECASE,
)

# Concept keywords that signal a major section even without numbering
_CONCEPT_KEYWORDS = [
    "chemical equations",
    "balanced chemical equations",
    "writing a chemical equation",
    "types of chemical reactions",
    "combination reaction",
    "decomposition reaction",
    "displacement reaction",
    "double displacement reaction",
    "oxidation and reduction",
    "corrosion",
    "rancidity",
    "introduction",
    "overview",
    "mechanism",
    "properties",
    "classification",
    "structure",
    "applications",
    "synthesis",
    "equilibrium",
    "kinetics",
    "thermodynamics",
]


# ── Unicode sanitization ────────────────────────────────────────────────────

def _sanitize_text(text: str) -> str:
    """Strip non-printable, replacement, and garbled Unicode from extracted text."""
    if not text:
        return ""

    text = text.replace("\x00", "").replace("\u0000", "")
    text = text.replace("\ufffd", "")

    cleaned = []
    for ch in text:
        cp = ord(ch)
        if ch in ("\n", "\t", " "):
            cleaned.append(ch)
            continue
        if 0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD:
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("C"):
            continue
        cleaned.append(ch)

    result = "".join(cleaned).strip()
    result = re.sub(r"[ \t]{3,}", "  ", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def _is_mostly_garbage(text: str) -> bool:
    """Check if text is mostly non-ASCII garbage (PUA chars, symbols, etc.)."""
    if not text or len(text.strip()) < 2:
        return True
    non_space = [ch for ch in text if not ch.isspace()]
    if not non_space:
        return True
    normal = 0
    for ch in non_space:
        cp = ord(ch)
        if cp < 0x0300 or (0x0900 <= cp <= 0x097F) or (0x2000 <= cp <= 0x206F) or (0x2070 <= cp <= 0x209F) or (0x2200 <= cp <= 0x22FF):
            normal += 1
    return (normal / len(non_space)) < 0.4


# ── Public API ───────────────────────────────────────────────────────────────

def extract_pdf_structure(file_path: str | Path) -> dict[str, Any]:
    """Deep structural extraction of a PDF into clean educational sections.

    Returns:
        {
            "page_count": int,
            "document_title": str,
            "toc": [{"level": int, "title": str, "page": int}],
            "sections": [
                {
                    "heading": str,          # section title
                    "level": int,            # heading depth (1=top, 2=sub, …)
                    "page_start": int,
                    "page_end": int,
                    "text": str,             # full section body text
                    "formulas": [str],       # detected equation lines
                    "word_count": int,
                }
            ],
            "body_text": str,                # full document text
            "dominant_font_size": float,
        }
    """
    try:
        import fitz  # type: ignore  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("PyMuPDF not installed — pip install pymupdf") from exc

    doc = fitz.open(str(file_path))
    page_count = len(doc)

    # 1. Embedded Table of Contents (from PDF outline metadata, if present)
    toc = _extract_toc(doc)

    # 2. Extract clean page lines with shadow-text deduplication
    clean_pages = _extract_clean_pages(doc)
    doc.close()

    # 3. Infer clean Document / Chapter Title
    document_title = _extract_document_title(clean_pages, toc)

    # 4. Extract structured sections using numbered & semantic heading detection
    sections = _extract_sections(clean_pages, document_title)

    # 5. Merge tiny micro-sections into adjacent sections
    sections = _merge_tiny_sections(sections)

    # 6. Assemble full body text
    body_text = "\n\n".join(s["text"] for s in sections)

    print(
        f"[pdf_structure] Extracted {len(sections)} clean sections for '{document_title}' "
        f"across {page_count} pages"
    )

    return {
        "page_count": page_count,
        "document_title": document_title,
        "toc": toc,
        "sections": sections,
        "body_text": body_text,
        "dominant_font_size": 10.5,
    }


# ── Page-Level Extraction with Shadow Deduplication ─────────────────────────

def _extract_clean_pages(doc: Any) -> list[dict[str, Any]]:
    """Extract clean lines per page, removing 3D shadow text and vertical banners."""
    clean_pages = []

    for page_idx, page in enumerate(doc):
        raw_text = page.get_text("text") or ""
        raw_lines = raw_text.split("\n")
        dedup_lines: list[str] = []

        for line in raw_lines:
            line_s = _sanitize_text(line.strip())
            if not line_s:
                continue

            # Skip single-letter vertical banner glyphs (Q, U, E, S, T, I, O, N, S, ?, !)
            if len(line_s) == 1 and line_s in "QUESTIONS?EXERCISES!":
                continue

            # Skip garbage
            if _is_mostly_garbage(line_s):
                continue

            # Deduplicate shadow text:
            # Drop identical consecutive lines
            if dedup_lines and dedup_lines[-1] == line_s:
                continue

            # Drop substring / partial shadow duplicates
            if dedup_lines:
                prev = dedup_lines[-1]
                if (line_s in prev or prev in line_s) and len(line_s) < 40 and len(prev) < 40:
                    # Replace with the longer/more complete version
                    if len(line_s) > len(prev):
                        dedup_lines[-1] = line_s
                    continue

            dedup_lines.append(line_s)

        clean_pages.append({
            "page": page_idx + 1,
            "lines": dedup_lines,
            "text": "\n".join(dedup_lines),
        })

    return clean_pages


def _extract_toc(doc: Any) -> list[dict]:
    """Read PDF's embedded table of contents if available."""
    raw = doc.get_toc(simple=False)
    out = []
    for item in raw:
        level, title, page = item[0], item[1], item[2]
        if title and title.strip():
            clean = _sanitize_text(title.strip())
            if clean and not _is_mostly_garbage(clean) and not _NOISE_HEADING_RE.match(clean):
                out.append({"level": level, "title": clean, "page": page})
    return out


# ── Title & Section Extraction ──────────────────────────────────────────────

def _extract_document_title(clean_pages: list[dict], toc: list[dict]) -> str:
    """Extract a clean chapter/document title from Page 1 or TOC."""
    if toc:
        top = [t for t in toc if t["level"] == 1]
        if top and len(top[0]["title"]) >= 4:
            return _clean_title_str(top[0]["title"])

    if not clean_pages:
        return "Chapter Lesson"

    p1_lines = clean_pages[0]["lines"]
    title_parts = []

    for l in p1_lines[:12]:
        # Skip standalone numbers, "CHAPTER 1", "CHAPTER", etc.
        if re.match(r"^(?:chapter\s*\d*|\d+|unit\s*\d*)$", l, re.IGNORECASE):
            continue
        if _NOISE_HEADING_RE.match(l):
            continue

        # Look for chapter title text
        l_clean = l.strip()
        if any(w in l_clean.lower() for w in [
            "reactions and equations", "chemical reactions", "acid", "bases", "metals",
            "carbon and its compounds", "life processes", "control and coordination",
            "heredity", "light", "electricity", "magnetic effects", "our environment",
            "mechanics", "optics", "thermodynamics", "organic chemistry", "biology", "physics"
        ]):
            title_parts.append(l_clean)
        elif len(title_parts) > 0 and len(title_parts) < 3 and len(l_clean) < 50:
            title_parts.append(l_clean)
        elif not title_parts and len(l_clean) >= 5 and len(l_clean) <= 60 and not l_clean.endswith("."):
            # Potential title line
            title_parts.append(l_clean)

    if title_parts:
        candidate = " ".join(title_parts)
        return _clean_title_str(candidate)

    # Fallback to first non-empty line
    for l in p1_lines:
        if len(l) >= 4 and not re.match(r"^(?:chapter|\d+)", l, re.IGNORECASE):
            return _clean_title_str(l)

    return "Chapter Lesson"


def _clean_title_str(title: str) -> str:
    """Clean up title string."""
    title = re.sub(r"^(?:chapter\s*\d+[\s:.\-]*|unit\s*\d+[\s:.\-]*|\d+[\s:.\-]+)", "", title, flags=re.IGNORECASE).strip()
    # Remove watermarks / reprint notices
    title = re.sub(r"reprint\s*\d{4}[–\-]\d{2,4}", "", title, flags=re.IGNORECASE).strip()
    # Remove trailing broken sentences
    title = re.split(r"(?i)\s+(?:when\s*[–\-]|consider\s+the\s+following|think\s+what\s+happens)", title)[0].strip()
    # Clean non-alphanumeric trailing
    title = re.sub(r"[\s:;,–—\-]+$", "", title).strip()
    return title.title() if title.isupper() else title if len(title) >= 3 else "Chapter Lesson"


def _extract_sections(clean_pages: list[dict], doc_title: str) -> list[dict[str, Any]]:
    """Extract structured sections from clean pages."""
    sections: list[dict[str, Any]] = []

    # Initial section named directly from doc_title / topic
    initial_heading = (doc_title or "Core Lesson Concepts").strip()
    current_sec: dict[str, Any] = {
        "heading": initial_heading,
        "level": 1,
        "page_start": 1,
        "page_end": 1,
        "lines": [],
        "formulas": [],
    }

    for p in clean_pages:
        page_num = p["page"]
        lines = p["lines"]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line is a section heading
            is_sec, heading_text, advance = _check_is_heading(lines, i)

            if is_sec and heading_text and not _NOISE_HEADING_RE.match(heading_text):
                # Flush previous section
                if current_sec["lines"]:
                    text = "\n".join(current_sec["lines"]).strip()
                    current_sec["text"] = text
                    current_sec["word_count"] = len(text.split())
                    current_sec["formulas"] = list(dict.fromkeys(current_sec["formulas"]))
                    sections.append(current_sec)

                level = 1 if re.match(r"^\d+\.\d+\s", heading_text) else 2
                current_sec = {
                    "heading": heading_text,
                    "level": level,
                    "page_start": page_num,
                    "page_end": page_num,
                    "lines": [],
                    "formulas": [],
                }
                i += advance
                continue
            else:
                current_sec["lines"].append(line)
                current_sec["page_end"] = page_num

                # Check for formula line
                if (
                    any(sym in line for sym in ["→", "⟶", "⇌", "=", "+"])
                    and any(c.isupper() for c in line)
                    and len(line) < 100
                    and not line.startswith("http")
                ):
                    current_sec["formulas"].append(line.strip())

            i += 1

    # Flush final section
    if current_sec["lines"]:
        text = "\n".join(current_sec["lines"]).strip()
        current_sec["text"] = text
        current_sec["word_count"] = len(text.split())
        current_sec["formulas"] = list(dict.fromkeys(current_sec["formulas"]))
        sections.append(current_sec)

    return sections


def _check_is_heading(lines: list[str], idx: int) -> tuple[bool, str, int]:
    """Check if lines[idx] is a section heading, handling multi-line wrapped headers."""
    line = lines[idx].strip()

    if _NOISE_HEADING_RE.match(line):
        return False, "", 0

    # 1. Numbered section heading: "1.1 Chemical Equations", "1.2.1 Combination Reaction"
    m_num = _NUMBERED_SEC_RE.match(line)
    if m_num:
        num = m_num.group(1)
        rest = m_num.group(2).strip()
        advance = 1

        # If the title text was wrapped onto the next line (e.g. "1.1 CHEMICAL EQUA" + "TIONS")
        if idx + 1 < len(lines):
            next_l = lines[idx + 1].strip()
            if not _NOISE_HEADING_RE.match(next_l) and len(next_l) < 50 and not next_l.endswith((".", ":", ";")):
                # Check if next line is a continuation word
                if next_l.isupper() or next_l[0].isupper():
                    if rest and not rest.endswith((".", "?", "!")):
                        rest = f"{rest} {next_l}"
                        advance = 2
                    elif not rest:
                        rest = next_l
                        advance = 2

        full_heading = f"{num} {rest}".strip() if rest else ""
        if full_heading and len(rest) >= 3 and not _NOISE_HEADING_RE.match(rest):
            # Clean up all-caps / shadow fragments in the heading
            clean_h = _normalize_heading_title(full_heading)
            return True, clean_h, advance

    # 2. Semantic concept keyword match (for unnumbered sections)
    line_lower = line.lower()
    for kw in _CONCEPT_KEYWORDS:
        if line_lower == kw or line_lower.startswith(f"{kw}:") or line_lower.startswith(f"{kw} -"):
            return True, line.strip().title(), 1

    return False, "", 0


def _normalize_heading_title(heading: str) -> str:
    """Normalize heading title: fix broken capitalizations, strip shadow noise."""
    # Remove watermarks / reprint notices
    heading = re.sub(r"reprint\s*\d{4}[–\-]\d{2,4}", "", heading, flags=re.IGNORECASE).strip()
    # Fix shadow duplicates like "1.1 CHEMICAL EQUA AL EQUATIONS" -> "1.1 Chemical Equations"
    heading = re.sub(r"\bEQUA\s+AL\s+EQUATIONS\b", "EQUATIONS", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\bREA\s+AL\s+REACTIONS\b", "REACTIONS", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\bEQUA\s+TIONS\b", "EQUATIONS", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\bREA\s+CTIONS\b", "REACTIONS", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\bOXID\s+ATION\b", "OXIDATION", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\bAL\s+EQUATIONS\b", "EQUATIONS", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\bAL\s+REACTIONS\b", "REACTIONS", heading, flags=re.IGNORECASE)
    heading = re.sub(r"\s+", " ", heading).strip()
    # Strip trailing punctuation
    heading = re.sub(r"[\s:;,–—\-]+$", "", heading).strip()

    # If the heading text (excluding number) is ALL CAPS, convert it to Title Case
    m = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", heading)
    if m:
        num, text = m.group(1), m.group(2)
        if text.isupper():
            text = text.title()
        return f"{num} {text}"
    elif heading.isupper():
        return heading.title()

    return heading


def _merge_tiny_sections(sections: list[dict]) -> list[dict]:
    """Merge sections with very little text (< 20 words) into adjacent sections."""
    if len(sections) <= 1:
        return sections

    merged: list[dict] = []
    pending_text: list[str] = []
    pending_formulas: list[str] = []

    for i, sec in enumerate(sections):
        is_tiny = sec["word_count"] < _MIN_SECTION_WORDS_TO_KEEP and not sec.get("formulas")

        if is_tiny and i < len(sections) - 1:
            if sec.get("text"):
                pending_text.append(sec["text"])
            pending_formulas.extend(sec.get("formulas", []))
        else:
            if pending_text:
                combined_text = "\n".join(pending_text) + "\n" + sec.get("text", "")
                sec = {
                    **sec,
                    "text": combined_text.strip(),
                    "word_count": len(combined_text.split()),
                    "formulas": list(dict.fromkeys(pending_formulas + sec.get("formulas", []))),
                }
                pending_text = []
                pending_formulas = []
            merged.append(sec)

    # If the last section was tiny or there's pending text, merge it into the previous section
    if (pending_text or (merged and merged[-1]["word_count"] < _MIN_SECTION_WORDS_TO_KEEP and len(merged) > 1)):
        if len(merged) > 1 and merged[-1]["word_count"] < _MIN_SECTION_WORDS_TO_KEEP:
            last = merged.pop()
            pending_text.append(last["text"])
            pending_formulas.extend(last.get("formulas", []))
        if merged and pending_text:
            prev = merged[-1]
            combined = prev["text"] + "\n" + "\n".join(pending_text)
            merged[-1] = {
                **prev,
                "text": combined.strip(),
                "word_count": len(combined.split()),
                "formulas": list(dict.fromkeys(prev.get("formulas", []) + pending_formulas)),
            }

    return merged
