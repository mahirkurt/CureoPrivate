#!/usr/bin/env python3
"""Context-economy P3 — synthetic 40-paper offline eval.

No live MCP, no copyrighted dumps. Simulates PRISMA search → screen → cite/skip
against the working-set ledger + Completeness Gate v2 helpers landed in P0–P2.

Metrics
-------
  skip_silent_rate
      |{include_set ∩ neither cited nor skipped_with_reason}| / |include_set|
      (= Gate v2 uncovered / include_set). Floor when ledger used correctly: **0.0**.

  cite_coverage
      |cited| / |include_set|  (strict cite rate).

  cite_coverage_gate_v2
      cited_or_skipped_with_reason / include_set  (aligned with Completeness Gate v2).

  dump_chars_in_context (proxy)
      count of simulated oversized payloads that would fire retrieve-don't-dump
      (fulltext ≥3 KB / bulk ≥8 KB) — never counts real copyrighted bodies.

Scenarios (fixture ``context-economy-40.json``)
  * correct_ledger — every gold include cited or skip_reasoned → silent=0, Gate pass
  * silent_skips   — planted uncovered IDs → coverage_gate must list them
  * dump_pressure  — oversized payload table → RDD trigger count

Usage:
  python3 skills/medical-research/evals/context_economy_synth.py
  python3 hooks/test_hooks.py   # imports run_eval via _context_economy_p3_cases
  python3 tests/run_suites.py   # GATES entry

Exit: 0 = floors met · 1 = assertion failure · 2 = setup error.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
FIXTURE = EVAL_DIR / "context-economy-40.json"
PLUGIN_ROOT = EVAL_DIR.parent.parent.parent
HOOKS = PLUGIN_ROOT / "hooks"

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def load_fixture(path: Path = FIXTURE) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"missing fixture: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "evidentia.context_economy_synth.v1":
        raise ValueError(f"unexpected schema: {data.get('schema')}")
    return data


def _record_key(paper: dict) -> str:
    kind = str(paper.get("id_kind") or "id").lower()
    rid = str(paper.get("id") or "").strip()
    if kind == "doi":
        rid = rid.lower()
    elif kind == "nct":
        rid = rid.upper()
    return f"{kind}:{rid}" if kind != "id" else rid


def build_identified_ws(fixture: dict) -> dict:
    """Simulate P1/P2 search hits → ledger status=identified for all papers."""
    sys.path.insert(0, str(HOOKS))
    import working_set_ledger as wsl  # noqa: E402

    rid = fixture.get("run_id") or "ce40synth0001"
    ws = wsl.empty_working_set(rid)
    for paper in fixture.get("papers") or []:
        key_kind = str(paper.get("id_kind") or "pmid").lower()
        hit = {
            "id": paper["id"],
            "id_kind": key_kind,
            "title": paper.get("title") or "",
            "sources": ["synth_search"],
        }
        wsl.upsert_identified(ws, hit, phase="P1", source="synth_search")
    return ws


def apply_screening(ws: dict, fixture: dict) -> None:
    """Gold include → included; non-gold → skipped with reason (screened out)."""
    sys.path.insert(0, str(HOOKS))
    import working_set_ledger as wsl  # noqa: E402

    gold = set(fixture.get("gold_include") or [])
    for key, rec in list((ws.get("records") or {}).items()):
        if key in gold:
            wsl.set_status(ws, key, "included", phase="P3")
        else:
            wsl.set_status(
                ws, key, "skipped",
                skip_reason="screened_out_eligibility",
                phase="P3",
            )


def apply_outcomes(
    ws: dict,
    *,
    cite: list[str],
    skip_reasoned: dict[str, str],
    silent_included: list[str] | None = None,
) -> None:
    """Promote include_set rows to cited / skipped_with_reason; leave silent alone."""
    sys.path.insert(0, str(HOOKS))
    import working_set_ledger as wsl  # noqa: E402

    silent = set(silent_included or [])
    for key in cite:
        if key in silent:
            continue
        wsl.set_status(
            ws, key, "cited", phase="P6",
            cited_chunk=f"synth::{key}::0",
        )
    for key, reason in (skip_reasoned or {}).items():
        if key in silent:
            continue
        wsl.set_status(ws, key, "skipped", skip_reason=reason, phase="P4")
    # silent_included: intentionally leave status=included (no cite, no reason)


def metrics(ws: dict, gate: str = "standard") -> dict:
    """Compute P3 metrics from a working-set ledger."""
    sys.path.insert(0, str(HOOKS))
    import working_set_ledger as wsl  # noqa: E402

    block = wsl.coverage_block(ws, gate=gate)
    n_inc = int(block.get("n_include") or 0)
    n_cited = int(block.get("n_cited") or 0)
    n_unc = len(block.get("uncovered") or [])
    skip_silent_rate = (n_unc / n_inc) if n_inc else 0.0
    cite_coverage = (n_cited / n_inc) if n_inc else 1.0
    return {
        "include_set": n_inc,
        "n_cited": n_cited,
        "n_skipped_reasoned": int(block.get("n_skipped_reasoned") or 0),
        "n_uncovered": n_unc,
        "uncovered_keys": [u.get("key") for u in (block.get("uncovered") or [])],
        "skip_silent_rate": round(skip_silent_rate, 4),
        "cite_coverage": round(cite_coverage, 4),
        "cite_coverage_gate_v2": float(block.get("coverage") or 0.0),
        "gate_pass": bool(block.get("pass")),
        "floor": block.get("floor"),
        "gate": block.get("gate"),
        "coverage_block": block,
    }


def simulate_dump_triggers(payloads: list[dict]) -> dict:
    """Proxy for dump_chars_in_context: count RDD hook firings on synthetic sizes."""
    triggers = 0
    expected_ok = True
    details = []
    for row in payloads or []:
        tool = row.get("tool") or "mcp__openathens__oa_fetch_fulltext"
        nchars = int(row.get("chars") or 0)
        want = bool(row.get("expect_trigger"))
        payload = {"tool_name": tool, "tool_result": "x" * nchars}
        p = subprocess.run(
            [sys.executable, str(HOOKS / "retrieve_dont_dump.py")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env={k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"},
        )
        out = (p.stdout or "").strip()
        fired = bool(out)
        if fired:
            try:
                j = json.loads(out)
                fired = bool(j.get("systemMessage"))
            except Exception:
                fired = True
        if fired:
            triggers += 1
        if fired != want:
            expected_ok = False
        details.append({
            "tool": tool,
            "chars": nchars,
            "fired": fired,
            "expect_trigger": want,
        })
    return {
        "dump_trigger_events": triggers,
        "dump_chars_proxy_ok": expected_ok,
        "details": details,
    }


def coverage_gate_reports_uncovered(ws: dict, uncovered_keys: list[str]) -> bool:
    """Drive coverage_gate UserPromptSubmit and require uncovered IDs in advisory."""
    sys.path.insert(0, str(HOOKS))
    import anamnesis_run as ar  # noqa: E402
    import working_set_ledger as wsl  # noqa: E402

    tmp = tempfile.mkdtemp()
    ws_dir = tempfile.mkdtemp()
    rid = ws.get("run_id") or "ce40synth0001"
    led_path = Path(tmp) / "ledger.json"
    led = ar.empty_ledger(rid)
    led_path.write_text(json.dumps(led), encoding="utf-8")

    prev = {
        "EVIDENTIA_WORKING_SET_DIR": os.environ.get("EVIDENTIA_WORKING_SET_DIR"),
        "CLAUDE_PROJECT_DIR": os.environ.get("CLAUDE_PROJECT_DIR"),
        "EVIDENTIA_ANAMNESIS_LEDGER": os.environ.get("EVIDENTIA_ANAMNESIS_LEDGER"),
        "EVIDENTIA_ANAMNESIS_NO_NETWORK": os.environ.get("EVIDENTIA_ANAMNESIS_NO_NETWORK"),
    }
    try:
        # Parent-process save_working_set must see the same override as the hook.
        os.environ["EVIDENTIA_WORKING_SET_DIR"] = ws_dir
        os.environ["CLAUDE_PROJECT_DIR"] = tmp
        os.environ["EVIDENTIA_ANAMNESIS_LEDGER"] = str(led_path)
        os.environ["EVIDENTIA_ANAMNESIS_NO_NETWORK"] = "1"
        wsl.save_working_set(ws)

        env = {k: v for k, v in os.environ.items()}
        env.pop("EVIDENTIA_COVERAGE_ENFORCE", None)

        p = subprocess.run(
            [sys.executable, str(HOOKS / "coverage_gate.py")],
            input=json.dumps({
                "hook_event_name": "UserPromptSubmit",
                "prompt": "/evidentia-synthesize finalize Completeness Gate",
            }),
            capture_output=True,
            text=True,
            env=env,
        )
        out = (p.stdout or "").strip()
        if not out:
            return False
        try:
            j = json.loads(out)
        except Exception:
            return False
        msg = (
            j.get("systemMessage")
            or (j.get("hookSpecificOutput") or {}).get("additionalContext")
            or ""
        )
        if "Completeness Gate" not in msg and "uncovered" not in msg.lower():
            return False
        for key in uncovered_keys:
            bare = key.split(":", 1)[-1] if ":" in key else key
            if key not in msg and bare not in msg:
                return False
        return True
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def run_scenario_correct(fixture: dict) -> tuple[dict, list[str]]:
    fails: list[str] = []
    floors = fixture.get("floors") or {}
    sc = (fixture.get("scenarios") or {}).get("correct_ledger") or {}
    ws = build_identified_ws(fixture)
    apply_screening(ws, fixture)
    apply_outcomes(
        ws,
        cite=list(sc.get("cite") or []),
        skip_reasoned=dict(sc.get("skip_reasoned") or {}),
    )
    # Gold-scoped metrics: Gate v2 include_set also counts screened_out skips;
    # P3 silent-skip / cite floors are defined over the gold include subset.
    m = metrics(ws, gate=str(floors.get("gate") or "standard"))
    gold = set(fixture.get("gold_include") or [])
    gold_m = _gold_scoped_metrics(ws, gold, gate=str(floors.get("gate") or "standard"))
    m["gold"] = gold_m

    if gold_m["skip_silent_rate"] > float(floors.get("skip_silent_rate_max_correct", 0.0)):
        fails.append(
            f"correct: skip_silent_rate={gold_m['skip_silent_rate']} "
            f"> max {floors.get('skip_silent_rate_max_correct')}"
        )
    if gold_m["cite_coverage_gate_v2"] < float(
        floors.get("gate_v2_coverage_min_correct", 0.9)
    ):
        fails.append(
            f"correct: gate_v2 coverage={gold_m['cite_coverage_gate_v2']} "
            f"< floor {floors.get('gate_v2_coverage_min_correct')}"
        )
    if not gold_m["gate_pass"]:
        fails.append("correct: Completeness Gate v2 should pass on gold include")
    if gold_m["n_uncovered"] != 0:
        fails.append(f"correct: uncovered={gold_m['uncovered_keys']} expected []")
    return {"scenario": "correct_ledger", "metrics": m, "gold_metrics": gold_m}, fails


def _gold_scoped_metrics(ws: dict, gold: set[str], gate: str) -> dict:
    """Restrict coverage_block denominator to the gold include subset."""
    sys.path.insert(0, str(HOOKS))
    import working_set_ledger as wsl  # noqa: E402

    # Build a virtual ws with only gold keys (statuses already applied).
    slim = {
        "run_id": ws.get("run_id"),
        "schema": ws.get("schema"),
        "records": {
            k: v for k, v in (ws.get("records") or {}).items() if k in gold
        },
    }
    return metrics(slim, gate=gate)


def run_scenario_silent(fixture: dict) -> tuple[dict, list[str]]:
    fails: list[str] = []
    floors = fixture.get("floors") or {}
    sc = (fixture.get("scenarios") or {}).get("silent_skips") or {}
    ws = build_identified_ws(fixture)
    apply_screening(ws, fixture)
    silent = list(sc.get("silent_included") or [])
    apply_outcomes(
        ws,
        cite=list(sc.get("cite") or []),
        skip_reasoned=dict(sc.get("skip_reasoned") or {}),
        silent_included=silent,
    )
    gold = set(fixture.get("gold_include") or [])
    gold_m = _gold_scoped_metrics(ws, gold, gate=str(floors.get("gate") or "standard"))

    min_silent = float(floors.get("skip_silent_rate_min_bad", 0.2))
    if gold_m["skip_silent_rate"] < min_silent:
        fails.append(
            f"silent: skip_silent_rate={gold_m['skip_silent_rate']} "
            f"< planted min {min_silent}"
        )
    min_unc = int(floors.get("uncovered_min_bad", 3))
    if gold_m["n_uncovered"] < min_unc:
        fails.append(
            f"silent: n_uncovered={gold_m['n_uncovered']} < planted min {min_unc}"
        )
    for key in silent:
        if key not in (gold_m.get("uncovered_keys") or []):
            fails.append(f"silent: planted {key} missing from uncovered")

    # coverage_gate must surface uncovered IDs in advisory text.
    if not coverage_gate_reports_uncovered(ws, silent):
        fails.append("silent: coverage_gate advisory did not list uncovered IDs")

    return {
        "scenario": "silent_skips",
        "gold_metrics": gold_m,
        "planted_silent": silent,
    }, fails


def run_scenario_dump(fixture: dict) -> tuple[dict, list[str]]:
    fails: list[str] = []
    floors = fixture.get("floors") or {}
    sc = (fixture.get("scenarios") or {}).get("dump_pressure") or {}
    dump = simulate_dump_triggers(list(sc.get("dump_payloads") or []))
    min_trig = int(floors.get("dump_trigger_min", 3))
    if dump["dump_trigger_events"] < min_trig:
        fails.append(
            f"dump: trigger_events={dump['dump_trigger_events']} < min {min_trig}"
        )
    if not dump["dump_chars_proxy_ok"]:
        fails.append("dump: per-payload expect_trigger mismatch vs retrieve_dont_dump")
    return {"scenario": "dump_pressure", "dump": dump}, fails


def run_eval(fixture_path: Path | None = None) -> tuple[int, dict]:
    """Run all P3 scenarios. Returns (exit_code, report)."""
    try:
        fixture = load_fixture(fixture_path or FIXTURE)
    except Exception as exc:
        return 2, {"error": str(exc)}

    # Sanity: fixture shape
    papers = fixture.get("papers") or []
    gold = fixture.get("gold_include") or []
    if len(papers) != int(fixture.get("n_papers") or 0):
        return 2, {"error": "n_papers != len(papers)"}
    if not (12 <= len(gold) <= 15):
        return 2, {"error": f"gold_include size {len(gold)} not in 12–15"}
    keys = {_record_key(p) for p in papers}
    missing = [g for g in gold if g not in keys]
    if missing:
        return 2, {"error": f"gold keys not in papers: {missing}"}

    report: dict = {
        "schema": "evidentia.context_economy_synth.report.v1",
        "n_papers": len(papers),
        "n_gold_include": len(gold),
        "floors": fixture.get("floors"),
        "scenarios": {},
    }
    all_fails: list[str] = []

    for runner in (run_scenario_correct, run_scenario_silent, run_scenario_dump):
        result, fails = runner(fixture)
        report["scenarios"][result["scenario"]] = result
        all_fails.extend(fails)

    report["fails"] = all_fails
    report["pass"] = not all_fails
    return (0 if not all_fails else 1), report


def main() -> int:
    code, report = run_eval()
    if code == 2:
        print(f"{RED}SETUP{RESET}  {report.get('error')}")
        return 2

    floors = report.get("floors") or {}
    print(
        f"context-economy P3 synth — {report['n_papers']} papers, "
        f"gold_include={report['n_gold_include']}"
    )

    correct = (report.get("scenarios") or {}).get("correct_ledger") or {}
    gm = correct.get("gold_metrics") or {}
    print(
        f"  correct_ledger: skip_silent_rate={gm.get('skip_silent_rate')} "
        f"(floor≤{floors.get('skip_silent_rate_max_correct', 0)})  "
        f"gate_v2={gm.get('cite_coverage_gate_v2')} "
        f"(floor≥{floors.get('gate_v2_coverage_min_correct', 0.9)})  "
        f"cite_coverage={gm.get('cite_coverage')}"
    )

    silent = (report.get("scenarios") or {}).get("silent_skips") or {}
    sm = silent.get("gold_metrics") or {}
    print(
        f"  silent_skips:   skip_silent_rate={sm.get('skip_silent_rate')}  "
        f"uncovered={sm.get('n_uncovered')} {sm.get('uncovered_keys')}  "
        f"coverage_gate lists uncovered=yes"
    )

    dump = ((report.get("scenarios") or {}).get("dump_pressure") or {}).get("dump") or {}
    print(
        f"  dump_pressure:  dump_trigger_events={dump.get('dump_trigger_events')} "
        f"(floor≥{floors.get('dump_trigger_min', 3)})"
    )

    if report.get("fails"):
        for f in report["fails"]:
            print(f"  {RED}FAIL{RESET}  {f}")
        print(f"\n{RED}P3 EVAL FAILED ({len(report['fails'])}){RESET}")
        return 1

    print(f"\n{GREEN}P3 EVAL PASSED{RESET}  "
          f"{DIM}silent_skip_rate=0 on correct ledger; "
          f"coverage_gate surfaces uncovered; RDD proxy ok{RESET}")
    return 0


def test_context_economy_p3():
    """pytest entry — same assertions as the standalone runner."""
    code, report = run_eval()
    assert code != 2, report.get("error")
    assert code == 0, report.get("fails")


if __name__ == "__main__":
    sys.exit(main())
