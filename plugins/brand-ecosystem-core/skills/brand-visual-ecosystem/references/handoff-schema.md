# brand-visual-ecosystem — Handoff Schema

This document defines the canonical schema for both (a) the enrichment artifact this skill provides to `brand-visual`, and (b) the forward-flowing handoff this skill produces for `brand-touchpoint` downstream.

## enrichment-schema

```yaml
# brand-visual-ecosystem enrichment artifact
# Consumed by brand-visual during its 4-route exploration phase

enrichment_version: "1.0"
generated_at: <ISO 8601 timestamp>
source_skill: brand-visual-ecosystem
target_skill: brand-visual

# --- Upstream context summary ------------------------------------------------
upstream_context:
  brand_platform_present: <true|false>
  brand_audit_present: <true|false>
  brand_story_present: <true|false>
  brand_maker_present: <true|false>
  archetype: <Jung archetype>
  positioning_essence: <distilled positioning>
  voice_register: <voice register>

# --- Competitive visual audit (when brand-audit upstream) --------------------
competitive_visual_audit:
  primary_competitors_visual:
    - name: <competitor>
      color_anchor: <dominant color signal>
      form_language: <geometric|organic|mixed>
      typography_classification: <serif|sans|display>
  white_space_opportunities:
    color_white_space:
      - <available color territory>
    form_white_space:
      - <available form language territory>
    typography_white_space:
      - <available typographic territory>

# --- Touchpoint anticipation (when brand-touchpoint downstream) --------------
touchpoint_anticipation:
  scope:
    - stationery: <required|optional|out_of_scope>
    - signage: <required|optional|out_of_scope>
    - packaging: <required|optional|out_of_scope>
    - retail_interior: <required|optional|out_of_scope>
    - vehicle_livery: <required|optional|out_of_scope>
    - digital: <required|optional|out_of_scope>
    - uniforms: <required|optional|out_of_scope>
  material_atlas_prefigured:
    paper_stock: <description>
    signage_substrate: <description>
    packaging_materials: <description>
    fabric_weights: <description>
  motion_language:
    animation_cadence: <quick|moderate|slow>
    transition_curve: <linear|ease-in|ease-out|elastic>
    kinetic_behavior: <description>
  scale_specimens:
    favicon_16px_legibility: <requirement>
    billboard_30m_impact: <requirement>
  sensory_layer:
    acoustic_profile: <description if multi-sensory active>
    scent_stance: <ambient|signature|none>
    tactile_finish: <description>

# --- Corporate signature (when corporate B2B opt-in active) ------------------
corporate_signature_active: <true|false>
corporate_signature:
  signature_hierarchy:
    primary: <description>
    secondary: <description>
    with_tagline: <description>
    with_descriptor: <description>
  brand_architecture: <monolithic|endorsed|pluralistic>
  identity_mix_coverage:
    visual_identity: <covered>
    corporate_communications: <covered>
    behavior: <documented>
    naming_system: <covered>

# --- Multi-sensory atmosphere (when multi-sensory opt-in active) -------------
multi_sensory_active: <true|false>
multi_sensory:
  sonic_logo_brief:
    mnemonic_structure: <description>
    timbre_palette: <description>
    duration: <seconds>
  scent_strategy:
    stance: <ambient|signature|associative>
    olfactory_notes: <description>
  music_palette:
    era: <description>
    instrumentation: <description>
    tempo_range: <BPM>
    mood_gradient: <description>
  voice_character:
    persona: <description>
    register: <formal|conversational>
    tone: <warm|neutral|authoritative>

# --- Phase 5 asset management preparation ------------------------------------
asset_management:
  file_naming_convention:
    pattern: "<brand-prefix>-<asset-type>-<variant>-<version>"
    example: "brandname-logo-primary-v1.0.svg"
  design_tokens:
    color_tokens: <count and structure>
    typography_tokens: <count and structure>
    spacing_tokens: <count and structure>
    motion_tokens: <count and structure>
  brand_center_asset_prep:
    formats: ["SVG", "PNG (multi-resolution)", "EPS", "PDF"]
    resolutions: ["16px favicon", "256px app icon", "1024px hero", "vector master"]
  asset_retirement_policy:
    deprecation_path: <description>
```

## handoff-schema (forward to brand-touchpoint downstream)

```yaml
handoff_version: "1.0"
generated_at: <ISO 8601 timestamp>
source_skill: brand-visual-ecosystem
target_downstream: brand-touchpoint

visual_identity_locked:
  logo_primary: <reference or filename>
  logo_variants: <list>
  color_palette:
    primary: <hex>
    secondary: <hex>
    accent: <hex>
    neutrals: <list of hex>
  typography:
    primary_font: <font family>
    secondary_font: <font family>
    weights_in_use: <list>
  iconography_style: <description>
  imagery_style: <description>

touchpoint_constraint_kit:
  material_atlas: <full atlas from enrichment>
  motion_language: <full motion spec>
  scale_specimens: <full scale spec>
  sensory_layer: <full sensory spec if active>
  atmospheric_descriptors:
    warmth_axis: <warm|cool|neutral>
    density_axis: <dense|open>
    gravity_axis: <heavy|light>
    velocity_axis: <fast|slow>

design_tokens:
  color_tokens: <complete token set>
  typography_tokens: <complete token set>
  spacing_tokens: <complete token set>

phase5_asset_governance:
  file_naming_convention: <full convention>
  asset_retirement_policy: <full policy>
  brand_center_preparation: <prep state>

opt_in_modules_inherited:
  luxury_active: <true|false>
  corporate_b2b_active: <true|false>
  multi_sensory_active: <true|false>
```

---

## Reverse Content Audit Discipline (D11-rev-1)

Before finalizing the enrichment artifact, conduct a reverse content audit verifying that every claim in the output is grounded in either (a) the upstream skill handoff, (b) a canonical reference, or (c) the user's brief. No fabrication rule applies: every interpretive claim must be traceable to documented logic. The forward pass (all schema fields populated correctly) and reverse pass (every populated field has provenance) must both succeed.
