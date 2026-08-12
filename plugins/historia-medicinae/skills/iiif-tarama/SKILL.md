---
name: iiif-tarama
description: "Dijitalleştirilmiş birincil kaynak avı — IIIF koleksiyonlarında (Wellcome Collection, Gallica/BnF, Internet Archive, Princeton, DPLA) yazma, erken basma, herbal, anatomi atlası ve risale bulur; Wellcome'da SAYFA DÜZEYİNDE tam-metin araması yapar. Kaynak-başına ölçülmüş yetenek matrisi ve bloklu yüzeylerin (LoC 403, NLM bot kapısı) dürüst yol haritası. Kullanın: 'bu eserin dijital kopyası var mı', 'yazma bul', 'IIIF', 'Wellcome', 'Gallica', 'el yazması tara', 'erken basma', 'anatomi atlası bul' isteklerinde."
argument-hint: "<eser/konu> [kurum] [dönem]"
allowed-tools: Read, Glob, Grep, WebFetch
disable-model-invocation: false
---

# IIIF Tarama — dijital birincil kaynak avı

Yükle: `../historia-medicinae/references/iiif-capability-matrix.md`.

## Temel gerçek: kaynaklar eşit yetenekte değil (ölçüldü 2026-08-11)

| Kaynak | Keşif | Manifest | **Sayfa-içi arama** |
|---|---|---|---|
| **Wellcome Collection** | ✅ | ✅ | ✅ **tek yüzey** |
| Gallica (BnF) | ✅ | ✅ | ❌ |
| Internet Archive | ✅ | ✅ | ❌ |
| Princeton Figgy | ✅ | ✅ | ❌ |
| DPLA | ✅ (yalnız bu connector üzerinden) | kısmi | ❌ |
| Library of Congress | ✅ | ❌ **403** | ❌ |
| NLM Digital Collections | ❌ **bot kapısı** | ❌ | ❌ |

Bu yüzden arama **Wellcome-önceliklidir**: metnin *içinde* ne yazdığını programatik olarak
öğrenebildiğimiz tek yer.

## Zincir A — konu taraması

```
ottoman_search_iiif("<konu>")     # 8 kaynakta arar
```
⚠️ Sıralama **"Ottoman-relevance first"**tir → küresel sorguda gürültü üretir. Ölçülen örnek:
`"plague treatise"` sorgusunda üst Gallica sonucu *Champavert: contes immoraux* (1832 roman);
gerçek isabetler (*A treatise of the plague* 1603/1721/1799) alttaydı.
**Sonuçlar başlık + tarih + kurum ile elenir. Üst sonuç körlemesine alınmaz.**

## Zincir B — Wellcome tam zinciri (uçtan uca doğrulandı)

```
1) Katalog (authless, WebFetch)
   https://api.wellcomecollection.org/catalogue/v2/works?query=<konu>&include=items

2) Manifest URI'sini AYIKLA — TÜRETME
   locations[].locationType.id == "iiif-presentation"  →  .url
   ⚠️ Dijitalleşmemiş eserde bu location YOKTUR → filtre şart

3) ottoman_fetch_iiif_manifest(<manifest URL>)
   → canvas listesi + metadata + LİSANS (manifestten okunur, varsayılmaz)

4) ottoman_search_within_manifest(<manifest>, "<terim>")
   → canvas + xywh koordinatlı isabetler        ← filonun tek sayfa-düzeyi yeteneği

5) Yalnız hedef canvas okunur (bağlam ekonomisi)
```

**Lisans:** Wellcome içeriği çoğunlukla **CC BY-NC 4.0** — atıf zorunlu, ticari kullanım yok.

## Sayfa-içi arama olmayan kaynaklarda

1. **Metadata + yapı** — canvas etiketleri, `structures` bloğu, bölüm başlıkları.
2. **Dış tam-metin** — aynı eserin IA OCR metni veya kritik edisyonu (openathens → annas-reader).
3. **Görsel okuma** — hedef canvas görüntüsü asistan görüsüyle okunur; **transkripsiyon iddiası
   olarak işaretlenir**, güven düzeyi ve okunamayan yerler yazılır.

## Bloklu yüzeyler — ne söylenir

| Kaynak | Yapılacak |
|---|---|
| **LoC** | Keşif sonucu + `tile.loc.gov` tek görseli kullanılabilir; sayfa listesi yok → `loc.gov` item sayfası verilir |
| **NLM** | Programatik erişim yok → koleksiyon adı + arama URL'si ile erişim yol haritası |
| **Europeana** | Sunucuda anahtar yapılandırılmamış → manifestoda `degraded` |
| **BHL** (herbal/materia medica) | Ücretsiz anahtar alınmamış → manifestoda `gap`; materia medica sorgularında bu boşluk **yazılır** |

**Değişmez:** bloklu yüzeyden içerik uydurulmaz.

## İki sert kural

1. **Manifest URI asla üretilmez** — daima arama sonucundan veya katalog API'sinden gelir.
   Şablondan tahmin edilmiş adres, çalışsa bile yanlış esere işaret edebilir → no-fabrication
   ihlali.
2. **Osmanlıca el yazması okuma bu skill'in işi değildir** → `vekayinuvis` delegasyonu.

## Çıktı

Bulunan eser tablosu: eser · kurum · shelfmark · tarih · manifest URI · lisans · sayfa-içi arama
var mı · erişim durumu.
