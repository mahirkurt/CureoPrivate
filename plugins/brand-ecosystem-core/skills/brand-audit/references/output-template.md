<!-- ============================================================
     CANONICAL HANDOFF SCHEMA REFERENCE
     This output template extends the canonical schema defined in
     /docs/CANONICAL_HANDOFF_SCHEMA.md (Brand Ecosystem v1.0).
     The canonical core fields (provenance, project, execution,
     downstream_hints, citation_trail, maintenance, reverse_content_audit)
     are mandatory. The output: block below extends the canonical schema
     with skill-specific fields.
     ============================================================ -->

# Output Template — brand-audit v1.0

## Part A — Findings Report (human-readable)

```markdown
# Brand Audit — Findings Report — <Brand Name>
**Version**: 1.0 | **Date**: <ISO date> | **Brief**: <brief-id>
**Audit scope**: [asset_inventory, competitive, ip, process]

## Executive Summary
[1-2 paragraph synthesis. The opportunity statement appears here in its decision-ready form.]

## 1. Brand Asset Inventory

### 1.1 Visual Assets
[Tabular: Asset | Description | Condition | Keep/Evolve/Retire | Rationale]

### 1.2 Verbal Assets
[Tabular]

### 1.3 Strategic Assets
[Tabular]

### 1.4 Operational Assets
[Tabular]

### 1.5 Inventory Summary
| Category | Keep | Evolve | Retire |
|---|---|---|---|
| Visual | <n> | <n> | <n> |
| Verbal | <n> | <n> | <n> |
| Strategic | <n> | <n> | <n> |
| Operational | <n> | <n> | <n> |

### 1.6 Migration Considerations
[Which Retire decisions need sequenced migration]

## 2. Competitive Audit

### 2.1 Competitive Set
| Competitor | Type | Direct/Indirect/Aspirational |
|---|---|---|

### 2.2 Per-Competitor Profiles
[For each competitor: positioning claim, archetype, visual character, voice, persona, touchpoints, recent shifts]

### 2.3 Positioning Matrix
[Text-described 2x2 with competitor placements]

### 2.4 White Space Analysis
- Positioning white space: [...]
- Visual white space: [...]
- Voice white space: [...]
- Audience white space: [...]
- Touchpoint white space: [...]

## 3. IP & Trademark Audit

### 3.1 Trademark Status
| Mark | Jurisdiction | Class(es) | Status | Renewal due |
|---|---|---|---|---|

### 3.2 Domain Portfolio
[Primary + defensive registrations]

### 3.3 Social Handle Inventory
[Platforms + handles]

### 3.4 Risks and Gaps
- Jurisdiction gaps
- Class gaps
- Pending conflicts
- Renewal urgency

## 4. Process Audit (if in scope)

### 4.1 Governance Model
Current: Cop / Hybrid / Concierge
Recommended: Cop / Hybrid / Concierge

### 4.2 Brand Guidelines
[Existence, currency, adoption, gaps]

### 4.3 Brand Center / Asset Library
[Existence, platform, accessibility]

### 4.4 Champion Network
[Existence, training, distribution]

### 4.5 Operational Gaps
[List]

## 5. Gap Analysis

### 5.1 Strategic Gaps
### 5.2 Visual Gaps
### 5.3 Verbal Gaps
### 5.4 Operational Gaps
### 5.5 Legal Gaps

## 6. Opportunity Statement
[Single paragraph stating the strategic opportunity the audit reveals. This becomes the brief for brand-platform.]

## 7. Recommendations
- For brand-platform: [specific recommendations]
- For brand-visual: [specific recommendations]
- For brand-launch: [specific recommendations]

## Appendix A — Quality Gates
[Status table]

## Appendix B — Bibliography
[Cited canonical sources]
```

## Part B — Machine-Readable Handoff

```yaml
ecosystem_version: "1.0"
producer_skill: brand-audit
producer_version: "1.0"
timestamp: <ISO 8601>
brief_id: <string>
language_primary: en|tr

artifact_payload:
  audit_scope: [<string>, ...]
  
  asset_inventory:
    visual:
      - asset: <string>
        description: <string>
        current_condition: <string>
        assessment: keep|evolve|retire
        rationale: <string>
    verbal: [...]
    strategic: [...]
    operational: [...]
    summary:
      keep_count: <int>
      evolve_count: <int>
      retire_count: <int>

  competitive_landscape:
    direct_competitors:
      - name: <string>
        positioning_claim: <string>
        archetype: <string>
        visual_character: <object>
        voice: <object>
        persona_served: <string>
        touchpoint_footprint: [<string>, ...]
        recent_narrative_shifts: <string>
    indirect_competitors: [...]
    aspirational_references: [...]
    positioning_matrix:
      x_axis: <string>
      y_axis: <string>
      placements: [...]
    positioning_gaps: [<string>, ...]
    visual_white_space: [<string>, ...]
    voice_white_space: [<string>, ...]
    audience_white_space: [<string>, ...]
    touchpoint_white_space: [<string>, ...]

  ip_status:
    trademarks_registered:
      - mark: <string>
        jurisdiction: <string>
        classes: [<int>, ...]
        status: active|pending|lapsed
        renewal_due: <ISO date>
    trademark_conflicts: [<string>, ...]
    jurisdiction_gaps: [<string>, ...]
    class_gaps: [<string>, ...]
    domain_portfolio: [<string>, ...]
    social_handles: [<object>, ...]

  process_diagnosis:
    governance_model_current: cop|hybrid|concierge
    governance_model_recommended: cop|hybrid|concierge
    guidelines_strength: weak|medium|strong
    operational_gaps: [<string>, ...]

  gap_analysis:
    strategic_gaps: [<string>, ...]
    visual_gaps: [<string>, ...]
    verbal_gaps: [<string>, ...]
    operational_gaps: [<string>, ...]
    legal_gaps: [<string>, ...]

  opportunity_statement: <paragraph>

  downstream_recommendations:
    for_brand_platform: [<string>, ...]
    for_brand_visual: [<string>, ...]
    for_brand_launch: [<string>, ...]

human_deliverable_path: ./brand-audit-output.md
quality_gates_passed: [...]
quality_gates_failed: [...]
remediation_required: <boolean>
```

## Part C — Bibliography for Audit Scope

Same as `bibliography.md`. Key citations:
- `[Wheeler 6th, Phase 1]` — overall audit framework
- `[Wheeler 5th, Brand Audit Section]` — extended audit detail
- `[Johnson, Step 1]` — investigate phase
- `[Geyrhalter, Step 2]` — competitive context
- `[Foroudi et al., Ch. 8]` — corporate brand audit

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
