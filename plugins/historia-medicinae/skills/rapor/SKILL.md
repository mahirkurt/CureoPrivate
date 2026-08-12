---
name: rapor
description: "RELATIO modu — birikmiş bulguları yayımlanabilir akademik makaleye dönüştürür (Türkçe veya İngilizce). Temiz-kopya doktrini, Chicago atıf, kaynak envanteri, sınırlılıklar bölümü, kronoloji şeridi. Kullanın: 'raporu yaz', 'makaleye dönüştür', 'akademik rapor', 'bunu yayına hazırla', 'derle ve yaz' isteklerinde."
argument-hint: "[tr|en] [başlık]"
allowed-tools: Read, Write, Glob, Grep, Task
disable-model-invocation: false
---

# RELATIO — Akademik Rapor

Flagship protokolü `RELATIO` moduyla çalıştır. RELATIO **daima başka bir modun üstüne biner**;
tek başına araştırma yapmaz, biriken bulguyu yazıya döker.

## Zorunlu yükleme

```
view ../historia-medicinae/references/report-template.md
view ../historia-medicinae/references/citation-and-transliteration.md
view ../../shared/composition-contract.md
```

## Dil

`report_language` (userConfig veya `.claude/historia-medicinae.local.md`) ile belirlenir.
**İkisi de yoksa kullanıcıya sor** — varsayma.

## İki katman

- **Katman A (görünür):** bitmiş akademik makale. Araç adı, connector, MCP, mod kodu, çağrı
  sayısı, kapsam manifestosu **gövdeye giremez**. Yöntem bölümü yalnız kamuya açık veritabanı ve
  arşiv adlarını anar.
- **Katman B/C (görünmez):** `<!-- VIZ: … -->` ve `<!-- OPS: … -->` — G0 manifestosu, arama
  günlüğü, gap listesi burada yaşar.

## Beş zorunlu unsur

1. Kronoloji şeridi (konu bir süreçse) — grafik öncesi `dataviz` skill'i okunur.
2. Kaynak envanteri tablosu (kurum · seri · kapsam · erişim durumu).
3. **Sınırlılıklar bölümü boş bırakılamaz** — en az kaynak boşluğu + dijitalleştirme/OCR kısıtı.
4. Retro-hipotez beyanı (modern tanı etiketi geçtiyse).
5. Çift tarih (Miladî olmayan her tarihte).

## Teslim zinciri

1. Temiz-kopya `.md` üret.
2. **`sci-audit`** çağır (atıf-adli + iddia temellendirme + Türkçe dil). Kurulu değilse
   "bağımsız denetim yapılmadı" olarak **çıktıda beyan et**.
3. Dosya raporu → **`carbon-html-report`**; istatistik/tablo ağırlıklıysa →
   **`carbon-quarto-scientific`**.

## Değişmez

Tanımlayıcı uydurulmaz. Pre-DOI monograf **bibliyografik künyeyle** atıflanır — sahte DOI,
eksik künyeden kötüdür.
