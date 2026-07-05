---
description: Axis E only — check a manuscript against a reporting guideline
argument-hint: <file-or-paste> [--type prisma|prisma-scr|consort|consort-ai|strobe|coreq|srqr|jars|tripod|tripod-ai|stard|spirit|cheers|arrive]
allowed-tools: Read, Bash, Grep, Task
---

Run axis E (reporting-guideline conformance) over the text in `$ARGUMENTS`.

1. Run the deterministic section pre-scan for a quick presence map:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/sci-audit-orchestrator/scripts/guideline_prescan.py" <file>
   ```
2. Determine the guideline. If `--type` is given, use it. Otherwise infer from
   the design: systematic review → PRISMA; scoping review → PRISMA-ScR; RCT →
   CONSORT (AI/ML → CONSORT-AI); observational → STROBE; qualitative
   interviews/focus groups → COREQ; other qualitative → SRQR; diagnostic
   accuracy → STARD; general quantitative → JARS; prediction model → TRIPOD
   (ML → TRIPOD+AI); trial protocol → SPIRIT; health-economic → CHEERS; animal
   study → ARRIVE. State which you chose and why.
3. Load the matching checklist from
   `skills/sci-audit-orchestrator/references/guidelines/<name>.md`.
3. Use the `guideline-mapper` subagent to map each checklist item to the text:
   present / missing / partial, with the locating quote.
4. Highlight the guideline's "red flags for LLM text" (each checklist file lists
   them) — these are the items LLM drafts most often fake or omit.

Output a checklist table: `item | status | evidence/quote | note`. Missing
mandatory items are majors; internally contradictory reporting (e.g. a flow
diagram whose numbers do not reconcile) is a blocker. Absence of a section is
reported as missing, not inferred as satisfied.
