import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const {
  normalizeEndpoint, isAllowedEndpoint, buildOpenFdaUrl,
  stripEm, buildIcd11SearchUrl, shapeIcd11Entities,
  ENDPOINTS, OPENFDA, WHO_ICD_BASE,
} = __testing;

// Added 2026-08-07. This Worker shipped with no server.test.ts, so its SSRF allowlist and
// every URL/shape transform were unpinned: a refactor could widen the allowlist or drop a
// query parameter and all suites would still pass. Test titles are ASCII on purpose -- the
// workerd test pool sends them in an HTTP header and warns on non-ASCII.

describe("endpoint normalisation", () => {
  it("trims whitespace and strips wrapping slashes", () => {
    expect(normalizeEndpoint("  /drug/event/ ")).toBe("drug/event");
    expect(normalizeEndpoint("///drug/label///")).toBe("drug/label");
  });

  it("coerces null/undefined to an empty string instead of throwing", () => {
    expect(normalizeEndpoint(undefined)).toBe("");
    expect(normalizeEndpoint(null)).toBe("");
  });

  it("does NOT rewrite interior path segments", () => {
    // Only the wrapping slashes are stripped; a traversal attempt stays intact so the
    // allowlist -- not the normaliser -- is what rejects it.
    expect(normalizeEndpoint("drug/../../etc/passwd")).toBe("drug/../../etc/passwd");
  });
});

describe("SSRF gate (endpoint allowlist)", () => {
  it("accepts every advertised dataset", () => {
    for (const ep of ENDPOINTS) expect(isAllowedEndpoint(ep)).toBe(true);
  });

  it("rejects traversal, absolute URLs and host injection", () => {
    for (const bad of [
      "drug/../../etc/passwd",
      "../drug/event",
      "https://evil.example/x",
      "//evil.example/x",
      "drug/event?x=1",
      "drug/event#frag",
      "drug/eventX",
      "DRUG/EVENT",
      "",
    ]) {
      expect(isAllowedEndpoint(bad), `must reject ${JSON.stringify(bad)}`).toBe(false);
    }
  });

  it("pins the allowlist size so a widening is a deliberate, reviewed change", () => {
    expect(ENDPOINTS).toHaveLength(23);
    expect(new Set(ENDPOINTS).size).toBe(ENDPOINTS.length); // no duplicates
  });

  it("keeps every allowlisted endpoint inside an FDA-owned namespace", () => {
    const roots = new Set(ENDPOINTS.map((e: string) => e.split("/")[0]));
    expect([...roots].sort()).toEqual(
      ["animalandveterinary", "device", "drug", "food", "other", "tobacco"]);
    for (const ep of ENDPOINTS) expect(ep).toMatch(/^[a-z0-9]+\/[a-z0-9]+$/);
  });
});

describe("openFDA URL construction", () => {
  it("targets api.fda.gov with a .json suffix", () => {
    expect(buildOpenFdaUrl("drug/event", undefined, undefined, undefined, undefined))
      .toBe(`${OPENFDA}/drug/event.json`);
  });

  it("passes search, count and skip through", () => {
    const u = new URL(buildOpenFdaUrl("drug/label", 'openfda.generic_name:"adalimumab"',
      "patient.reaction.reactionmeddrapt.exact", undefined, 10));
    expect(u.searchParams.get("search")).toBe('openfda.generic_name:"adalimumab"');
    expect(u.searchParams.get("count")).toBe("patient.reaction.reactionmeddrapt.exact");
    expect(u.searchParams.get("skip")).toBe("10");
  });

  it("drops limit when count is set (openFDA rejects the combination)", () => {
    const withCount = new URL(buildOpenFdaUrl("drug/event", undefined, "field.exact", 50, undefined));
    expect(withCount.searchParams.has("limit")).toBe(false);
    const noCount = new URL(buildOpenFdaUrl("drug/event", undefined, undefined, 50, undefined));
    expect(noCount.searchParams.get("limit")).toBe("50");
  });

  it("keeps limit=0 and skip=0 (falsy but meaningful) rather than dropping them", () => {
    const u = new URL(buildOpenFdaUrl("drug/event", undefined, undefined, 0, 0));
    expect(u.searchParams.get("limit")).toBe("0");
    expect(u.searchParams.get("skip")).toBe("0");
  });

  it("percent-encodes a Lucene query instead of splicing it raw", () => {
    const raw = 'patient.drug.medicinalproduct:"HUMIRA" AND x&y=z';
    const s = buildOpenFdaUrl("drug/event", raw, undefined, 1, undefined);
    expect(s).not.toContain('"HUMIRA"');           // must be encoded
    expect(new URL(s).searchParams.get("search")).toBe(raw); // and round-trip exactly
  });
});

describe("stripEm (WHO highlight markup)", () => {
  it("removes <em> wrappers and trims", () => {
    expect(stripEm("  <em class='found'>diabetes</em> mellitus ")).toBe("diabetes mellitus");
    expect(stripEm("<em>a</em><em>b</em>")).toBe("ab");
  });

  it("returns an empty string for null/undefined instead of 'null'", () => {
    expect(stripEm(undefined)).toBe("");
    expect(stripEm(null)).toBe("");
  });

  it("leaves non-em markup alone (it is a highlight stripper, not a sanitiser)", () => {
    expect(stripEm("<b>x</b>")).toBe("<b>x</b>");
  });
});

describe("ICD-11 search URL and shaping", () => {
  it("builds the MMS search URL with flatResults", () => {
    const u = new URL(buildIcd11SearchUrl("2024-01", "type 2 diabetes"));
    expect(u.origin + u.pathname).toBe(`${WHO_ICD_BASE}/2024-01/mms/search`);
    expect(u.searchParams.get("q")).toBe("type 2 diabetes");
    expect(u.searchParams.get("flatResults")).toBe("true");
  });

  it("projects entities, strips highlight markup and honours the limit", () => {
    const j = {
      destinationEntities: [
        { id: "i1", theCode: "5A11", title: "<em>Type 2</em> diabetes", chapter: "05", score: 0.9 },
        { id: "i2", theCode: "5A10", title: "Type 1 diabetes", chapter: "05", score: 0.7 },
        { id: "i3", theCode: "5A14", title: "Other", chapter: "05", score: 0.5 },
      ],
    };
    const out = shapeIcd11Entities(j, 2);
    expect(out).toHaveLength(2);
    expect(out[0]).toEqual({ id: "i1", code: "5A11", title: "Type 2 diabetes", chapter: "05", score: 0.9 });
  });

  it("nulls a missing code rather than inventing one, and survives an empty response", () => {
    expect(shapeIcd11Entities({ destinationEntities: [{ id: "x", title: "t" }] }, 5)[0])
      .toEqual({ id: "x", code: null, title: "t", chapter: null, score: null });
    expect(shapeIcd11Entities({}, 5)).toEqual([]);
    expect(shapeIcd11Entities(null, 5)).toEqual([]);
  });
});
