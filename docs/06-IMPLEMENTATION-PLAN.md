# 06 — Implementation Plan — Shikshak AI

Ordered so that every phase produces something demoable on its own, in case time runs out before the plan is finished. Each task is atomic enough to hand to a coding agent one at a time.

## Phase 0 — Scaffolding (no AI logic yet)

1. Init monorepo: `apps/web` (Next.js 15, TS strict, Tailwind v4, shadcn/ui installed) and `apps/api` (FastAPI, Poetry or plain venv + `requirements.txt` from `02-TRD.md`).
2. Create Supabase project; run all migrations in `05-BACKEND-SCHEMA.md` in numeric order via `supabase db push` or the SQL editor.
3. Wire Supabase Auth in the frontend (email + Google), protected route middleware for the `(app)` route group.
4. Set up Redis locally (`docker run -p 6379:6379 redis`) and `celery_app.py` with a working `group()`/`chain()` smoke test task.
5. Apply the CSS variables from `04-UI-UX-BRIEF.md` to `globals.css`; install the fonts (Inter).
6. **Checkpoint:** a logged-in user lands on an empty `/dashboard` showing the correct empty state.

## Phase 1 — Core teaching logic (text-only, no video)

7. Build `skills/pdf_parsing.py`, `docx_parsing.py`, `pptx_parsing.py` — pure functions, unit-test each against one sample file per type.
8. Build `skills/chunking_embedding.py` (sentence-window chunker + embedding call) and `skills/vector_search.py` (pgvector query).
9. Build `agents/content_ingestion.py` — wraps the three parsers, writes chunks + embeddings to `document_chunks`.
10. Build `agents/knowledge_retrieval.py` — given a query, returns top-k chunks with `section_label`.
11. Build `skills/prompt_templating.py` and `skills/json_schema_validation.py` — the shared foundation every LLM-calling agent will use from here on.
12. Build `agents/lesson_planning.py` — outputs an ordered list of segment briefs (concept, depth, suggested visual type) as validated JSON.
13. Build `agents/personalization.py` and `agents/time_budgeting.py` — transform the plan per level/time.
14. Build `agents/language.py` and `agents/explanation.py` — produce final narration scripts per segment.
15. Build `agents/visual_selection.py` — tags each segment's `visual_type`.
16. Build `agents/qa_grounding_guard.py` — checks explanation text against retrieved chunks (document sessions only), flags/regenerates unsupported claims.
17. Build `orchestrator/router.py` and `orchestrator/execution_plan.py` — wires agents 9-16 into the parallel/sequential DAG per `AI-TEACHER-AGENT-ARCHITECTURE.md` Section 5.
18. Wire `POST /api/v1/sessions` end-to-end against the orchestrator.
19. **Checkpoint:** hitting the endpoint with a topic or an uploaded PDF returns a full, personalized, grounded lesson plan as JSON — testable via Postman/curl with zero frontend.

## Phase 2 — Interactivity and assessment (still no video)

20. Build `agents/interaction.py` — generates checkpoint questions at planned pause points.
21. Build `agents/answer_evaluation.py` — grades a submitted answer against expected reasoning.
22. Build `agents/misconception_detection.py` and `skills/misconception_analogy_bank.py` — diagnoses wrong answers, produces a re-explanation.
23. Build `agents/assessment.py` — end-of-session quiz + report generation.
24. Wire `POST /api/v1/sessions/{id}/answer` and `GET /api/v1/sessions/{id}/report`.
25. **Checkpoint:** a full text-based lesson-question-wrong-answer-reteach-report loop works via API calls alone. This is your minimum viable demo if video runs out of time.

## Phase 3 — Learner memory and curriculum

26. Build `agents/learner_profile.py` — read/write to `learner_profiles`, called at session end and session start.
27. Build `agents/learning_path.py` — breaks a broad topic into `learning_path_items`.
28. Wire `/api/v1/learner-profile/*` and `/api/v1/learning-paths/*`.
29. **Checkpoint:** a second session for the same student reflects prior weak areas in its lesson plan.

## Phase 4 — Video pipeline

30. Build `skills/tts_synthesis.py` (XTTS-v2) — lock one reference voice clip, verify consistent output across 3 test sentences.
31. Build `skills/lip_sync_rendering.py` (Wav2Lip baseline) — lock one reference face image, verify consistent identity across 3 test clips.
32. Build `skills/video_generation/base.py`, `manim_provider.py` (default), `wan_zerogpu_provider.py`, `flow_cache_provider.py`, and `factory.py` — implement Manim first since it's zero-risk, add the other two only once Manim path is proven end-to-end.
33. Build `agents/voice_synthesis.py`, `agents/avatar_rendering.py`, `agents/concept_animation.py` as thin wrappers around the skills above.
34. Build `skills/video_stitching.py` (ffmpeg concat + Remotion overlay for captions/on-screen text) and `agents/video_compositing.py`.
35. Build `skills/caching.py` and wire it into `video_cache` — hash `(prompt, provider, params)`, check before generating.
36. Wire `POST /api/v1/sessions/{id}/segments/{segmentId}/render` and the automatic fallback chain (`wan_zerogpu` -> `manim` on timeout/failure).
37. **Checkpoint:** at least one full segment produces a real composited video (avatar + voice + a Manim concept animation) end-to-end.

## Phase 5 — Frontend build-out

38. Build the marketing page (`/`) per `03-APP-FLOW.md`.
39. Build `/dashboard` with real data fetching, loading skeletons, empty state.
40. Build `/session/new` with the upload/topic tab toggle and full form validation.
41. Build `/session/[sessionId]` — the lesson player, `SegmentTimeline`, inline `QuestionCard`, language switcher. This is the most complex screen; build it in sub-steps: static video playback first, then polling for rendering segments, then the inline question flow, then the language-switch flow.
42. Build `/session/[sessionId]/report` and `/learning-path/[pathId]`.
43. Build `/settings`.
44. **Checkpoint:** full click-through demo works end-to-end in the browser for at least one topic and one uploaded document.

## Phase 6 — Polish and hardening

45. Pass every screen against `04-UI-UX-BRIEF.md` — colors, radii, spacing, no ad-hoc values.
46. Add every error/loading/empty state listed in `03-APP-FLOW.md` — do not skip these, they're graded implicitly through "reliability."
47. Add rate limiting on `/api/v1/sessions` and `/api/v1/.../render` per the TRD security checklist.
48. Pre-generate and cache 5-10 full lesson videos across varied topics/subjects the night before the demo, so the actual live demo pulls from `video_cache` rather than generating live.
49. Manually verify every acceptance criterion in `01-PRD.md` against the running app.

## Phase 7 — Deployment and submission

50. Deploy frontend to Vercel; deploy backend + Celery worker to Render/Railway free tier, or run backend locally with a tunnel (ngrok/Cloudflare Tunnel) if free-tier compute is too limited for Celery workers.
51. Point `NEXT_PUBLIC_API_BASE_URL` at the deployed/tunneled backend.
52. Record the 3-7 minute submission video showing: document upload -> personalized lesson -> video segment -> in-lesson question -> wrong-answer re-teach -> final report -> a second session showing memory of weak areas.
53. Assemble the written report per the brief's submission requirements, disclosing the full tech stack from `02-TRD.md` honestly.
54. Final check against the Definition of Done checklist in `00-MASTER-PROMPT.md`.

## Testing strategy

- **Unit tests**: every skill in `skills/` gets at least one test with a real (small) sample input — parsers against one sample PDF/DOCX/PPTX, chunker against a known string, cache against a known hash collision case.
- **Agent tests**: each agent gets a test that mocks its LLM call and asserts the output validates against its Pydantic schema — catches prompt regressions without burning API quota on every test run.
- **Integration test**: one full scripted run of Phase 1's checkpoint (topic -> lesson plan) and Phase 2's checkpoint (question -> wrong answer -> re-teach -> report), run before every demo rehearsal.
- **Manual QA pass**: the full acceptance criteria list in `01-PRD.md`, checked by hand at least once the day before submission.

## Deployment checklist

- [ ] All environment variables from `02-TRD.md` set in both Vercel and the backend host
- [ ] Supabase RLS policies verified with a non-owner test account (confirm they actually get denied)
- [ ] `VIDEO_PROVIDER` set to `manim` as the safe default for the deployed demo; `wan_zerogpu`/`flow_cache` only enabled if verified working in the deployed environment beforehand
- [ ] Free-tier API quotas (Gemini, Groq, HF) checked to confirm headroom for a live judged demo session
- [ ] A pre-recorded fallback demo video exists in case live infra has any issue during judging

## Common failure points to pre-empt

- **LLM returns malformed JSON under load** — always validate + retry-once per the TRD error strategy before it reaches the frontend.
- **Video generation timeout mid-demo** — this is why the fallback chain and pre-generated cache from step 48 exist; never rely on a live generation succeeding in front of judges.
- **RLS misconfiguration silently returning empty results instead of an error** — test with a second real account, not just the owner account, before assuming security is correct.
- **Celery worker not running** — a very common "works on my machine" gap; document the exact `celery -A celery_app worker --loglevel=info` command in the README and confirm it's part of the deployed process, not just local dev.
