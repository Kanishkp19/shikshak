# 00 — MASTER PROMPT — Shikshak AI (AI Teacher)

Read this file first. It orchestrates every other document in this folder.

## Project summary

**Shikshak AI** is a multi-agent AI Teacher: a student uploads a book/PDF/notes/slides or names a topic, states their level, available time, and preferred language, and the system produces a structured, personalized, interactive video lesson — a lip-synced avatar teacher with voice, plus subject-appropriate diagrams/animations — that pauses to ask questions, detects misconceptions, adapts on the fly, and ends with a scored report and a recommendation for what to study next. Built for the AI Innovation Hackathon 2026 (Bharat Academix, Round 2).

## Tech stack (one line each)

- **Frontend:** Next.js 15 (App Router), TypeScript strict, Tailwind CSS v4, shadcn/ui
- **Backend:** FastAPI (Python 3.11), Celery + Redis for async agent orchestration
- **Database:** Supabase Postgres + pgvector extension (RAG embeddings) + Supabase Storage (documents, audio, video, cached clips)
- **Auth:** Supabase Auth (email + Google OAuth)
- **LLM:** Gemini 2.0/2.5 Flash (free tier, AI Studio) as primary; Groq Llama 3.3 70B for low-latency interaction turns
- **Voice:** Coqui XTTS-v2 (self-hosted, voice-cloned, multilingual)
- **Avatar:** Wav2Lip (baseline, reliable) with SadTalker as a quality upgrade path
- **Concept animation:** swappable provider interface — Manim (default, deterministic, zero-cost, zero-GPU) with Wan2.1-ZeroGPU / cached Google Flow clips as alternate providers
- **Video assembly:** ffmpeg + Remotion
- **Deployment:** Vercel (frontend), Render/Railway free tier or local tunnel (backend + Celery workers) for the demo

## Full folder structure

```
shikshak-ai/
├── apps/
│   ├── web/                          # Next.js frontend
│   │   ├── app/
│   │   │   ├── (marketing)/page.tsx
│   │   │   ├── (app)/dashboard/page.tsx
│   │   │   ├── (app)/session/new/page.tsx
│   │   │   ├── (app)/session/[sessionId]/page.tsx
│   │   │   ├── (app)/session/[sessionId]/report/page.tsx
│   │   │   ├── (app)/learning-path/[pathId]/page.tsx
│   │   │   ├── (app)/settings/page.tsx
│   │   │   ├── api/auth/callback/route.ts
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn primitives
│   │   │   ├── lesson/               # LessonPlayer, SegmentTimeline, QuestionCard
│   │   │   ├── upload/               # DocumentUploader, TopicForm
│   │   │   └── report/               # ScoreCard, WeakAreaList
│   │   ├── lib/
│   │   │   ├── supabase/client.ts
│   │   │   ├── api.ts                # typed fetch wrapper to FastAPI
│   │   │   └── types.ts
│   │   └── package.json
│   └── api/                          # FastAPI backend
│       ├── main.py
│       ├── orchestrator/
│       │   ├── router.py             # Orchestrator Agent
│       │   └── execution_plan.py
│       ├── agents/
│       │   ├── content_ingestion.py
│       │   ├── knowledge_retrieval.py
│       │   ├── lesson_planning.py
│       │   ├── personalization.py
│       │   ├── time_budgeting.py
│       │   ├── language.py
│       │   ├── explanation.py
│       │   ├── visual_selection.py
│       │   ├── voice_synthesis.py
│       │   ├── avatar_rendering.py
│       │   ├── concept_animation.py
│       │   ├── video_compositing.py
│       │   ├── interaction.py
│       │   ├── answer_evaluation.py
│       │   ├── misconception_detection.py
│       │   ├── assessment.py
│       │   ├── learner_profile.py
│       │   ├── learning_path.py
│       │   └── qa_grounding_guard.py
│       ├── skills/
│       │   ├── pdf_parsing.py
│       │   ├── docx_parsing.py
│       │   ├── pptx_parsing.py
│       │   ├── chunking_embedding.py
│       │   ├── vector_search.py
│       │   ├── prompt_templating.py
│       │   ├── json_schema_validation.py
│       │   ├── translation.py
│       │   ├── tts_synthesis.py
│       │   ├── lip_sync_rendering.py
│       │   ├── video_generation/
│       │   │   ├── base.py
│       │   │   ├── wan_zerogpu_provider.py
│       │   │   ├── manim_provider.py
│       │   │   ├── flow_cache_provider.py
│       │   │   └── factory.py
│       │   ├── video_stitching.py
│       │   ├── misconception_analogy_bank.py
│       │   ├── caching.py
│       │   └── supabase_persistence.py
│       ├── models/                   # Pydantic schemas
│       ├── celery_app.py
│       ├── config.py
│       └── requirements.txt
├── supabase/
│   └── migrations/
├── docs/                             # this folder
└── README.md
```

## Documents in this suite, in reading order

1. `01-PRD.md` — what we're building and why, features, personas, success metrics
2. `02-TRD.md` — full technical spec, architecture diagram, packages, env vars
3. `03-APP-FLOW.md` — every screen, route, and interaction in the frontend
4. `04-UI-UX-BRIEF.md` — design system (tokens, components) adapted from the supplied Notion-style design reference
5. `05-BACKEND-SCHEMA.md` — database tables, SQL migrations, RLS, full API contract
6. `06-IMPLEMENTATION-PLAN.md` — phase-by-phase build sequence with exact tasks
7. `README.md` — setup and run instructions

## Agent operating rules

- Always check `05-BACKEND-SCHEMA.md` before writing any API route or database query — never invent a column or table.
- Always match Tailwind classes and component variants to `04-UI-UX-BRIEF.md` — never introduce a new color or radius not in the token list.
- Every agent (see `AI-TEACHER-AGENT-ARCHITECTURE.md` in this folder) is a single-responsibility module with one input contract and one output contract. Never fold two agents' responsibilities into one function.
- All LLM outputs that feed into code (lesson plans, question objects, visual briefs) must be validated against a Pydantic schema before being trusted — never parse free-text LLM output with regex.
- The video-generation step must always go through `skills/video_generation/factory.py` — never call a video model's SDK/API directly from an agent.
- Independent agents run via `celery.group()`; dependent agents run via `celery.chain()`. Check `AI-TEACHER-AGENT-ARCHITECTURE.md` Section 5 before wiring a new agent call.

## Build command sequence

```
init  -> apps/web (Next.js) + apps/api (FastAPI) scaffolds, monorepo root package.json
db    -> supabase db push (run all migrations in 05-BACKEND-SCHEMA.md in order)
auth  -> Supabase Auth wiring, protected route middleware
core  -> Orchestrator + Content Ingestion + Knowledge Retrieval + Lesson Planning agents (text-only, testable via API/Postman before any frontend exists)
adapt -> Personalization + Time Budgeting + Language + Explanation agents
teach -> Interaction + Answer Evaluation + Misconception Detection + Assessment agents
data  -> Learner Profile + Learning Path agents
video -> Voice Synthesis + Avatar Rendering + Concept Animation (via swappable provider) + Video Compositing
web   -> frontend screens per 03-APP-FLOW.md, wired to the above via lib/api.ts
polish -> UI pass against 04-UI-UX-BRIEF.md, error/empty/loading states
test  -> manual pass of every acceptance criterion in 01-PRD.md
deploy -> per 06-IMPLEMENTATION-PLAN.md deployment checklist
```

## Definition of Done

- [ ] A student can upload a PDF and receive a personalized lesson plan grounded in that document (RAG citations present, no unsupported claims)
- [ ] A student can request a topic with no upload and receive a lesson plan
- [ ] The lesson plan respects the stated level, time budget, and language
- [ ] The system produces an actual video (avatar + voice + at least one subject-appropriate visual) for at least one lesson segment
- [ ] The lesson pauses at least once to ask a question, evaluates the answer, and — if wrong — re-explains with a different analogy
- [ ] A final report (score, strong/weak areas, recommendation) is generated and persisted to the learner profile
- [ ] Swapping the video provider (env var change + one new class) requires zero changes to any agent code
- [ ] All 7 docs in this folder are internally consistent (every PRD feature has a screen, an API endpoint, and an implementation task)
