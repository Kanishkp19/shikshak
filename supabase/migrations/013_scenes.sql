-- 013_scenes.sql
-- Shikshak AI — Scene-first video lesson architecture.
--
-- Each lesson_segment now decomposes into 3-6 short, purposeful scenes.
-- A scene is the atomic render unit: one learning objective, one visual mode,
-- one narration passage, timed to real audio duration.
--
-- visual_mode values (chemistry pack first; others to follow after benchmark):
--   reaction_lab            | beakers mix → precipitate / colour change forms
--   equation_build          | equation constructed term-by-term
--   experiment_observation  | setup → action → observable change
--   balancing_exercise      | atom counters confirm conservation
--   generic_explainer       | illustrated explainer — meaningful fallback
--
-- visual_payload is a JSONB column whose schema is validated by the Pydantic
-- model matching the visual_mode before it ever touches a renderer.

create table scenes (
  id                 uuid primary key default gen_random_uuid(),
  segment_id         uuid references lesson_segments(id) on delete cascade not null,
  scene_order        int not null,

  -- Instructional contract
  learning_objective text not null,
  narration_text     text not null,

  -- Visual intent (typed payload validated by Pydantic before render)
  visual_mode        text not null check (visual_mode in (
    'reaction_lab',
    'equation_build',
    'experiment_observation',
    'balancing_exercise',
    'generic_explainer'
  )),
  visual_payload     jsonb not null default '{}',

  -- On-screen overlays
  on_screen_equation text    not null default '',
  on_screen_labels   text[]  not null default '{}',
  key_takeaway       text    not null default '',

  -- Audio timing (populated after TTS; drives scene-clip trimming)
  start_time_ms      int,
  end_time_ms        int,

  -- Optional interaction hook (null = no pause; used by Phase 5 player)
  interaction_cue    jsonb,

  -- Render pipeline state
  render_status      text not null check (render_status in (
    'pending', 'rendering', 'ready', 'failed'
  )) default 'pending',
  rendered_clip_path text,           -- local tmp path after render
  rendered_clip_url  text,           -- Supabase Storage URL after upload

  -- Quality gate trace (recorded by skills/quality_gate.py)
  quality_check      jsonb,

  created_at         timestamptz not null default now()
);

-- RLS: students read only scenes that belong to their own sessions
alter table scenes enable row level security;

create policy "Users read scenes of their own sessions"
  on scenes for select
  using (
    segment_id in (
      select ls.id
      from   lesson_segments ls
      join   sessions s on s.id = ls.session_id
      where  s.student_id = auth.uid()
    )
  );

-- Index for per-segment ordered traversal (the primary access pattern)
create index scenes_segment_idx on scenes(segment_id, scene_order);
-- Index for render-queue workers polling by status
create index scenes_render_status_idx on scenes(render_status);
