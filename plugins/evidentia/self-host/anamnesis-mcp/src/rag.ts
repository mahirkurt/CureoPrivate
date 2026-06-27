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
  ];
  for (const s of stmts) await env.DB.prepare(s).run();
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

  // D1 text store
  for (const c of chunks) {
    await env.DB.prepare(
      `INSERT OR REPLACE INTO chunks (id, doc_id, idx, text, token_est, source, title, created_at)
       VALUES (?,?,?,?,?,?,?,?)`,
    ).bind(chunkId(args.doc_id, c.idx), args.doc_id, c.idx, c.text, c.tokenEst,
           args.source ?? null, args.title ?? null, now).run();
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
}

function normalizeMatches(raw: unknown): Array<{ id: string; score: number; metadata?: Record<string, unknown> }> {
  const r = raw as Record<string, unknown> | undefined;
  if (r && Array.isArray(r["matches"])) return r["matches"] as never;
  if (Array.isArray(raw)) return raw as never;
  return [];
}

/** Vector top-k retrieval with D1 text hydration. Optional doc_id scoping via metadata filter. */
export async function semanticSearch(
  env: RagEnv,
  args: { query: string; k?: number; doc_id?: string },
): Promise<RetrievedChunk[]> {
  await ensureSchema(env);
  const k = Math.min(Math.max(args.k ?? 8, 1), 50);
  const qv = await embedOne(env, args.query);
  const opts: Record<string, unknown> = { topK: k, returnMetadata: "all" };
  if (args.doc_id) opts["filter"] = { doc_id: args.doc_id };
  const raw = await env.VECTORIZE.query(qv, opts);
  const matches = normalizeMatches(raw);
  if (!matches.length) return [];

  const ids = matches.map((m) => m.id);
  const placeholders = ids.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT id, doc_id, idx, text, title, source FROM chunks WHERE id IN (${placeholders})`,
  ).bind(...ids).all();
  const byId = new Map<string, Record<string, unknown>>();
  for (const row of (rows.results ?? []) as Array<Record<string, unknown>>) byId.set(String(row["id"]), row);

  const out: RetrievedChunk[] = [];
  for (const m of matches) {
    const row = byId.get(m.id);
    if (!row) continue;
    out.push({
      doc_id: String(row["doc_id"]),
      idx: Number(row["idx"]),
      score: m.score,
      text: String(row["text"]),
      title: (row["title"] as string) ?? null,
      source: (row["source"] as string) ?? null,
    });
  }
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

  // 3) D1 chunk text + manifest
  await env.DB.prepare(`DELETE FROM chunks WHERE doc_id = ?`).bind(docId).run();
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
