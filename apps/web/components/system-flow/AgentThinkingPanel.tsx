"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { ThinkingLog } from "./stages";

interface AgentThinkingPanelProps {
  logs: ThinkingLog[];
  visibleCount: number;
  stageTitle: string;
}

export function AgentThinkingPanel({
  logs,
  visibleCount,
  stageTitle,
}: AgentThinkingPanelProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [visibleCount]);

  return (
    <div className="rounded-xl border border-[var(--color-hairline-chalk)] bg-[var(--color-chalk-board)] shadow-chalk overflow-hidden flex flex-col min-h-[280px]">
      <div className="flex items-center justify-between gap-3 border-b border-[var(--color-hairline-chalk)] px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="flex gap-1" aria-hidden>
            <span className="h-2.5 w-2.5 rounded-full bg-[#f87171]/80" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#fbbf24]/80" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#34d399]/80" />
          </span>
          <p className="text-[11px] font-mono uppercase tracking-wider text-[var(--color-chalk-muted)]">
            agent_runtime · {stageTitle}
          </p>
        </div>
        <span className="text-[10px] font-mono text-[var(--color-accent-teal)]">LIVE</span>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-3 font-mono text-[12px] leading-relaxed space-y-2"
      >
        {logs.slice(0, visibleCount).map((log, i) => (
          <div
            key={`${log.agent}-${i}`}
            className={cn(
              "sf-log-enter flex gap-2 items-start",
              i === visibleCount - 1 && "text-[var(--color-chalk-text)]"
            )}
          >
            <span className="shrink-0 text-[var(--color-accent-teal)]">›</span>
            <div className="min-w-0">
              <span className="text-[var(--color-accent-amber)]">[{log.agent}]</span>{" "}
              <span className="text-[var(--color-chalk-muted)]">{log.message}</span>
            </div>
          </div>
        ))}
        {visibleCount < logs.length && (
          <div className="flex items-center gap-2 text-[var(--color-chalk-muted)] opacity-60">
            <span className="sf-cursor-blink">▌</span>
            <span>thinking…</span>
          </div>
        )}
        {visibleCount >= logs.length && logs.length > 0 && (
          <div className="pt-2 text-[var(--color-accent-teal)] text-[11px]">
            ✓ stage complete — advance or inspect agents below
          </div>
        )}
      </div>
    </div>
  );
}
