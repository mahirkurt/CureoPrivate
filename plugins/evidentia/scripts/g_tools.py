#!/usr/bin/env python3
"""
g_tools.py — G-TOOLS gate. Live `tools/list` contract + optional functional `tools/call` smoke
over every remote declared in evidentia's `.mcp.json`.

WHY THIS GATE EXISTS
--------------------
G-PROBE proves a connector is REACHABLE (`initialize` → 2xx). G-IDENTITY proves each self-host
Worker advertises its own realm. G-BUNDLE proves the bundle is internally consistent. Nothing
proved the thing the skill actually depends on: **which tools a server exposes**.

The 2026-08-07 audit measured the whole fleet and found the docs had quietly drifted away from
the live surface while every gate stayed green:

    med-terminologies   docs said 37 tools   -> 31 live
    pubmed-epmc         docs said 10 tools   -> 11 live  (and v2.9.7 -> v2.10.2)
    openathens          docs said  7 tools   -> 10 live
    openalex            docs said v0.7.2     -> v0.7.8 live
    globocan            docs said 36 cancer sites -> 41 live

None of that is catastrophic on its own; together it is a registry the model is told to trust and
that no longer describes reality. This gate turns the tool surface into a COMMITTED CONTRACT
(`fleet.tools.json`) and fails when live drifts from it — so the next drift is a red gate, not a
discovery three months later.

USAGE
  python3 scripts/g_tools.py                 # contract check (tools/list only, no tool calls)
  python3 scripts/g_tools.py --smoke         # + one read-only functional call per server
  python3 scripts/g_tools.py --update        # rewrite the baseline from live (deliberate act)
  python3 scripts/g_tools.py --json

Gated connectors need their keys in the environment:
  doppler run -p cureohub -c dev_personal -- python3 scripts/g_tools.py

Exit: 0 = live matches the contract; 1 = drift / unreachable / smoke failure; 2 = setup error.
A connector whose key is absent is reported as NOT MEASURED and still fails the gate, mirroring
G-PROBE — a silent skip is how the gated half of the fleet hid outside the green headline before.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_JSON = ROOT / ".mcp.json"
BASELINE = ROOT / "fleet.tools.json"

ENV_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18",
    # urllib's default UA is bot-flagged (403) by Cloudflare on several MCP gateways.
    "User-Agent": "evidentia-g-tools/1.0 (+https://cureonics.com)",
}

# One READ-ONLY call per server, with an argument set verified against the live schema on
# 2026-08-07. `expect` is matched case-insensitively against the response text and MUST NOT be a
# string the server merely echoes back from the request — an echoed query makes the assertion
# vacuous (that is exactly how `gco_resolve_population("Turkey") -> 0 hits` first read as a pass).
SMOKE: dict = {
    "med-terminologies": ("atc_classify", {"drug_name": "warfarin"}, "B01A"),
    "nih-clinicaltables": ("drugs", {"terms": "warfarin", "count": 3}, "Warfarin"),
    "nlm-rxnorm": ("rxnorm_get_properties", {"rxcui": "11289"}, "warfarin"),
    "iuphar-gtopdb": ("search_targets", {"name": "thrombin", "limit": 3}, "thrombin"),
    "semantic-scholar": ("search_papers", {"query": "emicizumab hemophilia A", "limit": 3}, None),
    "openalex": ("openalex_resolve_name",
                 {"entity_type": "institutions", "query": "Hacettepe University"}, "ror.org"),
    "pubmed-epmc": ("pubmed_search_articles",
                    {"query": "emicizumab hemophilia A", "maxResults": 3}, "pubmed"),
    "pophive": ("get_current_status", {"disease": "covid"}, None),
    "who-gho": ("who_gho_query",
                {"indicator_code": "WHOSIS_000001", "country": "TUR", "year": 2019}, "77"),
    # Regression for the 2026-08-07 false negative: the English exonym must resolve to code 792.
    "globocan": ("gco_resolve_population", {"query": "Turkey"}, "792"),
    "ema": ("ema_get_medicine", {"identifier": "Hemlibra"}, "emicizumab"),
    "mevzuat-bilgisi": ("search_mevzuat", {"phrase": "ilac", "page_size": 20}, "total"),
    "titck": ("get_atc_hierarchy", {"code": "B01AA03"}, "arfarin"),
    "yok-akademik": ("yok_list_fields", {}, None),
    "openathens": ("oa_server_info", {}, "mcp_verified"),
    "annas-reader": ("article_search", {"query": "emicizumab hemophilia", "limit": 3}, None),
    "anamnesis": ("corpus_stats", {}, "chunks"),
    "drugddx": ("normalize_drug", {"name": "warfarin"}, "11289"),
    "openfda": ("icd11_search", {"query": "haemophilia", "limit": 3}, "ICD-11"),
    "evidentia-kb": ("kb_search", {"query": "GRADE certainty of evidence", "k": 3}, "grading"),
}


# ----------------------------------------------------------------- transport --
def _resolve(headers: dict):
    out = {}
    for k, v in (headers or {}).items():
        if not isinstance(v, str):
            continue
        s = v
        for var in ENV_REF.findall(v):
            val = os.environ.get(var)
            if not val:
                return None, var
            s = s.replace("${" + var + "}", val)
        out[k] = s
    return out, ""


def _first_json(body: str):
    """Body may be plain JSON or SSE ('data: {...}')."""
    for line in body.splitlines():
        c = line[5:].strip() if line.startswith("data:") else line.strip()
        if c.startswith("{"):
            try:
                return json.loads(c)
            except json.JSONDecodeError:
                continue
    return None


def _post(url, payload, auth, session, timeout, notify=False):
    hdr = dict(HEADERS)
    if auth:
        hdr.update(auth)
    if session:
        hdr["Mcp-Session-Id"] = session
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=hdr, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(4_000_000).decode("utf-8", "replace")
            return {"status": r.status, "json": None if notify else _first_json(raw),
                    "sid": r.headers.get("Mcp-Session-Id")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "json": None, "sid": None, "err": str(e.reason)}
    except Exception as e:  # noqa: BLE001
        return {"status": -1, "json": None, "sid": None, "err": f"{type(e).__name__}: {e}"}


class Conn:
    def __init__(self, url, auth, timeout):
        self.url, self.auth, self.timeout, self.sid, self.info = url, auth, timeout, None, {}

    def open(self):
        r = _post(self.url, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "evidentia-g-tools", "version": "1.0.0"}}},
            self.auth, None, self.timeout)
        self.sid = r.get("sid")
        if r.get("json") and "result" in r["json"]:
            self.info = r["json"]["result"].get("serverInfo", {}) or {}
        if 200 <= r["status"] < 300:
            _post(self.url, {"jsonrpc": "2.0", "method": "notifications/initialized"},
                  self.auth, self.sid, self.timeout, notify=True)
        return r

    def tools(self):
        """Paginated tools/list — a server that pages would otherwise look like it shrank."""
        names, cursor, r = [], None, {}
        for _ in range(20):
            params = {"cursor": cursor} if cursor else {}
            r = _post(self.url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                                 "params": params}, self.auth, self.sid, self.timeout)
            res = (r.get("json") or {}).get("result")
            if res is None:
                return names, r
            names.extend(t.get("name", "") for t in res.get("tools", []))
            cursor = res.get("nextCursor")
            if not cursor:
                break
        return names, r

    def call(self, name, args):
        r = _post(self.url, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                             "params": {"name": name, "arguments": args}},
                  self.auth, self.sid, max(self.timeout, 90))
        j = r.get("json") or {}
        if r["status"] < 200 or r["status"] >= 300:
            return False, "HTTP %s %s" % (r["status"], r.get("err", ""))
        if "error" in j:
            return False, "RPC %s" % str(j["error"])[:160]
        res = j.get("result", {})
        txt = "".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        if res.get("isError"):
            return False, "tool error: %s" % txt[:160]
        if not txt.strip():
            return False, "empty content"
        return True, txt



# ---------------------------------------------------------------- HTTP surface --
# The seven self-host Workers must satisfy an HTTP contract that `initialize` cannot see.
# Measured 2026-08-07: `OPTIONS /mcp` with `Origin: https://claude.ai` returned a bare 401 with
# no Access-Control-* headers on all three GATED Workers — a preflight is credential-free by
# specification, so a bearer gate in front of it makes the Worker un-addable from any browser
# client (claude.ai web, grok.com, ChatGPT web). The four keyless Workers answered 200 only
# because their gate never fires; the ordering defect was identical, merely unobservable.
SELF_HOST = {
    "anamnesis": "https://anamnesis-mcp.cureonics.workers.dev",
    "drugddx": "https://drugddx-mcp.cureonics.workers.dev",
    "ema": "https://ema-mcp.cureonics.workers.dev",
    "evidentia-kb": "https://evidentia-kb-mcp.cureonics.workers.dev",
    "globocan": "https://globocan-mcp.cureonics.workers.dev",
    "openfda": "https://openfda-mcp.cureonics.workers.dev",
    "who-gho": "https://who-gho-mcp.cureonics.workers.dev",
}


def _raw(url, method="GET", extra=None, timeout=25):
    hdr = dict(HEADERS)
    hdr.pop("Content-Type", None)
    hdr.update(extra or {})
    req = urllib.request.Request(url, headers=hdr, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}
    except Exception as e:  # noqa: BLE001
        return -1, {"_err": f"{type(e).__name__}: {e}"}


def _post_status(url, timeout):
    """Unauthenticated POST /mcp with a well-formed initialize; returns (status, lower-cased headers)."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "evidentia-g-tools", "version": "1.0.0"}}}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=dict(HEADERS), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}
    except Exception as e:  # noqa: BLE001
        return -1, {"_err": f"{type(e).__name__}: {e}"}


def check_surface(name, base, timeout):
    issues = []
    # 1. CORS preflight must short-circuit AHEAD of the bearer gate.
    st, h = _raw(base + "/mcp", "OPTIONS", {
        "Origin": "https://claude.ai", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type"}, timeout)
    if st not in (200, 204):
        issues.append(f"OPTIONS /mcp -> {st} (bekleneni 204; bearer kapisi preflight'in onunde)")
    else:
        allow = (h.get("access-control-allow-headers") or "").lower()
        expose = (h.get("access-control-expose-headers") or "").lower()
        if not h.get("access-control-allow-origin"):
            issues.append("preflight'te Access-Control-Allow-Origin yok")
        if "authorization" not in allow:
            issues.append("allow-headers 'Authorization' icermiyor -> gercek istek bearer tasiyamaz")
        if "www-authenticate" not in expose:
            issues.append("expose-headers 'WWW-Authenticate' icermiyor -> RFC 9728 isaretcisi "
                          "tarayici JS'ine gorunmez")
    # 2. RFC 9728 protected-resource metadata, both path forms (claude.ai bare / ChatGPT inserted).
    for path in ("/.well-known/oauth-protected-resource", "/.well-known/oauth-protected-resource/mcp"):
        s2, _ = _raw(base + path, timeout=timeout)
        if s2 != 200:
            issues.append(f"{path} -> {s2}")
    s3, _ = _raw(base + "/.well-known/oauth-authorization-server", timeout=timeout)
    if s3 != 200:
        issues.append(f"/.well-known/oauth-authorization-server -> {s3}")
    s4, _ = _raw(base + "/health", timeout=timeout)
    if s4 != 200:
        issues.append(f"/health -> {s4}")
    # 3. An unauthenticated POST must be either a clean 401 carrying the RFC 9728 pointer
    #    (gated) or a 200 (deliberately keyless) — never anything else. The body must be a REAL
    #    initialize: a bodyless POST is rejected 400 by the SDK transport before the gate, which
    #    would make every keyless Worker look broken (this check first read 400 for that reason).
    st5, h5 = _post_status(base + "/mcp", timeout)
    if st5 == 401:
        if "resource_metadata" not in (h5.get("www-authenticate") or ""):
            issues.append("401 WWW-Authenticate'inde resource_metadata yok (RFC 9728)")
        mode = "gated"
    elif 200 <= st5 < 300:
        mode = "keyless"
    else:
        issues.append(f"kimliksiz POST /mcp -> {st5}")
        mode = "?"
    return mode, issues

# ------------------------------------------------------------------- targets --
def load_targets():
    raw = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    out = []
    for name, cfg in raw.get("mcpServers", {}).items():
        if name.startswith("__") or name.startswith("$") or not isinstance(cfg, dict):
            continue
        url = cfg.get("url", "")
        if not url or "${" in url:
            continue
        auth, missing = _resolve(cfg.get("headers", {}))
        out.append({"name": name, "url": url, "tier": cfg.get("_tier", "?"),
                    "auth": auth, "missing": missing})
    return out


def inspect(t, timeout, smoke):
    res = {"name": t["name"], "tier": t["tier"]}
    if t["auth"] is None:
        res["state"] = "auth_missing"
        res["detail"] = "$%s ortamda yok" % t["missing"]
        return res
    c = Conn(t["url"], t["auth"], timeout)
    r = c.open()
    if not (200 <= r["status"] < 300):
        res["state"] = "unreachable"
        res["detail"] = "initialize %s %s" % (r["status"], r.get("err", ""))
        return res
    names, last = c.tools()
    res["version"] = c.info.get("version", "?")
    res["server_name"] = c.info.get("name", "?")
    res["tools"] = sorted(names)
    if not names:
        res["state"] = "no_tools"
        res["detail"] = "tools/list %s — bos" % last.get("status")
        return res
    res["state"] = "ok"
    if smoke and t["name"] in SMOKE:
        tool, args, expect = SMOKE[t["name"]]
        if tool not in names:
            res["smoke"] = ("fail", "'%s' sunucuda yok" % tool)
        else:
            ok, out = c.call(tool, args)
            if not ok:
                res["smoke"] = ("fail", out)
            elif expect and expect.lower() not in out.lower():
                res["smoke"] = ("fail", "'%s' beklendi, yok · %dch" % (expect, len(out)))
            else:
                res["smoke"] = ("ok", "%s · %dch" % (tool, len(out)))
    return res


# -------------------------------------------------------------------- report --
def compare(live, base):
    """Human-readable drift lines; empty list means the contract holds."""
    issues = []
    lt, bt = set(live.get("tools", [])), set(base.get("tools", []))
    for gone in sorted(bt - lt):
        issues.append("arac KAYBOLDU: %s" % gone)
    for new in sorted(lt - bt):
        issues.append("arac EKLENDI: %s" % new)
    if live.get("version") != base.get("version"):
        issues.append("serverInfo surumu %s -> %s" % (base.get("version"), live.get("version")))
    return issues


def main():
    ap = argparse.ArgumentParser(description="G-TOOLS live tool-surface contract gate")
    ap.add_argument("--smoke", action="store_true", help="also run one read-only call per server")
    ap.add_argument("--surface", action="store_true",
                    help="also check the 7 self-host Workers' HTTP/CORS/RFC-9728 contract")
    ap.add_argument("--update", action="store_true", help="rewrite fleet.tools.json from live")
    ap.add_argument("--only", metavar="NAME",
                    help="with --update: refresh ONLY this server, leaving every other baseline "
                         "entry untouched. For a deliberate single-server change while another "
                         "connector is unmeasurable (e.g. a third-party outage).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=45)
    args = ap.parse_args()

    if not MCP_JSON.exists():
        print("%sSETUP ERROR%s: %s yok" % (RED, RESET, MCP_JSON))
        return 2

    targets = load_targets()
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda t: inspect(t, args.timeout, args.smoke), targets))

    if args.update and args.only:
        # Targeted refresh. The wholesale --update refuses to run while ANY server is unmeasurable,
        # because a partial rewrite would silently drop the unmeasured connectors out of the
        # contract. That guard is right, but it also blocks a legitimate case: one server changed
        # on purpose while an unrelated third party is down (2026-08-08: caseyjhand.com returned
        # HTTP 530 for openalex + pubmed-epmc). This mode touches exactly the named server and
        # says so, so the change stays deliberate and auditable.
        hit = next((r for r in results if r["name"] == args.only), None)
        if hit is None:
            print("%s--only%s: '%s' .mcp.json'da yok" % (RED, RESET, args.only))
            return 1
        if hit["state"] != "ok":
            print("%s--only REDDEDILDI%s: '%s' olculemedi (%s) — taban cizgisi tahminle guncellenmez"
                  % (RED, RESET, args.only, hit.get("detail", hit["state"])))
            return 1
        if not BASELINE.exists():
            print("%sSETUP ERROR%s: %s yok" % (RED, RESET, BASELINE.name))
            return 2
        doc = json.loads(BASELINE.read_text(encoding="utf-8"))
        before = doc["servers"].get(args.only, {}).get("tools", [])
        doc["servers"][args.only] = {"version": hit.get("version"),
                                     "tool_count": len(hit["tools"]), "tools": hit["tools"]}
        BASELINE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        added = sorted(set(hit["tools"]) - set(before))
        gone = sorted(set(before) - set(hit["tools"]))
        print("%s%s guncellendi%s — %d arac (+%s / -%s); diger %d sunucu DOKUNULMADI"
              % (GREEN, args.only, RESET, len(hit["tools"]),
                 ", ".join(added) or "yok", ", ".join(gone) or "yok", len(doc["servers"]) - 1))
        return 0

    if args.update:
        not_ok = [r["name"] for r in results if r["state"] != "ok"]
        if not_ok:
            print("%s--update REDDEDILDI%s: su sunucular olculemedi -> %s\n"
                  "  Kismi bir taban cizgisi, eksik connector'lari sozlesmeden sessizce silerdi. "
                  "Anahtarlarla tekrar kos." % (RED, RESET, ", ".join(not_ok)))
            return 1
        payload = {
            "_comment": ("evidentia MCP tool-surface contract — the COMMITTED expectation that "
                         "`python3 scripts/g_tools.py` checks against live. Regenerate deliberately "
                         "with `--update` (under `doppler run`, so gated connectors are included) "
                         "and review the diff: a vanished tool is a capability the skill may still "
                         "be documenting."),
            "servers": {r["name"]: {"version": r.get("version"),
                                    "tool_count": len(r.get("tools", [])),
                                    "tools": r.get("tools", [])}
                        for r in sorted(results, key=lambda x: x["name"])},
        }
        BASELINE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print("%sfleet.tools.json guncellendi%s — %d sunucu, %d arac"
              % (GREEN, RESET, len(payload["servers"]),
                 sum(v["tool_count"] for v in payload["servers"].values())))
        return 0

    if not BASELINE.exists():
        print("%sSETUP ERROR%s: %s yok — once `doppler run -p cureohub -c dev_personal -- "
              "python3 scripts/g_tools.py --update`" % (RED, RESET, BASELINE.name))
        return 2
    base = json.loads(BASELINE.read_text(encoding="utf-8")).get("servers", {})

    failed, report = [], []
    for r in sorted(results, key=lambda x: x["name"]):
        n = r["name"]
        if r["state"] != "ok":
            failed.append(n)
            report.append((RED, r["state"].upper(), n, r.get("detail", "")))
            continue
        b = base.get(n)
        if b is None:
            failed.append(n)
            report.append((RED, "SOZLESMEDE YOK", n,
                           "%d arac — `--update` ile taban cizgisine ekle" % len(r["tools"])))
            continue
        issues = compare(r, b)
        smoke_state, smoke_txt = r.get("smoke", (None, ""))
        if smoke_state == "fail":
            issues.append("smoke: %s" % smoke_txt)
        if issues:
            failed.append(n)
            report.append((RED, "DRIFT", n, " · ".join(issues)))
        else:
            tail = " · smoke %s" % smoke_txt if smoke_state == "ok" else ""
            report.append((GREEN, "OK", n, "%d arac · v%s%s" % (len(r["tools"]), r["version"], tail)))

    if args.json:
        print(json.dumps({"results": results, "failed": failed}, ensure_ascii=False, indent=2))
        return 1 if failed else 0

    print("G-TOOLS — canli tools/list sozlesmesi%s\n"
          % (" + islevsel smoke" if args.smoke else ""))
    for color, tag, name, detail in report:
        print("  %s%-14s%s %-20s %s" % (color, tag, RESET, name, detail))
    if args.surface:
        print("\n  HTTP yuzeyi (7 self-host Worker: CORS preflight + RFC 9728 + health)")
        with ThreadPoolExecutor(7) as ex:
            surf = list(ex.map(lambda kv: (kv[0],) + check_surface(kv[0], kv[1], args.timeout),
                               sorted(SELF_HOST.items())))
        for name, mode, issues in surf:
            if issues:
                failed.append(name + ":surface")
                print("  %s%-14s%s %-20s %s" % (RED, "SURFACE", RESET, name, " · ".join(issues)))
            else:
                print("  %s%-14s%s %-20s %s" % (GREEN, "OK", RESET, name,
                                                "preflight 204 · PRM x2 · AS · health · %s" % mode))

    ok = sum(1 for c, t, _, _ in report if t == "OK")
    print("\n  %d sunucu denetlendi · %s%d sozlesmeye uygun%s · %d sorunlu"
          % (len(results), GREEN, ok, RESET, len(failed)))
    if failed:
        print("\n%sG-TOOLS DRIFT: %s%s" % (RED, ", ".join(failed), RESET))
        print("%s  Surukleme kasitliysa: belgeleri guncelle, sonra `--update` ile "
              "sozlesmeyi yenile.%s" % (DIM, RESET))
        return 1
    print("\n%sTOOL SURFACE CONTRACT HOLDS%s" % (GREEN, RESET))
    return 0


if __name__ == "__main__":
    sys.exit(main())
