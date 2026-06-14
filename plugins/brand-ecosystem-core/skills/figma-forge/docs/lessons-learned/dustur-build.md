# Lessons Learned — Düstur Build (2026-05-26)

**Bundle:** dustur-figma-library v1.0.0  
**Source:** [mahirkurt/Dustur v1.2.0](https://github.com/mahirkurt/Dustur)  
**Generator:** figma-forge v0.2.1  
**Outcome:** Pre-publish lint 9/9 PASS, 102 dosya, 231 token, 339 component variant, 17 pattern, 74 icon, 17 Code Connect mapping.

Bu doküman, Düstur Tasarım Sistemi'ni figma-forge ile Figma kütüphanesi mimarisine dönüştürme sürecinde **karşılaşılan friksiyon noktalarını, çözüm yollarını ve bu çözümlerin gelecekteki roadmap milestone'larına dönüştürülmesini** sistematikleştirir. Lessons-learned methodology, ISO/IEC/IEEE 16085:2021 (Risk Management) ve PMI's "Lessons Learned Knowledge Base" çerçevesini izler.

---

## L1 — Alias Path Hierarchy Mismatch

### Bulgu

DTCG primitive ve semantic token dosyaları ayrı maintain edildiğinde (Düstur'da olduğu gibi: `primitives/color.json` + `semantic/tier.json`), merge sırasında alias path'leri farklı hierarchy seviyelerinde tanımlanır. Düstur'da `tier.json` içindeki referans `{tbk.9}` formundayken, merged DTCG'de aynı token `color.tbk.9` path'ine yerleşir.

İlk merge denemesinde **89 unresolved alias warning** üretildi (`dtcg_to_variables.py` çıktısı).

### Çözüm

Manual `rewrite_aliases()` helper yazıldı — color family adlarını ve semantic grupları regex ile tanıyıp `{tbk.9}` → `{color.tbk.9}` dönüşümü yapan ad-hoc bir Python script.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | Auto-remediation: G13 (token alias resolve) gate fail → otomatik path rewriter PR/script önerisi |
| **v0.4.0** | Built-in DTCG normalizer in `tokens_import` mode — flat vs nested input formatları için tek API |

**Etki büyüklüğü:** Her DTCG merge işleminde ortaya çıkan klasik bir sorun. ~89/231 token = **%38.5 alias rewrite gerekti** Düstur'da. Production-grade kütüphanelerde bu rakam çoğunlukla %25-50 aralığında.

---

## L2 — Composite Typography Tokens vs Figma Variables

### Bulgu

Figma Variables API, **composite type** (`$type: typography` veya `$type: border`) tokenlerini desteklemez — sadece atomic değerler (color, dimension, number, string, boolean). Düstur'un `semantic/typography.json` dosyası 12 composite role tanımlıyor (`display`, `section`, `body`, `code`, ...). Bunlar Variables'a değil **Text Styles** olarak yüklenmelidir.

### Çözüm

Merge işleminde composite tokenleri ayrı `dustur.text-styles.json` dosyasına çıkardık. Figma Plugin Channel 3 ile Text Style olarak yüklenmek üzere bekletildi.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | `tokens_import` mode'una composite detection: composite tipler otomatik `text-styles.json`'a route'lanır + uyarı verir |
| **v0.4.0** | Plugin Channel ile Text Style auto-import pipeline (Variables ve Text Styles tek komutla) |

**Etki büyüklüğü:** Düstur'da 12 composite role. Carbon/Material-3 baz'lı sistemlerde tipik olarak 8-15 composite typography role bulunur.

---

## L3 — Multi-File Library Architecture Coordination

### Bulgu

4 dosyalı kütüphane mimarisi (Foundations + Components + Patterns + Icons) cross-file consume zincirini gerektiriyor: Components Foundations'u tüketir, Patterns hem Foundations hem Components'i. `publish_order` zorunlu — yanlış sıra publish_audit'in G16/G18 gate'lerini fail eder.

### Çözüm

`library-registry.json`'a explicit `publish_order` ve her dosya için `expected_pages` array'i ekledik. publish_audit v0.2.0 zaten multi-file support kazanmıştı; v0.2.1 calibration ile stabilize oldu.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.2.x** | ✅ Tamamlandı (v0.2.0 multi-file context, v0.2.1 calibration) |
| **v0.3.1** | Diff mode: iki publish_audit raporu arasındaki delta — yeni page eklendi mi, var olan page silindi mi, modifiye edildi mi? |

---

## L4 — Static Pre-Publish Lint Gap

### Bulgu

Live Figma file_key olmadan da bundle bütünlüğü doğrulanabiliyor: JSON validity, primitive token count, alias resolvability, component spec schema, pattern→component referans tutarlılığı, SVG validity, Code Connect tamlık, manifest envanteri, accessibility coverage. Bu **canlı Figma sunucusuna bağlanmaya gerek olmadan** çalışan 9 kontrol.

publish_audit v0.2.1'in tüm 19 gate'i (G1-G19) **live Figma context** gerektiriyor (FigmaFile + REST payload). Static-only bir mode yok.

### Çözüm

Düstur için tek seferlik static lint script'i yazdık (9 check). Bu pattern bir CLI mode'a dönüşmeli.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | `publish_audit.py --static-only` veya yeni komut `figma-forge pre-publish-lint` — 9 static check |
| **v0.3.1** | Static + dynamic lint sonuçlarını birleştiren unified report formatı |

**Stratejik fayda:** CI/CD pipeline'larında Figma PAT olmadan da kalite kontrolü → developer-experience iyileşmesi.

---

## L5 — Component Variant Count Auto-Calculation

### Bulgu

Component spec'lerinde `variants.expected_count` manüel doldurulmak zorunda. Düstur'da 17 component için Cartesian product hesaplaması ad-hoc yapıldı:

```python
n = 1
for axis_values in c["variants"].values():
    n *= len(axis_values)
```

`disabled_combinations` alanı varsa bu da çıkarılmalı.

Yüzey Badge: 7 tier × 3 variant × 3 size = **63** (doğrulandı).

### Çözüm

İçeride 17 component için döngü ile hesapladık. publish_audit G7 gate'i bu sayıyı live Figma'dan doğrulamak için kullanıyor ama spec'i değil.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | `components-build` mode'unda spec'ten variant matrisi otomatik hesaplama. Spec'te `expected_count` opsiyonel hale getir; hesap yanlışsa flag at |
| **v0.3.0** | Auto-remediation: G7 fail → spec patch önerisi |

---

## L6 — Icon SVG Canonical Adaptation

### Bulgu

74 ikondan **48'i generic UI** (navigation, action, status, document general, mobile). Bunları sıfırdan çizmek pratik değil — Tabler Icons (MIT, 5,200+ ikon) referans kütüphane olarak kullanıldı. Adaptasyon protokolü yazıldı:

- Stroke 2px → 1.5px
- stroke-linecap: round
- viewBox: 24×24
- Türkçe `<title>` tag eklemesi (a11y)
- `currentColor` kullanımı

### Çözüm

`docs/icon-strategy.md` dokumanı ve ad-hoc bir post-processor önerisi (uygulanmamış).

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | `icons-build` mode'una `--tabler-adapter` veya `--lucide-adapter` opsiyonu. Otomatik stroke + title + viewBox normalize |
| **v0.4.0** | İkonkit-3 referansları (Heroicons, Feather, Material Symbols, Phosphor) için adapter genişlemesi |

---

## L7 — Bundle Manifest with SHA-256 Hashes

### Bulgu

Bundle teslim edilirken her dosyanın **SHA-256 hash**'i ve envanteri (kategorize) production-grade güvenlik gerektirir (supply-chain integrity, reproducible builds). figma-forge'da bu komut yok; ad-hoc Python ile üretildi.

### Çözüm

Düstur için custom `manifest.json` üretimi. 102 dosya × 64-byte hash.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | Yeni komut: `figma-forge bundle-manifest --library-dir <dir> --output manifest.json` |
| **v1.0.0** | Sigstore/Cosign entegrasyonu (cryptographic attestation) — opsiyonel imzalama |

---

## L8 — Orchestration Pipeline Manifest

### Bulgu

9-stage pipeline manuel olarak `orchestration.json`'a yazıldı. Her stage için: command, outputs, estimated_time, prerequisite. Bu kullanıcının "tek komut" çalıştırması için temel.

### Çözüm

Düstur için custom orchestration manifest. `figma-forge orchestrate --manifest orchestration.json` komutu **yok** (henüz).

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | Yeni komut: `figma-forge orchestrate --manifest orchestration.json [--dry-run]` |
| **v0.3.1** | Resume from last failed stage (`--resume`) |

---

## L9 — Code Connect Mapping Templates

### Bulgu

17 component için React + Web Components + CSS class şablonları **manuel** üretildi. Çoğunlukla aynı boilerplate. figma-forge'da `templates/code-connect/` dizini var ama Düstur build sürecinde kullanılmadı (yapısı keşfedilmeden bypass edildi).

### Çözüm

Ad-hoc Python loop ile 16 mapping üretildi (1'i manuel).

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.0** | `code-connect` mode otomatik template doldurma — component spec'inden React/WC/CSS örnekleri türetme |
| **v0.3.0** | Auto-remediation: G17 (code-connect badges) fail → eksik mapping JSON'ları auto-generate |

---

## L10 — Heuristic Gate Calibration Insight

### Bulgu

v0.2.1'de calibration framework (G7/G13/G14/G15) tanıtıldı — heuristic eşiklerin ne kadar isabetli çalıştığını boundary-decision histogramı ile kaydeder. Düstur build'inde bu data toplanmadı (live audit yapılmadı). Bu eksiklik diff-mode'da regression tracking için kritik.

### Çözüm

Düstur için sadece static lint koştu. v0.3.1'de canlı çalıştırma + diff için altyapı hazır olmalı.

### Roadmap İçeriği

| Sürüm | Eylem |
|-------|-------|
| **v0.3.1** | Diff mode: iki calibration report arası delta. Hangi gate'in eşiği şu yöne kayıyor? |
| **v1.0.0** | Calibration data anonymize + community sharing protocol — 3rd-party kütüphanelerden feedback loop |

---

## Roadmap Özet Tablosu

| Lesson | Etki | v0.3.0 | v0.3.1 | v0.4.0 | v1.0.0 |
|--------|------|:------:|:------:|:------:|:------:|
| L1 — Alias path mismatch | %38.5 token | 🟢 | | 🟡 | |
| L2 — Composite typography | 12 role | 🟢 | | 🟢 | |
| L3 — Multi-file coordination | 4 file | ✅ (v0.2) | 🟢 | | |
| L4 — Static pre-publish lint | 9 check | 🟢 | 🟡 | | |
| L5 — Variant count auto-calc | 339 variant | 🟢 | | | |
| L6 — Icon SVG adapter | 48 icon | 🟢 | | 🟢 | |
| L7 — Bundle manifest | 102 file | 🟢 | | | 🟡 |
| L8 — Orchestration pipeline | 9 stage | 🟢 | 🟢 | | |
| L9 — Code Connect templates | 17 mapping | 🟢 | | | |
| L10 — Calibration delta | 4 gate | | 🟢 | | 🟢 |

🟢 = Yeni özellik / 🟡 = Yan etki iyileştirmesi / ✅ = Önceki sürümde tamamlandı

---

## Metrikler

**Düstur build sırasında:**
- Toplam manual Python helper kodu: ~250 satır (ad-hoc rewriter, manifest, lint, ZIP)
- Toplam figma-forge çağrı: 1 (sadece `dtcg_to_variables.py`)
- Otomasyon oranı: ~%10 (build sürecinin %90'ı manuel)

**v0.3.0 hedef:**
- Otomasyon oranı: %70+ (auto-remediation + pre-publish lint + orchestrate komutları)
- Manuel kod yazma ihtiyacı: <50 satır

**v1.0.0 hedef:**
- Otomasyon oranı: %95+
- Plugin ecosystem: 3+ third-party gate / strategy katkısı
- Anonymized calibration corpus: 10+ DS

---

*Bu doküman, Düstur Tasarım Sistemi'ni Figma kütüphanesine dönüştürme sürecinde toplanan friksiyon noktalarının sistematik analizini sunar. Roadmap'in **lived-experience driven** olduğunu doğrular — özelliklerin sentetik kullanım senaryolarından değil, gerçek production build'in ortaya çıkardığı ihtiyaçlardan türetildiğini belgeler.*
