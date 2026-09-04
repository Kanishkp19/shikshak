"""
Shikshak AI — Celery application definition.

Independent agents run via celery.group(); dependent agents run via
celery.chain() — see orchestrator/execution_plan.py.
"""
from __future__ import annotations

from celery import Celery

from config import settings

celery_app = Celery(
    "shikshak_ai",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        # declare tasks modules so Celery auto-discovers them at worker boot
        "agents.content_ingestion",
        "agents.knowledge_retrieval",
        "agents.lesson_planning",
        "agents.personalization",
        "agents.time_budgeting",
        "agents.language",
        "agents.explanation",
        "agents.visual_selection",
        "agents.voice_synthesis",
        "agents.avatar_rendering",
        "agents.concept_animation",
        "agents.video_compositing",
        "agents.interaction",
        "agents.answer_evaluation",
        "agents.misconception_detection",
        "agents.assessment",
        "agents.learner_profile",
        "agents.learning_path",
        "agents.qa_grounding_guard",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=240,           # 4-minute hard limit per task (video fallback)
    task_soft_time_limit=210,
    task_default_retry_delay=2,
    task_default_max_retries=1,
)


@celery_app.task(name="smoke_test")
def smoke_test(x: int, y: int) -> int:
    """Used by Phase 0 / docker-compose to confirm the worker is alive."""
    return x + y
