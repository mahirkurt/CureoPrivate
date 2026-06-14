# pharmaintel — T6: Head-to-Head Comparison Playbook

## Scope

Competitive benchmarking between two or more assets in the same or overlapping indication. Produces a structured comparison covering efficacy, safety, dosing/administration, regulatory standing, payer positioning, and commercial trajectory. Often requested by medical affairs (positioning preparation) or BD teams (asset scouting).

## Deliverable structure

```
# [Asset A] vs [Asset B] [vs ...] — Head-to-Head Comparison

## 0. Comparison frame
  - Indication in scope (exact NCCN / ESMO / label wording)
  - Patient population overlap (full, partial, distinct)
  - Line of therapy
  - Comparator choice rationale

## 1. Identity table
  | Attribute | Asset A | Asset B |
  | INN / brand / target / sponsor / modality / first approval / current indications |

## 2. Efficacy
  ### 2.1 Direct head-to-head trials (if any)
  ### 2.2 Pivotal trials (indirect)
  ### 2.3 Indirect comparison caveats (ITC / MAIC availability)

## 3. Safety
  ### 3.1 Label comparison (boxed warnings, Grade ≥3 common AEs)
  ### 3.2 Post-marketing signals (FAERS disproportionality where relevant)

## 4. Dosing & administration
  - Schedule, route, premedication, monitoring
  - Patient convenience / feasibility

## 5. Regulatory status comparison
  - FDA indications side-by-side
  - EMA indications side-by-side
  - Accelerated approval / full approval
  - Post-marketing requirements

## 6. Payer / HTA positioning
  - NICE / ICER / CADTH / PBAC: any comparative assessment
  - Published cost-effectiveness (if any)

## 7. Commercial positioning
  - Reported sales, launch trajectory
  - Market share (if available from class-level reports)

## 8. Pipeline evolution
  - Indication-expansion trials for each
  - Next-generation assets from same sponsor

## 9. Differentiation summary
  - Where each asset's evidence is strongest
  - Where each asset's evidence is weakest
  - Unresolved comparative questions

## 10. Limitations & gaps
```

---

## Phase 1 — Comparison frame (critical step)

Before any search, explicitly define:
- **Population:** exact NCCN/ESMO/label wording. E.g., "relapsed/refractory DLBCL after ≥2 prior lines of systemic therapy"
- **Line of therapy:** 1L / 2L / 3L+
- **Comparator group:** e.g., "BCMA-directed therapies in MM post-4L" = CAR-T + bispecifics + ADC collapsed; "CAR-T in MM post-4L" narrower
- **Direct vs indirect:** is there a head-to-head trial? If not, the analysis is indirect and requires ITC disclaimer

Without explicit framing, comparisons become apples-to-oranges. Document frame decisions in §0.

---

## Phase 2 — Discovery

For each asset: load `task-asset.md` Phase 2 + 3 steps (asset profiling).

Additionally:

1. **PubMed MCP** (direct H2H): `("<INN A>"[Substance Name] AND "<INN B>"[Substance Name])` + RCT filter
2. **Cochrane** (Fetch): search for systematic review covering both
3. **PubMed** for **ITC / MAIC** publications: `("<INN A>" OR "<INN B>") AND ("indirect treatment comparison" OR "matching-adjusted indirect comparison")`
4. **ClinicalTrials.gov MCP** for any ongoing direct H2H trials
5. **Consensus MCP**: "Is <A> superior to <B> in <population>?"
6. **NICE TA for both** — if both assessed, NICE often does ITC
7. **ICER assessment for the class** — often compares multiple options

---

## Phase 3 — Deep-dive

### 3.1 Efficacy

**Priority 1 — Direct head-to-head RCTs:**
- Most authoritative. Extract: NCT, n, randomization, primary endpoint definition, point estimate + CI, p-value, key secondary endpoints
- Confirm in regulatory review (FDA Medical Review, EMA EPAR) if cited in label

**Priority 2 — Indirect comparison (published ITC/MAIC):**
- Published ITCs often sponsor-funded; flag in analysis
- Matching-Adjusted Indirect Comparison (MAIC) preferred over naive ITC
- Check HTA assessments (NICE especially) for agency-performed ITCs — often most credible

**Priority 3 — Naive cross-trial comparison (narrative):**
- If only single-arm trials exist, cross-trial comparison is qualitative only
- Must flag: different populations, different imaging, different assessment intervals, different stop rules

**Priority 4 — Real-world comparative effectiveness:**
- Published RWE studies comparing the two
- Usually retrospective cohort analyses; confounding risk

For each priority level used, extract:
- Effect size magnitude + CI
- Population characteristics
- Follow-up duration (critical for survival endpoints)

### 3.2 Safety

1. **Label-to-label comparison** — DailyMed / EMA SmPC side by side
   - Boxed warnings
   - Contraindications
   - Grade ≥3 common AEs with incidence
   - Dose-modifying AEs
2. **Meta-analysis of safety** — PubMed for systematic reviews
3. **FAERS Public Dashboard** — compare top reported events for each (signal, not definitive — PRR / ROR caveats)
4. **EudraVigilance** — EU signal
5. Published post-marketing safety papers

### 3.3 Dosing / administration

From label:
- Dose + schedule
- Route (IV, SC, oral)
- Administration setting (infusion center vs self-admin)
- Premedications required
- Required monitoring (lab, imaging, cardiac)
- Duration of therapy (fixed vs until progression)
- REMS / risk management

Patient-convenience differentiation often moves real-world uptake; capture it.

### 3.4 Regulatory comparison

1. Side-by-side indication wording (FDA + EMA)
2. Approval pathway (standard / accelerated / conditional)
3. Post-marketing commitments
4. Any restrictions (e.g., NSCLC-specific histology, biomarker gating, prior-therapy requirement)

### 3.5 Payer / HTA

1. Any HTA that assessed both → compare
2. NICE TA with ITC in appendix → authoritative comparison
3. Value-based pricing (if any) in major markets
4. Published cost-effectiveness studies (search PubMed `"cost-effectiveness" AND "<A>" AND "<B>"`)

### 3.6 Commercial trajectory

- Sponsor 10-K / 10-Q for each (reported sales, launch trajectory)
- Quarterly growth comparison
- Geographic split (if disclosed)
- Market-size context from IQVIA Institute free report or Evaluate Vantage
- Analyst-media "takes" for differentiated positioning

### 3.7 Pipeline evolution

- Indication-expansion trials for each
- Combination trials
- Next-generation assets from same sponsor (could obsolete the current leader)

---

## Phase 4 — Triangulation

- **Efficacy effect sizes** — always double-source: publication + label or regulatory review
- **Safety** — label + meta-analysis; single label claim is acceptable if primary source
- **HTA opinions** — agency primary documents
- **Commercial claims** — sponsor disclosure + (if available) class-level free report

### ITC confidence handling

Indirect comparisons are **inherently lower** confidence than direct. When citing an ITC:
- Always state that it is indirect
- State the method (naive, Bucher, MAIC, STC)
- State who performed it (sponsor, academic, HTA)
- Cap confidence at Medium unless conducted by an HTA body AND concordant with other ITCs

## Phase 5 — Report

Per `assets/report-template.md`, comparison variant. Heavy use of side-by-side tables. End with a **differentiation summary** that is neither promotional nor falsely balanced — where the evidence favors one, state it; where evidence is uncertain, state that clearly.

---

## Specific pitfalls to avoid

1. **Cherry-picked endpoints** — don't anchor the comparison on the endpoint where A wins if the pre-specified primary was different
2. **Different populations treated as comparable** — label populations often have subtle differences; flag
3. **Unreported baseline imbalances** — for small trials, baseline imbalance can drive apparent difference
4. **Survival follow-up differences** — Trial A's 24mo OS isn't comparable to Trial B's 36mo OS
5. **Assay / imaging differences** — radiographic PFS by different criteria (RECIST 1.1 vs modified) isn't directly comparable
6. **Publication bias in ITCs** — sponsor-funded ITCs typically favor sponsor's asset; triangulate with HTA agency ITC where possible
7. **Market-share "facts" from secondary sources** — often estimates; tag as Medium at best
8. **Conflating regulatory approval with practice** — being approved ≠ being recommended ≠ being used

---

## When NCCN / ESMO / guideline recommendations help

Guideline committees often provide the **de facto** head-to-head positioning where no formal H2H exists:
- NCCN category 1 (uniform consensus based on high-level evidence)
- ESMO-MCBS grade
- ASCO rapid updates

Treat guideline positioning as important context, but not a substitute for primary data. Report both.

---

## Limitations (standard)

- No direct H2H trial → analysis is indirect; magnitude of difference uncertain
- Different regulatory paths can obscure comparability
- HTA assessments may not cover both assets
- Real-world data often biased by treatment selection
- Publication bias affects the ITC literature

Surface in §Limitations section.


---

## Sub-mode: Sponsor-Specific Competitive Defense (T6-Defense, v1.8.0+)

The default T6 task is **sponsor-agnostic**: comparison is presented as factual landscape with abstract stakeholder framing for strategic implications. This default is mandatory per `generic-by-default.md` Article 3.

When the user **explicitly invokes sponsor-specific defense framing** (named sponsor + perspective phrase), T6 enters the **T6-Defense sub-mode** governed by `task-comparison-defense.md`. Key characteristics:

- **Activation:** Explicit query-content trigger only (no semantic auto-trigger)
- **Scope:** Selective 2-of-8 G22 override (G22.4 + G22.7) within §10.B / §10.C Strategic Implications ONLY
- **Symmetry requirement:** Mandatory parallel competitor perspective section (§10.C alongside §10.B)
- **Audit:** New gate G24 with 6 well-formedness checks
- **Validator:** `# T6-DEFENSE:` annotation class + `--enforce-g24` CLI flag

If the user query is ambiguous between standard T6 and T6-Defense, **default to standard T6** (sponsor-agnostic). Never assume defense framing without explicit invocation.

See `task-comparison-defense.md` for full sub-mode specification including activation triggers (§1), selective override pattern (§2), symmetric framing requirements (§3), output structure (§4), strategic implications discipline (§5), mandatory triple disclosure (§6), G24 gate audit (§7), validator integration (§8), and worked example (§9).

