import { Badge } from "@/components/ui/badge";

/**
 * Shikshak AI — ScoreBadge signature component.
 * - score >= 70  → accent-green fill + dark green text
 * - score <  70  → accent-orange fill + dark orange text
 * (semantic, not subject color, per 04-UI-UX-BRIEF.md)
 */
export function ScoreBadge({ score }: { score: number }) {
  const variant = score >= 70 ? "score-good" : "score-low";
  return <Badge variant={variant}>Score: {Math.round(score)}</Badge>;
}
