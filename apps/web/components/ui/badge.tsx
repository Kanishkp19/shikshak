import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — Badge primitive (Notion-style pill).
 *
 * Variants follow 04-UI-UX-BRIEF.md:
 *  - default   : canvas surface, hairline border
 *  - filled    : solid background using a subject color token
 *  - score-good: accent-green fill
 *  - score-low : accent-orange fill
 */
export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "filled" | "score-good" | "score-low";
  color?: string;
}

export function Badge({
  className,
  variant = "default",
  color,
  children,
  ...rest
}: BadgeProps) {
  const style: React.CSSProperties = {};
  if (color) {
    style.background = color;
    style.color = "white";
  }
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-1 text-eyebrow",
        variant === "default" &&
          "border border-[var(--color-hairline)] bg-[var(--color-canvas)] text-[var(--color-ink-secondary)]",
        variant === "filled" && "text-white",
        variant === "score-good" && "bg-[var(--color-accent-green)] text-white",
        variant === "score-low" && "bg-[var(--color-accent-orange)] text-white",
        className,
      )}
      style={style}
      {...rest}
    >
      {children}
    </span>
  );
}
