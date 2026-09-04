"""Unit tests for skills/json_schema_validation.py.

Verifies the LLM-output → Pydantic validator handles code fences, prose
prefixed, malformed JSON, and the retry-once-with-stricter-instruction
strategy.
"""
import pytest
from pydantic import BaseModel, Field

from skills.json_schema_validation import (
    validate_llm_json,
    call_llm_with_retry,
    _strip_code_fences,
    _extract_first_json_object,
)


class _Schema(BaseModel):
    score: float
    strong_areas: list[str] = Field(default_factory=list)


def test_strip_code_fences_json():
    raw = "```json\n{\"score\": 80}\n```"
    out = _strip_code_fences(raw)
    assert out == '{"score": 80}'


def test_strip_code_fences_plain():
    raw = '{"score": 80}'
    out = _strip_code_fences(raw)
    assert out == '{"score": 80}'


def test_extract_first_json_object_with_prose():
    raw = "Here is your answer: {\"score\": 80, \"strong_areas\": [\"X\"]} Thanks!"
    out = _extract_first_json_object(raw)
    assert out == '{"score": 80, "strong_areas": ["X"]}'


def test_validate_llm_json_valid():
    raw = '{"score": 80, "strong_areas": ["X"]}'
    s = validate_llm_json(raw, _Schema)
    assert s.score == 80
    assert s.strong_areas == ["X"]


def test_validate_llm_json_with_fences():
    raw = '```json\n{"score": 95}\n```'
    s = validate_llm_json(raw, _Schema)
    assert s.score == 95


def test_validate_llm_json_malformed_raises():
    with pytest.raises(ValueError):
        validate_llm_json("not json at all", _Schema)


def test_validate_llm_json_schema_fails_raises():
    with pytest.raises(ValueError):
        validate_llm_json('{"strong_areas": ["X"]}', _Schema)  # missing score


def test_call_llm_with_retry_first_attempt_valid():
    calls = []

    def fake_llm(prompt: str) -> str:
        calls.append(prompt)
        return '{"score": 50}'

    s = call_llm_with_retry(fake_llm, "prompt", _Schema)
    assert s.score == 50
    assert len(calls) == 1


def test_call_llm_with_retry_second_attempt_valid():
    calls = []

    def fake_llm(prompt: str) -> str:
        calls.append(prompt)
        if len(calls) == 1:
            return "this is not json"
        return '{"score": 70}'

    s = call_llm_with_retry(fake_llm, "prompt", _Schema)
    assert s.score == 70
    assert len(calls) == 2


def test_call_llm_with_retry_both_fail():
    calls = []

    def fake_llm(prompt: str) -> str:
        calls.append(prompt)
        return "garbage"

    with pytest.raises(ValueError):
        call_llm_with_retry(fake_llm, "prompt", _Schema)
    assert len(calls) == 2
