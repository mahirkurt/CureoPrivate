---
description: Run the Brand Ecosystem build pipeline end to end — audit (optional) → platform → story → naming → visual identity → touchpoints → launch — then hand off to the brand-voice plugin for the voice layer.
argument-hint: [brand/venture brief, e.g. "Hemantix — new hematology diagnostics brand, B2B, Türkiye + EMEA, rebrand of an existing line"]
---

You are running the **Brand Ecosystem build pipeline** for: $ARGUMENTS

Execute the ecosystem skills in canonical composition order, passing each
skill's handoff to the next. Address the user in formal Turkish ("siz")
throughout, independent of the register the brand later adopts for its own
audience. Do not skip a stage's quality gates; where a stage lacks input, raise
an open question with a recommendation rather than inventing signal.

## Order of operations

1. **brand-audit** *(only for a rebrand / refresh / M&A / post-launch case)* —
   asset inventory, competitive + IP audit, gap analysis, opportunity statement.
   Skip for a true greenfield brand and start at step 2.
2. **brand-platform** — the strategic bedrock: vision, mission, values,
   personality (Jung + Aaker), persona (4Cs + Maslow), Ries-Trout positioning,
   promise, voice principles. Every downstream stage consumes its handoff.
3. **brand-story** — the SB7 BrandScript and three-layer problem analysis,
   reading the platform handoff.
4. **brand-maker** *(+ brand-maker-ecosystem)* — verbal identity / naming, with
   the ecosystem companion supplying platform- and story-aware naming bias and
   sector/luxury constraints.
5. **brand-visual** *(+ brand-visual-ecosystem)* — the visual identity system,
   with the companion supplying touchpoint-atmosphere, corporate-signature and
   sensory layers. Use **figma-forge** when the locked identity should be
   operationalised into a Figma library (variables, styles, components,
   Code Connect).
6. **brand-touchpoint** — per-surface specifications from the locked visual
   identity (stationery, signage, packaging, retail, digital, ephemera).
7. **brand-launch** — internal-first rollout, brand-champion program, brand
   center spec, guidelines anatomy, trademark/domain/handle checklist, KPI
   dashboard. The terminal stage.

## Voice layer (separate plugin)

The **voice & tone identity** is owned by the `brand-voice` plugin, not this
one. At the platform stage, hand the platform (and story) off to
`brand-voice:guideline-generation` to produce the operational voice guideline —
including the mandatory Turkish sen/siz/biz register decision — and use
`brand-voice:brand-voice-enforcement` for copy on launch surfaces. If
`brand-voice` is not installed, note the gap and continue.

## Finish

Offer to package any deliverable via `carbon-html-report` (A4 brand book),
`carbon-pptx` (deck) or `docx`; this ecosystem defers all HTML/print/deck
rendering to those skills. For any regulated-sector brand (pharma, health,
finance, legal), route promotional-claim review to `promo-censor` /
`cureolex`.
