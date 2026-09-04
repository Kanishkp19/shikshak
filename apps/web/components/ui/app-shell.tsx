"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ClassroomBackground } from "@/components/ui/classroom-background";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Study Desk",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  {
    href: "/session/new",
    label: "New Lesson",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
  },
  {
    href: "/learning-path",
    label: "Curriculum Map",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
  },
  {
    href: "/settings",
    label: "Settings",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
];

export function AppShellNav() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col justify-between w-60 shrink-0 border-r border-[var(--color-hairline)] bg-[var(--color-canvas)] p-5 z-20 sticky top-0 h-screen overflow-y-auto">
      <div>
        {/* Brand & Edition */}
        <Link href="/dashboard" className="group mb-7 block">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[var(--color-primary)] text-white text-xs font-serif font-bold tracking-wider">
              ∑
            </div>
            <div>
              <span className="block text-sm font-bold tracking-tight text-[var(--color-ink)] leading-none">
                Shikshak AI
              </span>
              <span className="text-[10.5px] font-mono tracking-wider text-[var(--color-ink-faint)] uppercase">
                Socratic Workspace
              </span>
            </div>
          </div>
        </Link>

        {/* Daily Study Streak Tracker */}
        <div className="mb-6 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas-soft)] p-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-semibold text-[var(--color-ink)] flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-accent-amber)]" />
              4-Day Focus Streak
            </span>
            <span className="text-[10px] font-mono text-[var(--color-ink-faint)]">30m Target</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-[var(--color-hairline)] overflow-hidden">
            <div className="h-full w-[70%] rounded-full bg-[var(--color-primary-accent)]" />
          </div>
          <p className="mt-1.5 text-[11px] text-[var(--color-ink-muted)]">
            22 mins completed today
          </p>
        </div>

        {/* Main Navigation */}
        <p className="text-[10.5px] font-mono font-semibold tracking-wider text-[var(--color-ink-faint)] uppercase mb-2 px-1">
          Navigation
        </p>
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "relative flex items-center gap-2.5 rounded-md px-2.5 py-2 text-xs font-medium transition-colors",
                  active
                    ? "bg-[var(--color-canvas-desk)] text-[var(--color-primary-accent)] font-semibold"
                    : "text-[var(--color-ink-secondary)] hover:bg-[var(--color-canvas-soft)] hover:text-[var(--color-ink)]"
                )}
              >
                {active && (
                  <span className="absolute left-0 top-1/2 h-4 w-1 -translate-y-1/2 rounded-r-full bg-[var(--color-primary-accent)]" />
                )}
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Subject Binder Shortcuts */}
        <div className="mt-7">
          <p className="text-[10.5px] font-mono font-semibold tracking-wider text-[var(--color-ink-faint)] uppercase mb-2 px-1">
            Subject Binders
          </p>
          <div className="flex flex-col gap-1 text-xs text-[var(--color-ink-secondary)]">
            <Link
              href="/dashboard?subject=mathematics"
              className="flex items-center justify-between rounded-md px-2 py-1.5 hover:bg-[var(--color-canvas-soft)] transition-colors"
            >
              <span className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-sky-500" />
                Mathematics
              </span>
              <span className="text-[10px] font-mono text-[var(--color-ink-faint)]">Calculus</span>
            </Link>
            <Link
              href="/dashboard?subject=physics"
              className="flex items-center justify-between rounded-md px-2 py-1.5 hover:bg-[var(--color-canvas-soft)] transition-colors"
            >
              <span className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Physics
              </span>
              <span className="text-[10px] font-mono text-[var(--color-ink-faint)]">Mechanics</span>
            </Link>
            <Link
              href="/dashboard?subject=chemistry"
              className="flex items-center justify-between rounded-md px-2 py-1.5 hover:bg-[var(--color-canvas-soft)] transition-colors"
            >
              <span className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                Chemistry
              </span>
              <span className="text-[10px] font-mono text-[var(--color-ink-faint)]">Organic</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Student Profile Carrel */}
      <div className="pt-4 border-t border-[var(--color-hairline)] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-canvas-desk)] text-[var(--color-ink)] font-semibold text-xs border border-[var(--color-hairline)]">
            AP
          </div>
          <div>
            <p className="text-xs font-semibold text-[var(--color-ink)] leading-tight">
              Aarav Pandey
            </p>
            <p className="text-[10px] text-[var(--color-ink-faint)] font-mono">
              Grade 11 · CBSE Prep
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <ClassroomBackground variant="parchment" className="flex min-h-screen">
      <AppShellNav />
      <main className="flex-1 min-w-0 overflow-x-hidden min-h-screen">{children}</main>
    </ClassroomBackground>
  );
}
