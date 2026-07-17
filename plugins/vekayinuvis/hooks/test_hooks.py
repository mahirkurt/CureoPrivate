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

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
PASS, FAIL = 0, 0


def run(script, text, extra=None):
    payload = {"last_assistant_message": text}
    if extra:
        payload.update(extra)
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
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

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
