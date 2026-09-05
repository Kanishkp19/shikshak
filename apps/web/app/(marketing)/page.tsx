"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ClassroomBackground } from "@/components/ui/classroom-background";

export default function MarketingPage() {
  const router = useRouter();
  const [topicInput, setTopicInput] = React.useState("");
  const [selectedAnswer, setSelectedAnswer] = React.useState<number | null>(null);

  function handleStartLesson(e: React.FormEvent) {
    e.preventDefault();
    const query = topicInput.trim() || "Calculus Chain Rule Intuition";
    router.push(`/session/new?topic=${encodeURIComponent(query)}`);
  }

  return (
    <ClassroomBackground variant="parchment" className="flex flex-col justify-between">
      {/* Editorial Navigation */}
      <header className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas)]/80 backdrop-blur-md sticky top-0 z-30">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--color-primary)] text-white text-xs font-serif font-bold tracking-wider">
              ∑
            </div>
            <div>
              <span className="text-base font-semibold tracking-tight text-[var(--color-ink)] block leading-none">
                Shikshak AI
              </span>
              <span className="text-[10px] uppercase tracking-widest text-[var(--color-ink-faint)] font-mono">
                Socratic Tutoring Engine
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              href="/how-it-works"
              className="text-xs font-medium text-[var(--color-ink-secondary)] hover:text-[var(--color-ink)] transition-colors px-2 py-1"
            >
              How it works
            </Link>
            <Link
              href="/dashboard"
              className="text-xs font-medium text-[var(--color-ink-secondary)] hover:text-[var(--color-ink)] transition-colors px-2 py-1 hidden sm:inline"
            >
              Student Desk
            </Link>
            <Link
              href="/session/new"
              className="rounded-lg bg-[var(--color-primary)] text-white text-xs font-medium px-4 py-2 hover:bg-[var(--color-primary-hover)] transition-colors shadow-xs"
            >
              Start a Lesson
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section: Two-Column Editorial & Interactive Slate */}
      <main className="flex-1">
        <section className="mx-auto max-w-6xl px-6 pt-12 pb-20 lg:pt-16 lg:pb-24">
          <div className="grid gap-12 lg:grid-cols-[1.1fr_1fr] items-center">
            {/* Left: Scholarly Narrative & Functional Command Input */}
            <div>
              <div className="inline-flex items-center gap-2 rounded-md border border-[var(--color-hairline-strong)] bg-[var(--color-canvas)] px-3 py-1 text-[11.5px] font-mono uppercase tracking-wider text-[var(--color-ink-secondary)] mb-6">
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-accent-teal)]" />
                Document-Grounded Socratic Learning
              </div>

              <h1 className="text-display-1 font-serif text-[var(--color-ink)] mb-6 tracking-tight">
                Any textbook.
                <br />
                Any tough chapter.
                <br />
                <span className="italic font-normal text-[var(--color-primary-accent)]">
                  Your patient teacher.
                </span>
              </h1>

              <p className="text-body-md text-[var(--color-ink-secondary)] mb-8 leading-relaxed max-w-xl">
                Upload your syllabus, PDF notes, or enter any complex concept.
                Shikshak AI synthesizes an interactive video lesson with step-by-step
                chalkboard derivations, pauses to check your intuition, and re-explains
                misconceptions with fresh analogies.
              </p>

              {/* Direct Topic Inquiry Input */}
              <form onSubmit={handleStartLesson} className="mb-6 max-w-xl">
                <div className="flex items-center rounded-xl border border-[var(--color-hairline-strong)] bg-[var(--color-canvas)] p-1.5 shadow-sm focus-within:border-[var(--color-primary-accent)] focus-within:ring-2 focus-within:ring-[var(--color-primary-accent)]/10 transition-all">
                  <input
                    type="text"
                    value={topicInput}
                    onChange={(e) => setTopicInput(e.target.value)}
                    placeholder="Enter any concept (e.g. 'Calculus Chain Rule', 'Entropy')..."
                    className="flex-1 bg-transparent px-3.5 py-2 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-faint)] focus:outline-none"
                  />
                  <button
                    type="submit"
                    className="rounded-lg bg-[var(--color-primary)] px-4 py-2 text-xs font-semibold text-white hover:bg-[var(--color-primary-hover)] transition-all cursor-pointer whitespace-nowrap"
                  >
                    Teach Me →
                  </button>
                </div>
              </form>

              {/* Curated Syllabus Topics */}
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-[var(--color-ink-muted)]">
                <span className="font-mono uppercase text-[10.5px] text-[var(--color-ink-faint)]">
                  Curated sparks:
                </span>
                {[
                  { label: "Chain Rule", q: "Calculus Chain Rule Intuition" },
                  { label: "Newton's 3 Laws", q: "Newton's 3 Laws of Motion with Intuition" },
                  { label: "Electrophilic Substitution", q: "Electrophilic Aromatic Substitution" },
                  { label: "Light Reactions", q: "Photosynthesis Light Dependent Reactions" },
                ].map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    onClick={() => setTopicInput(item.q)}
                    className="underline decoration-[var(--color-hairline-strong)] hover:text-[var(--color-primary-accent)] hover:decoration-[var(--color-primary-accent)] transition-colors cursor-pointer"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Right: The Interactive Study Slate (Live Interactive Demo) */}
            <div className="relative">
              {/* Outer Slate Frame */}
              <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-xl">
                {/* Chalkboard Screen */}
                <div className="rounded-xl border border-white/10 bg-[var(--color-chalk-board)] p-5 text-white shadow-inner relative overflow-hidden">
                  {/* Subtle chalkboard margin code */}
                  <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-chalk-muted)] mb-4 border-b border-white/10 pb-2.5">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                      CALCULUS · LECTURE 03
                    </span>
                    <span>1080p Lip-Synced Teacher</span>
                  </div>

                  {/* Chalkboard Equation Visual */}
                  <div className="py-5 text-center">
                    <p className="text-xs font-mono uppercase tracking-wider text-[var(--color-accent-amber)] mb-2">
                      The Limit Definition of the Derivative
                    </p>
                    <div className="rounded-lg bg-black/30 border border-white/5 py-4 px-6 inline-block font-serif text-xl sm:text-2xl text-slate-100 tracking-wide">
                      f&apos;(x) = lim<sub>h → 0</sub>{" "}
                      <span className="inline-block text-sky-300 font-mono text-base sm:text-lg align-middle">
                        [ f(x + h) − f(x) ]
                      </span>{" "}
                      / h
                    </div>
                  </div>

                  {/* Teacher Spoken Line */}
                  <div className="rounded-lg bg-white/5 border border-white/10 p-3 text-xs text-slate-200 mb-3 flex items-start gap-2.5">
                    <div className="h-6 w-6 shrink-0 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-[10px]">
                      AI
                    </div>
                    <p className="leading-relaxed">
                      &ldquo;Notice how the secant line between the two sample points pivots until
                      it matches the instantaneous slope as <span className="font-mono text-amber-300">h</span> shrinks to zero.&rdquo;
                    </p>
                  </div>
                </div>

                {/* Interactive Socratic Check Card */}
                <div className="mt-4 rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-soft)] p-4">
                  <div className="flex items-center justify-between text-xs mb-2">
                    <span className="font-semibold text-[var(--color-ink)]">
                      Socratic Checkpoint:
                    </span>
                    <span className="text-[11px] text-[var(--color-ink-faint)]">Interactive Check</span>
                  </div>
                  <p className="text-xs text-[var(--color-ink-secondary)] mb-3">
                    In this definition, what does <span className="font-mono font-semibold">h</span> physically represent?
                  </p>

                  <div className="grid gap-2 text-xs">
                    <button
                      type="button"
                      onClick={() => setSelectedAnswer(1)}
                      className={`rounded-lg border px-3 py-2 text-left transition-all ${
                        selectedAnswer === 1
                          ? "border-[var(--color-accent-teal)] bg-[var(--color-accent-teal-soft)]/50 text-[var(--color-ink)] font-medium"
                          : "border-[var(--color-hairline)] bg-[var(--color-canvas)] text-[var(--color-ink-secondary)] hover:border-[var(--color-hairline-strong)]"
                      }`}
                    >
                      A. The horizontal separation between the two curve points.
                    </button>
                    <button
                      type="button"
                      onClick={() => setSelectedAnswer(2)}
                      className={`rounded-lg border px-3 py-2 text-left transition-all ${
                        selectedAnswer === 2
                          ? "border-[var(--color-accent-coral)] bg-[var(--color-accent-coral-soft)]/50 text-[var(--color-ink)]"
                          : "border-[var(--color-hairline)] bg-[var(--color-canvas)] text-[var(--color-ink-secondary)] hover:border-[var(--color-hairline-strong)]"
                      }`}
                    >
                      B. The slope of the tangent line.
                    </button>
                  </div>

                  {selectedAnswer === 1 && (
                    <div className="mt-2.5 rounded-md border border-[var(--color-accent-teal)]/30 bg-[var(--color-accent-teal-soft)]/40 p-2 text-[11.5px] text-[var(--color-ink)]">
                      <strong className="text-[var(--color-accent-teal)]">Correct intuition:</strong> As that horizontal gap shrinks to 0, the secant line becomes the tangent slope!
                    </div>
                  )}
                  {selectedAnswer === 2 && (
                    <div className="mt-2.5 rounded-md border border-[var(--color-accent-coral)]/30 bg-[var(--color-accent-coral-soft)]/40 p-2 text-[11.5px] text-[var(--color-ink)]">
                      <strong className="text-[var(--color-accent-coral)]">Misconception caught:</strong> That&apos;s <span className="font-mono">f&apos;(x)</span>! <span className="font-mono">h</span> is the tiny step width. The teacher immediately re-teaches this step.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* The 3 Scholarly Pillars */}
        <section className="border-t border-[var(--color-hairline)] bg-[var(--color-canvas)] py-16 px-6">
          <div className="mx-auto max-w-6xl">
            <div className="max-w-xl mb-12">
              <span className="text-[11px] font-mono uppercase tracking-widest text-[var(--color-ink-faint)]">
                Architectural Invariants
              </span>
              <h2 className="text-heading-1 font-serif text-[var(--color-ink)] mt-1">
                How Shikshak AI teaches differently
              </h2>
              <p className="text-body-sm text-[var(--color-ink-secondary)] mt-3">
                Prefer a full agent walkthrough?{" "}
                <Link
                  href="/how-it-works"
                  className="font-medium text-[var(--color-primary-accent)] hover:underline"
                >
                  Open the interactive system flow →
                </Link>
              </p>
            </div>

            <div className="grid gap-8 md:grid-cols-3">
              <div className="rounded-xl border border-[var(--color-hairline)] p-6 bg-[var(--color-canvas-soft)]">
                <div className="font-mono text-xs text-[var(--color-primary-accent)] mb-3">01 / FIDELITY</div>
                <h3 className="text-heading-3 text-[var(--color-ink)] mb-2">
                  Document-Grounded Only
                </h3>
                <p className="text-body-sm text-[var(--color-ink-secondary)] leading-relaxed">
                  The lesson plan only teaches concepts present in your material. Every claim,
                  equation, and definition references the exact source page and chapter.
                </p>
              </div>

              <div className="rounded-xl border border-[var(--color-hairline)] p-6 bg-[var(--color-canvas-soft)]">
                <div className="font-mono text-xs text-[var(--color-accent-amber)] mb-3">02 / HUMAN CADENCE</div>
                <h3 className="text-heading-3 text-[var(--color-ink)] mb-2">
                  Chalkboard Derivations
                </h3>
                <p className="text-body-sm text-[var(--color-ink-secondary)] leading-relaxed">
                  Instead of flashing walls of bullet points, equations unfold step-by-step
                  on the virtual board in sync with the spoken explanation.
                </p>
              </div>

              <div className="rounded-xl border border-[var(--color-hairline)] p-6 bg-[var(--color-canvas-soft)]">
                <div className="font-mono text-xs text-[var(--color-accent-teal)] mb-3">03 / EMPATHY</div>
                <h3 className="text-heading-3 text-[var(--color-ink)] mb-2">
                  Misconception Healing
                </h3>
                <p className="text-body-sm text-[var(--color-ink-secondary)] leading-relaxed">
                  When you answer a checkpoint question incorrectly, the system diagnoses the root
                  misunderstanding and immediately presents an intuitive real-world analogy.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Editorial Footer */}
      <footer className="border-t border-[var(--color-hairline)] bg-[var(--color-canvas-soft)] py-8 px-6 text-center text-xs text-[var(--color-ink-muted)]">
        <p className="font-serif italic text-sm mb-1 text-[var(--color-ink-secondary)]">
          &ldquo;Study without stress. Understand with precision.&rdquo;
        </p>
        <p className="font-mono text-[11px] text-[var(--color-ink-faint)]">
          Shikshak AI · Bharat Academix Engineering
        </p>
      </footer>
    </ClassroomBackground>
  );
}
