# Benchmark Suite (v8.2)

**Loaded:** dev / pre-release. **Recreated v8.2.0 (UP-004).**
The executable harness lives in `../evals/`. This file documents it.

## 1. Deterministic integrity gates — `evals/check_integrity.py`
- **G-REF** every references/*.md cited by SKILL.md exists (blocking).
- **G-ALWAYS** the six Adım 0 always-load files present (blocking).
- **G-CONN** every connector in connector-registry resolves to a manifest runtime entry (blocking).
- **G-VERSION** manifest ↔ SKILL.md version agreement (non-blocking).
Run: `python3 evals/check_integrity.py` (exit 0 = pass, 1 = blocked, 3 = IO error).

## 2. Regression queries — `evals/benchmark-queries.json`
10 queries, each asserting expected axis activation + connector set + sections (and handoff where
relevant). Run qualitatively via SKILL.md (Claude.ai has no subagents): for each, confirm the named
axes fire and the named connectors are called. See `benchmark-protocol.md` for the procedure.

## 3. Pass criteria (release gate)
All blocking integrity gates PASS · all 10 regression queries activate their expected axes/connectors
· copyright gate documented · no reader-facing tooling leakage (report-presentation.md G1–G7).
