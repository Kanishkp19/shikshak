"""
Shikshak AI — JSON schema validation skill.

Every LLM output that feeds into code (lesson plans, question objects, visual
briefs) MUST be validated against a Pydantic schema before being trusted —
never parse free-text LLM output with regex (per 00-MASTER-PROMPT.md).

Provides:
  - validate_llm_json: one-shot validation, raises ValueError on failure.
  - call_llm_with_retry: calls a callable LLM fn, validates against the
    schema, retries once with a stricter "return only valid JSON" instruction
    before failing (per 02-TRD.md error strategy).
"""
from __future__ import annotations

import json
import re
from typing import Callable, Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _strip_code_fences(raw: str) -> str:
    """Models sometimes wrap JSON in ```json ... ``` fences — strip them."""
    s = raw.strip()
    if s.startswith("```"):
        # remove first fence line
        s = re.sub(r"^```(?:json)?\s*\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s)
    return s.strip()


def _extract_first_json_object(raw: str) -> str:
    """If the LLM prefixed with prose, find the first { ... } block."""
    s = _strip_code_fences(raw)
    if not s:
        return raw
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end < start:
        return s
    return s[start : end + 1]


def validate_llm_json(raw: str, schema: Type[T]) -> T:
    """Parse raw LLM output into a validated Pydantic instance.

    Raises ValueError if the JSON cannot be parsed or the schema fails.
    """
    cleaned = _extract_first_json_object(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM output was not valid JSON: {e}\nRaw: {raw[:400]}") from e
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}") from e


def call_llm_with_retry(
    llm_fn: Callable[[str], str],
    prompt: str,
    schema: Type[T],
    model_name: str = "llm",
) -> T:
    """Call llm_fn(prompt) -> raw_str; validate against schema.

    On failure, retry once with a stricter instruction prepended.
    If still fails, raise ValueError (caller decides fallback strategy).
    """
    raw = llm_fn(prompt)
    try:
        return validate_llm_json(raw, schema)
    except ValueError as first_err:
        # retry with stricter instruction
        stricter = (
            "Return ONLY valid minified JSON that matches the schema. "
            "No prose, no code fences, no comments. "
            "Every required field MUST be present — use sensible zero-value "
            "defaults (0 for numbers, empty string for text, empty list for "
            "arrays) rather than omitting fields.\n\n"
        )
        retry_prompt = stricter + prompt
        try:
            raw_retry = llm_fn(retry_prompt)
            return validate_llm_json(raw_retry, schema)
        except ValueError as second_err:
            raise ValueError(
                f"LLM '{model_name}' failed schema after retry. "
                f"First err: {first_err}. Second err: {second_err}"
            ) from second_err
