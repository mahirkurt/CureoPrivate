/**
 * community.ts — GraphRAG global search substrate for anamnesis-mcp.
 *
 * WHY THIS SHAPE (BUILD-BRIEF §5): Microsoft-GraphRAG global search needs a community partition
 * (Leiden) plus community summaries. §5 deliberately did NOT ship it, because a request-scoped
 * Worker is the wrong place for batch graph clustering and because summarising with a weak
 * in-Worker model would put untrustworthy prose into the evidence substrate. That reasoning still
 * holds, so the work is split three ways and nothing here approximates anything:
 *
 *   - The Worker STORES a partition and SERVES it (this module). No clustering happens here.
 *   - An offline indexer on HP computes the partition with real Leiden (`anamnesis-indexer`),
 *     reads the graph via `graph_export` and writes it back via `upsert_communities`. Leiden is
 *     pure graph mathematics — no language model is involved, so nothing is approximated.
 *   - Summaries are written by the ORCHESTRATOR (Claude) via `community_summarize`, exactly like
 *     triples are extracted by the orchestrator via `upsert_triples`. Same doctrine, extended.
 *
 * Until a community has a summary, `global_query` says so (`summary_status: "absent"`) and hands
 * back the member/edge bundle for the caller to reason over. It never invents a summary, and it
 * never presents a heuristic ranking as if it were semantic retrieval.
 */

import type { D1Like } from "./rag.js";
import { requireCollection } from "./collection.js";

export interface CommunityEnv { DB: D1Like; }

export interface ExportedNode { id: string; label: string; type?: string | null }
export interface ExportedEdge { subject: string; predicate: string; object: string; weight: number }

/** Whole-graph read for the offline indexer. Collection-scoped like every other graph path. */
export async function exportGraph(
  env: CommunityEnv, collectionRaw: string,
): Promise<{ collection: string; nodes: ExportedNode[]; edges: ExportedEdge[] }> {
  const collection = requireCollection(collectionRaw, "graph_export");
  const nodeRows = await env.DB.prepare(
    `SELECT id, label, type FROM nodes WHERE collection = ? ORDER BY id`,
  ).bind(collection).all();
  const edgeRows = await env.DB.prepare(
    `SELECT subject, predicate, object, weight FROM edges WHERE collection = ? ORDER BY weight DESC`,
  ).bind(collection).all();
  return {
    collection,
    nodes: ((nodeRows.results ?? []) as Array<Record<string, unknown>>).map((r) => ({
      id: String(r["id"]), label: String(r["label"]), type: (r["type"] as string) ?? null,
    })),
    edges: ((edgeRows.results ?? []) as Array<Record<string, unknown>>).map((r) => ({
      subject: String(r["subject"]), predicate: String(r["predicate"]),
      object: String(r["object"]), weight: Number(r["weight"] ?? 1),
    })),
  };
}

export interface CommunityInput {
  level: number;
  members: string[];
  edge_count?: number;
}

async function ensureCommunityTable(env: CommunityEnv): Promise<void> {
  await env.DB.prepare(
    `CREATE TABLE IF NOT EXISTS communities (
       id TEXT PRIMARY KEY, collection TEXT NOT NULL, level INTEGER NOT NULL,
       members TEXT NOT NULL, edge_count INTEGER, summary TEXT, summary_by TEXT,
       updated_at INTEGER)`,
  ).run();
  await env.DB.prepare(
    `CREATE INDEX IF NOT EXISTS idx_communities_collection ON communities(collection, level)`,
  ).run();
}

/**
 * Replace this collection's partition. A partition is a WHOLE object — writing a new one must
 * drop the old communities, or a re-index that finds fewer clusters would leave orphans behind
 * that `global_query` would keep serving (the same stale-tail hazard re-ingest has).
 */
export async function upsertCommunities(
  env: CommunityEnv, collectionRaw: string, communities: CommunityInput[],
): Promise<{ collection: string; upserted: number; replaced: number }> {
  const collection = requireCollection(collectionRaw, "upsert_communities");
  await ensureCommunityTable(env);

  const prior = await env.DB.prepare(`SELECT COUNT(*) AS n FROM communities WHERE collection = ?`)
    .bind(collection).first<{ n: number }>();
  // Carry summaries across a re-index when the membership is unchanged: they were expensive
  // (a Claude turn each) and a partition often only shifts in part.
  const oldRows = await env.DB.prepare(
    `SELECT members, summary, summary_by FROM communities WHERE collection = ? AND summary IS NOT NULL`,
  ).bind(collection).all();
  const carried = new Map<string, { summary: string; by: string }>();
  for (const r of (oldRows.results ?? []) as Array<Record<string, unknown>>) {
    carried.set(String(r["members"]), {
      summary: String(r["summary"]), by: String(r["summary_by"] ?? "claude"),
    });
  }

  await env.DB.prepare(`DELETE FROM communities WHERE collection = ?`).bind(collection).run();

  const now = Date.now();
  let n = 0;
  for (const c of communities) {
    const members = [...new Set((c.members ?? []).filter(Boolean))].sort();
    if (!members.length) continue;
    const key = JSON.stringify(members);
    const keep = carried.get(key);
    await env.DB.prepare(
      `INSERT INTO communities (id, collection, level, members, edge_count, summary, summary_by, updated_at)
       VALUES (?,?,?,?,?,?,?,?)`,
    ).bind(
      `${collection}::${c.level}::${n}`, collection, c.level, key, c.edge_count ?? 0,
      keep?.summary ?? null, keep?.by ?? null, now,
    ).run();
    n++;
  }
  return { collection, upserted: n, replaced: Number(prior?.n ?? 0) };
}

/** Attach an orchestrator-written summary. Refuses a community owned by another collection. */
export async function summarizeCommunity(
  env: CommunityEnv, collectionRaw: string, communityId: string, summary: string,
): Promise<{ collection: string; community_id: string; summary_by: string }> {
  const collection = requireCollection(collectionRaw, "community_summarize");
  await ensureCommunityTable(env);
  const row = await env.DB.prepare(`SELECT collection FROM communities WHERE id = ?`)
    .bind(communityId).first<{ collection: string }>();
  if (!row) throw new Error(`community_summarize: unknown community '${communityId}'`);
  if (row.collection !== collection) {
    throw new Error(
      `community_summarize refused: community '${communityId}' belongs to collection ` +
      `'${row.collection}', not '${collection}'.`,
    );
  }
  await env.DB.prepare(
    `UPDATE communities SET summary = ?, summary_by = 'claude', updated_at = ? WHERE id = ?`,
  ).bind(summary, Date.now(), communityId).run();
  return { collection, community_id: communityId, summary_by: "claude" };
}

export interface CommunityHit {
  id: string;
  level: number;
  size: number;
  edge_count: number;
  summary: string | null;
  summary_status: "claude" | "absent";
  members: string[];
  score: number;
}

const tokens = (s: string): string[] =>
  (s.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? []).filter((t) => t.length > 1);

/**
 * Rank a collection's communities against a question.
 *
 * The ranking is a LEXICAL overlap heuristic over each community's summary (when one exists) and
 * its member labels — not embedding retrieval. That is stated in the response so a caller never
 * mistakes it for semantic search; global search is about picking which clusters to read, and the
 * reading itself is the orchestrator's job.
 */
export interface GlobalQueryResult {
  collection: string;
  query: string;
  level: number | null;
  communities: CommunityHit[];
  ranking: "lexical-overlap";
  note: string;
}

export async function globalQuery(
  env: CommunityEnv,
  args: { collection: string; query: string; level?: number; k?: number },
): Promise<GlobalQueryResult> {
  const collection = requireCollection(args.collection, "global_query");
  await ensureCommunityTable(env);
  const k = Math.min(Math.max(args.k ?? 5, 1), 25);

  const clauses = ["collection = ?"];
  const binds: unknown[] = [collection];
  if (args.level !== undefined) { clauses.push("level = ?"); binds.push(args.level); }
  const rows = await env.DB.prepare(
    `SELECT id, level, members, edge_count, summary, summary_by FROM communities
      WHERE ${clauses.join(" AND ")}`,
  ).bind(...binds).all();

  const q = new Set(tokens(args.query));
  const hits: CommunityHit[] = [];
  for (const r of (rows.results ?? []) as Array<Record<string, unknown>>) {
    let members: string[] = [];
    try { members = JSON.parse(String(r["members"] ?? "[]")); } catch { members = []; }
    const summary = (r["summary"] as string) ?? null;
    // Node ids are "<collection>::<label>" — strip the prefix so the collection name itself
    // cannot inflate every score.
    const labels = members.map((m) => m.slice(m.indexOf("::") + 2));
    const hay = new Set(tokens([summary ?? "", ...labels].join(" ")));
    let overlap = 0;
    for (const t of q) if (hay.has(t)) overlap++;
    hits.push({
      id: String(r["id"]), level: Number(r["level"]), size: members.length,
      edge_count: Number(r["edge_count"] ?? 0), summary,
      summary_status: summary ? "claude" : "absent",
      members: labels,
      score: q.size ? overlap / q.size : 0,
    });
  }
  hits.sort((a, b) => b.score - a.score || b.edge_count - a.edge_count);
  const top = hits.slice(0, k);
  const missing = top.filter((h) => h.summary_status === "absent").length;

  return {
    collection,
    query: args.query,
    level: args.level ?? null,
    communities: top,
    ranking: "lexical-overlap" as const,
    note:
      "GLOBAL SEARCH over a stored Leiden partition. Communities are ranked by LEXICAL overlap " +
      "against their summary and member labels — this is a routing heuristic, not embedding " +
      "retrieval, so treat the order as a reading suggestion. " +
      (missing
        ? `${missing} of these communities have NO summary yet (summary_status:"absent"); their ` +
          "member lists are returned instead. Write one back with community_summarize so later " +
          "runs can reuse it. A summary is never generated for you."
        : "Summaries were written by the orchestrator (community_summarize), not by a model " +
          "inside this Worker."),
  };
}
