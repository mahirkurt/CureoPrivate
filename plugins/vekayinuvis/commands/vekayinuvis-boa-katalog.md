---
description: Resmî Devlet Arşivleri kataloğunda (BOA/BCA/Diplomatik/Askeri) doğrudan fon/kutu/gömlek araması + belge künyesi çeker (devlet-arsivleri connector).
argument-hint: <konu/terim [+ arşiv: Osmanlı|Cumhuriyet|Diplomatik|Askeri], örn. "veba tahaffuzhane 1890 Osmanlı">
---

`vekayinuvis` skill'ini **ARCHIVE_DEEP_DIVE** modunda, **`devlet-arsivleri`** connector'ı
odağıyla çalıştır. Referans: `references/devlet-arsivleri-katalog.md`.

Hedef: "$ARGUMENTS" için resmî katalog kaydı bul ve künyele.

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
3. **`devarsiv_get_belge(item_id, hash, arsiv)`** — en ilgili 1–3 kayıt için künye + erişim/satın-alma durumu.
4. Hicrî tarihleri `ottoman_convert_date` ile Miladî'ye eşle; ilgili transkripsiyon tezini
   `yoktez`'de ara.

Çıktı: **atıf-hazır** katalog kayıtları (fon/kutu/gömlek + Hicrî(+Miladî) + katalog URL), erişim
durumu ve varsa transkripsiyon-tezi köprüsü. **No-fabrication:** belge görüntüleri/tam-metni
üretilmez (eSatış/on-site); `hash` daima arama sonucundan gelir. Çıktıya **G0 kapsam manifestosu**
ekle (shared/coverage-manifest.md); ağır getirimde `arsiv-tarama-distilleri` ajanına delege et.
