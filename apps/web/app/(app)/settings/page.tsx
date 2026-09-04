"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { signOut } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import type { LearnerProfile } from "@/lib/types";

const STUDENT_ID =
  process.env.NEXT_PUBLIC_STUDENT_ID ?? "00000000-0000-0000-0000-000000000001";

export default function SettingsPage() {
  const router = useRouter();
  const { push } = useToast();
  const [profile, setProfile] = React.useState<LearnerProfile | null>(null);
  const [level, setLevel] = React.useState("beginner");
  const [language, setLanguage] = React.useState("en");
  const [saving, setSaving] = React.useState(false);

  React.useEffect(() => {
    api
      .getLearnerProfile(STUDENT_ID)
      .then((p) => {
        setProfile(p);
        setLevel(p.defaultLevel ?? "beginner");
        setLanguage(p.defaultLanguage ?? "en");
      })
      .catch(() => {
        push("error", "Couldn't load profile.");
      });
  }, [push]);

  async function handleSave() {
    setSaving(true);
    try {
      await api.patchLearnerProfile(STUDENT_ID, {
        defaultLevel: level,
        defaultLanguage: language,
      });
      push("success", "Settings saved.");
    } catch {
      push("error", "Couldn't save.");
    } finally {
      setSaving(false);
    }
  }

  async function handleSignOut() {
    await signOut();
    router.push("/");
  }

  return (
    <div className="mx-auto max-w-[640px] px-6 py-12">
      <h1 className="text-heading-1 text-[var(--color-ink)] mb-6">Settings</h1>
      <Card variant="elevated">
        <CardBody>
          <CardTitle className="mb-4">Defaults</CardTitle>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-eyebrow text-[var(--color-ink-muted)] mb-1 block">
                Default level
              </label>
              <Select value={level} onChange={(e) => setLevel(e.target.value)}>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </Select>
            </div>
            <div>
              <label className="text-eyebrow text-[var(--color-ink-muted)] mb-1 block">
                Default language
              </label>
              <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">English</option>
                <option value="hi">हिन्दी</option>
                <option value="hi-Latn">Hinglish</option>
                <option value="ta">தமிழ்</option>
                <option value="te">తెలుగు</option>
              </Select>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-between">
            <Button variant="utility" onClick={handleSignOut}>
              Sign out
            </Button>
            <Button onClick={handleSave} loading={saving}>
              Save changes
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
