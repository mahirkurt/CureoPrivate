import { describe, it, expect } from "vitest";
import { semanticChunk, type EmbedFn } from "../src/chunk.js";

/** Same deterministic fake embedder as chunk.test.ts: one-hot on the window's first token. */
const fakeEmbed: EmbedFn = async (texts) =>
  texts.map((t) => {
    const w = (t.trim().split(/\s+/)[0] || "").toLowerCase();
    let h = 0;
    for (const c of w) h = (h * 31 + c.charCodeAt(0)) % 8;
    const v = new Array(8).fill(0);
    v[h] = 1;
    return v;
  });

const norm = (s: string) => s.replace(/\s+/g, " ").trim();

/** Wrapped-line prose: the shape that defeats the old indexOf() offset recovery, because
 *  splitBlocks joins intra-paragraph lines with " " so the chunk text never occurs verbatim. */
const WRAPPED = [
  "Alpha opens the argument here.",
  "Alpha continues onto a second wrapped line.",
  "",
  "Beta introduces a different claim.",
  "Beta closes the second paragraph.",
].join("\n");

describe("chunk source spans (A4 — no fabricated offsets)", () => {
  it("every chunk span slices back to that chunk's own text", async () => {
    const { chunks } = await semanticChunk(WRAPPED, fakeEmbed, {});
    expect(chunks.length).toBeGreaterThan(0);
    for (const c of chunks) {
      expect(norm(WRAPPED.slice(c.charStart, c.charEnd))).toBe(norm(c.text));
    }
  });

  it("spans stay ordered and inside the source", async () => {
    const { chunks } = await semanticChunk(WRAPPED, fakeEmbed, {});
    let prevEnd = 0;
    for (const c of chunks) {
      expect(c.charStart).toBeGreaterThanOrEqual(prevEnd);
      expect(c.charEnd).toBeLessThanOrEqual(WRAPPED.length);
      prevEnd = c.charEnd;
    }
  });
});

describe("truncation reporting (A1 — no silent loss)", () => {
  const MANY = Array.from({ length: 12 }, (_, i) => `Topic${i} states its own claim plainly.`).join("\n\n");

  it("reports how far it actually indexed when the window cap fires", async () => {
    const res = await semanticChunk(MANY, fakeEmbed, { maxWindows: 3 });
    expect(res.truncated).toBe(true);
    expect(res.charsIndexed).toBeGreaterThan(0);
    expect(res.charsIndexed).toBeLessThan(MANY.length);
  });

  it("reports full coverage when nothing is dropped", async () => {
    const res = await semanticChunk(MANY, fakeEmbed, {});
    expect(res.truncated).toBe(false);
    expect(res.charsIndexed).toBe(MANY.length);
  });

  it("resumes from an offset so a capped document can be completed", async () => {
    const first = await semanticChunk(MANY, fakeEmbed, { maxWindows: 3 });
    const second = await semanticChunk(MANY, fakeEmbed, { offset: first.charsIndexed });
    expect(second.chunks.length).toBeGreaterThan(0);
    // The continuation must start at or after where part 1 stopped — no re-indexing, no gap.
    expect(second.chunks[0].charStart).toBeGreaterThanOrEqual(first.charsIndexed);
    expect(second.charsIndexed).toBe(MANY.length);
    // Together the two parts must cover every topic the source contains.
    const covered = [...first.chunks, ...second.chunks].map((c) => c.text).join(" ");
    for (let i = 0; i < 12; i++) expect(covered).toContain(`Topic${i}`);
  });
});
