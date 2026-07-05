---
name: stats-forensics
description: Use when checking the internal statistical consistency of an LLM-generated scientific text (axis C) — trigger on "check the stats", "do these p-values add up", "statcheck this", "GRIM test", "are these percentages consistent", "istatistik tutarlılığı", "p değeri kontrolü". Recomputes p-values from reported test statistics, runs GRIM on reported means, and flags impossible effect sizes.
---

# Statistics Forensics (axis C)

Catch statistics that are internally impossible — the p-value that does not
follow from its test statistic, the mean that cannot arise from its N, the
correlation outside [-1, 1]. These are detectable without any external source.

## Method

Run the deterministic checker (stdlib-only, no network):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/stats-forensics/scripts/stats_forensics.py" <file> --fail-on error
# multi-item summed scale? pass the item count so GRIM uses the right granularity:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/stats-forensics/scripts/stats_forensics.py" <file> --grim-scale 20
```

What it does:

- **statcheck.** Extracts inline `t(df)=…, p=…`, `F(df1,df2)=…, p=…`,
  `χ²(df)=…, p=…`, `r(df)=…, p=…`, `z=…, p=…`, recomputes the two-sided p from
  the statistic (exact stdlib CDFs), and flags inconsistencies. A **decision-
  changing** inconsistency (reported significant, recomputed not — or vice
  versa) is a **blocker**; a non-decision-changing mismatch is a **major**.
- **GRIM.** For a reported mean of an integer-item measure over N observations,
  checks the mean is achievable as k/N. An impossible mean is a **major** (flag,
  because multi-item scales change granularity — use `--grim-scale`).
- **Effect-size plausibility.** `|r|>1`, negative df, impossible proportions →
  **blocker**.

## Judgement layer

For heterogeneity, base-rate, or effect-size *plausibility* that needs domain
reasoning (not arithmetic), use the `stats-checker` agent — but it calls this
script for the arithmetic and never overrides a deterministic impossibility.

## Invariant

A clean run means "no inconsistency detected in the machine-readable inline
statistics", not "the statistics are correct". Prose-only statistics the regex
cannot parse are reported as `not machine-checkable`, not as passing.
