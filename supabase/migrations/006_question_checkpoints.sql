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
