/**
 * server.ts — who-gho-mcp tool layer (Cureonics self-host, evidentia Tier-O).
 *
 * Serves the WHO Global Health Observatory (GHO) OData API — global disease-burden / mortality /
 * risk-factor / coverage indicators for ALL WHO member states and regions. This closes the
 * documented "global burden" gap in evidentia's evidence roster: PopHIVE covers the US only, and
 * GLOBOCAN/IHME have no native API, so before this Worker global/Türkiye burden was reported as an
 * unreachable gap. GHO gives country-level (ISO3, incl. TUR) and regional/global figures natively.
 *
 *   who_gho_search_indicators — resolve a topic (e.g. "tuberculosis mortality") to GHO indicator
 *                               codes (fetches the full Indicator catalogue, case-insensitive
 *                               substring filter).
 *   who_gho_query             — fetch data rows for one indicator code, filtered by country
 *                               (SpatialDim), year (TimeDim) and/or a disaggregation dim (Dim1).
 *   who_gho_dimensions        — list dimensions, or the allowed values of one dimension (e.g.
 *                               COUNTRY -> ISO3 codes, SEX -> SEX_MLE/SEX_FMLE/SEX_BTSX).
 *
 * UPSTREAM IS AUTHLESS (ghoapi.azureedge.net) — this Worker holds NO server-side secret, so it is
 * KEYLESS by design (no credential to protect, no confused-deputy). Read-only.
 *
 * HONEST SCOPE: GHO values are a mix of MODELLED estimates and REPORTED data; each row is
 * point-in-time and carries WHO's own value string. If a requested country/year combination has no
 * row, report the gap — never fabricate or interpolate.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface WhoGhoEnv {
  GHO_API_BASE?: string; // optional override (smoke/testing); defaults to the public GHO OData API
}

const DEFAULT_BASE = "https://ghoapi.azureedge.net/api";
const UA = "who-gho-mcp/1.0 (+https://cureonics.com)";

const GHO_CAVEAT =
  "WHO GHO (Global Health Observatory, ghoapi.azureedge.net, authless public). Values are a MIX of " +
  "MODELLED estimates and REPORTED country data — point-in-time; do not treat as exact counts. " +
  "SpatialDim is ISO3 country OR a WHO region/global code; TimeDim is the year; Dim1 is a " +
  "disaggregation (e.g. SEX_BTSX = both sexes). A missing country/year row means NO DATA — never " +
  "interpolate or fabricate.";

// A GHO indicator code (path segment) / dimension code — SSRF-safe allowlist.
// Must start with an alphanumeric and use only single _ . - separators between alphanumeric
// groups. This rejects bare/leading/trailing/consecutive dots (e.g. '.', '..', '../') so no path
// segment can normalize away the fixed host, while still matching every real GHO code
// (WHOSIS_000001, MDG_0000000017, SEX_BTSX, COUNTRY, AGEGROUP …).
const CODE_RE = /^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$/;

function baseOf(env: WhoGhoEnv): string {
  return (env.GHO_API_BASE || DEFAULT_BASE).replace(/\/+$/, "");
}

// ------------------------------------------------------------- pure helpers ---
// URL builders + row shapers are pure and unit-tested (no network) via __testing.

function indicatorCatalogueUrl(base: string): string {
  return `${base}/Indicator`;
}

function filterIndicators(
  rows: Array<{ IndicatorCode?: string; IndicatorName?: string }>,
  query: string,
  limit: number,
): Array<{ code: string; name: string }> {
  const q = query.trim().toLowerCase();
  const out: Array<{ code: string; name: string }> = [];
  for (const r of rows) {
    const name = String(r.IndicatorName ?? "");
    const code = String(r.IndicatorCode ?? "");
    if (!code) continue;
    if (q === "" || name.toLowerCase().includes(q) || code.toLowerCase().includes(q)) {
      out.push({ code, name });
      if (out.length >= limit) break;
    }
  }
  return out;
}

function odataEscape(v: string): string {
  return v.replace(/'/g, "''"); // OData single-quote escaping
}

function buildDataUrl(
  base: string,
  indicatorCode: string,
  opts: { country?: string; year?: number; dim1?: string; top?: number },
): string {
  const clauses: string[] = [];
  if (opts.country) clauses.push(`SpatialDim eq '${odataEscape(opts.country.toUpperCase())}'`);
  if (opts.year != null) clauses.push(`TimeDim eq ${Math.trunc(opts.year)}`);
  if (opts.dim1) clauses.push(`Dim1 eq '${odataEscape(opts.dim1.toUpperCase())}'`);
  const u = new URL(`${base}/${indicatorCode}`);
  if (clauses.length) u.searchParams.set("$filter", clauses.join(" and "));
  u.searchParams.set("$top", String(opts.top ?? 50));
  return u.toString();
}

function shapeDataRows(
  rows: Array<Record<string, unknown>>,
  limit: number,
): Array<Record<string, unknown>> {
  return rows.slice(0, limit).map((r) => ({
    country: r.SpatialDim ?? null,
    spatial_type: r.SpatialDimType ?? null,
    year: r.TimeDim ?? null,
    dim1_type: r.Dim1Type ?? null,
    dim1: r.Dim1 ?? null,
    value: r.Value ?? null,
    numeric: r.NumericValue ?? null,
    low: r.Low ?? null,
    high: r.High ?? null,
    comments: r.Comments ?? null,
  }));
}

function dimensionUrl(base: string, dimension?: string): string {
  if (dimension) return `${base}/DIMENSION/${dimension.toUpperCase()}/DimensionValues`;
  return `${base}/Dimension`;
}

// -------------------------------------------------------------- network ------
async function ghoFetch(url: string): Promise<{ status: number; body: any }> {
  const r = await fetch(url, { headers: { accept: "application/json", "user-agent": UA } });
  let body: any = null;
  try { body = await r.json(); } catch { body = { error: "upstream returned non-JSON" }; }
  return { status: r.status, body };
}

// --------------------------------------------------------------- register ----
export function registerTools(server: McpServer, env: WhoGhoEnv): void {
  const base = baseOf(env);

  server.tool(
    "who_gho_search_indicators",
    "Resolve a health-topic term to WHO GHO indicator codes. Fetches the full GHO Indicator " +
      "catalogue and returns codes whose name (or code) contains your query, case-insensitive. " +
      "Use the returned `code` with who_gho_query. " + GHO_CAVEAT,
    {
      query: z.string().describe("Topic term, e.g. 'tuberculosis mortality', 'measles immunization', 'life expectancy'"),
      limit: z.number().int().min(1).max(100).optional().describe("Max indicator matches (1-100, default 25)"),
    },
    async ({ query, limit }) => {
      try {
        const { status, body } = await ghoFetch(indicatorCatalogueUrl(base));
        if (status >= 400) {
          return { isError: true, content: [{ type: "text", text: `GHO Indicator catalogue ${status}` }] };
        }
        const rows = Array.isArray(body?.value) ? body.value : [];
        const matches = filterIndicators(rows, query, limit ?? 25);
        return { content: [{ type: "text", text: JSON.stringify({ query, total: matches.length, indicators: matches, caveat: GHO_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `who_gho_search_indicators failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "who_gho_query",
    "Fetch WHO GHO data rows for ONE indicator code (get it from who_gho_search_indicators). " +
      "Filter by country (SpatialDim ISO3, e.g. 'TUR'; or a WHO region/global code), year " +
      "(TimeDim), and/or a disaggregation dimension value (Dim1, e.g. 'SEX_BTSX'). Read-only. " + GHO_CAVEAT,
    {
      indicator_code: z.string().describe("GHO indicator code, e.g. 'WHOSIS_000001' (life expectancy at birth)"),
      country: z.string().optional().describe("ISO3 country code (e.g. 'TUR', 'USA', 'DEU') or WHO region/global code (e.g. 'GLOBAL', 'EUR')"),
      year: z.number().int().min(1900).max(2100).optional().describe("Year (TimeDim), e.g. 2019"),
      dim1: z.string().optional().describe("Disaggregation value (Dim1), e.g. 'SEX_MLE', 'SEX_FMLE', 'SEX_BTSX'. Use who_gho_dimensions to discover."),
      limit: z.number().int().min(1).max(200).optional().describe("Max rows to return (1-200, default 50)"),
    },
    async ({ indicator_code, country, year, dim1, limit }) => {
      const code = String(indicator_code).trim();
      if (!CODE_RE.test(code)) {
        return { isError: true, content: [{ type: "text", text: `Invalid indicator_code '${code}' (allowed: letters, digits, _ . -)` }] };
      }
      const top = limit ?? 50;
      try {
        const url = buildDataUrl(base, code, { country, year, dim1, top });
        const { status, body } = await ghoFetch(url);
        if (status >= 400) {
          const e = body?.error ?? body;
          return { isError: true, content: [{ type: "text", text: `GHO ${status}: ${JSON.stringify(e).slice(0, 400)}` }] };
        }
        const rows = Array.isArray(body?.value) ? body.value : [];
        const shaped = shapeDataRows(rows, top);
        return { content: [{ type: "text", text: JSON.stringify({ indicator_code: code, filters: { country: country ?? null, year: year ?? null, dim1: dim1 ?? null }, total: shaped.length, rows: shaped, caveat: GHO_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `who_gho_query failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "who_gho_dimensions",
    "List WHO GHO dimensions (no argument) or the allowed values of one dimension. Use this to " +
      "resolve country codes (dimension 'COUNTRY' -> ISO3), regions ('REGION'), or disaggregation " +
      "codes ('SEX', 'AGEGROUP') before calling who_gho_query. Read-only. " + GHO_CAVEAT,
    {
      dimension: z.string().optional().describe("Dimension code to expand, e.g. 'COUNTRY', 'REGION', 'SEX', 'AGEGROUP'. Omit to list all dimensions."),
      limit: z.number().int().min(1).max(500).optional().describe("Max values to return (1-500, default 300)"),
    },
    async ({ dimension, limit }) => {
      if (dimension && !CODE_RE.test(dimension)) {
        return { isError: true, content: [{ type: "text", text: `Invalid dimension '${dimension}' (allowed: letters, digits, _ . -)` }] };
      }
      const cap = limit ?? 300;
      try {
        const { status, body } = await ghoFetch(dimensionUrl(base, dimension));
        if (status >= 400) {
          return { isError: true, content: [{ type: "text", text: `GHO dimensions ${status}` }] };
        }
        const rows = Array.isArray(body?.value) ? body.value : [];
        const shaped = rows.slice(0, cap).map((r: any) => ({ code: r.Code ?? null, title: r.Title ?? null, dimension: r.Dimension ?? null, parent_code: r.ParentCode ?? null, parent_title: r.ParentTitle ?? null }));
        return { content: [{ type: "text", text: JSON.stringify({ dimension: dimension ?? null, total: shaped.length, values: shaped, caveat: GHO_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `who_gho_dimensions failed: ${e.message}` }] };
      }
    },
  );
}

export const __testing = {
  baseOf,
  indicatorCatalogueUrl,
  filterIndicators,
  buildDataUrl,
  shapeDataRows,
  dimensionUrl,
  odataEscape,
  CODE_RE,
  GHO_CAVEAT,
  DEFAULT_BASE,
};
