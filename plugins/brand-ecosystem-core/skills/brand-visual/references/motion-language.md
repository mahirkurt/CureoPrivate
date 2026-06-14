# Brand Motion Language — Marka Hareket Dili Sistemi

> **Bu dosya `brand-visual` skill'inin Adım 5 kapsamında, statik kimlikten **kinetic kimliğe** geçişi belgelenir.**
>
> 2026'da motion **opsiyonel değildir**. Marka kılavuzunda motion bölümü olmamak, **2006'da renk paleti olmamak** kadar amatörcedir (All In Motion 2026).

---

## Felsefi Temel

> "Brand artık baktığınız bir şey değil. **Zamanın içinde hareket ettiğiniz bir şey**." — All In Motion 2026

### 2026'nın Realitesi
Modern markalarla insanların temas ettiği yüzeylerin neredeyse tamamı **animasyonlu**:
- Sosyal medya feed (motion-first)
- Yazılım UI (transitions, micro-interactions)
- Web hero (loop, breathe, scroll-tied)
- Sales presentation (motion graphics)
- Logo stinger (intro/outro animations)
- Product onboarding (Lottie animations)

Ve bunların hiçbiri için **standardize edilmemiş motion guidance** yoksa, marka her temasta **rastgele tasarımcı kararı**na kalır → tutarsızlık.

### brand-visual'ın Yaklaşımı
Bu skill, marka kimliği teslimat'ının bir parçası olarak **5 motion artifact** üretir:
1. **Motion personality statement** — markanın hareket karakteri (1 paragraf)
2. **Duration ladder** — 4-tier zaman skalası (micro / UI / transition / logo-stinger)
3. **Easing palette** — primary + secondary cubic-bezier curves
4. **Animation primitives** — markanın "izinli" hareket vocabulary'si
5. **Lottie skeleton** — designer'ın After Effects'te dolduracağı stub JSON

---

## Marka Motion Kişiliği — Arketip Mapping

Her arketip kendi motion gramerini taşır. **Outlaw'ın spring-bounce yapması yanlıştır**; Caregiver için harsh-cut yanlıştır. `scripts/motion_spec_generator.py` bu mapping'i otomatik uygular.

| Arketip | Personality | Duration Character | Primary Easing |
|---------|-------------|--------------------|-----------------|
| Innocent | Soft, optimistic, gentle bounce | 250-450ms | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` ease-out-soft |
| Everyman | Direct, no-nonsense, functional | 150-300ms | `cubic-bezier(0, 0, 0.2, 1)` ease-out |
| Hero | Cesur, decisive, confident | 180-350ms | `cubic-bezier(0.16, 1, 0.3, 1)` ease-out-decisive |
| Outlaw | Asi, bozuk, kasıtlı tutarsızlık | 80-200ms | `cubic-bezier(0.7, 0, 0.84, 0)` ease-in-cut |
| Explorer | Akan, organic, doğa ritmi | 400-800ms | `cubic-bezier(0.215, 0.61, 0.355, 1)` ease-out-organic |
| Creator | Yaratıcı, hand-drawn, generative | 200-700ms | `cubic-bezier(0.34, 1.56, 0.64, 1)` ease-out-back |
| Ruler | Yetkili, contained, precise | 200-350ms | `cubic-bezier(0.25, 0.1, 0.25, 1)` ease-out-precise |
| Magician | Dönüşüm, smooth-impossible morphs | 300-600ms | `cubic-bezier(0.83, 0, 0.17, 1)` ease-in-out-mystic |
| Lover | Romantic, sensual, velvet | 350-700ms | `cubic-bezier(0.77, 0, 0.175, 1)` ease-in-out-romantic |
| Jester | Playful, bouncy, unexpected | 250-500ms | `cubic-bezier(0.34, 1.56, 0.64, 1)` ease-out-back |
| Caregiver | Soft, protective, slow-down | 300-500ms | `cubic-bezier(0.215, 0.61, 0.355, 1)` ease-out-soft |
| Sage | Considered, slow, intentional | 300-450ms | `cubic-bezier(0, 0, 0.2, 1)` ease-out |

> Tam spec ve no-go zonelar için `scripts/motion_spec_generator.py --archetype <X>` çalıştır.

---

## Duration Ladder Standartları

### 4-Tier Zaman Skalası

Markanın motion language'ı **4 timeframe'de** çalışır:

| Tier | Use Case | Range | Örnekler |
|------|----------|-------|----------|
| **Micro** | UI feedback, button hover, tap response | 80-200ms | Button color change, hover state, focus ring appear |
| **UI** | Modal açılma, dropdown reveal, toast notification | 200-400ms | Sidebar slide, modal fade-in, tooltip appear |
| **Transition** | Page transition, view change, scene transition | 250-500ms | Route navigation, view fade, cross-fade |
| **Logo-Stinger** | Brand intro/outro, splash screen, video opener | 1.0-2.5s | App launch animation, video stinger |

### Endüstri Tavanı: 2.5 saniye

> "Logo animasyonları 2.5 saniyeyi geçmemeli — enterprise kontekslerde." (All In Motion 2026)

Daha uzun stinger = izleyici dikkati kaybeder, marka mesajı seyrek olur. Apple'ın WWDC opening stinger'ları **2.0 sn'nin altındadır**; Google'ın `g` morph'u **1.5 sn**.

### Tonality Modifier'lar

Default duration ladder'a aşağıdaki çarpanlar uygulanır:

| Tonality | Duration Çarpan | Easing Bias |
|----------|------------------|-------------|
| `premium`, `luxury` | ×1.15 — ×1.25 (yavaşlatır) | More curve (more refined) |
| `fast`, `snappy`, `bold`, `cesur` | ×0.75 — ×0.85 (hızlandırır) | Snappier (more aggressive) |
| `calm`, `minimal`, `sıcak` | ×1.10 — ×1.20 (yavaşlatır) | More linear (less drama) |

`scripts/motion_spec_generator.py --tonality "premium,calm"` ile composability.

---

## Easing Curves — Marka DNA'sı

Easing curve, marka karakterinin **matematiksel ifadesi**. Aynı duration'da **farklı easing**, tamamen farklı brand feel verir:

### Modernist / Material Design Default
```css
/* Standard ease-out (Material Design Standard Easing) */
cubic-bezier(0.4, 0, 0.2, 1)
```
**Use**: 90% of UI motion. Material Design + iOS Human Interface'in default'u.

### Decisive / Hero Brand
```css
cubic-bezier(0.16, 1, 0.3, 1)  /* ease-out-decisive */
```
**Use**: Sharp, confident; nothing apologetic. Nike, BMW tarzı.

### Cut / Outlaw / Glitch
```css
cubic-bezier(0.7, 0, 0.84, 0)  /* ease-in-cut */
steps(3, end)                  /* alternative: stepped easing */
```
**Use**: Liquid Death, Diesel, Harley tarzı; "polish reddediyor" ifadesi.

### Spring / Jester / Playful
```css
cubic-bezier(0.34, 1.56, 0.64, 1)  /* ease-out-back, overshoots */
spring(1, 80, 10, 0)               /* iOS spring physics */
```
**Use**: Mailchimp, Slack, Discord; warm/playful brand'ler.

### Organic / Explorer / Caregiver
```css
cubic-bezier(0.215, 0.61, 0.355, 1)  /* ease-out-organic */
```
**Use**: Patagonia, Aesop, Method tarzı; doğa ritmi.

### Romantic / Lover / Luxury
```css
cubic-bezier(0.77, 0, 0.175, 1)  /* ease-in-out-romantic */
```
**Use**: Chanel, Dior, lüks fashion; velvet feel.

---

## Animation Primitives — Markanın "İzinli Hareket Vocabulary"si

Her marka kendi izinli hareket setine sahip. Outlaw için "soft-fade" yasak, Sage için "spring-bounce" yasak. brand-visual bu vocabulary'yi arketipten türetir:

### Universal Primitives (her arketip için OK)
- **fade-in / fade-out**: opacity 0 → 100
- **slide-in (from direction)**: position offset → 0
- **scale-in / scale-out**: scale 0.8 → 1.0

### Hero Primitives
- **slam-arrive**: scale 1.5 → 1.0 + opacity rapid
- **diagonal-stripe-reveal**: clip-path angle motion
- **scale-up-bold**: scale 0 → 1.0 with overshoot

### Outlaw Primitives
- **glitch-cut**: 3-4 hızlı opacity 0/100 cycle
- **harsh-snap**: instant transform with no easing
- **torn-reveal**: clip-path irregular shape
- **static-buzz**: position jitter (±2px random)

### Magician Primitives
- **morph-transform**: SVG path morph (one shape → another)
- **particle-coalesce**: many → one (Genie effect tarzı)
- **alchemy-fade**: gradient color shift on fade

### Lover Primitives
- **velvet-fade**: opacity + slight scale + slowed easing
- **curve-trace**: stroke-dasharray draw-on
- **soft-bloom**: scale up slightly + brightness pulse

### Caregiver Primitives
- **soft-fade**: slow opacity transition
- **embrace-scale**: scale around center, slow
- **warm-pulse**: subtle scale 1.0 → 1.03 → 1.0 loop

### Jester Primitives
- **spring-bounce**: scale with spring physics overshoot
- **wiggle-pulse**: rotate ±5° rapid loop
- **playful-rotate**: 360° rotation with overshoot

---

## Lottie Spec v1.0 — Standardize Format

### Neden Lottie
- **Vector-based**: SVG gibi infinite scalable
- **JSON format**: Designer After Effects'te yapar, web/iOS/Android tek dosya
- **2-10 KB icon animation** vs **50-500 KB equivalent GIF**
- **60fps native** her platform'da
- **Programmatic control**: Color tema değiştirilebilir, runtime'da scrub edilebilir
- **Standart**: Lottie Animation Community (LAC), Linux Foundation altında, Specification v1.0 (Sept 2024)

### Lottie File Structure (Özet)
```json
{
  "v": "5.7.0",        // Lottie version
  "fr": 60,            // Frame rate
  "ip": 0,             // In point
  "op": 90,            // Out point (frame)
  "w": 1024,           // Width
  "h": 1024,           // Height
  "nm": "Brand Logo Stinger",
  "layers": [
    {
      "ty": 4,         // Shape layer
      "nm": "logo",
      "ks": {          // Transform: opacity, position, scale, rotation
        "o": {...},    // Each can be animated with keyframes
        "p": {...},
        "s": {...},
        "r": {...}
      },
      "shapes": [...]  // Vector path data
    }
  ]
}
```

### Production Workflow
1. **Designer After Effects'te animasyon yapar** (vector shape layers ile, **NOT raster**)
2. **Bodymovin** veya **LottieFiles** plugin'i export
3. JSON file delivery (web için CDN'de host)
4. Web'de `lottie-web` library ile render:
   ```html
   <div id="logo-anim"></div>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
   <script>
     lottie.loadAnimation({
       container: document.getElementById('logo-anim'),
       renderer: 'svg',
       loop: false,
       autoplay: true,
       path: '/assets/logo-stinger.json'
     });
   </script>
   ```
5. iOS: `lottie-ios` (Swift Package), Android: `lottie-android` (Gradle)

### Lottie Limitations (Brand Designer'ı Bilmeli)
- **Layer style effects**: Drop-shadow, glow ✗ (hacky workarounds)
- **Some blend modes**: Subset only
- **Text rendering**: Glyphs as paths (font dosyası gerekmez ama text edit edilemez)
- **3D**: Limited support (no real 3D layers)
- **Audio**: Lottie ses çalmaz; ayrıca audio track gerek

### Designer Brief'inde Belirt
brand-visual çıktısı, designer'a şunu hand-off eder:
- **Composition size**: 1024×1024 (master), 512×512 (mobile-optimized)
- **Frame rate**: 60fps (web/mobile native)
- **Duration**: max 2.5s (per logo-stinger ceiling)
- **Easing curves**: per archetype motion spec
- **Background**: transparent (alpha)
- **Color tokens**: Brand `--brand-9` ve accent
- **Export settings**: Bodymovin → "Standard" preset, Glyphs ON, Hidden layers OFF

---

## Light vs Dark Mode Variants — KRİTİK

Bir logo animasyonu light background'da çalışıyorsa **dark background'da çalışmayabilir**. Aşağıdaki sebepler:
- White-fill sembol koyu arkaplanda görünmez (invert gerek)
- Drop-shadow / glow effect dark mode'da yanlış görünür
- Stroke-only logoda thin lines koyu arka planda absorbe olur

**Brand book'ta her motion variant için** light + dark mode örneği şart.

---

## Motion Brand Voice — Senaryolar

### Senaryo 1: Premium B2B SaaS (Sage + Premium tonality)
```
Personality:    Considered, slow, intentional. Akademik dinginlik.
Logo stinger:   2.1s (Sage default 1.5s × premium 1.4 modifier)
Easing primary: cubic-bezier(0, 0, 0.2, 1)
Primitives:     scholarly-reveal, measured-fade, centered-stillness
No-go:          spring-bounce, decorative flourish, playful overshoot
```
**Örnek brands**: McKinsey, Salesforce premium tier, Linear, Notion enterprise.

### Senaryo 2: Disruptor DTC Coffee (Outlaw + Cesur tonality)
```
Personality:    Asi, bozuk, kasıtlı tutarsızlık.
Logo stinger:   0.7s (Outlaw default 0.8s × bold 0.85 modifier)
Easing primary: cubic-bezier(0.7, 0, 0.84, 0) ease-in-cut
Primitives:     glitch-cut, harsh-snap, torn-reveal
No-go:          smooth bezier, gentle ease, perfectionist polish
```
**Örnek brands**: Liquid Death, Onyx Coffee Lab, Compass Coffee.

### Senaryo 3: Pediatric Clinic (Caregiver + Sıcak tonality)
```
Personality:    Soft, protective, slow-down. 'Her şey yolunda' hissi.
Logo stinger:   2.0s (Caregiver default 1.8s × sıcak 1.10 modifier)
Easing primary: cubic-bezier(0.215, 0.61, 0.355, 1) ease-out-soft
Primitives:     soft-fade, embrace-scale, warm-pulse
No-go:          harsh cut, aggressive snap, anxiety-inducing flicker
```
**Örnek brands**: Lovevery, Maisonette, ozlemmurzoglu.com.

---

## Hand-off Specification — Designer'a Verilecek

`brand-visual` Adım 5 çıktısının motion bölümü, motion designer'a şunu sunar:

```markdown
## Motion Brief — [Marka Adı] Logo Stinger

**Hedef**: 1024×1024 logo entry animation, web (Lottie) + video (MP4 ProRes 4444)

**Marka motion personality**:
[motion_spec_generator.py'den çıkan archetype-based personality statement]

**Duration**: [logo-stinger value, max 2.5s]
**Frame rate**: 60 fps (web optimized)
**Easing primary**: [archetype-specific cubic-bezier]
**Easing secondary**: [archetype-specific]

**Animation breakdown** (designer fills in):
- 0.0s — 0.3s:  [primitive 1, e.g. logomark scales from 80% to 100% with ease-out-decisive]
- 0.3s — 1.0s:  [primitive 2, e.g. logotype types in left-to-right with stagger]
- 1.0s — 2.0s:  [primitive 3, e.g. tagline fades in below]

**Color tokens**:
- Primary fill: var(--brand-9) [HEX]
- Background: transparent (master) / var(--brand-1) (light demo) / var(--brand-12) (dark demo)

**Variants required**:
- Light mode (transparent)
- Dark mode (transparent, with white logo fill if needed)

**Delivery formats**:
- Master: After Effects .aep
- Web: Lottie JSON (via Bodymovin export, "Standard" preset)
- Video: MP4 ProRes 4444 (transparent background)
- Animated GIF: 480px max width fallback (legacy email clients)

**No-go zone**: [archetype-specific don'ts]
```

`scripts/motion_spec_generator.py --archetype <X> --tonality <Y> --emit-lottie` komutu bu brief'i + Lottie skeleton JSON'u otomatik üretir.

---

## Implementation Tools

### Production
- **Adobe After Effects** — Industry standard motion design
- **Bodymovin plugin** — AE → Lottie export
- **LottieFiles plugin** — Alternative AE → Lottie export + cloud library
- **Rive** — Interactive Lottie alternatives, real-time state machines
- **Haiku Animator** — Open-source AE alternative

### Web Rendering
- **lottie-web** — Official Airbnb/LAC web renderer
- **dotLottie** — Compressed Lottie format (.lottie), 60% smaller
- **Lottie Player Web Component** — `<lottie-player src="..."/>`

### Mobile
- **lottie-ios** — Native iOS (Swift)
- **lottie-android** — Native Android (Java/Kotlin)
- **lottie-react-native** — Cross-platform RN

### CSS-Only Alternatives (Lottie kurmadan)
- **Animate.css** — Pre-built CSS animations
- **Framer Motion** (React) — Declarative motion library
- **GSAP** — Tween library, paid pro
- **Motion One** — Lightweight web animation API

---

## Brand Book'ta Motion Bölümü Şablonu

```markdown
# Motion Language

## Personality
[1-paragraph statement from motion_spec_generator.py]

## Duration Ladder
[Table from spec]

## Easing Curves
[Primary + Secondary cubic-beziers]

## Animation Primitives
[Allowed: list]
[Forbidden: list]

## Logo Stinger
[Embedded Lottie or video preview]
[Duration: X.Xs at 60fps]
[Variants: light + dark mode]

## Don't
- Don't exceed 2.5s for logo stinger
- Don't use forbidden primitives [list]
- Don't combine ease-out-decisive with ease-in-out-romantic (mismatch)
- Don't animate logo on every page load (annoying)
- Don't apply motion to typography wordmark (hard to read)

## Implementation Resources
- Lottie JSON: [url to brand asset]
- After Effects source: [internal link]
- CSS easing variables: see design-system-tokens.md
```

---

## Sonuç: Motion as Brand Asset

> 2026'da motion bir özellik değil, **bir marka boyutudur**. Renk paleti gibi, font ailesi gibi, logo şekli gibi — motion'un da kendi kuralı, kendi kişiliği, kendi yasağı vardır.

`brand-visual` skill, bu boyutu **arketipinize bağlı, sistemik ve ölçülebilir** bir form'da kodlar. AI çıktıdaki concept logo'dan başlayarak, **production-ready motion brief**'e kadar zincirin tamamını docs eder.

`scripts/motion_spec_generator.py` bunu çalıştırılabilir bir araç olarak verir.
