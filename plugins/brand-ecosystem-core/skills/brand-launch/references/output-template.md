<!-- ============================================================
     CANONICAL HANDOFF SCHEMA REFERENCE
     This output template extends the canonical schema defined in
     /docs/CANONICAL_HANDOFF_SCHEMA.md (Brand Ecosystem v1.0).
     The canonical core fields (provenance, project, execution,
     downstream_hints, citation_trail, maintenance, reverse_content_audit)
     are mandatory. The output: block below extends the canonical schema
     with skill-specific fields.
     ============================================================ -->

# Output Template — brand-launch v1.0

## Part A — Launch Plan Document (human-readable)

```markdown
# Brand Launch Plan — <Brand Name>
**Version**: 1.0 | **Date**: <ISO date>
**Upstream**: brand-platform + brand-touchpoint + brand-story + brand-maker + brand-visual + brand-audit

## Executive Summary
[1-paragraph: launch context, timeline summary, critical pre-launch items.]

## 1. Launch Context
**Context type**: Greenfield / Rebrand / Sub-brand / M&A integration / Refresh / Repositioning
**Rationale**: [1 paragraph explaining context determination]

## 2. Pre-Launch Foundation

### 2.1 Trademark Status
[Full checklist per trademark-domain-social-checklist.md]

### 2.2 Domain Status
[Full checklist]

### 2.3 Social Handle Status
[Full checklist]

### 2.4 Brand Asset Production Status
| Touchpoint category | Asset status |
|---|---|
| Stationery | Ready / In production / Specced |
| Signage | Ready / In production / Specced |
| Packaging | Ready / In production / Specced |
| Web | Ready / In production / Specced |
| Presentation deck | Ready / In production / Specced |
| Social templates | Ready / In production / Specced |

## 3. Internal-First Launch Plan

### 3.1 Internal Timeline
| Week | Milestone | Owner |
|---|---|---|
| -8 | Leadership briefing | <role> |
| -6 | Manager cascade | <role> |
| -4 | All-hands event | <role> |
| -3 | Department workshops | <role> |
| -2 | Champion training | <role> |
| -1 | Internal artifact distribution | <role> |
| 0 | External launch begins | <role> |

### 3.2 Leadership Engagement
[Paragraph specification of leadership briefing format + content]

### 3.3 All-Hands Event
[Format, content arc, take-home artifacts]

### 3.4 Department Workshops
[Per-department workshop specifications]

### 3.5 Saturation Indicators
[How brand team will know internal saturation is achieved]

## 4. Brand Champion Program

### 4.1 Champion Identification
**Criteria**: [...]
**Selection ratio**: <%>
**Cross-department representation**: [...]

### 4.2 Champion Training
**Format**: <2-day intensive / 4 half-day / self-paced + cohort>
**Module structure**: [...]

### 4.3 Champion Network
[Channel, calls, summit, recognition]

### 4.4 Champion Lifecycle
[Onboarding, active phase, sunset]

## 5. Brand Center Specification

### 5.1 Platform Decision
**Approach**: <build / SaaS / hybrid / lightweight>
**Rationale**: [paragraph]

### 5.2 User Groups + Access Model
[Per user-group access table]

### 5.3 Content Scope
[Categories included at launch + categories added post-launch]

### 5.4 Migration Plan
[Where existing assets come from + timeline]

### 5.5 Governance
**Owner role**: <role>
**Annual budget**: <range>
**Review cadence**: <interval>

### 5.6 Launch Timeline
[Deployment + content readiness + access provisioning]

## 6. Brand Guidelines Document Outline

### 6.1 Format Decision
<Web + PDF download / Web only / PDF only / Interactive web platform>

### 6.2 Document Structure
[Full structure per brand-guidelines-anatomy doctrine]

### 6.3 Production Brief
[Brief for design partner to execute brand guidelines document]

## 7. Employee Onboarding + eLearning

### 7.1 New Hire Brand Onboarding
- Day 1: <spec>
- Week 1: <spec>
- 30-day: <spec>
- 90-day: <spec>

### 7.2 eLearning Module
[Specifications + LMS integration]

## 8. External Launch Plan

### 8.1 External Launch Sequencing
**Pre-launch teaser phase**: [Yes / No + spec]
**Launch peak**: <date + content>
**Post-launch sustainment**: <4-12 week structured rollout>

### 8.2 Story Sequencing
**Lead SB7 element**: <element>
**Support elements**: [...]

### 8.3 Channel Mix
| Channel | Role | % effort | Launch-week presence |
|---|---|---|---|
| Owned | <role> | <%> | <activities> |
| Earned | <role> | <%> | <activities> |
| Paid | <role> | <%> | <activities> |
| Event-based | <role> | <%> | <activities> |

### 8.4 Customer Migration (if rebrand)
[Customer notification timing, FAQ, migration timeline]

### 8.5 Multi-Stakeholder Communication (if corporate)
[Per-stakeholder communication timing + mode]

### 8.6 Bilingual Rollout (if applicable)
[Language-specific launch considerations]

## 9. KPI Dashboard

### 9.1 Awareness Metrics
[Metrics + targets + measurement method]

### 9.2 Consideration Metrics
[Metrics + targets + measurement method]

### 9.3 Preference Metrics
[Metrics + targets + measurement method]

### 9.4 Advocacy Metrics
[Metrics + targets + measurement method]

### 9.5 Measurement Cadence
[Continuous / monthly / quarterly / annual]

### 9.6 Dashboard Format
[Single-page format + distribution to leadership]

## 10. Post-Launch Sustainment

### 10.1 Weeks 1-2 Plan
### 10.2 Weeks 3-6 Plan
### 10.3 Weeks 7-12 Plan
### 10.4 Quarter 2+ Integration into Normal Rhythm

## 11. Governance Evolution

### 11.1 Current Governance Model
<Cop / Hybrid / Concierge>

### 11.2 Target Governance Model
<Cop / Hybrid / Concierge>

### 11.3 Transition Timeline
[Months or quarters to evolve]

## 12. Risks + Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|

## Appendix A — Quality Gates Audit
## Appendix B — Bibliography
```

## Part B — Machine-Readable Handoff Schema

```yaml
ecosystem_version: "1.0"
producer_skill: brand-launch
producer_version: "1.0"
timestamp: <ISO 8601>
brief_id: <string>
upstream_checksums:
  brand_platform: <sha256>
  brand_touchpoint: <sha256>
  brand_story: <sha256|null>
  brand_maker: <sha256|null>
  brand_visual: <sha256|null>
  brand_audit: <sha256|null>

artifact_payload:
  launch_context: greenfield|rebrand|sub_brand|ma_integration|refresh|repositioning
  
  pre_launch_foundation:
    trademark_status:
      jurisdictions_filed: [...]
      classes_covered: [...]
      watch_service: <vendor|null>
      conflicts_identified: [...]
    domain_status:
      primary_domain: <string>
      defensive_registrations: [...]
      tld_coverage: {...}
      dns_configured: <boolean>
    social_handle_status:
      handles_secured:
        - platform: <string>
          handle: <string>
          verified: <boolean>
    asset_production_status:
      [touchpoint]: ready|in_production|specced

  internal_launch_plan:
    timeline:
      - week: -8
        milestone: <string>
        owner: <role>
    saturation_indicators: [...]
    leadership_engagement_spec: <string>
    all_hands_event_spec: <string>
    department_workshop_specs: [...]

  champion_program:
    identification_criteria: [...]
    selection_ratio: <%>
    training_format: <string>
    network_infrastructure: <string>
    recognition_model: <string>

  brand_center:
    platform_decision: build|saas|hybrid|lightweight
    rationale: <string>
    user_groups_access_model: {...}
    content_scope:
      launch: [...]
      post_launch: [...]
    migration_plan: <string>
    owner_role: <role>
    annual_budget_range: <string>

  brand_guidelines:
    format_decision: <string>
    document_structure: [...]
    production_brief: <string>

  employee_onboarding:
    day_1_spec: <string>
    week_1_spec: <string>
    thirty_day_check: <string>
    ninety_day_contribution: <string>
    elearning_module_spec: <string>

  external_launch_plan:
    pre_launch_teaser: <object|null>
    launch_peak_date: <ISO date>
    post_launch_sustainment_weeks: 4|12
    story_sequencing:
      lead_element: <SB7 element>
      support_elements: [...]
    channel_mix:
      owned: <%>
      earned: <%>
      paid: <%>
      event_based: <%>
    customer_migration: <object|null>
    multi_stakeholder_communication: <object|null>
    bilingual_rollout: <object|null>

  kpi_dashboard:
    awareness_metrics: [...]
    consideration_metrics: [...]
    preference_metrics: [...]
    advocacy_metrics: [...]
    measurement_cadence:
      continuous: [...]
      monthly: [...]
      quarterly: [...]
      annual: [...]
    dashboard_format: <string>
    leadership_distribution_cadence: <string>

  post_launch_sustainment:
    weeks_1_2_plan: <string>
    weeks_3_6_plan: <string>
    weeks_7_12_plan: <string>
    quarter_2_integration: <string>

  governance_evolution:
    current_model: cop|hybrid|concierge
    target_model: cop|hybrid|concierge
    transition_timeline: <string>

  risks:
    - risk: <string>
      likelihood: low|medium|high
      impact: low|medium|high
      mitigation: <string>

human_deliverable_path: ./brand-launch-output.md
quality_gates_passed: [...]
quality_gates_failed: [...]

ecosystem_complete: true
final_handoff: true
```

## Part C — Validation Rules

1. `pre_launch_foundation.trademark_status.jurisdictions_filed` must have ≥1 entry.
2. `pre_launch_foundation.domain_status.primary_domain` must be non-null.
3. `pre_launch_foundation.social_handle_status.handles_secured` must have ≥5 entries.
4. `internal_launch_plan.timeline` must show internal milestones before week 0 (external launch).
5. `external_launch_plan.channel_mix` percentages must sum to ≈100%.
6. `kpi_dashboard` must include at least one metric per category (awareness, consideration, preference, advocacy).
7. `governance_evolution` must declare current + target model.
8. `ecosystem_complete: true` flags that this is the terminal artifact of the ecosystem chain.

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
