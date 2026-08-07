# Certification — evidentia gap-closing connectors (who-gho · globocan · ema)

**Date:** 2026-07-05 · **Verdict:** ✅ **CERTIFIED** (all components PASS; every confirmed finding
remediated and re-verified) · **Scope:** the three self-host MCP connectors built to close
evidentia's documented WHO-GHO / GLOBOCAN / EMA gaps, plus their roster/doc wiring, plus the
reader-MCP extraction-quality work (annas-reader-mcp, openathens-mcp).

Certification method: adversarial multi-dimension audit — live end-to-end tool exercise + **cross-
validation against the authoritative upstream** + security/keyless review + doc-consistency gates +
build/test verification. Findings were adversarially verified before being accepted, and every
confirmed defect was fixed and re-tested against ground truth.

---

## Component verdicts

| Component | Status | Basis |
|---|---|---|
| **globocan-mcp** | ✅ PASS *(after critical fix)* | Sex/type path-order bug **found, fixed, re-verified against published Türkiye figures** |
| **who-gho-mcp** | ✅ PASS | Exact upstream match; SSRF nit hardened |
| **ema-mcp** | ✅ PASS | AND-semantics, honest-absence, corpus↔stats cross-validation all exact |
| **security (3 workers)** | ✅ PASS | auth.ts byte-identical ×4; keyless justified; OAuth S256; SSRF closed |
| **docs / roster consistency** | ✅ PASS | G-BUNDLE consistent; gap-lines correct; wrong-value claims corrected |
| **tests / build** | ✅ PASS | typecheck + unit suites green; the `ajv` routing.test failure is environmental |
| **annas + openathens extraction** | ✅ PASS *(after fix)* | 84 + 93 tests green; `uv run pytest` fixed |

Fleet health at certification: **G-PROBE 14 live · 0 failed**; **G-BUNDLE CONSISTENT** (20 servers);
**21/21 hook tests**; all three new connectors keyless (no bearer) and OAuth-additive.

---

## Confirmed findings & remediation

### 🔴 CRITICAL — globocan sex/type path slots were swapped (returned wrong data)
- **Defect:** `dataUrl` built `data/rate/{sex}/{type}/…` but the IARC GCO API path order is
  `data/rate/{type}/{sex}/…`. Every `gco_query` therefore returned the wrong measure and sex —
  incidence↔mortality swapped, and `type=2` (prevalence) leaked in producing spurious 3-row
  `prev_time` sets. The initial E2E "male lung incidence 38,505" was actually **both-sex mortality**;
  "female breast incidence 21,564" was actually **1-year prevalence** — plausible magnitudes masked it.
- **Detection:** adversarial cross-validation against published Türkiye 2022 values (female breast
  female mortality must be ~7,360 — the buggy build returned an empty/prevalence result).
- **Fix:** `dataUrl(base, type, sex, …)` → `data/rate/{type}/{sex}/`; `type` enum extended with
  `prevalence`; `prev_time` surfaced in `shapeData`; regression tests pin the path order.
- **Re-verification (live, Version 8825e031):** female breast **mortality 7,360** ✓ / **incidence
  25,249** ✓ (both match published GLOBOCAN 2022 Türkiye); male lung incidence 33,039 > mortality
  32,119 ✓; all-cancers female → Breast rank 1 (25,249) ✓; prevalence → prev_time 1/3/5 ✓.

### 🟠 MEDIUM — globocan silently truncated all-cancers results (limit=40 dropped cancers)
- **Defect:** an all-cancers query can return up to 99 rows (prevalence) or ~34–40 (incidence);
  the old default `limit=40` silently dropped rows (e.g. breast fell off), violating the
  completeness/no-silent-cap invariant.
- **Fix:** default `limit` raised to 120 (max 300) and the response now emits an explicit
  `truncated`/`available_rows`/`note` block when capped — never a silent drop.
- **Re-verification:** all-cancers female incidence → 34 rows, `truncated:false`, breast present.

### 🟡 NIT — who-gho `CODE_RE` accepted bare `.`/`..` segments
- **Defect:** the SSRF allowlist regex `^[A-Za-z0-9_.\-]+$` permitted `.`, `..`, `../…`; the fixed
  hard-coded host made it non-exploitable, but it was a robustness gap.
- **Fix:** `^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$` (must start alphanumeric; no bare/consecutive
  dots) + a regression test asserting real GHO codes pass and `.`/`..`/`../etc` are rejected.
- **Re-verification (live, Version 42665235):** `../etc` and `..` rejected; `WHOSIS_000001` → 77.6.

### 🔵 MINOR — annas-reader / openathens test suites didn't run via the documented command
- **Defect:** both `pyproject.toml` lacked `pythonpath = ["."]`, so `uv run pytest` (the CLAUDE.md
  command) failed at collection with `ModuleNotFoundError: No module named 'app'` — the new
  `test_textproc.py` and all sibling suites were only runnable with a manual `PYTHONPATH=.`.
- **Fix:** added `pythonpath = ["."]` to `[tool.pytest.ini_options]` in both servers.
- **Re-verification:** `uv run pytest` now green out-of-the-box — **annas 84 passed · openathens 93
  passed**. The extraction-quality overhaul itself was already correct (all tests pass); only the
  test-harness path was fixed. ruff clean (openathens; annas env lacks ruff, code unaffected).

---

## What was empirically verified (not assumed)

- **who-gho** — `who_gho_query(WHOSIS_000001, TUR, 2019)` returns 77.6/75.1/80.1 (BTSX/MLE/FMLE),
  **byte-identical to `ghoapi.azureedge.net` direct**; GLOBAL/region disaggregation correct; honest
  empty on missing year; SSRF (`../etc`, `A B`) rejected pre-fetch; every response carries a caveat.
- **globocan** — path order + sex/type mapping proven against **published Türkiye 2022** figures
  (female breast mort 7,360 / inc 25,249); label-join correct; error/SSRF (`79a`, `../`, `x)`)
  rejected; `Turkey`→∅ is honest (GCO labels it "Türkiye"); every response carries the modelled-
  estimate caveat + `ui`.
- **ema** — `ema_stats` live (2,712 / orphan 249 / conditional 60 / prime 46 / authorised 1,863)
  **exactly matches the baked corpus**; `ema_filter` AND-semantics hold on every returned row;
  nonexistent lookup → honest `found:false` + note; `brief` drops long fields, `ema_get_medicine`
  returns them; ISO date parsing correct (Keytruda opinion 2015-05-20).
- **security** — `auth.ts` byte-identical across who-gho/ema/globocan/openfda; **no server-side
  secret or upstream credential** in any of the three (keyless is sound, no confused-deputy);
  OAuth metadata S256-only (no `plain`), PRM → `/mcp`, keyless `/mcp` → 200; redirect allowlist =
  claude.ai/claude.com/grok.com/chatgpt.com.

## Known, accepted limitations (not defects)

- ~~`routing.test.ts` fails in every self-host worker~~ — **RESOLVED 2026-08-07.** The scope in
  this line was also understated: the failure hit **all seven** workers (not the four named),
  so **49 routing/OAuth tests never executed** — `/health`, unknown-path 404, S256-only
  metadata, redirect allowlist, bearer gate. Root cause: `ajv/dist/core.js` `require()`s a
  JSON file and the CJS shim in `@cloudflare/vitest-pool-workers@0.8.71` parsed it as
  JavaScript. Fixed by upgrading the pool to `0.12.21` (newest release still peering on
  vitest 3.2). All 7 workers now `npm test` exit=0; suite total 151 → **200 tests**.
- **wrangler stays on 4.x/`^4.20.0` (installed 4.104.0) — DELIBERATE HOLD, measured 2026-08-07.**
  The CLI prints "update available 4.119.0", but the bump is not isolatable: `wrangler@4.120`
  declares `peerOptional @cloudflare/workers-types@^5.20260801.1`, while
  `@cloudflare/vitest-pool-workers@0.12.21` pins `wrangler@4.72.0` (which wants
  `workers-types@^4.20260310.1`) and `agents`→`partyserver` wants `workers-types@^4.20240729.0`.
  So wrangler 4.119+ forces workers-types v5 and breaks both the test pool and the agents SDK.
  Moving forward means a COORDINATED major bump — vitest 3.2→4, pool-workers 0.12→0.20,
  workers-types 4→5, wrangler 4.104→4.120 — across all seven Workers. That is its own reviewed
  change, not an audit side-effect. Deploys on 4.104.0 are verified working (three Workers
  shipped 2026-08-07). Do not retry a lone `npm i -D wrangler@latest`: it ERESOLVEs.
- GLOBOCAN figures are modelled estimates (2022); EMA is a point-in-time baked snapshot
  (`generated_at` stamped, refresh via `npm run build:corpus`). Both carry mandatory caveats.
- **IHME/GBD remains a documented gap** (no keyless API; account + ToS + row-cap) — honestly marked
  across all docs.

## Provenance

- Deployed versions: who-gho `42665235`, globocan `8825e031`, ema `ff226c89`.
- Sources: `self-host/{who-gho-mcp,globocan-mcp,ema-mcp}/`; reader work in
  CureoHub `mcp-servers/{annas-reader-mcp,openathens-mcp}/` (commit `b066ed3f`, pythonpath fix on top).
- Gates: `scripts/g_bundle.py`, `scripts/g_probe.py`, `scripts/g_identity.py` (2026-08-07), `hooks/test_hooks.py`, `skills/medical-research/evals/check_integrity.py`, `skills/medical-research/evals/rag_quality.py`, `tools/fleetkit/check_drift.py --all`.
