#!/usr/bin/env python3
"""lex-sanitas hook harness — 4 hook'un davranış matrisi (bağımlılıksız, stdlib).

Çalıştırma: python3 hooks/test_hooks.py  (plugin kökünden)
Her vaka hook'u gerçek subprocess olarak, gerçek stdin sözleşmesiyle çağırır.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
ROOT = os.path.dirname(HERE)
PASS, FAIL = 0, 0

sys.path.insert(0, SCRIPTS)
import fleet_probe  # noqa: E402
import stop_coverage  # noqa: E402


def run(script, payload, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30, env=env,
    )
    out = None
    if r.stdout.strip():
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"_raw": r.stdout}
    return r.returncode, out


def check(name, cond, detail=""):
    global PASS, FAIL
    status = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))


print("== fleet_probe.py (canlı prob sınıflandırması) ==")
check("401 → unauthorized (titck sınıfı: YAPILANDIRMA ARIZASI, degrade değil)",
      fleet_probe.classify(401, "") == "unauthorized")
check("403 → unauthorized", fleet_probe.classify(403, "") == "unauthorized")
check("200 + JSON-RPC result → ok",
      fleet_probe.classify(200, '{"jsonrpc":"2.0","id":1,"result":{"x":1}}') == "ok")
check("200 + SSE gövdesi → ok",
      fleet_probe.classify(
          200, 'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"x":1}}\n') == "ok")
check("200 + JSON-RPC error → error",
      fleet_probe.classify(200, '{"jsonrpc":"2.0","id":1,"error":{"code":-1}}') == "error")
check("200 + ayrıştırılamaz gövde → error", fleet_probe.classify(200, "<html>") == "error")
check("503 → unreachable", fleet_probe.classify(503, "") == "unreachable")
check("bağlantı yok (http=None) → unreachable", fleet_probe.classify(None, "") == "unreachable")

_r = fleet_probe.probe_server(
    {"name": "x", "url": "https://ornek.invalid/mcp", "auth_env": "YOK_BOYLE_ANAHTAR"},
    env={}, timeout=0.1)
check("anahtar yoksa AĞA ÇIKILMAZ → auth_missing",
      _r["status"] == "auth_missing" and _r["http"] is None, str(_r))

with tempfile.TemporaryDirectory() as _d:
    _c = os.path.join(_d, "fleet_probe.json")
    with open(_c, "w", encoding="utf-8") as fh:
        json.dump({"ts": time.time(), "results": {"a": {"status": "ok"}}}, fh)
    check("taze cache okunur", fleet_probe.read_cache(_c, ttl=86400) == {"a": {"status": "ok"}})
    with open(_c, "w", encoding="utf-8") as fh:
        json.dump({"ts": time.time() - 90000, "results": {}}, fh)
    check("bayat cache → None (yeniden prob)", fleet_probe.read_cache(_c, ttl=86400) is None)
    with open(_c, "w", encoding="utf-8") as fh:
        fh.write("bu json değil {{{")
    check("bozuk cache → None (fail-open)", fleet_probe.read_cache(_c, ttl=86400) is None)

check("lock yoksa None (fail-open)", fleet_probe.load_lock("/olmayan/yol") is None)
_lock = fleet_probe.load_lock(ROOT)
check("fleet.lock.json okunur ve 19 server taşır",
      bool(_lock) and _lock["counts"]["servers"] == 19)
with open(os.path.join(SCRIPTS, "fleet_probe.py"), encoding="utf-8") as fh:
    _src = fh.read()
check("hook YALNIZ stdlib (PyYAML/requests yok)",
      "import yaml" not in _src and "import requests" not in _src)

# ── Sahada yakalanan iki arıza — regresyon koruması ────────────────────────
# Her ikisi de SAĞLIKLI server'ları sahte arızalı gösteriyordu, yani prob'un
# teşhis etmek için var olduğu hatanın aynısını üretiyorlardı.
check("açık User-Agent (urllib varsayılanı Cloudflare 1010 → sahte unauthorized)",
      "User-Agent" in _src and "Python-urllib" not in fleet_probe.USER_AGENT)
check("okuma sınırı oecd'nin 32KB initialize gövdesini kesmiyor",
      fleet_probe.READ_LIMIT > 32716)
_truncated = '{"jsonrpc":"2.0","id":1,"result":{"capabilities":{"too'
check("kesik JSON gövdesi → error (sessizce 'ok' sayılmaz)",
      fleet_probe.classify(200, _truncated) == "error")
check("eşik anamnesis'in ölçülen ~11sn gecikmesinin üstünde",
      fleet_probe.PER_ENDPOINT_TIMEOUT > 11.0)
check("tek dalga — worker sayısı ≥ filo boyutu (duvar-saati = en yavaş server)",
      fleet_probe.MAX_WORKERS >= (_lock or {}).get("counts", {}).get("servers", 99))

print("== session_start.py ==")
import session_start  # noqa: E402

rc, out = run("session_start.py", {})
ctx = (out or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
check("çıkış 0 + geçerli hook JSON", rc == 0 and bool(ctx))
check("konvansiyon enjeksiyonu (TAM-FİLO + NO-FABRICATION + companion zorunluluğu)",
      all(s in ctx for s in ("TAM-FİLO", "NO-FABRICATION", "ZORUNLU üyeleridir")))
check("delegasyon kurulum algısı satırı", "[preflight/delegasyon]" in ctx or "KURULU" in ctx)
check("tam-metin şelalesi invaryantı enjekte edilir (openathens→annas sırası)",
      "TAM-METİN ŞELALESİ" in ctx and "YALNIZ ANALİZ" in ctx)

# ── Lock + prob tümleşimi (v3.5.0) ────────────────────────────────────────
_L = {"counts": {"servers": 19, "gated": 16, "public": 3,
                 "companions": 5, "delegations": 2},
      "servers": [{"name": "titck", "auth_env": "TITCK_MCP_API_KEY"}],
      "companions": [{"name": "Yargı", "tool_prefixes": ["mcp__Yarg__"], "gate": "G5",
                      "manifest_row": "Yargı (companion — G5 içtihat)",
                      "degrade": "G5 CONDITIONAL"}],
      "delegations": [{"name": "evidentia", "plugin_id_prefix": "evidentia@",
                       "manifest_row": "evidentia (klinik delegasyon)"}]}

check("sağlıklı filoda preflight bölümü SESSİZ",
      "[preflight]" not in session_start.build_context(
          _L, {"titck": {"name": "titck", "status": "ok", "http": 200}}, {}))

_ctx_401 = session_start.build_context(
    _L, {"titck": {"name": "titck", "status": "unauthorized", "http": 401,
                   "detail": ""}}, {})
check("401 → 'YAPILANDIRMA ARIZASI' (degrade olarak sunulmaz)",
      "titck" in _ctx_401 and "YAPILANDIRMA ARIZASI" in _ctx_401
      and "degrade DEĞİL" in _ctx_401)

_ctx_miss = session_start.build_context(
    _L, {"titck": {"name": "titck", "status": "auth_missing", "http": None,
                   "detail": "${TITCK_MCP_API_KEY} süreç ortamında yok"}}, {})
check("auth_missing → doppler çözüm yolu (meşru degrade)",
      "doppler run" in _ctx_miss and "skipped: anahtar yok" in _ctx_miss)

_ctx_plain = session_start.build_context(_L, {}, {})
check("sayılar lock'tan gelir (hardcode 14 yok)",
      "19 hukuk MCP" in _ctx_plain and "14" not in _ctx_plain)
check("prob boş dönse bile bağlam üretilir (fail-open)",
      _ctx_plain.startswith("[lex-sanitas]"))
check("lock None iken de çökmez (fail-open)",
      session_start.build_context(None, {}, {}).startswith("[lex-sanitas]"))

with open(os.path.join(SCRIPTS, "session_start.py"), encoding="utf-8") as fh:
    _ss = fh.read()
check("hardcoded GATED sözlüğü kaldırıldı", "\nGATED = {" not in _ss)
check("titck 'public, etkilenmez' yalanı kaldırıldı",
      "Public server'lar — titck" not in _ss)
check("preflight fleet.lock.json'a bağlı", "load_lock" in _ss)

# Uçtan uca: anahtarı boşalt + cache'i izole et → prob TAZE koşar ve mevzuat
# 'auth_missing' düşer. (auth_missing yolu ağa çıkmaz, bu yüzden çevrimdışı da geçer.)
with tempfile.TemporaryDirectory() as _cd:
    rc, out = run("session_start.py", {},
                  env_extra={"MEVZUAT_MCP_API_KEY": "", "XDG_CACHE_HOME": _cd})
    ctx2 = (out or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
    check("uçtan uca: eksik anahtar → preflight uyarısı + doppler çözümü",
          "MEVZUAT_MCP_API_KEY" in ctx2 and "doppler run" in ctx2, ctx2[-220:])
    check("uçtan uca: cache izole dizine yazıldı",
          os.path.exists(os.path.join(_cd, "lex-sanitas", "fleet_probe.json")))

print("== scope_guard.py (UserPromptSubmit) ==")
rc, out = run("scope_guard.py", {"prompt": "SGK ödeme reddi davam için itiraz dilekçesi yaz"})
check("kapsam-dışı (bireysel dava) → uyarı/yönlendirme", out is not None and rc == 0,
      f"rc={rc} out={str(out)[:80]}")
rc, out = run("scope_guard.py", {"prompt": "ATMP yönetmelik taslağı hazırla"})
check("kapsam-içi (reform) → sessiz geçiş", rc == 0 and (out is None or not (out or {}).get("decision")))

print("== retrieve_dont_dump.py (PostToolUse) ==")
small = {"tool_name": "mcp__mevzuat__search_mevzuat", "tool_response": {"content": [{"type": "text", "text": "kısa sonuç"}]}}
rc, out = run("retrieve_dont_dump.py", small)
check("küçük çıktı → sessiz", rc == 0 and (out is None or not out))
big = {"tool_name": "mcp__mevzuat__get_mevzuat_text", "tool_response": {"content": [{"type": "text", "text": "X" * 8000}]}}
rc, out = run("retrieve_dont_dump.py", big)
check("6KB+ çıktı → devre-kesici uyarısı", rc == 0 and out is not None and bool(str(out)),
      f"rc={rc} out={str(out)[:80]}")
huge = {"tool_name": "mcp__mevzuat__get_mevzuat_text", "tool_response": {"content": [{"type": "text", "text": "X" * 40000}]}}
rc, out = run("retrieve_dont_dump.py", huge)
check("30KB+ çıktı → anamnesis/Tier-2 yönlendirmesi", rc == 0 and "anamnesis" in str(out).lower())

print("== stop_coverage.py (Stop) ==")
rc, out = run("stop_coverage.py", {"last_assistant_message": "Bugün hava güzel.", "stop_hook_active": False})
check("lex-dışı tur → sessiz", rc == 0 and not out)
rc, out = run("stop_coverage.py", {"last_assistant_message": "MADDE 1 - ... gerekçe ... 5210 uyumlu yönetmelik taslağı", "stop_hook_active": False})
check("mod-çıktısı, manifesto+label YOK → block", (out or {}).get("decision") == "block")
partial = ("MADDE 1 - ... gerekçe ... Kapsam Manifestosu (G0): mevzuat → hit 3; titck → hit 1; "
           "confidence_label: combined_confidence MODERATE human_review_required:true")
rc, out = run("stop_coverage.py", {"last_assistant_message": partial, "stop_hook_active": False})
reason = (out or {}).get("reason", "")
check("manifesto var ama companion/delegasyon satırları eksik → block + isim listesi",
      (out or {}).get("decision") == "block" and all(x in reason for x in (
          "Yargı", "Open Law", "Ansvar", "Fedlex", "YokTez", "Türk Patent", "evidentia", "sci-audit")))
full = ("MADDE 1 - ... gerekçe ... Kapsam Manifestosu (G0): mevzuat → hit 3; Yarg → hit 2; "
        "Open_Law → skipped: companion bağlı değil ⇒ G6 CONDITIONAL; Ansvar → empty; "
        "Fedlex_Swiss → skipped: companion bağlı değil (CH satırı manual_required); "
        "YokTez → hit 1; Turk_Patent → skipped: mod için N/A (IP-boyut yok); evidentia → hit; "
        "sci-audit → hit; confidence_label: combined_confidence MODERATE human_review_required:true")
rc, out = run("stop_coverage.py", {"last_assistant_message": full, "stop_hook_active": False})
check("tam çıktı-sözleşmesi → sessiz PASS", rc == 0 and not out)
rc, out = run("stop_coverage.py", {"last_assistant_message": "MADDE 1 gerekçe 5210", "stop_hook_active": True})
check("stop_hook_active döngü koruması → sessiz", rc == 0 and not out)

print(f"\nTOPLAM: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
