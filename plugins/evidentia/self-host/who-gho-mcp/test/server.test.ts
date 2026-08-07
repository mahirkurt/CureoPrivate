import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const {
  baseOf, indicatorCatalogueUrl, filterIndicators, buildDataUrl,
  shapeDataRows, dimensionUrl, odataEscape, CODE_RE, DEFAULT_BASE,
} = __testing;

describe("CODE_RE - SSRF-safe indicator/dimension code allowlist", () => {
  it("accepts every real GHO code shape", () => {
    for (const c of ["WHOSIS_000001", "MDG_0000000017", "SEX_BTSX", "COUNTRY", "AGEGROUP", "EUR", "E11"])
      expect(CODE_RE.test(c)).toBe(true);
  });
  it("rejects bare/leading/trailing/consecutive dots and path-traversal (the nit)", () => {
    for (const bad of [".", "..", "../", "../etc", "a..b", ".x", "x.", "A B", "", "/", "a/b"])
      expect(CODE_RE.test(bad)).toBe(false);
  });
});

describe("baseOf - env override with trailing-slash trim", () => {
  it("defaults to the public GHO OData base", () => {
    expect(baseOf({})).toBe(DEFAULT_BASE);
  });
  it("honours GHO_API_BASE and trims trailing slashes", () => {
    expect(baseOf({ GHO_API_BASE: "https://mock.test/api/" })).toBe("https://mock.test/api");
  });
});

describe("filterIndicators - case-insensitive substring on name/code", () => {
  const rows = [
    { IndicatorCode: "WHOSIS_000001", IndicatorName: "Life expectancy at birth (years)" },
    { IndicatorCode: "MDG_0000000017", IndicatorName: "Tuberculosis mortality rate" },
    { IndicatorCode: "", IndicatorName: "no code -> dropped" },
  ];
  it("matches by name, case-insensitive", () => {
    const m = filterIndicators(rows, "TUBERCULOSIS", 25);
    expect(m).toEqual([{ code: "MDG_0000000017", name: "Tuberculosis mortality rate" }]);
  });
  it("matches by code substring", () => {
    expect(filterIndicators(rows, "whosis", 25)[0].code).toBe("WHOSIS_000001");
  });
  it("drops rows with no IndicatorCode and respects limit", () => {
    const m = filterIndicators(rows, "", 1);
    expect(m).toHaveLength(1);
    expect(m[0].code).toBe("WHOSIS_000001");
  });
});

describe("buildDataUrl - OData $filter assembly + SSRF-safe path", () => {
  it("builds SpatialDim + TimeDim + Dim1 filter with $top", () => {
    const u = new URL(buildDataUrl("https://mock.test/api", "WHOSIS_000001", { country: "tur", year: 2019, dim1: "sex_btsx", top: 10 }));
    expect(u.pathname).toBe("/api/WHOSIS_000001");
    expect(u.searchParams.get("$filter")).toBe("SpatialDim eq 'TUR' and TimeDim eq 2019 and Dim1 eq 'SEX_BTSX'");
    expect(u.searchParams.get("$top")).toBe("10");
  });
  it("omits $filter when no filters, keeps $top default", () => {
    const u = new URL(buildDataUrl("https://mock.test/api", "X", {}));
    expect(u.searchParams.has("$filter")).toBe(false);
    expect(u.searchParams.get("$top")).toBe("50");
  });
  it("escapes single quotes in country code (OData injection guard)", () => {
    expect(odataEscape("O'Brien")).toBe("O''Brien");
  });
});

describe("shapeDataRows - GHO row projection + limit", () => {
  it("projects the fields evidentia consumes and caps at limit", () => {
    const rows = [
      { SpatialDim: "TUR", SpatialDimType: "COUNTRY", TimeDim: 2019, Dim1: "SEX_BTSX", Value: "78.6", NumericValue: 78.6, Low: 77.9, High: 79.3, Comments: null },
      { SpatialDim: "USA", TimeDim: 2019, Value: "78.5" },
    ];
    const out = shapeDataRows(rows, 1);
    expect(out).toHaveLength(1);
    expect(out[0]).toMatchObject({ country: "TUR", year: 2019, dim1: "SEX_BTSX", numeric: 78.6, low: 77.9, high: 79.3 });
  });
});

describe("dimensionUrl - dimension list vs values", () => {
  it("lists all dimensions when no arg", () => {
    expect(dimensionUrl("https://mock.test/api")).toBe("https://mock.test/api/Dimension");
  });
  it("expands a single dimension's values (uppercased)", () => {
    expect(dimensionUrl("https://mock.test/api", "country")).toBe("https://mock.test/api/DIMENSION/COUNTRY/DimensionValues");
  });
});

describe("indicatorCatalogueUrl", () => {
  it("points at /Indicator", () => {
    expect(indicatorCatalogueUrl("https://mock.test/api")).toBe("https://mock.test/api/Indicator");
  });
});
