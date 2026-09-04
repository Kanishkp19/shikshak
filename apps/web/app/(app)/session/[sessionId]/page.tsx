"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { LessonPlayer } from "@/components/lesson/LessonPlayer";
import { SegmentTimeline } from "@/components/lesson/SegmentTimeline";
import { ChapterContents } from "@/components/lesson/ChapterContents";
import { QuestionCard } from "@/components/lesson/QuestionCard";
import { RelatedConcepts } from "@/components/lesson/RelatedConcepts";
import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { LessonSegment, Session, SubmitAnswerResponse } from "@/lib/types";

/**
 * Shikshak AI — Lesson Player screen (/session/[sessionId]) (v2).
 *
 * Major improvements:
 *   - No intro clip — jumps directly to concept content
 *   - Related concepts panel for deep-dive exploration
 *   - Synchronized scrolling transcript in LessonPlayer
 *   - Deep-dive segment generation on concept selection
 *   - Concept exploration tracking
 */

interface RelatedConcept {
  concept: string;
  brief: string;
  prerequisite: boolean;
  difficulty: string;
}

export default function SessionPlayerPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;
  const router = useRouter();
  const { push } = useToast();

  const [session, setSession] = React.useState<Session | null>(null);
  const [activeOrder, setActiveOrder] = React.useState(1);
  const [renderStatus, setRenderStatus] = React.useState<
    Record<string, "pending" | "rendering" | "ready" | "failed">
  >({});
  const [showQuestionFor, setShowQuestionFor] = React.useState<string | null>(null);
  const [submittingAnswer, setSubmittingAnswer] = React.useState(false);
  const [graded, setGraded] = React.useState<{ correct: boolean | null; misconception?: string | null }>(
    { correct: null },
  );

  // Related concepts state
  const [relatedConcepts, setRelatedConcepts] = React.useState<RelatedConcept[]>([]);
  const [loadingRelated, setLoadingRelated] = React.useState(false);
  const [exploredConcepts, setExploredConcepts] = React.useState<Set<string>>(new Set());
  const [generatingDeepDive, setGeneratingDeepDive] = React.useState(false);

  // Helper to sync render status and videoUrl into React state
  function updateSegmentRender(
    segmentId: string,
    status: "ready" | "failed" | "rendering" | "pending",
    videoUrl?: string | null
  ) {
    setRenderStatus((prev) => ({ ...prev, [segmentId]: status }));
    if (videoUrl) {
      setSession((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          segments: prev.segments.map((s) =>
            s.id === segmentId ? { ...s, videoUrl } : s
          ),
        };
      });
    }
  }

  // Fetch related concepts for a segment
  const fetchRelatedConcepts = React.useCallback(
    async (segmentId: string) => {
      setLoadingRelated(true);
      try {
        const res = await api.getRelatedConcepts(sessionId, segmentId);
        setRelatedConcepts(res.related || []);
      } catch {
        setRelatedConcepts([]);
      } finally {
        setLoadingRelated(false);
      }
    },
    [sessionId],
  );

  const triggerRender = React.useCallback(
    (segment: LessonSegment) => {
      setRenderStatus((prev) => ({ ...prev, [segment.id]: "rendering" }));
      api
        .renderSegment(sessionId, segment.id)
        .then((res) => {
          updateSegmentRender(segment.id, res.status as any, res.videoUrl);
        })
        .catch((e) => {
          const msg = e instanceof ApiError ? e.message : "Render failed.";
          push("error", `Video unavailable for this part — audio lesson below. (${msg})`);
          setRenderStatus((prev) => ({ ...prev, [segment.id]: "failed" }));
        });
    },
    [sessionId, push],
  );

  // Load session
  React.useEffect(() => {
    if (!sessionId) return;
    api
      .getSession(sessionId)
      .then((s) => {
        setSession(s);
        const initialMap: Record<string, any> = {};
        s.segments.forEach((seg) => {
          if (seg.videoUrl) initialMap[seg.id] = "ready";
        });
        setRenderStatus((prev) => ({ ...initialMap, ...prev }));

        // Immediately render the first segment (no intro delay)
        if (s.segments.length > 0) {
          const first = s.segments[0];
          if (!first.videoUrl) {
            triggerRender(first);
          }
        }
      })
      .catch((e) => {
        const msg = e instanceof ApiError ? e.message : "Couldn't load lesson.";
        push("error", msg);
      });
  }, [sessionId, push, triggerRender]);

  // Poll render status of active segment
  React.useEffect(() => {
    if (!session) return;
    const active = session.segments.find((s) => s.order === activeOrder);
    if (!active) return;
    if (renderStatus[active.id] === "ready") {
      if (active.hasCheckpoint) setShowQuestionFor(active.id);
      // Fetch related concepts when segment is ready
      fetchRelatedConcepts(active.id);
      return;
    }
    let cancelled = false;
    const interval = setInterval(async () => {
      try {
        const res = await api.getSegmentStatus(sessionId, active.id);
        if (cancelled) return;
        updateSegmentRender(active.id, res.status as any, res.videoUrl);
        if (res.status === "ready") {
          if (active.hasCheckpoint) setShowQuestionFor(active.id);
          fetchRelatedConcepts(active.id);
          clearInterval(interval);
        } else if (res.status === "failed") {
          clearInterval(interval);
        }
      } catch {
        // keep polling
      }
    }, 2500);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [session, activeOrder, renderStatus, fetchRelatedConcepts, sessionId]);

  function nextSegment() {
    if (!session) return;
    const next = session.segments.find((s) => s.order > activeOrder);
    if (next) {
      setActiveOrder(next.order);
      setGraded({ correct: null });
      setShowQuestionFor(null);
      setRelatedConcepts([]);
      if (renderStatus[next.id] !== "ready" && renderStatus[next.id] !== "rendering") {
        triggerRender(next);
      }
    } else {
      // No more segments → go to report
      router.push(`/session/${sessionId}/report`);
    }
  }

  // Handle deep-dive concept selection
  async function handleConceptSelect(concept: string) {
    if (!session) return;
    const active = session.segments.find((s) => s.order === activeOrder);
    if (!active) return;

    setGeneratingDeepDive(true);
    setExploredConcepts((prev) => new Set(prev).add(concept));

    try {
      push("info", `Generating deep-dive on "${concept}"…`);
      const newSegment = await api.generateNextSegment(sessionId, active.id, concept);

      // Refresh session to include the new segment
      const fresh = await api.getSession(sessionId);
      setSession(fresh);

      // Navigate to the new segment
      if (newSegment.order) {
        setActiveOrder(newSegment.order);
        setGraded({ correct: null });
        setShowQuestionFor(null);
        setRelatedConcepts([]);

        // Find the segment in the fresh session and trigger render
        const seg = fresh.segments.find((s) => s.order === newSegment.order);
        if (seg && renderStatus[seg.id] !== "ready") {
          triggerRender(seg);
        }
      }

      push("success", `Deep-dive on "${concept}" ready!`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Couldn't generate deep-dive.";
      push("error", msg);
    } finally {
      setGeneratingDeepDive(false);
    }
  }

  async function handleAnswer(answer: string) {
    if (!session) return;
    const active = session.segments.find((s) => s.order === activeOrder);
    if (!active) return;
    setSubmittingAnswer(true);
    try {
      // NOTE: The backend auto-creates a checkpoint when a segment has
      // has_checkpoint=true. The frontend doesn't know the checkpoint_id
      // from /sessions/{id} — to keep the demo self-contained, we POST
      // a placeholder id derived from the segment id and the backend's
      // submit_answer handler resolves it.
      const res: SubmitAnswerResponse = await api.submitAnswer(
        sessionId,
        active.id, // backend tolerates a segment id fallback
        answer,
      );
      setGraded({
        correct: res.isCorrect,
        misconception: res.misconception,
      });
      if (res.isCorrect) {
        push("success", "Correct! Moving on.");
        setTimeout(nextSegment, 1500);
      } else {
        push("warning", "Re-teaching this concept with a different analogy.");
        // The backend has spliced a remediation segment — refetch session
        const fresh = await api.getSession(sessionId);
        setSession(fresh);
        setTimeout(nextSegment, 2000);
      }
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Couldn't submit answer.";
      push("error", msg);
    } finally {
      setSubmittingAnswer(false);
    }
  }

  async function handleLanguageChange(lang: string) {
    try {
      await api.switchLanguage(sessionId, lang);
      push("info", `Switching to ${lang} for the remaining segments…`);
      // Refetch to get regenerated narration
      const fresh = await api.getSession(sessionId);
      setSession(fresh);
    } catch (e) {
      push("error", (e as Error).message);
    }
  }

  if (!session) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-3 flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-sky-400" />
          </div>
          <p className="text-body-md text-[var(--color-ink-muted)]">Loading your lesson…</p>
        </div>
      </div>
    );
  }

  const activeSegment = session.segments.find((s) => s.order === activeOrder);
  const checkpoints = session.segments
    .filter((s) => s.hasCheckpoint)
    .map((s) => s.order);
  const completed = activeOrder - 1;
  const activeStatus = activeSegment
    ? renderStatus[activeSegment.id] ?? "pending"
    : "pending";

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Studio Desk Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-[var(--color-hairline)] pb-4">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs font-medium text-[var(--color-ink-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-all shrink-0"
          >
            <span>←</span>
            <span>Study Desk</span>
          </Link>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-heading-2 font-bold text-[var(--color-ink)] leading-tight truncate">
                {session.topic ?? "Classroom Lesson"}
              </h1>
              <span className="shrink-0 rounded-md bg-[var(--color-accent-amber-soft)] text-[var(--color-accent-amber)] px-2 py-0.5 text-[11px] font-semibold border border-[var(--color-accent-amber)]/30">
                {session.level}
              </span>
            </div>
            <p className="text-caption text-[var(--color-ink-muted)] truncate">
              Interactive Classroom Studio · Topic {activeOrder} of {session.segments.length}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button onClick={nextSegment} variant="study-amber" className="text-xs px-4 py-2">
            {activeOrder < session.segments.length ? "Next Segment →" : "Finish Lesson →"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_340px] 2xl:grid-cols-[minmax(0,1fr)_370px] gap-6 items-start">
        {/* Left: Blackboard Stage + Question Checkpoint + Deep Dive Concepts */}
        <div className="space-y-6 min-w-0">
          {activeSegment && (
            <>
              {/* Slate Blackboard Video Frame */}
              <div className="rounded-2xl border border-[var(--color-hairline-chalk)] bg-[var(--color-chalk-board)] p-3.5 shadow-xl relative overflow-hidden">
                <LessonPlayer
                  videoUrl={activeSegment.videoUrl}
                  status={activeStatus}
                  narrationScript={activeSegment.narrationScript}
                  language={session.language}
                  onLanguageChange={handleLanguageChange}
                />
              </div>

              {/* Segment Timeline (Roadmap) */}
              <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-xs">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-[var(--color-ink-muted)] uppercase tracking-wider">
                    Lesson Roadmap
                  </span>
                  <span className="text-xs font-semibold text-[var(--color-primary)] truncate max-w-[65%] text-right">
                    Topic {activeOrder} of {session.segments.length}: {activeSegment.concept}
                  </span>
                </div>
                <SegmentTimeline
                  total={session.segments.length}
                  current={activeOrder}
                  completed={completed}
                  checkpoints={checkpoints}
                  onSelect={(i) => setActiveOrder(i + 1)}
                />
              </div>
            </>
          )}

          {/* Socratic Checkpoint question */}
          {showQuestionFor === activeSegment?.id && graded.correct === null && (
            <div className="animate-in fade-in slide-in-from-top-3 duration-200">
              <QuestionCard
                prompt={`Check your understanding of: ${activeSegment?.concept}`}
                type="short_answer"
                options={null}
                submitting={submittingAnswer}
                gradedCorrect={null}
                onSubmit={handleAnswer}
              />
            </div>
          )}

          {/* Related Concepts for deep-dive exploration */}
          {activeSegment && activeStatus === "ready" && (
            <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-5 shadow-xs">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-[var(--color-ink-muted)] flex items-center gap-1.5">
                  <span>🗺️</span>
                  <span>Explore Related Topics (Curiosity Branch)</span>
                </span>
                <span className="text-[11px] text-[var(--color-ink-faint)]">Click to auto-generate a deep dive</span>
              </div>
              <RelatedConcepts
                concepts={relatedConcepts as any}
                loading={loadingRelated || generatingDeepDive}
                onSelect={handleConceptSelect}
                exploredConcepts={exploredConcepts}
              />
            </div>
          )}
        </div>

        {/* Right: Spiral Notebook Co-pilot (Syllabus Roadmap + Lecture Notes + Segment Info) */}
        <div className="space-y-5 min-w-0">
          {/* Chapter Contents / Syllabus Table */}
          <ChapterContents
            segments={session.segments}
            activeOrder={activeOrder}
            renderStatus={renderStatus}
            onSelectSegment={(order) => {
              const target = session.segments.find((s) => s.order === order);
              if (target) {
                setActiveOrder(target.order);
                setGraded({ correct: null });
                setShowQuestionFor(null);
                setRelatedConcepts([]);
                if (
                  renderStatus[target.id] !== "ready" &&
                  renderStatus[target.id] !== "rendering"
                ) {
                  triggerRender(target);
                }
              }
            }}
          />

          {/* My Study Spiral Notes & Spoken Transcript */}
          <Card variant="notebook" className="shadow-xs">
            <CardBody className="p-4 sm:p-5">
              <div className="flex items-center justify-between mb-3 border-b border-[var(--color-hairline)] pb-2.5">
                <CardTitle className="text-xs font-bold text-[var(--color-ink)] flex items-center gap-2 uppercase tracking-wide">
                  <span>📝</span>
                  <span>Study Spiral Notes</span>
                </CardTitle>
                <span className="text-[10px] font-semibold text-[var(--color-primary)] bg-[var(--color-accent-sky-soft)] px-2 py-0.5 rounded-full border border-[var(--color-primary)]/20">
                  Topic {activeOrder}
                </span>
              </div>
              <div className="max-h-52 overflow-y-auto pr-1 text-xs text-[var(--color-ink-secondary)] leading-relaxed whitespace-pre-wrap scrollbar-thin">
                {activeSegment?.narrationScript || "Lecture notes and key definitions will stream here when the topic begins."}
              </div>
            </CardBody>
          </Card>

          {/* Segment Details Card */}
          {activeSegment && (
            <Card variant="elevated" className="bg-[var(--color-canvas)]">
              <CardBody className="p-4 sm:p-5">
                <CardTitle className="text-xs font-bold uppercase tracking-wide mb-3 flex items-center gap-2 text-[var(--color-ink)]">
                  <span>📊</span>
                  <span>Topic Blueprint</span>
                </CardTitle>
                <div className="space-y-2.5 text-xs text-[var(--color-ink-secondary)]">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[var(--color-ink-muted)] shrink-0">Current Concept:</span>
                    <span className="font-semibold text-[var(--color-ink)] text-right truncate">{activeSegment.concept}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[var(--color-ink-muted)]">Pedagogic Depth:</span>
                    <span className="capitalize font-semibold text-[var(--color-primary)]">{activeSegment.depth}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[var(--color-ink-muted)]">Tutor Engine:</span>
                    <span className={
                      activeStatus === "ready" ? "text-[var(--color-accent-teal)] font-medium" :
                      activeStatus === "rendering" ? "text-[var(--color-accent-amber)] font-medium animate-pulse" :
                      activeStatus === "failed" ? "text-[var(--color-accent-coral)] font-medium" :
                      "text-[var(--color-ink-muted)]"
                    }>
                      {activeStatus === "ready" ? "✓ Video & Audio Active" :
                       activeStatus === "rendering" ? "⏳ Synthesizing Board Visuals…" :
                       activeStatus === "failed" ? "✗ Audio Fallback" :
                       "Queued"}
                    </span>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Delete Lesson Section */}
          <DeleteSessionSection sessionId={sessionId} topic={session.topic} />
        </div>
      </div>
    </div>
  );
}

function DeleteSessionSection({ sessionId, topic }: { sessionId: string; topic?: string | null }) {
  const router = useRouter();
  const { push } = useToast();
  const [confirmDelete, setConfirmDelete] = React.useState(false);
  const [deleting, setDeleting] = React.useState(false);

  async function handleDelete() {
    setDeleting(true);
    try {
      await api.deleteSession(sessionId);
      push("success", `Deleted lesson: "${topic || "Untitled"}"`);
      router.push("/dashboard");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to delete lesson.";
      push("error", msg);
      setDeleting(false);
      setConfirmDelete(false);
    }
  }

  return (
    <Card variant="elevated" className="border border-red-500/20 bg-red-500/5">
      <CardBody>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-body-sm font-medium text-red-400">Delete Lesson</p>
            <p className="text-caption text-[var(--color-ink-muted)]">Remove this lesson and its data</p>
          </div>
          {!confirmDelete ? (
            <button
              onClick={() => setConfirmDelete(true)}
              className="px-3 py-1.5 text-xs font-medium rounded-md border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors"
            >
              Delete
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                disabled={deleting}
                onClick={handleDelete}
                className="px-3 py-1.5 text-xs font-semibold rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 transition-colors"
              >
                {deleting ? "Deleting…" : "Confirm"}
              </button>
              <button
                disabled={deleting}
                onClick={() => setConfirmDelete(false)}
                className="px-2.5 py-1.5 text-xs rounded-md bg-white/10 text-[var(--color-ink)] hover:bg-white/20 transition-colors"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}

