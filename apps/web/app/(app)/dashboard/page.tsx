"use client";

import * as React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { formatRelativeDate, subjectColor } from "@/lib/utils";
import type { LearnerProfile, Session } from "@/lib/types";

// Placeholder student id — production: read from Supabase auth state.
const STUDENT_ID =
  process.env.NEXT_PUBLIC_STUDENT_ID ?? "00000000-0000-0000-0000-000000000001";

export default function DashboardPage() {
  const { push } = useToast();
  const [sessions, setSessions] = React.useState<Session[] | null>(null);
  const [profile, setProfile] = React.useState<LearnerProfile | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [activeFilter, setActiveFilter] = React.useState<string>("all");

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const [sess, prof] = await Promise.all([
          api.listSessions(STUDENT_ID).catch((e) => {
            if (e instanceof ApiError) push("error", e.message);
            return [] as Session[];
          }),
          api.getLearnerProfile(STUDENT_ID).catch(() => null),
        ]);
        if (cancelled) return;
        setSessions(sess);
        setProfile(prof);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [push]);


  // Filter sessions by subject tab
  const filteredSessions = React.useMemo(() => {
    if (!sessions) return [];
    if (activeFilter === "all") return sessions;
    return sessions.filter((s) => subjectLabel(s.topic ?? "").toLowerCase() === activeFilter);
  }, [sessions, activeFilter]);

  return (
    <div className="mx-auto max-w-[1140px] px-6 py-10">
      {/* Desk Greeting Header */}
      <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-heading-1 font-serif text-[var(--color-ink)] mb-1">
            Today&apos;s Study Desk
          </h1>
          <p className="text-body-sm text-[var(--color-ink-muted)]">
            Pick up right where you left off or start exploring a new topic.
          </p>
        </div>

        <Link href="/session/new">
          <Button variant="primary" className="shadow-xs text-xs px-4 py-2">
            Start a New Lesson →
          </Button>
        </Link>
      </header>

      {/* Learner Progress & Mastery Garden Card */}
      <Card variant="elevated" className="mb-10 bg-[var(--color-canvas)]">
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <CardTitle className="text-base font-semibold">Study Progress & Mastery</CardTitle>
            <span className="text-xs font-mono text-[var(--color-ink-faint)]">Updated today</span>
          </div>

          {profile ? (
            <div className="grid gap-6 sm:grid-cols-4">
              <Stat label="Topics Explored" value={profile.topicsStudied.length} />
              <Stat label="Average Score" value={`${Math.round(profile.averageScore)}%`} />
              <div className="sm:col-span-2">
                <p className="text-eyebrow text-[var(--color-ink-muted)] mb-1.5 flex items-center gap-1">
                  <span>Concepts to Polish</span>
                </p>
                {profile.weakConcepts.length === 0 ? (
                  <p className="text-body-sm text-[var(--color-accent-teal)] font-medium">
                    ✓ All concepts well understood! Keep exploring new topics.
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {profile.weakConcepts.map((concept) => (
                      <Link
                        key={concept}
                        href={`/session/new?topic=${encodeURIComponent(concept)}`}
                        className="group inline-flex items-center gap-1 rounded-md border border-[var(--color-accent-amber)]/30 bg-[var(--color-accent-amber-soft)]/40 px-2.5 py-1 text-xs text-[var(--color-ink-secondary)] hover:bg-[var(--color-accent-amber-soft)] transition-colors"
                      >
                        <span>{concept}</span>
                        <span className="text-[10px] font-mono text-[var(--color-accent-amber)] group-hover:underline font-semibold">
                          Review 5m →
                        </span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <p className="text-body-sm text-[var(--color-ink-muted)]">
              Loading your study stats…
            </p>
          )}
        </CardBody>
      </Card>

      {/* Subject Notebook Binders Section */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-heading-2 text-[var(--color-ink)]">Recent Lesson Notebooks</h2>

        {/* Subject Filter Tabs */}
        <div className="flex items-center gap-1 text-xs">
          {["all", "math", "science", "cs", "history"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveFilter(tab)}
              className={`rounded-full px-3 py-1 font-medium capitalize transition-colors ${
                activeFilter === tab
                  ? "bg-[var(--color-primary)] text-white"
                  : "text-[var(--color-ink-secondary)] hover:bg-[var(--color-canvas-desk)]"
              }`}
            >
              {tab === "all" ? "All" : tab}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid gap-5 md:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : filteredSessions.length === 0 ? (
        <Card variant="study-desk">
          <CardBody className="text-center py-12">
            <div className="w-8 h-8 rounded-full bg-[var(--color-canvas-desk)] border border-[var(--color-hairline)] mx-auto flex items-center justify-center text-xs font-serif text-[var(--color-ink-faint)] mb-3">
              ∑
            </div>
            <p className="text-body-md text-[var(--color-ink-secondary)] mb-4 font-medium">
              No lesson notebooks found in this category.
            </p>
            <Link href="/session/new">
              <Button variant="primary">Start a New Lesson</Button>
            </Link>
          </CardBody>
        </Card>
      ) : (
        <div className="grid gap-5 md:grid-cols-3">
          {filteredSessions.map((s) => (
            <SessionCard
              key={s.id}
              session={s}
              onDelete={(id) => {
                setSessions((prev) => (prev ? prev.filter((item) => item.id !== id) : prev));
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-3.5">
      <div className="text-[10.5px] font-mono uppercase tracking-wider text-[var(--color-ink-muted)] mb-1">
        {label}
      </div>
      <p className="text-xl font-bold font-serif text-[var(--color-ink)]">{value}</p>
    </div>
  );
}


function SessionCard({
  session,
  onDelete,
}: {
  session: Session;
  onDelete: (id: string) => void;
  }) {
  const { push } = useToast();
  const color = subjectColor(session.topic ?? "");
  const [confirmDelete, setConfirmDelete] = React.useState(false);
  const [deleting, setDeleting] = React.useState(false);

  async function handleDelete(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDeleting(true);
    try {
      await api.deleteSession(session.id);
      push("success", `Deleted lesson: "${session.topic || "Untitled"}"`);
      onDelete(session.id);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to delete lesson.";
      push("error", msg);
      setDeleting(false);
      setConfirmDelete(false);
    }
  }

  return (
    <Card headerColor={color} className="h-full transition-all hover:shadow-[var(--shadow-level-2)] hover:-translate-y-0.5 relative flex flex-col justify-between bg-[var(--color-canvas)]">
      <CardBody className="flex flex-col h-full">
        <div className="mb-2 flex items-start justify-between gap-2">
          <Link href={`/session/${session.id}`} className="hover:text-[var(--color-primary)] transition-colors flex-1">
            <CardTitle className="line-clamp-2 leading-snug">{session.topic ?? "Untitled lesson"}</CardTitle>
          </Link>
          <div className="flex items-center gap-1.5 shrink-0">
            <Badge color={color}>{subjectLabel(session.topic ?? "")}</Badge>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setConfirmDelete((v) => !v);
              }}
              title="Delete lesson"
              className="p-1 rounded-md text-[var(--color-ink-faint)] hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>

        <p className="text-caption text-[var(--color-ink-faint)] mb-4">
          {formatRelativeDate(session.createdAt)} · {session.timeBudgetMinutes}m · {session.level}
        </p>

        {confirmDelete && (
          <div className="mb-3 p-2.5 rounded-lg bg-red-50 border border-red-200 text-body-sm text-red-800 animate-in fade-in duration-150">
            <p className="font-medium text-xs mb-2">Permanently delete this lesson?</p>
            <div className="flex items-center gap-2">
              <button
                disabled={deleting}
                onClick={handleDelete}
                className="px-2.5 py-1 text-xs font-semibold rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 transition-colors"
              >
                {deleting ? "Deleting…" : "Yes, delete"}
              </button>
              <button
                disabled={deleting}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setConfirmDelete(false);
                }}
                className="px-2.5 py-1 text-xs rounded bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between mt-auto pt-3 border-t border-[var(--color-hairline)]">
          {session.status === "in_progress" && (
            <Badge variant="filled" color="var(--color-accent-teal)">In progress</Badge>
          )}
          {session.status === "completed" && (
            <Link href={`/session/${session.id}/report`}>
              <Button variant="utility" className="text-xs">Report</Button>
            </Link>
          )}
          <Link href={`/session/${session.id}`}>
            <Button variant="utility" className="text-xs font-semibold">Study Now →</Button>
          </Link>
        </div>
      </CardBody>
    </Card>
  );
}

function SkeletonCard() {
  return (
    <Card className="animate-pulse bg-[var(--color-canvas)]">
      <div className="h-1.5 rounded-t-lg bg-[var(--color-hairline)]" />
      <CardBody>
        <div className="h-6 w-2/3 rounded-md bg-[var(--color-hairline)] mb-3" />
        <div className="h-4 w-1/3 rounded-md bg-[var(--color-hairline)]" />
      </CardBody>
    </Card>
  );
}

function subjectLabel(topic: string): string {
  const t = topic.toLowerCase();
  if (t.includes("math") || t.includes("algebra") || t.includes("calculus")) return "Math";
  if (t.includes("physics") || t.includes("chemistry") || t.includes("biology") || t.includes("science")) return "Science";
  if (t.includes("history") || t.includes("social") || t.includes("polity")) return "History";
  if (t.includes("react") || t.includes("python") || t.includes("code") || t.includes("cs")) return "CS";
  if (t.includes("english") || t.includes("literature") || t.includes("hindi")) return "Language";
  return "General";
}
