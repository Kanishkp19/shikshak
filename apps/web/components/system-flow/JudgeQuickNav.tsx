"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { STAGES, type StageId } from "./stages";

interface JudgeQuickNavProps {
  activeId: StageId;
  onSelect: (id: StageId) => void;
}

export function JudgeQuickNav({ activeId, onSelect }: JudgeQuickNavProps) {
  return (
    <nav
      aria-label="Stage quick navigation"
      className="fixed bottom-5 left-1/2 z-40 -translate-x-1/2 hidden sm:flex items-center gap-1.5 rounded-full border border-[var(--color-hairline-strong)] bg-[var(--color-canvas)]/95 backdrop-blur-md px-3 py-2 shadow-level-2"
    >
      {STAGES.map((s) => {
        const active = s.id === activeId;
        return (
          <button
            key={s.id}
            type="button"
            title={s.title}
            aria-label={`Go to ${s.title}`}
            aria-current={active ? "step" : undefined}
            onClick={() => onSelect(s.id)}
            className={cn(
              "h-2.5 rounded-full transition-all cursor-pointer",
              active
                ? "w-6 bg-[var(--color-primary)]"
                : "w-2.5 bg-[var(--color-hairline-strong)] hover:bg-[var(--color-ink-faint)]"
            )}
          />
        );
      })}
      <span className="ml-2 pl-2 border-l border-[var(--color-hairline)] text-[10px] font-mono text-[var(--color-ink-faint)] hidden md:inline">
        ← → keys
      </span>
    </nav>
  );
}
