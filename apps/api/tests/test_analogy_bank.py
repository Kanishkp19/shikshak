"""Unit tests for skills/misconception_analogy_bank.py."""
from skills.misconception_analogy_bank import pick_alternative_analogies, DEFAULT_ANALOGIES


def test_keyword_match_returns_analogies():
    out = pick_alternative_analogies("Newton's first law of motion")
    assert len(out) >= 1
    assert out[0]  # non-empty


def test_no_keyword_match_returns_defaults():
    out = pick_alternative_analogies("Some unknown topic")
    assert out == DEFAULT_ANALOGIES[:3]


def test_excludes_original_analogy():
    out = pick_alternative_analogies(
        "Newton's first law of motion",
        original_analogy="Pushing a heavy shopping cart",
    )
    assert all("Pushing a heavy shopping cart" not in a for a in out)
