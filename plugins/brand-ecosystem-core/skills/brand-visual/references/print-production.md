# Print Production — Pantone, CMYK, Paper Stock, Foil/Emboss

> **Bu dosya `brand-visual` skill'inin Adım 5 kapsamında, ekran/dijital kimliğinden **fiziksel üretime** geçiş için yüklenen referansıdır.**
>
> Marka çıktıları: business cards, packaging, foyer signage, billboards, branded merchandise, event collateral. Hepsi **fiziksel substrate**larda üretilir; ekran rengi orada hiç beklediğiniz gibi görünmez.

---

## Felsefi Temel

> "Renk ekranda RGB; printer'da CMYK; spot inkte Pantone; tekstilde TPX; plastikte yine farklı. Production-grade marka kimliği **tüm bu uzayları yönetir**." — brand-visual print doktrini

Pantone'ın 2026 Color of the Year **Cloud Dancer (PMS 11-4201)** beyazı seçmesi tesadüf değil — minimalist tasarımın yükselişi (özellikle marka kimliklerinde). Ama "beyaz", paper stock, ink, finish kombinasyonuna göre **on farklı görüntüye** dönüşür. Bu skill o kombinasyonları sistemik olarak yönetmenize yardım eder.

---

## Renk Sistemleri Karşılaştırması

| Sistem | Domain | Gamut | Tutarlılık | Örnek HEX/Code |
|--------|--------|-------|-------------|-----------------|
| **RGB / sRGB** | Ekran (web, mobil) | Wide | Cihaz-bağımlı (calibration) | `#5B5BD6` |
| **CMYK** | Print (offset, digital) | Narrower than RGB | Press-bağımlı (ICC profile) | `C57 M57 Y0 K16` |
| **Pantone PMS C** | Spot ink, coated paper | ~2,390 colors | Standardize | `PMS 2725 C` |
| **Pantone PMS U** | Spot ink, uncoated paper | ~2,390 colors | Standardize (looks duller) | `PMS 2725 U` |
| **Pantone TPX/TPG** | Tekstil/fashion | ~2,310 colors | Substrate-tested | `Pantone 18-3949 TPG` |
| **OKLCH** | Modern web (2023+) | Perceptually uniform | Cihaz-bağımlı | `oklch(54% 0.18 278)` |

### Pantone'un Premium Pozisyonu

Pantone Matching System (PMS), 1963'te **Lawrence Herbert** tarafından geliştirildi. Standardize **spot color** sistemi — her renk fiziksel ink karışımı olarak tanımlanır. Pantone Formula Guide (fiziksel fan deck) kritik production aracıdır:
- **Coated (C)**: Parlak/satin coated paper'da
- **Uncoated (U)**: Mat/uncoated paper'da
- **TPG**: Textile Paper Glossy (tekstil için paper proxy)
- **TPX**: Textile Paper Cotton (eski standart, deprecated)
- **Metallic, Neon, Pastel** seri

> **2026 Color of the Year**: PMS 11-4201 Cloud Dancer (TCX) ≈ HEX `#F0EEE9`, CMYK ≈ `0/1/3/6`. Pantone'un ilk **beyaz** Color of the Year'ı — minimalist tasarımın 2026'daki yükselişini sembolize ediyor.

---

## Renk Conversion Pipeline'ı

### sRGB HEX → CMYK
**Conversion** ICC profile'a göre değişir:
- **GRACoL (Generic offset, US Sheetfed Coated)** — En çok kullanılan
- **SWOP (US Web Coated)** — Magazine/web press
- **FOGRA39 (Europe coated)** — EU offset
- **Japan Color** — Asya pazarı

**Pratik kural**: Adobe Illustrator/Photoshop'ta `Edit > Convert to Profile > CMYK` ile dönüştür. Ama **gerçek press output** her zaman printer ile **proof** check edilmeli.

### sRGB HEX → Pantone PMS
Bu skill `scripts/pantone_matcher.py` aracılığıyla:
- ΔE CIEDE2000 algoritması ile en yakın 3-5 PMS bulur
- ΔE < 2.0 = Pantone resmi tolerance hedefi (excellent match)
- ΔE > 5.0 = "no good PMS match — consider custom spot ink"

```bash
python scripts/pantone_matcher.py "#5B5BD6" --top 5 --include-cmyk
```

### Pantone PMS → CMYK
Pantone Formula Guide'ın her PMS için CMYK approximation'u var. Ama **30% PMS color CMYK ile reproduce edilemez** (gamut dışında — özellikle saturated reds, oranges, deep blues).

---

## Paper Stock — GSM ve Material

### Paper Weight (GSM = Grams per Square Meter)

| GSM | İsim | Kullanım | Hissi |
|-----|------|----------|-------|
| 80-100 | Bond/Letterhead | A4 ofis kağıdı, mektup | Standart, ince |
| 120-150 | Light cardstock | Flyer, broşür | Hafif kalın |
| 200-250 | Medium cardstock | Postcard, business card light | Premium hissi başlangıç |
| 300-350 | Heavy cardstock | Business card standart, packaging | Lüks hissi |
| 400-600 | Ultra heavy | Premium business card, gift card | "Deluxe" |
| 600+ | Triplexed (3-layer) | Mega-premium business card (Moo Luxe gibi) | Statement |

### Coated vs Uncoated

**Coated (Glossy/Satin/Matte)**:
- Surface clay-coated → ink topta oturur
- **Pantone C** colors burada matched
- Renk parlak, doygun
- Kullanım: magazine, packaging, marketing collateral
- Trade-off: yazma dostu değil, parmak izi gösterir

**Uncoated (Natural texture)**:
- Surface unprocessed → ink fiber'a emer
- **Pantone U** colors burada matched (renk daha mat görünür)
- Doğal, "honest" feel
- Kullanım: business cards (modern luxury), letterhead, craft brand'ler
- Trade-off: renk softer; coated palette doğrudan transfer olmaz

### Specialty Paper Stocks

| Stock | Karakter | Use Case |
|-------|----------|----------|
| **Cotton-rag (Crane's, Mohawk)** | Ultra-premium, taktil | Lüks business card, wedding invitations |
| **Recycled (kraft, FSC-certified)** | Eco signal, doğal renk | Sustainability brand'ler, packaging |
| **Soft-touch laminated** | Velvet feel | Premium book covers, business cards (Moo) |
| **Letterpress paper (cotton thick)** | Deep impression için yumuşak | Letterpress printing |
| **Vellum** | Translucent | Wedding overlay, premium menus |
| **Synthetic (Yupo)** | Tear-resistant, waterproof | Maps, restaurant menus, outdoor |

> Reference: **Mohawk** (mohawkconnects.com), **Neenah** (neenahpaper.com), **Crane's** — premium paper houses; her marka projesinde swatch book gönderirler.

---

## Print Methods

### Offset Lithography (Klasik)
- **Volume**: 500+ adet (cost-effective)
- **Quality**: En yüksek (tight color, sharp detail)
- **Spot color support**: Evet (Pantone direkt)
- **Cost**: Setup pahalı, per-unit ucuz
- **Use**: Magazine, packaging, premium business cards, brand books

### Digital Print (HP Indigo, Xerox iGen)
- **Volume**: 1+ adet (anlık)
- **Quality**: Çok iyi (CMYK + extended gamut)
- **Spot color**: Sınırlı simülasyon
- **Cost**: Setup ucuz, per-unit middle
- **Use**: Short-run brand collateral, on-demand business cards, customized print

### Letterpress (Heritage)
- **Volume**: 50-1000 (artisan)
- **Quality**: Deep impression visible
- **Spot color**: Pantone (single ink rolls)
- **Cost**: Yüksek setup + per-unit
- **Use**: Wedding invitations, ultra-premium business cards (Crane's)

### Foil Stamping
- **Method**: Heated die transfers metallic foil
- **Color**: Gold, silver, copper, holographic, custom
- **Cost**: Premium add-on (per-color setup)
- **Use**: Luxury packaging, premium business cards, certificate seals

### Embossing / Debossing
- **Embossing**: Kabartma (relief raised)
- **Debossing**: Içe basma (relief sunken)
- **Cost**: Die création + per-impression
- **Use**: Premium logo treatment, luxury packaging, wedding stationery

### UV Coating (Spot UV)
- **Method**: UV-cured glossy spot on top of print
- **Effect**: Sembol parlak, çevre matte (tactile contrast)
- **Use**: Luxury packaging, premium business cards (logo glossy on matte body)

---

## brand-visual Print Spec Output Template

Adım 5 çıktısının "Print Production" bölümü:

```markdown
## Print Production Specification

### Color Conversions

| Brand Color | HEX (sRGB) | CMYK (GRACoL) | Pantone PMS C | Pantone PMS U | ΔE00 |
|-------------|------------|----------------|---------------|----------------|------|
| Primary     | #5B5BD6    | C57 M57 Y0 K16 | PMS 2725 C    | PMS 2725 U     | 6.75 |
| Accent      | #FFB400    | C0 M30 Y100 K0 | PMS 130 C     | PMS 130 U      | 1.20 |
| Text Dark   | #2E2E80    | C100 M100 Y28 K22 | PMS 2766 C | PMS 2766 U     | 2.85 |

> **Note**: Primary brand color #5B5BD6 has no Pantone match within ΔE 2.0
> tolerance — production options:
> 1. Use closest PMS 2725 C (acceptable but visibly different)
> 2. Use **custom spot ink** mixed by printer (Pantone Color Bridge formula)
> 3. Use CMYK conversion only (digital press, no spot color)

### Recommended Paper Stock
- **Business cards**: 350gsm uncoated cotton, letterpress-friendly
- **Stationery (letterhead)**: 120gsm uncoated, FSC-certified
- **Brand book**: 150gsm coated matte interior, 350gsm soft-touch cover
- **Packaging**: 400gsm SBS (Solid Bleached Sulfate) coated

### Print Methods
- **Business cards**: Letterpress (deep deboss for logo) on cotton stock
- **Brochure**: Offset CMYK + Pantone 2725 C (brand color spot)
- **Packaging**: Offset CMYK, gloss UV varnish on logo, soft-touch laminate body
- **Premium edition**: Add gold foil (Pantone 871) on logotype lock-up

### Finishing Options
- **Logo treatment**: Deboss (uncoated stock) OR Foil Stamp (Pantone Premium Metallics 871 Gold)
- **Edge treatment**: Painted edge color match `--brand-9` for triplexed cards
- **Lamination**: Soft-touch matte (luxury) OR satin matte (modern minimal)

### Proofing Protocol
1. Press proof on actual stock (mandatory for ≥1000 unit runs)
2. Color review under D50 lighting (5000K, color-correct)
3. Compare to physical Pantone Formula Guide fan deck
4. Sign-off form before production run
```

---

## Substrate-Specific Color Behavior

Aynı PMS color farklı substrate'lerde **tamamen farklı** görünür:

| PMS Code | Coated Paper | Uncoated Paper | Plastic | Tekstil (cotton) | Metal (anodized) |
|----------|--------------|-----------------|---------|-------------------|--------------------|
| PMS 185 C (Red) | Vivid bright red | Slightly dusty red | Plastic-y orange-red | Coral-red (dye uptake) | Burgundy-leaning |
| PMS 286 C (Blue) | Royal blue | Steel-blue | Plastic blue | Indigo-shift | Purple-leaning |

**Production lesson**: Multi-substrate brand (örn: digital + business card + tekstil merch) için **substrate-specific Pantone testing** zorunlu. Pantone TCX (Textile Cotton) veya TPG (Textile Paper Glossy) ek standartları kullan.

---

## Embossing/Deboss/Foil — Tactile Brand

### Letterpress + Deboss Combination
**Modern luxury formula**:
1. Cotton paper (Crane's Lettra 400gsm)
2. Letterpress logo (single ink, deep deboss)
3. Reverse side: blind deboss (no ink, just impression)
4. Edge paint: brand color

**Cost**: $3-8 per business card (high-volume), $20+ per card (small run)

### Foil Stamping Specifications
**Specs to provide printer**:
- **Foil color**: Pantone Premium Metallics catalog (PMS 871-877 Gold/Silver/Copper)
- **Foil type**: Standard / Holographic / Pearl / Pigment / Diffraction
- **Die size**: Logo dimensions in mm
- **Pressure**: Light (kiss-fit) / Medium / Heavy (deep deboss + foil)

### Spot UV (Glossy on Matte)
**Effect**: Logo sembol matte-coated body üzerinde glossy çıkar; substrate ışıkta aşağı yukarı oynayınca logo öne çıkar.
**Cost**: ~30% upcharge over standard print
**Use case**: Premium business cards, luxury packaging covers

---

## Color Management Setup (ICC Profile Workflow)

### Adobe Creative Cloud
```
Edit > Color Settings:
  - Working Space (RGB):  sRGB IEC61966-2.1
  - Working Space (CMYK): Coated GRACoL 2006
  - Color Management Policies: Preserve Embedded Profiles
  - Conversion Options: Adobe ACE engine, Relative Colorimetric, Black Point Compensation ON
```

### Print Provider Communication
1. **Soft-proof** Photoshop'ta: `View > Proof Setup > Custom > [printer's profile]`
2. **Deliver press-ready file**: PDF/X-1a (CMYK preserved) OR PDF/X-4 (color management embedded)
3. **Include Pantone callouts** in delivery: "Use PMS 2725 C as 5th color"
4. **Request press proof** on actual stock (not just print mockup)

---

## Production Checklist

### Before Print Run
- [ ] Vector logo file delivered as `.pdf` veya `.eps` (not raster)
- [ ] Color profiles embedded (sRGB for RGB, GRACoL for CMYK)
- [ ] Pantone PMS callouts specified per element
- [ ] Bleed area defined (3mm standart)
- [ ] Crop marks visible
- [ ] Color separations (one PDF per ink)
- [ ] Trim/fold lines marked
- [ ] Press-grade paper stock specified (manufacturer + GSM)

### Pre-Press
- [ ] Pre-flight check (Adobe PreFlight veya Enfocus PitStop)
- [ ] Press proof on actual stock
- [ ] D50 lighting review (color-correct)
- [ ] Pantone fan deck physical comparison
- [ ] Sign-off form

### Post-Production
- [ ] Quality control sample (1 per 100 units)
- [ ] Color uniformity check (front to back of run)
- [ ] Finishing quality (foil adhesion, deboss depth, edge cleanliness)
- [ ] Packaging for shipment (no shifting in transit)

---

## Common Print Production Problems

### "My HEX color looks dull printed"
**Cause**: HEX (sRGB) → CMYK conversion lost saturation. Many vivid screen colors can't be reproduced in CMYK.
**Solution**: Use Pantone spot ink for the brand-critical color (5th-color Pantone over CMYK).

### "Color shifted between business cards and brochure"
**Cause**: Two different print runs, different ICC profiles or paper stocks.
**Solution**: Centralize at one printer using same paper + same calibration. OR specify Pantone for both runs.

### "Foil logo looks 'cheap'"
**Cause**: Foil too shiny/bright relative to brand tone. Or wrong foil type (e.g., generic gold foil for sophisticated luxury brand).
**Solution**: Use **matte foil** or **antiqued foil** for luxury; **brushed foil** for modern; **holographic** only for entertainment/youth brands.

### "Logo looks fuzzy in print"
**Cause**: Raster file used at insufficient DPI (300 DPI minimum for print; ideally vector).
**Solution**: ALWAYS deliver vector PDF/EPS for print. brand-visual'ın `vector_trace.py` workflow uygulayın.

---

## Sustainability in Print

2026 brand expectation: **eco-conscious print specs**.

### Eco-Friendly Choices
- **FSC-certified paper** (Forest Stewardship Council)
- **Recycled content** (post-consumer waste %)
- **Soy-based inks** (vs petroleum-based)
- **Vegetable-based binding** (gluten alternatives in book covers)
- **Letterpress + digital combo** (less ink than offset)
- **Local printing** (lower carbon footprint)

### Brand-Visual Recommendation
For sustainability-positioned brands (Patagonia archetype), **explicitly call out eco-print specs** in brand book. Example:
> "All printed materials use Mohawk Renewal 100% PCW, FSC-certified, manufactured with wind energy. Letterpress production via [printer name], Brooklyn NY."

---

## Print Tools & Resources

### Pantone
- **Pantone Connect** (Adobe CC plugin) — digital Pantone library
- **Pantone Formula Guide** (physical fan deck) — production gold standard, $200-300 per set
- **Pantone Color Bridge Guide** — CMYK approximations of all PMS

### Print Service Providers (Premium)
- **Moo (moo.com)** — Premium business cards, soft-touch, triplexed
- **MOO Luxe** — Top-tier (cotton + foil + edge paint)
- **Crane's** — American premium (cotton paper specialist)
- **Vistaprint** — Mid-tier accessible
- **GotPrint** — Wholesale

### Pre-Press Tools
- **Adobe Acrobat Pro** — PDF/X verification, soft-proofing
- **Enfocus PitStop** — Industry-standard PDF preflight
- **CHILI Publisher** — Web-to-print automation
- **Esko** — Packaging-specific pre-press

### Color Calibration
- **X-Rite ColorMunki** — Display + printer calibration
- **Datacolor SpyderX** — Display calibration
- **i1 Display Pro** — Pro-grade colorimeter

---

## Sonuç: Print as Brand Reality

> Bir markanın gerçek "brand reality test'i" — websitede mükemmel görünüyorsa kolay. Business card'da, packaging'de, billboard'da, tekstil merch'de **tutarlı ve uyumlu** görünüyorsa o **gerçek brand identity**'dir.

`brand-visual` skill, ekran kimliğinden fiziksel kimliğe geçişi **sistemik olarak** belgelendirir. `pantone_matcher.py` ekran HEX'inizi spot ink dünyasına bağlar; bu reference dosyası ise paper stock, finishing, ve production workflow'unu tarif eder.

**Pratik kural**: Production'a vermeden önce her zaman **press proof** isteyin ve **D50 lighting altında** Pantone fan deck'le karşılaştırın. Hiçbir digital simulation gerçek substrate ile aynı değildir.
