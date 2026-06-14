# Adaptive / Living Identity Systems

> **Route 4 dayanak dosyası.** `brand-visual` v1.3'te eklendi. Yüklenme tetikleyicisi: "adaptive", "fluid", "living", "morphing", "generative", "responsive logo", "dynamic logo", "variable identity" veya Route 4 seçimi.

## Tez

**"A logo is no longer a museum piece. It is an open canvas with a strong frame."** (Kittl 2026 Trend Report)

2026'da marka kimliği tek statik bir işaret olmaktan çıktı. Nike'ın dinamik logo pairings'i, Coca-Cola'nın contextual variants'ı, Adobe Substance 3D cube'un rotation states'i, Google Doodle'ın brand-level extension'ı — bunların hepsi aynı doktrine işaret ediyor: **markanın ruhu (spine) sabit kalır, etrafındaki kabuk (shell) bağlama göre değişir**.

Bu skill protokolünde Route 4 olarak konumlandırılan Adaptive Identity, 2026'nın en büyük brand design trendidir. Ama **her marka için uygun değildir** — doğru arketip (Magician, Explorer, Creator, Jester) + doğru sektör (Tech, Media, Consumer, Retail) + yeterli brand governance altyapısı gerektirir.

---

## Anatomik Yapı: Core Spine + Variable Shell

Adaptive identity iki katmanlı sistemdir:

### Katman 1: Core Spine (Değişmez DNA)
- Her varyasyonda **eksiksiz bulunur**
- %100 sabit geometri, renk, oran
- 16px favicon'da sadece bu görünür
- Trademark başvurusunda bu kaydedilir
- **Marka equity'sinin deposu** — markanın tanınırlığı buradan gelir

**Disiplin**: Core spine yeterince **basit** olmalı (minimum 1-3 primitive form) ve **karakteristik** olmalı (rakiplerden ayrıştırıcı).

### Katman 2: Variable Shell (Değişken Kabuk)
- Bağlama göre değişen outer geometry
- Core'u sarmalayan, tamamlayan, anlamlandıran
- Değişim **kural sistemi** ile disiplinlidir
- Varyasyon sayısı: minimum 3, optimum 5-12, maksimum 24 (yıl içi variants Google Doodle için)

**Disiplin**: Shell değişimi **randomness değil**, **bir logic'e** göre yapılır.

---

## Adaptive Variable Parameters (Neye Göre Değişir)

| Parameter | Açıklama | Örnek Uygulama | Zorluk |
|---|---|---|---|
| **Time** | Saat / gün / mevsim | Coca-Cola Christmas variant, Google Doodle daily | ★★ |
| **Geographic** | Lokasyon / kültür / dil | Coca-Cola regional variants, Airbnb city-specific | ★★★ |
| **Persona** | Kullanıcı segmenti / age / profil | Nike basketball vs running, Spotify Wrapped | ★★★★ |
| **Content Category** | Blog post, product, campaign | Disney+ category-specific title cards | ★★★ |
| **Aspect-Ratio Responsive** | Viewport / format | Mobile vs desktop vs print | ★★ |
| **State** | UI state (loading, success, error) | Adaptive UI logos | ★★★ |
| **Real-Time Data** | Weather, stocks, social trends | Weather app logos, live event | ★★★★★ |
| **User Interaction** | Hover, click, scroll | Interactive web marks | ★★★ |
| **Campaign / Season** | Marketing calendar | Seasonal campaign variants | ★★ |
| **Collaboration** | Partnership co-brand | "X × Y" special edition marks | ★★★ |

**Önerilen başlangıç**: Bir markanın ilk adaptive system'ı için **2-3 parameter** yeterli. Genellikle **Time + Aspect-Ratio Responsive + Campaign**. İlerleyen olgunlukta daha karmaşık parameters eklenir.

---

## Transition Rules (Nasıl Değişir)

### 1. Instant (Binary Switch)
- Logo A → Logo B, arada geçiş yok
- Örnek: Light mode / dark mode logo switch
- CSS: `[data-theme="dark"] .logo-shell { ... }`

### 2. Animated Crossfade
- 200-400ms fade transition
- Nike dynamic logo pairings default transition
- CSS: `transition: opacity 240ms cubic-bezier(0.4, 0.0, 0.2, 1)`

### 3. Morph (Shape Interpolation)
- SVG path interpolation (SMIL veya GSAP MorphSVG)
- En pahalı teknik — custom paths'lerin aynı node sayısına sahip olması gerekir
- Örnek: MIT Media Lab 2011 dynamic identity, Atlassian logo morph animations

### 4. Generative Regeneration
- Her yüklemede programmatic olarak yeni variant üretilir
- Core spine sabit, shell parameters random/seeded
- En ileri seviye; Google Doodle mimarisi

### 5. Stateful (Snapshot)
- Belirli bir context kilidi — "şu anda X varyasyonunda" — ve kullanıcı aynı session'da aynı varyasyonu görür
- Consistency korumak için
- Spotify Wrapped year-end logo

**Tasarım kararı**: Marka olgunluğuna göre seç. Yeni markalar **Instant / Animated Crossfade** ile başlar. Olgun markalar **Morph / Generative** kullanır.

---

## Constraint System: Equity Korumak

Adaptive sistem **tanınırlığı kaybetmemeli**. Kilit sorular:

### Q1: Core Spine ne kadar değişmez kalmalı?
**Cevap**: Minimum **%60 visual consistency** her varyasyonda. Öneri: **core spine pixel-for-pixel identical**, shell %40'a kadar özgür.

### Q2: Renk paleti ne kadar genişleyebilir?
**Cevap**: Primary brand color **her varyasyonda bulunmalı**. Secondary/accent colors değişebilir. Maximum 4 paralel color theme.

### Q3: Tipografi ne kadar esnek olmalı?
**Cevap**: Brand wordmark sabit; adaptive elements içinde supplementary type family için variable font weights (300-700 arası) spectrum izinli.

### Q4: "Favicon test" hâlâ geçerli mi?
**Cevap**: **Evet, kritik olarak.** 16px'te **SADECE core spine** görünür. Shell detayları kaybolur. Core spine bu boyutta **kendi başına tanınabilir** olmalı — yoksa tüm adaptive sistem anlamsız.

### Q5: Ne zaman logo "değişmiş" sayılır (rebrand), ne zaman "varyant"?
**Cevap**: Core spine değişirse = rebrand. Shell değişirse = variant. Markanın **evrim belgesine** core spine change'i kaydedilir.

---

## Implementation Specification Templates

Adım 5.8'de production brief olarak üretilir. Üç teknik yol:

### Yol A: CSS Custom Properties + SVG (Basit, Web-first)

```html
<!-- Core spine SVG -->
<svg class="brand-logo" viewBox="0 0 100 100">
  <defs>
    <symbol id="core-spine" viewBox="0 0 100 100">
      <!-- SABİT geometri buraya -->
      <path d="..." fill="var(--brand-primary)"/>
    </symbol>
  </defs>
  
  <!-- Shell (variable) -->
  <g class="shell">
    <circle cx="50" cy="50" r="var(--shell-radius, 30)" 
            fill="var(--shell-color, transparent)"/>
  </g>
  
  <!-- Core spine (invariant) -->
  <use href="#core-spine"/>
</svg>
```

```css
:root {
  --brand-primary: #5B5BD6;
  --shell-radius: 30;
  --shell-color: transparent;
}

[data-season="winter"] {
  --shell-radius: 35;
  --shell-color: #E8F4FF;
}

[data-season="summer"] {
  --shell-radius: 25;
  --shell-color: #FFF4E8;
}

@media (prefers-color-scheme: dark) {
  :root { --brand-primary: #9F9FF8; }
}
```

### Yol B: Figma Variants + Design Tokens

- Figma Variants ile 4-12 state tanımla
- Each variant = different parameter combination
- Design tokens (W3C DTCG) ile paylaş
- Token Studio / Style Dictionary pipeline'ı ile CSS/JSON export
- Developer handoff: tokens consume eder

### Yol C: Programmatic Generative SVG

```javascript
// Core spine fixed
const coreSpine = `<path d="..." fill="${brand.primary}"/>`;

// Shell generated based on context
function generateShell(context) {
  const { season, persona, time } = context;
  const hue = calculateHue(season, time);
  const shape = selectShape(persona);
  return `<${shape} style="fill: hsl(${hue}, 50%, 50%)"/>`;
}

function renderAdaptiveLogo(context) {
  return `<svg viewBox="0 0 100 100">
    ${generateShell(context)}
    ${coreSpine}
  </svg>`;
}
```

---

## Case Study Library (2026 Kanonik Örnekler)

### Case 1 — Nike Dynamic Logo Pairings (2024+)
- **Core spine**: Swoosh (Carolyn Davidson, 1971, sabit)
- **Variable shell**: Sport category, collaboration, campaign-specific color + type pairing
- **Variants count**: 50+ pairings (Nike Run Club, Nike Basketball, Off-White × Nike, Air Jordan sub-brand)
- **Parameter**: Primarily persona (sport/audience)
- **Transition**: Instant (context-based)
- **Lesson**: Core spine bir sembol kadar sabit olmalı; shell bir typography system kadar genişletilebilir.

### Case 2 — Adobe Substance 3D Cube (2023+)
- **Core spine**: 3D cube geometric form
- **Variable shell**: Each product (Painter, Designer, Sampler, Stager) farklı rotation state + accent color
- **Variants count**: 5 product + master brand
- **Parameter**: Content category (hangi product)
- **Transition**: Instant (product-based)
- **Lesson**: Tactile dimensional refinement (Trend 8) + Adaptive (Route 4) kombinasyonu enterprise tech için güçlü.

### Case 3 — Google Doodle Architecture (2001+)
- **Core spine**: "Google" wordmark letterforms
- **Variable shell**: Daily illustration variant, sometimes replacing letter entirely
- **Variants count**: Thousands over years
- **Parameter**: Time (daily) + Event (anniversaries, holidays)
- **Transition**: Instant (daily), animated variants mevcut
- **Lesson**: Brand equity o kadar güçlü ki "G" harfi bir letterform olarak silinse bile Google tanınıyor. **Bu güven yoksa adaptive system erken aşamada uygulanmaz.**

### Case 4 — MIT Media Lab (2011, Sagmeister)
- **Core spine**: 3-line mark
- **Variable shell**: Color + rotation variants
- **Variants count**: 40+ (her lab member + her deparment farklı)
- **Parameter**: Persona (internal unit) + generative
- **Transition**: Generative (algorithmic)
- **Lesson**: Generative morphing, research/academic kurumlarda çok güçlü — "complexity as identity".

### Case 5 — Coca-Cola Contextual Variants (2020+)
- **Core spine**: Spencerian script wordmark + white
- **Variable shell**: Background context, special edition bottle design, event variants
- **Parameter**: Campaign + season + geographic
- **Transition**: Instant + campaign-defined
- **Lesson**: 100+ yıl brand equity olan markalarda bile core spine **tek harf dahi değişmez**.

### Case 6 — Airbnb "Belo" Variations
- **Core spine**: Belo symbol (4-element composite)
- **Variable shell**: Colorway varyasyonu + city-specific illustration ile kombinasyon
- **Variants count**: 10+ (global campaign)
- **Parameter**: Geographic (destination) + campaign
- **Lesson**: Adaptive identity brand values'unu (belonging, home, welcome) uygulamada yaşatabilir.

---

## Adaptive Identity Doctrine — 10 Kural

1. **Core spine favicon-grade simple olmalı** — 16px test geçmeli.

2. **Shell equity'ye zarar vermemeli** — %60 minimum visual consistency.

3. **Minimum 3 varyant, maksimum 24** — 3'ten az = static, 24'ten fazla = kaos.

4. **Her varyant stratejik bir gerekçe taşımalı** — "güzel oldu" yeterli değil.

5. **Core rengi her varyantta bulunmalı** — secondary değişebilir.

6. **Brand governance altyapısı zorunlu** — guideline + DAM + variant library.

7. **Transition tipi brand personality'ye uymalı** — Sage brand morphing yapmaz, instant switches kullanır.

8. **Değişim bir idea'yı desteklemeli** — değişim için değişim değersiz.

9. **Accessibility korunmalı** — her varyantta WCAG AA kontrast, her varyantta CVD test.

10. **C2PA provenance her varyantta korunmalı** — AI-generated adaptive elements için.

---

## Adım 5.8 Output Template (Bu Dosyayı Kullanarak)

Route 4 seçildiğinde Adım 5.8'de üretilen yapı:

```markdown
## 5.8 Adaptive Identity Rules

### Core Spine Specification
- **Geometry**: [SVG path description / image reference]
- **Dimensions**: [X units wide × Y units tall, aspect X:Y]
- **Primary color**: [HEX + Pantone]
- **Scalability**: Favicon-grade 16px silhouette confirmed
- **Trademark status**: This is the registered mark

### Variable Parameters
1. **[Parameter 1 — e.g., Season]**
   - Input values: [spring / summer / autumn / winter]
   - Triggered element: [shell color palette]
   - Range: [4 discrete states]

2. **[Parameter 2 — e.g., Aspect Ratio]**
   - Input values: [1:1 / 16:9 / 9:16 / 3:1]
   - Triggered element: [composition rebalancing]
   - Range: [continuous responsive]

3. **[Parameter 3]**
   - ...

### Variant Library (Minimum 3, Optimum 5-12)
| ID | Name | Parameter State | Preview | Usage Context |
|----|------|-----------------|---------|---------------|
| V01 | Primary | Default (all defaults) | [SVG] | Master brand asset |
| V02 | Winter | Season=winter | [SVG] | Nov-Feb campaigns |
| V03 | Summer | Season=summer | [SVG] | Jun-Aug campaigns |
| V04 | Mobile | AR=9:16 | [SVG] | App icon, story |
| V05 | Print | AR=1:1 + muted | [SVG] | Print collateral |

### Transition Rules
- **Within web UI**: [Animated crossfade 240ms cubic-bezier(0.4, 0.0, 0.2, 1)]
- **Between campaigns**: [Instant switch]
- **Print / static**: [Variant locked per asset]
- **Reduced-motion preference**: [Instant switch, no animation]

### Constraint System
- **Core visual consistency**: ≥ 60% geometric overlap
- **Primary brand color**: Mandatory in all variants
- **Favicon rendering (16px)**: Core spine only, shell stripped
- **Trademark boundary**: Only core spine registered; variants documented in brand book

### Implementation Spec (Technical Brief for Dev / Design Team)

**Yol seçim**: [A = CSS + SVG / B = Figma Variants + Design Tokens / C = Programmatic Generative]

**Design tokens** (W3C DTCG format):
```json
{
  "brand": {
    "core-spine": { "$type": "other", "$value": "[SVG reference]" },
    "primary": { "$type": "color", "$value": "#5B5BD6" },
    "shell": {
      "winter": { "$value": "#E8F4FF" },
      "summer": { "$value": "#FFF4E8" }
    },
    "transition-duration": { "$type": "duration", "$value": "240ms" }
  }
}
```

**CSS hook example**: [kod örneği]
**JavaScript handler example**: [kod örneği]
**Figma file structure**: [component library layout]

### Governance Requirements
- **Variant approval workflow**: [Brand team review process]
- **DAM (Digital Asset Management)**: [Tool + folder structure]
- **Usage guideline document**: [Brand book section X]
- **Annual variant review**: [Q4 of each year]

### Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Variant proliferation (>24) | Medium | Annual cull + 3-variant rule |
| Equity dilution | Low | Core spine constraint ≥60% |
| Inconsistent implementation | High | Design tokens + automation |
| Accessibility regression | Medium | Per-variant WCAG + CVD test |
```

---

## Arketip-Adaptive Affinity Matrix

Hangi arketipler adaptive identity için natively uygun?

| Arketip | Affinity | Gerekçe |
|---------|:-:|---|
| **Magician** | ★★★★★ | Transformation DNA'da — adaptive = marka özü |
| **Explorer** | ★★★★★ | Discovery/journey = context-responsive |
| **Creator** | ★★★★ | Remix/play — adaptive iyi partner |
| **Jester** | ★★★★ | Playful variants native uygun |
| **Outlaw** | ★★★ | Rebellion = expected unpredictability |
| **Ruler** | ★★ | Stability beklenir — adaptive gergin |
| **Hero** | ★★★ | Mission-focused — limited adaptive |
| **Sage** | ★★★ | Wisdom consistency bekler — subtle adaptive |
| **Everyman** | ★★★ | Relatability için persona-variant uygun |
| **Lover** | ★★ | Intimate consistency — adaptive zor |
| **Innocent** | ★★ | Purity/simplicity — minimum adaptive |
| **Caregiver** | ★★ | Trust = stability — adaptive risk |

**Doktrin**: Adaptive identity **her markaya değil, doğru markaya**. Magician/Explorer/Creator/Jester markaları için Route 4 default tercih. Ruler/Innocent/Caregiver markaları için Route 2 Geometric (static) daha uygun.

---

## Red Lines (Adaptive için)

1. **Core spine'ı değiştirme** — "genel güncelleme" için bile değiştirmek = rebrand = marka equity kaybı.
2. **Variant proliferasyonu** — yıllık cull olmadan varyant biriktirme = kaos.
3. **Automation zorunluluğu** — manuel variant yönetimi ölçekte başarısız. Design tokens pipeline zorunlu.
4. **Brand governance eksikliği** — marka guideline + onay süreci olmadan adaptive başlatma = **kontrolsüz evrim**.
5. **Accessibility testlerini atlama** — her varyant ayrı test edilmeli; "core kabul edildi" yetmez.
6. **Gereksiz karmaşıklık** — küçük marka + küçük team için Route 4 genelde over-engineered. Route 2 (static) + yıllık campaign refresh yeterli olabilir.

---

> **Kapanış doktrini**: Adaptive identity **bir kimlik sistemi**, bir **koleksiyon** değil. Core spine marka DNA'sıdır. Variable shell marka hikâyesidir. İkisi birbirini besler — ayrı düşerse kimlik dağılır. Pentagram'ın Casa da Música doktrini: *"Brand = system, not logo. Identity = rules, not image."*
