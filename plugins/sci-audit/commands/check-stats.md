---
description: Axis C only — recompute p-values, run GRIM, flag impossible statistics
argument-hint: <file-or-paste> [--grim-scale N]
allowed-tools: Read, Bash, Task
---

Run axis C (statistical consistency) over the text in `$ARGUMENTS`.

Load the `stats-forensics` skill and run the deterministic checker:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/stats-forensics/scripts/stats_forensics.py" <file> --fail-on error
```

If the text reports means of summed multi-item scales, pass `--grim-scale N`
(the item count) so GRIM uses the right granularity.

Report:
- statcheck inconsistencies, marking decision-changing ones as blockers;
- GRIM-impossible means as majors (note multi-item scales change granularity);
- impossible effect sizes (|r|>1, negative df) as blockers.

For heterogeneity / effect-size *plausibility* that needs domain reasoning
(not arithmetic), use the `stats-checker` subagent — but it never overrides a
deterministic impossibility. A clean run means "no inconsistency detected in
machine-readable inline statistics", not "the statistics are correct"; say so.
