"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { LearnerProfile } from "@/lib/types";

// Student identity context
const STUDENT_ID =
  process.env.NEXT_PUBLIC_STUDENT_ID ?? "00000000-0000-0000-0000-000000000001";

// Curated academic curriculum tracks with structured progression steps
const CURATED_TRACKS = [
  {
    id: "track-calculus",
    title: "Calculus & Real Analysis",
    field: "Mathematics",
    color: "blue" as const,
    description:
      "Rigorous foundations from infinitesimal limits to differential calculus, integral accumulation, and the Fundamental Theorem.",
    estimatedHours: 18,
    steps: [
      { order: 1, topic: "Limits & Epsilon-Delta Intuition", status: "unlocked" },
      { order: 2, topic: "Derivatives as Instantaneous Rates of Change", status: "unlocked" },
      { order: 3, topic: "Chain Rule & Implicit Differentiation", status: "unlocked" },
      { order: 4, topic: "Riemann Sums & Definite Integrals", status: "locked" },
      { order: 5, topic: "The Fundamental Theorem of Calculus", status: "locked" },
    ],
  },
  {
    id: "track-mechanics",
    title: "Classical & Vector Mechanics",
    field: "Physics",
    color: "emerald" as const,
    description:
      "Newtonian dynamics, conservation laws, rotational kinematics, and harmonic oscillations grounded in experimental observation.",
    estimatedHours: 15,
    steps: [
      { order: 1, topic: "Vector Kinematics & Projectile Motion", status: "unlocked" },
      { order: 2, topic: "Newton's Laws & Free-Body Analysis", status: "unlocked" },
      { order: 3, topic: "Work-Energy Theorem & Conservation", status: "locked" },
      { order: 4, topic: "Linear Momentum & Elastic Collisions", status: "locked" },
      { order: 5, topic: "Rotational Inertia & Torque", status: "locked" },
    ],
  },
  {
    id: "track-organic",
    title: "Organic Chemistry: Mechanisms & Synthesis",
    field: "Chemistry",
    color: "amber" as const,
    description:
      "Three-dimensional stereochemistry, electrophilic addition, SN1/SN2 substitution kinetics, and carbonyl reaction pathways.",
    estimatedHours: 16,
    steps: [
      { order: 1, topic: "Hybridization & Resonance Structures", status: "unlocked" },
      { order: 2, topic: "Stereochemistry & Chiral Centers", status: "unlocked" },
      { order: 3, topic: "Nucleophilic Substitution: SN1 vs SN2", status: "locked" },
      { order: 4, topic: "Elimination Mechanisms: E1 and E2", status: "locked" },
      { order: 5, topic: "Carbonyl Nucleophilic Addition", status: "locked" },
    ],
  },
  {
    id: "track-algorithms",
    title: "Data Structures & Algorithmic Thinking",
    field: "Computer Science",
    color: "violet" as const,
    description:
      "Asymptotic complexity, recursive tree traversals, graph connectivity, and dynamic programming memoization models.",
    estimatedHours: 20,
    steps: [
      { order: 1, topic: "Big-O Notation & Complexity Analysis", status: "unlocked" },
      { order: 2, topic: "Binary Search Trees & Balancing", status: "unlocked" },
      { order: 3, topic: "Graph Traversals: BFS & DFS Search", status: "locked" },
      { order: 4, topic: "Dijkstra's Shortest Path Algorithm", status: "locked" },
      { order: 5, topic: "Dynamic Programming Memoization", status: "locked" },
    ],
  },
];

export default function CurriculumMapPage() {
  const router = useRouter();
  const { push } = useToast();
  const [profile, setProfile] = React.useState<LearnerProfile | null>(null);
  const [customTopic, setCustomTopic] = React.useState("");
  const [generating, setGenerating] = React.useState(false);
  const [activeTrackField, setActiveTrackField] = React.useState<string>("all");

  React.useEffect(() => {
    api
      .getLearnerProfile(STUDENT_ID)
      .then(setProfile)
      .catch(() => null);
  }, []);

  async function handleCreatePath(topicToBuild: string) {
    if (!topicToBuild.trim() || generating) return;
    setGenerating(true);
    try {
      const created = await api.createLearningPath(STUDENT_ID, topicToBuild.trim());
      push("success", `Curriculum roadmap created for "${topicToBuild}"`);
      router.push(`/learning-path/${created.id}`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to generate learning path.";
      push("error", msg);
      setGenerating(false);
    }
  }

  const filteredTracks = React.useMemo(() => {
    if (activeTrackField === "all") return CURATED_TRACKS;
    return CURATED_TRACKS.filter(
      (t) => t.field.toLowerCase() === activeTrackField.toLowerCase()
    );
  }, [activeTrackField]);

  return (
    <div className="mx-auto max-w-[1140px] px-6 py-10">
      {/* Editorial Header */}
      <header className="mb-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="text-[11px] font-mono tracking-widest uppercase text-[var(--color-primary-accent)] mb-1 block">
              Curriculum Architecture
            </span>
            <h1 className="text-heading-1 font-serif text-[var(--color-ink)] mb-1.5">
              Subject Roadmaps & Progression
            </h1>
            <p className="text-body-sm text-[var(--color-ink-muted)] max-w-2xl">
              Structured Socratic trajectories from foundational prerequisites to advanced
              synthesis. Each milestone reinforces prerequisite concepts before unlocking the next tier.
            </p>
          </div>

          <Link href="/dashboard">
            <Button variant="secondary" className="text-xs px-3.5 py-1.5">
              ← Return to Desk
            </Button>
          </Link>
        </div>
      </header>

      {/* Dynamic Curriculum Generator Bar */}
      <Card variant="elevated" className="mb-10 bg-[var(--color-canvas)]">
        <CardBody className="p-6">
          <div className="max-w-2xl">
            <p className="text-xs font-mono uppercase tracking-wider text-[var(--color-ink-faint)] mb-1">
              Custom Path Synthesis
            </p>
            <h2 className="text-base font-semibold text-[var(--color-ink)] mb-2">
              Generate a Tailored Curriculum Roadmap
            </h2>
            <p className="text-body-sm text-[var(--color-ink-muted)] mb-4">
              Enter any textbook chapter, syllabus topic, or exam domain. The AI pedagogical engine
              will decompose it into an ordered, step-by-step Socratic progression.
            </p>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleCreatePath(customTopic);
            }}
            className="flex flex-col sm:flex-row gap-2 max-w-2xl"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                placeholder="e.g. Electromagnetism & Maxwell's Equations, Macroeconomics, Linear Algebra..."
                className="w-full rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas-soft)] px-4 py-2.5 text-xs text-[var(--color-ink)] placeholder:text-[var(--color-ink-faint)] focus:border-[var(--color-primary)] focus:bg-white focus:outline-none transition-colors"
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              disabled={generating || !customTopic.trim()}
              className="text-xs px-5 py-2.5 shrink-0 shadow-xs"
            >
              {generating ? "Synthesizing Roadmap…" : "Build Roadmap →"}
            </Button>
          </form>
        </CardBody>
      </Card>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-heading-2 text-[var(--color-ink)] mb-0.5">
            Core Academic Roadmaps
          </h2>
          <p className="text-caption text-[var(--color-ink-muted)]">
            Explore verified benchmark curricula calibrated to CBSE Class 11–12 and undergraduate foundations.
          </p>
        </div>

        <div className="flex items-center gap-1 text-xs">
          {["all", "mathematics", "physics", "chemistry", "computer science"].map((f) => (
            <button
              key={f}
              onClick={() => setActiveTrackField(f)}
              className={`rounded-full px-3 py-1 font-medium capitalize transition-colors ${
                activeTrackField === f
                  ? "bg-[var(--color-primary)] text-white"
                  : "text-[var(--color-ink-secondary)] hover:bg-[var(--color-canvas-desk)]"
              }`}
            >
              {f === "all" ? "All Tracks" : f}
            </button>
          ))}
        </div>
      </div>

      {/* Track Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {filteredTracks.map((track) => (
          <Card
            key={track.id}
            variant="elevated"
            className="flex flex-col justify-between bg-[var(--color-canvas)] transition-all hover:shadow-[var(--shadow-level-2)] hover:-translate-y-0.5"
          >
            <CardBody className="p-6">
              <div className="flex items-center justify-between mb-3">
                <Badge color={track.color}>{track.field}</Badge>
                <span className="text-[11px] font-mono text-[var(--color-ink-faint)]">
                  ~{track.estimatedHours}h Total Study
                </span>
              </div>

              <CardTitle className="text-base font-semibold text-[var(--color-ink)] mb-1.5">
                {track.title}
              </CardTitle>
              <p className="text-body-sm text-[var(--color-ink-muted)] mb-5 leading-relaxed">
                {track.description}
              </p>

              {/* Milestone Stepper Preview */}
              <div className="space-y-2 border-t border-[var(--color-hairline)] pt-4 mb-6">
                <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-ink-faint)] mb-2">
                  Curriculum Milestones ({track.steps.length} Steps)
                </p>
                {track.steps.map((step) => (
                  <div
                    key={step.order}
                    className="flex items-center justify-between rounded-md bg-[var(--color-canvas-soft)] px-3 py-2 text-xs border border-[var(--color-hairline)]/50"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-canvas-desk)] text-[10px] font-mono text-[var(--color-ink-secondary)] font-semibold border border-[var(--color-hairline)]">
                        {step.order}
                      </span>
                      <span className="font-medium text-[var(--color-ink-secondary)]">
                        {step.topic}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-[var(--color-ink-faint)] uppercase">
                      {step.status === "unlocked" ? "Ready" : "Locked"}
                    </span>
                  </div>
                ))}
              </div>

              <Button
                variant="primary"
                onClick={() => handleCreatePath(track.title)}
                disabled={generating}
                className="w-full text-xs py-2 shadow-xs"
              >
                Launch This Learning Track →
              </Button>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
