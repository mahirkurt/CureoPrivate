import { describe, it, expect } from "vitest";
import { __testing, RERANK_MODEL } from "../src/rag.js";
import { cosine } from "../src/embed.js";

const { chunkId, normalizeMatches, rrfFuse, buildFtsMatch } = __testing;

// Added 2026-08-07. anamnesis carried helper suites for chunk.ts and graph.ts but NONE for
// rag.ts or embed.ts, so hybrid-retrieval ranking and the FTS5 injection guard were unpinned.
// Test titles are ASCII on purpose -- the workerd pool sends them in an HTTP header.

describe("chunkId", () => {
  it("is stable and namespaced by doc", () => {
    expect(chunkId("doc-a", 0)).toBe("doc-a::0");
    expect(chunkId("doc-a", 12)).toBe("doc-a::12");
  });

  it("keeps two docs from colliding at the same index", () => {
    expect(chunkId("a", 1)).not.toBe(chunkId("b", 1));
  });
});

describe("normalizeMatches (Vectorize V1/V2 shape tolerance)", () => {
  it("unwraps the V2 { matches: [...] } envelope", () => {
    expect(normalizeMatches({ matches: [{ id: "x", score: 1 }] })).toEqual([{ id: "x", score: 1 }]);
  });

  it("accepts a bare array (V1)", () => {
    expect(normalizeMatches([{ id: "y", score: 2 }])).toEqual([{ id: "y", score: 2 }]);
  });

  it("returns an empty array for anything unrecognised instead of throwing", () => {
    for (const bad of [null, undefined, {}, { matches: "nope" }, 42, "str"]) {
      expect(normalizeMatches(bad)).toEqual([]);
    }
  });
});

describe("rrfFuse (Reciprocal Rank Fusion)", () => {
  it("ranks by RANK, not by raw score, so arms with different scales fuse fairly", () => {
    // Vector arm returns cosine (0..1), lexical arm returns BM25 (unbounded). RRF only
    // ever sees positions, so the scale mismatch cannot bias the result. Fusing two
    // exactly-opposed rankings must therefore surface all three ids, scored purely by
    // position -- no input score is consulted at all.
    const out = rrfFuse([["a", "b", "c"], ["c", "b", "a"]]);
    expect(out.map((r: any) => r.id).sort()).toEqual(["a", "b", "c"]);
  });

  it("gives a 1st+3rd placement a hair MORE than a 2nd+2nd one (RRF convexity)", () => {
    // 1/61 + 1/63 = 0.0322657 vs 2 x 1/62 = 0.0322581. This is a real, intended property of
    // 1/(k+rank): the curve is convex, so a confident-in-one-arm result edges out a
    // consistently-mediocre one. Pinned because it is counter-intuitive and easy to
    // "fix" into a wrong averaging scheme.
    const out = rrfFuse([["a", "b", "c"], ["c", "b", "a"]]);
    const by = Object.fromEntries(out.map((r: any) => [r.id, r.score]));
    expect(by.a).toBeCloseTo(1 / 61 + 1 / 63, 12);
    expect(by.b).toBeCloseTo(2 / 62, 12);
    expect(by.a).toBeGreaterThan(by.b);
    expect(by.c).toBeCloseTo(by.a, 12);
  });

  it("rewards an id that appears in several lists", () => {
    const out = rrfFuse([["x", "y"], ["x", "z"], ["x", "w"]]);
    expect(out[0].id).toBe("x");
  });

  it("uses the standard k=60 weighting", () => {
    const [top] = rrfFuse([["a"]]);
    expect(top.score).toBeCloseTo(1 / 61, 10);
    const [t2] = rrfFuse([["a"]], 1);
    expect(t2.score).toBeCloseTo(1 / 2, 10);
  });

  it("returns a descending, deduplicated ranking", () => {
    const out = rrfFuse([["a", "b"], ["b", "a"], ["b"]]);
    expect(new Set(out.map((r: any) => r.id)).size).toBe(out.length);
    for (let i = 1; i < out.length; i++) expect(out[i - 1].score).toBeGreaterThanOrEqual(out[i].score);
  });

  it("handles empty input without throwing", () => {
    expect(rrfFuse([])).toEqual([]);
    expect(rrfFuse([[], []])).toEqual([]);
  });
});

describe("buildFtsMatch (FTS5 operator-injection guard)", () => {
  it("emits quoted tokens joined by OR", () => {
    expect(buildFtsMatch("hemophilia emicizumab")).toBe('"hemophilia" OR "emicizumab"');
  });

  it("lowercases and drops single-character noise", () => {
    expect(buildFtsMatch("A Factor VIII")).toBe('"factor" OR "viii"');
  });

  it("neutralises FTS5 operators in user text", () => {
    // NEAR/ * / ^ / - / : are FTS5 syntax. After quoting they are literal terms, and the
    // punctuation is dropped by the unicode word split -- the MATCH cannot be broken out of.
    const m = buildFtsMatch('cancer NEAR/3 "drop table" AND x* ^y -z');
    expect(m).not.toContain("*");
    expect(m).not.toContain("^");
    expect(m).not.toMatch(/\bNEAR\/\d/);
    expect(m!.split(" OR ").every((t: string) => /^"[^"]*"$/.test(t))).toBe(true);
  });

  it("can never let a raw double quote reach the MATCH", () => {
    // A raw quote would close the FTS5 string literal. TWO independent guards stop it:
    // (1) the \p{L}\p{N} tokeniser treats " as a separator, so it is dropped before quoting;
    // (2) a .replace(/"/g,'""') escape behind it. Guard (1) fires first, so the escape is
    // unreachable defence-in-depth today -- assert the OBSERVABLE property (no stray quote),
    // not the mechanism, so either guard alone still satisfies this test.
    const m = buildFtsMatch('say"hi there');
    expect(m).toBe('"say" OR "hi" OR "there"');
    expect(m!.split(" OR ").every((t: string) => /^"[^"]*"$/.test(t))).toBe(true);
  });

  it("caps the token count so a huge query cannot blow up the MATCH", () => {
    const many = Array.from({ length: 100 }, (_, i) => `tok${i}`).join(" ");
    expect(buildFtsMatch(many)!.split(" OR ")).toHaveLength(24);
  });

  it("returns null (not an empty MATCH) when nothing survives tokenisation", () => {
    // An empty MATCH would be an FTS5 syntax error; the caller short-circuits on null.
    expect(buildFtsMatch("")).toBe(null);
    expect(buildFtsMatch("   ")).toBe(null);
    expect(buildFtsMatch("a b c")).toBe(null);   // all single-char
    expect(buildFtsMatch("!!! ??? ***")).toBe(null);
  });

  it("keeps non-Latin script (the corpus is Turkish-heavy)", () => {
    expect(buildFtsMatch("kanıt sentezi")).toBe('"kanıt" OR "sentezi"');
  });
});

describe("cosine similarity", () => {
  it("is 1 for identical vectors and 0 for orthogonal ones", () => {
    expect(cosine([1, 0], [1, 0])).toBeCloseTo(1, 10);
    expect(cosine([1, 0], [0, 1])).toBeCloseTo(0, 10);
  });

  it("is scale-invariant", () => {
    expect(cosine([1, 2, 3], [10, 20, 30])).toBeCloseTo(1, 10);
  });

  it("is -1 for opposed vectors", () => {
    expect(cosine([1, 0], [-1, 0])).toBeCloseTo(-1, 10);
  });

  it("returns 0 for a zero vector instead of NaN", () => {
    // A NaN here would silently poison every downstream ranking comparison.
    expect(cosine([0, 0], [1, 1])).toBe(0);
    expect(cosine([], [])).toBe(0);
  });

  it("compares over the shorter length when dimensions differ", () => {
    expect(cosine([1, 0, 999], [1, 0])).toBeCloseTo(1, 10);
  });
});

describe("rerank model", () => {
  it("is the bge cross-encoder the pipeline was tuned against", () => {
    expect(RERANK_MODEL).toBe("@cf/baai/bge-reranker-base");
  });
});
