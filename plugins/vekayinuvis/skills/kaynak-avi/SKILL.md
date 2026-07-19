---
name: kaynak-avi
description: Bir konu hakkında mevcut Osmanlı/Türk arşiv ve akademik kaynakları tarar (SOURCE_HUNT modu) — kaynak matrisi üretir.
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

**Geniş tarama `arsiv-tarama-distilleri` alt-ajanına DELEGE EDİLİR.** Çok-connector taraması
yoğunlaştıkça (7+ paralel çağrı) taramayı Task/Agent aracıyla bu ajana devret: ham çıktı ajanın
kendi penceresinde tüketilir, ana pencereye yalnız kompakt `arsiv_distillate` + `coverage` döner.
Bu delegasyon **Claude Code'da** mevcuttur; **claude.ai'de plugin alt-ajanı yoksa** doğrudan
Tier-2 anamnesis'e ingest→bounded query ile daralt (bkz. ${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md).
