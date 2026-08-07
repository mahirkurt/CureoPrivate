import { describe, it, expect } from "vitest";
import { __testing } from "../src/graph.js";

const { nodeKey, edgeId } = __testing;

describe("nodeKey - entity normalization", () => {
  it("lowercases and collapses whitespace", () => {
    expect(nodeKey("  Emicizumab  ")).toBe("emicizumab");
    expect(nodeKey("Hemophilia   A")).toBe("hemophilia a");
  });
  it("is stable across surface variants", () => {
    expect(nodeKey("FACTOR VIII")).toBe(nodeKey("factor viii"));
  });
});

describe("edgeId - deterministic, order-sensitive", () => {
  it("same triple => same id", async () => {
    const a = await edgeId("emicizumab", "treats", "hemophilia a");
    const b = await edgeId("emicizumab", "treats", "hemophilia a");
    expect(a).toBe(b);
    expect(a).toMatch(/^[0-9a-f]{24}$/);
  });
  it("different predicate => different id", async () => {
    const a = await edgeId("emicizumab", "treats", "hemophilia a");
    const c = await edgeId("emicizumab", "associated_with", "hemophilia a");
    expect(a).not.toBe(c);
  });
});
