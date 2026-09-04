"""
Shikshak AI — Avatar Rendering Agent.

Single responsibility: take the synthesised audio and produce a lip-synced
avatar video. Wraps the lip-sync skill — never calls Wav2Lip directly.
"""
from __future__ import annotations

from celery_app import celery_app
from skills.lip_sync_rendering import render_lip_sync


def render(*, audio_path: str) -> str:
    """Return the path to the rendered avatar video file."""
    return render_lip_sync(audio_path=audio_path)


@celery_app.task(name="agents.avatar_rendering.run")
def run(audio_path: str) -> str:
    return render(audio_path=audio_path)
