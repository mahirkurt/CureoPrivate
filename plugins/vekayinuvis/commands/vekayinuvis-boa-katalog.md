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
2. **`devarsiv_search(query, arsiv=?)`** — arsiv: 2=Osmanlı/BOA · 1=Cumhuriyet/BCA · 3=Diplomatik ·
   4=Askeri (belirtilmemişse konudan çıkar/hepsini tara). Sonuç: fon/kutu/gömlek + özet + Hicrî
   tarih + item_id/hash + fon facet'leri. **Geniş sorgu `refine_required` dönerse daralt** (fon/tarih ekle).
3. **`devarsiv_get_belge(item_id, hash, arsiv)`** — en ilgili 1–3 kayıt için künye + erişim/satın-alma durumu.
4. Hicrî tarihleri `ottoman_convert_date` ile Miladî'ye eşle; ilgili transkripsiyon tezini
   `yoktez`'de ara.

Çıktı: **atıf-hazır** katalog kayıtları (fon/kutu/gömlek + Hicrî(+Miladî) + katalog URL), erişim
durumu ve varsa transkripsiyon-tezi köprüsü. **No-fabrication:** belge görüntüleri/tam-metni
üretilmez (eSatış/on-site); `hash` daima arama sonucundan gelir. Çıktıya **G0 kapsam manifestosu**
ekle (shared/coverage-manifest.md); ağır getirimde `arsiv-tarama-distilleri` ajanına delege et.
