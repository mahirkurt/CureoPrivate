# medical-research v8.1 — Deliverable Index

**v8.1 (Jun 2026) — Clean-Copy Presentation Doctrine.** Adds an always-loaded
`references/report-presentation.md` + a new **Adım 5** in `SKILL.md` that turn file-based
reports into journal-grade Turkish clean copies: full sentences, scholarly register, explicit
Vancouver references, info boxes/abbreviations index, reader-facing Methods/Limitations — with
**no tooling/connector/telemetry leakage** in the visible body. All visualization directives are
isolated in non-rendering `<!-- VIZ: … -->` comments and all operational trace (incl. the
Cömertlik Garantisi) in `<!-- OPS: … -->` comments, neither of which reaches the reader. Research
depth (Adım 0–4) and connector wiring are unchanged.

Ground-truth connector integration rewrite (v8.0). Tool names/parameters verified by **live MCP
probe on 9 June 2026** (not assumed). The skill files here are READ-ONLY in this session's
cache; to adopt them, copy into your saved skill via **Ayarlar > Capabilities** (or your skill
repo) — they are not auto-installed.

## Files
| File | What it is | Status |
|---|---|---|
| `00-IYILESTIRME-PLANI.md` | **Keystone:** comprehensive improvement plan — gap analysis (severity-rated), live-probe evidence table, full connector registry map, v8.0 architecture, risks/alternatives, file-by-file migration roadmap | ✅ full |
| `SKILL.md` | v8.0 orchestration core — native-first protocol, verified registry, 10-axis classifier (+0.5.K epidemiology), real Adım 1 call list, output contract, SMP manifest | ✅ full rewrite |
| `references/connector-registry.md` | Verified tool table (replaces `connector-api.md`); native-first ladder; per-connector notes; limitations | ✅ full (new) |
| `references/drug-intelligence-layer.md` | **CRITICAL FIX** — real AdisInsight schema (`search_drugs`/`get_drug` HyDE/`generate_chart`); v7.1 fictional schema removed | ✅ full rewrite |
| `references/turkiye-layer.md` | **NEW** — TİTCK 15+ native tools + Mevzuat + TÜRKPATENT + YÖK (replaces Exa TR scraping) | ✅ full (new) |
| `references/regulatory-intelligence.md` | **NEW** — native openFDA + WHO ICD-11 + WHO GHO + Health Canada + Federal Register + EUR-Lex | ✅ full (new) |
| `references/fulltext-retrieval.md` | **NEW** — full-text cascade EPMC PMC → copyright → annas-mcp (verified) → paper-download → Wiley; copyright gate | ✅ full (new) |
| `references/report-presentation.md` | **NEW (v8.1)** — clean-copy doctrine: scholarly Turkish, no tooling leakage, journal-style Methods, info boxes, `<!-- VIZ -->`/`<!-- OPS -->` isolation, scaffold→clean-copy map, finalization gate G1–G7 | ✅ full (new) |
| `references/v8-wiring-patch.md` | Precise find→replace spec for the remaining existing files (extended-api, evidence-grading, output-templates, 8 specialty layers, osint/execution/composition/benchmark) — retains clinical content, swaps connector wiring | ✅ actionable spec |

## What's done vs. remaining
- **P0 (this turn):** plan + SKILL.md + connector-registry + drug-intelligence-layer + turkiye-layer — full files.
- **P1 (this turn):** regulatory-intelligence + fulltext-retrieval — full files.
- **P2/P3 (next turn, specified in `v8-wiring-patch.md`):** apply the patch to extended-api.md, evidence-grading.md, output-templates.md, and the 8 specialty layers + infra files. Clinical content is preserved; only connector calls change. Can be executed file-by-file on request.

## The single most important fix
`drug-intelligence-layer.md`: v7.1 told the model to call AdisInsight with parameters that
**do not exist** on the connected MCP (`organisations`/`phases`/`moas`/`drugClass`/`locations`).
v8.0 uses the **verified** interface — confirmed by a live `search_drugs("glofitamab")` call
returning a full Columvi/Roche/STARGLO/ODAC/CRL profile.

## Verification (live probes, 9 Jun 2026)
AdisInsight ✅ (glofitamab profile) · TİTCK ✅ (trastuzumab + biosimilars + 2026 prices) ·
annas-mcp ✅ (GRADE 2008 downloaded) · WHO GHO ✅ (Türkiye life-expectancy) · openFDA/ICD-11/
EPMC/ChEMBL schemas ✅ · Tavily ⚠️ quota (Exa-fallback) · Regulatory MCP ⚠️ latency (single+retry) ·
OpenTargets ❌ offline (conditional).
