"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { AGENTS, DAG_EDGES, type AgentNode, type StageId } from "./stages";

interface AgentDagMapProps {
  activeStageId: StageId;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

export function AgentDagMap({ activeStageId, selectedId, onSelect }: AgentDagMapProps) {
  const selected: AgentNode | undefined = AGENTS.find((a) => a.id === selectedId);

  return (
    <section className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-level-1 overflow-hidden">
      <div className="border-b border-[var(--color-hairline)] px-5 py-4">
        <p className="text-eyebrow text-[var(--color-ink-muted)] mb-1">Agent DAG</p>
        <h2 className="text-heading-2 font-serif text-[var(--color-ink)]">
          Click an agent to inspect
        </h2>
        <p className="text-body-sm text-[var(--color-ink-secondary)] mt-1 max-w-2xl">
          Ordered to match the orchestrator execution plan. Nodes lit for the current stage.
        </p>
      </div>

      <div className="grid lg:grid-cols-[1.4fr_1fr] gap-0">
        <div className="p-4 lg:p-5 overflow-x-auto border-b lg:border-b-0 lg:border-r border-[var(--color-hairline)]">
          <div className="flex flex-wrap gap-2 min-w-[520px]">
            {AGENTS.map((agent, i) => {
              const inStage = agent.stageIds.includes(activeStageId);
              const isSelected = agent.id === selectedId;
              const hasOutgoing = DAG_EDGES.some(([from]) => from === agent.id);

              return (
                <React.Fragment key={agent.id}>
                  <button
                    type="button"
                    onClick={() => onSelect(isSelected ? null : agent.id)}
                    className={cn(
                      "rounded-lg border px-3 py-2 text-left transition-all cursor-pointer max-w-[160px]",
                      isSelected
                        ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white shadow-level-1"
                        : inStage
                          ? "border-[var(--color-accent-sky)] bg-[var(--color-accent-sky-soft)] text-[var(--color-ink)]"
                          : "border-[var(--color-hairline)] bg-[var(--color-canvas-soft)] text-[var(--color-ink-secondary)] hover:border-[var(--color-hairline-strong)]"
                    )}
                  >
                    <span className="block font-mono text-[9px] uppercase tracking-wider opacity-70 mb-0.5">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="block text-xs font-semibold leading-snug">{agent.label}</span>
                  </button>
                  {hasOutgoing && i < AGENTS.length - 1 && (
                    <span
                      className={cn(
                        "self-center text-[10px] font-mono",
                        inStage ? "text-[var(--color-accent-teal)]" : "text-[var(--color-ink-faint)]"
                      )}
                      aria-hidden
                    >
                      →
                    </span>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* Compact edge legend */}
          <div className="mt-5 rounded-lg border border-dashed border-[var(--color-hairline-strong)] p-3">
            <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-ink-faint)] mb-2">
              Chain (execution_plan.py)
            </p>
            <p className="text-[11px] font-mono text-[var(--color-ink-muted)] leading-relaxed break-all">
              {DAG_EDGES.map(([a, b], i) => (
                <span key={`${a}-${b}`}>
                  {i === 0 && <span className="text-[var(--color-ink-secondary)]">{a}</span>}
                  <span className="text-[var(--color-ink-faint)]"> → </span>
                  <span className="text-[var(--color-ink-secondary)]">{b}</span>
                </span>
              ))}
            </p>
          </div>
        </div>

        <div className="p-5 bg-[var(--color-canvas-desk)] min-h-[220px]">
          {selected ? (
            <div className="sf-stage-enter space-y-4">
              <div>
                <p className="text-eyebrow text-[var(--color-accent-sky)] mb-1">Agent</p>
                <h3 className="text-heading-3 text-[var(--color-ink)]">{selected.label}</h3>
                <p className="text-[11px] font-mono text-[var(--color-ink-muted)] mt-0.5">
                  agents.{selected.id}
                </p>
              </div>
              <p className="text-body-sm text-[var(--color-ink-secondary)] leading-relaxed">
                {selected.responsibility}
              </p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-ink-faint)] mb-1.5">
                    Inputs
                  </p>
                  <ul className="space-y-1">
                    {selected.inputs.map((inp) => (
                      <li
                        key={inp}
                        className="rounded-md bg-[var(--color-canvas)] border border-[var(--color-hairline)] px-2 py-1 text-[11px] font-mono text-[var(--color-ink)]"
                      >
                        {inp}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-ink-faint)] mb-1.5">
                    Outputs
                  </p>
                  <ul className="space-y-1">
                    {selected.outputs.map((out) => (
                      <li
                        key={out}
                        className="rounded-md bg-[var(--color-accent-teal-soft)] border border-[var(--color-accent-teal)]/20 px-2 py-1 text-[11px] font-mono text-[var(--color-ink)]"
                      >
                        {out}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-center px-4">
              <p className="text-body-sm text-[var(--color-ink-muted)]">
                Select any agent node to see its contract — inputs, outputs, and responsibility.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
