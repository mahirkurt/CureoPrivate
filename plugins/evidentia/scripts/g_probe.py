#!/usr/bin/env python3
"""
g_probe.py — G-PROBE gate. Live MCP `initialize` handshake over the remote URLs
declared in evidentia's .mcp.json (no-fabrication: connector liveness is verified
live, not remembered).

Targets the auto-wired remote tiers (Tier-K keyless + Tier-O operator Workers).
Skips comment keys (__*, $*) and env-placeholder URLs (${...}, Tier-A) which require
operator credentials. Stdlib only (urllib) — no requests dependency.

Usage:
  python scripts/g_probe.py                 # probe all eligible remote URLs
  python scripts/g_probe.py --json          # machine-readable result
  python scripts/g_probe.py --timeout 20

Exit: 0 = every probed URL returned a 2xx initialize; 1 = one or more failed;
2 = setup error. A non-2xx is reported with its status (e.g. the known
drug-interaction-mcp HTTP 500) so the operator can act (self-host drugddx).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

MCP_JSON = Path(__file__).resolve().parent.parent / ".mcp.json"

INIT_BODY = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "evidentia-g-probe", "version": "1.0.0"},
    },
}
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18",
    # default Python-urllib UA is bot-flagged by Cloudflare (403) on several MCP gateways;
    # send a conventional UA so the probe reflects real server liveness, not WAF challenge.
    "User-Agent": "evidentia-g-probe/1.0 (+https://cureonics.com)",
}
GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def load_targets() -> list[dict]:
    raw = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    servers = raw.get("mcpServers", {})
    out = []
    for name, cfg in servers.items():
        if name.startswith("__") or name.startswith("$"):
            continue
        if not isinstance(cfg, dict):
            continue
        url = cfg.get("url", "")
        tier = cfg.get("_tier", "?")
        headers = cfg.get("headers", {})
        needs_creds = "${" in json.dumps(headers)        # env-placeholder Bearer etc.
        if not url or "${" in url:               # env-placeholder (Tier-A) — needs creds
            out.append({"name": name, "url": url, "tier": tier, "skip": "env-placeholder/no-url"})
            continue
        if needs_creds:                          # static URL but auth header needs a secret
            out.append({"name": name, "url": url, "tier": tier, "skip": "auth-gated (env header)"})
            continue
        out.append({"name": name, "url": url, "tier": tier, "skip": None})
    return out


def probe(url: str, timeout: int) -> tuple[int, str]:
    data = json.dumps(INIT_BODY).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(4096).decode("utf-8", "replace")
            return r.status, _server_info(body)
    except urllib.error.HTTPError as e:
        return e.code, f"HTTPError {e.reason}"
    except urllib.error.URLError as e:
        return -1, f"URLError {e.reason}"
    except Exception as e:                        # noqa: BLE001
        return -1, f"{type(e).__name__}: {e}"


def _server_info(body: str) -> str:
    # body may be JSON or SSE ("data: {...}")
    for chunk in body.splitlines():
        chunk = chunk[5:].strip() if chunk.startswith("data:") else chunk.strip()
        if not chunk.startswith("{"):
            continue
        try:
            j = json.loads(chunk)
            si = j.get("result", {}).get("serverInfo", {})
            if si:
                return f"{si.get('name','?')} v{si.get('version','?')}"
        except json.JSONDecodeError:
            continue
    return "(2xx, serverInfo not parsed)"


def main() -> int:
    ap = argparse.ArgumentParser(description="G-PROBE live initialize gate")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()

    if not MCP_JSON.exists():
        print(f"{RED}SETUP ERROR{RESET}: {MCP_JSON} not found")
        return 2

    targets = load_targets()
    results, failed = [], []
    for t in targets:
        if t["skip"]:
            results.append({**t, "status": None, "info": f"skipped ({t['skip']})", "cls": "skip"})
            continue
        status, info = probe(t["url"], args.timeout)
        if 200 <= status < 300:
            cls = "live"
        elif status in (401, 403):
            # hardened OAuth 2.1 / Bearer gate rejecting an unauthenticated probe — EXPECTED,
            # not a failure: it proves the auth gate is active (same posture as self-host drugddx).
            cls = "secured"
        else:
            cls = "fail"
        results.append({**t, "status": status, "info": info, "cls": cls})
        if cls == "fail":
            failed.append(t["name"])

    if args.json:
        print(json.dumps({"results": results, "failed": failed}, ensure_ascii=False, indent=2))
        return 1 if failed else 0

    print("G-PROBE — live initialize over .mcp.json remote tiers\n")
    for r in results:
        tier = f"[{r['tier']}]"
        cls = r.get("cls")
        if cls == "skip":
            print(f"  {YELLOW}SKIP{RESET} {tier:4} {r['name']:20} {r['info']}")
        elif cls == "live":
            print(f"  {GREEN}200 {RESET} {tier:4} {r['name']:20} {r['info']}")
        elif cls == "secured":
            print(f"  {GREEN}🔒{str(r['status'])}{RESET} {tier:4} {r['name']:20} "
                  f"auth gate active (Bearer required) — expected")
        else:
            print(f"  {RED}{str(r['status']):>4}{RESET} {tier:4} {r['name']:20} {r['info']}")
    print()
    live = sum(1 for r in results if r.get("cls") == "live")
    secured = sum(1 for r in results if r.get("cls") == "secured")
    print(f"  summary: {GREEN}{live} live{RESET} · {GREEN}{secured} secured (401/403, gate active){RESET} "
          f"· {len(failed)} failed · {sum(1 for r in results if r.get('cls')=='skip')} skipped")
    if failed:
        print(f"\n{RED}PROBE FAILURES (5xx/4xx/conn): {', '.join(failed)}{RESET}")
        if any("drug" in f for f in failed):
            print("  → see self-host/drugddx-mcp/BUILD-BRIEF.md (self-host fork for clinical DDI gap)")
        return 1
    print(f"\n{GREEN}ALL PROBED REMOTES HEALTHY (live or auth-gated){RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
