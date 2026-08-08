import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const { baseOf, contact, eutilsUrl, RETRY_ON, BACKOFF_MS, cleanIds, buildQuery, shapeSummary, xmlToText, clip,
  formatCitation, CITATION_STYLES, D_EUTILS, D_EPMC } = __testing;

// Test titles are ASCII on purpose — the workerd pool sends them in an HTTP header.

describe("baseOf / contact - env overrides with trailing-slash trim", () => {
  it("defaults to the public upstreams", () => {
    expect(baseOf({}, "EUTILS_BASE")).toBe(D_EUTILS);
    expect(baseOf({}, "EPMC_BASE")).toBe(D_EPMC);
  });
  it("honours an override and trims trailing slashes", () => {
    expect(baseOf({ EUTILS_BASE: "https://mock.test/eutils/" }, "EUTILS_BASE")).toBe("https://mock.test/eutils");
  });
  it("falls back to the default courtesy contact", () => {
    expect(contact({})).toContain("@");
    expect(contact({ CONTACT_EMAIL: " a@b.test " })).toBe("a@b.test");
  });
});

describe("eutilsUrl - NCBI courtesy identification is NOT optional", () => {
  // NCBI asks unauthenticated clients to send tool+email; omitting them is what gets a proxy
  // rate-limited or blocked outright, and the failure would look like "PubMed is down".
  it("always appends tool and email", () => {
    const u = new URL(eutilsUrl({}, "esearch.fcgi", { db: "pubmed", term: "x" }));
    expect(u.searchParams.get("tool")).toBeTruthy();
    expect(u.searchParams.get("email")).toContain("@");
  });
  it("drops undefined and empty params instead of sending blanks", () => {
    const u = new URL(eutilsUrl({}, "esearch.fcgi", { db: "pubmed", term: "x", sort: undefined, retmax: "" }));
    expect(u.searchParams.has("sort")).toBe(false);
    expect(u.searchParams.has("retmax")).toBe(false);
  });
  it("URL-encodes the term rather than splicing it into the query string", () => {
    const u = new URL(eutilsUrl({}, "esearch.fcgi", { db: "pubmed", term: 'a b&c=d "q"' }));
    expect(u.searchParams.get("term")).toBe('a b&c=d "q"');   // round-trips intact
    expect(u.toString()).not.toContain("&c=d");                 // never a second parameter
  });
});

describe("cleanIds - the injection boundary (ids are concatenated into id=)", () => {
  it("keeps well-formed PMIDs and drops everything else", () => {
    expect(cleanIds(["18436948", "abc", "", "12,34", "18436948"], "pmid")).toEqual(["18436948"]);
  });
  it("normalises PMCIDs and rejects bare digits", () => {
    expect(cleanIds(["pmc1234567", "1234567"], "pmcid")).toEqual(["PMC1234567"]);
  });
  it("accepts DOIs but rejects ones carrying whitespace or quotes", () => {
    expect(cleanIds(["10.1136/bmj.39489.470347.AD", '10.1/x"y', "10.1/a b", "notadoi"], "doi"))
      .toEqual(["10.1136/bmj.39489.470347.AD"]);
  });
  it("deduplicates, so one id is never fetched twice", () => {
    expect(cleanIds(["1", "1", "2"], "pmid")).toEqual(["1", "2"]);
  });
  it("returns an empty array for a non-array input instead of throwing", () => {
    for (const bad of [null, undefined, "18436948", 42, {}]) {
      expect(cleanIds(bad, "pmid")).toEqual([]);
    }
  });
});

describe("buildQuery - filters become native PubMed field tags", () => {
  // The upstream does the matching. If we filtered client-side instead, `total` would describe a
  // different set than the one returned, and a PRISMA flow count would be wrong.
  it("wraps the free-text query and ANDs each filter", () => {
    const q = buildQuery({ query: "emicizumab", author: "Guyatt G", journal: "BMJ" });
    expect(q).toContain("(emicizumab)");
    expect(q).toContain('"Guyatt G"[Author]');
    expect(q).toContain('"BMJ"[Journal]');
    expect(q.split(" AND ")).toHaveLength(3);
  });
  it("emits one MeSH clause per term and one clause per publication type", () => {
    const q = buildQuery({ query: "x", meshTerms: ["Hemophilia A", "Factor VIII"], publicationTypes: ["Randomized Controlled Trial"] });
    expect(q).toContain('"Hemophilia A"[MeSH Terms]');
    expect(q).toContain('"Factor VIII"[MeSH Terms]');
    expect(q).toContain('"Randomized Controlled Trial"[Publication Type]');
  });
  it("builds an open-ended date range when only one bound is given", () => {
    expect(buildQuery({ query: "x", dateRange: { from: "2020/01/01" } })).toContain('"2020/01/01"[Date - Publication] : "3000/12/31"');
    expect(buildQuery({ query: "x", dateRange: { to: "2020/12/31" } })).toContain('"1800/01/01"[Date - Publication] : "2020/12/31"');
  });
  it("adds nothing for absent filters", () => {
    expect(buildQuery({ query: "x" })).toBe("(x)");
  });
});

describe("shapeSummary - provenance without invention", () => {
  const raw = {
    uid: "18436948", title: "GRADE: an emerging consensus", fulljournalname: "BMJ",
    pubdate: "2008 Apr 26", authors: [{ name: "Guyatt GH" }, { name: "Oxman AD" }],
    articleids: [{ idtype: "doi", value: "10.1136/bmj.39489.470347.AD" }, { idtype: "pmc", value: "PMC2335261" }],
    pubtype: ["Journal Article"],
  };
  it("projects the fields the skill cites from", () => {
    expect(shapeSummary(raw)).toMatchObject({
      pmid: "18436948", journal: "BMJ", doi: "10.1136/bmj.39489.470347.AD", pmcid: "PMC2335261",
      authors: ["Guyatt GH", "Oxman AD"], url: "https://pubmed.ncbi.nlm.nih.gov/18436948/",
    });
  });
  it("returns null - never a guess - when an id is absent", () => {
    const s = shapeSummary({ uid: "1", title: "t", articleids: [] });
    expect(s.doi).toBeNull();
    expect(s.pmcid).toBeNull();
  });
  it("survives a malformed record instead of throwing", () => {
    expect(() => shapeSummary({})).not.toThrow();
    expect(shapeSummary({}).authors).toEqual([]);
  });
});

describe("xmlToText - lossy by design, and honest about it", () => {
  it("strips tags and keeps the readable body", () => {
    const out = xmlToText('<article><sec><title>Methods</title><p>We did <italic>x</italic>.</p></sec></article>');
    expect(out).toContain("Methods");
    expect(out).toContain("We did x .".replace(" .", " ."));
    expect(out).not.toContain("<");
  });
  it("decodes the common entities", () => {
    expect(xmlToText("<p>a &amp; b &lt;c&gt; &quot;d&quot;</p>")).toContain('a & b <c> "d"');
  });
  it("drops script/style content rather than inlining it as prose", () => {
    expect(xmlToText("<p>keep</p><script>alert(1)</script>")).not.toContain("alert");
  });
  it("collapses runaway whitespace so the budget is spent on text", () => {
    expect(xmlToText("<p>a</p>\n\n\n\n<p>b</p>")).not.toMatch(/\n{3,}/);
  });
});

describe("clip - truncation is reported, never silent", () => {
  it("passes short text through untouched", () => {
    expect(clip("abc", 10)).toEqual({ text: "abc", truncated: false, full_chars: 3 });
  });
  it("cuts and states the full size", () => {
    expect(clip("abcdef", 3)).toEqual({ text: "abc", truncated: true, full_chars: 6 });
  });
  it("treats a missing budget as unlimited", () => {
    expect(clip("abcdef").truncated).toBe(false);
  });
});

describe("formatCitation - built from the live record, in four styles", () => {
  const s = { pmid: "18436948", title: "GRADE: an emerging consensus.", journal: "BMJ",
    pubdate: "2008 Apr 26", authors: ["Guyatt GH", "Oxman AD"], doi: "10.1136/bmj.39489.470347.AD" };
  it("apa carries year, title, journal and a resolvable DOI link", () => {
    const c = formatCitation(s, "apa");
    expect(c).toContain("(2008)");
    expect(c).toContain("BMJ");
    expect(c).toContain("https://doi.org/10.1136/bmj.39489.470347.AD");
  });
  it("vancouver carries the PMID", () => {
    expect(formatCitation(s, "vancouver")).toContain("PMID: 18436948");
  });
  it("vancouver uses et al past six authors", () => {
    const many = { ...s, authors: ["a", "b", "c", "d", "e", "f", "g"] };
    expect(formatCitation(many, "vancouver")).toContain("et al");
  });
  it("bibtex and ris are structurally well formed", () => {
    expect(formatCitation(s, "bibtex")).toMatch(/^@article\{pmid18436948,[\s\S]*\}$/);
    const ris = formatCitation(s, "ris");
    expect(ris.startsWith("TY  - JOUR")).toBe(true);
    expect(ris.trimEnd().endsWith("ER  -")).toBe(true);
  });
  it("an unknown style falls back to apa rather than emitting nothing", () => {
    expect(formatCitation(s, "chicago")).toBe(formatCitation(s, "apa"));
  });
  it("omits the DOI link entirely when there is no DOI (no fabricated URL)", () => {
    expect(formatCitation({ ...s, doi: null }, "apa")).not.toContain("doi.org");
  });
  it("pins the advertised style set", () => {
    expect([...CITATION_STYLES].sort()).toEqual(["apa", "bibtex", "ris", "vancouver"]);
  });
});

describe("NCBI throttle handling (shared Worker egress IP)", () => {
  // Measured 2026-08-08: the SAME esearch returned 200 from a residential IP and 429 from the
  // Worker. NCBI throttles unauthenticated callers per SOURCE address and a Worker egresses from
  // a shared pool, so the 3 req/s budget is spent by unrelated traffic. Surfacing that first 429
  // would make a healthy upstream look dead.
  it("retries the statuses that are transient, not the ones that are answers", () => {
    expect(RETRY_ON.has(429)).toBe(true);
    for (const s of [500, 502, 503, 504]) expect(RETRY_ON.has(s)).toBe(true);
    for (const s of [200, 400, 404]) expect(RETRY_ON.has(s)).toBe(false);   // 404 is a RESULT
  });
  it("uses a bounded, deterministic backoff", () => {
    expect(BACKOFF_MS.length).toBeGreaterThan(0);
    expect(BACKOFF_MS.length).toBeLessThanOrEqual(4);           // bounded: no unbounded hammering
    for (let i = 1; i < BACKOFF_MS.length; i++) {
      expect(BACKOFF_MS[i]).toBeGreaterThan(BACKOFF_MS[i - 1]); // strictly increasing
    }
  });
  it("omits api_key when none is configured (this is what keeps the Worker keyless)", () => {
    expect(new URL(eutilsUrl({}, "esearch.fcgi", { db: "pubmed" })).searchParams.has("api_key")).toBe(false);
  });
  it("sends api_key when one IS configured", () => {
    const u = new URL(eutilsUrl({ NCBI_API_KEY: "k123" }, "esearch.fcgi", { db: "pubmed" }));
    expect(u.searchParams.get("api_key")).toBe("k123");
  });
});
