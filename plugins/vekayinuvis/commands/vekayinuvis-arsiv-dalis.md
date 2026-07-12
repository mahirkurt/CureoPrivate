---
description: Belirli bir arşiv/fond/tasnif içinde derin dalış yapar (ARCHIVE_DEEP_DIVE modu) — fond yol haritası + erişim talimatı.
argument-hint: <arşiv + fond + dönem, örn. "BOA HAT II. Mahmud tıbbiye">
---

`vekayinuvis` skill'ini **ARCHIVE_DEEP_DIVE** modunda çalıştır.

Hedef: "$ARGUMENTS" için fond/tasnif yol haritası + **canlı resmî katalog kayıtları** çıkar.
Önce `devarsiv_session_status`; sonra **`devarsiv_search(arsiv=1/2)`** (modern/dönem-değişken
terimde **`devarsiv_semantic_search`**) → resmî katalog kayıtları (fon/kutu/gömlek + özet +
item_id/hash + `capped`) ve ilgili kayıtta `devarsiv_get_belge`. **Kapsamlı erişim** (konu >1000,
`capped:true`): `devarsiv_list_fon_categories(arsiv)` → her üst-fon için `devarsiv_detailed_search
(arsiv, ust_fon=fon, ozet=<konu>[, tarih_turu/yil_bas/yil_bit])` → `item_id` union ile 1000-tavanı
aş (`devlet-arsivleri-katalog.md` §2b). Buna ottoman-archives (get_source, search_literature,
get_islam_ansiklopedisi) + yoktez (transkripsiyon tezi) + literatur ekle.

**TAM-FİLO + bağlam ekonomisi:** bağlama uygun tüm server'ları çalıştır ve çıktıya **G0 kapsam
manifestosu** ekle (shared/coverage-manifest.md). Ağır getirimi `arsiv-tarama-distilleri` ajanına
delege et; büyük tam-metni anamnesis'e ingest et.

Belge görüntüsü/OCR/HTR yalnız gerçek `devarsiv_get_belge_image`, `devarsiv_ocr_belge`
veya satın alınmış çok-sayfada `devarsiv_ocr_belge_pages` çıktısı varsa aktarılır; yoksa
yalnız katalog kaydı + erişim talimatı ver. TKGM/ATASE/İSAM/Süleymaniye gibi diğer kısıtlı
kaynaklarda içerik uydurma. `session_required` ise re-login yol haritası + degrade. Çift/üçlü
tarih notasyonu ve çeviriyazı tutarlılığını koru.
