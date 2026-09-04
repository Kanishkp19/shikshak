"""
Shikshak AI — Orchestrator Router.

Single responsibility: take a session_id and dispatch the agent DAG
defined in execution_plan.py — independent agents run via celery.group(),
dependent agents run via celery.chain() (per AI-TEACHER-AGENT-ARCHITECTURE.md
Section 5).

Also exposes a synchronous entry-point `run_session_pipeline()` for use
inside FastAPI request handlers when Celery isn't strictly required.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from orchestrator.execution_plan import build_execution_plan, Step
from skills.supabase_persistence import (
    get_session,
    update_session,
    insert_segments,
    update_segment,
    list_segments,
    insert_scenes,
    list_scenes,
    log_agent_run,
)
from skills.per_concept_retrieval import retrieve_for_concept_with_fallback
import agents.content_ingestion as a_content
import agents.knowledge_retrieval as a_kr
import agents.lesson_planning as a_lp
import agents.personalization as a_pers
import agents.time_budgeting as a_tb
import agents.language as a_lang
import agents.explanation as a_expl
import agents.scene_planning as a_sp
import agents.visual_selection as a_vs
import agents.interaction as a_int
import agents.qa_grounding_guard as a_qa
import agents.learner_profile as a_lp_profile
import skills.quality_gate as s_qg


_AGENT_FUNCS: dict[str, Any] = {
    "content_ingestion": a_content.ingest_document,
    "knowledge_retrieval": a_kr.retrieve,
    "lesson_planning": a_lp.plan_lesson,
    "personalization": a_pers.personalize,
    "time_budgeting": a_tb.budget_segments,
    "language": a_lang.apply_language,
    "visual_selection": a_vs.select_visuals,
    "explanation": a_expl.explain_segment,
    "scene_planning": a_sp.plan_scenes_for_segment,
    "qa_grounding_guard": a_qa.guard,
    "interaction": a_int.generate_checkpoint,
}


def run_session_pipeline(session_id: str) -> dict[str, Any]:
    """Synchronous orchestrator entry point — runs the DAG in-process.

    Returns the final session state with persisted segments + checkpoints.
    """
    sess = get_session(session_id)
    if not sess:
        raise ValueError(f"Session {session_id} not found")

    # Read student weak concepts so the lesson plan can remediate them
    profile = a_lp_profile.read_profile(sess["student_id"])
    weak_concepts = profile.get("weak_concepts") or []

    steps = build_execution_plan(
        session_id=session_id,
        student_id=sess["student_id"],
        source_type=sess["source_type"],
        document_id=sess.get("document_id"),
        topic=sess.get("topic"),
        level=sess["level"],
        language=sess["language"],
        time_budget_minutes=sess["time_budget_minutes"],
        weak_concepts=weak_concepts,
    )

    plan: dict[str, Any] = {"topic": sess.get("topic"), "language": sess["language"], "level": sess["level"]}
    retrieved_chunks: list[dict] = []
    chunks_per_segment: dict[int, list[dict]] = {}
    pdf_structure: dict[str, Any] = {}
    document_id: str | None = sess.get("document_id")

    for step in steps:
        t0 = time.time()
        try:
            if step.agent == "content_ingestion":
                result = a_content.ingest_document(step.args["document_id"])
                pdf_structure = result.get("pdf_structure") or {}
                if pdf_structure.get("sections"):
                    print(
                        f"[orchestrator] PDF structure extracted: "
                        f"{len(pdf_structure['sections'])} sections, "
                        f"{pdf_structure.get('page_count', '?')} pages"
                    )
            elif step.agent == "knowledge_retrieval":
                retrieved_chunks = a_kr.retrieve(
                    query=step.args["query"],
                    document_id=step.args["document_id"],
                )
            elif step.agent == "lesson_planning":
                plan = a_lp.plan_lesson(
                    topic=step.args["topic"],
                    level=step.args["level"],
                    time_budget_minutes=step.args["time_budget_minutes"],
                    language=step.args["language"],
                    has_source=step.args["has_source"],
                    weak_concepts=step.args["weak_concepts"],
                    document_id=step.args["document_id"],
                    pdf_structure=pdf_structure,
                )
            elif step.agent == "personalization":
                plan = a_pers.personalize(
                    plan=plan,
                    level=step.args["level"],
                    weak_concepts=step.args["weak_concepts"],
                )
            elif step.agent == "time_budgeting":
                plan = a_tb.budget_segments(
                    plan=plan,
                    time_budget_minutes=step.args["time_budget_minutes"],
                )
            elif step.agent == "visual_selection":
                plan = a_vs.select_visuals(plan)
            elif step.agent == "language":
                plan = a_lang.apply_language(
                    plan=plan,
                    target_language=step.args["target_language"],
                    current_language=step.args["current_language"],
                )
            elif step.agent == "explanation":
                per_seg_words = plan.get("per_segment_words", 200)
                for s in plan["segments"]:
                    if s.get("narration_script"):
                        continue
                    seg_chunks = retrieve_for_concept_with_fallback(
                        concept=s["concept"],
                        document_id=document_id,
                        source_text=s.get("source_text") or "",
                        top_k=5,
                    )
                    if not seg_chunks and retrieved_chunks and not s.get("is_remediation"):
                        seg_chunks = retrieved_chunks

                    source_text = s.get("source_text", "").strip()
                    if source_text:
                        source_chunk = {
                            "content": source_text,
                            "section_label": s["concept"],
                            "chunk_index": -1,
                        }
                        seg_chunks = [source_chunk] + [
                            c for c in (seg_chunks or [])
                            if c.get("content", "").strip() != source_text
                        ][:4]
                    elif not seg_chunks:
                        if document_id and not s.get("is_remediation"):
                            # Corrective RAG (CRAG) decline: concept absent from uploaded document
                            print(f"[orchestrator] CRAG decline: '{s['concept']}' not covered in document {document_id}")
                            s["not_covered"] = True
                            s["narration_script"] = (
                                f"The concept '{s['concept']}' is not covered in the uploaded material. "
                                "Shikshak AI will not invent information outside your source document."
                            )
                            s["has_checkpoint"] = False
                            continue
                        print(
                            f"[orchestrator] WARNING: No source material for "
                            f"'{s['concept']}' — LLM will generate from scratch"
                        )

                    # 1. Explanation Blueprint
                    expl_result = a_expl.explain_segment_with_blueprint(
                        concept=s["concept"],
                        level=s["depth"],
                        language=sess["language"],
                        retrieved_chunks=seg_chunks,
                        per_segment_words=per_seg_words,
                    )
                    s["narration_script"] = expl_result["narration_script"]
                    s["diagram_spec"] = expl_result.get("diagram_spec")
                    s["animation_scenes"] = expl_result.get("scenes")
                    chunks_per_segment[s["order"]] = seg_chunks

                    # 2. Scene Planning Agent
                    raw_scenes = a_sp.plan_scenes_for_segment(
                        concept=s["concept"],
                        level=s["depth"],
                        language=sess["language"],
                        narration_script=s["narration_script"],
                        retrieved_chunks=seg_chunks,
                        animation_scenes=s.get("animation_scenes"),
                    )

                    # 3. Quality Gate Audit
                    audited_scenes = s_qg.audit_scenes_for_segment(
                        scenes=raw_scenes,
                        concept=s["concept"],
                        session_id=session_id,
                    )
                    s["scenes"] = audited_scenes

            elif step.agent == "qa_grounding_guard":
                for s in plan["segments"]:
                    seg_chunks = chunks_per_segment.get(s["order"], [])
                    result = a_qa.guard(
                        concept=s["concept"],
                        level=s["depth"],
                        language=sess["language"],
                        narration_script=s["narration_script"],
                        retrieved_chunks=seg_chunks,
                    )
                    s["narration_script"] = result["narration_script"]
            elif step.agent == "interaction":
                # Persist segments FIRST (so checkpoints and scenes can FK them)
                _persist_segments(session_id, plan)
                for s in plan["segments"]:
                    if s.get("has_checkpoint"):
                        a_int.generate_checkpoint(
                            segment_id=s["_db_id"],
                            concept=s["concept"],
                            level=s["depth"],
                            language=sess["language"],
                        )
            _log_step(session_id, step.agent, t0, "success")
        except Exception as e:
            _log_step(session_id, step.agent, t0, "failed", error=str(e))
            raise

    # If segments weren't persisted yet (no interaction step), persist now
    if not _segments_persisted(session_id):
        _persist_segments(session_id, plan)

    update_session(session_id, {"status": "in_progress"})
    return {"session_id": session_id, "status": "in_progress", "segments": plan["segments"]}


def _persist_segments(session_id: str, plan: dict[str, Any]) -> None:
    """Insert lesson_segments and scenes rows (idempotent)."""
    existing = list_segments(session_id)
    if existing:
        for s in plan["segments"]:
            for e in existing:
                if e["segment_order"] == s["order"]:
                    s["_db_id"] = e["id"]
                    # If scenes not in DB, insert them
                    if s.get("scenes"):
                        insert_scenes(e["id"], s["scenes"])
                    break
        return

    rows = []
    for s in plan["segments"]:
        row_data = {
            "session_id": session_id,
            "segment_order": s["order"],
            "concept": s["concept"],
            "depth": s["depth"],
            "visual_type": s.get("visual_type", "none"),
            "narration_script": s.get("narration_script", ""),
            "has_checkpoint": s.get("has_checkpoint", False),
            "status": "pending",
        }
        if s.get("diagram_spec"):
            row_data["diagram_spec_json"] = s["diagram_spec"]
        if s.get("animation_scenes"):
            row_data["animation_scenes_json"] = s["animation_scenes"]
        if s.get("related_concepts"):
            row_data["related_concepts"] = s["related_concepts"]
        rows.append(row_data)

    inserted = insert_segments(rows)
    for s, row in zip(plan["segments"], inserted):
        s["_db_id"] = row["id"]
        # Persist structured scenes for this segment
        if s.get("scenes"):
            try:
                insert_scenes(row["id"], s["scenes"])
            except Exception as e:
                print(f"[orchestrator] Notice: scenes persistence ({e})")


def _segments_persisted(session_id: str) -> bool:
    return bool(list_segments(session_id))


def _log_step(
    session_id: str,
    agent_name: str,
    t0: float,
    status: str,
    error: Optional[str] = None,
) -> None:
    try:
        log_agent_run(
            session_id=session_id,
            agent_name=agent_name,
            status=status,
            duration_ms=int((time.time() - t0) * 1000),
            error_message=error,
        )
    except Exception:
        pass
