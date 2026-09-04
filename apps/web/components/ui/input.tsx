import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — Input primitives.
 * - TextInput: radius-xs (4px), tight square corners
 * - Select: same chrome as text-input with chevron
 * - FileDropzone: dashed hairline border, radius-lg
 */
export const TextInput = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...rest }, ref) => (
  <input
    ref={ref}
    className={cn(
      "w-full rounded-xs border border-[var(--color-hairline)] bg-[var(--color-canvas)]",
      "px-3 py-2 text-body-md text-[var(--color-ink)] placeholder:text-[var(--color-ink-faint)]",
      "focus:border-[var(--color-primary)] focus:shadow-[var(--shadow-level-1)] focus:outline-none",
      className,
    )}
    {...rest}
  />
));
TextInput.displayName = "TextInput";

export const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...rest }, ref) => (
  <div className="relative inline-block w-full">
    <select
      ref={ref}
      className={cn(
        "w-full appearance-none rounded-xs border border-[var(--color-hairline)] bg-[var(--color-canvas)]",
        "px-3 py-2 pr-8 text-body-md text-[var(--color-ink)]",
        "focus:border-[var(--color-primary)] focus:shadow-[var(--shadow-level-1)] focus:outline-none",
        className,
      )}
      {...rest}
    >
      {children}
    </select>
    <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-ink-muted)]">
      ▾
    </span>
  </div>
));
Select.displayName = "Select";

export function FileDropzone({
  onFile,
  accept,
  maxSizeMb = 25,
  className,
}: {
  onFile: (file: File) => void;
  accept?: string;
  maxSizeMb?: number;
  className?: string;
}) {
  const [dragOver, setDragOver] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  function handleFiles(files: FileList | null) {
    if (!files || !files[0]) return;
    const file = files[0];
    if (file.size > maxSizeMb * 1024 * 1024) {
      setError(`File must be under ${maxSizeMb}MB`);
      return;
    }
    setError(null);
    onFile(file);
  }

  return (
    <label
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={cn(
        "block cursor-pointer rounded-lg border-2 border-dashed bg-[var(--color-canvas-soft)] p-8 text-center",
        dragOver
          ? "border-[var(--color-primary)]"
          : "border-[var(--color-hairline)]",
        className,
      )}
    >
      <input
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <div className="text-body-sm text-[var(--color-ink-muted)]">
        <div className="mb-2 text-3xl">📄</div>
        <p>Drag and drop your file here, or click to browse.</p>
        <p className="mt-1 text-caption text-[var(--color-ink-faint)]">
          PDF, DOCX, or PPTX · max {maxSizeMb}MB
        </p>
        {error && (
          <p className="mt-2 text-caption text-[var(--color-danger)]">{error}</p>
        )}
      </div>
    </label>
  );
}
