"use client";

import * as React from "react";
import { Pause, Play, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { STAGES, type StageId } from "./stages";

interface PipelineStepperProps {
  activeId: StageId;
  playing: boolean;
  progress: number;
  onSelect: (id: StageId) => void;
  onTogglePlay: () => void;
  onReplay: () => void;
}

export function PipelineStepper({
  activeId,
  playing,
  progress,
  onSelect,
  onTogglePlay,
  onReplay,
}: PipelineStepperProps) {
  return (
    <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-level-1 overflow-hidden">
      <div className="flex items-center justify-between gap-3 border-b border-[var(--color-hairline)] px-4 py-3">
        <div>
          <p className="text-eyebrow text-[var(--color-ink-muted)]">Pipeline</p>
          <p className="text-sm font-medium text-[var(--color-ink)]">
            Six stages · click any to inspect
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onTogglePlay}
            aria-label={playing ? "Pause tour" : "Play tour"}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--color-hairline-strong)] text-[var(--color-ink)] hover:bg-[var(--color-canvas-desk)] transition-colors cursor-pointer"
          >
            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <button
            type="button"
            onClick={onReplay}
            aria-label="Replay from start"
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--color-hairline-strong)] text-[var(--color-ink)] hover:bg-[var(--color-canvas-desk)] transition-colors cursor-pointer"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="px-3 py-4 overflow-x-auto">
        <div className="flex min-w-[640px] items-stretch gap-0">
          {STAGES.map((stage, i) => {
            const isActive = stage.id === activeId;
            const activeIndex = STAGES.findIndex((s) => s.id === activeId);
            const isDone = i < activeIndex;

            return (
              <React.Fragment key={stage.id}>
                <button
                  type="button"
                  onClick={() => onSelect(stage.id)}
                  className={cn(
                    "group relative flex flex-1 flex-col items-start gap-1 rounded-lg px-3 py-2.5 text-left transition-all cursor-pointer",
                    isActive
                      ? "bg-[var(--color-accent-sky-soft)] ring-1 ring-[var(--color-accent-sky)]/30"
                      : "hover:bg-[var(--color-canvas-desk)]"
                  )}
                >
                  <span
                    className={cn(
                      "font-mono text-[10px] uppercase tracking-widest",
                      isActive
                        ? "text-[var(--color-accent-sky)]"
                        : isDone
                          ? "text-[var(--color-accent-teal)]"
                          : "text-[var(--color-ink-faint)]"
                    )}
                  >
                    0{stage.number}
                  </span>
                  <span
                    className={cn(
                      "text-sm font-semibold leading-tight",
                      isActive ? "text-[var(--color-ink)]" : "text-[var(--color-ink-secondary)]"
                    )}
                  >
                    {stage.title}
                  </span>
                  <span className="text-[11px] text-[var(--color-ink-muted)] line-clamp-1">
                    {stage.subtitle}
                  </span>
                  {isActive && (
                    <span
                      className="absolute bottom-0 left-3 right-3 h-0.5 origin-left rounded-full bg-[var(--color-accent-sky)] transition-[transform] duration-100 ease-linear"
                      style={{ transform: `scaleX(${Math.max(0.04, progress)})` }}
                    />
                  )}
                </button>
                {i < STAGES.length - 1 && (
                  <div
                    className={cn(
                      "mt-6 h-px w-3 shrink-0 self-start",
                      i < activeIndex
                        ? "bg-[var(--color-accent-teal)]"
                        : "bg-[var(--color-hairline-strong)]"
                    )}
                    aria-hidden
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
}
