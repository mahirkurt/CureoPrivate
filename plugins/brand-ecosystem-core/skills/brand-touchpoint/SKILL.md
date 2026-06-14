---
name: brand-touchpoint
description: >
  Touchpoint application protocol for transforming a locked visual identity
  into specifications for every customer-facing surface — stationery,
  signage, vehicle livery, packaging, retail/hospitality environment,
  branded office, trade show booth, digital touchpoints (web, social,
  deck, email), uniforms, ephemera. Operationalizes Wheeler Phase 4 +
  Geyrhalter Brand Atmosphere Touch Points + Chermayeff/Geismar/Haviv
  application principles. Composable upstream with brand-visual;
  downstream with brand-launch. USE for: touchpoints, temas noktaları,
  brand application, brand atmosphere, marka atmosferi, stationery,
  business card, kartvizit, signage, tabela, vehicle livery, araç
  giydirme, packaging, ambalaj, retail interior, perakende, social media
  templates, presentation deck, branded environment, "design our
  packaging", "how should our brand show up in retail". Use AFTER
  brand-visual locks the identity, BEFORE brand-launch.
---

# brand-touchpoint v1.0 — Application Protocol

## Raison d'être

The visual identity is locked. The narrative is set. Now the brand must show up — on a business card, on a vehicle, on a retail facade, in a presentation, on an email signature, in the office where employees work. Every touchpoint is an opportunity to either reinforce the identity or fragment it.

Most brand programs underinvest in touchpoint design. The result is identity systems that look strong in the brand guidelines and weak in the real world — strong on the logo and weak on the business card, strong on the website and weak on the email signature.

This skill produces per-touchpoint specifications dense enough that a production partner (printer, signage fabricator, web developer, retail designer) can execute without ambiguity. The discipline is to design every surface as deliberately as the logo was designed.

The thesis (Geyrhalter): every touchpoint contributes to the brand atmosphere — the aggregate sensory + emotional experience customers carry away from any encounter with the brand. Touchpoints are not isolated; they compose.

## Canonical Authority Base

| Source | Author | Role in this skill |
|---|---|---|
| *Designing Brand Identity* (6th ed.) | Wheeler | Phase 4 application protocol; touchpoint category list; production-partner brief construction |
| *How to Launch a Brand* | Geyrhalter | Brand Atmosphere Touch Points; sensory-aware touchpoint design |
| *Identify* | Chermayeff, Geismar & Haviv | Application principles drawn from 50+ years of identity practice |
| *Branding: In Five and a Half Steps* | Johnson | "Implement" phase; design system to touchpoint translation |
| *Corporate Brand Design* | Foroudi et al. | Multi-stakeholder touchpoint mapping for B2B brands |

Full bibliography in `references/bibliography.md`.

## MANDATORY EXECUTION PROTOCOL

### Step 0 — Mandatory Reference Load

```
view ./references/atmosphere-touchpoint-doctrine.md
view ./references/output-template.md
```

### Step 0.5 — Upstream Handoff Detection

`brand-touchpoint` REQUIRES `brand-visual/handoff.yaml` as input. Without it, stop:
> "This skill requires a locked visual identity system as input. Please run `brand-visual` first."

Read also `brand-platform/handoff.yaml` for sector context.

### Step 1 — Touchpoint Set Definition

Based on sector signals from upstream platform and brand business model, define the relevant touchpoint set. Standard categories (load reference per category as triggered):

| Category | Always relevant | Conditionally relevant |
|---|---|---|
| Stationery | ✓ | — |
| Email signature | ✓ | — |
| Digital touchpoints (social, deck) | ✓ | — |
| Web atmosphere | ✓ | — |
| Signage | — | Physical presence required |
| Vehicle livery | — | Mobile/fleet brand |
| Packaging | — | Physical product brand |
| Retail interior | — | Direct-to-consumer retail or hospitality |
| Trade show booth | — | B2B brand with event presence |
| Branded environment (office) | ✓ | — |
| Uniform / dress code | — | Service brand with customer-facing staff |
| Ephemera / swag | ✓ | — |

For each in-scope category, reference loading:

| Category | Reference loaded |
|---|---|
| Stationery | `stationery-business-papers.md` |
| Signage / wayfinding | `signage-environment.md` |
| Vehicle livery | `vehicle-livery.md` |
| Packaging | `packaging-structural-graphic.md` |
| Retail interior | `retail-environment.md` |
| Digital | `digital-touchpoints.md` |
| Email signature | `email-signature.md` |
| Social media templates | `social-media-templates.md` |
| Presentation deck | `presentation-deck-system.md` |
| Uniform | `uniform-design.md` |
| Ephemera | `ephemera-merchandise.md` |
| Branded environment | `branded-environment-office.md` |

### Step 2 — Per-Touchpoint Specification

For each in-scope touchpoint, produce a specification including:

**Mandatory specification elements**:
- **Purpose**: what role this touchpoint plays in the brand experience
- **Audience**: who encounters this touchpoint, in what context
- **Visual specifications**: dimensions, materials, color application, typography, layout
- **Verbal specifications**: copy elements (mandatory, optional, prohibited)
- **Production specifications**: file formats, materials, fabrication methods, production partner brief
- **Atmosphere contribution**: how this touchpoint contributes to the overall brand atmosphere (per Geyrhalter)
- **Variants**: when this touchpoint exists in multiple forms (e.g., business cards for different roles)
- **Governance**: who owns this touchpoint, what change requires approval

### Step 3 — Touchpoint Priority Ordering

Not all touchpoints are equal. Produce a priority order based on:

- **Customer journey frequency**: which touchpoints customers encounter most often
- **First-impression weight**: which touchpoints are the brand's first encounter for new customers
- **Decision-stage criticality**: which touchpoints support pivotal customer decisions
- **Investment leverage**: which touchpoints deliver brand impact per dollar/effort spent

Typical priority patterns by brand type:

| Brand type | Top-3 priority touchpoints |
|---|---|
| B2B SaaS | Web atmosphere, presentation deck, email signature |
| DTC consumer | Packaging, web atmosphere, social media templates |
| Hospitality | Retail/property interior, signage, branded environment |
| Luxury | Packaging, retail interior, stationery |
| Professional services | Presentation deck, stationery, web atmosphere |
| Industrial | Vehicle livery, uniform, signage |
| Cultural institution | Signage, wayfinding, environmental graphics |

The priority order is the recommended sequence for production investment.

### Step 4 — Atmosphere Coherence Check

After per-touchpoint specifications, validate cross-touchpoint coherence:

- **Visual consistency**: do all touchpoints express the same identity?
- **Material consistency**: do material choices reinforce the brand atmosphere?
- **Verbal consistency**: does copy across touchpoints share the same voice?
- **Sensory consistency**: does the multi-sensory experience hold together?
- **Emotional consistency**: do touchpoints produce a coherent emotional residue?

If any touchpoint diverges in a way that breaks atmosphere coherence, flag for redesign.

### Step 5 — Quality Gates

| Gate | Check | Action if failed |
|---|---|---|
| G1 | Upstream brand-visual handoff present | Block, request visual first |
| G2 | All in-scope touchpoints specified | Block, complete missing |
| G3 | ≥10 touchpoint categories specified | Flag if below threshold |
| G4 | Atmosphere coherence verified | Block, remediate inconsistencies |
| G5 | Production partner brief included per touchpoint | Block, complete briefs |
| G6 | Priority order produced | Block, produce priority |
| G7 | Governance assignments per touchpoint | Block, assign owners |

### Step 6 — Output

Produce:
1. **Touchpoint specifications document** — markdown, 15-40 pages depending on scope
2. **Per-touchpoint mini-briefs** — extractable production briefs (one per touchpoint)
3. **handoff.yaml** — machine-readable artifact

## Output Contract

```yaml
producer_skill: brand-touchpoint
artifact_payload:
  touchpoint_categories_in_scope: [<string>, ...]
  touchpoints:
    stationery:
      business_card: <full spec>
      letterhead: <full spec>
      envelope: <full spec>
      email_signature: <full spec>
    signage:
      primary_signage: <full spec or n/a>
      wayfinding: <full spec or n/a>
      vehicle_livery: <full spec or n/a>
    packaging:
      structural: <full spec or n/a>
      graphic: <full spec or n/a>
    environmental:
      retail_interior: <full spec or n/a>
      branded_environment_office: <full spec>
      trade_show_booth: <full spec or n/a>
    digital:
      web_atmosphere: <full spec>
      social_media_template_kit: <full spec>
      presentation_deck_system: <full spec>
    human:
      uniform_dress_code: <full spec or n/a>
    ephemera:
      merchandise: <full spec>
  touchpoint_priority_order: [tp1, tp2, ...]
  atmosphere_coherence_check: pass|fail
  atmosphere_coherence_notes: <string>
```

## Version

**v1.0 — May 2026.**

## Known Limits

- Produces specifications, not finished design files. Production partners (designers, printers, fabricators, developers) execute from specifications.
- Cannot predict production cost; cost estimation requires production partner involvement.
- Material specifications assume standard production. Premium/custom materials may require sample sourcing.
- Cultural specificity in touchpoints (e.g., right-to-left layout for Arabic markets) requires explicit declaration in brief.
