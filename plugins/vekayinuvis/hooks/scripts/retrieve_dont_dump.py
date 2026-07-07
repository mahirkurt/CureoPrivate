#!/usr/bin/env python3
"""vekayinuvis PostToolUse advisory — retrieve-don't-dump + anamnesis evidence_index (arşiv metni).

Bir arşiv/tez/literatür MCP aracı büyük bir gövde (belge transkripsiyonu, tez tam-metni, DergiPark
PDF→HTML tam-metin, İА maddesi, IIIF within-manifest bloğu, geniş katalog sonuç seti) döndürdüğünde
bu hook, modele ham dökümü ana bağlamda AKIL YÜRÜTMEMESİNİ hatırlatır — ham döküm bağlam-penceresini
taşırır ve detay atlar (bağlam-ekonomisi Tier 0 ihlali). İki katmanlı yönlendirme
(shared/context-economy-contract.md):
  * küçük-eşik üstü (>threshold): ağır çok-connector getirim → `arsiv-tarama-distilleri` alt-ajanına
    delege (Tier 1); ana pencereye kompakt `arsiv_distillate` + coverage döner.
  * BÜYÜK-eşik üstü (>big_threshold): tek belge çok büyük → `anamnesis.ingest_document(doc_id=<kanonik>)`
    ile Tier 2 RAG substratına indeksle → hybrid_query(queries[]) ile bounded, provenance-damgalı
    dilim çek. Aynı doc_id iki kez ingest edilmez (kanonik cache).
Advisory only — asla bloklamaz. Fail-open. Eşikler VEKAYI_DUMP_THRESHOLD / VEKAYI_BIG_THRESHOLD (karakter).
"""
import json
import os
import re
import sys

# Çıktısı tam-metin / büyük gövde olan arşiv/tez/literatür araçları (basename eşleşmesi).
BIG_OUTPUT_TOOLS = {
    # YÖK Tez tam-metin
    "get_yok_tez_document_markdown", "get_yok_tez_thesis_details",
    # Ottoman Archives büyük gövde
    "ottoman_get_dspace_item", "ottoman_get_islam_ansiklopedisi",
    "ottoman_search_within_manifest", "ottoman_fetch_iiif_manifest",
    "ottoman_browse_iiif_collection", "ottoman_export_html",
    "ottoman_escriptorium_get_transcription",
    # Devlet Arşivleri katalog
    "devarsiv_search", "devarsiv_get_belge",
    # Tam-metin (kitap+makale)
    "oa_fetch_fulltext", "oa_batch_result",
    "read_document", "read_article", "get_document_info", "search_in_document",
}
# Literatür (DergiPark) ve diğer tam-metin araçları için isim-desen sezgiseli (kesin ad bilinmiyorsa).
FULLTEXT_NAME = re.compile(
    r"(fulltext|full_text|pdf|read_|_content|document|references|makale|article|get_belge)",
    re.IGNORECASE,
)

DEFAULT_THRESHOLD = 6000      # karakter — Tier 1 distiller yönlendirmesi
DEFAULT_BIG_THRESHOLD = 30000  # karakter — Tier 2 anamnesis ingest yönlendirmesi


def result_len(data):
    r = data.get("tool_result", data.get("tool_response", ""))
    try:
        return len(r) if isinstance(r, str) else len(json.dumps(r, ensure_ascii=False))
    except Exception:
        return 0


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = str(data.get("tool_name", ""))
    if not tool.startswith("mcp__"):
        sys.exit(0)
    base = tool.split("__")[-1]
    is_literatur = "literatur" in tool.lower()
    if base not in BIG_OUTPUT_TOOLS and not (is_literatur and FULLTEXT_NAME.search(base)):
        sys.exit(0)

    try:
        threshold = int(os.environ.get("VEKAYI_DUMP_THRESHOLD", DEFAULT_THRESHOLD))
    except Exception:
        threshold = DEFAULT_THRESHOLD
    try:
        big = int(os.environ.get("VEKAYI_BIG_THRESHOLD", DEFAULT_BIG_THRESHOLD))
    except Exception:
        big = DEFAULT_BIG_THRESHOLD

    n = result_len(data)
    if n <= threshold:
        sys.exit(0)

    if n > big:
        msg = (
            "[vekayinuvis] büyük-veri: '{base}' ~{kb} KB tek büyük gövde döndürdü (Tier 0 sınırı aşıldı). "
            "Bunu HAM işleme. Tier 2 RAG substratına indeksle: "
            "anamnesis.ingest_document(doc_id=<kanonik: devarsiv:arsiv/fon/kutu-gömlek / yoktez:tez-no / "
            "doi:… / iiif:manifest-url>, text=<gövde>) → anamnesis.hybrid_query(doc_scope=<doc_id>, "
            "queries=[<hedef kişi/olay/tarih/kavram>]) ile bounded, provenance-damgalı dilim çek. Aynı "
            "doc_id iki kez ingest edilmez (kanonik cache; shared/context-economy-contract.md §3). anamnesis "
            "anahtarı yoksa → bounded-chunk fallback: ottoman_search_within_manifest / get_yok_tez_document_"
            "markdown(page) ile hedefi lokalize et, yalnız o parçayı çek. Detay ATLAMA: grafiğe upsert_triples "
            "ile kişi↔görev↔belge / olay↔tarih↔kaynak ilişkilerini de yaz."
        ).format(base=base, kb=round(n / 1024, 1))
    else:
        msg = (
            "[vekayinuvis] retrieve-don't-dump: '{base}' ~{kb} KB büyük arşiv/tez/literatür gövdesi döndürdü. "
            "Bunu HAM olarak akıl yürütme (bağlam taşması → atlanmış belge/detay). Ağır çok-connector getirimi "
            "`arsiv-tarama-distilleri` alt-ajanına tek görevde delege et → ana pencereye yalnız kompakt "
            "`arsiv_distillate` + coverage bloğu gelsin (tam-filo G0 + Tier 1 + temiz-kopya). Belge görüntüsü/"
            "tam-metni kısıtlı kaynak ise uydurma — yalnız katalog kaydı + erişim durumu."
        ).format(base=base, kb=round(n / 1024, 1))

    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg},
        "systemMessage": msg,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
