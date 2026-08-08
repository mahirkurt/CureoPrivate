/**
 * server.ts — pubmed-mcp tool layer (Cureonics self-host, evidentia Tier-K bibliographic core).
 *
 * WHY THIS WORKER EXISTS
 * ----------------------
 * evidentia's PubMed/EuropePMC/Unpaywall rung ran on `pubmed.caseyjhand.com` — a third-party,
 * unauthenticated, individual-operator host. connector-registry.md §6.3P documented the risk and
 * named the fix ("self-host the cyanheads OSS servers as operator Cloudflare Workers"). On
 * 2026-08-08 the risk materialised: that host returned HTTP 530 (origin down) for both
 * `pubmed-epmc` and `openalex`, taking out the bibliographic core's PubMed breadth AND Tier 6 of
 * the full-text cascade (Unpaywall legal-OA) at once. This Worker collapses that trust boundary.
 *
 * Tool names and argument names are REPLICATED from the retired connector's live `inputSchema`
 * (captured 2026-08-07, before the outage) so the swap is drop-in: the skill, the registry, the
 * agent allowlist and the G-TOOLS smoke matrix all keep working unchanged.
 *
 * UPSTREAMS — all authless, so this Worker holds NO server-side secret and is KEYLESS by design
 * (who-gho/globocan/ema/drugddx precedent; no credential to protect, no confused-deputy):
 *   NCBI E-utilities   eutils.ncbi.nlm.nih.gov  — esearch/esummary/efetch/elink/espell
 *   NCBI ID converter  www.ncbi.nlm.nih.gov/pmc/utils/idconv
 *   Europe PMC         www.ebi.ac.uk/europepmc/webservices/rest
 *   Unpaywall          api.unpaywall.org        — legal OA location for a DOI
 * NCBI asks unauthenticated clients to identify themselves with `tool` + `email`; both are
 * PUBLIC courtesy parameters, not credentials, and are sent on every E-utilities call.
 *
 * HONEST SCOPE: this is a retrieval proxy. It returns what the upstreams return; an empty result
 * means the upstream had nothing, never that the article does not exist. Full text is only
 * available for the open-access subset — a paywalled article yields metadata + a documented gap,
 * never fabricated body text.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface PubmedEnv {
  /** Public courtesy contact for the NCBI/Unpaywall polite pools. NOT a secret. */
  CONTACT_EMAIL?: string;
  /** NCBI E-utilities API key (Doppler `PUBMED_API_KEY`; the operator's canonical name for it). Unset by default, which is why this Worker is KEYLESS.
   *  Why it matters: NCBI rate-limits UNAUTHENTICATED callers per SOURCE IP (3 req/s), and a
   *  Cloudflare Worker egresses from a SHARED address pool — so the budget is spent by unrelated
   *  traffic and NCBI answers 429. Measured 2026-08-08: the same esearch returned 200 from a
   *  residential IP and 429 from the Worker. A key moves the limit onto the key (10 req/s).
   *  ⚠️ If you set it, the Worker then holds a credential: re-gate the deployment
   *  (`MCP_ALLOW_NO_AUTH=0` + MCP_API_KEY), because the keyless rationale is "nothing to protect". */
  PUBMED_API_KEY?: string;
  EUTILS_BASE?: string;   // test override
  EPMC_BASE?: string;     // test override
  UNPAYWALL_BASE?: string;// test override
  IDCONV_BASE?: string;   // test override
}

const D_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";
const D_EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest";
const D_UNPAYWALL = "https://api.unpaywall.org/v2";
const D_IDCONV = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0";
const TOOL_NAME = "evidentia-pubmed-mcp";
const DEFAULT_EMAIL = "ops@cureonics.com";
const UA = "pubmed-mcp/1.0 (+https://cureonics.com)";

const CAVEAT =
  "Source: NCBI E-utilities / Europe PMC / Unpaywall (all authless public APIs), proxied by the " +
  "Cureonics self-host pubmed-mcp. An empty result means the upstream returned nothing for this " +
  "query — it is NOT evidence the article does not exist. Full text is available only for the " +
  "open-access subset; a paywalled record yields metadata plus a stated gap, never invented body " +
  "text. Verify every citation against the primary record before use.";

const ok = (o: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(o, null, 2) }] });
const fail = (m: string) => ({ isError: true, content: [{ type: "text" as const, text: m }] });

// ------------------------------------------------------------- pure helpers --
function baseOf(env: PubmedEnv, key: "EUTILS_BASE" | "EPMC_BASE" | "UNPAYWALL_BASE" | "IDCONV_BASE"): string {
  const d = { EUTILS_BASE: D_EUTILS, EPMC_BASE: D_EPMC, UNPAYWALL_BASE: D_UNPAYWALL, IDCONV_BASE: D_IDCONV }[key];
  return (env[key] || d).replace(/\/+$/, "");
}

function contact(env: PubmedEnv): string {
  return (env.CONTACT_EMAIL || DEFAULT_EMAIL).trim();
}

/** E-utilities URL with the mandatory courtesy identification appended. */
function eutilsUrl(env: PubmedEnv, endpoint: string, params: Record<string, string | number | undefined>): string {
  const u = new URL(`${baseOf(env, "EUTILS_BASE")}/${endpoint}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && String(v) !== "") u.searchParams.set(k, String(v));
  }
  u.searchParams.set("tool", TOOL_NAME);
  u.searchParams.set("email", contact(env));
  if (env.PUBMED_API_KEY) u.searchParams.set("api_key", env.PUBMED_API_KEY);
  return u.toString();
}

/** PMIDs are digits. Rejecting anything else keeps a hostile id out of the upstream query
 *  string entirely — the ids are concatenated into `id=`, so this is the injection boundary. */
const PMID_RE = /^\d{1,9}$/;
const PMCID_RE = /^PMC\d{1,9}$/i;

function cleanIds(ids: unknown, kind: "pmid" | "pmcid" | "doi"): string[] {
  const arr = Array.isArray(ids) ? ids : [];
  const out: string[] = [];
  for (const raw of arr) {
    const s = String(raw ?? "").trim();
    if (!s) continue;
    if (kind === "pmid" && PMID_RE.test(s)) out.push(s);
    else if (kind === "pmcid" && PMCID_RE.test(s)) out.push(s.toUpperCase());
    else if (kind === "doi" && s.startsWith("10.") && !/[\s"']/.test(s)) out.push(s);
  }
  return [...new Set(out)];
}

/** Compose the PubMed search term from the structured filters the retired connector accepted.
 *  Each filter becomes a native PubMed field tag so the upstream — not us — does the matching. */
function buildQuery(a: {
  query: string; author?: string; journal?: string; meshTerms?: string[];
  language?: string; publicationTypes?: string[]; hasAbstract?: boolean;
  freeFullText?: boolean; species?: string; dateRange?: { from?: string; to?: string };
}): string {
  const parts = [`(${a.query.trim()})`];
  if (a.author) parts.push(`"${a.author}"[Author]`);
  if (a.journal) parts.push(`"${a.journal}"[Journal]`);
  for (const m of a.meshTerms ?? []) parts.push(`"${m}"[MeSH Terms]`);
  for (const p of a.publicationTypes ?? []) parts.push(`"${p}"[Publication Type]`);
  if (a.language) parts.push(`"${a.language}"[Language]`);
  if (a.species) parts.push(`"${a.species}"[MeSH Terms]`);
  if (a.hasAbstract) parts.push(`hasabstract[All Fields]`);
  if (a.freeFullText) parts.push(`"free full text"[Filter]`);
  const from = a.dateRange?.from, to = a.dateRange?.to;
  if (from || to) parts.push(`("${from || "1800/01/01"}"[Date - Publication] : "${to || "3000/12/31"}"[Date - Publication])`);
  return parts.join(" AND ");
}

/** Project an esummary JSON record into the shape the skill cites from. */
function shapeSummary(r: any): Record<string, unknown> {
  const ids: any[] = r?.articleids ?? [];
  const pick = (t: string) => ids.find((x) => x?.idtype === t)?.value ?? null;
  return {
    pmid: String(r?.uid ?? ""),
    title: r?.title ?? null,
    journal: r?.fulljournalname ?? r?.source ?? null,
    pubdate: r?.pubdate ?? null,
    authors: (r?.authors ?? []).map((a: any) => a?.name).filter(Boolean),
    doi: pick("doi"),
    pmcid: pick("pmc"),
    pubtypes: r?.pubtype ?? [],
    url: r?.uid ? `https://pubmed.ncbi.nlm.nih.gov/${r.uid}/` : null,
  };
}

/** Strip XML/JATS tags to readable text. Deliberately simple and LABELLED as such: workerd has no
 *  XML parser, and a regex stripper is honest about being lossy in a way a fake parser is not. */
function xmlToText(xml: string): string {
  return xml
    .replace(/<\?xml[\s\S]*?\?>/g, "")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<(script|style)[\s\S]*?<\/\1>/gi, "")
    .replace(/<\/(p|sec|title|abstract|article-title|li)>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&#x?[0-9a-f]+;/gi, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/** Apply the caller's character budget, reporting the cut instead of hiding it. */
function clip(text: string, max?: number): { text: string; truncated: boolean; full_chars: number } {
  const n = text.length;
  if (!max || n <= max) return { text, truncated: false, full_chars: n };
  return { text: text.slice(0, max), truncated: true, full_chars: n };
}

const CITATION_STYLES = new Set(["apa", "vancouver", "bibtex", "ris"]);

/** Render one shaped summary in the requested style. Pure, so every style is unit-pinned. */
function formatCitation(s: Record<string, any>, style: string): string {
  const authors: string[] = s.authors ?? [];
  const year = String(s.pubdate ?? "").slice(0, 4) || "n.d.";
  const j = s.journal ?? "";
  const t = String(s.title ?? "").replace(/\s+$/, "").replace(/\.$/, "");
  const doi = s.doi ? ` https://doi.org/${s.doi}` : "";
  switch (style) {
    case "vancouver":
      return `${authors.slice(0, 6).join(", ")}${authors.length > 6 ? ", et al" : ""}. ${t}. ${j}. ${year}. PMID: ${s.pmid}.${doi}`;
    case "bibtex":
      return `@article{pmid${s.pmid},\n  title = {${t}},\n  author = {${authors.join(" and ")}},\n  journal = {${j}},\n  year = {${year}},\n  pmid = {${s.pmid}}${s.doi ? `,\n  doi = {${s.doi}}` : ""}\n}`;
    case "ris":
      return ["TY  - JOUR", ...authors.map((a) => `AU  - ${a}`), `TI  - ${t}`, `JO  - ${j}`,
        `PY  - ${year}`, `AN  - ${s.pmid}`, ...(s.doi ? [`DO  - ${s.doi}`] : []), "ER  - "].join("\n");
    default: // apa
      return `${authors.join(", ")} (${year}). ${t}. ${j}.${doi}`;
  }
}

// ----------------------------------------------------------------- network --
/** Retry budget for NCBI's per-source-IP throttle. A Worker shares its egress address, so a 429
 *  here usually means somebody else spent the 3 req/s — a short backoff clears it, whereas
 *  surfacing the first 429 would make a healthy upstream look broken. Bounded and jitter-free
 *  (deterministic) so the behaviour is testable. */
const RETRY_ON = new Set([429, 500, 502, 503, 504]);
const BACKOFF_MS = [250, 750, 1500];

async function fetchRetrying(url: string, accept: string): Promise<Response> {
  let r = await fetch(url, { headers: { accept, "user-agent": UA } });
  for (let i = 0; i < BACKOFF_MS.length && RETRY_ON.has(r.status); i++) {
    await new Promise((res) => setTimeout(res, BACKOFF_MS[i]));
    r = await fetch(url, { headers: { accept, "user-agent": UA } });
  }
  return r;
}

async function getJson(url: string): Promise<{ status: number; body: any }> {
  const r = await fetchRetrying(url, "application/json");
  let body: any = null;
  try { body = await r.json(); } catch { body = null; }
  return { status: r.status, body };
}

async function getText(url: string): Promise<{ status: number; body: string }> {
  const r = await fetchRetrying(url, "text/plain, application/xml, */*");
  return { status: r.status, body: await r.text() };
}

/** esearch -> PMIDs; esummary -> shaped records. Shared by search and the MeSH lookup. */
async function esearchSummaries(env: PubmedEnv, db: string, term: string, retmax: number, retstart: number, sort?: string) {
  const s = await getJson(eutilsUrl(env, "esearch.fcgi", { db, term, retmode: "json", retmax, retstart, sort }));
  if (s.status >= 400 || !s.body) throw new Error(`NCBI esearch ${s.status}`);
  const res = s.body.esearchresult ?? {};
  const idlist: string[] = res.idlist ?? [];
  const total = Number(res.count ?? 0);
  if (!idlist.length) return { total, records: [] as any[], idlist };
  const sum = await getJson(eutilsUrl(env, "esummary.fcgi", { db, id: idlist.join(","), retmode: "json" }));
  if (sum.status >= 400 || !sum.body?.result) return { total, records: [], idlist };
  const records = idlist.map((id) => sum.body.result[id]).filter(Boolean);
  return { total, records, idlist };
}

// -------------------------------------------------------------- registration --
export function registerTools(server: McpServer, env: PubmedEnv): void {
  const RO = { readOnlyHint: true } as const;

  server.tool(
    "pubmed_search_articles",
    "Search PubMed with structured filters (author/journal/MeSH/publication type/date range/…), " +
      "returning shaped records with PMID, title, journal, authors, DOI and PMCID. " + CAVEAT,
    {
      query: z.string().describe("Free-text or PubMed-syntax query"),
      maxResults: z.number().int().min(1).max(100).optional().describe("Max records (1-100, default 10)"),
      offset: z.number().int().min(0).optional().describe("Result offset for paging (default 0)"),
      sort: z.enum(["relevance", "pub_date", "author", "journal"]).optional(),
      author: z.string().optional(), journal: z.string().optional(),
      meshTerms: z.array(z.string()).optional(), language: z.string().optional(),
      publicationTypes: z.array(z.string()).optional().describe("e.g. ['Randomized Controlled Trial']"),
      hasAbstract: z.boolean().optional(), freeFullText: z.boolean().optional(),
      species: z.enum(["Humans", "Animals"]).optional(),
      dateRange: z.object({ from: z.string().optional(), to: z.string().optional() }).optional()
        .describe("Publication date bounds, YYYY/MM/DD"),
    },
    RO,
    async (a: any) => {
      try {
        const term = buildQuery(a);
        const { total, records } = await esearchSummaries(
          env, "pubmed", term, a.maxResults ?? 10, a.offset ?? 0,
          a.sort === "pub_date" ? "pub+date" : a.sort);
        return ok({ query: a.query, term, total, returned: records.length,
          articles: records.map(shapeSummary), caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_search_articles failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_fetch_articles",
    "Fetch metadata + abstracts for known PMIDs (the detail step after pubmed_search_articles). " + CAVEAT,
    {
      pmids: z.array(z.string()).describe("PubMed IDs (digits)"),
      includeAbstract: z.boolean().optional().describe("Include abstract text (default true)"),
      maxCharacters: z.number().int().min(200).max(200000).optional().describe("Abstract budget per call"),
    },
    RO,
    async ({ pmids, includeAbstract, maxCharacters }: any) => {
      try {
        const ids = cleanIds(pmids, "pmid");
        if (!ids.length) return fail("no valid PMIDs (expected digit strings)");
        const sum = await getJson(eutilsUrl(env, "esummary.fcgi", { db: "pubmed", id: ids.join(","), retmode: "json" }));
        if (sum.status >= 400 || !sum.body?.result) return fail(`NCBI esummary ${sum.status}`);
        const articles = ids.map((id) => sum.body.result[id]).filter(Boolean).map(shapeSummary);
        let abstracts: Record<string, string> | undefined;
        if (includeAbstract !== false) {
          const t = await getText(eutilsUrl(env, "efetch.fcgi",
            { db: "pubmed", id: ids.join(","), rettype: "abstract", retmode: "text" }));
          if (t.status < 400) {
            const c = clip(t.body.trim(), maxCharacters ?? 20000);
            abstracts = { combined: c.text, ...(c.truncated ? { _truncated: `${c.full_chars} chars available` } : {}) } as any;
          }
        }
        return ok({ requested: ids.length, articles, abstracts, caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_fetch_articles failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_fetch_fulltext",
    "Resolve LEGAL open-access full text for PMCIDs / PMIDs / DOIs — Europe PMC fullTextXML first, " +
      "then Unpaywall for an OA location. This is Tier 6 of evidentia's full-text cascade. A " +
      "paywalled record returns metadata + an explicit gap, never invented text. " + CAVEAT,
    {
      pmcids: z.array(z.string()).optional().describe("PMC IDs, e.g. ['PMC1234567']"),
      pmids: z.array(z.string()).optional(),
      dois: z.array(z.string()).optional(),
      includeReferences: z.boolean().optional(),
      maxSections: z.number().int().min(1).max(100).optional(),
      sections: z.array(z.string()).optional(),
      maxCharacters: z.number().int().min(200).max(400000).optional().describe("Total budget (default 40000)"),
      maxCharactersPerSection: z.number().int().min(200).max(200000).optional(),
      overflowMode: z.enum(["truncate", "summarize"]).optional().describe("Only 'truncate' is honest here; 'summarize' is accepted and treated as truncate"),
    },
    RO,
    async (a: any) => {
      try {
        const pmcids = cleanIds(a.pmcids, "pmcid");
        const pmids = cleanIds(a.pmids, "pmid");
        const dois = cleanIds(a.dois, "doi");
        if (!pmcids.length && !pmids.length && !dois.length) return fail("give at least one of pmcids/pmids/dois");
        const budget = a.maxCharacters ?? 40000;
        const out: any[] = [];

        for (const pmcid of pmcids) {
          const r = await getText(`${baseOf(env, "EPMC_BASE")}/${pmcid}/fullTextXML`);
          if (r.status >= 400 || !r.body.trim()) {
            out.push({ id: pmcid, source: "europepmc", full_text: null,
              gap: `Europe PMC has no open-access full text for ${pmcid} (HTTP ${r.status}) — not proof it is unavailable elsewhere.` });
            continue;
          }
          const c = clip(xmlToText(r.body), a.maxCharactersPerSection ?? budget);
          out.push({ id: pmcid, source: "europepmc", extraction: "regex tag-strip (workerd has no XML parser — lossy by design, never reconstructed)",
            full_text: c.text, truncated: c.truncated, full_chars: c.full_chars });
        }
        for (const doi of dois) {
          const u = await getJson(`${baseOf(env, "UNPAYWALL_BASE")}/${encodeURIComponent(doi)}?email=${encodeURIComponent(contact(env))}`);
          const loc = u.body?.best_oa_location;
          out.push(loc
            ? { id: doi, source: "unpaywall", is_oa: !!u.body?.is_oa, oa_status: u.body?.oa_status ?? null,
                pdf_url: loc.url_for_pdf ?? null, landing_url: loc.url ?? null, license: loc.license ?? null,
                note: "Unpaywall returns a LOCATION, not the body. Fetch the URL to read it." }
            : { id: doi, source: "unpaywall", is_oa: false, gap: `No legal OA location for ${doi} (HTTP ${u.status}).` });
        }
        for (const pmid of pmids) {
          const conv = await getJson(`${baseOf(env, "IDCONV_BASE")}/?ids=${pmid}&format=json&tool=${TOOL_NAME}&email=${encodeURIComponent(contact(env))}`);
          const rec = conv.body?.records?.[0];
          out.push(rec?.pmcid
            ? { id: pmid, source: "idconv", pmcid: rec.pmcid, doi: rec.doi ?? null,
                note: "Has a PMCID — call pubmed_fetch_fulltext again with pmcids:[…] to read the body." }
            : { id: pmid, source: "idconv", pmcid: null, doi: rec?.doi ?? null,
                gap: `PMID ${pmid} has no PMC record, so no Europe PMC full text. Try the DOI via Unpaywall, or the licensed tiers (openathens).` });
        }
        return ok({ requested: { pmcids: pmcids.length, pmids: pmids.length, dois: dois.length },
          results: out, caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_fetch_fulltext failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_find_related",
    "Related / cited-by articles for one PMID via NCBI elink. " + CAVEAT,
    {
      pmid: z.string().describe("A single PubMed ID"),
      relationship: z.enum(["pubmed_pubmed", "pubmed_pubmed_citedin", "pubmed_pubmed_refs"]).optional(),
      maxResults: z.number().int().min(1).max(100).optional(),
      offset: z.number().int().min(0).optional(),
    },
    RO,
    async ({ pmid, relationship, maxResults, offset }: any) => {
      try {
        const [id] = cleanIds([pmid], "pmid");
        if (!id) return fail(`invalid PMID '${pmid}' (expected digits)`);
        const linkname = relationship ?? "pubmed_pubmed";
        const r = await getJson(eutilsUrl(env, "elink.fcgi", { dbfrom: "pubmed", db: "pubmed", id, linkname, retmode: "json" }));
        if (r.status >= 400) return fail(`NCBI elink ${r.status}`);
        const sets = r.body?.linksets?.[0]?.linksetdbs ?? [];
        const linked: string[] = (sets.find((s: any) => s.linkname === linkname)?.links ?? []).map(String);
        const page = linked.slice(offset ?? 0, (offset ?? 0) + (maxResults ?? 10));
        if (!page.length) return ok({ pmid: id, relationship: linkname, total: 0, related: [], caveat: CAVEAT });
        const sum = await getJson(eutilsUrl(env, "esummary.fcgi", { db: "pubmed", id: page.join(","), retmode: "json" }));
        const recs = page.map((p) => sum.body?.result?.[p]).filter(Boolean).map(shapeSummary);
        return ok({ pmid: id, relationship: linkname, total: linked.length, returned: recs.length, related: recs, caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_find_related failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_convert_ids",
    "Crosswalk between PMID / PMCID / DOI via the NCBI ID converter. " + CAVEAT,
    {
      ids: z.array(z.string()).describe("Identifiers to convert"),
      idType: z.enum(["pmid", "pmcid", "doi"]).describe("Type of the SUPPLIED ids"),
    },
    RO,
    async ({ ids, idType }: any) => {
      try {
        const clean = cleanIds(ids, idType);
        if (!clean.length) return fail(`no valid ${idType} values supplied`);
        const u = `${baseOf(env, "IDCONV_BASE")}/?ids=${encodeURIComponent(clean.join(","))}&format=json&tool=${TOOL_NAME}&email=${encodeURIComponent(contact(env))}`;
        const r = await getJson(u);
        if (r.status >= 400) return fail(`NCBI idconv ${r.status}`);
        const records = (r.body?.records ?? []).map((x: any) => ({
          requested: x?.["requested-id"] ?? null, pmid: x?.pmid ?? null,
          pmcid: x?.pmcid ?? null, doi: x?.doi ?? null, error: x?.errmsg ?? null,
        }));
        return ok({ idType, requested: clean.length, converted: records.filter((x: any) => !x.error).length, records, caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_convert_ids failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_lookup_mesh",
    "Look up MeSH descriptors for a term — the controlled vocabulary that makes a PRISMA search " +
      "strategy reproducible. " + CAVEAT,
    {
      query: z.string().describe("Concept to resolve, e.g. 'hemophilia A'"),
      maxResults: z.number().int().min(1).max(50).optional(),
      offset: z.number().int().min(0).optional(),
      includeDetails: z.boolean().optional(),
    },
    RO,
    async ({ query, maxResults, offset, includeDetails }: any) => {
      try {
        const { total, records } = await esearchSummaries(env, "mesh", query, maxResults ?? 10, offset ?? 0);
        const terms = records.map((r: any) => ({
          uid: String(r?.uid ?? ""), name: r?.ds_meshterms?.[0] ?? r?.title ?? null,
          scope: includeDetails ? (r?.ds_scopenote ?? null) : undefined,
          tree_numbers: includeDetails ? (r?.ds_idxlinks ?? r?.ds_treenumbers ?? null) : undefined,
        }));
        return ok({ query, total, returned: terms.length, mesh_terms: terms, caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_lookup_mesh failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_lookup_citation",
    "Resolve a PARTIAL reference (journal + year + volume + first page, and/or author/title) to a " +
      "PMID via NCBI ecitmatch — the deterministic path for checking a bibliography entry. " + CAVEAT,
    {
      journal: z.string().optional(), year: z.string().optional(), volume: z.string().optional(),
      firstPage: z.string().optional(), author: z.string().optional(), title: z.string().optional(),
    },
    RO,
    async ({ journal, year, volume, firstPage, author, title }: any) => {
      try {
        if (journal && year) {
          // ecitmatch is pipe-delimited: journal|year|volume|first_page|author|key|
          const key = "q1";
          const line = [journal, year, volume ?? "", firstPage ?? "", author ?? "", key, ""].join("|");
          const r = await getText(eutilsUrl(env, "ecitmatch.cgi", { db: "pubmed", retmode: "xml", bdata: line }));
          const m = /\|(\d{4,9})\s*$/m.exec(r.body.trim());
          if (m) return ok({ method: "ecitmatch", input: { journal, year, volume, firstPage, author }, pmid: m[1], caveat: CAVEAT });
        }
        // Fall back to a field-tagged search; report WHICH path answered so the caller can judge.
        const term = buildQuery({ query: title || author || journal || "", author, journal,
          dateRange: year ? { from: `${year}/01/01`, to: `${year}/12/31` } : undefined });
        const { total, records } = await esearchSummaries(env, "pubmed", term, 5, 0);
        return ok({ method: "search_fallback", term, total, candidates: records.map(shapeSummary),
          note: "ecitmatch needs journal+year; this is a ranked search, so confirm the match before citing.",
          caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_lookup_citation failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_spell_check",
    "NCBI espell suggestion for a query — catches the misspelling that silently returns zero hits. " + CAVEAT,
    { query: z.string().describe("Query to spell-check") },
    RO,
    async ({ query }: any) => {
      try {
        const r = await getText(eutilsUrl(env, "espell.fcgi", { db: "pubmed", term: query }));
        if (r.status >= 400) return fail(`NCBI espell ${r.status}`);
        const m = /<CorrectedQuery>([\s\S]*?)<\/CorrectedQuery>/i.exec(r.body);
        const corrected = m ? m[1].trim() : "";
        return ok({ query, corrected: corrected || null,
          changed: !!corrected && corrected.toLowerCase() !== query.trim().toLowerCase(), caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_spell_check failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_format_citations",
    "Render citations for known PMIDs in APA / Vancouver / BibTeX / RIS, built from the LIVE " +
      "esummary record so no field is invented. " + CAVEAT,
    {
      pmids: z.array(z.string()).describe("PubMed IDs"),
      format: z.enum(["apa", "vancouver", "bibtex", "ris"]).optional().describe("Default apa"),
    },
    RO,
    async ({ pmids, format }: any) => {
      try {
        const ids = cleanIds(pmids, "pmid");
        if (!ids.length) return fail("no valid PMIDs");
        const style = CITATION_STYLES.has(String(format)) ? String(format) : "apa";
        const sum = await getJson(eutilsUrl(env, "esummary.fcgi", { db: "pubmed", id: ids.join(","), retmode: "json" }));
        if (sum.status >= 400 || !sum.body?.result) return fail(`NCBI esummary ${sum.status}`);
        const found = ids.map((id) => sum.body.result[id]).filter(Boolean).map(shapeSummary);
        const missing = ids.filter((id) => !sum.body.result[id]);
        return ok({ format: style, citations: found.map((s) => ({ pmid: s.pmid, citation: formatCitation(s, style) })),
          ...(missing.length ? { not_found: missing } : {}), caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_format_citations failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_europepmc_search",
    "Search Europe PMC — broader than PubMed (preprints, agricola, patents, theses) and the right " +
      "second pass when PubMed comes up empty. " + CAVEAT,
    {
      query: z.string(),
      pageSize: z.number().int().min(1).max(100).optional(),
      cursorMark: z.string().optional().describe("Paging cursor from a previous response ('*' to start)"),
      sources: z.array(z.string()).optional().describe("Restrict to sources, e.g. ['MED','PPR']"),
      resultType: z.enum(["idlist", "lite", "core"]).optional(),
      sort: z.string().optional().describe("e.g. 'P_PDATE_D desc' or 'CITED desc'"),
    },
    RO,
    async ({ query, pageSize, cursorMark, sources, resultType, sort }: any) => {
      try {
        // EPMC field values are NOT quoted. Measured 2026-08-08: `SRC:"MED" AND EXT_ID:"18436948"`
        // -> hitCount 0, `SRC:MED AND EXT_ID:18436948` -> hitCount 1. Quoting made the `sources`
        // filter silently return nothing, which reads as "no such literature" rather than a bug.
        const src = (sources ?? []).map((s: string) => String(s).trim().toUpperCase())
          .filter((s: string) => /^[A-Z]{2,10}$/.test(s));
        const q = src.length ? `(${query}) AND (${src.map((s: string) => `SRC:${s}`).join(" OR ")})` : query;
        const u = new URL(`${baseOf(env, "EPMC_BASE")}/search`);
        u.searchParams.set("query", q);
        u.searchParams.set("format", "json");
        u.searchParams.set("pageSize", String(pageSize ?? 10));
        u.searchParams.set("resultType", resultType ?? "lite");
        u.searchParams.set("cursorMark", cursorMark ?? "*");
        if (sort) u.searchParams.set("sort", sort);
        const r = await getJson(u.toString());
        if (r.status >= 400) return fail(`Europe PMC search ${r.status}`);
        const results = (r.body?.resultList?.result ?? []).map((x: any) => ({
          source: x.source, epmcId: x.id, pmid: x.pmid ?? null, pmcid: x.pmcid ?? null,
          doi: x.doi ?? null, title: x.title ?? null, authors: x.authorString ?? null,
          journal: x.journalTitle ?? null, year: x.pubYear ?? null,
          isOpenAccess: x.isOpenAccess === "Y", citedBy: x.citedByCount ?? null,
        }));
        return ok({ query: q, hitCount: r.body?.hitCount ?? 0, nextCursorMark: r.body?.nextCursorMark ?? null,
          returned: results.length, results,
          note: "Pass a row's `source` + `epmcId` to pubmed_europepmc_fetch for its full record.",
          caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_europepmc_search failed: ${e.message}`); }
    },
  );

  server.tool(
    "pubmed_europepmc_fetch",
    "Fetch one Europe PMC record in full (abstract + metadata) by its `source` + `epmcId` from a " +
      "pubmed_europepmc_search hit. " + CAVEAT,
    {
      source: z.string().describe("Europe PMC source code, e.g. 'MED' or 'PPR'"),
      epmcId: z.string().describe("The `id` field of the search hit"),
      maxCharacters: z.number().int().min(200).max(200000).optional(),
    },
    RO,
    async ({ source, epmcId, maxCharacters }: any) => {
      try {
        const src = String(source).trim().toUpperCase();
        const id = String(epmcId).trim();
        if (!/^[A-Z]{2,10}$/.test(src) || !/^[A-Za-z0-9._-]{1,40}$/.test(id)) {
          return fail("invalid source/epmcId (source: letters; id: alphanumeric from a search hit)");
        }
        const u = new URL(`${baseOf(env, "EPMC_BASE")}/search`);
        u.searchParams.set("query", `SRC:${src} AND EXT_ID:${id}`);   // unquoted — see search note
        u.searchParams.set("format", "json");
        u.searchParams.set("resultType", "core");
        u.searchParams.set("pageSize", "1");
        const r = await getJson(u.toString());
        const rec = r.body?.resultList?.result?.[0];
        if (!rec) return ok({ source: src, epmcId: id, found: false,
          gap: `Europe PMC returned no record for ${src}:${id} — not proof it does not exist.`, caveat: CAVEAT });
        const abs = clip(String(rec.abstractText ?? ""), maxCharacters ?? 20000);
        return ok({ source: src, epmcId: id, found: true,
          record: { title: rec.title ?? null, authors: rec.authorString ?? null, journal: rec.journalInfo?.journal?.title ?? null,
            year: rec.pubYear ?? null, doi: rec.doi ?? null, pmid: rec.pmid ?? null, pmcid: rec.pmcid ?? null,
            isOpenAccess: rec.isOpenAccess === "Y", abstract: abs.text,
            ...(abs.truncated ? { abstract_truncated: `${abs.full_chars} chars available` } : {}) },
          caveat: CAVEAT });
      } catch (e: any) { return fail(`pubmed_europepmc_fetch failed: ${e.message}`); }
    },
  );
}

export const __testing = {
  baseOf, contact, eutilsUrl, RETRY_ON, BACKOFF_MS, cleanIds, buildQuery, shapeSummary, xmlToText, clip,
  formatCitation, CITATION_STYLES, CAVEAT, D_EUTILS, D_EPMC, D_UNPAYWALL, D_IDCONV,
};
