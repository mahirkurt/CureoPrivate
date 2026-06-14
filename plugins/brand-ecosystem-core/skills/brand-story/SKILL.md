---
name: brand-story
description: >
  Customer-centric brand narrative protocol. Operationalizes Miller's
  SB7 Framework (Character → Problem → Guide → Plan → CTA → Failure →
  Success) plus Rodriguez IMC Reimagined diffusion plan into a
  single-page BrandScript, three-layer problem analysis
  (external/internal/philosophical), villain framework, and
  Robin-to-Batman compliance check. Reads brand-platform handoff as
  input. USE for: brand story, marka hikâyesi, BrandScript, SB7,
  StoryBrand, three-layer problem, üç-katmanlı problem,
  Robin-to-Batman, customer-as-hero narrative, müşteri-kahraman, brand
  narrative arc, marka anlatısı, IMC plan, internal-first diffusion,
  villain framework, antagonist, philosophical layer, message
  hierarchy, brand voice principles, narrative coherence, B2B
  narrative, luxury narrative restraint, purpose narrative.
---

# brand-story v1.0 — Customer-Centric Narrative Protocol

## Raison d'être

Most brand strategy documents stop at positioning. Then a separate "messaging exercise" produces fragmented taglines, value propositions, and elevator pitches that don't cohere. This skill closes that gap by producing a single-page BrandScript — a structured narrative artifact every downstream activity reads as a parameter.

The core thesis (Miller, 2017): **the customer is the hero, the brand is the guide**. Brands that cast themselves as heroes lose. Brands that cast themselves as Yoda to the customer's Luke Skywalker — that wisely, generously help the customer succeed — win.

The diffusion thesis (Rodriguez, 2020): **brand stories must be socialized internally before they go to market externally**. An IMC Reimagined plan sequences internal storytellers (employees becoming evangelists) before external campaigns. This is the opposite of the traditional advertising-led launch.

This skill produces both: the BrandScript and the IMC Reimagined diffusion plan. Together they constitute the narrative spine that every downstream skill references.

## Canonical Authority Base

| Source | Author | Role in this skill |
|---|---|---|
| *Building a StoryBrand* | Donald Miller | SB7 Framework (7 elements), Robin-to-Batman doctrine, three-layer problem analysis |
| *Brand Storytelling* | Miri Rodriguez | IMC Reimagined plan, internal-first diffusion, villains/antagonists framework, Haystack trend curation method |
| *How to Launch a Brand* | Fabian Geyrhalter | Brand character development, Mr. Clean / Most Interesting Man case studies |
| *Designing Brand Identity* (6th ed.) | Alina Wheeler | Messaging hierarchy, voice + tone consistency principles |
| *Branding: In Five and a Half Steps* | Michael Johnson | Strategy-to-narrative bridge, brand voice articulation |

Full bibliography in `references/bibliography.md`.

## MANDATORY EXECUTION PROTOCOL

### Step 0 — Mandatory Reference Load

Every invocation loads these references first:

```
view ./references/sb7-framework-detailed.md
view ./references/three-layer-problem.md
view ./references/output-template.md
```

### Step 0.5 — Upstream Handoff Detection (REQUIRED)

`brand-story` REQUIRES `brand-platform/handoff.yaml` as input. If absent, stop and respond:

> "This skill requires a Brand Platform document as input. Please run `brand-platform` first, or provide an equivalent platform artifact."

Extract from the platform handoff:
- `target_persona` → seeds the SB7 "Character" (the customer/hero)
- `positioning_statement.who` → seeds the three-layer problem analysis
- `brand_personality` → constrains the brand's voice as guide
- `brand_promise` → seeds the SB7 "Success" outcome
- `brand_voice_principles` → constrains all narrative copy

### Step 1 — Brief Triage and Reference Routing

Based on platform handoff content + any additional brief, load additional references:

| Trigger | Reference loaded |
|---|---|
| B2B / enterprise / professional services | `b2b-narrative-stakeholders.md` |
| Consumer DTC / FMCG / retail | `consumer-narrative-emotion.md` |
| Luxury (if luxury module was active in platform) | `luxury-narrative-restraint.md` |
| Mission-driven / purpose / impact brand | `purpose-narrative-stance.md` |
| Rebrand (story shift required) | `rebrand-narrative-bridge.md` |
| Multi-audience brand (B2B with end-user vs buyer) | `multi-stakeholder-narrative.md` |
| Default | `imc-reimagined-plan.md` + `villains-antagonists.md` |

### Step 2 — SB7 Framework Construction

This is the core. Construct each of Miller's seven elements, in order, drawing from the platform handoff.

#### 2.1 Character (the Hero — the customer)

Pull from `target_persona` in platform handoff. Translate the persona block into a hero archetype:
- What does the customer want? (concrete, in their own words)
- What life stage are they in?
- What story are they currently living?

The Character clause is one sentence: *"<Persona descriptor> wants <concrete want>."*

#### 2.2 Has a Problem (three-layer analysis)

Reference `three-layer-problem.md` for full treatment. Every customer faces:

- **External problem**: the observable obstacle in the world
- **Internal problem**: the emotional frustration the external problem causes
- **Philosophical problem**: the "this is wrong in the world" stance the brand takes

Construct one paragraph per layer. The external problem is what the customer says out loud. The internal problem is what they feel. The philosophical problem is what they sense but rarely articulate.

#### 2.3 Meets a Guide (the brand)

The brand enters the story as the wise mentor, not the hero. The guide has two qualities (Miller):

- **Empathy**: the guide demonstrates understanding of the hero's struggle
- **Authority**: the guide demonstrates competence to help

Construct one paragraph each:
- Empathy statement (how the brand has experienced or deeply understands the hero's struggle)
- Authority statement (the brand's credentials, methodology, or evidence of capability)

These together produce the BrandScript's "Guide" section.

#### 2.4 Who Gives Them a Plan

A three-step plan the hero can follow. Each step must be:
- Concrete (the hero knows what to do)
- Sequential (step 2 builds on step 1)
- Owned (the hero, not the brand, takes the action)

The plan is what reduces friction. Customers don't engage brands whose path is unclear.

#### 2.5 And Calls Them to Action

Two CTAs are needed:

- **Direct CTA**: the explicit ask (Buy, Schedule, Sign Up, Contact)
- **Transitional CTA**: the lower-commitment ask (Read more, Download guide, Get quote)

Direct CTAs convert customers ready now. Transitional CTAs nurture customers not yet ready. Brands without both leave money on the table.

#### 2.6 That Helps Them Avoid Failure

The stakes. What happens if the hero doesn't engage the brand? Three or four concrete consequences. These are not the brand bragging about superiority; these are honest portrayals of the cost of inaction or wrong choice.

#### 2.7 And Ends in Success

The transformation. The before/after picture. What does the hero's life look like once the problem is resolved? This must be concrete (visualizable), believable (proportionate to the brand's actual delivery), and emotionally resonant.

### Step 3 — Villains & Antagonists Framework (Rodriguez)

Beyond the hero-guide dynamic, identify the antagonist(s):

- **The personification of the problem**: who or what embodies the obstacle the hero faces?
- **The competing brands**: not as enemies, but as the alternative paths the hero might wrongly choose
- **The industry/cultural norms**: the broader pattern the brand challenges

Villains add narrative tension. Without them, brand stories flatten into self-promotion. With them, the story takes on the structure of conflict-resolution that audiences recognize and engage with.

### Step 4 — Robin-to-Batman Compliance Test

The hard quality gate. Read the constructed BrandScript and ask:

- Does the customer appear as the hero, or does the brand?
- Is the brand a sidekick (Robin) supporting the customer (Batman), or does the brand cast itself as Batman?
- When a stranger reads the BrandScript, who do they identify with — the customer or the brand?

Brands consistently fail this test. The temptation to make the brand the hero is enormous. The discipline is to resist it.

If the BrandScript fails the Robin-to-Batman test, rewrite. Do not proceed.

### Step 5 — IMC Reimagined Diffusion Plan

The narrative must be diffused. Rodriguez's IMC Reimagined plan (Integrated Marketing Communications Reimagined) sequences:

#### 5.1 Internal Phase

Before any external storytelling, the brand story is socialized internally:
- **Leadership briefing**: leaders internalize the BrandScript
- **Employee evangelization**: every employee can tell the story
- **Champion identification**: internal storytellers are identified by role and aptitude
- **Storyteller training**: champions learn to tell the brand story authentically in their own voice
- **Internal-facing artifacts**: employee handbooks, all-hands presentations, onboarding programs

Output: a paragraph specification of the internal phase plus a list of internal artifacts to be produced.

#### 5.2 External Phase

Only after the internal phase has saturated:
- **Storytelling priority channels**: where the story will be told first externally
- **Sequencing of messages**: which SB7 element leads, which support
- **Channel mix**: PR, social, content, advertising — in what proportion
- **Story testing protocol**: how the brand will know if the story is landing

Output: a paragraph specification of the external phase plus channel-and-sequence recommendations.

### Step 6 — Quality Gates

| Gate | Check | Action if failed |
|---|---|---|
| G1 | Upstream platform handoff present | Block, request platform first |
| G2 | All 7 SB7 elements complete | Block, return to incomplete element |
| G3 | Three-layer problem analysis present (all 3 layers) | Block, complete missing layer |
| G4 | Robin-to-Batman test pass | Block, rewrite narrative |
| G5 | Empathy AND authority both demonstrated in Guide section | Block, complete missing dimension |
| G6 | Direct AND Transitional CTA both present | Block, add missing CTA |
| G7 | Villain/antagonist explicitly identified | Block, identify antagonist |
| G8 | IMC Reimagined plan covers internal + external phases | Block, complete plan |
| G9 | Bilingual rationale on narrative arc + voice | Block, add TR rationale |

### Step 7 — Output

Produce:
1. **BrandScript** — single-page narrative summary, per Miller's format, bilingual TR/EN
2. **Three-Layer Problem Analysis** — paragraph per layer
3. **Villains & Antagonists block**
4. **IMC Reimagined Plan** — internal phase + external phase
5. **Robin-to-Batman test results**
6. **handoff.yaml** — machine-readable output per schema in `output-template.md`

## Output Contract

```yaml
producer_skill: brand-story
producer_version: 1.0
artifact_payload:
  brandscript:
    character: <hero description>
    has_a_problem:
      external: <observable problem paragraph>
      internal: <emotional problem paragraph>
      philosophical: <"why it's wrong" paragraph>
    meets_a_guide:
      empathy_statement: <paragraph>
      authority_statement: <paragraph>
    who_gives_them_a_plan: [step1, step2, step3]
    and_calls_them_to_action:
      direct_cta: <phrase>
      transitional_cta: <phrase>
    that_helps_them_avoid_failure: [stake1, stake2, stake3]
    and_ends_in_success: <transformation paragraph>
  villains_antagonists:
    personified_problem: <description>
    competing_alternatives: [...]
    industry_norms_challenged: [...]
  robin_to_batman_test: pass|fail
  imc_diffusion_plan:
    internal_phase: <paragraph>
    internal_artifacts: [...]
    external_phase: <paragraph>
    external_channel_sequence: [...]
  narrative_arc_milestones: [m1, m2, m3]
```

## Version

**v1.0 — May 2026.** Initial release. SB7 + IMC Reimagined + Villains framework integrated.

## Known Limits

- Cannot validate that a story resonates with real customers. Validation is a separate workstream (concept testing, message testing).
- Cannot generate brand-voice-perfect copy. Produces narrative architecture; copywriting is downstream.
- Cannot resolve fundamental positioning conflicts. If the platform document has weak positioning, the BrandScript will inherit that weakness.
- IMC Reimagined assumes the brand has employees who can be storytellers. Solopreneur or pre-launch brands receive a modified internal-phase recommendation.
