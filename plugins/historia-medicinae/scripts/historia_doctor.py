#!/usr/bin/env python3
"""historia-medicinae filo doctor — bant bazlı preflight raporu.

Kullanım:
    python3 scripts/historia_doctor.py           # statik (ağ yok)
    python3 scripts/historia_doctor.py --live    # anahtarı olanlara MCP initialize dener

Kaynak: fleet.lock.json (gen_fleet.py türevi). fleet.yaml tek gerçek kaynaktır.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BAND_ORDER = [
    ("academic-core", "Akademik çekirdek"),
    ("primary-source", "Birincil kaynak"),
    ("fulltext", "Tam-metin şelalesi"),
    ("legal-history", "Tarihsel yasama"),
    ("terminology", "Terminoloji"),
    ("epidemiology", "Epidemiyoloji"),
    ("turkiye", "Türkiye kolu"),
    ("support", "Destekleyici"),
    ("web", "Web (üçüncül)"),
    ("substrate", "Substrat"),
]

CRITICAL = {
    "PUBMED_MCP_API_KEY": "MeSH K01.400 dönem-kilitli arama YAPILAMAZ",
    "OTTOMAN_ARCHIVES_MCP_API_KEY": "dijital birincil kaynak erişimi KAPALI",
    "OPENALEX_MCP_API_KEY": "beşeri bilimler literatürü + atıf grafı KAPALI",
}

PERMANENT_BLOCKS = [
    ("Library of Congress manifest", "HTTP 403 — evrensel (iki bağımsız ağdan ölçüldü)"),
    ("NLM Digital Collections", "Akamai bot kapısı (202 / 0 bayt)"),
    ("Perseus / Scaife CTS", "DNS ölü + 502 + SPA kabuğu"),
    ("HathiTrust tam-metin", "Data API 403 (Bib API 200 — metadata açık)"),
    ("Europeana", "anahtar sunucuda yapılandırılmamış"),
    ("BHL (herbal/materia medica)", "ücretsiz anahtar alınmamış"),
]

DELEGATIONS = {
    "vekayinuvis": "Osmanlıca el yazması paleografi/HTR",
    "evidentia": "çağdaş klinik geçerlilik",
    "sci-audit": "RELATIO çıktı-QA",
}


def load_lock():
    p = ROOT / "fleet.lock.json"
    if not p.is_file():
        sys.exit("fleet.lock.json yok — önce: python3 tools/fleetkit/gen_fleet.py historia-medicinae")
    return json.loads(p.read_text(encoding="utf-8"))


def probe(url, key):
    """MCP initialize → sadece HTTP durumunu ölçer. Ağ hatası = ölçülemedi."""
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "historia-doctor", "version": "0.1.0"}},
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"
    except Exception as e:
        return f"ölçülemedi ({type(e).__name__})"


def plugin_installed(name):
    """~/.claude/plugins altında kurulu mu (kaba kontrol)."""
    base = Path.home() / ".claude" / "plugins"
    if not base.is_dir():
        return None
    return any(name in str(p) for p in base.rglob("plugin.json"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="MCP initialize dene (ağ gerektirir)")
    args = ap.parse_args()

    lock = load_lock()
    servers = lock.get("servers", [])
    by_band = {}
    for s in servers:
        by_band.setdefault(s.get("tier") or "?", []).append(s)

    print(f"historia-medicinae v{lock.get('plugin_version','?')} — filo durumu")
    print(f"{len(servers)} server · {lock['counts']['gated']} anahtarlı · "
          f"{lock['counts']['public']} public · {lock['counts']['companions']} companion · "
          f"{lock['counts']['delegations']} delegasyon\n")

    ok = missing = 0
    crit_missing = []
    seen = set()
    for band, label in BAND_ORDER:
        rows = by_band.get(band, [])
        if not rows:
            continue
        print(f"── {label}")
        for s in rows:
            seen.add(s["name"])
            env = s.get("auth_env")
            if not env:
                state, ok = "public", ok + 1
            elif os.environ.get(env, "").strip():
                state, ok = f"anahtar VAR ({env})", ok + 1
            else:
                state, missing = f"ANAHTAR YOK ({env})", missing + 1
                if env in CRITICAL:
                    crit_missing.append((s["name"], env))
            line = f"   {s['name']:<20} {state}"
            if args.live and (not env or os.environ.get(env, "").strip()):
                line += f"  → {probe(s['url'], os.environ.get(env or '', ''))}"
            print(line)
        print()

    leftover = [s for s in servers if s["name"] not in seen]
    if leftover:
        print("── Bant tanımsız")
        for s in leftover:
            print(f"   {s['name']:<20} tier={s.get('tier')!r}")
        print()

    print(f"Özet: {ok} kullanılabilir · {missing} anahtarsız")
    if crit_missing:
        print("\nKRİTİK EKSİK:")
        for name, env in crit_missing:
            print(f"  ! {name} ({env}) → {CRITICAL[env]}")
        print("  Çözüm: doppler run -p cureohub -c dev_personal -- claude")

    print("\nKALICI BLOKLAR (anahtarla çözülmez — ölçülmüş):")
    for name, why in PERMANENT_BLOCKS:
        print(f"  · {name}: {why}")

    print("\nDELEGASYONLAR:")
    for name, role in DELEGATIONS.items():
        st = plugin_installed(name)
        mark = "kurulu" if st else ("kurulu DEĞİL" if st is False else "bilinmiyor")
        print(f"  · {name:<14} {mark:<14} ({role})")

    print("\nNot: devlet-arsivleri tek-cihaz oturum kilidi taşır — sorgudan önce "
          "devarsiv_session_status ile canlılık doğrulanır.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
