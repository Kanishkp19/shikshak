# Shikshak AI — AI Teacher

Human-like AI educator that teaches through personalized, interactive video lessons — grounded in your own uploaded material or any topic, adapted to your level, time, and language.

Built for the AI Innovation Hackathon 2026 (Bharat Academix, Round 2).

## What this is

A student uploads a book/PDF/notes/slides, or just names a topic. The system plans a lesson, personalizes it to the student's level and available time, generates an actual teaching video (lip-synced avatar + voice + subject-appropriate diagrams/animations), pauses to ask questions during the lesson, diagnoses and re-teaches misconceptions when the student gets something wrong, and ends with a scored report and a recommendation — remembering weak areas for next time.

## Documentation

Read in this order:

1. [`docs/00-MASTER-PROMPT.md`](docs/00-MASTER-PROMPT.md) — orchestrating document, folder structure, build sequence, Definition of Done
2. [`docs/01-PRD.md`](docs/01-PRD.md) — features, personas, acceptance criteria, success metrics
3. [`docs/02-TRD.md`](docs/02-TRD.md) — full tech stack, architecture diagram, environment variables
4. [`docs/03-APP-FLOW.md`](docs/03-APP-FLOW.md) — every screen, route, and interaction
5. [`docs/04-UI-UX-BRIEF.md`](docs/04-UI-UX-BRIEF.md) — design tokens and component system
6. [`docs/05-BACKEND-SCHEMA.md`](docs/05-BACKEND-SCHEMA.md) — database schema, migrations, full API contract
7. [`docs/06-IMPLEMENTATION-PLAN.md`](docs/06-IMPLEMENTATION-PLAN.md) — phase-by-phase build plan
8. [`docs/AI-TEACHER-AGENT-ARCHITECTURE.md`](docs/AI-TEACHER-AGENT-ARCHITECTURE.md) — the 20-agent / 16-skill multi-agent design and the swappable video-generation interface

## Tech stack

Next.js 15 + TypeScript + Tailwind — FastAPI + Celery + Redis — Supabase (Postgres + pgvector + Storage + Auth) — Gemini 2.0/2.5 Flash + Groq Llama 3.3 — Coqui XTTS-v2 — Wav2Lip — Manim (default) / Wan2.1 / cached Flow clips for concept animation — ffmpeg + Remotion.

Full justification for every choice is in `docs/02-TRD.md`.

## Local setup

### Prerequisites
- Node.js 18+
- Python 3.11
- Redis (`docker run -d -p 6379:6379 redis` or a native install)
- A Supabase project (free tier)
- API keys: Gemini (AI Studio), Groq, Hugging Face (only if using the `wan_zerogpu` video provider)

### 1. Clone and install
```bash
git clone <repo-url> shikshak-ai
cd shikshak-ai

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
Copy `.env.example` to `.env` in both `apps/web` and `apps/api`, and fill in every variable listed in `docs/02-TRD.md` under "Environment variables."

### 3. Set up the database
```bash
# From the project root, with the Supabase CLI installed and linked to your project
supabase db push
```
This runs every migration in `supabase/migrations/` in order (see `docs/05-BACKEND-SCHEMA.md` for what each one creates).

### 4. Run the backend
```bash
cd apps/api
uvicorn main:app --reload --port 8000
```

In a second terminal, start the Celery worker (required — agents run as Celery tasks):
```bash
cd apps/api
celery -A celery_app worker --loglevel=info
```

### 5. Run the frontend
```bash
cd apps/web
npm run dev
```

Visit `http://localhost:3000`.

## Video provider configuration

The concept-animation step is swappable without touching any agent code — set `VIDEO_PROVIDER` in `apps/api/.env` to one of:
- `manim` (default) — deterministic, zero-cost, zero-GPU, always available. Use this unless you've specifically verified an alternative works in your environment.
- `wan_zerogpu` — routes through a Hugging Face ZeroGPU Space via `gradio_client`; requires `HF_TOKEN`, subject to shared queue/quota limits.
- `flow_cache` — serves pre-generated clips you manually created in Google Flow and cached by prompt hash; requires populating `video_cache` ahead of time.

See `docs/AI-TEACHER-AGENT-ARCHITECTURE.md` Section 4 for the interface every provider implements, and how to add a new one.

## Running tests

```bash
# Backend
cd apps/api
pytest

# Frontend
cd apps/web
npm run test
```

## Known limitations

- Live, low-latency conversational voice interaction is out of scope for this submission (see `01-PRD.md` Non-goals) — interaction is turn-based.
- Generative concept-animation quality depends on the selected `VIDEO_PROVIDER`; the default `manim` provider prioritizes reliability and factual accuracy over cinematic realism.
- Free-tier API quotas (Gemini, Groq, HF ZeroGPU) apply; see `docs/02-TRD.md` for rate-limiting mitigations.

## License

Built for hackathon submission purposes.
