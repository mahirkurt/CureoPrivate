#!/usr/bin/env python3
"""
g_bundle.py — G-BUNDLE gate. Cross-validates the .mcp.json bundled roster against
CONNECTORS.md (the single source of truth, ADR-03):

  1. every remote URL in .mcp.json appears in CONNECTORS.md (no undocumented bundle)
  2. every Tier-K/Tier-O URL listed in CONNECTORS.md (§1.4/§1.5/§1.6) appears in the
     roster OR is explicitly marked not-yet-wired (e.g. drugddx pre-deploy)

Stdlib only. Exit: 0 = consistent; 1 = drift (delta printed); 2 = setup error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_JSON = ROOT / ".mcp.json"
CONNECTORS = ROOT / "CONNECTORS.md"

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+")


def _norm_url(u: str) -> str:
    return u.rstrip("/").split("?")[0].strip("`<>()")


def roster_urls() -> set[str]:
    raw = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    out = set()
    for name, cfg in raw.get("mcpServers", {}).items():
        if name.startswith("__") or name.startswith("$") or not isinstance(cfg, dict):
            continue
        url = cfg.get("url", "")
        if url and "${" not in url:
            out.add(_norm_url(url))
    return out


def connectors_urls() -> set[str]:
    text = CONNECTORS.read_text(encoding="utf-8")
    return {_norm_url(u) for u in URL_RE.findall(text) if "${" not in u}


def main() -> int:
    if not MCP_JSON.exists() or not CONNECTORS.exists():
        print(f"{RED}SETUP ERROR{RESET}: .mcp.json or CONNECTORS.md missing")
        return 2

    roster = roster_urls()
    documented = connectors_urls()

    # 1. undocumented bundle: in roster, not in CONNECTORS.md
    undocumented = sorted(u for u in roster if u not in documented
                          and not any(u in d or d in u for d in documented))

    # 2. wired roster URLs all documented?
    print("G-BUNDLE — .mcp.json roster  <->  CONNECTORS.md (SSOT)\n")
    print(f"  roster remote URLs (env-placeholders excluded): {len(roster)}")
    print(f"  URLs documented in CONNECTORS.md:               {len(documented)}\n")

    ok = True
    for u in sorted(roster):
        matched = u in documented or any(u in d or d in u for d in documented)
        mark = f"{GREEN}OK  {RESET}" if matched else f"{RED}DRIFT{RESET}"
        if not matched:
            ok = False
        print(f"  {mark} {u}")

    if undocumented:
        ok = False
        print(f"\n{RED}UNDOCUMENTED BUNDLE (in .mcp.json, absent from CONNECTORS.md):{RESET}")
        for u in undocumented:
            print(f"    - {u}  → add a row to CONNECTORS.md §1")

    # advisory: expansion URLs documented but not yet in roster (e.g. drugddx pre-deploy)
    expected_wired = {
        "https://medical.sidneybissoli.com/mcp",
        "https://gateway.pipeworx.io/clinicaltables/mcp",
        "https://gateway.pipeworx.io/rxnorm/mcp",
        "https://gateway.pipeworx.io/guidetopharmacology/mcp",
    }
    missing_expected = sorted(u for u in expected_wired if u not in roster)
    if missing_expected:
        ok = False
        print(f"\n{RED}EXPECTED Tier-K NOT WIRED in roster:{RESET}")
        for u in missing_expected:
            print(f"    - {u}")

    drugddx = "https://drugddx-mcp.cureonics.workers.dev/mcp"
    if _norm_url(drugddx) not in roster:
        print(f"\n  {YELLOW}NOTE{RESET} drugddx not yet in roster (expected pre-deploy; "
              f"add as Tier-O after self-host/drugddx-mcp deploy)")

    print()
    if ok:
        print(f"{GREEN}BUNDLE CONSISTENT{RESET}")
        return 0
    print(f"{RED}BUNDLE DRIFT — reconcile .mcp.json and CONNECTORS.md{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
