# Regulatory Intelligence & Epidemiology Layer (v8.0 — NEW)

**Loaded when:** 0.5.C (Regulatory), 0.5.D (HTA), or 0.5.K (Epidemiology/Disease Burden) fires.
**Purpose:** Replace Python-`requests` openFDA + Exa-scraped regulatory/epidemiology with a
**native multi-jurisdiction regulatory MCP** plus WHO epidemiology. Complements (does not
replace) the clinical `regulatory-science-layer.md` and `hta-layer.md` — those keep the
domain logic; this file provides the **verified native data plumbing**.

**Primary connector:** Regulatory MCP (`922d7cdc…`).
**⚠️ Latency warning (probe-observed):** this server can be slow (a parallel call hit a
180 s timeout). **Call its tools singly (not in a parallel burst), allow one retry, and
mark non-critical calls skippable.**

---

## 1. Native openFDA (replaces Python requests)

`openfda_search(endpoint, search, count?, limit?, skip?)` — Lucene/Elasticsearch syntax.

| Endpoint | Use | Example `search` / `count` |
|---|---|---|
| `drug/drugsfda` | FDA approval records (NDA/BLA, approval date, sponsor) | `search='openfda.generic_name:"glofitamab"'` |
| `drug/label` | Structured product labeling (indications, boxed warning, dosing) | `search='openfda.brand_name:"COLUMVI"'` |
| `drug/event` | **FAERS** adverse events (signal counts) | `search='patient.drug.medicinalproduct:"pembrolizumab"'`, `count='patient.reaction.reactionmeddrapt.exact'` |
| `drug/enforcement` | Recalls | `search='product_description:"..."'` |
| `device/*`, `food/*`, `other/nsde` | Device/food/NSDE | as needed |

**FAERS discipline:** counts = **spontaneous reporting**, NOT incidence/prevalence. Always
caveat. For disproportionality (PRR/ROR) compute via `bash_tool` from the count output
(`evidence-grading.md §5 Pattern A`). `count` aggregation returns top PTs directly.

This **removes** the v7.1 `extended-api`/`connector-api` Python openFDA block. Use native
`openfda_search`; fall back to `bash_tool` + `api.fda.gov` only if the MCP stalls.

---

## 2. WHO ICD-11 — indication coding

`icd11_search(query, lang?, release?, limit?)` → MMS entities + codes.
Use for: encoding the indication (regulatory/HTA dossier ICD citation), mapping a Turkish
disease term to a standard code, harmonizing across jurisdictions. Pair with the indication
in CT.gov / TİTCK / EMA records.

---

## 3. WHO GHO — disease burden / epidemiology (axis 0.5.K)

`who_gho_query(indicator?, filter?, limit?)` — OData. Omit `indicator` to list indicators.
**Verified example:** `who_gho_query(indicator="WHOSIS_000001", filter="SpatialDim eq 'TUR'")`
→ Türkiye life-expectancy series 2001–2021 with CIs.

Common indicators: `WHOSIS_000001` (life expectancy), cancer/NCD mortality, immunization,
risk-factor prevalence. Filter by `SpatialDim eq '<ISO3>'` (TUR, USA, DEU…), `TimeDim`,
`Dim1` (SEX). Use for: HTA budget-impact denominators, rare-disease prevalence context,
Türkiye epidemiologic baseline.

**GLOBOCAN/IARC** (cancer incidence/mortality, no native MCP) → Exa `site:gco.iarc.fr`.
**SEER** → Exa `site:seer.cancer.gov`. **TÜİK/Türkiye Kanser İstatistikleri** → Exa
`site:hsgm.saglik.gov.tr OR kanser.gov.tr`.

⚠️ WHO GHO can be slow — single call + retry; if it stalls, proceed with GLOBOCAN/SEER via
Exa and note the substitution.

---

## 4. Multi-jurisdiction regulatory cross-reference

| Source | Tool | Use |
|---|---|---|
| Health Canada DPD | `health_canada_dpd(resource, params)` | DIN/brand/ingredient/ATC — Canadian approval cross-ref |
| US Federal Register | `federal_register_search(query, type?)` | NPRM/Final Rule — regulatory rationale (RIA) |
| EUR-Lex | `eurlex_expert_search(...)` | EU legal acts (EMA framework, orphan regulation) |
| EMA | (no native MCP) → Exa `site:ema.europa.eu` | EPAR, CHMP opinion/minutes, PRIME |
| FDA AdComm | (no native) → Exa `site:fda.gov/advisory-committees` | ODAC/briefing docs (cross-ref AdisInsight `history_events`) |
| TİTCK | **`turkiye-layer.md`** (native) | TR ruhsat/askıya alma/Madde-23 |

---

## 5. How this layer feeds the clinical layers

- **0.5.C Regulatory** (`regulatory-science-layer.md`): native `drugsfda` approval timeline +
  `drug/label` boxed warnings + AdisInsight `history_events` (CRL/ODAC/registration) + EMA
  (Exa) → §13 regulatory trajectory. **Withdrawal pool**: `openfda_search(endpoint="drug/enforcement")`
  + AdisInsight discontinued/withdrawn phases.
- **0.5.D HTA** (`hta-layer.md`): WHO GHO burden + ICD-11 coding → budget-impact denominators;
  NICE/CADTH/IQWiG/HAS via Exa; TİTCK price (native) + Mevzuat SUT (native) → §14.f Türkiye.
- **0.5.K Epidemiology** (output §21): WHO GHO + ICD-11 + GLOBOCAN/SEER/TÜİK → incidence,
  prevalence, mortality, DALY context for any clinical/HTA/rare query.

---

## 6. Output — `epidemiology_payload` sidecar (v8.0)
```json
"epidemiology_payload": {
  "icd11": [{"code":"...","title":"...","release":"2024-01"}],
  "burden": [{"source":"WHO GHO|GLOBOCAN|SEER|TÜİK","indicator":"...","geo":"TUR|GLOBAL","year":0,"value":0,"ci":"...","unit":"per 100k|absolute"}],
  "notes": "FAERS=reporting not incidence; GHO latency-substituted if applicable"
}
```
Plus `regulatory_timeline` (output-templates) populated from native `drugsfda` + AdisInsight
`history_events` + EMA(Exa) + TİTCK(native), each with `verification`.

---

## 7. Known limitations
1. **Latency** — single calls + retry; skippable; substitute Exa epidemiology if GHO stalls.
2. **FAERS ≠ incidence** — always caveat; disproportionality computed, not reported raw.
3. **No native EMA / FDA-AdComm connector** — Exa site-restricted; cross-ref AdisInsight history.
4. **WHO GHO indicator discovery** — list indicators (omit `indicator`) before deep queries.
5. **openFDA `skip+limit ≤ 25000`** — paginate within bounds.

---

*v8.0 — `who_gho_query` verified (Türkiye life-expectancy); `openfda_search`/`icd11_search`/
`health_canada_dpd`/`federal_register_search` schemas verified 9 June 2026. Latency caveat
based on observed 180 s timeout.*
