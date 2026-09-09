import { describe, it, expect } from "vitest";
import { upsertTriples, neighbors, subgraph, edgesByDocs } from "../src/graph.js";
import { ensureSchema } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const COLL = "evidentia:run:5a5a5a5a5a5a";

describe("subgraph induces on the whole edge set, not a pre-cut slice (A9)", () => {
  it("returns an induced edge that sits beyond the internal prefilter", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    const c = "evidentia:run:5a5a5a5a5a5b";

    // edgesTouching() pre-cuts with `ORDER BY weight DESC LIMIT 500` and the induced test
    // ("both endpoints in the requested set") used to run AFTER that cut. With more than 500
    // edges touching the seed set, non-induced neighbours crowd the real induced edges out and
    // subgraph returns EMPTY while the edge plainly exists.
    const fillers = Array.from({ length: 510 }, (_, i) => ({
      subject: "core-a", predicate: "rel", object: `filler-${i}`, doc_id: `d${i}`,
    }));
    await upsertTriples(env, fillers, c);
    // Inserted last so it falls outside the first 500 rows of the pre-cut.
    await upsertTriples(env, [{ subject: "core-a", predicate: "binds", object: "core-b", doc_id: "dx" }], c);

    const sg = await subgraph(env, ["core-a", "core-b"], 200, c);
    expect(sg.edges.length).toBe(1);
    expect(sg.edges[0].predicate).toBe("binds");
  }, 120_000);

  it("returns only edges whose BOTH endpoints are in the requested set", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    const c = "evidentia:run:5a5a5a5a5a5c";
    await upsertTriples(env, [
      { subject: "a", predicate: "binds", object: "b", doc_id: "d1" },
      { subject: "a", predicate: "rel", object: "outsider", doc_id: "d1" },
    ], c);
    const sg = await subgraph(env, ["a", "b"], 200, c);
    expect(sg.edges.map((e) => e.predicate)).toEqual(["binds"]);
  });
});

describe("neighbour expansion", () => {
  it("reaches a second-hop entity only when hops allows it", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    const c = "evidentia:run:5a5a5a5a5a5d";
    await upsertTriples(env, [
      { subject: "x", predicate: "rel", object: "y", doc_id: "d1" },
      { subject: "y", predicate: "rel", object: "z", doc_id: "d1" },
    ], c);
    const one = await neighbors(env, "x", 1, 100, c);
    expect(one.entities.some((e) => e.endsWith("::z"))).toBe(false);
    const two = await neighbors(env, "x", 2, 100, c);
    expect(two.entities.some((e) => e.endsWith("::z"))).toBe(true);
  });

  it("reports found:false for an unknown entity instead of erroring", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    const n = await neighbors(env, "nobody-here", 1, 10, COLL);
    expect(n.found).toBe(false);
    expect(n.edges).toEqual([]);
  });
});

describe("document-sourced graph context", () => {
  it("returns only edges attributed to the requested documents", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    const c = "evidentia:run:5a5a5a5a5a5e";
    await upsertTriples(env, [
      { subject: "p", predicate: "from", object: "q", doc_id: "want" },
      { subject: "r", predicate: "from", object: "s", doc_id: "other" },
    ], c);
    const edges = await edgesByDocs(env, ["want"], 40, c);
    expect(edges.map((e) => e.predicate)).toEqual(["from"]);
    expect(edges[0].doc_id).toBe("want");
  });
});
