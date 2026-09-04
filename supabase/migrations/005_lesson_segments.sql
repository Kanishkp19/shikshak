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
