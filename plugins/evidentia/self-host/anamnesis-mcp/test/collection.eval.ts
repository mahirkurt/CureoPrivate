/**
 * P3 collection isolation eval — miniflare D1 + mock Vectorize/AI.
 * Does not touch the live corpus. Titles are ASCII (workerd header constraint).
 */
import { describe, it, expect, beforeEach } from "vitest";
import { ingestDocument, semanticSearch, forgetCollection, listDocs, corpusStats } from "../src/rag.js";
import { upsertTriples, neighbors, nodeKey } from "../src/graph.js";
import { runHybridQuery } from "../src/server.js";
import { CollectionRequiredError } from "../src/collection.js";
import { evalEnv, MockVectorize, NSCLC_DOC, EMICIZUMAB_DOC } from "./harness.js";

const A = "eval:run:aaaaaaaaaaaa";
const B = "eval:run:bbbbbbbbbbbb";
const DOC_A = "eval-nsclc-doc";
const DOC_B = "eval-emi-doc";

describe("P3 collection isolation", () => {
  let vz: MockVectorize;
  let env: ReturnType<typeof evalEnv>;

  beforeEach(async () => {
    vz = new MockVectorize();
    env = evalEnv(vz);
    await forgetCollection(env, A);
    await forgetCollection(env, B);
  });

  it("1. search/hybrid on B returns 0 chunks from A (NSCLC vs emicizumab)", async () => {
    await ingestDocument(env, { text: NSCLC_DOC, doc_id: DOC_A, collection: A, title: "NSCLC" });
    await ingestDocument(env, { text: EMICIZUMAB_DOC, doc_id: DOC_B, collection: B, title: "Emi" });

    const hits = await semanticSearch(env, { query: "emicizumab hemophilia factor VIII", collection: B, k: 8 });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((h) => h.doc_id === DOC_B)).toBe(true);
    expect(hits.every((h) => h.collection === B)).toBe(true);
    expect(hits.some((h) => h.doc_id === DOC_A)).toBe(false);

    const bundle = await runHybridQuery(env, { query: "emicizumab prophylaxis", collection: B, k: 8 });
    const chunks = bundle["chunks"] as Array<{ doc_id: string }>;
    expect(chunks.length).toBeGreaterThan(0);
    expect(chunks.every((c) => c.doc_id === DOC_B)).toBe(true);
    expect(chunks.some((c) => c.doc_id === DOC_A)).toBe(false);
  });

  it("2. forget_collection B does not delete A", async () => {
    await ingestDocument(env, { text: NSCLC_DOC, doc_id: DOC_A, collection: A });
    await ingestDocument(env, { text: EMICIZUMAB_DOC, doc_id: DOC_B, collection: B });

    const gone = await forgetCollection(env, B);
    expect(gone.existed).toBe(true);
    expect(gone.deleted.chunks).toBeGreaterThan(0);

    const listedA = await listDocs(env, A);
    expect(listedA.docs.some((d) => d["id"] === DOC_A)).toBe(true);
    const listedB = await listDocs(env, B);
    expect(listedB.docs.length).toBe(0);

    const hitsA = await semanticSearch(env, { query: "NSCLC pembrolizumab", collection: A, k: 8 });
    expect(hitsA.some((h) => h.doc_id === DOC_A)).toBe(true);
    expect(vz.ids().some((id) => id.startsWith(DOC_A + "::"))).toBe(true);
    expect(vz.ids().some((id) => id.startsWith(DOC_B + "::"))).toBe(false);

    const statsA = await corpusStats(env, A);
    expect(Number(statsA["docs"])).toBeGreaterThanOrEqual(1);
    const statsB = await corpusStats(env, B);
    expect(Number(statsB["docs"])).toBe(0);
  });

  it("3. re-ingest shorter doc does not leave old tail vectors", async () => {
    const long = EMICIZUMAB_DOC + " " + EMICIZUMAB_DOC + " " + EMICIZUMAB_DOC;
    const first = await ingestDocument(env, { text: long, doc_id: DOC_B, collection: B });
    expect(first.n_chunks).toBeGreaterThan(1);
    const before = vz.ids().filter((id) => id.startsWith(DOC_B + "::"));
    expect(before.length).toBe(first.n_chunks);

    const short = "Emicizumab prophylaxis for hemophilia A.";
    const second = await ingestDocument(env, { text: short, doc_id: DOC_B, collection: B });
    expect(second.n_chunks).toBeLessThan(first.n_chunks);

    const after = vz.ids().filter((id) => id.startsWith(DOC_B + "::"));
    expect(after.length).toBe(second.n_chunks);
    for (let i = second.n_chunks; i < first.n_chunks; i++) {
      expect(vz.store.has(`${DOC_B}::${i}`)).toBe(false);
    }

    const hits = await semanticSearch(env, { query: "emicizumab", collection: B, doc_id: DOC_B, k: 20 });
    expect(hits.every((h) => h.idx < second.n_chunks)).toBe(true);
  });

  it("4. unscoped hybrid_query is an MCP error, not empty success", async () => {
    await ingestDocument(env, { text: EMICIZUMAB_DOC, doc_id: DOC_B, collection: B });
    await expect(runHybridQuery(env, { query: "emicizumab", collection: "" }))
      .rejects.toBeInstanceOf(CollectionRequiredError);
    try {
      await runHybridQuery(env, { query: "emicizumab", collection: "" });
      expect.fail("unscoped hybrid_query must throw");
    } catch (e) {
      expect(e).toBeInstanceOf(CollectionRequiredError);
      expect((e as Error).message).toMatch(/requires collection/i);
    }
  });

  it("5. graph nodes do not merge across collections", async () => {
    await ingestDocument(env, { text: NSCLC_DOC, doc_id: DOC_A, collection: A });
    await ingestDocument(env, { text: EMICIZUMAB_DOC, doc_id: DOC_B, collection: B });

    await upsertTriples(env, [
      { subject: "emicizumab", predicate: "mentioned_in", object: "nsclc paper", doc_id: DOC_A },
    ], A);
    await upsertTriples(env, [
      { subject: "emicizumab", predicate: "treats", object: "hemophilia A", doc_id: DOC_B },
    ], B);

    expect(nodeKey(A, "emicizumab")).not.toBe(nodeKey(B, "emicizumab"));

    const nA = await neighbors(env, "emicizumab", 1, 50, A);
    const nB = await neighbors(env, "emicizumab", 1, 50, B);
    expect(nA.found).toBe(true);
    expect(nB.found).toBe(true);
    expect(nA.edges.some((e) => e.predicate === "treats")).toBe(false);
    expect(nB.edges.some((e) => e.predicate === "mentioned_in")).toBe(false);
    expect(nB.edges.some((e) => e.predicate === "treats")).toBe(true);
    expect(nA.entities).not.toContain(nodeKey(B, "emicizumab"));
    expect(nB.entities).not.toContain(nodeKey(A, "emicizumab"));
  });
});
