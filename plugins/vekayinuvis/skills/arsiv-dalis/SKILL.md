---
name: arsiv-dalis
description: Belirli bir arşiv/fond/tasnif içinde derin dalış yapar (ARCHIVE_DEEP_DIVE modu) — fond yol haritası + erişim talimatı.
---

`vekayinuvis` skill'ini **ARCHIVE_DEEP_DIVE** modunda çalıştır.

Hedef: kullanıcının belirttiği arşiv + fond + dönem (örn. "BOA HAT II. Mahmud
tıbbiye") için fond/tasnif yol haritası + **canlı resmî katalog kayıtları** çıkar.
Önce `devarsiv_session_status`; sonra **`devarsiv_search(arsiv=1/2)`** (modern/dönem-değişken
terimde **`devarsiv_semantic_search`**) → resmî katalog kayıtları (fon/kutu/gömlek + özet +
item_id/hash + `capped`) ve ilgili kayıtta `devarsiv_get_belge`. **Kapsamlı erişim** (konu >1000,
`capped:true`): birincil yol **`devarsiv_deep_search(query, arsiv?, ust_fon?)`** — otomatik
arşiv×üst-fon×tarih süpürme (arsiv boş→dört arşiv birden), store'a yazar, `job_id` döner →
**`devarsiv_deep_result(job_id)` ile poll** (kapsam manifestosu; `complete=false`→boş ≠ "yok";
tamlık yalnız `year_bounds`/`fon_bounds` içinde). Store kapalıysa (`store_required`) manuel
enumerasyona (`list_fon_categories`+`detailed_search`+`item_id` union) degrade et
(`${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/devlet-arsivleri-katalog.md` §2b). **Boş sonuçtan "arşivde yok"
SONUCUNA VARMADAN ÖNCE** `devarsiv_coverage(arsiv?, ust_fon?)` ile hasat defterine bak (§3
no-fabrication). Buna ottoman-archives (get_source, search_literature, get_islam_ansiklopedisi) +
yoktez (transkripsiyon tezi) + literatur ekle.

**Erişim dalı (`devarsiv_get_belge.access`):** `access=="purchasable"` dönerse (belge henüz
satın alınmamış) ve kullanıcı belgenin **tüm** sayfalarına ihtiyaç duyuyorsa → **`/vekayinuvis:satinalma`**
akışına yönlendir (yalnız önizleme yeterliyse `devarsiv_get_belge_image`/`devarsiv_ocr_belge` ile
devam edilir, satın alma zorunlu değildir). `access=="purchased"` ise okuma DAİMA yerel arşivden
başlar: `devarsiv_list_archive` → `devarsiv_get_archive_page` (300 DPI + görü) — adım-adım okuma
akışı için `boa-katalog/SKILL.md` (adım 3–4). **Çok-sayfa okumada K4 kararı:** ≤5 sayfa VE tek motor →
`devarsiv_ocr_archive_pages` (sync); >5 sayfa VEYA çok-motorlu (`both`) tam belge → `devarsiv_ocr_submit`
→ `devarsiv_ocr_result` ile poll → **`/vekayinuvis:toplu-okuma`** akışına devret.

**TAM-FİLO + bağlam ekonomisi:** bağlama uygun tüm server'ları çalıştır ve çıktıya **G0 kapsam
manifestosu** ekle (${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md). Ağır çok-connector fan-out'unda
(7+ paralel çağrı) taramayı `arsiv-tarama-distilleri` alt-ajanına **DELEGE ET** (Task/Agent aracıyla):
ham çıktı ajanın kendi penceresinde tüketilir, ana pencereye yalnız kompakt `arsiv_distillate` +
`coverage` döner — Claude Code'da bu delegasyon mevcuttur, claude.ai'de yoksa doğrudan Tier-2
anamnesis'e ingest→bounded query ile işle. Büyük tam-metni anamnesis'e ingest et.

Belge görüntüsü/OCR/HTR yalnız gerçek `devarsiv_get_belge_image`, `devarsiv_ocr_belge`
veya satın alınmış çok-sayfada `devarsiv_get_archive_page`/`devarsiv_ocr_belge_pages` çıktısı varsa
aktarılır; yoksa yalnız katalog kaydı + erişim talimatı ver. TKGM/ATASE/İSAM/Süleymaniye gibi diğer kısıtlı
kaynaklarda içerik uydurma. `session_required` ise re-login yol haritası + degrade. Çift/üçlü
tarih notasyonu ve çeviriyazı tutarlılığını koru.
