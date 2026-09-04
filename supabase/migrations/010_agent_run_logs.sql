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
