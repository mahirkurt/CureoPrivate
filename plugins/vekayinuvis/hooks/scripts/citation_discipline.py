#!/usr/bin/env python3
"""vekayinuvis Stop hook — arşiv atıf-disiplini + no-fabrication bütünlük kapısı.

Bir çıktı arşiv belgesine atıfta bulunuyorsa (BOA/BCA/fon kodu/gömlek/devarsiv/katalog),
SKILL §6 gereği (a) fon/kutu/gömlek kayıt yapısı ve (b) orijinal takvim + Miladî **çift-tarih**
taşımalıdır; devlet-arsivleri-doğrulanmış kayıtlarda katalog URL'i dipnota eklenmelidir. Bu hook
son asistan mesajını inceler: arşiv-atıf imzası varsa AMA çift-tarih disiplini görünmüyorsa, turu
bloklamadan devam ettirir ve disiplini tamamlatır + no-fabrication (kısıtlı belge görüntüsü/
tam-metni uydurulmadı mı) hatırlatır. Arşiv-atıfı olmayan turlarda SESSİZ. Fail-open;
stop_hook_active döngüyü kırar.

Stop sözleşmesi: {"decision":"block","reason":...} turu reddetmez — verilen gerekçeyle devam ettirir.
"""
import json
import os
import re
import sys

# Arşiv-belge atıf imzası (en az bir güçlü sinyal → arşiv-atıf bağlamı say).
ARCHIVE_SIGNALS = [
    re.compile(r"\b(BOA|BCA)\b"),
    re.compile(r"\bgömlek\b", re.IGNORECASE),
    re.compile(r"devarsiv|katalog\.devletarsivleri|BelgeGoster", re.IGNORECASE),
    re.compile(r"\b(HAT|BEO|MV|ŞD|DH\.[A-ZÇĞİÖŞÜ]{1,4}|A\.MKT|İ\.[A-ZÇĞİÖŞÜ]{2,4}|Y\.[A-ZÇĞİÖŞÜ]{1,4})\b"),
    re.compile(r"\b030\.\d{2}\b"),  # BCA fon (ör. 030.10)
    re.compile(r"Sicill-i\s+Ahval|DH\.SAİD", re.IGNORECASE),
]
# Çift-tarih disiplini (orijinal takvim + Miladî). Parantez içi 4-haneli yıl / "Miladî" / "M. YYYY".
HAS_DOUBLE_DATE = re.compile(r"\(\s*(M\.\s*)?\d{3,4}\s*\)|\bMil[aâ]dî?\b|\bM\.\s*\d{3,4}\b", re.IGNORECASE)
# devlet-arsivleri kaydı imzası → katalog URL'i beklenir.
HAS_DEVARSIV = re.compile(r"devarsiv|katalog\.devletarsivleri|BelgeGoster", re.IGNORECASE)
HAS_CATALOG_URL = re.compile(r"katalog\.devletarsivleri\.gov\.tr|BelgeGoster\.aspx", re.IGNORECASE)


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

    # Arşiv-atıf bağlamı yoksa sessiz.
    if not any(sig.search(text) for sig in ARCHIVE_SIGNALS):
        sys.exit(0)

    issues = []
    if not HAS_DOUBLE_DATE.search(text):
        issues.append(
            "orijinal takvim + Miladî **çift-tarih** (SKILL §6.1; ör. 'H-27-12-1337 (M. 1919)') — "
            "her arşiv-belge atıfında zorunlu"
        )
    if HAS_DEVARSIV.search(text) and not HAS_CATALOG_URL.search(text):
        issues.append(
            "devlet-arsivleri-doğrulanmış kayıt için **katalog URL'i** (belge_url / BelgeGoster.aspx) "
            "dipnota eklenmeli (citation §6.3)"
        )

    if not issues:
        sys.exit(0)  # disiplin tam → sessiz

    reason = (
        "[vekayinuvis atıf-disiplini] Bu çıktı arşiv belgesine atıfta bulunuyor ama şu disiplin "
        "eksik: " + "; ".join(issues) + ". Tamamla. Ayrıca NO-FABRICATION teyidi: kısıtlı kaynağın "
        "(BOA/BCA/TKGM/ATASE/İSAM…) belge GÖRÜNTÜSÜ/tam-metni ÜRETİLMEDİĞİNDEN emin ol — yalnız "
        "katalog kaydı (fon/kutu/gömlek), künye ve erişim durumu aktarılır; belge metni ancak "
        "transkripsiyon tezinden (yoktez) veya kullanıcının kendi çalışmasından doğrulanır. "
        "Referans: references/citation-and-transliteration.md §6, references/devlet-arsivleri-katalog.md §5."
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
