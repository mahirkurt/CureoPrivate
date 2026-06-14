# Design System Tokens — Mimari ve Multi-Brand Orchestration

> **Bu dosya `brand-visual` skill'inin Adım 5 işleminde aktif kullanılır.**
> Modern marka kimliği bir logo değil, bir **tasarım sistemidir**. Sistemin kalbi: **design tokens** — markanın tüm görsel kararlarının makine-okunabilir, platform-bağımsız ifadesi.

---

## Felsefi Temel (2026 Paradigması)

> "In 2026, design tokens have evolved from simple key-value pairs (`color-primary: #000`) into multi-dimensional data objects that contain logic, intent, and cross-platform mapping." — Presta Design Systems Report 2026

Tokens = **markanın DNA'sının kod-haline gelmiş hali**. Bir HEX kodu değil — bir **anlam**:

❌ `--color-blue-500: #5B5BD6;` — sadece bir renk
✓ `--brand-action-primary: var(--blue-9);` — **anlam** (action color, primary intent)

Bu ayrımın yarattığı güç: rebrand veya dark mode geçişinde, **tek bir token** değişir, tüm sistem güncellenir.

---

## TOKEN HİYERARŞİSİ — 3 KATMAN

Modern design system architecture **3 katmanlıdır**:

### Katman 1 — PRIMITIVE TOKENS (Foundation)

Ham değerler. **Brand-agnostic**. Sadece ölçüm/renk/ses-değer:

```json
{
  "color": {
    "blue": {
      "100": { "$value": "#E6E6FB", "$type": "color" },
      "500": { "$value": "#5B5BD6", "$type": "color" },
      "900": { "$value": "#2E2E80", "$type": "color" }
    }
  },
  "spacing": {
    "1": { "$value": "0.25rem" },
    "4": { "$value": "1rem" },
    "8": { "$value": "2rem" }
  }
}
```

> **Primitive tokens componenent'larda DOĞRUDAN kullanılmaz.** Onlar sadece **palette**dir.

### Katman 2 — SEMANTIC TOKENS (Intent)

Anlam katmanı. Primitive token'lara **referans** verir:

```json
{
  "color": {
    "background": {
      "primary": { "$value": "{color.gray.100}" },
      "subtle": { "$value": "{color.gray.50}" }
    },
    "text": {
      "primary": { "$value": "{color.gray.900}" },
      "subtle": { "$value": "{color.gray.700}" },
      "inverse": { "$value": "{color.gray.50}" }
    },
    "action": {
      "primary": { "$value": "{color.blue.500}" },
      "primary-hover": { "$value": "{color.blue.600}" },
      "destructive": { "$value": "{color.red.500}" }
    },
    "border": {
      "default": { "$value": "{color.gray.300}" },
      "focus": { "$value": "{color.blue.500}" }
    }
  }
}
```

> **Component'lar yalnızca semantic token'ları kullanır.** Primitive ile semantic arasındaki ayrım, **rebrand fleksibilitesini** sağlar.

### Katman 3 — COMPONENT TOKENS (Specific)

En spesifik. Bir component'ın belirli bir state'i için. Semantic token'lara referans verir:

```json
{
  "button": {
    "primary": {
      "background": { "$value": "{color.action.primary}" },
      "background-hover": { "$value": "{color.action.primary-hover}" },
      "text": { "$value": "{color.text.inverse}" },
      "border-radius": { "$value": "{radius.md}" },
      "padding-x": { "$value": "{spacing.4}" },
      "padding-y": { "$value": "{spacing.2}" }
    }
  }
}
```

### Hiyerarşi Görselleştirme

```
COMPONENT TOKENS  →  SEMANTIC TOKENS  →  PRIMITIVE TOKENS
button.primary       color.action          color.blue
.background          .primary              .500
   ↓                    ↓                     ↓
[Component]         [Intent layer]        [Raw value]
[Specific use]      [Brand meaning]       [Just hex]
```

---

## W3C DESIGN TOKENS FORMAT MODULE

W3C Community Group tarafından geliştirilen **standart spec**. 2024'te draft yayımlandı, 2026 itibariyle ana foundation.

### Spec URL
- **Specification**: https://design-tokens.github.io/community-group/format/
- **Tools-friendly**: Style Dictionary, Tokens Studio, Specify, Supernova

### Kanonik Format

```json
{
  "$schema": "https://design-tokens.org/draft-1.json",

  "color": {
    "brand": {
      "$type": "color",

      "primary": {
        "$value": "#5B5BD6",
        "$description": "Primary brand action color. Used for CTA buttons, key highlights, primary links."
      },

      "primary-hover": {
        "$value": "{color.brand.primary}",
        "$extensions": {
          "com.brand-visual.opacity-mod": 0.85
        },
        "$description": "Brand primary hover state. 85% opacity overlay."
      }
    }
  },

  "typography": {
    "$type": "typography",

    "heading-1": {
      "$value": {
        "fontFamily": "{font.family.display}",
        "fontSize": "{font.size.5xl}",
        "fontWeight": 700,
        "lineHeight": "{font.line-height.tight}",
        "letterSpacing": "{font.tracking.tight}"
      }
    }
  },

  "shadow": {
    "$type": "shadow",
    "elevation-1": {
      "$value": {
        "color": "{color.gray.900}",
        "offsetX": "0",
        "offsetY": "1px",
        "blur": "2px",
        "spread": "0",
        "type": "dropShadow"
      }
    }
  }
}
```

### Token Types

| Type | Example | Use |
|------|---------|-----|
| `color` | `"#5B5BD6"` | Renk değerleri |
| `dimension` | `"1.5rem"`, `"24px"` | Boyut (spacing, sizing) |
| `fontFamily` | `["Inter", "sans-serif"]` | Font family stack |
| `fontWeight` | `400`, `"semibold"` | Font weight |
| `duration` | `"250ms"` | Animation/transition |
| `cubicBezier` | `[0.4, 0, 0.2, 1]` | Easing function |
| `number` | `1.5` | Numeric (line-height, opacity) |
| `typography` | `{...}` composite | Typography composite |
| `shadow` | `{...}` composite | Shadow composite |
| `border` | `{...}` composite | Border composite |
| `transition` | `{...}` composite | Transition composite |
| `gradient` | `[{...}]` array | Gradient stops |

---

## MULTI-BRAND ORCHESTRATION

Modern enterprise senaryosu: **bir core codebase, çoklu brand skin** (örn: Shopify storefronts, Roche'un global vs Türkiye marka adaptation, Anthropic Claude vs internal dev tools).

### Architecture: Hybrid Approach

```
┌─────────────────────────────────────────┐
│   COMPONENT LIBRARY (single codebase)   │
│   <Button>, <Input>, <Card>, etc.       │
└──────────┬──────────────────────────────┘
           │ consumes
           ↓
┌─────────────────────────────────────────┐
│   COMPONENT TOKENS                      │
│   button.primary.background, etc.       │
└──────────┬──────────────────────────────┘
           │ references
           ↓
┌─────────────────────────────────────────┐
│   SEMANTIC TOKENS                       │
│   color.action.primary, etc.            │
└──────────┬──────────────────────────────┘
           │ references
           ↓
┌─────────────────────────────────────────┐
│   PRIMITIVE TOKENS                      │
│   ┌──────────────────────────────────┐  │
│   │  Brand A: indigo, sage, warm     │  │
│   │  Brand B: terra, sand, premium   │  │
│   │  Brand C: black, neon, disrupt   │  │
│   └──────────────────────────────────┘  │
│   Switchable per environment            │
└─────────────────────────────────────────┘
```

### Practical Implementation (Tailwind + Radix Style)

```javascript
// tailwind.config.js — multi-brand
const brand = process.env.BRAND || 'default';

const brandTokens = require(`./tokens/brands/${brand}.json`);

module.exports = {
  theme: {
    extend: {
      colors: brandTokens.color,
      fontFamily: brandTokens.font,
      // ...
    },
  },
};
```

### Build-Time vs Runtime Switching

| Approach | Pro | Con | Use |
|----------|-----|-----|-----|
| **Build-time** (env-based) | Performance, smaller bundle | Restart per brand | Static sites, separate deployments |
| **Runtime** (CSS vars + class) | Single bundle, instant switch | Slightly larger bundle | Multi-tenant SaaS, white-label products |
| **Module Federation** (Webpack 5+) | Isolated brand modules | Complex setup | Micro-frontend architectures |

> **Önerilen default**: Runtime (CSS vars), data-attribute switching (`data-brand="default"`, `data-theme="dark"`).

---

## STYLE DICTIONARY — TOKEN BUILD PIPELINE

**Style Dictionary** (Amazon, OFL): tokens.json → multi-platform output (CSS, JS, Swift, Kotlin, XML).

### Setup

```bash
npm install -D style-dictionary
```

### Config

```javascript
// style-dictionary.config.js
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'build/css/',
      files: [{ destination: 'tokens.css', format: 'css/variables' }],
    },
    js: {
      transformGroup: 'js',
      buildPath: 'build/js/',
      files: [{ destination: 'tokens.js', format: 'javascript/es6' }],
    },
    ios: {
      transformGroup: 'ios-swift',
      buildPath: 'build/ios/',
      files: [{ destination: 'Tokens.swift', format: 'ios-swift/class.swift', className: 'BrandTokens' }],
    },
    android: {
      transformGroup: 'android',
      buildPath: 'build/android/',
      files: [{ destination: 'colors.xml', format: 'android/colors' }],
    },
  },
};
```

### Output (CSS örneği)

```css
:root {
  --color-brand-primary: #5B5BD6;
  --color-text-primary: #2E2E80;
  --spacing-4: 1rem;
  --typography-heading-1-font-size: 3.052rem;
  --typography-heading-1-font-weight: 700;
}
```

### Build

```bash
npx style-dictionary build
```

---

## FIGMA VARIABLES — DESIGNER ↔ DEVELOPER SYNC

Figma Variables (2023+) = design tools'ta token native support. Multi-mode (light/dark/brand-A/brand-B) destekli.

### Tokens Studio Plugin (en güçlü)

Free + Pro version. Tokens.json'u Figma'da read/write.

### Sync Pattern

```
Designer (Figma) ←→ Tokens Studio Plugin ←→ GitHub Repo (tokens.json)
                                                     ↓
                                                  Build pipeline
                                                     ↓
                                          CSS / JS / Swift / Kotlin
                                                     ↓
                                                  Application
```

### Variable Modes (Figma Native)

```
[Tema/Brand]
  - Default Mode
  - Dark Mode
  - Brand A
  - Brand B
  - High Contrast
```

Bir Variable (örn: `color/brand-primary`) tüm mode'larda farklı değer alır. Frame seçilen mode'u takip eder.

---

## MCP SERVER OLARAK DESIGN SYSTEM (2026 TREND)

> **Yeni paradigma** (Presta 2026 Report): "By exposing your design system as an MCP (Model Context Protocol) server, you provide autonomous agents with the structured context they need to understand and navigate your UI accurately and efficiently."

Design system, AI agent'ları (browsing agent, code generation, autonomous shopping) için **structured API** olarak expose edilir.

### MCP Design System Server Spec

```yaml
# design-system-mcp.yaml
server:
  name: "brand-design-system"
  description: "Component library and design tokens for [Brand]"

resources:
  - tokens.json (W3C Design Tokens format)
  - components.json (component manifests)
  - guidelines.md (usage rules)

tools:
  - get_token(name: string) → returns token value
  - get_component_props(component: string) → returns valid props
  - check_component_usage(html: string) → returns compliance report
```

> **Implementation**: Mahir'in `smp-orchestrator` skill'i bu pattern'i marka skill'leri için uyguluyor — `brand-visual` çıktısı bir SMP-uyumlu manifest olarak diğer skill'lere expose edilir.

---

## TOKEN NAMING CONVENTIONS

Token naming **brand cohesion**'un ilk göstergesidir. Tutarlılık zorunlu.

### Pattern: `category.scale.purpose.modifier`

| Pattern | Örnek | Açıklama |
|---------|-------|----------|
| `category.value` | `color.blue` | Primitive |
| `category.scale.intensity` | `color.blue.500` | Primitive scaled |
| `category.purpose` | `color.background` | Semantic |
| `category.purpose.variant` | `color.background.primary` | Semantic with variant |
| `component.purpose.state` | `button.primary.hover` | Component-specific |

### Naming Conventions Comparison

| Standard | Naming | Pro | Con |
|----------|--------|-----|-----|
| **Tailwind** | `text-blue-500` | Compact, utility-first | Primitive-heavy |
| **Material Design** | `md.sys.color.primary` | Semantic-first | Verbose |
| **IBM Carbon** | `$layer-01`, `$text-primary` | Semantic system | Brand-specific terminology |
| **Salesforce Lightning** | `--lwc-color-text-default` | Prefix isolation | Long names |
| **Radix** | `--blue-9` | Numerical clarity | Less semantic |
| **W3C Design Tokens** | `{color.brand.primary}` | Standardized | Less compact |

> **Önerilen yaklaşım**: Hibrit — primitive için Radix-style numerical (`--brand-9`), semantic için descriptive (`--color-action-primary`).

---

## RAPOR ENTEGRASYONU (Adım 5'te kullan)

```markdown
## Design Token Architecture

### Primitive Tokens (Foundation Palette)
[12-step color scales: brand, accent, gray + functional]
[Spacing scale: 4px base, 8pt grid]
[Typography scale: 1.250 modular]
[Radii, shadows, motion durations]

### Semantic Tokens (Intent Layer)
| Token | References | Use |
|-------|-----------|-----|
| `--color-action-primary` | `{brand.9}` | CTA buttons, primary links |
| `--color-text-primary` | `{gray.12}` | Body, headings |
| `--color-text-subtle` | `{gray.11}` | Secondary text |
| `--color-bg-app` | `{gray.1}` | Page background |
| `--color-bg-surface` | `{gray.2}` | Card, modal background |
| `--color-border-default` | `{gray.6}` | Component borders |
| `--color-border-focus` | `{brand.8}` | Focus ring |

### Component Tokens (Specific)
[Button, Input, Card, Modal etc. — semantic referenced]

### Multi-Mode Support
- Default (light)
- Dark
- High Contrast (accessibility)
- [Brand variants if applicable]

### Build Pipeline
- Source: `tokens/**/*.json` (W3C Design Tokens format)
- Build: Style Dictionary → CSS, JS, Swift, Kotlin
- Sync: Tokens Studio plugin (Figma) ↔ GitHub
```

---

## EXPORT TEMPLATE — FULL DESIGN SYSTEM JSON

Bu format, `assets/design-tokens-export.json` olarak kaydedilir ve diğer skill'lere (carbon-pptx, medmarketing) geçirilir:

```json
{
  "$schema": "https://design-tokens.org/draft-1.json",
  "metadata": {
    "brand": "[Brand Name]",
    "version": "1.0.0",
    "generated": "2026-04-15",
    "generator": "brand-visual v1.0"
  },

  "color": {
    "brand": { "1": {...}, "2": {...}, /* ... 12 ... */ },
    "accent": { "1": {...}, /* ... */ },
    "gray": { "1": {...}, /* ... */ },
    "functional": {
      "success": { "9": {...} },
      "error": { "9": {...} },
      "warning": { "9": {...} },
      "info": { "9": {...} }
    }
  },

  "typography": {
    "family": {
      "display": {...},
      "body": {...},
      "mono": {...}
    },
    "scale": { "xs": {...}, /* ... 5xl ... */ },
    "weight": { "regular": {...}, /* ... */ },
    "lineHeight": {...},
    "tracking": {...},
    "composite": {
      "logotype": {...},
      "heading-1": {...},
      "body-default": {...}
    }
  },

  "spacing": {
    "1": { "$value": "0.25rem" },
    "2": { "$value": "0.5rem" },
    "4": { "$value": "1rem" },
    "8": { "$value": "2rem" }
  },

  "radius": { "sm": {...}, "md": {...}, "lg": {...}, "full": {...} },

  "shadow": { "sm": {...}, "md": {...}, "lg": {...} },

  "motion": {
    "duration": { "fast": {...}, "base": {...}, "slow": {...} },
    "easing": { "standard": {...}, "decelerate": {...}, "accelerate": {...} }
  }
}
```

---

## YAYGIN HATALAR

### Hata 1 — Sadece primitive layer
❌ Component'ta direkt `color: #5B5BD6;` kullanım
✓ Component → semantic → primitive zinciri

### Hata 2 — Token name = renk adı
❌ `--color-blue: #5B5BD6` (intent yok)
✓ `--color-action-primary: var(--blue-9)` (intent + reference)

### Hata 3 — Magic numbers
❌ `padding: 13px;` (random)
✓ `padding: var(--spacing-4);` (token)

### Hata 4 — Multi-brand için duplicate primitive
❌ Brand A'nın blue paleti ile Brand B'nin blue paleti **farklı dosyalarda** kopya
✓ Tek primitive, brand-spesifik semantic mapping

### Hata 5 — Tokens.json sürüm kontrolü yok
❌ Figma'da değiştirilen tokens kod tarafına manuel sync
✓ Tokens Studio + Git + CI/CD pipeline

---

## KAYNAKLAR

- **W3C Design Tokens Spec**: design-tokens.github.io/community-group
- **Style Dictionary**: amzn.github.io/style-dictionary
- **Tokens Studio**: tokens.studio (Figma plugin)
- **Specify**: specifyapp.com (token management platform)
- **Supernova**: supernova.io (design system platform)
- **Figma Variables Docs**: help.figma.com/hc/en-us/articles/15145852043927
- **Radix UI Themes**: radix-ui.com/themes (Color + token system reference)
- **Anthropic Design System Public Docs** (eğer açıksa): anthropic.com/design
- **Material Design Tokens**: m3.material.io/foundations/design-tokens
- **IBM Carbon Tokens**: carbondesignsystem.com/elements/themes/overview
- **Presta Design Systems 2026 Report**: wearepresta.com/design-systems-for-scale-2026 (multi-brand orchestration)
