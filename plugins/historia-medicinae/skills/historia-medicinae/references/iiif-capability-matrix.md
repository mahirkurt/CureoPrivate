# IIIF Yetenek Matrisi — ölçülmüş, iddia edilmemiş

Birincil kaynak getiriminde yüklenir. İlgili skill: `skills/iiif-tarama/SKILL.md`.
Ölçüm tarihi: **2026-08-11**.

---

## 1. Neden matris gerekiyor

`ottoman-archives` tek bir connector'dır ama arkasındaki kaynaklar **eşit yetenekte değildir**.
Bir kaynağın "IIIF destekliyor" olması, o kaynakta **sayfa-içi metin araması yapılabileceği**
anlamına gelmez. Fark, araştırma stratejisini kökten değiştirir.

| Kaynak | Keşif (`search_iiif`) | Manifest (`fetch_iiif_manifest`) | Sayfa-içi arama (`search_within_manifest`) |
|---|---|---|---|
| **Wellcome Collection** | ✅ | ✅ | ✅ **`search_service` DOLU** |
| Gallica (BnF) | ✅ | ✅ | ❌ (`search_service: null`) |
| Internet Archive | ✅ | ✅ (HTTP 200 ölçüldü) | ❌ |
| Princeton Figgy | ✅ | ✅ | ❌ |
| DPLA | ✅ (yalnız bu connector üzerinden) | kısmi | ❌ |
| SALT Research | ✅ | kısmi | ❌ |
| **Library of Congress** | ✅ | ❌ **403** | ❌ |
| **NLM Digital Collections** | ❌ | ❌ **bot kapısı (202/0 bayt)** | ❌ |

**Sonuç:** birincil kaynak avı **Wellcome-önceliklidir**. Bir metnin *içinde* ne yazdığını
programatik olarak öğrenebildiğimiz tek yüzey odur.

---

## 2. Wellcome zinciri — uçtan uca doğrulandı

```
1) Katalog araması (authless, WebFetch)
   https://api.wellcomecollection.org/catalogue/v2/works?query=<konu>&include=items
   → totalResults; her work'te locations[]

2) Manifest URI'sini AYIKLA — uydurma
   locations[].locationType.id == "iiif-presentation"  →  .url
   ⚠️ Dijitalleşmemiş eserde bu location YOKTUR (ölçüldü: s6w6vqcg boş, drfupc3x dolu)
      → filtre şart; manifest URI'si b-numarasından TÜRETİLMEZ

3) Manifest ayrıştır
   ottoman_fetch_iiif_manifest(<manifest URL>)
   → canvas listesi + metadata + lisans (ölçüldü: b3135631x → 180 canvas, CC BY-NC 4.0)

4) Sayfa-içi arama  ← FİLONUN TEK BU YÜZEYDEKİ YETENEĞİ
   ottoman_search_within_manifest(<manifest>, "<terim>")
   → canvas + xywh koordinatlı isabetler (ölçüldü: "dissection" → 3 sayfa-düzeyi isabet)

5) Yalnız hedef canvas'ı oku — bkz. context-economy-contract §4
```

**Lisans:** Wellcome içeriği çoğunlukla **CC BY-NC 4.0**'tır → atıf zorunlu, ticari kullanım yok.
Lisans manifestten okunur, varsayılmaz.

---

## 3. Sıralama gürültüsü — ölçülmüş tuzak

`ottoman_search_iiif` sonuçları **"Ottoman-relevance first"** sıralar. Küresel bir sorguda bu,
özellikle Gallica sonuçlarında alakasız üst-sıralar üretir.

> Ölçülen örnek: `"plague treatise"` sorgusunda üst Gallica sonucu ***Champavert: contes
> immoraux*** (1832 edebiyat eseri) idi. Aynı sorgunun gerçek isabetleri listenin altındaydı:
> *A treatise of the plague* 1603 / 1721 / 1799.

**Kural:** sonuçlar başlık + tarih + kurum ile **elenir**. Üst sonuç körlemesine alınmaz.

---

## 4. Bloklu yüzeyler — ne yapılır

| Kaynak | Durum | Yapılacak |
|---|---|---|
| **LoC** | Manifest 403 (evrensel; iki bağımsız ağdan ölçüldü). `tile.loc.gov` görsel ucu **200** | Keşif sonucu ve **tek görsel** kullanılabilir; sayfa listesi yok → kullanıcıya `loc.gov` item sayfası verilir |
| **NLM** | Akamai bot kapısı (202, 0 bayt) | Programatik erişim yok → koleksiyon adı + arama URL'si ile erişim yol haritası |
| **Europeana** | Sunucuda anahtar yapılandırılmamış | Manifestoda `degraded`; ücretsiz anahtar + sunucu env'i tek satırlık düzeltme |
| **BHL** (herbal/materia medica) | Ücretsiz anahtar alınmamış | Manifestoda `gap`; materia medica sorgularında bu boşluk **yazılır** |

**Değişmez:** bloklu yüzeyden içerik **uydurulmaz**. Katalog künyesi + erişim yol haritası verilir.

---

## 5. Diğer kaynaklarda strateji (sayfa-içi arama yokken)

Gallica/IA/Princeton'da metnin içine programatik olarak bakılamaz. Üç yol:

1. **Metadata + yapı:** manifest canvas etiketleri, bölüm başlıkları, `structures` bloğu.
2. **Dış tam-metin:** aynı eserin Internet Archive OCR metni veya bir kritik edisyonu
   (tam-metin şelalesi: openathens → annas-reader).
3. **Görsel okuma:** hedef canvas görüntüsü çekilir ve **asistan görüsüyle** okunur; okuma
   **transkripsiyon iddiası olarak işaretlenir** ve güven düzeyi belirtilir.

⚠️ Osmanlıca **el yazması** okuma bu plugin'in işi değildir → `vekayinuvis` delegasyonu
(ölçülmüş motor tablosu ve iki-okuyucu uzlaştırma orada).

---

## 6. Manifest URI'si asla üretilmez

Bir IIIF manifest adresi **daima bir arama sonucundan veya katalog API'sinden gelir**.
Şablondan türetilmiş adres (`.../presentation/v2/<tahmin>`) **no-fabrication ihlalidir**:
çalışsa bile yanlış esere işaret edebilir.
