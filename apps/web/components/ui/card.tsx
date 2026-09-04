import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — Card primitives (Classroom Study & Notion-style system).
 *
 * Variants:
 *  - default     : flat paper card with hairline border
 *  - elevated    : subtle multi-stop ambient shadow
 *  - notebook    : faint notebook paper lines with hairline border
 *  - chalkboard  : deep slate blackboard card for studio/player
 *  - study-desk  : warm parchment inset card
 */
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "notebook" | "chalkboard" | "study-desk";
  /** Optional colored header band using a subject color-coding token. */
  headerColor?: string;
}

export function Card({
  className,
  variant = "default",
  headerColor,
  children,
  ...rest
}: CardProps) {
  const isChalkboard = variant === "chalkboard";

  return (
    <div
      className={cn(
        "rounded-lg border transition-all duration-150",
        isChalkboard
          ? "border-[var(--color-hairline-chalk)] bg-[var(--color-chalk-surface)] text-[var(--color-chalk-text)] shadow-[var(--shadow-chalk)]"
          : "border-[var(--color-hairline)] bg-[var(--color-canvas)] text-[var(--color-ink)]",
        variant === "elevated" && "shadow-[var(--shadow-level-1)]",
        variant === "notebook" && "bg-notebook-paper shadow-[var(--shadow-level-1)]",
        variant === "study-desk" && "bg-[var(--color-canvas-desk)] border-[var(--color-hairline)]",
        className
      )}
      {...rest}
    >
      {headerColor && (
        <div
          className="h-1.5 rounded-t-lg"
          style={{ background: headerColor }}
        />
      )}
      {children}
    </div>
  );
}

export function CardBody({
  className,
  ...rest
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-5 sm:p-6", className)} {...rest} />;
}

export function CardTitle({
  className,
  ...rest
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("text-heading-3 text-inherit", className)}
      {...rest}
    />
  );
}
