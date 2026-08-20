import { describe, it, expect } from "vitest";
import { semanticChunk, estimateTokens, __testing, type EmbedFn } from "../src/chunk.js";

const { splitBlocks, splitSentences } = __testing;

/**
 * Deterministic fake embedder: an 8-dim one-hot keyed by the first token of each window.
 * → windows starting with the same word are identical (cosine 1, merge); different first
 *   word ⇒ orthogonal (cosine 0 < 0.55 threshold ⇒ semantic boundary). No Workers AI needed.
 */
const fakeEmbed: EmbedFn = async (texts) =>
  texts.map((t) => {
    const w = (t.trim().split(/\s+/)[0] || "").toLowerCase();
    let h = 0;
    for (const c of w) h = (h * 31 + c.charCodeAt(0)) % 8;
    const v = new Array(8).fill(0);
    v[h] = 1;
    return v;
  });

describe("estimateTokens", () => {
  it("scales with word count", () => {
    expect(estimateTokens("one two three four")).toBeGreaterThanOrEqual(4);
    expect(estimateTokens("")).toBe(1);
  });

  it("floors by char length when spaces are scarce (PDF/OCR)", () => {
    const dense = "a".repeat(400);
    expect(estimateTokens(dense)).toBeGreaterThanOrEqual(100);
  });
});

describe("resolveOpts", () => {
  const { resolveOpts } = __testing;

  it("keeps defaults when caller passes explicit undefined (MCP omit)", () => {
    const o = resolveOpts({ breakThreshold: undefined, maxTokens: undefined });
    expect(o.maxTokens).toBe(512);
    expect(o.breakThreshold).toBe(0.55);
  });

  it("honors an explicit maxTokens override", () => {
    expect(resolveOpts({ maxTokens: 64 }).maxTokens).toBe(64);
  });
});

describe("semanticChunk - undefined opts must not disable the token cap", () => {
  it("splits a long same-topic run when opts carry undefined maxTokens", async () => {
    const sent = "Alpha " + "word ".repeat(40) + ".";
    // ~52 tokens/window × 20 windows ≫ default maxTokens 512 → must split
    const text = (sent + " ").repeat(20);
    // Reproduce the MCP handler shape: always spread optional fields, even when unset.
    const { chunks, windowCount } = await semanticChunk(
      text, fakeEmbed, { breakThreshold: undefined, maxTokens: undefined, windowSentences: 1 });
    expect(windowCount).toBeGreaterThan(1);
    expect(chunks.length).toBeGreaterThan(1);
  });
});

describe("splitBlocks", () => {
  it("splits on blank lines and promotes headings", () => {
    const blocks = splitBlocks("Methods\n\nWe enrolled patients. They were adults.\n\nResults\n\nThe drug worked.");
    expect(blocks).toContain("Methods");
    expect(blocks).toContain("Results");
    expect(blocks.length).toBeGreaterThanOrEqual(4);
  });
});

describe("splitSentences", () => {
  it("does not break on common abbreviations", () => {
    const s = splitSentences("We used drug X (e.g. aspirin) in adults. It worked well.");
    expect(s.length).toBe(2);
  });
});

describe("semanticChunk - boundary detection", () => {
  it("merges similar adjacent windows and breaks on semantic shift", async () => {
    // 4 single-sentence windows: Alpha, Alpha, Beta, Beta ⇒ expect 2 chunks
    const text = "Alpha first point here. Alpha second point here. Beta different topic now. Beta more of it.";
    const { chunks } = await semanticChunk(text, fakeEmbed, { windowSentences: 1, breakThreshold: 0.55 });
    expect(chunks.length).toBe(2);
    expect(chunks[0].text.toLowerCase().startsWith("alpha")).toBe(true);
    expect(chunks[1].text.toLowerCase().startsWith("beta")).toBe(true);
    // each chunk carries a stored vector (mean-pooled)
    expect(chunks[0].vector?.length).toBe(8);
  });

  it("respects the token cap even within a similar run", async () => {
    const sent = "Alpha " + "word ".repeat(20) + ".";
    const text = (sent + " ").repeat(6); // all 'Alpha' ⇒ similar, but token cap forces splits
    const { chunks } = await semanticChunk(text, fakeEmbed, { windowSentences: 1, maxTokens: 40 });
    expect(chunks.length).toBeGreaterThan(1);
    for (const c of chunks) expect(c.tokenEst).toBeLessThanOrEqual(80); // cap + last-window slack
  });

  it("handles a single-window document", async () => {
    const { chunks } = await semanticChunk("Only one sentence here.", fakeEmbed, { windowSentences: 5 });
    expect(chunks.length).toBe(1);
    expect(chunks[0].idx).toBe(0);
  });

  it("returns nothing for empty input", async () => {
    const { chunks } = await semanticChunk("   ", fakeEmbed);
    expect(chunks.length).toBe(0);
  });
});
