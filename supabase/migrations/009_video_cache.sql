-- 009_video_cache.sql
-- Shikshak AI — keyed cache for generated concept animation clips

create table video_cache (
  id uuid primary key default gen_random_uuid(),
  prompt_hash text unique not null,
  provider text not null,           -- 'manim' | 'wan_zerogpu' | 'flow_cache'
  storage_path text not null,
  created_at timestamptz default now()
);

create index video_cache_hash_idx on video_cache(prompt_hash);
