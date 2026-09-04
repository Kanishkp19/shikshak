-- 001_learner_profiles.sql
-- Shikshak AI — learner profile table (1:1 with Supabase auth.users)

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

-- auto-update updated_at trigger
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger learner_profiles_updated_at
  before update on learner_profiles
  for each row execute function set_updated_at();
-- 002_documents.sql
-- Shikshak AI — uploaded source documents (PDF/DOCX/PPTX)

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
-- 003_document_chunks.sql
-- Shikshak AI — chunked document content + pgvector embeddings (RAG)

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
-- 003b_match_chunks.sql
-- Shabshak AI — stored function for vector search (used by skills/vector_search.py)

create or replace function match_document_chunks(
  query_embedding vector,
  filter_doc_id uuid,
  match_count int default 5,
  threshold float default 0.30
)
returns table (
  id uuid,
  document_id uuid,
  chunk_index int,
  content text,
  section_label text,
  score float
)
language sql
stable
as $$
  select
    dc.id,
    dc.document_id,
    dc.chunk_index,
    dc.content,
    dc.section_label,
    1 - (dc.embedding <=> query_embedding) as score
  from document_chunks dc
  where dc.document_id = filter_doc_id
    and 1 - (dc.embedding <=> query_embedding) >= threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
$$;
-- 004_sessions.sql
-- Shikshak AI — teaching sessions (one per "lesson")

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

create trigger sessions_updated_at
  before update on sessions
  for each row execute function set_updated_at();
-- 005_lesson_segments.sql
-- Shikshak AI — ordered teaching segments within a session

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

create policy "Service role manages segments"
  on lesson_segments for all
  using (true)
  with check (true);

create index lesson_segments_session_idx on lesson_segments(session_id, segment_order);
-- 006_question_checkpoints.sql
-- Shikshak AI — in-lesson and end-of-lesson questions

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
  )
  with check (
    segment_id in (
      select ls.id from lesson_segments ls
      join sessions s on s.id = ls.session_id
      where s.student_id = auth.uid()
    )
  );
-- 007_assessment_reports.sql
-- Shikshak AI — end-of-lesson scored report

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

create policy "Service role writes reports"
  on assessment_reports for insert
  with check (true);

create policy "Service role updates reports"
  on assessment_reports for update
  using (true);
-- 008_learning_paths.sql
-- Shikshak AI — ordered curriculum breakdowns of broad topics

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
  using (learning_path_id in (select id from learning_paths where student_id = auth.uid()))
  with check (learning_path_id in (select id from learning_paths where student_id = auth.uid()));

create index learning_path_items_path_idx on learning_path_items(learning_path_id, item_order);
-- 009_video_cache.sql
-- Shikshak AI — keyed cache for generated concept animation clips

create table video_cache (
  id uuid primary key default gen_random_uuid(),
  prompt_hash text unique not null,
  provider text not null,           -- 'manim' | 'wan_zerogpu' | 'flow_cache'
  storage_path text not null,
  created_at timestamptz default now()
);

create index video_cache_hash_idx on video_cache(prompt_hash);
-- 010_agent_run_logs.sql
-- Shikshak AI — observability log for agent runs

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
create index agent_run_logs_agent_idx on agent_run_logs(agent_name);

alter table agent_run_logs enable row level security;

create policy "Users read logs of their own sessions"
  on agent_run_logs for select
  using (session_id in (select id from sessions where student_id = auth.uid()));

create policy "Service role writes logs"
  on agent_run_logs for insert
  with check (true);
-- 011_seed_data.sql
-- Shikshak AI — local development seed data

-- NOTE: this references the auth.users table; for local dev you can either
-- register a real Supabase Auth user and use their id, or use the placeholder
-- below if your local Supabase instance has the test user pre-seeded.

-- Seed test auth user so foreign key constraint succeeds
insert into auth.users (id, email, raw_user_meta_data)
values (
  '00000000-0000-0000-0000-000000000001',
  'test.student@example.com',
  '{"display_name": "Test Student"}'::jsonb
)
on conflict (id) do nothing;

insert into learner_profiles (id, display_name, default_level, default_language)
values ('00000000-0000-0000-0000-000000000001', 'Test Student', 'beginner', 'en')
on conflict (id) do nothing;

insert into sessions (id, student_id, source_type, topic, level, language, time_budget_minutes, status)
values (
  '00000000-0000-0000-0000-000000000002',
  '00000000-0000-0000-0000-000000000001',
  'topic',
  'Photosynthesis',
  'beginner',
  'en',
  20,
  'planning'
)
on conflict (id) do nothing;
