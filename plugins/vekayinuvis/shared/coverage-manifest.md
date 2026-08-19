# Kapsam Manifestosu (G0) — biçim ve örnek

**Amaç:** "wire edilmiş tüm araçlar bağlama uygun her sorguda çalıştı" iddiasının doğrulanabilir kanıtı. Her substantif vekayinüvis çıktısı (SOURCE_HUNT, ARCHIVE_DEEP_DIVE, PROSOPOGRAPHY, EVENT_RECONSTRUCTION, HISTORIOGRAPHY, ACADEMIC_REPORT, KANUN_GEREKÇESİ) bu bloğu taşır (başta veya sonda). Eksik satır = **G0 FAIL** (**Claude Code'da** Stop hook tamamlatır; **claude.ai'de plugin hook'ları çalışmaz → bu kapıyı çıktıdan önce kendi-disiplininle doğrula, manifestoyu sen ekle**). Tek-tool/hızlı sorgu (ör. yalnız CHRONOLOGY_CONVERSION) manifesto gerektirmez.

## Kurallar

- Wire edilmiş **17 server** için (çekirdek: ottoman-archives · devlet-arsivleri · yoktez; akademik: literatur · consensus · scholar-gateway · exa · tavily · paper-search; tam-metin: openathens · annas-reader; yasama/mevzuat: resmigazete · mevzuat · tbmm; destekleyici: yok-akademik · detsis; substrat: anamnesis) **birer satır** — bağlı olsun olmasın. (`marmara` bu turda wire edilmedi — DNS yayınlanmadı, bkz. CONNECTORS.md § 1 not; manifestoya dahil değil.)
- Durum sözlüğü: `hit N` (N kayıt döndü) · `empty` (çalıştı, sonuç yok) · `degraded` (fetch fallback / `mcp_verified=false` / session_required) · `skipped: <gerekçe>` (anahtar yok / mod için N/A / oturum düşük).
- `skipped` gerekçesi zorunlu ve denetlenebilir olmalı ("anahtar yok", "mod için N/A", "session_required — re-login gerekli", "companion bağlı değil"). **Gerekçesiz skip yasak.**
- **Bağlı/kurulu katman atlanamaz:** bir connector bağlıyken tetiklenmiş bağlamda `skipped` yazmak **meşru değildir** (G0 FAIL). `skipped: … bağlı değil` yalnız gerçek yoklukta doğrudur.
- **devlet-arsivleri özel:** anahtar bağlı olsa bile upstream oturum düşükse `degraded: session_required (HP noVNC re-login)` yazılır — bu **skip değil degrade**'dir; resmî katalog atlanmış sayılmaz, dürüstçe raporlanır ve ottoman/yoktez ile ikame edilir.
- **yok-akademik destekleyicidir:** modern akademisyen/ekol bağlamı yoksa `skipped: mod için N/A` meşrudur; bağlam varken bağlıyken atlanması G0 ihlalidir.
- **anamnesis substrat satırı** her manifestoda mevcuttur; collection **`vekayinuvis:run:<12hex>`**,
  doc_id **`vkrun:<12hex>:<kanonik>`**. `corpus_stats` çalışma seti değildir.
- Manifesto, `arsiv-tarama-distilleri`'nin döndürdüğü `coverage` bloğundan türetilir; alt-ajan çağrılmadıysa doğrudan araç çağrılarından derlenir.

## Örnek

```
### Kapsam Manifestosu (G0) — Mod: ARCHIVE_DEEP_DIVE · Konu: İzmir'de veba/tahaffuzhane tedbirleri (geç Osmanlı)
Çekirdek arşiv
  ottoman-archives     → hit 5   (İА "Tahaffuzhane", IIIF Gallica sağlık nizamnamesi, convert_date H-1337)
  devlet-arsivleri     → hit 13  (BOA arsiv=2: DH.İ.UM 22/19, Y..EE..KP 11/1095, DH.MUİ 55/41 … + fon facet)
  yoktez               → hit 3   (Osmanlı'da karantina/tahaffuzhane doktora tezleri; transkripsiyon)
Akademik
  literatur            → hit 4   (DergiPark: 19.yy Osmanlı karantina makaleleri, tam-metin + referans)
  consensus            → hit 2   (salgın-tarihi hakemli sentez)
  scholar-gateway      → hit 1   (pasaj-düzeyi: Ottoman public health)
  exa                  → hit 2   (akademik blog / kurum sayfası)
  tavily               → empty   (modern haber yok — tarihsel konu)
  paper-search         → hit 3   (Google Scholar/Semantic Scholar: Ottoman quarantine)
Tam-metin (kitap+makale)
  openathens           → hit 2   (Millet Kütüphanesi: 19.yy karantina monografı tam-metin → anamnesis)
  annas-reader         → skipped: gerekmedi (lisanslı band yeterli)
Yasama/mevzuat
  resmigazete          → skipped: mod için N/A (ARCHIVE_DEEP_DIVE — KANUN_GEREKÇESİ değil)
  mevzuat              → skipped: mod için N/A (ARCHIVE_DEEP_DIVE — KANUN_GEREKÇESİ değil)
  tbmm                 → skipped: mod için N/A (ARCHIVE_DEEP_DIVE — KANUN_GEREKÇESİ değil)
Destekleyici
  yok-akademik         → skipped: mod için N/A (modern akademisyen prosopografisi kapsamda değil)
  detsis               → skipped: mod için N/A (kurumsal prosopografi kapsamda değil; ayrıca Cumhuriyet-sınırlı)
Büyük-veri substratı (Tier 2)
  anamnesis            → ingest 2 belge (collection=vekayinuvis:run:<id>; vkrun:<id>:yoktez:<tez-no>, vkrun:<id>:devarsiv:2/DH.İ.UM/22-19) · 7 bounded query
```

Büyük-veri satırı (Tier 2) kullanıma göre değişir:
- Büyük tam-metin ingest edildiyse: `anamnesis → ingest N belge (doc_id'ler) · M bounded query`
- Getirim küçük kaldıysa: `anamnesis → skipped: gerekmedi (küçük getirim)`
- Anahtar yoksa: `anamnesis → skipped: anahtar yok (bounded-chunk fallback)`

Not: `empty` ve `skipped` **başarısızlık değil**, kapsamın dürüst kanıtıdır — mühim olan hiçbir server'ın sessizce atlanmamasıdır. `degraded` (session_required dahil) de dürüst bir durumdur; resmî katalogun atlanmadığını, yalnız ikame edildiğini gösterir.
