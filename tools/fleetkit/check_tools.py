#!/usr/bin/env python3
"""ARAÇ-DÜZEYİ canlı denetim — `tools_used` beyanı ↔ sunucunun gerçek `tools/list`'i.

NEDEN VAR: `audit_plugins.py` her uca yalnız `initialize` gönderir; 200 dönen bir
sunucu "sağlıklı" sayılır. Ama sağlık ≠ İŞLEVSELLİK. fleet.yaml'ın `tools_used`
alanı skill/agent düzyazısına ve mod×server matrisine akar; orada yazan bir araç
sunucuda YOKSA model onu çağırır, `Unknown tool` alır ve bunu bir veri-yokluğu
gibi raporlar. Bu sınıf arıza `initialize`-only probun kör noktasıdır: uç
mükemmel sağlıklıdır, çağrılan araç ise mevcut değildir.

Üç bulgu sınıfı:
  MISSING  — beyan edildi, canlıda YOK. Kırık: fantom araç çağrısı. → FAIL
  RENAMED  — beyan edilen ad yok ama çok benzeri var (upstream yeniden adlandırdı). → FAIL + öneri
  UNUSED   — canlıda var, beyan edilmemiş. Bilgilendirme: kullanılmayan yetenek.

`initialize` → (session header) → `notifications/initialized` → `tools/list`
zinciri MCP Streamable HTTP sözleşmesidir; sunucu `Mcp-Session-Id` verirse
sonraki isteklerde taşınmazsa 400 döner (sahte "araç yok" sonucu).
"""
import difflib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
UA = "cureonics-tools-audit/1.0 (+https://cureonics.com)"
TIMEOUT, READ_LIMIT = 25.0, 4 * 1024 * 1024
ENV_RX = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class KeepPost(urllib.request.HTTPRedirectHandler):
    """307/308'i METOT ve GÖVDE koruyarak takip et (FastMCP /mcp → /mcp/)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (307, 308):
            return urllib.request.Request(
                newurl, data=req.data, headers=req.headers,
                method=req.get_method(), unverifiable=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(KeepPost)


def _payload(body):
    """JSON-RPC gövdesini düz JSON'dan VEYA SSE `data:` çerçevelerinden çıkar.

    Streamable HTTP sunucuları aynı ucu iki content-type ile servis edebilir;
    yalnız `json.loads(body)` denemek SSE konuşan sağlıklı sunucuyu 'error'
    gösterir.
    """
    for raw in [body] + [l[5:].strip() for l in body.splitlines() if l.startswith("data:")]:
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                return json.loads(raw)
            except ValueError:
                continue
    return None


def _post(url, obj, headers, _retry=True):
    """5xx'i BİR KEZ yeniden dener.

    fastmcp.app gibi soğuk-başlayan barındırıcılar ilk isteğe 502 döndürebiliyor
    (2026-08-07 ölçümü: yoktez 502 → aynı URL 3/3 yeniden denemede 200). Yeniden
    deneme olmadan geçici soğuk-başlangıç kalıcı bir bulgu gibi raporlanır.
    """
    req = urllib.request.Request(
        url, data=json.dumps(obj).encode(), headers=headers, method="POST")
    try:
        with OPENER.open(req, timeout=TIMEOUT) as r:
            return r.status, r.read(READ_LIMIT).decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        try:
            b = e.read(READ_LIMIT).decode("utf-8", "replace")
        except Exception:
            b = ""
        if e.code >= 500 and _retry:
            return _post(url, obj, headers, _retry=False)
        return e.code, b, dict(e.headers or {})


def _headers(key):
    h = {"Content-Type": "application/json",
         "Accept": "application/json, text/event-stream", "User-Agent": UA}
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


# İşlevsel duman testinde çağrılmasına izin verilen araç adı kalıpları.
# KATI ALLOWLIST: yalnız argümansız envanter/kimlik uçları. Yazan, indiren,
# ücret doğuran veya uzak durum değiştiren hiçbir araç bu kalıplara uymaz —
# duman testi filoyu ASLA mutasyona uğratmaz.
SAFE_RX = re.compile(
    r"^(server_info|about|corpus_stats)$"
    r"|_server_info$|_info$|^list_|_list_|^get_categories$|^get_popular_datasets$"
    r"|^list_sources$|^describe_|^probe_",
)


def call_safe(url, key, tools, budget=3):
    """Argümansız salt-okunur araçları GERÇEKTEN çağır — (ok, fail, atlanan).

    `tools/list` bir aracın VAR olduğunu kanıtlar, ÇALIŞTIĞINI değil. Upstream
    şeması bozulduğunda, arka uç deposu düştüğünde veya araç yalnız kayıtlıyken
    gövdesi hata verdiğinde uç hâlâ 200/`initialize` döner ve envanter denetimi
    temiz görünür. Bu katman o boşluğu kapatır.
    """
    h = _headers(key)
    st, body, hdrs = _post(url, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "tools-audit", "version": "1"}}}, h)
    sid = hdrs.get("Mcp-Session-Id") or hdrs.get("mcp-session-id")
    if sid:
        h["Mcp-Session-Id"] = sid
    _post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, h)

    picked = [t for t in tools
              if SAFE_RX.search(t["name"])
              and not (t.get("inputSchema") or {}).get("required")][:budget]
    ok, fail = [], []
    for t in picked:
        st, body, _ = _post(url, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                  "params": {"name": t["name"], "arguments": {}}}, h)
        p = _payload(body) or {}
        res = p.get("result")
        if st != 200 or "error" in p:
            msg = p.get("error", {}).get("message", f"http {st}")
            fail.append((t["name"], str(msg)[:70]))
        elif res is not None and res.get("isError"):
            # JSON-RPC başarılı ama ARAÇ hata döndürdü — `error` anahtarı yok,
            # `isError:true` var. Bu ayrım gözetilmezse kırık araç 'ok' sayılır.
            txt = " ".join(c.get("text", "") for c in res.get("content", []))
            fail.append((t["name"], txt[:70] or "isError"))
        else:
            ok.append(t["name"])
    return ok, fail, len(picked)


def live_tools(url, key):
    """Uçtaki araç nesnelerini döndür — (tools|None, hata_metni)."""
    h = _headers(key)
    try:
        st, body, hdrs = _post(url, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "tools-audit", "version": "1"}}}, h)
    except Exception as e:
        return None, type(e).__name__
    if st in (401, 403):
        return None, "unauthorized"
    if st != 200 or not _payload(body):
        return None, f"init http {st}"
    # Oturum kimliği verilmişse SONRAKİ her istekte taşınmalı; taşınmazsa
    # sunucu 400 döner ve bu 'araç yok' gibi okunur.
    sid = hdrs.get("Mcp-Session-Id") or hdrs.get("mcp-session-id")
    if sid:
        h["Mcp-Session-Id"] = sid
    try:
        _post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, h)
    except Exception:
        pass

    names, cursor = [], None
    for _ in range(20):  # sayfalama tavanı — sonsuz cursor döngüsüne karşı
        params = {"cursor": cursor} if cursor else {}
        try:
            st, body, _hdrs = _post(url, {"jsonrpc": "2.0", "id": 2,
                                          "method": "tools/list", "params": params}, h)
        except Exception as e:
            return None, type(e).__name__
        p = _payload(body)
        if st != 200 or not p or "result" not in p:
            err = (p or {}).get("error", {}).get("message", f"http {st}")
            return None, f"tools/list: {str(err)[:60]}"
        res = p["result"]
        names += list(res.get("tools", []))
        cursor = res.get("nextCursor")
        if not cursor:
            break
    return names, None


def audit(plugin_dir, only=None, do_call=False):
    fleet = yaml.safe_load((plugin_dir / "fleet.yaml").read_text(encoding="utf-8"))
    mcp = json.loads((plugin_dir / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]

    targets = []
    for s in fleet["servers"]:
        n = s["name"]
        if only and n not in only:
            continue
        entry = mcp.get(n, {})
        auth = entry.get("headers", {}).get("Authorization", "")
        env = (ENV_RX.findall(auth) or [None])[0]
        targets.append((n, entry.get("url") or s.get("url"), env,
                        list(s.get("tools_used") or [])))

    def run(t):
        n, url, env, declared = t
        key = os.environ.get(env) if env else None
        if env and not key:
            return n, declared, None, f"${env} ortamda yok", None
        tools, err = live_tools(url, key)
        smoke = call_safe(url, key, tools) if (do_call and tools) else None
        return n, declared, tools, err, smoke

    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(run, targets))

    fails, broken, skipped = [], [], []
    print(f"ARAÇ-DÜZEYİ CANLI DENETİM — {fleet['plugin']} v{fleet['plugin_version']}"
          + ("  [+ işlevsel duman testi]" if do_call else "") + "\n")
    for name, declared, live, err, smoke in sorted(rows, key=lambda r: r[0]):
        if live is None:
            skipped.append((name, err))
            print(f"  ?  {name:20} atlandı — {err}")
            continue
        lnames = [t["name"] for t in live]
        lset = set(lnames)
        missing = [d for d in declared if d not in lset]
        sugg = {}
        for m in missing:
            near = difflib.get_close_matches(m, lnames, n=1, cutoff=0.75)
            if near:
                sugg[m] = near[0]
        smoke_txt = ""
        if smoke:
            ok, sf, n_picked = smoke
            smoke_txt = ("   duman —" if not n_picked
                         else f"   duman {len(ok)}/{n_picked}")
            broken += [(name,) + f for f in sf]
        mark = "✗" if (missing or (smoke and smoke[1])) else "✓"
        print(f"  {mark}  {name:20} beyan {len(declared):3}/canlı {len(lnames):3}"
              f"   kullanılmayan {len(lset - set(declared)):3}{smoke_txt}")
        for m in missing:
            hint = f"  → canlıda benzeri: '{sugg[m]}'" if m in sugg else ""
            print(f"        ✗ BEYAN EDİLDİ AMA YOK: {m}{hint}")
            fails.append((name, m, sugg.get(m)))
        for _srv, tool, msg in [b for b in broken if b[0] == name]:
            print(f"        ✗ ÇAĞRI BAŞARISIZ: {tool} — {msg}")
    print()
    if fails:
        print(f"FANTOM ARAÇ: {len(fails)} beyan canlı sunucuda karşılıksız")
    if broken:
        print(f"KIRIK ARAÇ: {len(broken)} salt-okunur çağrı hata döndürdü")
    if not fails and not broken:
        print(f"ARAÇ BEYANLARI TEMİZ — {len(rows) - len(skipped)} sunucu doğrulandı"
              + (f", {len(skipped)} atlandı" if skipped else ""))
    return 1 if (fails or broken) else 0


if __name__ == "__main__":
    flags = {a for a in sys.argv[1:] if a.startswith("-")}
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    plugin = args[0] if args else "lex-sanitas"
    only = set(args[1:]) or None
    sys.exit(audit(ROOT / "plugins" / plugin, only, do_call="--call" in flags))
