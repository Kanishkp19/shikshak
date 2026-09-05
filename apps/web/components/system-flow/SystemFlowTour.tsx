"use client";

import * as React from "react";
import Link from "next/link";
import { SystemFlowHero } from "@/components/system-flow/SystemFlowHero";
import { PipelineStepper } from "@/components/system-flow/PipelineStepper";
import { StageCanvas } from "@/components/system-flow/StageCanvas";
import { AgentThinkingPanel } from "@/components/system-flow/AgentThinkingPanel";
import { AgentDagMap } from "@/components/system-flow/AgentDagMap";
import { LearningLoopViz } from "@/components/system-flow/LearningLoopViz";
import { TeachSim } from "@/components/system-flow/TeachSim";
import { JudgeQuickNav } from "@/components/system-flow/JudgeQuickNav";
import {
  STAGES,
  STAGE_DURATION_MS,
  type StageId,
} from "@/components/system-flow/stages";

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = React.useState(false);
  React.useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/**
 * Interactive multi-agent walkthrough used inside the student app shell
 * (and reusable from marketing if needed).
 */
export function SystemFlowTour() {
  const tourRef = React.useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  const [activeId, setActiveId] = React.useState<StageId>("ingest");
  const [playing, setPlaying] = React.useState(false);
  const [progress, setProgress] = React.useState(0);
  const [highlightIndex, setHighlightIndex] = React.useState(0);
  const [logCount, setLogCount] = React.useState(1);
  const [selectedAgent, setSelectedAgent] = React.useState<string | null>(null);

  const stage = STAGES.find((s) => s.id === activeId) ?? STAGES[0];
  const stageIdx = STAGES.findIndex((s) => s.id === activeId);

  const jumpTo = React.useCallback((id: StageId) => {
    setActiveId(id);
    setPlaying(false);
    setProgress(0);
    setHighlightIndex(0);
    setLogCount(1);
  }, []);

  const startTour = React.useCallback(() => {
    setActiveId("ingest");
    setProgress(0);
    setHighlightIndex(0);
    setLogCount(1);
    setPlaying(true);
    tourRef.current?.scrollIntoView({
      behavior: reducedMotion ? "auto" : "smooth",
      block: "start",
    });
  }, [reducedMotion]);

  const replay = React.useCallback(() => {
    setActiveId("ingest");
    setProgress(0);
    setHighlightIndex(0);
    setLogCount(1);
    setPlaying(true);
  }, []);

  React.useEffect(() => {
    if (!playing) return;
    if (reducedMotion) {
      setHighlightIndex(stage.diagramNodes.length - 1);
      setLogCount(stage.thinking.length);
      const t = window.setTimeout(() => {
        if (stageIdx >= STAGES.length - 1) {
          setPlaying(false);
          setProgress(1);
          return;
        }
        setActiveId(STAGES[stageIdx + 1].id);
        setProgress(0);
        setHighlightIndex(0);
        setLogCount(1);
      }, 2500);
      return () => window.clearTimeout(t);
    }

    const start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const elapsed = now - start;
      const p = Math.min(1, elapsed / STAGE_DURATION_MS);
      setProgress(p);

      const nodeCount = stage.diagramNodes.length;
      const logLen = stage.thinking.length;
      setHighlightIndex(Math.min(nodeCount - 1, Math.floor(p * nodeCount)));
      setLogCount(Math.min(logLen, Math.max(1, Math.ceil(p * logLen))));

      if (p >= 1) {
        if (stageIdx >= STAGES.length - 1) {
          setPlaying(false);
          return;
        }
        setActiveId(STAGES[stageIdx + 1].id);
        setProgress(0);
        setHighlightIndex(0);
        setLogCount(1);
        return;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, activeId, stage, stageIdx, reducedMotion]);

  React.useEffect(() => {
    if (playing) return;
    setHighlightIndex(0);
    setLogCount(1);
    if (reducedMotion) {
      setHighlightIndex(stage.diagramNodes.length - 1);
      setLogCount(stage.thinking.length);
      return;
    }
    const timers: number[] = [];
    stage.diagramNodes.forEach((_, i) => {
      timers.push(window.setTimeout(() => setHighlightIndex(i), 280 * (i + 1)));
    });
    stage.thinking.forEach((log, i) => {
      timers.push(
        window.setTimeout(() => setLogCount(i + 1), log.delayMs || 400 * (i + 1))
      );
    });
    return () => timers.forEach((t) => clearTimeout(t));
  }, [activeId, playing, reducedMotion, stage]);

  React.useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)
        return;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        jumpTo(STAGES[Math.min(STAGES.length - 1, stageIdx + 1)].id);
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        jumpTo(STAGES[Math.max(0, stageIdx - 1)].id);
      } else if (e.key === " ") {
        e.preventDefault();
        setPlaying((p) => !p);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [stageIdx, jumpTo]);

  React.useEffect(() => {
    const first = stage.thinking[0]?.agent;
    if (first && first !== "orchestrator") {
      setSelectedAgent(first);
    }
  }, [stage]);

  return (
    <div className="relative pb-20">
      <SystemFlowHero onStartTour={startTour} />

      <div className="mx-auto w-full max-w-6xl px-6 space-y-8 pb-10">
        <div ref={tourRef} className="scroll-mt-8 space-y-5">
          <PipelineStepper
            activeId={activeId}
            playing={playing}
            progress={progress}
            onSelect={jumpTo}
            onTogglePlay={() => setPlaying((p) => !p)}
            onReplay={replay}
          />

          <div className="grid lg:grid-cols-[1.35fr_0.85fr] gap-5">
            <StageCanvas
              stage={stage}
              activeId={activeId}
              highlightIndex={highlightIndex}
            />
            <AgentThinkingPanel
              logs={stage.thinking}
              visibleCount={logCount}
              stageTitle={stage.title}
            />
          </div>
        </div>

        <TeachSim visible={activeId === "teach"} />

        <AgentDagMap
          activeStageId={activeId}
          selectedId={selectedAgent}
          onSelect={setSelectedAgent}
        />

        <LearningLoopViz active={activeId === "adapt" || !playing} />

        <section className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-chalk-board)] px-6 py-10 text-center text-[var(--color-chalk-text)]">
          <h2 className="text-heading-1 font-serif mb-3">Ready to see it teach?</h2>
          <p className="text-body-sm text-[var(--color-chalk-muted)] max-w-xl mx-auto mb-6">
            Upload a chapter or enter any concept — the same agents you just inspected will
            build a personalized interactive lesson.
          </p>
          <Link
            href="/session/new"
            className="inline-flex rounded-lg bg-white text-[var(--color-primary)] text-sm font-semibold px-5 py-2.5 hover:bg-[var(--color-accent-sky-soft)] transition-colors"
          >
            Open lesson studio →
          </Link>
        </section>
      </div>

      <JudgeQuickNav activeId={activeId} onSelect={jumpTo} />
    </div>
  );
}
