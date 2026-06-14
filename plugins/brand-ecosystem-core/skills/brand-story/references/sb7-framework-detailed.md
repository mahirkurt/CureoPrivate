# SB7 Framework — Detailed Operational Reference

**Mandatory reference, loaded at Step 0.**

The SB7 Framework was developed by Donald Miller in *Building a StoryBrand* (2017). It is the most operationally useful customer-centric brand narrative framework in current practice. This reference is the canonical operational treatment.

## The Seven Elements

```
A Character — has a Problem — and meets a Guide — who gives them a Plan
— and calls them to Action — that helps them avoid Failure — and ends in Success.
```

Every effective brand story contains all seven. Missing any one collapses the narrative.

## Element 1: A Character (the Hero)

### Discipline

The character is **the customer**, not the brand. This is the central inversion that most brands fail to perform.

The character clause has the form:
> *<Persona descriptor> wants <concrete want>.*

The want must be:
- Stated in the customer's vocabulary
- Concrete enough to visualize
- Singular (one dominant want, not three)

### Sources to draw from

- `target_persona` block in `brand-platform/handoff.yaml`
- The psychographic paragraph from the platform document
- Maslow layer placement from the platform document

### Failure modes

| Failure | Symptom | Fix |
|---|---|---|
| Brand-as-character | "Our brand wants to revolutionize…" | Replace with customer: "The independent consultant wants…" |
| Abstract want | "Customers want quality" | Replace with concrete want: "wants their daily coffee ritual to feel intentional" |
| Multiple wants | "Customers want speed, quality, and value" | Pick the dominant one |
| Persona drift | Hero doesn't match platform persona | Recheck platform persona; reconcile |

## Element 2: Has a Problem (three-layer analysis)

This is the most consequential element. See `three-layer-problem.md` for full treatment. Summary:

### External Problem

The observable obstacle in the world. What the customer says when asked, "what's the problem?"

Example for a specialty coffee brand: *"It's hard to find coffee that tastes the way it should — consistent, fresh, traceable, brewed with intention."*

### Internal Problem

The emotional frustration the external problem causes. What the customer feels but doesn't always articulate.

Example: *"The customer feels disappointed when they spend money on premium coffee that tastes ordinary, and they feel slightly foolish for having been promised something they didn't receive."*

### Philosophical Problem

The stance — the "why this is wrong in the world" position. The brand's broader critique of the category.

Example: *"Coffee — like everything else in modern life — has been industrialized to the point of mediocrity, and customers deserve to know who roasted their beans, where they came from, and why."*

### Use in BrandScript

The BrandScript surfaces all three layers, but the external + internal are the dominant communicative layers. The philosophical layer informs brand voice and shows up in long-form content (manifesto, founder letter, packaging copy).

## Element 3: Meets a Guide (the brand)

### Discipline

The brand enters as **Yoda, not Luke**. The brand has:
- Walked the path the customer is now on
- Acquired wisdom from the journey
- Is now generously sharing that wisdom

The guide demonstrates two qualities (Miller):

### Empathy

The brand shows it understands the customer's struggle from inside. Not "we see your pain" (which sounds clinical) but "we know this struggle because we've lived it."

Empathy statement examples:
- "We left corporate roasting because we saw what scale was doing to coffee."
- "We built this practice because we needed it ourselves and couldn't find it."
- "We started this brand for the customer we couldn't find a solution for — ourselves."

### Authority

The brand shows it has competence to help — credentials, methodology, evidence.

Authority sources:
- **Heritage**: founding date, lineage
- **Methodology**: documented approach, named system
- **Credentials**: certifications, qualifications, awards
- **Evidence**: customer outcomes, third-party validation
- **Founder credibility**: relevant expertise

Authority statement examples:
- "We've roasted 14 tons of single-origin beans across 11 years of practice."
- "Our 32 advisors have served on the boards of 47 venture-backed companies."
- "We've designed visual identities for 200+ brands across 28 countries."

### Failure modes

| Failure | Symptom | Fix |
|---|---|---|
| Empathy without authority | Brand seems caring but unproven | Add evidence of competence |
| Authority without empathy | Brand seems competent but cold | Add evidence of understanding |
| Brand-as-hero | Guide section reads as brand achievements parade | Reframe achievements as service to customers |

## Element 4: Who Gives Them a Plan

### Discipline

The customer does not know how to engage the brand without a plan. The plan reduces friction.

The plan has three steps. Each step:
- Concrete (the customer knows what to do)
- Sequential (step 2 follows step 1)
- Owned (the customer takes the action, not the brand)

### Two plan types

**Process plan**: shows the customer's journey
- Step 1: Get a free assessment
- Step 2: Receive a tailored proposal
- Step 3: Begin work in 14 days

**Agreement plan**: addresses customer's fears
- We respect your time
- We respond within 24 hours
- We honor your privacy

Most brands use process plans. Brands operating in fear-charged categories (health, finance, legal) often combine both.

## Element 5: And Calls Them to Action

### Discipline

Two CTAs are required:

**Direct CTA** — the explicit ask
- Buy now
- Schedule a consultation
- Sign up
- Contact us

**Transitional CTA** — the lower-commitment ask
- Read the field guide
- Download the white paper
- Get a free assessment
- Watch the case study

Direct CTAs convert customers ready to commit now. Transitional CTAs nurture customers not yet ready. Brands without both leave conversions on the table.

### Placement discipline

- Direct CTA: top of every page, end of every email, end of every conversation
- Transitional CTA: secondary placement, lead-magnet positioning, end-of-content nudge

## Element 6: That Helps Them Avoid Failure

### Discipline

What happens if the customer doesn't engage the brand? Three or four concrete consequences. These are NOT the brand bragging about superiority. These are honest portrayals of the cost of inaction or wrong choice.

### Failure stakes examples

For a specialty coffee brand:
- Continue paying premium prices for ordinary coffee
- Daily coffee ritual remains a missed opportunity for intentionality
- Support an industry that flattens craft into commodity

For a B2B consulting practice:
- Continue making decisions on incomplete information
- Lose competitive position while peers move faster
- Carry strategic blind spots that compound over time

### Failure modes

| Failure | Symptom | Fix |
|---|---|---|
| Catastrophizing | Stakes are wildly exaggerated | Calibrate to proportionality |
| Self-promotional stakes | Stakes are really brand bragging | Rewrite from customer's perspective |
| Abstract stakes | Stakes are vague | Make concrete and visualizable |

## Element 7: And Ends in Success

### Discipline

The transformation. The before/after picture. What does the customer's life look like once the problem is resolved?

The success state must be:
- **Concrete** — visualizable, not abstract
- **Believable** — proportionate to what the brand actually delivers
- **Emotionally resonant** — connects to the internal problem from Element 2

### Success examples

Bad (abstract): "Customers experience excellence."
Good (concrete): "Every morning, the customer reaches for their coffee with the same anticipation as for a good book — knowing exactly where the beans came from and tasting the deliberateness in each cup."

Bad (overpromising): "Our consulting transforms your entire industry."
Good (proportionate): "Within 90 days, the client makes their next three major decisions with research rigor they didn't have access to before."

### The transformation arc

The success state implicitly references the hero's starting position. The contrast is the transformation. A BrandScript without an implicit before/after lacks narrative force.

## The Single-Page BrandScript Document

The deliverable form is a single page (or a tightly composed page-and-a-half) presenting all seven elements as flowing prose with clear element markers. Format:

```
THE CUSTOMER who is [persona descriptor], wants [concrete want].

THE PROBLEM is [external problem]. This makes the customer feel [internal problem]. We believe [philosophical problem].

OUR BRAND has [authority evidence] and understands this struggle because [empathy evidence].

WE OFFER A PLAN: [Step 1]. [Step 2]. [Step 3].

YOU CAN [direct CTA] or [transitional CTA].

WITHOUT OUR BRAND, you risk: [failure stake 1], [failure stake 2], [failure stake 3].

WITH OUR BRAND, you experience: [success state in 1-2 sentences].
```

This single page is the most-referenced narrative artifact across the brand's life. Every employee should know it; every external storyteller should work from it.
