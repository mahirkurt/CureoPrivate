/**
 * Offline eval harness — mock Vectorize + mock Workers AI, real miniflare D1.
 * Never talks to the live anamnesis-index / production D1.
 */
import { env } from "cloudflare:workers";
import type { AnamEnv } from "../src/server.js";
import type { VectorizeBinding } from "../src/rag.js";

const DIM = 32;
const VOCAB = [
  "nsclc", "lung", "adenocarcinoma", "pembrolizumab", "checkpoint", "egfr",
  "emicizumab", "hemophilia", "factor", "viii", "inhibitor", "bleed",
];

function tokenize(text: string): string[] {
  return (text.toLowerCase().match(/[a-z0-9]+/g) ?? []);
}

export function bagEmbed(text: string): number[] {
  const v = new Array(DIM).fill(0);
  for (const w of tokenize(text)) {
    const i = VOCAB.indexOf(w);
    if (i >= 0) v[i] += 1;
    else {
      let h = 0;
      for (let k = 0; k < w.length; k++) h = (h * 31 + w.charCodeAt(k)) >>> 0;
      v[12 + (h % (DIM - 12))] += 0.2;
    }
  }
  let n = 0;
  for (const x of v) n += x * x;
  n = Math.sqrt(n) || 1;
  return v.map((x) => x / n);
}

function cosine(a: number[], b: number[]): number {
  let d = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) d += a[i] * b[i];
  return d;
}

export class MockVectorize implements VectorizeBinding {
  store = new Map<string, { values: number[]; metadata: Record<string, unknown> }>();

  async upsert(vectors: Array<{ id: string; values: number[]; metadata?: Record<string, unknown> }>): Promise<unknown> {
    for (const v of vectors) this.store.set(v.id, { values: v.values, metadata: v.metadata ?? {} });
    return { count: vectors.length };
  }

  async deleteByIds(ids: string[]): Promise<unknown> {
    for (const id of ids) this.store.delete(id);
    return { count: ids.length };
  }

  async query(vector: number[], opts: Record<string, unknown>): Promise<unknown> {
    const filter = (opts["filter"] ?? {}) as Record<string, unknown>;
    const topK = Number(opts["topK"] ?? 10);
    const scored: Array<{ id: string; score: number; metadata: Record<string, unknown> }> = [];
    for (const [id, row] of this.store) {
      if (filter["collection"] != null && row.metadata["collection"] !== filter["collection"]) continue;
      if (filter["doc_id"] != null && row.metadata["doc_id"] !== filter["doc_id"]) continue;
      scored.push({ id, score: cosine(vector, row.values), metadata: row.metadata });
    }
    scored.sort((a, b) => b.score - a.score);
    return { matches: scored.slice(0, topK) };
  }

  ids(): string[] { return [...this.store.keys()]; }
}

export class MockAI {
  async run(model: string, input: unknown): Promise<unknown> {
    const inp = input as Record<string, unknown>;
    if (String(model).includes("reranker")) {
      const q = String(inp["query"] ?? "");
      const ctx = (inp["contexts"] as Array<{ text?: string }>) ?? [];
      const qv = bagEmbed(q);
      return ctx.map((c, id) => ({ id, score: cosine(qv, bagEmbed(String(c.text ?? ""))) }));
    }
    const texts = (inp["text"] as string[]) ?? [];
    return { data: texts.map((t) => bagEmbed(t)) };
  }
}

export function evalEnv(vectorize: MockVectorize = new MockVectorize()): AnamEnv & { VECTORIZE: MockVectorize } {
  const db = (env as { DB: AnamEnv["DB"] }).DB;
  if (!db) throw new Error("miniflare D1 binding DB is missing — wrangler.jsonc d1_databases required");
  return { DB: db, VECTORIZE: vectorize, AI: new MockAI() };
}

export const NSCLC_DOC =
  "NSCLC adenocarcinoma of the lung is treated with pembrolizumab checkpoint blockade. " +
  "EGFR-mutant NSCLC may also receive tyrosine-kinase inhibitors. " +
  "Lung-cancer staging for NSCLC uses TNM. " +
  "Pembrolizumab improved overall survival in metastatic NSCLC adenocarcinoma. " +
  "Checkpoint inhibitors changed first-line NSCLC care. " +
  "This NSCLC paragraph is deliberately long so semantic chunking yields several windows.";

export const EMICIZUMAB_DOC =
  "Emicizumab is a bispecific antibody used for hemophilia A prophylaxis. " +
  "It bridges factor IXa and factor X, substituting for missing factor VIII. " +
  "Patients with factor VIII inhibitors can receive emicizumab. " +
  "Bleed rates fall under emicizumab prophylaxis in hemophilia A. " +
  "Emicizumab does not treat NSCLC or lung adenocarcinoma. " +
  "This hemophilia paragraph is deliberately long so semantic chunking yields several windows.";
