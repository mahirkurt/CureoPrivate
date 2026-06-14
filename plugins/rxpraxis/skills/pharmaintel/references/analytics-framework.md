# analytics-framework.md

**Computational Analytics Framework Reference (v3.0.0)**

> **Architectural role:** Cross-cutting capability reference for pharmaintel analytical templates. Provides discipline for risk-adjusted NPV modeling, sensitivity analysis, and scenario forecasting. Accompanied by three runnable Python scripts:
> - `scripts/analytics-npv.py` — rNPV calculator
> - `scripts/analytics-sensitivity.py` — tornado + one-way/two-way sensitivity
> - `scripts/analytics-scenario.py` — base/bull/bear + Monte Carlo primitive

---

## §1. Scope & Discipline

### 1.1 What this framework provides

Pharmaintel analytical outputs may include quantitative projections. When quantitative NPV / sensitivity / scenario modeling is in scope:
1. Framework documented here establishes discipline
2. Runnable Python scripts in `/scripts/` execute computation
3. Confidence stamping per `triangulation.md` applied to all quantitative claims
4. Forbidden patterns per `§10` enforced

### 1.2 What this framework does NOT provide

- NOT a substitute for sponsor-supplied valuation models
- NOT market-grade equity research (no comparable multiples, no precedent transactions beyond public disclosure)
- NOT proprietary forecasting methodology (uses standard pharma valuation conventions)
- NOT a replacement for `task-hta.md` for health economic modeling (QALY, ICER, budget impact)

### 1.3 Discipline principle: inputs determine confidence

Quantitative output confidence = **minimum** of input confidences. A NPV projection using high-confidence peak sales + low-confidence probability of success = overall **low-confidence** output. Confidence downgrade must be stamped in `Provenance` section of generated reports.

---

## §2. Risk-Adjusted NPV (rNPV) Framework

### 2.1 Conceptual framework

**NPV** = ∑ (CFₜ / (1+r)ᵗ) — standard DCF

**rNPV** = ∑ (CFₜ × PoSₜ / (1+r)ᵗ) — risk-adjusted DCF where PoSₜ is cumulative probability of success from current stage through cash flow year t

Pharmaceutical asset valuation convention: **apply stage-based PoS to all cash flows pre-launch + pre-LOE commercial cash flows**.

### 2.2 Stage-based probability of success (PoS) benchmarks

**Per BIO/QLS/Informa Pharma Intelligence 2020-2024 meta-analyses** (primary sources: BIO Industry Analysis "Clinical Development Success Rates 2011-2020"; Thomas DW et al., approximation):

| Development stage | Oncology PoS | Non-oncology PoS | Rare disease PoS |
|---|---|---|---|
| Preclinical → Phase 1 | 60-70% | 60-70% | 60-70% |
| Phase 1 → Phase 2 | 50-60% | 50-65% | 60-70% |
| Phase 2 → Phase 3 | 25-35% | 30-45% | 40-55% |
| Phase 3 → BLA/NDA | 50-65% | 55-70% | 65-75% |
| BLA/NDA → Approval | 85-90% | 85-90% | 85-90% |
| **Cumulative Phase 1 → Approval** | **5-10%** | **10-15%** | **15-25%** |
| **Cumulative Phase 2 → Approval** | **10-15%** | **15-25%** | **25-40%** |
| **Cumulative Phase 3 → Approval** | **45-60%** | **55-70%** | **65-80%** |

**Discipline:**
- PoS benchmarks are **class-level averages** — individual asset deviation can be 2x higher or lower
- Rare disease boost partly driven by regulatory flexibility (accelerated approval, surrogate endpoints, small populations)
- Oncology penalty driven by biomarker subsetting failures + active comparator arm requirements
- PoS is backward-looking; innovative mechanisms may deviate from historical benchmarks

### 2.3 Discount rate (WACC / cost of capital) conventions

Standard pharmaceutical rNPV WACC range:
- **Big Pharma** (MRK, PFE, NVS, JNJ, etc.): 7-9%
- **Mid-cap biotech** ($5-50B market cap): 9-12%
- **Small-cap biotech** ($500M-$5B): 12-15%
- **Pre-revenue clinical-stage**: 15-20% (or higher with binary catalyst weighting)
- **Private / pre-IPO**: 20-30% (liquidity premium)

**Discipline:** WACC must be stamped in Provenance with justification. Confidential actual WACC (per sponsor 10-K disclosure) takes priority over benchmark ranges when available.

### 2.4 Cash flow projection framework

For each forecast year t, project:
```
Net Revenue_t = Patient_Population_t × Treatment_Rate_t × Price_t × Share_t
Gross Profit_t = Net Revenue_t × (1 - COGS%)
R&D Expense_t = (stage-based allocation; clinical + CMC + regulatory)
SG&A Expense_t = Net Revenue_t × SGA%_t (typically 25-35% for specialty pharma)
EBITDA_t = Gross Profit_t - R&D_t - SGA_t
Tax_t = EBITDA_t × Effective_Tax_Rate (global blended ~18-22% 2026)
After-Tax_Cash_Flow_t = EBITDA_t × (1 - Tax_Rate) + Depreciation_t - CapEx_t - ΔWC_t
```

Terminal value typically assumed at LOE (first major generic/biosimilar competition):
- **Pre-LOE**: explicit forecast year-by-year
- **Post-LOE**: 10-20% of pre-LOE peak as steady-state residual revenue (mature generic competition)
- **Discontinuation**: typically 3-7 years post-LOE for specialty products; longer for long-tail chronic products

### 2.5 Royalty / milestone structures

For BD-acquired assets or in-licensed compounds:
- **Upfront payment** — recognized immediately (negative cash outflow to acquirer)
- **Development milestones** — PoS-weighted
- **Regulatory milestones** — PoS-weighted
- **Commercial milestones** — achievement-threshold weighted
- **Royalties** — tiered by revenue threshold (typical 5-25% single-digit to mid-teens)

See `task-deal.md` for BD deal analytical frame.

### 2.6 Python implementation

Runnable Python calculator in `scripts/analytics-npv.py` (see §7 for structure).

---

## §3. Sensitivity Analysis Framework

### 3.1 Why sensitivity matters

rNPV is highly sensitive to input assumptions. Sensitivity analysis reveals:
- Which input variables drive output variance
- Directional relationships (linear vs non-linear)
- Break-even thresholds (input level at which NPV = 0)
- Robustness of investment / pipeline prioritization decisions

### 3.2 One-way sensitivity (tornado diagram)

For each input variable x_i, hold others at base case, vary x_i across range (typically ±20% or ±1 standard deviation), measure ΔNPV.

**Tornado presentation:**
- Y-axis: variables ranked by |ΔNPV| (widest impact first)
- X-axis: ΔNPV range for each variable's perturbation
- Bar width = sensitivity
- Variables contributing >10% of base NPV typically shown

**Typical pharma tornado order:**
1. Peak sales / share (usually highest sensitivity)
2. Probability of success (Phase 2 → Phase 3 transition particularly)
3. Pricing assumptions (price × share tightly linked)
4. Discount rate / WACC
5. Time to launch
6. LOE / generic entry timing
7. SG&A / COGS ratios
8. Cannibalization from own-portfolio products

### 3.3 Two-way sensitivity (heatmap)

For two inputs varied jointly, produce NPV surface. Common pairs:
- PoS × peak sales (how much PoS reduction can a high peak sales absorb?)
- Discount rate × peak sales
- Time to launch × market growth
- Price × share (since revenue = price × share, curves show iso-revenue lines)

### 3.4 Break-even analysis

For each high-sensitivity input, find the value at which NPV = 0:
- "At what PoS does this asset cross NPV = 0?"
- "At what peak sales does this asset justify the current acquisition price?"

### 3.5 Python implementation

Runnable Python calculator in `scripts/analytics-sensitivity.py` (see §7).

---

## §4. Scenario Forecasting Framework

### 4.1 Three-scenario framework (base/bull/bear)

Standard pharmaceutical commercial forecasting uses:
- **Base case** — most likely trajectory, aligned with sponsor-guidance + market consensus
- **Bull case** — upside ~1.5-2.5x base (expanded indications, faster uptake, premium pricing retention, slower erosion)
- **Bear case** — downside ~30-60% of base (label restrictions, slower uptake, accelerated competition, earlier LOE)

**Symmetry bias caution:** Asymmetric distributions common in pharma — limited downside (regulatory denial = zero commercial) vs unlimited upside (blockbuster indication expansion). Document asymmetry explicitly.

### 4.2 Probability-weighted NPV

```
Probability-Weighted NPV = P(Base) × NPV(Base) + P(Bull) × NPV(Bull) + P(Bear) × NPV(Bear)
```

Typical pre-launch clinical asset weights:
- **Before Phase 2 readout:** Base 40%, Bull 20%, Bear 40%
- **After positive Phase 2:** Base 50%, Bull 30%, Bear 20%
- **After positive Phase 3 pivotal:** Base 65%, Bull 25%, Bear 10%
- **After approval:** Base 70%, Bull 20%, Bear 10%
- **Post-LOE declining:** Base 60%, Bull 15%, Bear 25% (uncertain erosion kinetics)

### 4.3 Monte Carlo simulation (primitive)

Discipline: use only when input distributions are characterizable and correlations understood. Full-scale Monte Carlo is overkill for most pharmaintel use cases; 3-scenario framework suffices.

When used:
- 10,000 iteration minimum for converged distribution
- Distribution assumptions per input (triangular for bounded; lognormal for revenue; binary for catalyst events)
- Correlation matrix for correlated inputs (price × share positive; PoS × time to launch negative)
- Output: distribution of NPV with 5th/50th/95th percentiles

### 4.4 Python implementation

Runnable Python calculator in `scripts/analytics-scenario.py` (see §7).

---

## §5. Pharma-Spesifik Analytical Considerations

### 5.1 Peak sales forecasting — three main approaches

| Method | Description | When to use |
|---|---|---|
| **Top-down epidemiology** | Prevalence × diagnosis rate × treatment rate × addressable share × price | Novel mechanism, limited precedent |
| **Analog-based** | Scale from comparable product's trajectory | Established modality in known indication |
| **Bottom-up physician demand** | Survey-based intended-use × total prescriber population | Launch-stage, post-commercial |

Pharmaintel free-tier constraint: physician survey data typically unavailable; rely on top-down + analog-based.

### 5.2 Launch curve archetypes

| Archetype | Curve shape | Pharma examples |
|---|---|---|
| **Explosive** | Steep ramp, <3 years to peak | Keytruda melanoma, Eliquis, Humira |
| **Gradual** | 5-7 years to peak | Specialty biologics with narrow indication then expansion |
| **Slow** | 7-10 years to peak | Rare disease drugs, payor-access-constrained products |
| **Stalled** | Plateaus below guidance | Specialty products with access challenges (Aduhelm precedent) |

Launch curve archetype drives revenue shape assumption in rNPV.

### 5.3 LOE erosion kinetics

Per `task-modality-smallmol.md` §10 and `task-modality-biosimilar.md` §14:
- **Small molecule** — aggressive (90-95% net revenue erosion within 24 months)
- **Biosimilar** — moderate (50-70% erosion first 3 years, steady-state 30-40% vs pre-LOE)
- **Complex generics** — slow (peptide, topical, nasal)
- **Brand resilience factors** — patent thicket, reformulation, authorized generic, long-tail specialty

### 5.4 Cannibalization discipline

When sponsor has multiple assets in same disease area (tirzepatide cannibalizing dulaglutide, dostarlimab positioning vs pembrolizumab, etc.):
- Cross-asset cannibalization rate (typically 50-80% for same-class same-sponsor)
- Net portfolio NPV < sum of individual NPVs
- Discipline: always flag cannibalization in multi-asset sponsor analyses

---

## §6. Confidence Stamping for Analytical Claims

| Claim type | Default confidence |
|---|---|
| FDA/EMA approval dates | **High** (statutory primary) |
| Sponsor-reported Peak Sales Guidance (in SEC filings) | **Medium-High** (sponsor-disclosed but forward-looking) |
| Consensus analyst estimates | **Medium** (averaged biases across analysts) |
| rNPV projection | **Medium-Low** (derivative of many inputs; confidence = minimum of inputs) |
| PoS benchmarks (BIO/QLS) | **Medium** (class-averaged, backward-looking) |
| Sensitivity elasticities | **Medium** (dependent on underlying rNPV quality) |
| Bull/Bear scenario deltas | **Low-Medium** (inherently speculative) |
| Monte Carlo percentile outputs | **Low-Medium** (distribution assumptions fragile) |
| Confidential IQVIA MIDAS / proprietary data | Should not be used (free-tier discipline) |

---

## §7. Runnable Python Scripts

### 7.1 `scripts/analytics-npv.py`

**Purpose:** Risk-adjusted NPV calculation from structured input JSON.

**Input format:**
```json
{
  "wacc": 0.10,
  "pos": 0.55,
  "cash_flows": [
    {"year": 2026, "revenue": 0, "cogs_pct": 0.15, "sga_pct": 0.30, "rd": 150e6},
    {"year": 2027, "revenue": 100e6, "cogs_pct": 0.15, "sga_pct": 0.40, "rd": 100e6},
    ...
  ],
  "terminal": {"year": 2040, "terminal_value": 500e6}
}
```

**Output:** Stage-by-stage discounted cash flow + aggregate rNPV with confidence stamp.

### 7.2 `scripts/analytics-sensitivity.py`

**Purpose:** Generate tornado diagram data + one-way sensitivity table.

**Input:** base case NPV JSON + list of variables with perturbation ranges.

**Output:** JSON sorted by absolute sensitivity, renderable as tornado chart in matplotlib or pptx.

### 7.3 `scripts/analytics-scenario.py`

**Purpose:** Compute probability-weighted NPV across base/bull/bear + optional Monte Carlo.

**Input:** base case + bull/bear multipliers + scenario weights + (optional) Monte Carlo input distributions.

**Output:** Probability-weighted NPV + percentile distribution if MC enabled.

### 7.4 Script invocation discipline

From Claude:
1. Read `analytics-framework.md` first (this file)
2. Construct input JSON per framework convention
3. Run `python3 scripts/analytics-{npv|sensitivity|scenario}.py input.json`
4. Parse output JSON
5. Integrate into report with confidence stamping per `§6`

---

## §8. Integration with Existing Reports

### 8.1 Report template integration

`assets/report-template.md` may include optional T5 (Financial Projection) section. When analytical output is generated:
- Document assumptions transparently in Provenance section
- Flag all inputs with confidence stamps
- Show full sensitivity tornado (not just headline NPV)
- Present base/bull/bear scenario range (not point estimate only)

### 8.2 Defensive formatting

Financial projection sections must include caveat block:
```
DISCLAIMER: Projections are model-derived from publicly-available inputs using
standard pharmaceutical valuation conventions. Confidence stamping per each input.
Not a substitute for sponsor-supplied valuation. Not investment advice.
```

---

## §9. Cross-Layer Integration

### 9.1 With modality templates
- ADC: valuation sensitivity to ILD discontinuation rate affecting uptake
- Cell/gene: one-shot pricing + patient-count-limited demand forecasting
- Radiopharm: isotope supply constraint as revenue cap
- Small molecule generic: Hatch-Waxman erosion curve modeling
- Biosimilar: BPCIA discount banding + tender market dynamics

### 9.2 With TA templates (v3.0.0 Layer 2)
- Oncology: biomarker-positive subset sizing + sequencing cannibalization
- Autoimmune: line of therapy positioning + step therapy coverage dynamics
- Rare disease: orphan exclusivity + pediatric exclusivity + outcomes-based contracting
- CNS: placebo response rate as risk variable + trial failure historical patterns
- Metabolic: adherence discounting + real-world effectiveness gaps

### 9.3 With sub-protocols
- `sub-protocol-catalyst-watch.md`: event-driven NPV re-estimation post-readout
- `sub-protocol-turkey.md`: SGK SUT reimbursement scenarios as sensitivity input

---

## §10. Forbidden Analytical Patterns

- ❌ Presenting rNPV point estimates without sensitivity range
- ❌ Using confidential IQVIA / Clarivate / paywalled data as input
- ❌ Forecasting peak sales of >2x sponsor guidance without explicit justification
- ❌ Applying generic PoS benchmarks to novel mechanisms without class-deviation acknowledgment
- ❌ Using probability-weighted NPV to recommend investment decisions (this is a decision tool, not a recommendation)
- ❌ Publishing Monte Carlo percentiles with <10,000 iterations (convergence unreliable)
- ❌ Correlating inputs via Monte Carlo when correlation structure unjustified
- ❌ Using rNPV in T6-Defense contexts to argue superiority of sponsor product (violates evenhandedness — use symmetric opposite analysis per T6 discipline)

---

## §11. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. Cross-cutting computational analytics framework covering: rNPV framework with stage-based PoS benchmarks per BIO/QLS meta-analyses (oncology 5-10% P1→approval vs 15-25% rare disease P1→approval; P3→approval 45-60% oncology vs 65-80% rare disease), WACC conventions by sponsor size (Big Pharma 7-9% / mid-cap biotech 9-12% / small-cap 12-15% / pre-revenue 15-20% / private pre-IPO 20-30%), cash flow projection framework (revenue-based forecasting with SGA 25-35% specialty pharma benchmark + tax 18-22% blended 2026 + LOE terminal convention), royalty/milestone BD structures, sensitivity analysis (one-way tornado + two-way heatmap + break-even analysis + typical pharma tornado order), scenario forecasting (base/bull/bear with typical pre-launch 40/20/40 vs post-P3 65/25/10 weights + asymmetric distribution bias + Monte Carlo primitive with 10,000 iteration minimum), pharma-spesifik considerations (peak sales 3 approaches top-down/analog/bottom-up + launch curve archetypes explosive/gradual/slow/stalled + LOE erosion kinetics by modality + cannibalization discipline for multi-asset sponsors), confidence stamping framework + accompanying runnable Python scripts analytics-npv.py + analytics-sensitivity.py + analytics-scenario.py. New manifest gates G37 (NPV), G38 (sensitivity), G39 (scenario). Cross-layer integration with modality templates (v2.0-2.6) + TA templates (v3.0 Layer 2) + sub-protocols.
