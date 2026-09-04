"use client";

import * as React from "react";
import type { LessonSegment, Level } from "@/lib/types";
import { cn } from "@/lib/utils";

export interface ChapterContentsProps {
  segments: LessonSegment[];
  activeOrder: number;
  renderStatus: Record<string, "pending" | "rendering" | "ready" | "failed">;
  onSelectSegment: (order: number) => void;
  className?: string;
}

const DEPTH_BADGES: Record<Level, { label: string; className: string }> = {
  beginner: {
    label: "Foundational",
    className: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  },
  intermediate: {
    label: "Core",
    className: "bg-sky-500/10 text-sky-400 border-sky-500/20",
  },
  advanced: {
    label: "Deep Dive",
    className: "bg-violet-500/10 text-violet-400 border-violet-500/20",
  },
};

export function ChapterContents({
  segments,
  activeOrder,
  renderStatus,
  onSelectSegment,
  className,
}: ChapterContentsProps) {
  const completedCount = segments.filter((s) => s.order < activeOrder).length;
  const progressPercent = Math.round(
    (completedCount / Math.max(1, segments.length)) * 100
  );

  return (
    <div
      className={cn(
        "rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-xs",
        className
      )}
    >
      {/* Header */}
      <div className="mb-3 flex items-center justify-between border-b border-[var(--color-hairline)] pb-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-[var(--color-canvas-desk)] text-xs text-[var(--color-primary)] border border-[var(--color-hairline)]">
              📚
            </span>
            <h3 className="font-semibold text-[var(--color-ink)] text-xs tracking-wide uppercase truncate">
              Chapter Syllabus
            </h3>
          </div>
          <p className="mt-0.5 text-[11px] text-[var(--color-ink-muted)]">
            {segments.length} topics · {progressPercent}% completed
          </p>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-[var(--color-primary)] font-semibold bg-[var(--color-accent-sky-soft)] px-2.5 py-0.5 rounded-full border border-[var(--color-primary)]/20 shrink-0">
          <span>Part {activeOrder}</span>
          <span className="text-[var(--color-ink-muted)]">/</span>
          <span>{segments.length}</span>
        </div>
      </div>

      {/* Interactive Topics Table / List */}
      <div className="max-h-[300px] space-y-1.5 overflow-y-auto pr-1 scrollbar-thin">
        {segments.map((seg) => {
          const isActive = seg.order === activeOrder;
          const isPassed = seg.order < activeOrder;
          const status = renderStatus[seg.id] || (seg.videoUrl ? "ready" : "pending");
          const isOverview = seg.order === 1 || seg.concept.toLowerCase().includes("overview");
          const depthBadge = DEPTH_BADGES[seg.depth] || DEPTH_BADGES.intermediate;

          return (
            <button
              key={seg.id || seg.order}
              onClick={() => onSelectSegment(seg.order)}
              className={cn(
                "group w-full text-left rounded-lg p-2.5 transition-all duration-150 flex items-start gap-2.5 border",
                isActive
                  ? "bg-[var(--color-canvas-desk)] border-[var(--color-primary)] shadow-xs"
                  : isPassed
                  ? "bg-[var(--color-canvas-soft)]/50 border-[var(--color-hairline)] hover:bg-[var(--color-canvas-soft)] hover:border-[var(--color-hairline-strong)]"
                  : "bg-transparent border-transparent hover:bg-[var(--color-canvas-soft)] hover:border-[var(--color-hairline)]"
              )}
            >
              {/* Order / Status Badge */}
              <div className="flex-shrink-0 mt-0.5">
                <div
                  className={cn(
                    "flex h-6 w-6 items-center justify-center rounded-md text-[11px] font-semibold transition-colors",
                    isActive
                      ? "bg-[var(--color-primary)] text-white shadow-xs"
                      : isPassed
                      ? "bg-[var(--color-accent-teal-soft)] text-[var(--color-accent-teal)] border border-[var(--color-accent-teal)]/30"
                      : "bg-[var(--color-canvas-soft)] text-[var(--color-ink-muted)] border border-[var(--color-hairline)] group-hover:text-[var(--color-ink)]"
                  )}
                >
                  {isPassed ? "✓" : seg.order}
                </div>
              </div>

              {/* Topic Information */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  {isOverview && (
                    <span className="px-1 py-0.2 rounded text-[9px] font-bold bg-[var(--color-accent-amber-soft)] text-[var(--color-accent-amber)] border border-[var(--color-accent-amber)]/30">
                      OVERVIEW
                    </span>
                  )}
                  <span
                    className={cn(
                      "text-xs font-medium truncate block max-w-full transition-colors",
                      isActive
                        ? "text-[var(--color-primary)] font-semibold"
                        : "text-[var(--color-ink)] group-hover:text-[var(--color-primary)]"
                    )}
                    title={seg.concept}
                  >
                    {seg.concept}
                  </span>
                </div>

                {/* Subtitle / Metadata badges */}
                <div className="mt-1 flex items-center gap-1.5 text-[10.5px] text-[var(--color-ink-muted)]">
                  <span
                    className={cn(
                      "px-1.5 py-0.2 rounded border text-[9.5px] font-medium",
                      depthBadge.className
                    )}
                  >
                    {depthBadge.label}
                  </span>

                  {seg.hasCheckpoint && (
                    <span className="flex items-center gap-0.5 text-[var(--color-accent-amber)] text-[10px] font-medium">
                      <span>?</span> Quiz
                    </span>
                  )}

                  <span className="text-[var(--color-ink-faint)]">·</span>

                  {/* Render state indicator */}
                  <span className="text-[10px]">
                    {status === "ready" ? (
                      <span className="text-[var(--color-accent-teal)] font-medium">Ready</span>
                    ) : status === "rendering" ? (
                      <span className="text-[var(--color-accent-amber)] animate-pulse font-medium">
                        Rendering…
                      </span>
                    ) : status === "failed" ? (
                      <span className="text-[var(--color-accent-coral)] font-medium">Audio Lesson</span>
                    ) : (
                      <span className="text-[var(--color-ink-faint)]">Upcoming</span>
                    )}
                  </span>
                </div>
              </div>

              {/* Active / Action indicator */}
              <div className="flex-shrink-0 self-center">
                {isActive ? (
                  <span className="flex h-1.5 w-1.5 rounded-full bg-[var(--color-primary)] ring-4 ring-[var(--color-primary)]/20" />
                ) : (
                  <span className="text-[var(--color-ink-faint)] group-hover:text-[var(--color-ink-muted)] text-xs">
                    →
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
