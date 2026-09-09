import { describe, it, expect } from "vitest";
import { ingestDocument, semanticSearch, hybridRetrieve } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const COLL = "evidentia:run:ddddeeeeffff";

/** Records every filter the Worker sends to Vectorize, so we can assert the query we issue. */
class RecordingVectorize extends MockVectorize {
  filters: Array<Record<string, unknown> | undefined> = [];
  override async query(vector: number[], opts: Record<string, unknown>): Promise<unknown> {
    this.filters.push(opts["filter"] as Record<string, unknown> | undefined);
    return super.query(vector, opts);
  }
}

describe("embedder outage degrades instead of failing (A6)", () => {
  it("still answers from the lexical arm when Workers AI is down", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, {
      text: "Pembrolizumab treats NSCLC adenocarcinoma of the lung.",
      doc_id: "deg:a", collection: COLL,
    });
    const broken = { ...env, AI: { run: async () => { throw new Error("Workers AI down"); } } };
    const res = await hybridRetrieve(broken, { query: "pembrolizumab", collection: COLL });
    expect(res.chunks.length).toBeGreaterThan(0);
    expect(res.degraded).toBe("vector_unavailable");
    expect(res.chunks[0].retrieval).toContain("lexical");
  });

  it("reports no degradation on the healthy path", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, {
      text: "Emicizumab is used for hemophilia A prophylaxis.", doc_id: "deg:b", collection: COLL,
    });
    const res = await hybridRetrieve(env, { query: "emicizumab", collection: COLL });
    expect(res.degraded).toBeNull();
  });
});

describe("score scale is self-describing (A11)", () => {
  it("labels an RRF score when rerank is off", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, {
      text: "Emicizumab bridges factor IXa and factor X in hemophilia A.",
      doc_id: "sk:a", collection: COLL,
    });
    const hits = await semanticSearch(env, { query: "emicizumab", collection: COLL, rerank: false });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0].score_kind).toBe("rrf");
  });

  it("labels a cross-encoder score when rerank runs", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, {
      text: "Emicizumab prophylaxis lowers bleed rates. Factor VIII inhibitors do not block it.",
      doc_id: "sk:b", collection: COLL,
    });
    const hits = await semanticSearch(env, { query: "emicizumab", collection: COLL, rerank: true });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0].score_kind).toBe("rerank");
  });
});

describe("multi-document narrowing is pushed to the vector arm (A5)", () => {
  it("scopes the Vectorize query to every requested doc_id, not just a single one", async () => {
    const vec = new RecordingVectorize();
    const env = evalEnv(vec);
    await ingestDocument(env, { text: "Alpha document about lung cancer.", doc_id: "nar:a", collection: COLL });
    await ingestDocument(env, { text: "Beta document about hemophilia.", doc_id: "nar:b", collection: COLL });
    vec.filters.length = 0;
    await semanticSearch(env, { query: "document", collection: COLL, doc_ids: ["nar:a", "nar:b"], rerank: false });
    expect(vec.filters.length).toBeGreaterThan(0);
    // Before the fix the filter carried only `collection`, so Vectorize returned an unfiltered
    // top-K across the whole collection and D1 discarded most of it — recall collapsed exactly
    // on the narrowing path the plugin contracts prescribe.
    const f = vec.filters[0] as Record<string, unknown>;
    expect(f["doc_id"]).toEqual({ $in: ["nar:a", "nar:b"] });
  });

  it("still uses an equality filter for a single doc_id", async () => {
    const vec = new RecordingVectorize();
    const env = evalEnv(vec);
    await ingestDocument(env, { text: "Gamma document about staging.", doc_id: "nar:c", collection: COLL });
    vec.filters.length = 0;
    await semanticSearch(env, { query: "document", collection: COLL, doc_ids: ["nar:c"], rerank: false });
    expect((vec.filters[0] as Record<string, unknown>)["doc_id"]).toBe("nar:c");
  });
});

describe("ingest input size is bounded (A12)", () => {
  it("rejects a body beyond the byte cap instead of embedding 400 windows first", async () => {
    const env = evalEnv(new MockVectorize());
    const huge = "Sentence about lungs. ".repeat(60_000); // > 1 MB
    await expect(
      ingestDocument(env, { text: huge, doc_id: "big:a", collection: COLL }),
    ).rejects.toThrow(/too large|byte/i);
  });
});
