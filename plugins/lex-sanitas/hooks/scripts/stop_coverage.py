#!/usr/bin/env python3
"""lex-sanitas Stop hook — G0 kapsam manifestosu + confidence_label bütünlük kapısı.

Bir lex-sanitas reform modu (DRAFT/AMEND/ANALYZE/COMPLY/OPINE/RIA/COMPARATIVE/TBMM/EX_POST)
koştuğunda çıktı ZORUNLU olarak (a) tam-filo kanıtı olan **kapsam manifestosu (G0)** ve
(b) **confidence_label**'ı taşımalıdır (SKILL §7). Bu hook, son asistan mesajını inceler:
lex-sanitas mod-çıktısı imzası varsa AMA manifesto/label eksikse, turu bloklamadan devam
ettirir ve eksiği tamamlatır. lex-sanitas ile ilgisiz turlarda SESSİZ. Fail-open; stop_hook_active
döngüyü kırar.

Stop sözleşmesi: {"decision":"block","reason":...} turu reddetmez — verilen gerekçeyle devam ettirir.
"""
import json
import os
import re
import sys

# Bir lex-sanitas reform-modu çıktısının imzası (en az iki farklı sinyal → mod-çıktısı say).
MODE_SIGNALS = [
    re.compile(r"\bMADDE\s+\d+", re.IGNORECASE),
    re.compile(r"gerekçe", re.IGNORECASE),
    re.compile(r"(yönetmelik|tebliğ|kanun teklifi|CBK|genelge)\s+(taslağı|metni|değişik)", re.IGNORECASE),
    re.compile(r"\b(DRAFT|AMEND|ANALYZE|COMPLY|OPINE|RIA|COMPARATIVE_LAW|TBMM_KANUN_TEKLIFI|EX_POST)", re.IGNORECASE),
    re.compile(r"5210", re.IGNORECASE),
    re.compile(r"(karşılaştırma cetveli|DEA|BEF|R6b|belirlilik ilkes)", re.IGNORECASE),
]
# Zorunlu çıktı bileşenleri.
HAS_MANIFEST = re.compile(r"(kapsam manifesto|coverage manifest|\bG0\b|hit \d|skipped:|empty\b)", re.IGNORECASE)
HAS_CONFIDENCE = re.compile(r"(confidence[_ ]?label|combined_confidence|human_review_required|güven etiketi)", re.IGNORECASE)
# Manifesto varsa içinde görünmesi ZORUNLU satırlar: 3 companion + 2 delegasyon plugin'i
# (durum ne olursa olsun — hit/empty/degraded/skipped-with-reason — satır mevcut olmalı).
MANDATORY_ROWS = {
    "Yargı (companion — G5 içtihat)": re.compile(r"\bYarg", re.IGNORECASE),
    "Open Law (companion — G6 CELEX)": re.compile(r"Open[_ ]?Law", re.IGNORECASE),
    "Ansvar (companion — Mod7 58-yargı)": re.compile(r"\bAnsvar", re.IGNORECASE),
    "evidentia (klinik delegasyon)": re.compile(r"\bevidentia", re.IGNORECASE),
    "sci-audit (çıktı-QA delegasyonu)": re.compile(r"\bsci[- ]?audit", re.IGNORECASE),
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

    signals = sum(1 for rx in MODE_SIGNALS if rx.search(text))
    if signals < 2:
        sys.exit(0)  # lex-sanitas mod-çıktısı değil → sessiz

    missing = []
    if not HAS_MANIFEST.search(text):
        missing.append("kapsam manifestosu (G0 — wire'lı tüm MCP'lerin hit/empty/degraded/skipped-with-reason kanıtı)")
    else:
        # Manifesto var → companion + delegasyon satırları da mevcut olmalı (SKILL §7 / coverage-manifest.md).
        absent_rows = [label for label, rx in MANDATORY_ROWS.items() if not rx.search(text)]
        if absent_rows:
            missing.append(
                "manifestoda zorunlu satır(lar): " + ", ".join(absent_rows)
                + " (her biri hit/empty/degraded/skipped-with-reason olarak yazılmalı; "
                "companion skip'i ilgili kapıyı CONDITIONAL yapar)"
            )
    if not HAS_CONFIDENCE.search(text):
        missing.append("confidence_label (mod + combined_confidence + human_review_required:true + scope_disclaimer)")

    if not missing:
        sys.exit(0)  # tam → sessiz

    reason = (
        "[lex-sanitas G0/çıktı-sözleşmesi] Bu reform-modu çıktısı şu ZORUNLU bileşen(ler)i "
        "taşımıyor: " + "; ".join(missing) + ". SKILL §7 gereği bunları ekleyerek tamamla. "
        "Manifesto biçimi: shared/coverage-manifest.md. Tam-filo iddiası (hepsi her sorguda "
        "çalıştı) manifesto olmadan doğrulanamaz. Herhangi bir server atlandıysa gerekçesi "
        "('anahtar yok' / 'mod için N/A') yazılmalı — sessiz atlama yasak."
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
