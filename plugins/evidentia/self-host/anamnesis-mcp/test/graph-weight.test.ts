import { describe, it, expect } from "vitest";
import { upsertTriples, neighbors } from "../src/graph.js";
import { ensureSchema } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const COLL = "evidentia:run:cafe1234beef";
const T = (object: string, doc_id?: string) => ({
  subject: "emicizumab", predicate: "treats", object, ...(doc_id ? { doc_id } : {}),
});

describe("edge weight measures evidence, not repetition (A10)", () => {
  it("does not inflate weight when the same triple is re-asserted from the same document", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    await upsertTriples(env, [T("hemophilia-a", "doc-1")], COLL);
    await upsertTriples(env, [T("hemophilia-a", "doc-1")], COLL);
    await upsertTriples(env, [T("hemophilia-a", "doc-1")], COLL);

    const n = await neighbors(env, "emicizumab", 1, 10, COLL);
    const edge = n.edges.find((e) => e.object.endsWith("hemophilia-a"));
    expect(edge).toBeDefined();
    // Previously `weight = weight + 1` on every re-assert, so weight counted how many times
    // the orchestrator happened to repeat itself and every `ORDER BY weight DESC` inherited
    // that bias. Weight must count DISTINCT supporting documents.
    expect(edge!.weight).toBe(1);
    expect(edge!.assert_count).toBe(3);
  });

  it("raises weight when a second document supports the same claim", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    await upsertTriples(env, [T("bleed-reduction", "doc-1")], COLL);
    await upsertTriples(env, [T("bleed-reduction", "doc-2")], COLL);

    const n = await neighbors(env, "emicizumab", 1, 10, COLL);
    const edge = n.edges.find((e) => e.object.endsWith("bleed-reduction"));
    expect(edge!.weight).toBe(2);
    expect(edge!.doc_ids).toEqual(["doc-1", "doc-2"]);
  });

  it("ranks a two-document claim above a repeated one-document claim", async () => {
    const env = evalEnv(new MockVectorize());
    await ensureSchema(env);
    const c = "evidentia:run:cafe1234bee2";
    await upsertTriples(env, [T("repeated", "doc-1"), T("repeated", "doc-1"), T("repeated", "doc-1")], c);
    await upsertTriples(env, [T("corroborated", "doc-1"), T("corroborated", "doc-2")], c);

    const n = await neighbors(env, "emicizumab", 1, 10, c);
    expect(n.edges[0].object.endsWith("corroborated")).toBe(true);
  });
});
