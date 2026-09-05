"use client";

import * as React from "react";
import Link from "next/link";
import { Play } from "lucide-react";

interface SystemFlowHeroProps {
  onStartTour: () => void;
}

export function SystemFlowHero({ onStartTour }: SystemFlowHeroProps) {
  return (
    <section className="mx-auto max-w-6xl px-6 pt-14 pb-10 lg:pt-20 lg:pb-14">
      <div className="max-w-3xl">
        <p className="inline-flex items-center gap-2 rounded-md border border-[var(--color-hairline-strong)] bg-[var(--color-canvas)] px-3 py-1 text-[11.5px] font-mono uppercase tracking-wider text-[var(--color-ink-secondary)] mb-6">
          <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-accent-teal)] animate-pulse" />
          Student desk · Live agent DAG
        </p>

        <h1 className="text-display-1 font-serif text-[var(--color-ink)] mb-5 tracking-tight">
          How Shikshak{" "}
          <span className="italic font-normal text-[var(--color-primary-accent)]">thinks</span>
        </h1>

        <p className="text-body-md text-[var(--color-ink-secondary)] mb-8 leading-relaxed max-w-2xl">
          Follow the real multi-agent pipeline — from PDF ingest to Socratic reteaching —
          and watch what each agent decides, why it remediates, and how the learner profile
          improves the next lesson.
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={onStartTour}
            className="inline-flex items-center gap-2 rounded-lg bg-[var(--color-primary)] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[var(--color-primary-hover)] transition-colors shadow-xs cursor-pointer"
          >
            <Play className="h-4 w-4" fill="currentColor" />
            Start guided tour
          </button>
          <Link
            href="/session/new"
            className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-hairline-strong)] bg-[var(--color-canvas)] px-5 py-2.5 text-sm font-medium text-[var(--color-ink)] hover:border-[var(--color-primary-accent)] transition-colors"
          >
            Try a real lesson →
          </Link>
        </div>
      </div>
    </section>
  );
}
