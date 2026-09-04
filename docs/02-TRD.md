# 02 — Technical Requirements Document — Shikshak AI

## Tech stack

| Layer | Choice | Version | Justification |
|---|---|---|---|
| Frontend framework | Next.js | 15.x (App Router) | Team familiarity, free Vercel hosting, server components for fast initial load |
| Language | TypeScript | 5.x strict | Type safety across a large, agent-heavy API surface |
| Styling | Tailwind CSS + shadcn/ui | Tailwind v4 | Matches `04-UI-UX-BRIEF.md` token system directly |
| Backend framework | FastAPI | 0.115.x | Async-native, plays well with Celery, matches team's default stack |
| Task queue | Celery + Redis | Celery 5.4.x, Redis 7.x | Required for parallel/sequential agent orchestration (see agent architecture doc) |
| Database | Supabase Postgres + pgvector | Postgres 15, pgvector 0.7.x | Free tier sufficient for hackathon scale; pgvector avoids a separate vector DB |
| File/object storage | Supabase Storage | — | Documents, generated audio, avatar clips, final videos |
| Auth | Supabase Auth | — | Email + Google OAuth, free tier |
| Primary LLM | Gemini 2.0/2.5 Flash | via AI Studio API | Free tier, strong structured JSON output, good multilingual support |
| Fast-turn LLM | Groq (Llama 3.3 70B) | via Groq API | Low latency for the interactive Q&A loop |
| Embeddings | `text-embedding-004` or `bge-small-en` | — | Free tier / fully local fallback |
| TTS | Coqui XTTS-v2 | self-hosted | Free, voice cloning, multilingual, consistent voice identity |
| Avatar lip-sync | Wav2Lip (SadTalker optional) | self-hosted | Free, reliable on CPU/MPS, no GPU dependency |
| Concept animation | Manim (default) / Wan2.1-ZeroGPU / cached Flow clips | swappable via provider interface | Zero-cost deterministic default; generative upgrade path optional |
| Video assembly | ffmpeg + Remotion | — | Free, local, CPU-only |
| Hosting | Vercel (frontend), Render/Railway free tier or local tunnel (backend) | — | Zero-cost hosting for a hackathon demo |

## Architecture diagram

```
                         +----------------------+
                         |   Next.js Frontend   |
                         |  (Vercel, TS/Tailwind)|
                         +----------+-----------+
                                    | REST (typed fetch)
                                    v
                         +----------------------+
                         |   FastAPI Backend    |
                         |  /api/v1/* endpoints |
                         +----------+-----------+
                                    | dispatches
                                    v
                         +----------------------+
                         | Orchestrator Agent   |
                         | (builds execution DAG)|
                         +----------+-----------+
                                    |
                +-------------------+-------------------+
                |                                       |
                v                                       v
     +---------------------+                 +---------------------+
     |  Celery group()     |                 |  Celery chain()     |
     |  (parallel agents)  |                 |  (sequential agents)|
     +----------+----------+                 +----------+----------+
                |                                       |
                +-------------------+-------------------+
                                    v
                         +----------------------+
                         |   20 Agents (see     |
                         | AI-TEACHER-AGENT-    |
                         | ARCHITECTURE.md)     |
                         +----------+-----------+
                                    | call
                                    v
                         +----------------------+
                         |   16 Skills modules   |
                         | (parsing, RAG, TTS,   |
                         |  video, persistence)  |
                         +----------+-----------+
                                    |
                +-------------------+-------------------+
                v                   v                   v
      +----------------+  +----------------+  +------------------+
      | Supabase        |  | Redis          |  | External LLM /   |
      | Postgres+pgvector|  | (Celery broker,|  | TTS / video APIs |
      | + Storage        |  |  result cache) |  | (Gemini, Groq,   |
      +----------------+  +----------------+  | HF Spaces)        |
                                               +------------------+
```

## Full folder/file structure

See `00-MASTER-PROMPT.md` for the complete tree — it is the canonical copy, referenced here rather than duplicated to avoid drift.

## Package list

### Backend (`apps/api/requirements.txt`)
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
celery==5.4.0
redis==5.0.8
supabase==2.7.4
pydantic==2.9.2
python-multipart==0.0.9
pymupdf==1.24.10          # PDF parsing
python-docx==1.1.2        # DOCX parsing
python-pptx==0.6.23       # PPTX parsing
google-generativeai==0.8.1 # Gemini
groq==0.11.0
sentence-transformers==3.1.1  # local embeddings fallback
TTS==0.22.0                # Coqui XTTS-v2
ffmpeg-python==0.2.0
gradio-client==1.4.0       # HF Spaces (Wan2.1) fallback provider
manim==0.18.1
python-dotenv==1.0.1
```

### Frontend (`apps/web/package.json` — key deps)
```
next@15.0.0
react@18.3.1
typescript@5.6.2
tailwindcss@4.0.0
@supabase/supabase-js@2.45.4
@supabase/ssr@0.5.1
zustand@4.5.5
@tanstack/react-query@5.56.2
react-hook-form@7.53.0
zod@3.23.8
lucide-react@0.445.0
```

## Environment variables

| Variable | Type | Example | Used by |
|---|---|---|---|
| `SUPABASE_URL` | string | `https://xxxx.supabase.co` | frontend + backend |
| `SUPABASE_ANON_KEY` | string | `eyJ...` | frontend |
| `SUPABASE_SERVICE_ROLE_KEY` | string | `eyJ...` | backend only, never exposed to client |
| `GEMINI_API_KEY` | string | `AIza...` | backend (LLM agents) |
| `GROQ_API_KEY` | string | `gsk_...` | backend (interaction-loop agents) |
| `HF_TOKEN` | string | `hf_...` | backend (Wan2.1 ZeroGPU provider, logged-in quota) |
| `REDIS_URL` | string | `redis://localhost:6379/0` | backend (Celery broker) |
| `VIDEO_PROVIDER` | string enum | `manim` \| `wan_zerogpu` \| `flow_cache` | `skills/video_generation/factory.py` |
| `XTTS_MODEL_PATH` | string | `./models/xtts_v2` | TTS skill |
| `TEACHER_REFERENCE_IMAGE` | string | `./assets/teacher_ref.png` | avatar rendering skill (locked identity) |
| `TEACHER_REFERENCE_VOICE` | string | `./assets/teacher_voice.wav` | TTS skill (locked voice) |
| `NEXT_PUBLIC_API_BASE_URL` | string | `http://localhost:8000` | frontend fetch wrapper |

## Third-party API integrations

| Service | Endpoint used | Auth | Request shape | Response shape |
|---|---|---|---|---|
| Gemini | `generateContent` (2.0/2.5 Flash) | API key header | `{contents, generationConfig: {responseMimeType: "application/json"}}` | `{candidates: [{content: {parts: [{text}]}}]}` |
| Groq | `/openai/v1/chat/completions` | Bearer token | OpenAI-compatible chat body | OpenAI-compatible chat completion |
| HF Wan2.1 Space | `gradio_client.submit(...)` | `HF_TOKEN` (logged-in for higher quota) | prompt, negative_prompt, size, steps | job -> `.result()` video path |
| Supabase | REST/Postgres client | anon/service key | table-specific | table-specific |

## TypeScript interfaces (frontend, mirrors backend Pydantic models)

```typescript
interface LessonSegment {
  id: string;
  order: number;
  concept: string;
  depth: "beginner" | "intermediate" | "advanced";
  visualType: "diagram" | "equation" | "code" | "animation" | "none";
  narrationScript: string;
  videoUrl: string | null;
  hasCheckpoint: boolean;
}

interface Session {
  id: string;
  studentId: string;
  sourceType: "document" | "topic";
  documentId: string | null;
  topic: string | null;
  level: "beginner" | "intermediate" | "advanced";
  language: string;          // BCP-47, e.g. "hi", "en", "hi-Latn" for Hinglish
  timeBudgetMinutes: number;
  status: "planning" | "in_progress" | "completed";
  segments: LessonSegment[];
  createdAt: string;
}

interface QuestionCheckpoint {
  id: string;
  segmentId: string;
  type: "mcq" | "short_answer" | "conceptual";
  prompt: string;
  options: string[] | null;
  studentAnswer: string | null;
  isCorrect: boolean | null;
  misconception: string | null;
}

interface AssessmentReport {
  sessionId: string;
  score: number;             // 0-100
  strongAreas: string[];
  weakAreas: string[];
  recommendation: string;
}

interface LearnerProfile {
  studentId: string;
  topicsStudied: string[];
  weakConcepts: string[];
  strongConcepts: string[];
  averageScore: number;
}
```

## Error handling strategy

| Layer | Failure mode | Handling |
|---|---|---|
| Frontend | API request fails/times out | React Query retry (2x, exponential backoff), then a toast + inline retry button; never a blank screen |
| FastAPI | Agent raises an exception | Caught at the orchestrator level, logged with the agent name + input hash, returns a structured `{error, agent, retryable}` to the client |
| Celery | Task times out (e.g. video generation) | Hard timeout per task (see below), automatic fallback to the next provider in `video_generation/factory.py` |
| LLM call | Malformed/non-JSON output | `json_schema_validation` skill retries the same call once with a stricter "return only valid JSON" instruction before failing the agent |
| Video provider | ZeroGPU quota exhausted / Space down | Falls back to `ManimProvider` automatically; student never sees a raw provider error |
| Database | Supabase write conflict/timeout | Retried once with exponential backoff; surfaced as a toast if it still fails |

## Performance requirements

- Text-only agent chain (ingestion -> retrieval -> planning -> explanation) responds within 15 seconds for a live demo.
- Video generation for a single segment (Manim path) completes within 60 seconds; ZeroGPU path has a 4-minute hard timeout before automatic fallback.
- Frontend lesson player must show a loading skeleton, never a blank white screen, for any state waiting on backend generation.

## Security checklist

- [ ] Supabase Row Level Security enabled on every table containing student data — a student can only read/write their own rows.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` never sent to the frontend; only used server-side in FastAPI.
- [ ] Uploaded documents scanned for file type/size limits before parsing (max 25MB, PDF/DOCX/PPTX only).
- [ ] All LLM prompts that embed user-uploaded content are constructed via the `prompt_templating` skill, not raw string concatenation, to reduce prompt-injection risk from malicious document content.
- [ ] Rate limiting on session-creation and video-generation endpoints to protect free-tier API quotas (Gemini, Groq, HF ZeroGPU) from being exhausted by repeated calls.
