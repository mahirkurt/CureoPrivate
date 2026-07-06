/**
 * server.ts — globocan-mcp tool layer (Cureonics self-host, evidentia Tier-K-epi).
 *
 * Serves IARC's Global Cancer Observatory (GLOBOCAN 2022) — global/country cancer INCIDENCE and
 * MORTALITY estimates for 36 cancer sites across 185+ countries (incl. Türkiye), with ASR, crude
 * rate, cumulative risk, rank and uncertainty intervals. This closes evidentia's global cancer-
 * burden gap that PopHIVE (US-only) and who-gho (general GHO) do not cover.
 *
 *   gco_list_cancers      — the 36 GLOBOCAN cancer sites (id, label, ICD-10) — resolve names→codes.
 *   gco_resolve_population — find a country/region code by name or ISO3 (data endpoint needs codes).
 *   gco_query             — incidence or mortality for a population × cancer(s) × sex, joined with
 *                           cancer labels; returns total cases/deaths, ASR, crude rate, rank, UI.
 *
 * UPSTREAM IS AUTHLESS & HEADERLESS (gco-api.iarc.fr) — this Worker holds NO server-side secret, so
 * it is KEYLESS by design (no credential to protect, no confused-deputy). Read-only.
 *
 * HONEST SCOPE: GLOBOCAN figures are MODELLED ESTIMATES (not registry counts) for the reference year
 * 2022, with methodology varying by country data availability — every output carries an uncertainty
 * interval where available + a mandatory caveat. A population/cancer combination that returns no row
 * means NO ESTIMATE — never fabricate or interpolate.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface GlobocanEnv {
  GCO_API_BASE?: string; // optional override (smoke/testing); defaults to the public GLOBOCAN 2022 API
}

const DEFAULT_BASE = "https://gco-api.iarc.fr/api/globocan/v3/2022";
const UA = "globocan-mcp/1.0 (+https://cureonics.com)";

const GCO_CAVEAT =
  "IARC Global Cancer Observatory, GLOBOCAN 2022 (gco-api.iarc.fr, authless). Figures are MODELLED " +
  "ESTIMATES for reference year 2022 — NOT registry counts; methodology varies by country data " +
  "availability (see the uncertainty interval `ui`). ASR = age-standardised rate per 100,000 (World " +
  "standard); crude_rate per 100,000; cum_risk_74 = cumulative risk to age 74 (%). A missing " +
  "population/cancer row means NO ESTIMATE — never interpolate or fabricate.";

// SSRF-safe: population codes are digits, cancer id is digits-or-'all'.
const POP_RE = /^\d{1,4}$/;

function baseOf(env: GlobocanEnv): string {
  return (env.GCO_API_BASE || DEFAULT_BASE).replace(/\/+$/, "");
}

// -------------------------------------------------------------- pure helpers --
function metaUrl(base: string, kind: "cancers" | "populations"): string {
  return `${base}/meta/${kind}/all/`;
}

// data/rate/{type}/{sex}/({pop,pop,...})/{cancers}/?flags — key=rate returns all metrics.
// IMPORTANT: the GCO path order is {type}/{sex} (empirically verified 2026-07-05: the returned
// rows' `type`/`sex` fields match the FIRST/SECOND path slots respectively). type: 0=incidence,
// 1=mortality, 2=prevalence (prevalence rows carry a `prev_time` period). sex: 0=both, 1=male, 2=female.
function dataUrl(base: string, type: number, sex: number, pops: number[], cancer: string): string {
  const popList = `(${pops.join(",")})`;
  const q = "include_nmsc=0&include_nmsc_other=1&group_CRC=1&ages_group=0_17";
  return `${base}/data/rate/${type}/${sex}/${popList}/${cancer}/?${q}`;
}

function shapeCancers(rows: any[]): Array<{ id: number; label: string; icd: string | null; gender: number }> {
  return rows.map((r) => ({ id: r.cancer ?? r.id, label: r.label, icd: r.ICD ?? null, gender: r.gender ?? 0 }));
}

function findPopulations(rows: any[], query: string, limit: number) {
  const q = query.trim().toLowerCase();
  const out: any[] = [];
  for (const r of rows) {
    const label = String(r.label ?? "").toLowerCase();
    const iso3 = String(r.country_iso3 ?? "").toLowerCase();
    const code = String(r.country ?? r.country_code ?? "");
    if (q === "" || label.includes(q) || iso3 === q || code === q) {
      out.push({ code: r.country ?? r.country_code, label: r.label, iso3: r.country_iso3 ?? null, who_region: r.who_label ?? r.who_region ?? null, hdi: r.hdi_label ?? null, income: r.income_label ?? null });
      if (out.length >= limit) break;
    }
  }
  return out;
}

function shapeData(dataset: any[], cancerLabels: Map<number, string>, limit: number) {
  return (dataset || []).slice(0, limit).map((d) => ({
    cancer_code: d.cancer_code,
    cancer: cancerLabels.get(d.cancer_code) ?? null,
    total: d.total,                       // cases (incidence) / deaths (mortality) / prevalent cases (prevalence)
    total_pop: d.total_pop,
    asr: d.asr,                           // age-standardised rate /100k
    crude_rate: d.crude_rate,
    cum_risk_74: d.cum_risk_74,
    rank: d.rank ?? null,
    prev_time: d.prev_time ?? null,       // prevalence period in years (1/3/5) — only for type=prevalence
    ui: d.ui ?? null,                     // uncertainty interval {low, high}
  }));
}

// -------------------------------------------------------------- network ------
async function ghoJson(url: string): Promise<{ status: number; body: any }> {
  const r = await fetch(url, { headers: { accept: "application/json", "user-agent": UA } });
  let body: any = null;
  try { body = await r.json(); } catch { body = { error: "upstream returned non-JSON" }; }
  return { status: r.status, body };
}

async function loadCancerLabels(base: string): Promise<Map<number, string>> {
  const { status, body } = await ghoJson(metaUrl(base, "cancers"));
  const m = new Map<number, string>();
  if (status < 400 && Array.isArray(body)) for (const r of body) m.set(r.cancer ?? r.id, r.label);
  return m;
}

// --------------------------------------------------------------- register ----
export function registerTools(server: McpServer, env: GlobocanEnv): void {
  const base = baseOf(env);

  server.tool(
    "gco_list_cancers",
    "List the 36 GLOBOCAN cancer sites with their id, label and ICD-10 code. Use the `id` as the " +
      "`cancer` argument to gco_query (or 'all' for every site). " + GCO_CAVEAT,
    {},
    async () => {
      try {
        const { status, body } = await ghoJson(metaUrl(base, "cancers"));
        if (status >= 400 || !Array.isArray(body)) {
          return { isError: true, content: [{ type: "text", text: `GLOBOCAN meta/cancers ${status}` }] };
        }
        return { content: [{ type: "text", text: JSON.stringify({ total: body.length, cancers: shapeCancers(body), caveat: GCO_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `gco_list_cancers failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "gco_resolve_population",
    "Resolve a country/region to its GLOBOCAN population code (the data endpoint needs numeric " +
      "codes, not names). Search by name or ISO3 (e.g. 'Turkey' / 'TUR' → 792). Returns code + " +
      "label + ISO3 + WHO region + HDI/income band. " + GCO_CAVEAT,
    {
      query: z.string().describe("Country/region name or ISO3, e.g. 'Turkey', 'TUR', 'Germany', 'DEU'"),
      limit: z.number().int().min(1).max(50).optional().describe("Max matches (1-50, default 15)"),
    },
    async ({ query, limit }) => {
      try {
        const { status, body } = await ghoJson(metaUrl(base, "populations"));
        if (status >= 400 || !Array.isArray(body)) {
          return { isError: true, content: [{ type: "text", text: `GLOBOCAN meta/populations ${status}` }] };
        }
        const matches = findPopulations(body, query, limit ?? 15);
        return { content: [{ type: "text", text: JSON.stringify({ query, total: matches.length, populations: matches, caveat: GCO_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `gco_resolve_population failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "gco_query",
    "Fetch GLOBOCAN 2022 cancer INCIDENCE, MORTALITY or PREVALENCE for a population. Give `population` " +
      "as a numeric GLOBOCAN code (from gco_resolve_population, e.g. 792=Türkiye). `cancer`='all' for " +
      "every site or a numeric cancer id (from gco_list_cancers). `sex`: both/male/female. `type`: " +
      "incidence/mortality/prevalence. For prevalence, each cancer returns THREE rows — 1-, 3- and " +
      "5-year prevalence (see `prev_time`). Returns total cases/deaths/prevalent-cases, ASR, crude " +
      "rate, cumulative risk, rank and uncertainty interval, joined with cancer labels. " + GCO_CAVEAT,
    {
      population: z.string().describe("GLOBOCAN population code, e.g. '792' (Türkiye), '900' (World). Resolve names via gco_resolve_population."),
      cancer: z.string().optional().describe("'all' (default) or a numeric cancer id from gco_list_cancers (e.g. '15'=trachea/bronchus/lung)"),
      sex: z.enum(["both", "male", "female"]).optional().describe("Sex (default 'both')"),
      type: z.enum(["incidence", "mortality", "prevalence"]).optional().describe("Estimate type (default 'incidence'). Prevalence returns 1/3/5-year rows per cancer."),
      limit: z.number().int().min(1).max(300).optional().describe("Max rows (1-300, default 120 — covers all ~36 sites, incl. the 3× rows of an all-cancers prevalence query, without silent truncation)"),
    },
    async ({ population, cancer, sex, type, limit }) => {
      const pop = String(population).trim();
      if (!POP_RE.test(pop)) {
        return { isError: true, content: [{ type: "text", text: `Invalid population code '${pop}' (expected numeric GLOBOCAN code; use gco_resolve_population)` }] };
      }
      const cancerArg = (cancer ?? "all").trim();
      if (cancerArg !== "all" && !/^\d{1,3}$/.test(cancerArg)) {
        return { isError: true, content: [{ type: "text", text: `Invalid cancer '${cancerArg}' (use 'all' or a numeric id from gco_list_cancers)` }] };
      }
      const sexN = sex === "male" ? 1 : sex === "female" ? 2 : 0;
      const typeN = type === "mortality" ? 1 : type === "prevalence" ? 2 : 0;
      const cap = limit ?? 120;
      try {
        const [labels, res] = await Promise.all([
          loadCancerLabels(base),
          ghoJson(dataUrl(base, typeN, sexN, [Number(pop)], cancerArg)),
        ]);
        if (res.status >= 400) {
          return { isError: true, content: [{ type: "text", text: `GLOBOCAN data ${res.status}: ${JSON.stringify(res.body).slice(0, 300)}` }] };
        }
        const dataset = res.body?.dataset ?? [];
        const rows = shapeData(dataset, labels, cap);
        const truncated = dataset.length > rows.length;
        return { content: [{ type: "text", text: JSON.stringify({ population: pop, sex: sex ?? "both", type: type ?? "incidence", cancer: cancerArg, total_rows: rows.length, ...(truncated ? { truncated: true, available_rows: dataset.length, note: `Showing ${rows.length} of ${dataset.length} rows — raise 'limit' to see all.` } : {}), rows, caveat: GCO_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `gco_query failed: ${e.message}` }] };
      }
    },
  );
}

export const __testing = { baseOf, metaUrl, dataUrl, shapeCancers, findPopulations, shapeData, GCO_CAVEAT, DEFAULT_BASE };
