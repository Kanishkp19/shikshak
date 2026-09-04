"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/input";
import { DocumentUploader } from "@/components/upload/DocumentUploader";
import { TopicForm } from "@/components/upload/TopicForm";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { CreateSessionRequest } from "@/lib/types";

const STUDENT_ID =
  process.env.NEXT_PUBLIC_STUDENT_ID ?? "00000000-0000-0000-0000-000000000001";

type Tab = "upload" | "topic";

function NewSessionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTopic = searchParams?.get("topic") ?? "";

  const { push } = useToast();
  const [tab, setTab] = React.useState<Tab>(initialTopic ? "topic" : "upload");
  const [documentId, setDocumentId] = React.useState<string | null>(null);
  const [topic, setTopic] = React.useState(initialTopic);
  const [level, setLevel] = React.useState<CreateSessionRequest["level"]>("beginner");
  const [language, setLanguage] = React.useState("en");
  const [timeBudget, setTimeBudget] = React.useState(20);
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (initialTopic) {
      setTopic(initialTopic);
      setTab("topic");
    }
  }, [initialTopic]);

  function switchTab(t: Tab) {
    setTab(t);
    if (t === "upload") setTopic("");
    if (t === "topic") setDocumentId(null);
  }

  async function handleSubmit() {
    if (tab === "upload" && !documentId) {
      push("error", "Please upload study notes or a textbook chapter first.");
      return;
    }
    if (tab === "topic" && topic.trim().length < 3) {
      push("error", "Enter the concept or topic you want to learn (min 3 characters).");
      return;
    }
    setSubmitting(true);
    try {
      const body: CreateSessionRequest = {
        sourceType: tab === "upload" ? "document" : "topic",
        documentId: documentId ?? undefined,
        topic: tab === "topic" ? topic : undefined,
        level,
        language,
        timeBudgetMinutes: timeBudget,
      };
      const { sessionId } = await api.createSession(body, STUDENT_ID);
      push("success", "Your lesson is being prepared! Opening the classroom…");
      router.push(`/session/${sessionId}`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Couldn't start your lesson — please try again.";
      push("error", msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-[700px] px-6 py-10">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 rounded-md border border-[var(--color-hairline-strong)] bg-[var(--color-canvas)] px-3 py-1 text-[11px] font-mono uppercase tracking-wider text-[var(--color-ink-secondary)] mb-3">
          Socratic Lesson Builder
        </div>
        <h1 className="text-heading-1 font-serif text-[var(--color-ink)] mb-2 font-bold">
          What are we studying today?
        </h1>
        <p className="text-body-sm text-[var(--color-ink-muted)]">
          Ground your lesson in textbook notes, or enter any concept you want explained from scratch.
        </p>
      </div>

      <Card variant="elevated" className="bg-[var(--color-canvas)]">
        <CardBody className="p-6 sm:p-8">
          {/* Pathway Tabs */}
          <div className="mb-6 grid grid-cols-2 gap-2 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas-desk)] p-1">
            <button
              type="button"
              onClick={() => switchTab("upload")}
              className={`flex items-center justify-center gap-2 rounded-md py-2 text-xs font-medium transition-all ${
                tab === "upload"
                  ? "bg-[var(--color-canvas)] text-[var(--color-ink)] font-semibold shadow-xs"
                  : "text-[var(--color-ink-secondary)] hover:text-[var(--color-ink)]"
              }`}
            >
              Upload Material (PDF / Notes)
            </button>
            <button
              type="button"
              onClick={() => switchTab("topic")}
              className={`flex items-center justify-center gap-2 rounded-md py-2 text-xs font-medium transition-all ${
                tab === "topic"
                  ? "bg-[var(--color-canvas)] text-[var(--color-ink)] font-semibold shadow-xs"
                  : "text-[var(--color-ink-secondary)] hover:text-[var(--color-ink)]"
              }`}
            >
              Enter a Concept / Topic
            </button>
          </div>

          {/* Source Input Area */}
          <div className="mb-8">
            {tab === "upload" ? (
              <div className="rounded-xl border border-dashed border-[var(--color-hairline-strong)] bg-[var(--color-canvas-soft)] p-4">
                <DocumentUploader
                  studentId={STUDENT_ID}
                  onUploaded={setDocumentId}
                />
              </div>
            ) : (
              <TopicForm value={topic} onChange={setTopic} />
            )}
          </div>

          {/* Level Customization */}
          <div className="mb-6">
            <label className="text-eyebrow text-[var(--color-ink-muted)] mb-2 block font-mono">
              Learning Depth
            </label>
            <div className="grid gap-2 sm:grid-cols-3">
              {[
                { id: "beginner", label: "Foundational", desc: "Intuitive analogies & fundamental mechanics" },
                { id: "intermediate", label: "Standard / College", desc: "Formulas, proofs & step-by-step logic" },
                { id: "advanced", label: "Exam Mastery", desc: "Rigorous speed shortcuts & complex problem types" },
              ].map((lvl) => (
                <button
                  type="button"
                  key={lvl.id}
                  onClick={() => setLevel(lvl.id as any)}
                  className={`rounded-lg border p-3 text-left transition-all ${
                    level === lvl.id
                      ? "border-[var(--color-primary-accent)] bg-[var(--color-canvas-desk)] text-[var(--color-ink)] shadow-xs"
                      : "border-[var(--color-hairline)] bg-[var(--color-canvas)] text-[var(--color-ink-secondary)] hover:border-[var(--color-hairline-strong)]"
                  }`}
                >
                  <p className="text-xs font-semibold text-[var(--color-ink)] mb-0.5">{lvl.label}</p>
                  <p className="text-[11px] text-[var(--color-ink-muted)] leading-tight">{lvl.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Language & Time Settings */}
          <div className="grid gap-4 sm:grid-cols-2 mb-8 pt-4 border-t border-[var(--color-hairline)]">
            <div>
              <label className="text-eyebrow text-[var(--color-ink-muted)] mb-1.5 block">
                Teaching Language
              </label>
              <Select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="hi-Latn">Hinglish (Hindi + English)</option>
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="te">తెలుగు (Telugu)</option>
              </Select>
            </div>

            <div>
              <label className="text-eyebrow text-[var(--color-ink-muted)] mb-1.5 block">
                Time Budget (Ruler)
              </label>
              <Select
                value={String(timeBudget)}
                onChange={(e) => setTimeBudget(Number(e.target.value))}
              >
                <option value="5">⏱️ 5 min — Coffee break summary</option>
                <option value="20">⏱️ 20 min — Standard focused lesson</option>
                <option value="45">⏱️ 45 min — Complete chapter deep dive</option>
                <option value="10080">📅 7 days — Structured syllabus sprint</option>
              </Select>
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-between pt-2">
            <p className="text-caption text-[var(--color-ink-faint)]">
              Takes ~15 seconds to synthesize your personalized plan.
            </p>
            <Button
              variant="study-amber"
              onClick={handleSubmit}
              loading={submitting}
              className="px-7 py-3 text-sm shadow-md"
            >
              Generate My Lesson →
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

export default function NewSessionPage() {
  return (
    <React.Suspense fallback={<div className="p-12 text-center text-body-sm text-[var(--color-ink-muted)]">Loading study bench…</div>}>
      <NewSessionContent />
    </React.Suspense>
  );
}
