# medical-research v9.0.2 — Deliverable Index

**v9.0.2 (Aug 2026) — Ordered PRISMA tool playbook.** `references/execution-map.md` binds
MUST/SHOULD/MAY/OUT + `SKIP-REASON` for all **19 bundled servers + 9 companions**. Completeness
Gate requires skip reasons. **who-gho / globocan / ema** are native (IHME/GBD still gap).
Anamnesis exclusive-run (`collection=evidentia:run:<id>` + `evrun:`) hybrid is P4/P6 MUST after
ingest. New gate **G-PLAYBOOK**. Plugin version stays **2.7.2**.

**v8.5.0 (Jun 2026) — Extended-Tier Promotion & Epidemiology Wiring.** The Extended Tier-K connectors
(`med-terminologies`, `nih-clinicaltables`, `nlm-rxnorm`, `iuphar-gtopdb`) are promoted to **first-class**
with tool-level whitelists + cross-validation gates (`connector-registry.md §2.6`); broken upstream tools
(D1/D2/D3/D6) are routed to working alternatives and the pipeworx generics are out-of-whitelist.
**drugddx** is live (Tier-O clinical-DDI). The **D-α** drift is fixed — the legacy "Regulatory MCP" is
replaced by **`openfda`** (openFDA + WHO ICD-11; WHO-GHO/Health-Canada/Federal-Register/EUR-Lex →
documented gap). **PopHIVE** is wired for **US** epidemiology (axis 0.5.K; **US-only** — global/Türkiye
burden stays a documented gap). New executable gates **G-PROBE / G-XVAL / G-WHITELIST**; everything
probe-verified by a live re-probe 2026-06-28 (`connector-registry.md §8` Probe Log). Additive/ADR-05-safe.

**v8.4.0 (Jun 2026) — Structured-Authoritative Refocus (web tier + OSINT removed).** evidentia is
now a **pure structured-authoritative evidence engine**: the Exa/Tavily web-retrieval tier and the
entire OSINT axis (`osint-playbook.md`, social-listening) were **removed**. The Native-First ladder
ends at a **documented gap** — sources with no native API (EMA CHMP/EPAR, ESMO/NCCN/NICE guideline
PDFs, GLOBOCAN/IHME/WHO-GHO burden) are reported as an unreachable gap, **never web-scraped or
fabricated**. Full-text cascade Tier 5 (was Exa) → **pubmed-epmc Unpaywall legal-OA**. **Three
keyless Tier-K academic connectors** were added (probe-verified 2026-06-27): **OpenAlex**
(KOL/citation-network/institution disambiguation), **PubMed-EPMC** (Europe PMC breadth + Unpaywall
legal-OA full text), **Semantic Scholar** (citation graph) — promoted from `native_rest_fallback`.
Web/OSINT competitive intelligence now hands off to external `pharmaintel`. The 3P-untrusted keyless
trust posture is documented (`connector-registry §6.3P`; keyless ⇒ no secret leak).

**v8.3.0 — semantic coverage mechanism.** New always-loaded `references/knowledge-map.md` +
mandatory **Adım 0.4 (Semantic Scope Scan)**: decomposes the question into a concept set, resolves
sections via the knowledge-map Inverted Map, optionally calls the `kb_search` booster, and emits an
auditable `coverage_set`. Adım 0.5 now loads the **UNION** of that set (keyword signals only add,
never shrink); a new **Completeness Gate** re-scans for unconsulted axes before finalising. New
**`G-COVERAGE`** gate in `evals/check_integrity.py`. The optional `evidentia-kb` (`kb_search`)
booster is graceful-degrade — it can only raise recall, never gate the flow.

**v8.2.0 — Reference-Integrity & Operability Release.** Closed the v8.0/8.1 incomplete-migration gap
(22 cited reference files, of which only 6 existed): recreated the missing always-load files + 8
specialty layers + infra files so **all references resolve**; promoted the embedded SMP excerpt to a
standalone, parseable **`skill-manifest.yaml`**; added an **executable** verification harness
(`evals/check_integrity.py` — G-REF / G-ALWAYS / G-CONN / G-VERSION + 10 regression queries). The
P2/P3 wiring patch (`v8-wiring-patch.md`) was **applied this release** — the 8 specialty layers were
rebuilt with verified connector wiring (clinical content preserved, ADR-05).

**v8.1 — Clean-Copy Presentation Doctrine.** Always-loaded `references/report-presentation.md` + a
new **Adım 5** that turns file-based reports into journal-grade Turkish clean copies (full sentences,
scholarly register, explicit Vancouver references, info boxes/abbreviations index, reader-facing
Methods/Limitations) with **no tooling/connector/telemetry leakage** in the visible body;
visualization directives isolated in non-rendering `<!-- VIZ -->` and operational trace in
`<!-- OPS -->`.

Ground-truth connector integration rewrite (v8.0): tool names/parameters verified by **live MCP
probe on 9 June 2026** (not assumed); the keyless Tier-K trio was **re-probed 2026-06-27**. To adopt
the skill, install the `evidentia` plugin (or copy into your saved skill repo) — see the plugin
`INSTALL.md`; it is not auto-installed.

## Files (corpus: 23 reference files under `references/` + the `evals/` harness)
| File | What it is | Status |
|---|---|---|
| `SKILL.md` | v8.5 orchestration core — native-first protocol, verified registry, 10-axis classifier (+0.5.K epidemiology + PopHIVE), Adım 0.4 semantic scan, Adım 1/B Extended-Tier recipes, §1–21 output contract, SMP excerpt | ✅ current |
| `skill-manifest.yaml` | Standalone SMP v1.0 manifest (runtime.mcp_servers + composition + verification gates + constraints) | ✅ current |
| `evals/check_integrity.py` | Executable gate harness — G-REF (mount-tolerant) / G-ALWAYS / G-CONN / G-VERSION / G-COVERAGE | ✅ present |
| `evals/rag_quality.py` | G-RAG output-faithfulness eval (gold set + planted negative controls; optional `--judge` layer) | ✅ present |
| `references/connector-registry.md` | Verified tool table (replaces `connector-api.md`); native-first ladder; per-connector notes; §6.3P third-party trust | ✅ current |
| `references/knowledge-map.md` | **v8.3** semantic coverage index (drives Adım 0.4); always-load | ✅ current |
| `references/drug-intelligence-layer.md` | Real AdisInsight schema (`search_drugs`/`get_drug` HyDE/`generate_chart`); v7.1 fictional schema removed | ✅ current |
| `references/turkiye-layer.md` | TİTCK 15+ native tools + TÜRKPATENT + YÖK (native TR sources, no web scraping; SUT/mevzuat → cureolex) | ✅ current |
| `references/regulatory-intelligence.md` | Native openFDA + WHO ICD-11 (via openfda Worker); no-API burden/guideline sources = documented gap | ✅ current |
| `references/fulltext-retrieval.md` | Full-text cascade (legal-first 6-tier): EPMC PMC OA → Paper Search → OpenAthens/Millet Kütüphanesi (Tier 3 licensed) → Wiley (Tier 4) → annas-mcp (Tier 5 last resort) → pubmed-epmc Unpaywall (Tier 6) | ✅ current |
| `references/report-presentation.md` | v8.1 clean-copy doctrine; `<!-- VIZ -->`/`<!-- OPS -->` isolation; finalization gate G1–G7 | ✅ current |
| `references/{oncology,hematology,regulatory-science,hta,medaffairs-ops,immunology,neurology,rare-disease}-layer.md` | 8 specialty layers — clinical content + verified connector wiring | ✅ current |
| `references/v8-wiring-patch.md` | find→replace wiring spec — **applied in v8.2** (retained as provenance) | ✅ applied |
| `00-IYILESTIRME-PLANI.md` | v7.1→v8.0 improvement plan — **SUPERSEDED / HISTORICAL** (Exa/Tavily prescriptions void as of v8.4; audit-trail only) | ⛔ historical |

## What's done vs. remaining
- **v8.0 / 8.1:** plan + SKILL.md + connector-registry + drug-intelligence + turkiye + regulatory-intelligence + fulltext + report-presentation — full files.
- **v8.2 (DONE — no longer "remaining"):** the P2/P3 wiring patch was **applied** (8 specialty layers + infra files rebuilt with verified wiring); standalone manifest + executable `evals/` harness shipped; all references resolve.
- **v8.3 (DONE):** semantic coverage mechanism — knowledge-map + Adım 0.4 + Completeness Gate + `G-COVERAGE`.
- **v8.4 (DONE):** web/OSINT tier removed; keyless Tier-K trio (OpenAlex / PubMed-EPMC / Semantic Scholar) promoted; full-text Tier 5 → Unpaywall legal-OA.
- **Remaining (optional):** deploy-gated self-host Tier-O Workers (e.g. `drugddx`) per their BUILD-BRIEF DoD; the LLM-judge layer for G-RAG (`--judge` with `EVIDENTIA_JUDGE_KEY`).

## The single most important fix (v8.0, retained)
`drug-intelligence-layer.md`: v7.1 told the model to call AdisInsight with parameters that **do not
exist** on the connected MCP (`organisations`/`phases`/`moas`/`drugClass`/`locations`). v8.0 uses the
**verified** interface — confirmed by a live `search_drugs("glofitamab")` call returning a full
Columvi/Roche/STARGLO/ODAC/CRL profile.

## Verification (live probes)
**Connector probe 9 Jun 2026:** AdisInsight ✅ (glofitamab profile) · TİTCK ✅ (trastuzumab +
biosimilars + 2026 prices) · annas-mcp ✅ (GRADE 2008 downloaded) · openFDA / WHO ICD-11 / EPMC /
ChEMBL schemas ✅ · OpenTargets ❌ offline (conditional). *(WHO-GHO was then wired via the legacy
Regulatory MCP; in v8.4 WHO-GHO / Health Canada / Federal Register / EUR-Lex are **documented gaps** —
the `openfda` Worker now serves openFDA + WHO ICD-11 only.)* **Keyless Tier-K re-probe 2026-06-27:**
OpenAlex ✅ (v0.7.2, 5 tools) · PubMed-EPMC ✅ (v2.9.7, 10 tools) · Semantic Scholar ✅ (pipeworx
gateway). **Executable gates:** `python3 evals/check_integrity.py` (G-REF mount-tolerant + G-ALWAYS +
G-CONN + G-VERSION + G-COVERAGE) and `python3 evals/rag_quality.py` (G-RAG) — all green.
