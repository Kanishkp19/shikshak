/**
 * Shikshak AI — ReportBand signature component.
 *
 * Top band of the report screen — the one other place besides the marketing
 * hero and lesson player that uses the dark inversion (secondary color).
 * White display-2 score numeral centered.
 */
export function ReportBand({ score }: { score: number }) {
  return (
    <div className="flex h-64 items-center justify-center rounded-lg bg-[var(--color-secondary)]">
      <div className="text-center">
        <p className="text-eyebrow text-white/70">FINAL SCORE</p>
        <p className="text-display-2 text-white">{Math.round(score)}</p>
        <p className="text-caption text-white/70">out of 100</p>
      </div>
    </div>
  );
}
