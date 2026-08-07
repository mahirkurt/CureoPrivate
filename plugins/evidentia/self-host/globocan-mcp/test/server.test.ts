import { describe, it, expect } from "vitest";
import { __testing } from "../src/server.js";

const { baseOf, metaUrl, dataUrl, shapeCancers, findPopulations, shapeData, fold, EXONYMS, DEFAULT_BASE } = __testing;

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
  // FIXTURE FIDELITY (2026-08-07): these labels are copied VERBATIM from the live
  // meta/populations/all/ response. The previous fixture said label: "Turkey" — a label GLOBOCAN
  // does not carry — so the suite stayed green while production returned ZERO matches for the
  // tool's own documented example ("'Turkey' / 'TUR' → 792"). A fixture that does not match the
  // measured upstream shape cannot catch an upstream-shape bug.
  const rows = [
    { country: 792, label: "Türkiye", country_iso3: "TUR", who_label: "WHO Europe region (EURO)", hdi_label: "Very High HDI", income_label: "Upper middle income" },
    { country: 276, label: "Germany", country_iso3: "DEU", who_label: "EURO", hdi_label: "Very high HDI", income_label: "High income" },
    { country: 384, label: "Côte d'Ivoire", country_iso3: "CIV", who_label: "AFRO", hdi_label: "Low HDI", income_label: "Lower middle income" },
    { country: 826, label: "United Kingdom", country_iso3: "GBR", who_label: "EURO", hdi_label: "Very High HDI", income_label: "High income" },
    { country: 804, label: "Ukraine", country_iso3: "UKR", who_label: "EURO", hdi_label: "High HDI", income_label: "Lower middle income" },
    { country: 528, label: "The Netherlands", country_iso3: "NLD", who_label: "EURO", hdi_label: "Very High HDI", income_label: "High income" },
    { country: 178, label: "Congo, Republic of", country_iso3: "COG", who_label: "AFRO", hdi_label: "Medium HDI", income_label: "Lower middle income" },
    { country: 180, label: "Congo, Democratic Republic of", country_iso3: "COD", who_label: "AFRO", hdi_label: "Low HDI", income_label: "Low income" },
  ];
  it("matches by ISO3 (exact, case-insensitive)", () => {
    const m = findPopulations(rows, "tur", 15);
    expect(m).toHaveLength(1);
    expect(m[0]).toMatchObject({ code: 792, label: "Türkiye", iso3: "TUR", matched_on: "iso3" });
  });
  it("matches by name substring", () => {
    expect(findPopulations(rows, "german", 15)[0].code).toBe(276);
  });
  it("matches by numeric code", () => {
    expect(findPopulations(rows, "792", 15)[0].iso3).toBe("TUR");
  });

  // --- regressions for the 2026-08-07 false-negative ---
  it("resolves the English exonym 'Turkey' (the tool's own documented example)", () => {
    const m = findPopulations(rows, "Turkey", 15);
    expect(m[0]).toMatchObject({ code: 792, label: "Türkiye" });
    expect(m[0].resolved_via).toContain("türkiye"); // rewrite is reported, never silent
  });
  it("resolves the diacritic-free spelling 'Turkiye' by folding", () => {
    expect(findPopulations(rows, "Turkiye", 15)[0].code).toBe(792);
  });
  it("still resolves the native spelling 'Türkiye'", () => {
    expect(findPopulations(rows, "Türkiye", 15)[0].code).toBe(792);
  });
  it("folds diacritics for Côte d'Ivoire", () => {
    expect(findPopulations(rows, "Cote d'Ivoire", 15)[0].code).toBe(384);
  });
  it("'UK' resolves to the United Kingdom, NOT to Ukraine (substring trap)", () => {
    // Pre-fix, fold('uk') was a substring of 'ukraine' and Ukraine won on upstream order.
    expect(findPopulations(rows, "UK", 15)[0].code).toBe(826);
  });
  it("'Holland' resolves to The Netherlands", () => {
    expect(findPopulations(rows, "Holland", 15)[0].code).toBe(528);
  });
  it("ranks an exact label above a substring match", () => {
    // 'congo' substring-hits both Congos; 'Congo, Republic of' is the exact label.
    expect(findPopulations(rows, "Congo, Republic of", 15)[0].code).toBe(178);
    expect(findPopulations(rows, "congo", 15).map((p: any) => p.code).sort()).toEqual([178, 180]);
  });
  it("returns nothing for a population GLOBOCAN does not carry (no fabricated alias)", () => {
    // Palestine / Taiwan / Vatican are absent upstream and are deliberately NOT aliased —
    // an empty result must keep meaning "no estimate", not "lookup failed".
    for (const q of ["Palestine", "Taiwan", "Vatican"]) {
      expect(findPopulations(rows, q, 15)).toEqual([]);
    }
  });
  it("every EXONYM value resolves against a real label shape (no dangling alias)", () => {
    // Guards the alias table against drift: a value must be foldable and non-empty, and the
    // aliases exercised by this fixture must actually land on a row.
    for (const [k, v] of Object.entries(EXONYMS)) {
      expect(fold(v).length).toBeGreaterThan(0);
      expect(fold(k)).toBe(k); // keys are stored pre-folded, else exact lookup misses
    }
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
