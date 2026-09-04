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
