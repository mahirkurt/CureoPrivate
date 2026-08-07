# globocan-mcp

Keyless Cloudflare Worker MCP exposing **IARC's Global Cancer Observatory (GLOBOCAN 2022)** to the
`evidentia` plugin — global/country cancer **incidence and mortality** estimates for 41 cancer sites (measured 2026-08-07)
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

> **Test note (toolchain, 2026-08-07):** `npm test` runs on **vitest 4 +
> `@cloudflare/vitest-pool-workers` 0.20 + `@cloudflare/workers-types` 5 + wrangler 4.120**.
> Two migrations landed the same day: (1) pool 0.8.71 could not `require()` a JSON file
> (`ajv/dist/core.js`), which killed `routing.test.ts` in ALL SEVEN Workers -- 49 tests never
> ran; (2) pool 0.20 removed the `/config` subpath export, so `vitest.config.ts` now registers
> the pool as a **Vite plugin** (`cloudflareTest`) instead of `test.poolOptions.workers`.
> Known upstream noise: `@modelcontextprotocol/sdk` ships sourcemaps referencing unpublished
> sources, so each run prints ~26 "points to missing source files" lines. Measured: a Vite
> `customLogger` does NOT intercept them (they come from inside the workerd isolate), so they
> are left visible rather than fake-fixed. Suites pass, exit 0.

## Upstream reference (endpoints empirically captured 2026-07-05 via the Cancer Today XHR)

- Base: `https://gco-api.iarc.fr/api/globocan/v3/2022` (OData-free JSON, authless, no headers required)
- Cancers: `GET /meta/cancers/all/` → `[{cancer, label, ICD, gender}]`
- Populations: `GET /meta/populations/all/` → `[{country, label, country_iso3, who_label, hdi_label, income_label}]`
- Data: `GET /data/rate/{type}/{sex}/({pop,pop})/{cancer|all}/?include_nmsc=0&include_nmsc_other=1&group_CRC=1&ages_group=0_17`
  - **path order is `{type}/{sex}`** (verified: the returned rows' `type`/`sex` fields match the 1st/2nd slots)
  - `type` 0=incidence 1=mortality 2=prevalence · `sex` 0=both 1=male 2=female
  - → `{dataset:[{country_code, cancer_code, type, sex, prev_time, total, total_pop, asr, crude_rate, cum_risk_74, rank, ui:{low,high}}]}`
  - prevalence (type=2) returns 3 rows/cancer (`prev_time` = 1/3/5-year); incidence/mortality → 1 row/cancer (`prev_time`=null)
