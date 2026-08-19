#!/usr/bin/env python3
"""PostToolUse — büyük getirimi Tier-1/Tier-2'ye yönlendirir. Advisory, bloklamaz."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_payload  # noqa: E402

TIER1 = 6_000
TIER2 = 30_000

# Ölçülmüş tuzak taşıyan araçlar → sonuç geldiğinde uyarı eklenir
TRAPS = {
    "find_equivalent": (
        "`find_equivalent` match_score TERS çalışır (doğru ICD-11 isabetleri 0, yanlış sözlüksel "
        "isabetler 0.833; consumption→tüberküloz hiç dönmez). Skoru sıralamada KULLANMA; sonucu "
        "yalnız DOĞRULAMA olarak ele al ve historical-nosology.md küratörlü sözlüğüne başvur."
    ),
    "ottoman_search_iiif": (
        "`ottoman_search_iiif` sıralaması Osmanlı-öncelikli — küresel sorguda üst sonuçlar "
        "alakasız olabilir (ölçülen örnek: 'plague treatise' → üstte bir 1832 romanı). "
        "Sonuçları başlık + tarih + kurum ile ELE; üst sonucu körlemesine alma."
    ),
}


def size_of(payload):
    resp = payload.get("tool_response")
    if resp is None:
        return 0
    try:
        return len(resp if isinstance(resp, str) else json.dumps(resp, ensure_ascii=False))
    except Exception:
        return 0


def main():
    payload = read_payload()
    tool = str(payload.get("tool_name", ""))
    size = size_of(payload)

    notes = []
    for key, msg in TRAPS.items():
        if key in tool:
            notes.append(f"⚠️ ÖLÇÜLMÜŞ TUZAK — {msg}")

    if size >= TIER2:
        notes.append(
            f"Bu getirim ~{size // 1024} KB. TIER-2: ana bağlamda akıl yürütme; "
            "`anamnesis.ingest_document(collection=histmed:run:<12hex>, "
            "doc_id=hmrun:<12hex>:<kanonik>)` ile indeksle "
            "(ön-ek ZORUNLU: `histmed:run:` / `hmrun:`) → "
            "`hybrid_query(collection=histmed:run:<12hex>)` ile sınırlı dilim çek. "
            "Cevap yalnız bu chunk'lardan; atıf `doc_id::idx`. Ham gövde ne bağlama "
            "ne çıktıya kopyalanır."
        )
    elif size >= TIER1:
        notes.append(
            f"Bu getirim ~{size // 1024} KB. TIER-1: çok-server tarama sürüyorsa "
            "`tarih-tarama-distilleri` alt-ajanına devret — ham gövde yerine "
            "`tarih_distillate` zarfı döner."
        )

    if notes:
        print("\n".join(notes))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
