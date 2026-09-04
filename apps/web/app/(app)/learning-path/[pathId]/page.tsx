"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { LearningPath } from "@/lib/types";
import { cn } from "@/lib/utils";

export default function LearningPathPage() {
  const params = useParams<{ pathId: string }>();
  const pathId = params.pathId;
  const { push } = useToast();
  const [path, setPath] = React.useState<LearningPath | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!pathId) return;
    api
      .getLearningPath(pathId)
      .then(setPath)
      .catch((e) => {
        const msg = e instanceof ApiError ? e.message : "Couldn't load path.";
        push("error", msg);
      })
      .finally(() => setLoading(false));
  }, [pathId, push]);

  if (loading) {
    return (
      <div className="mx-auto max-w-[640px] px-6 py-12">
        <div className="h-12 animate-pulse rounded-md bg-[var(--color-hairline)] mb-6" />
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg bg-[var(--color-hairline)] mb-3" />
        ))}
      </div>
    );
  }

  if (!path) return null;

  const completedCount = path.items.filter((i) => i.status === "completed").length;
  const progress = Math.round((completedCount / path.items.length) * 100);

  return (
    <div className="mx-auto max-w-[640px] px-6 py-12">
      <h1 className="text-heading-1 text-[var(--color-ink)] mb-2">
        {path.broadTopic}
      </h1>
      <p className="text-body-sm text-[var(--color-ink-muted)] mb-6">
        {completedCount} of {path.items.length} complete
      </p>

      {/* Progress bar */}
      <div className="mb-8 h-2 w-full rounded-full bg-[var(--color-hairline)]">
        <div
          className="h-2 rounded-full bg-[var(--color-primary)] transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Stepper list */}
      <div className="flex flex-col gap-3">
        {path.items.map((item) => (
          <Card key={item.id}>
            <CardBody className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-full text-eyebrow",
                    item.status === "completed" && "bg-[var(--color-accent-green)] text-white",
                    item.status === "unlocked" && "bg-[var(--color-primary)] text-white",
                    item.status === "locked" && "bg-[var(--color-hairline)] text-[var(--color-ink-muted)]",
                  )}
                >
                  {item.status === "completed" ? "✓" : item.itemOrder}
                </span>
                <div>
                  <CardTitle>{item.subTopic}</CardTitle>
                  <p className="text-caption text-[var(--color-ink-faint)] mt-0.5">
                    Step {item.itemOrder}
                  </p>
                </div>
              </div>
              {item.status === "locked" ? (
                <Badge>Locked</Badge>
              ) : item.status === "completed" ? (
                <Badge variant="score-good">Done</Badge>
              ) : (
                <Link
                  href={{
                    pathname: "/session/new",
                    query: { topic: item.subTopic },
                  }}
                >
                  <Button variant="utility">Start →</Button>
                </Link>
              )}
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
