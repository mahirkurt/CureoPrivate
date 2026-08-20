# Context-economy P3 — synthetic 40-paper eval

Offline, deterministic, **no live MCP**, **no copyrighted dumps**. Synthetic PMIDs /
DOIs / NCT IDs and titles only.

## What it measures

| Metric | Definition | Floor (correct ledger) |
|---|---|---|
| `skip_silent_rate` | uncovered / gold `include_set` — included/extracted with neither `cited` nor `skipped`+`skip_reason` | **0.0** |
| `cite_coverage` | `n_cited` / gold `include_set` | informational |
| `cite_coverage_gate_v2` | `cited_or_skipped_with_reason` / gold `include_set` (Completeness Gate v2) | **≥ 0.90** (standard) |
| `dump_chars_in_context` (proxy) | count of synthetic oversized payloads that fire `retrieve_dont_dump` (3 KB fulltext / 8 KB bulk) | ≥ 3 triggers in `dump_pressure` |

## Scenarios (`context-economy-40.json`)

1. **`correct_ledger`** — P0–P2 helpers used correctly: every gold include is `cited` or
   `skipped` with reason → `skip_silent_rate == 0`, Gate v2 passes.
2. **`silent_skips`** — three gold IDs left as bare `included` → Gate reports them in
   `uncovered[]`; `coverage_gate` UserPromptSubmit advisory must name those IDs.
3. **`dump_pressure`** — table of synthetic char sizes vs `retrieve_dont_dump` thresholds.

Gold include size: **14** of **40** papers (within the 12–15 band).

## How it runs

```bash
# standalone
python3 skills/medical-research/evals/context_economy_synth.py

# via hook pack (imports run_eval)
python3 hooks/test_hooks.py

# CI entry (GATES)
python3 tests/run_suites.py
```

Skill version stays **9.0.6** — P3 adds measurement only; doctrine text is unchanged
(P0–P2 already shipped Completeness Gate v2 + ledger + coverage_gate).

## Anamnesis exclusivity

The bibliographic working-set (`ledger.json` under `evidentia-run/<id>/`) is **not**
merged with the Anamnesis doc_id ledger. This eval never calls Anamnesis MCP and never
touches mevzuat.
