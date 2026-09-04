# Graph Report - shikshak-ai  (2026-08-31)

## Corpus Check
- 212 files · ~139,671 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1536 nodes · 2923 edges · 138 communities (86 shown, 49 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 90 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- assessment.py
- router.py
- dependencies
- devDependencies
- compilerOptions
- VideoGenerationRequest
- supabase_persistence.py
- types.ts
- diagram_engine/renderer.py
- cn
- select_visuals
- lip_sync_rendering.py
- common.py
- call_llm_with_retry
- SQL migrations
- Core features
- dashboard/page.tsx
- new/page.tsx
- [pathId]/page.tsx
- personalize
- interaction.py
- chunking_embedding.py
- toast.tsx
- render_segment
- answer_evaluation.py
- Supabase
- lesson_planning.py
- explain_segment
- Changelog
- circuit_diagram/renderer.py
- test_video_pipeline_contracts.py
- Kit 2 — Circuit Symbol Kit (Electricity chapter)
- llm.py
- Shikshak AI — AI Teacher
- Changelog
- Writing Guidelines for Postgres References
- test_flow_cache_provider.py
- PromptTemplate
- test_science_visual_kits.py
- synthesize_speech
- rdkit_renderer.py
- app-shell.tsx
- SessionPlayerPage
- client.ts
- package.json
- .eslintrc.json
- middleware.ts
- misconception_detection.py
- conftest.py
- Shikshak AI — AI Teacher
- tests/__init__.py
- next.config.mjs
- next-env.d.ts
- postcss.config.mjs
- learner_profile.py
- extract_pdf_structure
- Screen specifications
- 02 — Technical Requirements Document — Shikshak AI
- 06 — Implementation Plan — Shikshak AI
- universal_diagram.py
- test_integration_phase1_2.py
- unhandled_exception_handler
- Section Definitions
- 04 — UI/UX Design System — Shikshak AI
- 00 — MASTER PROMPT — Shikshak AI (AI Teacher)
- language.py
- VisualBrief
- Supabase Postgres Best Practices
- scripts
- content_scriptwriter.py
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
- get_content_llm
- RateLimiter
- generate_with_fallback
- .generate
- explanation.py
- FlowCacheProvider
- .generate
- config.py
- README.md
- Local setup
- diagram_provider.py
- celery_app.py
- SKILL: Diagram Animation Engine (Shikshak AI)
- test_content_scriptwriter.py
- Shikshak AI — Visual Architecture & Dataflow Guide
- text_measure.py
- 01 — Product Requirements Document — Shikshak AI
- Components
- Agent Behavioral & Cognitive Standards
- Colors
- make_prompt_hash
- .is_available

## God Nodes (most connected - your core abstractions)
1. `get_client()` - 39 edges
2. `VisualBrief` - 36 edges
3. `VideoGenerationRequest` - 29 edges
4. `cn()` - 29 edges
5. `VideoGenerationResult` - 25 edges
6. `run_session_pipeline()` - 24 edges
7. `DiagramNode` - 24 edges
8. `call_llm_with_retry()` - 24 edges
9. `VideoGenerationProvider` - 23 edges
10. `ContentBlueprint` - 22 edges

## Surprising Connections (you probably didn't know these)
- `test_fallback_blueprint_structure()` --uses--> `ContentBlueprint`  [INFERRED]
  apps/api/tests/test_content_scriptwriter.py → apps/api/agents/content_scriptwriter.py
- `_callout_node_svg()` --uses--> `PositionedNode`  [INFERRED]
  apps/api/skills/bio_illustration/renderer.py → apps/api/skills/diagram_engine/layout/common.py
- `_fallback()` --uses--> `CircuitDiagramSpec`  [INFERRED]
  apps/api/skills/circuit_diagram/renderer.py → apps/api/skills/circuit_diagram/schemas.py
- `_render_node()` --uses--> `PositionedNode`  [INFERRED]
  apps/api/skills/video_generation/diagram_provider.py → apps/api/skills/diagram_engine/layout/common.py
- `_render_edge()` --uses--> `LayoutResult`  [INFERRED]
  apps/api/skills/video_generation/diagram_provider.py → apps/api/skills/diagram_engine/layout/common.py

## Import Cycles
- None detected.

## Communities (138 total, 49 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.08
Nodes (49): create_learning_path(), _format_video_url(), get_document(), get_learner_profile(), get_learning_path(), get_related_concepts(), get_report(), get_segment_status() (+41 more)

### Community 1 - "assessment.py"
Cohesion: 0.27
Nodes (10): assess_session(), AssessmentPlan, Any, BaseModel, task, Shikshak AI — Assessment Agent. Single responsibility: at the end of a session,…, Produce and persist the assessment report for `session_id`., run() (+2 more)

### Community 2 - "router.py"
Cohesion: 0.12
Nodes (24): generate_deep_dive(), Any, task, Shikshak AI — Deep Dive Generation Agent. Single responsibility: when the user…, Generate a deep-dive segment for the given concept. Returns a segment dict with…, run(), Shikshak AI — agents package. Each agent is a single-responsibility module with…, build_execution_plan() (+16 more)

### Community 3 - "dependencies"
Cohesion: 0.12
Nodes (17): dependencies, clsx, lucide-react, next, react-hook-form, @supabase/ssr, @supabase/supabase-js, typescript (+9 more)

### Community 4 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, autoprefixer, eslint, eslint-config-next, postcss, tailwindcss, @types/node, @types/react (+9 more)

### Community 5 - "compilerOptions"
Cohesion: 0.07
Nodes (26): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+18 more)

### Community 6 - "VideoGenerationRequest"
Cohesion: 0.12
Nodes (28): ABC, Shikshak AI — video generation provider base. Every video provider (FlowCache,…, Every video provider implements this interface., Render or retrieve a video for the request and return a VideoGenerationResult., Request contract for video generation providers., Result returned by video generation providers., VideoGenerationProvider, VideoGenerationRequest (+20 more)

### Community 7 - "supabase_persistence.py"
Cohesion: 0.09
Nodes (38): ingest_document(), _parse(), Any, task, Shikshak AI — Content Ingestion Agent. Single responsibility: take an uploaded…, Synchronous entry point (also called from the FastAPI request handler when the…, Celery task wrapper for the Content Ingestion Agent., run() (+30 more)

### Community 8 - "types.ts"
Cohesion: 0.17
Nodes (15): ApiError, call(), AgentError, CreateSessionRequest, DocumentOut, LearnerProfile, LearningPath, LearningPathItem (+7 more)

### Community 9 - "diagram_engine/renderer.py"
Cohesion: 0.11
Nodes (37): _fallback(), animation_state(), AnimationState, keyframe_times(), ContentBlueprint, Deterministic node/edge animation timing synced to narration duration., audio_duration_ms(), compose_video() (+29 more)

### Community 10 - "cn"
Cohesion: 0.11
Nodes (22): NOTE: The backend auto-creates a checkpoint when a segment has, RelatedConcept, ChapterContents(), ChapterContentsProps, DEPTH_BADGES, LessonPlayer(), LessonPlayerProps, LOADING_MESSAGES (+14 more)

### Community 11 - "select_visuals"
Cohesion: 0.22
Nodes (14): _infer_visual_type(), Any, task, Shikshak AI — Visual Selection Agent. Single responsibility: ensure every…, Walk every segment and upgrade 'none' to a better type if detectable from the…, run(), select_visuals(), Unit tests for agents/visual_selection.py. (+6 more)

### Community 12 - "lip_sync_rendering.py"
Cohesion: 0.23
Nodes (14): Path, Shikshak AI — lip-sync rendering skill (improved Wav2Lip + SadTalker). Uses a…, Use Wav2Lip for fast lip sync (works on CPU/MPS)., Loop a single still frame over the audio duration — 'photo + voice' fallback…, Write a professional-looking placeholder avatar image., Combine the teacher reference image with `audio_path` into a talking avatar…, Resolve the teacher reference image path, falling back to placeholder., Use SadTalker for natural head motion + expression-driven lip sync. SadTalker… (+6 more)

### Community 13 - "common.py"
Cohesion: 0.14
Nodes (31): assert_no_overlaps(), boxes_overlap(), LayoutResult, PositionedEdge, PositionedNode, Shared computed geometry; never part of LLM-facing schemas., layout_comparison(), DiagramSpec (+23 more)

### Community 14 - "call_llm_with_retry"
Cohesion: 0.14
Nodes (23): call_llm_with_retry(), _extract_first_json_object(), Shikshak AI — JSON schema validation skill. Every LLM output that feeds into…, Models sometimes wrap JSON in ```json ... ``` fences — strip them., If the LLM prefixed with prose, find the first { ... } block., Parse raw LLM output into a validated Pydantic instance. Raises ValueError if…, Call llm_fn(prompt) -> raw_str; validate against schema. On failure, retry once…, _strip_code_fences() (+15 more)

### Community 15 - "SQL migrations"
Cohesion: 0.08
Nodes (25): `001_learner_profiles.sql`, `002_documents.sql`, `003_document_chunks.sql`, `004_sessions.sql`, `005_lesson_segments.sql`, `006_question_checkpoints.sql`, `007_assessment_reports.sql`, `008_learning_paths.sql` (+17 more)

### Community 16 - "Core features"
Cohesion: 0.18
Nodes (11): 10. Persistent learner profile and learning paths, 1. Document-grounded learning (RAG), 2. Topic-based learning (no upload required), 3. Personalized depth and style, 4. Time-adaptive lesson structuring, 5. Multilingual teaching with mid-lesson switching, 6. Human-like AI teaching video, 7. Interactive questioning during the lesson (+3 more)

### Community 17 - "dashboard/page.tsx"
Cohesion: 0.26
Nodes (6): SessionCard(), subjectLabel(), Badge(), BadgeProps, formatRelativeDate(), subjectColor()

### Community 18 - "new/page.tsx"
Cohesion: 0.16
Nodes (12): DashboardPage(), LearningPathPage(), NewSessionPage(), Tab, ReportPage(), FileDropzone(), Select, TextInput (+4 more)

### Community 19 - "[pathId]/page.tsx"
Cohesion: 0.23
Nodes (11): ReportBand(), ScoreCard(), Button, ButtonProps, ButtonVariant, VARIANT_CLASS, Card(), CardBody() (+3 more)

### Community 20 - "personalize"
Cohesion: 0.38
Nodes (6): personalize(), Any, task, Shikshak AI — Personalization Agent. Single responsibility: given a lesson plan…, Rewrite segment depths to match `level`, and prepend one remediation segment…, run()

### Community 21 - "interaction.py"
Cohesion: 0.23
Nodes (10): generate_checkpoint(), Any, BaseModel, task, QuestionObject, Shikshak AI — Interaction Agent. Single responsibility: generate checkpoint…, Return a persisted checkpoint row for the segment., run() (+2 more)

### Community 22 - "chunking_embedding.py"
Cohesion: 0.08
Nodes (33): Any, task, Shikshak AI — Knowledge Retrieval Agent. Single responsibility: given a…, Return top_k chunks for the query. If document_id is None (topic-only mode),…, retrieve(), run(), chunk_pages(), _embed_gemini() (+25 more)

### Community 23 - "toast.tsx"
Cohesion: 0.18
Nodes (9): inter, metadata, BORDER_COLOR, ToastContext, ToastContextValue, ToastKind, ToastProvider(), ToastState (+1 more)

### Community 24 - "render_segment"
Cohesion: 0.15
Nodes (13): create_session(), generate_next_segment(), NextSegmentRequest, BaseModel, Upload a PDF/DOCX/PPTX source document. Triggers Content Ingestion Agent., Create a new teaching session. Triggers the Orchestrator → agent DAG., Generate a deep-dive segment for a related concept. If selected_concept is…, Trigger the video pipeline for a single segment. Runs: Voice Synthesis →… (+5 more)

### Community 25 - "answer_evaluation.py"
Cohesion: 0.36
Nodes (7): evaluate_answer(), Any, task, Shikshak AI — Answer Evaluation Agent. Single responsibility: given a…, Grade a student's answer against the checkpoint's correct answer., run(), get_checkpoint()

### Community 26 - "Supabase"
Cohesion: 0.11
Nodes (15): Fix suggestion, Source, What happened, Skill Feedback, Steps, Core Principles, Debugging, Making and Committing Schema Changes (+7 more)

### Community 27 - "lesson_planning.py"
Cohesion: 0.10
Nodes (30): LessonPlan, plan_lesson(), Any, BaseModel, task, Shikshak AI — Lesson Planning Agent (v3). Two modes: document mode: uses…, Return a validated lesson plan as a dict. When pdf_structure is provided…, run() (+22 more)

### Community 28 - "explain_segment"
Cohesion: 0.25
Nodes (10): explain_segment(), Return narration script string for backward compatibility. Used by callers that…, _find_unsupported_claims(), guard(), Any, task, Shikshak AI — QA Grounding Guard Agent. Single responsibility: check…, Return {narration_script, flagged_claims, regenerated}. If narration_script… (+2 more)

### Community 29 - "Changelog"
Cohesion: 0.12
Nodes (16): [1.2.0](https://github.com/supabase/agent-skills/compare/v1.1.1...v1.2.0) (2026-06-02), [1.3.0](https://github.com/supabase/agent-skills/compare/v1.2.0...v1.3.0) (2026-06-05), [1.4.0](https://github.com/supabase/agent-skills/compare/v1.3.0...v1.4.0) (2026-07-10), [1.5.0](https://github.com/supabase/agent-skills/compare/supabase-postgres-best-practices-v1.4.0...supabase-postgres-best-practices-v1.5.0) (2026-07-30), [1.6.0](https://github.com/supabase/agent-skills/compare/supabase-postgres-best-practices-v1.5.0...supabase-postgres-best-practices-v1.6.0) (2026-07-30), Bug Fixes, Bug Fixes, Bug Fixes (+8 more)

### Community 30 - "circuit_diagram/renderer.py"
Cohesion: 0.15
Nodes (28): current_flow_dash_offset(), current_flow_direction(), Deterministic current-flow timing for circuit SVG frames., Layouts encode wires clockwise/left-to-right, the convention used in render., Negative offset moves dashed current clockwise along each stored wire path., IEC-symbol circuit diagrams routed outside generative video providers., assert_no_symbol_overlap(), CircuitLayout (+20 more)

### Community 31 - "test_video_pipeline_contracts.py"
Cohesion: 0.06
Nodes (45): composite_lesson(), composite_lesson_task(), composite_segment(), composite_segment_task(), task, Shikshak AI — Video Compositing Agent. Single responsibility: combine avatar +…, Return the final per-segment video path., Stitch all per-segment videos into one final lesson video. (+37 more)

### Community 32 - "Kit 2 — Circuit Symbol Kit (Electricity chapter)"
Cohesion: 0.07
Nodes (26): Acceptance tests, Directory, Directory, Directory, Input contract, Input contract, Input contract, Kit 1 — Molecular Structure Kit (RDKit) (+18 more)

### Community 33 - "llm.py"
Cohesion: 0.14
Nodes (21): _extract_topic_from_prompt(), gemini_llm(), get_animation_llm(), get_fast_llm(), get_request_counts(), groq_llm(), Shared LLM caller helpers used by every agent. Dual-provider architecture: -…, Call Groq with a text prompt; return the raw text response. Automatically tries… (+13 more)

### Community 34 - "Shikshak AI — AI Teacher"
Cohesion: 0.20
Nodes (10): Asset placeholders, Documentation, Known limitations, License, Monorepo layout, Running tests, Shikshak AI — AI Teacher, Tech stack (+2 more)

### Community 35 - "Changelog"
Cohesion: 0.12
Nodes (15): [0.1.3](https://github.com/supabase/agent-skills/compare/v0.1.2...v0.1.3) (2026-06-02), [0.1.4](https://github.com/supabase/agent-skills/compare/v0.1.3...v0.1.4) (2026-06-05), [0.1.5](https://github.com/supabase/agent-skills/compare/v0.1.4...v0.1.5) (2026-07-10), [0.1.6](https://github.com/supabase/agent-skills/compare/v0.1.5...supabase-v0.1.6) (2026-07-30), [0.1.7](https://github.com/supabase/agent-skills/compare/v0.1.6...supabase-v0.1.7) (2026-08-12), Bug Fixes, Bug Fixes, Bug Fixes (+7 more)

### Community 36 - "Writing Guidelines for Postgres References"
Cohesion: 0.12
Nodes (15): 1. Concrete Transformation Patterns, 2. Error-First Structure, 3. Quantified Impact, 4. Self-Contained Examples, 5. Semantic Naming, Code Example Standards, Comments, Impact Level Guidelines (+7 more)

### Community 37 - "test_flow_cache_provider.py"
Cohesion: 0.09
Nodes (29): get_supabase_client(), main(), populate_video_cache(), Path, build_cache_prompt(), cached_or_compute(), hash_prompt(), Shikshak AI — caching skill. Hashes (prompt, provider, params) into a stable… (+21 more)

### Community 38 - "PromptTemplate"
Cohesion: 0.40
Nodes (3): PromptTemplate, Any, Simple Jinja-like template — no external dependency, escapes nothing, but…

### Community 39 - "test_science_visual_kits.py"
Cohesion: 0.19
Nodes (19): Manifest of curated biological illustration vector assets., _asset_uri(), _callout_node_svg(), _generic_fallback(), Path, Biological illustration renderer combining BioIcons vector assets with cross-…, Render a biological illustration with satellite callouts to PNG bytes., Fallback to generic cross_section layout with plain labeled boxes. (+11 more)

### Community 40 - "synthesize_speech"
Cohesion: 0.15
Nodes (19): task, Shikshak AI — Voice Synthesis Agent. Single responsibility: take a final…, Return the path to the synthesised audio file., run(), synthesize(), Path, Shikshak AI — TTS synthesis skill (Edge TTS primary, Coqui XTTS-v2 fallback).…, Use Coqui XTTS-v2 for local voice cloning (requires model + reference voice). (+11 more)

### Community 41 - "rdkit_renderer.py"
Cohesion: 0.16
Nodes (16): Resolve teacher-friendly bond labels to deterministic RDKit bond indices., resolve_bond_indices(), Locked NCERT compound-name to SMILES lookup; no runtime name resolution., Scientifically accurate, local RDKit molecular diagrams., _generic_fallback(), RDKit 2D structure renderer using Diagram Engine style tokens., Plain labeled box fallback for unknown compounds, never a network call., render_molecular_diagram() (+8 more)

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

### Community 48 - "misconception_detection.py"
Cohesion: 0.15
Nodes (17): diagnose_and_reteach(), Any, BaseModel, task, Shikshak AI — Misconception Detection Agent. Single responsibility: when an…, Returns a re-teach segment the orchestrator will splice in next., ReExplanation, run() (+9 more)

### Community 50 - "Shikshak AI — AI Teacher"
Cohesion: 0.12
Nodes (15): 1. Clone and install, 2. Configure environment variables, 3. Set up the database, 4. Run the backend, 5. Run the frontend, Documentation, Known limitations, License (+7 more)

### Community 58 - "learner_profile.py"
Cohesion: 0.30
Nodes (11): Any, task, Shikshak AI — Learner Profile Agent. Single responsibility: read and update the…, Return the student's profile, creating an empty one if absent., At session end, merge the report's strong/weak areas into the profile, add the…, read_profile(), read_task(), update_profile_from_report() (+3 more)

### Community 59 - "extract_pdf_structure"
Cohesion: 0.15
Nodes (19): _annotate_spans(), _dominant_font_size(), _extract_page_blocks(), extract_pdf_structure(), _extract_toc(), _group_into_sections(), _heading_level(), _is_heading() (+11 more)

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
Cohesion: 0.12
Nodes (30): DiagramEdge, DiagramNode, DiagramSpec, _ease_in_out(), _edge_svg(), _empty_frame_svg(), _fallback_spec(), _layout_positions() (+22 more)

### Community 64 - "test_integration_phase1_2.py"
Cohesion: 0.27
Nodes (8): budget_segments(), Any, task, Shikshak AI — Time Budgeting Agent. Single responsibility: ensure the lesson…, run(), Integration test: full Phase 1 + Phase 2 checkpoint flow via API calls. Per…, End-to-end: topic → plan → personalize → budget → visuals → explain →…, test_phase1_phase2_pipeline_topic_only()

### Community 65 - "unhandled_exception_handler"
Cohesion: 0.29
Nodes (7): _check_render_rate(), _check_session_rate(), Exception, Catch-all → structured {error, agent, retryable} per TRD error strategy., unhandled_exception_handler(), exception_handler, Request

### Community 66 - "Section Definitions"
Cohesion: 0.20
Nodes (9): 1. Query Performance (query), 2. Connection Management (conn), 3. Security & RLS (security), 4. Schema Design (schema), 5. Concurrency & Locking (lock), 6. Data Access Patterns (data), 7. Monitoring & Diagnostics (monitor), 8. Advanced Features (advanced) (+1 more)

### Community 67 - "04 — UI/UX Design System — Shikshak AI"
Cohesion: 0.22
Nodes (9): 04 — UI/UX Design System — Shikshak AI, Accessibility, Breakpoints (unchanged from source), CSS variables (paste into `globals.css`), Design philosophy, Elevation, Layout, Shapes (+1 more)

### Community 68 - "00 — MASTER PROMPT — Shikshak AI (AI Teacher)"
Cohesion: 0.22
Nodes (8): 00 — MASTER PROMPT — Shikshak AI (AI Teacher), Agent operating rules, Build command sequence, Definition of Done, Documents in this suite, in reading order, Full folder structure, Project summary, Tech stack (one line each)

### Community 69 - "language.py"
Cohesion: 0.25
Nodes (9): apply_language(), Any, task, Shikshak AI — Language Agent. Single responsibility: ensure the narration…, Translate narration scripts in the plan from `current_language` to…, run(), Shikshak AI — translation skill. Lightweight wrapper for language switching…, Translate `text` into `target_language` (BCP-47 like 'hi' or 'en'). Falls back… (+1 more)

### Community 70 - "VisualBrief"
Cohesion: 0.22
Nodes (11): Legacy visual brief contract maintained for backwards compatibility., VisualBrief, Verify DiagramProvider renders video directly from pre-computed spec (no LLM)., test_deterministic_diagram_render_with_precomputed_spec(), _BrokenProvider, Path, A returned path is not success until its media stream is validated., The planned visual should cover the spoken narration, not a fixed 15s. (+3 more)

### Community 71 - "Supabase Postgres Best Practices"
Cohesion: 0.33
Nodes (5): How to Use, References, Rule Categories by Priority, Supabase Postgres Best Practices, When to Apply

### Community 72 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, start, test

### Community 73 - "content_scriptwriter.py"
Cohesion: 0.20
Nodes (18): _build_diagram_from_scenes(), ContentBlueprint, DiagramSpecBlueprint, _extract_narration_from_scenes(), _fallback_blueprint(), generate_content_blueprint(), BaseModel, Shikshak AI — Content Scriptwriter Agent (v3). Generates a **single unified… (+10 more)

### Community 74 - "web/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 75 - "get_video_stream"
Cohesion: 0.67
Nodes (3): api_route, get_video_stream(), Stream locally rendered MP4 video files to the browser.

### Community 116 - "get_content_llm"
Cohesion: 0.16
Nodes (17): _grade(), Heuristic grader: case-insensitive match for MCQ (letter or value) and…, get_content_llm(), get_llm(), Return the configured primary LLM callable (Groq by default for content)., Return the LLM for content/orchestration work. This handles: lesson planning,…, build_concept_graph(), ConceptGraph (+9 more)

### Community 118 - "generate_with_fallback"
Cohesion: 0.27
Nodes (9): animate_segment(), Any, task, Shikshak AI — Concept Animation Agent. Single responsibility: take a segment's…, Return {video_path, video_url, provider, cache_hit, video_cache_id}. Args:…, run(), generate_with_fallback(), Path (+1 more)

### Community 119 - ".generate"
Cohesion: 0.31
Nodes (5): Path, Create a clean dark gradient canvas as fallback., Apply smooth Ken Burns motion (gentle pan + zoom) with title overlay., Generate a cinematic concept animation video., Fetch a high-quality educational illustration from Pollinations AI.

### Community 120 - "explanation.py"
Cohesion: 0.20
Nodes (11): explain_segment_narration_only(), explain_segment_with_blueprint(), _format_chunks(), Any, task, Shikshak AI — Explanation Agent (v2). Uses the unified ContentBlueprint from…, Celery task — returns narration script only for backward compat., Return narration script AND diagram spec for one segment. Returns: dict with… (+3 more)

### Community 121 - "FlowCacheProvider"
Cohesion: 0.21
Nodes (7): Exception, Typed error raised when a video generation provider fails., VideoGenerationError, FlowCacheProvider, Any, Shikshak AI — Flow Cache Video Provider. Serves pre-generated clips manually…, Lookup-only provider that retrieves pre-cached Google Flow clips from Supabase.

### Community 122 - ".generate"
Cohesion: 0.32
Nodes (7): _build_scene_script(), _find_rendered_video(), Path, Last-resort: tiny valid mp4 placeholder., Generate the source code for a Manim Scene describing this concept., Render a Manim scene for the given concept., _write_placeholder_video()

### Community 123 - "config.py"
Cohesion: 0.33
Nodes (5): get_settings(), BaseModel, Shikshak AI — Backend configuration. Loads environment variables and exposes…, Cached Settings singleton., Settings

### Community 124 - "README.md"
Cohesion: 0.17
Nodes (6): 03 — App Flow & Screen Specifications — Shikshak AI, Global error states, Modals / drawers / sheets, Navigation diagram, Route table, Toast / notification triggers

### Community 125 - "Local setup"
Cohesion: 0.29
Nodes (7): 1. Install dependencies, 2. Configure environment variables, 3. Set up the database, 4. Run the backend, 5. Run the frontend, Local setup, Prerequisites

### Community 126 - "diagram_provider.py"
Cohesion: 0.20
Nodes (14): center(), _brief_to_blueprint(), _detect_bio_structure(), _detect_compound(), _extract_nodes_from_brief(), ContentBlueprint, DiagramNode, DiagramSpec (+6 more)

### Community 127 - "celery_app.py"
Cohesion: 0.20
Nodes (9): task, Shikshak AI — Avatar Rendering Agent. Single responsibility: take the…, Return the path to the rendered avatar video file., render(), run(), task, Shikshak AI — Celery application definition. Independent agents run via…, Used by Phase 0 / docker-compose to confirm the worker is alive. (+1 more)

### Community 128 - "SKILL: Diagram Animation Engine (Shikshak AI)"
Cohesion: 0.18
Nodes (10): Acceptance tests for this skill, Directory structure, Input contract: `ContentBlueprint`, Layout templates (fixed algorithms, not LLM-improvised), Pipeline (zero LLM calls at render time), Purpose, Section 5 — Where generative video (LTX-Video / CogVideoX) fits, and where it explicitly does not, SKILL: Diagram Animation Engine (Shikshak AI) (+2 more)

### Community 129 - "test_content_scriptwriter.py"
Cohesion: 0.20
Nodes (9): Test suite for Content Scriptwriter agent and the Dual-Output Video Pipeline.…, Verify narration script can be synthesized to audio (Output 1 pipeline)., Verify fallback blueprint generates aligned narration and diagram spec., Verify explain_segment_with_blueprint returns dual outputs., Verify legacy explain_segment returns str narration., test_dual_output_narration_and_audio(), test_explain_segment_backward_compat(), test_explain_segment_with_blueprint() (+1 more)

### Community 130 - "Shikshak AI — Visual Architecture & Dataflow Guide"
Cohesion: 0.20
Nodes (9): 1. Quick Mental Model (The 30-Second View), 2. Complete Visual System Architecture, 3. Step-by-Step Dataflow (Box-by-Box), 4. Why There Is Zero Content-Video Mismatch, 5. The Dual-LLM Routing Shield (No More Rate Limits), 6. Interactive Checkpoint & Reteach Flow, 7. Database Entity Box Diagram, 8. Summary of Benefits (+1 more)

### Community 131 - "text_measure.py"
Cohesion: 0.33
Nodes (8): get_font(), measure_text(), MeasuredText, Measured text geometry used by every deterministic diagram layout., Use a stable system font when Inter is not installed on the renderer., _wrap(), FreeTypeFont, ImageFont

### Community 132 - "01 — Product Requirements Document — Shikshak AI"
Cohesion: 0.22
Nodes (9): 01 — Product Requirements Document — Shikshak AI, App name & tagline, Elevator pitch, Nice-to-have features (v2), Non-goals, Problem statement, Success metrics, Target personas (+1 more)

### Community 133 - "Components"
Cohesion: 0.25
Nodes (8): Buttons, Cards, Components, Inputs, Loading skeletons, Navigation, Signature components (new, specific to Shikshak AI), Toast/alert

### Community 134 - "Agent Behavioral & Cognitive Standards"
Cohesion: 0.29
Nodes (6): 1. Operating Mindset & Epistemic Rigor, 2. Communication & Output Discipline, 3. Precision Code Operations & Execution, 4. Context Integration & Memory Discipline, 5. Security & Safety Integrity, Agent Behavioral & Cognitive Standards

### Community 135 - "Colors"
Cohesion: 0.29
Nodes (7): Brand & accent, Colors, Lesson Player exception, Semantic (added for this product — the source design system has none, so we define our own, kept separate from the sticker/subject palette), Subject color-coding (repurposed sticker palette — functional, not decorative), Surface, Text

### Community 136 - "make_prompt_hash"
Cohesion: 0.67
Nodes (3): make_prompt_hash(), Any, Return a 16-char hash of any tuple of JSON-serialisable inputs.

## Knowledge Gaps
- **355 isolated node(s):** `extends`, `next/core-web-vitals`, `RelatedConcept`, `Tab`, `inter` (+350 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 802 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_session_pipeline()` connect `router.py` to `main.py`, `test_integration_phase1_2.py`, `language.py`, `supabase_persistence.py`, `select_visuals`, `explain_segment`, `personalize`, `interaction.py`, `chunking_embedding.py`, `render_segment`, `learner_profile.py`, `lesson_planning.py`, `explanation.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `VisualBrief` connect `VisualBrief` to `test_content_scriptwriter.py`, `test_flow_cache_provider.py`, `VideoGenerationRequest`, `generate_with_fallback`, `.generate`, `FlowCacheProvider`, `.generate`, `test_video_pipeline_contracts.py`, `diagram_provider.py`, `universal_diagram.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `call_llm_with_retry()` connect `call_llm_with_retry` to `assessment.py`, `llm.py`, `supabase_persistence.py`, `content_scriptwriter.py`, `misconception_detection.py`, `get_content_llm`, `interaction.py`, `lesson_planning.py`, `universal_diagram.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `VisualBrief` (e.g. with `CinematicProvider` and `_brief_to_blueprint()`) actually correct?**
  _`VisualBrief` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `VideoGenerationRequest` (e.g. with `CinematicProvider` and `DiagramProvider`) actually correct?**
  _`VideoGenerationRequest` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `VideoGenerationResult` (e.g. with `CinematicProvider` and `DiagramProvider`) actually correct?**
  _`VideoGenerationResult` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `extends`, `next/core-web-vitals`, `RelatedConcept` to the rest of the system?**
  _355 weakly-connected nodes found - possible documentation gaps or missing edges._