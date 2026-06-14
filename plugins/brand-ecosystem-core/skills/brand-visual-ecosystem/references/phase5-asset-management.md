# Phase 5 Asset Management — Reference for brand-visual

Loaded when brand-visual produces outputs that will flow downstream to brand-launch's Phase 5 governance infrastructure.

## Why asset management matters at brand-visual stage

Most brand-visual work focuses on the design itself — the logo, the color palette, the typography system. The asset management dimension — how these will live in production, how they will be governed, how they will be deployed across brand center + brand guidelines + touchpoints — is often deferred to "later" and then poorly handled.

When brand-visual anticipates Phase 5 from the outset, the outputs are production-ready:
- File naming conventions established
- Variant management systematic
- Design tokens prepared for design system deployment
- Asset packaging ready for brand center upload

This saves Phase 5 enormous work and prevents drift.

## Asset packaging discipline

### Logo files

Every logo variant produced in a complete package:

```
logos/
├── primary/
│   ├── full-color/
│   │   ├── brand-primary-fullcolor.svg
│   │   ├── brand-primary-fullcolor.eps
│   │   ├── brand-primary-fullcolor.png (4 sizes: 256, 512, 1024, 2048)
│   │   └── brand-primary-fullcolor.pdf
│   ├── single-color/
│   │   ├── brand-primary-black.svg + eps + png + pdf
│   │   └── brand-primary-white.svg + eps + png + pdf
│   └── knockout/
│       └── brand-primary-knockout.svg + eps + png + pdf
├── secondary/
│   └── [same structure for secondary lockup if exists]
├── monochrome/
│   └── [single-color treatments]
├── favicon/
│   ├── favicon-16.png
│   ├── favicon-32.png
│   ├── favicon-180.png (Apple touch icon)
│   └── favicon-512.png (PWA / manifest)
└── special-applications/
    ├── embroidery-spec.pdf (uniform stitching brief)
    ├── etching-spec.pdf (glass/metal etching brief)
    └── signage-spec.pdf (large-format signage brief)
```

This structure is what brand-launch expects to deploy to brand center.

### Color palette package

```
colors/
├── primary-palette/
│   ├── color-1.hex (with sidecar JSON: hex, RGB, CMYK, Pantone, name)
│   ├── color-2.hex
│   └── ...
├── secondary-palette/
│   └── ...
├── functional/
│   ├── success.hex
│   ├── warning.hex
│   ├── error.hex
│   └── info.hex
├── extended-radix/
│   └── [12-step Radix scales per primary color if applicable]
└── ase/
    └── brand-palette.ase (Adobe Swatch Exchange — universal palette file)
```

### Typography package

```
typography/
├── fonts/
│   ├── primary-typeface/
│   │   ├── primary-regular.woff2
│   │   ├── primary-medium.woff2
│   │   ├── primary-bold.woff2
│   │   └── [other weights]
│   ├── secondary-typeface/
│   │   └── [if applicable]
│   └── variable/
│       └── brand-variable.woff2 (if variable font)
├── licenses/
│   ├── license-document.pdf
│   └── license-terms.md
├── webfont-css/
│   └── @font-face declarations
└── specimen-pdf/
    └── full-typography-specimen.pdf
```

License documentation MUST accompany font files. Phase 5 brand center deployment requires license clarity.

### Icon + illustration libraries

Each library packaged as:
- SVG source files (vector, editable)
- PNG renders at standard sizes
- Manifest JSON listing all icons / illustrations with metadata
- Usage examples

### Photography + video assets

```
photography/
├── hero/
│   └── [hero imagery with metadata sidecars]
├── product/
│   └── ...
├── lifestyle/
│   └── ...
├── portrait/
│   └── [if relevant — leadership, customer portraits]
└── metadata/
    └── photography-metadata.csv (filename, photographer, license, usage rights, expiry)
```

Photography rights / licenses MUST be tracked. Brand center deployment requires usage-rights clarity per asset.

## File naming conventions

Convention recommendation:

```
{brand-prefix}-{category}-{descriptor}-{variant}.{extension}
```

Examples:
- `acmeco-logo-primary-fullcolor.svg`
- `acmeco-icon-search-outline.svg`
- `acmeco-photo-hero-office-001.jpg`

Discipline:
- Lowercase throughout
- Hyphens (not underscores) as separators
- No spaces ever
- No special characters
- Brand prefix consistent across all files
- Descriptive but concise (long names fail at scale)

## Design tokens preparation

When the brand visual identity will deploy into a design system, design tokens must be prepared. Following W3C Design Tokens Community Group (DTCG) standard:

```json
{
  "color": {
    "brand": {
      "primary": {
        "value": "#1A2B3C",
        "type": "color"
      },
      "secondary": {
        "value": "#4D5E6F",
        "type": "color"
      }
    }
  },
  "typography": {
    "heading": {
      "fontFamily": {
        "value": "Brand Display",
        "type": "fontFamily"
      },
      "fontWeight": {
        "value": 700,
        "type": "fontWeight"
      }
    }
  },
  "spacing": {
    "scale": {
      "1": { "value": "4px", "type": "dimension" },
      "2": { "value": "8px", "type": "dimension" },
      "3": { "value": "16px", "type": "dimension" }
    }
  }
}
```

Design tokens enable design system tooling — Figma → Code synchronization, Style Dictionary builds, etc.

If design system deployment is downstream, brand-visual produces design tokens alongside other assets.

## Variant management

A brand visual identity may have variants:
- Sub-brand variants (per architecture decision)
- Language variants (where typography differs by language)
- Cultural variants (regional adaptations)
- Adaptive identity variants (Route 4)

Variant management discipline:
- Single source of truth (one master file per variant)
- Variant manifest (document listing every variant + relationship to master)
- Variant naming convention (consistent suffix indicating variant type)
- Variant governance (which variants require approval to modify vs which are deterministically derived)

## Brand guidelines preparation

Brand-visual outputs should be ready for brand guidelines documentation:

- High-resolution specimen images of each visual element
- Annotated specimens explaining decisions
- Anti-pattern examples (what NOT to do)
- Application examples across touchpoints

These accelerate brand guidelines authoring downstream.

## Asset versioning protocol

When the brand evolves (refresh, sub-brand addition, error correction), version control matters:

- Master files versioned (v1.0, v1.1, v2.0, etc.)
- Changelog documenting every version (what changed, why, when)
- Previous versions retained (audit trail, rollback option)
- Distribution channels updated systematically (brand center, partner toolkits, etc.)

Even at initial brand-visual output, version assets explicitly as v1.0 to establish the protocol.

## Production partner brief (per asset category)

For each major asset category, a production partner brief (templated):

```markdown
# Production Brief — [Asset Category]

## Asset
[Files included]

## Specifications
[Technical specs]

## Production method
[Recommended production approach]

## Materials
[Substrate, ink, finishing]

## Quality control
[Acceptance criteria]

## Delivery
[Timeline, format, quantity]
```

This makes the brand-visual output ready for direct vendor handoff.

## Anti-patterns

| Anti-pattern | Symptom | Remedy |
|---|---|---|
| Single-format delivery | Logo delivered only as PNG | Multi-format package (SVG, EPS, PNG sizes, PDF) |
| No license documentation | Fonts shipped without license terms | Mandatory license documentation |
| Naming chaos | Files named "Logo_Final_v3_REAL_FINAL.psd" | Conventional naming from Day 1 |
| Design tokens absent | Identity ships without machine-readable tokens | Generate tokens for system deployment |
| Variant confusion | Multiple variants exist; no manifest documents them | Variant manifest mandatory |
| Stale photography rights | Photography deployed without license tracking | Photography rights database |
| Phase 5 surprise | Brand guidelines authoring discovers asset gaps | Brand-visual anticipates Phase 5 from outset |
