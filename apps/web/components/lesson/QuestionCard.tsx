"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { TextInput } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — QuestionCard (Socratic Classroom Flashcard).
 *
 * In-line comprehension checkpoint designed with student encouragement:
 * - Gentle feedback states that avoid anxiety-inducing red buzzer alerts
 * - Clear option tiles with tactile focus states
 * - Explanatory misconception guidance
 */
export interface QuestionCardProps {
  prompt: string;
  type: "mcq" | "short_answer" | "conceptual";
  options: string[] | null;
  submitting?: boolean;
  gradedCorrect: boolean | null;
  misconception?: string | null;
  onSubmit: (answer: string) => void;
}

export function QuestionCard({
  prompt,
  type,
  options,
  submitting,
  gradedCorrect,
  misconception,
  onSubmit,
}: QuestionCardProps) {
  const [answer, setAnswer] = React.useState("");

  const statusBorderColor =
    gradedCorrect === true
      ? "var(--color-accent-teal)"
      : gradedCorrect === false
        ? "var(--color-accent-coral)"
        : "var(--color-hairline)";

  return (
    <div
      className={cn(
        "rounded-xl border bg-[var(--color-canvas)] transition-all duration-200 shadow-[var(--shadow-level-1)] overflow-hidden",
        gradedCorrect === true && "border-[var(--color-accent-teal)] ring-1 ring-[var(--color-accent-teal)]/30",
        gradedCorrect === false && "border-[var(--color-accent-coral)] ring-1 ring-[var(--color-accent-coral)]/20"
      )}
      style={{ borderTop: `4px solid ${statusBorderColor}` }}
    >
      <div className="p-4 sm:p-5">
        {/* Socratic Checkpoint Eyebrow */}
        <div className="flex items-center justify-between mb-2">
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-accent-amber)]">
            <span>💡</span>
            <span>Quick Concept Check-in</span>
          </span>
          <span className="text-[11px] text-[var(--color-ink-faint)]">Self-check · No grading pressure</span>
        </div>

        <p className="text-sm sm:text-base text-[var(--color-ink)] font-semibold leading-snug mb-3">
          {prompt}
        </p>

        {/* Options / Text Input */}
        <div className="mt-4">
          {type === "mcq" && options ? (
            <div className="flex flex-col gap-2.5">
              {options.map((opt, i) => {
                const selected = answer === opt;
                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setAnswer(opt)}
                    className={cn(
                      "rounded-lg border px-4 py-3 text-body-sm text-left transition-all flex items-center justify-between group",
                      selected
                        ? "border-[var(--color-primary)] bg-[var(--color-accent-sky-soft)]/40 text-[var(--color-ink)] font-medium shadow-xs"
                        : "border-[var(--color-hairline)] bg-[var(--color-canvas-soft)] text-[var(--color-ink-secondary)] hover:border-[var(--color-primary)] hover:bg-[var(--color-canvas)]"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-[var(--color-hairline-strong)] text-xs font-semibold text-[var(--color-ink-muted)] group-hover:border-[var(--color-primary)] group-hover:text-[var(--color-primary)]">
                        {String.fromCharCode(65 + i)}
                      </span>
                      <span>{opt}</span>
                    </div>
                    {selected && (
                      <span className="text-xs font-bold text-[var(--color-primary)]">✓</span>
                    )}
                  </button>
                );
              })}
            </div>
          ) : (
            <TextInput
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your explanation or answer in your own words…"
              disabled={submitting}
            />
          )}
        </div>

        {/* Socratic Encouragement / Misconception Feedback */}
        {gradedCorrect === true && (
          <div className="mt-5 rounded-lg border border-[var(--color-accent-teal)]/30 bg-[var(--color-accent-teal-soft)]/50 p-3.5 text-body-sm text-[var(--color-ink)] flex items-start gap-2.5">
            <span className="text-lg">🎉</span>
            <div>
              <strong className="text-[var(--color-accent-teal)] block font-semibold">Spot on!</strong>
              <span>You understood the core concept. Ready for the next chapter!</span>
            </div>
          </div>
        )}

        {gradedCorrect === false && misconception && (
          <div className="mt-5 rounded-lg border border-[var(--color-accent-coral)]/30 bg-[var(--color-accent-coral-soft)]/40 p-3.5 text-body-sm text-[var(--color-ink)] flex items-start gap-2.5">
            <span className="text-lg">💡</span>
            <div>
              <strong className="text-[var(--color-accent-coral)] block font-semibold">
                Close! Let&apos;s look at this differently:
              </strong>
              <p className="mt-0.5 text-[var(--color-ink-secondary)] leading-relaxed">{misconception}</p>
              <p className="mt-2 text-xs text-[var(--color-primary)] font-medium">
                Your teacher will explain this with a fresh analogy in a moment.
              </p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-4 flex items-center justify-between pt-2 border-t border-[var(--color-hairline)]">
          <p className="text-caption text-[var(--color-ink-faint)]">
            Take your time — learning happens when we explore mistakes.
          </p>
          <Button
            variant={gradedCorrect !== null ? "secondary" : "study-amber"}
            onClick={() => onSubmit(answer)}
            loading={submitting}
            disabled={!answer || gradedCorrect !== null}
            className="px-6 py-2.5 text-sm"
          >
            {gradedCorrect !== null ? "Answer Recorded" : "Submit Answer"}
          </Button>
        </div>
      </div>
    </div>
  );
}
