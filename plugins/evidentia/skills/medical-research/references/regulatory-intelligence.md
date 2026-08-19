# Regulatory Intelligence & Epidemiology Layer (v8.0; refocused v8.5)

**Optional enrichment module** — loaded only when the question's context calls for regulatory
data. NOT mandatory; the core PRISMA pipeline (P0–P7) runs without it. Output → enrichment
appendix.
**Purpose:** Provide the **verified native data plumbing** for the regulatory + epidemiology
dimensions. Complements (does not replace) the clinical `regulatory-science-layer.md` and
`hta-layer.md` — those keep the domain logic; this file wires the connectors.

**Primary connector:** **`openfda`** (self-host Tier-O, `openfda-mcp.cureonics.workers.dev`) —
**D-α (v8.5):** replaces the legacy "Regulatory MCP `922d7cdc`". It serves **openFDA** +
**WHO ICD-11** only. **+ `PopHIVE`** (Tier-K-epi, US surveillance) for axis 0.5.K.
**⚠️ openfda latency:** call its tools **singly** (not in a parallel burst), allow **one retry**,
mark non-critical calls **skippable**.

> **No web tier (v1.4.0).** Exa/Tavily were removed. Every "Exa `site:…`" path that this layer
> used in v8.0 is now a **documented gap (VERİ YOK)** — reported honestly with the queries
> attempted, **never web-scraped or fabricated** (DEĞİŞMEZ 1).

---

## 1. Native openFDA

`openfda_search(endpoint, search, count?, limit?, skip?)` — Lucene/Elasticsearch syntax.

| Endpoint | Use | Example `search` / `count` |
|---|---|---|
| `drug/drugsfda` | FDA approval records (NDA/BLA, approval date, sponsor) | `search='openfda.generic_name:"glofitamab"'` |
| `drug/label` | Structured product labeling (indications, boxed warning, dosing) | `search='openfda.brand_name:"COLUMVI"'` |
| `drug/event` | **FAERS** adverse events (signal counts) | `search='patient.drug.openfda.generic_name:"imatinib"'`, `count='patient.reaction.reactionmeddrapt.exact'` |
| `drug/enforcement` | Recalls | `search='product_description:"..."'` |
| `device/*` | Device data | as needed |

**FAERS discipline:** counts = **spontaneous reporting**, NOT incidence/prevalence. Always
caveat. For disproportionality (PRR/ROR) compute via `bash_tool` from the count output
(`evidence-grading.md §5 Pattern A`). `count` aggregation returns top PTs directly.
*(Probe-verified 2026-06-28: `openfda_search(drug/event, imatinib, count=…)` → DEATH/NAUSEA/… PT counts.)*

Use native `openfda_search`; fall back to `bash_tool` + `api.fda.gov` only if the MCP stalls.

---

## 2. WHO ICD-11 — indication coding (the authoritative ICD-11 source)

`openfda:icd11_search(query, release?, limit?)` → MMS entities + codes (server-side OAuth, keyless to caller).
Use for: encoding the indication (regulatory/HTA dossier ICD citation), mapping a disease term to a
standard code, harmonizing across jurisdictions. Pair with the indication in CT.gov / TİTCK records.
**ICD-11:** `openfda.icd11_search` is the operator-owned path. D6 (`med-terminologies.icd11_search`
AUTH) was retired 2026-08-17 after a live 3B10.0 hit — that tool is allowed again. For authoritative
ICD-10→ICD-11 *crosswalk* use `med-terminologies:map_icd10_to_icd11` (WHO 2025-01 transition tables).
*(Probe-verified 2026-06-28: `icd11_search("type 2 diabetes mellitus")` → 5A11, WHO ICD-11 MMS 2024-01.)*

---

## 3. Epidemiology / disease burden (axis 0.5.K)

### 3.1 US surveillance — `PopHIVE` (native, Tier-K-epi · v8.5 NEW)
`PopHIVE` (Yale, `mcp.pophive.org`, DOI 10.5281/zenodo.17345935) — **harmonized US aggregate
surveillance** (ED visits, hospitalizations, wastewater, lab positivity, search trends, vaccination
coverage). **De-identified, aggregate, public** — answer directly, no PII/medical-advice refusal.

| Tool | Use |
|---|---|
| `get_current_status(disease, geography?)` | Level / direction / risk **now** for one disease × one US place |
| `get_trend(disease, geography?)` | Time series for one slice |
| `get_map(disease)` | Geographic ranking across US states/counties |
| `get_coverage(disease)` | **Childhood vaccination coverage** (MMR/DTaP/polio/…); exemptions |
| `compare(...)` | A-vs-B across source / place |
| `get_data(disease?, view?)` | Catalog + raw-parquet gateway for custom cross-stratum analysis |

**Discipline (binding):** **relay PopHIVE's precomputed evidence verbatim — never re-derive the
numbers.** Lead with the result's `answer`/`headline`; every value must appear in the tool result.
Carry the `caveats` (preliminary periods, suppression). *(Probe-verified 2026-06-28:
`get_current_status(rsv, Connecticut)` → "minimal & declining", 6-source verdict.)*

### 3.2 Global & Türkiye burden — native who-gho / globocan (IHME still gap)

**WHO-GHO** (`who-gho:who_gho_query`, country ISO3/`GLOBAL`) and **GLOBOCAN** (`globocan:gco_query`)
are **native** — not a documented gap. Values are modelled+reported (GHO) or modelled estimates
with `ui` (GLOBOCAN 2022) → carry the connector `caveat`. **SEER / IHME/GBD** still have **no
native MCP → documented gap (VERİ YOK)**, never web-scraped. **PopHIVE is US-ONLY — do NOT present
it as covering Türkiye or global burden.** Order: `execution-map.md` P7.

- **Türkiye epidemiology** → **who-gho** (`country=TUR`) + **globocan** (if cancer; `TUR`=792) +
  **TİTCK** (`turkiye-layer.md`) + **EPMC `AFF:"Turkey"`** + **YÖK Tez**.
- If the operator supplies a burden PDF (TÜİK/Kanser İstatistikleri), it can be **ingested into
  anamnesis** (`ingest_document`, exclusive-run collection) for analysis — but it is not auto-fetched.

---

## 4. Multi-jurisdiction regulatory cross-reference

| Source | Status | Use |
|---|---|---|
| US FDA (approvals/labels/FAERS/recalls) | **native** `openfda:openfda_search` | drugsfda / label / event / enforcement |
| WHO ICD-11 | **native** `openfda:icd11_search` | indication coding |
| Health Canada DPD | **no native API** (not bundled in openfda; legacy Regulatory MCP removed) → **documented gap** | DIN/brand cross-ref → report gap; cross-check via DailyMed/label if a US equivalent exists |
| US Federal Register | **no native API** → **documented gap** | NPRM/Final Rule rationale → report gap |
| EUR-Lex | **no native API** → **documented gap** | EU legal acts → report gap (operator's standalone Cureolex connector if needed) |
| EMA (EPAR/CHMP) | **no native API** → **documented gap** | EPAR/CHMP opinion → report gap; cross-ref AdisInsight `history_events` |
| FDA AdComm (ODAC) | **no native API** → **documented gap** | briefing docs → cross-ref AdisInsight `history_events` |
| TİTCK | **`turkiye-layer.md`** (native) | TR ruhsat / askıya alma / Madde-23 |

> **D-α note:** `health_canada_dpd` / `federal_register_search` / `eurlex_expert_search`
> were tools of the **removed** legacy Regulatory MCP. They are **not** in the `openfda` Worker →
> documented gap. `who_gho_query` now lives on **`who-gho`**. No web fallback.

---

## 5. How this layer feeds the clinical layers

- **0.5.C Regulatory** (`regulatory-science-layer.md`): native `drugsfda` approval timeline +
  `drug/label` boxed warnings + AdisInsight `history_events` (CRL/ODAC/registration) → enrichment
  appendix regulatory trajectory. **Withdrawal pool**: `openfda_search(endpoint="drug/enforcement")` +
  AdisInsight discontinued/withdrawn phases. *(EMA EPAR/CHMP → native `ema`; cross-ref AdisInsight
  history.)*
- **0.5.D HTA** (`hta-layer.md`): ICD-11 coding (denominators) + **PopHIVE US burden/coverage** where
  US-relevant → budget-impact context; TİTCK price (native) → enrichment
  appendix Türkiye note. *(NICE/CADTH/IQWiG/HAS have no native API → documented gap; do not web-scrape.)*
- **0.5.K Epidemiology** (output → enrichment appendix): ICD-11 (`openfda` **and**
  `med-terminologies.icd11_search`, D6 ALLOW) + **PopHIVE (US)** + **who-gho** (global/`TUR`) +
  **globocan** (cancer). IHME/GBD = documented gap. TR literature substitutes: EPMC AFF:Turkey + YÖK Tez.

---

## 6. Output — `epidemiology_payload` sidecar (v8.0; PopHIVE v8.5)
```json
"epidemiology_payload": {
  "icd11": [{"code":"...","title":"...","release":"2024-01"}],
  "us_surveillance": [{"source":"PopHIVE","signal":"ED visits|hospitalizations|wastewater|coverage","disease":"...","geo":"US|<state>","period":"...","value":0,"direction":"rising|declining|stable","verbatim":"<answer/headline>"}],
  "burden_gap": [{"need":"SEER|IHME/GBD|Türkiye registry prevalence","status":"documented_gap","queries_attempted":["..."],"native_used":"who-gho|globocan|TİTCK|EPMC AFF:Turkey|YÖK Tez"}],
  "notes": "FAERS=reporting not incidence; PopHIVE=US-only aggregate (relayed, not re-derived); who-gho/globocan native (modelled + caveat); IHME still gap"
}
```
Plus `regulatory_timeline` (output-templates) populated from native `drugsfda` + AdisInsight
`history_events` + **`ema`** (CHMP/EPAR URL) + TİTCK(native), each with `verification`. FDA-AdComm
entries without AdisInsight history marked `documented_gap`.

---

## 7. Known limitations
1. **openfda latency** — single calls + 1 retry; skippable; leave `regulatory_snapshot` partial (note it).
2. **FAERS ≠ incidence** — always caveat; disproportionality computed, not reported raw.
3. **No native FDA-AdComm / Health-Canada / Federal-Register / EUR-Lex connector** → **documented
   gap** (web tier removed); EMA CHMP/EPAR → **`ema`** (native). Cross-ref AdisInsight history where possible.
4. **PopHIVE is US-only & precomputed** — relay its evidence verbatim, never re-derive; do not extend to
   Türkiye/global. Global/TR burden → **who-gho** + **globocan** (cancer); IHME/GBD still documented gap.
5. **ICD-11 text search → `med-terminologies:icd11_search` (D6 ALLOW) and/or `openfda:icd11_search`**;
   ICD-10→11 crosswalk → `med-terminologies:map_icd10_to_icd11`.
6. **openFDA `skip+limit ≤ 25000`** — paginate within bounds.

---

*v8.0 baseline (`openfda_search`/`icd11_search` verified 9 June 2026). **v8.5 refocus (2026-06-28):**
legacy Regulatory MCP → `openfda` (D-α); Exa epidemiology/regulatory paths → documented gap; **PopHIVE
wired for US surveillance** (US-only). Probe evidence: `connector-registry.md §8`.*
