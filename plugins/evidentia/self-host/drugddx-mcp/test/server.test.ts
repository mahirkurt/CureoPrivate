import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const {
  rxcuiUrl, approxUrl, splListUrl,
  pickExactRxcui, pickApproxRxcui, pickSetid, buildSplPointer,
  RXNAV, DAILYMED, CAVEAT,
} = __testing;

// Added 2026-08-07. This Worker shipped with no server.test.ts. Test titles are ASCII on
// purpose -- the workerd test pool sends them in an HTTP header and warns on non-ASCII.

describe("upstream URL builders", () => {
  it("targets the keyless NIH/FDA hosts", () => {
    expect(rxcuiUrl("warfarin").startsWith(RXNAV)).toBe(true);
    expect(approxUrl("warfarin").startsWith(RXNAV)).toBe(true);
    expect(splListUrl("warfarin").startsWith(DAILYMED)).toBe(true);
  });

  it("percent-encodes the drug name instead of splicing it raw", () => {
    const nasty = 'a b&c=d#e/../f';
    for (const u of [rxcuiUrl(nasty), approxUrl(nasty), splListUrl(nasty)]) {
      expect(u).not.toContain(" ");
      expect(u).not.toContain("#");
      expect(u).not.toContain("/../");
    }
    expect(new URL(rxcuiUrl(nasty)).searchParams.get("name")).toBe(nasty);
    expect(new URL(approxUrl(nasty)).searchParams.get("term")).toBe(nasty);
    expect(new URL(splListUrl(nasty)).searchParams.get("drug_name")).toBe(nasty);
  });

  it("keeps the query knobs the upstreams require", () => {
    expect(new URL(rxcuiUrl("x")).searchParams.get("search")).toBe("2");
    expect(new URL(approxUrl("x")).searchParams.get("maxEntries")).toBe("3");
    expect(new URL(splListUrl("x")).searchParams.get("pagesize")).toBe("1");
  });
});

describe("RxNav exact match parsing", () => {
  it("takes the first rxnormId and keeps the full candidate list", () => {
    expect(pickExactRxcui({ idGroup: { rxnormId: ["11289", "99"] } }))
      .toEqual({ rxcui: "11289", candidates: ["11289", "99"] });
  });

  it("returns null with an empty candidate list when RxNav has no hit", () => {
    expect(pickExactRxcui({ idGroup: {} })).toEqual({ rxcui: null, candidates: [] });
    expect(pickExactRxcui({})).toEqual({ rxcui: null, candidates: [] });
    expect(pickExactRxcui(null)).toEqual({ rxcui: null, candidates: [] });
  });
});

describe("RxNav approximate fallback parsing", () => {
  it("takes the best candidate's rxcui", () => {
    const a = { approximateGroup: { candidate: [{ rxcui: "5640", score: "50" }, { rxcui: "1", score: "10" }] } };
    expect(pickApproxRxcui(a).rxcui).toBe("5640");
    expect(pickApproxRxcui(a).candidates).toHaveLength(2);
  });

  it("returns null rather than inventing an rxcui when nothing approximates", () => {
    expect(pickApproxRxcui({ approximateGroup: { candidate: [] } })).toEqual({ rxcui: null, candidates: [] });
    expect(pickApproxRxcui({})).toEqual({ rxcui: null, candidates: [] });
    expect(pickApproxRxcui(null)).toEqual({ rxcui: null, candidates: [] });
  });

  it("survives a candidate object with no rxcui field", () => {
    expect(pickApproxRxcui({ approximateGroup: { candidate: [{ score: "1" }] } }).rxcui).toBe(null);
  });
});

describe("DailyMed setid parsing", () => {
  it("takes the first setid", () => {
    expect(pickSetid({ data: [{ setid: "abc-123" }, { setid: "zzz" }] })).toBe("abc-123");
  });

  it("returns null for an empty or malformed listing", () => {
    expect(pickSetid({ data: [] })).toBe(null);
    expect(pickSetid({ data: [{}] })).toBe(null);
    expect(pickSetid({})).toBe(null);
    expect(pickSetid(null)).toBe(null);
  });
});

describe("SPL pointer (copyright boundary)", () => {
  const p = buildSplPointer("abc-123");

  it("carries the setid and a resolvable DailyMed lookup URL", () => {
    expect(p).toContain("setid=abc-123");
    expect(p).toContain("https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=abc-123");
    expect(p).toContain("34073-7"); // the LOINC section the reader must fetch
  });

  it("states the copyright bound so the label body is never dumped in bulk", () => {
    expect(p.toLowerCase()).toContain("copyright-bounded");
    expect(p.toLowerCase()).toContain("do not reproduce in bulk");
  });

  it("stays a pointer, not a payload", () => {
    expect(p.length).toBeLessThan(400);
  });
});

describe("honest-scope caveat", () => {
  it("states plainly that this is NOT a clinical pairwise DDI engine", () => {
    expect(CAVEAT).toContain("NOT a clinical pairwise DDI engine");
    expect(CAVEAT).toContain("discontinued Jan 2024");
    expect(CAVEAT).toMatch(/Lexicomp|UpToDate|DrugBank/);
  });
});
