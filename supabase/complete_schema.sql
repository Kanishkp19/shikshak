-- ==============================================================================
-- Shikshak AI — Complete Consolidated Database Schema
-- Includes Migrations 001 through 017
-- Safe and idempotent for execution in the Supabase SQL Editor
-- ==============================================================================

-- Enable required Postgres extensions
create extension if not exists "uuid-ossp";
create extension if not exists vector;

-- ──────────────────────────────────────────────────────────────────────────────
-- 001: Learner Profiles (1:1 with auth.users)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists learner_profiles (
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

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users manage their own profile' and tablename = 'learner_profiles') then
    create policy "Users manage their own profile"
      on learner_profiles for all
      to authenticated
      using ((select auth.uid()) = id)
      with check ((select auth.uid()) = id);
  end if;
end $$;

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists learner_profiles_updated_at on learner_profiles;
create trigger learner_profiles_updated_at
  before update on learner_profiles
  for each row execute function set_updated_at();

-- ──────────────────────────────────────────────────────────────────────────────
-- 002: Documents (Uploaded PDF/DOCX/PPTX)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists documents (
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

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users manage their own documents' and tablename = 'documents') then
    create policy "Users manage their own documents"
      on documents for all
      to authenticated
      using ((select auth.uid()) = owner_id)
      with check ((select auth.uid()) = owner_id);
  end if;
end $$;

create index if not exists documents_owner_idx on documents(owner_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- 003: Document Chunks + Vector Embeddings
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade not null,
  chunk_index int not null,
  content text not null,
  section_label text,
  embedding vector(768),
  created_at timestamptz default now()
);

create index if not exists document_chunks_document_idx on document_chunks(document_id);

do $$ begin
  if not exists (select 1 from pg_indexes where indexname = 'document_chunks_embedding_idx') then
    create index document_chunks_embedding_idx on document_chunks
      using ivfflat (embedding vector_cosine_ops) with (lists = 100);
  end if;
exception when others then
  -- In case ivfflat with lists=100 fails when table is empty in some PG versions
  null;
end $$;

alter table document_chunks enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users read chunks of their own documents' and tablename = 'document_chunks') then
    create policy "Users read chunks of their own documents"
      on document_chunks for select
      to authenticated
      using (
        document_id in (select id from documents where owner_id = (select auth.uid()))
      );
  end if;
end $$;

-- 003b: Stored procedure for vector search
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
language sql stable security invoker
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
    and (1 - (dc.embedding <=> query_embedding)) >= threshold
  order score desc
  limit match_count;
$$;

-- ──────────────────────────────────────────────────────────────────────────────
-- 004: Sessions
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  source_type text check (source_type in ('document','topic','standard_topic')) not null,
  document_id uuid references documents(id) on delete set null,
  topic text not null,
  level text check (level in ('beginner','intermediate','advanced')) not null default 'beginner',
  language text not null default 'en',
  time_budget_minutes int not null check (time_budget_minutes between 5 and 60) default 15,
  status text check (status in ('planning','delivering','completed','failed')) default 'planning',
  active_segment_id uuid,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table sessions enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users manage their own sessions' and tablename = 'sessions') then
    create policy "Users manage their own sessions"
      on sessions for all
      to authenticated
      using ((select auth.uid()) = student_id)
      with check ((select auth.uid()) = student_id);
  end if;
end $$;

create index if not exists sessions_student_idx on sessions(student_id);

drop trigger if exists sessions_updated_at on sessions;
create trigger sessions_updated_at
  before update on sessions
  for each row execute function set_updated_at();

-- ──────────────────────────────────────────────────────────────────────────────
-- 005: Lesson Segments (with Diagram Spec columns from 012)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists lesson_segments (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade not null,
  segment_order int not null,
  concept text not null,
  depth text check (depth in ('beginner','intermediate','advanced')) not null default 'beginner',
  time_budget_seconds int not null default 180,
  visual_type text check (visual_type in ('animated_concept','screen_recording','talking_head','hybrid')) default 'animated_concept',
  narration_script text,
  language text not null default 'en',
  status text check (status in ('pending','generating','rendering','ready','delivered','failed')) default 'pending',
  video_url text,
  diagram_spec_json jsonb,
  animation_scenes_json jsonb,
  related_concepts jsonb,
  created_at timestamptz default now()
);

-- Ensure columns exist if table was previously created
alter table lesson_segments add column if not exists diagram_spec_json jsonb;
alter table lesson_segments add column if not exists animation_scenes_json jsonb;
alter table lesson_segments add column if not exists related_concepts jsonb;

alter table lesson_segments enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users read segments of their own sessions' and tablename = 'lesson_segments') then
    create policy "Users read segments of their own sessions"
      on lesson_segments for select
      to authenticated
      using (
        session_id in (select id from sessions where student_id = (select auth.uid()))
      );
  end if;
end $$;

create index if not exists lesson_segments_session_idx on lesson_segments(session_id, segment_order);

-- ──────────────────────────────────────────────────────────────────────────────
-- 006: Question Checkpoints (with 015 adaptive attempts)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists question_checkpoints (
  id uuid primary key default gen_random_uuid(),
  segment_id uuid references lesson_segments(id) on delete cascade not null,
  question text not null,
  options jsonb not null,
  correct_index int not null check (correct_index between 0 and 3),
  explanation text not null,
  misconception_distractors jsonb,
  student_answer int check (student_answer between 0 and 3),
  is_correct boolean,
  attempt_number int default 1,
  reteach_strategy text check (reteach_strategy in ('simplify','concrete_example','atomic_steps')),
  prior_analogies_used text[] default '{}',
  answered_at timestamptz,
  created_at timestamptz default now()
);

-- Ensure 015 columns exist
alter table question_checkpoints add column if not exists attempt_number int default 1;
alter table question_checkpoints add column if not exists reteach_strategy text check (reteach_strategy in ('simplify','concrete_example','atomic_steps'));
alter table question_checkpoints add column if not exists prior_analogies_used text[] default '{}';

alter table question_checkpoints enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users manage checkpoints of their own sessions' and tablename = 'question_checkpoints') then
    create policy "Users manage checkpoints of their own sessions"
      on question_checkpoints for all
      to authenticated
      using (
        segment_id in (
          select ls.id from lesson_segments ls
          join sessions s on s.id = ls.session_id
          where s.student_id = (select auth.uid())
        )
      )
      with check (
        segment_id in (
          select ls.id from lesson_segments ls
          join sessions s on s.id = ls.session_id
          where s.student_id = (select auth.uid())
        )
      );
  end if;
end $$;

create index if not exists question_checkpoints_segment_idx on question_checkpoints(segment_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- 007: Assessment Reports
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists assessment_reports (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade unique not null,
  score numeric(5,2) not null,
  total_questions int not null,
  correct_count int not null,
  mastered_concepts text[] default '{}',
  struggling_concepts text[] default '{}',
  feedback text,
  recommended_next text,
  created_at timestamptz default now()
);

alter table assessment_reports enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users read their own assessment reports' and tablename = 'assessment_reports') then
    create policy "Users read their own assessment reports"
      on assessment_reports for select
      to authenticated
      using (
        session_id in (select id from sessions where student_id = (select auth.uid()))
      );
  end if;
end $$;

-- ──────────────────────────────────────────────────────────────────────────────
-- 008: Learning Paths
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists learning_paths (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  goal text not null,
  current_level text check (current_level in ('beginner','intermediate','advanced')) not null,
  target_level text check (target_level in ('beginner','intermediate','advanced')) not null,
  estimated_hours numeric(4,1) not null,
  milestones jsonb not null,
  created_at timestamptz default now()
);

alter table learning_paths enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users manage their own learning paths' and tablename = 'learning_paths') then
    create policy "Users manage their own learning paths"
      on learning_paths for all
      to authenticated
      using ((select auth.uid()) = student_id)
      with check ((select auth.uid()) = student_id);
  end if;
end $$;

create index if not exists learning_paths_student_idx on learning_paths(student_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- 009: Video Cache
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists video_cache (
  id uuid primary key default gen_random_uuid(),
  concept text not null,
  visual_type text not null,
  duration_bucket int not null,
  storage_path text not null,
  hit_count int default 0,
  created_at timestamptz default now(),
  unique(concept, visual_type, duration_bucket)
);

create index if not exists video_cache_lookup_idx on video_cache(concept, visual_type, duration_bucket);

alter table video_cache enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Video cache is readable by authenticated users' and tablename = 'video_cache') then
    create policy "Video cache is readable by authenticated users"
      on video_cache for select
      to authenticated
      using (true);
  end if;
end $$;

-- ──────────────────────────────────────────────────────────────────────────────
-- 010: Agent Run Logs (with 014 scene_id column)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists agent_run_logs (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade not null,
  agent_name text not null,
  step int,
  input_summary text,
  output_summary text,
  tokens_used int default 0,
  latency_ms int,
  status text check (status in ('success','fallback','error')),
  error_message text,
  scene_id uuid,
  created_at timestamptz default now()
);

alter table agent_run_logs add column if not exists scene_id uuid;

create index if not exists agent_run_logs_session_idx on agent_run_logs(session_id);
create index if not exists agent_run_logs_scene_idx on agent_run_logs(scene_id);

alter table agent_run_logs enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users read logs of their own sessions' and tablename = 'agent_run_logs') then
    create policy "Users read logs of their own sessions"
      on agent_run_logs for select
      to authenticated
      using (session_id in (select id from sessions where student_id = (select auth.uid())));
  end if;
  if not exists (select 1 from pg_policies where policyname = 'Service role writes logs' and tablename = 'agent_run_logs') then
    create policy "Service role writes logs"
      on agent_run_logs for insert
      to authenticated
      with check (true);
  end if;
end $$;

-- ──────────────────────────────────────────────────────────────────────────────
-- 013: Scenes (Scene-First Atomic Video Units)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists scenes (
  id                 uuid primary key default gen_random_uuid(),
  segment_id         uuid references lesson_segments(id) on delete cascade not null,
  scene_order        int not null,
  learning_objective text not null,
  narration_text     text not null,
  visual_mode        text not null check (visual_mode in (
    'reaction_lab',
    'equation_build',
    'experiment_observation',
    'balancing_exercise',
    'generic_explainer'
  )),
  visual_payload     jsonb not null default '{}',
  on_screen_equation text    not null default '',
  on_screen_labels   text[]  not null default '{}',
  key_takeaway       text    not null default '',
  start_time_ms      int,
  end_time_ms        int,
  interaction_cue    jsonb,
  render_status      text not null check (render_status in (
    'pending', 'rendering', 'ready', 'failed'
  )) default 'pending',
  rendered_clip_path text,
  rendered_clip_url  text,
  quality_check      jsonb,
  created_at         timestamptz not null default now()
);

alter table scenes enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users read scenes of their own sessions' and tablename = 'scenes') then
    create policy "Users read scenes of their own sessions"
      on scenes for select
      to authenticated
      using (
        segment_id in (
          select ls.id
          from   lesson_segments ls
          join   sessions s on s.id = ls.session_id
          where  s.student_id = (select auth.uid())
        )
      );
  end if;
end $$;

create index if not exists scenes_segment_idx on scenes(segment_id, scene_order);
create index if not exists scenes_render_status_idx on scenes(render_status);

-- ──────────────────────────────────────────────────────────────────────────────
-- 016: Concept Mastery Tracking
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists concept_mastery (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  concept text not null,
  score numeric(4,3) not null default 0,
  status text check (status in ('weak','moderate','strong')) default 'weak',
  attempts int default 0,
  consecutive_strong int default 0,
  last_updated timestamptz default now(),
  unique(student_id, concept)
);

create index if not exists concept_mastery_student_idx on concept_mastery(student_id);
create index if not exists concept_mastery_concept_idx on concept_mastery(concept);

alter table concept_mastery enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users manage their own concept mastery' and tablename = 'concept_mastery') then
    create policy "Users manage their own concept mastery"
      on concept_mastery for all
      to authenticated
      using ((select auth.uid()) = student_id)
      with check ((select auth.uid()) = student_id);
  end if;
end $$;

-- ──────────────────────────────────────────────────────────────────────────────
-- 017: Concept Dependencies (Lightweight Knowledge Graph)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists concept_dependencies (
  id uuid primary key default gen_random_uuid(),
  learning_path_id uuid references learning_paths(id) on delete cascade not null,
  concept text not null,
  depends_on_concept text,
  created_at timestamptz default now()
);

create index if not exists concept_dependencies_path_idx on concept_dependencies(learning_path_id);
create index if not exists concept_dependencies_concept_idx on concept_dependencies(concept);

alter table concept_dependencies enable row level security;

do $$ begin
  if not exists (select 1 from pg_policies where policyname = 'Users read dependencies of their own learning paths' and tablename = 'concept_dependencies') then
    create policy "Users read dependencies of their own learning paths"
      on concept_dependencies for select
      to authenticated
      using (learning_path_id in (select id from learning_paths where student_id = (select auth.uid())));
  end if;
end $$;

-- ──────────────────────────────────────────────────────────────────────────────
-- 011: Local & Demo Seed Data
-- ──────────────────────────────────────────────────────────────────────────────
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
  'completed'
)
on conflict (id) do nothing;
