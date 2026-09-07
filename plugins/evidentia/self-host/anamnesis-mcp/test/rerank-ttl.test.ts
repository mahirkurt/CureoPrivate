import { describe, it, expect } from "vitest";
import { ingestDocument, semanticSearch, listDocs } from "../src/rag.js";
import { evalEnv, MockVectorize, bagEmbed } from "./harness.js";

const COLL = "evidentia:run:7c7c7c7c7c7c";

/** Workers AI has published several reranker response shapes across doc revisions; the Worker
 *  normalises `response` / `result` / a bare array. Pin all of them plus the failure fallback. */
function aiWithRerankShape(shape: "response" | "result" | "bare" | "garbage" | "throw") {
  return {
    run: async (model: string, input: unknown) => {
      const inp = input as Record<string, unknown>;
      if (!String(model).includes("reranker")) {
        return { data: ((inp["text"] as string[]) ?? []).map((t) => bagEmbed(t)) };
      }
      if (shape === "throw") throw new Error("reranker unavailable");
      const ctx = (inp["contexts"] as Array<{ text?: string }>) ?? [];
      const ranked = ctx.map((_, id) => ({ id, score: 1 - id / 100 }));
      if (shape === "response") return { response: ranked };
      if (shape === "result") return { result: ranked };
      if (shape === "bare") return ranked;
      return { unexpected: "shape" };
    },
  };
}

const BODY =
  "Pembrolizumab treats NSCLC adenocarcinoma. Checkpoint blockade changed first-line care. " +
  "EGFR-mutant lung tumours receive inhibitors instead. Staging for NSCLC uses TNM.";

describe("reranker response-shape tolerance", () => {
  for (const shape of ["response", "result", "bare"] as const) {
    it(`accepts the '${shape}' envelope and reports a rerank score`, async () => {
      const base = evalEnv(new MockVectorize());
      await ingestDocument(base, { text: BODY, doc_id: `rr:${shape}`, collection: COLL });
      const hits = await semanticSearch({ ...base, AI: aiWithRerankShape(shape) }, {
        query: "pembrolizumab", collection: COLL, doc_id: `rr:${shape}`,
      });
      expect(hits.length).toBeGreaterThan(0);
      expect(hits[0].score_kind).toBe("rerank");
    });
  }

  for (const shape of ["garbage", "throw"] as const) {
    it(`falls back to the fused order when the reranker returns '${shape}'`, async () => {
      const base = evalEnv(new MockVectorize());
      await ingestDocument(base, { text: BODY, doc_id: `rrf:${shape}`, collection: COLL });
      const hits = await semanticSearch({ ...base, AI: aiWithRerankShape(shape) }, {
        query: "pembrolizumab", collection: COLL, doc_id: `rrf:${shape}`,
      });
      // A broken reranker must degrade to RRF order, never throw away the search.
      expect(hits.length).toBeGreaterThan(0);
      expect(hits[0].score_kind).toBe("rrf");
    });
  }
});

describe("expired scratch is filtered at READ time, before the reaper runs", () => {
  it("hides an expired document from search and from list_docs", async () => {
    const vec = new MockVectorize();
    const env = evalEnv(vec);
    await ingestDocument(env, {
      text: BODY, doc_id: "ttl:a", collection: COLL, ttl_hours: 1,
    });
    expect((await semanticSearch(env, { query: "pembrolizumab", collection: COLL, doc_id: "ttl:a", rerank: false })).length)
      .toBeGreaterThan(0);

    // Expire it in place: the nightly reaper has not run yet, so the rows and vectors are
    // still there and only the read-side filter stands between them and the caller.
    await env.DB.prepare(`UPDATE docs SET expires_at = ? WHERE id = ?`)
      .bind(Date.now() - 1000, "ttl:a").run();

    expect(await semanticSearch(env, { query: "pembrolizumab", collection: COLL, doc_id: "ttl:a", rerank: false }))
      .toEqual([]);
    expect((await listDocs(env, COLL)).docs.some((d) => d["id"] === "ttl:a")).toBe(false);
    expect(vec.ids().some((i) => i.startsWith("ttl:a"))).toBe(true); // still occupying the index
  });
});
