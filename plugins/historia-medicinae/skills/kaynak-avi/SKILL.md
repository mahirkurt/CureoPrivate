---
name: kaynak-avi
description: "SOURCE_HUNT modu — bir tıp tarihi konusu için birincil ve ikincil kaynak envanteri çıkarır: hangi koleksiyonda ne var, dijital mi, erişim yolu ne, hangisi bloklu. Kullanın: 'bu konuda hangi kaynaklar var', 'kaynak taraması', 'nereden başlamalıyım', 'hangi arşivde', 'bibliyografya çıkar' sorularında."
argument-hint: "<konu> [dönem] [coğrafya]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# SOURCE_HUNT — Kaynak Avı

Flagship protokolü `SOURCE_HUNT` moduyla çalıştır.
Yükle: `source-typology.md` · `iiif-capability-matrix.md` · `search-strategy.md` · `region-layers.md`.

## Çıktı: kaynak envanteri tablosu

| Kaynak | Tür (P1/P2/P3) | Kurum/koleksiyon | Dijital mi | Erişim yolu | Durum |
|---|---|---|---|---|---|

**Durum sözlüğü:** `erişilebilir` · `lisanslı band gerekir` · `bloklu (gerekçe)` ·
`dijitalleşmemiş — fiziksel erişim` · `bulunamadı (arandı: <terimler>)`.

## Sıra

1. **İkincil harita** — openalex (T12324/T12990/T14475/T12778) + pubmed-epmc (MeSH K01.400) +
   paper-search (monograf katmanı) ile alanın standart eserlerini ve son çalışmaları çıkar.
2. **Birincil tarama** — IIIF (`iiif-tarama` skill'i): Wellcome öncelikli, sonra Gallica/IA/
   Princeton. Sıralama gürültüsü elenir.
3. **Yasama kaydı** — konu kurumsal/politik boyut taşıyorsa Hansard/GovInfo/TBMM.
4. **Bölgesel/dil katmanı** — en az iki dil-bölge (`region-layers.md`); TR için literatur+yoktez.
5. **Erişilemeyenler** — bloklu yüzeyler (LoC manifest, NLM, HathiTrust tam-metin) için
   **erişim yol haritası** yazılır: kurum, koleksiyon adı, arama sayfası, alternatif kopya.

## Değişmezler

- Manifest URI veya çağrı numarası **uydurulmaz**; daima bir arama sonucundan gelir.
- "Kaynak yok" denmez — "şu terimlerle şurada arandı, sonuç boş" denir.
