#!/usr/bin/env python3
"""Deterministic regression tests for the evidentia hook layer.

Run: python3 hooks/test_hooks.py   (exit 0 = all pass, 1 = a failure)
Also collectable by pytest — see test_hook_layer() at the bottom. Before 2026-08-07
this module was named test_*.py but exposed no pytest-visible test, so a repo-wide
`pytest` reported "no tests ran" and EXITED 0: a false green over 21 real assertions.

Covers the three enforcement hooks with deny/allow/edge cases so the guard logic (least-privilege
whitelist, D1/D2 broken-tool avoidance, retrieve-don't-dump threshold, credential preflight)
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
import time

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
    ("mcp__claude_ai_med-terminologies__icd11_search", "ALLOW"),     # D6 retired — live ICD-11
    ("mcp__claude_ai_openfda__icd11_search", "ALLOW"),               # operator-owned icd11
    ("mcp__nlm-rxnorm__rxnorm_approximate", "DENY"),                 # allowlist: not §2.6
    ("mcp__nih-clinicaltables__npi_lookup", "DENY"),                 # allowlist: dump surface
    ("mcp__claude_ai_nih-clinicaltables__drugs", "ALLOW"),
    ("mcp__claude_ai_nlm-rxnorm__rxnorm_search", "ALLOW"),
    ("mcp__claude_ai_semantic-scholar__search_papers", "ALLOW"),
    ("mcp__claude_ai_anamnesis__forget_document", "DENY"),           # unscoped wipe
    ("mcp__claude_ai_PubMed__search_articles", "ALLOW"),
    ("Read", "ALLOW"),
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
    ("mcp__claude_ai_openathens__oa_fetch_pdf", 8000, "MSG", "ingest_document",
     "openathens original PDF tool is classified as fulltext"),
    ("mcp__annas-reader__read_document", 8000, "MSG", "ingest_document",
     "annas read_document (real fleet name, was missing from the list)"),
    ("mcp__annas-reader__download_document", 8000, "MSG", "ingest_document",
     "annas original-file tool is classified as fulltext"),
    ("mcp__openfda__openfda_search", 254891, "MSG", "DARALT",
     "openfda 250KB bulk dump must warn and say narrow-the-query"),
    ("mcp__titck__search_drugs", 78837, "MSG", "DARALT", "titck 79KB bulk dump must warn"),
    ("mcp__anamnesis__semantic_search", 50444, "MSG", "DARALT", "anamnesis 50KB bulk dump must warn"),
    ("mcp__globocan__gco_list_cancers", 4596, "ALLOW", None,
     "normal-sized result stays silent (hook must not become noise)"),
    ("Read", 999999, "ALLOW", None, "non-MCP tools are out of scope"),
]


ANAM_RUN = "aabbccddeeff"
ANAM_PREFIX = f"evrun:{ANAM_RUN}:"


def _anam_env(docs=None):
    tmp = tempfile.mkdtemp()
    ledger = os.path.join(tmp, "ledger.json")
    log = os.path.join(tmp, "forget.jsonl")
    payload = {
        "run_id": ANAM_RUN,
        "prefix": ANAM_PREFIX,
        "doc_ids": list(docs or []),
        "pending_forget": [],
        "status": "active",
    }
    with open(ledger, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    env = {
        "EVIDENTIA_ANAMNESIS_LEDGER": ledger,
        "EVIDENTIA_ANAMNESIS_FORGET_LOG": log,
        "EVIDENTIA_ANAMNESIS_NO_NETWORK": "1",
        "CLAUDE_PROJECT_DIR": tmp,
    }
    return env, ledger, log


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _anamnesis_cases():
    """Exclusive-run isolate + cleanup. Never hits live Anamnesis (forget stub)."""
    fails = 0
    env, ledger, log = _anam_env()
    scoped = ANAM_PREFIX + "10.1234/emicizumab"
    nsclc = "10.9999/nsclc-chunk"

    def g(tool, inp=None, e=None):
        payload = {"tool_name": tool}
        if inp is not None:
            payload["tool_input"] = inp
        _, j = run("guard_tool_call.py", payload, e or env)
        return decision(j), j

    cases = [
        ("mcp__claude_ai_anamnesis__ingest_document", None, "DENY",
         "ingest missing doc_id"),
        ("mcp__claude_ai_anamnesis__ingest_document", {"doc_id": nsclc}, "DENY",
         "ingest unprefixed DOI"),
        ("mcp__user-anamnesis__ingest_document", {"doc_id": scoped}, "ALLOW",
         "ingest prefixed"),
        ("mcp__anamnesis__semantic_search", {"query": "emicizumab"}, "DENY",
         "search without doc_id (shared-corpus leak)"),
        ("mcp__anamnesis__semantic_search",
         {"query": "emicizumab", "doc_id": nsclc}, "DENY",
         "search other-run / unprefixed id"),
        ("mcp__anamnesis__semantic_search",
         {"query": "emicizumab", "doc_id": scoped, "queries": ["efficacy"]},
         "ALLOW", "search scoped"),
        ("mcp__anamnesis__hybrid_query", {"query": "emicizumab"}, "DENY",
         "hybrid_query is unscoped"),
        ("mcp__anamnesis__hybrid_query",
         {"query": "emicizumab", "collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "hybrid_query scoped to this run"),
        ("mcp__anamnesis__hybrid_query",
         {"query": "emicizumab", "collection": "evidentia:run:ffffffffffff"},
         "DENY", "hybrid_query other-run collection"),
        ("mcp__anamnesis__graph_neighbors", {"entity": "emicizumab"}, "DENY",
         "graph_neighbors is unscoped"),
        ("mcp__anamnesis__graph_neighbors",
         {"entity": "emicizumab", "collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "graph_neighbors scoped"),
        ("mcp__anamnesis__subgraph", {"entities": ["emicizumab"]}, "DENY",
         "subgraph is unscoped"),
        ("mcp__anamnesis__subgraph",
         {"entities": ["emicizumab"], "collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "subgraph scoped"),
        ("mcp__anamnesis__semantic_search",
         {"query": "emicizumab", "collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "search by collection only"),
        ("mcp__anamnesis__semantic_search",
         {"query": "emicizumab", "doc_ids": [scoped]},
         "ALLOW", "search by prefixed doc_ids[]"),
        ("mcp__anamnesis__list_docs",
         {"collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "list_docs this run"),
        ("mcp__anamnesis__list_docs",
         {"collection": "evidentia:run:ffffffffffff"},
         "DENY", "list_docs other collection"),
        ("mcp__anamnesis__forget_collection",
         {"collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "forget_collection this run"),
        ("mcp__anamnesis__forget_collection",
         {"collection": "evidentia:run:ffffffffffff"},
         "DENY", "forget_collection foreign"),
        ("mcp__anamnesis__ingest_document",
         {"doc_id": nsclc, "collection": f"evidentia:run:{ANAM_RUN}"},
         "ALLOW", "ingest collection-scoped even if doc_id unprefixed"),
        ("mcp__anamnesis__corpus_stats", {}, "ALLOW", "corpus_stats observe-only"),
        ("mcp__anamnesis__forget_document", {"doc_id": nsclc}, "DENY",
         "forget foreign id"),
        ("mcp__anamnesis__forget_document", {"doc_id": scoped}, "ALLOW",
         "forget own prefixed id"),
        ("mcp__anamnesis__upsert_triples",
         {"triples": [{"subject": "a", "predicate": "treats", "object": "b"}]},
         "DENY", "triples missing doc_id"),
        ("mcp__anamnesis__upsert_triples",
         {"triples": [{"subject": "a", "predicate": "treats", "object": "b",
                       "doc_id": scoped}]},
         "ALLOW", "triples prefixed"),
        ("mcp__claude_ai_PubMed__search_articles", None, "ALLOW",
         "non-anamnesis unchanged"),
    ]
    for tool, inp, want, label in cases:
        got, j = g(tool, inp)
        if got != want:
            fails += 1
            print(f"FAIL anam-guard {label}: {got} != {want}")
        elif want == "DENY":
            reason = ((j or {}).get("hookSpecificOutput") or {}).get(
                "permissionDecisionReason", "")
            if "anamnesis" not in reason.lower() and "münhasır" not in reason:
                fails += 1
                print(f"FAIL anam-guard {label}: deny reason missing münhasır")

    # disable-flag still bypasses the exclusive deny (same file as G-WHITELIST)
    off = tempfile.mkdtemp()
    os.makedirs(os.path.join(off, ".claude"))
    open(os.path.join(off, ".claude", "evidentia-guard.off"), "w").close()
    got, _ = g("mcp__anamnesis__hybrid_query", {"query": "x"},
               {**env, "CLAUDE_PROJECT_DIR": off})
    if got != "ALLOW":
        fails += 1
        print("FAIL anam-guard disable-flag still denies hybrid_query")

    # PostToolUse ledger records prefixed ingest, ignores NSCLC id
    env2, ledger2, _ = _anam_env()
    _, j = run("anamnesis_ledger.py", {
        "tool_name": "mcp__plugin-evidentia-anamnesis__ingest_document",
        "tool_input": {"doc_id": scoped, "text": "body"},
        "tool_result": json.dumps({"doc_id": scoped, "chunks": 3}),
    }, env2)
    stored = _read_json(ledger2).get("doc_ids") or []
    if scoped not in stored:
        fails += 1
        print("FAIL anam-ledger ingest not recorded")
    if decision(j) != "MSG":
        fails += 1
        print("FAIL anam-ledger ingest should inject prefix context")

    _, _ = run("anamnesis_ledger.py", {
        "tool_name": "mcp__anamnesis__ingest_document",
        "tool_input": {"doc_id": nsclc, "text": "nsclc"},
        "tool_result": "{}",
    }, env2)
    if nsclc in (_read_json(ledger2).get("doc_ids") or []):
        fails += 1
        print("FAIL anam-ledger recorded unprefixed foreign id")

    _, _ = run("anamnesis_ledger.py", {
        "tool_name": "mcp__anamnesis__forget_document",
        "tool_input": {"doc_id": scoped},
        "tool_result": json.dumps({"existed": True}),
    }, env2)
    if scoped in (_read_json(ledger2).get("doc_ids") or []):
        fails += 1
        print("FAIL anam-ledger forget did not drop id")

    # SessionStart startup forgets leftover, mints a NEW run (not the old id)
    env3, ledger3, log3 = _anam_env(docs=[scoped])
    _, j = run("anamnesis_lifecycle.py", {
        "hook_event_name": "SessionStart",
        "source": "startup",
    }, env3)
    after = _read_json(ledger3)
    if after.get("run_id") == ANAM_RUN:
        fails += 1
        print("FAIL anam-lifecycle startup did not mint a new run_id")
    if scoped in (after.get("doc_ids") or []):
        fails += 1
        print("FAIL anam-lifecycle startup left previous docs in the new run")
    if not os.path.isfile(log3) or scoped not in open(log3, encoding="utf-8").read():
        fails += 1
        print("FAIL anam-lifecycle startup did not stub-forget leftover docs")
    ctx = ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
    if after.get("prefix", "") not in ctx:
        fails += 1
        print("FAIL anam-lifecycle startup context missing new prefix")

    # resume keeps the run and does NOT forget
    env4, ledger4, log4 = _anam_env(docs=[scoped])
    _, _ = run("anamnesis_lifecycle.py", {
        "hook_event_name": "SessionStart",
        "source": "resume",
    }, env4)
    if _read_json(ledger4).get("run_id") != ANAM_RUN:
        fails += 1
        print("FAIL anam-lifecycle resume rotated the run")
    if os.path.isfile(log4) and open(log4, encoding="utf-8").read().strip():
        fails += 1
        print("FAIL anam-lifecycle resume forgot docs")

    # compact keeps (human-approval checkpoint must not wipe)
    env5, ledger5, log5 = _anam_env(docs=[scoped])
    _, _ = run("anamnesis_lifecycle.py", {
        "hook_event_name": "SessionStart",
        "source": "compact",
    }, env5)
    if _read_json(ledger5).get("run_id") != ANAM_RUN or scoped not in (
            _read_json(ledger5).get("doc_ids") or []):
        fails += 1
        print("FAIL anam-lifecycle compact wiped the working set")

    # SessionEnd forgets only prefixed ids; leftover unprefixed in file ignored
    env6, ledger6, log6 = _anam_env(docs=[scoped])
    poisoned = _read_json(ledger6)
    poisoned["doc_ids"] = [scoped, nsclc]
    with open(ledger6, "w", encoding="utf-8") as fh:
        json.dump(poisoned, fh)
    _, _ = run("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"}, env6)
    if os.path.isfile(log6):
        logged = open(log6, encoding="utf-8").read()
    else:
        logged = ""
    if scoped not in logged:
        fails += 1
        print("FAIL anam-lifecycle SessionEnd did not forget own id")
    if nsclc in logged:
        fails += 1
        print("FAIL anam-lifecycle SessionEnd forgot an unprefixed foreign id")
    end_led = _read_json(ledger6)
    if end_led.get("doc_ids"):
        fails += 1
        print("FAIL anam-lifecycle SessionEnd left doc_ids")

    # empty SessionEnd is idempotent (no stub lines required)
    env7, _, log7 = _anam_env(docs=[])
    rc, _ = run("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"}, env7)
    if rc != 0:
        fails += 1
        print("FAIL anam-lifecycle empty SessionEnd non-zero")
    if os.path.isfile(log7) and open(log7, encoding="utf-8").read().strip():
        fails += 1
        print("FAIL anam-lifecycle empty SessionEnd wrote forget calls")

    # /evidentia remints; /evidentia-fulltext does not; approval prompt does not
    env8, ledger8, log8 = _anam_env(docs=[scoped])
    _, _ = run("anamnesis_lifecycle.py", {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "/evidentia-fulltext 10.1234/x",
    }, env8)
    if _read_json(ledger8).get("run_id") != ANAM_RUN:
        fails += 1
        print("FAIL anam-lifecycle fulltext reminted")

    _, _ = run("anamnesis_lifecycle.py", {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "P3 taramasını onaylıyorum, devam",
    }, env8)
    if _read_json(ledger8).get("run_id") != ANAM_RUN:
        fails += 1
        print("FAIL anam-lifecycle approval reminted")

    _, j = run("anamnesis_lifecycle.py", {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "/evidentia emicizumab hemophilia A",
    }, env8)
    after8 = _read_json(ledger8)
    if after8.get("run_id") == ANAM_RUN:
        fails += 1
        print("FAIL anam-lifecycle /evidentia did not remint")
    if scoped not in open(log8, encoding="utf-8").read():
        fails += 1
        print("FAIL anam-lifecycle /evidentia did not forget previous docs")
    if after8.get("prefix", "") not in (
            (j or {}).get("hookSpecificOutput") or {}).get("additionalContext", ""):
        fails += 1
        print("FAIL anam-lifecycle /evidentia context missing new prefix")

    env9, ledger9, log9 = _anam_env(docs=[scoped])
    _, _ = run("anamnesis_lifecycle.py", {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "please run /evidentia-synthesize for GRADE",
    }, env9)
    if _read_json(ledger9).get("run_id") == ANAM_RUN:
        fails += 1
        print("FAIL anam-lifecycle /evidentia-synthesize did not remint")
    if scoped not in open(log9, encoding="utf-8").read():
        fails += 1
        print("FAIL anam-lifecycle synthesize did not forget previous docs")

    return fails


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

    fails += _anamnesis_cases()

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

    # --- fleet_probe cache invalidation (2026-08-08) ---------------------------------
    # A stale cache is the MIRROR of this plugin's core sin: instead of claiming data that is not
    # there, it claims a GAP that is not there. Measured that day: the cache written at 12:40
    # recorded HTTP 530 for `openalex`/`pubmed-epmc` while they were still on the third-party
    # host; both were migrated to operator Workers ~20 minutes later and became healthy, but the
    # 24h TTL meant SessionStart kept reporting the DEAD url's failure — telling the model to
    # declare "degraded: unreachable" for two working connectors. Age alone is not enough: the
    # cache must also die when the roster changes.
    sys.path.insert(0, os.path.join(HERE, "scripts"))
    import fleet_probe as _fp   # noqa: E402
    import tempfile as _tf

    with open(os.path.join(ROOT, "fleet.lock.json"), encoding="utf-8") as fh:
        _lock = json.load(fh)
    fp1 = _fp.roster_fingerprint(_lock)
    cache_file = os.path.join(_tf.mkdtemp(), "c.json")
    _fp.write_cache(cache_file, {"x": {"status": "ok"}}, fp1)

    if _fp.read_cache(cache_file, 86400, fp1) is None:
        fails += 1
        print("FAIL fleet_probe: unchanged roster should REUSE the cache")

    for label, mutate in (
        ("url", lambda L: L["servers"][0].__setitem__("url", "https://moved.example/mcp")),
        ("auth_env", lambda L: L["servers"][0].__setitem__("auth_env", "NEW_KEY")),
        ("server removed", lambda L: L["servers"].pop(0)),
    ):
        mutated = json.loads(json.dumps(_lock))
        mutate(mutated)
        if _fp.read_cache(cache_file, 86400, _fp.roster_fingerprint(mutated)) is not None:
            fails += 1
            print(f"FAIL fleet_probe: cache survived a roster change ({label}) — a migrated "
                  f"connector would keep reporting its OLD url's failure")

    # A pre-fingerprint cache file must not be trusted either.
    legacy = os.path.join(_tf.mkdtemp(), "legacy.json")
    with open(legacy, "w", encoding="utf-8") as fh:
        json.dump({"ts": time.time(), "results": {"x": {"status": "ok"}}}, fh)
    if _fp.read_cache(legacy, 86400, fp1) is not None:
        fails += 1
        print("FAIL fleet_probe: legacy cache without a roster stamp must be re-probed")

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
    #   5 = fleet_probe cache: reuse-on-same + 3 roster mutations + legacy-format
    #  51 = anamnesis exclusive-run isolate + cleanup (guard/ledger/lifecycle; live MCP yok)
    #      27 table-driven guard + 24 ledger/lifecycle (dual-write collection + prefix)
    total = len(CASES_GUARD) + len(CASES_RDD) + 3 + 5 + 2 * len(gated) + 51
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
