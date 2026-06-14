# Brand Asset Audit Methodology

Mandatory reference loaded at Step 0. Operationalizes Wheeler's brand asset inventory framework.

## The asset inventory thesis

Before designing what the brand will become, document what it is. The brand asset inventory is the unsentimental catalog of everything the brand currently has — visual, verbal, strategic, operational. Each asset receives an assessment: **Keep / Evolve / Retire**.

This produces decision-readiness: the rebrand team knows what to preserve (carrying brand equity forward), what to evolve (preserving recognition while modernizing expression), and what to retire (cutting losses on weak assets).

## Asset categories

### Visual assets

**Logos and marks**:
For each logo variant, document:
- File format availability (vector, raster, fonts embedded)
- Resolution range (favicon to billboard)
- Color variants (full color, single color, knockout, reversed)
- Lockup variations (horizontal, stacked, tagline-included)
- Usage history (where it appears, how long it's been in use)
- Trademark status (registered, applied, common law only)
- Assessment: Keep / Evolve / Retire

**Color palette**:
- Primary colors (hex, RGB, CMYK, Pantone if specified)
- Secondary palette
- Functional colors (success, warning, error)
- Color history (how long this palette has been in use)
- Color recognition assessment (does the audience associate these colors with the brand?)
- Assessment per color: Keep / Evolve / Retire

**Typography**:
- Primary typeface (designer, foundry, license type)
- Secondary typeface
- Display/decorative faces
- Web fonts (if different from print)
- Typography hierarchy (sizes, weights, leading conventions)
- Custom typography (if any)
- Assessment: Keep / Evolve / Retire

**Iconography**:
- Custom icon library (if exists): style, count, format
- UI icons (if differentiated)
- Decorative icons
- Assessment: Keep / Evolve / Retire

**Photography style**:
- Style guide (if exists)
- Photo library (size, organization, recency)
- Lighting/composition conventions
- Subject conventions (people, products, contexts)
- Assessment: Keep / Evolve / Retire

**Illustration system**:
- Style guide (if exists)
- Library size and recency
- Use cases (editorial, packaging, marketing)
- Assessment: Keep / Evolve / Retire

### Verbal assets

**Brand name(s)**:
- Legal entity name vs trade name
- Variants by market (if multi-language brand)
- Trademark registration by jurisdiction and class
- Assessment: Keep / Evolve / Retire

**Taglines**:
- Current tagline
- Historical taglines (if reuse considered)
- Tagline use patterns (where it appears, lockup with logo or independent)
- Assessment: Keep / Evolve / Retire

**Boilerplate copy**:
- About paragraph (standard length variants: 25-word, 50-word, 100-word)
- Mission/vision statements
- Brand story (long-form narrative)
- Assessment: Keep / Evolve / Retire

**Voice guidelines (if exist)**:
- Documented? Where?
- Adopted in practice?
- Assessment: Keep / Evolve / Retire

### Strategic assets

**Brand platform document (if exists)**:
- Vision, mission, values
- Positioning statement
- Brand promise
- Personality framework
- Currency: when last updated
- Adoption: actively referenced or shelf document?
- Assessment: Keep / Evolve / Retire

**Brand guidelines document**:
- Existence, completeness
- Format (PDF, online, both)
- Recency
- Adoption (used by internal teams, used by external partners)
- Assessment: Keep / Evolve / Retire

**Customer research**:
- Quantitative studies on file (segmentation, brand tracking, etc.)
- Qualitative research (focus groups, ethnography, in-depth interviews)
- Currency: dated within 18-24 months?
- Use: actively referenced or filed away?
- Assessment: Keep / Evolve / Retire / Re-commission

**Market positioning analyses**:
- Internal analyses
- External (consultant or agency-produced)
- Recency
- Assessment: Keep / Evolve / Retire

### Operational assets

**Trademark portfolio**:
For each registered trademark:
- Mark
- Jurisdiction
- Class(es) covered
- Registration date
- Expiration / renewal date
- Status (active, pending, lapsed)
- Use evidence

**Domain portfolio**:
- Primary domain
- Defensive registrations (variants, common misspellings, geographic TLDs)
- Subdomain structure
- DNS health (if applicable)

**Social media handles**:
- Platforms with brand handle
- Handle consistency across platforms (same handle? close variants?)
- Account verification status

**Brand center / online asset library**:
- Existence
- Platform (DAM, internal wiki, file share)
- Asset accessibility (who can access, how)
- Asset currency (latest versions present)

## The Keep / Evolve / Retire framework

For every asset, apply the three-option assessment:

### Keep

The asset is performing strategically and aesthetically. It should carry forward unchanged.

Criteria:
- Asset has strong recognition in target audience
- Asset aligns with intended brand positioning
- Asset is technically current (file formats, scalability)
- No legal risks attached

### Evolve

The asset has equity that should be preserved, but the current expression needs modernization.

Criteria:
- Audience recognition is real but the asset's execution has aged
- Strategic intent is sound but expression has drifted
- Technical implementation needs updating
- The asset's "DNA" should survive in a new form

Evolve assessments produce design briefs for downstream brand-visual work.

### Retire

The asset should be discontinued.

Criteria:
- Asset doesn't serve current strategy
- Asset confuses or contradicts other brand elements
- Asset's recognition is weak or non-existent
- Asset has legal risks
- Asset's continued use blocks better choices

Retire decisions require careful sequencing — assets with audience recognition need migration plans, not abrupt removal.

## Decision support framework

When the assessment is ambiguous (a strong case for both Keep and Evolve), use these tiebreakers:

1. **Recognition test**: Show the asset to 10 target-persona representatives. Can they identify it as the brand? Recognition strong → lean Keep. Recognition weak → lean Evolve or Retire.

2. **Strategic alignment test**: Does the asset support the positioning the brand intends to claim? Yes → Keep or Evolve. No → Retire.

3. **Modernization cost test**: How much investment to evolve vs replace? Low cost to evolve → Evolve. High cost to evolve → Retire and rebuild.

4. **Sentimental attachment test**: Is the team resisting Retire because of emotional attachment rather than strategic merit? If yes, lean Retire harder.

## Output format

The asset inventory section of the findings report uses tabular structure:

```markdown
## 1. Brand Asset Inventory

### 1.1 Visual Assets

| Asset | Description | Current condition | Assessment | Rationale |
|---|---|---|---|---|
| Primary logo | Custom wordmark, 2018 | Strong recognition, dated execution | Evolve | Preserve wordmark concept, modernize letterforms |
| Logomark | Abstract symbol, 2018 | Weak recognition | Retire | Audience doesn't associate it with brand |
| Color palette — primary | Deep blue + warm orange | Strong recognition | Keep | Distinctive in category |
| Color palette — secondary | Five-color extended palette | Inconsistent application | Evolve | Reduce to three colors |
| Primary typeface | Custom commission, 2018 | Adequate, costly to license | Evolve | Replace with available alternative |

### 1.2 Verbal Assets
[Same tabular format]

### 1.3 Strategic Assets
[Same tabular format]

### 1.4 Operational Assets
[Same tabular format]

### 1.5 Summary
- Assets to Keep: <count>
- Assets to Evolve: <count>
- Assets to Retire: <count>

### 1.6 Migration considerations
[Paragraph: which Retire decisions require migration plans, sequencing, communication.]
```

## Anti-patterns

| Anti-pattern | Symptom | Remedy |
|---|---|---|
| Universal Keep | Inventory marks everything as Keep | Apply pressure — assessment must distinguish |
| Universal Retire | Inventory marks everything as Retire | Equity is being underestimated; audit recognition |
| Missing operational assets | Only visual + verbal cataloged | Add IP, domain, social handle inventory |
| Stale inventory | Inventory months out of date | Re-confirm before passing to brand-platform |
| Vague assessment | Keep/Evolve/Retire without rationale | Force rationale per asset |
