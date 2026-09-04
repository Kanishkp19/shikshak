# Graph Report - shikshak-ai  (2026-08-31)

## Corpus Check
- 169 files · ~119,854 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1147 nodes · 1926 edges · 126 communities (74 shown, 48 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- assessment.py
- router.py
- dependencies
- devDependencies
- compilerOptions
- VideoGenerationProvider
- supabase_persistence.py
- types.ts
- video_compositing.py
- cn
- select_visuals
- lip_sync_rendering.py
- content_ingestion.py
- call_llm_with_retry
- SQL migrations
- Core features
- dashboard/page.tsx
- new/page.tsx
- [pathId]/page.tsx
- test_integration_phase1_2.py
- get_llm
- chunking_embedding.py
- toast.tsx
- upload_document
- answer_evaluation.py
- Supabase
- lesson_planning.py
- qa_grounding_guard.py
- Changelog
- test_chunking.py
- require_playable_video
- knowledge_retrieval.py
- llm.py
- Shikshak AI — AI Teacher
- Changelog
- Writing Guidelines for Postgres References
- caching.py
- prompt_templating.py
- parse_docx
- parse_pdf
- parse_pptx
- app-shell.tsx
- SessionPlayerPage
- client.ts
- package.json
- .eslintrc.json
- middleware.ts
- submit_answer
- conftest.py
- Shikshak AI — AI Teacher
- tests/__init__.py
- next.config.mjs
- next-env.d.ts
- postcss.config.mjs
- learner_profile.py
- get_session
- Screen specifications
- 02 — Technical Requirements Document — Shikshak AI
- 06 — Implementation Plan — Shikshak AI
- universal_diagram.py
- celery_app.py
- unhandled_exception_handler
- Section Definitions
- 04 — UI/UX Design System — Shikshak AI
- 00 — MASTER PROMPT — Shikshak AI (AI Teacher)
- language.py
- VisualBrief
- Supabase Postgres Best Practices
- scripts
- web/package.json
- get_video_stream
- rules/graphify.md
- advanced-full-text-search.md
- advanced-jsonb-indexing.md
- conn-idle-timeout.md
- conn-limits.md
- conn-pooling.md
- conn-prepared-statements.md
- data-batch-inserts.md
- data-n-plus-one.md
- data-pagination.md
- data-upsert.md
- lock-advisory.md
- lock-deadlock-prevention.md
- lock-short-transactions.md
- lock-skip-locked.md
- monitor-explain-analyze.md
- monitor-pg-stat-statements.md
- monitor-vacuum-analyze.md
- query-composite-indexes.md
- query-covering-indexes.md
- query-index-types.md
- query-missing-indexes.md
- query-partial-indexes.md
- schema-constraints.md
- schema-data-types.md
- schema-foreign-key-indexes.md
- schema-lowercase-identifiers.md
- schema-partitioning.md
- schema-primary-keys.md
- security-privileges.md
- security-rls-basics.md
- security-rls-performance.md
- _template.md
- workflows/graphify.md
- react
- react-dom
- tailwind-merge
- @tailwindcss/postcss
- @tanstack/react-query
- zustand
- concept_graph.py
- RateLimiter
- generate_with_fallback
- CinematicProvider
- explanation.py
- flow_cache_provider.py
- .generate
- config.py
- 03 — App Flow & Screen Specifications — Shikshak AI
- Local setup

## God Nodes (most connected - your core abstractions)
1. `get_client()` - 37 edges
2. `VisualBrief` - 34 edges
3. `cn()` - 27 edges
4. `run_session_pipeline()` - 23 edges
5. `call_llm_with_retry()` - 22 edges
6. `VideoGenerationProvider` - 22 edges
7. `get_llm()` - 20 edges
8. `CamelModel` - 20 edges
9. `compilerOptions` - 16 edges
10. `useToast()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `CinematicProvider` --uses--> `VisualBrief`  [INFERRED]
  apps/api/skills/video_generation/cinematic_provider.py → apps/api/skills/video_generation/base.py
- `DiagramProvider` --uses--> `VisualBrief`  [INFERRED]
  apps/api/skills/video_generation/diagram_provider.py → apps/api/skills/video_generation/base.py
- `generate_with_fallback()` --uses--> `VisualBrief`  [INFERRED]
  apps/api/skills/video_generation/factory.py → apps/api/skills/video_generation/base.py
- `FlowCacheProvider` --uses--> `VisualBrief`  [INFERRED]
  apps/api/skills/video_generation/flow_cache_provider.py → apps/api/skills/video_generation/base.py
- `_hash_brief()` --uses--> `VisualBrief`  [INFERRED]
  apps/api/skills/video_generation/flow_cache_provider.py → apps/api/skills/video_generation/base.py

## Import Cycles
- None detected.

## Communities (126 total, 48 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.12
Nodes (30): create_learning_path(), get_document(), get_learning_path(), Shikshak AI — FastAPI application entry point. Wires every endpoint defined in…, AgentError, AssessmentReportOut, _cam(), CamelModel (+22 more)

### Community 1 - "assessment.py"
Cohesion: 0.25
Nodes (10): assess_session(), AssessmentPlan, Any, BaseModel, task, Shikshak AI — Assessment Agent. Single responsibility: at the end of a session,…, Produce and persist the assessment report for `session_id`., run() (+2 more)

### Community 2 - "router.py"
Cohesion: 0.19
Nodes (15): build_execution_plan(), Shikshak AI — Execution Plan builder. Given a CreateSessionRequest, returns the…, One step of the execution DAG., Return the ordered list of Steps for the orchestrator to dispatch. The DAG (per…, Step, Shikshak AI — orchestrator package., _log_step(), _persist_segments() (+7 more)

### Community 3 - "dependencies"
Cohesion: 0.12
Nodes (17): dependencies, clsx, lucide-react, next, react-hook-form, @supabase/ssr, @supabase/supabase-js, typescript (+9 more)

### Community 4 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, autoprefixer, eslint, eslint-config-next, postcss, tailwindcss, @types/node, @types/react (+9 more)

### Community 5 - "compilerOptions"
Cohesion: 0.07
Nodes (26): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+18 more)

### Community 6 - "VideoGenerationProvider"
Cohesion: 0.15
Nodes (19): ABC, Shikshak AI — video generation provider base. Every video provider (Manim…, Every provider implements exactly this interface., Return False if the provider can't be used right now (missing deps, quota,…, VideoGenerationProvider, Shikshak AI — Cinematic AI Video Generation Provider (improved). Generates…, DiagramProvider, Diagram / Structured Vector Animation Provider for Shikshak AI. Generates… (+11 more)

### Community 7 - "supabase_persistence.py"
Cohesion: 0.16
Nodes (19): build_path(), PathPlan, Any, BaseModel, task, Shikshak AI — Learning Path Agent. Single responsibility: break a broad topic…, Generate + persist a learning path. Returns the path with items., run() (+11 more)

### Community 8 - "types.ts"
Cohesion: 0.15
Nodes (17): ApiError, call(), AgentError, AssessmentReport, CreateSessionRequest, DocumentOut, LearnerProfile, LearningPath (+9 more)

### Community 9 - "video_compositing.py"
Cohesion: 0.31
Nodes (8): composite_lesson(), composite_lesson_task(), composite_segment(), composite_segment_task(), task, Shikshak AI — Video Compositing Agent. Single responsibility: combine avatar +…, Return the final per-segment video path., Stitch all per-segment videos into one final lesson video.

### Community 10 - "cn"
Cohesion: 0.12
Nodes (18): NOTE: The backend auto-creates a checkpoint when a segment has, RelatedConcept, LessonPlayer(), LessonPlayerProps, LOADING_MESSAGES, splitSentences(), QuestionCard(), QuestionCardProps (+10 more)

### Community 11 - "select_visuals"
Cohesion: 0.22
Nodes (14): _infer_visual_type(), Any, task, Shikshak AI — Visual Selection Agent. Single responsibility: ensure every…, Walk every segment and upgrade 'none' to a better type if detectable from the…, run(), select_visuals(), Unit tests for agents/visual_selection.py. (+6 more)

### Community 12 - "lip_sync_rendering.py"
Cohesion: 0.16
Nodes (19): task, Shikshak AI — Avatar Rendering Agent. Single responsibility: take the…, Return the path to the rendered avatar video file., render(), run(), Path, Shikshak AI — lip-sync rendering skill (improved Wav2Lip + SadTalker). Uses a…, Use Wav2Lip for fast lip sync (works on CPU/MPS). (+11 more)

### Community 13 - "content_ingestion.py"
Cohesion: 0.27
Nodes (11): ingest_document(), _parse(), Any, task, Shikshak AI — Content Ingestion Agent. Single responsibility: take an uploaded…, Synchronous entry point (also called from the FastAPI request handler when the…, Celery task wrapper for the Content Ingestion Agent., run() (+3 more)

### Community 14 - "call_llm_with_retry"
Cohesion: 0.08
Nodes (39): diagnose_and_reteach(), Any, BaseModel, task, Shikshak AI — Misconception Detection Agent. Single responsibility: when an…, Returns a re-teach segment the orchestrator will splice in next., ReExplanation, run() (+31 more)

### Community 15 - "SQL migrations"
Cohesion: 0.08
Nodes (25): `001_learner_profiles.sql`, `002_documents.sql`, `003_document_chunks.sql`, `004_sessions.sql`, `005_lesson_segments.sql`, `006_question_checkpoints.sql`, `007_assessment_reports.sql`, `008_learning_paths.sql` (+17 more)

### Community 16 - "Core features"
Cohesion: 0.10
Nodes (20): 01 — Product Requirements Document — Shikshak AI, 10. Persistent learner profile and learning paths, 1. Document-grounded learning (RAG), 2. Topic-based learning (no upload required), 3. Personalized depth and style, 4. Time-adaptive lesson structuring, 5. Multilingual teaching with mid-lesson switching, 6. Human-like AI teaching video (+12 more)

### Community 17 - "dashboard/page.tsx"
Cohesion: 0.26
Nodes (6): SessionCard(), subjectLabel(), Badge(), BadgeProps, formatRelativeDate(), subjectColor()

### Community 18 - "new/page.tsx"
Cohesion: 0.17
Nodes (11): DashboardPage(), LearningPathPage(), NewSessionPage(), Tab, ReportPage(), FileDropzone(), Select, TextInput (+3 more)

### Community 19 - "[pathId]/page.tsx"
Cohesion: 0.24
Nodes (11): ReportBand(), ScoreCard(), Button, ButtonProps, ButtonVariant, VARIANT_CLASS, Card(), CardBody() (+3 more)

### Community 20 - "test_integration_phase1_2.py"
Cohesion: 0.24
Nodes (9): personalize(), Any, task, Shikshak AI — Personalization Agent. Single responsibility: given a lesson plan…, Rewrite segment depths to match `level`, and prepend one remediation segment…, run(), Integration test: full Phase 1 + Phase 2 checkpoint flow via API calls. Per…, End-to-end: topic → plan → personalize → budget → visuals → explain →… (+1 more)

### Community 21 - "get_llm"
Cohesion: 0.23
Nodes (11): generate_checkpoint(), Any, BaseModel, task, QuestionObject, Shikshak AI — Interaction Agent. Single responsibility: generate checkpoint…, Return a persisted checkpoint row for the segment., run() (+3 more)

### Community 22 - "chunking_embedding.py"
Cohesion: 0.24
Nodes (10): _embed_gemini(), _embed_local(), embed_query(), embed_texts(), Shikshak AI — chunking + embedding skill. Sentence-window chunker with optional…, Embed a single query string (used by the knowledge_retrieval agent)., Embed a list of strings using Gemini text-embedding-004, or fall back to…, Shikshak AI — vector search skill. Issues pgvector cosine-similarity queries… (+2 more)

### Community 23 - "toast.tsx"
Cohesion: 0.18
Nodes (9): inter, metadata, BORDER_COLOR, ToastContext, ToastContextValue, ToastKind, ToastProvider(), ToastState (+1 more)

### Community 24 - "upload_document"
Cohesion: 0.13
Nodes (16): create_session(), generate_next_segment(), NextSegmentRequest, BaseModel, Upload a PDF/DOCX/PPTX source document. Triggers Content Ingestion Agent., Create a new teaching session. Triggers the Orchestrator → agent DAG., Switch language mid-session. Re-renders remaining segments in the new language., Generate a deep-dive segment for a related concept. If selected_concept is… (+8 more)

### Community 25 - "answer_evaluation.py"
Cohesion: 0.27
Nodes (10): evaluate_answer(), _grade(), Any, task, Shikshak AI — Answer Evaluation Agent. Single responsibility: given a…, Grade a student's answer against the checkpoint's correct answer., Heuristic grader: case-insensitive match for MCQ (letter or value) and…, run() (+2 more)

### Community 26 - "Supabase"
Cohesion: 0.11
Nodes (15): Fix suggestion, Source, What happened, Skill Feedback, Steps, Core Principles, Debugging, Making and Committing Schema Changes (+7 more)

### Community 27 - "lesson_planning.py"
Cohesion: 0.27
Nodes (9): LessonPlan, plan_lesson(), Any, BaseModel, task, Shikshak AI — Lesson Planning Agent (v2). Generates structured lesson plans…, Return a validated lesson plan as a dict (snake_case for downstream agents)., run() (+1 more)

### Community 28 - "qa_grounding_guard.py"
Cohesion: 0.31
Nodes (8): _find_unsupported_claims(), guard(), Any, task, Shikshak AI — QA Grounding Guard Agent. Single responsibility: check…, Return {narration_script, flagged_claims, regenerated}. If narration_script…, Naive check: extract capitalised noun phrases from the script and verify each…, run()

### Community 29 - "Changelog"
Cohesion: 0.12
Nodes (16): [1.2.0](https://github.com/supabase/agent-skills/compare/v1.1.1...v1.2.0) (2026-06-02), [1.3.0](https://github.com/supabase/agent-skills/compare/v1.2.0...v1.3.0) (2026-06-05), [1.4.0](https://github.com/supabase/agent-skills/compare/v1.3.0...v1.4.0) (2026-07-10), [1.5.0](https://github.com/supabase/agent-skills/compare/supabase-postgres-best-practices-v1.4.0...supabase-postgres-best-practices-v1.5.0) (2026-07-30), [1.6.0](https://github.com/supabase/agent-skills/compare/supabase-postgres-best-practices-v1.5.0...supabase-postgres-best-practices-v1.6.0) (2026-07-30), Bug Fixes, Bug Fixes, Bug Fixes (+8 more)

### Community 30 - "test_chunking.py"
Cohesion: 0.31
Nodes (9): chunk_pages(), Cheap sentence splitter — handles Latin + Devanagari sentence enders., Sentence-window chunker. Args: pages: list of {"page": int, "section_label"?:…, _sentence_split(), Unit tests for skills/chunking_embedding.py. Verifies the sentence-window…, test_chunk_pages_handles_empty_input(), test_chunk_pages_returns_chunks(), test_sentence_split_basic() (+1 more)

### Community 31 - "require_playable_video"
Cohesion: 0.17
Nodes (20): Path, MediaInfo, MediaValidationError, probe_media(), Path, Small, strict media probes used at each video-pipeline boundary. The pipeline…, Raised when an expected media asset is absent or not decodable., Return decoded stream metadata, or raise when ffprobe rejects `path`. (+12 more)

### Community 32 - "knowledge_retrieval.py"
Cohesion: 0.28
Nodes (7): Any, task, Shikshak AI — Knowledge Retrieval Agent. Single responsibility: given a…, Return top_k chunks for the query. If document_id is None (topic-only mode),…, retrieve(), run(), Shikshak AI — skills package.

### Community 33 - "llm.py"
Cohesion: 0.24
Nodes (11): _extract_topic_from_prompt(), gemini_llm(), get_fast_llm(), groq_llm(), Shared LLM caller helpers used by every agent. Agents never call `genai` or…, Return the fast-turnaround LLM callable (Groq, for interaction loop)., Extract topic/concept from prompt text for dynamic fallback responses., Dynamic fallback response that incorporates the actual concept name. (+3 more)

### Community 34 - "Shikshak AI — AI Teacher"
Cohesion: 0.20
Nodes (10): Asset placeholders, Documentation, Known limitations, License, Monorepo layout, Running tests, Shikshak AI — AI Teacher, Tech stack (+2 more)

### Community 35 - "Changelog"
Cohesion: 0.12
Nodes (15): [0.1.3](https://github.com/supabase/agent-skills/compare/v0.1.2...v0.1.3) (2026-06-02), [0.1.4](https://github.com/supabase/agent-skills/compare/v0.1.3...v0.1.4) (2026-06-05), [0.1.5](https://github.com/supabase/agent-skills/compare/v0.1.4...v0.1.5) (2026-07-10), [0.1.6](https://github.com/supabase/agent-skills/compare/v0.1.5...supabase-v0.1.6) (2026-07-30), [0.1.7](https://github.com/supabase/agent-skills/compare/v0.1.6...supabase-v0.1.7) (2026-08-12), Bug Fixes, Bug Fixes, Bug Fixes (+7 more)

### Community 36 - "Writing Guidelines for Postgres References"
Cohesion: 0.12
Nodes (15): 1. Concrete Transformation Patterns, 2. Error-First Structure, 3. Quantified Impact, 4. Self-Contained Examples, 5. Semantic Naming, Code Example Standards, Comments, Impact Level Guidelines (+7 more)

### Community 37 - "caching.py"
Cohesion: 0.29
Nodes (6): cached_or_compute(), make_prompt_hash(), Any, Shikshak AI — caching skill. Hashes (prompt, provider, params) into a stable…, Return a 16-char hash of any tuple of JSON-serialisable inputs., Generic cache helper used by the voice_synthesis and concept_animation agents.…

### Community 38 - "prompt_templating.py"
Cohesion: 0.29
Nodes (4): PromptTemplate, Any, Shikshak AI — shared prompt templating skill. Every LLM call that embeds user-…, Simple Jinja-like template — no external dependency, escapes nothing, but…

### Community 39 - "parse_docx"
Cohesion: 0.33
Nodes (5): parse_docx(), Any, Path, Shikshak AI — DOCX parsing skill. Wraps python-docx with a single function…, Parse a DOCX file into paragraphs grouped by heading. Returns: { "page_count":…

### Community 40 - "parse_pdf"
Cohesion: 0.33
Nodes (5): parse_pdf(), Any, Path, Shikshak AI — PDF parsing skill. Wraps PyMuPDF (fitz) with a single function…, Parse a PDF file into pages of plain text. Returns: { "page_count": int,…

### Community 41 - "parse_pptx"
Cohesion: 0.33
Nodes (5): parse_pptx(), Any, Path, Shikshak AI — PPTX parsing skill. Wraps python-pptx with a single function…, Parse a PPTX file into slide-level text chunks. Returns: { "page_count": int,…

### Community 42 - "app-shell.tsx"
Cohesion: 0.40
Nodes (3): AppShell(), AppShellNav(), NAV_ITEMS

### Community 43 - "SessionPlayerPage"
Cohesion: 0.40
Nodes (3): SessionPlayerPage(), handleAnswer(), nextSegment()

### Community 44 - "client.ts"
Cohesion: 0.20
Nodes (4): SettingsPage(), handleSignOut(), signOut(), supabase

### Community 45 - "package.json"
Cohesion: 0.33
Nodes (5): name, private, version, workspaces, apps/web

### Community 48 - "submit_answer"
Cohesion: 0.22
Nodes (11): generate_deep_dive(), Any, task, Shikshak AI — Deep Dive Generation Agent. Single responsibility: when the user…, Generate a deep-dive segment for the given concept. Returns a segment dict with…, run(), Shikshak AI — agents package. Each agent is a single-responsibility module with…, Submit an answer to a checkpoint. If wrong, returns a misconception re-teach… (+3 more)

### Community 50 - "Shikshak AI — AI Teacher"
Cohesion: 0.12
Nodes (15): 1. Clone and install, 2. Configure environment variables, 3. Set up the database, 4. Run the backend, 5. Run the frontend, Documentation, Known limitations, License (+7 more)

### Community 58 - "learner_profile.py"
Cohesion: 0.24
Nodes (14): Any, task, Shikshak AI — Learner Profile Agent. Single responsibility: read and update the…, Return the student's profile, creating an empty one if absent., At session end, merge the report's strong/weak areas into the profile, add the…, read_profile(), read_task(), update_profile_from_report() (+6 more)

### Community 59 - "get_session"
Cohesion: 0.18
Nodes (15): _format_video_url(), get_related_concepts(), get_report(), get_segment_status(), get_session(), get_session_status(), health(), list_sessions() (+7 more)

### Community 60 - "Screen specifications"
Cohesion: 0.25
Nodes (8): `/dashboard` — Student home, `/learning-path/[pathId]` — Curriculum view, `/` — Marketing landing, Screen specifications, `/session/new` — Start a lesson, `/session/[sessionId]` — Lesson player (core screen), `/session/[sessionId]/report` — Assessment report, `/settings` — Account settings

### Community 61 - "02 — Technical Requirements Document — Shikshak AI"
Cohesion: 0.15
Nodes (13): 02 — Technical Requirements Document — Shikshak AI, Architecture diagram, Backend (`apps/api/requirements.txt`), Environment variables, Error handling strategy, Frontend (`apps/web/package.json` — key deps), Full folder/file structure, Package list (+5 more)

### Community 62 - "06 — Implementation Plan — Shikshak AI"
Cohesion: 0.17
Nodes (12): 06 — Implementation Plan — Shikshak AI, Common failure points to pre-empt, Deployment checklist, Phase 0 — Scaffolding (no AI logic yet), Phase 1 — Core teaching logic (text-only, no video), Phase 2 — Interactivity and assessment (still no video), Phase 3 — Learner memory and curriculum, Phase 4 — Video pipeline (+4 more)

### Community 63 - "universal_diagram.py"
Cohesion: 0.06
Nodes (52): task, Shikshak AI — Voice Synthesis Agent. Single responsibility: take a final…, Return the path to the synthesised audio file., run(), synthesize(), Path, Shikshak AI — TTS synthesis skill (Edge TTS primary, Coqui XTTS-v2 fallback).…, Use Coqui XTTS-v2 for local voice cloning (requires model + reference voice). (+44 more)

### Community 64 - "celery_app.py"
Cohesion: 0.22
Nodes (9): budget_segments(), Any, task, Shikshak AI — Time Budgeting Agent. Single responsibility: ensure the lesson…, run(), task, Shikshak AI — Celery application definition. Independent agents run via…, Used by Phase 0 / docker-compose to confirm the worker is alive. (+1 more)

### Community 65 - "unhandled_exception_handler"
Cohesion: 0.29
Nodes (7): _check_render_rate(), _check_session_rate(), Catch-all → structured {error, agent, retryable} per TRD error strategy., unhandled_exception_handler(), Exception, exception_handler, Request

### Community 66 - "Section Definitions"
Cohesion: 0.20
Nodes (9): 1. Query Performance (query), 2. Connection Management (conn), 3. Security & RLS (security), 4. Schema Design (schema), 5. Concurrency & Locking (lock), 6. Data Access Patterns (data), 7. Monitoring & Diagnostics (monitor), 8. Advanced Features (advanced) (+1 more)

### Community 67 - "04 — UI/UX Design System — Shikshak AI"
Cohesion: 0.08
Nodes (24): 04 — UI/UX Design System — Shikshak AI, Accessibility, Brand & accent, Breakpoints (unchanged from source), Buttons, Cards, Colors, Components (+16 more)

### Community 68 - "00 — MASTER PROMPT — Shikshak AI (AI Teacher)"
Cohesion: 0.25
Nodes (8): 00 — MASTER PROMPT — Shikshak AI (AI Teacher), Agent operating rules, Build command sequence, Definition of Done, Documents in this suite, in reading order, Full folder structure, Project summary, Tech stack (one line each)

### Community 69 - "language.py"
Cohesion: 0.25
Nodes (9): apply_language(), Any, task, Shikshak AI — Language Agent. Single responsibility: ensure the narration…, Translate narration scripts in the plan from `current_language` to…, run(), Shikshak AI — translation skill. Lightweight wrapper for language switching…, Translate `text` into `target_language` (BCP-47 like 'hi' or 'en'). Falls back… (+1 more)

### Community 70 - "VisualBrief"
Cohesion: 0.16
Nodes (15): Path, Minimal contract for a concept animation request., Render a video for the brief to `out_path`. Return the path., VisualBrief, Path, _BrokenProvider, Path, Regression tests for the diagram-first video pipeline contracts. (+7 more)

### Community 71 - "Supabase Postgres Best Practices"
Cohesion: 0.33
Nodes (5): How to Use, References, Rule Categories by Priority, Supabase Postgres Best Practices, When to Apply

### Community 72 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, start, test

### Community 74 - "web/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 75 - "get_video_stream"
Cohesion: 0.67
Nodes (3): api_route, get_video_stream(), Stream locally rendered MP4 video files to the browser.

### Community 116 - "concept_graph.py"
Cohesion: 0.23
Nodes (11): build_concept_graph(), ConceptGraph, ConceptNode, get_concept_graph_dict(), Any, BaseModel, Shikshak AI — Concept Graph Builder skill. Given a main topic and current…, Generate a concept map of related topics for the given concept. (+3 more)

### Community 118 - "generate_with_fallback"
Cohesion: 0.27
Nodes (9): animate_segment(), Any, task, Shikshak AI — Concept Animation Agent. Single responsibility: take a segment's…, Return {video_path, provider}., run(), generate_with_fallback(), Path (+1 more)

### Community 119 - "CinematicProvider"
Cohesion: 0.33
Nodes (6): CinematicProvider, Path, Generate a cinematic concept animation video., Fetch a high-quality educational illustration from Pollinations AI., Create a clean dark gradient canvas as fallback., Apply smooth Ken Burns motion (gentle pan + zoom) with title overlay.

### Community 120 - "explanation.py"
Cohesion: 0.36
Nodes (7): explain_segment(), _format_chunks(), task, Shikshak AI — Explanation Agent. Single responsibility: given a segment brief +…, Return the final narration script text for one segment., run(), _truncate_to_word_target()

### Community 121 - "flow_cache_provider.py"
Cohesion: 0.32
Nodes (5): get_cached_video(), FlowCacheProvider, _hash_brief(), Path, Shikshak AI — cached Flow clips provider (alternate). Serves pre-generated…

### Community 122 - ".generate"
Cohesion: 0.32
Nodes (7): _build_scene_script(), _find_rendered_video(), Path, Render a Manim scene for the given concept., Last-resort: tiny valid mp4 placeholder., Generate the source code for a Manim Scene describing this concept., _write_placeholder_video()

### Community 123 - "config.py"
Cohesion: 0.33
Nodes (5): get_settings(), BaseModel, Shikshak AI — Backend configuration. Loads environment variables and exposes…, Cached Settings singleton., Settings

### Community 124 - "03 — App Flow & Screen Specifications — Shikshak AI"
Cohesion: 0.29
Nodes (6): 03 — App Flow & Screen Specifications — Shikshak AI, Global error states, Modals / drawers / sheets, Navigation diagram, Route table, Toast / notification triggers

### Community 125 - "Local setup"
Cohesion: 0.29
Nodes (7): 1. Install dependencies, 2. Configure environment variables, 3. Set up the database, 4. Run the backend, 5. Run the frontend, Local setup, Prerequisites

## Knowledge Gaps
- **311 isolated node(s):** `extends`, `next/core-web-vitals`, `RelatedConcept`, `Tab`, `inter` (+306 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 624 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `VisualBrief` connect `VisualBrief` to `VideoGenerationProvider`, `generate_with_fallback`, `CinematicProvider`, `flow_cache_provider.py`, `.generate`, `universal_diagram.py`, `require_playable_video`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `call_llm_with_retry()` connect `call_llm_with_retry` to `assessment.py`, `supabase_persistence.py`, `concept_graph.py`, `get_llm`, `lesson_planning.py`, `universal_diagram.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `run_session_pipeline()` connect `router.py` to `main.py`, `knowledge_retrieval.py`, `celery_app.py`, `language.py`, `get_session`, `select_visuals`, `content_ingestion.py`, `qa_grounding_guard.py`, `test_integration_phase1_2.py`, `get_llm`, `upload_document`, `learner_profile.py`, `lesson_planning.py`, `explanation.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `VisualBrief` (e.g. with `CinematicProvider` and `DiagramProvider`) actually correct?**
  _`VisualBrief` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `extends`, `next/core-web-vitals`, `RelatedConcept` to the rest of the system?**
  _311 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._