/**
 * rag.ts — Vector store (Cloudflare Vectorize) + chunk/doc text store (D1) for anamnesis-mcp.
 *
 * Design: Vectorize holds ONLY {id, values(1024-d), metadata:{collection, doc_id, idx}} — lean,
 * so we never hit Vectorize's per-vector metadata size ceiling. The chunk TEXT lives in D1
 * (`chunks`). A search returns chunk ids+scores from Vectorize, then we hydrate text from D1
 * by id and POST-FILTER by collection/doc_ids (Vectorize metadata indexes may be absent on
 * an older deploy; D1 is the isolation source of truth).
 *
 * Collection contract: "{plugin}:{kind}:{id}"; missing write collection → `_legacy`.
 * Re-ingest forgets the doc_id first so stale tail chunks/vectors cannot survive a shorter body.
 */

import { embedTexts, embedOne } from "./embed.js";
import { semanticChunk, type ChunkOpts } from "./chunk.js";
import {
  CollectionRequiredError,
  LEGACY_COLLECTION,
  isScratchCollection,
  resolveScopedCollection,
  resolveWriteCollection,
} from "./collection.js";

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
  /** "1" ⇒ an unscoped write/read/delete is an error instead of a `_legacy` bucket or a
   *  cross-tenant scan. See strictScope() for the transition contract. */
  STRICT_COLLECTION?: string;
}

/**
 * Tenancy transition switch (audit findings B2/B3).
 *
 * The server has always ACCEPTED unscoped calls: a missing collection on write silently lands in
 * `_legacy`, and an unscoped semantic_search reads `_legacy` plus every tenant. The only thing
 * preventing that was a set of fail-open Python PreToolUse hooks, which the claude.ai web
 * connector, ChatGPT, Cursor and plain curl never execute — so the contract was unenforced for
 * every client that is not Claude Code.
 *
 * Flipping straight to mandatory would break four plugins plus two sibling MCP servers at once,
 * so the switch ships OFF: violations are recorded as structured log lines (who, which tool,
 * why) and behaviour is unchanged. Once the logs are clean, `STRICT_COLLECTION=1` makes them
 * errors. Evidence first, breakage second.
 */
function strictScope(env: { STRICT_COLLECTION?: string }): boolean {
  return String(env.STRICT_COLLECTION ?? "0") === "1";
}

/** One structured line per unscoped call, so the operator can see who still needs migrating. */
function logScopeViolation(tool: string, detail: Record<string, unknown>): void {
  try {
    console.log(JSON.stringify({ evt: "anamnesis.scope_violation", tool, ...detail }));
  } catch { /* never throw */ }
}

/** Resolve a write collection under the transition contract. */
function writeScope(env: RagEnv, raw: string | undefined, tool: string): string {
  const collection = resolveWriteCollection(raw);
  if (collection === LEGACY_COLLECTION && !(raw ?? "").trim()) {
    if (strictScope(env)) throw new CollectionRequiredError(tool);
    logScopeViolation(tool, { reason: "missing_collection", bucketed_as: LEGACY_COLLECTION });
  }
  return collection;
}

async function tryAlter(env: RagEnv, sql: string): Promise<void> {
  try { await env.DB.prepare(sql).run(); } catch { /* column already exists */ }
}

// ---- schema --------------------------------------------------------------
/**
 * Bootstrap is memoised per isolate. It used to run on EVERY tool call — 7 CREATEs, 7 ALTERs,
 * 4 full-table `UPDATE ... WHERE collection IS NULL` writes and 2 COUNT(*) scans, with
 * hybrid_query paying the whole bill twice (once directly, once via semanticSearch). Measured
 * 2026-09-07: 24 statements per call. That grows into the dominant latency and D1
 * rows-read/written cost as the corpus grows (audit finding A3).
 *
 * A Promise (not a boolean) is memoised so concurrent requests in the same isolate await one
 * bootstrap instead of racing; a failure clears it so the next call retries rather than
 * inheriting a half-built schema.
 */
let schemaInit: Promise<void> | null = null;

export async function ensureSchema(env: RagEnv): Promise<void> {
  if (!schemaInit) {
    schemaInit = bootstrapSchema(env).catch((e: unknown) => { schemaInit = null; throw e; });
  }
  return schemaInit;
}

/** Test-only: forget the memo so a suite can observe bootstrap again. */
export function __resetSchemaMemo(): void { schemaInit = null; }

async function bootstrapSchema(env: RagEnv): Promise<void> {
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

  // Additive collection / TTL / offset columns. ALTER is idempotent via tryAlter.
  await tryAlter(env, `ALTER TABLE docs ADD COLUMN collection TEXT`);
  await tryAlter(env, `ALTER TABLE docs ADD COLUMN expires_at INTEGER`);
  await tryAlter(env, `ALTER TABLE chunks ADD COLUMN collection TEXT`);
  await tryAlter(env, `ALTER TABLE chunks ADD COLUMN char_start INTEGER`);
  await tryAlter(env, `ALTER TABLE chunks ADD COLUMN char_end INTEGER`);
  await tryAlter(env, `ALTER TABLE nodes ADD COLUMN collection TEXT`);
  await tryAlter(env, `ALTER TABLE edges ADD COLUMN collection TEXT`);
  // Evidence accounting (audit finding A10): `weight` counts DISTINCT supporting documents,
  // `assert_count` records how often the orchestrator restated the same triple.
  await tryAlter(env, `ALTER TABLE edges ADD COLUMN doc_ids TEXT`);
  await tryAlter(env, `ALTER TABLE edges ADD COLUMN assert_count INTEGER DEFAULT 1`);

  await env.DB.prepare(`CREATE INDEX IF NOT EXISTS idx_docs_collection ON docs(collection)`).run();
  await env.DB.prepare(`CREATE INDEX IF NOT EXISTS idx_chunks_collection ON chunks(collection)`).run();
  await env.DB.prepare(`CREATE INDEX IF NOT EXISTS idx_nodes_collection ON nodes(collection)`).run();
  await env.DB.prepare(`CREATE INDEX IF NOT EXISTS idx_edges_collection ON edges(collection)`).run();

  // Existing rows (pre-namespace) land in `_legacy`. Never invent another bucket name.
  await env.DB.prepare(`UPDATE docs SET collection = ? WHERE collection IS NULL OR collection = ''`)
    .bind(LEGACY_COLLECTION).run();
  await env.DB.prepare(`UPDATE chunks SET collection = ? WHERE collection IS NULL OR collection = ''`)
    .bind(LEGACY_COLLECTION).run();
  await env.DB.prepare(`UPDATE nodes SET collection = ? WHERE collection IS NULL OR collection = ''`)
    .bind(LEGACY_COLLECTION).run();
  await env.DB.prepare(`UPDATE edges SET collection = ? WHERE collection IS NULL OR collection = ''`)
    .bind(LEGACY_COLLECTION).run();

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

/**
 * Vectorize rejects a vector id longer than 64 bytes (VECTOR_UPSERT_ERROR 40008 "id too long")
 * and our id is `${doc_id}::${idx}`. The Worker used to leave this unchecked, so an over-long
 * doc_id blew up at UPSERT — AFTER the re-ingest had already forgotten the previous version
 * (audit 2026-09-07, findings A7+A8). Validate up front instead, and reserve headroom for the
 * "::" separator plus the chunk index. Clients no longer have to rediscover the cap: marmara-mcp
 * had independently derived its own MAX_DOC_ID for exactly this reason.
 */
export const VECTORIZE_ID_MAX_BYTES = 64;
const CHUNK_SUFFIX_HEADROOM = 8; // "::" + up to 6 digits of idx
export const MAX_DOC_ID_BYTES = VECTORIZE_ID_MAX_BYTES - CHUNK_SUFFIX_HEADROOM;

/** Upper bound on a single ingest body. Without it the Worker would embed up to 400 windows of
 *  an arbitrarily large payload and only then truncate (audit finding A12). */
export const MAX_TEXT_BYTES = 1_000_000;

function assertTextFits(text: string): void {
  // UTF-8 bytes >= chars, so a char count over the cap is already over — skip the encode.
  const bytes = text.length > MAX_TEXT_BYTES ? text.length : new TextEncoder().encode(text).length;
  if (bytes > MAX_TEXT_BYTES) {
    throw new Error(
      `text too large: ~${bytes} bytes, max ${MAX_TEXT_BYTES}. Split the document and ingest ` +
      `the parts under separate doc_ids (or use offset/next_offset to continue).`,
    );
  }
}

function assertDocIdFits(docId: string): void {
  const bytes = new TextEncoder().encode(docId).length;
  if (bytes > MAX_DOC_ID_BYTES) {
    throw new Error(
      `doc_id too long: ${bytes} bytes, max ${MAX_DOC_ID_BYTES} (chunk ids are ` +
      `"<doc_id>::<idx>" and Vectorize caps a vector id at ${VECTORIZE_ID_MAX_BYTES} bytes). ` +
      `Shorten the id — e.g. keep a readable prefix and append a hash tail.`,
    );
  }
}

function uniqueDocIds(docId?: string, docIds?: string[]): string[] | undefined {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const raw of [docId, ...(docIds ?? [])]) {
    const s = (raw ?? "").trim();
    if (!s || seen.has(s)) continue;
    seen.add(s);
    out.push(s);
  }
  return out.length ? out : undefined;
}

function nowMs(): number { return Date.now(); }

export interface IngestResult {
  doc_id: string;
  collection: string;
  n_chunks: number;
  truncated: boolean;
  window_count: number;
  /** Absolute offset in `text` up to which this call indexed. */
  chars_indexed: number;
  /** Full length of the supplied `text`. `chars_indexed < chars_total` ⇒ the tail is NOT indexed. */
  chars_total: number;
  /** Resume position when truncated; null when the document was fully indexed. */
  next_offset: number | null;
  expires_at?: number | null;
  manifest: Array<{ idx: number; token_est: number; preview: string; char_start: number; char_end: number }>;
}

/**
 * Ingest a document: forget prior same-id rows → semantic-chunk → embed → Vectorize + D1.
 * Returns a MANIFEST (idx + token estimate + 160-char preview) — NOT the full text.
 */
export async function ingestDocument(
  env: RagEnv,
  args: {
    text: string;
    doc_id: string;
    collection?: string;
    title?: string;
    source?: string;
    ttl_hours?: number;
    offset?: number;
    chunkOpts?: ChunkOpts;
  },
): Promise<IngestResult> {
  await ensureSchema(env);
  const collection = writeScope(env, args.collection, "ingest_document");
  assertDocIdFits(args.doc_id);
  assertTextFits(args.text);

  // Chunk BEFORE forgetting. Embedding is the expensive, failure-prone step (Workers AI outage,
  // rate limit); doing it first means a failed re-ingest leaves the previous version intact
  // instead of deleting it and then throwing (audit finding A7). Re-ingest still MUST forget
  // before writing — INSERT OR REPLACE by chunk id leaves a stale tail when the new body
  // produces fewer chunks (idx 5..N would survive).
  const embed = (texts: string[]) => embedTexts(env, texts);
  const chunkOpts: ChunkOpts = { ...(args.chunkOpts ?? {}) };
  if (args.offset !== undefined) chunkOpts.offset = args.offset;
  const { chunks, truncated, windowCount, charsIndexed } = await semanticChunk(args.text, embed, chunkOpts);

  await forgetDocument(env, args.doc_id, collection, { adoptLegacy: true });
  const now = nowMs();
  let expiresAt: number | null = null;
  if (typeof args.ttl_hours === "number" && args.ttl_hours > 0 && isScratchCollection(collection)) {
    expiresAt = now + Math.round(args.ttl_hours * 3600 * 1000);
  }

  const located = chunks.map((c) => ({ ...c, char_start: c.charStart, char_end: c.charEnd }));

  if (located.length) {
    await env.VECTORIZE.upsert(
      located.map((c) => ({
        id: chunkId(args.doc_id, c.idx),
        values: c.vector as number[],
        metadata: { collection, doc_id: args.doc_id, idx: c.idx },
      })),
    );
  }

  for (const c of located) {
    const cid = chunkId(args.doc_id, c.idx);
    await env.DB.prepare(
      `INSERT OR REPLACE INTO chunks
         (id, doc_id, idx, text, token_est, source, title, created_at, collection, char_start, char_end)
       VALUES (?,?,?,?,?,?,?,?,?,?,?)`,
    ).bind(cid, args.doc_id, c.idx, c.text, c.tokenEst,
           args.source ?? null, args.title ?? null, now, collection, c.char_start, c.char_end).run();
    await env.DB.prepare(`INSERT INTO chunks_fts (id, doc_id, text) VALUES (?,?,?)`)
      .bind(cid, args.doc_id, c.text).run();
  }
  await env.DB.prepare(
    `INSERT OR REPLACE INTO docs (id, title, source, n_chunks, created_at, collection, expires_at)
     VALUES (?,?,?,?,?,?,?)`,
  ).bind(args.doc_id, args.title ?? null, args.source ?? null, located.length, now, collection, expiresAt).run();

  return {
    doc_id: args.doc_id,
    collection,
    n_chunks: located.length,
    truncated,
    window_count: windowCount,
    chars_indexed: charsIndexed,
    chars_total: args.text.length,
    next_offset: truncated ? charsIndexed : null,
    expires_at: expiresAt,
    manifest: located.map((c) => ({
      idx: c.idx, token_est: c.tokenEst, preview: c.text.slice(0, 160),
      char_start: c.char_start, char_end: c.char_end,
    })),
  };
}

export interface RetrievedChunk {
  doc_id: string;
  idx: number;
  score: number;
  text: string;
  title?: string | null;
  source?: string | null;
  collection?: string;
  char_start?: number | null;
  char_end?: number | null;
  /** Retrieval provenance: which arm(s) surfaced this chunk + final stage (rerank/rrf). §12.3. */
  retrieval?: string;
  /** Which SCALE `score` is on. A cross-encoder score and an RRF score (~0.01-0.05) are not
   *  comparable, and before this field the only hint was a suffix inside `retrieval` (A11). */
  score_kind?: "rerank" | "rrf";
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
function buildFtsMatch(query: string): string | null {
  const tokens = (query.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? []).filter((t) => t.length > 1).slice(0, 24);
  if (!tokens.length) return null;
  return tokens.map((t) => `"${t.replace(/"/g, '""')}"`).join(" OR ");
}

async function lexicalSearch(
  env: RagEnv,
  query: string,
  n: number,
  scope: { collection?: string; docIds?: string[] },
): Promise<string[]> {
  const match = buildFtsMatch(query);
  if (match === null) return [];
  const clauses = [`chunks_fts MATCH ?`];
  const binds: unknown[] = [match];
  // Isolation happens on the chunks table (FTS has no collection column — migrate-safe).
  if (scope.collection) {
    clauses.push(`c.collection = ?`);
    binds.push(scope.collection);
  }
  if (scope.docIds?.length === 1) {
    clauses.push(`c.doc_id = ?`);
    binds.push(scope.docIds[0]);
  } else if (scope.docIds && scope.docIds.length > 1) {
    clauses.push(`c.doc_id IN (${scope.docIds.map(() => "?").join(",")})`);
    binds.push(...scope.docIds);
  }
  clauses.push(`(d.expires_at IS NULL OR d.expires_at > ?)`);
  binds.push(nowMs());
  binds.push(n);
  const sql =
    `SELECT f.id AS id FROM chunks_fts f
     INNER JOIN chunks c ON c.id = f.id
     INNER JOIN docs d ON d.id = c.doc_id
     WHERE ${clauses.join(" AND ")}
     ORDER BY rank LIMIT ?`;
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
 *  (§2.3.2 only constrains stdio). Lets the operator watch recall/precision health over time.
 *  Never logs secret values or full chunk text. */
function logRetrieval(t: Record<string, unknown>): void {
  try { console.log(JSON.stringify({ evt: "anamnesis.retrieval", ...t })); } catch { /* never throw */ }
}

function vectorFilter(collection?: string, docIds?: string[]): Record<string, unknown> | undefined {
  // D1 post-filter remains the ISOLATION guarantee; this filter is about RECALL. Sending only
  // `collection` when the caller narrowed to several doc_ids made Vectorize return an unfiltered
  // top-K over the whole collection, which D1 then mostly discarded — recall collapsed on exactly
  // the `doc_ids=[...]` path the plugin contracts prescribe (audit finding A5). Vectorize metadata
  // filters support `$in`, so the narrowing travels with the query.
  const filter: Record<string, unknown> = {};
  if (collection) filter["collection"] = collection;
  if (docIds?.length === 1) filter["doc_id"] = docIds[0];
  else if (docIds && docIds.length > 1) filter["doc_id"] = { $in: docIds };
  return Object.keys(filter).length ? filter : undefined;
}

/**
 * Hybrid + multi-query retrieval — the FULL §4.1.1 production pipeline:
 *   [query decomposition: PRIMARY + caller sub-queries]
 *     → per query: vector (bge-m3) ∥ FTS5-BM25
 *     → RRF fusion across ALL queries × arms
 *     → cross-encoder rerank (bge-reranker) against the PRIMARY query
 *     → top-k.
 *
 * Scope: `collection` and/or `doc_id` / `doc_ids[]`. Unscoped (neither) is kept for
 * compat and CAN hit `_legacy` plus every tenant — Evidentia guard must still DENY it.
 * Isolation is enforced at D1 hydrate even if Vectorize metadata indexes are missing.
 */
export interface RetrievalResult {
  chunks: RetrievedChunk[];
  /** Non-null when an arm was lost. "vector_unavailable" = every query's embed call failed and
   *  the answer came from FTS5/BM25 alone. Surfaced so the caller can say so instead of
   *  silently presenting a half-pipeline result as a full one (audit finding A6). */
  degraded: "vector_unavailable" | null;
}

/** Chunks only — the long-standing signature, kept for callers that do not need diagnostics. */
export async function semanticSearch(
  env: RagEnv,
  args: {
    query: string;
    k?: number;
    doc_id?: string;
    doc_ids?: string[];
    collection?: string;
    rerank?: boolean;
    queries?: string[];
  },
): Promise<RetrievedChunk[]> {
  return (await hybridRetrieve(env, args)).chunks;
}

export async function hybridRetrieve(
  env: RagEnv,
  args: {
    query: string;
    k?: number;
    doc_id?: string;
    doc_ids?: string[];
    collection?: string;
    rerank?: boolean;
    queries?: string[];
  },
): Promise<RetrievalResult> {
  await ensureSchema(env);
  const k = Math.min(Math.max(args.k ?? 8, 1), 50);
  const pool = Math.min(Math.max(k * 5, 30), 80);
  const collection = resolveScopedCollection(args.collection);
  const docIds = uniqueDocIds(args.doc_id, args.doc_ids);
  if (!collection && !docIds) {
    if (strictScope(env)) throw new CollectionRequiredError("semantic_search");
    logScopeViolation("semantic_search", { reason: "unscoped_read", reads: "_legacy + all tenants" });
  }

  const primary = args.query;
  const queries = [...new Set([primary, ...((args.queries ?? []).map((q) => (q || "").trim()))].filter(Boolean))].slice(0, 8);

  const lists: string[][] = [];
  const vSet = new Set<string>(), lSet = new Set<string>();
  const vFilter = vectorFilter(collection, docIds);
  let vectorFailures = 0;
  for (const q of queries) {
    // The vector arm is best-effort, exactly like the lexical arm below. It used to be the one
    // unguarded await in the pipeline, so a Workers AI outage threw the whole search away even
    // though FTS5 alone could have answered it (audit finding A6).
    let vIds: string[] = [];
    try {
      const qv = await embedOne(env, q);
      const vOpts: Record<string, unknown> = { topK: pool, returnMetadata: "all" };
      if (vFilter) vOpts["filter"] = vFilter;
      vIds = normalizeMatches(await env.VECTORIZE.query(qv, vOpts)).map((m) => m.id);
    } catch { vectorFailures++; }
    if (vIds.length) { lists.push(vIds); vIds.forEach((id) => vSet.add(id)); }
    let lIds: string[] = [];
    try { lIds = await lexicalSearch(env, q, pool, { collection, docIds }); } catch { lIds = []; }
    if (lIds.length) { lists.push(lIds); lIds.forEach((id) => lSet.add(id)); }
  }
  const degraded: RetrievalResult["degraded"] =
    vectorFailures === queries.length ? "vector_unavailable" : null;

  if (!lists.length) {
    logRetrieval({ queries: queries.length, v: 0, l: 0, hits: 0, mode: "empty", degraded, collection: collection ?? null });
    return { chunks: [], degraded };
  }

  const fused = rrfFuse(lists).slice(0, pool);
  const candIds = fused.map((f) => f.id);
  const ph = candIds.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT c.id, c.doc_id, c.idx, c.text, c.title, c.source, c.collection,
            c.char_start, c.char_end, d.expires_at
       FROM chunks c
       LEFT JOIN docs d ON d.id = c.doc_id
      WHERE c.id IN (${ph})`,
  ).bind(...candIds).all();
  const byId = new Map<string, Record<string, unknown>>();
  const now = nowMs();
  const docSet = docIds ? new Set(docIds) : null;
  for (const row of (rows.results ?? []) as Array<Record<string, unknown>>) {
    const exp = row["expires_at"];
    if (exp != null && Number(exp) > 0 && Number(exp) <= now) continue;
    if (collection && String(row["collection"] ?? LEGACY_COLLECTION) !== collection) continue;
    if (docSet && !docSet.has(String(row["doc_id"]))) continue;
    byId.set(String(row["id"]), row);
  }
  const cands = fused.filter((f) => byId.has(f.id));
  if (!cands.length) {
    logRetrieval({ queries: queries.length, v: vSet.size, l: lSet.size, hits: 0, mode: "no-hydrate", degraded, collection: collection ?? null });
    return { chunks: [], degraded };
  }

  let order: Array<{ id: string; score: number }> = cands;
  let reranked = false;
  if (args.rerank !== false && cands.length > 1) {
    const rr = await rerankCandidates(env, primary, cands.map((c) => String(byId.get(c.id)!["text"])));
    if (rr) { order = rr.map((r) => ({ id: cands[r.idx].id, score: r.score })).filter((x) => x.id); reranked = true; }
  }

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
      collection: String(row["collection"] ?? collection ?? LEGACY_COLLECTION),
      char_start: row["char_start"] == null ? null : Number(row["char_start"]),
      char_end: row["char_end"] == null ? null : Number(row["char_end"]),
      retrieval: `${arm}→${reranked ? "rerank" : "rrf"}`,
      score_kind: reranked ? "rerank" : "rrf",
    });
  }
  logRetrieval({
    queries: queries.length, v: vSet.size, l: lSet.size, fused: fused.length,
    hits: out.length, reranked, mode: "hybrid", degraded, collection: collection ?? null,
  });
  return { chunks: out, degraded };
}

export async function listDocs(
  env: RagEnv,
  collection: string,
): Promise<{ collection: string; docs: Array<Record<string, unknown>> }> {
  await ensureSchema(env);
  const scoped = resolveScopedCollection(collection);
  if (!scoped) throw new Error("list_docs requires collection");
  const now = nowMs();
  const rows = await env.DB.prepare(
    `SELECT id, title, source, n_chunks, created_at, collection, expires_at
       FROM docs WHERE collection = ?
         AND (expires_at IS NULL OR expires_at > ?)
       ORDER BY created_at DESC`,
  ).bind(scoped, now).all();
  return { collection: scoped, docs: (rows.results ?? []) as Array<Record<string, unknown>> };
}

export async function corpusStats(
  env: RagEnv,
  collection?: string,
): Promise<Record<string, unknown>> {
  await ensureSchema(env);
  const scoped = resolveScopedCollection(collection);
  if (!scoped) {
    const d = await env.DB.prepare(`SELECT COUNT(*) AS n FROM docs`).first<{ n: number }>();
    const c = await env.DB.prepare(`SELECT COUNT(*) AS n FROM chunks`).first<{ n: number }>();
    const nodes = await env.DB.prepare(`SELECT COUNT(*) AS n FROM nodes`).first<{ n: number }>();
    const edges = await env.DB.prepare(`SELECT COUNT(*) AS n FROM edges`).first<{ n: number }>();
    return {
      scope: "global",
      note: "Global observation only — not a working set. Pass collection for a tenant count.",
      docs: Number(d?.n ?? 0), chunks: Number(c?.n ?? 0),
      nodes: Number(nodes?.n ?? 0), edges: Number(edges?.n ?? 0),
    };
  }
  const d = await env.DB.prepare(`SELECT COUNT(*) AS n FROM docs WHERE collection = ?`).bind(scoped).first<{ n: number }>();
  const c = await env.DB.prepare(`SELECT COUNT(*) AS n FROM chunks WHERE collection = ?`).bind(scoped).first<{ n: number }>();
  const nodes = await env.DB.prepare(`SELECT COUNT(*) AS n FROM nodes WHERE collection = ?`).bind(scoped).first<{ n: number }>();
  const edges = await env.DB.prepare(`SELECT COUNT(*) AS n FROM edges WHERE collection = ?`).bind(scoped).first<{ n: number }>();
  return {
    scope: "collection", collection: scoped,
    docs: Number(d?.n ?? 0), chunks: Number(c?.n ?? 0),
    nodes: Number(nodes?.n ?? 0), edges: Number(edges?.n ?? 0),
  };
}

export interface ForgetResult {
  doc_id: string;
  existed: boolean;
  deleted: { chunks: number; vectors: number; edges: number; nodes_removed: number; nodes_updated: number };
}

async function deleteVectors(env: RagEnv, chunkIds: string[]): Promise<number> {
  if (!chunkIds.length || typeof env.VECTORIZE.deleteByIds !== "function") return 0;
  for (let i = 0; i < chunkIds.length; i += 1000) {
    await env.VECTORIZE.deleteByIds!(chunkIds.slice(i, i + 1000));
  }
  return chunkIds.length;
}

async function shrinkNodesForDoc(env: RagEnv, docId: string, collection?: string): Promise<{ removed: number; updated: number }> {
  let nodes_removed = 0, nodes_updated = 0;
  const needle = `%${JSON.stringify(docId)}%`;
  const sql = collection
    ? `SELECT id, doc_ids FROM nodes WHERE collection = ? AND doc_ids LIKE ?`
    : `SELECT id, doc_ids FROM nodes WHERE doc_ids LIKE ?`;
  const binds = collection ? [collection, needle] : [needle];
  const nodeRows = await env.DB.prepare(sql).bind(...binds).all();
  const now = nowMs();
  for (const r of (nodeRows.results ?? []) as Array<{ id: string; doc_ids: string }>) {
    let docIds: string[] = [];
    try { docIds = JSON.parse(r.doc_ids || "[]"); } catch { docIds = []; }
    if (!docIds.includes(docId)) continue;
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
  return { removed: nodes_removed, updated: nodes_updated };
}

/**
 * Forget (hard-delete) a document by doc_id. Stays the per-document API;
 * `forget_by_prefix` is NOT a real tool — use `forget_collection` for a working set.
 *
 * `expectCollection` is the OWNERSHIP CHECK. Without it this tool took only a doc_id, resolved
 * the collection from the row and deleted it, so any authenticated caller who knew an id could
 * destroy another tenant's document — and the only thing standing in the way was a fail-open
 * Python PreToolUse hook that the claude.ai web connector, ChatGPT, Cursor and plain curl never
 * run (audit finding B1). When supplied, a mismatch is refused rather than silently obeyed.
 *
 * `adoptLegacy` exists for the re-ingest path only: a document sitting in the pre-namespace
 * `_legacy` bucket may be claimed by a properly scoped ingest, which is how old rows migrate.
 */
export async function forgetDocument(
  env: RagEnv, docId: string, expectCollection?: string, opts: { adoptLegacy?: boolean } = {},
): Promise<ForgetResult> {
  await ensureSchema(env);

  const chunkRows = await env.DB.prepare(`SELECT id FROM chunks WHERE doc_id = ?`).bind(docId).all();
  const chunkIds = ((chunkRows.results ?? []) as Array<{ id: string }>).map((r) => r.id);
  const docRow = await env.DB.prepare(`SELECT id, collection FROM docs WHERE id = ?`).bind(docId)
    .first<{ id: string; collection?: string }>();
  const existed = chunkIds.length > 0 || !!docRow;
  const collection = (docRow?.collection as string | undefined) || undefined;

  if (!expectCollection) {
    if (strictScope(env)) throw new CollectionRequiredError("forget_document");
    logScopeViolation("forget_document", { reason: "unscoped_delete", doc_id: docId });
  }

  if (expectCollection && docRow) {
    const want = resolveScopedCollection(expectCollection);
    const owner = collection || LEGACY_COLLECTION;
    const adoptable = opts.adoptLegacy === true && owner === LEGACY_COLLECTION;
    if (want && owner !== want && !adoptable) {
      logRetrieval({
        evt_kind: "scope_violation", tool: "forget_document",
        doc_id: docId, owner, requested: want,
      });
      throw new Error(
        `forget_document refused: doc_id '${docId}' belongs to collection '${owner}', ` +
        `not '${want}'. A document is only deletable by the collection that owns it.`,
      );
    }
  }

  const vectors = await deleteVectors(env, chunkIds);

  await env.DB.prepare(`DELETE FROM chunks WHERE doc_id = ?`).bind(docId).run();
  await env.DB.prepare(`DELETE FROM chunks_fts WHERE doc_id = ?`).bind(docId).run();
  await env.DB.prepare(`DELETE FROM docs WHERE id = ?`).bind(docId).run();

  const edgeCount = await env.DB.prepare(`SELECT COUNT(*) AS n FROM edges WHERE doc_id = ?`).bind(docId).first<{ n: number }>();
  const edges = Number(edgeCount?.n ?? 0);
  await env.DB.prepare(`DELETE FROM edges WHERE doc_id = ?`).bind(docId).run();

  const nodes = await shrinkNodesForDoc(env, docId, collection);

  return { doc_id: docId, existed, deleted: { chunks: chunkIds.length, vectors, edges, nodes_removed: nodes.removed, nodes_updated: nodes.updated } };
}

export interface ForgetCollectionResult {
  collection: string;
  existed: boolean;
  deleted: { docs: number; chunks: number; vectors: number; edges: number; nodes: number };
}

/**
 * Idempotent collection wipe. SQL + Vectorize deleteByIds for THIS collection only.
 * Never deletes another collection. Empty/unknown collection → existed:false, zeros.
 */
export async function forgetCollection(env: RagEnv, collectionRaw: string): Promise<ForgetCollectionResult> {
  await ensureSchema(env);
  const collection = resolveScopedCollection(collectionRaw);
  if (!collection) throw new Error("forget_collection requires collection");

  const chunkRows = await env.DB.prepare(`SELECT id FROM chunks WHERE collection = ?`).bind(collection).all();
  const chunkIds = ((chunkRows.results ?? []) as Array<{ id: string }>).map((r) => r.id);
  const docCount = await env.DB.prepare(`SELECT COUNT(*) AS n FROM docs WHERE collection = ?`).bind(collection).first<{ n: number }>();
  const edgeCount = await env.DB.prepare(`SELECT COUNT(*) AS n FROM edges WHERE collection = ?`).bind(collection).first<{ n: number }>();
  const nodeCount = await env.DB.prepare(`SELECT COUNT(*) AS n FROM nodes WHERE collection = ?`).bind(collection).first<{ n: number }>();
  const docs = Number(docCount?.n ?? 0);
  const edges = Number(edgeCount?.n ?? 0);
  const nodes = Number(nodeCount?.n ?? 0);
  const existed = chunkIds.length > 0 || docs > 0 || edges > 0 || nodes > 0;

  const vectors = await deleteVectors(env, chunkIds);

  // FTS has no collection column — delete by the chunk ids we already listed, then
  // also by doc_ids of this collection (covers a missed FTS row).
  const docRows = await env.DB.prepare(`SELECT id FROM docs WHERE collection = ?`).bind(collection).all();
  const docIds = ((docRows.results ?? []) as Array<{ id: string }>).map((r) => r.id);
  for (const did of docIds) {
    await env.DB.prepare(`DELETE FROM chunks_fts WHERE doc_id = ?`).bind(did).run();
  }
  await env.DB.prepare(`DELETE FROM chunks WHERE collection = ?`).bind(collection).run();
  await env.DB.prepare(`DELETE FROM docs WHERE collection = ?`).bind(collection).run();
  await env.DB.prepare(`DELETE FROM edges WHERE collection = ?`).bind(collection).run();
  await env.DB.prepare(`DELETE FROM nodes WHERE collection = ?`).bind(collection).run();

  return {
    collection,
    existed,
    deleted: { docs, chunks: chunkIds.length, vectors, edges, nodes },
  };
}

export const SYNTHESIZE_GUIDANCE =
  "Synthesize ONLY from these chunks; cite doc_id::idx. Do not use unlisted documents.";

// Pure helpers surfaced for test/rag.test.ts. Added 2026-08-07: anamnesis carried helper suites
// for chunk.ts and graph.ts but NONE for rag.ts, leaving the hybrid-retrieval ranking (rrfFuse)
// and the FTS5 injection guard (buildFtsMatch) unpinned.
export const __testing = { chunkId, normalizeMatches, rrfFuse, buildFtsMatch, uniqueDocIds, vectorFilter };
