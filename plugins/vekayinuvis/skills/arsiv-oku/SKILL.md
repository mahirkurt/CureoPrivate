---
name: arsiv-oku
description: Satın-alınmış belgeleri yerel BOA-kodlu arşivden okuma — 300 DPI görü birincil.
---

`vekayinuvis` skill'ini **ARŞİV OKUMA** akışında, **`devlet-arsivleri`** connector'ı
odağıyla çalıştır. Referans: `references/devlet-arsivleri-katalog.md` §8.2.

Hedef: `devarsiv_get_belge` çağrısının `access=="purchased"` döndürdüğü bir belgenin
tüm sayfalarını, katalog önizlemesinden değil **yerel arşivden**, 300 DPI görüyle
okumak.

Belge satın alınmışsa okuma DAİMA yerel arşivden başlar: devarsiv_list_archive → devarsiv_get_archive_page (300 DPI + görü); katalog önizlemesi (sample) yalnız satın-alınmamış belgeler içindir.

## Akış

1. **Code seçimi.** `devarsiv_list_archive(query?)` — BOA-kodlu yerel PDF arşivini
   sorgula; sonuç satırları `code`/`yer`/`tarih`/`özet`/`sayfa` taşır. Kullanıcının
   belirttiği belgeyle eşleşen `code`'u seç; birden fazla aday varsa özet/tarih ile
   daralt, gerekirse kullanıcıya sor.
2. **Sayfa-sayfa görüyle okuma (birincil).** Seçilen `code` için
   `devarsiv_get_archive_page(code, page)` ile her sayfayı sırayla çek — 300 DPI
   ImageContent, **birincil okuma kalitesi**. Görüntü ana pencerede sayfa-sayfa
   tüketilir (distiller'a gönderilmez — görü ana asistanda; bkz.
   `shared/context-economy-contract.md` §6). Osmanlı el yazması sayfada taramayı
   doğrudan görüyle transkribe et; Latin/basılı sayfada görsel doğrulama olarak
   kullan.
3. **Deterministik katman gerekiyorsa (≤5 sayfa).** `devarsiv_ocr_archive_pages(code,
   pages?, arsiv?, lang?, engine?)` — sync OCR, MULTIPAGE_MAX_PAGES (5) sınırına
   kadar. Motor seçimi K2 rehberine tabidir: `engine="auto"` Osmanlı için `both`'a
   düşer (Transkribus PyLaia el yazması + eScriptorium Kraken basılı, tesseract
   damga/referans-kodu katmanıyla üç sütun), diğer arşivler için `tesseract`'a
   düşer; `both` yalnız görünün değerli bulduğu sayfada çağrılır (kredi kuralı —
   Transkribus kredi tüketimini gereksiz sayfalarda harcamamak için).
4. **Künye/PDF gerekiyorsa.** `devarsiv_get_archive_pdf(code, include_base64?,
   max_bytes?)` — künye + sınırlı base64 PDF; büyük belgede `max_bytes` ile
   pencere taşmasını önle.
5. **>5 sayfa → toplu okumaya devret.** Sayfa sayısı sync OCR sınırını aşıyorsa
   veya `engine="both"` tam belge isteniyorsa `/vekayinuvis:toplu-okuma` akışına
   geç (K4 sync/async karar kuralı).

Not: `devarsiv_ocr_belge_pages(t, hash, arsiv?, pages?, lang?, engine?)` eSatış
viewer'ı üzerinden de çok-sayfa OCR sağlar ama **temsilî-sayfa sınırlıdır**;
yukarıdaki yerel-arşiv akışı TAM ve güvenilir yoldur.

## Atıf biçimi

Yerel arşivden okunan her sayfa şu biçimde atıflanır:

```
BOA <code>, s.<page> (yerel arşiv 300 DPI, görüyle okundu)
```

OCR/HTR katmanı da kullanıldıysa motor adı ve güven skoru dipnotta eklenir (§7.1 K2).
Görüntü **gerçek taramadır, uydurulmaz**; OCR düşük-güvende `mean_confidence` + `note`
ile dürüstçe raporlanır. Ham HTR metni rapora doğrudan alıntılanmaz — görüyle
doğrulanmış okuma alıntılanır, HTR dipnotta kalır (K6 madde 5). Transkripsiyon her
hâlde insan doğrulamasına tabidir; çift-tarih (Hicrî/Rumî + Miladî, `ottoman_convert_date`
ile) ve fon/kutu/gömlek atıf disiplini korunur.
