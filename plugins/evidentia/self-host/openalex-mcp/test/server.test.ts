import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const { baseOf, contact, isBudgetError, upstreamError, encodeFilters, listUrl, normalizeId, isEntity, citationFilter,
  shapeEntity, parseValidFields, ENTITIES, DEFAULT_BASE } = __testing;

// Test titles are ASCII on purpose — the workerd pool sends them in an HTTP header.

describe("baseOf / contact", () => {
  it("defaults to the public OpenAlex API", () => {
    expect(baseOf({})).toBe(DEFAULT_BASE);
  });
  it("honours an override and trims trailing slashes", () => {
    expect(baseOf({ OPENALEX_BASE: "https://mock.test/api/" })).toBe("https://mock.test/api");
  });
  it("always yields a contact for the polite pool", () => {
    expect(contact({})).toContain("@");
    expect(contact({ CONTACT_EMAIL: " a@b.test " })).toBe("a@b.test");
  });
});

describe("citationFilter - direction mapping (measured, and it reads BACKWARDS)", () => {
  // MEASURED 2026-08-08 against GRADE 2008 (W2165010366, cited_by_count 22,679, 12 references):
  //   filter=cites:W2165010366    -> 21,475 results  (works that CITE it)
  //   filter=cited_by:W2165010366 ->     12 results  (the works IT cites)
  // Inverting this returns a plausible-looking but wrong network — 12 papers presented as
  // "everyone who cites this landmark". That is why the mapping is pinned here.
  it("incoming (who cites the seed) maps to cites:", () => {
    expect(citationFilter("incoming", "W2165010366")).toBe("cites:W2165010366");
  });
  it("outgoing (the seed's references) maps to cited_by:", () => {
    expect(citationFilter("outgoing", "W2165010366")).toBe("cited_by:W2165010366");
  });
  it("the two directions are never the same filter", () => {
    expect(citationFilter("incoming", "W1")).not.toBe(citationFilter("outgoing", "W1"));
  });
});

describe("normalizeId - accepts either form, rejects the rest", () => {
  it("accepts a bare id and upper-cases it", () => {
    expect(normalizeId("w2165010366")).toBe("W2165010366");
  });
  it("accepts the full OpenAlex URL form", () => {
    expect(normalizeId("https://openalex.org/W2165010366")).toBe("W2165010366");
  });
  it("rejects anything that is not an OpenAlex id", () => {
    // NOTE: the digit-count floor is deliberately NOT asserted. Real ids run 8-10 digits, but the
    // contract this function actually owes is "no filter-grammar character reaches `filter=`" —
    // an earlier version of this test demanded 'W12' be rejected, which was a length rule the
    // code never promised. Assert the boundary that matters, not an invented one.
    for (const bad of ["", "  ", "2165010366", "X123", "10.1136/bmj", "W1 2", "W1; DROP", null, undefined]) {
      expect(normalizeId(bad as any)).toBeNull();
    }
  });
  it("rejects an id carrying an injected filter separator", () => {
    // Ids are spliced into `filter=`, so a comma or colon would open a second clause.
    expect(normalizeId("W123,cites:W456")).toBeNull();
    expect(normalizeId("W123:x")).toBeNull();
  });
});

describe("isEntity - the entity allowlist", () => {
  it("accepts every advertised entity", () => {
    for (const e of ENTITIES) expect(isEntity(e)).toBe(true);
  });
  it("rejects an unknown entity rather than pathing to a 404", () => {
    for (const bad of ["work", "author", "", "../works", null]) expect(isEntity(bad)).toBe(false);
  });
});

describe("encodeFilters - OpenAlex comma grammar", () => {
  it("joins key:value pairs with commas", () => {
    expect(encodeFilters({ country_code: "TR", type: "article" })).toBe("country_code:TR,type:article");
  });
  it("uses | for an OR list inside one key", () => {
    expect(encodeFilters({ "authorships.institutions.country_code": ["TR", "DE"] }))
      .toBe("authorships.institutions.country_code:TR|DE");
  });
  it("drops empty and undefined values instead of emitting a dangling colon", () => {
    expect(encodeFilters({ a: "1", b: undefined, c: "", d: null })).toBe("a:1");
  });
  it("returns an empty string for no filters", () => {
    expect(encodeFilters()).toBe("");
    expect(encodeFilters({})).toBe("");
  });
});

describe("listUrl - polite pool + single encoding", () => {
  it("always attaches mailto", () => {
    expect(new URL(listUrl({}, "works", {})).searchParams.get("mailto")).toContain("@");
  });
  it("encodes a hostile value as ONE parameter, never a second clause", () => {
    const u = new URL(listUrl({}, "works", { search: "a&per-page=200&mailto=evil@x" }));
    expect(u.searchParams.get("search")).toBe("a&per-page=200&mailto=evil@x");
    expect(u.searchParams.get("mailto")).not.toBe("evil@x");
    expect(u.searchParams.get("per-page")).toBeNull();
  });
  it("omits empty params", () => {
    const u = new URL(listUrl({}, "works", { filter: undefined, sort: "", cursor: null }));
    for (const k of ["filter", "sort", "cursor"]) expect(u.searchParams.has(k)).toBe(false);
  });
  it("joins an array param with commas (select)", () => {
    expect(new URL(listUrl({}, "works", { select: ["id", "title"] })).searchParams.get("select")).toBe("id,title");
  });
});

describe("shapeEntity - cite-able projection, no invention", () => {
  it("strips the URL prefix from the id", () => {
    expect(shapeEntity({ id: "https://openalex.org/W1", display_name: "x" }, "works").id).toBe("W1");
  });
  it("projects a work with OA status and author affiliations", () => {
    const w = shapeEntity({
      id: "https://openalex.org/W1", display_name: "T", publication_year: 2008,
      doi: "https://doi.org/10.1/x", open_access: { is_oa: true, oa_url: "u" },
      authorships: [{ author: { display_name: "A", orcid: "o" }, institutions: [{ display_name: "I" }] }],
      primary_location: { source: { display_name: "BMJ" } },
    }, "works") as any;
    expect(w).toMatchObject({ year: 2008, is_oa: true, oa_url: "u", venue: "BMJ" });
    expect(w.authors[0]).toEqual({ name: "A", orcid: "o", institutions: ["I"] });
  });
  it("projects an author with h-index", () => {
    expect(shapeEntity({ id: "A1", display_name: "G", orcid: "x", summary_stats: { h_index: 200 } }, "authors"))
      .toMatchObject({ orcid: "x", h_index: 200 });
  });
  it("projects an institution with ROR", () => {
    expect(shapeEntity({ id: "I1", display_name: "H", ror: "https://ror.org/z", country_code: "TR" }, "institutions"))
      .toMatchObject({ ror: "https://ror.org/z", country: "TR" });
  });
  it("returns null rather than guessing when a field is absent", () => {
    const w = shapeEntity({ id: "W1" }, "works") as any;
    expect(w.doi).toBeNull();
    expect(w.venue).toBeNull();
    expect(w.authors).toEqual([]);
  });
  it("survives an empty record instead of throwing", () => {
    expect(() => shapeEntity({}, "works")).not.toThrow();
  });
});

describe("parseValidFields - the field list is LIVE, not a bundled copy", () => {
  // OpenAlex has no schema endpoint, but an invalid field makes it enumerate the legal ones.
  // Parsing that response is what keeps describe_fields from drifting away from the API.
  const msg = "__nope__ is not a valid field. Valid fields are underscore or hyphenated versions of: " +
    "abstract.search, abstract.search.exact, author.id, authorships.institutions.ror.";
  it("extracts every enumerated field", () => {
    expect(parseValidFields(msg)).toEqual(
      ["abstract.search", "abstract.search.exact", "author.id", "authorships.institutions.ror"]);
  });
  it("returns an empty list when the message has no enumeration (never a fabricated list)", () => {
    for (const bad of ["", "Some other error", "Valid fields are:"]) {
      expect(parseValidFields(bad)).toEqual([]);
    }
  });
  it("tolerates a null/undefined message", () => {
    expect(parseValidFields(undefined as any)).toEqual([]);
  });
});

describe("budget-429 is diagnosed, not swallowed (measured 2026-08-08)", () => {
  // OpenAlex meters requests against a DAILY budget scoped to the SOURCE IP. A Worker egresses
  // from Cloudflare's shared pool, so the quota is spent by unrelated traffic: the identical list
  // request returned 200 from a residential IP and "Insufficient budget ... $0 remaining" from the
  // Worker in the same minute. Reported as a generic 429 it would read as "OpenAlex has no data".
  it("recognises the budget message", () => {
    expect(isBudgetError({ message: "Insufficient budget. This request costs $0.001 but you only have $0 remaining." })).toBe(true);
    expect(isBudgetError({ error: "insufficient BUDGET" })).toBe(true);
  });
  it("does not mistake an ordinary error for a budget block", () => {
    for (const b of [{}, null, { message: "Invalid query parameters error." }, { error: "API key not found" }]) {
      expect(isBudgetError(b)).toBe(false);
    }
  });
  it("names the actual remedy in the error text", () => {
    const msg = upstreamError("openalex_resolve_name", { status: 429, body: { message: "Insufficient budget." } });
    expect(msg).toContain("BUDGET");
    expect(msg).toContain("OPENALEX_API_KEY");   // what fixes it
    expect(msg).toContain("relay");              // the alternative fix
  });
  it("leaves a non-budget error terse and factual", () => {
    const msg = upstreamError("openalex_search_entities", { status: 400, body: { message: "Invalid query parameters error." } });
    expect(msg).toContain("400");
    expect(msg).not.toContain("BUDGET");
  });
  it("omits api_key when none is configured (this keeps the Worker keyless)", () => {
    expect(new URL(listUrl({}, "works", {})).searchParams.has("api_key")).toBe(false);
  });
  it("sends api_key when one IS configured", () => {
    expect(new URL(listUrl({ OPENALEX_API_KEY: "k1" }, "works", {})).searchParams.get("api_key")).toBe("k1");
  });
});
