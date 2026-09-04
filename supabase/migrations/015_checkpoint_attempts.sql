-- 015_checkpoint_attempts.sql
-- Shikshak AI — Adaptive reteach ladder attempt tracking & strategy selection

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
