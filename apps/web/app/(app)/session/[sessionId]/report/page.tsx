"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ReportBand } from "@/components/report/ReportBand";
import { ScoreCard } from "@/components/report/ScoreCard";
import { Button } from "@/components/ui/button";
import { Card, CardBody } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { AssessmentReport } from "@/lib/types";

export default function ReportPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;
  const router = useRouter();
  const { push } = useToast();
  const [report, setReport] = React.useState<AssessmentReport | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    (async () => {
      try {
        const r = await api.getReport(sessionId);
        if (!cancelled) setReport(r);
      } catch (e) {
        const msg = e instanceof ApiError ? e.message : "Couldn't generate report.";
        push("error", msg);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId, push]);

  if (loading) {
    return (
      <div className="mx-auto max-w-[640px] px-6 py-12">
        <div className="h-64 animate-pulse rounded-lg bg-[var(--color-hairline)]" />
        <div className="mt-6 h-40 animate-pulse rounded-lg bg-[var(--color-hairline)]" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="mx-auto max-w-[640px] px-6 py-12 text-center">
        <Card>
          <CardBody>
            <p className="text-body-md text-[var(--color-ink-secondary)] mb-4">
              Couldn&apos;t generate the report.
            </p>
            <Button onClick={() => router.refresh()}>Retry</Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[640px] px-6 py-12">
      <ReportBand score={report.score} />
      <div className="mt-6">
        <ScoreCard
          strongAreas={report.strongAreas}
          weakAreas={report.weakAreas}
          recommendation={report.recommendation}
        />
      </div>
      <div className="mt-6 flex justify-between">
        <Link href="/dashboard">
          <Button variant="secondary">Back to dashboard</Button>
        </Link>
        <Link
          href={{
            pathname: "/session/new",
            query: { topic: report.recommendation },
          }}
        >
          <Button>Start related lesson</Button>
        </Link>
      </div>
    </div>
  );
}
