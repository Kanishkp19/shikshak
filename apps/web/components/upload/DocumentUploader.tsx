"use client";

import * as React from "react";
import { FileDropzone } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/toast";

/**
 * Shikshak AI — DocumentUploader signature component.
 * Uploads the file immediately on selection, shows progress, returns
 * document_id to the parent form.
 */
export function DocumentUploader({
  studentId,
  onUploaded,
}: {
  studentId: string;
  onUploaded: (documentId: string) => void;
}) {
  const [uploading, setUploading] = React.useState(false);
  const [fileName, setFileName] = React.useState<string | null>(null);
  const { push } = useToast();

  async function handleFile(file: File) {
    setUploading(true);
    setFileName(file.name);
    try {
      const doc = await api.uploadDocument(file, studentId);
      onUploaded(doc.id);
      push("success", `Uploaded ${file.name} — ingesting now.`);
    } catch (e) {
      push("error", `Upload failed: ${(e as Error).message}`);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <FileDropzone accept=".pdf,.docx,.pptx" onFile={handleFile} />
      {fileName && (
        <div className="mt-2 flex items-center justify-between text-body-sm">
          <span className="text-[var(--color-ink-secondary)]">{fileName}</span>
          {uploading ? (
            <span className="text-[var(--color-ink-muted)]">Ingesting…</span>
          ) : (
            <span className="text-[var(--color-accent-green)]">Ready</span>
          )}
        </div>
      )}
    </div>
  );
}
