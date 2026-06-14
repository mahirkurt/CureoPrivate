# sub-protocol-catalyst-watch.md

**Pharma Catalyst Watch — Event-Specific Discipline Reference (v1.8.0)**

> **Auto-trigger logic (v1.8.0 — generic-by-default discipline):** This sub-protocol auto-loads when the user query explicitly invokes catalyst-watch content (PDUFA, CHMP, AdComm/AdCom, readout, embargo, earnings, guidance, milestone, primary completion, topline, action date) OR when the asset under analysis has a regulatory action or readout within the next 12 months. Trigger is **query-content-based, NOT user-identity-based** per `generic-by-default.md` Article 5.
>
> **FORBIDDEN as triggers:**
> - User's investment portfolio inferences (memory-derived holdings)
> - User's organizational position toward a sponsor (employer competitive interest)
> - User's geography vs catalyst geography matching (location-based inference)

---

## §1. Foundational Stance

Pharmaceutical catalysts are **discrete events** with material informational content for clinical, regulatory, commercial, or financial stakeholders. Each catalyst type has its own:
1. **Source hierarchy** — primary regulatory document → sponsor 8-K/press release → earnings call transcript → analyst note → industry media
2. **Temporal precision discipline** — exact date, calendar-quarter, fiscal-quarter, "year-end" all have different audit weight
3. **Pre-event vs post-event narrative control** — sponsor framing pre-decision vs FDA/EMA factual outcome post-decision
4. **Surprise vs expectation differentiation** — analyst consensus baseline before catalyst → actual outcome → market reaction
5. **Signal vs noise classification** — material information moves NPV; non-material updates do not

Catalyst Watch is NOT predictive forecasting. It is **factual event inventory + outcome documentation + post-event narrative reconciliation** with documented provenance and confidence stamping per `triangulation.md`.

---

## §2. PDUFA / FDA Action Date Discipline

### 2.1 Date precision categories

FDA action dates have **three distinct precision tiers** that must be preserved:

| Tier | Format | Example | Precision |
|---|---|---|---|
| **Goal Date (target)** | YYYY-MM-DD | "PDUFA goal date 2026-08-15" | Exact day; sponsor-disclosed at acceptance |
| **Calendar Quarter** | "Q3 2026" | "FDA decision expected Q3 2026" | ±3 month range; sponsor or analyst use |
| **Decision Date (actual)** | YYYY-MM-DD | "FDA approved 2026-07-22" | Exact day; FDA Drugs@FDA / press primary |

**Discipline:** When a report cites a PDUFA date, the precision tier MUST be preserved literally. Converting "Q3 2026" to "September 30, 2026" is a fabrication of false precision. Converting "August 15, 2026" to "Q3 2026" is loss of available precision.

### 2.2 Review pathway timeline differentiation

| Pathway | Standard timeline (post-acceptance) | Notes |
|---|---|---|
| **Standard Review** | 10 months | Default for non-priority NDA/BLA |
| **Priority Review** | 6 months | Granted for substantial improvement over existing therapy |
| **Real-Time Oncology Review (RTOR)** | Variable, often <6 months | Pilot for oncology applications; submission-during-data-finalization |
| **Accelerated Approval** | Standard or Priority timeline | Approval based on surrogate endpoint; confirmatory trial required |
| **Breakthrough Therapy Designation (BTD)** | Does not change PDUFA date | Confers intensive guidance + RTOR eligibility |
| **Type A meeting** | Goal: 30 days post-FDA receipt of meeting request | Pre-NDA dispute resolution context |

**Discipline:** PDUFA date alone does NOT indicate approval probability. Pathway type provides additional context. Avoid conflating "Priority Review granted" with "approval probable" — these are distinct.

### 2.3 BLA/NDA/sBLA serial numbering

FDA application numbering has structure:

| Format | Meaning | Example |
|---|---|---|
| **NDA-XXXXXX** | Original NDA | NDA 217564 (FRUZAQLA) |
| **BLA-XXXXXX** | Original BLA (biologic) | BLA 761139 (Enhertu) |
| **sNDA / sBLA** | Supplemental — efficacy or safety supplement | NDA 761139s028 (Enhertu boxed warning revision) |
| **Type II variation (EU)** | EMA equivalent of sNDA | EMA/CHMP/12345/2025 |

**Discipline:** When citing application context, use the FULL serial number including supplement designator. "BLA 761139s028" not "BLA 761139". This precision matters for label history reconstruction.

### 2.4 Common PDUFA failure modes

- **Missed-by-X-days:** FDA may complete review after the goal date with no formal "missed PDUFA" event; treat as routine variance unless >30 days late
- **Goal date pushed:** FDA may extend PDUFA up to 3 months for major amendment review; always extension is sponsor-disclosed
- **CRL (Complete Response Letter):** Not approval, not rejection — outlines deficiencies requiring resubmission
- **AdComm requirement late-added:** Extends timeline 1-2 months; signal of FDA uncertainty

---

## §3. CHMP / EC Opinion Discipline

### 3.1 Two-stage decision structure

EU centralized procedure has TWO distinct events that are often conflated:

| Stage | Authority | Output | Lag from prior stage |
|---|---|---|---|
| **CHMP positive opinion** | Committee for Medicinal Products for Human Use | Recommendation; binding for EC adoption | T0 (stage 1) |
| **CHMP Highlights publication** | EMA Communications | Public press summary | Same day or next business day |
| **EPAR (full assessment)** | EMA | Detailed scientific dossier | T+30-90 days post-EC approval |
| **EC Marketing Authorization** | European Commission | Legal authorization across EU | T+~67 days from CHMP opinion (per EU rules) |

**Discipline:** "EU approval" colloquially refers to BOTH CHMP opinion AND EC adoption. In a pharmaintel report, BOTH dates must be preserved separately:
- CHMP opinion: scientific recommendation date (e.g., "25 April 2024")
- EC adoption: legal market authorization date (e.g., "20 June 2024")

The 67-day Commission decision lag is rule-based; EC almost always follows CHMP opinion.

### 3.2 Type II Variation pattern

Post-authorization changes (new indication, new dosing, new safety) flow through Type II Variation:
- **EMA/CHMP/XXXXX/YYYY** number format (sequential per asset)
- Submitted by MAH, validated by EMA, reviewed by CHMP
- Outcome: positive opinion → EC implementing decision → SmPC update
- Timeline: 60-90 days for clinical trial efficacy variation; faster for safety updates

### 3.3 Scientific Advice (pre-submission)

CHMP Scientific Advice is **non-binding pre-submission consultation** between sponsor and EMA. References to "EMA agreed with X" should distinguish:
- **Scientific Advice** — pre-submission, advisory, non-binding
- **Pre-submission meeting** — operational logistics
- **MAA validation** — formal application acceptance
- **Day 80 / Day 120 / Day 180 questions** — review milestones

---

## §4. Clinical Readout Discipline

### 4.1 Major medical congress embargo calendar (annual)

| Congress | Approximate window | Embargo characteristics |
|---|---|---|
| **AACR (American Association for Cancer Research)** | April | Preclinical + early clinical onkoloji emphasis; Phase 1 readouts |
| **ASCO (American Society of Clinical Oncology)** | Late May/June | Largest oncology readout window; pivotal Phase 3 emphasis |
| **EHA (European Hematology Association)** | June | Hematology-spesifik; CAR-T, bispecific, immune therapy emphasis |
| **ESMO (European Society for Medical Oncology)** | September/October | Second-largest onkoloji window; presidential sessions |
| **ASH (American Society of Hematology)** | December | Largest hematology window; multiple myeloma, leukemia, lymphoma |
| **AHA (American Heart Association)** | November | Kardiyovasküler |
| **EASD (European Association for the Study of Diabetes)** | September | Diyabet/metabolik |
| **ADA (American Diabetes Association)** | June | Diyabet/metabolik |
| **AAN (American Academy of Neurology)** | April/May | Nöroloji |
| **CTAD (Clinical Trials on Alzheimer's Disease)** | November | Alzheimer-spesifik |

**Embargo discipline:** Pre-congress sponsor "topline" announcement (8-K) typically precedes congress oral presentation by 6-12 weeks. Discipline:
- **Topline (sponsor 8-K):** Hit/miss + headline HR + p-value; secondary endpoint summary
- **Oral presentation (congress):** Full primary + key secondary breakdown; subgroup analyses; safety detail
- **Peer-reviewed publication:** Full data + statistical methodology + supplementary appendix

Citing "FRESCO-2 mPFS HR 0.32" requires the publication source (Lancet 2023), not the sponsor 8-K, as the primary citation. Sponsor 8-K is an intermediate disclosure.

### 4.2 Primary vs secondary endpoint hierarchy

Modern Phase 3 trials use **sequential hierarchical testing** to control multiplicity:

```
Primary Endpoint (P)
    ↓ (only if P significant)
Key Secondary 1 (KS1)
    ↓ (only if KS1 significant)
Key Secondary 2 (KS2)
    ↓
Other Secondaries (OS) — descriptive only, no formal hypothesis testing
```

**Discipline:** When a trial's PFS (primary) hits but OS (key secondary) shows trend without significance, this is "PFS positive, OS immature" — NOT "OS hit". Sequential hierarchy means downstream endpoints are exploratory if upstream fails.

### 4.3 Hit-vs-miss interpretation pitfalls

| Outcome category | Material interpretation |
|---|---|
| **Statistically significant + clinically meaningful** | "Positive readout"; supports approval |
| **Statistically significant + small magnitude** | "Statistical hit, clinical relevance debate"; HTA risk |
| **Numerical improvement, not statistically significant** | "Failed primary endpoint"; do NOT call "trended positive" |
| **Pre-specified subgroup positive, ITT negative** | "Subgroup signal, ITT failed"; future trial design implication |
| **Crossover-confounded OS** | "OS confounded by post-progression therapy"; discount OS interpretation |

---

## §5. AdComm / AdCom Discipline

### 5.1 FDA Advisory Committee structure

Advisory Committees (AdComm/AdCom) are **non-binding expert panels** that vote on FDA decisions. Common types:

| Committee | Therapeutic area | Frequency |
|---|---|---|
| **ODAC (Oncologic Drugs Advisory Committee)** | Oncology | 4-6 meetings/year |
| **CRDAC (Cardiovascular and Renal Drugs Advisory Committee)** | CV/renal | 2-4 meetings/year |
| **PCNS (Peripheral and Central Nervous System Drugs Advisory Committee)** | Neurology/psychiatry | 2-4 meetings/year |
| **Pulmonary-Allergy** | Respiratory/allergy | 1-3 meetings/year |
| **Antimicrobial** | Infectious disease | 2-4 meetings/year |
| **Endocrinologic and Metabolic** | Endocrine/metabolic | 1-3 meetings/year |
| **GI** | Gastroenterology | 1-3 meetings/year |

### 5.2 Vote interpretation

AdComm vote outcomes have specific reporting conventions:
- **"X to Y in favor of approval"** — straightforward positive recommendation
- **"X to Y against approval"** — negative recommendation (sponsor warning)
- **"X to Y in favor of confirmatory study"** — approval with post-marketing requirement
- **"X to Y to recommend further analysis"** — punt; FDA decision still pending
- **Abstentions and recusals** — must be reported (e.g., "10-2-1" = 10 yes, 2 no, 1 abstain)

### 5.3 Vote vs FDA decision divergence

FDA is NOT bound by AdComm vote. Historical patterns show:
- ~75% of negative AdComm votes result in FDA non-approval (not 100%)
- ~95% of positive AdComm votes result in FDA approval
- Notable divergence cases: Aducanumab (AdComm 0-10-1 against; FDA approved June 2021); Casimersen (AdComm split; FDA approved); MyoKardia mavacamten (AdComm 9-0 in favor; FDA delayed for REMS)

**Discipline:** Pre-AdComm "background package" (FDA briefing document released ~2 days before meeting) often signals FDA reviewer concerns. Background package skepticism + AdComm negative vote = high non-approval probability. Background package supportive + AdComm split = approval still likely.

### 5.4 Background package timing

| Document | Public release | Significance |
|---|---|---|
| **AdComm meeting announcement** | ~30 days before | Sets meeting date, topic |
| **FDA Briefing Document** | ~2 days before meeting | FDA reviewer concerns surfaced |
| **Sponsor Briefing Document** | ~2 days before meeting | Sponsor counter-argument |
| **Live meeting webcast** | Day of meeting | Public observation |
| **Vote outcome** | End of meeting | Released same day |
| **FDA decision (final)** | T+~30-90 days | PDUFA goal date determines |

---

## §6. Earnings / Analyst Day Discipline

### 6.1 Guidance change framework

Public companies issue forward financial guidance with specific patterns:

| Guidance action | Material interpretation |
|---|---|
| **Raised guidance** | Positive signal; analyst consensus revisions upward |
| **Reaffirmed guidance** | Neutral; no surprise either direction |
| **Cut/lowered guidance** | Negative signal; warrants explanation in earnings call |
| **Withdrew guidance** | Significant negative signal (uncertainty); often M&A or major event |
| **Initiated guidance** | First-time guidance; baseline reset |

### 6.2 Currency normalization

Pharma multinationals report in functional currency (USD, JPY, CHF, EUR, GBP). Key disciplines:
- **At Constant Exchange Rates (CER):** Excludes FX; reflects underlying volume × price × mix
- **At Actual Rates:** Includes FX; reflects realized P&L impact
- **Reporting currency vs functional currency:** Different impacts

**Discipline:** When citing growth rates, specify CER or actual. "ELUNATE +%7" without specification → "ELUNATE +%7 (+%9 at CER)" if CER preferred (less FX noise).

### 6.3 Revenue recognition nuance

| Revenue type | Recognition trigger | Pharmaintel note |
|---|---|---|
| **Net product sales** | Sale to wholesaler/distributor | Standard top-line |
| **Royalty revenue** | Net sales × royalty rate; per agreement | Contractual; lagging recognition |
| **Milestone payment** | Achievement event (regulatory or sales threshold) | Lumpy; one-time |
| **Upfront license fee** | Deal closing | One-time; deferred over service period |
| **Manufacturing supply revenue** | Drug product delivery to partner | Pass-through; lower margin |

**Discipline:** Hutchmed's "consolidated $86.3M for ELUNATE" vs "$115M in-market sales" reflects revenue recognition (manufacturing supply + service fees + royalties = ~%75 of in-market) not commercial weakness. This nuance matters for analyst NPV models.

### 6.4 Analyst Day signal interpretation

Investor day / R&D day events have characteristic patterns:
- **New peak sales projections** — sponsor-set forward guidance; high optimism bias
- **Pipeline reprioritization** — discontinued programs vs accelerated programs; net-effect material
- **M&A signaling** — capital allocation framework; "we will be opportunistic" boilerplate vs specific TA focus
- **Guidance reaffirmation/raise/cut** — same conventions as quarterly earnings

---

## §7. Catalyst Calendar Construction

A catalyst watch report's §9 Near-Term Catalysts table follows this structure:

| Tarih (precision per §2.1) | Olay (catalyst type per §1) | Impact (on NPV / treatment paradigm) |

**Discipline:**
- **Date format:** Use highest available precision; never invent precision
- **Olay format:** Type + asset/program + sponsor (if relevant) + brief context
- **Impact format:** Material consequence on stakeholder decision-making; avoid speculation about share price movement (financial advice territory)

Example (good):
> | 2026-08-15 | DESTINY-Breast05 BLA Type II variation FDA goal date (post-neoadjuvan eBC) | T-DXd küratif-niyet eBC pazara giriş; Roche-perspective Kadcyla franchise erozyonu accelerator |

Example (bad):
> | Q3 2026 | DB-05 approval likely | T-DXd revenue boost expected |

(Bad examples: precision degradation, predictive language, speculation, no source attribution)

---

## §8. Confidence stamping for catalysts

Catalyst-derived claims have specific confidence patterns:

| Claim type | Default confidence |
|---|---|
| Past regulatory action (date, outcome, indication) | **High** (FDA Drugs@FDA / EMA EPAR primary) |
| Past pivotal readout (HR, p-value, sample) | **High** (peer-reviewed publication primary) |
| Future PDUFA goal date (sponsor-disclosed at acceptance) | **High** (8-K primary) |
| Future readout topline expected timing | **Medium** (sponsor guidance; may slip) |
| Analyst consensus on catalyst impact | **Medium** (synthesis; not statutory) |
| Speculated outcome of pending decision | **Low** (forward-looking; should be flagged as such) |

---

## §9. Forbidden patterns (per generic-by-default.md Article 2)

In a Catalyst Watch report:
- ❌ "[User Employer] for this catalyst should..." — strategic action recommendation contamination
- ❌ "Catalyst impact on [User Employer] portfolio: ..." — user-context anchoring
- ❌ "Investment thesis: buy/sell on this catalyst" — financial advice territory; not pharmaintel scope
- ❌ Speculating on share price reaction without quantitative basis

**Permitted:**
- ✅ "Incumbent franchise sponsorları için catalyst impact: ..." — abstract stakeholder
- ✅ "Late-entrant sponsorlar için differentiation alanı kısıtlanır: ..." — abstract stakeholder
- ✅ "Payer paydaşlar için catalyst sonrası HTA aktivite: ..." — abstract stakeholder
- ✅ "Patient stakeholder için access timing: ..." — abstract stakeholder

---

## §10. Integration with parent task

Catalyst Watch sub-protocol enriches:
- **T1 Company Deep-Dive** §6 Catalyst section
- **T2 Asset Profile** §9 Near-Term Catalysts section
- **T3 Modality Landscape** asset-level catalyst pipeline
- **T5 Catalyst Watch (standalone task)** entire report
- **T6 Head-to-Head** competitive catalyst timing comparison

When Catalyst Watch sub-protocol is loaded, the §9 / §catalyst section MUST conform to §7 calendar construction rules and §8 confidence stamping.

---

## §11. Versioning & changelog

- **v1.8.0 (2026-04-15):** Initial release. Added 11 sections covering 5 catalyst types (PDUFA, CHMP, readout, AdComm, earnings) with event-spesifik discipline references. Trigger logic query-content-based per generic-by-default.md Article 5. Forbidden patterns enumerated per Article 2. Integration points with T1/T2/T3/T5/T6 task playbooks specified.
