import type { Config } from "tailwindcss";

/**
 * Shikshak AI — Tailwind v4 configuration.
 * In Tailwind v4, the design tokens live in `app/globals.css` under the
 * `@theme` block, so this file is intentionally minimal.
 */
export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
