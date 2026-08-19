import { describe, it, expect } from "vitest";
import { __testing } from "../src/graph.js";

const { nodeKey, edgeId } = __testing;

describe("nodeKey - entity normalization is collection-scoped", () => {
  it("lowercases and collapses whitespace", () => {
    expect(nodeKey("eval:run:aaaaaaaaaaaa", "  Emicizumab  "))
      .toBe("eval:run:aaaaaaaaaaaa::emicizumab");
    expect(nodeKey("eval:run:aaaaaaaaaaaa", "Hemophilia   A"))
      .toBe("eval:run:aaaaaaaaaaaa::hemophilia a");
  });
  it("is stable across surface variants inside one collection", () => {
    expect(nodeKey("eval:run:aaaaaaaaaaaa", "FACTOR VIII"))
      .toBe(nodeKey("eval:run:aaaaaaaaaaaa", "factor viii"));
  });
  it("same label in two collections is two nodes", () => {
    expect(nodeKey("eval:run:aaaaaaaaaaaa", "emicizumab"))
      .not.toBe(nodeKey("eval:run:bbbbbbbbbbbb", "emicizumab"));
  });
});

describe("edgeId - deterministic, order-sensitive, collection-scoped", () => {
  it("same triple => same id", async () => {
    const a = await edgeId("eval:run:aaaaaaaaaaaa", "emicizumab", "treats", "hemophilia a");
    const b = await edgeId("eval:run:aaaaaaaaaaaa", "emicizumab", "treats", "hemophilia a");
    expect(a).toBe(b);
    expect(a).toMatch(/^[0-9a-f]{24}$/);
  });
  it("different predicate => different id", async () => {
    const a = await edgeId("eval:run:aaaaaaaaaaaa", "emicizumab", "treats", "hemophilia a");
    const c = await edgeId("eval:run:aaaaaaaaaaaa", "emicizumab", "associated_with", "hemophilia a");
    expect(a).not.toBe(c);
  });
  it("same triple in two collections => different id", async () => {
    const a = await edgeId("eval:run:aaaaaaaaaaaa", "emicizumab", "treats", "hemophilia a");
    const b = await edgeId("eval:run:bbbbbbbbbbbb", "emicizumab", "treats", "hemophilia a");
    expect(a).not.toBe(b);
  });
});
