"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — Button primitive (Classroom Study & Notion-style design system).
 *
 * Variants:
 *  - primary     : #0075de fill, pill
 *  - secondary   : white surface, ink text, pill, soft shadow
 *  - utility     : white surface, radius-md, hairline border
 *  - icon        : rgba(0,0,0,0.05) fill, circular
 *  - study-amber : warm amber study highlighter button
 *  - chalk       : chalk white outline on dark chalkboard
 */
export type ButtonVariant =
  | "primary"
  | "secondary"
  | "utility"
  | "icon"
  | "study-amber"
  | "chalk";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
}

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-active)] " +
    "rounded-full px-5 py-2.5 text-button-label shadow-[var(--shadow-level-1)] active:scale-[0.99]",
  secondary:
    "bg-[var(--color-canvas)] text-[var(--color-ink)] rounded-full px-5 py-2.5 " +
    "text-button-label border border-[var(--color-hairline)] shadow-[var(--shadow-level-1)] hover:bg-[var(--color-canvas-desk)] active:scale-[0.99]",
  utility:
    "bg-[var(--color-canvas)] text-[var(--color-ink)] rounded-md px-3.5 py-2 text-body-sm " +
    "border border-[var(--color-hairline)] hover:border-[var(--color-primary)] active:bg-[var(--color-canvas-desk)]",
  icon: "bg-[rgba(0,0,0,0.05)] rounded-full p-2 text-[var(--color-ink)] hover:bg-[rgba(0,0,0,0.09)] active:scale-95",
  "study-amber":
    "bg-[var(--color-accent-amber)] text-white hover:bg-[#b45309] " +
    "rounded-full px-5 py-2.5 text-button-label shadow-[var(--shadow-level-1)] active:scale-[0.99]",
  chalk:
    "bg-transparent text-[var(--color-chalk-text)] rounded-full px-5 py-2.5 " +
    "text-button-label border border-[var(--color-hairline-chalk)] hover:bg-[rgba(255,255,255,0.08)] active:scale-[0.99]",
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", loading, children, disabled, ...rest }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex items-center justify-center gap-2 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer",
          VARIANT_CLASS[variant],
          className,
        )}
        {...rest}
      >
        {loading && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </button>
    );
  },
);
Button.displayName = "Button";
