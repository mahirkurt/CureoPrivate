---
description: Belirli bir arşiv/fond/tasnif içinde derin dalış yapar (ARCHIVE_DEEP_DIVE modu) — fond yol haritası + erişim talimatı.
argument-hint: <arşiv + fond + dönem, örn. "BOA HAT II. Mahmud tıbbiye">
---

`vekayinuvis` skill'ini **ARCHIVE_DEEP_DIVE** modunda çalıştır.

Hedef: "$ARGUMENTS" için fond/tasnif yol haritası + **canlı resmî katalog kayıtları** çıkar.
Önce `devarsiv_session_status`; sonra **`devarsiv_search(arsiv=1/2)` → resmî katalog kayıtları**
(fon/kutu/gömlek + özet + item_id/hash) ve ilgili kayıtta `devarsiv_get_belge`. Buna
ottoman-archives (get_source, search_literature, get_islam_ansiklopedisi) + yoktez (transkripsiyon
tezi) + literatur ekle.

**TAM-FİLO + bağlam ekonomisi:** bağlama uygun tüm server'ları çalıştır ve çıktıya **G0 kapsam
manifestosu** ekle (shared/coverage-manifest.md). Ağır getirimi `arsiv-tarama-distilleri` ajanına
delege et; büyük tam-metni anamnesis'e ingest et.

Erişim-kısıtlı kaynakların **belge görüntüsü/tam-metni** üretilmez (BOA/BCA eSatış+on-site; TKGM/
ATASE/İSAM/Süleymaniye…) — yalnız katalog kaydı + erişim talimatı; `session_required` ise re-login
yol haritası + degrade. Çift/üçlü tarih notasyonu ve çeviriyazı tutarlılığını koru.
