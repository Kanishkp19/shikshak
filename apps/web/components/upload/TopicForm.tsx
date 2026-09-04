"use client";

import * as React from "react";
import { TextInput } from "@/components/ui/input";

/**
 * Shikshak AI — TopicForm signature component.
 * Plain text input for entering a topic to teach (used when source_type=topic).
 */
export function TopicForm({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="text-eyebrow text-[var(--color-ink-muted)] mb-1 block">
        Topic
      </label>
      <TextInput
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g. Newton's Laws of Motion"
        minLength={3}
        required
      />
      <p className="mt-1 text-caption text-[var(--color-ink-faint)]">
        Min 3 characters.
      </p>
    </div>
  );
}
