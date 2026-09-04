"""
Shikshak AI — Supabase persistence skill.

Wraps the Supabase Python client with typed helpers for every table
defined in 05-BACKEND-SCHEMA.md. All other modules go through this layer —
they never import supabase-py directly, so RLS / service-role decisions
live in exactly one place.
"""
from __future__ import annotations

import logging
from typing import Any, Optional
from functools import lru_cache

from config import settings

logger = logging.getLogger(__name__)


try:
    from supabase import create_client, Client  # type: ignore
except ImportError:  # pragma: no cover — allows local import without supabase installed
    Client = Any  # type: ignore
    create_client = None  # type: ignore


@lru_cache
def get_client() -> Any:
    """Return a Supabase client using the service role key (server-side only)."""
    if create_client is None:
        raise RuntimeError(
            "supabase package not installed — pip install supabase"
        )
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in env"
        )
    return create_client(
        settings.supabase_url, settings.supabase_service_role_key
    )


def _clean_data(data: Any) -> Any:
    """Strip PostgreSQL-incompatible null bytes (\\u0000) from payload data."""
    if isinstance(data, str):
        return data.replace("\x00", "").replace("\u0000", "")
    if isinstance(data, dict):
        return {k: _clean_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_clean_data(v) for v in data]
    return data


# ── Documents ───────────────────────────────────────────────────────────────
def insert_document(
    *, owner_id: str, file_name: str, file_type: str, storage_path: str, page_count: Optional[int] = None
) -> dict:
    row = _clean_data({
        "owner_id": owner_id,
        "file_name": file_name,
        "file_type": file_type,
        "storage_path": storage_path,
        "page_count": page_count,
        "status": "processing",
    })
    res = get_client().table("documents").insert(row).execute()
    return res.data[0]


def set_document_status(document_id: str, status: str, page_count: Optional[int] = None) -> dict:
    patch: dict = {"status": status}
    if page_count is not None:
        patch["page_count"] = page_count
    res = (
        get_client()
        .table("documents")
        .update(patch)
        .eq("id", document_id)
        .execute()
    )
    return res.data[0] if res.data else {}


def get_document(document_id: str) -> Optional[dict]:
    res = get_client().table("documents").select("*").eq("id", document_id).execute()
    return res.data[0] if res.data else None


# ── Document chunks ─────────────────────────────────────────────────────────
def insert_chunks(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    res = get_client().table("document_chunks").insert(_clean_data(rows)).execute()
    return res.data


# ── Sessions ─────────────────────────────────────────────────────────────────
def insert_session(**fields) -> dict:
    res = get_client().table("sessions").insert(_clean_data(fields)).execute()
    return res.data[0]


def update_session(session_id: str, patch: dict) -> dict:
    res = get_client().table("sessions").update(_clean_data(patch)).eq("id", session_id).execute()
    return res.data[0] if res.data else {}


def get_session(session_id: str) -> Optional[dict]:
    res = get_client().table("sessions").select("*").eq("id", session_id).execute()
    return res.data[0] if res.data else None


def list_sessions(student_id: str) -> list[dict]:
    res = (
        get_client()
        .table("sessions")
        .select("*")
        .eq("student_id", student_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


def delete_session(session_id: str) -> bool:
    """Cascade delete a session and all associated records."""
    client = get_client()

    # 1. Nullify related_session_id in learning_path_items
    try:
        client.table("learning_path_items").update({"related_session_id": None}).eq(
            "related_session_id", session_id
        ).execute()
    except Exception as e:
        logger.warning("Could not unlink learning_path_items for session %s: %s", session_id, e)

    # 2. Delete question checkpoints for segments of this session
    try:
        segments = client.table("lesson_segments").select("id").eq("session_id", session_id).execute()
        segment_ids = [s["id"] for s in (segments.data or []) if "id" in s]
        if segment_ids:
            client.table("question_checkpoints").delete().in_("segment_id", segment_ids).execute()
    except Exception as e:
        logger.warning("Could not delete question_checkpoints for session %s: %s", session_id, e)

    # 3. Delete lesson segments
    try:
        client.table("lesson_segments").delete().eq("session_id", session_id).execute()
    except Exception as e:
        logger.warning("Could not delete lesson_segments for session %s: %s", session_id, e)

    # 4. Delete assessment reports
    try:
        client.table("assessment_reports").delete().eq("session_id", session_id).execute()
    except Exception as e:
        logger.warning("Could not delete assessment_reports for session %s: %s", session_id, e)

    # 5. Delete agent run logs
    try:
        client.table("agent_run_logs").delete().eq("session_id", session_id).execute()
    except Exception as e:
        logger.warning("Could not delete agent_run_logs for session %s: %s", session_id, e)

    # 6. Delete the session row itself
    res = client.table("sessions").delete().eq("id", session_id).execute()
    return bool(res.data)



# ── Lesson segments ─────────────────────────────────────────────────────────
def insert_segments(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    cleaned = _clean_data(rows)
    try:
        res = get_client().table("lesson_segments").insert(cleaned).execute()
        return res.data
    except Exception as e:
        # If columns like diagram_spec_json / animation_scenes_json don't exist yet in Supabase,
        # strip them and insert the base columns so session creation never fails.
        err_msg = str(e).lower()
        if "column" in err_msg or "schema" in err_msg or "42703" in err_msg or "pgrst" in err_msg:
            base_keys = {
                "id", "session_id", "segment_order", "concept", "depth",
                "visual_type", "narration_script", "audio_url", "video_url",
                "video_cache_id", "has_checkpoint", "status", "created_at"
            }
            cleaned_rows = [
                {k: v for k, v in r.items() if k in base_keys}
                for r in cleaned
            ]
            res = get_client().table("lesson_segments").insert(cleaned_rows).execute()
            return res.data
        raise


def update_segment(segment_id: str, patch: dict) -> dict:
    res = (
        get_client()
        .table("lesson_segments")
        .update(patch)
        .eq("id", segment_id)
        .execute()
    )
    return res.data[0] if res.data else {}


def list_segments(session_id: str) -> list[dict]:
    res = (
        get_client()
        .table("lesson_segments")
        .select("*")
        .eq("session_id", session_id)
        .order("segment_order", desc=False)
        .execute()
    )
    return res.data


# ── Checkpoints ─────────────────────────────────────────────────────────────
def insert_checkpoint(**fields) -> dict:
    res = get_client().table("question_checkpoints").insert(fields).execute()
    return res.data[0]


def get_checkpoint(checkpoint_id: str) -> Optional[dict]:
    res = (
        get_client()
        .table("question_checkpoints")
        .select("*")
        .eq("id", checkpoint_id)
        .execute()
    )
    return res.data[0] if res.data else None


def update_checkpoint(checkpoint_id: str, patch: dict) -> dict:
    res = (
        get_client()
        .table("question_checkpoints")
        .update(patch)
        .eq("id", checkpoint_id)
        .execute()
    )
    return res.data[0] if res.data else {}


def list_checkpoints_for_session(session_id: str) -> list[dict]:
    res = (
        get_client()
        .table("question_checkpoints")
        .select("*, segment:lesson_segments!inner(session_id)")
        .eq("segment.session_id", session_id)
        .execute()
    )
    return res.data


# ── Assessment reports ──────────────────────────────────────────────────────
def upsert_report(**fields) -> dict:
    res = get_client().table("assessment_reports").upsert(fields).execute()
    return res.data[0]


def get_report(session_id: str) -> Optional[dict]:
    res = (
        get_client()
        .table("assessment_reports")
        .select("*")
        .eq("session_id", session_id)
        .execute()
    )
    return res.data[0] if res.data else None


# ── Learner profiles ─────────────────────────────────────────────────────────
def upsert_learner_profile(**fields) -> dict:
    res = get_client().table("learner_profiles").upsert(fields).execute()
    return res.data[0]


def get_learner_profile(student_id: str) -> Optional[dict]:
    res = (
        get_client()
        .table("learner_profiles")
        .select("*")
        .eq("id", student_id)
        .execute()
    )
    return res.data[0] if res.data else None


def patch_learner_profile(student_id: str, patch: dict) -> dict:
    res = (
        get_client()
        .table("learner_profiles")
        .update(patch)
        .eq("id", student_id)
        .execute()
    )
    return res.data[0] if res.data else {}


# ── Learning paths ────────────────────────────────────────────────────────────
def insert_learning_path(**fields) -> dict:
    res = get_client().table("learning_paths").insert(fields).execute()
    return res.data[0]


def insert_learning_path_items(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    res = get_client().table("learning_path_items").insert(rows).execute()
    return res.data


def get_learning_path(path_id: str) -> Optional[dict]:
    res = (
        get_client()
        .table("learning_paths")
        .select("*, learning_path_items(*)")
        .eq("id", path_id)
        .execute()
    )
    return res.data[0] if res.data else None


# ── Agent run logs ───────────────────────────────────────────────────────────
def log_agent_run(**fields) -> dict:
    res = get_client().table("agent_run_logs").insert(fields).execute()
    return res.data[0] if res.data else {}


# ── Video cache ───────────────────────────────────────────────────────────────
def get_cached_video(prompt_hash: str) -> Optional[dict]:
    res = (
        get_client()
        .table("video_cache")
        .select("*")
        .eq("prompt_hash", prompt_hash)
        .execute()
    )
    return res.data[0] if res.data else None


def insert_cached_video(**fields) -> dict:
    res = get_client().table("video_cache").insert(fields).execute()
    return res.data[0]


# ── Scenes (scene-first architecture) ────────────────────────────────────────

def insert_scenes(segment_id: str, scenes: list[dict]) -> list[dict]:
    """Insert one row per scene for a given segment.

    Each dict in `scenes` must already be validated against SceneIn before
    calling this function (the orchestrator is responsible for that validation).
    Returns the inserted rows with DB-assigned UUIDs.
    """
    if not scenes:
        return []

    import json as _json

    rows = []
    for sc in scenes:
        row: dict = {
            "segment_id": segment_id,
            "scene_order": sc["scene_order"],
            "learning_objective": sc["learning_objective"],
            "narration_text": sc["narration_text"],
            "visual_mode": sc["visual_mode"],
            "visual_payload": sc.get("visual_payload", {}),
            "on_screen_equation": sc.get("on_screen_equation", ""),
            "on_screen_labels": sc.get("on_screen_labels", []),
            "key_takeaway": sc.get("key_takeaway", ""),
            "render_status": "pending",
        }
        if sc.get("interaction_cue") is not None:
            row["interaction_cue"] = sc["interaction_cue"]
        # start_time_ms / end_time_ms populated later by TTS alignment
        rows.append(_clean_data(row))

    try:
        res = get_client().table("scenes").insert(rows).execute()
        return res.data
    except Exception as e:
        err_msg = str(e).lower()
        # If the scenes table doesn't exist yet (migration not run), log and
        # return empty list rather than hard-crashing the pipeline.
        if "42p01" in err_msg or "relation" in err_msg or "does not exist" in err_msg:
            logger.warning(
                "[supabase_persistence] scenes table missing — run migration 013. "
                "Scene rows not persisted for segment %s.", segment_id
            )
            return []
        raise


def update_scene(scene_id: str, patch: dict) -> dict:
    """Patch a single scene row (e.g., render_status, rendered_clip_url, timing)."""
    res = (
        get_client()
        .table("scenes")
        .update(_clean_data(patch))
        .eq("id", scene_id)
        .execute()
    )
    return res.data[0] if res.data else {}


def list_scenes(segment_id: str) -> list[dict]:
    """Return all scenes for a segment ordered by scene_order ascending."""
    res = (
        get_client()
        .table("scenes")
        .select("*")
        .eq("segment_id", segment_id)
        .order("scene_order", desc=False)
        .execute()
    )
    return res.data or []


# ── Concept mastery ──────────────────────────────────────────────────────────
def upsert_concept_mastery(
    *,
    student_id: str,
    concept: str,
    score: float,
    status: str,
    attempts: int,
    consecutive_strong: int,
) -> dict:
    """UPSERT a concept mastery score record for a student."""
    row = _clean_data({
        "student_id": student_id,
        "concept": concept,
        "score": score,
        "status": status,
        "attempts": attempts,
        "consecutive_strong": consecutive_strong,
    })
    try:
        res = (
            get_client()
            .table("concept_mastery")
            .upsert(row, on_conflict="student_id,concept")
            .execute()
        )
        return res.data[0] if res.data else row
    except Exception as e:
        logger.warning(
            "[supabase_persistence] Could not upsert concept_mastery for (%s, %s): %s",
            student_id, concept, e,
        )
        return row


def get_concept_mastery(student_id: str, concept: str) -> Optional[dict]:
    """Get a student's mastery record for a specific concept."""
    try:
        res = (
            get_client()
            .table("concept_mastery")
            .select("*")
            .eq("student_id", student_id)
            .eq("concept", concept)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as e:
        logger.warning(
            "[supabase_persistence] Could not get concept_mastery for (%s, %s): %s",
            student_id, concept, e,
        )
        return None


def list_concept_mastery(student_id: str) -> list[dict]:
    """List all concept mastery records for a student."""
    try:
        res = (
            get_client()
            .table("concept_mastery")
            .select("*")
            .eq("student_id", student_id)
            .order("score", desc=False)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.warning(
            "[supabase_persistence] Could not list concept_mastery for %s: %s",
            student_id, e,
        )
        return []


# ── Concept dependencies (Learning path graph) ────────────────────────────────
def insert_concept_dependencies(rows: list[dict]) -> list[dict]:
    """Insert adjacency list rows into concept_dependencies table."""
    if not rows:
        return []
    cleaned = _clean_data(rows)
    try:
        res = get_client().table("concept_dependencies").insert(cleaned).execute()
        return res.data or []
    except Exception as e:
        logger.warning(
            "[supabase_persistence] Could not insert concept_dependencies: %s", e
        )
        return cleaned


def list_concept_dependencies(learning_path_id: str) -> list[dict]:
    """List all concept dependencies for a learning path."""
    try:
        res = (
            get_client()
            .table("concept_dependencies")
            .select("*")
            .eq("learning_path_id", learning_path_id)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.warning(
            "[supabase_persistence] Could not list concept_dependencies for %s: %s",
            learning_path_id, e,
        )
        return []


def get_checkpoint_by_segment(segment_id: str) -> Optional[dict]:
    """Look up a checkpoint by segment_id (fallback for frontend submission)."""
    try:
        res = (
            get_client()
            .table("question_checkpoints")
            .select("*")
            .eq("segment_id", segment_id)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as e:
        logger.warning(
            "[supabase_persistence] Could not get checkpoint for segment %s: %s",
            segment_id, e,
        )
        return None


