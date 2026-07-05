#!/usr/bin/env python3
"""Deterministic regression tests for the evidentia hook layer.

Run: python3 hooks/test_hooks.py   (exit 0 = all pass, 1 = a failure)

Covers the three enforcement hooks with deny/allow/edge cases so the guard logic (least-privilege
whitelist, D1/D2/D6 broken-tool avoidance, retrieve-don't-dump threshold, credential preflight)
is regression-locked alongside the skill-level integrity gates.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


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
]


def main():
    fails = 0

    for tool, want in CASES_GUARD:
        _, j = run("guard_tool_call.py", {"tool_name": tool})
        got = decision(j)
        if got != want:
            fails += 1
            print(f"FAIL guard {tool}: {got} != {want}")

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

    # retrieve-don't-dump
    _, j = run("retrieve_dont_dump.py",
               {"tool_name": "mcp__claude_ai_openathens__oa_fetch_fulltext", "tool_result": "x" * 8000})
    if decision(j) != "MSG":
        fails += 1
        print("FAIL rdd large-fulltext")
    _, j = run("retrieve_dont_dump.py",
               {"tool_name": "mcp__claude_ai_openathens__oa_fetch_fulltext", "tool_result": "short"})
    if decision(j) != "ALLOW":
        fails += 1
        print("FAIL rdd small")
    _, j = run("retrieve_dont_dump.py",
               {"tool_name": "mcp__claude_ai_PubMed__search_articles", "tool_result": "y" * 99999})
    if decision(j) != "ALLOW":
        fails += 1
        print("FAIL rdd non-fulltext")

    # session preflight
    allenv = {k: "x" for k in ("OPENATHENS_MCP_API_KEY", "ANAMNESIS_MCP_API_KEY",
              "OPENFDA_MCP_API_KEY", "EVIDENTIA_KB_MCP_API_KEY", "ANNAS_MCP_API_KEY",
              "YOK_AKADEMIK_MCP_API_KEY")}
    _, j = run("session_preflight.py", {"hook_event_name": "SessionStart"}, allenv)
    if decision(j) != "ALLOW":
        fails += 1
        print("FAIL preflight all-present-silent")
    part = dict(allenv)
    part["OPENATHENS_MCP_API_KEY"] = ""
    _, j = run("session_preflight.py", {"hook_event_name": "SessionStart"}, part)
    if decision(j) != "MSG":
        fails += 1
        print("FAIL preflight missing-warns")

    total = len(CASES_GUARD) + 8
    if fails:
        print(f"\n{fails}/{total} FAILED")
        return 1
    print(f"ALL {total} HOOK TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
