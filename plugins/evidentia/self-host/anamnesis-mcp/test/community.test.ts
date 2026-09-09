import { describe, it, expect } from "vitest";
import { upsertTriples } from "../src/graph.js";
import { ensureSchema } from "../src/rag.js";
import { exportGraph, upsertCommunities, summarizeCommunity, globalQuery } from "../src/community.js";
import { evalEnv, MockVectorize } from "./harness.js";

const A = "evidentia:lib:corpusA";
const B = "evidentia:lib:corpusB";

async function seed(env: ReturnType<typeof evalEnv>, coll: string, prefix: string) {
  await ensureSchema(env);
  await upsertTriples(env, [
    { subject: `${prefix}-drug`, predicate: "treats", object: `${prefix}-disease`, doc_id: "d1" },
    { subject: `${prefix}-drug`, predicate: "inhibits", object: `${prefix}-target`, doc_id: "d1" },
    { subject: `${prefix}-policy`, predicate: "governs", object: `${prefix}-market`, doc_id: "d2" },
  ], coll);
}

describe("graph export feeds the offline indexer", () => {
  it("exports only the requested collection's nodes and edges", async () => {
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    await seed(env, B, "beta");
    const g = await exportGraph(env, A);
    expect(g.collection).toBe(A);
    expect(g.edges.length).toBe(3);
    expect(g.edges.every((e) => e.subject.startsWith(A))).toBe(true);
    expect(JSON.stringify(g)).not.toContain("beta-");
  });
});

describe("community storage", () => {
  it("stores a partition and keeps it scoped to its collection", async () => {
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    const g = await exportGraph(env, A);
    const r = await upsertCommunities(env, A, [
      { level: 0, members: g.nodes.slice(0, 2).map((n) => n.id), edge_count: 2 },
      { level: 0, members: g.nodes.slice(2).map((n) => n.id), edge_count: 1 },
    ]);
    expect(r.upserted).toBe(2);

    const inB = await globalQuery(env, { collection: B, query: "alpha" });
    expect(inB.communities).toEqual([]);
  });

  it("replaces a previous partition rather than accumulating stale ones", async () => {
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    const g = await exportGraph(env, A);
    await upsertCommunities(env, A, [{ level: 0, members: g.nodes.map((n) => n.id), edge_count: 3 }]);
    await upsertCommunities(env, A, [
      { level: 0, members: g.nodes.slice(0, 2).map((n) => n.id), edge_count: 2 },
      { level: 0, members: g.nodes.slice(2).map((n) => n.id), edge_count: 1 },
    ]);
    const q = await globalQuery(env, { collection: A, query: "alpha", k: 10 });
    expect(q.communities.length).toBe(2);
  });
});

describe("global_query is honest about missing summaries", () => {
  it("returns member bundles and says the summary is absent", async () => {
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    const g = await exportGraph(env, A);
    await upsertCommunities(env, A, [{ level: 0, members: g.nodes.map((n) => n.id), edge_count: 3 }]);

    const q = await globalQuery(env, { collection: A, query: "alpha-drug" });
    expect(q.communities.length).toBe(1);
    expect(q.communities[0].summary_status).toBe("absent");
    expect(q.communities[0].summary).toBeNull();
    // Without a summary the caller still needs something to reason over.
    expect(q.communities[0].members.length).toBeGreaterThan(0);
  });

  it("reports a Claude-written summary once one exists", async () => {
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    const g = await exportGraph(env, A);
    await upsertCommunities(env, A, [{ level: 0, members: g.nodes.map((n) => n.id), edge_count: 3 }]);
    const id = (await globalQuery(env, { collection: A, query: "alpha" })).communities[0].id;

    await summarizeCommunity(env, A, id, "Alpha ilacı hastalığı tedavi eder ve hedefi inhibe eder.");
    const q = await globalQuery(env, { collection: A, query: "tedavi" });
    expect(q.communities[0].summary_status).toBe("claude");
    expect(q.communities[0].summary).toContain("tedavi");
  });

  it("refuses to summarise a community of another collection", async () => {
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    const g = await exportGraph(env, A);
    await upsertCommunities(env, A, [{ level: 0, members: g.nodes.map((n) => n.id), edge_count: 3 }]);
    const id = (await globalQuery(env, { collection: A, query: "alpha" })).communities[0].id;
    await expect(summarizeCommunity(env, B, id, "hijack")).rejects.toThrow(/collection/i);
  });
});

describe("forget_collection also drops the partition", () => {
  it("leaves no communities behind after a collection wipe", async () => {
    const { forgetCollection } = await import("../src/rag.js");
    const env = evalEnv(new MockVectorize());
    await seed(env, A, "alpha");
    const g = await exportGraph(env, A);
    await upsertCommunities(env, A, [{ level: 0, members: g.nodes.map((n) => n.id), edge_count: 3 }]);
    expect((await globalQuery(env, { collection: A, query: "alpha" })).communities.length).toBe(1);

    await forgetCollection(env, A);
    // A wiped working set that still serves communities would hand the next run a summary of
    // documents that no longer exist — evidence pointing at nothing.
    expect((await globalQuery(env, { collection: A, query: "alpha" })).communities).toEqual([]);
  });
});
