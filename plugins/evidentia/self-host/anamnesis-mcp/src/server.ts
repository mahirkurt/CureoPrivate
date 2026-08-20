/**
 * server.ts — anamnesis-mcp tool layer (Cureonics Family A).
 *
 * WHY THIS WORKER EXISTS: tool outputs (full-text articles/books from Annas, EuropePMC OA,
 * Paper Search; large MCP result sets) overflow the model context window, which causes the
 * "incomplete / inconsistent" evaluations the operator wants eliminated. anamnesis is the
 * retrieval substrate: text is INGESTED (semantic-chunked + embedded + graphed) and then only
 * the bounded, query-relevant, provenance-stamped slice is surfaced — never the raw corpus.
 *
 * Tools:
 *   ingest_document   — semantic-chunk + embed + store; collection required for new clients
 *   semantic_search   — HYBRID; accept collection and/or doc_id / doc_ids[]
 *   upsert_triples    — collection-scoped graph write (nodeKey/edgeId include collection)
 *   graph_neighbors   — n-hop expansion; collection required
 *   subgraph          — induced edges; collection required
 *   hybrid_query      — FLAGSHIP; collection required (unscoped → MCP error)
 *   list_docs         — docs in one collection
 *   corpus_stats      — omit collection = global observation only (not a working set)
 *   forget_document   — hard-delete one doc_id (stays; forget_by_prefix is NOT the API)
 *   forget_collection — idempotent SQL + Vectorize deleteByIds for one collection
 *
 * Honest scope: extraction is Claude-in-the-loop (upsert_triples); Microsoft-GraphRAG global
 * community summarization is a documented Cloud Run add-on (NOT shipped as a weak in-Worker
 * approximation). Read paths carry readOnlyHint; ingest/upsert are mutations.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  ingestDocument, semanticSearch, corpusStats, forgetDocument, forgetCollection, listDocs,
  SYNTHESIZE_GUIDANCE, type RagEnv, type RetrievedChunk,
} from "./rag.js";
import { upsertTriples, neighbors, subgraph, edgesByDocs, type GraphEnv, type Triple, type GraphEdge } from "./graph.js";
import { CollectionRequiredError, InvalidCollectionError, requireCollection } from "./collection.js";
import pkg from "../package.json";

export type AnamEnv = RagEnv & GraphEnv;

const SUBSTRATE_NOTE =
  "anamnesis substrate: this is a context-window-bounded retrieval slice, not the full corpus. " +
  "Every chunk carries {doc_id, idx, score} provenance; cite at chunk granularity (doc_id::idx). " +
  "Graph triples were extracted by the orchestrator (Claude-in-the-loop), not a clinical knowledge " +
  "base — treat relations as evidence pointers to verify, not adjudicated facts. " +
  "collection = {plugin}:{run|sess|lib}:{id}; Evidentia scratch = evidentia:run:<12hex>. " +
  "Unscoped semantic_search (no collection and no doc_id/doc_ids) can hit _legacy + all tenants " +
  "and is kept only for compat — clients MUST scope.";

const ok = (obj: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(obj, null, 2) }] });
const err = (msg: string) => ({ isError: true, content: [{ type: "text" as const, text: msg }] });

function toolErr(e: unknown, tool: string): ReturnType<typeof err> {
  const msg = e instanceof Error ? e.message : String(e);
  if (e instanceof CollectionRequiredError || e instanceof InvalidCollectionError) return err(msg);
  return err(`${tool} failed: ${msg}`);
}

export interface HybridQueryArgs {
  query: string;
  collection: string;
  queries?: string[];
  k?: number;
  doc_id?: string;
  doc_ids?: string[];
  seed_entities?: string[];
  hops?: number;
  per_chunk_chars?: number;
  max_edges?: number;
}

/** Flagship retrieval. Unscoped (missing collection) throws CollectionRequiredError. */
export async function runHybridQuery(env: AnamEnv, a: HybridQueryArgs): Promise<Record<string, unknown>> {
  const collection = requireCollection(a.collection, "hybrid_query");
  const k = a.k ?? 8;
  const perChunk = a.per_chunk_chars ?? 1100;
  const maxEdges = a.max_edges ?? 40;

  const chunks: RetrievedChunk[] = await semanticSearch(env, {
    query: a.query, queries: a.queries, k, collection,
    doc_id: a.doc_id, doc_ids: a.doc_ids,
  });
  const docIds = [...new Set(chunks.map((c) => c.doc_id))];

  const docEdges = await edgesByDocs(env, docIds, maxEdges, collection);

  const seedEdges: GraphEdge[] = [];
  for (const ent of a.seed_entities ?? []) {
    const n = await neighbors(env, ent, a.hops ?? 1, Math.ceil(maxEdges / 2), collection);
    if (n.found) seedEdges.push(...n.edges);
  }

  const seen = new Set<string>();
  const graph = [...docEdges, ...seedEdges].filter((e) => {
    const key = `${e.subject}|${e.predicate}|${e.object}`;
    if (seen.has(key)) return false; seen.add(key); return true;
  }).slice(0, maxEdges);

  const bundleChunks = chunks.map((c) => ({
    doc_id: c.doc_id, idx: c.idx, score: Number(c.score.toFixed(4)),
    title: c.title ?? undefined, source: c.source ?? undefined,
    collection: c.collection ?? collection,
    char_start: c.char_start ?? undefined, char_end: c.char_end ?? undefined,
    text: c.text.length > perChunk ? c.text.slice(0, perChunk) + " …[truncated]" : c.text,
  }));

  const approxTokens =
    bundleChunks.reduce((s, c) => s + Math.round(c.text.length / 4), 0) +
    graph.length * 12;

  return {
    query: a.query,
    collection,
    retrieval: { pipeline: "vector∥bm25→rrf→rerank", k, chunks: bundleChunks.length, graph_edges: graph.length, docs: docIds },
    chunks: bundleChunks,
    graph,
    approx_token_budget: approxTokens,
    guidance: SYNTHESIZE_GUIDANCE,
    note: SUBSTRATE_NOTE,
  };
}

export function registerTools(server: McpServer, env: AnamEnv): void {
  // ---- ingest_document ----------------------------------------------------
  server.tool(
    "ingest_document",
    "Semantic-chunk + embed (bge-m3) + store a document into the anamnesis index (Vectorize + D1). " +
      "New clients MUST pass collection={plugin}:{run|sess|lib}:{id} (Evidentia scratch: " +
      "evidentia:run:<12hex>). Missing collection stores `_legacy` (compat). Re-ingest forgets " +
      "that doc_id first so stale tail chunks cannot survive a shorter body. Optional ttl_hours " +
      "on scratch (run/sess). Returns a MANIFEST — NOT the full text. " + SUBSTRATE_NOTE,
    {
      text: z.string().describe("Full document text to ingest (article body, book chapter, etc.)"),
      doc_id: z.string().describe("Stable id, e.g. a DOI or 'cochrane-handbook-ch8'. Re-ingest overwrites after forget."),
      collection: z.string().optional().describe("Tenant working set: {plugin}:{run|sess|lib}:{id}. Omit → _legacy."),
      title: z.string().optional().describe("Human title for provenance"),
      source: z.string().optional().describe("Source tag, e.g. 'EuropePMC OA' | 'annas' | 'Wiley' | 'PMC'"),
      ttl_hours: z.number().positive().max(24 * 30).optional().describe("Scratch TTL (run/sess only); ignored for lib"),
      break_threshold: z.number().min(0).max(1).optional().describe("Semantic boundary cosine threshold (default 0.55)"),
      max_tokens: z.number().int().min(64).max(2048).optional().describe("Hard token cap per chunk (default 512)"),
    },
    async (a) => {
      try {
        // Only forward defined chunk opts — spreading `undefined` over
        // semanticChunk defaults disables the token cap (see chunk.ts resolveOpts).
        const chunkOpts: { breakThreshold?: number; maxTokens?: number } = {};
        if (a.break_threshold !== undefined) chunkOpts.breakThreshold = a.break_threshold;
        if (a.max_tokens !== undefined) chunkOpts.maxTokens = a.max_tokens;
        const res = await ingestDocument(env, {
          text: a.text, doc_id: a.doc_id, collection: a.collection,
          title: a.title, source: a.source, ttl_hours: a.ttl_hours,
          chunkOpts,
        });
        return ok({ ...res, note: SUBSTRATE_NOTE });
      } catch (e: unknown) { return toolErr(e, "ingest_document"); }
    },
  );

  // ---- semantic_search ----------------------------------------------------
  server.tool(
    "semantic_search",
    "HYBRID + MULTI-QUERY retrieval. Pass collection and/or doc_id / doc_ids[] to isolate a " +
      "working set. Unscoped search (neither collection nor doc id(s)) is compat-only and can " +
      "hit `_legacy` + all tenants — clients MUST scope. Each chunk carries {doc_id, idx, score, " +
      "retrieval} provenance. Synthesize ONLY from returned chunks; cite doc_id::idx. " + SUBSTRATE_NOTE,
    {
      query: z.string().describe("PRIMARY natural-language query (Turkish or English); rerank target"),
      queries: z.array(z.string()).optional().describe("Decomposed sub-queries / synonyms / facets (max 8 incl primary)"),
      k: z.number().int().min(1).max(50).optional().describe("How many chunks to return after rerank (default 8)"),
      collection: z.string().optional().describe("Restrict to one collection ({plugin}:{kind}:{id})"),
      doc_id: z.string().optional().describe("Restrict to a single document"),
      doc_ids: z.array(z.string()).optional().describe("Restrict to these documents (kept alongside single doc_id)"),
      rerank: z.boolean().optional().describe("Cross-encoder rerank the fused candidates (default true)"),
    },
    async (a) => {
      try {
        const chunks = await semanticSearch(env, {
          query: a.query, queries: a.queries, k: a.k, collection: a.collection,
          doc_id: a.doc_id, doc_ids: a.doc_ids, rerank: a.rerank,
        });
        return ok({
          query: a.query, collection: a.collection ?? null,
          queries: a.queries?.length ?? 0, k: a.k ?? 8, hits: chunks.length,
          pipeline: "multiquery→vector∥bm25→rrf→rerank", chunks,
          guidance: SYNTHESIZE_GUIDANCE, note: SUBSTRATE_NOTE,
        });
      } catch (e: unknown) { return toolErr(e, "semantic_search"); }
    },
  );

  // ---- upsert_triples -----------------------------------------------------
  server.tool(
    "upsert_triples",
    "Write entity-relation triples into the D1 knowledge graph. Collection-scoped: nodeKey and " +
      "edgeId include collection so the same label in coll A ≠ coll B. Missing collection → " +
      "_legacy (compat). Extraction is done by YOU from retrieved chunks. Mutation.",
    {
      collection: z.string().optional().describe("Working set for these triples ({plugin}:{kind}:{id})"),
      triples: z.array(z.object({
        subject: z.string(), predicate: z.string(), object: z.string(),
        subject_type: z.string().optional(), object_type: z.string().optional(),
        doc_id: z.string().optional(), evidence: z.string().optional(),
        collection: z.string().optional(),
      })).describe("Triples extracted from chunks. Keep predicates short, e.g. 'inhibits','treats'."),
    },
    async (a) => {
      try {
        const r = await upsertTriples(env, a.triples as Triple[], a.collection);
        return ok({ upserted_nodes: r.nodes, upserted_edges: r.edges, collection: r.collection });
      } catch (e: unknown) { return toolErr(e, "upsert_triples"); }
    },
  );

  // ---- graph_neighbors ----------------------------------------------------
  server.tool(
    "graph_neighbors",
    "Local GraphRAG: expand n hops from one entity inside ONE collection. collection is " +
      "required (unscoped → MCP error). Read-only.",
    {
      collection: z.string().describe("Working set ({plugin}:{kind}:{id}) — required"),
      entity: z.string().describe("Entity label, e.g. 'emicizumab' or 'hemophilia A'"),
      hops: z.number().int().min(1).max(3).optional().describe("Hop radius (default 1, max 3)"),
      limit: z.number().int().min(1).max(300).optional().describe("Max edges (default 100)"),
    },
    async (a) => {
      try {
        return ok(await neighbors(env, a.entity, a.hops ?? 1, a.limit ?? 100, a.collection));
      } catch (e: unknown) { return toolErr(e, "graph_neighbors"); }
    },
  );

  // ---- subgraph -----------------------------------------------------------
  server.tool(
    "subgraph",
    "Induced subgraph inside ONE collection. collection is required (unscoped → MCP error). Read-only.",
    {
      collection: z.string().describe("Working set ({plugin}:{kind}:{id}) — required"),
      entities: z.array(z.string()).describe("Entity labels to induce the subgraph over"),
    },
    async (a) => {
      try { return ok(await subgraph(env, a.entities, 200, a.collection)); }
      catch (e: unknown) { return toolErr(e, "subgraph"); }
    },
  );

  // ---- hybrid_query (FLAGSHIP) -------------------------------------------
  server.tool(
    "hybrid_query",
    "FLAGSHIP retrieval: HYBRID + MULTI-QUERY chunk retrieval UNION graph expansion, assembled " +
      "into a COMPACT, provenance-stamped evidence bundle. collection is REQUIRED — unscoped " +
      "hybrid_query is an MCP error (not an empty success). Optional doc_ids[] further narrows. " +
      "Synthesize ONLY from these chunks; cite doc_id::idx. " + SUBSTRATE_NOTE,
    {
      query: z.string().describe("The PRIMARY synthesis question (Turkish or English)"),
      collection: z.string().describe("Working set ({plugin}:{kind}:{id}) — required"),
      queries: z.array(z.string()).optional().describe("Decomposed sub-aspects/synonyms of the question"),
      k: z.number().int().min(1).max(24).optional().describe("Vector chunks to retrieve (default 8)"),
      doc_id: z.string().optional().describe("Optional single-document narrowing"),
      doc_ids: z.array(z.string()).optional().describe("Optional document-id narrowing inside the collection"),
      seed_entities: z.array(z.string()).optional().describe("Named concepts to graph-expand (e.g. ['emicizumab'])"),
      hops: z.number().int().min(1).max(2).optional().describe("Graph hops for seed entities (default 1)"),
      per_chunk_chars: z.number().int().min(200).max(2000).optional().describe("Per-chunk char budget (default 1100)"),
      max_edges: z.number().int().min(0).max(120).optional().describe("Max graph edges in the bundle (default 40)"),
    },
    async (a) => {
      try { return ok(await runHybridQuery(env, a)); }
      catch (e: unknown) { return toolErr(e, "hybrid_query"); }
    },
  );

  // ---- list_docs ----------------------------------------------------------
  server.tool(
    "list_docs",
    "List documents in one collection (id, title, source, n_chunks). Expired scratch rows are omitted. Read-only.",
    {
      collection: z.string().describe("Working set ({plugin}:{kind}:{id})"),
    },
    async (a) => {
      try { return ok(await listDocs(env, a.collection)); }
      catch (e: unknown) { return toolErr(e, "list_docs"); }
    },
  );

  // ---- corpus_stats -------------------------------------------------------
  server.tool(
    "corpus_stats",
    "Index observability. Omit collection for a GLOBAL count (observation only — not a working " +
      "set). Pass collection for that tenant's docs/chunks/nodes/edges. Read-only.",
    {
      collection: z.string().optional().describe("Optional tenant scope; omit = global observation"),
    },
    async (a) => {
      try { return ok(await corpusStats(env, a.collection)); }
      catch (e: unknown) { return toolErr(e, "corpus_stats"); }
    },
  );

  // ---- forget_document ----------------------------------------------------
  server.tool(
    "forget_document",
    "Hard-delete one document from the index by doc_id. Removes Vectorize vectors, D1 chunk " +
      "text + manifest, graph edges, and shrinks node provenance. Idempotent. This stays the " +
      "per-document API — do not use a prefix wipe; for a working set call forget_collection.",
    {
      doc_id: z.string().describe("Stable id used at ingest. Exact match."),
    },
    async (a) => {
      try { return ok(await forgetDocument(env, a.doc_id)); }
      catch (e: unknown) { return toolErr(e, "forget_document"); }
    },
  );

  // ---- forget_collection --------------------------------------------------
  server.tool(
    "forget_collection",
    "Hard-delete ONE collection (SQL + Vectorize deleteByIds in batches). Idempotent. Never " +
      "wipes another collection. There is no global wipe tool. Destructive.",
    {
      collection: z.string().describe("Exact collection to delete ({plugin}:{kind}:{id} or _legacy)"),
    },
    async (a) => {
      try { return ok(await forgetCollection(env, a.collection)); }
      catch (e: unknown) { return toolErr(e, "forget_collection"); }
    },
  );
}

/** Convenience for tests / non-DO contexts. */
export function buildServer(env: AnamEnv): McpServer {
  const server = new McpServer({ name: "anamnesis-mcp", version: pkg.version });
  registerTools(server, env);
  return server;
}
