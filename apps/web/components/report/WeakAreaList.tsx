import { cn } from "@/lib/utils";

/**
 * Shikshak AI — WeakAreaList component.
 * Shows a list of weak concepts as orange-accented chips.
 */
export function WeakAreaList({
  items,
  className,
}: {
  items: string[];
  className?: string;
}) {
  if (items.length === 0) {
    return (
      <p className={cn("text-body-sm text-[var(--color-ink-muted)]", className)}>
        No weak areas recorded yet.
      </p>
    );
  }
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {items.map((c) => (
        <span
          key={c}
          className="inline-flex items-center rounded-md bg-[var(--color-accent-orange)] px-2 py-1 text-eyebrow text-white"
        >
          {c}
        </span>
      ))}
    </div>
  );
}
