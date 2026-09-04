# 05 — Backend Schema & API Contract — Shikshak AI

## Database choice

Supabase Postgres with the `pgvector` extension enabled. One database serves both relational data (sessions, profiles, questions) and vector search (document chunk embeddings) — avoids running a separate vector store for a hackathon timeline, and Supabase Storage sits alongside it for files/audio/video.

## Entity relationship overview

```
users (Supabase Auth) --1:1--> learner_profiles
learner_profiles --1:N--> sessions
sessions --1:1--> documents (nullable, only if sourceType = document)
documents --1:N--> document_chunks (pgvector embeddings)
sessions --1:N--> lesson_segments
lesson_segments --0:1--> question_checkpoints
sessions --1:1--> assessment_reports
learner_profiles --1:N--> learning_paths
learning_paths --1:N--> learning_path_items
video_cache (keyed by prompt hash, referenced by lesson_segments.video_cache_id)
agent_run_logs (referenced by sessions.id, for debugging/observability)
```

## SQL migrations

### `001_learner_profiles.sql`
```sql
create table learner_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  default_level text check (default_level in ('beginner','intermediate','advanced')) default 'beginner',
  default_language text default 'en',
  topics_studied text[] default '{}',
  weak_concepts text[] default '{}',
  strong_concepts text[] default '{}',
  average_score numeric(5,2) default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table learner_profiles enable row level security;

create policy "Users manage their own profile"
  on learner_profiles for all
  using (auth.uid() = id)
  with check (auth.uid() = id);
```

### `002_documents.sql`
```sql
create table documents (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users(id) on delete cascade not null,
  file_name text not null,
  file_type text check (file_type in ('pdf','docx','pptx')) not null,
  storage_path text not null,
  page_count int,
  status text check (status in ('processing','ready','failed')) default 'processing',
  created_at timestamptz default now()
);

alter table documents enable row level security;

create policy "Users manage their own documents"
  on documents for all
  using (auth.uid() = owner_id)
  with check (auth.uid() = owner_id);

create index documents_owner_idx on documents(owner_id);
```

### `003_document_chunks.sql`
```sql
create extension if not exists vector;

create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade not null,
  chunk_index int not null,
  content text not null,
  section_label text,          -- e.g. "Chapter 4, page 12"
  embedding vector(768),       -- text-embedding-004 dimension; adjust if using bge-small-en (384)
  created_at timestamptz default now()
);

create index document_chunks_document_idx on document_chunks(document_id);
create index document_chunks_embedding_idx on document_chunks
  using ivfflat (embedding vector_cosine_ops) with (lists = 100);

alter table document_chunks enable row level security;

create policy "Users read chunks of their own documents"
  on document_chunks for select
  using (
    document_id in (select id from documents where owner_id = auth.uid())
  );
```

### `004_sessions.sql`
```sql
create table sessions (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  source_type text check (source_type in ('document','topic')) not null,
  document_id uuid references documents(id),
  topic text,
  level text check (level in ('beginner','intermediate','advanced')) not null,
  language text not null default 'en',
  time_budget_minutes int not null,
  status text check (status in ('planning','in_progress','completed','failed')) default 'planning',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table sessions enable row level security;

create policy "Users manage their own sessions"
  on sessions for all
  using (auth.uid() = student_id)
  with check (auth.uid() = student_id);

create index sessions_student_idx on sessions(student_id);
```

### `005_lesson_segments.sql`
```sql
create table lesson_segments (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade not null,
  segment_order int not null,
  concept text not null,
  depth text check (depth in ('beginner','intermediate','advanced')) not null,
  visual_type text check (visual_type in ('diagram','equation','code','animation','none')) not null,
  narration_script text not null,
  audio_url text,
  video_url text,
  video_cache_id uuid,
  has_checkpoint boolean default false,
  status text check (status in ('pending','rendering','ready','failed')) default 'pending',
  created_at timestamptz default now()
);

alter table lesson_segments enable row level security;

create policy "Users read segments of their own sessions"
  on lesson_segments for select
  using (session_id in (select id from sessions where student_id = auth.uid()));

create index lesson_segments_session_idx on lesson_segments(session_id, segment_order);
```

### `006_question_checkpoints.sql`
```sql
create table question_checkpoints (
  id uuid primary key default gen_random_uuid(),
  segment_id uuid references lesson_segments(id) on delete cascade not null,
  question_type text check (question_type in ('mcq','short_answer','conceptual')) not null,
  prompt text not null,
  options text[],
  correct_answer text not null,
  student_answer text,
  is_correct boolean,
  misconception text,
  created_at timestamptz default now()
);

alter table question_checkpoints enable row level security;

create policy "Users manage checkpoints of their own sessions"
  on question_checkpoints for all
  using (
    segment_id in (
      select ls.id from lesson_segments ls
      join sessions s on s.id = ls.session_id
      where s.student_id = auth.uid()
    )
  );
```

### `007_assessment_reports.sql`
```sql
create table assessment_reports (
  session_id uuid primary key references sessions(id) on delete cascade,
  score numeric(5,2) not null,
  strong_areas text[] default '{}',
  weak_areas text[] default '{}',
  recommendation text not null,
  created_at timestamptz default now()
);

alter table assessment_reports enable row level security;

create policy "Users read reports of their own sessions"
  on assessment_reports for select
  using (session_id in (select id from sessions where student_id = auth.uid()));
```

### `008_learning_paths.sql`
```sql
create table learning_paths (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  broad_topic text not null,
  created_at timestamptz default now()
);

create table learning_path_items (
  id uuid primary key default gen_random_uuid(),
  learning_path_id uuid references learning_paths(id) on delete cascade not null,
  item_order int not null,
  sub_topic text not null,
  prerequisite_item_id uuid references learning_path_items(id),
  status text check (status in ('locked','unlocked','completed')) default 'locked',
  related_session_id uuid references sessions(id)
);

alter table learning_paths enable row level security;
alter table learning_path_items enable row level security;

create policy "Users manage their own learning paths"
  on learning_paths for all
  using (auth.uid() = student_id) with check (auth.uid() = student_id);

create policy "Users manage items of their own learning paths"
  on learning_path_items for all
  using (learning_path_id in (select id from learning_paths where student_id = auth.uid()));
```

### `009_video_cache.sql`
```sql
create table video_cache (
  id uuid primary key default gen_random_uuid(),
  prompt_hash text unique not null,
  provider text not null,           -- 'manim' | 'wan_zerogpu' | 'flow_cache'
  storage_path text not null,
  created_at timestamptz default now()
);

create index video_cache_hash_idx on video_cache(prompt_hash);
```

### `010_agent_run_logs.sql`
```sql
create table agent_run_logs (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade,
  agent_name text not null,
  input_summary jsonb,
  output_summary jsonb,
  status text check (status in ('success','failed','fallback_used')) not null,
  duration_ms int,
  error_message text,
  created_at timestamptz default now()
);

create index agent_run_logs_session_idx on agent_run_logs(session_id);
```

## Full API contract

### Documents
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `POST` | `/api/v1/documents` | multipart file | `{documentId, status: "processing"}` | Content Ingestion Agent |
| `GET` | `/api/v1/documents/{id}` | — | `Document` | — |

### Sessions
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `POST` | `/api/v1/sessions` | `{sourceType, documentId?, topic?, level, language, timeBudgetMinutes}` | `{sessionId, status: "planning"}` | Orchestrator -> Knowledge Retrieval (if document) -> Lesson Planning -> Personalization -> Time Budgeting -> Explanation -> Visual Selection (parallel per segment) |
| `GET` | `/api/v1/sessions/{id}` | — | `Session` (with segments) | — |
| `GET` | `/api/v1/sessions/{id}/status` | — | `{status}` | — |
| `POST` | `/api/v1/sessions/{id}/language` | `{language}` | `{status: "regenerating"}` | Language Agent -> Voice Synthesis -> Avatar Rendering -> Video Compositing (for remaining segments) |
| `GET` | `/api/v1/sessions?studentId=` | — | `Session[]` | — |

### Segments
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `GET` | `/api/v1/sessions/{id}/segments/{segmentId}/status` | — | `{status, videoUrl?}` | — |
| `POST` | `/api/v1/sessions/{id}/segments/{segmentId}/render` | — | `{status: "rendering"}` | Voice Synthesis -> (Avatar Rendering + Concept Animation, parallel) -> Video Compositing |

### Checkpoints
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `POST` | `/api/v1/sessions/{id}/answer` | `{checkpointId, answer}` | `{isCorrect, misconception?, nextSegmentId}` | Answer Evaluation Agent -> (if wrong) Misconception Detection Agent -> Explanation Agent -> Voice/Avatar/Compositing for the re-explanation clip |

### Assessment
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `GET` | `/api/v1/sessions/{id}/report` | — | `AssessmentReport` | Assessment Agent -> Learner Profile Agent (writes back) |

### Learner profile
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `GET` | `/api/v1/learner-profile/{studentId}` | — | `LearnerProfile` | — |
| `PATCH` | `/api/v1/learner-profile/{studentId}` | `{defaultLevel?, defaultLanguage?}` | `LearnerProfile` | — |

### Learning paths
| Method | Path | Body | Response | Agent(s) triggered |
|---|---|---|---|---|
| `POST` | `/api/v1/learning-paths` | `{studentId, broadTopic}` | `{pathId, items: [...]}` | Learning Path Agent |
| `GET` | `/api/v1/learning-paths/{id}` | — | `LearningPath` (with items) | — |

## Pydantic request/response models (backend, mirrors TRD TypeScript interfaces)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class CreateSessionRequest(BaseModel):
    source_type: Literal["document", "topic"]
    document_id: Optional[str] = None
    topic: Optional[str] = None
    level: Literal["beginner", "intermediate", "advanced"]
    language: str = "en"
    time_budget_minutes: int = Field(gt=0)

class LessonSegmentOut(BaseModel):
    id: str
    order: int
    concept: str
    depth: Literal["beginner", "intermediate", "advanced"]
    visual_type: Literal["diagram", "equation", "code", "animation", "none"]
    narration_script: str
    video_url: Optional[str] = None
    has_checkpoint: bool

class SubmitAnswerRequest(BaseModel):
    checkpoint_id: str
    answer: str

class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    misconception: Optional[str] = None
    next_segment_id: str

class AssessmentReportOut(BaseModel):
    session_id: str
    score: float
    strong_areas: list[str]
    weak_areas: list[str]
    recommendation: str
```

## Session status state machine

```
planning --(Lesson Planning Agent completes)--> in_progress --(Assessment Agent completes)--> completed
   |                                                  |
   +--(any agent fails after retry)--> failed <-------+
```

## Seed data (for local development)

```sql
insert into learner_profiles (id, display_name, default_level, default_language)
values ('00000000-0000-0000-0000-000000000001', 'Test Student', 'beginner', 'en');

insert into sessions (id, student_id, source_type, topic, level, language, time_budget_minutes, status)
values ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'topic', 'Photosynthesis', 'beginner', 'en', 20, 'planning');
```
