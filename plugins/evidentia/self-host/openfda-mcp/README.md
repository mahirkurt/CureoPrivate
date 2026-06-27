# openfda-mcp

Hardened-OAuth Cloudflare Worker MCP (Cureonics Family A) exposing a **single typed tool** over
the FDA **openFDA** API (`api.fda.gov`, keyless public REST).

## Why

evidentia's medical-evidence regulatory needs are **openFDA + ICD-11**. ICD-11 is already served
keyless by the `med-terminologies` connector (`icd11_search`). The broad comparative-legal
connector (Lex-Sanitas) carried ~40 legislation tools that are noise for clinical evidence, so it
was dropped from the roster. This Worker re-expresses **only** the openFDA surface as the typed
tool `openfda_search` — the exact tool name `medical-research` already calls — so no skill change
is needed.

## Tool

`openfda_search(endpoint, search?, count?, limit?, skip?)`

- `endpoint` — allowlisted dataset: `drug/event` (FAERS), `drug/label` (SPL), `drug/drugsfda`
  (approvals), `drug/enforcement` (recalls), `device/*`, `food/*`, … (SSRF-safe allowlist).
- `search` — openFDA Lucene query, e.g. `patient.drug.medicinalproduct:"HUMIRA"`.
- `count` — aggregate by a field (e.g. `patient.reaction.reactionmeddrapt.exact` → FAERS PT
  signal counts) instead of returning records.
- `limit` (1–100, default 5), `skip` (pagination).

**Honest scope:** FAERS/event counts are **spontaneous reports**, NOT incidence/prevalence — never
present a count as a rate. Every result carries this caveat.

## Auth

Family-A hardened OAuth 2.1 (`src/auth.ts`, 6 invariants): redirect-origin allowlist, PKCE
S256-only, escaped HTML, HMAC-signed 10-min codes, constant-time compares, secrets only in the
secret store. `access_token == MCP_API_KEY`.

## Deploy

```bash
npm install && npm run typecheck && npm test
openssl rand -hex 32 | xargs -I{} wrangler secret put MCP_API_KEY      # value entered interactively
openssl rand -hex 16 | xargs -I{} wrangler secret put AUTH_HMAC_SECRET
wrangler deploy
bash scripts/smoke_oauth_public.sh https://openfda-mcp.<subdomain>.workers.dev
```

Smoke expects: `/health` 200 · AS metadata S256-only · `/mcp` 401 without Bearer · 200 with key.
