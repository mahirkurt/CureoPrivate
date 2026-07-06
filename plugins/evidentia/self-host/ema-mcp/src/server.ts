/**
 * server.ts — ema-mcp tool layer (Cureonics self-host, evidentia Tier-O).
 *
 * Serves the EMA "Medicines" dataset (European Public Assessment Reports + status of opinions) —
 * every EU centrally-authorised medicine with its authorisation status, CHMP opinion/decision
 * dates, regulatory flags (orphan / conditional / accelerated / PRIME / advanced-therapy /
 * biosimilar / generic), ATC, INN, MAH, therapeutic indication and a link to the full EPAR page.
 * This closes evidentia's EMA/CHMP-EPAR gap (previously "no native API → documented gap").
 *
 *   ema_search_medicines — free-text search across name / INN / active substance / ATC / indication.
 *   ema_get_medicine     — one full record by exact name or EMA product number.
 *   ema_filter           — structured regulatory query (ATC prefix + status + flags + category).
 *   ema_stats            — corpus overview (counts by status/category + the source freshness stamp).
 *
 * BAKED CORPUS — served from src/data.gen.ts (built by scripts/build_corpus.mjs from the authless
 * EMA XLSX). No runtime upstream call, no secret. Point-in-time: every output carries the
 * generated_at stamp + a caveat. A medicine absent from the corpus means NOT in this snapshot —
 * not proof it does not exist; never fabricate. Full assessment text lives at the EPAR `url`
 * (fetch/ingest on demand).
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { EMA_MEDICINES, EMA_GENERATED_AT, EMA_SOURCE_URL, type EmaMedicine } from "./data.gen.js";

const CAVEAT =
  `EMA Medicines dataset (European Public Assessment Reports + status of opinions), baked snapshot ` +
  `generated_at=${EMA_GENERATED_AT} from ${EMA_SOURCE_URL} (authless, refreshed overnight upstream). ` +
  `Point-in-time: status/dates are as of the snapshot. A medicine absent from this snapshot is NOT ` +
  `proof of non-existence. Full assessment text is at the EPAR 'url' (not included here). Not medical advice.`;

const FLAG_KEYS = ["accelerated", "additional_monitoring", "advanced_therapy", "biosimilar", "conditional", "exceptional", "generic", "orphan", "prime"] as const;

function lc(s: string | null | undefined): string {
  return (s ?? "").toLowerCase();
}

// Compact projection for list results (keeps responses small; full record via ema_get_medicine).
function brief(m: EmaMedicine) {
  return {
    name: m.name, category: m.category, status: m.status, opinion_status: m.opinion_status,
    inn: m.inn, atc: m.atc, orphan: m.orphan, conditional: m.conditional, accelerated: m.accelerated,
    prime: m.prime, biosimilar: m.biosimilar, opinion_date: m.opinion_date, ma_date: m.ma_date,
    product_number: m.product_number, url: m.url,
  };
}

export function registerTools(server: McpServer): void {
  server.tool(
    "ema_search_medicines",
    "Free-text search the EMA Medicines dataset across medicine name, INN/common name, active " +
      "substance, ATC code and therapeutic indication (case-insensitive substring). Returns compact " +
      "records; use ema_get_medicine for the full record. " + CAVEAT,
    {
      query: z.string().describe("Search term, e.g. 'pembrolizumab', 'Keytruda', 'multiple myeloma', 'L01FF'"),
      category: z.enum(["Human", "Veterinary"]).optional().describe("Restrict to Human or Veterinary medicines"),
      status: z.string().optional().describe("Restrict to an authorisation status, e.g. 'Authorised', 'Withdrawn', 'Refused'"),
      limit: z.number().int().min(1).max(100).optional().describe("Max results (1-100, default 25)"),
    },
    async ({ query, category, status, limit }) => {
      const q = query.trim().toLowerCase();
      const cap = limit ?? 25;
      const hits: EmaMedicine[] = [];
      for (const m of EMA_MEDICINES) {
        if (category && m.category !== category) continue;
        if (status && lc(m.status) !== lc(status)) continue;
        if (
          q === "" ||
          lc(m.name).includes(q) || lc(m.inn).includes(q) || lc(m.active_substance).includes(q) ||
          lc(m.atc).includes(q) || lc(m.indication).includes(q)
        ) {
          hits.push(m);
          if (hits.length >= cap) break;
        }
      }
      return { content: [{ type: "text", text: JSON.stringify({ query, total: hits.length, medicines: hits.map(brief), caveat: CAVEAT }, null, 2) }] };
    },
  );

  server.tool(
    "ema_get_medicine",
    "Fetch ONE full EMA medicine record by exact medicine name or EMA product number. Returns every " +
      "field incl. CHMP opinion/decision dates, all regulatory flags, indication and the EPAR URL. " + CAVEAT,
    {
      identifier: z.string().describe("Exact medicine name (e.g. 'Keytruda') or EMA product number (e.g. 'EMEA/H/C/003820')"),
    },
    async ({ identifier }) => {
      const id = identifier.trim().toLowerCase();
      const m = EMA_MEDICINES.find((x) => lc(x.name) === id || lc(x.product_number) === id);
      if (!m) {
        return { content: [{ type: "text", text: JSON.stringify({ identifier, found: false, note: "No medicine with that exact name/product number in this snapshot (try ema_search_medicines).", caveat: CAVEAT }, null, 2) }] };
      }
      return { content: [{ type: "text", text: JSON.stringify({ found: true, medicine: m, caveat: CAVEAT }, null, 2) }] };
    },
  );

  server.tool(
    "ema_filter",
    "Structured regulatory query over the EMA Medicines dataset: filter by ATC prefix, authorisation " +
      "status, category and any regulatory flags (orphan / conditional / accelerated / PRIME / " +
      "advanced_therapy / biosimilar / generic / additional_monitoring / exceptional). All conditions " +
      "AND together. Use for e.g. 'all authorised orphan oncology (L01) medicines'. " + CAVEAT,
    {
      atc_prefix: z.string().optional().describe("ATC code prefix, e.g. 'L01' (antineoplastics), 'J05' (antivirals)"),
      status: z.string().optional().describe("Authorisation status, e.g. 'Authorised', 'Withdrawn', 'Refused', 'Suspended'"),
      category: z.enum(["Human", "Veterinary"]).optional().describe("Human or Veterinary"),
      orphan: z.boolean().optional().describe("Orphan medicine flag"),
      conditional: z.boolean().optional().describe("Conditional approval flag"),
      accelerated: z.boolean().optional().describe("Accelerated assessment flag"),
      prime: z.boolean().optional().describe("PRIME priority medicine flag"),
      advanced_therapy: z.boolean().optional().describe("Advanced therapy (ATMP) flag"),
      biosimilar: z.boolean().optional().describe("Biosimilar flag"),
      additional_monitoring: z.boolean().optional().describe("Additional monitoring (black triangle) flag"),
      limit: z.number().int().min(1).max(200).optional().describe("Max results (1-200, default 50)"),
    },
    async (args) => {
      const { atc_prefix, status, category, limit } = args;
      const cap = limit ?? 50;
      const atc = atc_prefix ? atc_prefix.trim().toUpperCase() : null;
      const hits: EmaMedicine[] = [];
      for (const m of EMA_MEDICINES) {
        if (atc && !(m.atc ?? "").toUpperCase().startsWith(atc)) continue;
        if (status && lc(m.status) !== lc(status)) continue;
        if (category && m.category !== category) continue;
        let flagOk = true;
        for (const k of FLAG_KEYS) {
          const want = (args as Record<string, unknown>)[k];
          if (typeof want === "boolean" && (m as unknown as Record<string, boolean>)[k] !== want) { flagOk = false; break; }
        }
        if (!flagOk) continue;
        hits.push(m);
        if (hits.length >= cap) break;
      }
      const applied = { atc_prefix: atc, status: status ?? null, category: category ?? null, ...Object.fromEntries(FLAG_KEYS.map((k) => [k, (args as Record<string, unknown>)[k] ?? null]).filter(([, v]) => v !== null)) };
      return { content: [{ type: "text", text: JSON.stringify({ filter: applied, total: hits.length, medicines: hits.map(brief), caveat: CAVEAT }, null, 2) }] };
    },
  );

  server.tool(
    "ema_stats",
    "Overview of the baked EMA Medicines corpus: total medicines, breakdown by category and " +
      "authorisation status, and the snapshot freshness stamp. Use to gauge coverage before querying. " + CAVEAT,
    {},
    async () => {
      const byStatus: Record<string, number> = {};
      const byCategory: Record<string, number> = {};
      let orphan = 0, conditional = 0, prime = 0;
      for (const m of EMA_MEDICINES) {
        byStatus[m.status ?? "?"] = (byStatus[m.status ?? "?"] ?? 0) + 1;
        byCategory[m.category ?? "?"] = (byCategory[m.category ?? "?"] ?? 0) + 1;
        if (m.orphan) orphan++;
        if (m.conditional) conditional++;
        if (m.prime) prime++;
      }
      return { content: [{ type: "text", text: JSON.stringify({ total: EMA_MEDICINES.length, generated_at: EMA_GENERATED_AT, source_url: EMA_SOURCE_URL, by_category: byCategory, by_status: byStatus, flags: { orphan, conditional, prime }, caveat: CAVEAT }, null, 2) }] };
    },
  );
}

export const __testing = { brief, lc, CAVEAT };
