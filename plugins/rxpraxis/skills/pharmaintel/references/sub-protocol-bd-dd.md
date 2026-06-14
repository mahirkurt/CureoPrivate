# sub-protocol-bd-dd.md

**Sub-Protocol — Business Development (BD) Due Diligence (v5.0.0)**

> **Purpose:** End-to-end due diligence orchestration for pharmaceutical BD transactions — licensing, M&A, option agreements, co-development, royalty financing. Wraps `sub-protocol-provenance.md` with BD-spesifik assessment discipline covering target company UBO + sanctions + litigation + regulatory history + commercial trajectory + scientific merit + deal structure considerations. Produces BD-grade risk register + forensic-grade evidence bundle as dual deliverable.
>
> **Architectural context:** New sub-protocol (v5.0.0). Operates at higher abstraction than `sub-protocol-provenance.md` — orchestrates multi-dimensional target assessment with provenance as embedded workflow. Invoked by user-facing BD DD requests or by `task-deal.md` / `task-company.md` workflows in due diligence context.

---

## §1. Activation Triggers

### 1.1 Explicit invocation

- "BD due diligence on <target>"
- "Target assessment for <company> licensing deal"
- "Evaluate <company> as acquisition target"
- "Due diligence report before term sheet on <asset>"
- "Ticaret DD <hedef şirket>" (Turkish DD)
- "Risk register for <target> before signing"
- "Pre-LOI assessment of <company>"

### 1.2 Implicit triggers (context-based)

Parent task detects BD DD context:
```
IF task ∈ {task-deal.md, task-company.md, task-asset.md}
AND context_signals ⊇ {
    "licensing_evaluation",
    "acquisition_target",
    "option_agreement",
    "royalty_financing",
    "co_development"
}
THEN activate sub-protocol-bd-dd
```

### 1.3 NOT triggered by

- ❌ General competitive intelligence (use `task-company.md` without DD context)
- ❌ Market landscape reports (use `task-asset.md` or TA templates)
- ❌ Simple company profiles without transaction context
- ❌ User employer engaging in BD alone (Roche employee asking about a company ≠ DD activation) per `generic-by-default.md` Article 5

---

## §2. Seven-Dimensional Target Assessment

Sub-protocol-bd-dd orchestrates assessment across **7 dimensions**. Each dimension produces evidence objects via sub-protocol-provenance chaining.

### 2.1 Dimension A — Corporate Structure + UBO

**Objective:** Establish target entity legal structure + investor chain + ultimate beneficial ownership.

**Workflow:**
1. Target company identification (name, jurisdiction, registration number)
2. Invoke `ubo-source-hierarchy.md` P0→P3 cascade per sub-protocol-provenance
3. Recursive investor chain walk (max 7 hops per `ubo-source-hierarchy.md` §7.3)
4. For each hop: evidence object emitted + cross-linked

**Outputs:**
- Investor chain tree (SVG + Markdown)
- List of ultimate natural persons or sovereign/public entities
- Obfuscation flag if trust/foundation/bearer-share pattern detected
- Evidence objects: 5-20 typical (one per hop + triangulation partners)

**Red flags:**
- Recent SPV (<30 days pre-deal)
- Formation agent registered address for direct shareholders
- Multiple jurisdiction hops through secrecy havens
- Nominee director pattern

### 2.2 Dimension B — Sanctions + PEP Screening

**Objective:** Verify no UBO chain member is sanctioned + identify PEP exposure.

**Workflow:**
1. Extract all natural persons + legal entities from Dimension A investor chain
2. Screen against all major sanctions lists:
   - OFAC SDN + Consolidated Sanctions List
   - EU Consolidated Financial Sanctions List (CFSL)
   - UK HMT / OFSI Consolidated List
   - UN Security Council Consolidated List
   - Türkiye MASAK (if Turkish target or UBO)
3. Screen against PEP (Politically Exposed Persons) databases
4. Fuzzy matching with phonetic + edit-distance for name variants

**Outputs:**
- Clean report if no hits: "clear" evidence object per entity
- Hit report if matches: BLOCKER flag + OFAC entry snapshot + advisory recommendation
- PEP exposure register

**BLOCKER behavior:** Sanctions hit → deal-killer at BD stage. Sub-protocol-bd-dd returns `status: "blocker_sanctions_hit"` + halts further dimensions unless explicit override.

### 2.3 Dimension C — Regulatory History

**Objective:** Document target's regulatory track record across FDA + EMA + PMDA + NMPA + TİTCK + other relevant authorities.

**Workflow:**
1. FDA history:
   - Drugs@FDA approvals + CRLs
   - Inspection 483s + Warning Letters + Untitled Letters
   - REMS modifications + recalls
   - FAERS signal emergence events
2. EMA history:
   - CHMP opinions + EPAR withdrawals + refusals
   - PRAC safety signals + risk minimization measures
3. PMDA history (if Japan exposure):
   - 添付文書 (tenpubunsho) revisions + Sakigake designations + PMDA meeting records
4. NMPA history (if China exposure):
   - CDE filings + priority review designations + review cycle metrics
5. TİTCK history (if Türkiye exposure):
   - Ruhsat onayı + komisyon kararları + geri çekme
6. Other authorities (MHRA + Health Canada + TGA + Swissmedic)

**Outputs:**
- Regulatory timeline (chronological, per authority)
- Recurring patterns (e.g., multiple Form 483s at same facility, multiple CRLs on same asset)
- Active regulatory obligations (REMS, PMCs, PMRs, Type A meeting commitments)

**Red flags:**
- Warning Letter within 36 months
- Withdrawn approval (voluntary or mandatory)
- Pattern of Information Request Letters
- Consent decree or corporate integrity agreement

### 2.4 Dimension D — Litigation + IP + Patent

**Objective:** Document litigation exposure + patent landscape + IP asset verification.

**Workflow:**
1. Active litigation:
   - Product liability (Prop 65, NY consumer protection, class actions)
   - Patent infringement (ANDA Paragraph IV, IPR, PGR, EPO opposition)
   - SEC enforcement / DOJ FCPA investigations
   - Employment + trade secret disputes
2. Patent portfolio verification:
   - Orange Book listings (current + expired)
   - Purple Book reference product listings
   - Patent family via Google Patents / USPTO / EPO / PCT
   - Patent cliff analysis (LOE dates per major patent)
3. IP ownership chain (for licensed assets):
   - Original inventor → licensor → target chain
   - Prior licensing encumbrances / reverse-payment obligations
   - Field-of-use + territory restrictions on licensed IP

**Outputs:**
- Litigation docket summary with active case NCT-style identifiers (PACER docket numbers)
- Patent portfolio table with LOE dates
- IP encumbrance register (exclusivity, field-of-use, territory)

**Red flags:**
- Active ANDA Paragraph IV with unfavorable scheduling order
- Pending IPR institution decision for key patent
- SEC subpoena or DOJ inquiry
- Unresolved trade secret misappropriation claim

### 2.5 Dimension E — Commercial Trajectory

**Objective:** Document product revenue + market share + growth trends + commercial execution quality.

**Workflow:**
1. Product-level revenue (if disclosed): 10-K / 20-F / annual report
2. Therapeutic area positioning: Layer 2 TA template invocation (task-ta-*.md)
3. Market share trajectory: IQVIA Institute free reports + symphony-like free-tier data
4. Payer access status (US): Medicare Part D + Part B + major PBM formulary position
5. Turkish access (if relevant): SGK SUT status + TİTCK ruhsat history

**Outputs:**
- 3-year revenue trajectory per product
- Market share snapshot
- Payer coverage breadth
- Commercial execution commentary

### 2.6 Dimension F — Scientific Merit

**Objective:** Assess scientific case for pipeline asset(s) without sponsor-bias.

**Workflow:**
1. Pivotal trial data via Clinical Trials:search_trials + medsearch:search
2. Publication track record + journal impact factors
3. Mechanism-of-action plausibility + class positioning
4. Competitive landscape via Layer 1 modality template + Layer 2 TA template
5. KOL sentiment via medsearch:search_investigators

**Outputs:**
- Pivotal trial readout table
- Publication list with citation metrics
- Mechanism-of-action commentary
- Competitive positioning assessment

### 2.7 Dimension G — Deal Structure Diligence

**Objective:** Document deal-spesifik considerations (for post-LOI phase).

**Workflow:**
1. Similar precedent transactions: `task-deal.md` comparables
2. Valuation NPV modeling: `scripts/analytics-npv.py` + sensitivity (`analytics-sensitivity.py`)
3. Deal structure considerations: upfront + milestones + royalty + territory
4. Representations & warranties standard clauses per jurisdiction
5. MAC (Material Adverse Change) clause benchmarks

**Outputs:**
- Comparable deal table with multiples
- Target rNPV range (base / bull / bear)
- Deal structure recommendation memo

---

## §3. Workflow Orchestration

### 3.1 Step-by-step sequence

```
[INVOCATION — user or parent task detects BD DD context]
        ↓
Step 1: Scoping Interview (operator in loop, optional)
    ├─ Target company identification
    ├─ Deal type (license / M&A / option / royalty / co-dev)
    ├─ Asset(s) in scope
    ├─ Territory scope
    ├─ Timeline (pre-LOI / post-LOI / closing)
    └─ Specific risk areas of concern
        ↓
Step 2: Dimension A + B — Corporate + Sanctions (parallel)
    ├─ A.1: Invoke ubo-source-hierarchy.md P0→P3 cascade
    ├─ A.2: Investor chain walk (recursive ≤7 hops)
    ├─ A.3: Emit evidence objects per hop via sub-protocol-provenance
    ├─ B.1: Extract entities + persons from A
    ├─ B.2: Screen against OFAC + EU + UK + UN + MASAK + PEP
    ├─ B.3: Emit evidence objects per screening result
    └─ CHECKPOINT: Sanctions hit → HALT with blocker unless override
        ↓
Step 3: Dimension C + D — Regulatory + Litigation (parallel)
    ├─ C: FDA + EMA + PMDA + NMPA + TİTCK + other regulatory history snapshot
    ├─ D: Litigation dockets + patent portfolio + IP chain
    └─ All findings emit evidence objects
        ↓
Step 4: Dimension E + F — Commercial + Scientific (parallel)
    ├─ E: Revenue + market share + payer access
    ├─ F: Pivotal trials + publications + KOL sentiment
    └─ Evidence objects for all forensic-grade claims
        ↓
Step 5: Dimension G — Deal Structure (when applicable)
    ├─ Comparable precedents
    ├─ rNPV modeling via analytics-framework
    └─ Deal structure recommendations
        ↓
Step 6: Synthesis + Risk Register
    ├─ Consolidate all dimension findings
    ├─ Produce color-coded risk register (RED / AMBER / GREEN per dimension)
    ├─ Executive summary with deal-go/no-go recommendation
    └─ Recommend follow-up diligence areas
        ↓
Step 7: Forensic Provenance Bundle Assembly
    ├─ All evidence objects from Steps 2-5 collected
    ├─ Bundle ZIP built via sub-protocol-provenance Step 5
    └─ Appendix B rendered in BD DD report
        ↓
Step 8: Deliverable Rendering
    ├─ BD DD report (markdown / carbon-html / carbon-pptx)
    ├─ Risk register (structured table + heatmap)
    ├─ Evidence Bundle ZIP (standalone deliverable)
    └─ Follow-up action list
        ↓
[RETURN TO PARENT — or deliver to user]
```

### 3.2 Parallel-safety annotations

Per `orchestration.md` v3.0.0:

**Parallel-safe across dimensions:**
- Steps 3+4 (Regulatory + Litigation + Commercial + Scientific) — full parallel execution
- Within each dimension, sub-queries parallel where source-independent

**Serial:**
- Step 2 (Corporate + Sanctions) — Sanctions depends on Corporate chain output
- Step 6 (Synthesis) — requires all prior steps complete
- Step 7 (Bundle assembly) — requires all evidence objects

### 3.3 Cache coordination

Sub-protocol-bd-dd leverages `orchestration.md` cache framework:
- Corporate + UBO cache: 7-day TTL per ubo-source-hierarchy.md §9.2 freshness discipline
- Sanctions cache: 24-hour TTL (daily OFAC updates)
- Regulatory history cache: 7-day TTL (weekly scan acceptable)
- Patent portfolio cache: 30-day TTL (monthly acceptable for USPTO/EPO)
- Revenue data cache: 90-day TTL (quarterly reporting cycle)

---

## §4. Output Contract

### 4.1 Primary deliverable — BD DD Report

Structured markdown report with sections:

```markdown
# BD Due Diligence Report — <Target Company>

## §Executive Summary
  - Deal type + scope + timeline
  - Overall risk rating: RED / AMBER / GREEN
  - Go / No-Go / Conditional recommendation
  - Top 3 critical risks
  - Top 3 confirmed strengths

## §1. Corporate Structure + UBO
  - Legal entity structure
  - Investor chain tree (SVG)
  - Ultimate beneficial owners
  - Obfuscation flags (if any)

## §2. Sanctions + PEP Screening
  - Screening results per UBO chain member
  - Clear / Hit determination
  - PEP exposure map

## §3. Regulatory History
  - FDA track record
  - EMA track record
  - PMDA track record (if applicable)
  - NMPA track record (if applicable)
  - TİTCK track record (if applicable)
  - Other authorities
  - Active regulatory obligations

## §4. Litigation + IP + Patent
  - Active litigation docket
  - Patent portfolio with LOE
  - IP encumbrances

## §5. Commercial Trajectory
  - Product revenue history
  - Market share trajectory
  - Payer access status
  - Turkish SGK SUT status (if applicable)

## §6. Scientific Merit
  - Pivotal trial data
  - Publications
  - Mechanism-of-action commentary
  - Competitive positioning

## §7. Deal Structure Considerations
  - Comparable precedent deals
  - rNPV valuation range
  - Deal structure recommendations

## §8. Risk Register
  - Dimension-spesifik color-coded heatmap
  - Risk items with severity + likelihood + mitigation

## §9. Follow-up Diligence Recommendations
  - Items requiring operator action
  - Items requiring external specialist (legal / tax / technical)
  - Timeline to address before LOI / close

## §Appendix A — Detailed Evidence Support
  - Per-claim evidence summaries

## §Appendix B — Evidence Bundle Manifest (forensic-grade)
  - Bundle ZIP SHA-256
  - Evidence index table
  - Verification instructions
  - Jurisdictional compliance notes
```

### 4.2 Structured risk register (YAML)

```yaml
# risk_register.yaml
target: "<company>"
deal_type: "<license | acquisition | option | royalty | codev>"
assessment_date: "2026-04-16"
overall_risk: "AMBER"
recommendation: "CONDITIONAL — proceed with remediation of Items 1-3"

dimensions:
  corporate_ubo:
    rating: "GREEN"
    findings:
      - id: "A.1"
        severity: "LOW"
        item: "Ultimate owner identified as [sovereign / individual / public entity]"
        evidence_ids: ["ev_..."]
  sanctions:
    rating: "GREEN"
    findings:
      - id: "B.1"
        severity: "NONE"
        item: "All UBO chain members cleared against OFAC + EU + UK + UN + MASAK"
  regulatory:
    rating: "AMBER"
    findings:
      - id: "C.1"
        severity: "MEDIUM"
        item: "Form 483 observation 2024-Q3 at contract manufacturer"
        mitigation: "CMO remediation plan verified; request CAPA closure documentation"
        evidence_ids: ["ev_..."]
  litigation:
    rating: "AMBER"
    findings:
      - id: "D.1"
        severity: "HIGH"
        item: "Active ANDA Paragraph IV litigation; trial scheduled 2027-Q1"
        mitigation: "Patent position opinion from <law firm>; IPR counter-strategy"
  commercial:
    rating: "GREEN"
  scientific:
    rating: "GREEN"
  deal_structure:
    rating: "GREEN"

critical_risks_top3:
  - id: "D.1"
    title: "Patent cliff litigation exposure"
  - id: "C.1"
    title: "CMO Form 483 unresolved"
  - id: "E.2"
    title: "Medicare Part B coverage gap in Q2 2026"

strengths_top3:
  - id: "F.1"
    title: "NEJM publication pivotal with HR 0.68 OS benefit"
  - id: "E.1"
    title: "Revenue trajectory +45% YoY 2024"
  - id: "A.2"
    title: "Institutional shareholder base (Fidelity + BlackRock + T. Rowe)"

follow_up_actions:
  - "Obtain CMO CAPA closure documentation before signing"
  - "Patent opinion from [law firm] on ANDA Paragraph IV exposure"
  - "Verify Medicare NCD update status for Q2 2026"

evidence_bundle:
  path: "<path>"
  sha256: "<hash>"
  evidence_count: <N>
```

### 4.3 Standalone deliverable — Evidence Bundle ZIP

Full Evidence Bundle ZIP per sub-protocol-provenance §4.3 — contains all evidence objects across 7 dimensions.

### 4.4 Return to parent or delivery to user

```yaml
return:
  status: "go" | "no_go" | "conditional" | "blocker_sanctions_hit" | "blocker_critical_risk"
  overall_risk: "RED" | "AMBER" | "GREEN"
  report_path: "<path>"
  risk_register_path: "<path>"
  evidence_bundle_zip_path: "<path>"
  evidence_bundle_zip_sha256: "<hash>"
  evidence_count: <N>
  critical_risks: [...]
  follow_up_actions: [...]
  validator_result:
    forensic_grade_gates_passed: <10/10 | N/10>
  total_duration_hours: <float>
```

---

## §5. Runbook — Illustrative BD DD Engagement

### 5.1 Example: Private Chinese biotech acquisition DD

```
Day 0: Scoping Interview
  Target: Shanghai Hypothetical Biotech Co.
  Deal type: Acquisition
  Timeline: Pre-LOI
  Concerns: CFIUS / FIRRMA exposure + China tech transfer risk

Day 1-2: Dimensions A + B (Corporate + Sanctions)
  A.1: SAIC Shanghai registry → found direct shareholders
  A.2: Chain walk via OpenCorporates + OCCRP Aleph
       → Cayman LP (Maples Corporate Services) → BVI GP
       → Ultimate: mainland Chinese individual X + State Fund (via SASAC)
  A.3: 12 evidence objects emitted
  B.1-3: All UBO chain members screened
       → Individual X: OFAC clear + EU clear + UK clear + UN clear
       → State Fund: check CFIUS FIRRMA Covered Persons List
         → TIER 2 concern flag (not block but requires CFIUS filing)
  Evidence objects: 17 total (A: 12 + B: 5)

Day 3: Dimensions C + D (Regulatory + Litigation)
  C.1: NMPA CDE history clean (2 IND + 1 clinical trial application)
  C.2: FDA history: Type C meeting 2024 on first-in-class MoA
  D.1: Litigation: 1 active patent infringement claim in Shanghai IP Court
       → obtain local counsel opinion
  D.2: Patent portfolio: 23 granted + 47 pending
  Evidence objects: 21 additional (total: 38)

Day 4: Dimensions E + F (Commercial + Scientific)
  E: No product revenue (preclinical-stage)
  F: 2 pivotal publications + KOL interviews via medsearch
     → MoA novelty confirmed + competitive analysis vs 3 similar assets
  Evidence objects: 11 additional (total: 49)

Day 5: Dimension G (Deal Structure)
  G: 4 comparable deals found (2021-2024)
     Target rNPV: $450M base / $620M bull / $280M bear
     Recommended structure: $50M upfront + $400M milestones + 5-15% royalty
  Evidence objects: 6 additional (total: 55)

Day 6: Step 6 Synthesis + Step 7 Bundle + Step 8 Report
  Overall risk: AMBER
  Recommendation: CONDITIONAL
    - Complete CFIUS pre-notification before LOI
    - Local counsel opinion on Shanghai IP Court exposure
    - Phase 1 dose-finding commitment at target
  Report delivered: bd_dd_shanghai_hypothetical_v1.md
  Risk register: bd_dd_shanghai_hypothetical_risk_register_v1.yaml
  Evidence bundle: bd_dd_shanghai_hypothetical_evidence_bundle.zip
    (55 evidence objects, 247 MB ZIP)

Retention: 7 years per KVKK/GDPR + IRA Foreign Entity of Concern compliance
```

### 5.2 Example: UK biotech licensing DD

```
Day 0: Scoping
  Target: Oxford-based precision oncology biotech
  Deal type: Exclusive worldwide license ex-China for lead asset
  Timeline: Pre-term sheet
  Concerns: UK-EU post-Brexit IP + trial data portability + MHRA alignment

Day 1: Dimensions A + B
  A: Companies House UK PSC register → clean chain
     → 4 institutional investors (25%+ aggregate) + founder (15%) + management (12%)
  B: All cleared
  Evidence objects: 9

Day 2: Dimensions C + D
  C: MHRA registry + FDA pre-IND + EMA SME designation
  D: 12 patent families + ANDA exposure: N/A (early-stage asset)
  Evidence objects: 14

Day 3: Dimensions E + F
  E: Pre-revenue
  F: Phase 1b/2a readout 2024 + Phase 3 readiness
  Evidence objects: 7

Day 4: Dimension G + Synthesis
  G: rNPV $180M-$350M range
  Overall: GREEN
  Recommendation: PROCEED with standard terms
  Evidence objects: 30 total → bundle 89 MB
```

---

## §6. Integration Points

### 6.1 With `sub-protocol-provenance.md` (v5.0.0)

Sub-protocol-bd-dd.md is the **primary caller** of sub-protocol-provenance. BD DD context = automatic forensic-grade mode activation.

### 6.2 With `ubo-source-hierarchy.md` (v5.0.0)

Dimension A explicitly invokes P0→P3 source cascade.

### 6.3 With `task-deal.md`, `task-company.md`, `task-asset.md`

Existing tasks may invoke sub-protocol-bd-dd when deal context detected. Task playbooks provide domain content; sub-protocol-bd-dd orchestrates forensic discipline.

### 6.4 With `sub-protocol-turkey.md`

Turkish target → sub-protocol-turkey provides regulatory + SGK SUT framework; sub-protocol-bd-dd provides DD orchestration. Both chain together.

### 6.5 With TA templates

Dimension F (scientific merit) invokes applicable Layer 2 TA template (oncology / CNS / rare / etc.) for competitive positioning.

### 6.6 With `analytics-framework.md` + `analytics-*.py`

Dimension G invokes NPV + sensitivity + scenario scripts with evidence-object-provenanced inputs (confidence stamping applies).

### 6.7 With `validate-report-discipline.py`

G51-G60 forensic-grade gates enforced across all evidence objects produced by sub-protocol-bd-dd.

---

## §7. Operational Discipline

### 7.1 Minimum viable BD DD

Baseline (non-forensic) BD DD produces:
- Full 7-dimension assessment
- Structured risk register
- Standard pharmaintel report
- **No Evidence Bundle ZIP** (optional in baseline)

Forensic-grade BD DD adds:
- All evidence objects with full custody (TSR + sigstore)
- Evidence Bundle ZIP mandatory
- G51-G60 all BLOCKER-level enforced
- §Appendix B section mandatory

### 7.2 Operator judgment calls

Sub-protocol-bd-dd does NOT replace operator judgment on:
- Final go/no-go decision (sub-protocol recommends; operator decides)
- Deal structure negotiation (sub-protocol informs; deal team executes)
- Risk tolerance calibration (dimension ratings are indicative; risk appetite varies)
- Confidential terms / material non-public information (NEVER captured by sub-protocol — scope exclusion)

### 7.3 Red-lines

- ❌ **MNPI (Material Non-Public Information):** Never captured or stored — pharmaintel operates on public + authorized sources only
- ❌ **Confidential deal data rooms:** Content inside VDRs is outside scope; sub-protocol-bd-dd operates on external + public sources
- ❌ **Active offensive OSINT:** Per sub-protocol-provenance §7.5 — passive GET only
- ❌ **Target employee surveillance:** No capture of individual target employees' social media without explicit KVKK meşru menfaat test passage
- ❌ **Competitive intelligence pretexting:** No impersonation + no direct outreach masquerading as customer/investor

### 7.4 Export control

- **Encrypted target data:** Evidence Bundle ZIP includes compliance flag for ITAR / EAR / US export-controlled technology references
- **CFIUS / FIRRMA flags:** Chinese / Russian / other covered-country exposure triggers flag in risk register
- **Dual-use research of concern (DURC):** Flagged when pathogen + gain-of-function + select agent related target identified

### 7.5 KVKK compliance for Turkish targets

Turkish target BD DD additional discipline:
- KVKK Madde 5/2(ç) meşru menfaat test documented in bundle
- Turkish PEP screening via MASAK + Cumhurbaşkanlığı liste
- Türk Ticaret Sicili Gazetesi PDFs archived with notary publication numbers
- Privacy-preserving redaction for Turkish natural persons (KVKK madde 7 silme hakkı)

---

## §8. Versioning & Changelog

- **v5.0.0 (2026-04-16):** Initial release. Sub-protocol-bd-dd establishes end-to-end BD due diligence orchestration surface. Seven-dimensional target assessment (A: Corporate Structure + UBO; B: Sanctions + PEP Screening; C: Regulatory History across FDA + EMA + PMDA + NMPA + TİTCK; D: Litigation + IP + Patent; E: Commercial Trajectory; F: Scientific Merit; G: Deal Structure Diligence). Workflow orchestration 8 steps (scoping → corporate+sanctions → regulatory+litigation → commercial+scientific → deal-structure → synthesis → bundle → rendering). Parallel-safety annotations per orchestration.md v3.0.0. Primary deliverable BD DD Report with 9-section markdown structure + §Appendix A detailed evidence + §Appendix B forensic bundle manifest. Standalone deliverable Evidence Bundle ZIP per sub-protocol-provenance §4.3. Structured YAML risk register with dimension ratings RED/AMBER/GREEN + critical risks top-3 + strengths top-3 + follow-up actions + evidence bundle reference. Runbook examples (Chinese biotech acquisition CFIUS exposure + UK biotech licensing clean). Integration points with sub-protocol-provenance (primary caller — automatic forensic-grade), ubo-source-hierarchy (Dimension A cascade), task-deal/company/asset (parent workflows), sub-protocol-turkey (Turkish target overlap), TA templates (Dimension F scientific positioning), analytics-framework + analytics scripts (Dimension G rNPV + sensitivity), validate-report-discipline.py (G51-G60 enforcement). Operational discipline (baseline vs forensic-grade + operator judgment preservation for go/no-go + red-lines MNPI/VDR/offensive OSINT/employee surveillance/pretexting exclusion + export control ITAR/EAR/CFIUS/DURC flags + KVKK Turkish target additional discipline). Cross-references: sub-protocol-provenance.md (forensic capture), ubo-source-hierarchy.md (P0-P3), provenance-engine.md (capability framework), evidence-object-schema.md (schema), validate-report-discipline.py (gates).
