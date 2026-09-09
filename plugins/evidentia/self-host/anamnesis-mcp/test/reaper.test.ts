import { describe, it, expect } from "vitest";
import { ingestDocument, listDocs, corpusStats } from "../src/rag.js";
import { reapExpired, DEFAULT_MAX_SCRATCH_AGE_MS } from "../src/reaper.js";
import { evalEnv, MockVectorize } from "./harness.js";

const SCRATCH = "evidentia:run:1234abcd5678";
const LIB = "evidentia:lib:corpus01";
const HOUR = 3600_000;

describe("expired scratch is actually collected (A2)", () => {
  it("deletes D1 rows AND the Vectorize vectors of an expired document", async () => {
    const vec = new MockVectorize();
    const env = evalEnv(vec);
    await ingestDocument(env, {
      text: "Alpha expiring body. Beta second sentence.",
      doc_id: "reap:a", collection: SCRATCH, ttl_hours: 1,
    });
    expect(vec.ids().filter((i) => i.startsWith("reap:a")).length).toBeGreaterThan(0);

    const r = await reapExpired(env, { now: Date.now() + 2 * HOUR });
    expect(r.docs).toBe(1);
    expect(r.vectors).toBeGreaterThan(0);
    // Vectorize was never TTL-filtered at all: expired vectors kept occupying the index and
    // kept coming back in the topK pool, crowding out live results before D1 dropped them.
    expect(vec.ids().filter((i) => i.startsWith("reap:a"))).toEqual([]);
    expect((await listDocs(env, SCRATCH)).docs.filter((d) => d["id"] === "reap:a")).toEqual([]);
  });

  it("leaves an unexpired scratch document alone", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, {
      text: "Gamma still fresh.", doc_id: "reap:fresh", collection: SCRATCH, ttl_hours: 24,
    });
    const r = await reapExpired(env, { now: Date.now() + HOUR });
    expect(r.docs).toBe(0);
    expect((await listDocs(env, SCRATCH)).docs.some((d) => d["id"] === "reap:fresh")).toBe(true);
  });

  it("never touches a durable lib collection", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: "Durable corpus body.", doc_id: "reap:lib", collection: LIB });
    const r = await reapExpired(env, { now: Date.now() + 10 * 365 * 24 * HOUR });
    expect(r.collections).not.toContain(LIB);
    expect((await listDocs(env, LIB)).docs.some((d) => d["id"] === "reap:lib")).toBe(true);
  });

  it("sweeps orphaned scratch that never got a TTL", async () => {
    const env = evalEnv(new MockVectorize());
    // No ttl_hours: the hook lifecycle was supposed to clean this up, but it is fail-open —
    // no key, no SessionEnd, a sub-agent ingest, or a crash all leave the row behind forever.
    await ingestDocument(env, { text: "Orphan body.", doc_id: "reap:orphan", collection: SCRATCH });
    const r = await reapExpired(env, { now: Date.now() + DEFAULT_MAX_SCRATCH_AGE_MS + HOUR });
    expect(r.docs).toBe(1);
    expect((await listDocs(env, SCRATCH)).docs.filter((d) => d["id"] === "reap:orphan")).toEqual([]);
  });

  it("does not sweep recent untagged scratch", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: "Recent body.", doc_id: "reap:recent", collection: SCRATCH });
    const r = await reapExpired(env, { now: Date.now() + HOUR });
    expect(r.docs).toBe(0);
  });
});

describe("legacy pollution is observable (B3 follow-up)", () => {
  it("reports legacy_docs in the global corpus_stats", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: "Unscoped body.", doc_id: "legacy:a" });
    const stats = await corpusStats(env);
    expect(stats["scope"]).toBe("global");
    expect(Number(stats["legacy_docs"])).toBeGreaterThan(0);
  });
});
