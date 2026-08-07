import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const { baseOf, metaUrl, dataUrl, shapeCancers, findPopulations, shapeData, DEFAULT_BASE } = __testing;

describe("baseOf - env override with trailing-slash trim", () => {
  it("defaults to the public GLOBOCAN 2022 base", () => {
    expect(baseOf({})).toBe(DEFAULT_BASE);
  });
  it("honours GCO_API_BASE and trims trailing slashes", () => {
    expect(baseOf({ GCO_API_BASE: "https://mock.test/api/v3/2022/" })).toBe("https://mock.test/api/v3/2022");
  });
});

describe("metaUrl", () => {
  it("builds cancers/populations meta paths", () => {
    expect(metaUrl("https://x/2022", "cancers")).toBe("https://x/2022/meta/cancers/all/");
    expect(metaUrl("https://x/2022", "populations")).toBe("https://x/2022/meta/populations/all/");
  });
});

describe("dataUrl - verified contract data/rate/{type}/{sex}/({pops})/{cancer}/", () => {
  // Signature is dataUrl(base, type, sex, pops, cancer). The GCO path order is TYPE then SEX
  // (empirically verified 2026-07-05 against known Türkiye values: female breast mortality 7,360 =
  // /rate/1/2/(792)/20/; female breast incidence 25,249 = /rate/0/2/(792)/20/).
  it("male incidence single-country single-cancer -> type=0/sex=1", () => {
    const u = dataUrl("https://x/2022", 0, 1, [792], "15"); // incidence, male
    expect(u.startsWith("https://x/2022/data/rate/0/1/(792)/15/?")).toBe(true);
    expect(u).toContain("include_nmsc=0");
  });
  it("female breast mortality -> type=1/sex=2 (regression: the sex/type-swap bug)", () => {
    const u = dataUrl("https://x/2022", 1, 2, [792], "20"); // mortality, female, breast
    expect(u.startsWith("https://x/2022/data/rate/1/2/(792)/20/?")).toBe(true);
  });
  it("both-sex prevalence all-cancers multi-country -> type=2/sex=0", () => {
    const u = dataUrl("https://x/2022", 2, 0, [792, 900], "all"); // prevalence, both
    expect(u.startsWith("https://x/2022/data/rate/2/0/(792,900)/all/?")).toBe(true);
  });
});

describe("shapeCancers", () => {
  it("projects id/label/icd/gender from meta rows", () => {
    const rows = [{ cancer: 15, id: 15, label: "Trachea, bronchus and lung", ICD: "C33-34", gender: 0 }];
    expect(shapeCancers(rows)).toEqual([{ id: 15, label: "Trachea, bronchus and lung", icd: "C33-34", gender: 0 }]);
  });
});

describe("findPopulations - resolve by name / ISO3 / code", () => {
  const rows = [
    { country: 792, label: "Turkey", country_iso3: "TUR", who_label: "WHO Europe region (EURO)", hdi_label: "High HDI", income_label: "Upper middle income" },
    { country: 276, label: "Germany", country_iso3: "DEU", who_label: "EURO", hdi_label: "Very high HDI", income_label: "High income" },
  ];
  it("matches by ISO3 (exact, case-insensitive)", () => {
    const m = findPopulations(rows, "tur", 15);
    expect(m).toHaveLength(1);
    expect(m[0]).toMatchObject({ code: 792, label: "Turkey", iso3: "TUR" });
  });
  it("matches by name substring", () => {
    expect(findPopulations(rows, "german", 15)[0].code).toBe(276);
  });
  it("matches by numeric code", () => {
    expect(findPopulations(rows, "792", 15)[0].iso3).toBe("TUR");
  });
});

describe("shapeData - join cancer labels + project metrics", () => {
  it("joins labels and keeps the GLOBOCAN metrics incl. UI", () => {
    const labels = new Map([[1, "Lip, oral cavity"]]);
    const ds = [{ cancer_code: 1, total: 2246, total_pop: 85561976, asr: 2.09, crude_rate: 2.62, cum_risk_74: 0.24, rank: 20, ui: { low: 1725, high: 2924 } }];
    const out = shapeData(ds, labels, 40);
    expect(out[0]).toMatchObject({ cancer_code: 1, cancer: "Lip, oral cavity", total: 2246, asr: 2.09, rank: 20, ui: { low: 1725, high: 2924 } });
    expect(out[0].prev_time).toBeNull(); // incidence/mortality rows have no prevalence period
  });
  it("surfaces prev_time for prevalence rows", () => {
    const out = shapeData([{ cancer_code: 20, total: 62724, prev_time: 3, asr: 116.93 }], new Map([[20, "Breast"]]), 40);
    expect(out[0]).toMatchObject({ cancer: "Breast", total: 62724, prev_time: 3 });
  });
  it("caps at limit and null-labels unknown codes", () => {
    const out = shapeData([{ cancer_code: 99, total: 1 }, { cancer_code: 1, total: 2 }], new Map(), 1);
    expect(out).toHaveLength(1);
    expect(out[0].cancer).toBeNull();
  });
});
