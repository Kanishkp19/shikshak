-- 016_concept_mastery.sql
-- Shikshak AI — Continuous Concept Mastery Tracking

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

create policy "Users manage their own concept mastery"
  on concept_mastery for all
  using (auth.uid() = student_id) with check (auth.uid() = student_id);

create policy "Service role manages concept mastery"
  on concept_mastery for all
  using (true) with check (true);
