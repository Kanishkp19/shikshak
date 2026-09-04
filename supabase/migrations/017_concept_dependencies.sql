-- 017_concept_dependencies.sql
-- Shikshak AI — Lightweight Concept-Dependency Graph (Learning Path Agent)

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

create policy "Users read dependencies of their own learning paths"
  on concept_dependencies for select
  using (learning_path_id in (select id from learning_paths where student_id = auth.uid()));

create policy "Service role manages concept dependencies"
  on concept_dependencies for all
  using (true) with check (true);
