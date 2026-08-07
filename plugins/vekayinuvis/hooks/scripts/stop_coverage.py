#!/usr/bin/env python3
"""vekayinuvis Stop hook — tam-filo G0 kapsam manifestosu bütünlük kapısı.

Bir substantif vekayinüvis araştırma-modu çıktısı (SOURCE_HUNT/ARCHIVE_DEEP_DIVE/PROSOPOGRAPHY/
EVENT_RECONSTRUCTION/HISTORIOGRAPHY/ACADEMIC_REPORT/KANUN_GEREKÇESİ) ZORUNLU olarak bir **kapsam
manifestosu** taşımalıdır (${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md): bağlama uygun tüm server'ların çalıştığının
(hit/empty/degraded/skipped-with-reason) kanıtı; sessiz atlama yasak. Bu hook son asistan mesajını
inceler: substantif çıktı imzası varsa AMA manifesto yoksa ya da çekirdek server satırları eksikse,
turu bloklamadan devam ettirir ve manifestoyu tamamlatır. Hafif/sohbet turlarında SESSİZ. Fail-open;
stop_hook_active döngüyü kırar.

Stop sözleşmesi: {"decision":"block","reason":...} turu reddetmez — verilen gerekçeyle devam ettirir.
"""
import json
import os
import re
import sys

from _signals import has_record_locator
from _turn_tools import fleet_data_tool_invoked, transcript_available

# Substantif araştırma-modu çıktısının imzası (en az bir güçlü sinyal).
# NOT: eskiden burada üçüncü bir "zayıf" sinyal vardı (`\bfon[/\s]|gömlek|BOA\b|BCA\b|devarsiv`)
# ve çıplak isim geçişine ateşliyordu — devlet-arsivleri MCP'sinin KENDİ KODU üzerinde çalışmak
# (araç adları, env değişkenleri, fixture'lar) her turda "manifesto eksik" hatası veriyordu.
# Kaldırıldı; yerine aşağıdaki fallback gerçek bir KAYIT YERİ arar (bkz. _signals.py).
MODE_SIGNALS = [
    re.compile(r"\b(SOURCE_HUNT|ARCHIVE_DEEP_DIVE|PROSOPOGRAPHY|EVENT_RECONSTRUCTION|"
               r"HISTORIOGRAPHY|ACADEMIC_REPORT|KANUN_GEREKÇES[İI])\b"),
    re.compile(r"kaynak matris", re.IGNORECASE),
]
# Birden fazla connector adının geçmesi de substantif-çıktı sinyalidir (tekil connector sohbeti değil).
CONNECTOR_MENTIONS = re.compile(
    r"ottoman[-_]archives|ottoman_|devlet[-_]arsivleri|devarsiv|yoktez|yok_tez|literatur|dergipark|anamnesis|"
    r"resmigazete|rg_get_item|\bmevzuat\b|mulga_mevzuat|\btbmm\b|\bdetsis\b",
    re.IGNORECASE,
)
# F9 (metin-yedeği META-TUR baskılayıcı) — kullanıcı 2026-07-19.
# Transkript-YOK yolunda mode_hit, filo/mod adlarını ANAN ama araç ÇAĞIRMAYAN turlarda
# (mimari inceleme, dokümantasyon, bu hook'un kendi kodu) yanlış-pozitif üretiyordu.
# Gerçek çıktı TEK mod bildirir + genelde arşiv künyesi taşır; meta-tur BİRÇOK modu anar
# ve/veya plugin-iç dosya/hook adları taşır ve künyesizdir. Yalnız transkript-YOK yolunu
# etkiler (transkript varken fleet_data_tool_invoked zaten kesin — orada bu baskılayıcı yok).
MODE_NAME = re.compile(
    r"\b(SOURCE_HUNT|ARCHIVE_DEEP_DIVE|MANUSCRIPT_TRANSCRIBE|PROSOPOGRAPHY|EVENT_RECONSTRUCTION|"
    r"HISTORIOGRAPHY|CHRONOLOGY_CONVERSION|ACADEMIC_REPORT|KANUN_GEREKÇES[İI])\b"
)
# Plugin-iç öz-referans imzaları (araştırma çıktısında görünmez; inceleme/mühendislik turunda görünür).
META_MARKERS = re.compile(
    r"plugins/vekayinuvis|hooks/scripts|_turn_tools|stop_coverage|citation_discipline|_signals|"
    r"SKILL\.md|coverage-manifest\.md|context-economy-contract|\.mcp\.json|plugin\.json|frontmatter",
    re.IGNORECASE,
)


def is_meta_turn(text):
    """Filo/mod ADINI anan ama üretmeyen tur mu? (inceleme/dokümantasyon/mühendislik)

    (a) plugin-iç öz-referans (dosya/hook adı) → kesin meta; VEYA
    (b) ≥3 farklı mod adı VE hiç arşiv KAYIT YERİ yok → mod-kataloğunu tartışan meta.
    Arşiv künyesi taşıyan çok-fazlı gerçek rapor (b)'den muaftır → susturulmaz."""
    if META_MARKERS.search(text):
        return True
    distinct_modes = len({m.upper() for m in MODE_NAME.findall(text)})
    return distinct_modes >= 3 and not has_record_locator(text)


# Manifesto imzası.
HAS_MANIFEST = re.compile(r"(kapsam manifesto|coverage manifest|\bG0\b)", re.IGNORECASE)
# Manifesto içinde durum satırı imzası.
HAS_STATUS_ROWS = re.compile(r"(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE)
# Manifestoda görünmesi ZORUNLU tam-filo satırları (durum ne olursa olsun).
# Satır yalnız server adını değil, hit/empty/degraded/skipped durumunu da taşımalı.
MANDATORY_ROWS = {
    "ottoman-archives": re.compile(r"ottoman[-_]archives\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "devlet-arsivleri": re.compile(r"(devlet[-_]arsivleri|devarsiv)\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "yoktez": re.compile(r"\byoktez\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "literatur": re.compile(r"\bliteratur\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "consensus": re.compile(r"\bconsensus\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "scholar-gateway": re.compile(r"scholar[-_]gateway\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "exa": re.compile(r"\bexa\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "tavily": re.compile(r"\btavily\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "paper-search": re.compile(r"paper[-_]search\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "openathens": re.compile(r"\bopenathens\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "annas-reader": re.compile(r"annas[-_]reader\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "yok-akademik": re.compile(r"yok[-_]akademik\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "anamnesis": re.compile(r"\banamnesis\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "resmigazete": re.compile(r"\bresmigazete\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "mevzuat": re.compile(r"\bmevzuat\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "tbmm": re.compile(r"\btbmm\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
    "detsis": re.compile(r"\bdetsis\b\s*(?:→|->)\s*(hit|empty|degraded|skipped)", re.IGNORECASE),
}


def last_assistant_message(event):
    msg = event.get("last_assistant_message")
    if isinstance(msg, str) and msg.strip():
        return msg
    path = event.get("transcript_path") or ""
    if not path or not os.path.exists(path):
        return ""
    try:
        last = ""
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") == "assistant" or rec.get("role") == "assistant":
                    content = rec.get("message", {}).get("content", rec.get("content", ""))
                    if isinstance(content, list):
                        content = " ".join(
                            b.get("text", "") for b in content if isinstance(b, dict)
                        )
                    if isinstance(content, str) and content.strip():
                        last = content
        return last
    except Exception:
        return ""


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("stop_hook_active"):
        sys.exit(0)  # döngü koruması

    text = last_assistant_message(event)
    if not text:
        sys.exit(0)

    # Substantif araştırma-çıktısı mı?
    #   (a) açık mod bildirimi / kaynak matrisi → kesin sinyal (bulgusuz taramayı da yakalar), VEYA
    #   (b) ≥2 farklı connector anması VE somut bir arşiv KAYIT YERİ → bulgu sunan tarama.
    # (b)'deki kayıt-yeri şartı olmadan iki connector ADININ yan yana geçmesi yetiyordu; bu,
    # filo hakkında KOD/PLAN konuşmasını (mevzuat+tbmm+devarsiv anmak) araştırma sanıyordu.
    # Bilinçli takas: mod bildirmeyen VE hiç künye içermeyen bir tarama artık kaçar. Bu dar
    # boşluk kabul edilebilir — SKILL zaten mod bildirimini zorunlu kılıyor, ve her turda
    # ateşleyen bir kapı yok sayılmayı öğretir ki bu invaryantın TAMAMEN kaybıdır.
    # DAVRANIŞ KAPISI (birincil, transkript varsa) — kullanıcı sertleştirmesi 2026-07-17.
    # Yer gerçeği: bu turda gerçek bir tam-filo veri-aracı ÇAĞRILDI mı? Filo hakkında KOD/PLAN
    # konuşması (mevzuat+tbmm+devarsiv adlarını port tablosu/.mcp.json'da anmak) araç çağırmaz
    # → kapı kapalı → sessiz (kör yanlış-pozitif ölür). Filo aracı çağrıldıysa manifesto beklenir
    # ve metin-sezgisi (mode/connector) ATLANIR — böylece "mod bildirmeyen VE künyesiz tarama"
    # açığı kapanır (araç çağrısı = substantif araştırma yer gerçeği).
    # Transkript YOKSA davranış kapısına güvenmeyiz → eski metin-sezgisi yedeğine düşeriz
    # (invaryant sessizce kaybolmasın): (a) mod bildirimi VEYA (b) ≥2 connector VE somut kayıt yeri.
    if transcript_available(event):
        if not fleet_data_tool_invoked(event):
            sys.exit(0)
    else:
        if is_meta_turn(text):
            sys.exit(0)  # F9: filo/mod adını anan ama üretmeyen inceleme/dokümantasyon turu → sessiz
        mode_hit = any(sig.search(text) for sig in MODE_SIGNALS)
        connector_hits = len(set(m.lower() for m in CONNECTOR_MENTIONS.findall(text)))
        if not (mode_hit or (connector_hits >= 2 and has_record_locator(text))):
            sys.exit(0)  # transkript yok + hafif/sohbet/mühendislik turu → sessiz

    missing = []
    if not (HAS_MANIFEST.search(text) and HAS_STATUS_ROWS.search(text)):
        missing.append(
            "G0 KAPSAM MANİFESTOSU (${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md biçimi: her server için "
            "hit/empty/degraded/skipped-with-reason) — tam-filo iddiası manifesto olmadan doğrulanamaz"
        )
    else:
        absent = [name for name, pat in MANDATORY_ROWS.items() if not pat.search(text)]
        if absent:
            missing.append(
                "manifestoda zorunlu tam-filo satır(lar): " + ", ".join(absent)
                + " (17 server'ın her biri 'server → hit/empty/degraded/skipped: gerekçe' "
                "biçiminde yazılmalı; devlet-arsivleri oturumu düşükse "
                "'degraded: session_required')"
            )

    if not missing:
        sys.exit(0)  # tam → sessiz

    reason = (
        "[vekayinuvis G0/tam-filo] Bu substantif araştırma çıktısı şu ZORUNLU bileşen(ler)i "
        "taşımıyor: " + "; ".join(missing) + ". Ekleyerek tamamla. Bağlama uygun TÜM server'lar "
        "(ottoman-archives · devlet-arsivleri · yoktez · literatur · consensus · scholar-gateway · "
        "exa · tavily · paper-search · openathens · annas-reader · resmigazete · mevzuat · tbmm · "
        "yok-akademik · detsis · anamnesis) "
        "çalıştırılmalı ve durumu manifestoya "
        "yazılmalı — sessiz atlama G0 FAIL. Herhangi biri atlandıysa gerekçesi ('anahtar yok' / "
        "'mod için N/A' / 'session_required') yazılmalı. Biçim: ${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md."
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
