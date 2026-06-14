# Personality Frameworks — Extended for brand-maker

Extension reference complementing brand-maker's existing personality material. Mirrors the three-layer composite from brand-platform's `personality-frameworks.md` and adds the archetype-driven naming bias matrix.

## Three-layer composite restated

For brand-maker's purposes, the personality profile from brand-platform/handoff.yaml arrives as:

```yaml
brand_personality:
  jung_primary: <archetype>
  jung_secondary: <archetype|null>
  aaker_5d:
    sincerity: 0-10
    excitement: 0-10
    competence: 0-10
    sophistication: 0-10
    ruggedness: 0-10
  voice_traits: [trait1, trait2, trait3]
```

Each layer biases naming differently.

## Archetype-driven naming bias matrix

| Archetype | Naming territories favored | Naming territories disfavored | Phonetic tendency |
|---|---|---|---|
| Sage | Substantive coinages, latinate roots, scholarly references | Playful, kinetic, performative | Open vowels, considered consonants |
| Outlaw | Declarative, oppositional, blunt, sometimes invented | Heritage, classical, polite | Hard consonants, percussive |
| Creator | Maker-references, craft-references, place-references | Generic, evasive, mass-market | Mid-range syllables, distinctive |
| Hero | Strong, active, declarative, sometimes verb-derived | Passive, decorative, abstract | Bold consonants, forward motion |
| Caregiver | Warm, human, relationship-suggestive | Cold, technical, distant | Soft consonants, embracing vowels |
| Magician | Transformative-suggestive, evocative, sometimes alchemical | Plain, descriptive, literal | Atmospheric, often invented |
| Everyman | Familiar, accessible, relatable | Pretentious, exclusive, jargon | Mid-range, conversational |
| Lover | Sensual, intimate, sometimes founder-name | Clinical, declarative, harsh | Soft, lingering |
| Jester | Playful, kinetic, sometimes invented or punning | Grave, considered, restrained | Sharp, percussive, irregular |
| Ruler | Authoritative, founder names, heritage references | Casual, playful, ephemeral | Substantive, classical |
| Innocent | Clean, simple, sometimes nature-references | Layered, complex, sophisticated | Open, simple |
| Explorer | Outdoor, geographic, journey-suggestive | Domestic, stationary, decorative | Rugged, sometimes outdoor-evoking |

When upstream platform's archetype is Sage + secondary Magician, brand-maker biases name candidates toward substantive coinages with evocative quality — Latinate roots that transform when said aloud. When archetype is Outlaw + secondary Creator, brand-maker biases toward declarative, maker-referential, sometimes oppositional names.

## Aaker 5-D as naming polygon

Aaker scores add granularity within an archetype:

- High Sincerity → names with warmth, plain-spoken character
- High Excitement → names with energy, often invented or kinetic
- High Competence → names with substance, often classical roots
- High Sophistication → names with restraint, often founder or heritage
- High Ruggedness → names with material weight, often outdoor

A brand scoring Magician archetype + high Sophistication + high Competence (luxury wellness brand) generates name candidates that differ sharply from Magician archetype + high Excitement + high Ruggedness (adventure tech brand) — even though they share the archetype.

## Voice traits as naming filter

The 3-5 voice traits act as final naming filter. After candidates pass archetype + Aaker filters, run them against voice traits:

- A "curious, plainspoken, generous" brand candidate name should feel curious, plainspoken, generous when said. Names that feel showy, evasive, or stingy fail this filter regardless of archetype fit.

## Bilingual personality considerations

Personality registers don't translate 1:1 across languages:

- A "warm + authoritative" register in EN may need different phonetic strategy in TR
- TR-pronunciation of name candidates must preserve personality register
- Test name candidates in both languages: does the personality survive pronunciation in each?

This is critical for TR-market brands using non-Turkish coined names — the personality must work when a Turkish speaker reads the name.

## Compositional rule

When upstream platform handoff is present:

1. Read jung_primary + jung_secondary → set archetype territory
2. Read aaker_5d → refine territory with personality granularity
3. Read voice_traits → set final filter
4. Run brand-maker's standard SMILE+M Lab + naming brainstorms within this constrained territory
5. Final candidates pass through voice-traits filter before presentation to user

This ensures every name candidate brand-maker presents is upstream-coherent.
