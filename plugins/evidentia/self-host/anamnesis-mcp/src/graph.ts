/**
 * graph.ts — Entity-relation knowledge graph (Cloudflare D1) for anamnesis-mcp.
 *
 * GraphRAG design decision (honest): entity/relation EXTRACTION is done by the orchestrating
 * model (Claude) — which is a far stronger extractor than an 8B in-Worker model — and written
 * here via `upsertTriples`. The Worker owns STORAGE + TRAVERSAL, not extraction. This is the
 * "LLM-in-the-loop GraphRAG" pattern; it avoids shipping a weak in-Worker extractor and being
 * dishonest about graph quality.
 *
 * Collection isolation: nodeKey / edgeId INCLUDE the collection, so emicizumab in coll A
 * is a different node from emicizumab in coll B. Forget-collection drops that collection's
 * edges and nodes. No in-Worker community detection (BUILD-BRIEF).
 */

import type { D1Like } from "./rag.js";
import { CollectionRequiredError, LEGACY_COLLECTION, resolveWriteCollection, requireCollection } from "./collection.js";

export interface GraphEnv { DB: D1Like; STRICT_COLLECTION?: string; }

export interface Triple {
  subject: string;
  predicate: string;
  object: string;
  subject_type?: string;
  object_type?: string;
  doc_id?: string;
  evidence?: string; // chunk id (e.g. "doc::3") or a SHORT pointer — never bulk text
  collection?: string;
}

/** Normalize an entity surface form to a stable node key. Collection is part of the identity. */
export function nodeKey(collection: string, label: string): string {
  const norm = label.trim().toLowerCase().replace(/\s+/g, " ").slice(0, 200);
  return `${collection}::${norm}`;
}

async function edgeId(collection: string, subject: string, predicate: string, object: string): Promise<string> {
  const msg = `${collection}|${subject}|${predicate}|${object}`.toLowerCase();
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(msg));
  const bytes = new Uint8Array(digest);
  let hex = "";
  for (let i = 0; i < 12; i++) hex += bytes[i].toString(16).padStart(2, "0");
  return hex;
}

async function upsertNode(
  env: GraphEnv, collection: string, label: string, type: string | undefined, docId?: string,
): Promise<string> {
  const id = nodeKey(collection, label);
  const now = Date.now();
  const existing = await env.DB.prepare(`SELECT doc_ids FROM nodes WHERE id = ?`).bind(id).first<{ doc_ids: string }>();
  let docIds: string[] = [];
  if (existing?.doc_ids) { try { docIds = JSON.parse(existing.doc_ids); } catch { docIds = []; } }
  if (docId && !docIds.includes(docId)) docIds.push(docId);
  await env.DB.prepare(
    `INSERT INTO nodes (id, label, type, doc_ids, updated_at, collection) VALUES (?,?,?,?,?,?)
     ON CONFLICT(id) DO UPDATE SET label=excluded.label,
        type=COALESCE(excluded.type, nodes.type), doc_ids=excluded.doc_ids,
        updated_at=excluded.updated_at, collection=excluded.collection`,
  ).bind(id, label.trim(), type ?? null, JSON.stringify(docIds), now, collection).run();
  return id;
}

export interface UpsertResult { nodes: number; edges: number; collection: string; }

export async function upsertTriples(
  env: GraphEnv, triples: Triple[], collectionRaw?: string,
): Promise<UpsertResult> {
  const defaultColl = resolveWriteCollection(collectionRaw);
  if (defaultColl === LEGACY_COLLECTION && !(collectionRaw ?? "").trim()) {
    // Same transition contract as rag.ts writeScope(): log now, enforce under the flag.
    if (String(env.STRICT_COLLECTION ?? "0") === "1") throw new CollectionRequiredError("upsert_triples");
    try {
      console.log(JSON.stringify({
        evt: "anamnesis.scope_violation", tool: "upsert_triples",
        reason: "missing_collection", bucketed_as: LEGACY_COLLECTION,
      }));
    } catch { /* never throw */ }
  }
  const nodeIds = new Set<string>();
  let edgeCount = 0;
  for (const t of triples) {
    if (!t.subject || !t.predicate || !t.object) continue;
    const collection = t.collection ? resolveWriteCollection(t.collection) : defaultColl;
    const sId = await upsertNode(env, collection, t.subject, t.subject_type, t.doc_id);
    const oId = await upsertNode(env, collection, t.object, t.object_type, t.doc_id);
    nodeIds.add(sId); nodeIds.add(oId);
    const eId = await edgeId(collection, sId, t.predicate, oId);
    const now = Date.now();
    // `weight` counts DISTINCT supporting documents. It used to be `weight + 1` on every write,
    // which made it a count of how often the orchestrator repeated itself — and every
    // `ORDER BY weight DESC` in this module inherited that bias (audit finding A10). Restating a
    // triple from the SAME document is not corroboration; a second document is. The read-modify-
    // write mirrors upsertNode, which already merges doc provenance this way.
    const prior = await env.DB.prepare(`SELECT doc_ids, assert_count FROM edges WHERE id = ?`)
      .bind(eId).first<{ doc_ids: string | null; assert_count: number | null }>();
    let edgeDocs: string[] = [];
    if (prior?.doc_ids) { try { edgeDocs = JSON.parse(prior.doc_ids); } catch { edgeDocs = []; } }
    if (t.doc_id && !edgeDocs.includes(t.doc_id)) edgeDocs.push(t.doc_id);
    const assertCount = Number(prior?.assert_count ?? 0) + 1;
    const weight = Math.max(1, edgeDocs.length);
    await env.DB.prepare(
      `INSERT INTO edges (id, subject, predicate, object, doc_id, evidence, weight, doc_ids, assert_count, updated_at, collection)
       VALUES (?,?,?,?,?,?,?,?,?,?,?)
       ON CONFLICT(id) DO UPDATE SET weight = excluded.weight,
         doc_id = COALESCE(excluded.doc_id, edges.doc_id),
         evidence = COALESCE(excluded.evidence, edges.evidence),
         doc_ids = excluded.doc_ids, assert_count = excluded.assert_count,
         updated_at = excluded.updated_at, collection = excluded.collection`,
    ).bind(eId, sId, t.predicate, oId, t.doc_id ?? null, t.evidence ?? null,
           weight, JSON.stringify(edgeDocs), assertCount, now, collection).run();
    edgeCount++;
  }
  return { nodes: nodeIds.size, edges: edgeCount, collection: defaultColl };
}

export interface GraphEdge {
  subject: string; predicate: string; object: string;
  doc_id?: string | null; evidence?: string | null;
  /** Number of DISTINCT documents supporting this triple. Ranking key for every graph read. */
  weight: number;
  /** Every document that asserted this triple. */
  doc_ids?: string[];
  /** How many times the triple was written. Repetition is transparency, never evidence. */
  assert_count?: number;
  collection?: string | null;
}

const EDGE_COLUMNS =
  "subject, predicate, object, doc_id, evidence, weight, doc_ids, assert_count, collection";

function mapEdgeRow(r: Record<string, unknown>, collection: string): GraphEdge {
  let docIds: string[] = [];
  try { docIds = JSON.parse(String(r["doc_ids"] ?? "[]")); } catch { docIds = []; }
  return {
    subject: String(r["subject"]), predicate: String(r["predicate"]), object: String(r["object"]),
    doc_id: (r["doc_id"] as string) ?? null, evidence: (r["evidence"] as string) ?? null,
    weight: Number(r["weight"] ?? 1),
    doc_ids: docIds,
    assert_count: Number(r["assert_count"] ?? 1),
    collection: (r["collection"] as string) ?? collection,
  };
}

async function edgesTouching(env: GraphEnv, ids: string[], collection: string): Promise<GraphEdge[]> {
  if (!ids.length) return [];
  const ph = ids.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT ${EDGE_COLUMNS} FROM edges
     WHERE collection = ? AND (subject IN (${ph}) OR object IN (${ph}))
     ORDER BY weight DESC LIMIT 500`,
  ).bind(collection, ...ids, ...ids).all();
  return ((rows.results ?? []) as Array<Record<string, unknown>>).map((r) => mapEdgeRow(r, collection));
}

/** N-hop neighbour expansion from one entity (BFS over the undirected edge set). Collection-scoped. */
export async function neighbors(
  env: GraphEnv, entity: string, hops = 1, limit = 100, collectionRaw?: string,
): Promise<{ center: string; found: boolean; collection: string; edges: GraphEdge[]; entities: string[] }> {
  const collection = requireCollection(collectionRaw, "graph_neighbors");
  const start = nodeKey(collection, entity);
  const node = await env.DB.prepare(`SELECT id FROM nodes WHERE id = ? AND collection = ?`)
    .bind(start, collection).first<{ id: string }>();
  if (!node) return { center: start, found: false, collection, edges: [], entities: [] };

  const visited = new Set<string>([start]);
  let frontier = [start];
  const allEdges: GraphEdge[] = [];
  const h = Math.min(Math.max(hops, 1), 3);
  for (let d = 0; d < h && frontier.length; d++) {
    const es = await edgesTouching(env, frontier, collection);
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
  const seen = new Set<string>();
  const edges = allEdges.filter((e) => {
    const k = `${e.subject}|${e.predicate}|${e.object}`;
    if (seen.has(k)) return false; seen.add(k); return true;
  }).slice(0, limit);
  return { center: start, found: true, collection, edges, entities: [...visited] };
}

/** Induced subgraph: edges whose BOTH endpoints fall in the given entity set. Collection-scoped. */
export async function subgraph(
  env: GraphEnv, entities: string[], limit = 200, collectionRaw?: string,
): Promise<{ collection: string; edges: GraphEdge[]; entities: string[] }> {
  const collection = requireCollection(collectionRaw, "subgraph");
  const keys = entities.map((e) => nodeKey(collection, e));
  if (keys.length < 1) return { collection, edges: [], entities: [] };
  const es = await edgesTouching(env, keys, collection);
  const keySet = new Set(keys);
  const edges = es.filter((e) => keySet.has(e.subject) && keySet.has(e.object)).slice(0, limit);
  return { collection, edges, entities: keys };
}

/** Edges sourced from a set of documents, ranked by weight (doc-scoped graph context). */
export async function edgesByDocs(
  env: GraphEnv, docIds: string[], limit: number, collection: string,
): Promise<GraphEdge[]> {
  const ids = [...new Set(docIds)].filter(Boolean);
  if (!ids.length) return [];
  const ph = ids.map(() => "?").join(",");
  const rows = await env.DB.prepare(
    `SELECT ${EDGE_COLUMNS} FROM edges
     WHERE collection = ? AND doc_id IN (${ph}) ORDER BY weight DESC LIMIT ?`,
  ).bind(collection, ...ids, limit).all();
  return ((rows.results ?? []) as Array<Record<string, unknown>>).map((r) => mapEdgeRow(r, collection));
}

export const __testing = { nodeKey, edgeId, LEGACY_COLLECTION };
