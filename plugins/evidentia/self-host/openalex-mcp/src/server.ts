/**
 * server.ts — openalex-mcp tool layer (Cureonics self-host, evidentia Tier-K bibliographic core).
 *
 * WHY THIS WORKER EXISTS
 * ----------------------
 * evidentia's OpenAlex rung (KOL mapping, citation networks, institution/author disambiguation —
 * §8 KOL Haritası) ran on `openalex.caseyjhand.com`, a third-party individual-operator host.
 * connector-registry.md §6.3P named the fix; on 2026-08-08 the risk materialised — that host
 * returned HTTP 530 (origin down) alongside `pubmed-epmc`. This Worker collapses the boundary.
 *
 * Tool and argument names are REPLICATED from the retired connector's live `inputSchema`
 * (captured 2026-08-07, before the outage) so the swap is drop-in for the skill, the registry,
 * the agent allowlist and the G-TOOLS smoke matrix.
 *
 * UPSTREAM: api.openalex.org — fully authless and open (CC0). No server-side secret, therefore
 * KEYLESS by design (who-gho/globocan/ema/drugddx precedent). `mailto` is the documented POLITE-POOL
 * courtesy parameter — a public contact address, not a credential — and it buys faster, more
 * reliable service, so it is sent on every request.
 *
 * HONEST SCOPE: a retrieval proxy over a bibliometric catalog. Counts are OpenAlex's, not ground
 * truth: coverage and author disambiguation are both imperfect, so a zero means "OpenAlex has no
 * matching record", never "this does not exist". Nothing is inferred or interpolated.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface OpenalexEnv {
  /** Public polite-pool contact. NOT a secret. */
  CONTACT_EMAIL?: string;
  /** OPTIONAL OpenAlex API key. Unset by default, which is why this Worker is KEYLESS.
   *
   *  ⚠️ OPERATIONAL LIMIT, MEASURED 2026-08-08. OpenAlex now meters requests against a daily
   *  budget scoped to the SOURCE IP ("Insufficient budget. This request costs $0.001 but you only
   *  have $0 remaining. Resets at midnight UTC"). A Cloudflare Worker egresses from a SHARED
   *  address pool, so that budget is spent by unrelated traffic before we ever call. Measured the
   *  same minute: the identical list request returned 200 from a residential IP and a budget-429
   *  from the Worker; single-entity GETs still succeeded. `mailto` alone does NOT exempt you.
   *  Setting this key moves the budget onto the key and restores full function.
   *  ⚠️ If you set it, re-gate the deployment (`MCP_ALLOW_NO_AUTH=0` + MCP_API_KEY) — the keyless
   *  rationale is "there is nothing to protect", and with a key there is. */
  OPENALEX_API_KEY?: string;
  OPENALEX_BASE?: string; // test override
}

const DEFAULT_BASE = "https://api.openalex.org";
const DEFAULT_EMAIL = "ops@cureonics.com";
const UA = "openalex-mcp/1.0 (+https://cureonics.com)";

const ENTITIES = ["works", "authors", "sources", "institutions", "topics",
  "keywords", "publishers", "funders", "concepts"] as const;
type Entity = (typeof ENTITIES)[number];

const CAVEAT =
  "Source: OpenAlex (api.openalex.org, authless CC0 catalog), proxied by the Cureonics self-host " +
  "openalex-mcp. Counts and links are OpenAlex's own: coverage is incomplete and author/institution " +
  "disambiguation is imperfect, so a zero means OpenAlex holds no matching record — NOT that the " +
  "work, person or institution does not exist. Nothing here is inferred; verify any identity claim " +
  "(ORCID/ROR) against the primary source before citing.";

const ok = (o: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(o, null, 2) }] });
const fail = (m: string) => ({ isError: true, content: [{ type: "text" as const, text: m }] });

// ------------------------------------------------------------- pure helpers --
function baseOf(env: OpenalexEnv): string {
  return (env.OPENALEX_BASE || DEFAULT_BASE).replace(/\/+$/, "");
}

function contact(env: OpenalexEnv): string {
  return (env.CONTACT_EMAIL || DEFAULT_EMAIL).trim();
}

/** `{a:1,b:"x"}` -> `a:1,b:x` — OpenAlex's comma-joined filter grammar. Values are passed through
 *  URLSearchParams by the caller, so they are encoded once and never spliced into the query. */
function encodeFilters(filters?: Record<string, unknown>): string {
  if (!filters) return "";
  return Object.entries(filters)
    .filter(([, v]) => v !== undefined && v !== null && String(v) !== "")
    .map(([k, v]) => `${k}:${Array.isArray(v) ? v.join("|") : String(v)}`)
    .join(",");
}

/** Build an entity-list URL. `mailto` is always attached (polite pool). */
function listUrl(env: OpenalexEnv, entity: string, params: Record<string, unknown>): string {
  const u = new URL(`${baseOf(env)}/${entity}`);
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || String(v) === "") continue;
    u.searchParams.set(k, Array.isArray(v) ? v.join(",") : String(v));
  }
  u.searchParams.set("mailto", contact(env));
  if (env.OPENALEX_API_KEY) u.searchParams.set("api_key", env.OPENALEX_API_KEY);
  return u.toString();
}

/** OpenAlex ids are `W…/A…/S…/I…/T…/P…/F…/C…` + digits, optionally as a full URL. Normalise to the
 *  bare id so a caller can paste either form; reject anything else before it reaches a filter. */
const OA_ID_RE = /^[WASITPFCK]\d{2,12}$/i;
function normalizeId(raw: string): string | null {
  const s = String(raw ?? "").trim().replace(/^https?:\/\/openalex\.org\//i, "");
  return OA_ID_RE.test(s) ? s.toUpperCase() : null;
}

function isEntity(e: unknown): e is Entity {
  return (ENTITIES as readonly string[]).includes(String(e));
}

/**
 * Citation direction → OpenAlex filter. MEASURED 2026-08-08, and it reads BACKWARDS from the
 * obvious guess — this is the trap the mapping exists to neutralise:
 *
 *   filter=cites:W2165010366     -> 21,475 results  (GRADE 2008's cited_by_count is 22,679)
 *   filter=cited_by:W2165010366  ->     12 results  (its referenced_works length is 12)
 *
 * So `cites:X` selects works that CITE X (incoming), and `cited_by:X` selects the works X cites
 * (outgoing references). Getting this backwards silently returns a plausible-looking but wrong
 * network — 12 papers presented as "who cites this landmark".
 */
function citationFilter(direction: string, id: string): string {
  return direction === "incoming" ? `cites:${id}` : `cited_by:${id}`;
}

/** Shape one entity record down to what the skill cites from — never the raw 40-field blob. */
function shapeEntity(r: any, entity: string): Record<string, unknown> {
  const base = {
    id: String(r?.id ?? "").replace(/^https?:\/\/openalex\.org\//i, ""),
    display_name: r?.display_name ?? null,
    cited_by_count: r?.cited_by_count ?? null,
    works_count: r?.works_count ?? null,
  };
  if (entity === "works") {
    return {
      ...base, doi: r?.doi ?? null, year: r?.publication_year ?? null,
      type: r?.type ?? null, is_oa: r?.open_access?.is_oa ?? null,
      oa_url: r?.open_access?.oa_url ?? null,
      authors: (r?.authorships ?? []).slice(0, 25).map((a: any) => ({
        name: a?.author?.display_name ?? null,
        orcid: a?.author?.orcid ?? null,
        institutions: (a?.institutions ?? []).map((i: any) => i?.display_name).filter(Boolean),
      })),
      venue: r?.primary_location?.source?.display_name ?? null,
    };
  }
  if (entity === "authors") {
    return { ...base, orcid: r?.orcid ?? null, h_index: r?.summary_stats?.h_index ?? null,
      i10: r?.summary_stats?.i10_index ?? null,
      affiliation: r?.last_known_institutions?.[0]?.display_name ?? r?.last_known_institution?.display_name ?? null };
  }
  if (entity === "institutions") {
    return { ...base, ror: r?.ror ?? null, country: r?.country_code ?? null, type: r?.type ?? null };
  }
  return { ...base, ...(r?.ror ? { ror: r.ror } : {}), ...(r?.issn_l ? { issn_l: r.issn_l } : {}) };
}

/** Pull the valid-field list out of OpenAlex's own error message. The API has no schema endpoint,
 *  but an invalid field name makes it enumerate every legal one — so the list is LIVE, never a
 *  bundled copy that can silently go stale. */
function parseValidFields(message: string): string[] {
  const m = /Valid fields are underscore or hyphenated versions of:\s*([\s\S]+)$/i.exec(message || "");
  if (!m) return [];
  return m[1].split(",").map((s) => s.trim().replace(/\.$/, "")).filter(Boolean);
}

// ----------------------------------------------------------------- network --
/** A budget-429 is NOT transient: the quota resets at midnight UTC, so retrying only burns time
 *  and hammers the upstream. Detect it and say what actually fixes it. A plain 429/5xx IS
 *  transient and gets one short backoff. */
function isBudgetError(body: any): boolean {
  return /insufficient budget/i.test(String(body?.message ?? body?.error ?? ""));
}

const BUDGET_HINT =
  "OpenAlex meters requests against a DAILY budget scoped to the SOURCE IP, and this Worker " +
  "egresses from Cloudflare's shared address pool — so the quota was spent by unrelated traffic. " +
  "Measured 2026-08-08: the same request returned 200 from a residential IP. `mailto` does not " +
  "exempt you. FIX: set the OPENALEX_API_KEY secret (moves the budget onto the key, then re-gate " +
  "with MCP_ALLOW_NO_AUTH=0), or route this Worker through the HP residential relay. Single-entity " +
  "GETs (openalex_search_entities with `id`) still work meanwhile.";

async function getJson(url: string): Promise<{ status: number; body: any }> {
  let r = await fetch(url, { headers: { accept: "application/json", "user-agent": UA } });
  let body: any = null;
  try { body = await r.json(); } catch { body = null; }
  if (r.status === 429 && !isBudgetError(body)) {
    await new Promise((res) => setTimeout(res, 600));
    r = await fetch(url, { headers: { accept: "application/json", "user-agent": UA } });
    try { body = await r.json(); } catch { body = null; }
  }
  return { status: r.status, body };
}

/** Uniform upstream-error text: a budget failure must never read like "OpenAlex has no data". */
function upstreamError(tool: string, r: { status: number; body: any }): string {
  const msg = String(r.body?.message ?? r.body?.error ?? "").slice(0, 200);
  return isBudgetError(r.body)
    ? `${tool}: OpenAlex request BUDGET exhausted for this Worker's egress IP (HTTP ${r.status}). ${msg}\n\n${BUDGET_HINT}`
    : `${tool}: OpenAlex ${r.status}: ${msg}`;
}

// -------------------------------------------------------------- registration --
export function registerTools(server: McpServer, env: OpenalexEnv): void {
  const RO = { readOnlyHint: true } as const;
  const entityArg = z.enum(ENTITIES);

  server.tool(
    "openalex_resolve_name",
    "Resolve a name to an OpenAlex entity + its persistent identifier (ORCID for an author, ROR " +
      "for an institution, ISSN-L for a source). Names are ambiguous, ids are not — resolve BEFORE " +
      "filtering by an entity. " + CAVEAT,
    {
      entity_type: entityArg.optional().describe("Default 'institutions'"),
      query: z.string().describe("Name to resolve, e.g. 'Hacettepe University'"),
      filters: z.record(z.any()).optional().describe("Extra OpenAlex filters, e.g. {country_code:'TR'}"),
    },
    RO,
    async ({ entity_type, query, filters }: any) => {
      try {
        const entity = isEntity(entity_type) ? entity_type : "institutions";
        const f = encodeFilters(filters);
        const r = await getJson(listUrl(env, entity, { search: query, filter: f || undefined, "per-page": 5 }));
        if (r.status >= 400) return fail(upstreamError("openalex_resolve_name", r));
        const matches = (r.body?.results ?? []).map((x: any) => shapeEntity(x, entity));
        return ok({ entity_type: entity, query, total: r.body?.meta?.count ?? 0,
          matches, note: "Use `id` (not the name) in downstream filters.", caveat: CAVEAT });
      } catch (e: any) { return fail(`openalex_resolve_name failed: ${e.message}`); }
    },
  );

  server.tool(
    "openalex_search_entities",
    "Search or fetch OpenAlex entities (works/authors/institutions/sources/topics/…) with the " +
      "native filter grammar, cursor paging and field selection. " + CAVEAT,
    {
      entity_type: entityArg,
      id: z.string().optional().describe("Fetch ONE entity by OpenAlex id (e.g. 'W2165010366')"),
      query: z.string().optional().describe("Free-text search"),
      search_mode: z.enum(["default", "title", "abstract", "fulltext"]).optional(),
      filters: z.record(z.any()).optional(),
      sort: z.string().optional().describe("e.g. 'cited_by_count:desc'"),
      select: z.array(z.string()).optional().describe("Restrict returned fields (cuts payload)"),
      per_page: z.number().int().min(1).max(200).optional(),
      cursor: z.string().optional().describe("Cursor from a previous response ('*' to start)"),
      sample: z.number().int().min(1).max(10000).optional().describe("Random sample size"),
      seed: z.string().optional().describe("Seed making `sample` reproducible"),
    },
    RO,
    async (a: any) => {
      try {
        if (!isEntity(a.entity_type)) return fail(`unknown entity_type '${a.entity_type}'`);
        if (a.id) {
          const id = normalizeId(a.id);
          if (!id) return fail(`invalid OpenAlex id '${a.id}' (expected e.g. W2165010366)`);
          const r = await getJson(listUrl(env, `${a.entity_type}/${id}`, {}));
          if (r.status >= 400) return fail(upstreamError("openalex_search_entities", r));
          return ok({ entity_type: a.entity_type, id, entity: shapeEntity(r.body, a.entity_type), caveat: CAVEAT });
        }
        const searchKey = a.search_mode && a.search_mode !== "default"
          ? `${a.search_mode}.search` : null;
        const filters = { ...(a.filters ?? {}) };
        if (a.query && searchKey) filters[searchKey] = a.query;
        const r = await getJson(listUrl(env, a.entity_type, {
          search: a.query && !searchKey ? a.query : undefined,
          filter: encodeFilters(filters) || undefined,
          sort: a.sort, select: a.select, "per-page": a.per_page ?? 10,
          cursor: a.cursor, sample: a.sample, seed: a.seed,
        }));
        if (r.status >= 400) return fail(upstreamError("openalex_analyze_trends", r));
        return ok({ entity_type: a.entity_type, total: r.body?.meta?.count ?? 0,
          next_cursor: r.body?.meta?.next_cursor ?? null,
          returned: (r.body?.results ?? []).length,
          results: (r.body?.results ?? []).map((x: any) => shapeEntity(x, a.entity_type)),
          caveat: CAVEAT });
      } catch (e: any) { return fail(`openalex_search_entities failed: ${e.message}`); }
    },
  );

  server.tool(
    "openalex_analyze_trends",
    "Group a filtered entity set by a field (publication_year, authorships.institutions.country_code, " +
      "type, open_access.is_oa, …) — the aggregate view behind a KOL or output-trend chart. " + CAVEAT,
    {
      entity_type: entityArg,
      group_by: z.string().describe("Field to group by, e.g. 'publication_year'"),
      filters: z.record(z.any()).optional().describe("⚠️ free text goes in `default.search`, not `search`"),
      include_unknown: z.boolean().optional(),
      per_page: z.number().int().min(1).max(200).optional(),
      order: z.enum(["count", "key"]).optional().describe("Sort groups by count (default) or key"),
      cursor: z.string().optional(),
    },
    RO,
    async (a: any) => {
      try {
        if (!isEntity(a.entity_type)) return fail(`unknown entity_type '${a.entity_type}'`);
        const r = await getJson(listUrl(env, a.entity_type, {
          group_by: a.group_by, filter: encodeFilters(a.filters) || undefined,
          "per-page": a.per_page ?? 50, cursor: a.cursor,
        }));
        if (r.status >= 400) return fail(upstreamError("openalex_get_citation_graph", r));
        let groups = (r.body?.group_by ?? []).map((g: any) => ({
          key: g?.key ?? null, label: g?.key_display_name ?? null, count: g?.count ?? 0,
        }));
        if (!a.include_unknown) groups = groups.filter((g: any) => String(g.key).toLowerCase() !== "unknown");
        if (a.order === "key") groups.sort((x: any, y: any) => String(x.key).localeCompare(String(y.key)));
        return ok({ entity_type: a.entity_type, group_by: a.group_by,
          total_entities: r.body?.meta?.count ?? 0, groups_returned: groups.length, groups, caveat: CAVEAT });
      } catch (e: any) { return fail(`openalex_analyze_trends failed: ${e.message}`); }
    },
  );

  server.tool(
    "openalex_get_citation_graph",
    "Walk the citation network around one work. `direction:'incoming'` = works that CITE the seed; " +
      "`direction:'outgoing'` = the works the seed cites (its references). " + CAVEAT,
    {
      seed_id: z.string().describe("OpenAlex work id, e.g. 'W2165010366'"),
      direction: z.enum(["incoming", "outgoing"]).describe("incoming = citing works; outgoing = references"),
      filters: z.record(z.any()).optional(),
      sort: z.string().optional().describe("e.g. 'cited_by_count:desc'"),
      select: z.array(z.string()).optional(),
      per_page: z.number().int().min(1).max(200).optional(),
      cursor: z.string().optional(),
    },
    RO,
    async ({ seed_id, direction, filters, sort, select, per_page, cursor }: any) => {
      try {
        const id = normalizeId(seed_id);
        if (!id) return fail(`invalid seed_id '${seed_id}' (expected e.g. W2165010366)`);
        const base = citationFilter(direction, id);
        const extra = encodeFilters(filters);
        const r = await getJson(listUrl(env, "works", {
          filter: extra ? `${base},${extra}` : base,
          sort: sort ?? "cited_by_count:desc", select,
          "per-page": per_page ?? 10, cursor,
        }));
        if (r.status >= 400) return fail(`OpenAlex ${r.status}: ${r.body?.message ?? ""}`.slice(0, 300));
        return ok({ seed_id: id, direction, filter: base,
          total: r.body?.meta?.count ?? 0, next_cursor: r.body?.meta?.next_cursor ?? null,
          returned: (r.body?.results ?? []).length,
          works: (r.body?.results ?? []).map((x: any) => shapeEntity(x, "works")),
          caveat: CAVEAT });
      } catch (e: any) { return fail(`openalex_get_citation_graph failed: ${e.message}`); }
    },
  );

  server.tool(
    "openalex_describe_fields",
    "List the field names that are LEGAL for a given entity in a given context (filter / sort / " +
      "select / group_by). Derived live from OpenAlex itself, so it can never drift from the API. " +
      "Call this before guessing a filter name. " + CAVEAT,
    {
      entity_type: entityArg,
      context: z.enum(["filter", "sort", "select", "group_by"]),
      query: z.string().optional().describe("Substring to narrow the list, e.g. 'institution'"),
    },
    RO,
    async ({ entity_type, context, query }: any) => {
      try {
        if (!isEntity(entity_type)) return fail(`unknown entity_type '${entity_type}'`);
        // Ask for a field that cannot exist; OpenAlex answers by enumerating the legal ones.
        const probe = "__evidentia_probe__";
        const params: Record<string, unknown> = context === "filter" ? { filter: `${probe}:1` } : { [context]: probe };
        const r = await getJson(listUrl(env, entity_type, params));
        const fields = parseValidFields(r.body?.message ?? "");
        if (!fields.length) {
          // A budget block is a DIFFERENT answer from "this context has no field list" — conflating
          // them would report an operational outage as an API limitation.
          if (isBudgetError(r.body)) return fail(upstreamError("openalex_describe_fields", r));
          return ok({ entity_type, context, fields: [], total: 0,
            note: `OpenAlex did not enumerate fields for context '${context}' (HTTP ${r.status}). ` +
                  `Message: ${String(r.body?.message ?? "").slice(0, 200)}`, caveat: CAVEAT });
        }
        const q = String(query ?? "").trim().toLowerCase();
        const shown = q ? fields.filter((f) => f.toLowerCase().includes(q)) : fields;
        return ok({ entity_type, context, total: fields.length, matched: shown.length,
          fields: shown, source: "live OpenAlex validation error (never a bundled copy)", caveat: CAVEAT });
      } catch (e: any) { return fail(`openalex_describe_fields failed: ${e.message}`); }
    },
  );
}

export const __testing = {
  baseOf, contact, isBudgetError, upstreamError, BUDGET_HINT, encodeFilters, listUrl, normalizeId, isEntity, citationFilter,
  shapeEntity, parseValidFields, ENTITIES, CAVEAT, DEFAULT_BASE,
};
