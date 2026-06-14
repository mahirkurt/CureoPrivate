# task-comparison-defense.md

**T6 Head-to-Head — Sponsor-Specific Competitive Defense Sub-Mode (v1.9.0)**

> **CRITICAL SCOPE NOTE:** This sub-playbook is the **single permitted exception** to the generic-by-default discipline established in v1.7.0 (`generic-by-default.md`). It is invoked ONLY when the user explicitly requests sponsor-specific competitive defense framing — never by inference, never by user-identity matching, never by semantic auto-trigger.
>
> **Activation requires both:**
> 1. Explicit query content invoking sponsor-specific perspective (see §1 trigger language)
> 2. Mandatory triple-disclosure in Provenance section (see §6)
>
> **Activation produces:**
> - Selective G22 override (2-of-8: G22.4 + G22.7) within §Strategic Implications block ONLY
> - All other 6 G22 checks remain in force
> - Mandatory symmetric framing: parallel "from competitor's perspective" section
> - G24 gate audit ensures the override is well-formed

---

## §1. Activation Triggers (EXPLICIT ONLY)

### 1.1 Permitted query-content triggers

T6-Defense activates ONLY when query contains:
- Explicit sponsor-perspective language: "**[Sponsor X] cephesinden [Asset/Threat Y] analizi**", "**[Sponsor X] için competitive defense pozisyonu**", "**[Sponsor X]'s perspective on [Asset Y]**", "**from [Sponsor X]'s perspective**", "**defense playbook for [Sponsor X]**"
- Explicit task tag prefix: "T6-Defense: [Sponsor X] vs [Sponsor Z]'s [Asset Y]"
- Explicit competitive defense framing: "biz X şirketiyiz, Y bizim asset'imize tehdit, defense önerisi ver" (with explicit "biz X" naming)

### 1.2 FORBIDDEN as triggers

- ❌ User employer inferred from memory (per generic-by-default.md Article 5)
- ❌ User location proxy ("Sen Türkiye'de Roche'tasın → defense Roche için")
- ❌ User specialty proxy ("Sen onkologsın → defense tüm onkoloji asset'leri için")
- ❌ Semantic match without explicit sponsor naming ("market leader analysis" ≠ defense for market leader)
- ❌ Generic competitive analysis question ("X vs Y nasıl rekabet ediyor" → standard T6, NOT T6-Defense)

If trigger ambiguity exists, default to standard T6 (sponsor-agnostic). Never assume T6-Defense.

### 1.3 Asymmetric vs symmetric query handling

| Query type | Mode |
|---|---|
| "X vs Y nasıl rekabet eder" | Standard T6 (sponsor-agnostic) |
| "X için defense önerisi" (sponsor named) | T6-Defense for X |
| "X için defense önerisi, Y de bu market'te oyuncu" | T6-Defense for X **with mandatory parallel Z perspective** if Z named |
| "X cephesinden Y'ye karşı" (both sponsors named) | T6-Defense for X with **mandatory parallel Y perspective** |

---

## §2. Selective G22 Override Pattern

### 2.1 What gets overridden

Within the report's §Strategic Implications block ONLY, the following G22 checks are programmatically overridden via `# T6-DEFENSE:` annotations:

| G22 Check | Override scope | Reason |
|---|---|---|
| **G22.4** (No sponsor-specific strategic action) | OVERRIDE within §Strategic Implications | Defense recommendations ARE sponsor-specific by design |
| **G22.7** (Scope note not employer-aligned) | OVERRIDE if scope note explicitly declares defense framing | "This report frames analysis from [Sponsor X]'s perspective per user request" — methodologically necessary |

### 2.2 What does NOT get overridden

| G22 Check | Status in T6-Defense |
|---|---|
| G22.1 (User name not in body) | **PRESERVED** — never address user by name in body |
| G22.2 (User employer not in body unless query mentions) | **PRESERVED** — sponsor in body is OK because it's IN THE QUERY |
| G22.3 (No auto-trigger user-identity rationale) | **PRESERVED** — auto-trigger logic remains query-content-based |
| G22.5 (Intended use sponsor-agnostic) | **PRESERVED** — Provenance intended audience remains generic |
| G22.6 (No coverage anchor asymmetry) | **PRESERVED** — coverage discipline remains positive-list |
| G22.8 (Disclosure free of user-context) | **PRESERVED** — disclosure references methodologically required only |

### 2.3 Annotation syntax

In report markdown:

```
# T6-DEFENSE: §X.Y Strategic Implications — sponsor-specific defense recommendations for [Sponsor X]
# T6-DEFENSE: G22.4 — Strategic action recommendations directed at [Sponsor X] per explicit user request invocation; methodologically required for T6-Defense scope
# T6-DEFENSE: G22.7 — Scope note explicitly framed from [Sponsor X]'s perspective per user request; symmetric parallel [Sponsor Z] perspective section also present at §X.Z
```

Annotations are picked up by `validate-report-discipline.py --accept-overrides` (v1.7.1+ mechanism, extended in v1.8.0 to recognize `T6-DEFENSE:` as a special override class beyond `G22-OVERRIDE:`).

---

## §3. Mandatory Symmetric Framing

When T6-Defense is invoked for Sponsor X against Asset Y (developed by Sponsor Z), the report MUST include:

### 3.1 Three required sections

**Section A — Standard sponsor-agnostic competitive landscape** (§5.X-style)
- Names X, Y, Z symmetrically as actual sponsors of their products
- No strategic action recommendations
- Standard T6 head-to-head efficacy/safety/payer comparison
- Generic incumbent-vs-entrant abstract framing

**Section B — From [Sponsor X]'s strategic perspective** (NEW in T6-Defense)
- Defensive moves available to X
- Asset position vulnerabilities to leverage
- Specific competitive defense recommendations
- Annotated with `# T6-DEFENSE:` annotations

**Section C — From [Sponsor Z]'s strategic perspective (parallel)** (MANDATORY symmetric)
- Offensive moves available to Z
- Z's natural advantages over X
- Specific competitive offensive recommendations  
- Same level of analytical rigor as Section B
- Annotated with `# T6-DEFENSE:` annotations

### 3.2 Why parallel Z section is non-negotiable

If T6-Defense renders only the X-perspective section, the report becomes one-sided sponsor advocacy — a marketing or financial promotion document, not pharmaintel. Mandatory parallel framing:
- Preserves analytical neutrality
- Forces honest competitive assessment (X's vulnerabilities are also stated)
- Enables both audiences (X-team AND Z-team) to use the report
- Aligns with ethical standards for competitive intelligence

### 3.3 Exception to symmetric requirement

If Z is not explicitly named in query (rare — possible in pure "defend X's market position" queries with abstract competitor):
- Section B = "From X's perspective"
- Section C = "From abstract entrant/disruptor perspective" (using stakeholder categories per generic-by-default Article 3.2)

This preserves symmetric framing requirement even when one side is abstract.

---

## §4. Output Structure

T6-Defense report sections are assembled as:

```
[standard T6 frontmatter — report_type, scope_note, etc.]

§Auto-Trigger Disclosure (G17)
- Standard sub-protocols loaded
- T6-Defense activated: "explicit user query content"
- Sponsor X named: [extract from query]
- Competitor Z named (if applicable): [extract from query]

§Executive Summary (3-5 sentences, sponsor-agnostic)

§1-4 Standard analytical sections (sponsor-agnostic)
- Identity, mechanism, regulatory status, clinical, label

§5 Competitive Position — Standard Section A (sponsor-agnostic)
- All sponsors named symmetrically
- Standard T6 comparison

§6 Commercial Trajectory (sponsor-agnostic)

§7 Payer & HTA Landscape (sponsor-agnostic)

§8 IP Position (sponsor-agnostic)

§9 Near-Term Catalysts (sponsor-agnostic)

§10 Strategic Implications — DEFENSE FRAMING (T6-Defense activated)

  §10.A Standard sponsor-agnostic implications
    (abstract stakeholder categories per generic-by-default Article 3.2)

  §10.B From [Sponsor X]'s perspective
    # T6-DEFENSE annotations
    Defense recommendations specific to X
    
  §10.C From [Sponsor Z]'s perspective (mandatory parallel)
    # T6-DEFENSE annotations
    Offensive recommendations specific to Z

§11 Limitations & Gaps

§12 Triangulation Notes

§Sponsor Sweep Disclosure

§Confidence Disclosure

§Provenance Disclosure (with mandatory triple T6-Defense disclosure per §6 below)
```

---

## §5. Strategic Implications Section Discipline

### 5.1 Format requirements for §10.B and §10.C

Each defense/offense recommendation must include:
- **Action category** (e.g., "Defensive niche maintenance", "Pricing pressure", "Combination clinical study", "Real-world evidence generation")
- **Specific action** (concrete, evidence-backed)
- **Source rationale** (which clinical/regulatory/payer fact justifies action)
- **Time horizon** (next 6 months / 12 months / 3 years)
- **Evidence base for assessment** (cite report sections that support the recommendation)

### 5.2 Format example (good)

> **§10.B.1 Defensive niche maintenance — [Sponsor X]**
> 
> *Action category:* Indication-specific market preservation
> 
> *Specific action:* Reinforce 2L positioning of [Asset Y2] via head-to-head trial against [Asset Z] in chemo-naive subset; prioritize 12-month enrollment.
> 
> *Source rationale:* Per §3.1 pivotal trial data, [Asset Y2] retains favorable HR vs chemo in pre-treated patients; per §5.1 NCCN guidelines, 2L positioning is contested.
> 
> *Time horizon:* 12-18 months (trial initiation to readout)
> 
> *Evidence base:* §3.1 pivotal data, §5.1 NCCN, §5.3 emerging competitor pipeline analysis

### 5.3 Format example (BAD — what NOT to do)

> **§10.B.1 Strategy:** [Sponsor X] should attack [Sponsor Z] aggressively in 2L. ❌

This is too vague; lacks evidence rationale; sounds like marketing copy. Reject.

### 5.4 Forbidden patterns even in T6-Defense

Even with T6-Defense activated, the following remain forbidden:
- ❌ Direct user address in body ("Sayın [User], [Sponsor X] için defense önerisi...")
- ❌ User employer name OUTSIDE the explicitly-named-in-query sponsor
- ❌ Investment thesis language ("Buy [Sponsor X] stock based on this analysis")
- ❌ Promotional/marketing tone ("[Sponsor X]'in üstün etkinliği...")
- ❌ Disparagement of competitor ("[Sponsor Z]'nin başarısız asset'i...")

T6-Defense provides analytical defense framing, not promotional or financial advisory output.

---

## §6. Mandatory Triple Disclosure (Provenance)

Every T6-Defense report's §Provenance Disclosure section MUST include:

```markdown
**T6-Defense activation disclosure (per task-comparison-defense.md §6):**

- Mode: T6 Head-to-Head with Sponsor-Specific Defense Framing
- Activation source: [Direct quote of user query language that triggered T6-Defense]
- Sponsor for defense framing: [Sponsor X full name]
- Competitive target asset(s): [Asset Y from Sponsor Z]
- Sections with sponsor-specific framing: §10.B ([Sponsor X] perspective), §10.C ([Sponsor Z] perspective — mandatory symmetric)
- Sections that remain sponsor-agnostic: §0-9, §10.A, §11, §12, all disclosure blocks except this T6-Defense annotation
- G22 audit: [N]/8 PASS, 2 OVERRIDE (G22.4 + G22.7) within §10.B and §10.C only
- G24 audit (T6-Defense well-formedness): [PASS/FAIL with rationale]
- This report includes sponsor-specific competitive intelligence per explicit user request and is NOT promotional material, financial advice, or substitute for professional regulatory/clinical/financial counsel.
```

This disclosure is **mandatory** — without it, T6-Defense activation is invalid and report fails G24 audit.

---

## §7. G24 Gate Audit (T6-Defense well-formedness)

The G24 gate verifies T6-Defense compliance with 6 checks:

| G24 Check | Pass criterion |
|---|---|
| **G24.1** | Activation source explicitly cited in Provenance §T6-Defense activation disclosure |
| **G24.2** | At least one of the explicit query-content triggers (per §1.1) is present in the cited activation source |
| **G24.3** | §10.B [Sponsor X perspective] section present and annotated with `# T6-DEFENSE:` |
| **G24.4** | §10.C [Sponsor Z perspective] section present (symmetric framing requirement per §3) — OR explicit abstract-competitor framing if Z not named in query |
| **G24.5** | §10.A standard sponsor-agnostic implications section present (preserved generic-by-default discipline outside §10.B/§10.C) |
| **G24.6** | All other report sections (§0-9, §11, §12, disclosure blocks) remain sponsor-agnostic per `generic-by-default.md` |

If any G24 check fails, the T6-Defense activation is malformed and report cannot be delivered. Either fix the issue OR fall back to standard T6 mode (sponsor-agnostic).

---

## §8. Validator Integration

`scripts/validate-report-discipline.py` v1.9.0+ recognizes two override classes:

```bash
# Standard G22 override (existing v1.7.1+):
# G22-OVERRIDE: G22.X — rationale

# T6-Defense override (new v1.9.0):
# T6-DEFENSE: G22.X — rationale (within §10.B or §10.C only)
```

Validator behavior:
- `--accept-overrides` flag honors BOTH override classes
- T6-DEFENSE overrides are restricted to G22.4 and G22.7 only (validator rejects T6-DEFENSE attempts to override other checks)
- Validator counts T6-DEFENSE overrides separately in JSON output (`t6_defense_overrides` field)
- New `--enforce-g24` flag runs the 6 G24 well-formedness checks (introduced in v1.9.0; see §7)

When T6-Defense is invoked, the standard validator command becomes:

```bash
python3 scripts/validate-report-discipline.py REPORT.md \
  --user-name "..." --user-employer "..." --query "..." \
  --accept-overrides --enforce-g24 \
  --json
```

---

## §9. Worked Example Skeleton

```markdown
---
report_type: T6 Head-to-Head (Sponsor-Specific Defense Mode)
subject: [Asset Y2 from Sponsor X] vs [Asset Y from Sponsor Z]
data_cutoff: 2026-04-15
pharmaintel_version: 1.9.0
t6_defense_mode: enabled
t6_defense_sponsor: [Sponsor X]
t6_defense_competitor: [Sponsor Z]
---

# [Asset Y2] vs [Asset Y] — Head-to-Head Sponsor-Specific Defense Analysis

[standard frontmatter, scope note, executive summary — all sponsor-agnostic]

## §1-§4 Standard analytical sections [sponsor-agnostic]

## §5 Competitive Position [sponsor-agnostic Section A]

[symmetric naming of all sponsors as product owners; no recommendations]

## §6 Commercial Trajectory [sponsor-agnostic]

## §7 Payer & HTA Landscape [sponsor-agnostic]

## §8 IP Position [sponsor-agnostic]

## §9 Near-Term Catalysts [sponsor-agnostic]

## §10 Strategic Implications

### §10.A Standard sponsor-agnostic stakeholder analysis
[Abstract stakeholder categories: incumbent franchise sponsors, late entrants, payers, patients]

### §10.B From [Sponsor X]'s perspective
# T6-DEFENSE: §10.B Strategic Implications — sponsor-specific defense recommendations for [Sponsor X]
# T6-DEFENSE: G22.4 — Strategic action recommendations directed at [Sponsor X] per explicit user request
# T6-DEFENSE: G22.7 — Scope note framing from [Sponsor X]'s perspective; symmetric §10.C [Sponsor Z] section also present

[Defense recommendations with §5.1 format requirements]

### §10.C From [Sponsor Z]'s perspective (mandatory parallel)
# T6-DEFENSE: §10.C Strategic Implications — sponsor-specific offensive recommendations for [Sponsor Z]
# T6-DEFENSE: G22.4 — Strategic action recommendations directed at [Sponsor Z] per symmetric framing requirement
# T6-DEFENSE: G22.7 — Scope note framing from [Sponsor Z]'s perspective; mandatory parallel to §10.B

[Offensive recommendations with §5.1 format requirements]

## §11 Limitations & Gaps [sponsor-agnostic]

## §12 Triangulation Notes [sponsor-agnostic]

## Sponsor Sweep Disclosure [sponsor-agnostic]

## Confidence Disclosure [sponsor-agnostic]

## Provenance Disclosure

[Standard provenance + mandatory T6-Defense triple disclosure per §6]
```

---

## §10. Integration with parent task and other sub-protocols

T6-Defense is compatible with:
- **sub-protocol-label.md** (label disciplines apply to all asset references)
- **sub-protocol-sponsor-sweep.md** (sweep documents both X and Z sponsors with full disclosure rigor)
- **sub-protocol-pmda.md / sub-protocol-nmpa.md / sub-protocol-turkey.md** (regional layers apply if asset has presence in those geographies)
- **sub-protocol-catalyst-watch.md** (catalysts factored into §10.B / §10.C time horizon analysis)
- **task-hta.md** (HTA analysis applies to all assets compared)

T6-Defense is INCOMPATIBLE with:
- T1 Company Deep-Dive (different task scope; for company-level competitive defense use T6-Defense with company asset portfolio comparison)
- T7 Regulatory Status Snapshot (snapshot scope too narrow for defense framing)
- T8 Pipeline Inventory (inventory scope; use T6-Defense if specific asset comparison needed)

---

## §11. Versioning & changelog

- **v1.9.0 (2026-04-15):** Initial public release. Single permitted exception to generic-by-default.md discipline. Activation requires explicit query-content trigger (no semantic auto-trigger). Selective 2-of-8 G22 override (G22.4 + G22.7) within §10.B and §10.C only. Mandatory symmetric framing (§10.B AND §10.C parallel sections required) — both Sponsor X perspective AND comparator Sponsor Z perspective must be rendered, preserving analytical neutrality and forcing honest competitive assessment of both sides. Mandatory triple-disclosure in Provenance section (activation source verbatim quote + sponsor identification + competitor identification + section scoping + G24 audit declaration). New manifest gate G24 (6-check well-formedness audit covering activation source citation, query-content trigger presence, §10.B + §10.C presence, §10.A baseline preservation, sponsor-agnostic sections outside §10.B/§10.C). Validator extension: `# T6-DEFENSE:` annotation class (parallel to existing `# G22-OVERRIDE:`) + `--enforce-g24` flag. Compatible with all existing sub-protocols (label, sponsor-sweep, pmda, nmpa, turkey, catalyst-watch). Worked example skeleton provided in §9.
