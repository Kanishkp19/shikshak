"""
Shikshak AI — Voice Synthesis Agent.

Single responsibility: take a final narration script + language, produce
an audio file. Wraps the TTS skill — never calls the TTS SDK directly so
the underlying engine can be swapped without touching agent code.
"""
from __future__ import annotations

from typing import Any

from celery_app import celery_app
from skills.tts_synthesis import synthesize_speech


def synthesize(*, narration_script: str, language: str) -> str:
    """Return the path to the synthesised audio file."""
    return synthesize_speech(narration_script, language=language)


@celery_app.task(name="agents.voice_synthesis.run")
def run(narration_script: str, language: str) -> str:
    return synthesize(narration_script=narration_script, language=language)
