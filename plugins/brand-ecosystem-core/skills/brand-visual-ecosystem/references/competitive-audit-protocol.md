# Competitive Visual Audit Protocol

Reference loaded when upstream brand-audit has produced a visual_white_space analysis. Operationalizes the visual side of competitive audit for brand-visual's 4-route exploration phase.

## How brand-visual consumes brand-audit output

When `brand-audit/handoff.yaml` is present, brand-visual reads:

```yaml
competitive_landscape:
  visual_white_space: [...]
  visual_character_per_competitor: [...]
```

These become constraints + opportunities for the 4-route strategic exploration.

## The visual_white_space layer

`visual_white_space` from brand-audit identifies unoccupied visual territories in the competitive set:

- **Color territory**: which colors / color combinations nobody owns
- **Typographic territory**: which type styles nobody owns
- **Logo type territory**: if everyone uses wordmarks, an emblem is white space
- **Imagery territory**: if everyone uses lifestyle photography, illustration is white space
- **Visual mood territory**: if everyone is clean/modernist, textured/handmade is white space
- **Form territory**: if everyone uses geometric forms, organic is white space
- **Compositional territory**: if everyone uses centered compositions, asymmetric is white space

## 4-Route strategic exploration informed by white space

Brand-visual's existing 4-route framework (Typographic / Geometric / Disruptor / Adaptive Living Identity) takes on different character when informed by competitive visual audit:

### Route 1 — Typographic
- If competitive set is mostly logomarks, typographic route is white space → strongly favored
- If competitive set is already typographic-dominant, the typographic route must differentiate within typography (different typography category, custom typography, or extreme typographic confidence)

### Route 2 — Geometric
- If competitive set is mostly organic / illustrative, geometric route is white space → strongly favored
- If competitive set is already geometric-dominant, geometric route must differentiate within geometry (different geometric family, unique geometric relationship, geometric system rather than single mark)

### Route 3 — Disruptor
- The disruptor route inherently seeks opposition to convention
- Read competitive convention carefully — disruption only registers against established convention
- If the entire category is already "disruptor-aesthetic" (some fashion and creative agency categories), the disruptor route may be no longer disruptive

### Route 4 — Adaptive Living Identity
- Less category-convention-dependent
- Selection depends on brand attributes (digital-native, multi-context, multi-stakeholder) rather than white space

## Per-competitor visual character analysis

From `brand-audit.competitive_landscape.direct_competitors`, brand-visual reads per-competitor visual character:

```yaml
direct_competitors:
  - name: <competitor>
    visual_character:
      logo_type: wordmark|logomark|emblem|monogram|abstract|pictorial
      color_palette: <descriptor>
      typography: <style descriptor>
      imagery_style: <descriptor>
      overall_visual_mood: <descriptor>
```

For each competitor, brand-visual maps:
- Where competitor occupies visual territory
- What competitor signals about category convention
- Where competitor leaves white space

## Visual differentiation strategy

After reading the white space + per-competitor analysis, brand-visual produces a differentiation strategy:

### Conformity-divergence calibration

For each visual dimension, declare brand's stance:

| Dimension | Brand's stance |
|---|---|
| Logo type | Conform to category convention / Diverge |
| Color palette | Conform / Diverge |
| Typography | Conform / Diverge |
| Imagery | Conform / Diverge |
| Visual mood | Conform / Diverge |
| Form language | Conform / Diverge |

A brand that conforms on every dimension is invisible in the category. A brand that diverges on every dimension may be hard to parse. The strategy is selective divergence — conform on some dimensions (to remain category-legible), diverge on others (to be distinctive).

The competitive visual audit informs which dimensions to diverge on.

### Differentiation depth

How far to diverge?

- **Subtle differentiation**: same logo type as competitors, but distinctive execution
- **Moderate differentiation**: different logo type than dominant competitors
- **Strong differentiation**: visually opposite the category convention
- **Category-creation differentiation**: visual language unprecedented in category

Selection depends on positioning strategy from brand-platform. A brand positioning as "considered alternative" generally chooses moderate to strong differentiation. A brand positioning as "credible new entrant" often chooses subtle to moderate.

## Visual differentiation as brand-visual output extension

When upstream brand-audit is present, brand-visual outputs add:

### Competitive visual map
A text-described map showing:
- Competitive set's visual positions (logo type × color territory × typographic style × imagery style × mood)
- Brand's intended visual position
- White space being claimed

### Differentiation strategy declaration
Per visual dimension:
- Brand's stance (conform / diverge)
- Rationale
- Risk

### Route selection rationale
The selected route (1/2/3/4) explained in competitive terms:
- Why this route works given the competitive landscape
- What white space it claims
- What category convention it diverges from

## Anti-patterns

| Anti-pattern | Symptom | Remedy |
|---|---|---|
| Differentiation-blind | Visual identity ignores competitors | Read brand-audit handoff competitive_landscape |
| Reactive differentiation | Brand defines self purely in opposition | Differentiate where it serves positioning, conform where it serves category-legibility |
| Hollow differentiation | Different colors but same everything else | Real differentiation across multiple dimensions |
| Stale audit | Visual identity built from out-of-date competitive audit | Refresh competitive audit before brand-visual |
| Imitation justified as conformity | Brand looks like dominant competitor | Conformity is conscious; imitation is failure |
