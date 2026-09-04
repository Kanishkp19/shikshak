-- 001_learner_profiles.sql
-- Shikshak AI — learner profile table (1:1 with Supabase auth.users)

create table learner_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  default_level text check (default_level in ('beginner','intermediate','advanced')) default 'beginner',
  default_language text default 'en',
  topics_studied text[] default '{}',
  weak_concepts text[] default '{}',
  strong_concepts text[] default '{}',
  average_score numeric(5,2) default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table learner_profiles enable row level security;

create policy "Users manage their own profile"
  on learner_profiles for all
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- auto-update updated_at trigger
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger learner_profiles_updated_at
  before update on learner_profiles
  for each row execute function set_updated_at();
