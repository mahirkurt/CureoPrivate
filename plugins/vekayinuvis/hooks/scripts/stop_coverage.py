#!/usr/bin/env python3
"""vekayinuvis Stop hook — tam-filo G0 kapsam manifestosu bütünlük kapısı.

Bir substantif vekayinüvis araştırma-modu çıktısı (SOURCE_HUNT/ARCHIVE_DEEP_DIVE/PROSOPOGRAPHY/
EVENT_RECONSTRUCTION/HISTORIOGRAPHY/ACADEMIC_REPORT/KANUN_GEREKÇESİ) ZORUNLU olarak bir **kapsam
manifestosu** taşımalıdır (shared/coverage-manifest.md): bağlama uygun tüm server'ların çalıştığının
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

# Substantif araştırma-modu çıktısının imzası (en az bir güçlü sinyal).
MODE_SIGNALS = [
    re.compile(r"\b(SOURCE_HUNT|ARCHIVE_DEEP_DIVE|PROSOPOGRAPHY|EVENT_RECONSTRUCTION|"
               r"HISTORIOGRAPHY|ACADEMIC_REPORT|KANUN_GEREKÇES[İI])\b"),
    re.compile(r"kaynak matris", re.IGNORECASE),
    re.compile(r"\bfon[/\s]|gömlek|BOA\b|BCA\b|devarsiv", re.IGNORECASE),
]
# Birden fazla connector adının geçmesi de substantif-çıktı sinyalidir (tekil connector sohbeti değil).
CONNECTOR_MENTIONS = re.compile(
    r"ottoman[-_]archives|ottoman_|devlet[-_]arsivleri|devarsiv|yoktez|yok_tez|literatur|dergipark|anamnesis",
    re.IGNORECASE,
)
# Manifesto imzası.
HAS_MANIFEST = re.compile(r"(kapsam manifesto|coverage manifest|\bG0\b)", re.IGNORECASE)
# Manifesto içinde durum satırı imzası.
HAS_STATUS_ROWS = re.compile(r"→\s*(hit|empty|degraded|skipped)", re.IGNORECASE)
# Manifestoda görünmesi ZORUNLU çekirdek + substrat satırları (durum ne olursa olsun).
MANDATORY_ROWS = {
    "ottoman-archives": re.compile(r"ottoman[-_]archives", re.IGNORECASE),
    "devlet-arsivleri": re.compile(r"devlet[-_]arsivleri|devarsiv", re.IGNORECASE),
    "yoktez": re.compile(r"\byoktez\b", re.IGNORECASE),
    "anamnesis": re.compile(r"\banamnesis\b", re.IGNORECASE),
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

    # Substantif araştırma-çıktısı mı? (mod sinyali VEYA ≥2 farklı connector anması)
    mode_hit = any(sig.search(text) for sig in MODE_SIGNALS)
    connector_hits = len(set(m.lower() for m in CONNECTOR_MENTIONS.findall(text)))
    if not (mode_hit or connector_hits >= 2):
        sys.exit(0)  # hafif/sohbet turu → sessiz

    missing = []
    if not (HAS_MANIFEST.search(text) and HAS_STATUS_ROWS.search(text)):
        missing.append(
            "G0 KAPSAM MANİFESTOSU (shared/coverage-manifest.md biçimi: her server için "
            "hit/empty/degraded/skipped-with-reason) — tam-filo iddiası manifesto olmadan doğrulanamaz"
        )
    else:
        absent = [name for name, pat in MANDATORY_ROWS.items() if not pat.search(text)]
        if absent:
            missing.append(
                "manifestoda zorunlu satır(lar): " + ", ".join(absent)
                + " (her biri hit/empty/degraded/skipped-with-reason olarak yazılmalı; "
                "devlet-arsivleri oturumu düşükse 'degraded: session_required')"
            )

    if not missing:
        sys.exit(0)  # tam → sessiz

    reason = (
        "[vekayinuvis G0/tam-filo] Bu substantif araştırma çıktısı şu ZORUNLU bileşen(ler)i "
        "taşımıyor: " + "; ".join(missing) + ". Ekleyerek tamamla. Bağlama uygun TÜM server'lar "
        "(ottoman-archives · devlet-arsivleri · yoktez · literatur · consensus · scholar-gateway · "
        "exa · tavily · paper-search · yok-akademik · anamnesis) çalıştırılmalı ve durumu manifestoya "
        "yazılmalı — sessiz atlama G0 FAIL. Herhangi biri atlandıysa gerekçesi ('anahtar yok' / "
        "'mod için N/A' / 'session_required') yazılmalı. Biçim: shared/coverage-manifest.md."
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
