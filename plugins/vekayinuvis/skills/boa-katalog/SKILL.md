---
name: boa-katalog
description: Resmî Devlet Arşivleri kataloğunda (BOA/BCA/Diplomatik/Askeri) doğrudan fon/kutu/gömlek araması + belge künyesi çeker (devlet-arsivleri connector).
---

`vekayinuvis` skill'ini **ARCHIVE_DEEP_DIVE** modunda, **`devlet-arsivleri`** connector'ı
odağıyla çalıştır. Referans: `${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/devlet-arsivleri-katalog.md`.

Hedef: kullanıcının belirttiği konu/terim (+ opsiyonel arşiv: Osmanlı|Cumhuriyet|Diplomatik|Askeri,
örn. "veba tahaffuzhane 1890 Osmanlı") için resmî katalog kaydı bul ve künyele.

Akış:
1. **`devarsiv_session_status`** — oturum canlı mı? `session_required` ise: kullanıcıya
   "resmî katalog oturumu düştü, HP noVNC re-login gerekli" bildir + ottoman-archives/yoktez ile
   degrade devam (asla uydurma).
2. **Arama** — arsiv: 2=Osmanlı/BOA · 1=Cumhuriyet/BCA · 3=Diplomatik · 4=Askeri (belirtilmemişse
   konudan çıkar/hepsini tara). Doğru aracı seç:
   - Bilinen tam terim/fon → **`devarsiv_search(query, arsiv=?)`**.
   - Modern/dönem-değişken terim (göç, salgın, karantina, belediye…) → **`devarsiv_semantic_search`**
     (Osmanlıca eşdeğer genişletme + bge-m3 rerank; `matched_variants` hangi karşılık eşleşti gösterir).
   - Sonuç: fon/kutu/gömlek + özet + Hicrî tarih + item_id/hash + fon facet'leri + `capped`.
   - **Geniş sorgu `refine_required` → daralt** (fon/tarih). **Tam 1000 (`capped:true`) → kapsamlı
     erişim:** `devarsiv_list_fon_categories(arsiv)` → her üst-fon için `devarsiv_detailed_search(arsiv,
     ust_fon=fon, ozet=<konu>[, tarih_turu/yil_bas/yil_bit])` → `item_id` union (§2b). Bu ağır fan-out
     `arsiv-tarama-distilleri` ajanına delege edilir.
3. **`devarsiv_get_belge(item_id, hash, arsiv)`** — en ilgili 1–3 kayıt için künye + erişim/satın-alma
   durumu (`access`). **`access=="purchasable"`** dönerse ve kullanıcı belgenin tüm sayfalarına
   ihtiyaç duyuyorsa → **`/vekayinuvis:satinalma`** akışına yönlendir (yalnız önizleme yeterliyse
   satın alma zorunlu değil, adım 4'e devam edilir). **`access=="purchased"`** ise okuma DAİMA
   yerel arşivden başlar (`devarsiv_list_archive` → `devarsiv_get_archive_page`, 300 DPI + görü);
   katalog önizlemesi yalnız satın-alınmamış belgeler içindir.
4. **BELGE OKUMA (istenirse):** `devarsiv_get_belge_image(item_id, hash, arsiv)` → sayfa
   taraması (önizleme, satın-almadan bağımsız). **Osmanlı el yazması** için taramayı **doğrudan
   görünle transkribe et**; Latin/Cumhuriyet için `devarsiv_ocr_belge` deterministik metin
   (basılı damga+referans kodu OCR ile doğrulanır). **Çok-sayfa okumada K4 kararı:** ≤5 sayfa
   VE tek motor → `devarsiv_ocr_archive_pages` (sync); >5 sayfa VEYA çok-motorlu (`both`) tam belge →
   `devarsiv_ocr_submit` → `devarsiv_ocr_result` ile poll → **`/vekayinuvis:toplu-okuma`** akışına
   devret. Tarama gerçek — uydurma yok; düşük-güven dürüstçe belirtilir; transkripsiyon insan
   doğrulamasına tabi (bkz. `devlet-arsivleri-katalog.md` §7).
5. Hicrî tarihleri `ottoman_convert_date` ile Miladî'ye eşle; ilgili transkripsiyon tezini
   `yoktez`'de ara.

Çıktı: **atıf-hazır** katalog kayıtları (fon/kutu/gömlek + Hicrî(+Miladî) + katalog URL), erişim
durumu ve varsa transkripsiyon-tezi köprüsü. **No-fabrication:** belge görüntüsü/OCR/HTR yalnız
gerçek araç çıktısı ve provenance ile aktarılır; çekilmediyse katalog düzeyinde kal. `hash` daima
arama sonucundan gelir. Çıktıya **G0 kapsam manifestosu** ekle (${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md);
ağır getirimde `arsiv-tarama-distilleri` ajanına delege et.
