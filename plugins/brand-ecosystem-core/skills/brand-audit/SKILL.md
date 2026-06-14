---
name: brand-audit
description: >
  Diagnostic brand audit protocol for rebrand, refresh, M&A
  integration, and post-launch performance assessment. Produces
  findings report covering brand asset inventory, competitive audit,
  IP/trademark audit, process audit, gap analysis, and opportunity
  statement. Operationalizes Wheeler 5th + 6th edition audit protocols.
  Optional entry point; feeds brand-platform downstream. USE for: brand
  audit, marka denetimi, competitive audit, rekabet denetimi, marka
  varlık envanteri, marka portföy denetimi, competitive landscape
  mapping, rebrand diagnostic, brand refresh, M&A brand integration,
  M&A marka bütünleşmesi, post-launch assessment, post-lansman
  değerlendirme, positioning gap analysis, visual white space, IP
  audit, IP denetimi, trademark portfolio review, brand governance
  audit, marka yönetişim denetimi, marka itibar denetimi, "audit our
  current brand", "competitive landscape analysis".
---

# brand-audit v1.0 — Brand Diagnostic Protocol

## Raison d'être

Rebrands fail when they begin without honest diagnosis. Teams begin redesigning before understanding what they have, what works, what doesn't, and where the competitive opportunity lies. This skill produces the diagnostic foundation — Wheeler's Phase 1 — that grounds every rebrand, refresh, M&A integration, or post-launch brand assessment.

The discipline covers four diagnostic dimensions:
1. **Brand asset inventory** — what the brand has today
2. **Competitive audit** — what competitors occupy and where the white space is
3. **IP & trademark audit** — what is legally protected and what is exposed
4. **Process audit** — how the brand is currently governed and applied

The output is a findings report that brand-platform reads as upstream input.

## When to use this skill

- Rebrand decision: should we rebrand, refresh, or hold?
- Refresh in progress: what to keep, evolve, or replace?
- M&A integration: how to align two brand systems?
- Post-launch assessment: is the brand performing as intended?
- Brand health check: routine 2-3 year diagnostic

## When NOT to use this skill

- Greenfield new venture with no prior brand: skip to brand-platform
- Product-naming-only briefs: skip to brand-maker
- Pure visual identity refresh without strategic shift: skip to brand-visual

## Canonical Authority Base

| Source | Author | Role in this skill |
|---|---|---|
| *Designing Brand Identity* (6th ed.) | Wheeler | Phase 1 audit protocol; brand audit + marketing audit + competitive audit distinction |
| *Designing Brand Identity* (5th ed.) | Wheeler | Brand asset inventory framework; brand governance audit (Cop vs Concierge models) |
| *Branding: In Five and a Half Steps* | Johnson | "Investigate" phase methodology; audit-to-strategy bridge |
| *How to Launch a Brand* | Geyrhalter | Brand DNA discovery via existing-asset analysis |
| *Corporate Brand Design* | Foroudi et al. | Stakeholder-perception audit methodology |

Full bibliography in `references/bibliography.md`.

## MANDATORY EXECUTION PROTOCOL

### Step 0 — Mandatory Reference Load

```
view ./references/competitive-audit-protocol.md
view ./references/brand-asset-audit.md
view ./references/output-template.md
```

### Step 1 — Brief Triage

Confirm audit scope. The user must declare which dimensions are in scope:

| Dimension | In scope? | Default for use case |
|---|---|---|
| Brand asset inventory | Y/N | Always Y for rebrand/refresh |
| Competitive audit | Y/N | Always Y |
| IP/trademark audit | Y/N | Always Y |
| Process audit | Y/N | Optional; Y if rebrand or M&A |

If brief doesn't declare scope, default to all four dimensions.

### Step 2 — Brand Asset Inventory

Catalog everything the brand has today:

**Visual assets**:
- Existing logos (all variants)
- Existing color palettes
- Existing typography systems
- Existing iconography
- Existing photography style
- Existing illustration library

**Verbal assets**:
- Brand name (and any legal variants)
- Tagline(s)
- Boilerplate copy
- Brand voice principles (if any)
- Existing positioning statement (if any)

**Strategic assets**:
- Brand platform document (if exists)
- Brand guidelines document
- Customer research conducted
- Market positioning analyses

**Operational assets**:
- Trademark portfolio (registered marks by jurisdiction)
- Domain portfolio
- Social handle inventory
- Brand center / online asset library (if exists)

The deliverable: a tabular inventory + assessment per asset (Keep / Evolve / Retire).

### Step 3 — Competitive Audit

Reference `competitive-audit-protocol.md` for full methodology. Summary:

**Map the competitive set**:
- 3-5 direct competitors (same category, same audience)
- 2-4 indirect competitors (different category, same wallet/time share)
- 1-2 aspirational reference brands (different stage, similar trajectory)

**For each competitor, document**:
- Positioning claim
- Brand archetype (inferred)
- Visual identity character (palette, type, imagery, voice)
- Brand voice characteristics
- Customer persona served
- Touchpoint footprint
- Recent narrative shifts

**Identify white space**:
- Positioning gaps (claims nobody owns)
- Visual white space (colors, typography territories nobody occupies)
- Voice white space (tones nobody adopts)
- Audience white space (segments underserved)
- Touchpoint white space (channels underutilized)

### Step 4 — IP & Trademark Audit

The legal foundation. Must cover:

- **Trademark registration status**: which marks are registered, in which jurisdictions, in which classes
- **Trademark conflicts**: any pending or potential conflicts identified
- **Expiration timeline**: when renewals are due
- **Geographic gaps**: jurisdictions where the brand operates but doesn't have trademark protection
- **Class coverage gaps**: product/service classes the brand operates in but doesn't have trademark protection
- **Domain portfolio**: principal domains owned, variants secured, defensive registrations
- **Social handle inventory**: handles secured across major platforms

Flag any pre-existing legal risks for resolution before brand-platform begins.

### Step 5 — Process Audit (if in scope)

How is the brand currently governed?

**Governance model**:
- **Cop model**: top-down enforcement, central approval required, slow but consistent
- **Hybrid model**: central guidelines + local interpretation, moderate consistency
- **Concierge model**: central enablement + decentralized execution, faster but requires strong system

Most brands today are evolving from Cop to Concierge. The audit identifies where the brand sits currently and what change is needed.

**Operational audit**:
- Brand guidelines: exist? completeness? currency?
- Brand center / online asset library: exist? adoption?
- Approval workflows: clear? bottlenecked?
- Champion network: exist? trained?
- Onboarding: brand introduction systematic?
- Cross-team consistency: assessed how?

### Step 6 — Gap Analysis + Opportunity Statement

Synthesize the four audit dimensions into:

**Gap analysis**:
- Strategic gaps: what positioning is undefended or weak
- Visual gaps: what visual choices fail current strategic intent
- Verbal gaps: what voice/message inconsistencies exist
- Operational gaps: what governance failures cause drift
- Legal gaps: what IP/trademark exposures need addressing

**Opportunity statement**:
A single paragraph stating the strategic opportunity the audit reveals. This becomes the brief for brand-platform.

Example:
> *"The brand currently occupies a defensible 'considered alternative' position within the specialty coffee category, but its visual identity expresses 'mass-premium' more than 'considered alternative' — creating a strategic-visual gap that competitors exploit. The opportunity is a visual identity refresh that aligns expression with positioning, paired with a strengthened brand voice that articulates what makes the brand 'considered' rather than 'premium'. No fundamental repositioning is required; the strategic foundation is sound."*

### Step 7 — Quality Gates

| Gate | Check | Action if failed |
|---|---|---|
| G1 | Audit scope declared | Block, request scope |
| G2 | All in-scope dimensions audited | Block, complete missing |
| G3 | ≥3 direct competitors mapped | Block, expand competitive set |
| G4 | IP audit covers ≥1 jurisdiction with trademark status | Block, complete IP review |
| G5 | Opportunity statement is single paragraph + decision-ready | Block, refine |
| G6 | Audit coverage ≥80% (declared scope items completed) | Flag for completeness |

### Step 8 — Output

Produce:
1. **Findings Report** — markdown document, 8-20 pages depending on scope
2. **handoff.yaml** — machine-readable per `references/output-template.md`

## Output Contract

```yaml
producer_skill: brand-audit
artifact_payload:
  audit_scope: [asset_inventory, competitive, ip, process]
  asset_inventory:
    visual: [...]
    verbal: [...]
    strategic: [...]
    operational: [...]
  competitive_landscape:
    direct_competitors: [...]
    indirect_competitors: [...]
    aspirational_references: [...]
    positioning_gaps: [...]
    visual_white_space: [...]
    voice_white_space: [...]
    audience_white_space: [...]
    touchpoint_white_space: [...]
  ip_status:
    trademarks_registered: [...]
    trademark_conflicts: [...]
    jurisdiction_gaps: [...]
    class_gaps: [...]
    domain_portfolio: [...]
    social_handles: [...]
  process_diagnosis:
    governance_model: cop|hybrid|concierge
    guidelines_strength: weak|medium|strong
    operational_gaps: [...]
  gap_analysis:
    strategic_gaps: [...]
    visual_gaps: [...]
    verbal_gaps: [...]
    operational_gaps: [...]
    legal_gaps: [...]
  opportunity_statement: <single paragraph>
```

## Version

**v1.0 — May 2026.** Initial release.

## Known Limits

- Cannot validate brand health through real consumer research; produces the research brief
- Trademark conflict identification is preliminary — formal IP counsel required
- Cannot assess employee perception without survey research — produces survey design
- Cannot measure brand equity without external benchmarking studies
