"""
Shared LLM caller helpers used by every agent.

Dual-provider architecture:
  - Groq (free tier): ALL content/orchestration — lesson planning, narration,
    explanation, QA guard, interaction, content blueprint
  - Gemini: ONLY animation diagram planning (creative visual generation)

Agents never call `genai` or `groq` directly — they go through these wrappers
so retries, timeouts, rate-limit handling, and model switching live in one place.
"""
from __future__ import annotations

import re
import time
from typing import Callable, Optional

from config import settings

_BACKUP_GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
]

_BACKUP_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "groq/compound-mini",
    "openai/gpt-oss-120b",
]

# ── Request budget tracking (per-session, resets on restart) ─────────────────
_request_counts: dict[str, int] = {"gemini": 0, "groq": 0}


def _track_request(provider: str) -> None:
    _request_counts[provider] = _request_counts.get(provider, 0) + 1


def get_request_counts() -> dict[str, int]:
    """Return the current request counts for monitoring."""
    return dict(_request_counts)


# ── Retry with exponential backoff ───────────────────────────────────────────

def _retry_with_backoff(
    fn: Callable[[], str],
    max_retries: int = 3,
    base_delay: float = 1.0,
    provider: str = "unknown",
) -> str:
    """Call fn() with exponential backoff on failure."""
    last_err = None
    for attempt in range(max_retries):
        try:
            result = fn()
            if result and len(result.strip()) > 0:
                return result
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            # If daily token quota is exhausted, retrying immediately won't help — fail fast to fallback
            if "tokens per day" in err_str or "tpd" in err_str:
                break
            # Rate limit errors get longer backoff
            if "rate" in err_str or "quota" in err_str or "429" in err_str:
                delay = base_delay * (4 ** attempt)
            else:
                delay = base_delay * (2 ** attempt)
            if attempt < max_retries - 1:
                print(f"[{provider}] Attempt {attempt + 1} failed: {e}; retrying in {delay:.1f}s")
                time.sleep(delay)
    raise RuntimeError(f"[{provider}] All attempts failed: {last_err}")


# ── Core LLM callers ────────────────────────────────────────────────────────

def gemini_llm(
    prompt: str,
    *,
    model: Optional[str] = None,
    timeout_seconds: float | None = None,
    try_backup_models: bool = True,
    fallback_to_groq: bool = True,
    temperature: float = 0.4,
) -> str:
    """Call Gemini with a text prompt; return the raw text response.
    Automatically tries backup models and Groq if quota is exceeded."""
    if not settings.gemini_api_key:
        if fallback_to_groq and settings.groq_api_key:
            return groq_llm(prompt, timeout_seconds=timeout_seconds, temperature=temperature)
        return _stub_response(prompt)

    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=settings.gemini_api_key)

        models_to_try = [model or settings.gemini_model]
        if try_backup_models:
            for m in _BACKUP_GEMINI_MODELS:
                if m not in models_to_try:
                    models_to_try.append(m)

        last_err = None
        for mod_name in models_to_try:
            try:
                g_model = genai.GenerativeModel(mod_name)
                kwargs = {
                    "generation_config": {
                        "response_mime_type": "application/json",
                        "temperature": temperature,
                    },
                }
                if timeout_seconds is not None:
                    kwargs["request_options"] = {"timeout": timeout_seconds}

                def _call():
                    res = g_model.generate_content(prompt, **kwargs)
                    return res.text if res.text else ""

                result = _retry_with_backoff(_call, max_retries=2, base_delay=2.0, provider=f"gemini/{mod_name}")
                _track_request("gemini")
                return result
            except Exception as e:
                last_err = e
                continue

        # If all Gemini models failed, try Groq
        if fallback_to_groq and settings.groq_api_key:
            try:
                return groq_llm(prompt, timeout_seconds=timeout_seconds, temperature=temperature)
            except Exception:
                pass

        print(f"[gemini_llm] All Gemini models failed ({last_err}); falling back to dynamic stub")
        return _stub_response(prompt)
    except Exception as e:
        print(f"[gemini_llm] Unexpected error ({e}); returning stub")
        return _stub_response(prompt)


def groq_llm(
    prompt: str,
    *,
    model: Optional[str] = None,
    timeout_seconds: float | None = None,
    temperature: float = 0.4,
) -> str:
    """Call Groq with a text prompt; return the raw text response.
    Automatically tries backup Groq models if model is not found or fails."""
    if not settings.groq_api_key:
        # If no Groq key, fall back to Gemini then stub
        if settings.gemini_api_key:
            return gemini_llm(prompt, timeout_seconds=timeout_seconds, fallback_to_groq=False, temperature=temperature)
        return _stub_response(prompt)

    try:
        from groq import Groq  # type: ignore
        client_kwargs = {"api_key": settings.groq_api_key}
        if timeout_seconds is not None:
            client_kwargs["timeout"] = timeout_seconds
        client = Groq(**client_kwargs)

        models_to_try = [model or settings.groq_model]
        for m in _BACKUP_GROQ_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_err = None
        for mod_name in models_to_try:
            try:
                def _call():
                    res = client.chat.completions.create(
                        model=mod_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        response_format={"type": "json_object"},
                    )
                    return res.choices[0].message.content or ""

                result = _retry_with_backoff(_call, max_retries=2, base_delay=1.0, provider=f"groq/{mod_name}")
                _track_request("groq")
                return result
            except Exception as e:

                last_err = e
                # If API key is invalid (401), stop immediately and fall back to Gemini
                err_str = str(e).lower()
                if "401" in err_str or "invalid api key" in err_str or "invalid_api_key" in err_str:
                    break
                continue

        # Fallback chain: Groq failed → try Gemini → stub
        if settings.gemini_api_key:
            try:
                return gemini_llm(prompt, timeout_seconds=timeout_seconds, fallback_to_groq=False)
            except Exception:
                pass
        return _stub_response(prompt)
    except Exception as e:
        print(f"[groq_llm] Unexpected error ({e}); returning stub")
        return _stub_response(prompt)


# ── Provider selectors ───────────────────────────────────────────────────────

def get_llm() -> Callable[[str], str]:
    """Return the configured primary LLM callable (Groq by default for content)."""
    return get_content_llm()


def get_fast_llm() -> Callable[[str], str]:
    """Return the fast-turnaround LLM callable (Groq, for interaction loop)."""
    return groq_llm


def get_content_llm(temperature: Optional[float] = None) -> Callable[[str], str]:
    """Return the LLM for content/orchestration work.

    This handles: lesson planning, narration script, explanation,
    QA grounding guard, interaction, content blueprint generation.
    Uses Groq by default (free tier, fast, no rate limit pain).
    """
    provider = settings.content_llm_provider.lower()
    base_fn = gemini_llm if provider == "gemini" else groq_llm
    if temperature is not None:
        return lambda prompt, **kwargs: base_fn(prompt, temperature=temperature, **kwargs)
    return base_fn


def get_animation_llm() -> Callable[[str], str]:
    """Return the LLM for animation/diagram planning.

    This handles ONLY: DiagramSpec generation (visual node/edge planning).
    Uses Gemini by default (better visual creativity).
    Falls back to Groq if Gemini key is missing.
    """
    provider = settings.animation_llm_provider.lower()
    if provider == "groq" or not settings.gemini_api_key:
        return groq_llm
    return gemini_llm


# ── Helpers ──────────────────────────────────────────────────────────────────

def _extract_topic_from_prompt(prompt: str) -> str:
    """Extract topic/concept from prompt text for dynamic fallback responses."""
    m = re.search(r"Concept:\s*([^\n\r]+)", prompt, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"Topic:\s*([^\n\r]+)", prompt, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "Learning Concept"


def _stub_response(prompt: str) -> str:
    """Dynamic fallback response that incorporates the actual concept name."""
    topic = _extract_topic_from_prompt(prompt)

    # Reteach ladder strategies
    if "reteach" in prompt.lower() or "strategy" in prompt.lower():
        if "atomic_steps" in prompt.lower():
            return (
                f'{{"strategy":"atomic_steps",'
                f'"explanation":"Step 1: Identify the fundamental state of {topic}.\\n'
                f'Step 2: Apply the governing transformation to {topic}.\\n'
                f'Step 3: Observe the resulting outcome without skipping any intermediate phase.",'
                f'"new_example":"Step-by-step assembly manual",'
                f'"follow_up_question":"What is verified in Step 1 before proceeding?"}}'
            )
        elif "concrete_example" in prompt.lower():
            return (
                f'{{"strategy":"concrete_example",'
                f'"explanation":"A frequent misconception with {topic} is assuming static behavior. '
                f'Consider a bicycle on an incline: pedaling uphill requires continuous work against gravity, '
                f'directly illustrating the underlying equilibrium.",'
                f'"new_example":"Riding a bicycle up a smooth incline",'
                f'"follow_up_question":"How does the incline angle alter the necessary input force?"}}'
            )
        elif "simplify" in prompt.lower():
            return (
                f'{{"strategy":"simplify",'
                f'"explanation":"Put very simply without jargon: {topic} is like passing a baton in a relay race. '
                f'Each piece hands energy directly to the next so the whole system keeps moving smoothly forward.",'
                f'"new_example":"A relay team passing a baton",'
                f'"follow_up_question":"What happens if one runner does not pass the baton?"}}'
            )

    # CRAG query reformulation
    if "reformulated_query" in prompt.lower() or "reformulate" in prompt.lower():
        return f'{{"reformulated_query":"{topic} fundamental principles overview"}}'

    # Concept dependency graph
    if "edges" in prompt.lower() and "concepts" in prompt.lower():
        return (
            f'{{"concepts":["Foundations of {topic}","Mechanisms of {topic}","Advanced {topic}"],'
            f'"edges":[["Foundations of {topic}","Mechanisms of {topic}"],["Mechanisms of {topic}","Advanced {topic}"]]}}'
        )

    if "score" in prompt.lower() or "recommendation" in prompt.lower():

        return (
            f'{{"score":85,"strong_areas":["{topic} Foundations"],'
            f'"weak_areas":["Advanced Applications"],"recommendation":"Continue exploring {topic} deeper."}}'
        )

    if "misconception" in prompt.lower():
        return (
            f'{{"misconception":"Confusion regarding the fundamental principles of {topic}.",'
            f'"re_explanation":"Let us look at {topic} from another angle with a real-world example: '
            f'observe how forces and components interact dynamically to produce the observed behavior."}}'
        )

    if "items" in prompt.lower() and "sub-topic" in prompt.lower():
        return (
            f'{{"items":["Introduction to {topic}","Core Principles of {topic}",'
            f'"Mechanism & Formula of {topic}","Real-world Applications of {topic}","Summary & Review"]}}'
        )

    if "Return a JSON object" in prompt or "Return JSON" in prompt or "segments" in prompt:
        return (
            f'{{"segments": ['
            f'{{"concept":"{topic} - Core Principles","depth":"beginner","visual_type":"diagram","has_checkpoint":false,'
            f'"related_concepts":["{topic} Formulas","Practical Applications of {topic}","Advanced Insights into {topic}"]}},'
            f'{{"concept":"{topic} - Mathematical Formulation","depth":"intermediate","visual_type":"diagram","has_checkpoint":true,'
            f'"related_concepts":["Derivation","Variables & Units","Case Studies"]}},'
            f'{{"concept":"{topic} - Real-World Applications","depth":"advanced","visual_type":"diagram","has_checkpoint":false,'
            f'"related_concepts":["Future Research","Complex Systems","Mastery Review"]}}'
            f']}}'
        )

    if "type" in prompt.lower() and "correct_answer" in prompt.lower():
        return (
            f'{{"type":"conceptual","prompt":"What is the central principle governing {topic}?",'
            f'"options":null,"correct_answer":"It describes how components interact systematically to produce predictable outcomes.",'
            f'"expected_reasoning":"Fundamental law of {topic}."}}'
        )

    if "Translate" in prompt:
        return prompt

    # Scene blueprint prompt — return a proper blueprint structure
    if "scene_title" in prompt.lower() or "visual_nodes" in prompt.lower():
        return (
            f'{{"concept":"{topic}","full_narration_script":"Let us explore {topic} in detail. '
            f'The fundamental principle behind {topic} governs how forces, objects, or systems interact in nature. '
            f'Understanding this core mechanism allows us to predict and analyze real-world behaviors with precision.",'
            f'"scenes":['
            f'{{"scene_number":1,"narration_text":"Let us explore {topic} in detail.",'
            f'"scene_title":"{topic} Overview","visual_nodes":[{{"id":"n1","label":"{topic}","detail":"Core concept","color":"#38bdf8"}},'
            f'{{"id":"n2","label":"Key Mechanism","detail":"How it works","color":"#818cf8"}}],'
            f'"visual_edges":[{{"from":"n1","to":"n2","label":"drives"}}],"layout":"flowchart","duration_hint_seconds":5}},'
            f'{{"scene_number":2,"narration_text":"The fundamental principle governs interactions in nature.",'
            f'"scene_title":"Core Principle","visual_nodes":[{{"id":"n3","label":"Applications","detail":"Real-world use","color":"#34d399"}}],'
            f'"visual_edges":[{{"from":"n2","to":"n3","label":"produces"}}],"layout":"flowchart","duration_hint_seconds":5}}'
            f'],'
            f'"diagram_spec":{{"layout":"flowchart","nodes":[{{"id":"n1","label":"{topic}","icon":"💡","color":"#38bdf8","detail":"Core concept"}},'
            f'{{"id":"n2","label":"Key Mechanism","icon":"⚙️","color":"#818cf8","detail":"How it works"}},'
            f'{{"id":"n3","label":"Applications","icon":"🎯","color":"#34d399","detail":"Real-world use"}}],'
            f'"edges":[{{"from":"n1","to":"n2","label":"drives","animated":true}},{{"from":"n2","to":"n3","label":"produces","animated":true}}],'
            f'"title":"{topic}","formula":"","key_insight":"Understanding {topic} step by step."}}}}'
        )

    # Narration-style prompt
    return (
        f"Let us explore {topic} in detail. The fundamental principle behind {topic} "
        f"governs how forces, objects, or systems interact in nature. Understanding this core mechanism "
        f"allows us to predict and analyze real-world behaviors with precision."
    )
