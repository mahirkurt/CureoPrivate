<!-- ============================================================
     CANONICAL HANDOFF SCHEMA REFERENCE
     This output template extends the canonical schema defined in
     /docs/CANONICAL_HANDOFF_SCHEMA.md (Brand Ecosystem v1.0).
     The canonical core fields (provenance, project, execution,
     downstream_hints, citation_trail, maintenance, reverse_content_audit)
     are mandatory. The output: block below extends the canonical schema
     with skill-specific fields.
     ============================================================ -->

# Output Template — brand-platform v1.0

This reference defines both the **human-readable deliverable** structure and the **machine-readable handoff** schema. Loaded mandatorily at Step 0.

## Part A — Human-Readable Deliverable

Produced as a markdown document, 8–15 pages (≈3,000–6,500 words). Structure:

```markdown
# Brand Platform — <Brand Name>
**Version**: 1.0 | **Date**: <ISO date> | **Brief**: <brief-id>

## Executive Summary
[1 paragraph synthesizing the eight elements. This is the only piece some stakeholders will read.]

## 1. Vision
[Single sentence in the brief's primary language.]

**EN**: <vision in EN>
**TR**: <vision in TR>

**Rationale** (paragraph): [Why this vision, why now, what it commits the brand to over a 10-year horizon.]

## 2. Mission
[Single sentence in the brief's primary language.]

**EN**: <mission in EN>
**TR**: <mission in TR>

**Rationale** (paragraph): [Verb + beneficiary + mechanism breakdown.]

## 3. Core Values
[3–5 values, each presented as: <Value Name> — <One-paragraph description> — <Three operational behaviors that express the value>]

### 3.1 <Value 1 Name>
[Description + operational behaviors]
[Opposite test: <opposite> is plausibly held by <type of brand>.]

### 3.2 <Value 2 Name>
…

## 4. Brand Personality

### 4.1 Jung Archetype
**Primary**: <archetype>
**Secondary** (if applicable): <archetype>

[Paragraph explaining the archetype choice with reference to the persona and competitive context.]

### 4.2 Aaker 5-Dimension Profile
| Dimension | Score (0–10) | Rationale |
|---|---|---|
| Sincerity | <0-10> | <one sentence> |
| Excitement | <0-10> | <one sentence> |
| Competence | <0-10> | <one sentence> |
| Sophistication | <0-10> | <one sentence> |
| Ruggedness | <0-10> | <one sentence> |

### 4.3 Voice Traits
1. <Trait 1>: <one-sentence description>
2. <Trait 2>: <one-sentence description>
3. <Trait 3>: <one-sentence description>
(optional 4 and 5)

## 5. Target Persona

### 5.1 Demographic
| Attribute | Value |
|---|---|
| Age range | <range> |
| Gender mix | <description if salient> |
| Income band | <range or descriptor> |
| Geography | <region/density> |
| Education | <level> |
| Occupation cluster | <description> |
| Household composition | <if salient> |
| Major life stage | <if salient> |

### 5.2 Psychographic Profile
**4Cs Segment**: <Resigned/Struggler/Mainstreamer/Aspirer/Succeeder/Explorer/Reformer>

[Paragraph 150–250 words: values, attitudes, daily life, media habits, brand affinities in and outside the category, unmet needs.]

### 5.3 Maslow Layer
**Primary level**: <layer name>

[One paragraph: why this brand operates at this Maslow level and what that implies for emotional register.]

## 6. Positioning Statement

### 6.1 Six-Clause Formula (EN)
For <target customer>,
who <unmet need>,
<Brand> is the <category>
that <benefit>,
unlike <named competitor>,
because <reason to believe>.

### 6.2 Six-Clause Formula (TR)
<Hedef müşteri> için,
ki <karşılanmamış ihtiyaç>,
<Marka>, <kategori> olarak konumlanır,
çünkü <fayda>,
<Adı verilen rakip> ile karşılaştırıldığında,
zira <inanma nedeni>.

### 6.3 Clause-by-Clause Rationale
| Clause | Strategic intent | Risk if changed |
|---|---|---|
| Target | <intent> | <risk> |
| Need | <intent> | <risk> |
| Category | <intent> | <risk> |
| Benefit | <intent> | <risk> |
| Competitor | <intent> | <risk> |
| Reason | <intent> | <risk> |

## 7. Brand Promise

**EN**: When you choose <Brand>, you experience <transformation>.
**TR**: <Marka>'yı seçtiğinizde, <dönüşüm> deneyimi yaşarsınız.

**Operational deliverability**: [Paragraph confirming the brand can deliver this on every primary touchpoint.]

## 8. Brand Voice Principles

### 8.1 Principle 1: <Principle name>
- **Does**: <positive directive>
- **Never**: <negative directive>
- **Yes example**: "<short example>"
- **No example**: "<short example>"

### 8.2 Principle 2: <Principle name>
…

(3–5 principles total)

## 9. Competitive Landscape Summary

[Single paragraph synthesizing competitive context.]

| Competitor | Type | Position | White space they leave |
|---|---|---|---|
| <Comp 1> | Direct | <their position> | <what they don't claim> |
| <Comp 2> | Direct | <their position> | <what they don't claim> |
| <Comp 3> | Direct | <their position> | <what they don't claim> |
| <Comp 4> | Indirect | <their position> | <what they don't claim> |
| <Comp 5> | Indirect | <their position> | <what they don't claim> |

**Strategic white space**: [One paragraph describing the unoccupied position this brand will claim.]

## 10. Sector Opt-In Module Outputs (if applicable)

[Luxury module, corporate B2B module, etc. — only present if triggered.]

## Appendix A — SAS Test Results (Geyrhalter)

- **Soul**: ✓/✗ — [evidence]
- **Attractive**: ✓/✗ — [evidence]
- **Smart**: ✓/✗ — [evidence]

## Appendix B — Quality Gates Audit

| Gate | Status | Notes |
|---|---|---|
| G1 — All 8 elements present | ✓/✗ | |
| G2 — Canonical citations | ✓/✗ | |
| G3 — Bilingual rationale | ✓/✗ | |
| G4 — Robin-to-Batman test | ✓/✗ | |
| G5 — SAS test | ✓/✗ | |
| G6 — Opposite test on values | ✓/✗ | |

## Appendix C — Bibliography

[Cited canonical sources with edition and chapter references.]
```

## Part B — Machine-Readable Handoff Schema

The `handoff.yaml` file produced alongside the deliverable:

```yaml
ecosystem_version: "1.0"
producer_skill: brand-platform
producer_version: "1.0"
timestamp: <ISO 8601>
brief_id: <string>
upstream_checksum: <sha256 of brand-audit handoff if present, else null>
language_primary: en|tr
sector_signals: [<string>, ...]
opt_in_modules_active: [<string>, ...]

artifact_payload:
  vision:
    en: <string>
    tr: <string>
  mission:
    en: <string>
    tr: <string>
  core_values:
    - name: <string>
      description: <string>
      opposite_test_pass: true|false
      operational_behaviors: [<string>, <string>, <string>]
  brand_personality:
    jung_primary: <string>
    jung_secondary: <string|null>
    aaker_5d:
      sincerity: <0-10>
      excitement: <0-10>
      competence: <0-10>
      sophistication: <0-10>
      ruggedness: <0-10>
    voice_traits: [<string>, <string>, <string>]
  target_persona:
    demographic:
      age_range: <string>
      gender_mix: <string>
      income_band: <string>
      geography: <string>
      education: <string>
      occupation_cluster: <string>
      household_composition: <string>
      life_stage: <string>
    psychographic_segment: <string>  # 4Cs label
    psychographic_summary: <string>  # 150-250 word paragraph
    maslow_layer: <string>
  positioning_statement:
    en:
      for: <string>
      who: <string>
      is: <string>
      that: <string>
      unlike: <string>
      because: <string>
    tr:
      for: <string>
      who: <string>
      is: <string>
      that: <string>
      unlike: <string>
      because: <string>
  brand_promise:
    en: <string>
    tr: <string>
  competitive_landscape:
    direct_competitors:
      - name: <string>
        position: <string>
        white_space_left: <string>
    indirect_competitors:
      - name: <string>
        position: <string>
        white_space_left: <string>
    strategic_white_space: <string>
  brand_voice_principles:
    - name: <string>
      does: <string>
      never: <string>
      yes_example: <string>
      no_example: <string>

  opt_in_module_outputs:
    luxury: <object if active>
    corporate_b2b: <object if active>

human_deliverable_path: ./brand-platform-output.md

quality_gates_passed: [<string>, ...]
quality_gates_failed: [<string>, ...]
remediation_required: <boolean>
remediation_notes: <string|null>

downstream_recommendations:
  next_skill: brand-story
  reasoning: <string>
  skip_recommendations: [<string>, ...]  # if any downstream skills can be safely skipped
```

## Part C — Validation Rules

Before writing the handoff:

1. Every required field must be non-null.
2. All `_test_pass` booleans must be `true`; if any are `false`, set `remediation_required: true` and document in `remediation_notes`.
3. The Aaker 5-D scores must sum to a sensible profile (a brand scoring 0 on every dimension or 10 on every dimension is suspect — flag for review).
4. The positioning statement EN and TR must be strategically equivalent; if literal translation produces drift, prefer adaptation over literal translation.
5. The competitive landscape must name at least 3 direct + 2 indirect competitors.

## Part D — Downstream Skill Recommendations

In the handoff's `downstream_recommendations` block:

- **Standard recommendation**: `brand-story` next.
- **Skip recommendation for B2B technical infrastructure brands**: brand-story may be lightweight; flag.
- **Skip recommendation for product-naming-only briefs**: jump direct to brand-maker.
- **Skip recommendation for visual-identity-only briefs**: jump direct to brand-visual.

These recommendations help orchestrators (smp-orchestrator, or human users running the pipeline) optimize the chain for the specific brief type.

## Reverse Content Audit Discipline (D11-rev-1)

Before finalizing the output document, conduct a **reverse content audit** — a provenance pass in the HTML/markdown → source direction. The goal is to verify that **every claim in the rendered output originates in the upstream source materials** (brief, handoffs, canonical references) and no fabrication has crept in.

### Reverse pass checklist

For every substantive claim in the document:
- [ ] Is the claim grounded in either: (a) the user's brief, (b) an upstream handoff artifact, (c) a canonical reference cited in this skill's bibliography, or (d) the user's explicit input?
- [ ] If the claim is interpretive (e.g., "this aligns with X archetype"), is the interpretive logic documented in the skill's references?
- [ ] If a parenthetical gloss or abbreviation expansion is introduced, did it exist in the source or did the skill invent it?

**No fabrication rule**: Any claim that cannot be traced through one of the four provenance paths must be either removed or explicitly marked as "interpretive judgment by the skill" with documented reasoning.

### Bidirectional content integrity

- **Forward pass** (source → output): every required element is present (covered by quality gates G1-G9)
- **Reverse pass** (output → source): every output claim has provenance (this section)

Both passes must succeed before the document is considered final. If the reverse pass surfaces a claim without provenance, the output is blocked and the claim must be either grounded or removed.
