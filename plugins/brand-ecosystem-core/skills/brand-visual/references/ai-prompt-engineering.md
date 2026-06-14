# AI Image Generation Prompt Engineering — Logo Üretimi İçin (v1.3)

> **Bu dosya `brand-visual` skill'inin Adım 4 işleminde her zaman aktif kullanılır.**
> **2026 Nisan itibariyle güncel** — Nano Banana 2 (Gemini 3.1 Flash Image, 26 Şubat 2026), Grok Imagine Aurora-2 (Ocak 2026), Nano Banana Pro (Gemini 3 Pro Image), Midjourney V7/V8, Niji 7.
>
> **v1.3 Radikal Sadeleştirme**: Önceki 5 variant (A-E) model-spesifik prompt mimarisi → **TEK Unified Multi-Model Prompt (UMMP)** + model-spesifik execution notes. Gerekçe: 2026'da iki primary model aynı prompt grammar'ına converge etti (narrative paragraph + semantic positive-constraint). Tek prompt, iki model, paralel execution.

---

## Felsefi Temel (2026 Güncel)

> "AI image models are not designers. They are **stochastic compositing engines**. Your job as creative director is not to ask for a logo — it is to **invoke a tradition** the model recognizes, then **shape its imagination** with positive-constraint semantic language."

**Dört çekirdek ilke**:

1. **Style anchoring** — Model, isim ile tanıdığı tasarımcıların estetiğini canlandırır. Tradition'ı invoke etme, taklit değil.

2. **Semantic positive-constraint > Negative list** — 2026 paradigma değişimi. "No gradient" yerine *"absolutely flat single-tone fill with no color transitions or luminous blending anywhere in the form"*. Ne istemediğini ne istediğinle söylemek.

3. **Iteration > perfection** — 3-5 iterasyondan sonra dur — daha fazlası stagnation. Nano Banana 2'nin "konuşmasal iterasyon" kabiliyeti (keep everything same, but...) 2026 süper gücü.

4. **Native convergence** — 2026 primary modeller aynı prompt grammar'ını kabul ediyor: narrative paragraph, semantic positive-constraint, in-sentence aspect ratio, embedded style anchor. Bir prompt, iki model, paralel.

---

## Major AI Models Karşılaştırma (Nisan 2026)

| Model | Güçlü Yönü | Zayıflığı | Logo Uygunluğu |
|---|---|---|---|
| **Nano Banana 2** (gemini-3.1-flash-image-preview) · **PRIMARY 2026** | Pro-kalite Flash hızında, 14 ref görsel, 5 karakter tutarlılığı, 131K context, web search grounding, konuşmasal iterasyon, native C2PA+SynthID, **%50 ucuz ($0.067/2K)**, 512px–4K, 16 aspect ratio | Free tier watermark; API key gerekli full access; parameter flag çalışmaz | ★★★★★ **Wordmark + Monogram + Mockup primary** |
| **Grok Imagine Aurora-2** (`grok-imagine-image`) · **PRIMARY 2026** | Best-in-class instruction following, director-style native, image-to-video chain, Temporal Latent Flow hızı, Quality/Speed/Pro modes, aggressive API fiyatı | Reproducibility orta; precise vector için MJ hâlâ refine; retro/bold bias | ★★★★★ **Route 3 Disruptor + Route 4 Adaptive primary** |
| **Nano Banana Pro** (gemini-3-pro-image-preview) | Maksimum fidelity, advanced "Thinking" reasoning, studio-quality text, precision | %100 daha pahalı ($0.134/2K); hız yarı | ★★★★★ Premium/büyük format |
| **Midjourney V7** | Klasik vektör/flat estetik, --sref olgunluğu, 4-grid workflow | Discord-only, parametre zorunlu, text rendering NB2'den zayıf, vector yok | ★★★★ Route 2 fallback |
| **Midjourney V8 Alpha** | V7 + cinematic ışık | V8.1 stable Mayıs 2026 bekleniyor | ★★★★ Bleeding edge |
| **Niji 7** | İllüstrasyon/mascot, temiz line work | Anime biased | ★★★★ Route 3 Mascot |
| **Flux.1 Dev/Schnell** | Açık kaynak, ComfyUI lokal | Stilizasyon NB2'den refine değil | ★★★ Iteration + A/B |
| **Ideogram 2.0** | Eski text rendering öncüsü | 2026'da NB2 üstün, gereksiz | ★★ Legacy |
| **Adobe Firefly 3** | IP indemnification, enterprise-safe | Konservatif stilizasyon | ★★★ Enterprise legal |
| **Stable Diffusion 3.5** | Full kontrol, lokal | Setup karmaşık | ★★ Power user |

> **2026 DEFAULT**: Her çağrı **UMMP üretir, paralel Nano Banana 2 + Grok Imagine koşturur**. Midjourney opsiyonel fallback (addenda ile). Niji 7 = mascot özel; Adobe Firefly = enterprise legal-safe.

---

## UMMP — UNIFIED MULTI-MODEL PROMPT ARCHITECTURE

### Temel İlke

**Tek prompt. İki primary model. Paralel execution. Parameter flag yok.**

Nano Banana 2 ve Grok Imagine Aurora-2 her ikisi de 2026'da aynı prompt grammar'ına converge etti:
- Narrative paragraph (keyword listesi değil)
- Semantic positive-constraints (negative flag yerine)
- Aspect ratio cümle içinde ("horizontal 16:9 composition")
- Style anchor embedded ("rendered in the tradition of X")
- Ölçülebilir detaylar (stroke weight, oranlar)

### UMMP 7-Element Grammar

```
[1: SUBJECT FRAMING]    A professional studio composition of [logo type] isolated on a pure white studio backdrop.
[2: FORM CONSTRUCTION]  The mark [forma dair tek cümle — elementler + gestalt operasyonu].
[3: STYLE ANCHOR]       It is rendered in the [tradition] of [designer anchor] [+ hybrid anchor optional].
[4: TECHNICAL SPEC]     with [stroke weight / proportion / symmetry / specific measurements].
[5: COMPOSITION]        The composition is [centered / asymmetric...] within a [aspect ratio] frame, designed for favicon scalability at 16 pixels.
[6: COLOR DIRECTION]    The coloring is solid [Color1] and [Color2] only, with absolutely flat single-tone fill — no color transitions, no luminous gradients, no dimensional shading, no drop shadows, no textural surface, no photographic depth, no 3D rendering. Every edge is mathematically sharp.
[7: 2026 TREND ANCHOR]  The visual sensibility is [warm neo-minimalism / hyperfunctional overlay / earthmark organic / kinetic adaptive spine — route-uygun].
```

### Element Deep Dive

#### [1] Subject Framing
"A professional studio composition" frazı 2026 modellerinde **logo/brand asset** olarak yorumlanıyor.

Varyasyonlar:
- `abstract logomark` (Route 2)
- `minimalist brand wordmark` (Route 1 Wordmark)
- `geometric monogram` (Route 1 Mono)
- `adaptive identity spine mark` (Route 4)
- `kinetic typography mark` (Route 1 Kinetic)
- `illustrated brand mascot` (Route 3 Mascot)

#### [2] Form Construction
Soyutlanan kavramı tarif et. **Marka adı yazma** (Route 1 Kinetic Wordmark hariç).

❌ "logo for Curio coffee"
✓ "The mark consists of a single luminous circular form intersecting with an interlocking geometric prism at 45-degree angle"

**Pattern**: `[element A] + [operation: combining/intersecting/interlocking/nested within/orbiting] + [element B]` + optionally `[gestalt effect]`.

Güçlü operasyonlar: combining, intersecting, interlocking, nested within, negative space reveals, implied continuity.

#### [3] Style Anchor
Tarihsel/güncel designer veya era'yı invoke et.

**Modeller tanıyor**: Paul Rand · Saul Bass · Massimo Vignelli · Milton Glaser · Sagi Haviv · Lance Wyman · Anton Stankowski · Lindon Leader · Carolyn Davidson · Pentagram · Koto · Wolff Olins · Stefan Sagmeister · Michael Bierut · Paula Scher.

**Era anchors**: "Logo Modernism 1960-80", "Swiss design International Typographic Style", "Bauhaus", "Constructivism", "Mid-century modern", "Brutalism", "Art Deco", "Memphis Group".

**2026 anchors**: "contemporary fluid identity tradition" (Nike/Adobe doctrine), "warm neo-minimalist sensibility", "hyperfunctional editorial overlay", "earthmark organic modernism".

**Hybrid örneği**: *"rendered in the modernist tradition of Massimo Vignelli grid logic meeting Aesop brutalist restraint applied to healthcare branding"*.

#### [4] Technical Spec
Ölçülebilir hassasiyet:
- `with uniform stroke weight throughout, approximately one unit thick relative to form total height`
- `with perfect rotational symmetry about the vertical axis`
- `with golden ratio proportional relationships (1:1.618)`
- `with optical correction applied so circular form sits 2% below geometric center`
- `with mathematically sharp vector edges`
- `with a single continuous bezier curve forming primary silhouette`

#### [5] Composition + Aspect Ratio
Aspect ratio cümleleri:
- `within a square 1:1 frame` — logo default
- `within a horizontal 16:9 frame` — hero
- `within a portrait 9:16 frame` — mobile
- `within a banner 3:1 horizontal frame` — wordmark lockup
- `within an ultrawide 21:9 cinematic frame` — premium
- `within a vertical 4:5 social frame` — Instagram

Composition: `centered with generous breathing room` / `asymmetric with negative-space tension on the right` / `off-center with form weighted toward lower third` / `circular composition within implied emblem frame`.

**Zorunlu favicon ifade**: `designed for favicon scalability at 16 pixels`.

#### [6] Color Direction (Semantic Flat Statement)

**Golden formula**:
```
The coloring is solid [Color1] and [Color2] only, with absolutely flat 
single-tone fill throughout the entire form — no color transitions, no 
luminous gradients, no dimensional shading, no drop shadows, no textural 
surface, no photographic depth, and no 3D rendering anywhere in the mark. 
Every edge is mathematically sharp.
```

Color anchor önerileri (arketip-bağlı):
- "indigo and warm ivory" (Sage)
- "deep emerald and cream" (luxury/warm neo-minimal)
- "burnt orange and charcoal" (creator/jester)
- "navy and antique gold" (ruler/classical)
- "Cloud Dancer cream and graphite" (2026 COY + modern)
- "deep terracotta and bone white" (earthmark)
- "electric cobalt and pure black" (hyperfunctional)

#### [7] 2026 Trend Anchor

- `"warm neo-minimalism"` — clean + welcoming + muted
- `"hyperfunctional editorial overlay"` — grid/timestamp/barcode aesthetic
- `"earthmark organic modernism"` — hand-drawn + earth palette
- `"kinetic adaptive spine"` — Route 4 core
- `"gothic revival structure"` — dramatic weight + heritage
- `"brutalist restraint"` — Aesop/Off-White
- `"tactile dimensional refinement"` — Adobe Substance 3D
- `"contemporary fluid identity"` — Nike/Coca-Cola adaptive

---

## UMMP ÖRNEK PROMPTLAR

### Örnek 1 — Route 2 Geometric, B2B AI "Verity"
```
A professional studio composition of an abstract logomark isolated on a pure 
white studio backdrop. The mark consists of a single luminous circular form 
intersecting with an interlocking geometric prism at a precise 45-degree 
angle, creating negative space that reads as an implied checkmark through 
Gestalt closure. It is rendered in the modernist tradition of Chermayeff and 
Geismar reductive geometry meeting Massimo Vignelli grid logic, with uniform 
stroke weight throughout and golden ratio proportional relationships. The 
composition is centered within a square 1:1 frame with generous padding on 
all sides, designed for favicon scalability at 16 pixels. The coloring is 
solid deep indigo and warm ivory only, with absolutely flat single-tone fill 
throughout the entire form — no color transitions, no luminous gradients, no 
dimensional shading, no drop shadows, no textural surface, no photographic 
depth, and no 3D rendering anywhere in the mark. Every edge is mathematically 
sharp. The visual sensibility is warm neo-minimalism with hyperfunctional 
precision.
```

### Örnek 2 — Route 1 Kinetic Wordmark, Wellness "Lumora"
```
A professional studio composition of a minimalist brand wordmark isolated on 
a pure white studio backdrop. The wordmark reads the word "lumora" in all 
lowercase letters, rendered in a custom geometric sans-serif typeface 
belonging to the Söhne and Neue Haas Grotesk family at approximately weight 
500, with tight negative letter-spacing and perfectly consistent stroke 
thickness across every letter. The two letter "o" characters in positions 
three and five are joined by a single horizontal hairline stroke running 
precisely through their optical centers, forming a subtle coordinate axis 
connecting the two circular forms — this connecting hairline is approximately 
one-quarter the stroke weight of the letters themselves. It is rendered in 
the contemporary editorial tradition of Massimo Vignelli grid logic meeting 
kinetic typography movement, with mathematically consistent proportions and 
optical correction on round forms. The composition is a horizontal 3:1 banner 
frame with generous breathing room above and below, designed for favicon 
scalability when reduced to the lowercase "l" mark alone. The coloring is 
solid pure black on a Cloud Dancer cream backdrop, with absolutely flat 
single-tone fill — no color transitions, no luminous gradients, no dimensional 
shading, no drop shadows, no textural surface, no photographic depth, and no 
3D rendering. Every letter edge is mathematically sharp. The visual 
sensibility is kinetic warm neo-minimalism.
```

### Örnek 3 — Route 3 Hyperfunctional, FinTech "Riot Capital"
```
A professional studio composition of an unconventional brand mark isolated on 
a pure white studio backdrop. The mark consists of a fractured geometric form 
with asymmetric angular composition, bordered by a thin precision frame 
resembling a technical contract layout — hairline registration marks in each 
corner and a single horizontal timestamp line running beneath the primary 
form, reading as a technical specification document rather than a 
conventional logo. It is rendered in the brutalist tradition of Aesop 
restraint meeting Off-White industrial typography and Nike hyperfunctional 
sports overlay aesthetic, with sharp 90-degree terminations and deliberate 
asymmetric tension. The composition is off-center within a square 1:1 frame 
with primary form weighted toward upper right and negative-space tension on 
the left, designed for favicon scalability at 16 pixels. The coloring is 
solid high-contrast pure black silhouette with a single crimson accent dot, 
on a pure white backdrop — with absolutely flat single-tone fill, no color 
transitions, no luminous gradients, no dimensional shading, no drop shadows, 
no textural surface, no photographic depth, and no 3D rendering. Every edge 
is mathematically sharp. The visual sensibility is hyperfunctional editorial 
overlay with anti-corporate rebellion attitude.
```

### Örnek 4 — Route 4 Adaptive Core Spine, Tech "Nexopharos"
```
A professional studio composition of an adaptive identity spine mark isolated 
on a pure white studio backdrop. The mark is a minimal geometric core — a 
single vertical hairline stroke bisected at the golden ratio point by a small 
circular node — designed as the immutable core of a larger adaptive identity 
system that will later wrap seasonal, contextual, or persona-variable outer 
geometry around this spine. The core itself consists of only two primitive 
forms: one stroke and one node, with node diameter exactly one-third the 
stroke total height. It is rendered in the contemporary fluid identity 
tradition of Nike dynamic pairings meeting Adobe Substance 3D architectural 
restraint, with mathematically precise proportions. The composition is 
centered within a square 1:1 frame with exactly 30% padding on all sides, 
designed for favicon scalability at 16 pixels where only core spine remains. 
The coloring is solid deep graphite on a Cloud Dancer cream backdrop, with 
absolutely flat single-tone fill — no color transitions, no luminous 
gradients, no dimensional shading, no drop shadows, no textural surface, no 
photographic depth, and no 3D rendering. Every edge is mathematically sharp. 
The visual sensibility is kinetic adaptive spine with architectural 
minimalism.
```

### Örnek 5 — Route 3 Earthmark, Wellness "Sage Botanicals"
```
A professional studio composition of an abstract organic logomark isolated on 
a pure white studio backdrop. The mark consists of a sage leaf and a water 
droplet combined through a single continuous bezier curve, where the leaf 
silhouette and droplet share one unbroken outline — the negative space 
between them reading as implied continuity through Gestalt figure-ground 
relationships. It is rendered in the earthmark organic tradition of Sagi 
Haviv reductive contemporary geometry meeting Aesop restrained botanical 
sensibility, with single weight stroke and gentle hand-rendered curves that 
suggest warmth without losing geometric precision. The composition is 
centered within a square 1:1 frame with soft generous padding, designed for 
favicon scalability at 16 pixels. The coloring is solid deep sage green and 
warm bone cream only, with absolutely flat single-tone fill — no color 
transitions, no luminous gradients, no dimensional shading, no drop shadows, 
no textural surface, no photographic depth, and no 3D rendering. Every curve 
edge is precisely controlled. The visual sensibility is earthmark organic 
modernism with warm neo-minimalist restraint.
```

---

## MODEL-SPECIFIC EXECUTION NOTES

### Nano Banana 2 (Gemini 3.1 Flash Image)

**Erişim**:
- Gemini app (free tier ~50 img/day, watermark) — `gemini.google.com`
- Google AI Studio (full access, API key) — `aistudio.google.com`
- Vertex AI (enterprise)
- API model ID: `gemini-3.1-flash-image-preview`
- Pricing: **$0.067/2K**, $0.12/4K (Pro'nun yarısı)

**Kullanım**:
1. Gemini app'te "🍌 Create images" → **Thinking mode** (Fast/Thinking/Pro arasından Thinking optimal).
2. UMMP'yi olduğu gibi yapıştır.
3. İlk generation sonrası konuşmasal iterasyon:
   - *"Keep everything exactly the same, but tighten the stroke weight by 15%."*
   - *"Same composition, but shift the mark 4% rightward for stronger negative-space tension on the left."*
   - *"Keep the form, but change the color pair to deep emerald and bone white."*
4. 14 reference image kabul ediyor — önceki iterasyonu reference olarak ekle.

**Güçlü yönleri**:
- Web search grounding → "render in current Adobe Substance 3D brand styling" real-time çekilir
- 14 reference → adaptive variants consistency lock
- 131K context → çok uzun narrative prompt destek
- Precise text rendering (wordmark kritik)
- SynthID + C2PA Content Credentials otomatik embed

**Watermark notu**: Free tier Gemini sparkle icon görünür; paid plan sadece invisible SynthID. Production için paid tier önerilir (veya vector conversion watermark'ı kaldırır).

### Grok Imagine Aurora-2

**Erişim**:
- `grok.com/imagine` (X Premium+ $16/ay, SuperGrok $30 Pro mode)
- X (Twitter) in-app
- xAI API: `grok-imagine-image`
- GenAIntel partner platform

**Modes (3 Nisan 2026 güncellemesi)**:
- **Speed** — hızlı moodboard, 1024px
- **Quality** — **logo için default**
- **Pro** — 1080p+ (Nisan sonu, SuperGrok)

**Kullanım**:
1. grok.com/imagine → **Quality mode** seç (Speed yetersiz).
2. UMMP'yi olduğu gibi yapıştır. Parameter flag yok.
3. Iteration için image-to-image edit mode:
   - *"Edit this: change geometric form to triangular base, keep color palette and style identical."*
   - *"Remove the inner circle, keep everything else exactly the same."*
   - *"Restyle with warm neo-minimalist sensibility instead of brutalist attitude."*
4. Image-to-video chain (logo stinger): logo + *"static mark transitions into motion with 3-second pulse, then returns to stillness"* → 10s 720p clip.

**Güçlü yönleri**:
- Best-in-class instruction following (xAI claim, benchmark doğrulu)
- Contextual material rendering ("matte black foil-stamped ink on debossed paper")
- Rapid iteration — saniyeler
- Director-style prompt native
- Route 3 Disruptor ideal bias
- Image-to-video logo stinger

**Zayıf yönleri**:
- Reproducibility orta — precise vector için hybrid approach (Grok'ta konsept → MJ/Illustrator'da refine)
- Konservatif kurumsal için fazla bold
- Pure abstract vector logomark NB2'den az refine

### Nano Banana Pro — Premium Fallback

UMMP aynı. Kullanım:
- Premium print / büyük format / maksimum fidelity
- Pricing: $0.134/2K, $0.24/4K
- "Thinking" mode advanced reasoning
- Gemini app Pro tier / AI Studio / Vertex
- Günlük iterasyon için NB2 yeterli; Pro sadece final hero

### Midjourney V7/V8 — Legacy Fallback

Parameter flag gerektirir. UMMP → keyword format + addenda:

**Dönüştürme reçetesi**:
1. UMMP cümlelerini virgülle ayrılmış phrase'lere parçala
2. "A professional studio composition of" → direkt "abstract logomark"
3. Aspect ratio cümlesi → `--ar 1:1` parameter
4. Semantic negative paragrafı → `--no` listesi

**Örnek dönüşüm** (Örnek 1 → MJ):
```
abstract logomark combining a luminous circular form and an interlocking 
geometric prism, intersecting at 45-degree angle, negative space reads as 
implied checkmark through gestalt closure, in the modernist tradition of 
Chermayeff & Geismar reductive geometry meeting Massimo Vignelli grid logic, 
single weight stroke, golden ratio composition, flat 2D vector, isolated on 
pure white background, solid deep indigo and warm ivory, centered generous 
padding, scalable to 16px favicon, warm neo-minimalist sensibility
--ar 1:1 --s 250 --v 7 --style raw --no text, typography, letters, words, 
realistic photo details, 3d render, gradient mesh, drop shadow, mockup 
environments, watermark, busy background, ornaments, sparkles, lens flare, 
sphere globe cliché
```

**Kullanım**: Discord → `/imagine` → 4-grid. `Vary (Subtle)`, `Vary (Region)`, `Upscale (Subtle)`. Pro plan $30/ay commercial.

**Neden legacy?** 2026'da NB2 ve Grok MJ'in logo-spesifik avantajlarını yakaladı + text rendering + konuşmasal iterasyonda öne geçti. MJ hâlâ güçlü ama workflow maliyeti (Discord, parametre, vector trace eksik) primary olmasını engelliyor.

### Niji 7 — Mascot Specialist

Sadece Route 3 illustrated mascot. UMMP adapte:

```
A professional studio composition of a minimalist friendly [animal] 
character mascot isolated on a pure white studio backdrop. The mascot 
[expression, posture]. It is rendered in the warm hand-illustrated tradition 
of Mailchimp Freddie meeting contemporary Japanese kawaii restraint, with 
[technical spec]. The composition is centered within a square 1:1 frame, 
designed for app icon scalability at 192 pixels. The coloring is solid 
[Color1] and [Color2] only, with absolutely flat single-tone fill — [semantic 
negative]. Every line is clean and uniform. The visual sensibility is 
friendly approachable character with restraint.
```

MJ üzerinden: `--niji 7 --ar 1:1 --s 200 --no text, ...`.

---

## MODEL SEÇİM DECISION TREE (2026)

```
Logo tipi ne?
│
├── Wordmark / Kinetic Typography (Route 1)
│   → PRIMARY: Nano Banana 2 (text üstün)
│     PARALLEL: Grok Imagine (contextual typography)
│     FALLBACK: Midjourney V7
│
├── Abstract Logomark (Route 2)
│   → PRIMARY: Nano Banana 2 + Grok Imagine Aurora-2 PARALEL
│     FALLBACK: Midjourney V7 (stilizasyon)
│
├── Monogram (Route 1 Mono)
│   → PRIMARY: Nano Banana 2 (text accuracy kritik)
│     PARALLEL: Grok Imagine
│
├── Disruptor / Bold (Route 3)
│   → PRIMARY: Grok Imagine Aurora-2 (bold/tactile native)
│     PARALLEL: Nano Banana 2 (konseptiyel doğrulama)
│     FALLBACK: MJ V7 --weird 500
│
├── Adaptive Core Spine (Route 4)
│   → PRIMARY: Nano Banana 2 (14 ref → variants consistency)
│     PARALLEL: Grok Imagine (image-to-video adaptive motion)
│
├── Illustrated Mascot
│   → PRIMARY: Niji 7
│     PARALLEL: Nano Banana 2 (friendly geometric)
│
├── Mockup / Logo-on-product / Brand presentation
│   → PRIMARY: Nano Banana 2 (14-input multi-ref exclusive)
│     Nano Banana Pro (hero asset)
│
├── Rapid moodboard
│   → PRIMARY: Grok Imagine Speed mode
│     SECONDARY: Flux.1 Schnell
│
└── Legal-safe enterprise
    → PRIMARY: Adobe Firefly 3
      SECONDARY: Nano Banana 2 paid tier (C2PA provenance)
```

---

## STYLE ANCHOR EFFECTIVENESS (2026)

| Anchor | R1 Kinetic | R2 Geom | R3 Disrupt | R4 Adaptive |
|---|:-:|:-:|:-:|:-:|
| Paul Rand minimalism | ★★★★★ | ★★★★ | ★★ | ★★★ |
| Saul Bass modernist | ★★★★ | ★★★★★ | ★★ | ★★ |
| Vignelli grid logic | ★★★★★ | ★★★★ | ★ | ★★★ |
| Chermayeff & Geismar reduction | ★★★ | ★★★★★ | ★★ | ★★★ |
| Wyman Mexico 68 kinetic | ★★★★ | ★★★★ | ★★★ | ★★★★★ |
| Stankowski geometry | ★★★★ | ★★★★★ | ★★ | ★★★ |
| Haviv contemporary | ★★★ | ★★★★★ | ★★ | ★★★ |
| Glaser illustration | ★★ | ★★★ | ★★★★ | ★★ |
| Davidson Nike movement | ★★ | ★★★★ | ★★★ | ★★★★ |
| Leader negative space | ★★★ | ★★★★★ | ★★ | ★★★ |
| Logo Modernism 1960-80 | ★★★★ | ★★★★★ | ★★ | ★★ |
| Swiss design | ★★★★★ | ★★★★ | ★★ | ★★★ |
| Bauhaus purity | ★★★ | ★★★★★ | ★★ | ★★★★ |
| Aesop brutalist | ★★★★ | ★★★ | ★★★★★ | ★★ |
| Mailchimp warm illust. | ★ | ★★ | ★★★★★ | ★★ |
| Liquid Death anti-corp | ★★ | ★★ | ★★★★★ | ★ |
| **2026: Nike dynamic pairings** | ★★ | ★★★ | ★★★ | ★★★★★ |
| **2026: Adobe Substance 3D** | ★ | ★★★★ | ★★ | ★★★★★ |
| **2026: JP Morgan subtle evo** | ★★★★ | ★★★★ | ★ | ★★★★ |
| **2026: Off-White hyperfunct.** | ★★ | ★★ | ★★★★★ | ★★ |
| **2026: warm neo-minimalism** | ★★★★ | ★★★★★ | ★★ | ★★★ |
| **2026: earthmark organic** | ★★ | ★★★★ | ★★★★ | ★★ |
| **2026: gothic revival** | ★★★★ | ★★★ | ★★★★ | ★ |

---

## ITERATION WORKFLOW (2026 DUAL-MODEL PARALLEL)

### Generation 1 — Initial Brief (Paralel)

**Step 1A**: UMMP → Nano Banana 2 Thinking mode → 3 generation
**Step 1B**: Paralel UMMP → Grok Imagine Quality mode → 3 generation

Toplam: **6 ham görsel** karşılaştırma için.

Değerlendirme:
- Hangi model brief'i daha iyi yorumladı?
- Hangi generation gestalt prensibini doğru işletti?
- Hangi görsel 16px'te silüet tanınır?

### Generation 2 — Refinement (Konuşmasal)

Seçilen en güçlü 1-2 görselin modelinde kal:

**Nano Banana 2**:
```
"Keep everything exactly the same, but tighten the stroke weight by 20% and 
shift the inner form 3 units upward to improve optical balance."
```

**Grok Imagine edit mode**:
```
"Edit this: remove the small secondary dot, keep every other element identical, 
add more negative-space breathing room on the right side."
```

### Generation 3 — Polish

Final konsept doğrulandığında:
- **Nano Banana Pro** hero asset (max fidelity), veya
- NB2 Thinking mode + 4K resolution

### STOP — 3-5 Generation

Daha fazlası stagnation. 5 sonrası tutmazsa → fundamental prompt değişikliği veya farklı route.

### Two-Model Convergence Bonus

Her iki model aynı brief'e **benzer çıktı verdiğinde** → brief'in güçlü olduğunun sinyali. **Farklı çıktı verdiğinde** → brief ambiguous; daha net form construction gerekir.

---

## SECTOR-SPECIFIC NEGATIVE SEMANTIC BANK

Semantic negative kısmına sektör-spesifik ek:

- **Fintech**: *"...and no credit card imagery, no dollar or euro symbols, no vault silhouettes, no blue-to-green fintech gradient cliché."*
- **Sağlık**: *"...and no stethoscope, no heart shape, no EKG waveform, no medical cross, no pill silhouette, no hands-cradling gesture."*
- **Tech/AI**: *"...and no circuit board pattern, no gear mechanism, no robot head, no brain icon, no neural network node diagram, no sphere globe, no blue-green tech gradient."*
- **Eko/Wellness**: *"...and no literal green leaf cliché, no recycling triangle, no earth globe, no tree silhouette, no watercolor splash, no hand-cradling gesture."*
- **Coffee/F&B**: *"...and no coffee cup silhouette, no mug handle, no steam spiral, no bean icon."*
- **Real Estate**: *"...and no house silhouette, no roof triangle, no location pin, no key icon."*
- **Education**: *"...and no graduation cap, no diploma scroll, no owl icon, no open book, no apple."*
- **Law/Finance**: *"...and no scales of justice, no gavel, no pillar column, no column silhouette."*

---

## COPYRIGHT VE LEGAL UYARILARI (2026 GÜNCEL)

### AI-Generated Outputs Copyrightability

- **USA**: US Copyright Office — AI-generated work not copyrightable under current law (Thaler v. Perlmutter, 2023). **2026 update**: USPTO 2025 revised guidance — human-authored **significant modifications** + documented creative process register copyright eligible olabilir.
- **EU**: AI Act 2024 fully in effect. **Disclosure zorunlu**: AI-generated/assisted assets için C2PA Content Credentials attach edilmeli (ticari yayında). Nano Banana 2 bunu otomatik gömüyor.
- **Türkiye**: SMK (Sınai Mülkiyet Kanunu) 6769 Md. 83 — trademark **tescili** AI çıktısı için mümkün (ayrıştırıcı olma koşuluyla); **telif** korumasında insan-yazarı eşik gerekli.

**Pratik implikasyon**:
1. AI ile üret
2. Vector rebuild + significant human modification (Pen Tool cleanup)
3. Process dokümente et (hangi prompt, hangi iterasyon, hangi manuel düzenleme)
4. C2PA metadata vector'da koru
5. Trademark başvurusunda insan-yazarı katkı dosyası ek yap

### Style Reference Riskleri

- "in the tradition of Paul Rand" → OK (style copyrighted değil)
- "in the style of Apple logo" → **ASLA** (trademark infringement)
- "inspired by the Nike swoosh" → Riskli (trade dress)
- Living designer style reference: çoğu durumda fair use ama commercial use'ta lawyer consultation tavsiye edilir

### Output Lisans (2026 Güncel)

- **Nano Banana 2 / Pro**: Google terms — commercial use Gemini app'te izinli, paid tier'de IP indemnification sınırlı. Vertex AI enterprise'da genişletilmiş indemnification.
- **Grok Imagine**: xAI terms — commercial use X Premium+ ve Pro tier'de izinli, enterprise contract ayrıca değerlendirilir.
- **Midjourney Pro/Mega**: Commercial use allowed ($30-120/ay).
- **Adobe Firefly**: Enterprise legal-safe, IP indemnification included.
- **Stable Diffusion**: Full commercial, ücretsiz.

---

## YAYGIN HATALAR VE DÜZELTME (2026)

### Hata 1 — Marka Adı Prompt'ta
❌ "Logo of Curio Coffee"
✓ "Abstract geometric mark combining a coffee bean and compass needle"

### Hata 2 — Parameter Flag Nano Banana 2'de
❌ "abstract logomark, --ar 1:1 --s 250"
✓ "The composition is centered within a square 1:1 frame..."

### Hata 3 — Negative Liste Nano Banana 2 / Grok'ta
❌ "--no gradient, shadow, 3d"
✓ "...with absolutely flat single-tone fill — no color transitions, no luminous gradients, no dimensional shading..."

### Hata 4 — "Make it stand out"
❌ Subjective adjective
✓ Spesifik composition: "off-center with negative-space tension on the right"

### Hata 5 — Sürekli farklı prompt
❌ Her iterasyonda tamamen farklı prompt
✓ Aynı prompt, **hedefli 2-3 kelime değişikliği** ile evolve + konuşmasal iterasyon

### Hata 6 — Text rendering beklemek (Route 1 dışında)
❌ "Logo with word CURIO visible"
✓ Sembol-only → typography adımında gerçek fontla lock

### Hata 7 — Tek modele güvenmek
❌ Sadece Nano Banana 2 veya sadece Grok
✓ Her ikisini paralel koştur, çıktıları karşılaştır

### Hata 8 — 5+ iterasyon
❌ 10 iterasyon sonrası "mükemmeli bulmak"
✓ 3-5'te dur, stagnation'dan kaç, route değiştir

---

## PROMPT QUALITY CHECKLIST (Model-Aware)

**UMMP genel** (Nano Banana 2 + Grok için):
- [ ] Prompt narrative paragraph (virgülle ayrılmış keyword değil)
- [ ] "A professional studio composition of..." ile başlıyor
- [ ] Semantic positive-constraint ("absolutely flat single-tone fill...")
- [ ] Aspect ratio cümle içinde ("within a square 1:1 frame")
- [ ] Favicon scalability ifadesi ("designed for favicon scalability at 16 pixels")
- [ ] Style anchor cümle içinde ("rendered in the tradition of X")
- [ ] 2026 trend anchor sonda ("The visual sensibility is...")
- [ ] Parameter flag YOK
- [ ] Marka adı YOK (Route 1 Kinetic Wordmark hariç)
- [ ] Color max 2 renk + backdrop (pure white veya Cloud Dancer)
- [ ] Technical spec ölçülebilir (stroke weight ratio, %, degree)
- [ ] Sektör-spesifik negative semantic bank uygulanmış

**Midjourney fallback için ek**:
- [ ] UMMP keyword formuna dönüştürülmüş
- [ ] `--ar 1:1 --s 250 --v 7` parametre eklenmiş
- [ ] `--no` extensive negative list eklenmiş
- [ ] `--style raw` Route 2 için ekstra (over-polished risk)

---

## FULL PROMPT GALERI — ARKETIP x ROUTE MATRISI

### Sage / B2B AI Platform — "Verity" (Route 2 Geometric)
```
A professional studio composition of an abstract logomark isolated on a pure 
white studio backdrop. The mark combines a geometric checkmark and an abstract 
data node through a single continuous stroke, creating implied continuity 
between verification and intelligence through Gestalt closure. It is rendered 
in the modernist tradition of Massimo Vignelli grid logic meeting Lance Wyman 
Mexico 68 kinetic system, with mathematical precision and golden ratio 
composition. The composition is centered within a square 1:1 frame with 
generous padding, designed for favicon scalability at 16 pixels. The coloring 
is solid deep indigo and warm white only, with absolutely flat single-tone 
fill — no color transitions, no luminous gradients, no dimensional shading, 
no drop shadows, no textural surface, no photographic depth, and no 3D 
rendering. And no brain icon, no robot head, no neural network diagram, no 
circuit board pattern, no sphere globe, no blue-green tech gradient. Every 
edge is mathematically sharp. The visual sensibility is warm neo-minimalism 
with hyperfunctional precision.
```

### Outlaw / Music Streaming — "Riot Audio" (Route 3 Disruptor)
```
A professional studio composition of an abstract bold mark isolated on a 
pure white studio backdrop. The mark combines a sound wave and a fractured 
geometric form through sharp angular intersection, with deliberate asymmetric 
tension and anti-corporate raw aesthetic. It is rendered in the brutalist 
tradition of Aesop Helvetica era applied to music industry rebellion meeting 
Off-White industrial typography, with high-contrast single color and 
intentional imperfection. The composition is off-center within a square 1:1 
frame with negative-space tension on the left side, designed for favicon 
scalability at 16 pixels. The coloring is solid charcoal black silhouette 
with a single crimson accent, on pure white backdrop — with absolutely flat 
single-tone fill, no color transitions, no luminous gradients, no dimensional 
shading, no drop shadows, no textural surface, no photographic depth, no 3D 
rendering. And no musical notes cliché, no headphones, no microphone, no 
equalizer bars, no polished corporate aesthetic. Every edge is sharp and 
deliberate. The visual sensibility is brutalist restraint with hyperfunctional 
overlay and rebellion attitude.
```

### Lover / Beauty — "Velvet Hour" (Route 2 Geometric + warm)
```
A professional studio composition of an elegant abstract logomark isolated on 
a pure white studio backdrop. The mark suggests a flowing silk ribbon 
intersecting with a crescent moon through a single continuous bezier curve, 
where the negative space reads as implied sensuality through figure-ground 
relationships. It is rendered in the contemporary luxury tradition of Koto 
Studio modern identity meeting Pentagram elegant restraint, with refined 
single-weight stroke and elegant proportion. The composition is centered 
symmetrically within a square 1:1 frame with refined padding, designed for 
favicon scalability at 16 pixels. The coloring is solid deep burgundy and 
warm antique gold only, with absolutely flat single-tone fill — no color 
transitions, no luminous gradients, no dimensional shading, no drop shadows, 
no textural surface, no photographic depth, no 3D rendering. And no lipstick 
silhouette, no flower motif, no watercolor splash, no cursive script 
flourish, no jewelry rendering, no sparkle effect. Every curve is precisely 
controlled. The visual sensibility is warm neo-minimalist luxury with 
earthmark warmth.
```

### Magician / Adaptive Tech — "Nexopharos" (Route 4 Adaptive Spine)
```
A professional studio composition of an adaptive identity spine mark isolated 
on a pure white studio backdrop. The mark is an immutable geometric core — a 
single vertical line and orbiting circular node at golden ratio point — 
designed as the unchanging DNA of a larger adaptive system that will wrap 
variable outer geometry (seasonal, contextual, persona) around this spine. 
Core consists of exactly two primitive forms with node diameter one-third 
stroke height. It is rendered in the contemporary fluid identity tradition 
of Nike dynamic pairings meeting Adobe Substance 3D architectural restraint 
and Lance Wyman Mexico 68 kinetic system, with mathematically precise 
proportions. The composition is centered within a square 1:1 frame with 
exactly 30% padding, designed for favicon scalability at 16 pixels where 
only core remains visible. The coloring is solid deep graphite on Cloud 
Dancer cream backdrop, with absolutely flat single-tone fill — no color 
transitions, no luminous gradients, no dimensional shading, no drop shadows, 
no textural surface, no photographic depth, no 3D rendering. Every edge is 
mathematically sharp. The visual sensibility is kinetic adaptive spine with 
warm neo-minimalist architecture.
```

### Jester / Snack Brand — "Wonderbite" (Route 3 Mascot via Niji 7)
```
A professional studio composition of an illustrated brand mascot isolated on 
a pure white studio backdrop. The mascot is a playful abstract creature 
combining a winking expression and a geometric burst of energy, with bold 
confident curves and character warmth. It is rendered in the warm 
hand-illustrated tradition of Mailchimp Freddie meeting Skittles taste-the-
rainbow joy, with single weight stroke and expressive but reductive form. 
The composition is centered dynamically within a square 1:1 frame with 
slight off-balance playfulness, designed for app icon scalability at 192 
pixels. The coloring is solid bright yellow, warm orange, and deep navy 
only, with absolutely flat single-tone fill — no color transitions, no 
luminous gradients, no dimensional shading, no drop shadows, no textural 
surface, no photographic depth, no 3D rendering. And no food photography, 
no generic mascot face, no pixel art, no retro 8-bit. Every line is clean 
and confident. The visual sensibility is friendly approachable character 
with earthmark warmth. [Niji 7 flag: --niji 7 --s 200 --ar 1:1]
```

---

## REKLAMASIZ FİNAL ÖNERİ (2026 UMMP WORKFLOW)

Her brand-visual çağrısında Adım 4 çıktısı **TEK UMMP + model-spesifik execution notes** içerir. Default kombinasyon:

**Paralel execution matrisi**:

| Route | Primary A | Primary B | Fallback |
|---|---|---|---|
| **Route 1 Kinetic/Wordmark** | Nano Banana 2 | Grok Imagine | Midjourney V7 |
| **Route 2 Geometric** | Nano Banana 2 | Grok Imagine Aurora-2 | Midjourney V7 |
| **Route 3 Disruptor** | Grok Imagine Aurora-2 | Nano Banana 2 | MJ V7 --weird 500 |
| **Route 3 Mascot** | Niji 7 | Nano Banana 2 | — |
| **Route 4 Adaptive Spine** | Nano Banana 2 (14-ref) | Grok Imagine (i2v) | — |
| **Mockup/Composition** | Nano Banana 2 (14-input) | Nano Banana Pro | — |
| **Enterprise IP-safe** | Adobe Firefly 3 | Nano Banana 2 Vertex | — |

**Neden paralel dual-model?** Her model farklı cognitive bias'a sahip: Nano Banana 2 "studio product photography" yönelimli, Grok Imagine Aurora-2 "bold contextual material" yönelimli. İki farklı bias'ın **aynı brief'e iki farklı stratejik yorumu** kullanıcıya **gerçek seçenek alanı** açar.

**Kullanıcıya kapanış mesajı template'i**:

> "UMMP'yi **iki modele paralel** çalıştırın:
>
> - **Nano Banana 2** — Gemini app "🍌 Create images" → Thinking mode → UMMP'yi yapıştır → 3 generation. Free tier yeterli (watermark post-processing'te kalkar). Konuşmasal iterasyonla refine edin.
> - **Grok Imagine** — grok.com/imagine → Quality mode → UMMP'yi yapıştır → 3 generation. X Premium+ ($16/ay) veya SuperGrok ($30/ay Pro mode end-April) erişim.
>
> Toplam 6 görsel. En güçlü 1-2 sonucu (toplam 2-3) iletin. Adım 5'te tasarım sistemini (Radix renkleri, variable font tipografi, design tokens, adaptive rules varsa, C2PA provenance) inşa edeceğiz.
>
> **Tahmini maliyet**:
> - Nano Banana 2: free tier $0 (Gemini app), veya $0.067/2K API
> - Grok Imagine: X Premium+ $16/ay subscription, veya API usage-based
> - Toplam ilk cycle: $0 (free tier) — $1-3 (paid)"

---

## TEKNİK REFERANS ÖZETİ

### Nano Banana 2 API Snippet (Python)
```python
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[UMMP_TEXT],  # UMMP narrative paragraph
)
for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("logo_nb2.png")
# C2PA Content Credentials + SynthID otomatik embed
```

### Grok Imagine API Snippet (Python xAI SDK)
```python
import xai_sdk
client = xai_sdk.Client()
response = client.image.sample(
    prompt=UMMP_TEXT,
    model="grok-imagine-image",
    aspect_ratio="1:1",  # opsiyonel override
)
print(response.url)  # image URL
```

### Midjourney (Discord komut)
```
/imagine prompt: [UMMP → keyword form] --ar 1:1 --s 250 --v 7 --style raw 
--no text, typography, letters, words, realistic photo details, 3d render, 
gradient mesh, drop shadow, mockup environments, watermark, busy background, 
ornaments, sparkles, lens flare
```

---

> **Kapanış ilkesi**: UMMP, bir creative director brief'idir. Parametre listesi değil. Her cümle bir stratejik karar olmalı. Eğer bir element "sadece olduğu için" var — kaldır. Nano Banana 2 ve Grok Aurora-2, brief'inizin disiplinine aynen saygı gösterir. "Disiplin sahibi olmak" 2026 prompt mühendisliğinin yeni zanaatıdır.
