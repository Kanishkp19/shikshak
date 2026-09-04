import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

/**
 * Shikshak AI — ScoreCard signature component.
 * Shows the strong and weak areas of a session's assessment report.
 */
export function ScoreCard({
  strongAreas,
  weakAreas,
  recommendation,
}: {
  strongAreas: string[];
  weakAreas: string[];
  recommendation: string;
}) {
  return (
    <Card variant="elevated">
      <CardBody>
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <CardTitle className="mb-2">Strong areas</CardTitle>
            <div className="flex flex-wrap gap-2">
              {strongAreas.length === 0 ? (
                <span className="text-body-sm text-[var(--color-ink-muted)]">
                  None yet — keep practising.
                </span>
              ) : (
                strongAreas.map((s) => (
                  <Badge key={s} variant="score-good">
                    {s}
                  </Badge>
                ))
              )}
            </div>
          </div>
          <div>
            <CardTitle className="mb-2">Weak areas</CardTitle>
            <div className="flex flex-wrap gap-2">
              {weakAreas.length === 0 ? (
                <span className="text-body-sm text-[var(--color-ink-muted)]">
                  No weak areas identified.
                </span>
              ) : (
                weakAreas.map((w) => (
                  <Badge key={w} variant="score-low">
                    {w}
                  </Badge>
                ))
              )}
            </div>
          </div>
        </div>
        <div className="mt-6 rounded-md border-l-4 border-[var(--color-primary)] bg-[var(--color-canvas-soft)] p-4">
          <p className="text-eyebrow text-[var(--color-ink-muted)] mb-1">
            Recommended next step
          </p>
          <p className="text-body-md text-[var(--color-ink)]">{recommendation}</p>
        </div>
      </CardBody>
    </Card>
  );
}
