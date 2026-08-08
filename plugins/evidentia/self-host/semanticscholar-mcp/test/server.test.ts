import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const { baseOf, normalizePaperId, apiUrl, shapePaper, shapeAuthor, upstreamError,
  RETRY_ON, BACKOFF_MS, PAPER_FIELDS, DEFAULT_BASE } = __testing;

// Test titles are ASCII on purpose — the workerd pool sends them in an HTTP header.

describe("baseOf", () => {
  it("defaults to the public Graph API", () => {
    expect(baseOf({})).toBe(DEFAULT_BASE);
  });
  it("honours an override and trims trailing slashes", () => {
    expect(baseOf({ S2_BASE: "https://mock.test/graph/v1/" })).toBe("https://mock.test/graph/v1");
  });
});

describe("normalizePaperId - the injection boundary (id goes into the URL PATH)", () => {
  it("accepts a 40-hex S2 paperId", () => {
    const id = "8da686b777ef41e017a94fc4529add7342a0f5ca";
    expect(normalizePaperId(id)).toBe(id);
  });
  it("prefixes a bare DOI so S2 resolves it as one", () => {
    expect(normalizePaperId("10.1136/bmj.39489.470347.AD")).toBe("DOI:10.1136/bmj.39489.470347.AD");
  });
  it("passes an already-prefixed id through untouched", () => {
    for (const id of ["DOI:10.1/x", "PMID:18436948", "PMCID:PMC2335261", "ARXIV:2101.00001",
                      "MAG:2165010366", "CorpusId:206890029", "ACL:P19-1285"]) {
      expect(normalizePaperId(id)).toBe(id);
    }
  });
  it("REJECTS anything carrying a query, fragment or backslash", () => {
    // These would escape the path segment and graft parameters onto the upstream request.
    for (const bad of ["10.1/x?fields=all", "PMID:1#frag", "10.1/x&limit=100", "PMID:1\\..\\admin"]) {
      expect(normalizePaperId(bad)).toBeNull();
    }
  });
  it("REJECTS whitespace and unknown shapes rather than guessing", () => {
    for (const bad of ["", "   ", "not an id", "PMID:abc", "PMCID:1234", "deadbeef", null, undefined, 42]) {
      expect(normalizePaperId(bad as any)).toBeNull();
    }
  });
  it("keeps the slash INSIDE a DOI - banning it would reject every real DOI", () => {
    expect(normalizePaperId("DOI:10.1136/bmj.39489.470347.AD")).toContain("/");
  });
});

describe("apiUrl - single encoding, no empty params", () => {
  it("encodes a hostile query as ONE parameter", () => {
    const u = new URL(apiUrl({}, "/paper/search", { query: "a&limit=999&fields=all" }));
    expect(u.searchParams.get("query")).toBe("a&limit=999&fields=all");
    expect(u.searchParams.get("limit")).toBeNull();   // never became a second parameter
  });
  it("omits undefined/empty params", () => {
    const u = new URL(apiUrl({}, "/paper/search", { query: "x", year: undefined, fieldsOfStudy: "" }));
    expect(u.searchParams.has("year")).toBe(false);
    expect(u.searchParams.has("fieldsOfStudy")).toBe(false);
  });
  it("requests the fields the skill actually cites from", () => {
    for (const f of ["externalIds", "citationCount", "isOpenAccess", "authors"]) {
      expect(PAPER_FIELDS).toContain(f);
    }
  });
});

describe("shapePaper - provenance without invention", () => {
  const raw = {
    paperId: "8da686b7", title: "GRADE", year: 2008, venue: "BMJ", citationCount: 22679,
    isOpenAccess: true, openAccessPdf: { url: "https://x/pdf" },
    externalIds: { DOI: "10.1136/bmj.39489.470347.AD", PubMed: "18436948", PubMedCentral: "PMC2335261" },
    authors: [{ authorId: "a1", name: "Guyatt GH" }],
  };
  it("lifts the external ids the fleet cross-walks on", () => {
    expect(shapePaper(raw)).toMatchObject({
      doi: "10.1136/bmj.39489.470347.AD", pmid: "18436948", pmcid: "PMC2335261",
      citationCount: 22679, oa_pdf: "https://x/pdf",
    });
  });
  it("returns null - never a guess - for ids S2 does not carry", () => {
    const s = shapePaper({ paperId: "x", externalIds: {} });
    expect(s.doi).toBeNull();
    expect(s.pmid).toBeNull();
    expect(s.arxiv).toBeNull();
  });
  it("survives an empty record instead of throwing", () => {
    expect(() => shapePaper({})).not.toThrow();
    expect(shapePaper({}).authors).toEqual([]);
  });
  it("caps the author list so one mega-author paper cannot flood the window", () => {
    const many = { authors: Array.from({ length: 400 }, (_, i) => ({ authorId: `a${i}`, name: `A${i}` })) };
    expect((shapePaper(many).authors as any[]).length).toBe(25);
  });
});

describe("shapeAuthor - KOL fields", () => {
  it("projects h-index and counts", () => {
    expect(shapeAuthor({ authorId: "A1", name: "G", hIndex: 250, paperCount: 900, citationCount: 400000 }))
      .toMatchObject({ hIndex: 250, paperCount: 900, citationCount: 400000 });
  });
  it("defaults affiliations to an empty list, not null-ish noise", () => {
    expect(shapeAuthor({}).affiliations).toEqual([]);
  });
});

describe("throttle handling - a 429 must never read as 'no such literature'", () => {
  // MEASURED 2026-08-08: three consecutive KEYED paper/search calls from one IP returned
  // 200 / 429 / 200. S2 throttles even with a key, so the first 429 is transient — surfacing it
  // raw would make a working connector look like an empty catalog.
  it("retries the transient statuses and NOT the answers", () => {
    for (const s of [429, 500, 502, 503, 504]) expect(RETRY_ON.has(s)).toBe(true);
    for (const s of [200, 400, 404]) expect(RETRY_ON.has(s)).toBe(false);  // 404 is an ANSWER
  });
  it("uses a bounded, strictly increasing backoff", () => {
    expect(BACKOFF_MS.length).toBeGreaterThan(0);
    expect(BACKOFF_MS.length).toBeLessThanOrEqual(4);
    for (let i = 1; i < BACKOFF_MS.length; i++) {
      expect(BACKOFF_MS[i]).toBeGreaterThan(BACKOFF_MS[i - 1]);
    }
  });
  it("says THROTTLE, not empty, when the limit survives every retry", () => {
    const msg = upstreamError("search_papers", { status: 429, body: { message: "Too Many Requests" } });
    expect(msg).toContain("THROTTLE");
    expect(msg).toContain("not an empty result");
    expect(msg).toContain("pubmed-epmc");   // names the fallback
  });
  it("leaves a non-429 error terse and factual", () => {
    const msg = upstreamError("get_paper", { status: 400, body: { error: "bad field" } });
    expect(msg).toContain("400");
    expect(msg).not.toContain("THROTTLE");
  });
});
