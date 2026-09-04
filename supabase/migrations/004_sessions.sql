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
