#!/usr/bin/env python3
"""Cureonics filo prob'u — YALNIZ stdlib, fail-open, 24 saat cache'li.

KANONİK KOPYA: tools/fleetkit/fleet_probe.py. Plugin'lere BİREBİR vendor edilir
(hooks/scripts/fleet_probe.py); `tools/fleetkit/check_drift.py --all` kopyaların
bayt-özdeşliğini doğrular. Plugin içinde düzenlemeyin — burada düzenleyip
`python3 tools/fleetkit/vendor.py` koşun.

NEDEN VAR: env-var varlığına bakmak YETMEZ. 2026-08-02'de TİTCK kapılandı;
lex-sanitas onu "public" saymaya devam etti ve her çağrıda 401 aldı (aynı hata
edupedia/maarif-mufredat, evidentia/titck-cache ve vekayinuvis/tavily'de de
bulundu) — preflight
bunu YAPISAL OLARAK göremedi, çünkü yalnız os.environ'a bakıyordu. Bu modül
gerçek bir MCP `initialize` isteği atar ve iki hâli AYIRIR:

  auth_missing  → anahtar bekleniyor ama ortamda yok (MEŞRU DEGRADE; ağa çıkılmaz)
  unauthorized  → sunucu 401/403 verdi (YAPILANDIRMA ARIZASI — düzeltilebilir)

Bu ayrım olmadan ikisi de "o katman çalışmıyor" diye görünür ve arıza degrade
kılığında sonsuza dek yaşar.

CLI:        python3 fleet_probe.py [--fresh] [--json] [--quiet]
Kütüphane:  cached_probe(root, os.environ)

Bağımlılık notu: bu dosya PyYAML kullanmaz ve gen_fleet'i import etmez —
fleet.lock.json'u stdlib json ile okur, böylece kullanıcı sisteminde PyYAML
kurulu olmasa da preflight çalışır.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

INIT_PAYLOAD = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "cureonics-preflight", "version": "1.0.0"}},
}).encode("utf-8")

# anamnesis initialize'ı ölçülen ~11 sn sürer (soğuk başlangıç değil, kalıcı) →
# eşik onun üstünde olmalı, yoksa sağlıklı bir server her koşumda 'unreachable'
# görünür. Tüm filo TEK dalgada (max_workers=20) koştuğu için toplam duvar-saati
# en yavaş server'a eşittir, toplamına değil. Sonuç 24 saat cache'lenir → bu
# maliyet günde bir kez ödenir; hook fail-open olduğu için oturumu bloklamaz.
PER_ENDPOINT_TIMEOUT = 12.0
TOTAL_DEADLINE = 14.0
MAX_WORKERS = 20
# oecd'nin initialize yanıtı 32 KB (uzun capabilities/instructions). Okuma sınırı
# gövdeyi JSON'un ORTASINDAN keserse ayrıştırma çöker ve sağlıklı server sahte
# 'error' verir — sınır en büyük gerçek yanıtın üstünde olmalı.
READ_LIMIT = 262144
CACHE_TTL = 86400  # 24 saat — her oturumda ağ trafiği olmasın

# ZORUNLU: urllib'in varsayılan 'Python-urllib/x.y' User-Agent'ı Cloudflare bot
# kuralına takılır ve TÜM cureonics.com/workers.dev uçları 403 (error 1010) döner.
# Bu, filonun tamamını sahte 'unauthorized' gösterir — yani prob'un teşhis etmek
# için var olduğu arızanın birebir aynısını ÜRETİR. Açık UA şart.
USER_AGENT = "cureonics-preflight/1.0 (+https://cureonics.com)"

SYMBOL = {"ok": "✓", "auth_missing": "○", "unauthorized": "✗",
          "unreachable": "✗", "error": "!", "unknown": "?"}


class _KeepPost(urllib.request.HTTPRedirectHandler):
    """307/308'i METOT ve GÖVDE korunarak takip eder.

    FastMCP `/mcp` altına mount edildiğinde bare `POST /mcp` → 307 `/mcp/` döner
    (edupedia modul-yayin bunu yapar). urllib POST'ta 307'yi takip etmez → sağlıklı
    server sahte 'error' görünür, yani prob teşhis ettiği arızayı kendisi üretir.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (307, 308):
            return urllib.request.Request(newurl, data=req.data, headers=req.headers,
                                          method=req.get_method(), unverifiable=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_KeepPost)


def load_lock(root):
    """fleet.lock.json'u okur; okunamazsa None (fail-open)."""
    try:
        return json.loads((Path(root) / "fleet.lock.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_json(body: str):
    """Düz JSON veya SSE (`data: {...}`) gövdesinden ilk JSON nesnesini çıkarır."""
    candidates = [body]
    candidates += [ln[5:].strip() for ln in body.splitlines() if ln.startswith("data:")]
    for raw in candidates:
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                return json.loads(raw)
            except ValueError:
                continue
    return None


def classify(http, body: str) -> str:
    """HTTP kodu + gövdeden durum türetir."""
    if http in (401, 403):
        return "unauthorized"
    if http is None or http >= 500:
        return "unreachable"
    if http != 200:
        return "error"
    payload = _extract_json(body)
    if payload is None:
        return "error"
    if "error" in payload:
        return "error"
    return "ok" if "result" in payload else "error"


def probe_server(server: dict, env, timeout: float = PER_ENDPOINT_TIMEOUT) -> dict:
    """Tek sunucuyu prob eder. Ağ hatası dâhil hiçbir istisna sızmaz."""
    name = server["name"]
    auth_env = server.get("auth_env")
    key = env.get(auth_env) if auth_env else None

    if auth_env and not key:
        return {"name": name, "status": "auth_missing", "http": None,
                "detail": "${%s} süreç ortamında yok" % auth_env}

    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream",
               "User-Agent": USER_AGENT}
    if key:
        headers["Authorization"] = "Bearer %s" % key
    req = urllib.request.Request(server["url"], data=INIT_PAYLOAD,
                                 headers=headers, method="POST")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            body = resp.read(READ_LIMIT).decode("utf-8", "replace")
            return {"name": name, "status": classify(resp.status, body),
                    "http": resp.status, "detail": ""}
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(READ_LIMIT).decode("utf-8", "replace")
        except Exception:
            body = ""
        return {"name": name, "status": classify(exc.code, body),
                "http": exc.code, "detail": body[:120].replace("\n", " ")}
    except Exception as exc:
        return {"name": name, "status": "unreachable", "http": None,
                "detail": type(exc).__name__}


def probe_fleet(lock: dict, env, deadline: float = TOTAL_DEADLINE) -> dict:
    """Tüm filoyu paralel prob eder; bütçe dolarsa kalanlar 'unknown' kalır."""
    servers = lock.get("servers", [])
    results = {s["name"]: {"name": s["name"], "status": "unknown",
                           "http": None, "detail": "bütçe doldu"} for s in servers}
    if not servers:
        return results
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(probe_server, s, env) for s in servers]
        try:
            for fut in as_completed(futures, timeout=deadline):
                try:
                    r = fut.result()
                    results[r["name"]] = r
                except Exception:
                    pass
        except TimeoutError:
            pass          # bütçe doldu → kalanlar 'unknown'
        except Exception:
            pass
        for fut in futures:
            fut.cancel()
    return results


def _cache_path(plugin: str = "") -> Path:
    """Cache plugin adına göre ayrışır — iki plugin birbirinin sonucunu ezmez."""
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return Path(base) / "cureonics-fleet" / f"{plugin or 'default'}.json"


def read_cache(path, ttl: int = CACHE_TTL):
    """Taze cache'i döner; bayat/bozuk/eksikse None."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if time.time() - float(data["ts"]) > ttl:
            return None
        return data["results"]
    except Exception:
        return None


def write_cache(path, results: dict) -> None:
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"ts": time.time(), "results": results}),
                        encoding="utf-8")
    except Exception:
        pass  # cache yazılamaması asla akışı bozmaz


def cached_probe(root, env, ttl: int = CACHE_TTL, fresh: bool = False) -> dict:
    """Cache'li prob. Lock yoksa veya her şey çökerse boş dict (fail-open)."""
    try:
        lock = load_lock(root)
        if not lock:
            return {}
        path = _cache_path((lock or {}).get("plugin", ""))
        if not fresh:
            cached = read_cache(path, ttl)
            if cached is not None:
                return cached
        results = probe_fleet(lock, env)
        write_cache(path, results)
        return results
    except Exception:
        return {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cureonics canlı filo prob'u")
    ap.add_argument("--fresh", action="store_true", help="cache'i atla")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--root", help="plugin kökü (kanonik kopyadan koşarken zorunlu)")
    args = ap.parse_args(argv)

    here = Path(__file__).resolve()
    # Vendor edilmiş kopya: <plugin>/hooks/scripts/ → kök 2 üstte.
    # Kanonik kopya: <repo>/tools/fleetkit/ → --root ile plugin verilmeli.
    root = Path(args.root).resolve() if args.root else here.parent.parent.parent
    results = cached_probe(root, os.environ, fresh=args.fresh)

    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif not args.quiet:
        if not results:
            print("prob çalıştırılamadı (lock yok veya ağ kapalı) — "
                  "preflight env-only moda düşer", file=sys.stderr)
        for name in sorted(results):
            r = results[name]
            http = r.get("http") or "-"
            print("%s %-18s %-14s %4s %s" % (
                SYMBOL.get(r["status"], "?"), name, r["status"], http,
                (r.get("detail") or "")[:60]))
        tally = {}
        for r in results.values():
            tally[r["status"]] = tally.get(r["status"], 0) + 1
        print("— " + " · ".join(f"{k}: {v}" for k, v in sorted(tally.items())))
    return 0  # HER ZAMAN 0 — fail-open, oturumu asla bloklamaz


if __name__ == "__main__":
    sys.exit(main())
