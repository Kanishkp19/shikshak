"use client";

import * as React from "react";

/**
 * Shikshak AI — Related Concepts Panel.
 *
 * Displays a grid of related topics for the current segment, allowing
 * the student to explore sub-topics by clicking on concept cards.
 * Shows prerequisite, same-level, and advanced concepts with visual indicators.
 */

interface RelatedConcept {
  concept: string;
  brief: string;
  prerequisite: boolean;
  difficulty: "easier" | "same" | "harder";
}

export interface RelatedConceptsProps {
  concepts: RelatedConcept[];
  loading: boolean;
  onSelect: (concept: string) => void;
  exploredConcepts?: Set<string>;
}

const DIFFICULTY_STYLES: Record<string, { bg: string; border: string; badge: string; label: string }> = {
  easier: {
    bg: "bg-emerald-500/5",
    border: "border-emerald-500/30 hover:border-emerald-400",
    badge: "bg-emerald-500/15 text-emerald-400",
    label: "Foundation",
  },
  same: {
    bg: "bg-sky-500/5",
    border: "border-sky-500/30 hover:border-sky-400",
    badge: "bg-sky-500/15 text-sky-400",
    label: "Related",
  },
  harder: {
    bg: "bg-violet-500/5",
    border: "border-violet-500/30 hover:border-violet-400",
    badge: "bg-violet-500/15 text-violet-400",
    label: "Advanced",
  },
};

export function RelatedConcepts({
  concepts,
  loading,
  onSelect,
  exploredConcepts = new Set(),
}: RelatedConceptsProps) {
  if (loading) {
    return (
      <div className="mt-4 rounded-xl bg-[var(--color-secondary)] p-4">
        <h3 className="text-heading-3 text-[var(--color-ink)] mb-3">
          🔗 Related Concepts
        </h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-24 animate-pulse rounded-lg bg-white/5 border border-white/10"
            />
          ))}
        </div>
      </div>
    );
  }

  if (!concepts.length) return null;

  return (
    <div className="mt-4 rounded-xl bg-[var(--color-secondary)] p-4">
      <h3 className="text-heading-3 text-[var(--color-ink)] mb-1">
        🔗 Explore Related Concepts
      </h3>
      <p className="text-body-sm text-[var(--color-ink-muted)] mb-3">
        Click a topic to deep-dive into it
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        {concepts.map((c) => {
          const style = DIFFICULTY_STYLES[c.difficulty] ?? DIFFICULTY_STYLES.same;
          const explored = exploredConcepts.has(c.concept);

          return (
            <button
              key={c.concept}
              onClick={() => onSelect(c.concept)}
              disabled={explored}
              className={`
                group relative rounded-lg border p-3 text-left transition-all duration-200
                ${style.bg} ${style.border}
                ${explored
                  ? "opacity-50 cursor-default"
                  : "cursor-pointer hover:scale-[1.02] active:scale-[0.98]"
                }
              `}
            >
              <div className="flex items-start justify-between gap-2">
                <h4 className="text-body-md font-semibold text-[var(--color-ink)]">
                  {c.prerequisite && "📋 "}
                  {c.concept}
                </h4>
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${style.badge}`}>
                  {c.prerequisite ? "Prerequisite" : style.label}
                </span>
              </div>
              {c.brief && (
                <p className="mt-1 text-body-sm text-[var(--color-ink-secondary)] line-clamp-2">
                  {c.brief}
                </p>
              )}
              {explored && (
                <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-black/30">
                  <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-400">
                    ✓ Explored
                  </span>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
