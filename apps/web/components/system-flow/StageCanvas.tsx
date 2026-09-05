"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { FlowStage, StageId } from "./stages";

interface StageCanvasProps {
  stage: FlowStage;
  activeId: StageId;
  highlightIndex: number;
}

export function StageCanvas({ stage, activeId, highlightIndex }: StageCanvasProps) {
  const nodes = stage.diagramNodes;

  return (
    <div
      key={activeId}
      className="sf-stage-enter rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-level-1 overflow-hidden"
    >
      <div className="border-b border-[var(--color-hairline)] px-5 py-4">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <div>
            <p className="text-eyebrow text-[var(--color-accent-sky)] mb-1">
              Stage {stage.number} · {stage.title}
            </p>
            <h2 className="text-heading-2 font-serif text-[var(--color-ink)]">{stage.subtitle}</h2>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-0">
        {/* Animated flow diagram */}
        <div className="relative p-5 lg:p-6 border-b lg:border-b-0 lg:border-r border-[var(--color-hairline)] bg-[var(--color-canvas-soft)]">
          <p className="text-caption text-[var(--color-ink-muted)] mb-4 font-mono uppercase tracking-wider">
            Data flow
          </p>

          <div className="flex flex-col gap-0">
            {nodes.map((node, i) => {
              const lit = i <= highlightIndex;
              const isCurrent = i === highlightIndex;
              return (
                <React.Fragment key={node.id}>
                  <div
                    className={cn(
                      "relative rounded-lg border px-4 py-3 transition-all duration-500",
                      lit
                        ? isCurrent
                          ? "border-[var(--color-accent-sky)] bg-[var(--color-accent-sky-soft)] shadow-level-1 scale-[1.02]"
                          : "border-[var(--color-accent-teal)]/40 bg-[var(--color-accent-teal-soft)]/40"
                        : "border-[var(--color-hairline)] bg-[var(--color-canvas)] opacity-55"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={cn(
                          "flex h-7 w-7 shrink-0 items-center justify-center rounded-md font-mono text-xs font-bold",
                          lit
                            ? "bg-[var(--color-primary)] text-white"
                            : "bg-[var(--color-canvas-desk)] text-[var(--color-ink-faint)]"
                        )}
                      >
                        {i + 1}
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-[var(--color-ink)] truncate">
                          {node.label}
                        </p>
                        <p className="text-[11px] text-[var(--color-ink-muted)] font-mono truncate">
                          {node.detail}
                        </p>
                      </div>
                      {isCurrent && (
                        <span className="ml-auto h-2 w-2 rounded-full bg-[var(--color-accent-sky)] sf-pulse" />
                      )}
                    </div>
                  </div>
                  {i < nodes.length - 1 && (
                    <div className="flex justify-center py-1" aria-hidden>
                      <div
                        className={cn(
                          "w-px h-5 transition-colors duration-500",
                          i < highlightIndex
                            ? "bg-[var(--color-accent-teal)]"
                            : "bg-[var(--color-hairline-strong)]"
                        )}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* SVG connector glow underlay */}
          <svg
            className="pointer-events-none absolute inset-0 opacity-20"
            width="100%"
            height="100%"
            aria-hidden
          >
            <defs>
              <linearGradient id="sf-flow-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0369a1" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#0f766e" stopOpacity="0.2" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Narrative split: student vs backend */}
        <div className="p-5 lg:p-6 flex flex-col gap-5">
          <div>
            <p className="text-eyebrow text-[var(--color-accent-amber)] mb-2">Student sees</p>
            <p className="text-body-sm text-[var(--color-ink)] leading-relaxed">
              {stage.studentSees}
            </p>
          </div>
          <div className="rounded-lg border border-[var(--color-hairline-chalk)] bg-[var(--color-chalk-board)] p-4 text-[var(--color-chalk-text)]">
            <p className="text-eyebrow text-[var(--color-accent-teal)] mb-2">Backend does</p>
            <p className="text-body-sm text-[var(--color-chalk-muted)] leading-relaxed">
              {stage.backendDoes}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
