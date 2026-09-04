-- 008_learning_paths.sql
-- Shikshak AI — ordered curriculum breakdowns of broad topics

create table learning_paths (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references auth.users(id) on delete cascade not null,
  broad_topic text not null,
  created_at timestamptz default now()
);

create table learning_path_items (
  id uuid primary key default gen_random_uuid(),
  learning_path_id uuid references learning_paths(id) on delete cascade not null,
  item_order int not null,
  sub_topic text not null,
  prerequisite_item_id uuid references learning_path_items(id),
  status text check (status in ('locked','unlocked','completed')) default 'locked',
  related_session_id uuid references sessions(id)
);

alter table learning_paths enable row level security;
alter table learning_path_items enable row level security;

create policy "Users manage their own learning paths"
  on learning_paths for all
  using (auth.uid() = student_id) with check (auth.uid() = student_id);

create policy "Users manage items of their own learning paths"
  on learning_path_items for all
  using (learning_path_id in (select id from learning_paths where student_id = auth.uid()))
  with check (learning_path_id in (select id from learning_paths where student_id = auth.uid()));

create index learning_path_items_path_idx on learning_path_items(learning_path_id, item_order);
