---
name: metin
description: "EDITIO modu — tarihsel bir tıp metnini okuma, konumlandırma ve edisyon eleştirisi: Hippokratik külliyat, Galen, el-Kânûn, herbal ve farmakopeler, veba risaleleri, anatomi atlasları, dönem ders kitapları. Hangi edisyon, hangi çeviri, hangi el yazması geleneği. Kullanın: 'bu metni oku', 'X eserinin edisyonu', 'hangi çeviri güvenilir', 'el yazması geleneği', 'metin eleştirisi', 'kritik edisyon' sorularında."
argument-hint: "<eser adı veya manifest/kaynak> [dil] [edisyon]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# EDITIO — Tarihsel Tıp Metni Okuma

Flagship protokolü `EDITIO` moduyla çalıştır.

## Zorunlu yükleme

```
view ../historia-medicinae/references/retrospective-diagnosis.md   # ZORUNLU (metinde hastalık tarifi geçer)
view ../historia-medicinae/references/historical-nosology.md
view ../historia-medicinae/references/citation-and-transliteration.md
view ../historia-medicinae/references/source-typology.md
```

## Sıra

1. **Eseri konumlandır** — yazar(lar), tarih, dil, tür, muhatap kitle. ⚠️ Hippokratik külliyat
   **tek yazarlı değildir**; "Hippokrat dedi ki" cümlesi çoğu kez yanlıştır.
2. **Aktarım zinciri** — metin bize hangi yolla ulaştı? (Yunanca → Süryanice → Arapça → Latince
   gibi zincirler analiz nesnesidir; Galen külliyatının büyük kısmı Arapça tercüme yoluyla
   korunmuştur.)
3. **Edisyon seç** — kritik edisyon var mı, hangisi? Çeviri kullanılıyorsa **çevirmen, yıl ve
   çeviri kararları** belirtilir. Kaynak metinden mi, ara dilden mi çevrilmiş?
4. **Metni getir** — sıra: IIIF (yazma/erken basma; **Wellcome'da sayfa-içi arama**) →
   openathens (kritik edisyon) → annas-reader (son çare). Perseus/Scaife CTS **ölü** (ölçüldü);
   Yunanca-Latince için Hopper `xmlchunk` veya GitHub `PerseusDL/canonical-greekLit`
   (Hipokrat `tlg0627`, Galen `tlg0057`).
5. **Oku ve alıntıla** — terim üçlüsü (özgün + çeviriyazı + açıklama); hastalık tarifleri
   **modern etikete çevrilmez** (dört kapı kuralı).
6. **Büyük metin** → `anamnesis` ingest (`histmed:` ön-eki) → sınırlı sorgu. Ham döküm yok.

## Osmanlıca / Arap harfli el yazması

Bu plugin **paleografi yapmaz**. Osmanlıca el yazması okuma → `vekayinuvis` delegasyonu
(ölçülmüş motor tablosu ve iki-okuyucu uzlaştırma orada). Kurulu değilse: katalog künyesi +
görüntü + "transkripsiyon yapılmadı" beyanı. Metin **asla uydurulmaz**.

## Görsel okuma yapılırsa

Sayfa görüntüsü asistan görüsüyle okunduysa bu **transkripsiyon iddiası olarak işaretlenir**,
güven düzeyi ve okunamayan yerler belirtilir.

## Çıktı

G0 manifestosu · edisyon künyesi tam · manifest URI (uydurulmamış) · alıntılar folio/canvas ile ·
çeviri kararları görünür.
