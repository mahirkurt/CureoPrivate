#!/usr/bin/env node
/**
 * build_corpus.mjs — download the EMA "Medicines" report (authless XLSX, refreshed overnight) and
 * bake it into src/data.gen.ts as a compact typed array. Re-run to refresh.
 *
 *   node scripts/build_corpus.mjs                       # download live + write src/data.gen.ts
 *   EMA_XLSX=/tmp/ema_current.xlsx node scripts/build_corpus.mjs   # use a local copy
 *
 * The Worker never parses XLSX at runtime — it serves from this baked artifact (mufredat pattern).
 * Source: https://www.ema.europa.eu/en/medicines/download-medicine-data  (canonical "Medicines" table).
 */
import * as XLSX from "xlsx";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, "..", "src", "data.gen.ts");
const SRC_URL =
  "https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx";

const nrm = (s) => String(s).replace(/\s+/g, " ").trim();

// Normalized EMA column name -> compact key. Only the columns evidentia needs.
const COLS = {
  "Category": "category",
  "Name of medicine": "name",
  "EMA product number": "product_number",
  "Medicine status": "status",
  "Opinion status": "opinion_status",
  "International non-proprietary name (INN) / common name": "inn",
  "Active substance": "active_substance",
  "Therapeutic area (MeSH)": "therapeutic_area",
  "Species (veterinary)": "species",
  "ATC code (human)": "atc",
  "ATCvet code (veterinary)": "atcvet",
  "Pharmacotherapeutic group (human)": "atc_group",
  "Therapeutic indication": "indication",
  "Accelerated assessment": "accelerated",
  "Additional monitoring": "additional_monitoring",
  "Advanced therapy": "advanced_therapy",
  "Biosimilar": "biosimilar",
  "Conditional approval": "conditional",
  "Exceptional circumstances": "exceptional",
  "Generic": "generic",
  "Orphan medicine": "orphan",
  "PRIME: priority medicine": "prime",
  "Marketing authorisation developer / applicant / holder": "mah",
  "European Commission decision date": "decision_date",
  "Start of rolling review date": "rolling_review_date",
  "Start of evaluation date": "evaluation_start_date",
  "Opinion adopted date": "opinion_date",
  "Marketing authorisation date": "ma_date",
  "Refusal of marketing authorisation date": "refusal_date",
  "First published date": "first_published",
  "Last updated date": "last_updated",
  "Medicine URL": "url",
};

const FLAGS = new Set(["accelerated", "additional_monitoring", "advanced_therapy", "biosimilar", "conditional", "exceptional", "generic", "orphan", "prime"]);
const DATES = new Set(["decision_date", "rolling_review_date", "evaluation_start_date", "opinion_date", "ma_date", "refusal_date", "first_published", "last_updated"]);

function norm(v) {
  if (v == null) return null;
  const s = String(v).trim();
  return s === "" ? null : s;
}
function flag(v) {
  return (norm(v) || "").toLowerCase() === "yes";
}
// EMA dates are DD/MM/YYYY (optionally " - HH:MM"). Convert to ISO YYYY-MM-DD; pass through anything else.
function euDate(v) {
  const s = norm(v);
  if (!s) return null;
  const m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})/);
  return m ? `${m[3]}-${m[2]}-${m[1]}` : s;
}

async function main() {
  let buf;
  if (process.env.EMA_XLSX) {
    buf = readFileSync(process.env.EMA_XLSX);
    console.error(`[build] using local ${process.env.EMA_XLSX} (${buf.length} bytes)`);
  } else {
    console.error(`[build] downloading ${SRC_URL}`);
    const r = await fetch(SRC_URL, { headers: { "user-agent": "ema-mcp-build/1.0 (+https://cureonics.com)" } });
    if (!r.ok) throw new Error(`EMA XLSX download ${r.status}`);
    buf = Buffer.from(await r.arrayBuffer());
    console.error(`[build] downloaded ${buf.length} bytes`);
  }

  const wb = XLSX.read(buf, { type: "buffer" });
  const ws = wb.Sheets[wb.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1, blankrows: false, raw: false });
  const hIdx = rows.findIndex((r) => Array.isArray(r) && r.some((c) => nrm(c) === "Name of medicine"));
  if (hIdx < 0) throw new Error("header row ('Name of medicine') not found");
  const header = rows[hIdx].map(nrm);
  const colIdx = {};
  for (const [emaName, key] of Object.entries(COLS)) {
    const i = header.indexOf(emaName);
    if (i >= 0) colIdx[key] = i;
    else console.error(`[build] WARN column not found: "${emaName}"`);
  }
  const nameI = colIdx.name;
  const out = [];
  for (const r of rows.slice(hIdx + 1)) {
    if (!r || !norm(r[nameI])) continue;
    const rec = {};
    for (const [key, i] of Object.entries(colIdx)) {
      const raw = r[i];
      if (FLAGS.has(key)) rec[key] = flag(raw);
      else if (DATES.has(key)) rec[key] = euDate(raw);
      else rec[key] = norm(raw);
    }
    out.push(rec);
  }

  // Generation timestamp from the sheet's own header banner ("... generated from content ... on: <ts>").
  let genAt = null;
  for (const r of rows.slice(0, hIdx)) {
    if (Array.isArray(r)) {
      const gi = r.findIndex((c) => String(c).toLowerCase().includes("generated from content"));
      if (gi >= 0 && r[gi + 1]) { genAt = norm(r[gi + 1]); break; }
    }
  }
  const stamp = genAt || "unknown";

  const banner =
    "// AUTO-GENERATED by scripts/build_corpus.mjs — DO NOT EDIT.\n" +
    "// Source: EMA Medicines report (authless XLSX, refreshed overnight). Re-run to refresh.\n";
  const body =
    `export const EMA_GENERATED_AT = ${JSON.stringify(stamp)};\n` +
    `export const EMA_SOURCE_URL = ${JSON.stringify(SRC_URL)};\n` +
    `export interface EmaMedicine {\n` +
    `  category: string | null; name: string | null; product_number: string | null;\n` +
    `  status: string | null; opinion_status: string | null; inn: string | null;\n` +
    `  active_substance: string | null; therapeutic_area: string | null; species: string | null;\n` +
    `  atc: string | null; atcvet: string | null; atc_group: string | null; indication: string | null;\n` +
    `  accelerated: boolean; additional_monitoring: boolean; advanced_therapy: boolean;\n` +
    `  biosimilar: boolean; conditional: boolean; exceptional: boolean; generic: boolean;\n` +
    `  orphan: boolean; prime: boolean; mah: string | null;\n` +
    `  decision_date: string | null; rolling_review_date: string | null; evaluation_start_date: string | null;\n` +
    `  opinion_date: string | null; ma_date: string | null; refusal_date: string | null;\n` +
    `  first_published: string | null; last_updated: string | null; url: string | null;\n` +
    `}\n` +
    `// Data is embedded as a JSON string and parsed at module load — this keeps TypeScript from\n` +
    `// analysing thousands of object literals (TS2590 'union type too complex'); the JSON.parse\n` +
    `// runs once per isolate at cold start (~ms).\n` +
    `export const EMA_MEDICINES: EmaMedicine[] = JSON.parse(${JSON.stringify(JSON.stringify(out))});\n`;

  writeFileSync(OUT, banner + body);
  const human = out.filter((m) => m.category === "Human").length;
  const authorised = out.filter((m) => m.status === "Authorised").length;
  console.error(`[build] wrote ${OUT}: ${out.length} medicines (${human} human, ${out.length - human} vet; ${authorised} authorised), generated_at=${stamp}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
