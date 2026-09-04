-- 014_agent_run_logs_scene_id.sql
-- Shikshak AI — Add scene-level tracing to agent_run_logs.
--
-- The quality gate (skills/quality_gate.py) logs one row per scene per check
-- pass, making bad output diagnosable at scene granularity rather than only
-- at session granularity.
--
-- scene_id is nullable so all existing log rows remain valid. Only quality-gate
-- rows and scene-renderer rows will carry a scene_id.

alter table agent_run_logs
  add column if not exists scene_id uuid references scenes(id) on delete set null;

comment on column agent_run_logs.scene_id is
  'Scene this agent run relates to — populated by the quality gate and scene '
  'renderers. NULL for session-level agents (lesson_planning, explanation, etc.).';

create index if not exists agent_run_logs_scene_idx on agent_run_logs(scene_id);
