"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — Toast primitive.
 * Colored left border (4px) only — no full-surface tint — per 04-UI-UX-BRIEF.md.
 */
export type ToastKind = "info" | "success" | "error" | "warning";

export interface ToastState {
  id: string;
  kind: ToastKind;
  message: string;
}

interface ToastContextValue {
  toasts: ToastState[];
  push: (kind: ToastKind, message: string) => void;
  dismiss: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastState[]>([]);
  const push = React.useCallback((kind: ToastKind, message: string) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, kind, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);
  const dismiss = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);
  return (
    <ToastContext.Provider value={{ toasts, push, dismiss }}>
      {children}
      <ToastViewport />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside <ToastProvider>");
  return ctx;
}

const BORDER_COLOR: Record<ToastKind, string> = {
  info: "var(--color-primary)",
  success: "var(--color-accent-green)",
  error: "var(--color-danger)",
  warning: "var(--color-accent-orange)",
};

function ToastViewport() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {ctx.toasts.map((t) => (
        <div
          key={t.id}
          className={cn(
            "rounded-lg border bg-[var(--color-canvas)] p-3 pr-4 shadow-[var(--shadow-level-1)]",
            "min-w-[280px] max-w-md text-body-sm text-[var(--color-ink-secondary)]",
          )}
          style={{ borderLeft: `4px solid ${BORDER_COLOR[t.kind]}` }}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
