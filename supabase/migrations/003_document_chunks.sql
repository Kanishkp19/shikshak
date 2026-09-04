-- 003_document_chunks.sql
-- Shikshak AI — chunked document content + pgvector embeddings (RAG)

create extension if not exists vector;

create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade not null,
  chunk_index int not null,
  content text not null,
  section_label text,          -- e.g. "Chapter 4, page 12"
  embedding vector(768),       -- text-embedding-004 dimension; adjust if using bge-small-en (384)
  created_at timestamptz default now()
);

create index document_chunks_document_idx on document_chunks(document_id);
create index document_chunks_embedding_idx on document_chunks
  using ivfflat (embedding vector_cosine_ops) with (lists = 100);

alter table document_chunks enable row level security;

create policy "Users read chunks of their own documents"
  on document_chunks for select
  using (
    document_id in (select id from documents where owner_id = auth.uid())
  );
