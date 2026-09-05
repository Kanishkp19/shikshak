-- ==============================================================================
-- Shikshak AI — Missing Migrations Patch (012, 015, 016, 017)
-- Run this in your Supabase SQL Editor to bring your database to 100% parity.
-- All statements are safe and idempotent (IF NOT EXISTS).
-- ==============================================================================

-- ──────────────────────────────────────────────────────────────────────────────
-- 1. Add Missing Columns to lesson_segments (Migration 012)
-- ──────────────────────────────────────────────────────────────────────────────
alter table lesson_segments
  add column if not exists diagram_spec_json jsonb;

alter table lesson_segments
  add column if not exists animation_scenes_json jsonb;

alter table lesson_segments
  add column if not exists related_concepts jsonb;

comment on column lesson_segments.diagram_spec_json is
  'Pre-computed DiagramSpec from content_scriptwriter — used at render time instead of LLM call';

comment on column lesson_segments.animation_scenes_json is
  'Per-scene animation breakdown with matched narration + visual elements';

comment on column lesson_segments.related_concepts is
  'Related sub-topics for deep-dive navigation';


-- ──────────────────────────────────────────────────────────────────────────────
-- 2. Add Missing Columns to question_checkpoints (Migration 015)
-- ──────────────────────────────────────────────────────────────────────────────
alter table question_checkpoints
  add column if not exists attempt_number int default 1;

alter table question_checkpoints
  add column if not exists reteach_strategy text
  check (reteach_strategy in ('simplify','concrete_example','atomic_steps'));

alter table question_checkpoints
  add column if not exists prior_analogies_used text[] default '{}';

comment on column question_checkpoints.attempt_number is
  'Number of attempts submitted by the student for this checkpoint (1 = first wrong, 2 = second wrong, 3+ = atomic steps).';

comment on column question_checkpoints.reteach_strategy is
  'Reteach ladder strategy chosen based on attempt_number: simplify, concrete_example, or atomic_steps.';

comment on column question_checkpoints.prior_analogies_used is
  'Accumulated analogies used in previous attempts for this checkpoint, to ensure subsequent attempts use distinct analogies.';


-- ──────────────────────────────────────────────────────────────────────────────
-- 3. Create concept_mastery Table (Migration 016)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists concept_mastery (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  concept text not null,
  score numeric(4,3) not null default 0,       -- 0.000–1.000
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
  if not exists (select 1 from pg_policies where policyname = 'Service role manages concept mastery' and tablename = 'concept_mastery') then
    create policy "Service role manages concept mastery"
      on concept_mastery for all
      to authenticated
      using (true)
      with check (true);
  end if;
end $$;


-- ──────────────────────────────────────────────────────────────────────────────
-- 4. Create concept_dependencies Table (Migration 017)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists concept_dependencies (
  id uuid primary key default gen_random_uuid(),
  learning_path_id uuid references learning_paths(id) on delete cascade not null,
  concept text not null,
  depends_on_concept text,   -- null for root/first concepts
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
  if not exists (select 1 from pg_policies where policyname = 'Service role manages concept dependencies' and tablename = 'concept_dependencies') then
    create policy "Service role manages concept dependencies"
      on concept_dependencies for all
      to authenticated
      using (true)
      with check (true);
  end if;
end $$;
