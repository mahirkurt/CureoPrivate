# Vector Conversion — Raster → Production-Grade SVG

> **Bu dosya `brand-visual` skill'inin Adım 5 kapsamında, AI-generated logo (raster) → production SVG geçişi için yüklenen referansıdır.**
>
> AI image generation (Midjourney, Niji, Flux, DALL-E) **raster (PNG)** üretir. Production logo **vector (SVG)** olmalıdır. Bu döşemeyi atlamak amatörlüktür ve markaya zarar verir.

---

## Felsefi Temel

> "AI bir tasarımcının yerini almaz. AI'ın çıktısı bir **brief**'tir, bir teslim değil. Production logo her zaman **insan-finalized**'dır." — brand-visual doktrini

AI çıktısının raster olarak kullanılması üç sorun yaratır:
1. **Ölçeklenebilirlik kaybı**: 1024×1024 PNG, billboard'da pixelleşir; favicon'da bulanıklaşır.
2. **Trademark zayıflığı**: Vector dosyası olmayan marka, USPTO/EUIPO tescilinde "production-grade representation" eksikliği nedeniyle reddedilebilir.
3. **Telif belirsizliği**: AI-generated raster ABD telif sisteminde korunmuyor (Şubat 2024 USCO ruling). Vector rebuild + significant human modification = telif altına girer.

Bu nedenle **her brand-visual çıktısı**, Adım 5'in kapanışında "vector rebuild required" notunu içermek zorundadır.

---

## Üç Yol: Otomatik / Hibrit / Manuel

### Yol 1: Otomatik Trace (Hızlı, Düşük Kalite)
**Araçlar**: VTracer, Vectorizer.AI, Vector Magic, Inkscape Trace Bitmap, Potrace
**Süre**: 5-30 saniye
**Kalite**: Bağımlı; basit semboller için kabul edilebilir, kompleks işler için yetersiz
**Kullanım**: Hızlı moodboard veya draft sunum için

### Yol 2: Hibrit (Otomatik + Manuel Cleanup) — **ÖNERİLEN**
**Araçlar**: VTracer ile otomatik trace + Adobe Illustrator/Figma'da manuel cleanup
**Süre**: 1-3 saat (trace + cleanup)
**Kalite**: Production-grade'e yakın
**Kullanım**: Çoğu marka projesi için optimal denge

### Yol 3: Tam Manuel Rebuild (Highest Quality)
**Araçlar**: Adobe Illustrator (Pen Tool) veya Figma (Vector Tool)
**Süre**: 2-8 saat (kompleks işler için 1+ gün)
**Kalite**: Pentagram-grade
**Kullanım**: Lüks markalar, kurumsal rebrand'lar, multi-million budget projeleri

---

## Otomatik Trace Tools — Karşılaştırmalı

### VTracer (visioncortex/vtracer) — **Önerilen Default**
- **Lisans**: MIT (open source, free)
- **Algoritma**: O(n) — Adobe Illustrator'ın O(n²) Image Trace'inden hızlı
- **Renk modu**: Color (full) + Binary (B/W)
- **Stacked vs Cutout**: Stacked default — paths üst üste yığılır, hole oluşturmaz; Adobe'dan **30-70% daha küçük SVG**
- **Çıktı modu**: pixel / polygon / spline (curves)
- **Python API**: `pip install vtracer`
- **CLI binary**: `cargo install vtracer`
- **Logo için ideal**: Evet — `--mode spline --hierarchical stacked --color_precision 6`

```bash
# Color logo
vtracer --input logo.png --output logo.svg \
        --mode spline --hierarchical stacked \
        --color_precision 6 --filter_speckle 4 \
        --corner_threshold 60 --segment_length 4

# Monochrome logo
vtracer --input logo.png --output logo.svg \
        --colormode binary --mode polygon \
        --corner_threshold 90 --filter_speckle 4
```

> brand-visual skill'inin `scripts/vector_trace.py` script'i VTracer'ı default backend olarak kullanır ve preset-driven workflow sunar.

### Vectorizer.AI (vectorizer.ai)
- **Lisans**: Ticari SaaS (~$10/ay)
- **Algoritma**: AI-assisted (deep learning trace)
- **Güçlü yönler**: Sub-pixel precision, palette adaptive, en iyi otomatik kalite (2026 itibarıyla)
- **Zayıf yönler**: Cloud-only, batch için pahalı, gizlilik (yüklediğiniz logo onlara gider)
- **Logo için ideal**: Tek seferlik premium projeler için
- **Tariff**: Free tier 2 image/day; Pro $9.99/month sınırsız

### Vector Magic (vectormagic.com)
- **Lisans**: Ticari SaaS / Desktop ($295 one-time)
- **Algoritma**: Klasik trace + manual hint system
- **Güçlü yönler**: Palette control, manuel hint sistemi
- **Zayıf yönler**: 2.4/5 Trustpilot rating (2026), no batch, eski UI
- **Logo için ideal**: Eskiden gold standard, şimdi Vectorizer.AI'a kaybetmiş

### Adobe Illustrator Image Trace
- **Lisans**: Creative Cloud subscription ($23/month)
- **Algoritma**: Klasik bitmap trace
- **Güçlü yönler**: Illustrator workflow'a entegre, post-trace cleanup kolay (Pen Tool ile)
- **Preset'ler**: "High Fidelity Photo", "Low Fidelity Photo", "3 Colors", "6 Colors", "16 Colors", "Black and White Logo", "Sketched Art", "Line Art", "Technical Drawing"
- **Logo için ideal**: "Black and White Logo" preset (mono), "6 Colors" (color), sonra **Object > Image Trace > Expand** + **Object > Path > Simplify**
- **Önerilen ayar**: Threshold 128 (B/W), Paths 50-80, Corners 50-75, Noise 10-25

### Inkscape Trace Bitmap
- **Lisans**: GPL (free)
- **Algoritma**: Potrace (B/W) + Color Quantization
- **Güçlü yönler**: Free, system-installable, batch via CLI
- **Zayıf yönler**: UI dated, color quality Inkscape Image Trace'in altında
- **CLI**: `inkscape --actions="trace-bitmap-brightness;export-do" file.png`

### Potrace
- **Lisans**: GPL (free)
- **Algoritma**: O(n²), klasik 1996+ trace
- **Renk modu**: Sadece B/W (monokrom)
- **Logo için ideal**: Saf monogram, tek-renk silüet logoları
- **CLI**: `potrace -s -o logo.svg logo.pbm` (PBM input gerekli; ImageMagick ile preprocess)
- **Parametre**: `--turdsize 8 --alphamax 1.0` (logo için temizlik)

### StarVector (2024 academic, 2025 production-ready)
- **Lisans**: Apache 2.0 (open source, model weights ayrı)
- **Algoritma**: 8B parameter foundation model, görsel→SVG code generation
- **Güçlü yönler**: SVG primitive kullanımı (rect/circle/path), VTracer'dan **~5x daha kompakt**
- **Zayıf yönler**: GPU gerek (8GB VRAM), inference yavaş
- **Logo için ideal**: 2026'nın bleeding edge'i; production hâlâ deneysel

---

## Hibrit Workflow (Önerilen) — Adım Adım

### 1. Auto-trace ile başla
```bash
python scripts/vector_trace.py logo-from-midjourney.png \
    --output logo-traced.svg \
    --backend vtracer \
    --preset logo-color
```

### 2. SVGO ile optimize et
```bash
npx svgo logo-traced.svg --multipass --pretty
# Veya online: https://jakearchibald.github.io/svgomg/
```

SVGO ne yapar:
- Gereksiz attribute'ları siler
- Düğüm sayısını minimize eder
- Decimal precision'ı azaltır
- Boş `<g>` gruplarını kaldırır
- Inline style'ları class'a çevirir

### 3. Adobe Illustrator / Figma'da aç
- **Anchor point optimizasyonu**: Pen Tool ile düğümleri manuel düzenle
- **Optical alignment**: Geometric centering = optical centering değil; ince ayarlar
- **Stroke vs Fill**: Auto-trace fill üretir; stroke gerekirse `Object > Path > Outline Stroke` reverse
- **Boolean operations**: `Pathfinder > Unite/Minus Front` ile path birleştir
- **Color cleanup**: Auto-trace 6 renk üretebilir, manuel olarak 2'ye indir

### 4. Brand-grade kontrol checklist
- [ ] Tüm path'lar pixel grid'e align (no half-pixel düğümler)
- [ ] Symmetric form symmetric mi (manuel ölçü kontrol)
- [ ] Optical compensation uygulandı mı? (O harfi x-height +2%)
- [ ] Stroke weight uniform mi (variable weight istemiyorsanız)
- [ ] Gereksiz anchor points elendi mi?
- [ ] Figma/Illustrator export'tan sonra SVGO ikinci pass

### 5. Final delivery
- **Master SVG**: 1024×1024 viewBox, pixel-perfect
- **PNG fallback'lar**: 16/32/64/128/192/256/512/1024 (favicon_simulator.py kullan)
- **PDF vector**: Adobe Illustrator'dan "Save As PDF (Press Quality)" — print için
- **EPS**: Legacy print providers için (Illustrator export)
- **AI source**: Adobe Illustrator native dosyası (.ai) — designer'lara hand-off

---

## Manual Rebuild Workflow (Premium Projeler)

### Pen Tool Discipline
- **Anchor minimization**: Bir Bezier curve, **3 anchor**'la modellenebiliyorsa 5 kullanma
- **Smooth vs Corner**: Smooth = gradual transition; Corner = sharp angle
- **Handle length**: Eşit handle uzunlukları = circular curves; asimetrik = organic curves
- **Tangent alignment**: Smooth anchor'lar için handle'lar tam karşı-yönde

### Geometric Construction
- **Grid system**: 8×8 modular grid (most logos), 12×12 (kompleks), 60° hex grid (organic)
- **Golden ratio**: 1.618 — major dimensions; tüm Apple logos, Twitter eski bird, Pepsi 2008+
- **Optical center**: Geometric center'ın **+3% yukarısı** = optical center (gözün rahat ettiği yer)

### Stroke Optimization
- **Single weight**: Modern logo doktrini (Sagi Haviv, modernist tradition)
- **Variable weight**: Klasik / luxury / heritage hissi (Gucci, Hermès tarzı)
- **Stroke caps**: round / square / butt — round = soft, square = neutral, butt = teknik
- **Stroke join**: round / mitre / bevel

---

## Trademark ve Telif Notları

### AI Output → Telif Sahipliği
**ABD durumu (Şubat 2024 USCO ruling)**: Pure AI-generated content **telif altında değildir**. Significant human modification gerekli.

**"Significant" tanımı (USCO guidance)**:
- ≥50% çıktıyı insan tarafından modify etmek
- Compositional kararlar (positioning, color, typography) insanın
- "Pencil and pixel" — AI prompt yetersiz; manuel rebuild yeterli

**Pratik tavsiye**: AI auto-trace + Illustrator manual rebuild = telif altına alınabilir. Sadece auto-trace'le yetinmeyin.

### Trademark Tescil için Vector
**USPTO**: Drawing must be in "high-quality format" — vector (SVG, EPS, PDF) önerilir. Raster JPG kabul edilse de **rejection riski yüksek**.

**EUIPO**: Vector EPS tercih edilir. Color profile (sRGB veya CMYK) belirtilmesi önerilir.

**TÜRKPATENT**: PDF veya yüksek-rezolüsyon JPG (300 DPI minimum). Vector zorunlu değil ama önerilir.

---

## Sektör-Spesifik Pratikleri

| Sektör | Tercih Edilen Vector Yaklaşım | Neden |
|--------|--------------------------------|-------|
| **Lüks/Fashion** | Tam manuel rebuild | Letterform precision kritik (Chanel CC kerning, YSL ligature) |
| **Tech/SaaS** | Hibrit (auto-trace + cleanup) | Hız + kalite dengesi; rebrand sıklığı yüksek |
| **B2B/Enterprise** | Hibrit veya tam manuel | Multi-application consistency için clean SVG şart |
| **Healthcare/Pharma** | Hibrit + regulatory review | TİTCK/FDA submission için "production-grade representation" gerekli |
| **Restaurant/F&B** | Hibrit (auto-trace + minor cleanup) | Menu/packaging için yeterli kalite, hız öncelik |
| **Local/Small Business** | Pure auto-trace + SVGO | Bütçe kısıtı, basit semboller için yeterli |

---

## Otomatik Workflow Komut Şablonu

`brand-visual` skill, Adım 5'in sonunda kullanıcıya bu komutu önerir:

```bash
# 1. AI'dan en iyi raster çıktıyı seçin (en yüksek resolution)
mv ~/Downloads/midjourney-best-variant.png ./logo-source.png

# 2. brand-visual'ın trace script'ini çalıştırın
python /path/to/brand-visual/scripts/vector_trace.py logo-source.png \
    --output logo-traced.svg \
    --preset logo-color  # veya logo-mono, bw-clean, sketch

# 3. SVGO ile optimize edin (npx ile, kurmadan)
npx svgo logo-traced.svg --output logo-optimized.svg --multipass --pretty

# 4. Favicon test paketi üretin
python /path/to/brand-visual/scripts/favicon_simulator.py logo-optimized.svg \
    --output-dir ./favicon-bundle

# 5. Pantone match için
python /path/to/brand-visual/scripts/pantone_matcher.py "#5B5BD6" \
    --top 3 --include-cmyk --format markdown > pantone-spec.md

# 6. (OPSIYONEL ama önerilen) Manuel cleanup için Adobe Illustrator
# veya Figma'da açın; anchor optimization + optical alignment yapın
open -a "Adobe Illustrator" logo-optimized.svg
```

---

## Kalite Doğrulama Checklist

Vector logo production'a vermeden önce:

### Teknik
- [ ] SVG file size < 10 KB (logo için ideal)
- [ ] Path count ≤ 5 (basit logo) veya ≤ 15 (kompleks logo)
- [ ] viewBox attribute set (responsive scalability için)
- [ ] No raster fallback embedded (`<image href="data:image/png;base64,..."/>` YOK)
- [ ] No inline filters (drop-shadow, blur — modern logo doktrini reddediyor)
- [ ] All paths closed (Z command sona)
- [ ] Color hex codes match brand palette exactly

### Optik
- [ ] 16px favicon test PASS (silhouette tanınır)
- [ ] Monochrome variant çalışır (siyah-on-beyaz + ters)
- [ ] Different background color test (light/dark mode)
- [ ] Print test PDF render (300 DPI bezel-to-bezel)
- [ ] App icon mask test (iOS rounded corner + Android adaptive)

### Yasal
- [ ] AI prompt'ta brand X "in the style of" referansı YOK (trademark safety)
- [ ] Significant human modification belgelendi (timestamp + designer notes)
- [ ] Trademark search ön-tarama yapıldı (USPTO TESS / EUIPO eSearch+ / TÜRKPATENT)
- [ ] Color closeness to existing famous logos check (Pantone Pepsi #DA291C, Coke #F40009 gibi)

---

## Sonuç: brand-visual Doktrini

> AI bir araç, designer bir mimar. Bu skill konsept, sembol metaforu ve sistemic spec üretir.
> Gerçek vector dosyası, **bilgili bir insanın elinden çıkar.** Otomatik trace bir başlangıç noktası,
> bir teslim değil.

`scripts/vector_trace.py` bu yolu kolaylaştırır ama sondan başa kadar otomasyon sunmaz.
**Skill'in çıktısı her zaman "designer cleanup required" notunu içermek zorundadır.**
