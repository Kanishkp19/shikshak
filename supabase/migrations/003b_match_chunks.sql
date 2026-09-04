-- 003b_match_chunks.sql
-- Shabshak AI — stored function for vector search (used by skills/vector_search.py)

create or replace function match_document_chunks(
  query_embedding vector,
  filter_doc_id uuid,
  match_count int default 5,
  threshold float default 0.30
)
returns table (
  id uuid,
  document_id uuid,
  chunk_index int,
  content text,
  section_label text,
  score float
)
language sql
stable
as $$
  select
    dc.id,
    dc.document_id,
    dc.chunk_index,
    dc.content,
    dc.section_label,
    1 - (dc.embedding <=> query_embedding) as score
  from document_chunks dc
  where dc.document_id = filter_doc_id
    and 1 - (dc.embedding <=> query_embedding) >= threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
$$;
