import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const { placeholders, shapeHits, SNIPPET_CHARS, EMBED_MODEL } = __testing;

// Added 2026-08-07. This Worker shipped with no server.test.ts. Test titles are ASCII on
// purpose -- the workerd test pool sends them in an HTTP header and warns on non-ASCII.

describe("bound placeholders (injection safety)", () => {
  it("emits one placeholder per id", () => {
    expect(placeholders(1)).toBe("?");
    expect(placeholders(3)).toBe("?,?,?");
    expect(placeholders(0)).toBe("");
  });

  it("never emits a value, only placeholders", () => {
    // The ids are passed to .bind(); if this ever returned literals instead, a chunk id
    // could close the IN(...) clause and inject SQL.
    expect(placeholders(5)).toMatch(/^[?,]+$/);
    expect(placeholders(5).split(",")).toHaveLength(5);
  });
});

describe("hit shaping: provenance fallback ladder", () => {
  it("prefers the D1 row over vector metadata", () => {
    const matches = [{ id: "a", score: 0.9, metadata: { file: "stale.md", section: "old" } }];
    const rows = { a: { file: "oncology-layer.md", section: "GRADE", text: "body" } };
    expect(shapeHits(matches, rows)[0]).toEqual({
      file: "oncology-layer.md", section: "GRADE", score: 0.9, snippet: "body",
    });
  });

  it("falls back to vector metadata when D1 has no row", () => {
    const matches = [{ id: "b", score: 0.5, metadata: { file: "hta-layer.md", section: "ICER" } }];
    expect(shapeHits(matches, {})[0]).toEqual({
      file: "hta-layer.md", section: "ICER", score: 0.5, snippet: "",
    });
  });

  it("returns null provenance rather than inventing a file or section", () => {
    expect(shapeHits([{ id: "c", score: 0.1 }], {})[0]).toEqual({
      file: null, section: null, score: 0.1, snippet: "",
    });
  });

  it("returns an empty array for no matches", () => {
    expect(shapeHits([], {})).toEqual([]);
  });

  it("preserves match order (Vectorize already ranked them)", () => {
    const matches = [{ id: "x", score: 0.9 }, { id: "y", score: 0.8 }, { id: "z", score: 0.7 }];
    expect(shapeHits(matches, {}).map((h: any) => h.score)).toEqual([0.9, 0.8, 0.7]);
  });
});

describe("retrieve-don't-dump snippet boundary", () => {
  it("caps the snippet at SNIPPET_CHARS", () => {
    const long = "x".repeat(SNIPPET_CHARS * 3);
    const out = shapeHits([{ id: "a", score: 1 }], { a: { text: long } })[0];
    expect(out.snippet).toHaveLength(SNIPPET_CHARS);
  });

  it("pins the cap so widening it is a deliberate, reviewed change", () => {
    // kb_search returns POINTERS; raising this turns the index into a bulk dump channel
    // and breaks the plugin's retrieve-don't-dump contract.
    expect(SNIPPET_CHARS).toBe(500);
  });

  it("leaves a short body intact", () => {
    const out = shapeHits([{ id: "a", score: 1 }], { a: { text: "short body" } })[0];
    expect(out.snippet).toBe("short body");
  });

  it("coerces a missing or non-string body to an empty string, not 'undefined'", () => {
    expect(shapeHits([{ id: "a", score: 1 }], { a: {} })[0].snippet).toBe("");
    expect(shapeHits([{ id: "a", score: 1 }], { a: { text: null } })[0].snippet).toBe("");
  });
});

describe("embedding model", () => {
  it("is the 1024-dim bge-m3 the Vectorize index was built with", () => {
    // A model swap silently invalidates every stored vector: the index would still answer,
    // just with meaningless neighbours. Pin it.
    expect(EMBED_MODEL).toBe("@cf/baai/bge-m3");
  });
});
