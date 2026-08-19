# Benchmark Protocol (v8.2)

**Loaded:** dev / pre-release. **Recreated v8.2.0 (UP-004).**

## 1. Integrity gates (deterministic, every release)
```
python3 evals/check_integrity.py            # all blocking gates
python3 evals/check_integrity.py --refs     # individual gate
```
Block release on exit 1. These are the gates that would have caught the v8.0/8.1
missing-reference-file regression (22 cited, 6 existing).

## 2. Regression procedure (qualitative, Claude.ai-compatible)
For each query in `evals/benchmark-queries.json`:
1. Read SKILL.md; run the query as the skill would.
2. Record which 0.5 axes fired and which connectors were called.
3. Assert against `expect_axes` / `expect_connectors` / `expect_sections` (+ `expect_handoff`).
4. A miss = the classifier or wiring drifted → fix before release.

## 3. What each query guards
- Q1/Q5 — TR access (TİTCK structural, not Exa scraping).
- Q2/Q9 — AdisInsight REAL schema + regulatory history.
- Q3 — full-text cascade + copyright gate.
- Q4/Q9 — epidemiology axis 0.5.K (WHO GHO + ICD-11).
- Q8 — α-layer YÖK Akademik Turkish-KOL wiring (UP-005).
- Q10 — no-signal core + evidence-grading methodology.

## 4. Provenance & honesty
No fabricated results. A connector that returns null is logged in `gaps[]`, never silently dropped.
