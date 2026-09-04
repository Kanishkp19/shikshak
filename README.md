# Shikshak AI — AI Teacher

Human-like AI educator that teaches through personalized, interactive video
lessons — grounded in your own uploaded material or any topic, adapted to your
level, time, and language.

Built for the AI Innovation Hackathon 2026 (Bharat Academix, Round 2).

## What this is

A student uploads a book/PDF/notes/slides, or just names a topic. The system
plans a lesson, personalizes it to the student's level and available time,
generates an actual teaching video (lip-synced avatar + voice + subject-
appropriate diagrams/animations), pauses to ask questions during the lesson,
diagnoses and re-teaches misconceptions when the student gets something wrong,
and ends with a scored report and a recommendation — remembering weak areas
for next time.

## Monorepo layout

```
shikshak-ai/
├── apps/
│   ├── web/          # Next.js 15 frontend (App Router, TS strict, Tailwind v4)
│   └── api/          # FastAPI backend (Celery + Redis + 20 agents + 16 skills)
├── supabase/
│   └── migrations/  # 11 SQL migration files (run in numeric order)
├── docs/             # 8 design + spec markdown files
├── assets/           # teacher reference image + voice clip (placeholders)
└── README.md
```

## Documentation

Read in this order:

1. [`docs/00-MASTER-PROMPT.md`](docs/00-MASTER-PROMPT.md) — orchestrating document, folder structure, build sequence, Definition of Done
2. [`docs/01-PRD.md`](docs/01-PRD.md) — features, personas, acceptance criteria, success metrics
3. [`docs/02-TRD.md`](docs/02-TRD.md) — full tech stack, architecture diagram, environment variables
4. [`docs/03-APP-FLOW.md`](docs/03-APP-FLOW.md) — every screen, route, and interaction
5. [`docs/04-UI-UX-BRIEF.md`](docs/04-UI-UX-BRIEF.md) — design tokens and component system
6. [`docs/05-BACKEND-SCHEMA.md`](docs/05-BACKEND-SCHEMA.md) — database schema, migrations, full API contract
7. [`docs/06-IMPLEMENTATION-PLAN.md`](docs/06-IMPLEMENTATION-PLAN.md) — phase-by-phase build plan

## Tech stack

Next.js 15 + TypeScript + Tailwind — FastAPI + Celery + Redis — Supabase
(Postgres + pgvector + Storage + Auth) — Gemini 2.0/2.5 Flash + Groq Llama 3.3
— Coqui XTTS-v2 — Wav2Lip — Manim (default) / Wan2.1 / cached Flow clips for
concept animation — ffmpeg + Remotion.

Full justification for every choice is in `docs/02-TRD.md`.

## Local setup

### Prerequisites

- Node.js 18+
- Python 3.11
- Redis (`docker run -d -p 6379:6379 redis` or a native install)
- A Supabase project (free tier)
- API keys: Gemini (AI Studio), Groq, Hugging Face (only if using the
  `wan_zerogpu` video provider)
- ffmpeg, Manim (optional — Manim only needed if you want the default
  concept-animation provider to render real animations)

### 1. Install dependencies

```bash
# Frontend
cd apps/web
npm install

# Backend
cd ../api
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` in both `apps/web` and `apps/api`, and fill in
every variable listed in `docs/02-TRD.md` under "Environment variables."

For local-dev without Supabase configured yet, you can leave the Supabase
URL empty and the frontend will use the seed profile id `00000000-0000-0000-0000-000000000001`
(from `supabase/migrations/011_seed_data.sql`) so you can click through the
demo. The backend, however, requires Supabase to be reachable to actually
store sessions/segments — without it, the API will return 500s on writes.

### 3. Set up the database

```bash
# From the project root, with the Supabase CLI installed and linked to your project
supabase db push
```

This runs every migration in `supabase/migrations/` in order (see
`docs/05-BACKEND-SCHEMA.md` for what each one creates). If you don't have
the Supabase CLI, paste the SQL files in order into the Supabase SQL editor.

### 4. Run the backend

```bash
cd apps/api
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

In a second terminal, start the Celery worker (required — agents are
declared as Celery tasks):

```bash
cd apps/api
celery -A celery_app worker --loglevel=info
```

> For local dev / hackathon demos, the FastAPI request handlers call agent
> functions synchronously (not via Celery) so you don't strictly need the
> worker running to click through the demo. The worker is required for the
> video pipeline (long-running) and for the production deployment.

### 5. Run the frontend

```bash
cd apps/web
npm run dev
```

Visit `http://localhost:3000`.

## Video provider configuration

The concept-animation step is swappable without touching any agent code —
set `VIDEO_PROVIDER` in `apps/api/.env` to one of:

- `manim` (default) — deterministic, zero-cost, zero-GPU, always available.
  Use this unless you've specifically verified an alternative works in your
  environment.
- `wan_zerogpu` — routes through a Hugging Face ZeroGPU Space via
  `gradio_client`; requires `HF_TOKEN`, subject to shared queue/quota limits.
- `flow_cache` — serves pre-generated clips you manually created in Google
  Flow and cached by prompt hash; requires populating the `video_cache`
  table ahead of time.

See `apps/api/skills/video_generation/factory.py` for the interface every
provider implements, and how to add a new one.

## Running tests

```bash
# Backend
cd apps/api
pytest

# Frontend
cd apps/web
npm run test
```

## Asset placeholders

`assets/teacher_ref.png` and `assets/teacher_voice.wav` are placeholders
you should replace with a real teacher reference image and voice clip before
recording the demo. Without them the avatar rendering skill produces a
single-frame placeholder video (still image + audio) so the rest of the
pipeline still runs.

## Known limitations

- Live, low-latency conversational voice interaction is out of scope for
  this submission (see `docs/01-PRD.md` Non-goals) — interaction is turn-based.
- Generative concept-animation quality depends on the selected
  `VIDEO_PROVIDER`; the default `manim` provider prioritizes reliability
  and factual accuracy over cinematic realism.
- Free-tier API quotas (Gemini, Groq, HF ZeroGPU) apply; see
  `docs/02-TRD.md` for rate-limiting mitigations.

## License

Built for hackathon submission purposes.
