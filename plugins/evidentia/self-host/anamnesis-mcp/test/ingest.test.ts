import { describe, it, expect } from "vitest";
import { ingestDocument, listDocs, semanticSearch } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const COLL = "evidentia:run:aaaabbbbcccc";
const LONG = Array.from(
  { length: 12 },
  (_, i) => `Topic${i} states its own distinct claim plainly.`,
).join("\n\n");

describe("ingest truncation honesty (A1)", () => {
  it("reports partial coverage instead of silently dropping the tail", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, {
      text: LONG, doc_id: "trunc:a", collection: COLL, chunkOpts: { maxWindows: 3 },
    });
    expect(r.truncated).toBe(true);
    expect(r.chars_total).toBe(LONG.length);
    expect(r.chars_indexed).toBeGreaterThan(0);
    expect(r.chars_indexed).toBeLessThan(LONG.length);
    expect(r.next_offset).toBe(r.chars_indexed);
  });

  it("reports full coverage and no next_offset when nothing is dropped", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, { text: LONG, doc_id: "trunc:b", collection: COLL });
    expect(r.truncated).toBe(false);
    expect(r.chars_indexed).toBe(LONG.length);
    expect(r.next_offset).toBeNull();
  });

  it("indexes the remainder when the caller resumes at next_offset", async () => {
    const env = evalEnv(new MockVectorize());
    const p1 = await ingestDocument(env, {
      text: LONG, doc_id: "trunc:part1", collection: COLL, chunkOpts: { maxWindows: 3 },
    });
    const p2 = await ingestDocument(env, {
      text: LONG, doc_id: "trunc:part2", collection: COLL, offset: p1.next_offset ?? 0,
    });
    expect(p2.chars_indexed).toBe(LONG.length);
    // Coverage must be provable by RETRIEVAL, not by manifest previews (those are capped at
    // 160 chars per chunk and would hide the tail even when it was indexed correctly).
    const both = ["trunc:part1", "trunc:part2"];
    for (const topic of ["Topic0", "Topic7", "Topic11"]) {
      const hits = await semanticSearch(env, {
        query: topic, collection: COLL, doc_ids: both, rerank: false,
      });
      expect(hits.some((h) => h.text.includes(topic)), `${topic} must be retrievable`).toBe(true);
    }
  });
});

describe("chunk offsets are real (A4)", () => {
  // CRLF is the case that actually breaks indexOf() recovery. A bare "\n" collapsing to " "
  // preserves LENGTH, so the old synthetic fallback happened to land correctly; "\r\n" (2 chars)
  // and runs of spaces/tabs collapse to 1 and shift every later offset. Real PDF/OCR and
  // Windows-authored sources are full of both.
  const WRAPPED = "Alpha opens here.\r\nAlpha wraps onto a second line.\r\n\r\nBeta \t makes  another claim.";

  it("each stored chunk span slices back to that chunk from the source", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: WRAPPED, doc_id: "off:a", collection: COLL });
    const hits = await semanticSearch(env, { query: "Alpha", collection: COLL, doc_id: "off:a", rerank: false });
    expect(hits.length).toBeGreaterThan(0);
    const norm = (s: string) => s.replace(/\s+/g, " ").trim();
    for (const h of hits) {
      expect(h.char_start).not.toBeNull();
      expect(norm(WRAPPED.slice(h.char_start as number, h.char_end as number))).toBe(norm(h.text));
    }
  });
});

describe("ingest is not destructive on failure (A7)", () => {
  it("keeps the previous version when the re-ingest embed fails", async () => {
    const env = evalEnv(new MockVectorize());
    await ingestDocument(env, { text: "Alpha one. Alpha two.", doc_id: "keep:a", collection: COLL });
    const before = (await listDocs(env, COLL)).docs.filter((d) => d["id"] === "keep:a");
    expect(before.length).toBe(1);

    const broken = { ...env, AI: { run: async () => { throw new Error("Workers AI down"); } } };
    await expect(
      ingestDocument(broken, { text: "Beta replacement text.", doc_id: "keep:a", collection: COLL }),
    ).rejects.toThrow();

    const after = (await listDocs(env, COLL)).docs.filter((d) => d["id"] === "keep:a");
    expect(after.length).toBe(1);
  });
});

describe("doc_id length is validated up front (A8)", () => {
  it("rejects a doc_id that would overflow the Vectorize 64-byte id cap", async () => {
    const env = evalEnv(new MockVectorize());
    await expect(
      ingestDocument(env, { text: "Alpha one.", doc_id: "x".repeat(70), collection: COLL }),
    ).rejects.toThrow(/doc_id/i);
  });

  it("rejects before deleting the existing document of that id", async () => {
    const env = evalEnv(new MockVectorize());
    const id = "y".repeat(62); // 62 + "::" + idx overflows 64 bytes
    // Seed under a short id, then prove a too-long id never reaches the delete path.
    await ingestDocument(env, { text: "Alpha one. Alpha two.", doc_id: "short:a", collection: COLL });
    await expect(
      ingestDocument(env, { text: "Alpha one.", doc_id: id, collection: COLL }),
    ).rejects.toThrow(/doc_id/i);
    expect((await listDocs(env, COLL)).docs.filter((d) => d["id"] === "short:a").length).toBe(1);
  });
});
