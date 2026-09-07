-- 0003 — GraphRAG global search: community partition store (BUILD-BRIEF §5 follow-through).
--
-- §5 deliberately did not ship global search rather than approximate it inside a request-scoped
-- Worker. The work is now split so nothing is approximated: an offline indexer on HP computes a
-- real Leiden partition (pure graph maths, no language model), this table stores it, and summaries
-- are written by the orchestrator (Claude) exactly like triples are.
--
-- Run once:
--   npx wrangler d1 execute anamnesis-graph --remote --file=migrations/0003_communities.sql
CREATE TABLE IF NOT EXISTS communities (
  id           TEXT PRIMARY KEY,   -- "<collection>::<level>::<idx>"
  collection   TEXT NOT NULL,
  level        INTEGER NOT NULL,   -- Leiden hierarchy level (0 = finest)
  members      TEXT NOT NULL,      -- JSON array of node ids, sorted (also the carry-over key)
  edge_count   INTEGER,
  summary      TEXT,               -- orchestrator-written; NULL until community_summarize
  summary_by   TEXT,               -- 'claude' | NULL. Never a Worker-side model.
  updated_at   INTEGER
);
CREATE INDEX IF NOT EXISTS idx_communities_collection ON communities(collection, level);
