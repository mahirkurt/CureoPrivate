# `audit-diff` — Calibration Delta CI Gate

> Status: v0.3.1-alpha.1 and onward · Stable schema v1.0

`audit-diff` is the **CI gate for design-system regressions**. Given
two schema-v1.0 audit reports (one baseline, one current), it
classifies every gate transition and surfaces sample-level resolved /
introduced failures. Use it to catch silent quality drift before it
accumulates.

## When to use

- **PR gate**: compare the audit produced from the PR branch against
  the audit from `main`. Fail the build on any regression.
- **Release gate**: compare a release-candidate bundle against the
  last shipped release; require the regression count to be zero before
  cutting the tag.
- **Post-incident triage**: re-run `audit-diff` over the 14-day
  baseline-to-incident window to localize exactly which gate failed
  first.

## End-to-end PR-gate workflow

```bash
# 1. Materialize the baseline audit from main
git checkout main
python3 scripts/publish_audit.py \
    --library-registry library-registry.json \
    --static-only --output-format json \
    --output audits/baseline.json

# 2. Materialize the current audit from the PR
git checkout feature/new-tokens
python3 scripts/publish_audit.py \
    --library-registry library-registry.json \
    --static-only --output-format json \
    --output audits/current.json

# 3. Compute the diff (Markdown for PR comment, JSON for CI)
python3 scripts/audit_diff.py \
    --baseline audits/baseline.json \
    --current  audits/current.json \
    --output pr-diff.md \
    --output-format markdown \
    --verbose

# Exit code: 0 if no regression, 1 if any regression
echo $?
```

## Transition classification

The classifier uses a **severity-aware result ordinal** where higher =
healthier:

| Result   | Ordinal | Comment                                  |
|----------|---------|------------------------------------------|
| `PASS`   | 5       | Healthiest                               |
| `N_A`    | 4       | Neutral (gate doesn't apply)             |
| `SKIP`   | 3       | Neutral (gate skipped explicitly)        |
| `FAIL`   | 0–2     | error severity: 0, warn: 1, info: 2     |
| `MISSING`| 0       | Gate absent in current report            |

A transition is classified as:

- **regression**: `current_ordinal < baseline_ordinal`
- **improvement**: `current_ordinal > baseline_ordinal`
- **no_change**: `current_ordinal == baseline_ordinal`
- **new**: gate absent from baseline, present in current
- **removed**: gate present in baseline, absent from current

## Exit-code semantics

| `--fail-on` | Behavior                                              |
|-------------|-------------------------------------------------------|
| `regression` (default) | Exit 1 on any regression, 0 otherwise        |
| `any-change` | Exit 1 on any movement (regression, improvement, new, or removed) |
| `never`      | Always exit 0 (report-only mode for comments)   |

## Sample-level diffs

When both baseline and current carry `samples` for the same gate, the
diff computes set differences on the message strings:

```json
{
  "gate_id": 102,
  "name": "DTCG alias resolvability",
  "classification": "regression",
  "samples_resolved":   ["color.x → was unresolved"],
  "samples_introduced": ["color.y → unresolved alias {z.w}"]
}
```

`samples_resolved` are failures that existed in the baseline but no
longer appear in the current (fixed); `samples_introduced` are new
failures that did not exist in the baseline (regressions).

## Empirical validation

Düstur build, synthetic regression test:

| Step                            | Score | Band       | Exit |
|---------------------------------|-------|------------|------|
| Baseline (clean Düstur)         | 10.0  | EXEMPLARY  | —    |
| Inject 1 broken alias           | 7.2   | STRONG     | —    |
| `audit-diff` baseline → current | Δ −2.8 | regressed | 1    |
| Restore alias                   | 10.0  | EXEMPLARY  | —    |
| `audit-diff` baseline → current | Δ 0   | stable     | 0    |

The CI gate semantic is correct: exit 1 only when a regression exists.
