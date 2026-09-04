"""
Shikshak AI — caching skill.

Hashes (prompt, provider, params) into a stable key. Used by the video
pipeline to short-circuit generation for repeated briefs (so the live demo
pulls from `video_cache` rather than regenerating clips).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def build_cache_prompt(concept: str, visual_type: str, depth: str, language: str) -> str:
    """Normalize (concept, visual_type, depth, language) into a canonical JSON string."""
    payload = {
        "concept": (concept or "").strip().lower(),
        "depth": (depth or "").strip().lower(),
        "language": (language or "").strip().lower(),
        "visual_type": (visual_type or "").strip().lower(),
    }
    return json.dumps(payload, sort_keys=True)


def hash_prompt(concept: str, visual_type: str, depth: str, language: str) -> str:
    """Return the SHA-256 hex digest of the canonical prompt."""
    canonical_prompt = build_cache_prompt(concept, visual_type, depth, language)
    return hashlib.sha256(canonical_prompt.encode("utf-8")).hexdigest()


def make_prompt_hash(*parts: Any) -> str:
    """Return a 16-char hash of any tuple of JSON-serialisable inputs."""
    payload = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]



def cached_or_compute(
    *,
    prompt_hash: str,
    load_fn,
    save_fn,
    compute_fn,
):
    """Generic cache helper used by the voice_synthesis and concept_animation
    agents.

    1. Try load_fn(prompt_hash) — return immediately if non-None.
    2. Otherwise call compute_fn() to get the artifact.
    3. save_fn(prompt_hash, artifact) for next time.
    4. Return the artifact.
    """
    existing = load_fn(prompt_hash)
    if existing is not None:
        return existing, True  # hit
    artifact = compute_fn()
    try:
        save_fn(prompt_hash, artifact)
    except Exception:
        pass
    return artifact, False  # miss
