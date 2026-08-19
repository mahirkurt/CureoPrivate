-- anamnesis-graph D1: collection isolation (P1).
-- apply on HP AFTER wrangler deploy of 1.2.0 (or before first live call — ensureSchema
-- also ALTERs additively). Safe to re-run: ADD COLUMN fails if present; UPDATEs are idempotent.
--
--   npx wrangler d1 execute anamnesis-graph --remote --file=migrations/0001_collection.sql
--
-- Does NOT wipe any collection. Existing rows become `_legacy`.

ALTER TABLE docs ADD COLUMN collection TEXT;
ALTER TABLE docs ADD COLUMN expires_at INTEGER;
ALTER TABLE chunks ADD COLUMN collection TEXT;
ALTER TABLE chunks ADD COLUMN char_start INTEGER;
ALTER TABLE chunks ADD COLUMN char_end INTEGER;
ALTER TABLE nodes ADD COLUMN collection TEXT;
ALTER TABLE edges ADD COLUMN collection TEXT;

CREATE INDEX IF NOT EXISTS idx_docs_collection ON docs(collection);
CREATE INDEX IF NOT EXISTS idx_chunks_collection ON chunks(collection);
CREATE INDEX IF NOT EXISTS idx_nodes_collection ON nodes(collection);
CREATE INDEX IF NOT EXISTS idx_edges_collection ON edges(collection);

UPDATE docs SET collection = '_legacy' WHERE collection IS NULL OR collection = '';
UPDATE chunks SET collection = '_legacy' WHERE collection IS NULL OR collection = '';
UPDATE nodes SET collection = '_legacy' WHERE collection IS NULL OR collection = '';
UPDATE edges SET collection = '_legacy' WHERE collection IS NULL OR collection = '';
