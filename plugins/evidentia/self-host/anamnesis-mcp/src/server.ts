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
 *   ingest_document   — semantic-chunk + embed + store; returns a MANIFEST, not the text
 *   semantic_search   — vector top-k chunks with provenance (doc_id, idx, score)
 *   upsert_triples    — write Claude-extracted entity/relation triples to the D1 graph
 *   graph_neighbors   — n-hop local GraphRAG expansion from one entity
 *   subgraph          — induced edges over an entity set (cross-document links)
 *   hybrid_query      — FLAGSHIP: vector top-k ∪ graph expansion -> compact evidence bundle
 *   corpus_stats      — doc/chunk/node/edge counts (observability)
 *   forget_document   — hard-delete a doc by doc_id: Vectorize vectors + D1 chunks/manifest +
 *                       graph edges; node provenance shrunk, orphan nodes removed (clean teardown)
 *
 * Honest scope: extraction is Claude-in-the-loop (upsert_triples); Microsoft-GraphRAG global
 * community summarization is a documented Cloud Run add-on (NOT shipped as a weak in-Worker
 * approximation). Read paths carry readOnlyHint; ingest/upsert are mutations.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { ingestDocument, semanticSearch, corpusStats, forgetDocument, type RagEnv, type RetrievedChunk } from "./rag.js";
import { upsertTriples, neighbors, subgraph, type GraphEnv, type Triple, type GraphEdge } from "./graph.js";

export type AnamEnv = RagEnv & GraphEnv;

const SUBSTRATE_NOTE =
  "anamnesis substrate: this is a context-window-bounded retrieval slice, not the full corpus. " +
  "Every chunk carries {doc_id, idx, score} provenance; cite at chunk granularity. Graph triples " +
  "were extracted by the orchestrator (Claude-in-the-loop), not a clinical knowledge base — " +
  "treat relations as evidence pointers to verify, not adjudicated facts.";

const ok = (obj: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(obj, null, 2) }] });
const err = (msg: string) => ({ isError: true, content: [{ type: "text" as const, text: msg }] });

/** Edges sourced from a set of documents, ranked by weight (doc-scoped graph context). */
async function edgesByDocs(env: AnamEnv, docIds: string[], limit: number): Promise<GraphEdge[]> {
  const ids = [...new Set(docIds)].filter(Boolean);
  if (!ids.length) return [];
  const ph = ids.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT subject, predicate, object, doc_id, evidence, weight FROM edges
     WHERE doc_id IN (${ph}) ORDER BY weight DESC LIMIT ?`,
  ).bind(...ids, limit).all();
  return ((rows.results ?? []) as Array<Record<string, unknown>>).map((r) => ({
    subject: String(r["subject"]), predicate: String(r["predicate"]), object: String(r["object"]),
    doc_id: (r["doc_id"] as string) ?? null, evidence: (r["evidence"] as string) ?? null,
    weight: Number(r["weight"] ?? 1),
  }));
}

export function registerTools(server: McpServer, env: AnamEnv): void {
  // ---- ingest_document ----------------------------------------------------
  server.tool(
    "ingest_document",
    "Semantic-chunk + embed (bge-m3) + store a document into the anamnesis index (Vectorize + D1). " +
      "Returns a MANIFEST (chunk count + per-chunk token estimate + 160-char preview) — NOT the full " +
      "text. Use this for any large full-text retrieval (Annas/EuropePMC OA/Paper Search/pasted PDF) " +
      "so the corpus stays OUT of the context window. " + SUBSTRATE_NOTE,
    {
      text: z.string().describe("Full document text to ingest (article body, book chapter, etc.)"),
      doc_id: z.string().describe("Stable id, e.g. a DOI or 'cochrane-handbook-ch8'. Re-ingest overwrites."),
      title: z.string().optional().describe("Human title for provenance"),
      source: z.string().optional().describe("Source tag, e.g. 'EuropePMC OA' | 'annas' | 'Wiley' | 'PMC'"),
      break_threshold: z.number().min(0).max(1).optional().describe("Semantic boundary cosine threshold (default 0.55)"),
      max_tokens: z.number().int().min(64).max(2048).optional().describe("Hard token cap per chunk (default 512)"),
    },
    async (a) => {
      try {
        const res = await ingestDocument(env, {
          text: a.text, doc_id: a.doc_id, title: a.title, source: a.source,
          chunkOpts: { breakThreshold: a.break_threshold, maxTokens: a.max_tokens },
        });
        return ok({ ...res, note: SUBSTRATE_NOTE });
      } catch (e: any) { return err(`ingest_document failed: ${e.message}`); }
    },
  );

  // ---- semantic_search ----------------------------------------------------
  server.tool(
    "semantic_search",
    "Vector top-k retrieval over ingested chunks (multilingual bge-m3 — Turkish query against " +
      "English corpus works). Returns chunks with {doc_id, idx, score} provenance. Read-only. " + SUBSTRATE_NOTE,
    {
      query: z.string().describe("Natural-language query (Turkish or English)"),
      k: z.number().int().min(1).max(50).optional().describe("How many chunks (default 8)"),
      doc_id: z.string().optional().describe("Restrict to a single document"),
    },
    async (a) => {
      try {
        const chunks = await semanticSearch(env, { query: a.query, k: a.k, doc_id: a.doc_id });
        return ok({ query: a.query, k: a.k ?? 8, hits: chunks.length, chunks, note: SUBSTRATE_NOTE });
      } catch (e: any) { return err(`semantic_search failed: ${e.message}`); }
    },
  );

  // ---- upsert_triples (Claude-in-the-loop graph write) --------------------
  server.tool(
    "upsert_triples",
    "Write entity-relation triples into the D1 knowledge graph. Extraction is done by YOU " +
      "(the orchestrator) from retrieved chunks — the Worker only stores + traverses. Pass " +
      "evidence = the chunk id (e.g. 'DOI::3') so relations stay traceable. Mutation.",
    {
      triples: z.array(z.object({
        subject: z.string(), predicate: z.string(), object: z.string(),
        subject_type: z.string().optional(), object_type: z.string().optional(),
        doc_id: z.string().optional(), evidence: z.string().optional(),
      })).describe("Triples extracted from chunks. Keep predicates short, e.g. 'inhibits','treats','associated_with'."),
    },
    async (a) => {
      try {
        const r = await upsertTriples(env, a.triples as Triple[]);
        return ok({ upserted_nodes: r.nodes, upserted_edges: r.edges });
      } catch (e: any) { return err(`upsert_triples failed: ${e.message}`); }
    },
  );

  // ---- graph_neighbors ----------------------------------------------------
  server.tool(
    "graph_neighbors",
    "Local GraphRAG: expand n hops from one entity over the knowledge graph. Returns the edges " +
      "(relations) and the entities reached. Use to ground multi-hop reasoning. Read-only.",
    {
      entity: z.string().describe("Entity label, e.g. 'emicizumab' or 'hemophilia A'"),
      hops: z.number().int().min(1).max(3).optional().describe("Hop radius (default 1, max 3)"),
      limit: z.number().int().min(1).max(300).optional().describe("Max edges (default 100)"),
    },
    async (a) => {
      try {
        const r = await neighbors(env, a.entity, a.hops ?? 1, a.limit ?? 100);
        return ok(r);
      } catch (e: any) { return err(`graph_neighbors failed: ${e.message}`); }
    },
  );

  // ---- subgraph -----------------------------------------------------------
  server.tool(
    "subgraph",
    "Induced subgraph: edges whose BOTH endpoints are in the given entity set — surfaces the " +
      "cross-document relations among a list of concepts. Read-only.",
    { entities: z.array(z.string()).describe("Entity labels to induce the subgraph over") },
    async (a) => {
      try { return ok(await subgraph(env, a.entities)); }
      catch (e: any) { return err(`subgraph failed: ${e.message}`); }
    },
  );

  // ---- hybrid_query (FLAGSHIP) -------------------------------------------
  server.tool(
    "hybrid_query",
    "FLAGSHIP retrieval: vector top-k chunks UNION graph expansion, assembled into a COMPACT, " +
      "provenance-stamped evidence bundle sized for the context window. This is the call that " +
      "yields broad + accurate + CONSISTENT answers without dumping the corpus. Pass seed_entities " +
      "to also graph-expand named concepts. Read-only. " + SUBSTRATE_NOTE,
    {
      query: z.string().describe("The synthesis question (Turkish or English)"),
      k: z.number().int().min(1).max(24).optional().describe("Vector chunks to retrieve (default 8)"),
      seed_entities: z.array(z.string()).optional().describe("Named concepts to graph-expand (e.g. ['emicizumab'])"),
      hops: z.number().int().min(1).max(2).optional().describe("Graph hops for seed entities (default 1)"),
      per_chunk_chars: z.number().int().min(200).max(2000).optional().describe("Per-chunk char budget (default 1100)"),
      max_edges: z.number().int().min(0).max(120).optional().describe("Max graph edges in the bundle (default 40)"),
    },
    async (a) => {
      try {
        const k = a.k ?? 8;
        const perChunk = a.per_chunk_chars ?? 1100;
        const maxEdges = a.max_edges ?? 40;

        // 1) vector retrieval
        const chunks: RetrievedChunk[] = await semanticSearch(env, { query: a.query, k });
        const docIds = [...new Set(chunks.map((c) => c.doc_id))];

        // 2) graph context: relations sourced from the retrieved documents (ranked by weight)
        const docEdges = await edgesByDocs(env, docIds, maxEdges);

        // 3) optional seed-entity expansion
        const seedEdges: GraphEdge[] = [];
        for (const ent of a.seed_entities ?? []) {
          const n = await neighbors(env, ent, a.hops ?? 1, Math.ceil(maxEdges / 2));
          if (n.found) seedEdges.push(...n.edges);
        }

        // merge + de-dupe edges, cap
        const seen = new Set<string>();
        const graph = [...docEdges, ...seedEdges].filter((e) => {
          const key = `${e.subject}|${e.predicate}|${e.object}`;
          if (seen.has(key)) return false; seen.add(key); return true;
        }).slice(0, maxEdges);

        // 4) assemble compact bundle (per-chunk truncation keeps total within budget)
        const bundleChunks = chunks.map((c) => ({
          doc_id: c.doc_id, idx: c.idx, score: Number(c.score.toFixed(4)),
          title: c.title ?? undefined, source: c.source ?? undefined,
          text: c.text.length > perChunk ? c.text.slice(0, perChunk) + " …[truncated]" : c.text,
        }));

        const approxTokens =
          bundleChunks.reduce((s, c) => s + Math.round(c.text.length / 4), 0) +
          graph.length * 12;

        return ok({
          query: a.query,
          retrieval: { vector_k: k, chunks: bundleChunks.length, graph_edges: graph.length, docs: docIds },
          chunks: bundleChunks,
          graph,
          approx_token_budget: approxTokens,
          guidance: "Synthesize ONLY from these chunks + relations; cite chunk provenance " +
            "(doc_id::idx). If coverage is thin, call ingest_document on more sources, then re-run.",
          note: SUBSTRATE_NOTE,
        });
      } catch (e: any) { return err(`hybrid_query failed: ${e.message}`); }
    },
  );

  // ---- corpus_stats -------------------------------------------------------
  server.tool(
    "corpus_stats",
    "Index observability: counts of docs, chunks, graph nodes and edges. Read-only.",
    {},
    async () => {
      try { return ok(await corpusStats(env)); }
      catch (e: any) { return err(`corpus_stats failed: ${e.message}`); }
    },
  );

  // ---- forget_document (destructive cleanup) ------------------------------
  server.tool(
    "forget_document",
    "Hard-delete one document from the index by doc_id — the clean teardown path ingest_document " +
      "lacked (re-ingest only overwrote same-id chunks, leaving stale vectors/graph). Removes: the " +
      "doc's Vectorize vectors, its D1 chunk text + manifest row, its graph edges, and its provenance " +
      "from graph nodes (a node that loses its LAST contributing doc is deleted; one still cited by " +
      "another doc is kept, provenance shrunk). DESTRUCTIVE + irreversible. Idempotent: an unknown " +
      "doc_id returns existed:false with zero counts. Use to purge test/smoke data or stale corpus.",
    {
      doc_id: z.string().describe("Stable id used at ingest (e.g. a DOI or 'cochrane-handbook-ch8'). Exact match."),
    },
    async (a) => {
      try { return ok(await forgetDocument(env, a.doc_id)); }
      catch (e: any) { return err(`forget_document failed: ${e.message}`); }
    },
  );
}

/** Convenience for tests / non-DO contexts. */
export function buildServer(env: AnamEnv): McpServer {
  const server = new McpServer({ name: "anamnesis-mcp", version: "1.0.0" });
  registerTools(server, env);
  return server;
}
