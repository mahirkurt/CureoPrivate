---
name: brand-platform
description: >
  Foundation document protocol for any brand venture. Produces vision,
  mission, core values, brand personality (Jung archetype + Aaker 5-D),
  target persona (demographic + 4Cs psychographic + Maslow), Ries-Trout
  six-clause positioning, brand promise, competitive landscape, and
  brand voice principles. Sector-agnostic; opt-in luxury + corporate
  B2B modules. Composable upstream with brand-audit; downstream with
  brand-story, brand-maker, brand-visual, brand-touchpoint,
  brand-launch. USE for: brand platform, marka platformu, brand
  strategy, marka stratejisi, positioning, konumlandırma, vision
  mission values, vizyon misyon değerler, target persona, hedef
  persona, brand personality, marka kişiliği, brand archetype, marka
  arketipi, brand voice, markanın sesi, before naming, before logo,
  brand foundation, rebrand foundation, sub-brand platform, B2B brand
  strategy, luxury brand strategy, startup brand foundation.
---

# brand-platform v1.0 — Foundation Protocol

## Raison d'être

Every serious brand starts with a foundation document. Without it, naming choices are arbitrary, visual identity has nothing to express, narrative has no anchor, and launch has no compass. This skill produces that foundation — not in the rambling form of a typical agency strategy deck, but as a tight, decision-ready document that downstream skills (brand-story, brand-maker, brand-visual, brand-touchpoint, brand-launch) can consume directly as a parameter.

The discipline is sector-agnostic. The same five-clause positioning formula, the same eight-element platform structure, the same archetypal personality framework applies to a B2B SaaS startup, a Gen-Z DTC beverage, a regional law firm, a luxury jeweler, or a municipal arts foundation. Regulated categories activate **opt-in modules**; without trigger signals they stay silent.

This skill **claude.ai-native** and **free-tier**. It depends on no paid APIs and no live market research databases. When primary research is required (segmentation studies, ethnography, conjoint analysis), this skill produces the research brief; the research itself must be commissioned externally.

## Canonical Authority Base

| Source | Author | Role in this skill |
|---|---|---|
| *How to Launch a Brand* (2nd ed.) | Geyrhalter | Brand Platform structure, SAS test (Soul/Attractive/Smart) |
| *Building a StoryBrand* | Miller | Customer-centricity discipline, internal vs external problem layer |
| *Designing Brand Identity* (6th ed.) | Wheeler | Phase 1 research, Phase 2 strategy clarification |
| *Branding: In Five and a Half Steps* | Johnson | Investigate phase, identity-to-branding doctrine |
| *Creating a Brand Identity* | Slade-Brooking | Psychographic profiling, Stephen King brand personality, 4Cs |
| *Corporate Brand Design* | Foroudi, Mahdavi & Foroudi | Corporate identity mix (mind/soul/voice × behaviour/communication/symbolism) |
| *Positioning: The Battle for Your Mind* | Ries & Trout | Six-clause positioning formula, category ladder doctrine |
| *The Hero and the Outlaw* | Pearson & Mark | 12 Jung archetypes operationalized |
| *Brand Asset Valuator* / *Aaker 5-D* | Y&R / Aaker | 5-dimension personality framework |
| *Designing Luxury Brands* | Derval | Luxury opt-in: positioning map, sensory mix, Hormonal Quotient® |

Full bibliography in `references/bibliography.md`.

## MANDATORY EXECUTION PROTOCOL

### Step 0 — Mandatory Reference Load

Every invocation of `brand-platform` MUST first load these three files. Progressive disclosure is **disabled** for them:

```
view ./references/platform-structure.md
view ./references/positioning-doctrine.md
view ./references/output-template.md
```

### Step 0.5 — Upstream Handoff Detection

If `brand-audit/handoff.yaml` exists, load it and treat its findings as input parameters:
- `competitive_landscape` → seeds Step 4's competitive analysis
- `positioning_gaps` → biases Step 5's positioning candidates
- `opportunity_statement` → frames Step 1's vision exploration

### Step 1 — Brief Triage and Reference Routing

Read the user's brief. Activate additional references based on these triggers:

| # | Trigger signal | Reference loaded |
|---|---|---|
| 1 | "B2B", "enterprise", "professional services", "consultancy" | `corporate-identity-mix.md` |
| 2 | "consumer", "DTC", "retail", "FMCG", "fashion" | `consumer-psychographics.md` |
| 3 | "luxury", "premium", "super-luxury", "haute couture", "fine X" | `luxury-platform-derval.md` (OPT-IN MODULE) |
| 4 | "startup", "new venture", "early-stage", "founder-led" | `startup-platform-shortcuts.md` |
| 5 | "rebrand", "refresh", "merger", "M&A integration" | `rebrand-foundation.md` |
| 6 | "sub-brand", "extension", "endorsed brand" | `sub-brand-platform.md` |
| 7 | "global", "born-global", "EMEA", "APAC", "multi-market" | `multi-market-platform.md` |
| 8 | Brief mentions specific reference brands | `competitive-benchmarking.md` |
| Default | Any brief | Personality (`personality-frameworks.md`) + Persona (`persona-construction.md`) |

**Rule**: If in doubt, load more. Opt-in modules are silent unless triggered.

### Step 2 — Brief Completeness Check (only if necessary)

If the brief lacks any of the following **five mandatory inputs**, ask them in a single message:

1. **Category & sector** — what does this brand do?
2. **Target geography** — where will this brand operate?
3. **Founder/leadership intent** — why does this brand exist?
4. **Competitive context** — who occupies adjacent positions?
5. **Constraints** — taboos, non-negotiables, existing assets to preserve.

If the brief already covers these, **proceed directly to Step 3**.

### Step 3 — Eight-Element Platform Construction

This is the core of the skill. Construct each of the eight elements in the platform document, in order.

#### 3.1 Vision

A single sentence describing the aspirational endpoint — what the world looks like when the brand has succeeded. Not the company's quarterly goal; the long-horizon picture.

- Format: `<Brand> envisions a world where <future state>.`
- Length: ≤25 words.
- Quality test: Could the vision survive a strategy pivot? If no, it's tactics, not vision.

#### 3.2 Mission

A single sentence describing why the brand exists today and what it does for customers. Operational, present-tense.

- Format: `<Brand> exists to <verb> <for whom> by <how>.`
- Length: ≤30 words.
- Quality test: Does this read as a verb + benefit + mechanism? If not, rewrite.

#### 3.3 Core Values (3–5 maximum)

Behavioral principles, not abstractions. Each value must:
- Be a single word or short phrase, not a sentence.
- Pass the "opposite test" — its opposite must be plausibly something another brand believes (if the opposite is absurd, the value is empty filler).
- Translate to specific operational behaviors (which Step 8 will define).

#### 3.4 Brand Personality (three-layer composite)

**Layer A — Jung archetype** (one primary, optional secondary):
Sage · Outlaw · Creator · Hero · Caregiver · Magician · Everyman · Lover · Jester · Ruler · Innocent · Explorer.

Reference `personality-frameworks.md` for the full visual + verbal translation matrix.

**Layer B — Aaker 5-dimension score (0–10 each):**
- Sincerity (down-to-earth, honest, wholesome, cheerful)
- Excitement (daring, spirited, imaginative, up-to-date)
- Competence (reliable, intelligent, successful)
- Sophistication (upper-class, charming)
- Ruggedness (outdoorsy, tough)

The brand's profile is a polygon across these five axes. Two brands can share an archetype but differ sharply on Aaker dimensions.

**Layer C — Voice traits (3–5 adjectives):**
Concrete adjectives describing how the brand sounds. Examples: "warm but authoritative", "wry and irreverent but never cynical", "precise without being clinical".

#### 3.5 Target Persona

**Demographic block:**
- Age range
- Gender mix (if salient)
- Income band
- Geography
- Education
- Occupation cluster
- Household composition (if salient)

**Psychographic block** (drawing on Slade-Brooking framework + Young & Rubicam 4Cs):
Place the persona within one of the seven 4Cs segments — *Resigned · Struggler · Mainstreamer · Aspirer · Succeeder · Explorer · Reformer* — and write a paragraph describing values, attitudes, daily life, media habits, brand affinities, and unmet needs.

**Maslow layer:**
At what level of Maslow's hierarchy does this brand operate primarily? (Physiological / Safety / Love-belonging / Esteem / Self-actualization). This dictates the emotional register downstream.

#### 3.6 Positioning Statement (Ries-Trout six-clause formula)

```
For <target customer>,
who <unmet need or problem>,
<Brand> is the <category>
that <key benefit or point of difference>,
unlike <primary competitor>,
because <reason to believe>.
```

This is the single most consequential output of the platform document. Every downstream skill reads this clause-by-clause:
- Clause 1 → brand-story uses this as the Hero
- Clause 2 → brand-story uses this for the three-layer problem analysis
- Clause 3 → brand-maker uses this to set category exemplar context
- Clause 4 → brand-visual uses this to find visual white space
- Clause 5 → brand-visual uses this for competitive visual differentiation
- Clause 6 → brand-launch uses this for messaging substantiation

#### 3.7 Brand Promise

A single sentence stating what the customer experiences. Forward-facing, customer-pointed, evidenced.

- Format: `When you choose <Brand>, you experience <transformation>.`
- Length: ≤20 words.
- Quality test: Can the brand operationally deliver this on every touchpoint? If no, the promise is fiction.

#### 3.8 Brand Voice Principles

3–5 principles governing how the brand speaks. Each principle must include:
- A positive directive (what the voice does)
- A negative directive (what the voice never does)
- A specimen pair: one "yes" example, one "no" example

Example:
> **Principle**: Concrete over abstract.
> *Yes*: "Ships in 48 hours."
> *No*: "Industry-leading delivery times."

### Step 4 — Competitive Landscape Summary

A single paragraph + one positioning matrix (text-described, not graphic). Identify:
- Three primary direct competitors (same category, same audience)
- Two indirect competitors (different category, same wallet share)
- The visual + verbal white space the brand will occupy

If `brand-audit/handoff.yaml` was loaded, this section synthesizes the audit's `competitive_landscape` into a single paragraph.

### Step 5 — Quality Gates

Before producing the final output, validate against these gates:

| Gate | Check | Action if failed |
|---|---|---|
| G1 | All eight elements present | Block output, return to incomplete element |
| G2 | Each claim has canonical citation | Block output, add citations |
| G3 | Bilingual rationale present on positioning + voice | Block output, add TR rationale |
| G4 | Robin-to-Batman compliance: positioning centers the customer, not the brand | Rewrite positioning |
| G5 | SAS test (Geyrhalter): Soul + Attractive + Smart all satisfied | Flag deficiency |
| G6 | Opposite test on all values: no opposite is universally agreed-upon | Replace failing values |

### Step 6 — Output

Produce:
1. **Human-readable deliverable**: Markdown document, 8–15 pages, structured per `output-template.md`.
2. **Machine-readable handoff**: `handoff.yaml` per the schema in `references/output-template.md`.
3. **Optional executive summary**: Single-page synthesis for stakeholder distribution.

## Sector Opt-In Modules

### Luxury Module *(live)*

Triggers: "luxury", "premium", "super-luxury", "haute couture", "fine jewelry", "high-end", "exclusive", "Bottega Veneta", "Hermès", "Loro Piana", "Cartier", "Patek Philippe", or similar reference brands.

When activated, loads `luxury-platform-derval.md` and adds these to Step 3:
- **Positioning map calibration** (Derval): premium vs luxury vs super-luxury vs affordable luxury
- **Brand codes** specification: signature elements that customers recognize before reading the name
- **Sensory mix** primary axis: which sense leads (visual/tactile/olfactory/auditory/gustatory)
- **Hormonal Quotient® persona overlay**: prenatal hormone influence on luxury purchase decisions
- **Wait Marketing** channel disposition: airport, hotel, private banking, atelier visit
- **Travel retail** strategic stance: present, absent, or selective

The luxury module adds approximately 1,500–2,500 words to the platform document.

### Corporate / B2B Module *(live)*

Triggers: "B2B", "enterprise", "professional services", "consultancy", "law firm", "accounting", "management consulting", "industrial".

When activated, loads `corporate-identity-mix.md` and overlays the Foroudi/Olins corporate identity framework on Step 3.4 (personality). Adds:
- Mind/Soul/Voice mapping: cognitive philosophy / subjective culture / total communication
- Behaviour/Communication/Symbolism trinity
- Stakeholder map: customers, employees, regulators, partners, investors, community
- Reputation vs identity vs image distinction

### Reserved Opt-In Slots

Architecturally ready, content pending:
- Fintech (regulatory advertising constraints, trust primitives)
- Food & Beverage (ingredient claims, sensory protocols)
- Hospitality (location-based cues, service-staging)
- Professional Services with regulated advertising (medical practice, legal counsel)
- Alcohol & Tobacco (age-gating, contextual restrictions)

## Output Contract

See `references/output-template.md` for the full schema. In brief:

```yaml
producer_skill: brand-platform
producer_version: 1.0
artifact_payload:
  vision: <string>
  mission: <string>
  core_values: [<string>, ...]
  brand_personality:
    jung_archetype: <string>
    aaker_5d: { ... }
    voice_traits: [<string>, ...]
  target_persona:
    demographic: { ... }
    psychographic_segment: <string>
    psychographic_summary: <string>
    maslow_layer: <string>
  positioning_statement:
    for: <string>
    who: <string>
    is: <string>
    that: <string>
    unlike: <string>
    because: <string>
  brand_promise: <string>
  competitive_landscape_summary: <string>
  brand_voice_principles: [{principle, yes_example, no_example}, ...]
```

## Version

**v1.0 — May 2026.** Initial release. Eight-element platform structure, luxury + corporate B2B opt-in modules live, five reserved opt-in slots architecturally ready.

## Known Limits

- No live market research surface. When primary research is required, this skill produces the research brief; commissioning is external.
- Persona psychographic block depends on the brief's quality. Bad brief in → bad persona out. The skill cannot invent market truth.
- Positioning statement requires honest competitive self-assessment. A brand claiming differentiation it doesn't have will produce a positioning statement that won't survive launch.
- The skill produces strategy, not market validation. Validation is a separate workstream (concept testing, MVP, ethnographic study).
