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
# Manifesto varsa içinde görünmesi ZORUNLU satırlar — companion'lar + delegasyon
# plugin'leri (durum ne olursa olsun: hit/empty/degraded/skipped-with-reason).
# v3.5.0'da liste HARDCODE DEĞİL, fleet.lock.json'dan türetilir: yoktez wire'landığı
# için companion olmaktan çıktı (8 → 7 satır) ve bu değişikliğin burada elle
# yapılması gerekseydi kaçınılmaz olarak unutulurdu. 2026-08-08'de AYNI geçiş
# Türk Patent'te yaşandı (7 → 6 satır): anahtarsız doğrudan ucu (markapatent-mcp)
# bulununca companion olmaktan çıkıp wire'lı `turk-patent` sunucusu oldu.
_TOKEN_RX = {
    "Yargı": r"\bYarg",
    "Open Law": r"Open[_ ]?Law",
    "Ansvar": r"\bAnsvar",
    "Fedlex Swiss": r"Fedlex",
    "evidentia": r"\bevidentia",
    "sci-audit": r"\bsci[- ]?audit",
}

# Lock okunamazsa kullanılacak asgari liste (fail-open) — 4 companion + 2 delegasyon.
_FALLBACK_ROWS = {
    "Yargı (companion — G5 içtihat)": re.compile(_TOKEN_RX["Yargı"], re.IGNORECASE),
    "Open Law (companion — G6 CELEX)": re.compile(_TOKEN_RX["Open Law"], re.IGNORECASE),
    "Ansvar (companion — Mod7 58-yargı)": re.compile(_TOKEN_RX["Ansvar"], re.IGNORECASE),
    "Fedlex Swiss (companion — Mod7 CH birincil metin)":
        re.compile(_TOKEN_RX["Fedlex Swiss"], re.IGNORECASE),
    "evidentia (klinik delegasyon)": re.compile(_TOKEN_RX["evidentia"], re.IGNORECASE),
    "sci-audit (çıktı-QA delegasyonu)": re.compile(_TOKEN_RX["sci-audit"], re.IGNORECASE),
}


def _load_lock():
    """fleet.lock.json'u stdlib json ile okur; okunamazsa None (fail-open)."""
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "fleet.lock.json")
        with open(os.path.normpath(path), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def mandatory_rows(lock=None):
    """Manifestoda BULUNMASI ZORUNLU satırları lock'tan türetir.

    Yalnız companion (wire edilemez dış connector) + delegasyon plugin'leri
    denetlenir. Wire'lı 20 server için satır-satır regex denetimi YAPILMAZ —
    kırılgan olur ve yanlış-pozitif üretir; onların kanıtı G0 manifestosunun
    varlığıdır. Bilinmeyen ad için ada dayalı jenerik desen üretilir.
    """
    if lock is None:
        lock = _load_lock()
    if not lock:
        return dict(_FALLBACK_ROWS)
    rows = {}
    for item in list(lock.get("companions", [])) + list(lock.get("delegations", [])):
        name = item.get("name", "")
        row = item.get("manifest_row") or name
        pattern = _TOKEN_RX.get(name)
        if pattern is None:  # fleet.yaml'e yeni ad eklenirse sessizce düşmesin
            pattern = re.escape(name).replace(r"\ ", r"[_ ]?").replace(r"\-", r"[- ]?")
        rows[row] = re.compile(pattern, re.IGNORECASE)
    return rows or dict(_FALLBACK_ROWS)


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
        absent_rows = [label for label, rx in mandatory_rows().items()
                       if not rx.search(text)]
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
