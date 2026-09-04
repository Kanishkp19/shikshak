-- 011_seed_data.sql
-- Shikshak AI — local development seed data

-- NOTE: this references the auth.users table; for local dev you can either
-- register a real Supabase Auth user and use their id, or use the placeholder
-- below if your local Supabase instance has the test user pre-seeded.

-- Seed test auth user so foreign key constraint succeeds
insert into auth.users (id, email, raw_user_meta_data)
values (
  '00000000-0000-0000-0000-000000000001',
  'test.student@example.com',
  '{"display_name": "Test Student"}'::jsonb
)
on conflict (id) do nothing;

insert into learner_profiles (id, display_name, default_level, default_language)
values ('00000000-0000-0000-0000-000000000001', 'Test Student', 'beginner', 'en')
on conflict (id) do nothing;

insert into sessions (id, student_id, source_type, topic, level, language, time_budget_minutes, status)
values (
  '00000000-0000-0000-0000-000000000002',
  '00000000-0000-0000-0000-000000000001',
  'topic',
  'Photosynthesis',
  'beginner',
  'en',
  20,
  'planning'
)
on conflict (id) do nothing;
