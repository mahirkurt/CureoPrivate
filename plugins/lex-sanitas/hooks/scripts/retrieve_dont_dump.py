#!/usr/bin/env python3
"""lex-sanitas PostToolUse advisory — retrieve-don't-dump + evidence_index (hukuk metni).

Bir hukuk MCP aracı büyük bir gövde (tam kanun metni, madde ağacı, RG OCR, yabancı statute, tam
gerekçe) döndürdüğünde bu hook, modele ham dökümü ana bağlamda AKIL YÜRÜTMEMESİNİ hatırlatır —
ham döküm bağlam-penceresini taşırır ve eksik/tutarsız değerlendirmeye yol açar (bağlam-ekonomisi
Tier 0 ihlali). İki katmanlı yönlendirme (shared/context-economy-contract.md):
  * ÇOK küçük-eşik üstü (>threshold): ağır çok-server getirim → `legal-distiller` /
    `comparative-law-researcher` alt-ajanına delege (Tier 1); ana pencereye kompakt zarf döner.
  * BÜYÜK-eşik üstü (>big_threshold): tek belge çok büyük → `anamnesis.ingest_document(doc_id=<kanonik>)`
    ile Tier 2 RAG substratına indeksle → hybrid_query(queries[]) ile bounded, provenance-damgalı
    dilim çek (evidence_index). Aynı doc_id iki kez ingest edilmez (kanonik cache).
Advisory only — asla bloklamaz. Fail-open. Eşikler LEX_DUMP_THRESHOLD / LEX_BIG_THRESHOLD (karakter).
"""
import json
import os
import sys

# Çıktısı tam-metin / büyük gövde olan hukuk araçları (basename eşleşmesi).
BIG_OUTPUT_TOOLS = {
    # TR mevzuat
    "get_mevzuat_content", "get_mevzuat_text", "get_mevzuat_madde_tree",
    "download_mevzuat_document", "get_anayasa", "get_mevzuat_gerekce",
    "get_mevzuat_content_markdown",
    # Resmî Gazete
    "rg_get_item", "rg_get_pdf", "rg_ocr_result",
    # Yargı içtihat (companion)
    "get_bedesten_document_markdown", "get_emsal_document_markdown",
    "get_anayasa_document_unified", "get_danistay_document_markdown",
    # Yabancı / karşılaştırmalı
    "ecfr_get", "australia_legislation_fetch", "canada_justicelaws_fetch",
    "japan_elaws_fetch", "spain_boe_fetch", "ireland_eisb_fetch",
    "get_provision", "get_law_text", "get_article", "fetch_eurlex",
    "fetch_judgment", "ich_get_guideline",
    # Doktrin / tez
    "get_yok_tez_document_markdown",
}

DEFAULT_THRESHOLD = 6000     # karakter — Tier 1 distiller yönlendirmesi
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
    if base not in BIG_OUTPUT_TOOLS:
        sys.exit(0)

    try:
        threshold = int(os.environ.get("LEX_DUMP_THRESHOLD", DEFAULT_THRESHOLD))
    except Exception:
        threshold = DEFAULT_THRESHOLD
    try:
        big = int(os.environ.get("LEX_BIG_THRESHOLD", DEFAULT_BIG_THRESHOLD))
    except Exception:
        big = DEFAULT_BIG_THRESHOLD

    n = result_len(data)
    if n <= threshold:
        sys.exit(0)

    if n > big:
        # Tier 2 — tek belge çok büyük → anamnesis evidence_index.
        msg = (
            "[lex-sanitas] büyük-veri: '{base}' ~{kb} KB tek büyük belge döndürdü (Tier 0 sınırı aşıldı). "
            "Bunu HAM işleme. Tier 2 RAG substratına indeksle: "
            "anamnesis.ingest_document(doc_id=<kanonik: mevzuat_no+tur / celex / ecli>, text=<gövde>) → "
            "anamnesis.hybrid_query(doc_scope=<doc_id>, queries=[<hedef maddeler/hükümler>]) ile bounded, "
            "provenance-damgalı dilim çek (evidence_index). Aynı doc_id iki kez ingest edilmez (kanonik cache; "
            "shared/context-economy-contract.md §3). anamnesis anahtarı yoksa → bounded-chunk fallback: "
            "get_mevzuat_madde_tree ile hedefi lokalize et, sonra yalnız o maddeyi/sayfayı çek (references/16 §C). "
            "İçtihat = reform-GEREKÇE sinyali, dava dilekçesi değil."
        ).format(base=base, kb=round(n / 1024, 1))
    else:
        # Tier 1 — distiller alt-ajanına delege.
        msg = (
            "[lex-sanitas] retrieve-don't-dump: '{base}' ~{kb} KB büyük hukuk-metni döndürdü. "
            "Bunu HAM olarak akıl yürütme (bağlam-penceresi taşması → eksik/tutarsız değerlendirme, "
            "kaçırılmış madde). Ağır çok-kaynak getirimi `legal-distiller` (veya çok-yargı ise "
            "`comparative-law-researcher`) alt-ajanına tek görevde delege et → ana pencereye yalnız "
            "kompakt retrieval_distillate + coverage bloğu gelsin (tam-filo G0 + Tier 1 + temiz-kopya). "
            "İçtihat kaynakları reform-GEREKÇE sinyalidir; dava dilekçesi için değil."
        ).format(base=base, kb=round(n / 1024, 1))

    # PostToolUse'da modeli yönlendiren kanal `hookSpecificOutput.additionalContext`'tır;
    # `systemMessage` yalnız kullanıcıya görünür. Devre-kesici modeli yönlendirmeli →
    # additionalContext birincil; systemMessage kullanıcı-görünür ayna olarak korunur.
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg},
        "systemMessage": msg,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
