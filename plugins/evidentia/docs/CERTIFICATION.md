# Certification — evidentia gap-closing connectors (who-gho · globocan · ema)

**Date:** 2026-07-05 · **Verdict:** ✅ **CERTIFIED** (all components PASS; every confirmed finding
remediated and re-verified) · **Scope:** the three self-host MCP connectors built to close
evidentia's documented WHO-GHO / GLOBOCAN / EMA gaps, plus their roster/doc wiring, plus the
reader-MCP extraction-quality work (annas-reader-mcp, openathens-mcp).

> ⚠️ **AMENDED 2026-08-07 — read `## Re-certification` at the end before relying on this record.**
> This document is a POINT-IN-TIME certification (2026-07-05) and is kept intact as history. A
> later audit falsified two of its verdicts below; those rows are annotated inline. The current
> state of the plugin is the re-certification section, not this table.

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
| **security (3 workers)** | ⚠️ PASS *(amended 2026-08-07)* | auth.ts byte-identical ×4; keyless justified; OAuth S256; SSRF closed. **The ×4 identity was literally true and that is exactly what hid the defect:** `REALM` was never localised when auth.ts was copied, so ema/globocan/who-gho served `resource_name: "openfda-mcp"` in production — on the RFC 9728 PRM, the OAuth `client_id`, the 401 realm and the **authorize consent page**. Per-Worker tests could not see it (each asserts its own wrong constant); only a cross-Worker comparison could. Fixed + deployed; now gated by `scripts/g_identity.py`. |
| **docs / roster consistency** | ✅ PASS | G-BUNDLE consistent; gap-lines correct; wrong-value claims corrected |
| **tests / build** | ❌ FALSIFIED *(2026-08-07)* | The `ajv` failure was **not** environmental — it was a fixable version pin (`vitest-pool-workers@0.8.71` could not `require()` a JSON file). Calling it environmental let **49 routing/OAuth tests stay dead in all seven Workers** for a month, and this line undercounted the blast radius as four. Fixed by upgrading the pool; suite 151 → 268. |
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
  vitest 3.2), then to **0.20.3 on vitest 4** the same day (see the toolchain entry below).
  All 7 workers `npm test` exit=0; suite total 151 → **268 tests**.
- ~~wrangler stays on 4.x — deliberate hold~~ — **HOLD LIFTED, migration DONE 2026-08-07.**
  The hold was correct about the constraint and wrong about the remedy being out of reach: a
  LONE `npm i -D wrangler@latest` ERESOLVEs (wrangler 4.120 wants `workers-types@^5`, while
  pool-workers' bundled wrangler and `agents`→`partyserver` want `^4`), but asking npm to
  resolve **all four together** succeeds. Migrated across all seven Workers:
  vitest 3.2.6 → **4.1.10**, pool-workers 0.12.21 → **0.20.3**, workers-types 4 → **5.20260804.1**,
  wrangler 4.104 → **4.120.0**. Required one code change: pool 0.20 dropped the `/config`
  subpath export, so `vitest.config.ts` registers the pool as a **Vite plugin**
  (`cloudflareTest({...})`) instead of `test.poolOptions.workers` — shape taken from the
  package's own `codemods/vitest-v3-to-v4`, not guessed. Verified: 7/7 `npm test` exit=0
  (268 tests, unchanged counts), 7/7 typecheck exit=0, 7/7 `wrangler deploy --dry-run` exit=0
  with unchanged bundle sizes.
- GLOBOCAN figures are modelled estimates (2022); EMA is a point-in-time baked snapshot
  (`generated_at` stamped, refresh via `npm run build:corpus`). Both carry mandatory caveats.
- **IHME/GBD remains a documented gap** (no keyless API; account + ToS + row-cap) — honestly marked
  across all docs.

## Provenance

- Deployed versions: who-gho `42665235`, globocan `8825e031`, ema `ff226c89`.
- Sources: `self-host/{who-gho-mcp,globocan-mcp,ema-mcp}/`; reader work in
  CureoHub `mcp-servers/{annas-reader-mcp,openathens-mcp}/` (commit `b066ed3f`, pythonpath fix on top).
- Gates: `scripts/g_bundle.py`, `scripts/g_probe.py`, `scripts/g_identity.py` (2026-08-07), `hooks/test_hooks.py`, `skills/medical-research/evals/check_integrity.py`, `skills/medical-research/evals/rag_quality.py`, `tools/fleetkit/check_drift.py --all`.

---

## Re-certification — 2026-08-07

**Verdict:** ✅ **RE-CERTIFIED** at plugin **v2.3.9** · **Scope:** the whole evidentia plugin
(not just the three gap-closing connectors), after a full integrity / functionality / health audit
and the repairs it produced.

What the 2026-08-07 audit found and closed (details in the git history — commits `a7ac446`,
`33279a3` and this one):

| Finding | Outcome |
|---|---|
| `/evidentia` command frontmatter was invalid YAML (only such file in 42) | fixed (`276ffd1`) |
| SessionStart preflight tracked 6 of 7 gated connectors and told the operator `titck-cache` was keyless | key map now DERIVED from `fleet.lock.json`; `fleet_probe` wired so `auth_missing` ≠ `unauthorized` |
| three Workers identified as `openfda-mcp` in production | `REALM` localised in 7/7, deployed, pinned by the new **G-IDENTITY** gate |
| 49 routing/OAuth tests never executed (all 7 Workers) | pool upgraded; suite 151 → 268 |
| `g_probe` skipped all 7 gated connectors yet printed "ALL PROBED REMOTES HEALTHY" | now resolves `${VAR}`, sends the Bearer, and names what it did NOT measure |
| user-facing pointers to a gitignored install doc | sanitised public `docs/KURULUM.md` |
| `test_hooks.py` reported "no tests ran" + exit 0 under pytest | pytest-visible entry point; 21 → 34 assertions |
| four Workers had untested pure logic (SSRF allowlist, FTS5 injection guard, RRF ranking, snippet cap) | `__testing` barrels + suites |
| toolchain frozen (vitest 3.2 / pool 0.12 / types 4 / wrangler 4.104) | coordinated migration to vitest 4 / pool 0.20 / types 5 / wrangler 4.120 |

**Gates at re-certification (all run, all green):** G-IDENTITY 7/7 · G-BUNDLE 20/20 ·
hook 34/34 (standalone **and** pytest) · skill integrity ALL PASS · G-RAG PASS ·
`check_drift --all` 9 plugins CLEAN · command frontmatter 42/42 · Workers **268 tests** +
7 typecheck + 7 `deploy --dry-run`, all exit 0.

**Live health:** fleet probe **20/20 HTTP 200** with Bearers resolved; 7/7 Workers serve their
own `resource_name`; live functional check on the refactored `openfda` (real query returns a real
product; the SSRF gate rejects traversal and absolute URLs).

**Honest limits of this re-certification.** It covers structure, gates, dependency health and
connector liveness. It does **not** re-validate every tool's output against its upstream — the
2026-07-05 cross-validation for who-gho/globocan/ema still stands as the last such check, and no
equivalent has been run for the other connectors. `@modelcontextprotocol/sdk` sourcemap warnings
remain visible by choice (measured unsuppressable from our side). Human review is still required
before any clinical use.

---

## Re-certification round 2 — 2026-08-07 (functional / endpoint sweep)

Round 1 audited structure. This round audited **behaviour**: 350 tools enumerated via live
`tools/list`, 60+ real `tools/call` invocations, the HTTP/auth surface of all seven self-host
Workers, and the mutating paths that no read-only probe can reach.

**Defects found and fixed (all deployed):**

| # | Defect | Why it survived |
|---|---|---|
| F17 | Full-text **Tier 5 was wired to tools that do not exist** — the always-load cascade recipe called `article_download`/`book_download`, but the bundled `annas-reader` is an ephemeral READER (`read_article` / `search_in_document` / `read_document`). Every last-resort full-text attempt would fail | The connector was re-architected from a downloader to a reader; the docs kept the old API. No gate read tool names |
| F18 | **All seven Workers rejected CORS preflight.** `OPTIONS /mcp` from `https://claude.ai` returned 401 with no `Access-Control-*` headers on the three gated Workers — and a preflight is credential-free by specification, so no browser client (claude.ai web, grok.com, ChatGPT web) could ever add them | `initialize` cannot see it: a non-browser client never sends a preflight. The keyless four answered 200 only because their gate never fires |

**Verified clean (no defect):**
- **anamnesis mutation round-trip** — ingest → query → graph → forget returns the corpus to its
  exact baseline (194/1091/1679/1194) with zero residue; `forget_document` is idempotent.
- **globocan** reproduces its published Türkiye figures exactly (7,360 / 25,249 / 33,039 / 32,119),
  does not silently truncate (34 rows, `truncated:false`), and rejects traversal + injection input.
- **OAuth 2.1 full dance** on all three gated Workers: DCR 201 echoing `redirect_uris` → authorize →
  code → token (`access_token` == `MCP_API_KEY`) → `initialize` 200; PKCE enforced (wrong verifier
  → 400); redirect allowlist rejects a foreign origin (→ 400).
- **Honest empties** — `yok_search` returns 20 hits for real Turkish terms and 0 for absent ones,
  never a fabricated hit.

**New gates.** `g_tools.py --surface` locks the Worker HTTP contract (preflight 204 + allow/expose
headers · RFC 9728 PRM in both path forms · AS metadata · `/health` · 401 shape). Combined with
`--smoke`, one command now covers reachability, tool surface, functional behaviour and auth surface.

**Method note, recorded because it changes how these results should be read.** Seven of the first
24 whitelist calls failed on *my own wrong argument names*, not on the servers. That is itself a
finding — a model reading the registry would guess identically — so the measured argument contracts
are now written down in `connector-registry.md` §2.7. Two reported observations in the round-2 log
were likewise harness artifacts and are NOT defects: a missing `Access-Control-Expose-Headers`
reading (case-sensitive dict lookup) and a 400 on unauthenticated POST (bodyless request rejected
by the SDK before the gate). Both probes were corrected.

**Honest limits of this round.** 60+ of 350 tools were exercised with real calls; the remainder were
validated at schema level only, so their *output correctness* is unverified. `evidentia-kb.kb_upsert`
was deliberately NOT exercised: unlike `anamnesis.forget_document` it has no inverse, so a probe
would permanently pollute the KB index. Upstream data accuracy is unchanged since the 2026-07-05
cross-validation for who-gho/globocan/ema; no equivalent has been run for the other connectors.

