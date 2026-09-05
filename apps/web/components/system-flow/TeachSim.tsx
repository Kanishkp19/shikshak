"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

const CHOICES = [
  { id: 0, text: "A precipitate formed from a chemical reaction", correct: true },
  { id: 1, text: "The temperature of the solution increased", correct: false },
  { id: 2, text: "The solvent simply evaporated", correct: false },
  { id: 3, text: "Light scattering made it look cloudy", correct: false },
] as const;

const RETEACH: Record<number, { strategy: string; explanation: string }> = {
  1: {
    strategy: "simplify",
    explanation:
      "Temperature can change without making new substances. Cloudy precipitate means new particles formed — a chemical change, not just heating.",
  },
  2: {
    strategy: "concrete_example",
    explanation:
      "Think of boiling water (physical — steam is still H₂O) vs burning paper (chemical — ash is a new substance). Cloudiness here is like forming salt crystals you can filter out.",
  },
  3: {
    strategy: "atomic_steps",
    explanation:
      "1) Start with dissolved ions. 2) They collide and bond. 3) Insoluble solid appears. 4) Light scatters off that solid — that is the cloudiness.",
  },
};

interface TeachSimProps {
  visible: boolean;
}

export function TeachSim({ visible }: TeachSimProps) {
  const [selected, setSelected] = React.useState<number | null>(null);
  const [attempt, setAttempt] = React.useState(0);
  const [phase, setPhase] = React.useState<"ask" | "reteach" | "done">("ask");

  React.useEffect(() => {
    if (!visible) {
      setSelected(null);
      setAttempt(0);
      setPhase("ask");
    }
  }, [visible]);

  function handlePick(id: number) {
    if (phase === "done") return;
    setSelected(id);
    const choice = CHOICES.find((c) => c.id === id);
    if (choice?.correct) {
      setPhase("done");
      return;
    }
    setAttempt((a) => a + 1);
    setPhase("reteach");
  }

  function handleRetry() {
    setSelected(null);
    setPhase("ask");
  }

  if (!visible) return null;

  const reteach =
    selected !== null && !CHOICES[selected]?.correct
      ? RETEACH[Math.min(attempt, 3)] ?? RETEACH[3]
      : null;

  return (
    <section className="sf-stage-enter rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-level-1 overflow-hidden">
      <div className="border-b border-[var(--color-hairline)] px-5 py-4">
        <p className="text-eyebrow text-[var(--color-accent-amber)] mb-1">Live simulation</p>
        <h2 className="text-heading-2 font-serif text-[var(--color-ink)]">
          Try a Socratic checkpoint
        </h2>
        <p className="text-body-sm text-[var(--color-ink-secondary)] mt-1">
          Pick a wrong answer to watch misconception detection escalate the reteach ladder.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-0">
        <div className="p-5 lg:p-6 border-b lg:border-b-0 lg:border-r border-[var(--color-hairline)]">
          <p className="text-sm font-semibold text-[var(--color-ink)] mb-4">
            Why did the solution turn cloudy?
          </p>
          <div className="space-y-2">
            {CHOICES.map((c) => {
              const isSel = selected === c.id;
              const showResult = phase === "done" || (phase === "reteach" && isSel);
              return (
                <button
                  key={c.id}
                  type="button"
                  disabled={phase === "done"}
                  onClick={() => handlePick(c.id)}
                  className={cn(
                    "w-full text-left rounded-lg border px-4 py-3 text-sm transition-all cursor-pointer",
                    isSel && c.correct && showResult
                      ? "border-[var(--color-accent-teal)] bg-[var(--color-accent-teal-soft)]"
                      : isSel && !c.correct && showResult
                        ? "border-[var(--color-accent-coral)] bg-[var(--color-accent-coral-soft)]"
                        : "border-[var(--color-hairline-strong)] hover:border-[var(--color-primary-accent)] bg-[var(--color-canvas)]",
                    phase === "done" && "cursor-default"
                  )}
                >
                  {c.text}
                </button>
              );
            })}
          </div>
          {phase === "done" && (
            <p className="mt-4 text-sm text-[var(--color-accent-teal)] font-medium">
              Correct — continuing to the next segment.
            </p>
          )}
          {phase === "reteach" && (
            <button
              type="button"
              onClick={handleRetry}
              className="mt-4 text-sm font-medium text-[var(--color-primary-accent)] hover:underline cursor-pointer"
            >
              Try again →
            </button>
          )}
        </div>

        <div className="p-5 lg:p-6 bg-[var(--color-chalk-board)] text-[var(--color-chalk-text)] min-h-[240px]">
          <p className="text-eyebrow text-[var(--color-chalk-muted)] mb-3">AI thinking</p>
          {phase === "ask" && (
            <p className="text-sm text-[var(--color-chalk-muted)]">
              Waiting for student answer… Interaction agent armed diagnostic distractors for
              common chemistry misconceptions.
            </p>
          )}
          {phase === "reteach" && reteach && (
            <div className="sf-stage-enter space-y-3">
              <p className="font-mono text-[11px] text-[var(--color-accent-amber)]">
                [misconception_detection] attempt #{attempt} → strategy=
                <span className="text-[var(--color-accent-teal)]">{reteach.strategy}</span>
              </p>
              <div className="rounded-lg border border-[var(--color-hairline-chalk)] bg-[var(--color-chalk-surface)] p-4">
                <p className="text-xs font-mono uppercase tracking-wider text-[var(--color-chalk-muted)] mb-2">
                  ReteachContent
                </p>
                <p className="text-sm leading-relaxed text-[var(--color-chalk-text)]">
                  {reteach.explanation}
                </p>
              </div>
              <p className="text-[11px] text-[var(--color-chalk-muted)]">
                Ladder: simplify (1) → concrete_example (2) → atomic_steps (3+)
              </p>
            </div>
          )}
          {phase === "done" && (
            <div className="sf-stage-enter space-y-2">
              <p className="font-mono text-[11px] text-[var(--color-accent-teal)]">
                [answer_evaluation] CORRECT
              </p>
              <p className="text-sm text-[var(--color-chalk-muted)]">
                Checkpoint cleared. Orchestrator advances to the next segment; concept tagged
                toward strong on profile writeback.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
