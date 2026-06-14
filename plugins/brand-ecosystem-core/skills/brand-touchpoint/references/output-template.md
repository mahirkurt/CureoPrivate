<!-- ============================================================
     CANONICAL HANDOFF SCHEMA REFERENCE
     This output template extends the canonical schema defined in
     /docs/CANONICAL_HANDOFF_SCHEMA.md (Brand Ecosystem v1.0).
     The canonical core fields (provenance, project, execution,
     downstream_hints, citation_trail, maintenance, reverse_content_audit)
     are mandatory. The output: block below extends the canonical schema
     with skill-specific fields.
     ============================================================ -->

# Output Template — brand-touchpoint v1.0

## Part A — Touchpoint Specifications Document (human-readable)

```markdown
# Brand Touchpoint Specifications — <Brand Name>
**Version**: 1.0 | **Date**: <ISO date>
**Upstream**: brand-visual v? + brand-platform v?

## Executive Summary
[1-paragraph overview: touchpoint set in scope, atmospheric throughline, priority order summary.]

## 1. Touchpoint Set Scope

### 1.1 In-Scope Categories
| Category | Reason in scope |
|---|---|

### 1.2 Out-of-Scope Categories
| Category | Reason excluded |
|---|---|

## 2. Atmospheric Intent

### 2.1 Atmospheric Descriptors
3-5 atmospheric descriptors drawn from brand-platform.

### 2.2 Atmospheric Throughline
[Paragraph describing how atmosphere expresses across touchpoint set.]

## 3. Per-Touchpoint Specifications

### 3.1 Stationery
[Business card, letterhead, envelope, compliments slip, email signature — full specifications per section in stationery-business-papers.md]

### 3.2 Signage & Wayfinding (if in scope)
[Per signage-environment.md]

### 3.3 Vehicle Livery (if in scope)
[Full specifications]

### 3.4 Packaging (if in scope)
[Per packaging-structural-graphic.md]

### 3.5 Retail / Hospitality Environment (if in scope)
[Per retail-environment.md]

### 3.6 Branded Office Environment
[Per retail-environment.md office section]

### 3.7 Trade Show Booth (if in scope)
[Full specifications]

### 3.8 Digital Touchpoints
[Per digital-touchpoints.md]

#### 3.8.1 Web Atmosphere
#### 3.8.2 Social Media Template Kit
#### 3.8.3 Presentation Deck System
#### 3.8.4 Email Atmosphere
#### 3.8.5 Mobile App (if applicable)

### 3.9 Uniform / Dress Code (if in scope)
[Full specifications]

### 3.10 Ephemera & Merchandise
[Full specifications]

## 4. Touchpoint Priority Order

| Rank | Touchpoint | Rationale | Investment level |
|---|---|---|---|
| 1 | <tp> | <why> | <high/medium/light> |

## 5. Atmospheric Coherence Check

| Check | Status | Notes |
|---|---|---|
| Visual consistency | ✓/✗ | |
| Material consistency | ✓/✗ | |
| Verbal consistency | ✓/✗ | |
| Sensory consistency | ✓/✗ | |
| Emotional consistency | ✓/✗ | |

**Overall coherence**: PASS / FAIL  
**If FAIL**: [Remediation notes]

## 6. Production Partner Briefs

Per touchpoint, ready-to-send brief:

### 6.1 Stationery Production Brief
### 6.2 Signage Production Brief
### 6.3 Packaging Production Brief
### 6.4 Vehicle Livery Production Brief
### 6.5 Environmental Design Brief
### 6.6 Digital Asset Production Brief
### 6.7 Uniform Production Brief

## 7. Governance Assignments

| Touchpoint | Owner role | Approval workflow |
|---|---|---|

## 8. Production Sequencing

[Recommended order of production execution; not all touchpoints must be produced before launch — phasing acceptable]

## Appendix A — Quality Gates Audit
## Appendix B — Bibliography
```

## Part B — Machine-Readable Handoff Schema

```yaml
ecosystem_version: "1.0"
producer_skill: brand-touchpoint
producer_version: "1.0"
timestamp: <ISO 8601>
brief_id: <string>
upstream_checksum: <sha256 of brand-visual handoff>

artifact_payload:
  touchpoint_categories_in_scope: [<string>, ...]
  atmospheric_descriptors: [<string>, ...]
  
  touchpoints:
    stationery:
      business_card: <spec object>
      letterhead: <spec object>
      envelope: <spec object>
      email_signature: <spec object>
      compliments_slip: <spec object | null>
      presentation_folder: <spec object | null>
    signage:
      primary_signage: <spec object | n/a>
      wayfinding: <spec object | n/a>
      vehicle_livery: <spec object | n/a>
    packaging:
      structural: <spec object | n/a>
      graphic: <spec object | n/a>
    environmental:
      retail_interior: <spec object | n/a>
      branded_environment_office: <spec object>
      trade_show_booth: <spec object | n/a>
      pop_up_temporary: <spec object | n/a>
    digital:
      web_atmosphere: <spec object>
      social_media_template_kit: <spec object>
      presentation_deck_system: <spec object>
      email_atmosphere: <spec object>
      mobile_app: <spec object | n/a>
    human:
      uniform_dress_code: <spec object | n/a>
    ephemera:
      merchandise: <spec object>

  touchpoint_priority_order:
    - rank: 1
      touchpoint: <string>
      rationale: <string>
      investment_level: high|medium|light

  atmospheric_coherence_check:
    visual: pass|fail
    material: pass|fail
    verbal: pass|fail
    sensory: pass|fail
    emotional: pass|fail
    overall: pass|fail
    remediation_notes: <string|null>

  production_partner_briefs:
    - touchpoint: <string>
      brief_summary: <string>
      file_references: [...]

  governance_assignments:
    - touchpoint: <string>
      owner_role: <string>
      approval_workflow: <string>

  production_sequencing:
    - phase: 1
      touchpoints: [...]
      timeline: <string>

human_deliverable_path: ./brand-touchpoint-output.md
quality_gates_passed: [...]
quality_gates_failed: [...]

downstream_recommendations:
  next_skill: brand-launch
  reasoning: "Touchpoint specifications complete; ready for production planning + launch orchestration"
```

## Part C — Validation Rules

1. All touchpoints declared in_scope must have non-null specifications.
2. `atmospheric_coherence_check.overall` must be `pass` to proceed downstream.
3. Each touchpoint specification must include production_partner_brief.
4. Priority order must rank every in-scope touchpoint.
5. Governance assignments required for every touchpoint.

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
