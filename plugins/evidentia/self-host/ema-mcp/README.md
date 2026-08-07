# ema-mcp

Keyless Cloudflare Worker MCP exposing the **EMA "Medicines"** dataset (European Public Assessment
Reports + status of opinions) to the `evidentia` plugin. Closes evidentia's **EMA/CHMP-EPAR gap**
(previously "no native API → documented gap"). Every EU centrally-authorised medicine with its
authorisation status, CHMP opinion/decision dates, regulatory flags, ATC, INN, MAH, therapeutic
indication and a link to the full EPAR page.

## Tools

| Tool | Purpose |
|---|---|
| `ema_search_medicines(query, category?, status?, limit?)` | Free-text search across name / INN / active substance / ATC / indication. |
| `ema_get_medicine(identifier)` | One full record by exact medicine name or EMA product number. |
| `ema_filter(atc_prefix?, status?, category?, orphan?, conditional?, accelerated?, prime?, advanced_therapy?, biosimilar?, additional_monitoring?, limit?)` | Structured regulatory query (all conditions AND). e.g. "authorised orphan L01 oncology". |
| `ema_stats()` | Corpus overview: counts by category/status + freshness stamp. |

## Data model — BAKED CORPUS

Served from `src/data.gen.ts`, built by `scripts/build_corpus.mjs` from the **authless EMA XLSX**
(`medicines-output-medicines-report_en.xlsx`, refreshed overnight upstream). ~2,700 medicines
(~2,300 human + ~390 veterinary), 30+ fields incl. CHMP `opinion_date`, `decision_date`, all
regulatory flags (orphan / conditional / accelerated / PRIME / advanced-therapy / biosimilar /
generic), lifecycle `status` (Authorised / Withdrawn / Refused / Suspended / Lapsed …), ATC, INN,
MAH, `indication`, and the EPAR `url`. Dates normalised DD/MM/YYYY → ISO.

**The Worker never parses XLSX at runtime** — it serves from the baked artifact (mufredat pattern).
To refresh: `npm run build:corpus` (downloads live) then `npm run deploy`.

## Auth model — KEYLESS by design

A baked public dataset with no runtime upstream call and no server-side secret → nothing to protect,
no confused-deputy surface, so `MCP_ALLOW_NO_AUTH="1"` (drugddx precedent). Hardened OAuth 2.1 +
Bearer is retained (additive) for claude.ai/ChatGPT connector flows. Re-gate: set
`MCP_ALLOW_NO_AUTH="0"` + `wrangler secret put MCP_API_KEY AUTH_HMAC_SECRET`.

## Honest scope (no-fabrication)

Point-in-time snapshot — every output carries the `generated_at` stamp + a `caveat`. A medicine
absent from the snapshot means NOT in this snapshot, not proof of non-existence. Full assessment
text is at the EPAR `url` (fetch/ingest on demand — e.g. into anamnesis). Not medical advice.

## Develop / test / deploy

```bash
npm ci
npm run build:corpus         # download EMA XLSX -> src/data.gen.ts (refresh)
npm run typecheck            # tsc --noEmit
npm test                     # vitest — server.test (corpus integrity + helpers) + auth.test
npm run deploy               # wrangler deploy
BASE=https://ema-mcp.<subdomain>.workers.dev ./scripts/smoke_oauth_public.sh
```

> **Test note (2026-08-07 çözüldü):** `routing.test.ts` (tam worker'ı workerd test
> havuzuna import eder) `@cloudflare/vitest-pool-workers@0.8.71`'in CJS shim'inde
> patlıyordu — `ajv/dist/core.js` bir JSON dosyasını `require()` ediyor ve shim onu
> JavaScript sanıp `SyntaxError: Unexpected token ':'` atıyordu. Arıza YEDİ self-host
> Worker'ın hepsini etkiliyordu (49 test hiç koşmuyordu), yalnız dördünü değil.
> Onarım: pool `0.12.21`'e yükseltildi (vitest 3.2 ile uyumlu en yeni sürüm). Artık
> üç paketin tamamı koşuyor ve `npm test` exit=0 veriyor.

## Upstream reference

- Download page: `https://www.ema.europa.eu/en/medicines/download-medicine-data` (updated overnight)
- Canonical table: `…/documents/report/medicines-output-medicines-report_en.xlsx` (authless XLSX)
- Related EMA tables (future): post-authorisation, referrals, orphan designations, shortages, DHPC.
