# pharmaintel — T2: Asset / Molecule Profile Playbook

## Scope

Single-asset deep-dive: mechanism, regulatory status, clinical data, competitive position, commercial trajectory. Often invoked alongside medsearch (scientific evidence) — this task focuses on the **commercial-regulatory-pipeline frame**.

## Deliverable structure

```
# [INN / Brand / Development Code] — Asset Profile

## 0. Identity
  - INN, brand name(s) by region, development code, target, modality, sponsor

## 1. Mechanism (brief — defer depth to medsearch)
  - Target biology
  - Modality class

## 2. Regulatory status (primary focus; see also sub-protocol-label.md for label semantic extraction + FAERS)
  - FDA: approval date(s), indication(s), label nuances, boxed warnings (fetch full label via DailyMed)
  - EMA: CHMP opinion + Commission decision, indication, SmPC highlights (fetch via EPAR)
  - Other major regions: Japan PMDA (sub-protocol-pmda.md), China NMPA, Health Canada, MHRA, TGA

## 3. Clinical development
  - Pivotal trials (NCT, design, n, endpoints, outcomes)
  - Current Phase 3 / registrational trials (in-progress)
  - Earlier-phase expansion trials
  - Investigator-initiated trials of note

## 4. Safety profile
  - Boxed warnings, contraindications, REMS
  - Key adverse events from label
  - Post-marketing signals (FAERS, EudraVigilance)

## 5. Competitive position
  - Direct competitors (same indication + similar modality)
  - Differentiation (efficacy, safety, route, dosing, patient population)
  - Place in treatment pathway

## 6. Commercial trajectory
  - Reported sales (if available from sponsor 10-K/10-Q)
  - Growth trend
  - Geographic split

## 7. Payer & HTA landscape
  - NICE TA / CADTH / ICER assessments
  - Any public reimbursement constraints

## 8. IP position
  - Orange Book / Purple Book patents + exclusivity
  - Generic / biosimilar threats
  - LOE horizon

## 9. Near-term catalysts
  - Upcoming PDUFA / CHMP
  - Readouts in next 12 months
  - Indication-expansion studies

## 10. Limitations & gaps
```

---

## Phase 1 — Terminology glossary (CRITICAL for asset work)

For every asset, build the glossary before any search:
- **INN:** e.g., trastuzumab deruxtecan
- **Brand:** Enhertu (US/EU), other regional names
- **Development code(s):** DS-8201, DS-8201a, T-DXd
- **Target:** HER2; modality = ADC (antibody-drug conjugate); payload = deruxtecan (topoisomerase I inhibitor)
- **Sponsor:** Daiichi Sankyo (developer); AstraZeneca (co-commercialisation)

Every downstream query uses these synonyms in OR combination. Missing synonyms = missed hits.

---

## Phase 2 — Discovery

Parallel:

1. **FDA Drugs@FDA** search (brand + INN) → approval record
2. **EMA medicines search** (brand + INN) → EPAR
3. **ClinicalTrials.gov MCP**: `intervention=<INN|brand|code>` (all phases, all statuses)
4. **WHO ICTRP + CTIS** (via Fetch) for non-US trials
5. **PubMed MCP**: `"<INN>"[Substance Name]` with date filter for pivotal / latest
6. **Tavily** (news, 90d): `"<brand OR INN> FDA OR phase 3 OR label"`
7. **Paper Search** (broad): `<INN>`
8. **Consensus MCP**: `"What is the efficacy of <INN> in <indication>?"` — for rapid evidence framing
9. **Google Patents**: assignee = sponsor + INN-linked claims
10. **Orange Book / Purple Book**: lookup by brand name

---

## Phase 3 — Deep-dive (primary sources)

### 3.1 Regulatory status

1. **FDA approval letter** — `https://www.accessdata.fda.gov/drugsatfda_docs/appletter/<year>/<appno>ltr.pdf`
2. **FDA current label (SPL)** via DailyMed — reads as PDF or structured data
3. **FDA Medical Review** — released 3-6mo post-approval; contains reviewer's critical assessment of pivotal data
4. **FDA Clinical Pharmacology Review** — PK/PD, dosing rationale
5. **EMA EPAR** — full scientific assessment; read "Assessment Report" PDF
6. **EMA Risk Management Plan (RMP)** summary — reveals agency-identified risks

Cross-check sections:
- Indication wording (often narrower than company claims)
- Approval conditions (accelerated approval? confirmatory study required?)
- Label differences US vs EU (common; e.g., EU often narrower)

### 3.2 Clinical development

1. **Pivotal trial NCT pages** (ClinicalTrials.gov) — design, enrolment, actual endpoints
2. **Pivotal publications** — NEJM / Lancet / JAMA / JCO / Blood for top-tier assets
3. **Conference presentations** — ASCO/ESMO/ASH/EHA abstracts and orals
4. **Latest investor deck** (sponsor IR) — integrated view of all trials
5. **10-K §Pipeline** section — regulatory milestones

### 3.3 Safety

1. **Current FDA label** → Boxed Warning, Contraindications, Warnings and Precautions, Adverse Reactions, Postmarketing Experience
2. **EMA SmPC** → Section 4.3 (contraindications), 4.4 (warnings), 4.8 (adverse reactions)
3. **FAERS Public Dashboard** — query drug name, review top reported events
4. **EudraVigilance (adrreports.eu)** — EU signal view
5. **VigiAccess** — WHO global signal view
6. **Post-marketing requirement studies** — FDA requires for many accelerated approvals; check FDA site for PMR/PMC status

### 3.4 Competitive position

1. **PubMed** for direct head-to-head trials: `("<INN1>" AND "<INN2>")[Title/Abstract]`
2. **ClinicalTrials.gov** for ongoing direct comparisons
3. **Guideline citations** — NCCN (oncology), ESMO, ACC/AHA, EASL, KDIGO, ADA — position in treatment algorithm
4. **IQVIA Institute free reports** for modality-level context

### 3.5 Commercial trajectory

1. Sponsor 10-K / 10-Q segment or product revenue disclosure
2. Earnings-call Q&A for forward guidance
3. For reported quarterly sales, build a time series
4. For geographic split, read segment footnotes
5. If IQVIA Institute has a free report covering the asset's class, extract context

### 3.6 Payer / HTA

1. NICE TA search — `nice.org.uk/guidance`
2. ICER assessment search — `icer.org/assessment`
3. CADTH — `cadth.ca/search`
4. SMC / AWMSG for Scotland / Wales
5. PBAC for Australia
6. G-BA for Germany (English summaries)

### 3.7 IP

1. Orange Book (small molecule) or Purple Book (biologic) entry
2. Linked patents → Google Patents for full text
3. Paragraph IV list (if NDA small molecule) — generic challenges
4. PTAB IPR — validity challenges in force
5. Exclusivity calendar — approval date + NCE/orphan/pediatric exclusivity

### 3.8 Catalysts

1. ClinicalTrials.gov: active Phase 3 with primary completion in next 12mo
2. Sponsor guidance from most recent earnings call
3. FDA Advisory Committee Calendar (if AdComm expected)
4. CHMP agenda (upcoming meeting items — usually revealed 1mo ahead)

---

## Phase 4 — Triangulation

- **Regulatory status** → §2.2
- **Pivotal readouts** → §2.1
- **Safety claims** → label + FAERS + publication; no single secondary stands alone
- **Commercial** → §2.4 (10-K/10-Q + earnings + inference)
- **IP** → Orange/Purple Book + patent primary + PTAB

## Phase 5 — Report

Per `assets/report-template.md`, asset profile version. Every claim stamped.

---

## Adaptations

### Pre-launch / pending approval

Asset not yet approved:
- Pivotal data from publications + conference + company press releases
- PDUFA / CHMP timing from company guidance + SEC 8-K
- Commercial forecast unknown (no revenue yet); approximate via class/indication precedent

### Combination products

If the asset is a combination (e.g., ADC + checkpoint inhibitor):
- Profile each component + the combination separately
- Regulatory status may differ for each component vs the combo

### Biosimilars

If profiling a biosimilar:
- Purple Book interchangeability status is the core regulatory fact
- Reference product regulatory history provides context
- Pricing / contracting dynamics drive commercial; consult free CMS data
- Biosimilar Report from IQVIA Institute (free) for class-level context
