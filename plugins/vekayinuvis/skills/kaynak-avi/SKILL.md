---
name: kaynak-avi
description: Bir konu hakkında mevcut Osmanlı/Türk arşiv ve akademik kaynakları tarar (SOURCE_HUNT modu) — kaynak matrisi üretir.
context: fork
---

`vekayinuvis` skill'ini **SOURCE_HUNT** modunda çalıştır.

Hedef: kullanıcının belirttiği konu / kişi / kurum / dönem hakkında hangi arşivlerin ve
kaynakların mevcut olduğunu sistematik tara. CONNECTORS.md § 7'deki SOURCE_HUNT connector
setini kullan: **devlet-arsivleri** (`devarsiv_search` — veya modern/dönem-değişken terimde
`devarsiv_semantic_search` — kanıt-yoğunluğu; `capped:true` ise `devarsiv_list_fon_categories`
ile kapsam-haritası) + ottoman-archives (list_sources, search_iiif, search_dergipark,
search_dspace) + yoktez + literatur (DergiPark tam-metin) + tavily_search (akademik filtre).

Çıktı: **kaynak matrisi** (tür × erişim × dil × kanıt-yoğunluğu; resmî katalogda kayıt sayısı +
`capped` durumu dahil). Erişim-kısıtlı kaynaklar için belge içeriği üretme; yalnız katalog-bilgisi
ve erişim yol haritası ver. Restricted-kaynak disiplinini (CONNECTORS.md § 8) uygula.

**Geniş tarama, `arsiv-tarama-distilleri` alt-ajanına devredilir.** Bu skill `context: fork`
ile çalışır: çok-connector taraması yoğunlaştıkça (7+ paralel çağrı) ham çıktı bu ajanın kendi
penceresinde tüketilir; ana pencereye yalnız kompakt `arsiv_distillate` + `coverage` döner
(bkz. shared/context-economy-contract.md).
