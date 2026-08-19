---
name: toplu-okuma
description: Çok-sayfalı satın-alınmış belgede async OCR (Transleyt varsayılan) + anamnesis ingest.
---

`vekayinuvis` skill'ini **ASYNC OCR** akışında, **`devlet-arsivleri`** + **`anamnesis`**
connector'ları odağıyla çalıştır. Referans: `${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/devlet-arsivleri-katalog.md` §8.4.

Hedef: satın-alınmış, çok-sayfalı bir belgeyi (>5 sayfa VEYA çok-motorlu (`both`) tam belge)
sync OCR sınırını aşan bir işle işlemek — async kuyruk + tek-seferlik tam-metin okuma +
`anamnesis` ingest ile bağlam ekonomisini korumak. ≤5 sayfalık tek-motor işler bu
skill'e gelmeden `/vekayinuvis:arsiv-oku`'nun sync yolunda çözülür; bu skill yalnız
aşağıdaki eşiği aşan işleri üstlenir.

## K4 — Sync/async karar kuralı

≤5 sayfa VE tek motor → `devarsiv_ocr_archive_pages` (sync). >5 sayfa VEYA `both` tam belge → `devarsiv_ocr_submit` → `devarsiv_ocr_result(include_text=false)` ile poll → `done`'da **tek sefer** `include_text=true` → anamnesis `ingest_document(collection=vekayinuvis:run:<12hex>, doc_id="vkrun:<12hex>:devarsiv:<code>", …)` → sonraki sorgular `hybrid_query(collection=…)`. `stale` → aynı parametrelerle resubmit (arşiv PDF yerel; maliyet tekrarlanmaz).

## Akış

0. **Arşiv önkoşulu.** `code` yerel arşivde yoksa (yeni satın alım) — `devarsiv_ocr_submit`
   yerel PDF arşivini okur — önce `devarsiv_rebuild_archive(incremental=True[, limit])` ile
   satın-alınanı 300 DPI kayıpsız PDF olarak indir. Oturum düşükse `session_required` (noVNC
   re-login; mevcut arşiv korunur). `devarsiv_list_archive` ile `code`'un geldiğini doğrula.
1. **Submit.** `devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)` — `[_RW]`,
   idempotent; `job_id` döner. Aynı `code`+`pages`+`engine` ile tekrar çağrı yeni iş
   kuyruklamaz.
2. **Poll disiplini.** `devarsiv_ocr_result(job_id, include_text=false)` ile
   ilerlemeyi izle; kullanıcıya ilerlemeyi kompakt raporla (ör. "3/15 sayfa"). Ham
   OCR metni bu aşamada **çekilmez** — yalnız durum (`queued`/`running`/`done`/
   `error`/`stale`) ve sayfa ilerlemesi.
3. **`done` → TEK SEFER tam metin.** İş bittiğinde `devarsiv_ocr_result(job_id,
   include_text=true)` **yalnız bir kez** çağrılır; dönen tam metin hemen
   `anamnesis.ingest_document(collection="vekayinuvis:run:<12hex>",
   doc_id="vkrun:<12hex>:devarsiv:<code>", text=<tam metin>,
   metadata={arsiv, sayfa, engine})` ile indekslenir.
4. **Ham metni pencereden düşür.** Ingest tamamlandıktan sonra ham OCR metni ana
   pencerede tutulmaz; izleyen erişim `anamnesis.hybrid_query(collection=
   "vekayinuvis:run:<12hex>", doc_ids=["vkrun:<12hex>:devarsiv:<code>"],
   queries=[...])` ile sınırlı, provenance-damgalı dilim çeker
   (atıf `doc_id::idx`; bkz. `${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md` §6).
5. **`stale` davranışı.** Durum `stale` dönerse iş süresi dolmuş veya sonuç
   temizlenmiştir; **aynı parametrelerle resubmit** edilir (adım 1'e dön) — arşiv
   PDF'i yerelde durduğu için bu tekrar maliyet doğurmaz, yalnız OCR işi yeniden
   kuyruklanır.
6. **Görü teyidi.** Osmanlı el yazması sayfalarda OCR/HTR çıktısı tek başına
   yeterli kanıt değildir; düşük-güven/çelişkili sayfalar için
   `devarsiv_get_archive_page(code, page)` ile görüyle çapraz-kontrol
   `/vekayinuvis:arsiv-oku` akışına devredilebilir.

## İş bitince özet tablo

İş `done` olduğunda ve ingest tamamlandığında kullanıcıya aşağıdaki biçimde bir
özet tablo sunulur:

| Sayfa | Motor | Kelime | Görü-teyit gereken mi |
|---|---|---|---|
| 1 | both (Transkribus+eScriptorium+tesseract) | ~120 | Hayır (yüksek güven) |
| 2 | both | ~95 | Evet (düşük güven / gürültülü el yazması) |
| … | … | … | … |

"Motor" sütunu düşen motor varsa `unavailable` nedenini taşır; "Görü-teyit gereken
mi" sütunu düşük-güven veya çelişkili sayfaları işaretler — bu sayfalar için
`devarsiv_get_archive_page` ile görüyle doğrulama önerilir.

**No-fabrication:** OCR/HTR çıktısı ölçülü %13-23 CER taşır (özel ad/tarih/meblağda hata
beklenir, çıktıda beyan edilir); Osmanlı el yazmasında varsayılan Transleyt + asistan görüsü
uzlaştırması (K2 — denk ve bağımsız; Transkribus taşra-kâtibi ellerinde gürültülü
olabilir). Ham HTR metni rapora doğrudan alıntılanmaz — görüyle doğrulanmış okuma
alıntılanır, HTR dipnotta kalır (K6 madde 5).
