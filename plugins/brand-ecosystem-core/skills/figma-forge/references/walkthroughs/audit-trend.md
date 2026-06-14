# `audit-trend` — Longitudinal Calibration Drift

> Status: v0.3.1 GA · Stable schema v1.0

`audit-trend` analyzes **N audit reports** as a time series and
surfaces drift, score volatility, band frequency, and per-gate
stability. Where `audit-diff` compares two snapshots, `audit-trend`
compares **N** — typically a rolling 30-day or 90-day window of daily
audits.

## When to use

- **Quarterly DS health review** — render a 90-day dashboard and walk
  it with the platform team
- **Calibration auditing** — high CDI (σ/μ > 0.10) means the audit
  itself is noisy or the design system is unstable; investigate
- **Flapping-gate detection** — gates that swing PASS↔FAIL repeatedly
  are usually signaling either a flaky check or a recurring author
  habit; identify them, then either fix the check or the habit
- **MTTF (Mean Time To Fix) targeting** — quantify how many audit
  cycles it takes for a regression to be resolved; set team SLOs
  against MTTF

## End-to-end dashboard workflow

```bash
# Render a 30-day HTML dashboard from daily audits in audits/
python3 scripts/audit_trend.py \
    --glob 'audits/*.json' \
    --since 2026-04-27 \
    --until 2026-05-27 \
    --output trend-30d.html \
    --output-format html \
    --verbose

# Or a Markdown PR comment
python3 scripts/audit_trend.py \
    --glob 'audits/*.json' \
    --output trend-30d.md \
    --output-format markdown

# Or schema-v1.0 JSON for downstream tooling
python3 scripts/audit_trend.py \
    --glob 'audits/*.json' \
    --output trend-30d.json \
    --output-format json
```

## Key metrics

| Metric                          | Formula / source                              | Interpretation                              |
|---------------------------------|-----------------------------------------------|---------------------------------------------|
| **Score mean (μ)**              | `mean(score over window)`                     | Average DS quality                          |
| **Score stdev (σ)**             | `population_stdev(score)`                     | Score volatility                            |
| **Score slope per audit**       | OLS slope of score over audit index           | Per-audit improvement / regression rate     |
| **Score slope per day**         | OLS slope of score over days since window start | Per-day improvement / regression rate     |
| **Calibration Drift Index**     | σ / μ                                          | Relative volatility; **0 = perfectly stable** |
| **Band frequency**              | Counts per EXEMPLARY / EXCELLENT / … / FAILING | Distribution of quality bands               |
| **Per-gate fail ratio**         | `fail_count / observations`                    | How often this gate fails                   |
| **Per-gate P→F / F→P transitions** | Adjacent-pair counts                        | Stability signature                         |
| **Mean Time To Fix (MTTF)**     | `mean(audits-between-FAIL-and-PASS)`           | How fast regressions get fixed              |

## Calibration Drift Index thresholds

| CDI Range  | Classification        | Action                                     |
|------------|------------------------|--------------------------------------------|
| `0`        | perfectly stable       | No action; this is the goal                |
| `0–0.02`   | stable                 | Healthy; monitor                           |
| `0.02–0.05`| minor drift            | Routine maintenance                        |
| `0.05–0.10`| moderate drift         | Investigate root cause                     |
| `> 0.10`   | high drift             | Escalate; `--fail-on-high-drift` triggers  |

## Per-gate stability labels

| Label          | Trigger                                                  |
|----------------|----------------------------------------------------------|
| **stable**     | No P→F and no F→P transitions                            |
| **improving**  | F→P transitions > P→F transitions                        |
| **regressing** | P→F transitions > F→P transitions                        |
| **flapping**   | P→F transitions == F→P transitions > 0                   |
| **absent**     | Gate never observed in the window                        |

A gate labeled "flapping" with high fail_ratio is the highest-priority
investigation target — it costs CI cycles, signals an unhealthy
calibration, and demoralizes contributors who fix the same thing
repeatedly.

## HTML dashboard

The HTML output is a **single-file, dependency-free dashboard**:

- Embedded SVG sparkline of score over time with a dashed reference
  line at score=8 (STRONG threshold)
- Band frequency bars colored by ordinal
- Sortable-but-static gate stability table with color-coded labels
- Dark theme matching modern OS appearance

Drop the file directly into a CI artifact server or GitHub Pages — no
JavaScript, no CDN dependencies, no external fonts.

## Schema v1.0

```jsonc
{
  "schema_version": "1.0",
  "report_timestamp": "2026-05-27T03:00:00Z",
  "window": {
    "start": "2026-04-27T12:00:00Z",
    "end":   "2026-05-06T12:00:00Z",
    "days": 9.0,
    "audit_count": 10
  },
  "score_series": {
    "mean":   9.39,
    "stdev":  0.93,
    "min":    7.2,
    "max":    10.0,
    "slope_per_audit": 0.0964,
    "slope_per_day":   0.0964
  },
  "calibration_drift_index": 0.0994,
  "band_frequency": {
    "EXEMPLARY": 7,
    "EXCELLENT": 2,
    "STRONG":    1
  },
  "points":   [ /* one entry per audit */ ],
  "gates":    [ /* one entry per gate */ ]
}
```
