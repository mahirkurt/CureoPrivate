/**
 * server.ts — openfda-mcp tool layer (Cureonics Family A).
 *
 * Serves the TWO regulatory/coding sources that matter for medical-evidence work — and only
 * those (the broad comparative-legal Lex-Sanitas connector was dropped from evidentia's roster
 * because its legislation tools are noise for clinical evidence):
 *
 *   openfda_search — FDA openFDA (api.fda.gov, keyless public): FAERS adverse events, SPL
 *                    labeling, drugsfda approvals, enforcement/recalls, device/*.
 *   icd11_search   — WHO ICD-11 (MMS linearization): disease/condition coding. Backed by the
 *                    official WHO ICD-11 API with SERVER-SIDE OAuth (client_credentials using
 *                    ICD11_CLIENT_ID / ICD11_CLIENT_SECRET secrets) → keyless to the caller.
 *                    (The community `med-terminologies` connector cannot serve ICD-11 — its
 *                    server has no WHO credentials — so evidentia gets a working ICD-11 here.)
 *
 * HONEST SCOPE: FAERS/event counts are SPONTANEOUS reports — NOT incidence/prevalence.
 * openFDA endpoints are an SSRF-safe allowlist. Read-only; no caller secrets. ICD-11 is disabled
 * (returns a clear error) if the WHO credentials are not configured.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface OpenFdaEnv {
  ICD11_CLIENT_ID?: string;
  ICD11_CLIENT_SECRET?: string;
}

// ---------------------------------------------------------------- openFDA ----
const OPENFDA = "https://api.fda.gov";
const UA = "openfda-mcp/1.0 (+https://cureonics.com)";

const ENDPOINTS = [
  "drug/event", "drug/label", "drug/ndc", "drug/enforcement", "drug/drugsfda", "drug/shortages",
  "device/event", "device/recall", "device/510k", "device/classification",
  "device/enforcement", "device/pma", "device/registrationlisting", "device/udi", "device/covid19serology",
  "food/event", "food/enforcement",
  "animalandveterinary/event",
  "other/historicaldocument", "other/nsde", "other/substance", "other/unii",
  "tobacco/problem",
];

const FDA_CAVEAT =
  "openFDA (api.fda.gov, keyless public). FAERS/event counts are SPONTANEOUS reports — NOT " +
  "incidence/prevalence; do not present counts as rates. Label/enforcement/approval records are " +
  "point-in-time. Rate-limited (no key). Cross-verify safety signals before clinical claims.";

/** Normalise a caller-supplied endpoint: trim, strip wrapping slashes. Pure. */
function normalizeEndpoint(endpoint: unknown): string {
  return String(endpoint ?? "").trim().replace(/^\/+|\/+$/g, "");
}

/** The SSRF gate: only the allowlisted openFDA datasets may be reached. Pure. */
function isAllowedEndpoint(ep: string): boolean {
  return ENDPOINTS.includes(ep);
}

/** Build the openFDA request URL. Pure — split out of openfdaQuery so it is testable. */
function buildOpenFdaUrl(
  endpoint: string,
  search: string | undefined,
  count: string | undefined,
  limit: number | undefined,
  skip: number | undefined,
): string {
  const u = new URL(`${OPENFDA}/${endpoint}.json`);
  if (search) u.searchParams.set("search", search);
  if (count) u.searchParams.set("count", count);
  if (limit != null && !count) u.searchParams.set("limit", String(limit));
  if (skip != null) u.searchParams.set("skip", String(skip));
  return u.toString();
}

async function openfdaQuery(
  endpoint: string,
  search: string | undefined,
  count: string | undefined,
  limit: number | undefined,
  skip: number | undefined,
): Promise<{ status: number; body: any }> {
  const r = await fetch(buildOpenFdaUrl(endpoint, search, count, limit, skip),
    { headers: { accept: "application/json", "user-agent": UA } });
  let body: any = null;
  try { body = await r.json(); } catch { body = { error: { code: "NON_JSON", message: "upstream returned non-JSON" } }; }
  return { status: r.status, body };
}

// --------------------------------------------------------------- ICD-11 ------
const WHO_TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token";
const WHO_ICD_BASE = "https://id.who.int/icd/release/11";
const ICD_DEFAULT_RELEASE = "2024-01";

async function whoToken(env: OpenFdaEnv): Promise<string> {
  if (!env.ICD11_CLIENT_ID || !env.ICD11_CLIENT_SECRET) {
    throw new Error("ICD-11 disabled: ICD11_CLIENT_ID / ICD11_CLIENT_SECRET secrets not configured on this Worker.");
  }
  const body = new URLSearchParams({
    client_id: env.ICD11_CLIENT_ID,
    client_secret: env.ICD11_CLIENT_SECRET,
    scope: "icdapi_access",
    grant_type: "client_credentials",
  });
  const r = await fetch(WHO_TOKEN_URL, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded", "user-agent": UA },
    body,
  });
  if (!r.ok) throw new Error(`WHO token endpoint ${r.status}`);
  const j: any = await r.json();
  if (!j?.access_token) throw new Error("WHO token: no access_token in response");
  return j.access_token as string;
}

function stripEm(s: unknown): string {
  return String(s ?? "").replace(/<\/?em[^>]*>/g, "").trim();
}

/** Build the WHO ICD-11 MMS search URL. Pure. */
function buildIcd11SearchUrl(release: string, query: string): string {
  const u = new URL(`${WHO_ICD_BASE}/${release}/mms/search`);
  u.searchParams.set("q", query);
  u.searchParams.set("flatResults", "true");
  return u.toString();
}

/** Project WHO destinationEntities into our shape. Pure — split out of icd11Search. */
function shapeIcd11Entities(j: any, limit: number): any[] {
  return (j?.destinationEntities ?? []).slice(0, limit).map((e: any) => ({
    id: e.id,
    code: e.theCode ?? null,
    title: stripEm(e.title),
    chapter: e.chapter ?? null,
    score: e.score ?? null,
  }));
}

async function icd11Search(env: OpenFdaEnv, query: string, release: string, limit: number): Promise<any> {
  const token = await whoToken(env);
  const r = await fetch(buildIcd11SearchUrl(release, query), {
    headers: {
      authorization: `Bearer ${token}`,
      accept: "application/json",
      "API-Version": "v2",
      "Accept-Language": "en",
      "user-agent": UA,
    },
  });
  if (!r.ok) throw new Error(`WHO ICD-11 search ${r.status}`);
  const j: any = await r.json();
  const ents = shapeIcd11Entities(j, limit);
  return { source: `WHO ICD-11 MMS ${release}`, release, query, total: ents.length, entities: ents };
}

// --------------------------------------------------------------- register ----
export function registerTools(server: McpServer, env: OpenFdaEnv): void {
  server.tool(
    "openfda_search",
    "Query the FDA openFDA API (api.fda.gov, keyless). `endpoint` selects the dataset " +
      "(drug/event = FAERS adverse events, drug/label = SPL labeling, drug/drugsfda = approvals, " +
      "drug/enforcement = recalls, device/* = device data). `search` is an openFDA Lucene query. " +
      "`count` aggregates by a field (e.g. patient.reaction.reactionmeddrapt.exact → FAERS PT-level " +
      "signal counts) instead of returning records. Read-only. " + FDA_CAVEAT,
    {
      endpoint: z.string().describe("openFDA dataset, e.g. 'drug/event', 'drug/label', 'drug/drugsfda', 'drug/enforcement', 'device/event'"),
      search: z.string().optional().describe('openFDA Lucene search, e.g. \'patient.drug.medicinalproduct:"HUMIRA"\' or \'openfda.generic_name:"adalimumab"\''),
      count: z.string().optional().describe("Field to aggregate counts by, e.g. 'patient.reaction.reactionmeddrapt.exact'. Omit for record listing."),
      limit: z.number().int().min(1).max(100).optional().describe("Max records (1-100, default 5). Ignored when `count` is set."),
      skip: z.number().int().min(0).max(25000).optional().describe("Pagination offset (0-25000)."),
    },
    async ({ endpoint, search, count, limit, skip }) => {
      const ep = normalizeEndpoint(endpoint);
      if (!isAllowedEndpoint(ep)) {
        return { isError: true, content: [{ type: "text", text: `Invalid endpoint '${ep}'. Allowed: ${ENDPOINTS.join(", ")}` }] };
      }
      try {
        const { status, body } = await openfdaQuery(ep, search, count, limit ?? 5, skip);
        if (status === 404 && body?.error?.code === "NOT_FOUND") {
          return { content: [{ type: "text", text: JSON.stringify({ endpoint: ep, search: search ?? null, count: count ?? null, meta: { results: { total: 0 } }, results: [], caveat: FDA_CAVEAT }, null, 2) }] };
        }
        if (status >= 400) {
          const e = body?.error ?? body;
          return { isError: true, content: [{ type: "text", text: `openFDA ${status}: ${JSON.stringify(e).slice(0, 400)}` }] };
        }
        return { content: [{ type: "text", text: JSON.stringify({ endpoint: ep, search: search ?? null, count: count ?? null, meta: body?.meta, results: body?.results, caveat: FDA_CAVEAT }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `openfda_search failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "icd11_search",
    "Search the WHO ICD-11 (MMS linearization) for diseases/conditions; returns ICD-11 codes + " +
      "titles + entity URIs. Backed by the official WHO ICD-11 API with server-side OAuth " +
      "(keyless to the caller). Read-only. This is the authoritative ICD-11 source for evidentia " +
      "(the community med-terminologies connector cannot serve ICD-11 — no WHO credentials).",
    {
      query: z.string().describe("Disease/condition term, e.g. 'haemophilia A' or 'multiple sclerosis'"),
      release: z.string().optional().describe("ICD-11 release id (default '2024-01')"),
      limit: z.number().int().min(1).max(50).optional().describe("Max entities to return (default 10)"),
    },
    async ({ query, release, limit }) => {
      try {
        const out = await icd11Search(env, query, release || ICD_DEFAULT_RELEASE, limit ?? 10);
        return { content: [{ type: "text", text: JSON.stringify(out, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `icd11_search failed: ${e.message}` }] };
      }
    },
  );
}

// Pure helpers surfaced for test/server.test.ts (house pattern: who-gho / globocan / ema).
// These carry the SSRF gate (endpoint allowlist) and every URL/shape transform, so they are
// exactly the logic that must not drift silently. 2026-08-07: this Worker had NO server.test.ts
// and the allowlist was therefore unpinned.
export const __testing = {
  normalizeEndpoint, isAllowedEndpoint, buildOpenFdaUrl,
  stripEm, buildIcd11SearchUrl, shapeIcd11Entities,
  ENDPOINTS, FDA_CAVEAT, OPENFDA, WHO_ICD_BASE, ICD_DEFAULT_RELEASE,
};
