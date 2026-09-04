import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** cn — merge Tailwind classes with conflict resolution. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** subjectColor — return the design-token accent for a given subject. */
export function subjectColor(subject: string): string {
  const s = subject.toLowerCase();
  if (
    s.includes("math") ||
    s.includes("algebra") ||
    s.includes("calculus") ||
    s.includes("geometry")
  )
    return "var(--color-accent-sky)";
  if (
    s.includes("science") ||
    s.includes("physics") ||
    s.includes("chemistry") ||
    s.includes("biology")
  )
    return "var(--color-accent-green)";
  if (s.includes("history") || s.includes("social"))
    return "var(--color-accent-orange)";
  if (
    s.includes("programming") ||
    s.includes("code") ||
    s.includes("computer") ||
    s.includes("react") ||
    s.includes("python")
  )
    return "var(--color-accent-purple)";
  if (s.includes("language") || s.includes("literature") || s.includes("english"))
    return "var(--color-accent-pink)";
  return "var(--color-accent-teal)";
}

/** formatRelativeDate — short humanised date. */
export function formatRelativeDate(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diff = (now.getTime() - date.getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`;
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)} d ago`;
  return date.toLocaleDateString();
}
