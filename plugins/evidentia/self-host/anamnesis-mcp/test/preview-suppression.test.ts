import { describe, it, expect } from "vitest";
import { ingestDocument } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

/**
 * Caller-declared preview suppression.
 *
 * MEASURED PROBLEM: every manifest entry carried `preview: c.text.slice(0, 160)`.
 * At the 512-token (~950 char) chunk cap that is ~17% of the document returned
 * VERBATIM, once per chunk — a 200-chunk monograph hands back ~32 000 characters.
 * The tool description promised "Returns a MANIFEST — NOT the full text", so the
 * contract described its own violation.
 *
 * Preview is LEGITIMATE for anamnesis' own non-licensed corpora (callers use it to
 * orient), so removing it outright would break honest users and destroy a contract
 * field. The licence is known to the CALLER, not to this substrate — hence an opt-out
 * the caller declares, defaulting to today's behaviour so no existing client changes.
 *
 * Deliberately NOT keyed on collection prefix (`marmara:run:*` etc.): the scope
 * contract is about TENANCY, not licensing, and prefix-sniffing would silently miss
 * every newly added licensed source.
 */
const COLL = "evidentia:run:aaaabbbbcccc";
const TEXT = Array.from(
  { length: 8 },
  (_, i) => `Segment${i} carries a sentence that must never be echoed back verbatim.`,
).join("\n\n");

describe("manifest preview suppression", () => {
  it("returns previews by default — existing callers are unaffected", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, { text: TEXT, doc_id: "p:default", collection: COLL });
    expect(r.manifest.length).toBeGreaterThan(0);
    expect(r.manifest.every((m) => typeof m.preview === "string")).toBe(true);
    expect(r.previews_suppressed).toBeFalsy();
  });

  it("omits every preview when the caller opts out", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, {
      text: TEXT, doc_id: "p:off", collection: COLL, includePreviews: false,
    });
    expect(r.manifest.length).toBeGreaterThan(0);
    expect(r.manifest.every((m) => m.preview === undefined)).toBe(true);
  });

  it("leaks no document text anywhere in the suppressed result", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, {
      text: TEXT, doc_id: "p:leak", collection: COLL, includePreviews: false,
    });
    const blob = JSON.stringify(r);
    for (const probe of ["Segment0", "Segment3", "echoed back verbatim"]) {
      expect(blob).not.toContain(probe);
    }
  });

  it("announces the suppression instead of doing it silently", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, {
      text: TEXT, doc_id: "p:flag", collection: COLL, includePreviews: false,
    });
    expect(r.previews_suppressed).toBe(true);
  });

  it("keeps the structural fields the manifest exists for", async () => {
    const env = evalEnv(new MockVectorize());
    const r = await ingestDocument(env, {
      text: TEXT, doc_id: "p:struct", collection: COLL, includePreviews: false,
    });
    for (const m of r.manifest) {
      expect(typeof m.idx).toBe("number");
      expect(typeof m.token_est).toBe("number");
      expect(typeof m.char_start).toBe("number");
      expect(typeof m.char_end).toBe("number");
    }
    expect(r.n_chunks).toBe(r.manifest.length);
    expect(r.chars_total).toBe(TEXT.length);
  });

  it("suppression does not change what is INDEXED — only what is returned", async () => {
    const env = evalEnv(new MockVectorize());
    const on = await ingestDocument(env, { text: TEXT, doc_id: "p:i1", collection: COLL });
    const off = await ingestDocument(env, {
      text: TEXT, doc_id: "p:i2", collection: COLL, includePreviews: false,
    });
    expect(off.n_chunks).toBe(on.n_chunks);
    expect(off.chars_indexed).toBe(on.chars_indexed);
  });
});
