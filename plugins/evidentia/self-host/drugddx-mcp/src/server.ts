/**
 * server.ts — drugddx-mcp tool layer (Cureonics Family A re-expression).
 *
 * WHY THIS WORKER EXISTS: the registry connector
 * io.github.guptaprakhariitr/drug-interaction-mcp returned HTTP 500 (Cloudflare 1101,
 * Worker exception) on live probe (2026-06-25) — deployment broken. evidentia forks the
 * capability as a hardened-OAuth Worker so the clinical-DDI GAP in medical-research /
 * evidentia has a controlled, honest fallback.
 *
 * HONEST SCOPE (read before trusting output):
 *   - The NLM RxNav **Drug Interaction API was DISCONTINUED in January 2024**. There is no
 *     longer a free authoritative pairwise interaction endpoint from NLM.
 *   - Therefore this Worker is NOT a clinical pairwise DDI engine. It provides:
 *       (a) normalize_drug   — INN/brand → RxNorm RxCUI (RxNav /rxcui, still live)
 *       (b) interaction_label — the FDA label "Drug Interactions" section (DailyMed SPL,
 *                               LOINC 34073-7) for a single drug, verbatim-bounded.
 *   - Output MUST be presented as "label-derived interaction text + normalization", never as
 *     a computed/clinical interaction verdict. Pairwise clinical DDI requires a licensed source
 *     (Lexicomp / UpToDate / DrugBank). The tool descriptions and every result carry this caveat.
 *
 * All tools are read-only (readOnlyHint: true). No secrets are read here; upstream calls are
 * keyless public NIH/FDA REST.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const RXNAV = "https://rxnav.nlm.nih.gov/REST";
const DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/services/v2";
const UA = "drugddx-mcp/1.0 (+https://cureonics.com)";

const CAVEAT =
  "NOT a clinical pairwise DDI engine. NLM RxNav interaction API was discontinued Jan 2024. " +
  "This is RxNorm normalization + FDA-label (DailyMed SPL) interaction-section text only. " +
  "Confirm clinical interactions with a licensed source (Lexicomp/UpToDate/DrugBank).";

async function getJson(u: string): Promise<any> {
  const r = await fetch(u, { headers: { accept: "application/json", "user-agent": UA } });
  if (!r.ok) throw new Error(`upstream ${r.status} ${u}`);
  return r.json();
}

/** INN/brand name -> RxCUI(s) via RxNav. */
async function normalizeToRxcui(name: string): Promise<{ rxcui: string | null; candidates: any }> {
  const j = await getJson(`${RXNAV}/rxcui.json?name=${encodeURIComponent(name)}&search=2`);
  const ids: string[] = j?.idGroup?.rxnormId ?? [];
  if (ids.length) return { rxcui: ids[0], candidates: ids };
  // fallback: approximate match
  const a = await getJson(`${RXNAV}/approximateTerm.json?term=${encodeURIComponent(name)}&maxEntries=3`);
  const cand = a?.approximateGroup?.candidate ?? [];
  return { rxcui: cand[0]?.rxcui ?? null, candidates: cand };
}

/** DailyMed SPL "Drug Interactions" (LOINC 34073-7) section for a drug name, length-bounded. */
async function labelInteractionSection(name: string): Promise<{ setid: string | null; title: string | null; text: string | null }> {
  const list = await getJson(`${DAILYMED}/spls.json?drug_name=${encodeURIComponent(name)}&pagesize=1`);
  const setid: string | undefined = list?.data?.[0]?.setid;
  if (!setid) return { setid: null, title: null, text: null };
  // Optional title lookup. DailyMed's per-SPL resource does not reliably serve JSON (observed
  // HTTP 415 on /spls/{setid}.json) and the title is non-essential — the tool's value is the
  // bounded SPL pointer below. Fetch tolerantly; degrade title to null on any failure.
  let title: string | null = null;
  try {
    const spl = await getJson(`${DAILYMED}/spls/${setid}.json`);
    title = spl?.data?.title ?? null;
  } catch {
    title = null; // 415/non-JSON from DailyMed full-SPL endpoint — pointer below still valid.
  }
  // The full structured body is large; we surface a bounded pointer rather than dumping verbatim.
  return {
    setid,
    title: title ?? null,
    text:
      `Drug Interactions section available in DailyMed SPL setid=${setid}. ` +
      `Retrieve the LOINC 34073-7 section from ` +
      `https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=${setid} ` +
      `(label text is copyright-bounded; do not reproduce in bulk).`,
  };
}

export function buildServer(): McpServer {
  const server = new McpServer({ name: "drugddx-mcp", version: "1.0.0" });

  server.tool(
    "normalize_drug",
    "Normalize an INN or brand drug name to its RxNorm RxCUI (RxNav /rxcui, keyless NIH). " +
      "Read-only. " + CAVEAT,
    { name: z.string().describe("Drug name (INN or brand), e.g. 'warfarin' or 'Coumadin'") },
    async ({ name }) => {
      try {
        const out = await normalizeToRxcui(name);
        return {
          content: [{
            type: "text",
            text: JSON.stringify({ input: name, rxcui: out.rxcui, candidates: out.candidates, caveat: CAVEAT }, null, 2),
          }],
        };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `normalize_drug failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "interaction_label",
    "Return a pointer to the FDA label 'Drug Interactions' section (DailyMed SPL, LOINC 34073-7) " +
      "for a single drug. This is label text, NOT a computed pairwise interaction. Read-only. " + CAVEAT,
    { name: z.string().describe("Drug name (INN or brand) to look up the FDA label interaction section for") },
    async ({ name }) => {
      try {
        const norm = await normalizeToRxcui(name);
        const lbl = await labelInteractionSection(name);
        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              input: name,
              rxcui: norm.rxcui,
              label: lbl,
              clinical_ddi: "NOT PROVIDED — use a licensed source for pairwise interaction verdicts",
              caveat: CAVEAT,
            }, null, 2),
          }],
        };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `interaction_label failed: ${e.message}` }] };
      }
    },
  );

  return server;
}
