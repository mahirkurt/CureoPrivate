---
name: olay
description: Bir tarihî olayı birincil kaynaklardan gün-gün yeniden kurgular (EVENT_RECONSTRUCTION modu) — kronolojik olay örgüsü + kaynak temeli.
---

`vekayinuvis` skill'ini **EVENT_RECONSTRUCTION** modunda çalıştır.

Hedef: kullanıcının belirttiği olay (örn. "31 Mart Vakası", "Vaka-i Hayriye",
"Kabakçı Mustafa İsyanı") için **gün-gün kronolojik örgü** kur — her adım tarih
(orijinal takvim + Miladî çift-tarih) + birincil/ikincil kaynak + fon/kutu/gömlek
künyesiyle çıpalanmış olarak.

Akış (bağlama uygun tümü **paralel** ilk turda):
1. **Resmî katalog kanıtı (`devlet-arsivleri`):** önce `devarsiv_session_status`;
   sonra `devarsiv_search`/`devarsiv_semantic_search(arsiv=1/2)` ile olaya dair
   BOA/BCA kayıtları (İrade/HAT/DH.* — telgraf, mazbata, tahkikat evrakı;
   fon/kutu/gömlek + item_id/hash). Geniş olayda `capped:true` → kapsam-haritası.
2. **Anlatı/literatür (`ottoman-archives` + `yoktez` + `literatur`):** vakanüvis
   kayıtları, hatırat, çağdaş matbuat (IIIF); transkripsiyon tezleri; DergiPark
   tam-metin monografi/makale. Uluslararası için `paper-search`/`consensus`/`exa`.
3. **Tarih omurgası (`ottoman-archives` hesaplama katmanı):** her düğüm için
   `convert_date`/`parse_ottoman_date` ile üç-takvim doğrulaması; Rumî sınır
   dönem (1839–1925) için doğrulamayı zorunlu yap (bkz.
   `${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/chronology.md`).
4. **Yasama boyutu (varsa — `resmigazete`/`mevzuat`/`tbmm`):** olay bir kanun/
   kararname/nizamnameyle sonuçlandıysa yasama soyağacını ekle (KANUN_GEREKÇESİ
   ile composable).

**No-fabrication:** her olay-düğümü gerçek bir kaynağa bağlıdır; boşluk varsa
`[bilinmiyor]`/`[tartışmalı]` işaretle, olay örgüsünü **uydurma bağlaçlarla
doldurma**. Çelişen anlatılar ayrı sunulur (tek "resmî" kurgu dayatılmaz).
Belge görüntüsü/OCR iddiası yalnız gerçek `devarsiv_get_belge_image`/
`devarsiv_ocr_belge` çıktısı + provenance ile aktarılır.

**TAM-FİLO + bağlam ekonomisi:** bağlama uygun tüm server'ları çalıştır ve
çıktıya **G0 kapsam manifestosu** ekle (`${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md`).
Ağır çok-connector fan-out'unu `arsiv-tarama-distilleri` alt-ajanına **DELEGE ET**
(Task/Agent aracıyla); büyük tam-metni `anamnesis`'e ingest→bounded query ile işle.
Bu delegasyon Claude Code'da mevcuttur; claude.ai'de plugin alt-ajanı yoksa
doğrudan Tier-2 anamnesis ile daralt (bkz.
`${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md`).

Çıktı: **gün-gün (veya safha-safha) kronolojik tablo** (tarih çift-notasyonu ×
olay × aktör × kaynak künyesi) + neden-sonuç örgüsü + kaynak-temelli belirsizlik
notları. Atıf disiplini (fon/kutu/gömlek + çift-tarih + katalog URL'i) ve IJMES/
TDV İA çeviriyazı zorunlu (bkz.
`${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/citation-and-transliteration.md`).
