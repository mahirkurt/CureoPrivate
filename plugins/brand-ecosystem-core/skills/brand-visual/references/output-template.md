# Output Template — Brand Identity System Report

> **Bu dosya `brand-visual` skill'inin Adım 5'in çıktı formatıdır.**
> Markdown formatında, agency-grade bir teslimat. Mock-ups yok — bunlar bir tasarım stüdyosunun Figma'da üreteceği şeyler için brief'tir.

---

## TEMPLATE — TAM ŞABLON

```markdown
# [Marka Adı] — Visual Identity System
*v1.0 · [tarih] · brand-visual protocol*

---

## 1. Executive Summary

[Marka Adı], **[arketip]** arketipi üzerine kurulmuş bir **[stratejik çıpa]** vaadi
sunan bir **[sektör]** markasıdır. Bu kimlik sistemi, [seçilen route — Tipografik /
Geometric / Radical Differentiation] yolunu izleyerek [büyük fikir tek cümle]
prensibine dayanır.

Sistem, **[X] core color**, **[Y] type family**, ve **[Z element design tokens]**
üzerine inşa edilmiş; **light + dark mode** desteği, **WCAG AA** erişilebilirlik
uyumu, ve **16px favicon-grade scalability** doğrulaması ile production-ready'dir.

**Stratejik vaat tek cümle**: [...]

---

## 2. Brand Strategy Anchor

### 2.1 Marka Arketipi
**[Arketip adı]** — [Jung'tan Pearson & Mark adaptasyonu]

[Arketip'in 100 kelime tanımı + bu marka için neden]

> **Görsel dile çevirisi**: [Bu arketip nasıl görsel form alır — geometri, palet,
> tipografi, hareket dilinde]

### 2.2 Stratejik Çıpa
Markanın zihinde sahiplenmek istediği **tek kelime**: **[kelime]**

[100 kelimelik açılım — çıpanın kategori-merdiveni içindeki yerini açıkla, rakip
kelime haritası]

### 2.3 Hedef Kitle Görsel Sözlüğü
[Persona — alt kültür, beğeni evreni, görsel referans dünyası]

### 2.4 Marka Kişiliği Boyutları (Aaker'dan)
| Boyut | Skor (1-10) | Görsel Karşılığı |
|-------|-------------|-------------------|
| Sincerity | X | Sıcak palette / yumuşak köşeler |
| Excitement | X | Cesur renk / dinamik form |
| Competence | X | Düz / sistemik / izleyebilir grid |
| Sophistication | X | Lüks tipografi / kısıtlı palette |
| Ruggedness | X | Keskin köşe / kontrast |

---

## 3. Logomark Specification

### 3.1 Seçilen Konsept

**Route**: [1 / 2 / 3 / Hibrit]
**Büyük Fikir**: [tek cümle]
**Soyutlanan kavram**: [...]

### 3.2 AI-Generated Reference

> **Not**: Bu sembol AI ile üretilmiş **kavram referansıdır**. Production-grade kullanım için bir vector designer tarafından **manuel rebuild** edilmesi gereklidir (Adobe Illustrator, Figma).

**Seçilen variant**: [Variant A / B / C — Adım 4'ten]
**Final prompt**: [...]
**Generation tool**: [Midjourney V7 / Niji 7 / Flux / DALL-E 3]
**Iteration count**: [3-5]

### 3.3 Grid ve Construction

[Mental sketch / vector ölçü logic'i:]
- **Base grid**: [örn: 8×8 modular grid / golden ratio rect / 60° hexagonal]
- **Optical compensation**: [örn: O harfi x-height'tan +2% büyük tutuldu]
- **Stroke weight**: [örn: tek-weight 2pt; veya çift-weight contrast 1:3]
- **Corner radius**: [örn: 0 sharp / 2pt soft / fillet across entire form]

```
[ASCII grid / şematik gösterim]

   ┌───────────────┐
   │       ╱╲      │  Base grid: 8×8
   │      ╱  ╲     │  Center anchor: (4, 4)
   │     ╱    ╲    │  Stroke: 1u
   │    ╱      ╲   │
   │   ╱________╲  │
   └───────────────┘
```

### 3.4 Clear Space Rule

Marka çevresinde **minimum boş alan**: logonun **x-height kadarı** her yönden.

```
┌─x─────────────x─┐
│                 │
x   [ LOGOMARK ]  x
│                 │
└─x─────────────x─┘
```

### 3.5 Minimum Size

| Medium | Minimum Size |
|--------|-------------|
| Print | 8mm yükseklik |
| Web (raster) | 24px yükseklik |
| Web (vector SVG) | 16px favicon (test edilmiş) |
| App icon | 1024×1024 master (iOS) / 512×512 master (Android) |

### 3.6 Color Variations

| Variation | Use | Specification |
|-----------|-----|---------------|
| Primary | Default | [Color 1] on [Background] |
| Reversed | Dark backgrounds | White on [Color 1 Step 9] |
| Monochrome positive | Print, fax, embossing | 100% [Color 1 Step 12] on white |
| Monochrome reversed | Single-color overlay | 100% White on [Color 1 Step 12] |
| Transparent watermark | Document watermarks | 30% opacity [Color 1] on background |

---

## 4. Color System (Radix-Style 12-Step)

> **Felsefe**: Renk paleti rastgele HEX kodları değil, **matematiksel olarak hesaplanmış 12-step sistemdir**. Her step belirli bir UI use-case için tasarlanır. Light ve dark mode arasında **otomatik invert + chroma adjustment** uygulanır.

### 4.1 Primary Brand Color

**HEX**: [#XXXXXX] **OKLCH**: oklch(L C H) **HSL**: hsl(H S% L%)

**Seçim rasyoneli**: [Renk teorisi + nöro-psikoloji + sektör konteksti — 100 kelime]

**Color name**: [Brand verir bir isim — örn: "Curio Indigo", "Lumora Coral"]

### 4.2 Light Mode Scale (1–12)

| Step | HEX | Use Case | APCA Lc vs. Step 1 |
|------|-----|----------|-------------------|
| 1 | #FCFCFD | App background | — |
| 2 | #F9F9FB | Subtle background | — |
| 3 | #EEEEF0 | UI element bg (default state) | — |
| 4 | #E0E0E5 | UI element bg (hover) | — |
| 5 | #D0D0D6 | UI element bg (pressed/selected) | — |
| 6 | #B9B9C2 | Subtle border (non-interactive) | — |
| 7 | #A0A0AB | Subtle border (interactive) | — |
| 8 | #8484A0 | Strong border / focus ring | — |
| 9 | #5B5BD6 | **Solid action (PRIMARY BRAND)** | — |
| 10 | #4F4FB8 | Solid hover | — |
| 11 | #4747B5 | Low-contrast text | Lc 60 (AA) |
| 12 | #2E2E80 | High-contrast text | Lc 90 (AAA) |

### 4.3 Dark Mode Scale (1–12)

| Step | HEX | Use Case |
|------|-----|----------|
| 1 | #0D0D0F | App background |
| 2 | #131319 | Subtle background |
| ... | ... | ... |
| 9 | #6E56CF | Solid action (PRIMARY BRAND, brightened) |
| ... | ... | ... |
| 12 | #E2E2FC | High-contrast text |

> **Kural**: Step numarası light/dark arasında **aynı semantik amacı** tutar. `--brand-9` her iki temada **primary action color**'dur.

### 4.4 Accent Color (Tamamlayıcı)

**HEX**: [#YYYYYY] — [renk adı: örn: "Curio Sun"]
**Seçim rasyoneli**: Primary'nin tamamlayıcısı (60-30-10 paleti içinde 30%)

[Aynı 12-step tablo accent için]

### 4.5 Gray Pairing

Marka primary'sine optimal gray scale: **[Slate / Mauve / Sage / Olive / Sand]**

> Radix mantığı: cool brand color → cool gray (Slate); warm brand color → warm gray (Sand); purple brand → mauve; green brand → sage; yellow brand → olive.

[Gray 12-step tablo light + dark]

### 4.6 Functional Colors (Semantic)

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--success-9` | #46A758 | #4CC367 | Success state |
| `--error-9` | #E5484D | #FF6369 | Error state |
| `--warning-9` | #F1A10D | #FFB224 | Warning state |
| `--info-9` | [primary 9] | [primary 9 dark] | Info — primary'den yan kullanım |

### 4.7 60-30-10 Palet Reçetesi

- **60%** dominant: `--gray-2` (background)
- **30%** secondary: `--gray-12` (text) + `--gray-6` (borders)
- **10%** accent: `--brand-9` (primary actions, key highlights)

---

## 5. Typography System

> **Felsefe**: Modern markalar **variable font** ile 1 dosyada tüm ağırlıkları taşır. Bu sistem **Display** + **Body** + opsiyonel **Mono** üçlüsü üzerine kurulur.

### 5.1 Display Font (Marka adı, başlıklar, hero)

**Family**: [Inter Display Variable / Söhne / Manrope / General Sans / Geist / Plus Jakarta Sans / Cabinet Grotesk]

| Property | Value |
|----------|-------|
| **Source** | Google Fonts / Adobe Fonts / [commercial] |
| **License** | OFL / SIL / Commercial seat-based |
| **Variable axes** | weight (100–900), opsz (10–60), italic 0/1 |
| **x-height** | High (modern screen optimization) / Medium / Low |
| **Style attributes** | Geometric / Humanist / Grotesque / Neo-grotesque |
| **Default weight (logotype)** | 600–700 |
| **Default weight (display)** | 500–700 |

**Source URL**: [https://fonts.google.com/specimen/...]

**Logotype lock-up specification**:
```
[Marka Adı]
- Font: [...]
- Weight: 600
- Tracking (letter-spacing): -20 to -30 (tight, premium feel)
- Custom kerning pairs: [(F,a: -25), (T,h: -10)]
- Optical size: 30-40 (display optimized)
```

### 5.2 Body Font (UI, body text)

**Family**: [Inter Variable / IBM Plex Sans / Geist Sans / Söhne]

| Property | Value |
|----------|-------|
| **Source** | Google Fonts / system |
| **System fallback** | `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` |
| **Default weight** | 400 (body), 500 (medium emphasis), 600 (strong) |
| **Line-height** | 1.5 (body), 1.2 (headings) |

### 5.3 Mono Font (opsiyonel — code, technical)

**Family**: [JetBrains Mono / Geist Mono / IBM Plex Mono]

### 5.4 Type Scale (Modular)

**Ratio**: 1.250 (Major Third) — uyumlu ve okunabilir

| Step | Size | Use |
|------|------|-----|
| -2 | 0.64rem (10.24px) | Caption, metadata |
| -1 | 0.8rem (12.8px) | Small text, labels |
| 0 | 1rem (16px) | Body text default |
| 1 | 1.25rem (20px) | Lead paragraph |
| 2 | 1.5625rem (25px) | Subheading |
| 3 | 1.953rem (31.25px) | H3 |
| 4 | 2.441rem (39px) | H2 |
| 5 | 3.052rem (48.8px) | H1 |
| 6 | 3.815rem (61px) | Display large |

### 5.5 Font Pairing Rasyoneli

[Display + Body kombinasyonu **neden**:
- Contrast level (geometric display + humanist body = soft contrast)
- x-height harmony (her ikisi de high x-height = tutarlı renk)
- Variable axes overlap (her ikisi variable = sistemik tutarlılık)]

---

## 6. Design Tokens

### 6.1 CSS Custom Properties

```css
:root {
  /* === Brand Colors (Light Mode) === */
  --brand-1: #FCFCFD;
  --brand-2: #F9F9FB;
  --brand-3: #EEEEF0;
  --brand-4: #E0E0E5;
  --brand-5: #D0D0D6;
  --brand-6: #B9B9C2;
  --brand-7: #A0A0AB;
  --brand-8: #8484A0;
  --brand-9: #5B5BD6;
  --brand-10: #4F4FB8;
  --brand-11: #4747B5;
  --brand-12: #2E2E80;

  /* === Accent Colors === */
  /* ... 12 step accent ... */

  /* === Gray Scale === */
  /* ... 12 step gray ... */

  /* === Functional === */
  --success-9: #46A758;
  --error-9: #E5484D;
  --warning-9: #F1A10D;

  /* === Typography === */
  --font-display: "[Display]", ui-sans-serif, system-ui;
  --font-body: "[Body]", ui-sans-serif, system-ui;
  --font-mono: "[Mono]", ui-monospace, monospace;

  --type-scale-ratio: 1.250;
  --text-xs: 0.64rem;
  --text-sm: 0.8rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.5625rem;
  --text-2xl: 1.953rem;
  --text-3xl: 2.441rem;
  --text-4xl: 3.052rem;
  --text-5xl: 3.815rem;

  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-loose: 1.75;

  /* === Spacing (8pt grid) === */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.5rem;   /* 24px */
  --space-6: 2rem;     /* 32px */
  --space-8: 3rem;     /* 48px */
  --space-10: 4rem;    /* 64px */

  /* === Radii === */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* === Shadows (depth tokens) === */
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* === Motion === */
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --duration-slow: 400ms;
  --easing-standard: cubic-bezier(0.4, 0, 0.2, 1);
}

[data-theme="dark"] {
  --brand-1: #0D0D0F;
  --brand-2: #131319;
  /* ... 1-12 dark scale ... */
  --brand-9: #6E56CF;
  --brand-12: #E2E2FC;

  /* ... rest of dark inverts ... */
}
```

### 6.2 Tailwind Config Snippet

```javascript
// tailwind.config.js
function getColorScale(name) {
  const scale = {};
  for (let i = 1; i <= 12; i++) {
    scale[i] = `var(--${name}-${i})`;
  }
  return scale;
}

module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: getColorScale('brand'),
        accent: getColorScale('accent'),
        gray: getColorScale('gray'),
      },
      fontFamily: {
        display: ['var(--font-display)'],
        sans: ['var(--font-body)'],
        mono: ['var(--font-mono)'],
      },
    },
  },
};
```

### 6.3 JSON Token Export (W3C Design Tokens)

```json
{
  "color": {
    "brand": {
      "1": { "value": "#FCFCFD", "type": "color" },
      "2": { "value": "#F9F9FB", "type": "color" },
      "9": { "value": "#5B5BD6", "type": "color", "description": "Primary brand action" },
      "12": { "value": "#2E2E80", "type": "color", "description": "High contrast text" }
    }
  },
  "typography": {
    "display": {
      "value": {
        "fontFamily": "[Display]",
        "fontSize": "{text-5xl}",
        "fontWeight": "700",
        "lineHeight": "{leading-tight}"
      },
      "type": "typography"
    }
  }
}
```

---

## 7. Favicon & App Icon Test

### 7.1 Scalability Verification

| Size | Status | Note |
|------|--------|------|
| 16×16 | ✓ Tanınır | [Tek-renk silüet stabil / Monogram okunur] |
| 32×32 | ✓ Tanınır | [Detay korunuyor] |
| 64×64 | ✓ Tanınır | [İkinci renk girer] |
| 192×192 | ✓ Tam form | [Tüm detaylar] |
| 512×512 | ✓ Mastered | [Production export] |
| Monokrom (1-color) | ✓ Çalışır | [Pozitif ve negatif] |

### 7.2 App Icon Specifications

**iOS**:
- Master: 1024×1024 PNG
- Safe area: dış 9% kırpma için padding
- Background: opsiyonel; logomark içeriği masking olmadan tam görünür olmalı
- Rounded corner: iOS otomatik mask (kullanıcı oluşturmaz)

**Android (Adaptive Icon)**:
- Master: 512×512 PNG
- Foreground layer: mark only, transparent background
- Background layer: solid color (genellikle `--brand-9`)
- Safe area: 66dp center (108dp toplam canvas, kalan padding için)

**PWA / Favicon**:
- 16×16, 32×32 ICO
- 180×180 apple-touch-icon
- 192×192 + 512×512 maskable PNG

### 7.3 Favicon HTML Setup

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="[--brand-9 hex]">
```

---

## 8. Vector Conversion Specification

> **AI çıktısı raster (PNG); production logo vector (SVG) olmalıdır.** Bu adım, designer'a hand-off için **production-ready SVG geçişini** belgeler.

### 8.1 Source Raster

- **Source file**: `[midjourney-best-variant.png]`
- **Dimensions**: `[1024×1024]` (önerilen minimum 1024px master için)
- **Format**: PNG (lossless preferred over JPG for vector conversion)
- **Color depth**: 8-bit per channel
- **Background**: Transparent veya solid white (vtracer için ideal)

### 8.2 Vectorization Method

| Method | Süre | Kalite | Use Case |
|--------|------|--------|----------|
| **Auto-trace (vtracer)** | 5-30 sn | %70 | Hızlı moodboard, draft sunum |
| **Hibrit (önerilen)** | 1-3 saat | %90 | Çoğu marka projesi optimal |
| **Tam manuel rebuild** | 2-8 saat | %100 | Lüks markalar, kurumsal rebrand |

### 8.3 Auto-Trace Sonucu

`scripts/vector_trace.py` ile çalıştırıldı:

```bash
python vector_trace.py logo.png --output logo-traced.svg --preset logo-color
```

**Diagnostic Report**:

| Metric | Değer |
|--------|-------|
| File size | `[X.X KB]` |
| Path count | `[N paths]` |
| Approx node count | `[N nodes]` |
| Complexity | `[simple / moderate / complex]` |
| Backend | vtracer 0.6.x |
| Preset | `[logo-color / logo-mono / bw-clean / sketch]` |

### 8.4 Designer Cleanup Recommendations

- [ ] Anchor point optimization (Pen Tool: gereksiz düğümleri sil)
- [ ] Optical alignment (geometric ≠ optical center; ~3% adjust)
- [ ] Stroke vs Fill normalization (modern doctrine: single weight stroke veya pure fill)
- [ ] Boolean operations cleanup (`Pathfinder > Unite` ile path birleştir)
- [ ] Color reduction (auto-trace 6 renk üretebilir, brand palette'ine indir)
- [ ] SVGO post-processing (`npx svgo logo.svg --multipass`)
- [ ] Final pixel grid alignment (favicon 16px için kritik)

### 8.5 Telif Notu (KRİTİK)

> **USCO ruling (Şubat 2024)**: Pure AI-generated content **ABD'de telif altında değildir**. Vector rebuild + significant human modification (≥50% modify, compositional kararlar insan'ın) yapıldığında telif altına alınabilir.

**Pratik tavsiye**: Auto-trace'i sadece başlangıç noktası olarak kullan; manuel rebuild + designer notes (timestamp + modifikasyon dökümü) telif iddiası için zorunlu.

### 8.6 Final Vector Delivery Package

- [ ] **Master SVG** (1024×1024 viewBox, pixel-perfect)
- [ ] **PNG fallback'lar** (16/32/64/128/192/256/512/1024 — `favicon_simulator.py` ile)
- [ ] **PDF vector** (Adobe Illustrator → "Save As PDF, Press Quality")
- [ ] **EPS** (legacy print providers için)
- [ ] **AI source** (Adobe Illustrator native `.ai` — designer hand-off)

---

## 9. Print Production Specification

> **Brand reality test**: Web'de mükemmel görünen logo, business card'da, packaging'de, billboard'da, tekstil merch'de **tutarlı** mı? Bu bölüm bu döşemeyi kapsar.

### 9.1 Color Conversion Matrix (her brand color × her renk uzayı)

`scripts/pantone_matcher.py` ile üretildi:

| Brand Color | HEX (sRGB) | CMYK (GRACoL) | PMS C | PMS U | ΔE00 | Tolerance |
|-------------|------------|----------------|-------|-------|------|-----------|
| Primary | `#XXXXXX` | C__ M__ Y__ K__ | PMS XXX C | PMS XXX U | X.XX | ✓/⚠/✗ |
| Accent  | `#XXXXXX` | C__ M__ Y__ K__ | PMS XXX C | PMS XXX U | X.XX | ✓/⚠/✗ |
| Text Dark | `#XXXXXX` | C__ M__ Y__ K__ | PMS XXX C | PMS XXX U | X.XX | ✓/⚠/✗ |

**Tolerance interpretasyonu**:
- ✓ ΔE00 < 2.0 — Pantone resmi tolerance hedefi (excellent match)
- ⚠ ΔE00 2.0-5.0 — Perceptible difference (acceptable for non-critical)
- ✗ ΔE00 > 5.0 — No good PMS match — **consider custom spot ink** (Pantone Color Bridge formula via printer)

### 9.2 Recommended Paper Stock

| Application | Stock | GSM | Coating | Notes |
|-------------|-------|-----|---------|-------|
| Business cards | `[Crane's Lettra cotton]` | 350 | Uncoated | Letterpress-friendly |
| Stationery (letterhead) | `[FSC-certified bond]` | 120 | Uncoated | Eco-conscious option |
| Brand book interior | `[Mohawk Superfine]` | 150 | Coated matte | Premium reading experience |
| Brand book cover | `[Soft-touch laminated]` | 350 | Soft-touch matte | Tactile premium |
| Packaging | `[SBS — Solid Bleached Sulfate]` | 400 | Coated, optional UV | Retail packaging standard |
| Premium edition | `[Triplexed cotton]` | 600+ | — | Statement luxury |

### 9.3 Print Methods & Finishing

**Per-touchpoint specification**:

- **Business cards**: `[Letterpress (deep deboss for logo) on 350gsm cotton]`
- **Brochure**: `[Offset CMYK + Pantone XXX C 5th-color spot]`
- **Packaging**: `[Offset CMYK, gloss UV varnish on logo, soft-touch laminate body]`
- **Premium edition logo treatment**: `[Foil Stamp — Pantone Premium Metallics PMS 871 Gold (matte foil for sophistication)]`
- **Edge treatment** (triplexed cards): `[Painted edge color matching --brand-9]`

### 9.4 Specialty Finishing Options

| Effect | Use When | Cost Add-on |
|--------|----------|-------------|
| **Foil stamping** | Lüks/heritage tonality | $$$ (per-color setup + per-impression) |
| **Embossing** (kabartma) | Premium signal, tactile depth | $$ (die création + per-impression) |
| **Debossing** (içe basma) | Modern minimal, subtle luxury | $$ |
| **Spot UV varnish** | Logo glossy on matte body, contrast | $ (relative add-on) |
| **Letterpress** | Heritage/artisan, cotton paper | $$$$ (small-batch only) |

### 9.5 Color Management Protocol

**Adobe Creative Cloud setup**:
```
Edit > Color Settings:
  - Working Space (RGB):  sRGB IEC61966-2.1
  - Working Space (CMYK): Coated GRACoL 2006
  - Color Management Policies: Preserve Embedded Profiles
  - Conversion Options: Adobe ACE engine, Relative Colorimetric, BPC ON
```

**Press-ready file delivery format**:
- **PDF/X-1a** (CMYK preserved, standart safe choice)
- **PDF/X-4** (color management embedded, modern preference)
- Pantone spot color callouts INCLUDED (e.g., "Use PMS 2725 C as 5th color")

### 9.6 Proofing Protocol (MANDATORY)

- [ ] Press proof on **actual stock** (not generic proof paper)
- [ ] Color review under **D50 lighting** (5000K, color-correct booth)
- [ ] Compare to **physical Pantone Formula Guide** fan deck
- [ ] Sign-off form before production run
- [ ] Sample retention (1 per 100 units for QC)

> **Bilinen hata kaynakları**: Aynı PMS color farklı substrate'lerde (kâğıt → plastik → tekstil → metal) farklı görünür. Multi-substrate brand için **substrate-specific Pantone testing** (TPG textile reference, vs.) zorunlu.

### 9.7 Sustainability Specifications (eğer marka eco-positioned'sa)

- [ ] FSC-certified paper (Forest Stewardship Council)
- [ ] Recycled content (%PCW — Post-Consumer Waste)
- [ ] Soy-based inks (vs petroleum-based)
- [ ] Vegetable-based binding adhesives
- [ ] Local printing (carbon footprint düşürme)
- [ ] Brand book'ta explicit eco callout ("Mohawk Renewal 100% PCW, FSC-certified, wind-powered manufacture")

---

## 10. Motion Language Specification

> **2026'da motion opsiyonel değil**. Marka kılavuzunda motion bölümü olmamak, **2006'da renk paleti olmamak** kadar amatörcedir (All In Motion 2026).

`scripts/motion_spec_generator.py --archetype <X> --tonality "<Y>" --emit-lottie` ile üretildi.

### 10.1 Motion Personality Statement

> **Personality**: `[archetype-derived, 1 paragraf — örn: "Considered, slow, intentional. Akademik dinginlik."]`
>
> **Duration character**: `[arketip-spesifik aralık — örn: "deliberate (300-450ms)"]`

### 10.2 Duration Ladder (4-Tier)

| Tier | Range | Brand-Specific Value | Use Case |
|------|-------|----------------------|----------|
| **Micro** | 80-200ms | `[X ms]` | Button hover, tap feedback, focus ring |
| **UI** | 200-400ms | `[X ms]` | Modal open, dropdown reveal, toast |
| **Transition** | 250-500ms | `[X ms]` | Page nav, view change, scene cut |
| **Logo-stinger** | 1.0-2.5s (max!) | `[X.X s]` | Brand intro, splash, video opener |

> **Endüstri tavanı**: Logo animasyonları 2.5 saniyeyi geçmemeli (All In Motion 2026 enterprise standard).

### 10.3 Easing Palette

| Role | Name | CSS / cubic-bezier |
|------|------|---------------------|
| **Primary** | `[archetype-derived]` | `cubic-bezier(...)` |
| **Secondary** | `[archetype-derived]` | `cubic-bezier(...)` |

**Tonality modifier'lar uygulandı**: `[premium / luxury / fast / calm / bold / cesur / ...]`
- Duration slowdown factor: `×[X.XX]`
- Easing bias: `[more curve / snappier / more linear]`

### 10.4 Animation Primitives — Markanın "İzinli Hareket Vocabulary"si

**İzinli (use these)**:
- `[primitive 1, e.g. soft-fade]`
- `[primitive 2, e.g. embrace-scale]`
- `[primitive 3, e.g. warm-pulse]`

**Yasak (NO-GO zone)**:
- `[arketip-spesifik don'ts — örn: harsh cut, aggressive snap, anxiety-inducing flicker]`

### 10.5 Logo Stinger Animation Breakdown

Designer After Effects'te dolduracak şablon (hand-off brief):

| Frame Range (60 fps) | Duration | Action |
|----------------------|----------|--------|
| 0.0s — 0.3s | 18 frames | Logomark scale 80% → 100% (primary easing) |
| 0.3s — 1.0s | 42 frames | Logotype types in left-to-right with stagger |
| 1.0s — 2.0s | 60 frames | Tagline fades in below logotype |
| 2.0s — 2.5s | 30 frames | Hold + gentle fade-out (loop point) |

### 10.6 Light vs Dark Mode Variants (ZORUNLU)

| Variant | Background | Logo Treatment | Notes |
|---------|------------|-----------------|-------|
| Light | `--brand-1` (#FCFCFD) | Primary fill `--brand-9` | Default delivery |
| Dark | `--brand-12` (#0D0D0F) | Inverted: white fill OR `--brand-3` light tint | Drop-shadow/glow gerekirse re-tune |
| Transparent (master) | Alpha | Primary fill | Web embed default |
| Video overlay | Variable | Adaptive based on background luminance | Editor karar verir |

### 10.7 Hand-off Specifications

| Format | Use | Tool |
|--------|-----|------|
| **Source**: `.aep` | Master After Effects project | Adobe AE |
| **Web/mobile**: Lottie JSON | Embed via lottie-web/ios/android | Bodymovin or LottieFiles plugin |
| **Video**: MP4 ProRes 4444 | Editing pipeline (transparent BG) | AE export |
| **GIF fallback**: 480px max | Legacy email clients | LottieFiles or Photoshop |
| **dotLottie**: `.lottie` | 60% smaller than JSON | dotlottie.io |

**Lottie skeleton dosyası**: `assets/[archetype-lower]-stinger-skeleton.json`
- Composition: `[1024×1024]` @ 60fps
- Duration: `[X.X s]` = `[N frames]`
- Layer count: 1 (placeholder — designer fills shapes)
- Background: transparent

### 10.8 Implementation Code Snippets

**Web embed**:
```html
<div id="logo-stinger" style="width:200px;height:200px"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<script>
  lottie.loadAnimation({
    container: document.getElementById('logo-stinger'),
    renderer: 'svg',
    loop: false,
    autoplay: true,
    path: '/assets/logo-stinger.json'
  });
</script>
```

**iOS** (Swift Package: `lottie-ios`):
```swift
let animationView = LottieAnimationView(name: "logo-stinger")
animationView.contentMode = .scaleAspectFit
animationView.play()
```

**React Native** (`lottie-react-native`):
```jsx
import LottieView from 'lottie-react-native';
<LottieView source={require('./logo-stinger.json')} autoPlay loop={false} />
```

---

## 11. Application Mockup Briefs

> **Not**: Bu skill **mockup üretmez**. Aşağıda, bir tasarım stüdyosunun (veya self-design'da Figma'da) öncelikli olarak üretmesi gereken **3-5 critical touchpoint** brief'i bulunur.

### 8.1 Web Hero Section

- Logomark + logotype lock-up (sol-üst veya merkez)
- Hero typography: [Display font] @ `--text-5xl`, weight 700
- Background: `--brand-2` veya tam görsel + `--brand-12` overlay text
- Primary CTA button: `--brand-9` background, white text

### 8.2 App Icon (1024×1024)

- Solid `--brand-9` background
- Logomark center, monochromatic white
- Padding: 18% all sides
- Master file: PNG + SVG

### 8.3 Business Card

- Boyut: 85×55mm (Avrupa) / 89×51mm (US)
- Front: Logomark + logotype, color
- Back: name + role typography
- Stock: 350gsm uncoated paper, optional letterpress emboss for brand mark
- Color: `--brand-9` solid OR uncoated white with `--brand-12` text

### 8.4 Pitch Deck Cover

- 16:9 aspect, 1920×1080 master
- Logomark large center / off-center
- Background: `--brand-9` veya `--brand-2`
- Tagline beneath in `--font-body` weight 500

### 8.5 Social Media Avatar

- 400×400 master
- Logomark only (no logotype)
- Background: solid `--brand-9` veya transparent
- Test in light/dark mode round masks

---

## 12. Forbidden Variations

> **Marka tutarlılığını koruyan "yapma" kuralları.** Brand guidelines kitabında her zaman bu bölüm vardır.

### 9.1 Logo

- ❌ Logo'yu **ger** veya **squash** etmeyin (oranı koruyun)
- ❌ Onaylanmış renk dışı renklerle kullanmayın
- ❌ Kompleks fotoğraf/desen üzerine doğrudan koymayın (her zaman solid renk veya kontrastlı arka plan)
- ❌ **Drop shadow / glow / outline / 3D effect** uygulamayın
- ❌ Logoyu rotate etmeyin (özel hareket exception olabilir)
- ❌ Logo elementlerini bireysel olarak ayırıp yeniden düzenlemeyin
- ❌ Çevresinde **clear space** kuralını ihlal etmeyin
- ❌ Minimum boyutun altında kullanmayın
- ❌ Logoyla aynı tonda arka planda kullanmayın (yetersiz kontrast)

### 9.2 Color

- ❌ Brand renkleri ile **gradient** yapmayın (özel app icon variant exception)
- ❌ Functional renkleri (success/error/warning) **brand color olarak kullanmayın**
- ❌ Step 9'u bir gri ile karıştırmayın

### 9.3 Typography

- ❌ Brand fontlar dışında font kullanmayın
- ❌ Logotype'ı **stretched** veya **condensed** versiyon ile değiştirmeyin
- ❌ Italik logotype kullanmayın (eğer logotype italik değilse)
- ❌ Body font'u 11px altında kullanmayın (okunabilirlik)

---

## 13. Bibliography & Inspirations

### 10.1 Methodology Sources
[Adım 5'te kullanılan kanonik kaynaklar — `references/bibliography.md`'den çek]

- Wheeler, A. & Meyerson, R. (2024). *Designing Brand Identity* (6th ed.). Wiley.
- Müller, J. (2015). *Logo Modernism*. Taschen.
- Evamy, M. (2012). *Logotype*. Laurence King.
- Chermayeff, I., Geismar, T., & Haviv, S. (2011). *Identify: Basic Principles of Identity Design*.
- Pearson, C. & Mark, M. (2001). *The Hero and the Outlaw*. McGraw-Hill.
- Burmann, C., Riley, N., Halaszovich, T., & Schade, M. (2017). *Identity-Based Brand Management*. Springer.
- Stocks, E. J. (2024). *Universal Principles of Typography*. Rockport.

### 10.2 Visual Inspirations Referenced
- [Listed historical brands and designers anchored throughout the protocol]
- Pentagram | Koto Studio | Wolff Olins | Chermayeff & Geismar & Haviv | Landor

### 10.3 Technical Standards
- Radix Colors — github.com/radix-ui/colors (12-step accessible color system)
- W3C Design Tokens Format Module — design-tokens.github.io
- WCAG 2.2 / APCA — w3.org/WAI/WCAG22
- Variable Fonts — variablefonts.io
- Inter font — github.com/rsms/inter

---

## 14. Implementation Checklist & Next Steps

- [ ] Logomark exported as SVG (master) + PNG @ 16/32/64/128/192/256/512/1024
- [ ] Logotype lock-up exported (color, monochrome positive, monochrome reversed)
- [ ] Color tokens implemented in CSS variables (light + dark mode)
- [ ] Typography fonts loaded (variable font @font-face)
- [ ] Tailwind config / design system framework integration
- [ ] Favicon set generated (realfavicongenerator.net)
- [ ] App icon master files (iOS, Android adaptive)
- [ ] Brand guidelines document (this report → PDF or web)
- [ ] Trademark registration filed (USPTO/EUIPO/TÜRKPATENT — see brand-maker output)
- [ ] First production touchpoint launched (web hero, app icon, business card)

---

### 14.1 Next Steps

### Immediate (1 hafta)
1. **Vector rebuild**: AI-generated mark'ı Adobe Illustrator/Figma'da temiz vektör olarak yeniden inşa et
2. **Favicon test**: Vector çıktıyı realfavicongenerator.net'te tüm platform varyasyonları için doğrula
3. **Brand color hex export**: 12-step palette'i tasarım sistemine import et

### Short term (1 ay)
4. **First production touchpoint**: Web hero veya app icon — sembolün gerçek dünyada nasıl yaşadığını gör
5. **Trademark filing**: brand-maker'dan WIPO/USPTO ön-tarama URL'leri ile başla
6. **Brand guidelines document**: Bu report'u PDF ya da Notion/Figma sayfasına çevir

### Medium term (3 ay)
7. **Brand voice copywriting**: Görsel kimlik ile uyumlu **verbal identity** geliştirin
8. **Photography style guide**: Görsel kimliği fotoğrafa nasıl genişletirsiniz
9. **Motion brand language**: Logo animasyon, transition, easing curve

### Long term (12 ay)
10. **Brand experience touchpoint audit**: Web, app, packaging, retail, event — tutarlılık denetimi
11. **Sub-brand architecture**: Yan markalar/ürünler için sistematik kuralları geliştir
12. **Brand book v2.0 release**: 1 yıllık öğrenme + iterasyon ile guidelines'ı revize et

---

*Bu rapor `brand-visual` skill v1.0 ile üretilmiştir. Üretim aşamasında bir profesyonel
tasarım stüdyosu (veya kalifikasyonlu bir designer) ile finalize edilmesi şiddetle
önerilir. AI üretimi konsept referansıdır, production-ready vector dosya değildir.*
```

---

---

## 15. Adaptive Identity Rules *(yalnızca Route 4 seçildiğinde)*

> v1.3 Genesis edition. Detaylı brief: `references/adaptive-identity.md`.

### 15.1 Core Spine Specification
| Attribute | Value |
|-----------|-------|
| Geometry | [SVG path / description of immutable core forms] |
| Primitive form count | [1-3] |
| Dimensions | [X × Y units, aspect X:Y] |
| Primary color (mandatory in all variants) | [HEX + Pantone] |
| Trademark asset | ✓ (this is the registered mark) |
| Favicon 16px silhouette | ✓ (core spine only, shell stripped) |

### 15.2 Variable Parameters
1. **[Parameter 1 — e.g., Season]**: Input values [list], Triggered element [shell color/shape], Range [discrete/continuous]
2. **[Parameter 2 — e.g., Aspect Ratio]**: ...
3. **[Parameter 3 — optional]**: ...

### 15.3 Variant Library (Minimum 3, Optimum 5-12)
| ID | Name | Parameter State | Usage Context |
|----|------|-----------------|---------------|
| V01 | Primary | (defaults) | Master brand asset |
| V02 | [variant name] | [parameter values] | [context] |
| ... | ... | ... | ... |

### 15.4 Transition Rules
- **Within web UI**: [instant / animated crossfade 240ms / morph / generative / stateful]
- **Between campaigns**: [behavior]
- **Print / static**: [variant locked per asset]
- **Reduced-motion preference**: instant switch, no animation

### 15.5 Constraint System
- Core visual consistency: **≥ 60%** geometric overlap across all variants
- Primary brand color: mandatory in every variant
- Favicon rendering (16px): core spine only

### 15.6 Implementation Path Selected
[ ] A: CSS Custom Properties + SVG (simple web)
[ ] B: Figma Variants + Design Tokens (design-led)
[ ] C: Programmatic Generative SVG (advanced)

Detailed design tokens + code scaffolding: see `references/adaptive-identity.md` Yol A/B/C templates.

### 15.7 Governance
- Variant approval workflow: [brand team review gate]
- DAM (Digital Asset Management): [tool + folder structure]
- Usage guideline document: [brand book section]
- Annual variant review: [quarter]

---

## 16. Sonic Identity Brief *(opsiyonel — v1.3)*

> v1.3 Genesis edition. Detaylı brief: `references/sonic-identity.md`.

### 16.1 Sonic Personality (Archetype-derived)
[2-3 sentence statement describing brand's audio character]

### 16.2 Core Sonic Logo Specification
| Attribute | Value |
|-----------|-------|
| Length | [1-3 seconds] |
| Note count | [3-7 notes] |
| Melodic contour | [ascending / descending / arch / inverted arch] |
| Interval pattern | [e.g., "perfect fifth up, minor third up"] |
| Rhythmic pattern | [e.g., "quarter-eighth-eighth-half"] |
| Key/Mode | [e.g., "D major" / "A Dorian"] |
| Tempo | [BPM range] |
| Primary timbre | [description] |
| Dynamic envelope | [attack-sustain-release] |
| Emotional register | [target feeling] |

### 16.3 Sonic Anchor References
1. [Composer/era reference 1]
2. [Composer/era reference 2]
3. [Contemporary production reference]

### 16.4 Use Case Variations
| Variant | Length | Context |
|---------|:-:|---|
| Full | 3.0s | Podcast opens, video intros |
| Chime | 1.5s | App activation, success feedback |
| Micro | 0.6s | Notifications, UI confirmation |

### 16.5 Earcon Library (7-item standard set)
[Notification / Success / Error / Transition / Onboarding welcome / Unlock / Close — see references/sonic-identity.md]

### 16.6 Voice Persona Parameters
| Parameter | Value |
|-----------|-------|
| Pitch range | [Hz band] |
| Speech rate | [WPM] |
| Warmth | [1-10 scale] |
| Formality | [1-10 scale] |
| Accent | [regional] |
| Emotional register | [description] |

### 16.7 AI Voice Model Parameters (rapid prototyping)
- **ElevenLabs**: Stability [0.50-0.65], Clarity [0.75+], Style [0.35-0.50]
- **OpenAI TTS**: Voice [nova/shimmer/onyx/sage], Model tts-1-hd, Speed [0.95-1.05]
- **Play.ht**: [style profile], Pronunciation library (brand terms)

### 16.8 Production Handoff & Licensing
[Composer shortlist, file formats (WAV/AIFF/MP3/AAC/Ogg), stems, rights model, EU AI Act disclosure if AI voice]

---

## 17. AI Discoverability Layer *(v1.3 — zorunlu)*

> v1.3 Genesis edition. Detaylı brief: `references/ai-discoverability.md`.

### 17.1 Canonical Brand Description Prompt (20 kelime altın cümle)
> "[Finalized 10-20 word description — used EVERYWHERE: website footer, LinkedIn, press boilerplate, podcast intros]"

### 17.2 Entity Knowledge Card (Schema.org JSON-LD)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Brand Name]",
  "description": "[20-word brand description prompt]",
  "foundingDate": "YYYY-MM-DD",
  "url": "[primary domain]",
  "logo": "[URL to canonical logo SVG]",
  "sameAs": ["[Wikipedia]", "[Wikidata]", "[LinkedIn]", "[Twitter]"],
  "knowsAbout": ["[topic 1]", "[topic 2]"],
  "makesOffer": [{"@type": "Offer", "name": "[Product/Service]"}]
}
```
**Deployment**: Ana website `<head>` içine gömülür + `/.well-known/brand.json` public endpoint.

### 17.3 Logo Alt Text Library
- **Short (≤125 char)**: "[Alt text for img tags]"
- **Voice description (AI-narration, 1-2 sentence)**: "[narrative description]"
- **Pronunciation**: IPA `/[...]/` · Plain `[...]` · Voice alias `[...]`

### 17.4 Agent-Era Brand Manifesto
**Location**: `/brand/manifesto.md` (public, crawlable markdown)
**Length**: ~500 words (30-line template in references/ai-discoverability.md)
**Key fields**: Who we are / What we do / Who we serve / What makes us distinct / What we don't do / Our values / Our visual identity / How to reference us / Machine-readable metadata links

### 17.5 AI-SEO Baseline Audit (5 Tests)
| Test | ChatGPT | Claude | Gemini | Grok | Notes |
|------|:-:|:-:|:-:|:-:|---|
| Direct Recognition | ✗/⚠/✓ | ✗/⚠/✓ | ✗/⚠/✓ | ✗/⚠/✓ | ... |
| Contextual Recommendation | ✗/⚠/✓ | ✗/⚠/✓ | ✗/⚠/✓ | ✗/⚠/✓ | ... |
| Comparative Accuracy | ✗/⚠/✓ | ✗/⚠/✓ | ✗/⚠/✓ | ✗/⚠/✓ | ... |
| Visual Description (image upload) | n/a | n/a | ✓ | ✓ | NB2/Grok native image |
| Voice UI Readability | — | — | ✓ | ✓ | Gemini/Grok voice |

**Baseline date**: [YYYY-MM-DD] · **Re-test schedule**: Q2, Q4 first year; annual thereafter.

### 17.6 Action Plan
1. Deploy structured data (JSON-LD) — Week 1
2. Publish `/brand/manifesto.md` — Week 1
3. Wikidata entry — Month 1-2
4. Wikipedia entity — Month 3-6 (after notability)
5. Social profile description consistency — Week 2
6. Press release boilerplate standardization — Ongoing
7. Quarterly AI-SEO audit — 5-test protocol

---

## 18. C2PA Content Credentials & AI Provenance *(v1.3 — zorunlu)*

> v1.3 Genesis edition. Detaylı brief: `references/c2pa-provenance.md`.

### 18.1 Provenance Chain Dokümantasyonu

**Generation Layer**:
- Model: [e.g., Nano Banana 2 (gemini-3.1-flash-image-preview)]
- Generation date: [YYYY-MM-DD]
- UMMP prompt (canonical): "[quoted full paragraph]"
- Iterations: [N rounds of conversational refinement]
- SynthID watermark: ✓ (invisible, embedded)
- C2PA manifest: ✓ (auto-generated by model)

**Transformation Layer**:
- Vector conversion: [vtracer / Illustrator / manual Pen Tool]
- Manual cleanup: [approx hours]
- Node count: [pre-cleanup X → post-cleanup Y]
- Metadata preservation: ✓ (C2PA transferred to SVG `<metadata>`)

**Publication Layer**:
- Primary asset: logo.svg (canonical, embedded C2PA)
- Secondary assets: logo.png (various sizes, manifest retained)
- Public Content Credentials URL: `[brand.com/content-credentials]`

### 18.2 EU AI Act Disclosure Statement
**Tier classification**: [Tier 1 core identity / Tier 2 campaign / Tier 3 mockup]
**Website footer disclosure (persistent)**:
> "Our brand identity was developed through creative direction with AI image generation (Nano Banana 2) and refined through manual vector design. [Content Credentials →]"

### 18.3 Trademark Strategy Package
- **Jurisdiction**: [USPTO / EUIPO / TÜRKPATENT / WIPO Madrid]
- **Nice Class**: [X]
- **Human authorship record**: [comprehensive process documentation]
- **AI Disclosure Statement**: [template from references/c2pa-provenance.md]
- **Filing date target**: [YYYY-MM-DD]

### 18.4 Copyright Position
- **USA (Thaler v. Perlmutter + USPTO 2025)**: [Human-authored significant modifications documented]
- **EU (AI Act)**: [Disclosure + provenance chain attached]
- **Türkiye (SMK 6769 + FSEK 5846)**: [Marka tescili + hususiyetli insan-yazarı argümanı]

### 18.5 Tooling & Governance
- **C2PA-compliant workflow**: Adobe Creative Suite 2026 native + c2patool CLI
- **Metadata preservation on social platforms**: [Platform-by-platform status]
- **Provenance Manager role**: [Designated person/team]
- **Quarterly provenance audit**: [Process]
- **Vendor contract C2PA clause**: [Required in partner agreements]

### 18.6 Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|:-:|:-:|---|
| Metadata strip on export | Medium | High | C2PA-native tools only |
| Third-party asset reuse w/o credentials | High | Medium | Vendor contracts require C2PA |
| Trademark challenge citing AI authorship | Low | High | Comprehensive human record |
| EU AI Act non-compliance | Medium | High | Tier 2/3 disclosures on all public assets |
| Social repost metadata loss | High | Low | Original assets on brand.com with full credentials |

---

> **v1.3 Template Kullanım Notu**: Section 15-18 v1.3 Genesis sürümünde eklenmiştir. Sections 15 (Adaptive Identity) ve 16 (Sonic Identity) **opsiyonel** (Route 4 seçimi ve marka olgunluğuna bağlı). Sections 17 (AI Discoverability) ve 18 (C2PA Provenance) **v1.3'te zorunlu** — her brand identity deliverable artık bu katmanları içermelidir.
