---
description: Bir konu hakkında mevcut Osmanlı/Türk arşiv ve akademik kaynakları tarar (SOURCE_HUNT modu) — kaynak matrisi üretir.
argument-hint: <konu / kişi / kurum / dönem>
---

`vekayinuvis` skill'ini **SOURCE_HUNT** modunda çalıştır.

Hedef: "$ARGUMENTS" konusunda hangi arşivlerin ve kaynakların mevcut
olduğunu sistematik tara. CONNECTORS.md § 7'deki SOURCE_HUNT connector
setini kullan: ottoman-archives (list_sources, search_iiif, search_dergipark,
search_dspace) + yoktez + tamamlayıcı akademik katman.

Çıktı: **kaynak matrisi** (tür × erişim × dil × kanıt-yoğunluğu). Erişim-kısıtlı
kaynaklar için belge içeriği üretme; yalnız katalog-bilgisi ve erişim yol
haritası ver. Restricted-kaynak disiplinini (CONNECTORS.md § 8) uygula.
