/**
 * rag.ts — Vector store (Cloudflare Vectorize) + chunk/doc text store (D1) for anamnesis-mcp.
 *
 * Design: Vectorize holds ONLY {id, values(1024-d), metadata:{doc_id, idx}} — lean, so we never
 * hit Vectorize's per-vector metadata size ceiling. The chunk TEXT lives in D1 (`chunks`). A
 * search returns chunk ids+scores from Vectorize, then we hydrate text from D1 by id. This is
 * the mechanism that keeps large corpora OUT of the model context: the book/article text sits in
 * D1+Vectorize, and only the top-k query-relevant chunks (bounded) are ever surfaced.
 *
 * VERIFIED Cloudflare API (2026-06):
 *   env.VECTORIZE.upsert([{ id, values, metadata }])              -> mutation
 *   env.VECTORIZE.query(vector, { topK, returnMetadata })        -> { matches:[{id,score,metadata}] }
 *   env.DB.prepare(sql).bind(...).run() / .all() / .first()      -> D1
 * Vectorize V2 `returnMetadata` accepts the string "all" (V1 accepted boolean true); we pass
 * "all" and tolerate either at runtime. Query result is normalized to `.matches`.
 */

import { embedTexts, embedOne } from "./embed.js";
import { semanticChunk, type ChunkOpts } from "./chunk.js";

// ---- minimal binding shapes (kept local so typecheck is stub-robust) -------
export interface VectorizeBinding {
  upsert: (vectors: Array<{ id: string; values: number[]; metadata?: Record<string, unknown> }>) => Promise<unknown>;
  query: (vector: number[], opts: Record<string, unknown>) => Promise<unknown>;
  // Cloudflare Vectorize V2 supports deleteByIds; optional so typecheck stays stub-robust.
  deleteByIds?: (ids: string[]) => Promise<unknown>;
}
export interface D1Like {
  prepare: (sql: string) => {
    bind: (...args: unknown[]) => {
      run: () => Promise<unknown>;
      all: () => Promise<{ results?: unknown[] }>;
      first: <T = unknown>() => Promise<T | null>;
    };
    run: () => Promise<unknown>;
    all: () => Promise<{ results?: unknown[] }>;
    first: <T = unknown>() => Promise<T | null>;
  };
}
export interface RagEnv {
  AI: { run: (model: string, input: unknown) => Promise<unknown> };
  VECTORIZE: VectorizeBinding;
  DB: D1Like;
}

// ---- schema --------------------------------------------------------------
export async function ensureSchema(env: RagEnv): Promise<void> {
  const stmts = [
    `CREATE TABLE IF NOT EXISTS docs (
       id TEXT PRIMARY KEY, title TEXT, source TEXT, n_chunks INTEGER, created_at INTEGER)`,
    `CREATE TABLE IF NOT EXISTS chunks (
       id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, idx INTEGER NOT NULL,
       text TEXT NOT NULL, token_est INTEGER, source TEXT, title TEXT, created_at INTEGER)`,
    `CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id)`,
    // graph tables (used by graph.ts; created here so a single ensureSchema bootstraps all)
    `CREATE TABLE IF NOT EXISTS nodes (
       id TEXT PRIMARY KEY, label TEXT NOT NULL, type TEXT, doc_ids TEXT, updated_at INTEGER)`,
    `CREATE TABLE IF NOT EXISTS edges (
       id TEXT PRIMARY KEY, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL,
       doc_id TEXT, evidence TEXT, weight INTEGER DEFAULT 1, updated_at INTEGER)`,
    `CREATE INDEX IF NOT EXISTS idx_edges_subject ON edges(subject)`,
    `CREATE INDEX IF NOT EXISTS idx_edges_object ON edges(object)`,
    // FTS5 lexical index over chunk text — the BM25 half of hybrid retrieval (§4.1.2).
    // id/doc_id UNINDEXED (stored, not tokenized); `text` is the searchable column.
    `CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(id UNINDEXED, doc_id UNINDEXED, text)`,
  ];
  for (const s of stmts) await env.DB.prepare(s).run();
  // One-time backfill: if a pre-existing deployment has chunks but the FTS index is empty
  // (table just created), mirror chunk text into FTS so lexical search covers legacy data.
  try {
    const fc = await env.DB.prepare(`SELECT COUNT(*) AS n FROM chunks_fts`).first<{ n: number }>();
    const cc = await env.DB.prepare(`SELECT COUNT(*) AS n FROM chunks`).first<{ n: number }>();
    if (Number(fc?.n ?? 0) === 0 && Number(cc?.n ?? 0) > 0) {
      await env.DB.prepare(`INSERT INTO chunks_fts (id, doc_id, text) SELECT id, doc_id, text FROM chunks`).run();
    }
  } catch { /* FTS backfill is best-effort; hybrid degrades to vector-only if unavailable */ }
}

function chunkId(docId: string, idx: number): string {
  return `${docId}::${idx}`;
}

export interface IngestResult {
  doc_id: string;
  n_chunks: number;
  truncated: boolean;
  window_count: number;
  manifest: Array<{ idx: number; token_est: number; preview: string }>;
}

/**
 * Ingest a document: semantic-chunk -> embed -> upsert to Vectorize + store text in D1.
 * Returns a MANIFEST (idx + token estimate + 160-char preview) — NOT the full text. This is
 * the contract that keeps raw corpus text out of the model context window.
 */
export async function ingestDocument(
  env: RagEnv,
  args: { text: string; doc_id: string; title?: string; source?: string; chunkOpts?: ChunkOpts },
): Promise<IngestResult> {
  await ensureSchema(env);
  const embed = (texts: string[]) => embedTexts(env, texts);
  const { chunks, truncated, windowCount } = await semanticChunk(args.text, embed, args.chunkOpts ?? {});
  const now = Date.now();

  // Vectorize upsert (lean metadata)
  if (chunks.length) {
    await env.VECTORIZE.upsert(
      chunks.map((c) => ({
        id: chunkId(args.doc_id, c.idx),
        values: c.vector as number[],
        metadata: { doc_id: args.doc_id, idx: c.idx },
      })),
    );
  }

  // D1 text store. Re-ingest: clear this doc's stale FTS rows first (chunks uses INSERT OR
  // REPLACE by id, but chunks_fts is a separate table that must be cleared by doc_id).
  await env.DB.prepare(`DELETE FROM chunks_fts WHERE doc_id = ?`).bind(args.doc_id).run();
  for (const c of chunks) {
    const cid = chunkId(args.doc_id, c.idx);
    await env.DB.prepare(
      `INSERT OR REPLACE INTO chunks (id, doc_id, idx, text, token_est, source, title, created_at)
       VALUES (?,?,?,?,?,?,?,?)`,
    ).bind(cid, args.doc_id, c.idx, c.text, c.tokenEst,
           args.source ?? null, args.title ?? null, now).run();
    // mirror into the FTS5 lexical index (BM25 half of hybrid retrieval)
    await env.DB.prepare(`INSERT INTO chunks_fts (id, doc_id, text) VALUES (?,?,?)`)
      .bind(cid, args.doc_id, c.text).run();
  }
  await env.DB.prepare(
    `INSERT OR REPLACE INTO docs (id, title, source, n_chunks, created_at) VALUES (?,?,?,?,?)`,
  ).bind(args.doc_id, args.title ?? null, args.source ?? null, chunks.length, now).run();

  return {
    doc_id: args.doc_id,
    n_chunks: chunks.length,
    truncated,
    window_count: windowCount,
    manifest: chunks.map((c) => ({ idx: c.idx, token_est: c.tokenEst, preview: c.text.slice(0, 160) })),
  };
}

export interface RetrievedChunk {
  doc_id: string;
  idx: number;
  score: number;
  text: string;
  title?: string | null;
  source?: string | null;
  /** Retrieval provenance: which arm(s) surfaced this chunk + final stage (rerank/rrf). §12.3. */
  retrieval?: string;
}

/** Cross-encoder reranker (Cloudflare Workers AI). Same AI binding as the bge-m3 embedder. */
export const RERANK_MODEL = "@cf/baai/bge-reranker-base";

function normalizeMatches(raw: unknown): Array<{ id: string; score: number; metadata?: Record<string, unknown> }> {
  const r = raw as Record<string, unknown> | undefined;
  if (r && Array.isArray(r["matches"])) return r["matches"] as never;
  if (Array.isArray(raw)) return raw as never;
  return [];
}

/** FTS5 lexical (BM25) arm of hybrid retrieval. Query is sanitised into an OR of quoted tokens
 *  (so FTS5 operators in user text can't break the MATCH). Returns chunk ids best-first. */
async function lexicalSearch(env: RagEnv, query: string, n: number, docId?: string): Promise<string[]> {
  const tokens = (query.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? []).filter((t) => t.length > 1).slice(0, 24);
  if (!tokens.length) return [];
  const match = tokens.map((t) => `"${t.replace(/"/g, '""')}"`).join(" OR ");
  const sql = docId
    ? `SELECT id FROM chunks_fts WHERE chunks_fts MATCH ? AND doc_id = ? ORDER BY rank LIMIT ?`
    : `SELECT id FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?`;
  const binds: unknown[] = docId ? [match, docId, n] : [match, n];
  const rows = await env.DB.prepare(sql).bind(...binds).all();
  return ((rows.results ?? []) as Array<{ id: string }>).map((r) => r.id);
}

/** Reciprocal Rank Fusion over ranked id lists (k=60, standard). Robust to differing scales
 *  between the vector (cosine) and lexical (BM25) arms — fuses by RANK, not raw score. */
function rrfFuse(lists: string[][], k = 60): Array<{ id: string; score: number }> {
  const score = new Map<string, number>();
  for (const list of lists) list.forEach((id, rank) => score.set(id, (score.get(id) ?? 0) + 1 / (k + rank + 1)));
  return [...score.entries()].map(([id, s]) => ({ id, score: s })).sort((a, b) => b.score - a.score);
}

/** Cross-encoder rerank of candidate texts against the query. Best-effort: returns ranked
 *  {idx,score} (idx = position in `texts`), or null on any error (caller keeps RRF order). */
async function rerankCandidates(env: RagEnv, query: string, texts: string[]): Promise<Array<{ idx: number; score: number }> | null> {
  try {
    const raw = await env.AI.run(RERANK_MODEL, { query, contexts: texts.map((t) => ({ text: t })) }) as Record<string, unknown>;
    const resp = (raw?.["response"] ?? raw?.["result"] ?? raw) as Array<{ id?: number; score?: number }> | undefined;
    if (!Array.isArray(resp) || !resp.length) return null;
    const ranked = resp
      .filter((r) => typeof r.id === "number" && r.id! >= 0 && r.id! < texts.length)
      .map((r) => ({ idx: r.id as number, score: Number(r.score ?? 0) }))
      .sort((a, b) => b.score - a.score);
    return ranked.length ? ranked : null;
  } catch { return null; }
}

/** §8 monitoring pillar — emit one structured retrieval telemetry line to CF Workers logs.
 *  This is an HTTP Worker (not stdio MCP), so console.log is the log stream, not the protocol
 *  (§2.3.2 only constrains stdio). Lets the operator watch recall/precision health over time. */
function logRetrieval(t: Record<string, unknown>): void {
  try { console.log(JSON.stringify({ evt: "anamnesis.retrieval", ...t })); } catch { /* never throw */ }
}

/**
 * Hybrid + multi-query retrieval — the FULL §4.1.1 production pipeline:
 *   [query decomposition: PRIMARY + caller sub-queries]
 *     → per query: vector (bge-m3) ∥ FTS5-BM25
 *     → RRF fusion across ALL queries × arms
 *     → cross-encoder rerank (bge-reranker) against the PRIMARY query
 *     → top-k.
 *
 * `queries[]` (optional) carries the orchestrator's decomposed sub-aspects/synonyms — this is the
 * query-transformation front that maximises RECALL ("miss no detail in the literature"); rerank
 * then restores precision. Each stage degrades gracefully: no FTS → vector-only; reranker error →
 * RRF order; no queries[] → single-query (prior behaviour). Optional `doc_id` scopes all arms.
 */
export async function semanticSearch(
  env: RagEnv,
  args: { query: string; k?: number; doc_id?: string; rerank?: boolean; queries?: string[] },
): Promise<RetrievedChunk[]> {
  await ensureSchema(env);
  const k = Math.min(Math.max(args.k ?? 8, 1), 50);
  // Larger candidate pool than k → maximise RECALL ("miss no detail") before rerank tightens precision.
  const pool = Math.min(Math.max(k * 5, 30), 80);

  // --- query set: PRIMARY + caller-decomposed sub-queries/synonyms (§4.1.1 query transformation).
  //     The orchestrator (Claude) decomposes the complex question; the Worker fuses across all of
  //     them — recall-maximising, no Worker-side LLM call (§12.5: let the strong model decompose). ---
  const primary = args.query;
  const queries = [...new Set([primary, ...((args.queries ?? []).map((q) => (q || "").trim()))].filter(Boolean))].slice(0, 8);

  const lists: string[][] = [];      // every ranked id-list (each query × each arm) for RRF
  const vSet = new Set<string>(), lSet = new Set<string>();
  for (const q of queries) {
    // vector arm
    const qv = await embedOne(env, q);
    const vOpts: Record<string, unknown> = { topK: pool, returnMetadata: "all" };
    if (args.doc_id) vOpts["filter"] = { doc_id: args.doc_id };
    const vIds = normalizeMatches(await env.VECTORIZE.query(qv, vOpts)).map((m) => m.id);
    if (vIds.length) { lists.push(vIds); vIds.forEach((id) => vSet.add(id)); }
    // lexical arm (BM25) — best-effort
    let lIds: string[] = [];
    try { lIds = await lexicalSearch(env, q, pool, args.doc_id); } catch { lIds = []; }
    if (lIds.length) { lists.push(lIds); lIds.forEach((id) => lSet.add(id)); }
  }
  if (!lists.length) { logRetrieval({ queries: queries.length, v: 0, l: 0, hits: 0, mode: "empty" }); return []; }

  // --- RRF fusion across ALL queries × arms ---
  const fused = rrfFuse(lists).slice(0, pool);

  // --- hydrate candidate texts from D1 ---
  const candIds = fused.map((f) => f.id);
  const ph = candIds.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT id, doc_id, idx, text, title, source FROM chunks WHERE id IN (${ph})`,
  ).bind(...candIds).all();
  const byId = new Map<string, Record<string, unknown>>();
  for (const row of (rows.results ?? []) as Array<Record<string, unknown>>) byId.set(String(row["id"]), row);
  const cands = fused.filter((f) => byId.has(f.id));
  if (!cands.length) { logRetrieval({ queries: queries.length, v: vSet.size, l: lSet.size, hits: 0, mode: "no-hydrate" }); return []; }

  // --- cross-encoder rerank against the PRIMARY query (best-effort; floor = RRF order) ---
  let order: Array<{ id: string; score: number }> = cands;
  let reranked = false;
  if (args.rerank !== false && cands.length > 1) {
    const rr = await rerankCandidates(env, primary, cands.map((c) => String(byId.get(c.id)!["text"])));
    if (rr) { order = rr.map((r) => ({ id: cands[r.idx].id, score: r.score })).filter((x) => x.id); reranked = true; }
  }

  // --- assemble top-k with retrieval provenance ---
  const out: RetrievedChunk[] = [];
  for (const c of order.slice(0, k)) {
    const row = byId.get(c.id);
    if (!row) continue;
    const arm = vSet.has(c.id) && lSet.has(c.id) ? "vector+lexical" : vSet.has(c.id) ? "vector" : "lexical";
    out.push({
      doc_id: String(row["doc_id"]),
      idx: Number(row["idx"]),
      score: c.score,
      text: String(row["text"]),
      title: (row["title"] as string) ?? null,
      source: (row["source"] as string) ?? null,
      retrieval: `${arm}→${reranked ? "rerank" : "rrf"}`,
    });
  }
  // §8 monitoring pillar — lightweight retrieval telemetry to CF Workers logs (HTTP Worker; not stdio).
  logRetrieval({ queries: queries.length, v: vSet.size, l: lSet.size, fused: fused.length, hits: out.length, reranked, mode: "hybrid" });
  return out;
}

export async function corpusStats(env: RagEnv): Promise<Record<string, number>> {
  await ensureSchema(env);
  const d = await env.DB.prepare(`SELECT COUNT(*) AS n FROM docs`).first<{ n: number }>();
  const c = await env.DB.prepare(`SELECT COUNT(*) AS n FROM chunks`).first<{ n: number }>();
  const nodes = await env.DB.prepare(`SELECT COUNT(*) AS n FROM nodes`).first<{ n: number }>();
  const edges = await env.DB.prepare(`SELECT COUNT(*) AS n FROM edges`).first<{ n: number }>();
  return {
    docs: Number(d?.n ?? 0), chunks: Number(c?.n ?? 0),
    nodes: Number(nodes?.n ?? 0), edges: Number(edges?.n ?? 0),
  };
}

export interface ForgetResult {
  doc_id: string;
  existed: boolean;
  deleted: { chunks: number; vectors: number; edges: number; nodes_removed: number; nodes_updated: number };
}

/**
 * Forget (hard-delete) a document by doc_id. The clean deletion path the index previously
 * lacked: `ingest_document` only overwrote same-doc_id chunks, leaving stale vectors/graph behind.
 *
 * Deletes, by doc_id:
 *   - Vectorize vectors (by chunk id `${doc_id}::${idx}`, via deleteByIds)
 *   - D1 `chunks` rows  + the `docs` manifest row
 *   - D1 graph `edges` sourced from this doc (edges.doc_id = doc_id)
 *   - D1 graph `nodes` provenance: removes doc_id from the node's doc_ids list; a node that
 *     loses its LAST contributing doc is deleted (orphan), otherwise its doc_ids is updated.
 *     (A node co-cited by another surviving doc is preserved — only its provenance shrinks.)
 *
 * Idempotent: forgetting an unknown doc_id returns existed:false with all-zero counts (no error).
 */
export async function forgetDocument(env: RagEnv, docId: string): Promise<ForgetResult> {
  await ensureSchema(env);

  // 1) chunk ids for this doc (drive both Vectorize delete + count)
  const chunkRows = await env.DB.prepare(`SELECT id FROM chunks WHERE doc_id = ?`).bind(docId).all();
  const chunkIds = ((chunkRows.results ?? []) as Array<{ id: string }>).map((r) => r.id);
  const docRow = await env.DB.prepare(`SELECT id FROM docs WHERE id = ?`).bind(docId).first<{ id: string }>();
  const existed = chunkIds.length > 0 || !!docRow;

  // 2) Vectorize: delete the doc's vectors (bounded batches; CF cap is generous but be safe)
  let vectors = 0;
  if (chunkIds.length && typeof env.VECTORIZE.deleteByIds === "function") {
    for (let i = 0; i < chunkIds.length; i += 1000) {
      await env.VECTORIZE.deleteByIds!(chunkIds.slice(i, i + 1000));
    }
    vectors = chunkIds.length;
  }

  // 3) D1 chunk text + FTS lexical index + manifest
  await env.DB.prepare(`DELETE FROM chunks WHERE doc_id = ?`).bind(docId).run();
  await env.DB.prepare(`DELETE FROM chunks_fts WHERE doc_id = ?`).bind(docId).run();
  await env.DB.prepare(`DELETE FROM docs WHERE id = ?`).bind(docId).run();

  // 4) graph edges sourced from this doc
  const edgeCount = await env.DB.prepare(`SELECT COUNT(*) AS n FROM edges WHERE doc_id = ?`).bind(docId).first<{ n: number }>();
  const edges = Number(edgeCount?.n ?? 0);
  await env.DB.prepare(`DELETE FROM edges WHERE doc_id = ?`).bind(docId).run();

  // 5) graph nodes: shrink provenance; orphan -> delete. LIKE pre-filters, JSON parse confirms
  //    (so a substring false-match never causes a wrong delete).
  let nodes_removed = 0, nodes_updated = 0;
  const needle = `%${JSON.stringify(docId)}%`; // matches the JSON-quoted doc id inside doc_ids
  const nodeRows = await env.DB.prepare(`SELECT id, doc_ids FROM nodes WHERE doc_ids LIKE ?`).bind(needle).all();
  const now = Date.now();
  for (const r of (nodeRows.results ?? []) as Array<{ id: string; doc_ids: string }>) {
    let docIds: string[] = [];
    try { docIds = JSON.parse(r.doc_ids || "[]"); } catch { docIds = []; }
    if (!docIds.includes(docId)) continue; // LIKE false-positive — skip
    const remaining = docIds.filter((d) => d !== docId);
    if (remaining.length === 0) {
      await env.DB.prepare(`DELETE FROM nodes WHERE id = ?`).bind(r.id).run();
      nodes_removed++;
    } else {
      await env.DB.prepare(`UPDATE nodes SET doc_ids = ?, updated_at = ? WHERE id = ?`)
        .bind(JSON.stringify(remaining), now, r.id).run();
      nodes_updated++;
    }
  }

  return { doc_id: docId, existed, deleted: { chunks: chunkIds.length, vectors, edges, nodes_removed, nodes_updated } };
}
