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
import os
import re
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


ENV_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _resolve_headers(headers: dict) -> tuple[dict | None, str]:
    """Substitute ${VAR} from the process env.

    Returns (resolved_headers, missing_var). When every placeholder resolves, the
    gated endpoint becomes probeable FOR REAL — which is the whole point: before
    2026-08-07 this probe skipped all seven gated connectors outright and still
    printed "ALL PROBED REMOTES HEALTHY", so 35% of the fleet (and seven of the
    eight advertised self-host connectors) sat outside the green gate. A resolved
    Bearer also separates `unauthorized` (401/403 WITH a key = configuration fault)
    from `auth_missing` (no key = legitimate degrade); the old code could not tell
    those apart because it never sent a credential.
    """
    resolved = {}
    for k, v in headers.items():
        if not isinstance(v, str):
            continue
        out, missing = v, None
        for var in ENV_REF.findall(v):
            val = os.environ.get(var)
            if not val:
                missing = var
                break
            out = out.replace("${" + var + "}", val)
        if missing:
            return None, missing
        resolved[k] = out
    return resolved, ""


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
        if not url or "${" in url:               # env-placeholder (Tier-A) — needs creds
            out.append({"name": name, "url": url, "tier": tier, "auth": None,
                        "skip": "env-placeholder/no-url"})
            continue
        if "${" in json.dumps(headers):          # gated: try to resolve the secret
            resolved, missing = _resolve_headers(headers)
            if resolved is None:
                out.append({"name": name, "url": url, "tier": tier, "auth": None,
                            "skip": f"auth_missing (${missing} ortamda yok)"})
                continue
            out.append({"name": name, "url": url, "tier": tier, "auth": resolved,
                        "skip": None})
            continue
        out.append({"name": name, "url": url, "tier": tier, "auth": None, "skip": None})
    return out


def probe(url: str, timeout: int, auth: dict | None = None) -> tuple[int, str]:
    data = json.dumps(INIT_BODY).encode("utf-8")
    headers = dict(HEADERS)
    if auth:
        headers.update(auth)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
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
        status, info = probe(t["url"], args.timeout, t.get("auth"))
        if 200 <= status < 300:
            cls = "live"
        elif status in (401, 403):
            if t.get("auth"):
                # We SENT a resolved Bearer and were still refused → this is a
                # CONFIGURATION FAULT (wrong/retired key, or a header .mcp.json
                # never wired), not a healthy gate. Treating it as "expected" is
                # precisely how the 2026-08-02 TİTCK gating hid for months.
                cls = "unauthorized"
            else:
                # No credential was sent, so a refusal only proves the gate is active.
                cls = "secured"
        else:
            cls = "fail"
        results.append({**t, "status": status, "info": info, "cls": cls})
        if cls in ("fail", "unauthorized"):
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
            gated = " (Bearer sent)" if r.get("auth") else ""
            print(f"  {GREEN}200 {RESET} {tier:4} {r['name']:20} {r['info']}{gated}")
        elif cls == "secured":
            print(f"  {GREEN}🔒{str(r['status'])}{RESET} {tier:4} {r['name']:20} "
                  f"auth gate active (Bearer required) — expected")
        elif cls == "unauthorized":
            print(f"  {RED}🔑{str(r['status'])}{RESET} {tier:4} {r['name']:20} "
                  f"UNAUTHORIZED — anahtar GÖNDERİLDİ ama reddedildi (yapılandırma arızası)")
        else:
            print(f"  {RED}{str(r['status']):>4}{RESET} {tier:4} {r['name']:20} {r['info']}")
    print()
    live = sum(1 for r in results if r.get("cls") == "live")
    secured = sum(1 for r in results if r.get("cls") == "secured")
    skipped = [r for r in results if r.get("cls") == "skip"]
    print(f"  summary: {GREEN}{live} live{RESET} · {GREEN}{secured} secured (401/403, gate active){RESET} "
          f"· {len(failed)} failed · {len(skipped)} skipped")
    if failed:
        print(f"\n{RED}PROBE FAILURES (5xx/4xx/conn/unauthorized): {', '.join(failed)}{RESET}")
        if any("drug" in f for f in failed):
            print("  → see self-host/drugddx-mcp/BUILD-BRIEF.md (self-host fork for clinical DDI gap)")
    # NEVER let a skipped endpoint hide inside a green headline. Pre-2026-08-07 the
    # gate printed "ALL PROBED REMOTES HEALTHY" while silently skipping every gated
    # connector; the honest statement names what was NOT measured.
    if skipped:
        print(f"\n{YELLOW}ÖLÇÜLMEDİ ({len(skipped)}/{len(results)}): "
              f"{', '.join(r['name'] for r in skipped)}{RESET}")
        print("  → anahtarlarla tam kapsam için: "
              "`doppler run -p cureohub -c dev_personal -- python3 scripts/g_probe.py`")
        return 1
    print(f"\n{GREEN}ALL PROBED REMOTES HEALTHY (live or auth-gated){RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
