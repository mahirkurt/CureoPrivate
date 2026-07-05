# Golden regression cases (deterministic axes)

These are the known-answer cases the unit tests assert. Extend them as new
signal patterns are added. All are stdlib-only and network-free.

## Axis C — statcheck (recomputed two-sided p)

| Reported | Recomputed p | Expected |
|---|---|---|
| `t(38)=2.50, p=0.20` | ≈0.017 | blocker (decision-changing) |
| `F(2,40)=5.00, p=0.30` | ≈0.011 | blocker (decision-changing) |
| `χ²(1)=10.0, p=0.50` | ≈0.0016 | blocker (decision-changing) |
| `t(38)=2.50, p=0.017` | ≈0.017 | clean |

## Axis C — GRIM / effect size

| Case | Expected |
|---|---|
| `Mean = 3.15, N = 4` | GRIM-impossible (major) |
| `r = 1.7` | impossible correlation (blocker) |

## Axis B — grounding

| Case | Expected |
|---|---|
| `prevalence was 34% in 2019.` (no marker) | unsourced-claim (blocker) |
| `12 percent improvement [3].` | grounded |

## Axis D — hallucination signals

| Case | Expected |
|---|---|
| `doi: not-a-doi` | malformed-doi (blocker) |
| `PMID: 1234567890` | suspicious-pmid (major) |
| `this proves definitively` | over-certainty (major) |

## Axis G — Turkish

| Case | Expected |
|---|---|
| `p < 0.05` in Turkish text | decimal-dot-p-value (blocker/error) |
| `inceledik` | first-person-register (major) |
| `calisma` | missing-diacritic (major) |
