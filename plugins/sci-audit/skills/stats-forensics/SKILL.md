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

This layer evaluates the numbers **as presented in the document** — it needs no
raw data, code, or reproduction. It consolidates the document-internal checks
formerly in the retired `replicatio` plugin's numeric-consistency layer
(statcheck + GRIM/GRIMMER + SPRITE), reimplemented stdlib-only.

What it does:

- **statcheck.** Extracts inline `t(df)=…, p=…`, `F(df1,df2)=…, p=…`,
  `χ²(df)=…, p=…`, `r(df)=…, p=…`, `z=…, p=…`, recomputes the two-sided p from
  the statistic (exact stdlib CDFs), and flags inconsistencies. **Decimal comma**
  (Turkish/APA-TR `t(38)=2,50, p=0,02`) is parsed too. A **decision-changing**
  inconsistency is a **blocker**; a non-decision-changing mismatch is a
  **major**; a mismatch that a **one-tailed** test would resolve is downgraded to
  an **info** note (confirm the test was one-sided).
- **GRIM / GRIMMER.** A reported mean (GRIM) and mean+SD (GRIMMER) of an
  integer-item measure over N observations must be achievable; an impossible
  value is a **major** (use `--grim-scale` for summed multi-item scales).
- **SPRITE bound.** When a scale range is stated (e.g. "1-5 scale"), checks the
  reported SD does not exceed the maximum possible SD for that mean and range —
  an infeasible SD is a **major**.
- **Confidence intervals.** The point estimate must lie within its CI
  (**blocker** if not); for a labelled ratio/difference, the CI's exclusion of
  the null must agree with a co-reported p (**major** mismatch).
- **Percentage sums.** A list of ≥3 percentages presented as a partition that
  does not sum to ~100% (**major**).
- **Subgroup Ns.** Subgroup counts that do not sum to the stated total N
  (**major**).
- **Effect-size plausibility.** `|r|>1`, negative df → **blocker**.

Every run carries a `caveat`: these are TRIGGER signals for manual review, not a
final arbiter or proof of misconduct — innocent causes include rounding, an
undisclosed multiple-comparison correction (statcheck does not recognise these),
copy-paste slips, or a different N. GRIM/GRIMMER/SPRITE apply to integer-item
scales only (false-positive risk on continuous measures).

## Judgement layer

For heterogeneity, base-rate, or effect-size *plausibility* that needs domain
reasoning (not arithmetic), use the `stats-checker` agent — but it calls this
script for the arithmetic and never overrides a deterministic impossibility.

## Invariant

A clean run means "no inconsistency detected in the machine-readable inline
statistics", not "the statistics are correct". Prose-only statistics the regex
cannot parse are reported as `not machine-checkable`, not as passing.
