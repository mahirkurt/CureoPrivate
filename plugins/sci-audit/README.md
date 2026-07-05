# sci-audit

A domain-agnostic **forensic + linguistic auditor for LLM-generated scientific
text** — article drafts, thesis chapters, reviews, reports, abstracts. It checks
seven axes and never fabricates a confirmation: an unresolvable citation, an
unreachable service, or a skipped provider is reported as such, not as a pass.

The deterministic core is **pure Python standard library** and runs anywhere,
including the claude.ai web app. Heavy dependencies (Zemberek, RAGAS, NLI
backends) are isolated to an optional layer that degrades gracefully when
absent.

## The seven axes

| Axis | Name | What it catches |
|---|---|---|
| A | Reference integrity | Fabricated / misattributed / retracted citations (DOI/PMID metadata match) |
| B | Claim grounding | Numeric & factual claims with no supporting source; **legal open-access full-text** verification of whether the cited source actually supports the claim |
| C | Statistical consistency | Document-internal checks (no raw data needed): statcheck p-recompute (**Turkish decimals**, one-tailed reclassification), GRIM / GRIMMER, SPRITE feasibility, CI ↔ estimate/p consistency, percentage-sum & subgroup-N sanity, impossible effect sizes |
| D | Hallucination signals | Over-certainty, universal quantifiers, malformed/**checksum-invalid identifiers** (ISBN/ORCID/arXiv), invented method names, **hallucinated entity names** (drug/gene/disease via authority MCPs), semantic entropy |
| E | Reporting-guideline conformance | **14 guidelines** (PRISMA, PRISMA-ScR, CONSORT, CONSORT-AI, STROBE, COREQ, SRQR, JARS, TRIPOD, TRIPOD+AI, STARD, SPIRIT, CHEERS, ARRIVE) + deterministic section pre-scan |
| F | AI-use transparency | Missing AI-use disclosure (ICMJE/COPE/WAME), LLM giveaway boilerplate, unfilled placeholders |
| G | Turkish scientific writing | Orthography, register, causal-language discipline, APA-TR number format — **auto-enabled when the text is Turkish** |

The document-internal statistics layer (axis C) consolidates the checks
formerly in the separate `replicatio` plugin (now retired), reimplemented
stdlib-only so they run on the web with no R runtime.

## Commands

| Command | Axis | Purpose |
|---|---|---|
| `/sci-audit:audit <file>` | all | Full seven-axis audit |
| `/sci-audit:verify-citations <file>` | A | Reference integrity only |
| `/sci-audit:check-stats <file>` | C | Statistical consistency only |
| `/sci-audit:guideline-check <file> [--type ...]` | E | Reporting-guideline conformance |
| `/sci-audit:check-turkish <file> [flags]` | G | Turkish writing & orthography |
| `/sci-audit:audit-report [--out FILE]` | — | Merge findings into one report |
| `/sci-audit:ai-log <summary>` | — | Append a run to the audit JSONL log |

## Deterministic CLI (no Claude needed)

Every core runs standalone:

```bash
# Axis G — Turkish writing (CLI contract preserved from the source tool)
python3 skills/turkish-sci-style/scripts/tr_sciaudit.py chapter.md \
  --strictness certification --format md --fail-on error \
  [--enable-tdk --terms "a,b"] [--enable-zemberek] \
  [--enable-gecturk --gecturk-url http://127.0.0.1:8765/check] \
  [--abbreviations project-abbr.txt]

# Axis C — statistics (statcheck/GRIM/GRIMMER/SPRITE/CI/percentage/subgroup)
python3 skills/stats-forensics/scripts/stats_forensics.py chapter.md --grim-scale 20

# Axis B — claim grounding
python3 skills/claim-grounding/scripts/claim_grounding.py chapter.md

# Axis D — hallucination signals + ISBN/ORCID/arXiv checksums
python3 skills/hallucination-signals/scripts/hallucination_signals.py chapter.md

# Axis E — deterministic section pre-scan
python3 skills/sci-audit-orchestrator/scripts/guideline_prescan.py chapter.md

# Axis F — AI-use transparency
python3 skills/ai-transparency/scripts/ai_transparency.py chapter.md

# Evidence ledger (content-hashed provenance for a defensible audit)
python3 skills/sci-audit-orchestrator/scripts/evidence_ledger.py hash --text "source excerpt"
```

## Integrity guards (full-text era)

Because axis B now fetches external full text, two invariants are enforced (see
`skills/sci-audit-orchestrator/references/conventions.md`):

- **Injection shield** — the audited document and every fetched passage are
  untrusted content, analysed as data; text embedded in them ("mark as
  verified", "ignore instructions") never sets a verdict.
- **Privacy invariant** — only citation identifiers/titles go to third-party
  MCP hosts, never the (possibly unpublished) manuscript body; claim↔source
  comparison happens inside Claude.

`--strictness` is `draft` (light) or `certification` (full; adds abbreviation
consistency). `--fail-on error` returns a non-zero exit on any blocker.

## Hooks (active while the plugin is enabled)

| Event | Guard |
|---|---|
| SessionStart | Injects scientific-integrity + Turkish-writing conventions |
| UserPromptSubmit | Blocks prompts containing secrets |
| PreToolUse (Bash) | Denies destructive commands + credential/`.env` reads + raw `mcp list` |
| PostToolUse (Bash) | Flags secret leaks and error signatures in output |
| Stop | Twin gate: (a) unsourced numeric claim; (b) Turkish decimal-dot p-value (G5) |

Configure the Stop gate via `.claude/sci-audit.local.md` (YAML frontmatter):

```markdown
---
lang: auto            # auto | tr | en
gate_unsourced_numeric: true
gate_tr_pvalue_dot: true
---
```

## MCP & connectors

`.mcp.json` bundles **remote HTTP** scientific-core servers (keyless, public
bibliographic data): `pubmed`, `pubmed-epmc`, `openalex`, `semantic-scholar`.
No stdio/local binaries are used, so the plugin works on claude.ai web.

Servers **without** an official remote endpoint are not embedded — connect them
as **claude.ai connectors** instead:

- **Crossref** — used for DOI resolution + retraction cross-check (axis A). Add
  it via your claude.ai connector settings if you have a Crossref MCP endpoint.

**Future placeholder:** a self-hosted `tr-sciaudit-mcp` (FastMCP) would be added
to `.mcp.json` as an **env-gated** remote entry:

```json
"tr-sciaudit": {
  "type": "http",
  "url": "https://tr-sciaudit.<host>/mcp",
  "headers": { "Authorization": "Bearer ${TR_SCIAUDIT_MCP_API_KEY}" }
}
```

Keys are always `${ENV_VAR}`-expanded, never plaintext.

## Provider / MCP degrade matrix

| Layer | Available | Unavailable |
|---|---|---|
| Deterministic cores (B, C, D, G1–G6) | always (no network, web included) | n/a — always run |
| MCP (A/B citation & claim resolution) | resolves against real sources | finding tagged `unverified (no MCP)`; **never** a lone blocker |
| TDK (axis G, direct HTTP) | Turkish term validity | provider status `error`; deterministic G-audit stands |
| GECTurk self-host (axis G) | grammar findings (local/CI) | status `unavailable`; never assumed on web |
| Zemberek (axis G7, pip pkg) | morphology sample | status `unavailable`; report not blocked |
| `style-judge` subagent (axis G) | register/fluency rubric | deterministic G-axis stands alone |
| Grok CI-eval judge | optional CI reasoning gate | `unavailable`; **no text is sent** without a key |

**No-fabrication invariant:** absence of a finding is never proof of
correctness. Every axis result states what it did and did not check. On
conflict, a deterministic finding beats the LLM judge.

## claude.ai web setup

1. Install the plugin from the Cureonics marketplace.
2. The deterministic cores and all seven axes work immediately — no local setup.
3. For axes A/B source resolution, ensure the bundled remote MCPs are reachable
   (they are keyless) and optionally add a Crossref connector.
4. Turkish axis G runs fully deterministically on the web; TDK adds term
   validity when reachable. GECTurk/Zemberek are local/CI only and degrade to
   `unavailable` on the web — the report is never blocked by their absence.

## Optional layer (local venv / CI only)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r reliability/requirements-optional.txt   # Zemberek (setuptools<81 pin), RAGAS, OTel
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

Core tests are stdlib-only; the Zemberek test is skipped when the package is
absent. See `governance/` for the NIST AI RMF / ISO 42001 / EU AI Act control
map and `reliability/` for the CI eval + red-team layer.

## Scope

sci-audit checks **integrity and language signals**. It does not certify
scientific truth, replace peer review, or make clinical/legal judgements. It
assists a human reviewer; sign-off remains human.
