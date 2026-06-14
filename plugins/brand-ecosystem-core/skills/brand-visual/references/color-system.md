# Color System — Radix 12-Step Matematiksel Palet Mimarisi

> **Bu dosya `brand-visual` skill'inin Adım 5 işleminde her zaman aktif kullanılır.**
> Modern marka kimliği rastgele HEX kodları **vermez**. Matematiksel olarak hesaplanmış, semantik olarak kodlanmış, light/dark mode arasında otomatik invert eden bir sistemdir.

---

## Felsefi Temel

Çoğu logo tasarımcısı tarihsel olarak Pantone solid coated katalogunda 2-3 renk seçer ve bitirir. Bu **2010'ların paradigması**.

**2026'nın paradigması**: Renk bir **dijital sistem**dir. Renk seçimi, ardından gelen 60+ UI state'in (button hover, focus ring, selected, disabled, success/error/warning, body text vs heading text) hepsini eş zamanlı çözmek **zorundadır**.

Bunun cevabı **Radix Colors** mantığıdır: 12-step ölçek, her step'in semantik bir use-case'i, light + dark mode otomatik dengelemesi, WCAG/APCA contrast hesaplı.

> **Kaynak**: github.com/radix-ui/colors (Workos/Radix UI tarafından geliştirilmiş, Apache-2.0 lisanslı)

---

## 12-STEP ÖLÇEK SEMANTİĞİ

Radix tarafından kanonik olarak tanımlanmış. Her step **belirli bir UI use-case için tasarlanmıştır**:

| Step | Use Case | Detay |
|------|----------|-------|
| **1** | App background | Sayfa zemini (en açık ton, light mode) / en koyu (dark mode) |
| **2** | Subtle background | Alt-section background, sidebar, modal back |
| **3** | UI element background (default) | Card, panel, input field default state |
| **4** | UI element background (hover) | Hover üzerine açılan state |
| **5** | UI element background (pressed/selected) | Active/pressed/checked |
| **6** | Subtle border (non-interactive) | Sidebar/header/card divider |
| **7** | Subtle border (interactive) | Input field border default |
| **8** | Strong border / focus ring | Focus state, strong divider |
| **9** | **Solid action color** | **PRIMARY BRAND** — button background, key highlight |
| **10** | Solid hover | Step 9'un hover state'i |
| **11** | Low-contrast text | Body text on Step 1-2 background, **APCA Lc 60** (WCAG AA) |
| **12** | High-contrast text | Heading text, emphasized text, **APCA Lc 90** (WCAG AAA) |

> **Kanon**: Step 11 ve 12, aynı scale'in Step 1 veya 2 background'u üzerinde **garanti** APCA Lc 60 ve Lc 90 kontrast sağlar. Bu, paletin **inherent accessibility** özelliğidir.

---

## RADIX SCALE ANATOMİSİ

Bir Radix scale (örn: blue) **30 değişken** içerir:

| Suffix | Açıklama | Örnek (blue) |
|--------|----------|--------------|
| `1-12` | Solid scale (light mode) | `--blue-1` ... `--blue-12` |
| `1Dark-12Dark` | Solid scale (dark mode) | `--blue-1` ... `--blue-12` (dark stylesheet'te aynı isim, farklı değer) |
| `A1-A12` | Alpha (transparent) variants — light | `--blue-a1` ... `--blue-a12` |
| `DarkA1-DarkA12` | Alpha variants — dark | `--blue-a1` ... `--blue-a12` (dark) |

> **Alpha variants** çok önemli: bir transparent background'un üstüne hue eklemek, marka rengini farklı surface'lerde **doğal** korur.

---

## RADIX'in 28 SCALE'i

Radix Colors **28 farklı renk scale'i** sağlar (her biri 12-step):

### Hue Scales (24 colors)

| Warm | Cool | Special |
|------|------|---------|
| Tomato | Iris | Gold |
| Red | Indigo | Bronze |
| Ruby | Blue | Brown |
| Crimson | Cyan | Orange |
| Pink | Teal | Yellow |
| Plum | Jade | Amber |
| Purple | Green | Lime |
| Violet | Grass | Mint |
|  | Sky | |

### Gray Scales (6 grays — kritik!)

Gray seçimi **brand color'a göre** yapılır. Cool brand → cool gray; warm → warm gray:

| Gray Scale | Karakter | Uyumlu Brand Hue |
|------------|----------|------------------|
| **Gray** | Pure neutral | Tüm hue'lar (default) |
| **Mauve** | Subtle warm purple-grey | Pink, Plum, Purple, Violet, Iris |
| **Slate** | Subtle cool blue-grey | Blue, Sky, Cyan, Teal |
| **Sage** | Subtle warm green-grey | Green, Grass, Jade, Mint |
| **Olive** | Subtle warm yellow-grey | Yellow, Amber, Lime |
| **Sand** | Subtle warm orange-grey | Tomato, Red, Crimson, Orange, Brown |

> **Kural**: Brand color seçildikten sonra, yukarıdaki tablodan optimal gray seçilir. Bu, **2010'ların** "her tasarımda neutral gray" yaklaşımının üstündedir — modern markalar **brand-imbued** gray kullanır.

### Bright Scales (4 brighter variants)
Daha doygun varyantlar: Sky, Mint, Lime, Yellow brand renkler için ekstra parlaklık.

---

## BRAND COLOR SEÇİMİ — SİSTEMATİK YAKLAŞIM

### Step 1 — Hue Belirleme (Arketip → Renk)

Arketipler ile uyumlu hue rehberi:

| Arketip | Recommended Hues | Avoid |
|---------|------------------|-------|
| Innocent | Sky, Mint, Yellow (light) | Black, deep red |
| Everyman | Brown, Orange, Yellow, Sand | Pastel, neon |
| Hero | Red, Crimson, Iris, Indigo (bold) | Soft pastel |
| Outlaw | Black/Slate dominant + Red/Crimson accent | Pastel, soft |
| Explorer | Brown, Bronze, Olive, Sage, Sand | Hot pink, neon |
| Creator | Multi-color OR pure black-white | Generic blue |
| Ruler | Indigo, Violet, Iris (deep), Bronze, Gold | Pastel, neon |
| Magician | Purple, Violet, Iris (mystical) | Generic warm |
| Lover | Crimson, Ruby, Pink, Plum, Bronze | Cold blue |
| Jester | Yellow, Orange, Lime, Sky (vivid) | Black dominant |
| Caregiver | Sky, Mint, Sage, Pink (soft) | Black, harsh red |
| Sage | Indigo, Slate, Mauve (academic) | Bright pastel |

### Step 2 — Saturation Tier

Marka kişiliğinin **enerji seviyesine** göre saturation tier:

- **Quiet / Sophisticated** → Slate, Mauve gibi grey-tinted brand colors (örn: Linear purple, Notion gri)
- **Confident / Standard** → Indigo, Iris, Crimson gibi medium-saturated (örn: Stripe, Figma)
- **Bold / Energetic** → Tomato, Lime, Sky gibi high-chroma (örn: Slack rainbow, Mailchimp yellow)

### Step 3 — Single Hue vs Dual Hue

**Single Hue Strategy** (Anthropic, Linear, Notion):
- Tek bir brand hue + paired gray
- Tüm UI hierarchy 12-step ile çözülür
- Disipliner, modern, scalable
- Önerilir: Yeni markalar, B2B SaaS, professional services

**Dual Hue Strategy** (Mailchimp yellow + black, Slack 11-color, NBC peacock):
- Primary + accent (genelde primary'nin complementary'si)
- Marketing material zenginliği
- Daha karmaşık system management
- Önerilir: Consumer brands, established markalar, multi-product

> **Kural**: Yeni marka için **Single Hue Strategy** önerin. Multi-color sistem ileride eklenebilir, ama başlangıçta restraint disiplini güçlendirir.

---

## CUSTOM PALETTE GENERATION (Radix Custom Palette Tool)

Radix bir online tool sağlar: https://www.radix-ui.com/colors/custom

### Process:
1. Bir base color seç (örn: `#5B5BD6` — Iris-inspired indigo)
2. Tool, **Light Mode 12-step** ve **Dark Mode 12-step** otomatik üretir
3. Algoritma:
   - Step 1-2: Background tones (very light / very dark)
   - Step 3-5: Component background gradients
   - Step 6-8: Border progression
   - Step 9: **Solid hue** (en doygun, en saf base)
   - Step 10: Slightly darker (hover state)
   - Step 11-12: Text optimized (APCA contrast guaranteed)

### Algoritmanın çekirdek mantığı:
- **OKLCH color space** kullanılır (perceptually uniform, hue-stable)
- Light mode: Lightness 99% → 25% (azalan)
- Dark mode: Lightness 8% → 95% (artan, ama hue korunur)
- Chroma (saturation) Step 1-8 düşük, Step 9-10 maksimum, Step 11-12 düşük (text okunabilirlik)

> **Manual hesaplama** için: `scripts/palette_generator.py` Radix algoritmasına yakın 12-step palette üretir.

---

## DARK MODE — FIRST-CLASS CITIZEN

> **Felsefe** (Muzli, 2026): "Dark mode is not a variant of light. It is a first-class design system context with its own visual logic, its own elevation language, and its own token architecture."

### Dark Mode Hatalı Yaklaşım
- Light mode'u invert et → kontrast bozulur, brand hue bulanıklaşır
- Sadece background siyah yap → renk paleti bütünleşmez
- Tüm parlaklıkları azalt → "dim" görünür, OLED avantajı kullanılmaz

### Dark Mode Doğru Yaklaşım
1. **Pure black (#000000) background** — OLED ekranlarda **0 watt** tüketim (Google ölçümü: dark mode'da YouTube **%43 daha az pil** kullanır OLED'de)
2. **Brand hue brightened** — dark mode'da brand rengi (Step 9) **daha parlak** olmalı (Light mode'da Step 9 koyu indigo ise, dark mode'da hafif lavender'a kayar — chroma artırılır, lightness yükseltilir)
3. **Text contrast prioritized** — Step 11 ve 12 dark mode'da **çok parlak** olmalı; Step 12 light mode'da Step 1'e karşı APCA Lc 90, dark mode'da da Step 1'e karşı **aynı** Lc 90 garanti

### Otomatik Theme Switch
```css
/* Light mode (default) */
:root {
  --brand-1: #FCFCFD;
  --brand-9: #5B5BD6;
  --brand-12: #2E2E80;
}

/* Dark mode (class-based veya media query) */
[data-theme="dark"] {
  --brand-1: #0D0D0F;
  --brand-9: #6E56CF;  /* slightly brighter */
  --brand-12: #E2E2FC;
}

/* Veya OS-level preference */
@media (prefers-color-scheme: dark) {
  :root {
    --brand-1: #0D0D0F;
    /* ... */
  }
}
```

> **Best practice**: **Class-based** (`data-theme="dark"`) öneriyoruz çünkü kullanıcıya **manuel toggle** imkanı verir (sistem-level otomatik mode'un tercih edilmediği case'ler için).

---

## ACCENT COLOR PAIRING

Brand color seçildikten sonra **accent color** seçimi sistematik olmalı:

### Yaklaşım 1 — Complementary (Tradisyonel)
Color wheel'de 180° karşı:
- Indigo (240°) ↔ Yellow (60°)
- Blue (210°) ↔ Orange (30°)
- Red (0°) ↔ Cyan (180°)

> **Not**: Complementary çok kontrastlı olduğu için **küçük dozda** kullanılır (60-30-10 paletinde 10% accent).

### Yaklaşım 2 — Analogous (Modern)
Color wheel'de 30-60° komşu:
- Indigo + Violet
- Blue + Cyan
- Crimson + Pink

> Daha **harmonious**, brand cohesion güçlü.

### Yaklaşım 3 — Triadic (Cesur)
120° eşit aralıklı 3 renk:
- Indigo + Crimson + Yellow
- Sky + Lime + Pink

> **NBC peacock** veya **Mailchimp** gibi multi-color sistemler için.

### Yaklaşım 4 — Monochromatic (Sophisticated)
Sadece **brand hue** + **gray pair**:
- Linear: Purple + Mauve gray
- Anthropic: Terra-cotta + Sand gray
- Stripe: Indigo + Slate gray

> En **disipliner**, en **modern**. Önerilen default.

---

## FUNCTIONAL COLORS (Semantic Status)

UI'da **brand-independent** olarak gerekli:

| Token | Use | Light Mode | Dark Mode |
|-------|-----|------------|-----------|
| `--success-9` | Success state | Grass `#46A758` | Grass dark `#4CC367` |
| `--error-9` | Error state | Red `#E5484D` | Red dark `#FF6369` |
| `--warning-9` | Warning state | Amber `#F1A10D` | Amber dark `#FFB224` |
| `--info-9` | Info state | Brand-9 OR Sky `#0090FF` | Brand-9 OR Sky dark |

> **Kural**: Brand color **DEĞİL** functional color olarak kullanılır (success ≠ brand). Bu, accessibility (renk-blind users) ve global UX (standart sembollendirme) için kritik.

---

## CONTRAST ACCESSIBILITY — WCAG 2.2 + APCA

### WCAG 2.2 (Web Content Accessibility Guidelines, 2023 revize)

| Standard | Kontrast Oranı | Use |
|----------|---------------|-----|
| AA (normal text) | 4.5:1 | Body text |
| AA (large text) | 3:1 | Heading > 18pt veya bold > 14pt |
| AA (UI elements) | 3:1 | Borders, icons, focus indicators |
| AAA (normal text) | 7:1 | Yüksek erişilebilirlik standart |
| AAA (large text) | 4.5:1 | Aynı |

### APCA (Accessible Perceptual Contrast Algorithm) — Modern Alternatif

WCAG'in **simplified** ve **font-weight aware** halefi (W3C tarafından AAA standardına dahil ediliyor):

| Lc Değer | Use Case |
|----------|----------|
| **Lc 90** | High-contrast text (heading, body important) — **Step 12 garanti** |
| **Lc 75** | Body text emphasis |
| **Lc 60** | Body text minimum (low-contrast) — **Step 11 garanti** |
| **Lc 45** | Labels, placeholder |
| **Lc 30** | Disabled text, very low-emphasis |

> Radix scale'leri **Lc 60 ve Lc 90** garanti eder Step 11/12 için Step 1/2 background'a karşı. Bu, manual hesaplamayı eler.

### Contrast Hesaplama
`scripts/wcag_contrast.py` script'i HEX color pair için:
- WCAG AA/AAA pass/fail
- APCA Lc value
- Recommended use cases

---

## 60-30-10 PALET REÇETESİ

UI design'da klasik kural:

- **60%** — Dominant background (`--gray-1` veya `--gray-2`)
- **30%** — Secondary (`--gray-12` text + `--gray-6` borders + `--brand-3/4` cards)
- **10%** — Accent (`--brand-9` solid actions, key highlights)

> **Brand-9 kullanımı kısıtlı** — bu, brand color'un her yerde olması gerektiği yanlış inancına karşı disiplindir. Brand-9 **özel anlam taşır** (CTA, primary action). Her yerde olursa, hiçbir yerde özel olmaz.

### Contoh Application (Brand color = Iris)

```
┌──────────────────────────────────────────┐
│  ← gray-1 background (60%)              │
│                                          │
│  ┌─[gray-12 text]─────────────────────┐ │  ← gray-12 text (30%)
│  │  Heading                           │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Body text in gray-11                   │
│  with [iris-9 link] inside              │  ← iris-9 link (10%)
│                                          │
│  ┌────────────────────┐                 │
│  │  iris-9 BUTTON     │ ← iris-9 (10%) │
│  └────────────────────┘                 │
│                                          │
│  ─── gray-6 divider ───                 │  ← gray-6 borders (30%)
│                                          │
└──────────────────────────────────────────┘
```

---

## OKLCH MODERN COLOR SPACE

CSS Color Module Level 4 (2024+) ile artık `oklch()` syntax kullanılabilir:

```css
:root {
  --brand-9: oklch(56% 0.20 270);  /* Lightness 56%, Chroma 0.20, Hue 270° (indigo) */
}
```

**Avantajlar**:
- **Perceptually uniform** — OKLCH'da Lightness 56% gerçekten "orta açıklık" insan algısına göre (HSL'de değil)
- **Hue-stable** — Chroma değiştirsen bile hue kaymaz (HSL'de kayıyor)
- **Wide gamut** — P3 ekranlarda daha geniş renk spektrumu

**Browser support** (Nisan 2026): Chrome 111+, Safari 15.4+, Firefox 113+ — production-ready.

> Modern marka tokens'larında **HEX + OKLCH dual** export öneriyoruz (HEX legacy support, OKLCH modern features).

---

## NÖROMARKETİNG: RENK PSİKOLOJİSİ İPUCU

> **Uyarı**: Renk psikolojisi **kültürel ve bağlama bağlıdır**. Aşağıdaki rehber **Batı + global metropolitan tüketici** için tipik çağrışımlar; her market için doğrulayın.

| Renk | Tipik Çağrışım | Sektör Aşırı Kullanım | Disruption Önerisi |
|------|---------------|----------------------|-------------------|
| **Mavi (Indigo, Sky, Blue)** | Güven, profesyonellik, sakinlik | Fintech, healthcare, tech (over-saturated) | Daha cesur saturation, beklenmedik accent (sarı, kırmızı) |
| **Kırmızı (Crimson, Red, Tomato)** | Acil, tutku, güç, iştah | F&B (Coca-Cola), entertainment | Soft pastel kırmızı (Crimson 9), monochrome ile dengeleme |
| **Yeşil (Grass, Green, Jade, Mint)** | Doğa, sağlık, büyüme, finans | Eco, wellness, fintech | Cesur deep green (forest), tek-renk minimalism |
| **Sarı (Yellow, Amber)** | Optimizm, dikkat, ucuzluk | Fast food, sale signs | Bold yellow + black contrast (Anthropic terra-cotta logic, IKEA) |
| **Mor (Purple, Violet, Iris)** | Lüks, mistik, vizyon | Beauty, gaming | Modern usage: tech (Stripe, Linear) lukse alternative |
| **Turuncu (Orange, Tomato)** | Enerji, eğlence, samimiyet | F&B, kids brands | Sophisticated burnt orange (Anthropic), warm minimal |
| **Pembe (Pink, Crimson)** | Romantik, oyuncu, feminine | Beauty, women products | Brutalist pink (Glossier — millennial pink), unisex modern |
| **Kahverengi (Brown, Bronze, Sand)** | Doğal, premium, organik | Eski-school, vintage | Modern earthy palette (Aesop) |
| **Siyah (Slate, Gray, Mauve)** | Lüks, otorite, modern | Minimalism over-used | Black + warm accent (terra-cotta, gold) |
| **Beyaz** | Saflık, minimalism, lüks | Tech minimalism over-used | Off-white (cream, ivory) ile sıcaklık |

---

## RAPOR ÇIKTI ŞABLONU (Adım 5'te kullan)

```markdown
## Renk Sistemi

**Primary Brand Color**: [#XXXXXX] · OKLCH: oklch(L% C H) · HSL: hsl(H S% L%)
**Color name**: [Brand-spesifik isim — örn: "Curio Indigo", "Lumora Coral"]

**Seçim rasyoneli**: [80-120 kelime]
- Hue rationale: [arketip uyumu]
- Saturation tier: [marka enerjisi]
- Sektör konteksti: [klişeden ayrışma stratejisi]

### Light Mode Scale (1-12)
[Tam tablo, scripts/palette_generator.py çıktısı]

### Dark Mode Scale (1-12)
[Tam tablo, brightened brand-9, inverted backgrounds]

### Accent Color
**HEX**: [#YYYYYY] · "[isim]"
**Pairing strategy**: [Complementary / Analogous / Triadic / Monochromatic]
[12-step accent scale tablo]

### Gray Pairing
Recommended: **[Slate / Mauve / Sage / Olive / Sand]**
[Rasyonel: brand hue → gray pairing rule]
[12-step gray scale tablo]

### Functional Colors
| Token | Light | Dark | Source |
|-------|-------|------|--------|
| --success-9 | #46A758 | #4CC367 | Radix Grass |
| --error-9 | #E5484D | #FF6369 | Radix Red |
| --warning-9 | #F1A10D | #FFB224 | Radix Amber |
| --info-9 | [brand-9] | [brand-9 dark] | Brand or Sky |

### 60-30-10 Application Recipe
- **60%**: --gray-2 backgrounds
- **30%**: --gray-12 text + --gray-6 borders
- **10%**: --brand-9 actions + --brand-3 highlights
```

---

## EXPORT FORMAT — DESIGN TOKENS

`scripts/palette_generator.py` çıktısı multi-format:

### CSS Custom Properties
```css
:root {
  --brand-1: #FCFCFD;
  --brand-2: #F9F9FB;
  /* ... */
  --brand-9: #5B5BD6;
  --brand-12: #2E2E80;
}
```

### Tailwind Config
```javascript
{
  brand: {
    1: 'var(--brand-1)', /* veya direkt HEX */
    9: 'var(--brand-9)',
    /* ... */
  }
}
```

### W3C Design Tokens JSON
```json
{
  "color": {
    "brand": {
      "1": { "$value": "#FCFCFD", "$type": "color" },
      "9": { "$value": "#5B5BD6", "$type": "color", "$description": "Primary action" }
    }
  }
}
```

### Figma Variables JSON (Tokens Studio plugin compatible)
```json
{
  "global": {
    "brand-1": { "value": "#FCFCFD", "type": "color" },
    "brand-9": { "value": "#5B5BD6", "type": "color" }
  }
}
```

> **Multi-format export** sağlamak, **engineer-designer handoff**'ı sürtüşmesiz yapar. Bir tasarım stüdyosuna teslim ettiğinizde, bu hazır JSON'lar **direkt entegrasyon** sağlar.

---

## YAYGIN HATALAR

### Hata 1 — Sadece HEX vermek
❌ "Brand color: #5B5BD6, dark accent: #2E2E80"
✓ Tam 12-step + light/dark mode + accent + gray + functional + tokens

### Hata 2 — Light mode'u invert ederek dark mode
❌ Light Step 1 #FCFCFD → Dark Step 1 #030302 (basit invert)
✓ Dark Step 1 #0D0D0F (OLED-optimized pure black, brand-tinted)

### Hata 3 — Brand color'u her yerde kullanmak
❌ Brand-9 background, brand-9 text, brand-9 border (her yerde)
✓ 60-30-10 disiplini: brand-9 sadece **CTA + key highlights**

### Hata 4 — Gri = neutral gray
❌ Sadece neutral gray kullanmak
✓ Brand hue'ya uyumlu **Slate / Mauve / Sage / Olive / Sand** seçimi

### Hata 5 — Functional color = brand color
❌ Success state = brand green
✓ Functional colors **brand'den ayrı** semantic system

---

## KAYNAKLAR

- **Radix Colors**: github.com/radix-ui/colors
- **Radix Custom Palette Tool**: radix-ui.com/colors/custom
- **APCA**: github.com/Myndex/apca-w3
- **OKLCH Color Picker**: oklch.com
- **Coolors**: coolors.co (genel palette inspiration, ama Radix mantığı için yetersiz)
- **W3C Design Tokens**: design-tokens.github.io/community-group

---

## v1.3 EKLENTİLERİ — 2026 Adaptive Era Katmanları

### 1. Pantone Cloud Dancer (2026 Color of the Year)

**HEX**: `#F3F2EA`
**RGB**: `243, 242, 234`
**OKLCH**: `oklch(95.1% 0.013 89)`
**CMYK yaklaşımı**: `2, 2, 5, 0`

**Neden önemli?** 2026'da Pantone'un seçtiği COY — "an extension of white space itself — clarity, calm, openness." Warm neutral. **Pure white alternatifi** olarak 2026'da yaygın kullanılıyor.

**Ne zaman pure white yerine Cloud Dancer?**
- Warm Neo-Minimalism stratejisi uygulanıyor (Trend 2)
- Earthmark Organic sensibility (Trend 5)
- Luxury / Wellness / Lifestyle sektörleri
- Printed collateral uncoated letterpress paper (doğal cream-warm renk eşleşir)
- "Sterile clean" yerine "warm clean" isteniyor

**Light mode Step 1 (page background) alternatifi olarak Cloud Dancer**:
```
gray-1 pure white:       #FCFCFD (cool, technical)
gray-1 Cloud Dancer:     #F3F2EA (warm, welcoming)  ← v1.3 warm option
gray-1 Off-white:        #F9F8F4 (between two)
```

**Palette eşleşmeleri**:
- Cloud Dancer + deep burgundy → Lover / Luxury
- Cloud Dancer + sage green → Innocent / Caregiver
- Cloud Dancer + graphite #333331 → Sage / Ruler
- Cloud Dancer + terracotta → Earthmark / Explorer

**Dark mode karşı kutup**: Cloud Dancer light mode kullanıldığında dark mode Step 1 olarak `#1A1A17` (warm graphite) tercih edilir — sadece pure black değil, warm dark counterpart.

**UMMP içinde kullanım**:
```
The coloring is solid [brand primary] on a Cloud Dancer cream backdrop,
with absolutely flat single-tone fill...
```

---

### 2. CVD (Color Vision Deficiency) Simulation Layer

**Neden zorunlu?** 2026 Neuro-Inclusive Design doktrini (Trend 12). Erkeklerin ~8%'i, kadınların ~0.5%'i color vision deficiency yaşar. Brand identity **onlar için de** çalışmalı.

### Üç Ana CVD Tipi

| Tip | Açıklama | Etkilenen | Görsel Sonuç |
|-----|---|---|---|
| **Protanopia** | Red-blind | ~1% erkek | Red → dark gray/brown, red-green confusion |
| **Deuteranopia** | Green-blind | ~1% erkek | Green → beige/gray, red-green confusion |
| **Tritanopia** | Blue-blind | <0.01% | Blue → green/gray, blue-yellow confusion |

### CVD-Safe Palette Design Prensipleri

1. **Hue farkı yetmez, luminance farkı şart** — brand + gri/siyah + aksan renkler arasında luminance ladder'ı olmalı (Radix 12-step zaten bunu sağlar)
2. **Red-green çifti risky** — arketip olarak Innocent/Nature/Growth'a red-green kombo ilkesel çekici ama CVD'de ayrıştırılamaz
3. **Blue-yellow complementary güvenli** — çoğu CVD tipi için ayrıştırılabilir
4. **Functional colors için sadece renk değil, ikon/pattern** — "Success" = yeşil + ✓, "Error" = kırmızı + ✗ (sadece renge güvenme)
5. **Brand color + high-contrast gri** → safe minimum (tek brand color + Step 11-12 text)

### CVD Simulation Test Protocol

Her finalize edilmiş palette için:

```bash
# scripts/wcag_contrast.py --cvd flag ile (v1.3)
python3 scripts/wcag_contrast.py palette.json --cvd
```

Çıktı:
```
Normal vision:         brand-9 vs gray-1 → APCA Lc 78 ✓
Protanopia sim:        brand-9' vs gray-1 → APCA Lc 72 ✓
Deuteranopia sim:      brand-9' vs gray-1 → APCA Lc 74 ✓
Tritanopia sim:        brand-9' vs gray-1 → APCA Lc 79 ✓

brand-9 vs brand-12:
Normal vision:         APCA Lc 85 ✓
Protanopia:            APCA Lc 62 ⚠️  (threshold ≥ 75 violated)
Deuteranopia:          APCA Lc 65 ⚠️  (threshold ≥ 75 violated)
Action: Accent color için brand-9 + brand-12 kombosu önerilmez CVD kullanıcılar için
```

### Alternatif CVD-Test Tools

- **Coblis Color Blindness Simulator**: color-blindness.com/coblis-color-blindness-simulator
- **Figma Stark plugin**: native Figma CVD simulation
- **Chrome DevTools**: Emulation → Vision deficiencies
- **iOS/Android**: OS-level color filter testing

### CVD Pass/Fail Kriterleri

- [ ] Primary CTA (brand-9 on gray-1): APCA Lc ≥ 75 across Normal + 3 CVD types
- [ ] Secondary buttons: APCA Lc ≥ 60 across Normal + 3 CVD types
- [ ] Information hierarchy (body vs. headline): minimum 3:1 luminance ratio (CVD-robust)
- [ ] Functional colors (success/error/warning/info): her birinde **ikon + renk** kombinasyonu
- [ ] Logo mark monokrom varyantı: CVD-invariant by design (tek renk)

### Output'a Ek Bölüm (Adım 5 Extended)

v1.3'te brand identity report'un renk bölümüne ek:

```markdown
### CVD Audit Results

| Test | Normal | Protanopia | Deuteranopia | Tritanopia | Pass |
|------|:-:|:-:|:-:|:-:|:-:|
| brand-9 on gray-1 (APCA Lc) | 78 | 72 | 74 | 79 | ✓ |
| brand-9 on brand-12 | 85 | 62 | 65 | 84 | ⚠️ |
| Success state | 76 | 58 | 60 | 75 | ⚠️ |
| Error state | 78 | 80 | 78 | 74 | ✓ |

**Doktrin**: APCA Lc ≥ 75 tüm CVD simülasyonlarında zorunlu primary actions
için. Failure pattern'leri üzerine revize — alternatif hue/luminance
kombinasyonları önerildi.

**Icon+color redundancy uygulanmış**: Success ✓, Error ✗, Warning ⚠, Info ℹ
```

---

### 3. Warm Neo-Minimalism Palette Tuning

v1.3'te ek öneri: Radix 12-step paletleri **warm-biased** versiyonlar üretmek.

**Standard gri (cool)** vs **Warm gray (Trend 2 için)**:

```
gray-1 cool:   #FCFCFD  (standard Radix Slate)
gray-1 warm:   #FAF9F5  (warm Radix Mauve-tinted)  ← 2026 warm neo-minimal

gray-12 cool:  #1D1F24  (standard Slate)
gray-12 warm:  #222220  (warm graphite)            ← 2026 warm neo-minimal
```

Warm-biased Radix scale için: Mauve, Sand, Olive variants seçin (Slate yerine). Bu, 2026 "warmth-over-sterility" doktrini ile hizalanır.

---

### 4. Earthmark Palette Templates (Trend 5)

Hazır palette templates:

**Sage Earthmark** (Innocent/Caregiver):
```
Primary:    #4A6B4E (deep sage)
Secondary:  #D4C9A8 (oat cream)
Accent:     #C69B6D (warm clay)
Neutral:    #F3F2EA (Cloud Dancer)
Dark:       #2D3B2E (forest shadow)
```

**Terracotta Earthmark** (Explorer/Creator):
```
Primary:    #B25C3E (warm terracotta)
Secondary:  #F4E8D5 (linen)
Accent:     #2E4A35 (deep forest)
Neutral:    #FAF7F1 (bone white)
Dark:       #2A1F1A (coffee grounds)
```

**Sand Earthmark** (Everyman/Innocent):
```
Primary:    #9B8268 (warm sand)
Secondary:  #E8DFD0 (oatmeal)
Accent:     #6B4A3B (cedar brown)
Neutral:    #F3F2EA (Cloud Dancer)
Dark:       #2C2622 (charred wood)
```

Bu template'ler **başlangıç** — marka arketip + sektörüne göre Radix 12-step full scale genişletilir.

---

> **v1.3 Kapanış**: Color system artık sadece "primary brand color + 12 step" değil. 2026'da bir brand palette: **warm-vs-cool seçimi × Cloud Dancer neutral mode × CVD-robust hierarchy × functional redundancy (icon+color) × adaptive variant support**. Disiplin yeni standart.
