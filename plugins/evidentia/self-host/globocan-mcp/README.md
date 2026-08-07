# globocan-mcp

Keyless Cloudflare Worker MCP exposing **IARC's Global Cancer Observatory (GLOBOCAN 2022)** to the
`evidentia` plugin — global/country cancer **incidence and mortality** estimates for 36 cancer sites
across 185+ countries (incl. Türkiye), with age-standardised rate (ASR), crude rate, cumulative risk,
rank and uncertainty intervals. Live proxy over the authless `gco-api.iarc.fr`. Closes evidentia's
global cancer-burden gap (that PopHIVE — US-only — and who-gho — general GHO — do not cover).

## Tools

| Tool | Purpose |
|---|---|
| `gco_list_cancers()` | The GLOBOCAN cancer sites (id, label, ICD-10). Use `id` as `cancer` in gco_query. |
| `gco_resolve_population(query, limit?)` | Resolve a country/region to its GLOBOCAN code by name or **ISO3** (e.g. `TUR`→792). The data endpoint needs numeric codes. |
| `gco_query(population, cancer?, sex?, type?, limit?)` | Incidence or mortality for a population × cancer(s) × sex, joined with cancer labels; returns total cases/deaths, ASR, crude rate, cumulative risk, rank and uncertainty interval. |

Typical flow: `gco_resolve_population("TUR")` → 792 → `gco_query(population="792", cancer="all", type="incidence")`.

> **Naming note:** GLOBOCAN 2022 labels the country **"Türkiye"** (not "Turkey") — resolve by ISO3
> `TUR` or `792` for reliability. `sex`: both/male/female. `type`: incidence/mortality.

## Auth model — KEYLESS by design

The upstream IARC GLOBOCAN API is **authless and headerless** and this Worker holds **no server-side
secret** → nothing to protect, no confused-deputy surface, so `MCP_ALLOW_NO_AUTH="1"` (who-gho/drugddx
precedent). Hardened OAuth 2.1 + Bearer is retained (additive) for claude.ai/ChatGPT connector flows.
Re-gate: `MCP_ALLOW_NO_AUTH="0"` + `wrangler secret put MCP_API_KEY AUTH_HMAC_SECRET`.

## Honest scope (no-fabrication)

GLOBOCAN figures are **MODELLED ESTIMATES** for reference year 2022 — NOT registry counts;
methodology varies by country data availability (reflected in the `ui` uncertainty interval). Every
output carries a mandatory `caveat`. A population/cancer combination with no row means NO ESTIMATE —
never interpolate or fabricate. ASR = age-standardised rate /100,000 (World standard).

## Develop / test / deploy

```bash
npm ci
npm run typecheck            # tsc --noEmit
npm test                     # vitest — server.test (pure url/join/resolve helpers) + auth.test
npm run dev                  # wrangler dev (local; hits live GCO upstream)
npm run deploy               # wrangler deploy
BASE=https://globocan-mcp.<subdomain>.workers.dev ./scripts/smoke_oauth_public.sh
```

> **Test note (2026-08-07 çözüldü):** `routing.test.ts` (tam worker'ı workerd test
> havuzuna import eder) `@cloudflare/vitest-pool-workers@0.8.71`'in CJS shim'inde
> patlıyordu — `ajv/dist/core.js` bir JSON dosyasını `require()` ediyor ve shim onu
> JavaScript sanıp `SyntaxError: Unexpected token ':'` atıyordu. Arıza YEDİ self-host
> Worker'ın hepsini etkiliyordu (49 test hiç koşmuyordu), yalnız dördünü değil.
> Onarım: pool `0.12.21`'e yükseltildi (vitest 3.2 ile uyumlu en yeni sürüm). Artık
> üç paketin tamamı koşuyor ve `npm test` exit=0 veriyor.

## Upstream reference (endpoints empirically captured 2026-07-05 via the Cancer Today XHR)

- Base: `https://gco-api.iarc.fr/api/globocan/v3/2022` (OData-free JSON, authless, no headers required)
- Cancers: `GET /meta/cancers/all/` → `[{cancer, label, ICD, gender}]`
- Populations: `GET /meta/populations/all/` → `[{country, label, country_iso3, who_label, hdi_label, income_label}]`
- Data: `GET /data/rate/{type}/{sex}/({pop,pop})/{cancer|all}/?include_nmsc=0&include_nmsc_other=1&group_CRC=1&ages_group=0_17`
  - **path order is `{type}/{sex}`** (verified: the returned rows' `type`/`sex` fields match the 1st/2nd slots)
  - `type` 0=incidence 1=mortality 2=prevalence · `sex` 0=both 1=male 2=female
  - → `{dataset:[{country_code, cancer_code, type, sex, prev_time, total, total_pop, asr, crude_rate, cum_risk_74, rank, ui:{low,high}}]}`
  - prevalence (type=2) returns 3 rows/cancer (`prev_time` = 1/3/5-year); incidence/mortality → 1 row/cancer (`prev_time`=null)
