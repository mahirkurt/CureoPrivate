import { describe, it, expect } from "vitest";
import { ingestDocument, semanticSearch, corpusStats } from "../src/rag.js";
import type { D1Like } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const COLL = "evidentia:run:1111222233ab";

/** Records the SQL text the Worker prepares, so we can assert what the hot path actually costs. */
function recordingDb(db: D1Like): { db: D1Like; sql: string[] } {
  const sql: string[] = [];
  const wrapped: D1Like = { prepare: (q: string) => { sql.push(q); return db.prepare(q); } };
  return { db: wrapped, sql };
}

const MIGRATION = /CREATE TABLE|CREATE VIRTUAL TABLE|CREATE INDEX|ALTER TABLE|collection IS NULL|COUNT\(\*\) AS n FROM chunks_fts/i;

describe("schema bootstrap stays off the hot path (A3)", () => {
  it("runs migration statements once, not on every tool call", async () => {
    const base = evalEnv(new MockVectorize());
    const rec = recordingDb(base.DB);
    const env = { ...base, DB: rec.db };

    await ingestDocument(env, { text: "Alpha one. Alpha two.", doc_id: "sch:a", collection: COLL });
    expect(rec.sql.some((q) => MIGRATION.test(q))).toBe(true); // first call bootstraps

    rec.sql.length = 0;
    await semanticSearch(env, { query: "alpha", collection: COLL, rerank: false });
    await corpusStats(env, COLL);
    const repeated = rec.sql.filter((q) => MIGRATION.test(q));
    // Previously EVERY call replayed 7 CREATEs, 7 ALTERs, 4 full-table `UPDATE ... WHERE
    // collection IS NULL` writes and 2 COUNT(*) scans — and hybrid_query paid it twice.
    expect(repeated).toEqual([]);
  });
});
