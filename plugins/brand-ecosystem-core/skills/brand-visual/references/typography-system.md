# Typography System — Variable Font Modernizmi

> **Bu dosya `brand-visual` skill'inin Adım 5 işleminde her zaman aktif kullanılır.**
> Modern marka tipografisi 2026'da: **variable fonts** (tek dosya = tüm ağırlıklar + style axes), **screen-first x-height** optimizasyonu, **modular type scale**, ve **Display + Body + opsiyonel Mono** üçlüsü.

---

## Felsefi Temel

> "Typography is two-dimensional architecture, based on experience and imagination, and guided by rules and readability." — Hermann Zapf

> "Type is the design of the brand. The brand is the design of the type." — Massimo Vignelli (American Airlines, Knoll, NYC Subway)

Çoğu marka kimliği projesinde tipografi **sonradan eklenir** — logo bittikten sonra "iyi font seçelim" şeklinde. Bu **2010'ların paradigmasıdır**.

**2026'nın paradigması**: Tipografi **brand DNA'sının kendisidir**. Wordmark = tipografi seçimidir. UI'da %90 yüzey tipografidir. Variable font teknolojisi, tek bir font ailesinin **tüm marka deneyimini** taşımasını mümkün kılar.

---

## VARIABLE FONT TEKNOLOJİSİ

### Tanım
Variable font (OpenType 1.8, 2016'da yayınlandı) **tek bir dosyada** birden çok stilin **sürekli** olarak interpolate edilebildiği font formatıdır.

**Geleneksel**: Inter Regular, Inter Medium, Inter Bold, Inter Italic, Inter Bold Italic = **5 ayrı dosya** (~150KB her biri = 750KB total)

**Variable**: Inter Variable = **1 dosya** (~250KB, tüm ağırlık + italic dahil)

### Ana Axes (Variation Axes)

| Axis | Tag | Range | Use |
|------|-----|-------|-----|
| **Weight** | `wght` | 100-900 | Light - Regular - Medium - Bold - Black |
| **Width** | `wdth` | 50-200 | Condensed - Normal - Extended |
| **Italic** | `ital` | 0 / 1 | Roman / Italic |
| **Slant** | `slnt` | -90 to 0 | Slanted (italic alternative) |
| **Optical Size** | `opsz` | 6-144 | Small text vs display optimization |
| **Grade** | `GRAD` | -200 to 150 | Custom darkness adjustment |

### CSS Kullanımı

```css
/* Static loading */
@font-face {
  font-family: "Inter Variable";
  src: url("/fonts/InterVariable.woff2") format("woff2-variations");
  font-weight: 100 900;  /* Range, not single value */
  font-style: normal;
  font-display: swap;
}

/* Dynamic variation */
.heading {
  font-family: "Inter Variable";
  font-weight: 750;  /* Inter doesn't have 750 statically — variable interpolates */
  font-variation-settings: "opsz" 32, "wght" 750;
  font-optical-sizing: auto;
}
```

### Avantajlar

1. **Performance** — 5 dosya yerine 1, sayfa yükü %70-80 azalır
2. **Granular control** — `font-weight: 612` gibi exact değerler (statik fontta yok)
3. **Animation** — weight, width axis'leri **animate** edilebilir
4. **Brand identity** — özel weight kombinasyonları "brand'e ait" olur
5. **Logotype precision** — wordmark için **kesin weight** (sadece 400, 600 ile sınırlı değil)

### Dezavantajları

- Eski browser desteği (IE11 ✗, ama IE11 zaten 2026'da sıfır market share)
- Bazı font foundry'leri variable license farklı fiyatlar (commercial seat-based)

---

## MODERN VARIABLE FONT KATALOĞU (2026 Önerilen)

### Display + Body Use (En Modern Stack)

| Font | Foundry | License | x-height | Karakter | Use Case |
|------|---------|---------|----------|----------|----------|
| **Inter Variable** | Rasmus Andersson | OFL (free) | High | Geometric humanist | Default modern UI/web |
| **Inter Display Variable** | Rasmus Andersson | OFL | High | Display-optimized Inter | Headings, hero |
| **Söhne** | Klim Type Foundry | Commercial seat | Medium-high | Neo-grotesque | Premium tech (used by ChatGPT, Stripe alternative) |
| **Geist** | Vercel | OFL | High | Geometric monospace family | Modern dev/tech (Vercel official font) |
| **Geist Sans** | Vercel | OFL | High | Sans companion | Modern dev/tech |
| **General Sans** | Indian Type Foundry (ITF) | OFL | High | Geometric humanist | Versatile modern |
| **Cabinet Grotesk** | Indian Type Foundry | OFL | Medium | Modern grotesque | Editorial display |
| **Plus Jakarta Sans** | Tokotype | OFL | Medium-high | Humanist grotesque | Modern UI |
| **Manrope** | Mikhail Sharanda | OFL | High | Modern geometric | Tech UI |
| **DM Sans Variable** | Colophon Foundry | OFL | Medium-high | Geometric | Google Material |
| **Recoleta** | Latinotype | Commercial | Medium | Soft serif display | Editorial / lifestyle |
| **Fraunces Variable** | Undercase Type | OFL | Medium | Old-style serif (modern revival) | Editorial / luxury |
| **Newsreader Variable** | Production Type | OFL | High | Transitional serif | News editorial |

### Mono Use

| Font | Foundry | License | Use |
|------|---------|---------|-----|
| **JetBrains Mono** | JetBrains | OFL | Code, technical, developer brands |
| **Geist Mono** | Vercel | OFL | Modern dev brands |
| **IBM Plex Mono** | IBM | OFL | Corporate technical |
| **Fira Code** | Mozilla | OFL | Code with ligatures |

### Lüks / Heritage (Variable Olmayanlar Hâlâ Geçerli)

| Font | Use |
|------|-----|
| **GT Sectra** | Editorial, lüks lifestyle |
| **Caslon** | Klasik publishing |
| **Trajan** | Roman authority (Hollywood film posters) |
| **Garamond** | Akademik publishing |
| **Didot** | Lüks fashion (Vogue legacy) |
| **Bodoni** | High-contrast lüks |

---

## X-HEIGHT FELSEFESİ — EKRAN OPTİMİZASYONU

**x-height**: Küçük 'x' harfinin yüksekliği. Cap height'a oranı kritik.

### Yüksek x-height (Modern, Screen-First)
- Inter, Geist, Söhne, Manrope
- Avantaj: Küçük font size'larda **okunabilirlik** çok yüksek (mobil UI'lar)
- Dezavantaj: Geleneksel "elegant" hissi azalır

### Orta x-height (Dengeli)
- Garamond, IBM Plex Sans
- Avantaj: Versatile, hem print hem screen
- Dezavantaj: Spesifik bir karakter taşımaz

### Düşük x-height (Editorial, Luxury)
- Didot, Bodoni, GT Sectra
- Avantaj: Sofistike, magazine elegance
- Dezavantaj: Mobil küçük boyutta okunabilirlik düşük

> **Marka için seçim kuralı**: B2B SaaS / mobile-first / consumer modern → **yüksek x-height** (Inter, Geist). Editorial / luxury / heritage → **düşük x-height** (Didot, Caslon).

---

## DISPLAY + BODY PAIRING SİSTEMATİĞİ

İki font kombinasyonu = brand voice'un yarısı.

### Pairing Stratejileri

#### 1. **Same Family Display+Text Variants**
- Inter Display + Inter
- Söhne Breit + Söhne
- IBM Plex Sans Condensed + IBM Plex Sans

> **Avantaj**: Maximum cohesion. Family aynı, sub-stylization farklı.
> **Önerilen**: Yeni markalar, B2B SaaS, profesyonel hizmetler.

#### 2. **Geometric Display + Humanist Body**
- Manrope (display) + Inter (body)
- General Sans (display) + Plus Jakarta Sans (body)

> **Avantaj**: Display'de impact, body'de okunabilirlik.
> **Önerilen**: Consumer brands, lifestyle.

#### 3. **Serif Display + Sans Body**
- Fraunces (display) + Inter (body)
- GT Sectra (display) + Söhne (body)
- Recoleta (display) + Manrope (body)

> **Avantaj**: Editorial heritage + modern usability.
> **Önerilen**: Editorial, publishing, lifestyle, luxury.

#### 4. **All Sans System (Most Common)**
- Söhne sadece (display + body weights)
- Inter sadece

> **Avantaj**: Maksimum minimalism, system management kolay.
> **Önerilen**: Tech, modernist brands.

#### 5. **Bold Contrast (Editorial/Magazine)**
- Druk Wide (display, condensed bold) + Tiempos Text (body serif)
- Akzidenz Grotesk Bold (display) + Caslon (body)

> **Avantaj**: Yüksek kontrast, editorial impact.
> **Önerilen**: Magazine, editorial, brand journalism.

### Pairing Test (Bir Marka için)

```
Sorular:
1. Markanın tonu **modern** mu, **heritage** mı? → Sans-only / Serif accent
2. Body text **yoğun** mu (uzun blog), **scattered** mi (UI labels)? → x-height önceliği
3. Multi-language (CJK, Arabic) destek lazım mı? → Inter, Söhne, IBM Plex (geniş glyph set)
4. Foundry / lisans budget? → OFL (free) önerilir başlangıçta, scale'de commercial
```

---

## TYPE SCALE (MODULAR RATIO)

Modular scale: matematiksel olarak hesaplanmış type size hierarchy.

### Common Ratios

| Ratio | Name | Karakter | Use |
|-------|------|----------|-----|
| **1.067** | Minor Second | Çok yumuşak | Dense UI, dashboard |
| **1.125** | Major Second | Yumuşak | Conservative, finance |
| **1.200** | Minor Third | Standart | Default modern web |
| **1.250** | Major Third | **Önerilen default** | Most balanced |
| **1.333** | Perfect Fourth | Belirgin | Editorial, content |
| **1.414** | Augmented Fourth | √2 ratio (paper sizes) | Editorial, publishing |
| **1.500** | Perfect Fifth | Kuvvetli | Marketing, hero pages |
| **1.618** | Golden Ratio | Klasik | Luxury, editorial classical |

### Önerilen: 1.250 (Major Third)

**Steps** (base 16px):

| Step | Size (rem) | Size (px) | Use |
|------|-----------|-----------|-----|
| -2 | 0.64 | 10.24 | Caption, metadata, fine print |
| -1 | 0.8 | 12.8 | Small label, tag, footnote |
| 0 | 1.0 | 16 | **Body default** |
| 1 | 1.25 | 20 | Lead paragraph, large body |
| 2 | 1.5625 | 25 | Subheading, H4 |
| 3 | 1.953 | 31.25 | H3, section title |
| 4 | 2.441 | 39 | H2, page heading |
| 5 | 3.052 | 48.8 | H1, hero subhead |
| 6 | 3.815 | 61 | Display, hero headline |
| 7 | 4.768 | 76.3 | Mega display, marketing hero |

### Type-utility CSS

```css
:root {
  --type-scale-ratio: 1.25;
  --text-base: 1rem;

  --text-xs: 0.64rem;
  --text-sm: 0.8rem;
  --text-md: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.5625rem;
  --text-2xl: 1.953rem;
  --text-3xl: 2.441rem;
  --text-4xl: 3.052rem;
  --text-5xl: 3.815rem;
}

.text-xs { font-size: var(--text-xs); line-height: 1.4; }
.text-sm { font-size: var(--text-sm); line-height: 1.5; }
.text-md { font-size: var(--text-md); line-height: 1.5; }
.text-lg { font-size: var(--text-lg); line-height: 1.4; }
.text-xl { font-size: var(--text-xl); line-height: 1.3; }
.text-2xl { font-size: var(--text-2xl); line-height: 1.2; font-weight: 600; }
.text-3xl { font-size: var(--text-3xl); line-height: 1.2; font-weight: 600; }
.text-4xl { font-size: var(--text-4xl); line-height: 1.1; font-weight: 700; }
.text-5xl { font-size: var(--text-5xl); line-height: 1.0; font-weight: 700; }
```

> **Line-height pattern**: Küçük text = yüksek line-height (1.5+), büyük text = sıkı line-height (1.0-1.2). İlişkisel: text büyüdükçe line-height küçülür.

---

## LOGOTYPE LOCK-UP SPECIFICATION

Wordmark seçildiğinde, **lock-up** (sıkı düzenleme) gereklidir.

### Anatomi

```
[Brand Name]

Font family: [exact name + foundry URL]
License: [OFL / SIL / Commercial seat / Adobe / Google]
Variable axes: [wght 100-900, opsz 10-60, italic 0/1]

Logotype-specific settings:
  Weight: 600 (Semibold)
  Optical size: 32 (display range)
  Italic: 0 (Roman)
  Slant: 0
  Width: 100 (Normal)

Tracking (letter-spacing): -25 (typographer units; CSS: -0.025em)
Kerning: optical (or custom pairs)

Custom kerning pairs:
  (T, h): -10
  (F, a): -25
  (W, A): -15
  (V, A): -20
  (L, T): +5

Cap height: 56pt (when logotype is 80pt total height)
x-height: 38pt
Baseline alignment: center

Color: --brand-12 (default), white reversed (--brand-1), monochrome
Minimum size:
  Print: 8mm wide
  Web: 80px wide minimum (full lockup)
  Vector unlimited (SVG)
```

### Custom Kerning — Niçin Kritik

Default fontlar **automatic kerning** ile gelir, ama **logotype** için bu yetersiz:

**Default**: "Curio" — harfler arası uniform mesafe
**Custom**: "Curio" — C-u arasında -5, r-i arasında +2, i-o arasında -3 = **optik dengeli** (sadece "matematiksel uniform" değil)

> Profesyonel logotype, **manual kerning** disiplinidir. Variable font ile bu kontrol granularize edilmiş.

---

## RAPOR ÇIKTI ŞABLONU (Adım 5'te kullan)

```markdown
## Tipografi Sistemi

### Display Font (Heading, Hero, Logotype)

**Family**: [örn: Inter Display Variable]
**Source**: [Google Fonts URL]
**License**: OFL (free commercial use)
**Variable axes**: wght 100-900, opsz 10-60
**x-height**: High (modern screen optimization)
**Style attributes**: Geometric humanist, neo-grotesque

**Default usage**:
- Logotype: weight 600, opsz 32, tracking -25
- H1 (hero): weight 700, opsz 60, line-height 1.0
- H2 (section): weight 700, opsz 40, line-height 1.1
- H3: weight 600, opsz 24, line-height 1.2

### Body Font (UI, Body Text, Forms)

**Family**: [örn: Inter Variable]
**System fallback stack**: `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
**License**: OFL
**Variable axes**: wght 100-900

**Default usage**:
- Body: weight 400, line-height 1.5
- Body emphasis: weight 500
- Strong: weight 600
- Caption: weight 400, opsz 10 (variable optical)

### Mono Font (Code, Technical) — Opsiyonel

**Family**: [örn: JetBrains Mono Variable]
**Source**: [...]
**Use**: Code blocks, technical specs, system numbers

### Type Scale

**Modular ratio**: 1.250 (Major Third)
**Base size**: 16px
[Tam tablo: -2 to +6 step]

### Logotype Lock-Up Specification

[Detailed spec with custom kerning pairs, exact tracking, color variations]

### Pairing Rasyonel

[Display + Body kombinasyonunun **neden seçildiği** — 100 kelime]
- Cohesion: same family / contrasting
- x-height harmony
- Variable axes overlap
- License compatibility
```

---

## CSS TOKEN EXPORT

```css
:root {
  /* === Font Families === */
  --font-display: "Inter Display Variable", ui-sans-serif, system-ui;
  --font-body: "Inter Variable", ui-sans-serif, system-ui;
  --font-mono: "JetBrains Mono Variable", ui-monospace, monospace;

  /* === Type Scale (1.250 Major Third) === */
  --type-scale-ratio: 1.25;
  --text-base: 1rem;
  --text-xs: 0.64rem;
  --text-sm: 0.8rem;
  --text-md: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.5625rem;
  --text-2xl: 1.953rem;
  --text-3xl: 2.441rem;
  --text-4xl: 3.052rem;
  --text-5xl: 3.815rem;

  /* === Line Heights === */
  --leading-tight: 1.0;
  --leading-snug: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 1.75;

  /* === Font Weights === */
  --font-light: 300;
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-black: 900;

  /* === Letter Spacing === */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}

/* Logotype specific */
.brand-logotype {
  font-family: var(--font-display);
  font-weight: 600;
  font-variation-settings: "opsz" 32, "wght" 600;
  font-optical-sizing: auto;
  letter-spacing: -0.025em;
  line-height: 1.0;
}
```

---

## TAILWIND CONFIG

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        display: ['var(--font-display)'],
        sans: ['var(--font-body)'],
        mono: ['var(--font-mono)'],
      },
      fontSize: {
        xs: 'var(--text-xs)',
        sm: 'var(--text-sm)',
        base: 'var(--text-md)',
        lg: 'var(--text-lg)',
        xl: 'var(--text-xl)',
        '2xl': 'var(--text-2xl)',
        '3xl': 'var(--text-3xl)',
        '4xl': 'var(--text-4xl)',
        '5xl': 'var(--text-5xl)',
      },
      lineHeight: {
        tight: 'var(--leading-tight)',
        snug: 'var(--leading-snug)',
        normal: 'var(--leading-normal)',
        relaxed: 'var(--leading-relaxed)',
        loose: 'var(--leading-loose)',
      },
      letterSpacing: {
        tight: 'var(--tracking-tight)',
        normal: 'var(--tracking-normal)',
        wide: 'var(--tracking-wide)',
      },
    },
  },
};
```

---

## YAYGIN HATALAR

### Hata 1 — Statik font katalog tüm weight'leri import
❌ Inter-100.woff2, Inter-200.woff2, ... Inter-900.woff2 + Inter-Italic-100.woff2 ... = **18 dosya, 2.5MB**
✓ InterVariable.woff2 = **1 dosya, 250KB**

### Hata 2 — Brand fontu sadece logoda
❌ Logoda Söhne, body'de Helvetica fallback = inconsistency
✓ Logoda Söhne weight 600, body'de Söhne weight 400 = full system

### Hata 3 — Liste-uzunluk system fallback
❌ `font-family: "Inter"` (no fallback) — load fail = serif default
✓ `font-family: "Inter Variable", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` (full chain)

### Hata 4 — `font-display: block` (FOIT — flash of invisible text)
❌ Block — text görünmeyene kadar font load bekler
✓ `font-display: swap` — system font ile başlar, custom font yüklenince swap (FOUT — flash of unstyled text, kabul edilebilir)

### Hata 5 — Multiple type scale ratios karıştırma
❌ H1 1.5, H2 1.25 ratio (inconsistent) = visual chaos
✓ Tek modular ratio (1.25 önerilir) — tüm hierarchy aynı orandan

### Hata 6 — Variable font axes hatalı kullanım
❌ `font-weight: 800` ile birlikte `font-variation-settings: "wght" 700` (conflict)
✓ Sadece bir tarafı kullan; modern: `font-variation-settings`

---

## KAYNAKLAR

- **Variable Fonts**: variablefonts.io (introduction + browser support)
- **Inter Font**: rsms.me/inter (Rasmus Andersson, full documentation)
- **Google Fonts**: fonts.google.com (free OFL fonts)
- **Future Fonts**: futurefonts.xyz (early-access modern fonts)
- **Type Scale**: typescale.com (modular scale generator)
- **Modular Scale**: modularscale.com (math-based scale)
- **Font Pair**: fontpair.co (curated pairings)
- **Type Sample**: typesample.com (try fonts on your text)
- **Google Variable Fonts**: fonts.google.com/variablefonts
- **Klim Type Foundry**: klim.co.nz (Söhne, GT Sectra alternatives)
- **Indian Type Foundry (ITF)**: indiantypefoundry.com (modern OFL fonts)

### Lisans Önemli
- **OFL (SIL Open Font License)**: Tam ücretsiz commercial use
- **Apache 2.0**: Aynı, ücretsiz commercial use
- **Adobe Originals**: Adobe Creative Cloud subscription
- **Commercial Seat**: Per-employee veya per-domain license (genelde $500-5000+ year)

> **Yeni marka için öneri**: OFL fonts (Inter, Geist, IBM Plex, General Sans) ile başla. Brand maturity'de commercial license'a geç.
