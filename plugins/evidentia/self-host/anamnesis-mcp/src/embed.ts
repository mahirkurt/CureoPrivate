/**
 * embed.ts — Workers AI embedding wrapper for anamnesis-mcp.
 *
 * Model: @cf/baai/bge-m3 — MULTILINGUAL (chosen deliberately: medical research mixes a
 * Turkish query surface with an English full-text corpus; an English-only model like
 * bge-base-en-v1.5 would degrade Turkish-query → English-chunk recall). bge-m3 = 1024 dims.
 *   → The Vectorize index MUST be created with `--dimensions=1024 --metric=cosine`.
 *
 * Call shape (VERIFIED against Cloudflare docs 2026-06):
 *   await env.AI.run("@cf/baai/bge-m3", { text: string[] })   // synchronous form
 * Response shape has drifted across CF doc revisions: newer docs return `{ shape, data }`
 * (data: number[][]); older RAG tutorials return `{ results }` (number[][]). We normalize
 * BOTH defensively rather than assume one — no fabrication of a single canonical field.
 *
 * NOTE: bge-m3 also exposes a batch/reranker binding form `{ requests:[{query,contexts}] }`
 * with `{ queueRequest:true }` that returns `{ status:"queued", request_id }` and must be
 * polled. We do NOT use that path — a request-scoped MCP tool needs synchronous embeddings.
 */

export const EMBED_MODEL = "@cf/baai/bge-m3";
export const EMBED_DIMS = 1024;

export interface AiEnv {
  AI: { run: (model: string, input: unknown) => Promise<unknown> };
}

/** Normalize the several documented Workers-AI embedding response shapes to number[][]. */
function normalizeVectors(raw: unknown): number[][] {
  const r = raw as Record<string, unknown> | undefined;
  // newer: { shape, data: number[][] }
  if (r && Array.isArray(r["data"])) return r["data"] as number[][];
  // some builds nest under result
  const res = r ? (r["result"] as Record<string, unknown> | undefined) : undefined;
  if (res && Array.isArray(res["data"])) return res["data"] as number[][];
  // older RAG tutorials: { results: number[][] }
  if (r && Array.isArray(r["results"])) return r["results"] as number[][];
  // already a bare array
  if (Array.isArray(raw)) return raw as number[][];
  throw new Error("Unrecognized Workers-AI embedding response shape (no data/results array)");
}

/**
 * Embed an array of texts. Batches to stay within Workers-AI per-request limits
 * (bge-m3 accepts up to ~100 inputs/call; we cap at 64 to be conservative).
 */
export async function embedTexts(env: AiEnv, texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];
  const BATCH = 64;
  const out: number[][] = [];
  for (let i = 0; i < texts.length; i += BATCH) {
    const slice = texts.slice(i, i + BATCH).map((t) => (t && t.trim() ? t : " "));
    const raw = await env.AI.run(EMBED_MODEL, { text: slice });
    const vecs = normalizeVectors(raw);
    if (vecs.length !== slice.length) {
      throw new Error(`embedding count mismatch: got ${vecs.length} for ${slice.length} inputs`);
    }
    for (const v of vecs) out.push(v);
  }
  return out;
}

/** Single-text convenience (query embedding). */
export async function embedOne(env: AiEnv, text: string): Promise<number[]> {
  const [v] = await embedTexts(env, [text]);
  return v;
}

/** Cosine similarity for two equal-length vectors (used by semantic chunk boundary detection). */
export function cosine(a: number[], b: number[]): number {
  let dot = 0;
  let na = 0;
  let nb = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  if (na === 0 || nb === 0) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}
