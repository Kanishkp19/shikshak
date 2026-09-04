# 03 — App Flow & Screen Specifications — Shikshak AI

## Route table

| Path | Component file | Auth required | Layout |
|---|---|---|---|
| `/` | `app/(marketing)/page.tsx` | No | Marketing layout |
| `/dashboard` | `app/(app)/dashboard/page.tsx` | Yes | App shell |
| `/session/new` | `app/(app)/session/new/page.tsx` | Yes | App shell |
| `/session/[sessionId]` | `app/(app)/session/[sessionId]/page.tsx` | Yes | App shell (full-bleed player) |
| `/session/[sessionId]/report` | `app/(app)/session/[sessionId]/report/page.tsx` | Yes | App shell |
| `/learning-path/[pathId]` | `app/(app)/learning-path/[pathId]/page.tsx` | Yes | App shell |
| `/settings` | `app/(app)/settings/page.tsx` | Yes | App shell |

## Navigation diagram

```
Marketing (/) --[Get started]--> Login/Signup (Supabase Auth) --> Dashboard
                                                                     |
                          +------------------------------------------+------------------------------+
                          |                        |                 |                               |
                    New Session            Continue Session   Learning Path                     Settings
                   (/session/new)       (/session/[id])     (/learning-path/[id])           (/settings)
                          |                        |
                          +--> creates session -->  Session Player (/session/[id])
                                                     |
                                                     +--> Checkpoint question (inline, no route change)
                                                     |
                                                     +--> Lesson complete --> Report (/session/[id]/report)
                                                                                   |
                                                                                   +--> Back to Dashboard
```

## Screen specifications

### `/` — Marketing landing
- Purpose: explain the product to a first-time visitor and drive signup.
- Layout: `hero-band` (dark indigo, per UI/UX brief) with headline, subhead, `button-primary` "Get started free" + `button-secondary` "See how it works".
- Visible elements: nav-bar, hero band, 3-up `feature-card` grid (Document-grounded / Personalized / Interactive), footer.
- Interactive elements: "Get started free" -> Supabase Auth signup; "See how it works" -> scroll to feature grid.
- Data fetched: none (static marketing content).
- Loading/empty/error states: none applicable (static page).

### `/dashboard` — Student home
- Purpose: entry point for starting a new lesson or resuming one, and a snapshot of learner progress.
- Layout: App shell with left sidebar nav (`ex-app-shell-row` pattern), main content area.
- Visible elements: "Start a new lesson" `button-primary`, list of past sessions as `feature-card` items (topic, date, score badge), a `LearnerProfile` summary card (topics studied count, average score, weak concepts as `badge-pill` chips).
- Interactive elements: clicking a past session card navigates to its report or resumes if `status: in_progress`; "Start a new lesson" navigates to `/session/new`.
- Data fetched: `GET /api/v1/sessions?studentId=...` on mount; `GET /api/v1/learner-profile/{studentId}`.
- Loading state: skeleton cards (3 placeholder `feature-card` shapes with shimmer).
- Empty state: `ex-empty-state-card` — "No lessons yet — start your first one" with a `button-primary` CTA.
- Error state: toast "Couldn't load your dashboard" with a retry button; cards area shows the empty state layout as a safe fallback.

### `/session/new` — Start a lesson
- Purpose: collect the inputs the Orchestrator needs — document or topic, level, language, time budget.
- Layout: single-column form card (`ex-auth-form-card` chrome reused), centered.
- Visible elements: tab toggle "Upload material" / "Enter a topic"; file dropzone (`DocumentUploader`) or `text-input` for topic; `level` select (beginner/intermediate/advanced); `language` select; `timeBudgetMinutes` select (5/20/60/"7 days"); `button-primary` "Start lesson".
- Interactive elements: file upload triggers immediate `POST /api/v1/documents` and shows a progress state before the rest of the form is usable; submitting the form triggers `POST /api/v1/sessions`.
- Form fields:
  - `file` (upload tab): type file, accepted `.pdf,.docx,.pptx`, max 25MB, error "File must be a PDF, DOCX, or PPTX under 25MB".
  - `topic` (topic tab): type text, required if no file, min 3 characters, error "Enter a topic to teach".
  - `level`: select, required, default `beginner`.
  - `language`: select, required, default `en`.
  - `timeBudgetMinutes`: select, required, default `20`.
- Loading state: "Start lesson" becomes a disabled spinner button while the Orchestrator builds the lesson plan (poll `GET /api/v1/sessions/{id}/status`).
- Empty/error state: inline field errors per validation above; a top-of-form banner if session creation fails ("Couldn't start your lesson — try again").
- Navigation trigger: on `status: planning -> in_progress`, auto-navigate to `/session/[sessionId]`.

### `/session/[sessionId]` — Lesson player (core screen)
- Purpose: play the generated video lesson segment by segment, surface checkpoint questions inline, and progress to the report at the end.
- Layout: full-bleed video player top, `SegmentTimeline` strip below it, chat-style transcript panel on the side (desktop) or below (mobile).
- Visible elements: video player (avatar + visuals), segment timeline dots (current segment highlighted per `activeIndicator` token), transcript of narration text, language switcher (`button-utility`), "pause/change language" control.
- Interactive elements:
  - Language switcher mid-lesson triggers `POST /api/v1/sessions/{id}/language` and regenerates the remaining segments' audio/video in the new language without resetting progress.
  - When a segment has `hasCheckpoint: true`, playback pauses and a `QuestionCard` modal-in-flow appears (not a full modal overlay — an inline card replacing the video area) with the question, options (if MCQ) or a `text-input`.
  - Submitting an answer triggers `POST /api/v1/sessions/{id}/answer`; on `isCorrect: false`, the response includes a `misconception` explanation segment that plays next before returning to the main lesson flow.
- Data fetched: `GET /api/v1/sessions/{id}` on mount, then polls `GET /api/v1/sessions/{id}/segments/{segmentId}/status` while a segment's video is still rendering.
- Loading state: while a segment is rendering, show a skeleton video frame with the loading messages ("Planning your lesson", "Rendering your teacher") and the narration text as soon as it's available even before video finishes, so the student isn't staring at nothing.
- Empty state: not applicable — a session always has at least one segment once created.
- Error state: if a segment's video generation fails even after provider fallback, the transcript text and audio-only playback are shown instead ("Video unavailable for this part — audio lesson below") rather than blocking the whole lesson.
- Navigation trigger: after the final segment and final assessment, auto-navigate to `/session/[sessionId]/report`.

### `/session/[sessionId]/report` — Assessment report
- Purpose: show the score, strong/weak areas, and recommendation; close the loop back to the learner profile.
- Layout: centered `feature-card-elevated` with a large score number, two-column strong/weak lists, a highlighted recommendation banner.
- Visible elements: score (large numeral, `{typography.display-2}`), `badge-pill` chips for strong areas (green sticker accent) and weak areas (orange sticker accent), recommendation text, "Back to dashboard" and "Start related lesson" buttons.
- Interactive elements: "Start related lesson" pre-fills `/session/new` with a suggested next topic from the Learning Path Agent.
- Data fetched: `GET /api/v1/sessions/{id}/report`.
- Loading state: skeleton score card while the Assessment Agent finalizes grading.
- Empty state: not applicable.
- Error state: toast + retry if report generation fails; session remains marked `in_progress` until it succeeds.

### `/learning-path/[pathId]` — Curriculum view
- Purpose: show an ordered breakdown of a broad topic into sub-topics with progress markers.
- Layout: vertical stepper list, each item a `feature-card` row.
- Visible elements: ordered sub-topic list with lock/complete/current status indicators, progress bar at top.
- Interactive elements: clicking an unlocked sub-topic navigates to `/session/new` pre-filled with that sub-topic.
- Data fetched: `GET /api/v1/learning-paths/{pathId}`.
- Loading/empty/error: skeleton stepper; error toast + retry.

### `/settings` — Account settings
- Purpose: manage language default, level default, and account info.
- Layout: simple form card.
- Visible elements: default language select, default level select, sign-out button.
- Interactive elements: saving triggers `PATCH /api/v1/learner-profile/{studentId}`.
- Data fetched: `GET /api/v1/learner-profile/{studentId}`.

## Modals / drawers / sheets

- **File upload progress**: inline within `/session/new`, not a separate modal.
- **QuestionCard**: inline-in-flow within the lesson player, not an overlay modal — deliberate, so it never blocks the student from seeing lesson context.
- **Confirm sign-out**: `ex-modal-card` chrome, "Are you sure you want to sign out?" with Cancel/Sign out buttons.

## Toast / notification triggers

- Session creation failure -> error toast
- Segment video generation fallback engaged -> informational toast ("Using a backup renderer for this part") — transparency, not hidden failure
- Report generation failure -> error toast with retry
- Settings saved -> success toast
- Network offline detected -> persistent warning toast until reconnected

## Global error states

- **Network down**: full-page banner "You're offline — reconnect to continue your lesson," lesson player pauses without losing state.
- **401 Unauthorized**: redirect to `/` with a toast "Please sign in again."
- **404**: dedicated not-found page with "Back to dashboard" link.
- **500 / agent failure**: session-level banner "Something went wrong generating this lesson — our team's been notified" with a retry action that re-triggers the failed agent only (not the whole session).
