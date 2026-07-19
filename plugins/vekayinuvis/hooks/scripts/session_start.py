#!/usr/bin/env python3
"""vekayinuvis SessionStart preflight — çekirdek arşiv connector'larının credential
kontrolü + no-fabrication/tek-cihaz-oturum konvansiyon enjeksiyonu.

vekayinuvis'in gated çekirdek/companion connector'ları Bearer anahtarını süreç ortamından
çözer (Doppler-injected: `doppler run -- claude`). Bir anahtar yoksa o connector çağrı
anında 401 döner ve ilgili katman degrade eder — çıktı DURMAZ, asla uydurma yapılmaz.
Bu hook: (a) eksik anahtarları bir kez yüzeye çıkarır, (b) her oturumda vekayinuvis çekirdek
konvansiyonlarını (connector kadrosu · devlet-arsivleri tek-cihaz oturum · no-fabrication ·
restricted-source · retrieve-don't-dump) kısa bir additionalContext olarak enjekte eder.
Fail-open.
"""
import json
import os
import sys

# Gated çekirdek + companion + substrat + yasama/mevzuat connector → env var
# (yoktez/literatur/consensus/scholar-gateway/exa/tavily authless veya OAuth → env-key yok;
#  paper-search Smithery key'i userConfig ile enable-time'da).
GATED = {
    "devlet-arsivleri": "DEVARSIV_MCP_API_KEY",
    "ottoman-archives": "OTTOMAN_ARCHIVES_MCP_API_KEY",
    "yok-akademik": "YOK_AKADEMIK_MCP_API_KEY",
    "openathens": "OPENATHENS_MCP_API_KEY",
    "annas-reader": "ANNAS_MCP_API_KEY",
    "anamnesis": "ANAMNESIS_MCP_API_KEY",
    "resmigazete": "RESMI_GAZETE_MCP_API_KEY",
    "mevzuat": "MEVZUAT_MCP_API_KEY",
    "tbmm": "TBMM_MCP_API_KEY",
    "detsis": "DETSIS_MCP_API_KEY",
}

CONVENTIONS = (
    "[vekayinuvis] Osmanlı/Türk tarih birincil-kaynak araştırma protokolü aktif. "
    "Connector kadrosu — ÇEKİRDEK (bundled): `ottoman-archives` (IIIF keşif + literatür + "
    "takvim/ebced + HTR + TDV İA), `devlet-arsivleri` (**resmî BOA/BCA/Diplomatik/Askeri "
    "katalog araması** — fon/kutu/gömlek + künye), `yoktez` (YÖK Tez transkripsiyon tezleri); "
    "COMPANION: `literatur` (DergiPark tam-metin), `yok-akademik` (destekleyici — akademisyen "
    "profilleri), `detsis` (destekleyici — kurumsal prosopografi, Cumhuriyet-sınırlı), "
    "paper-search/consensus/scholar-gateway/exa/tavily; YASAMA/MEVZUAT (v3.0): `resmigazete` "
    "(erken-Cumhuriyet /eskiler/ + rg-ocr), `mevzuat` (mülga mevzuat + gerekçe), `tbmm` (teklif→kanun "
    "soyağacı + Açık Erişim DSpace) — KANUN_GEREKÇESİ omurgası; TAM-METİN ŞELALESİ (kitap+makale): "
    "`openathens` (Tier 3 lisanslı — Millet Kütüphanesi 309 DB) → `annas-reader` (Tier 4 son çare; yalnız "
    "analiz; `marmara` Tier 3b wire bekliyor — DNS yayınlanmadı). Getirilen tam-metin > eşik → anamnesis'e ingest. "
    "Çekirdek invaryantlar: "
    "(1) DEVLET-ARSIVLERI TEK-CİHAZ OTURUM — resmî katalog oturumu HP'de kalıcı authenticated "
    "tarayıcıda yaşar; arşiv-katalog sorgusundan ÖNCE `devarsiv_session_status` ile canlılığı "
    "doğrula. `session_required` dönerse: kullanıcıya 'resmî katalog oturumu düştü, HP noVNC "
    "re-login gerekiyor' bildir + ottoman-archives/yoktez/literatur ile DEGRADE devam et (asla "
    "uydurma). Geniş sorgu → `refine_required` (daralt); `get_belge` için `hash` DAİMA "
    "`devarsiv_search` sonucundan gelir (uydurulamaz). "
    "(1a) KAPSAMLI SÜPÜRME + STORE-FIRST — konu >1000/tam tarama için birincil yol "
    "`devarsiv_deep_search` (otomatik arşiv×üst-fon×tarih süpürme, arsiv boş→dört arşiv; async) "
    "→ `devarsiv_deep_result(job_id)` ile poll (OCR K4 ile aynı sözleşme; idempotent). Kapsam "
    "manifestosu: `complete=false` iken boş sonuç 'yok' DEĞİLDİR; tamlık yalnız süpürülen "
    "year_bounds/fon_bounds içinde. Store kapalıysa `store_required` → manuel enumerasyona degrade. "
    "BOŞ SONUÇTAN 'arşivde yok' SONUCUNA VARMADAN ÖNCE `devarsiv_coverage` ile hasat defterine bak: "
    "kova defterde yoksa cevap 'bilmiyoruz/henüz hasat edilmedi'dir, 'yok' değil (no-fabrication). "
    "(2) BELGE OKUMA + NO-FABRICATION — katalog kaydı/künye DOĞRUDAN; ayrıca **belge sayfa "
    "taraması `devarsiv_get_belge_image` ile ÇEKİLİR** (önizleme, satın-almadan bağımsız → satın "
    "alınmamış da okunur) ve `devarsiv_ocr_belge` ile metne çevrilir: Latin/Cumhuriyet tam-metin, "
    "Osmanlı basılı damga+arşiv referans kodu (tesseract), **el yazması Arap-harfli gövde → "
    "varsayılan `engine=\"transleyt\"`** (ölçülen en iyi okuyucu, CER 0.130-0.230); en doğru okuma "
    "Transleyt + asistan görüsü (0.154) UZLAŞTIRMASIdır — ikisi DENK ve bağımsızdır, hiçbiri "
    "diğerini otomatik yenmez (ölçüm: uzlaştırma 0.231→0.162). Transkribus Latin çeviriyazı yazar "
    "(transkripsiyon rakibi değil); eScriptorium keşif taraması içindir (0.479). Harici IIIF "
    "görüntüsü → `devarsiv_ocr_image` (AYNI motor beyni). Tarama GERÇEKtir, uydurulmaz; OCR "
    "düşük-güvende dürüstçe raporlanır; el yazması transkripsiyon ölçülü %13-23 CER taşır "
    "(özel ad/tarih/yer/meblağda hata beklenir; bu hata payı çıktıda beyan edilir). "
    "(2a) SEPET state-changing-ama-ödemesiz — `devarsiv_add_to_cart`/`_remove_from_cart` eSatış "
    "sepetini değiştirir ama asla otonom ödeme yapmaz. "
    "(2b) CHECKOUT yalnız-noVNC-URL — `devarsiv_checkout_cart` ödemeyi YAPMAZ, yalnız "
    "`https://devarsiv-vnc.cureonics.com/vnc.html` + sepet döner; kullanıcıyı DAİMA uyar: 'Kendi "
    "cihazınızdan kataloğa GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür.' "
    "(2c) ARŞİV-ÖNCELİKLİ OKUMA — satın alınmış belgede birincil okuma `devarsiv_get_archive_page` "
    "(300 DPI görüntü) + `devarsiv_ocr_archive_pages` (Transleyt) UZLAŞTIRMASI; viewer temsilî-sayfa "
    "OCR/HTR (`devarsiv_ocr_belge_pages`) ikincil kanıttır, TAM yol yerel arşivdir. "
    "(2d) K4 SYNC/ASYNC — ≤5 sayfa → `devarsiv_ocr_archive_pages` (sync); >5 sayfa veya çok-motorlu "
    "(`both`) tam belge → `devarsiv_ocr_submit` → `devarsiv_ocr_result(include_text=false)` ile "
    "poll → `done`'da tek-sefer `include_text=true` → anamnesis ingest; `stale` → aynı "
    "parametrelerle resubmit (maliyet tekrarlanmaz). "
    "(3) ATIF DİSİPLİNİ — her arşiv iddiası fon/kutu/gömlek + orijinal takvim + Miladî çift-tarih; "
    "devlet-arsivleri-doğrulanmış kayıt için katalog URL'i (belge_url) dipnota eklenir. IJMES/TDV İA "
    "çeviriyazı. (bkz. references/citation-and-transliteration.md, references/devlet-arsivleri-katalog.md) "
    "(4) TAM-FİLO + BAĞLAM EKONOMİSİ — `.mcp.json`'da bundled 17 server'ın bağlama uygun olanı "
    "HER substantif sorguda çalışır (sessiz atlama YOK); her çıktı G0 kapsam manifestosu taşır "
    "(shared/coverage-manifest.md: her server için hit/empty/degraded/skipped-with-reason). Ham veri "
    "ana pencerede akıl yürütülmez: ağır çok-connector süpürme → `arsiv-tarama-distilleri` alt-ajanı "
    "(retrieve-don't-dump; ≤4 paralel shard); büyük tam-metin (belge transkripsiyonu/tez PDF/DergiPark "
    "tam-metin/İА maddesi) → `anamnesis` Tier-2 ingest→bounded query (kişi↔görev↔belge / olay↔tarih↔kaynak "
    "grafiği). Büyük belge KÖR getirilmez (yapısal navigasyon → hedef chunk → gerekirse anamnesis). "
    "shared/context-economy-contract.md. Bir katman yoksa alt katmana degrade + manifestoda beyan "
    "(anahtar yok / oturum düşük / companion bağlı değil) — asla ham döküm, asla uydurma. "
    "(5) İNSAN DENETİMİ — birincil-kaynak yorumu her çıktıda araştırmacı doğrulamasına tabidir."
)


def main():
    try:
        sys.stdin.read()  # SessionStart payload (kullanılmıyor)
    except Exception:
        pass

    ctx = CONVENTIONS
    missing = [f"{c} (${v})" for c, v in GATED.items() if not os.environ.get(v)]
    if missing:
        ctx += (
            "\n[preflight] Şu connector anahtar(lar)ı süreç ortamında YOK: "
            + ", ".join(missing)
            + ". Bunlar çağrı anında 401 döner ve ilgili katman degrade eder (çıktı durmaz, "
            "uydurma yok). Çözüm: oturumu `doppler run -p cureohub -c dev_personal -- claude` "
            "ile başlat → tüm ${VAR}'lar otomatik enjekte olur. (yoktez ve literatur authless — "
            "etkilenmez.) devlet-arsivleri anahtarı olsa bile upstream katalog oturumu ayrıca "
            "HP'de canlı olmalı (`devarsiv_session_status`)."
        )

    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
