-- 002_documents.sql
-- Shikshak AI — uploaded source documents (PDF/DOCX/PPTX)

create table documents (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users(id) on delete cascade not null,
  file_name text not null,
  file_type text check (file_type in ('pdf','docx','pptx')) not null,
  storage_path text not null,
  page_count int,
  status text check (status in ('processing','ready','failed')) default 'processing',
  created_at timestamptz default now()
);

alter table documents enable row level security;

create policy "Users manage their own documents"
  on documents for all
  using (auth.uid() = owner_id)
  with check (auth.uid() = owner_id);

create index documents_owner_idx on documents(owner_id);
