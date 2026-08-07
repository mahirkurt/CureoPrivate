# who-gho-mcp

Keyless Cloudflare Worker MCP exposing the **WHO Global Health Observatory (GHO)** OData API to the
`evidentia` plugin. Closes evidentia's **global disease-burden gap**: PopHIVE covers the US only, and
GLOBOCAN/IHME have no native API, so before this Worker global/Türkiye burden was a documented
"VERİ YOK" gap. GHO gives country-level (ISO3, incl. `TUR`) and regional/global figures natively.

## Tools

| Tool | Purpose |
|---|---|
| `who_gho_search_indicators(query, limit?)` | Resolve a topic to GHO indicator **codes** (fetches the full Indicator catalogue, case-insensitive substring on name/code). |
| `who_gho_query(indicator_code, country?, year?, dim1?, limit?)` | Fetch data rows for one indicator, filtered by country (`SpatialDim` ISO3 / region / `GLOBAL`), year (`TimeDim`), and/or disaggregation (`Dim1`, e.g. `SEX_BTSX`). |
| `who_gho_dimensions(dimension?, limit?)` | List dimensions, or the allowed values of one dimension (`COUNTRY`→ISO3, `SEX`, `AGEGROUP`, `REGION`). |

Typical flow: `who_gho_search_indicators("life expectancy")` → pick `WHOSIS_000001` →
`who_gho_query("WHOSIS_000001", country="TUR", year=2019)`.

## Auth model — KEYLESS by design

Upstream WHO GHO OData (`https://ghoapi.azureedge.net/api`) is **authless** and this Worker holds
**no server-side secret** → there is no credential to protect and no confused-deputy surface, so
`MCP_ALLOW_NO_AUTH="1"` (drugddx precedent). The hardened OAuth 2.1 + Bearer layer is retained
(additive) so claude.ai/ChatGPT connector flows keep working. To re-gate: set
`MCP_ALLOW_NO_AUTH="0"` and `wrangler secret put MCP_API_KEY` + `AUTH_HMAC_SECRET`, then redeploy.

## Honest scope (no-fabrication)

GHO values mix **modelled estimates** and **reported** data; each row is point-in-time and carries
WHO's own value string (e.g. `"77.6 [77.2-78.1]"`). A missing country/year row means **NO DATA** —
never interpolate or fabricate. Every tool output carries a `caveat`.

## Develop / test / deploy

```bash
npm ci
npm run typecheck            # tsc --noEmit
npm test                     # vitest — server.test (pure OData url/shape helpers) + auth.test
npm run dev                  # wrangler dev (local; hits live GHO upstream)
npm run deploy               # wrangler deploy
BASE=https://who-gho-mcp.<subdomain>.workers.dev ./scripts/smoke_oauth_public.sh
```

> **Test note (2026-08-07 çözüldü):** `routing.test.ts` (tam worker'ı workerd test
> havuzuna import eder) `@cloudflare/vitest-pool-workers@0.8.71`'in CJS shim'inde
> patlıyordu — `ajv/dist/core.js` bir JSON dosyasını `require()` ediyor ve shim onu
> JavaScript sanıp `SyntaxError: Unexpected token ':'` atıyordu. Arıza YEDİ self-host
> Worker'ın hepsini etkiliyordu (49 test hiç koşmuyordu), yalnız dördünü değil.
> Onarım: pool `0.12.21`'e yükseltildi (vitest 3.2 ile uyumlu en yeni sürüm). Artık
> üç paketin tamamı koşuyor ve `npm test` exit=0 veriyor.

## Upstream reference

- API root: `https://ghoapi.azureedge.net/api` (OData v4, authless)
- Indicator catalogue: `GET /Indicator` → `{value:[{IndicatorCode,IndicatorName,Language}]}`
- Data: `GET /{IndicatorCode}?$filter=SpatialDim eq 'TUR' and TimeDim eq 2019&$top=50`
- Dimensions: `GET /Dimension`; values: `GET /DIMENSION/{CODE}/DimensionValues`
