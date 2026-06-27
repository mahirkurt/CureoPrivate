/**
 * graph.ts — Entity-relation knowledge graph (Cloudflare D1) for anamnesis-mcp.
 *
 * GraphRAG design decision (honest): entity/relation EXTRACTION is done by the orchestrating
 * model (Claude) — which is a far stronger extractor than an 8B in-Worker model — and written
 * here via `upsertTriples`. The Worker owns STORAGE + TRAVERSAL, not extraction. This is the
 * "LLM-in-the-loop GraphRAG" pattern; it avoids shipping a weak in-Worker extractor and being
 * dishonest about graph quality.
 *
 * What ships in v1: local (entity-centric) graph — upsert, 1..n-hop neighbor expansion, and
 * induced subgraph over an entity set. This is enough to ground cross-document, multi-hop
 * synthesis and keep answers CONSISTENT (the same relations are retrieved every time).
 *
 * DEFERRED (documented in BUILD-BRIEF, NOT faked here): Microsoft-GraphRAG global search —
 * Leiden community detection + hierarchical community summaries — belongs in a batch Cloud Run
 * indexer, not a request-scoped Worker. `community_summary`/`global_query` are roadmap, not a
 * weak approximation masquerading as the real thing.
 */

import type { D1Like } from "./rag.js";

export interface GraphEnv { DB: D1Like; }

export interface Triple {
  subject: string;
  predicate: string;
  object: string;
  subject_type?: string;
  object_type?: string;
  doc_id?: string;
  evidence?: string; // chunk id (e.g. "doc::3") or a SHORT pointer — never bulk text
}

/** Normalize an entity surface form to a stable node key. */
export function nodeKey(label: string): string {
  return label.trim().toLowerCase().replace(/\s+/g, " ").slice(0, 200);
}

async function edgeId(subject: string, predicate: string, object: string): Promise<string> {
  const msg = `${subject}|${predicate}|${object}`.toLowerCase();
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(msg));
  const bytes = new Uint8Array(digest);
  let hex = "";
  for (let i = 0; i < 12; i++) hex += bytes[i].toString(16).padStart(2, "0");
  return hex;
}

async function upsertNode(env: GraphEnv, label: string, type: string | undefined, docId?: string): Promise<string> {
  const id = nodeKey(label);
  const now = Date.now();
  const existing = await env.DB.prepare(`SELECT doc_ids FROM nodes WHERE id = ?`).bind(id).first<{ doc_ids: string }>();
  let docIds: string[] = [];
  if (existing?.doc_ids) { try { docIds = JSON.parse(existing.doc_ids); } catch { docIds = []; } }
  if (docId && !docIds.includes(docId)) docIds.push(docId);
  await env.DB.prepare(
    `INSERT INTO nodes (id, label, type, doc_ids, updated_at) VALUES (?,?,?,?,?)
     ON CONFLICT(id) DO UPDATE SET label=excluded.label,
        type=COALESCE(excluded.type, nodes.type), doc_ids=excluded.doc_ids, updated_at=excluded.updated_at`,
  ).bind(id, label.trim(), type ?? null, JSON.stringify(docIds), now).run();
  return id;
}

export interface UpsertResult { nodes: number; edges: number; }

export async function upsertTriples(env: GraphEnv, triples: Triple[]): Promise<UpsertResult> {
  const nodeIds = new Set<string>();
  let edgeCount = 0;
  for (const t of triples) {
    if (!t.subject || !t.predicate || !t.object) continue;
    const sId = await upsertNode(env, t.subject, t.subject_type, t.doc_id);
    const oId = await upsertNode(env, t.object, t.object_type, t.doc_id);
    nodeIds.add(sId); nodeIds.add(oId);
    const eId = await edgeId(sId, t.predicate, oId);
    const now = Date.now();
    await env.DB.prepare(
      `INSERT INTO edges (id, subject, predicate, object, doc_id, evidence, weight, updated_at)
       VALUES (?,?,?,?,?,?,1,?)
       ON CONFLICT(id) DO UPDATE SET weight = edges.weight + 1,
         doc_id = COALESCE(excluded.doc_id, edges.doc_id),
         evidence = COALESCE(excluded.evidence, edges.evidence), updated_at = excluded.updated_at`,
    ).bind(eId, sId, t.predicate, oId, t.doc_id ?? null, t.evidence ?? null, now).run();
    edgeCount++;
  }
  return { nodes: nodeIds.size, edges: edgeCount };
}

export interface GraphEdge {
  subject: string; predicate: string; object: string;
  doc_id?: string | null; evidence?: string | null; weight: number;
}

async function edgesTouching(env: GraphEnv, ids: string[]): Promise<GraphEdge[]> {
  if (!ids.length) return [];
  const ph = ids.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT subject, predicate, object, doc_id, evidence, weight FROM edges
     WHERE subject IN (${ph}) OR object IN (${ph})
     ORDER BY weight DESC LIMIT 500`,
  ).bind(...ids, ...ids).all();
  return ((rows.results ?? []) as Array<Record<string, unknown>>).map((r) => ({
    subject: String(r["subject"]), predicate: String(r["predicate"]), object: String(r["object"]),
    doc_id: (r["doc_id"] as string) ?? null, evidence: (r["evidence"] as string) ?? null,
    weight: Number(r["weight"] ?? 1),
  }));
}

/** N-hop neighbour expansion from one entity (BFS over the undirected edge set). */
export async function neighbors(
  env: GraphEnv, entity: string, hops = 1, limit = 100,
): Promise<{ center: string; found: boolean; edges: GraphEdge[]; entities: string[] }> {
  const start = nodeKey(entity);
  const node = await env.DB.prepare(`SELECT id FROM nodes WHERE id = ?`).bind(start).first<{ id: string }>();
  if (!node) return { center: start, found: false, edges: [], entities: [] };

  const visited = new Set<string>([start]);
  let frontier = [start];
  const allEdges: GraphEdge[] = [];
  const h = Math.min(Math.max(hops, 1), 3);
  for (let d = 0; d < h && frontier.length; d++) {
    const es = await edgesTouching(env, frontier);
    const next: string[] = [];
    for (const e of es) {
      allEdges.push(e);
      for (const side of [e.subject, e.object]) {
        if (!visited.has(side)) { visited.add(side); next.push(side); }
      }
      if (allEdges.length >= limit) break;
    }
    frontier = next;
    if (allEdges.length >= limit) break;
  }
  // de-dupe edges
  const seen = new Set<string>();
  const edges = allEdges.filter((e) => {
    const k = `${e.subject}|${e.predicate}|${e.object}`;
    if (seen.has(k)) return false; seen.add(k); return true;
  }).slice(0, limit);
  return { center: start, found: true, edges, entities: [...visited] };
}

/** Induced subgraph: edges whose BOTH endpoints fall in the given entity set. */
export async function subgraph(env: GraphEnv, entities: string[], limit = 200): Promise<{ edges: GraphEdge[]; entities: string[] }> {
  const keys = entities.map(nodeKey);
  if (keys.length < 1) return { edges: [], entities: [] };
  const es = await edgesTouching(env, keys);
  const keySet = new Set(keys);
  const edges = es.filter((e) => keySet.has(e.subject) && keySet.has(e.object)).slice(0, limit);
  return { edges, entities: keys };
}

export const __testing = { nodeKey, edgeId };
