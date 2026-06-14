<!-- ============================================================
     CANONICAL HANDOFF SCHEMA REFERENCE
     This output template extends the canonical schema defined in
     /docs/CANONICAL_HANDOFF_SCHEMA.md (Brand Ecosystem v1.0).
     The canonical core fields (provenance, project, execution,
     downstream_hints, citation_trail, maintenance, reverse_content_audit)
     are mandatory. The output: block below extends the canonical schema
     with skill-specific fields.
     ============================================================ -->

# Output Template — brand-story v1.0

## Part A — Human-Readable Deliverable

### Structure (markdown, 3-6 pages)

```markdown
# BrandScript — <Brand Name>
**Version**: 1.0 | **Date**: <ISO date> | **Brief**: <brief-id>
**Upstream**: brand-platform v1.0

## The Single-Page BrandScript (EN)

THE CUSTOMER who is [persona descriptor], wants [concrete want].

THE PROBLEM is [external problem]. This makes the customer feel [internal problem]. We believe [philosophical problem].

OUR BRAND has [authority evidence] and understands this struggle because [empathy evidence].

WE OFFER A PLAN: [Step 1]. [Step 2]. [Step 3].

YOU CAN [direct CTA] or [transitional CTA].

WITHOUT OUR BRAND, you risk: [failure stake 1], [failure stake 2], [failure stake 3].

WITH OUR BRAND, you experience: [success state].

## The Single-Page BrandScript (TR)

MÜŞTERİ [persona tanımı], [somut istek] arzular.

PROBLEM [dışsal problem]. Bu, müşteriye [içsel duygu] hissettirir. Biz [felsefi problem] olduğuna inanırız.

MARKAMIZ [yetki kanıtı] ve bu mücadeleyi anlar çünkü [empati kanıtı].

BİR PLAN SUNUYORUZ: [Adım 1]. [Adım 2]. [Adım 3].

[Doğrudan CTA] yapabilir veya [Geçiş CTA] tercih edebilirsiniz.

MARKAMIZ OLMADAN [risk 1], [risk 2], [risk 3] ile karşılaşırsınız.

MARKAMIZLA [başarı durumu] deneyimini yaşarsınız.

## 1. Three-Layer Problem Analysis

### 1.1 External Problem
[Paragraph]

### 1.2 Internal Problem
[Paragraph]

### 1.3 Philosophical Problem
[Paragraph]

### 1.4 Coherence Check
[Bottom-up + top-down trace confirming the three layers are causally linked.]

## 2. The Guide: Empathy + Authority

### 2.1 Empathy Statement
[Paragraph demonstrating brand's understanding of customer struggle from inside.]

### 2.2 Authority Statement
[Paragraph demonstrating brand's competence to help — credentials, methodology, evidence.]

## 3. The Plan (3 Steps)

| # | Step | Customer action |
|---|---|---|
| 1 | <step name> | <what the customer does> |
| 2 | <step name> | <what the customer does> |
| 3 | <step name> | <what the customer does> |

## 4. Calls to Action

| Type | CTA | When used |
|---|---|---|
| Direct | <phrase> | Top of every page, end of every email |
| Transitional | <phrase> | Secondary placement, content nurture |

## 5. Failure Stakes

What the customer risks by not engaging:
- [Stake 1]
- [Stake 2]
- [Stake 3]
- [Stake 4 if applicable]

## 6. Success Transformation

[Paragraph 100-150 words describing the customer's life after engaging the brand.]

## 7. Villains & Antagonists

### 7.1 Personified Problem
[Who or what embodies the obstacle the hero faces.]

### 7.2 Competing Alternatives
[The other paths the hero might wrongly choose.]

### 7.3 Industry/Cultural Norms Challenged
[The broader pattern the brand opposes.]

## 8. Robin-to-Batman Compliance Test

| Question | Result |
|---|---|
| Does the customer appear as hero or does the brand? | Customer / Brand |
| Is the brand a sidekick or does it cast itself as Batman? | Sidekick / Batman |
| Who does a stranger identify with reading this BrandScript? | Customer / Brand |

**Result**: PASS / FAIL
**If FAIL**: [Remediation notes]

## 9. IMC Reimagined Diffusion Plan

### 9.1 Internal Phase

**Timeline**: <weeks/months from BrandScript approval>

**Leadership briefing**: [Paragraph specification]

**Employee evangelization**: [Paragraph specification]

**Champion identification criteria**:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

**Storyteller training brief**: [Paragraph]

**Internal-facing artifacts to produce**:
- [Artifact 1] — owner: [role]
- [Artifact 2] — owner: [role]
- [Artifact 3] — owner: [role]

### 9.2 External Phase

**Timeline**: <after internal saturation>

**Story sequencing — which SB7 element leads, which support**:
1. Lead: <element>
2. Support: <element>
3. Support: <element>

**Channel mix**:
| Channel | Role | % of effort |
|---|---|---|
| PR | <role> | <%> |
| Content | <role> | <%> |
| Social | <role> | <%> |
| Advertising | <role> | <%> |

**Story testing protocol**: [Paragraph describing how the brand will validate the story is landing]

## 10. Narrative Arc Milestones

| Month | Internal milestone | External milestone |
|---|---|---|
| 0 | BrandScript approved | — |
| 1 | Leadership briefed | — |
| 2 | Champions trained | — |
| 3 | Internal saturation | Soft external launch |
| 6 | First story-feedback loop | Full external launch |
| 12 | Story refinement | First anniversary moment |

## Appendix A — Quality Gates Audit

| Gate | Status |
|---|---|
| G1 Upstream platform present | ✓ |
| G2 All 7 SB7 elements | ✓ |
| G3 Three problem layers | ✓ |
| G4 Robin-to-Batman test | ✓ |
| G5 Empathy + Authority | ✓ |
| G6 Direct + Transitional CTA | ✓ |
| G7 Villain identified | ✓ |
| G8 IMC internal + external | ✓ |
| G9 Bilingual rationale | ✓ |

## Appendix B — Bibliography

[Cited canonical sources]
```

## Part B — Machine-Readable Handoff Schema

```yaml
ecosystem_version: "1.0"
producer_skill: brand-story
producer_version: "1.0"
timestamp: <ISO 8601>
brief_id: <string>
upstream_checksum: <sha256 of brand-platform handoff>
language_primary: en|tr
sector_signals: [<string>, ...]
opt_in_modules_active: [<string>, ...]

artifact_payload:
  brandscript:
    character:
      persona_descriptor: <string>
      concrete_want: <string>
      one_sentence_en: <string>
      one_sentence_tr: <string>
    has_a_problem:
      external:
        en: <string>
        tr: <string>
      internal:
        en: <string>
        tr: <string>
      philosophical:
        en: <string>
        tr: <string>
      coherence_check_pass: <boolean>
    meets_a_guide:
      empathy_statement:
        en: <string>
        tr: <string>
      authority_statement:
        en: <string>
        tr: <string>
    who_gives_them_a_plan:
      plan_type: process|agreement|combined
      steps:
        - name: <string>
          customer_action: <string>
    and_calls_them_to_action:
      direct_cta:
        en: <string>
        tr: <string>
      transitional_cta:
        en: <string>
        tr: <string>
    that_helps_them_avoid_failure:
      - en: <string>
        tr: <string>
    and_ends_in_success:
      en: <string>
      tr: <string>

  villains_antagonists:
    personified_problem: <string>
    competing_alternatives: [<string>, ...]
    industry_norms_challenged: [<string>, ...]

  robin_to_batman_test:
    result: pass|fail
    customer_as_hero_confirmed: <boolean>
    brand_as_guide_confirmed: <boolean>
    reader_identifies_with: customer|brand
    remediation_notes: <string|null>

  imc_diffusion_plan:
    internal_phase:
      timeline: <string>
      leadership_briefing_spec: <string>
      employee_evangelization_spec: <string>
      champion_criteria: [<string>, ...]
      storyteller_training_brief: <string>
      internal_artifacts:
        - name: <string>
          owner_role: <string>
    external_phase:
      timeline: <string>
      story_sequencing_lead: <SB7 element>
      story_sequencing_support: [<SB7 element>, ...]
      channel_mix:
        pr: <%>
        content: <%>
        social: <%>
        advertising: <%>
      story_testing_protocol: <string>

  narrative_arc_milestones:
    - month: <int>
      internal: <string|null>
      external: <string|null>

human_deliverable_path: ./brand-story-output.md
quality_gates_passed: [G1, G2, G3, G4, G5, G6, G7, G8, G9]
quality_gates_failed: []
remediation_required: false

downstream_recommendations:
  next_skill: brand-maker (if naming) | brand-visual (if naming done)
  reasoning: <string>
```

## Part C — Validation Rules

1. `robin_to_batman_test.result` MUST be `pass` to proceed downstream.
2. Both `direct_cta` and `transitional_cta` are required (cannot be null).
3. `has_a_problem` requires all three layers (external/internal/philosophical) populated in both EN and TR.
4. `meets_a_guide` requires both empathy AND authority populated.
5. `who_gives_them_a_plan.steps` must have exactly 3 entries.
6. `that_helps_them_avoid_failure` must have 3-4 entries.
7. `coherence_check_pass` MUST be true — meaning the three problem layers are causally linked.

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
