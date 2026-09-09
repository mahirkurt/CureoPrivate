/**
 * reaper.ts — scheduled garbage collection for anamnesis-mcp.
 *
 * WHY (audit 2026-09-07, finding A2): `docs.expires_at` was written at ingest and honoured when
 * READING, but nothing ever deleted an expired row — there was no cron trigger and no scheduled()
 * handler. Two consequences, both silent:
 *
 *  1. D1 grew without bound.
 *  2. Worse: Vectorize was never TTL-filtered AT ALL. Expired chunk vectors kept occupying the
 *     index and kept being returned inside the `topK` candidate pool (30-80), where the D1
 *     post-filter then discarded them. Every dead scratch document therefore stole candidate
 *     slots from live ones, so recall decayed as the index filled with corpses.
 *
 * The hook-side lifecycle was supposed to prevent this, but it is fail-open by design: no key,
 * no SessionEnd event, an ingest made inside a sub-agent, or a crash all leave rows behind. This
 * reaper is the LAST line of defence, so it also sweeps scratch (`run`/`sess`) documents that
 * never received a ttl_hours at all once they are older than `maxScratchAgeMs`.
 *
 * `lib` collections are DURABLE and are never swept — that is the whole point of the kind.
 */

import { forgetDocument, type RagEnv, ensureSchema } from "./rag.js";
import { isScratchCollection, LEGACY_COLLECTION } from "./collection.js";

/** Untagged scratch older than this is treated as abandoned. */
export const DEFAULT_MAX_SCRATCH_AGE_MS = 14 * 24 * 3600 * 1000;

export interface ReapResult {
  docs: number;
  chunks: number;
  vectors: number;
  edges: number;
  nodes: number;
  /** Collections that lost at least one document. */
  collections: string[];
  reasons: { expired: number; abandoned_scratch: number };
}

interface Candidate {
  id: string;
  collection: string;
  reason: "expired" | "abandoned_scratch";
}

/**
 * Delete every document whose TTL has passed, plus abandoned untagged scratch.
 * Idempotent: a second run over the same corpus reaps nothing.
 */
export async function reapExpired(
  env: RagEnv, opts: { now?: number; maxScratchAgeMs?: number } = {},
): Promise<ReapResult> {
  await ensureSchema(env);
  const now = opts.now ?? Date.now();
  const maxAge = opts.maxScratchAgeMs ?? DEFAULT_MAX_SCRATCH_AGE_MS;
  const staleBefore = now - maxAge;

  const rows = await env.DB.prepare(
    `SELECT id, collection, expires_at, created_at FROM docs
      WHERE (expires_at IS NOT NULL AND expires_at > 0 AND expires_at <= ?)
         OR (expires_at IS NULL AND created_at IS NOT NULL AND created_at < ?)`,
  ).bind(now, staleBefore).all();

  const candidates: Candidate[] = [];
  for (const r of (rows.results ?? []) as Array<Record<string, unknown>>) {
    const collection = String(r["collection"] ?? LEGACY_COLLECTION);
    const exp = r["expires_at"];
    if (exp != null && Number(exp) > 0 && Number(exp) <= now) {
      candidates.push({ id: String(r["id"]), collection, reason: "expired" });
      continue;
    }
    // Age-based sweep applies ONLY to scratch. `lib` is durable and `_legacy` is not ours to
    // reap on a timer — an operator deletes it deliberately with forget_collection.
    if (isScratchCollection(collection)) {
      candidates.push({ id: String(r["id"]), collection, reason: "abandoned_scratch" });
    }
  }

  const out: ReapResult = {
    docs: 0, chunks: 0, vectors: 0, edges: 0, nodes: 0,
    collections: [], reasons: { expired: 0, abandoned_scratch: 0 },
  };
  const touched = new Set<string>();
  for (const c of candidates) {
    // Reuse the per-document delete so vectors, FTS rows, edges and node provenance all go the
    // same way they do on an explicit forget. The owning collection is passed so the ownership
    // check stays satisfied under STRICT_COLLECTION.
    const r = await forgetDocument(env, c.id, c.collection);
    if (!r.existed) continue;
    out.docs++;
    out.chunks += r.deleted.chunks;
    out.vectors += r.deleted.vectors;
    out.edges += r.deleted.edges;
    out.nodes += r.deleted.nodes_removed;
    out.reasons[c.reason]++;
    touched.add(c.collection);
  }
  out.collections = [...touched];

  try {
    console.log(JSON.stringify({ evt: "anamnesis.reap", ...out, now }));
  } catch { /* never throw */ }
  return out;
}
