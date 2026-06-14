# brand-maker-ecosystem — Handoff Schema

This document defines the canonical schema for the enrichment artifact produced by `brand-maker-ecosystem` for `brand-maker` consumption.

## enrichment-schema

```yaml
# brand-maker-ecosystem enrichment artifact
# Consumed by brand-maker during its Strategic Decoding phase

enrichment_version: "1.0"
generated_at: <ISO 8601 timestamp>
source_skill: brand-maker-ecosystem
target_skill: brand-maker

# --- Upstream context summary -------------------------------------------------
upstream_context:
  brand_platform_present: <true|false>
  brand_story_present: <true|false>
  archetype: <Jung archetype assigned in brand-platform>
  positioning_essence: <distilled positioning core, 1 sentence>
  voice_register: <voice register from brand-platform>

# --- SB7 brief layer (when brand-story handoff present) -----------------------
sb7_naming_bias:
  semantic_territory: <derived from Character>
  oppositional_stance: <derived from three-layer problem>
  authority_register: <sage|mentor|partner|catalyst>
  pronunciation_friction: <low|medium|high>
  gravity_calibration: <light|moderate|heavy>
  affect_target: <uplift|calm|awe|intimacy|conviction|delight>
  opposite_signal: <what the failure-state brand would sound like>

# --- Archetype-driven naming bias --------------------------------------------
archetype_bias:
  primary_archetype: <Sage|Jester|Ruler|Magician|Hero|Outlaw|Caregiver|Lover|Explorer|Creator|Innocent|Everyman>
  recommended_patterns:
    - <pattern 1 from personality-frameworks-extended.md>
    - <pattern 2>
  avoid_patterns:
    - <pattern 1>
    - <pattern 2>
  example_names_in_archetype:
    - <existing brand 1>
    - <existing brand 2>

# --- Sector taxonomy mapping --------------------------------------------------
sector_taxonomy:
  primary_sector: <one of 9 Wiedemann/Taschen sectors>
  convention_alignment: <align|depart|hybrid>
  if_depart_rationale: <why deliberately departing from convention>

# --- Luxury constraints (if luxury opt-in active) -----------------------------
luxury_constraints_active: <true|false>
luxury_constraints:
  tier: <super-luxury|luxury|affordable-luxury|avant-garde-luxury>
  founder_name_pattern_preferred: <true|false>
  heritage_signaling_required: <true|false>
  classical_form_preferred: <true|false>
  neologism_permitted: <false (always false in luxury)>
  acceptable_origin_languages: [<list>]

# --- Recommendations for brand-maker -----------------------------------------
recommendations:
  category_a_weighting: <descriptive|associative|founder|invented|metaphor> # +/-/neutral
  category_b_weighting: <same axes>
  category_c_weighting: <same axes>
  category_d_weighting: <same axes>
  category_e_weighting: <same axes>
  smile_m_priority_attribute: <S|M|I|L|E|M which to prioritize>
```

## handoff-schema (forward to downstream)

When this skill produces a forward-flowing handoff (for brand-visual, brand-touchpoint downstream awareness), the schema is:

```yaml
handoff_version: "1.0"
generated_at: <ISO 8601 timestamp>
source_skill: brand-maker-ecosystem
final_naming_decisions:
  selected_name: <name>
  pronunciation_guide: <phonetic>
  archetype_alignment_confirmed: <archetype>
  luxury_compliance: <true|false|N/A>
  sector_alignment: <align|depart|hybrid>
  reasoning_summary: <1-2 sentence rationale>

naming_implications_for_visual:
  recommended_voice: <verbal voice that the visual should match>
  typography_bias: <serif|sans|display|mixed>
  formality_register: <formal|conversational|informal>
  cultural_origin_signaling: <if name has cultural origin, document for visual>
```

---

## Reverse Content Audit Discipline (D11-rev-1)

Before finalizing the enrichment artifact, conduct a reverse content audit verifying that every claim in the output is grounded in either (a) the upstream skill handoff, (b) a canonical reference, or (c) the user's brief. No fabrication rule applies: every interpretive claim must be traceable to documented logic. The forward pass (all schema fields populated correctly) and reverse pass (every populated field has provenance) must both succeed.
