#!/usr/bin/env python3
"""vekayinuvis Stop-hook davranış matrisi (bağımlılıksız, stdlib).

Çalıştırma: python3 hooks/test_hooks.py   (plugin kökünden)
Her vaka hook'u gerçek subprocess olarak, gerçek stdin sözleşmesiyle çağırır.

Odak: hook'ların ATIF ile İSİM GEÇİŞİ'ni ayırt etmesi. devlet-arsivleri MCP'sinin kendi
kodu üzerinde çalışmak (araç adları, env değişkenleri, test fixture'ları) atıf DEĞİLDİR
ve hook'u ateşlememelidir; gerçek bir arşiv künyesi ise disiplini aynen zorlamalıdır.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
PASS, FAIL = 0, 0


def run(script, text, extra=None, env=None):
    payload = {"last_assistant_message": text}
    if extra:
        payload.update(extra)
    e = os.environ.copy()
    if env:
        e.update(env)
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        env=e,
    )
    out = None
    if r.stdout.strip():
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"_raw": r.stdout}
    return out


def blocks(script, text, extra=None):
    out = run(script, text, extra)
    return bool(out and out.get("decision") == "block")


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))


def additional_context(out):
    return ((out or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")


# --- gerçek atıf örnekleri (hook ATEŞLEMELİ / disiplin tamsa susmalı) ---------------
CITATION_NO_DATE = (
    "Tahaffuzhane inşasına dair kayıt: BOA, DH.MKT 1234/56. Belge karantina "
    "tedbirlerini düzenliyor."
)
CITATION_FULL = (
    "Tahaffuzhane inşasına dair: BOA, DH.MKT 1234/56, H-27-12-1337 (M. 1919). "
    "Katalog: https://katalog.devletarsivleri.gov.tr/Sayfalar/eSatis/BelgeGoster.aspx"
    "?ItemId=31664060&Hash=758C&A=2"
)
CITATION_NO_URL = (
    "devarsiv_search ile doğrulanan kayıt: BOA, İ.SH. 12/3, H-1310 (M. 1892). "
    "Fon Dahiliye Sıhhiye."
)
OCR_CLAIM_NO_PROV = (
    "BOA, DH.MKT 1234/56, H-1310 (M. 1892) — OCR ile okundu. Katalog: "
    "https://katalog.devletarsivleri.gov.tr/BelgeGoster.aspx?ItemId=1&Hash=A "
    "Metin: 'tahaffuzhane inşasına dair...'"
)

# --- mühendislik bağlamı (hook SUSMALI — bu turun düzelttiği yanlış-pozitif) --------
ENGINEERING_TOOLS = (
    "devarsiv_get_belge item_id + hash alıyor; hash yalnız arama sonucundan gelir. "
    "devarsiv_ocr_belge OCR/HTR metni döner. Store şeması item_id, fon, kutu, gomlek, "
    "ozet, tarih, belge_url taşıyacak."
)
ENGINEERING_FIXTURE = (
    'Test fixture: {"item_id": "1", "arsiv_kod": "2", "fon": "DH.MKT", "kutu": "1", '
    '"gomlek": "2", "ozet": "tahaffuzhane", "hash": "ABC123"}. '
    "DEVARSIV_STORE_PATH ayarlıysa store açılır; BelgeGoster.aspx sayfa taramasını "
    "sample_picture içinde base64 verir."
)
ENGINEERING_PLAN = (
    "Plan 1: store.py + harvest defteri + devarsiv_deep_search. fon/kutu/gömlek üçlüsü "
    "üzerinden dedup. mcp-servers/devlet-arsivleri-mcp/src/devlet_arsivleri_mcp/store.py "
    "oluşturulacak; mevzuat ve tbmm connector'larıyla aynı kalıp."
)

print("== citation_discipline.py ==")
check("gerçek künye, çift-tarih yok → BLOCK",
      blocks("citation_discipline.py", CITATION_NO_DATE))
check("gerçek künye + çift-tarih + katalog URL → sessiz",
      not blocks("citation_discipline.py", CITATION_FULL))
check("devarsiv-doğrulanmış künye, katalog URL yok → BLOCK",
      blocks("citation_discipline.py", CITATION_NO_URL))
check("OCR iddiası, provenance yok → BLOCK",
      blocks("citation_discipline.py", OCR_CLAIM_NO_PROV))
check("araç adları/şema konuşması → sessiz (isim geçişi atıf değil)",
      not blocks("citation_discipline.py", ENGINEERING_TOOLS))
check('test fixture "fon": "DH.MKT" → sessiz (kutu/gömlek numarası yok)',
      not blocks("citation_discipline.py", ENGINEERING_FIXTURE))
check("uygulama planı düzyazısı → sessiz",
      not blocks("citation_discipline.py", ENGINEERING_PLAN))
check("stop_hook_active → sessiz (döngü koruması)",
      not blocks("citation_discipline.py", CITATION_NO_DATE, {"stop_hook_active": True}))
check("boş mesaj → sessiz", not blocks("citation_discipline.py", ""))

print("== full-text delivery hooks ==")
pdf_out = run(
    "retrieve_dont_dump.py", "",
    {"tool_name": "mcp__openathens__oa_fetch_pdf", "tool_result": "x" * 7000},
)
check("oa_fetch_pdf büyük çıktısı retrieve-don't-dump uyarısı üretir",
      "retrieve-don't-dump" in additional_context(pdf_out))
download_out = run(
    "retrieve_dont_dump.py", "",
    {"tool_name": "mcp__annas-reader__download_document", "tool_result": "x" * 31000},
)
check("download_document çok büyük çıktısı anamnesis'e yönlenir",
      "anamnesis.ingest_document" in additional_context(download_out))
session_out = run("session_start.py", "")
session_ctx = additional_context(session_out)
check("SessionStart yeni dosya araçlarını ve checksum disiplinini enjekte eder",
      all(s in session_ctx for s in ("oa_fetch_pdf", "download_document", "SHA-256")))

print("== stop_coverage.py ==")
MANIFEST_ROWS = " ".join(
    f"{s} → empty: kapsam dışı." for s in [
        "ottoman-archives", "devlet-arsivleri", "yoktez", "literatur", "consensus",
        "scholar-gateway", "exa", "tavily", "paper-search", "openathens",
        "annas-reader", "yok-akademik", "anamnesis", "resmigazete", "mevzuat",
        "tbmm", "detsis",
    ]
)
MODE_NO_MANIFEST = "SOURCE_HUNT modunda tarama yapıldı; sonuçlar aşağıda."
MODE_WITH_MANIFEST = "SOURCE_HUNT taraması. G0 kapsam manifestosu: " + MANIFEST_ROWS
RESEARCH_NO_MANIFEST = (
    "devarsiv ve ottoman-archives taramasından: BOA, DH.MKT 1234/56, H-1310 (M. 1892) "
    "tahaffuzhane kaydı bulundu."
)

check("mod bildirimi var, manifesto yok → BLOCK",
      blocks("stop_coverage.py", MODE_NO_MANIFEST))
check("mod + tam 17-satır manifesto → sessiz",
      not blocks("stop_coverage.py", MODE_WITH_MANIFEST))
check("künye + 2 connector, manifesto yok → BLOCK",
      blocks("stop_coverage.py", RESEARCH_NO_MANIFEST))
check("araç adları/şema konuşması → sessiz (isim geçişi tarama değil)",
      not blocks("stop_coverage.py", ENGINEERING_TOOLS))
check("uygulama planı (devarsiv+mevzuat+tbmm anılıyor) → sessiz",
      not blocks("stop_coverage.py", ENGINEERING_PLAN))
check("test fixture → sessiz",
      not blocks("stop_coverage.py", ENGINEERING_FIXTURE))
check("stop_hook_active → sessiz (döngü koruması)",
      not blocks("stop_coverage.py", MODE_NO_MANIFEST, {"stop_hook_active": True}))

# --- Anamnesis münhasır collection (canlı MCP yok; FORGET_LOG stub) --------------
ANAM_RUN = "aabbccddeeff"
ANAM_PREFIX = f"vkrun:{ANAM_RUN}:"
ANAM_COLL = f"vekayinuvis:run:{ANAM_RUN}"


def run_payload(script, payload, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        env=e,
    )
    out = None
    if r.stdout.strip():
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"_raw": r.stdout}
    return r.returncode, out


def decision(j):
    if not j:
        return "ALLOW"
    hso = j.get("hookSpecificOutput", {})
    if hso.get("permissionDecision") == "deny":
        return "DENY"
    if j.get("systemMessage") or hso.get("additionalContext"):
        return "MSG"
    return "ALLOW"


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _anam_env(docs=None):
    tmp = tempfile.mkdtemp()
    ledger = os.path.join(tmp, "ledger.json")
    log = os.path.join(tmp, "forget.jsonl")
    payload = {
        "run_id": ANAM_RUN,
        "collection": ANAM_COLL,
        "prefix": ANAM_PREFIX,
        "doc_ids": list(docs or []),
        "pending_forget": [],
        "status": "active",
    }
    with open(ledger, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    env = {
        "VEKAYI_ANAMNESIS_LEDGER": ledger,
        "VEKAYI_ANAMNESIS_FORGET_LOG": log,
        "VEKAYI_ANAMNESIS_NO_NETWORK": "1",
        "CLAUDE_PROJECT_DIR": tmp,
    }
    return env, ledger, log


print("== anamnesis guard / ledger / lifecycle ==")
env, ledger, log = _anam_env()
scoped = ANAM_PREFIX + "devarsiv:2/DH.I.UM/22-19"
foreign = "doi:10.9999/foreign-chunk"


def g(tool, inp=None, e=None):
    payload = {"tool_name": tool}
    if inp is not None:
        payload["tool_input"] = inp
    _, j = run_payload("anamnesis_guard.py", payload, e or env)
    return decision(j), j


guard_cases = [
    ("mcp__anamnesis__ingest_document", None, "DENY", "ingest missing collection/doc_id"),
    ("mcp__anamnesis__ingest_document", {"doc_id": "devarsiv:2/DH.I.UM/22-19"}, "DENY",
     "ingest unprefixed devarsiv"),
    ("mcp__anamnesis__ingest_document",
     {"collection": ANAM_COLL, "doc_id": "devarsiv:2/DH.I.UM/22-19"}, "DENY",
     "ingest collection but unprefixed doc_id"),
    ("mcp__anamnesis__ingest_document",
     {"collection": ANAM_COLL, "doc_id": scoped}, "ALLOW",
     "ingest collection + vkrun prefix"),
    ("mcp__anamnesis__hybrid_query", {"query": "tahaffuzhane"}, "DENY",
     "hybrid_query unscoped"),
    ("mcp__anamnesis__hybrid_query",
     {"query": "tahaffuzhane", "collection": ANAM_COLL}, "ALLOW",
     "hybrid_query scoped"),
    ("mcp__anamnesis__hybrid_query",
     {"query": "x", "collection": "vekayinuvis:run:ffffffffffff"}, "DENY",
     "hybrid_query other-run"),
    ("mcp__anamnesis__hybrid_query",
     {"query": "x", "collection": "evidentia:run:ffffffffffff"}, "ALLOW",
     "hybrid_query peer evidentia pass-through"),
    ("mcp__anamnesis__hybrid_query",
     {"query": "x", "collection": "cureolex:sess:aabbccddeeff"}, "ALLOW",
     "hybrid_query peer cureolex pass-through"),
    ("mcp__anamnesis__graph_neighbors", {"node": "kişi:x"}, "DENY",
     "graph_neighbors unscoped"),
    ("mcp__anamnesis__graph_neighbors",
     {"node": "kişi:x", "collection": ANAM_COLL}, "ALLOW",
     "graph_neighbors scoped"),
    ("mcp__anamnesis__subgraph", {"entities": ["x"]}, "DENY", "subgraph unscoped"),
    ("mcp__anamnesis__subgraph",
     {"entities": ["x"], "collection": ANAM_COLL}, "ALLOW", "subgraph scoped"),
    ("mcp__anamnesis__semantic_search", {"query": "x"}, "DENY",
     "semantic_search unscoped"),
    ("mcp__anamnesis__semantic_search",
     {"query": "x", "collection": ANAM_COLL}, "ALLOW",
     "semantic_search by collection"),
    ("mcp__anamnesis__semantic_search",
     {"query": "x", "doc_ids": [scoped]}, "ALLOW",
     "semantic_search by prefixed doc_ids[]"),
    ("mcp__anamnesis__forget_document", {"doc_id": foreign}, "DENY",
     "forget_document foreign"),
    ("mcp__anamnesis__forget_document", {"doc_id": scoped}, "ALLOW",
     "forget_document own prefix"),
    ("mcp__anamnesis__forget_collection",
     {"collection": "vekayinuvis:run:ffffffffffff"}, "DENY",
     "forget_collection other-run"),
    ("mcp__anamnesis__forget_collection",
     {"collection": "evidentia:run:ffffffffffff"}, "ALLOW",
     "forget_collection peer pass-through"),
    ("mcp__anamnesis__forget_collection",
     {"collection": ANAM_COLL}, "ALLOW", "forget_collection own"),
    ("mcp__anamnesis__corpus_stats", {}, "ALLOW", "corpus_stats observe-only"),
    ("mcp__anamnesis__list_docs", {"collection": ANAM_COLL}, "ALLOW",
     "list_docs this run"),
    ("mcp__claude_ai_PubMed__search_articles", None, "ALLOW",
     "non-anamnesis unchanged"),
]
for tool, inp, want, label in guard_cases:
    got, j = g(tool, inp)
    check(f"guard {label}", got == want, f"{got} != {want}")
    if want == "DENY" and got == "DENY":
        reason = ((j or {}).get("hookSpecificOutput") or {}).get(
            "permissionDecisionReason", "")
        check(f"guard {label} reason",
              "anamnesis" in reason.lower() or "münhasır" in reason)

off = tempfile.mkdtemp()
os.makedirs(os.path.join(off, ".claude"))
open(os.path.join(off, ".claude", "vekayinuvis-anamnesis.off"), "w").close()
got, _ = g("mcp__anamnesis__hybrid_query", {"query": "x"},
           {**env, "CLAUDE_PROJECT_DIR": off})
check("guard disable-flag bypasses unscoped hybrid", got == "ALLOW")

env2, ledger2, _ = _anam_env()
_, j = run_payload("anamnesis_ledger.py", {
    "tool_name": "mcp__plugin-vekayinuvis-anamnesis__ingest_document",
    "tool_input": {"doc_id": scoped, "collection": ANAM_COLL, "text": "body"},
    "tool_result": json.dumps({"doc_id": scoped, "chunks": 3}),
}, env2)
check("ledger records prefixed ingest",
      scoped in (_read_json(ledger2).get("doc_ids") or []))
check("ledger ingest injects context", decision(j) == "MSG")

_, _ = run_payload("anamnesis_ledger.py", {
    "tool_name": "mcp__anamnesis__ingest_document",
    "tool_input": {"doc_id": foreign, "text": "nsclc"},
    "tool_result": "{}",
}, env2)
check("ledger ignores unprefixed foreign id",
      foreign not in (_read_json(ledger2).get("doc_ids") or []))

_, _ = run_payload("anamnesis_ledger.py", {
    "tool_name": "mcp__anamnesis__forget_document",
    "tool_input": {"doc_id": scoped},
    "tool_result": json.dumps({"existed": True}),
}, env2)
check("ledger forget drops id",
      scoped not in (_read_json(ledger2).get("doc_ids") or []))

env3, ledger3, log3 = _anam_env(docs=[scoped])
_, j = run_payload("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart",
    "source": "startup",
}, env3)
after = _read_json(ledger3)
check("lifecycle startup mints new run_id", after.get("run_id") != ANAM_RUN)
check("lifecycle startup drops previous docs",
      scoped not in (after.get("doc_ids") or []))
logged3 = open(log3, encoding="utf-8").read() if os.path.isfile(log3) else ""
check("lifecycle startup stub-forgets leftover", scoped in logged3)
ctx = ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
check("lifecycle startup context has new prefix",
      str(after.get("prefix") or "") in ctx)

env4, ledger4, log4 = _anam_env(docs=[scoped])
_, _ = run_payload("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart",
    "source": "resume",
}, env4)
check("lifecycle resume keeps run", _read_json(ledger4).get("run_id") == ANAM_RUN)
check("lifecycle resume does not forget",
      not (os.path.isfile(log4) and open(log4, encoding="utf-8").read().strip()))

env5, ledger5, log5 = _anam_env(docs=[scoped])
_, _ = run_payload("anamnesis_lifecycle.py", {
    "hook_event_name": "SessionStart",
    "source": "compact",
}, env5)
led5 = _read_json(ledger5)
check("lifecycle compact keeps working set",
      led5.get("run_id") == ANAM_RUN and scoped in (led5.get("doc_ids") or []))

env6, ledger6, log6 = _anam_env(docs=[scoped])
poisoned = _read_json(ledger6)
poisoned["doc_ids"] = [scoped, foreign]
with open(ledger6, "w", encoding="utf-8") as fh:
    json.dump(poisoned, fh)
_, _ = run_payload("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"}, env6)
logged6 = open(log6, encoding="utf-8").read() if os.path.isfile(log6) else ""
check("lifecycle SessionEnd forgets own id", scoped in logged6)
check("lifecycle SessionEnd skips unprefixed foreign", foreign not in logged6)
check("lifecycle SessionEnd clears doc_ids",
      not _read_json(ledger6).get("doc_ids"))

env7, _, log7 = _anam_env(docs=[])
rc, _ = run_payload("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"}, env7)
check("lifecycle empty SessionEnd exit 0", rc == 0)
check("lifecycle empty SessionEnd writes no stub lines",
      not (os.path.isfile(log7) and open(log7, encoding="utf-8").read().strip()))

env8, ledger8, log8 = _anam_env(docs=[scoped])
_, _ = run_payload("anamnesis_lifecycle.py", {
    "hook_event_name": "UserPromptSubmit",
    "prompt": "/vekayinuvis:kaynak-avi tahaffuzhane",
}, env8)
check("lifecycle subcommand does not remint",
      _read_json(ledger8).get("run_id") == ANAM_RUN)

_, j = run_payload("anamnesis_lifecycle.py", {
    "hook_event_name": "UserPromptSubmit",
    "prompt": "/vekayinuvis tahaffuzhane",
}, env8)
after8 = _read_json(ledger8)
check("lifecycle /vekayinuvis remints", after8.get("run_id") != ANAM_RUN)
check("lifecycle /vekayinuvis forgets previous",
      scoped in open(log8, encoding="utf-8").read())
check("lifecycle /vekayinuvis context has new prefix",
      str(after8.get("prefix") or "") in
      ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext", ""))

env9, _, log9 = _anam_env(docs=[scoped])
_, _ = run_payload("anamnesis_lifecycle.py", {"hook_event_name": "Stop"}, env9)
check("lifecycle Stop does not forget",
      not (os.path.isfile(log9) and open(log9, encoding="utf-8").read().strip()))

with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as fh:
    hooks_json = json.load(fh)
stop_cmds = []
for block in hooks_json.get("hooks", {}).get("Stop", []):
    for h in block.get("hooks", []):
        stop_cmds.append(h.get("command") or "")
check("Stop hooks.json has no anamnesis forget",
      not any("anamnesis" in c for c in stop_cmds))

for s in ("anamnesis_guard.py", "anamnesis_ledger.py", "anamnesis_lifecycle.py"):
    p = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, s)],
        input="}{bozuk", capture_output=True, text=True, timeout=30,
    )
    check(f"{s} malformed fail-open", p.returncode == 0)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
