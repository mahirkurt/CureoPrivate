#!/usr/bin/env python3
"""evidentia PreToolUse guard — runtime enforcement of the tool-level least-privilege
whitelist (DEĞİŞMEZ 5 / G-WHITELIST) and the known-broken-tool avoidance list (D1/D2/D6).

The skill documents these invariants in prose (connector-registry.md §2.6 / §8); this hook
makes them *enforced* — a forbidden or broken MCP tool call is DENIED with a redirect to the
verified-working alternative, so the model cannot silently spend a call on a pipeworx-generic
tool or a 404/AUTH-broken endpoint.

Scope is deliberately narrow and server-aware to avoid false positives:
  * pipeworx-generic names are denied ONLY on the four pipeworx-gateway servers that expose them
    (semantic-scholar / nih-clinicaltables / nlm-rxnorm / iuphar-gtopdb) — never on unrelated MCPs;
  * icd11_search is denied ONLY on med-terminologies (D6 AUTH-broken) — openfda.icd11_search
    (the working one) is untouched;
  * icd10cm is NOT touched (D3 is input-dependent: code→desc works, only name-search fails).

Fail-open: any parse/logic error → allow (exit 0). A guard bug must never brick a tool call.
Disable: create  <project>/.claude/evidentia-guard.off  to bypass entirely.
Input: PreToolUse JSON on stdin. Output on deny: hookSpecificOutput.permissionDecision=deny.
"""
import json
import os
import sys

# 30 pipeworx-generic tool names (mirror of check_integrity.py PIPEWORX_GENERIC / §2.6).
PIPEWORX_GENERIC = {
    "ask_pipeworx", "ask_pipeworx_grounded", "discover_tools", "remember", "recall",
    "forget", "subscribe", "unsubscribe", "list_subscriptions", "validate_claim",
    "suggest_questions", "deep_research", "bet_research", "compare_entities",
    "entity_profile", "resolve_entity", "recent_alerts", "recent_changes",
    "pipeworx_feedback", "pipeworx_trending", "ai_visibility_check", "generate_llms_txt",
    "scan_competitor_ai_presence", "scan_dependency", "search_within",
    "polymarket_arbitrage", "polymarket_edges", "polymarket_edge_tracker",
    "polymarket_fill_risk", "polymarket_kalshi_spread",
}

# Server identifiers whose generic surface is forbidden (substring-matched against the tool name,
# tolerant of the mcp__claude_ai_<server>__ and mcp__<server>__ prefixes).
PIPEWORX_SERVERS = ("semantic-scholar", "nih-clinicaltables", "nlm-rxnorm", "iuphar-gtopdb")

REDIRECT_GENERIC = (
    "en-az-yetki (DEĞİŞMEZ 5 / G-WHITELIST): pipeworx-generic aracı '{base}' evidentia "
    "whitelist-dışıdır. Bu sunucuda yalnız §2.6'daki doğrulanmış tıbbi araçları çağır "
    "(nih-clinicaltables: drugs/icd10cm[kod→desc]/conditions · nlm-rxnorm: "
    "rxnorm_search/rxnorm_get_properties · iuphar-gtopdb: search_targets/search_ligands/"
    "*_interactions · semantic-scholar: search_papers/get_paper/get_paper_citations/get_author). "
    "Katalog-genişletme/finans/bellek jenerikleri asla çağrılmaz."
)

# Known-broken tools → deny + redirect (connector-registry.md §8 D1/D2/D6).
def broken_reason(base, tool):
    if base == "rxnorm_interactions":
        return ("D1: nlm-rxnorm.rxnorm_interactions kaldırıldı (NLM RxNav Interaction API, "
                "Oca-2024 → HTTP 404). Klinik-DDI için drugddx.normalize_drug → "
                "drugddx.interaction_label (DailyMed SPL) + DailyMed label DDI-bölümü kullan.")
    if base == "rxnorm_related":
        return ("D2/D4: nlm-rxnorm.rxnorm_related → HTTP 400. Brand↔generic eşleme için "
                "med-terminologies.atc_classify veya TİTCK.find_equivalent_products_by_substance kullan.")
    if base == "icd11_search" and "med-terminologies" in tool:
        return ("D6: med-terminologies.icd11_search sunucuda WHO creds yok → AUTH_CONFIG_ERROR. "
                "ICD-11 metin araması için DAİMA openfda.icd11_search kullan (WHO ICD-11 MMS).")
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

    # Rule 1 — pipeworx-generic on a pipeworx-gateway server.
    if base in PIPEWORX_GENERIC and any(s in tool for s in PIPEWORX_SERVERS):
        deny(REDIRECT_GENERIC.format(base=base))

    # Rule 2 — known-broken (server-aware).
    reason = broken_reason(base, tool)
    if reason:
        deny(reason)

    sys.exit(0)  # allow


if __name__ == "__main__":
    main()
