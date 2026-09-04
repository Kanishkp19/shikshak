"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — SegmentTimeline signature component.
 *
 * Horizontal strip of dots; current segment dot filled primary,
 * completed dots filled ink-faint, upcoming dots hollow with hairline.
 * Checkpoint segments show a "?" glyph above their dot.
 */
export interface SegmentTimelineProps {
  total: number;
  current: number;
  completed: number;
  checkpoints: number[];
  onSelect?: (index: number) => void;
}

export function SegmentTimeline({
  total,
  current,
  completed,
  checkpoints,
  onSelect,
}: SegmentTimelineProps) {
  const isLarge = total > 12;
  const progressPercent = Math.min(100, Math.round(((current - 1) / Math.max(1, total - 1)) * 100));
  const nextCheckpoint = checkpoints.find((c) => c >= current);

  // If large, render windowed pagination around current step
  const windowedIndices = React.useMemo(() => {
    if (!isLarge) {
      return Array.from({ length: total }, (_, i) => i + 1);
    }
    // Show first, last, and window around current (± 2)
    const set = new Set<number>();
    set.add(1);
    set.add(total);
    for (let offset = -2; offset <= 2; offset++) {
      const val = current + offset;
      if (val >= 1 && val <= total) {
        set.add(val);
      }
    }
    return Array.from(set).sort((a, b) => a - b);
  }, [isLarge, total, current]);

  return (
    <div className="w-full space-y-3">
      {/* Top Meta Bar */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="font-mono font-medium text-[var(--color-ink)]">
            Progress: {progressPercent}%
          </span>
          {nextCheckpoint && (
            <span className="inline-flex items-center gap-1 rounded-md bg-[var(--color-accent-amber-soft)] px-2 py-0.5 text-[11px] font-medium text-[var(--color-accent-amber)] border border-[var(--color-accent-amber)]/30">
              <span>Quiz at Topic {nextCheckpoint}</span>
            </span>
          )}
        </div>

        {/* Step Navigation Controls */}
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onSelect?.(Math.max(0, current - 2))}
            disabled={current <= 1}
            className="rounded-md border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-2.5 py-1 text-xs font-medium text-[var(--color-ink-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] disabled:opacity-30 disabled:pointer-events-none transition-all"
            aria-label="Previous topic"
          >
            ← Prev
          </button>
          <span className="font-mono text-[11px] text-[var(--color-ink-muted)] px-1">
            {current} / {total}
          </span>
          <button
            type="button"
            onClick={() => onSelect?.(Math.min(total - 1, current))}
            disabled={current >= total}
            className="rounded-md border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-2.5 py-1 text-xs font-medium text-[var(--color-ink-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] disabled:opacity-30 disabled:pointer-events-none transition-all"
            aria-label="Next topic"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Progress Track Bar */}
      <div className="h-1.5 w-full rounded-full bg-[var(--color-hairline)] overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-accent-sky)] transition-all duration-300"
          style={{ width: `${Math.max(4, progressPercent)}%` }}
        />
      </div>

      {/* Interactive Step Nodes */}
      {!isLarge ? (
        // Clean compact milestone track for <= 12 steps
        <div className="flex items-center justify-between gap-1 pt-1 overflow-x-auto scrollbar-none">
          {Array.from({ length: total }, (_, i) => {
            const idx = i + 1;
            const isCurrent = idx === current;
            const isCompleted = idx <= completed;
            const isCheckpoint = checkpoints.includes(idx);

            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelect?.(i)}
                className={cn(
                  "group relative flex flex-col items-center gap-1 transition-all",
                  "focus:outline-none"
                )}
                title={`Topic ${idx}${isCheckpoint ? " (Includes Checkpoint)" : ""}`}
              >
                <span
                  className={cn(
                    "flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-semibold transition-all",
                    isCurrent
                      ? "bg-[var(--color-primary)] text-white shadow-sm ring-2 ring-[var(--color-primary)]/20 scale-110"
                      : isCompleted
                      ? "bg-[var(--color-canvas-desk)] text-[var(--color-primary)] border border-[var(--color-primary)]/30"
                      : "border border-[var(--color-hairline)] bg-[var(--color-canvas)] text-[var(--color-ink-muted)] hover:border-[var(--color-ink-secondary)]"
                  )}
                >
                  {isCompleted && !isCurrent ? "✓" : idx}
                </span>
                {isCheckpoint && (
                  <span className="text-[10px] text-[var(--color-accent-amber)] font-bold">
                    ?
                  </span>
                )}
              </button>
            );
          })}
        </div>
      ) : (
        // Windowed Pill Stepper for > 12 steps (e.g. 64 steps)
        <div className="flex items-center justify-center gap-1.5 pt-1 flex-wrap">
          {windowedIndices.map((idx, index) => {
            const prevIdx = index > 0 ? windowedIndices[index - 1] : null;
            const hasGap = prevIdx !== null && idx - prevIdx > 1;
            const isCurrent = idx === current;
            const isCompleted = idx <= completed;
            const isCheckpoint = checkpoints.includes(idx);

            return (
              <React.Fragment key={idx}>
                {hasGap && (
                  <span className="px-1 text-xs text-[var(--color-ink-muted)] font-mono select-none">
                    ···
                  </span>
                )}
                <button
                  type="button"
                  onClick={() => onSelect?.(idx - 1)}
                  className={cn(
                    "flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-medium transition-all",
                    isCurrent
                      ? "bg-[var(--color-primary)] text-white font-bold shadow-xs scale-105"
                      : isCompleted
                      ? "bg-[var(--color-canvas-soft)] text-[var(--color-ink)] border border-[var(--color-hairline)] hover:border-[var(--color-primary)]"
                      : "bg-[var(--color-canvas)] text-[var(--color-ink-muted)] border border-[var(--color-hairline)] hover:text-[var(--color-ink)] hover:border-[var(--color-hairline-strong)]"
                  )}
                  title={`Topic ${idx}${isCheckpoint ? " (Quiz)" : ""}`}
                >
                  <span>Part {idx}</span>
                  {isCheckpoint && (
                    <span className={cn(
                      "text-[10px] font-bold rounded px-1",
                      isCurrent ? "bg-white/20 text-white" : "text-[var(--color-accent-amber)]"
                    )}>
                      ?
                    </span>
                  )}
                </button>
              </React.Fragment>
            );
          })}
        </div>
      )}
    </div>
  );
}
