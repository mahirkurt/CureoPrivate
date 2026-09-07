import { describe, it, expect } from "vitest";
import { ingestDocument, forgetDocument, listDocs, semanticSearch } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const A = "evidentia:run:aaaa0000aaaa";
const B = "cureolex:sess:bbbb1111bbbb";

describe("forget_document cannot reach across collections (B1)", () => {
  it("refuses to delete a document that belongs to another collection", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: "Alpha tenant document.", doc_id: "ten:a", collection: A });

    // Tenant B knows the id but must not be able to destroy tenant A's row. Before this guard
    // forget_document took ONLY doc_id, resolved the collection from the row, and deleted it —
    // the sole protection was a fail-open Python hook that no claude.ai / ChatGPT / Cursor /
    // curl client ever runs.
    await expect(forgetDocument(env, "ten:a", B)).rejects.toThrow(/collection/i);
    expect((await listDocs(env, A)).docs.filter((d) => d["id"] === "ten:a").length).toBe(1);
  });

  it("deletes when the caller names the owning collection", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: "Alpha tenant document.", doc_id: "ten:b", collection: A });
    const r = await forgetDocument(env, "ten:b", A);
    expect(r.existed).toBe(true);
    expect((await listDocs(env, A)).docs.filter((d) => d["id"] === "ten:b").length).toBe(0);
  });

  it("stays idempotent for an unknown id", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await forgetDocument(env, "ten:missing", A);
    expect(r.existed).toBe(false);
  });
});

describe("STRICT_COLLECTION flagged transition (B2/B3)", () => {
  const strict = (e: object) => ({ ...e, STRICT_COLLECTION: "1" });

  it("still buckets an unscoped ingest into _legacy while the flag is off", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, { text: "Unscoped body.", doc_id: "flag:a" });
    expect(r.collection).toBe("_legacy");
  });

  it("refuses an unscoped ingest once the flag is on", async () => {
    const env = strict(evalEnv(new MockVectorize()));
    await expect(
      ingestDocument(env as never, { text: "Unscoped body.", doc_id: "flag:b" }),
    ).rejects.toThrow(/collection/i);
  });

  it("refuses an unscoped search once the flag is on", async () => {
    const env = strict(evalEnv(new MockVectorize()));
    await expect(
      semanticSearch(env as never, { query: "anything" }),
    ).rejects.toThrow(/collection/i);
  });

  it("allows a doc-scoped search under the flag", async () => {
    const base = evalEnv(new MockVectorize());
    await ingestDocument(base, { text: "Alpha scoped body.", doc_id: "flag:c", collection: A });
    const hits = await semanticSearch(strict(base) as never, {
      query: "alpha", collection: A, rerank: false,
    });
    expect(hits.length).toBeGreaterThan(0);
  });

  it("refuses an unscoped forget_document once the flag is on", async () => {
    const env = strict(evalEnv(new MockVectorize()));
    await expect(forgetDocument(env as never, "flag:d")).rejects.toThrow(/collection/i);
  });
});
