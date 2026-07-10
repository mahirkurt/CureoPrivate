---
description: Compile per-axis findings into a single merged sci-audit report
argument-hint: "[--format md|json] [--out FILE]"
allowed-tools: Read, Bash, Write
---

Compile the findings gathered this session (from `/sci-audit:audit` or from
individual axis commands) into one merged report.

1. Collect the per-axis results already produced in this conversation. If none
   exist yet, tell the user to run `/sci-audit:audit` or an individual axis
   command first.
2. Fill `skills/sci-audit-orchestrator/references/report-template.md`:
   - the axis-score table (100 − 15/blocker − 5/major − 1/minor, floored at 0);
   - blockers, majors, minors as evidence-quoting lists;
   - the "What was NOT checked" section (unreachable MCP, skipped provider,
     sampled sections) — mandatory;
   - the provider/MCP status line.
3. State the overall verdict and, for `certification` + `--fail-on error`,
   whether the gate closes.
4. If `--out FILE` is given, write the report there (Markdown by default, JSON
   with `--format json`). Otherwise print it.

Report language follows the user; section titles are EN + TR paired. Never
invent a score for an axis that was not run — mark it `not run` or
`not applicable`.
