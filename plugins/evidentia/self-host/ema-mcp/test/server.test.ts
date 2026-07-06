import { describe, it, expect } from "vitest";
import { EMA_MEDICINES, EMA_GENERATED_AT, type EmaMedicine } from "../src/data.gen.js";
import { __testing } from "../src/server.js";

const { brief, lc } = __testing;

describe("baked corpus integrity", () => {
  it("has a substantial medicine count + a freshness stamp", () => {
    expect(EMA_MEDICINES.length).toBeGreaterThan(2000);
    expect(typeof EMA_GENERATED_AT).toBe("string");
    expect(EMA_GENERATED_AT.length).toBeGreaterThan(0);
  });

  it("carries both Human and Veterinary categories", () => {
    const cats = new Set(EMA_MEDICINES.map((m) => m.category));
    expect(cats.has("Human")).toBe(true);
    expect(cats.has("Veterinary")).toBe(true);
  });

  it("Keytruda is present with parsed ISO dates + flags + EPAR url", () => {
    const k = EMA_MEDICINES.find((m) => m.name === "Keytruda") as EmaMedicine;
    expect(k).toBeTruthy();
    expect(k.status).toBe("Authorised");
    expect(k.atc).toBe("L01FF02");
    expect(k.inn).toBe("pembrolizumab");
    expect(k.opinion_date).toMatch(/^\d{4}-\d{2}-\d{2}$/); // DD/MM/YYYY -> ISO
    expect(k.url).toContain("/medicines/human/EPAR/");
    expect(typeof k.orphan).toBe("boolean");
  });
});

describe("brief projection", () => {
  it("keeps the compact list fields and drops long text (indication)", () => {
    const k = EMA_MEDICINES.find((m) => m.name === "Keytruda") as EmaMedicine;
    const b = brief(k) as Record<string, unknown>;
    expect(b.name).toBe("Keytruda");
    expect(b.atc).toBe("L01FF02");
    expect("indication" in b).toBe(false);
    expect("active_substance" in b).toBe(false);
  });
});

describe("lc helper", () => {
  it("lowercases and null-guards", () => {
    expect(lc("ABC")).toBe("abc");
    expect(lc(null)).toBe("");
    expect(lc(undefined)).toBe("");
  });
});

describe("filter/search invariants over the real corpus", () => {
  it("ATC prefix L01 yields oncology medicines, all matching", () => {
    const l01 = EMA_MEDICINES.filter((m) => (m.atc ?? "").toUpperCase().startsWith("L01"));
    expect(l01.length).toBeGreaterThan(10);
    expect(l01.every((m) => (m.atc ?? "").toUpperCase().startsWith("L01"))).toBe(true);
  });

  it("orphan flag is boolean and a meaningful subset are orphan", () => {
    const orphans = EMA_MEDICINES.filter((m) => m.orphan === true);
    expect(orphans.length).toBeGreaterThan(50);
    expect(orphans.length).toBeLessThan(EMA_MEDICINES.length);
  });

  it("status vocabulary includes the core lifecycle states", () => {
    const statuses = new Set(EMA_MEDICINES.map((m) => m.status));
    expect(statuses.has("Authorised")).toBe(true);
    expect(statuses.has("Withdrawn")).toBe(true);
    expect(statuses.has("Refused")).toBe(true);
  });
});
