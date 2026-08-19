#!/usr/bin/env python3
"""evidentia PreToolUse guard — runtime enforcement of the tool-level least-privilege
whitelist (DEĞİŞMEZ 5 / G-WHITELIST), the known-broken-tool avoidance list (D1/D2),
and the Anamnesis exclusive-run working set (no shared-corpus leak).

The skill documents these invariants in prose (connector-registry.md §2.6 / §8); this hook
makes them *enforced* — a forbidden or broken MCP tool call is DENIED with a redirect to the
verified-working alternative, so the model cannot silently spend a call on a pipeworx-generic
tool or a 404/AUTH-broken endpoint.

Scope is deliberately narrow and server-aware to avoid false positives:
  * pipeworx-gateway servers (nih-clinicaltables / nlm-rxnorm / iuphar-gtopdb, plus
    semantic-scholar as defence-in-depth) advertise thousands of generic tools. The
    guard is an ALLOWLIST: only §2.6 domain tools pass; everything else is denied.
    A 30-name denylist cannot cover a ~5558-tool dump.
  * icd11_search on med-terminologies is ALLOWED (D6 retired 2026-08-17 — live ICD-11
    returned 3B10.0). openfda.icd11_search remains the operator-owned path.
  * icd10cm is NOT touched (D3 is input-dependent: code→desc works, only name-search fails).

Fail-open: any parse/logic error → allow (exit 0). A guard bug must never brick a tool call.
Disable: create  <project>/.claude/evidentia-guard.off  to bypass entirely.
Input: PreToolUse JSON on stdin. Output on deny: hookSpecificOutput.permissionDecision=deny.
"""
import json
import os
import sys

# §2.6 domain allowlist — the ONLY tools permitted on pipeworx-gateway servers.
# Names not in this set (pipeworx generics, dynamic dumps, D1/D2 broken tools) are denied.
PIPEWORX_ALLOW = {
    "semantic-scholar": {
        "search_papers", "get_paper", "get_paper_citations", "get_author",
    },
    "nih-clinicaltables": {"drugs", "icd10cm", "conditions"},
    "nlm-rxnorm": {"rxnorm_search", "rxnorm_get_properties"},
    "iuphar-gtopdb": {
        "search_targets", "search_ligands",
        "target_interactions", "ligand_interactions",
    },
}

# NOTE (2026-08-17): `semantic-scholar` is CureoHub HP (`semanticscholar.cureonics.com`)
# with ONLY the 4 whitelisted tools — pipeworx generics no longer exist there. Entry kept
# as defence-in-depth if the connector is ever re-pointed at a gateway.
PIPEWORX_SERVERS = tuple(PIPEWORX_ALLOW)

REDIRECT_GENERIC = (
    "en-az-yetki (DEĞİŞMEZ 5 / G-WHITELIST): araç '{base}' bu sunucunun §2.6 "
    "domain allowlist'inde değil. Yalnız doğrulanmış tıbbi araçları çağır "
    "(nih-clinicaltables: drugs/icd10cm[kod→desc]/conditions · nlm-rxnorm: "
    "rxnorm_search/rxnorm_get_properties · iuphar-gtopdb: search_targets/search_ligands/"
    "*_interactions · semantic-scholar: search_papers/get_paper/get_paper_citations/get_author). "
    "Katalog-genişletme/finans/bellek jenerikleri asla çağrılmaz."
)

# Known-broken tools → deny + redirect (connector-registry.md §8 D1/D2).
# D6 (med-terminologies.icd11_search AUTH) retired 2026-08-17: live call returned ICD-11 3B10.0.
def broken_reason(base, tool):
    if base == "rxnorm_interactions":
        return ("D1: nlm-rxnorm.rxnorm_interactions kaldırıldı (NLM RxNav Interaction API, "
                "Oca-2024 → HTTP 404). Klinik-DDI için drugddx.normalize_drug → "
                "drugddx.interaction_label (DailyMed SPL) + DailyMed label DDI-bölümü kullan.")
    if base == "rxnorm_related":
        return ("D2/D4: nlm-rxnorm.rxnorm_related → HTTP 400. Brand↔generic eşleme için "
                "med-terminologies.atc_classify veya TİTCK.find_equivalent_products_by_substance kullan.")
    return None


def pipeworx_server(tool):
    for name in PIPEWORX_SERVERS:
        if name in tool:
            return name
    return None


def deny(reason):
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "[evidentia guard] " + reason,
        }
    }))
    sys.exit(0)


def main():
    # Disable flag → allow everything.
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj and os.path.isfile(os.path.join(proj, ".claude", "evidentia-guard.off")):
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open

    tool = str(data.get("tool_name", ""))
    if not tool.startswith("mcp__"):
        sys.exit(0)
    base = tool.split("__")[-1]

    # Rule 1 — known-broken first so D1/D2 keep their specific redirect (not the generic one).
    reason = broken_reason(base, tool)
    if reason:
        deny(reason)

    # Rule 2 — pipeworx-gateway allowlist (covers the ~5558 generic dump, not just 30 names).
    host = pipeworx_server(tool)
    if host and base not in PIPEWORX_ALLOW[host]:
        deny(REDIRECT_GENERIC.format(base=base))

    # Rule 3 — Anamnesis exclusive working set. Worker 1.2.0 is collection-scoped
    # (evidentia:run:<12hex>). Dual-write keeps evrun:<12hex>: prefixes.
    # ALLOW hybrid/search/graph when collection matches this run (and/or prefixed
    # doc_id / doc_ids[]). Still DENY unscoped hybrid/graph/global search.
    # Imports are local so a helper bug cannot take down Rules 1–2 (fail-open).
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from anamnesis_run import (
            deny_reason, ensure_ledger, is_anamnesis_tool, tool_input_of,
        )
        if is_anamnesis_tool(tool):
            reason = deny_reason(base, tool_input_of(data), ensure_ledger())
            if reason:
                deny(reason)
    except Exception:
        pass

    sys.exit(0)  # allow


if __name__ == "__main__":
    main()
