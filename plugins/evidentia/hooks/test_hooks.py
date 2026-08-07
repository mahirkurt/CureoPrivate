#!/usr/bin/env python3
"""Deterministic regression tests for the evidentia hook layer.

Run: python3 hooks/test_hooks.py   (exit 0 = all pass, 1 = a failure)
Also collectable by pytest — see test_hook_layer() at the bottom. Before 2026-08-07
this module was named test_*.py but exposed no pytest-visible test, so a repo-wide
`pytest` reported "no tests ran" and EXITED 0: a false green over 21 real assertions.

Covers the three enforcement hooks with deny/allow/edge cases so the guard logic (least-privilege
whitelist, D1/D2/D6 broken-tool avoidance, retrieve-don't-dump threshold, credential preflight)
is regression-locked alongside the skill-level integrity gates.

The preflight cases derive their key list from fleet.lock.json rather than hardcoding it.
That is deliberate: the 2026-08-07 audit found the hook hardcoding SIX gated connectors
while the fleet had SEVEN, and a hardcoded test list would have ratified the same gap.
PREFLIGHT_ENV disables the network probe so the suite stays offline and deterministic.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def gated_from_lock():
    """{connector: env_var} straight from the generated lock — single source of truth."""
    with open(os.path.join(ROOT, "fleet.lock.json"), encoding="utf-8") as fh:
        lock = json.load(fh)
    return {s["name"]: s["auth_env"] for s in lock["servers"] if s.get("auth_env")}


def run(script, payload, env=None):
    e = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    if env:
        e.update(env)
    p = subprocess.run([sys.executable, os.path.join(HERE, script)],
                       input=json.dumps(payload), capture_output=True, text=True, env=e)
    out = p.stdout.strip()
    return p.returncode, (json.loads(out) if out else None)


def decision(j):
    if not j:
        return "ALLOW"
    hso = j.get("hookSpecificOutput", {})
    if hso.get("permissionDecision") == "deny":
        return "DENY"
    if j.get("systemMessage") or hso.get("additionalContext"):
        return "MSG"
    return "ALLOW"


CASES_GUARD = [
    ("mcp__claude_ai_semantic-scholar__ask_pipeworx", "DENY"),
    ("mcp__nih-clinicaltables__deep_research", "DENY"),
    ("mcp__claude_ai_iuphar-gtopdb__polymarket_edges", "DENY"),
    ("mcp__claude_ai_nlm-rxnorm__rxnorm_interactions", "DENY"),      # D1
    ("mcp__nlm-rxnorm__rxnorm_related", "DENY"),                     # D2/D4
    ("mcp__claude_ai_med-terminologies__icd11_search", "DENY"),      # D6
    ("mcp__claude_ai_openfda__icd11_search", "ALLOW"),               # working icd11
    ("mcp__claude_ai_nih-clinicaltables__drugs", "ALLOW"),
    ("mcp__claude_ai_nlm-rxnorm__rxnorm_search", "ALLOW"),
    ("mcp__claude_ai_semantic-scholar__search_papers", "ALLOW"),
    ("mcp__claude_ai_anamnesis__forget_document", "ALLOW"),          # not 'forget'
    ("mcp__claude_ai_PubMed__search_articles", "ALLOW"),
    ("Read", "ALLOW"),
    # D7 — argument-level guard. `search_mevzuat` without an explicit page_size (or with >20)
    # is a call that CANNOT succeed: the server default of 25 exceeds the bedesten cap of 20 and
    # the upstream returns the error as plain text with no isError, so the model would read a
    # failure as data. Measured 2026-08-07: page_size=20 → 938 results; bare call → error string.
    ("mcp__mevzuat-bilgisi__search_mevzuat", "DENY", {"phrase": "ilaç"}),
    ("mcp__mevzuat-bilgisi__search_mevzuat", "DENY", {"phrase": "ilaç", "page_size": 25}),
    ("mcp__mevzuat-bilgisi__search_mevzuat", "ALLOW", {"phrase": "ilaç", "page_size": 20}),
    ("mcp__mevzuat-bilgisi__search_mevzuat", "ALLOW", {"phrase": "ilaç", "page_size": 5}),
    # Sibling tools go through the mevzuat.gov.tr path, accept 25, and must NOT be caught.
    ("mcp__mevzuat-bilgisi__search_khk", "ALLOW", {"mevzuat_adi": "ilaç"}),
    ("mcp__mevzuat-bilgisi__search_tuzuk", "ALLOW", {"mevzuat_adi": "ilaç", "page_size": 25}),
]

# retrieve-don't-dump scenarios: (tool_name, result_chars, expected_decision, message_substring, label).
#
# SIZE — not the tool name — is the trigger (fixed 2026-08-07). The assertion that used to live
# here demanded SILENCE for a 99,999-char non-fulltext result, i.e. it encoded the very defect the
# hook exists to prevent. The three "bulk" sizes below are the ones MEASURED on the live fleet that
# day, each of which the old name-keyed hook let through without a word.
CASES_RDD = [
    ("mcp__claude_ai_openathens__oa_fetch_fulltext", 8000, "MSG", "ingest_document",
     "fulltext over threshold"),
    ("mcp__claude_ai_openathens__oa_fetch_fulltext", 5, "ALLOW", None,
     "fulltext under threshold stays silent"),
    ("mcp__annas-reader__read_document", 8000, "MSG", "ingest_document",
     "annas read_document (real fleet name, was missing from the list)"),
    ("mcp__openfda__openfda_search", 254891, "MSG", "DARALT",
     "openfda 250KB bulk dump must warn and say narrow-the-query"),
    ("mcp__titck__search_drugs", 78837, "MSG", "DARALT", "titck 79KB bulk dump must warn"),
    ("mcp__anamnesis__semantic_search", 50444, "MSG", "DARALT", "anamnesis 50KB bulk dump must warn"),
    ("mcp__globocan__gco_list_cancers", 4596, "ALLOW", None,
     "normal-sized result stays silent (hook must not become noise)"),
    ("Read", 999999, "ALLOW", None, "non-MCP tools are out of scope"),
]


def main():
    fails = 0

    for case in CASES_GUARD:
        tool, want = case[0], case[1]
        payload = {"tool_name": tool}
        if len(case) > 2:                     # argument-level cases (D7) carry a tool_input
            payload["tool_input"] = case[2]
        _, j = run("guard_tool_call.py", payload)
        got = decision(j)
        if got != want:
            fails += 1
            print(f"FAIL guard {tool} {case[2] if len(case) > 2 else ''}: {got} != {want}")

    # disable flag
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".claude"))
    open(os.path.join(tmp, ".claude", "evidentia-guard.off"), "w").close()
    _, j = run("guard_tool_call.py",
               {"tool_name": "mcp__claude_ai_semantic-scholar__ask_pipeworx"},
               {"CLAUDE_PROJECT_DIR": tmp})
    if decision(j) != "ALLOW":
        fails += 1
        print("FAIL guard disable-flag")

    # malformed → fail-open
    p = subprocess.run([sys.executable, os.path.join(HERE, "guard_tool_call.py")],
                       input="{bad", capture_output=True, text=True)
    if p.returncode != 0 or p.stdout.strip():
        fails += 1
        print("FAIL guard fail-open")

    # retrieve-don't-dump — table-driven so the assertion count is DERIVED, never hand-counted.
    for tool, nchars, want, must_contain, label in CASES_RDD:
        _, j = run("retrieve_dont_dump.py", {"tool_name": tool, "tool_result": "x" * nchars})
        got = decision(j)
        ok = got == want
        if ok and must_contain:
            ok = must_contain in (j or {}).get("systemMessage", "")
        if not ok:
            fails += 1
            print(f"FAIL rdd {label}: {got} != {want}"
                  + (f" (mesaj '{must_contain}' içermiyor)" if got == want else ""))

    # session preflight — key list comes from fleet.lock.json, never hardcoded
    gated = gated_from_lock()
    allenv = {v: "x" for v in gated.values()}
    allenv["EVIDENTIA_PREFLIGHT_NO_PROBE"] = "1"   # offline + deterministic

    _, j = run("session_preflight.py", {"hook_event_name": "SessionStart"}, allenv)
    if decision(j) != "ALLOW":
        fails += 1
        print("FAIL preflight all-present-silent")

    # EVERY gated connector must be covered. This loop is the regression lock for
    # audit finding MAJOR-2: titck-cache (renamed `titck` 2026-08-07) was gated in
    # .mcp.json but absent from the
    # hook's map, so its missing key warned nobody. Dropping any one key must warn,
    # and the warning must NAME that connector.
    for name, var in sorted(gated.items()):
        part = dict(allenv)
        part[var] = ""
        _, j = run("session_preflight.py", {"hook_event_name": "SessionStart"}, part)
        if decision(j) != "MSG":
            fails += 1
            print(f"FAIL preflight missing-warns[{name}]: {var} eksikken sessiz kaldı")
            continue
        ctx = j.get("hookSpecificOutput", {}).get("additionalContext", "")
        if name not in ctx or var not in ctx:
            fails += 1
            print(f"FAIL preflight names-connector[{name}]: uyarı '{name}'/'{var}' içermiyor")

    # Every term is DERIVED from a table or the lock — no hand-maintained magic number. The old
    # literal `7` silently understated the headline as soon as assertions were added or removed,
    # which is the same stale-count drift this audit found in the connector docs.
    #   3 = guard disable-flag + guard fail-open + preflight all-present-silent
    total = len(CASES_GUARD) + len(CASES_RDD) + 3 + 2 * len(gated)
    if fails:
        print(f"\n{fails}/{total} FAILED")
        return 1
    print(f"ALL {total} HOOK TESTS PASSED")
    return 0


def test_hook_layer():
    """pytest entry point.

    This module is named test_*.py, so pytest collects the FILE regardless. Without a
    pytest-visible test function it reported "no tests ran" and exited 0 — a false green
    that hid 21 real assertions from any repo-wide `pytest` run (2026-08-07 audit MINOR-3).
    Delegating to main() keeps ONE implementation: the standalone runner and pytest
    execute the same assertions, so the two paths can never disagree.
    """
    assert main() == 0, "evidentia hook regresyon paketi düştü (ayrıntı için stdout'a bak)"


if __name__ == "__main__":
    sys.exit(main())
