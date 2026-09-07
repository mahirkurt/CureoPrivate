-- 0002 — edge evidence accounting (audit 2026-09-07, finding A10).
--
-- `weight` used to be incremented on every re-assert of the same triple, so it measured how
-- often the orchestrator repeated itself rather than how well the claim is supported. Every
-- `ORDER BY weight DESC` in graph.ts (neighbors, subgraph, edgesByDocs, and therefore the
-- hybrid_query graph bundle) inherited that bias. Weight now counts DISTINCT supporting
-- documents; `assert_count` keeps the repetition visible instead of hiding it inside weight.
--
-- Additive and idempotent-by-intent; run once:
--   npx wrangler d1 execute anamnesis-graph --remote --file=migrations/0002_edge_evidence.sql
ALTER TABLE edges ADD COLUMN doc_ids TEXT;
ALTER TABLE edges ADD COLUMN assert_count INTEGER DEFAULT 1;

-- Backfill: pre-migration rows know only their single `doc_id`. Their old weight is a repetition
-- count, so it is preserved as assert_count and the evidence weight is reset to the honest value.
UPDATE edges
   SET doc_ids = CASE WHEN doc_id IS NULL OR doc_id = '' THEN '[]' ELSE json_array(doc_id) END,
       assert_count = COALESCE(weight, 1),
       weight = CASE WHEN doc_id IS NULL OR doc_id = '' THEN 1 ELSE 1 END
 WHERE doc_ids IS NULL;
