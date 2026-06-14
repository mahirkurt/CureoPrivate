# StoryBrand SB7 — Naming Brief Layer

Reference loaded by brand-maker when an upstream `brand-story/handoff.yaml` is present.

## How SB7 becomes a naming constraint

The BrandScript produced by brand-story contains seven elements (Character, Has-a-Problem, Meets-a-Guide, Who-Gives-Them-a-Plan, Calls-to-Action, Avoid-Failure, Ends-in-Success). Each constrains the name in a specific way.

### Character → name semantic territory

The Character clause describes the customer's want in their own vocabulary. The name should be parseable to this customer — using language patterns the customer would recognize as theirs.

If the Character is an "independent design consultant who treats craft as practice", names with overly tech-startup phonetic patterns (Zipify, Loomly) will jar. Names with craft / studio / heritage / classical phonetic patterns (Hearth, Atelier-derived, latinate) will resonate.

### Three-layer problem → name oppositional stance

The brand stands against something. The name can quietly encode the oppositional stance:

- Brand opposes "industrial mediocrity" → names evoking handmade, deliberate, specific
- Brand opposes "performative authenticity" → names that are themselves plain-spoken
- Brand opposes "status display" → names that don't perform their own status

The opposition shapes name affect. A name that visibly tries hard contradicts a brand whose stance is restraint.

### Meets-a-Guide → name authority register

The Guide combines empathy + authority. The name's authority register should match:

- Heritage authority → names referencing time, lineage, founder, place
- Technical authority → names with substantive, specific, definite qualities
- Craft authority → names referencing material, method, place
- Modern authority → names with confident, contemporary, definite qualities

A heritage-authority brand named in a contemporary-tech register signals confusion.

### Plan → name pronunciation friction

If the brand offers a three-step plan to reduce friction, the name itself should be low-friction. Easily pronounceable. Easily spelled from sound. Easily remembered.

A brand promising "frictionless setup" with a name customers can't pronounce contradicts its own promise.

### Calls-to-Action → name verb-adjacency

Names that lend themselves to verb construction (Slack > slacking; Zoom > zoom in/out) accelerate CTAs. Names with awkward verb forms slow CTAs.

Sometimes the brand wants verb-adjacency (consumer tools, frequent-use products). Sometimes the brand specifically doesn't (luxury, professional services where the name remains a noun, never an action).

### Failure stakes → name gravity calibration

Brands whose stakes are high (security, financial, healthcare-adjacent service, legal) need name gravity. Playful names undercut high-stakes positioning.

Brands whose stakes are low/fun (entertainment, snacks, lifestyle accessories) can afford lighter naming registers.

### Success transformation → name aspiration encoding

The success state suggests the affect the name should evoke. If the success state is "calm confidence", the name should feel calm + confident. If the success state is "delight in daily ritual", the name can feel light + ritualistic.

## Naming brief synthesis

From the BrandScript, brand-maker derives a synthetic naming brief:

```yaml
naming_brief_from_brandscript:
  semantic_territory: <derived from Character vocabulary>
  oppositional_stance: <derived from three-layer problem>
  authority_register: <derived from Meets-a-Guide>
  pronunciation_friction_target: low|medium|allowable_high
  verb_adjacency_desired: <yes|no|neutral>
  gravity_level: <playful|moderate|grave>
  affect_target: <derived from success transformation>
```

This synthetic brief becomes an additional constraint layer in brand-maker's 5-category brainstorm + SMILE+M Lab phases.

## Brandscript-to-name pattern table

| BrandScript signal | Naming bias |
|---|---|
| Customer is craft-affinity | Heritage names, founder names, place names, latinate roots |
| Customer is tech-savvy + ambitious | Confident coinages, geometric phonetics, definite qualities |
| Problem layer is "industrial mediocrity" | Handmade-evoking, specific, against-scale |
| Problem layer is "performative authenticity" | Plain-spoken, declarative, anti-aspirational |
| Guide authority = heritage | Founder names, classical forms, time references |
| Guide authority = technical | Substantive coinages, scientific roots, definite |
| Plan = frictionless | Short, pronounceable, memorable in 1 listen |
| Plan = considered methodology | Names with weight, can survive multi-syllable |
| Stakes = high (financial, security, legal) | Grave register, names with gravitas |
| Stakes = low (entertainment, lifestyle) | Light register, playful permissible |
| Success = calm confidence | Calm-sounding phonetics, restraint |
| Success = energetic transformation | Kinetic phonetics, sharp consonants |

## Anti-patterns

| Anti-pattern | Symptom |
|---|---|
| Name contradicts story | BrandScript opposes "industrial mediocrity"; name sounds like a Big Brand |
| Name fights customer voice | BrandScript Character speaks plain English; name is unpronounceable coinage |
| Wrong gravity | Stakes are high (finance, healthcare); name is playful |
| Verb-adjacency mismatch | Luxury brand picks verbifiable name; B2B SaaS picks awkward verb form |

When brand-maker's name candidates contradict the BrandScript, surface this back to brand-story for refinement — sometimes the story is right and the name should change; sometimes the story can absorb a less-obvious-fit name.
