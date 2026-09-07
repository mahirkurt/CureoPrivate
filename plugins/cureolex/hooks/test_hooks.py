#!/usr/bin/env python3
"""cureolex hook harness — hook davranış matrisi (bağımlılıksız, stdlib).

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
    # Cache sertleştirildi (salt + kimlik eşleştirme): elle yazılan LEGACY şema
    # artık kasten reddedilir. Fixture bu yüzden modülün kendi write_cache'ini
    # kullanır — hem gerçek gidiş-dönüşü sınar hem şema evrilince bayatlamaz.
    fleet_probe.write_cache(_c, {"a": {"status": "ok"}})
    check("taze cache okunur", fleet_probe.read_cache(_c, ttl=86400) == {"a": {"status": "ok"}})
    # Bayatlık testi TTL'i sınamalı, şema reddini değil: geçerli cache yazılır,
    # yalnız zaman damgası geriye alınır (kimlik alanları korunur).
    _blob = json.loads(open(_c, encoding="utf-8").read())
    _blob["ts"] = time.time() - 90000
    with open(_c, "w", encoding="utf-8") as fh:
        json.dump(_blob, fh)
    check("bayat cache → None (yeniden prob)", fleet_probe.read_cache(_c, ttl=86400) is None)
    with open(_c, "w", encoding="utf-8") as fh:
        fh.write("bu json değil {{{")
    check("bozuk cache → None (fail-open)", fleet_probe.read_cache(_c, ttl=86400) is None)

check("lock yoksa None (fail-open)", fleet_probe.load_lock("/olmayan/yol") is None)
_lock = fleet_probe.load_lock(ROOT)
check("fleet.lock.json okunur ve 22 server taşır",
      bool(_lock) and _lock["counts"]["servers"] == 22)
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
      all(s in ctx for s in ("TAM-METİN ŞELALESİ", "YALNIZ ANALİZ",
                             "oa_fetch_pdf", "download_document", "SHA-256")))

# ── Lock + prob tümleşimi (v3.5.0) ────────────────────────────────────────
_L = {"counts": {"servers": 22, "gated": 19, "public": 3,
                 "companions": 3, "delegations": 2},
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
      "22 hukuk MCP" in _ctx_plain and "14" not in _ctx_plain)
check("prob boş dönse bile bağlam üretilir (fail-open)",
      _ctx_plain.startswith("[cureolex]"))
check("lock None iken de çökmez (fail-open)",
      session_start.build_context(None, {}, {}).startswith("[cureolex]"))

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
    # Cache artık plugin adına göre ayrışır (cureonics-fleet/<plugin>.json) —
    # iki plugin aynı makinede birbirinin prob sonucunu ezmesin diye.
    check("uçtan uca: cache plugin-ayrışık izole dizine yazıldı",
          os.path.exists(os.path.join(_cd, "cureonics-fleet", "cureolex.json")))

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
          "Yargı", "Open Law", "Ansvar",
          "evidentia", "sci-audit")))

# ── Zorunlu satırlar lock'tan türer (v3.5.0) ──────────────────────────────
_rows = stop_coverage.mandatory_rows()
check("zorunlu satır sayısı = 3 companion + 2 delegasyon", len(_rows) == 5,
      f"{len(_rows)}: {sorted(_rows)}")
check("yoktez ARTIK zorunlu companion satırı değil (wire'landı)",
      not [k for k in _rows if "YokTez" in k or "YÖK-Tez" in k], sorted(_rows))
check("lock yoksa gömülü listeye düşer (fail-open)",
      len(stop_coverage.mandatory_rows({})) == 5)
with open(os.path.join(SCRIPTS, "stop_coverage.py"), encoding="utf-8") as fh:
    _sc = fh.read()
check("hardcoded MANDATORY_ROWS sabiti kaldırıldı", "\nMANDATORY_ROWS = {" not in _sc)
check("kök hooks.json kopyası kaldırıldı (hooks/hooks.json kanonik)",
      not os.path.exists(os.path.join(ROOT, "hooks.json")))
full = ("MADDE 1 - ... gerekçe ... Kapsam Manifestosu (G0): mevzuat → hit 3; Yarg → hit 2; "
        "Open_Law → skipped: companion bağlı değil ⇒ G6 CONDITIONAL; Ansvar → empty; "
        "Fedlex_Swiss → skipped: companion bağlı değil (CH satırı manual_required); "
        "YokTez → hit 1; Turk_Patent → skipped: mod için N/A (IP-boyut yok); evidentia → hit; "
        "sci-audit → hit; confidence_label: combined_confidence MODERATE human_review_required:true")
rc, out = run("stop_coverage.py", {"last_assistant_message": full, "stop_hook_active": False})
check("tam çıktı-sözleşmesi → sessiz PASS", rc == 0 and not out)
rc, out = run("stop_coverage.py", {"last_assistant_message": "MADDE 1 gerekçe 5210", "stop_hook_active": True})
check("stop_hook_active döngü koruması → sessiz", rc == 0 and not out)

# ── Kapsam daraltma (2026-09-07): mühendislik turu reform çıktısı sanılmasın ──
# ÖLÇÜLEN YANLIŞ POZİTİF: üç MCP sunucusunun denetim raporu, yalnız "gerekçe" +
# "madde 4.3" kelimeleri yüzünden reform-modu sanılıp G0 manifestosu istendi.
_eng = ("Üç sunucunun kaynak kodunu okudum. Reddettiğim seçenekleri gerekçeleriyle yazdım; "
        "ayrıntı planda madde 4.3 olarak duruyor. Ölçüm: 6/6 kayıt DOI taşıyor.")
rc, out = run("stop_coverage.py", {"last_assistant_message": _eng, "stop_hook_active": False})
check("mühendislik turu ('gerekçe' + 'madde 4.3') → sessiz", rc == 0 and not out,
      f"out={str(out)[:120]}")

# Mod jetonları BÜYÜK-HARF DUYARLI olmalı: sıradan İngilizce kelimeler mod bildirimi değildir.
_eng_en = ("I will draft the change, analyze the failure, and comply with the amendment "
           "policy. The rationale is recorded. This is a code review, not legislation.")
rc, out = run("stop_coverage.py", {"last_assistant_message": _eng_en, "stop_hook_active": False})
check("İngilizce 'draft/analyze/comply/amend' → mod bildirimi DEĞİL → sessiz",
      rc == 0 and not out, f"out={str(out)[:120]}")

# META-TUR baskılayıcı: hook'un kendi kodunu konuşan tur.
_meta = ("hooks/scripts/stop_coverage.py içindeki MODE_SIGNALS listesini daralttım; "
         "MADDE 1 gibi örnekler yalnız fixture. 5210 sayılı kanun örnek olarak geçiyor.")
rc, out = run("stop_coverage.py", {"last_assistant_message": _meta, "stop_hook_active": False})
check("plugin-iç öz-referans (meta-tur) → sessiz", rc == 0 and not out, f"out={str(out)[:120]}")

# Gerçek reform metni HÂLÂ yakalanmalı (daraltma invaryantı öldürmedi).
rc, out = run("stop_coverage.py",
              {"last_assistant_message": "MADDE 3 - Bu Yönetmeliğin amacı ... 3359 sayılı Kanun",
               "stop_hook_active": False})
check("gerçek yasama metni (MADDE + 'sayılı') → hâlâ block",
      (out or {}).get("decision") == "block", f"out={str(out)[:120]}")


def _transcript(tool_names):
    """Son kullanıcı prompt'u + verilen araçları çağıran asistan turu (JSONL)."""
    fd = tempfile.mkdtemp()
    path = os.path.join(fd, "t.jsonl")
    recs = [{"type": "user", "message": {"content": [{"type": "text", "text": "yap"}]}}]
    recs.append({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": n} for n in tool_names]}})
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return path


_reform_text = "MADDE 1 - ... gerekçe ... 5210 uyumlu yönetmelik taslağı"
# Davranış kapısı: filo aracı çağrılmadıysa metin ne derse desin sessiz.
rc, out = run("stop_coverage.py", {"last_assistant_message": _reform_text,
                                   "transcript_path": _transcript(["Bash", "Read", "Write"]),
                                   "stop_hook_active": False})
check("transkript var + filo aracı YOK → davranış kapısı kapalı → sessiz",
      rc == 0 and not out, f"out={str(out)[:120]}")

# Saf teşhis ucu kapıyı AÇMAZ (bir sunucuyu yoklamak hukuk araştırması değildir).
rc, out = run("stop_coverage.py", {"last_assistant_message": _reform_text,
                                   "transcript_path": _transcript(
                                       ["mcp__openathens__oa_server_info"]),
                                   "stop_hook_active": False})
check("yalnız *_server_info çağrıldı → kapı kapalı → sessiz",
      rc == 0 and not out, f"out={str(out)[:120]}")

# Gerçek filo veri-aracı çağrıldıysa manifesto BEKLENİR.
rc, out = run("stop_coverage.py", {"last_assistant_message": _reform_text,
                                   "transcript_path": _transcript(
                                       ["mcp__mevzuat__search_mevzuat"]),
                                   "stop_hook_active": False})
check("gerçek filo veri-aracı çağrıldı + manifesto yok → block",
      (out or {}).get("decision") == "block", f"out={str(out)[:120]}")

import _turn_tools as _tt  # noqa: E402
check("_turn_tools: companion (Yargı/Open_Law/Ansvar) filo aracı sayılır",
      all(_tt.fleet_data_tool_invoked({"transcript_path": _transcript([n])})
          for n in ("mcp__Yarg__search_detailed", "mcp__Open_Law__lookup_statute",
                    "mcp__claude_ai_Ansvar__search")))
check("_turn_tools: transkript yoksa transcript_available False (yedeğe düşülür)",
      not _tt.transcript_available({"transcript_path": "/yok/olmayan.jsonl"}))

print("== anamnesis collection (guard / ledger / lifecycle) ==")
import json as _json
import anamnesis_run as _ar  # noqa: E402

ANAM_SID = "aabbccddeeff"
ANAM_COLL = f"cureolex:sess:{ANAM_SID}"
ANAM_DOC = f"{ANAM_COLL}:mevzuat:1219/1"
ANAM_FOREIGN = "celex:99999R0000"


def _anam_env(docs=None, pending=None):
    tmp = tempfile.mkdtemp()
    ledger = os.path.join(tmp, "anamnesis-cureolex.json")
    log = os.path.join(tmp, "forget.jsonl")
    payload = {
        "plugin": "cureolex",
        "kind": "sess",
        "session_id": ANAM_SID,
        "collection": ANAM_COLL,
        "doc_ids": list(docs or []),
        "pending_forget": list(pending or []),
        "status": "active",
    }
    with open(ledger, "w", encoding="utf-8") as fh:
        _json.dump(payload, fh)
    env = {
        "CUREOLEX_ANAMNESIS_LEDGER": ledger,
        "CUREOLEX_ANAMNESIS_FORGET_LOG": log,
        "CUREOLEX_ANAMNESIS_NO_NETWORK": "1",
        "CLAUDE_PROJECT_DIR": tmp,
    }
    return env, ledger, log


def _anam_decision(j):
    if not j:
        return "ALLOW"
    hso = j.get("hookSpecificOutput", {})
    if hso.get("permissionDecision") == "deny":
        return "DENY"
    if j.get("systemMessage") or hso.get("additionalContext"):
        return "MSG"
    return "ALLOW"


def _g(tool, inp=None, e=None):
    payload = {"tool_name": tool}
    if inp is not None:
        payload["tool_input"] = inp
    _, j = run("anamnesis_guard.py", payload, env_extra=e)
    return _anam_decision(j), j


env, ledger, log = _anam_env()
got, j = _g("mcp__mevzuat__search_mevzuat", {}, env)
check("non-anamnesis MCP → ALLOW (kaynak filo bloklanmaz)", got == "ALLOW")

got, j = _g("mcp__anamnesis__hybrid_query", {"queries": ["ruhsat"]}, env)
check("hybrid_query unscoped → DENY", got == "DENY")
reason = ((j or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")
check("hybrid deny reason mentions collection / doc_scope yok",
      "collection" in reason.lower() and "doc_scope" in reason.lower())

got, _ = _g("mcp__anamnesis__hybrid_query",
            {"collection": ANAM_COLL, "queries": ["ruhsat"]}, env)
check("hybrid_query + collection → ALLOW", got == "ALLOW")

got, _ = _g("mcp__anamnesis__hybrid_query",
            {"collection": "evidentia:run:ffffffffffff", "queries": ["x"]}, env)
check("hybrid_query peer evidentia collection → ALLOW", got == "ALLOW")
got, _ = _g("mcp__anamnesis__semantic_search",
            {"query": "x", "collection": "evidentia:run:aabbccddeeff"}, env)
check("semantic_search peer evidentia collection → ALLOW", got == "ALLOW")
got, _ = _g("mcp__anamnesis__hybrid_query",
            {"collection": "cureolex:sess:ffffffffffff", "queries": ["x"]}, env)
check("hybrid_query wrong own sess → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__hybrid_query",
            {"doc_ids": ["evrun:ffffffffffff:10.1/x"], "queries": ["x"]}, env)
check("hybrid_query peer evrun doc_ids → ALLOW", got == "ALLOW")

got, _ = _g("mcp__anamnesis__hybrid_query",
            {"doc_ids": [ANAM_DOC], "queries": ["ruhsat"]}, env)
check("hybrid_query + prefixed doc_ids[] → ALLOW", got == "ALLOW")

got, _ = _g("mcp__anamnesis__graph_neighbors", {"node": "madde:8"}, env)
check("graph_neighbors unscoped → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__graph_neighbors",
            {"collection": ANAM_COLL, "node": "madde:8"}, env)
check("graph_neighbors + collection → ALLOW", got == "ALLOW")
got, _ = _g("mcp__anamnesis__subgraph", {"seed": "mevzuat:1219/1"}, env)
check("subgraph unscoped → DENY", got == "DENY")

got, _ = _g("mcp__anamnesis__ingest_document",
            {"doc_id": ANAM_FOREIGN, "text": "x"}, env)
check("ingest unprefixed / no collection → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__ingest_document",
            {"collection": ANAM_COLL, "doc_id": ANAM_FOREIGN, "text": "x"}, env)
check("ingest collection + unprefixed human id → DENY (rewrite)", got == "DENY")
got, _ = _g("mcp__anamnesis__ingest_document",
            {"collection": ANAM_COLL, "doc_id": ANAM_DOC, "text": "x"}, env)
check("ingest collection + prefixed doc_id → ALLOW", got == "ALLOW")
got, _ = _g("mcp__anamnesis__ingest_document",
            {"collection": f"cureolex:lib:{ANAM_SID}",
             "doc_id": f"cureolex:lib:{ANAM_SID}:mevzuat:1219/1", "text": "x"}, env)
check("ingest lib while sess active → DENY (lib not default)", got == "DENY")

got, _ = _g("mcp__anamnesis__semantic_search", {"query": "ruhsat"}, env)
check("semantic_search unscoped → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__semantic_search",
            {"query": "ruhsat", "doc_id": ANAM_DOC}, env)
check("semantic_search prefixed doc_id → ALLOW", got == "ALLOW")

got, _ = _g("mcp__anamnesis__corpus_stats", {}, env)
check("corpus_stats observe-only → ALLOW", got == "ALLOW")
got, _ = _g("mcp__anamnesis__forget_document", {"doc_id": ANAM_FOREIGN}, env)
check("forget foreign/unprefixed → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__forget_document", {"doc_id": ANAM_DOC}, env)
check("forget own prefixed id → ALLOW", got == "ALLOW")
got, _ = _g("mcp__anamnesis__forget_collection",
            {"collection": "evidentia:run:ffffffffffff"}, env)
check("forget_collection peer plugin → ALLOW (pass-through)", got == "ALLOW")
got, _ = _g("mcp__anamnesis__forget_collection",
            {"collection": "cureolex:sess:ffffffffffff"}, env)
check("forget_collection wrong own sess → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__forget_collection",
            {"collection": ANAM_COLL}, env)
check("forget_collection own sess → ALLOW", got == "ALLOW")

got, _ = _g("mcp__anamnesis__upsert_triples",
            {"triples": [{"subject": "a", "predicate": "dayanak", "object": "b"}]},
            env)
check("triples missing prefixed doc_id → DENY", got == "DENY")
got, _ = _g("mcp__anamnesis__upsert_triples",
            {"triples": [{"subject": "a", "predicate": "dayanak", "object": "b",
                          "doc_id": ANAM_DOC}]}, env)
check("triples prefixed → ALLOW", got == "ALLOW")

off = tempfile.mkdtemp()
os.makedirs(os.path.join(off, ".claude"))
open(os.path.join(off, ".claude", "cureolex-anamnesis-guard.off"), "w").close()
got, _ = _g("mcp__anamnesis__hybrid_query", {"queries": ["x"]},
            {**env, "CLAUDE_PROJECT_DIR": off})
check("disable-flag bypasses unscoped hybrid deny", got == "ALLOW")

check("scoped_doc_id keeps human mevzuat: suffix",
      _ar.scoped_doc_id(ANAM_COLL, "mevzuat:1219/1") == ANAM_DOC)
check("scoped_doc_id rewrites stale sess prefix",
      _ar.scoped_doc_id(ANAM_COLL, "cureolex:sess:ffffffffffff:celex:32007R1394")
      == f"{ANAM_COLL}:celex:32007R1394")

env2, ledger2, _ = _anam_env()
_, j = run("anamnesis_ledger.py", {
    "tool_name": "mcp__plugin-cureolex-anamnesis__ingest_document",
    "tool_input": {"collection": ANAM_COLL, "doc_id": ANAM_DOC, "text": "gövde"},
    "tool_result": _json.dumps({"doc_id": ANAM_DOC, "chunks": 3}),
}, env_extra=env2)
stored = _json.loads(open(ledger2, encoding="utf-8").read()).get("doc_ids") or []
check("ledger records prefixed ingest", ANAM_DOC in stored)
check("ledger ingest injects collection context", _anam_decision(j) == "MSG"
      and ANAM_COLL in str(j))

_, _ = run("anamnesis_ledger.py", {
    "tool_name": "mcp__anamnesis__ingest_document",
    "tool_input": {"doc_id": ANAM_FOREIGN, "text": "x"},
    "tool_result": "{}",
}, env_extra=env2)
check("ledger ignores unprefixed foreign id",
      ANAM_FOREIGN not in (_json.loads(open(ledger2, encoding="utf-8").read())
                           .get("doc_ids") or []))

_, _ = run("anamnesis_ledger.py", {
    "tool_name": "mcp__anamnesis__forget_document",
    "tool_input": {"doc_id": ANAM_DOC},
    "tool_result": _json.dumps({"existed": True}),
}, env_extra=env2)
check("ledger drops forgotten id",
      ANAM_DOC not in (_json.loads(open(ledger2, encoding="utf-8").read())
                       .get("doc_ids") or []))

env3, ledger3, log3 = _anam_env(docs=[ANAM_DOC])
_, j = run("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart", "source": "startup",
}, env_extra=env3)
after = _json.loads(open(ledger3, encoding="utf-8").read())
check("startup mints a new session_id", after.get("session_id") != ANAM_SID)
check("startup collection is cureolex:sess:",
      str(after.get("collection", "")).startswith("cureolex:sess:"))
check("startup does not carry previous docs into the new sess",
      ANAM_DOC not in (after.get("doc_ids") or []))
check("startup stub-forgets leftover docs (crash residue)",
      os.path.isfile(log3) and ANAM_DOC in open(log3, encoding="utf-8").read())
ctx = ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
check("startup context names the new collection",
      after.get("collection", "") in ctx)

env4, ledger4, log4 = _anam_env(docs=[ANAM_DOC])
_, _ = run("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart", "source": "resume",
}, env_extra=env4)
check("resume keeps sess (G0–G9 cache)",
      _json.loads(open(ledger4, encoding="utf-8").read()).get("session_id") == ANAM_SID)
check("resume does not forget",
      not (os.path.isfile(log4) and open(log4, encoding="utf-8").read().strip()))

env5, ledger5, log5 = _anam_env(docs=[ANAM_DOC])
_, _ = run("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart", "source": "compact",
}, env_extra=env5)
check("compact keeps working set",
      ANAM_DOC in (_json.loads(open(ledger5, encoding="utf-8").read())
                   .get("doc_ids") or []))

env6, ledger6, log6 = _anam_env(docs=[ANAM_DOC])
poisoned = _json.loads(open(ledger6, encoding="utf-8").read())
poisoned["doc_ids"] = [ANAM_DOC, ANAM_FOREIGN]
open(ledger6, "w", encoding="utf-8").write(_json.dumps(poisoned))
_, _ = run("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"},
           env_extra=env6)
logged_ids = []
if os.path.isfile(log6):
    for line in open(log6, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            row = _json.loads(line)
        except Exception:
            continue
        if row.get("doc_id"):
            logged_ids.append(row["doc_id"])
check("SessionEnd forgets own prefixed id", ANAM_DOC in logged_ids)
check("SessionEnd does not forget unprefixed foreign id",
      ANAM_FOREIGN not in logged_ids)
check("SessionEnd clears doc_ids",
      not _json.loads(open(ledger6, encoding="utf-8").read()).get("doc_ids"))

env7, _, log7 = _anam_env(docs=[])
rc, _ = run("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"},
            env_extra=env7)
check("empty SessionEnd exit 0", rc == 0)
check("empty SessionEnd writes no forget calls",
      not (os.path.isfile(log7) and open(log7, encoding="utf-8").read().strip()))

env8, ledger8, log8 = _anam_env(docs=[ANAM_DOC])
_, j = run("anamnesis_lifecycle.py", {
    "hook_event_name": "UserPromptSubmit",
    "prompt": "/lex-draft ATMP yönetmeliği",
}, env_extra=env8)
check("/lex-draft does NOT remint (G0–G9 same sess)",
      _json.loads(open(ledger8, encoding="utf-8").read()).get("session_id") == ANAM_SID)
check("/lex-draft does not forget",
      not (os.path.isfile(log8) and open(log8, encoding="utf-8").read().strip()))
check("/lex-draft re-injects collection",
      ANAM_COLL in (((j or {}).get("hookSpecificOutput") or {})
                    .get("additionalContext", "")))

_, _ = run("anamnesis_lifecycle.py", {
    "hook_event_name": "UserPromptSubmit",
    "prompt": "/lex-connectors",
}, env_extra=env8)
check("/lex-connectors does not remint",
      _json.loads(open(ledger8, encoding="utf-8").read()).get("session_id") == ANAM_SID)

env9, ledger9, log9 = _anam_env(docs=[ANAM_DOC], pending=[ANAM_DOC])
# pending_forget on startup is crash residue — rotate must stub-forget it
_, _ = run("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart", "source": "startup",
}, env_extra=env9)
check("startup forgets pending_forget crash residue",
      os.path.isfile(log9) and ANAM_DOC in open(log9, encoding="utf-8").read())

with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as fh:
    _hj = _json.load(fh)
check("PreToolUse anamnesis guard wired",
      any("anamnesis_guard" in (h.get("command") or "")
          for ev in _hj["hooks"].get("PreToolUse", [])
          for block in ev.get("hooks", [])
          for h in ([block] if "command" in block else block.get("hooks", []))))
# flatten: our json has hooks[].hooks[].command
_pre = [h.get("command", "") for ev in _hj["hooks"]["PreToolUse"]
        for h in ev["hooks"]]
check("PreToolUse command is anamnesis_guard.py",
      any("anamnesis_guard.py" in c for c in _pre))
_stop = [h.get("command", "") for ev in _hj["hooks"]["Stop"] for h in ev["hooks"]]
check("Stop has no anamnesis forget (yalnız stop_coverage)",
      all("anamnesis" not in c for c in _stop) and any("stop_coverage" in c for c in _stop))
_end = [h.get("command", "") for ev in _hj["hooks"].get("SessionEnd", [])
        for h in ev["hooks"]]
check("SessionEnd lifecycle wired", any("anamnesis_lifecycle.py" in c for c in _end))
check("ledger filename is plugin-private (not evidentia)",
      _ar.LEDGER_NAME == "anamnesis-cureolex.json")
check("kind default is sess not lib", _ar.KIND_DEFAULT == "sess")

# retrieve_dont_dump must not recommend phantom doc_scope
huge = {"tool_name": "mcp__mevzuat__get_mevzuat_text",
        "tool_response": {"content": [{"type": "text", "text": "X" * 40000}]}}
rc, out = run("retrieve_dont_dump.py", huge, env_extra=env)
check("30KB+ yönlendirme collection kullanır, doc_scope önermez",
      rc == 0 and "collection" in str(out).lower()
      and "doc_scope=" not in str(out).lower())

print(f"\nTOPLAM: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
