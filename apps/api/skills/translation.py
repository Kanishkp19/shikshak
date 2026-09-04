"""
Shikshak AI — translation skill.

Lightweight wrapper for language switching mid-session. Uses Gemini for
multilingual translation. Falls back to a no-op if no LLM is configured
(useful for local testing in English-only mode).
"""
from __future__ import annotations

from typing import Optional


def translate_text(text: str, target_language: str, source_language: str = "auto") -> str:
    """Translate `text` into `target_language` (BCP-47 like 'hi' or 'en').

    Falls back to the original text if translation isn't available.
    """
    from config import settings

    if not settings.gemini_api_key:
        return text  # no-op fallback

    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        prompt = (
            f"Translate the following text into language code '{target_language}'. "
            f"Return ONLY the translation, no preamble.\n\n{text}"
        )
        res = model.generate_content(prompt)
        out = res.text.strip()
        return out or text
    except Exception:
        return text
