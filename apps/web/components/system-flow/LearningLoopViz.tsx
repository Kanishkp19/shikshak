"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

const LOOP_STEPS = [
  {
    id: "checkpoint",
    label: "Checkpoint",
    detail: "Video pauses · MCQ with diagnostic distractors",
  },
  {
    id: "diagnose",
    label: "Diagnose",
    detail: "Misconception detection from wrong answer",
  },
  {
    id: "reteach",
    label: "Reteach",
    detail: "Ladder: simplify → concrete → atomic steps",
  },
  {
    id: "mastery",
    label: "Mastery",
    detail: "Concept status updated on learner profile",
  },
  {
    id: "next",
    label: "Next lesson",
    detail: "Personalization prepends remediation first",
  },
] as const;

interface LearningLoopVizProps {
  active: boolean;
}

export function LearningLoopViz({ active }: LearningLoopVizProps) {
  const [step, setStep] = React.useState(0);
  const [session, setSession] = React.useState<1 | 2>(1);

  React.useEffect(() => {
    if (!active) return;
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setStep(LOOP_STEPS.length - 1);
      return;
    }
    setStep(0);
    const id = window.setInterval(() => {
      setStep((s) => {
        const next = (s + 1) % LOOP_STEPS.length;
        if (next === 0) setSession((prev) => (prev === 1 ? 2 : 1));
        return next;
      });
    }, 2200);
    return () => window.clearInterval(id);
  }, [active]);

  const weakS1 = ["physical vs chemical change"];
  const strongS1 = ["balancing equations"];
  const weakS2 = session === 1 ? weakS1 : [];
  const strongS2 =
    session === 1 ? strongS1 : [...strongS1, "physical vs chemical change"];

  return (
    <section className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-level-1 overflow-hidden">
      <div className="border-b border-[var(--color-hairline)] px-5 py-4">
        <p className="text-eyebrow text-[var(--color-accent-coral)] mb-1">Closed loop</p>
        <h2 className="text-heading-2 font-serif text-[var(--color-ink)]">
          How the AI improves over time
        </h2>
        <p className="text-body-sm text-[var(--color-ink-secondary)] mt-1 max-w-2xl">
          Wrong answers feed the reteach ladder; session end writes the profile; the next
          session opens with remediation.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-0">
        <div className="p-5 lg:p-6 border-b lg:border-b-0 lg:border-r border-[var(--color-hairline)]">
          <div className="relative flex flex-col gap-0">
            {LOOP_STEPS.map((item, i) => {
              const lit = i <= step;
              const current = i === step;
              return (
                <React.Fragment key={item.id}>
                  <div
                    className={cn(
                      "rounded-lg border px-4 py-3 transition-all duration-500",
                      current
                        ? "border-[var(--color-accent-coral)] bg-[var(--color-accent-coral-soft)]"
                        : lit
                          ? "border-[var(--color-accent-teal)]/30 bg-[var(--color-accent-teal-soft)]/30"
                          : "border-[var(--color-hairline)] opacity-50"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={cn(
                          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold font-mono",
                          current
                            ? "bg-[var(--color-accent-coral)] text-white"
                            : lit
                              ? "bg-[var(--color-accent-teal)] text-white"
                              : "bg-[var(--color-canvas-desk)] text-[var(--color-ink-faint)]"
                        )}
                      >
                        {i + 1}
                      </span>
                      <div>
                        <p className="text-sm font-semibold text-[var(--color-ink)]">{item.label}</p>
                        <p className="text-[11px] text-[var(--color-ink-muted)]">{item.detail}</p>
                      </div>
                    </div>
                  </div>
                  {i < LOOP_STEPS.length - 1 && (
                    <div className="flex justify-center py-1" aria-hidden>
                      <div
                        className={cn(
                          "w-px h-4",
                          i < step
                            ? "bg-[var(--color-accent-teal)]"
                            : "bg-[var(--color-hairline-strong)]"
                        )}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
            {/* Loop-back hint */}
            <p className="mt-3 text-[11px] font-mono text-[var(--color-ink-faint)] text-center">
              ↺ loops until mastery · then profile writeback
            </p>
          </div>
        </div>

        <div className="p-5 lg:p-6 bg-[var(--color-canvas-soft)]">
          <div className="flex items-center justify-between mb-4">
            <p className="text-eyebrow text-[var(--color-ink-muted)]">Learner profile</p>
            <div className="flex rounded-lg border border-[var(--color-hairline-strong)] overflow-hidden text-xs">
              <button
                type="button"
                onClick={() => setSession(1)}
                className={cn(
                  "px-3 py-1.5 cursor-pointer transition-colors",
                  session === 1
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-[var(--color-canvas)] text-[var(--color-ink-secondary)]"
                )}
              >
                Session 1
              </button>
              <button
                type="button"
                onClick={() => setSession(2)}
                className={cn(
                  "px-3 py-1.5 cursor-pointer transition-colors",
                  session === 2
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-[var(--color-canvas)] text-[var(--color-ink-secondary)]"
                )}
              >
                Session 2
              </button>
            </div>
          </div>

          <div
            key={session}
            className="sf-stage-enter space-y-4 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4"
          >
            <div>
              <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-accent-coral)] mb-2">
                Weak concepts
              </p>
              {weakS2.length === 0 ? (
                <p className="text-sm text-[var(--color-accent-teal)]">
                  Cleared — remediations succeeded
                </p>
              ) : (
                <ul className="space-y-1.5">
                  {weakS2.map((c) => (
                    <li
                      key={c}
                      className="rounded-md bg-[var(--color-accent-coral-soft)] px-3 py-1.5 text-sm text-[var(--color-ink)]"
                    >
                      {c}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-accent-teal)] mb-2">
                Strong concepts
              </p>
              <ul className="space-y-1.5">
                {strongS2.map((c) => (
                  <li
                    key={c}
                    className="rounded-md bg-[var(--color-accent-teal-soft)] px-3 py-1.5 text-sm text-[var(--color-ink)]"
                  >
                    {c}
                  </li>
                ))}
              </ul>
            </div>
            <p className="text-[11px] text-[var(--color-ink-muted)] leading-relaxed border-t border-[var(--color-hairline)] pt-3">
              {session === 1
                ? "After Session 1, weak concepts are written to learner_profiles."
                : "Session 2 opens with a Recap remediation segment before new material."}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
