"""
Shikshak AI — FastAPI application entry point.

Wires every endpoint defined in 05-BACKEND-SCHEMA.md → "Full API contract".

Run locally:
    uvicorn main:app --reload --port 8000

In production, also start the Celery worker:
    celery -A celery_app worker --loglevel=info
"""
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import (
    FastAPI, UploadFile, File, HTTPException, Depends, Request, status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response, StreamingResponse
from pydantic import BaseModel

from config import settings
from models import (
    CreateSessionRequest,
    CreateLearningPathRequest,
    LanguageSwitchRequest,
    LessonSegment,
    Session,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    DocumentOut,
    AssessmentReportOut,
    LearnerProfileOut,
    PatchLearnerProfileRequest,
    LearningPathOut,
    ConceptMasteryOut,
)
from skills import supabase_persistence as db
from orchestrator.router import run_session_pipeline
import agents.content_ingestion as a_content
import agents.interaction as a_int
import agents.answer_evaluation as a_eval
import agents.misconception_detection as a_md
import agents.assessment as a_assess
import agents.learner_profile as a_profile
import agents.learning_path as a_lpath
import agents.voice_synthesis as a_voice
import agents.avatar_rendering as a_avatar
import agents.concept_animation as a_concept
import agents.video_compositing as a_composite
import agents.deep_dive_generation as a_deep_dive
from skills.concept_graph import get_concept_graph_dict
from skills.video_generation.media import require_playable_audio


app = FastAPI(
    title="Shikshak AI",
    version="0.1.0",
    description="Multi-agent AI Teacher backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── In-process rate limiter (very basic, demo-grade) ─────────────────────────
class RateLimiter:
    """Simple sliding-window in-memory limiter — sufficient for a hackathon
    demo. Replace with redis-backed limiter (e.g. slowapi) for production."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str, max_per_min: int) -> bool:
        now = time.time()
        hits = [t for t in self._hits.get(key, []) if now - t < 60]
        if len(hits) >= max_per_min:
            return False
        hits.append(now)
        self._hits[key] = hits
        return True


_rate_limiter = RateLimiter()


def _check_session_rate(request: Request) -> None:
    ip = request.client.host if request.client else "anon"
    if not _rate_limiter.allow(f"session:{ip}", settings.session_create_rate):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many session requests. Slow down.",
        )


def _check_render_rate(request: Request) -> None:
    ip = request.client.host if request.client else "anon"
    if not _rate_limiter.allow(f"render:{ip}", settings.render_rate):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many render requests. Slow down.",
        )


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shikshak-ai-api"}


# ── Documents ─────────────────────────────────────────────────────────────────
@app.post("/api/v1/documents", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    owner_id: str = "",
):
    """Upload a PDF/DOCX/PPTX source document. Triggers Content Ingestion Agent."""
    if not owner_id:
        raise HTTPException(400, "owner_id query param is required (will be auth.uid() in production)")

    # File validation per TRD security checklist
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.allowed_upload_ext:
        raise HTTPException(400, f"File must be a {settings.allowed_upload_ext} file")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(400, f"File must be under {settings.max_upload_mb}MB")

    # Persist raw file to a local cache dir (in production: Supabase Storage)
    storage_dir = Path("/tmp/shikshak_uploads")
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / f"{uuid.uuid4().hex}_{file.filename}"
    storage_path.write_bytes(content)

    row = db.insert_document(
        owner_id=owner_id,
        file_name=file.filename or "untitled",
        file_type=suffix.lstrip("."),
        storage_path=str(storage_path),
    )

    # Run content ingestion synchronously (the agent is light for the demo)
    try:
        a_content.ingest_document(row["id"])
    except Exception as e:
        # Background failure shouldn't block the upload response — frontend polls status
        db.set_document_status(row["id"], "failed")
        print(f"[upload_document] ingestion failed: {e}")

    doc = db.get_document(row["id"])
    return DocumentOut(
        id=doc["id"],
        file_name=doc["file_name"],
        file_type=doc["file_type"],
        page_count=doc.get("page_count"),
        status=doc["status"],
    )


@app.get("/api/v1/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: str):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return DocumentOut(
        id=doc["id"],
        file_name=doc["file_name"],
        file_type=doc["file_type"],
        page_count=doc.get("page_count"),
        status=doc["status"],
    )


# ── Sessions ──────────────────────────────────────────────────────────────────
@app.post("/api/v1/sessions", response_model=dict, dependencies=[Depends(_check_session_rate)])
def create_session(
    body: CreateSessionRequest,
    student_id: str = "",
):
    """Create a new teaching session. Triggers the Orchestrator → agent DAG."""
    if not student_id:
        raise HTTPException(400, "student_id query param is required (will be auth.uid() in production)")
    if body.source_type == "topic" and not body.topic:
        raise HTTPException(400, "topic is required when source_type='topic'")
    if body.source_type == "document" and not body.document_id:
        raise HTTPException(400, "document_id is required when source_type='document'")

    row = db.insert_session(
        student_id=student_id,
        source_type=body.source_type,
        document_id=body.document_id,
        topic=body.topic,
        level=body.level,
        language=body.language,
        time_budget_minutes=body.time_budget_minutes,
        status="planning",
    )

    # Run the orchestrator pipeline synchronously (hackathon-grade).
    # For production move this to celery.canvas( chain(group(), chain()) ).
    try:
        run_session_pipeline(row["id"])
    except Exception as e:
        db.update_session(row["id"], {"status": "failed"})
        raise HTTPException(500, f"Pipeline failed: {e}")

    return {"sessionId": row["id"], "status": "in_progress"}


@app.get("/api/v1/sessions", response_model=list[Session])
def list_sessions(student_id: str):
    rows = db.list_sessions(student_id)
    out: list[Session] = []
    for r in rows:
        out.append(_session_row_to_model(r, with_segments=False))
    return out


@app.get("/api/v1/sessions/{session_id}", response_model=Session)
def get_session(session_id: str):
    row = db.get_session(session_id)
    if not row:
        raise HTTPException(404, "Session not found")
    return _session_row_to_model(row, with_segments=True)


@app.get("/api/v1/sessions/{session_id}/status")
def get_session_status(session_id: str):
    row = db.get_session(session_id)
    if not row:
        raise HTTPException(404, "Session not found")
    return {"status": row["status"]}


@app.delete("/api/v1/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a lesson session and its dependent records from the database."""
    row = db.get_session(session_id)
    if not row:
        raise HTTPException(404, "Session not found")
    db.delete_session(session_id)
    return {"ok": True, "sessionId": session_id, "message": "Session deleted successfully"}


@app.post("/api/v1/sessions/{session_id}/language")
def switch_session_language(session_id: str, body: LanguageSwitchRequest):
    """Switch language mid-session. Re-renders remaining segments in the new language."""
    row = db.get_session(session_id)
    if not row:
        raise HTTPException(404, "Session not found")
    db.update_session(session_id, {"language": body.language})
    # In production, dispatch the language agent on remaining segments.
    # For the demo, we mark the session as 'regenerating' and trust the FE
    # to refetch segments; their narration scripts will be translated lazily.
    return {"status": "regenerating", "language": body.language}



def _format_video_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/tmp/"):
        filename = Path(url).name
        return f"http://localhost:8000/api/v1/videos/{filename}"
    return url


@app.api_route("/api/v1/videos/{filename}", methods=["GET", "HEAD"])
def get_video_stream(filename: str, request: Request):
    """Stream locally rendered MP4 video files with full HTTP 206 Range seeking support."""
    file_path: Optional[Path] = None
    for base in [Path("/tmp/shikshak_final"), Path("/tmp/shikshak_avatar"), Path("/tmp/shikshak_concept")]:
        p = base / filename
        if p.exists() and p.is_file():
            file_path = p
            break
    if not file_path:
        raise HTTPException(404, "Video not found")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("Range")

    if not range_header:
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
        }
        if request.method == "HEAD":
            return Response(status_code=200, headers=headers)

        def full_iter():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk

        return StreamingResponse(full_iter(), status_code=200, headers=headers, media_type="video/mp4")

    # Parse Range: bytes=start-end
    try:
        range_str = range_header.replace("bytes=", "").strip()
        parts = range_str.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        if start > end or start >= file_size:
            return Response(status_code=416, headers={"Content-Range": f"bytes */{file_size}"})
    except Exception:
        start = 0
        end = file_size - 1

    content_length = (end - start) + 1
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": "video/mp4",
    }

    if request.method == "HEAD":
        return Response(status_code=206, headers=headers)

    def range_iter(start_byte: int, end_byte: int):
        with open(file_path, "rb") as f:
            f.seek(start_byte)
            remaining = (end_byte - start_byte) + 1
            while remaining > 0:
                chunk_size = min(1024 * 1024, remaining)
                data = f.read(chunk_size)
                if not data:
                    break
                remaining -= len(data)
                yield data

    return StreamingResponse(
        range_iter(start, end),
        status_code=206,
        headers=headers,
        media_type="video/mp4",
    )


# ── Segments ──────────────────────────────────────────────────────────────────
@app.get("/api/v1/sessions/{session_id}/segments/{segment_id}/status")
def get_segment_status(session_id: str, segment_id: str):
    seg = (
        db.get_client()
        .table("lesson_segments")
        .select("*")
        .eq("id", segment_id)
        .eq("session_id", session_id)
        .execute()
    )
    if not seg.data:
        raise HTTPException(404, "Segment not found")
    s = seg.data[0]
    return {"status": s["status"], "videoUrl": _format_video_url(s.get("video_url"))}


# ── Deep Dive / Next Segment ─────────────────────────────────────────────────
class NextSegmentRequest(BaseModel):
    current_segment_id: str
    selected_concept: Optional[str] = None  # If None, auto-picks from related_concepts


@app.post("/api/v1/sessions/{session_id}/next-segment")
def generate_next_segment(session_id: str, body: NextSegmentRequest):
    """Generate a deep-dive segment for a related concept.

    If selected_concept is provided, generates a segment for that concept.
    Otherwise, picks the first unused related concept from the current segment.
    """
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(404, "Session not found")

    # Resolve the concept to dive into
    concept = body.selected_concept
    if not concept:
        # Find the current segment's related concepts
        seg = (
            db.get_client()
            .table("lesson_segments")
            .select("*")
            .eq("id", body.current_segment_id)
            .execute()
        )
        if seg.data:
            related = seg.data[0].get("related_concepts") or []
            concept = related[0] if related else seg.data[0].get("concept", "Review")

    if not concept:
        raise HTTPException(400, "No concept selected and no related concepts available")

    result = a_deep_dive.generate_deep_dive(
        session_id=session_id,
        concept=concept,
        level=sess["level"],
        language=sess["language"],
        parent_segment_order=0,
    )
    return result


@app.get("/api/v1/sessions/{session_id}/segments/{segment_id}/related-concepts")
def get_related_concepts(session_id: str, segment_id: str):
    """Get the concept graph (related topics) for a given segment."""
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(404, "Session not found")

    seg = (
        db.get_client()
        .table("lesson_segments")
        .select("*")
        .eq("id", segment_id)
        .execute()
    )
    if not seg.data:
        raise HTTPException(404, "Segment not found")

    s = seg.data[0]

    # If the segment already has related_concepts stored, return them
    stored = s.get("related_concepts")
    if stored and isinstance(stored, list) and len(stored) > 0:
        return {"related": [{"concept": c, "brief": "", "prerequisite": False, "difficulty": "same"} for c in stored]}

    # Otherwise, generate on demand
    topic = sess.get("topic", s.get("concept", ""))
    concepts = get_concept_graph_dict(
        topic=topic,
        current_concept=s["concept"],
        level=sess["level"],
    )
    return {"related": concepts}


@app.post(
    "/api/v1/sessions/{session_id}/segments/{segment_id}/render",
    dependencies=[Depends(_check_render_rate)],
)
def render_segment(session_id: str, segment_id: str):
    """Trigger the video pipeline for a single segment.
    Runs: Voice Synthesis → (Avatar Rendering + Concept Animation in parallel) → Video Compositing.
    """
    seg = (
        db.get_client()
        .table("lesson_segments")
        .select("*")
        .eq("id", segment_id)
        .eq("session_id", session_id)
        .execute()
    )
    if not seg.data:
        raise HTTPException(404, "Segment not found")
    s = seg.data[0]
    if not s.get("narration_script"):
        raise HTTPException(400, "Segment has no narration script to render")

    db.update_segment(segment_id, {"status": "rendering"})
    try:
        audio_path = a_voice.synthesize(
            narration_script=s["narration_script"],
            language=s.get("language", "en"),
        )
        audio_info = require_playable_audio(audio_path)
        # Avatar + concept run sequentially here (would be group() in Celery)
        avatar_path = a_avatar.render(audio_path=audio_path)
        scenes_list = db.list_scenes(segment_id)
        concept_out = a_concept.animate_segment(
            concept=s["concept"],
            visual_type=s["visual_type"],
            narration_script=s["narration_script"],
            language=s.get("language", "en"),
            depth=s.get("depth", "beginner"),
            segment_id=segment_id,
            duration_seconds=audio_info.duration_seconds,
            diagram_spec=s.get("diagram_spec_json"),
            scenes=scenes_list if scenes_list else s.get("animation_scenes_json"),
        )
        final_path = a_composite.composite_segment(
            avatar_video_path=avatar_path,
            concept_video_path=concept_out["video_path"],
            audio_path=audio_path,
            caption_text=s["concept"],
            language=s.get("language", "en"),
        )
        db.update_segment(segment_id, {"status": "ready", "video_url": final_path})
        return {"status": "ready", "videoUrl": _format_video_url(final_path), "provider": concept_out["provider"]}
    except Exception as e:
        db.update_segment(segment_id, {"status": "failed"})
        raise HTTPException(500, f"Rendering failed: {e}")


# ── Checkpoints ──────────────────────────────────────────────────────────────
@app.post("/api/v1/sessions/{session_id}/answer", response_model=SubmitAnswerResponse)
def submit_answer(session_id: str, body: SubmitAnswerRequest):
    """Submit an answer to a checkpoint. If wrong, returns an escalated misconception
    re-teach segment based on attempt count (simplify -> concrete_example -> atomic_steps)."""
    cp = db.get_checkpoint(body.checkpoint_id)
    if not cp:
        # Graceful fallback: check if body.checkpoint_id is a segment_id
        cp = db.get_checkpoint_by_segment(body.checkpoint_id)
    if not cp:
        raise HTTPException(404, "Checkpoint not found")

    result = a_eval.evaluate_answer(
        checkpoint_id=cp["id"],
        student_answer=body.answer,
    )

    if not result["is_correct"]:
        # Wire attempt counter: increment on each wrong answer
        # If it's the very first attempt on this checkpoint, attempt_number = 1
        if cp.get("student_answer") is not None or cp.get("reteach_strategy") is not None:
            attempt_number = int(cp.get("attempt_number") or 1) + 1
        else:
            attempt_number = 1

        strategy = a_md.select_reteach_strategy(attempt_number)

        # Diagnose + re-teach — fetch parent segment narration
        seg = (
            db.get_client()
            .table("lesson_segments")
            .select("*")
            .eq("id", cp["segment_id"])
            .execute()
        )
        original_explanation = seg.data[0]["narration_script"] if seg.data else ""
        reteach = a_md.diagnose_and_reteach(
            checkpoint_id=cp["id"],
            concept=seg.data[0]["concept"] if seg.data else (cp.get("concept") or "(unknown)"),
            student_answer=body.answer,
            correct_answer=cp["correct_answer"],
            original_explanation=original_explanation,
            language=(db.get_session(session_id) or {}).get("language", "en"),
            attempt_number=attempt_number,
            strategy=strategy,
            prior_analogies_used=cp.get("prior_analogies_used") or [],
            session_id=session_id,
        )
        # Persist the remediation as a new segment in the same session with order = max + 1
        existing = db.list_segments(session_id)
        next_order = (max((e["segment_order"] for e in existing), default=0)) + 1
        rows = db.insert_segments([{
            "session_id": session_id,
            "segment_order": next_order,
            "concept": reteach["concept"],
            "depth": reteach["depth"],
            "visual_type": reteach.get("visual_type", "diagram"),
            "narration_script": reteach["narration_script"],
            "has_checkpoint": False,
            "status": "pending",
        }])
        return SubmitAnswerResponse(
            is_correct=False,
            misconception=reteach["misconception"],
            next_segment_id=rows[0]["id"] if rows else None,
            attempt_number=attempt_number,
            reteach_strategy=strategy,
        )

    # Correct answer — find the next segment to play
    existing = db.list_segments(session_id)
    current_seg_order = (
        next((e["segment_order"] for e in existing if e["id"] == cp["segment_id"]), 0)
    )
    next_seg = next(
        (e for e in existing if e["segment_order"] > current_seg_order),
        None,
    )
    return SubmitAnswerResponse(
        is_correct=True,
        misconception=None,
        next_segment_id=next_seg["id"] if next_seg else None,
        attempt_number=cp.get("attempt_number", 1),
        reteach_strategy=cp.get("reteach_strategy"),
    )



# ── Assessment ────────────────────────────────────────────────────────────────
@app.get("/api/v1/sessions/{session_id}/report", response_model=AssessmentReportOut)
def get_report(session_id: str):
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(404, "Session not found")

    row = db.get_report(session_id)
    if not row:
        # Generate on-demand
        row = a_assess.assess_session(session_id=session_id)
        # Write back to learner profile
        a_profile.update_profile_from_report(
            student_id=sess["student_id"],
            topic=sess.get("topic") or "",
            score=row["score"],
            strong_areas=row["strong_areas"],
            weak_areas=row["weak_areas"],
        )
        db.update_session(session_id, {"status": "completed"})

    return AssessmentReportOut(
        session_id=row["session_id"],
        score=row["score"],
        strong_areas=row["strong_areas"],
        weak_areas=row["weak_areas"],
        recommendation=row["recommendation"],
    )


# ── Learner profile ───────────────────────────────────────────────────────────
@app.get("/api/v1/learner-profile/{student_id}", response_model=LearnerProfileOut)
def get_learner_profile(student_id: str):
    p = a_profile.read_profile(student_id)
    return LearnerProfileOut(
        student_id=p["id"],
        topics_studied=p.get("topics_studied", []),
        weak_concepts=p.get("weak_concepts", []),
        strong_concepts=p.get("strong_concepts", []),
        average_score=p.get("average_score", 0),
    )


@app.get("/api/v1/concept-mastery/{student_id}", response_model=list[ConceptMasteryOut])
def get_student_concept_mastery(student_id: str):
    """Return all continuous concept mastery records for a student."""
    rows = db.list_concept_mastery(student_id)
    return [
        ConceptMasteryOut(
            id=str(r.get("id") or ""),
            student_id=str(r.get("student_id") or student_id),
            concept=str(r.get("concept") or ""),
            score=float(r.get("score", 0.0)),
            status=r.get("status", "weak"),
            attempts=int(r.get("attempts", 0)),
            consecutive_strong=int(r.get("consecutive_strong", 0)),
            last_updated=r.get("last_updated"),
        )
        for r in rows
    ]



@app.patch("/api/v1/learner-profile/{student_id}", response_model=LearnerProfileOut)
def patch_learner_profile(student_id: str, body: PatchLearnerProfileRequest):
    patch = {}
    if body.default_level:
        patch["default_level"] = body.default_level
    if body.default_language:
        patch["default_language"] = body.default_language
    if patch:
        a_profile.read_profile(student_id)  # ensure exists
        db.patch_learner_profile(student_id, patch)
    return get_learner_profile(student_id)


# ── Learning paths ─────────────────────────────────────────────────────────────
@app.post("/api/v1/learning-paths", response_model=LearningPathOut)
def create_learning_path(body: CreateLearningPathRequest):
    path = a_lpath.build_path(student_id=body.student_id, broad_topic=body.broad_topic)
    # Fetch the persisted rows so we can return the real ids
    full = db.get_learning_path(path["id"])
    items = []
    for it in (full.get("learning_path_items") if full else []) or []:
        items.append({
            "id": it["id"],
            "item_order": it["item_order"],
            "sub_topic": it["sub_topic"],
            "status": it["status"],
            "related_session_id": it.get("related_session_id"),
        })
    return LearningPathOut(
        id=path["id"],
        broad_topic=body.broad_topic,
        items=sorted(items, key=lambda x: x["item_order"]),
    )


@app.get("/api/v1/learning-paths/{path_id}", response_model=LearningPathOut)
def get_learning_path(path_id: str):
    full = db.get_learning_path(path_id)
    if not full:
        raise HTTPException(404, "Learning path not found")
    items = []
    for it in full.get("learning_path_items") or []:
        items.append({
            "id": it["id"],
            "item_order": it["item_order"],
            "sub_topic": it["sub_topic"],
            "status": it["status"],
            "related_session_id": it.get("related_session_id"),
        })
    return LearningPathOut(
        id=full["id"],
        broad_topic=full["broad_topic"],
        items=sorted(items, key=lambda x: x["item_order"]),
    )


# ── Helpers ────────────────────────────────────────────────────────────────────
def _session_row_to_model(row: dict, with_segments: bool) -> Session:
    segments: list[LessonSegment] = []
    if with_segments:
        seg_rows = db.list_segments(row["id"])
        for s in seg_rows:
            segments.append(LessonSegment(
                id=s["id"],
                order=s["segment_order"],
                concept=s["concept"],
                depth=s["depth"],
                visual_type=s["visual_type"],
                narration_script=s["narration_script"],
                video_url=_format_video_url(s.get("video_url")),
                has_checkpoint=s.get("has_checkpoint", False),
            ))
    return Session(
        id=row["id"],
        student_id=row["student_id"],
        source_type=row["source_type"],
        document_id=row.get("document_id"),
        topic=row.get("topic"),
        level=row["level"],
        language=row["language"],
        time_budget_minutes=row["time_budget_minutes"],
        status=row["status"],
        segments=segments,
        created_at=row["created_at"],
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all → structured {error, agent, retryable} per TRD error strategy."""
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "agent": "unknown",
            "retryable": False,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
