---
name: sci-audit-orchestrator
description: Use when auditing an LLM-generated scientific text (article draft, thesis chapter, review, report, abstract) for integrity and language quality — trigger on "audit this text", "check this draft", "is this citation real", "verify these stats", "bilimsel metni denetle", "kaynakları doğrula", "Türkçe imla kontrol". Detects language (Turkish auto-enables axis G), section type, splits long text, fans out the seven audit axes, and merges the scores into one report.
---

# sci-audit Orchestrator

Coordinate a seven-axis forensic + linguistic audit of LLM-generated scientific
text. This skill is the entry point; it plans and merges. The per-axis work runs
in the axis skills and subagents.

## The seven axes

| Axis | Name | Deterministic core | MCP / subagent escalation |
|---|---|---|---|
| A | Reference integrity | — | `citation-verifier` agent → openalex+crossref+pubmed |
| B | Claim grounding | `claim-grounding` skill | `claim-extractor` + `claim-refuter` agents |
| C | Statistical consistency | `stats-forensics` skill (statcheck/GRIM) | `stats-checker` agent |
| D | Hallucination signals | `hallucination-signals` skill | `semantic_entropy.py` via a subagent |
| E | Reporting-guideline conformance | `guideline-mapper` agent + `references/guidelines/` | — |
| F | AI-use transparency | this skill (disclosure scan) | — |
| G | Turkish scientific writing | `turkish-sci-style` skill (`tr_sciaudit.py`) | `style-judge` agent |

## Workflow

1. **Read** the target text (a file path, a pasted block, or the current diff).
   Never read participant data, PII, transcripts, or `.env`/credentials — the
   PreToolUse hook enforces this; respect it.
2. **Detect language.** If the text is Turkish (Turkish-specific letters
   present) or the user passed `--lang tr`, axis G is REQUIRED. Otherwise G is
   skipped and noted as "not applicable (non-Turkish)".
3. **Detect document type** to select the axis-E guideline: systematic
   review → PRISMA; RCT → CONSORT; observational → STROBE; qualitative →
   COREQ/SRQR; diagnostic/prognostic model → TRIPOD; general empirical report →
   JARS. When unsure, ask or run the closest fit and say so.
4. **Section the text** if it is long (> ~4000 words): split on headings and
   fan out sections to subagents so each fits a clean context window. Merge
   findings by axis afterward.
5. **Run the deterministic cores first** (they need no network and never
   fabricate): `claim-grounding`, `stats-forensics`, `hallucination-signals`,
   and — for Turkish — `turkish-sci-style/scripts/tr_sciaudit.py`. Reference
   the exact commands in each axis skill.
6. **Escalate to MCP / subagents** for axes A/B where a claim or citation must
   be resolved against a real source. Route per the table in
   `references/conventions.md`. If an MCP is unavailable, mark that finding
   `unverified (no MCP)` — no score penalty, and it can NOT be a blocker.
7. **Score & merge.** Each axis gets 0–100 (see scoring below). Map severities:
   `error → blocker`, `warning → major`, `info → minor`. Render the merged
   report from `references/report-template.md`; report language = the user's
   language, with EN+TR paired section titles.

## Severity, strictness, and the gate

- **Strictness modes** (preserved from `tr_sciaudit`): `draft` (light pass) and
  `certification` (full pass; axis G adds abbreviation consistency).
- **`--fail-on`** mirrors the CLI: in `certification` mode the report states the
  gate outcome — with `--fail-on error`, any blocker means "gate does not
  close". This is REPORTED, never silently enforced by fabrication.
- A deterministic finding always beats an LLM-judge finding on conflict: if
  `style-judge` disagrees with `tr_sciaudit`, the deterministic result wins.

## Scoring

Per axis: start at 100, subtract 15 per blocker, 5 per major, 1 per minor,
floor at 0. Report the raw finding list alongside the score — the evidence is
the product, the number is a summary. Never invent a score for an axis you did
not run; mark it `not run` or `not applicable`.

## No-fabrication invariant

Absence of a detected problem is NOT proof of correctness — every axis result
carries a scope note saying what it did and did not check. An unresolved
citation, an unreachable MCP, or a skipped provider is reported as such, never
as a pass. See `references/conventions.md`.

## References

- `references/conventions.md` — scientific-integrity conventions, the axis→MCP
  routing table, and the provider-degrade matrix (injected at SessionStart).
- `references/report-template.md` — the seven-axis merged report shell.
- `references/guidelines/` — PRISMA/CONSORT/STROBE/COREQ/SRQR/JARS/TRIPOD item
  checklists for axis E.
