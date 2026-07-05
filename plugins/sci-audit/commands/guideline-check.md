---
description: Axis E only — check a manuscript against a reporting guideline
argument-hint: <file-or-paste> [--type prisma|consort|strobe|coreq|srqr|jars|tripod]
allowed-tools: Read, Bash, Grep, Task
---

Run axis E (reporting-guideline conformance) over the text in `$ARGUMENTS`.

1. Determine the guideline. If `--type` is given, use it. Otherwise infer from
   the design: systematic review → PRISMA; RCT → CONSORT; observational →
   STROBE; qualitative interviews/focus groups → COREQ; other qualitative →
   SRQR; general quantitative → JARS; prediction model → TRIPOD. State which you
   chose and why.
2. Load the matching checklist from
   `skills/sci-audit-orchestrator/references/guidelines/<name>.md`.
3. Use the `guideline-mapper` subagent to map each checklist item to the text:
   present / missing / partial, with the locating quote.
4. Highlight the guideline's "red flags for LLM text" (each checklist file lists
   them) — these are the items LLM drafts most often fake or omit.

Output a checklist table: `item | status | evidence/quote | note`. Missing
mandatory items are majors; internally contradictory reporting (e.g. a flow
diagram whose numbers do not reconcile) is a blocker. Absence of a section is
reported as missing, not inferred as satisfied.
