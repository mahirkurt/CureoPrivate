# pharmaintel — HTA Deep-Dive Reference

## Scope

Health Technology Assessment (HTA) intelligence for major markets — methodology, agency-specific decision frameworks, public document taxonomy, free-tier access strategy, and triangulation patterns. Loaded on demand when:

- User asks "is X reimbursed in Y country" / "what did NICE decide about Z" / "HAS SMR/ASMR for [asset]"
- T2 Asset Profile or T4 Deal/M&A includes access/pricing layer
- T6 Head-to-Head Comparison specifies HTA implications
- Any query involves the words "HTA", "reimbursement", "geri ödeme", "payer", "cost-effectiveness", "ICER threshold", "G-BA benefit", "SMR", "ASMR"

This reference complements `sources-catalog.md §HTA` (catalog of URLs) and `triangulation.md §3` (conflict hierarchy for regulatory-vs-HTA discordance).

---

## Free-tier access map per agency

| Agency | Country/Region | Free-tier documents | What's paid / gated | Typical fetch target |
|---|---|---|---|---|
| **NICE** | England/Wales (UK) | Technology Appraisals (TA) Final Appraisal Documents (FAD), committee papers, Evidence Review Group (ERG) reports, public stakeholder comments | Full confidential appendices (patient-level data, commercial-in-confidence pricing) | `nice.org.uk/guidance/ta[N]` |
| **CADTH** | Canada | pCODR/CDR Final Recommendation, Reimbursement Review reports, clinical + economic review reports | Commercial pricing, confidential pCPA negotiations | `cadth.ca/[drug-name]` |
| **G-BA (IQWiG)** | Germany | IQWiG Dossier assessment (primarily German; machine translate), G-BA decision (Nutzenbewertung), G-BA Tragende Gründe | AMNOG post-negotiation price (redacted); PAS data | `g-ba.de/bewertungsverfahren/nutzenbewertung/[N]` and `iqwig.de/projekte/` |
| **HAS (Transparency Commission)** | France | Avis (SMR + ASMR classification), Commission Economique public opinions, HAS website publishes full Avis | CEPS price negotiation detail; confidential rebates | `has-sante.fr/jcms/[id]` |
| **PBAC** | Australia | Public Summary Document (PSD), Minutes (redacted), PBS listing | Deed of agreement detail; confidential rebates | `pbs.gov.au/info/industry/listing/elements/pbac-meetings/psd/[date]` |
| **CDE** | Taiwan | Health Technology Assessment reports, NHIA decisions | — | `nhi.gov.tw` |
| **HIRA** | South Korea | Benefit determination reports (Korean-primary; summary in English sometimes available) | Risk-sharing agreement detail | `hira.or.kr` |
| **ZIN** | Netherlands | GVS advies + ZIN package advice | — | `zorginstituutnederland.nl` |
| **TLV** | Sweden | Beslut (decisions) + underlag (rationale) | — | `tlv.se` |

**Access principle:** Every decision document listed above is publicly available at zero cost. Commercial-in-confidence pricing and patient-level sub-analyses are gated — pharmaintel explicitly flags these as `[INACCESSIBLE — commercial-in-confidence]` rather than approximating them.

---

## Decision frameworks — how each agency thinks

### NICE (England/Wales)

**Core question:** Is this cost-effective at the ICER threshold?

- **Threshold:** £20,000–£30,000 per QALY gained is the standard range; up to £50,000/QALY for end-of-life criteria; up to £100,000–£300,000/QALY for Highly Specialised Technologies (HST)
- **Key metrics reported:** Incremental Cost-Effectiveness Ratio (ICER), QALYs gained, deterministic + probabilistic sensitivity analyses
- **Key document:** Final Appraisal Determination (FAD) → Technology Appraisal Guidance (TA) number
- **Outcome types:** Recommended / Recommended with restrictions / Only in research (OIR) / Not recommended
- **Managed access:** Cancer Drugs Fund (CDF) for oncology with data uncertainty; Innovative Medicines Fund (IMF) for non-oncology
- **Appeal window:** 15 working days post-FAD

**What to extract for a pharmaintel report:**
1. TA number + date of FAD
2. Recommended/not outcome
3. Population scope (full label vs restricted subgroup)
4. ICER point estimate if published (often presented as a range to protect commercial pricing)
5. Managed access entry: CDF/IMF? For how long?
6. Key ERG critique themes (indirect comparison quality, utility mapping, time horizon)

### CADTH (Canada)

**Core question:** Does clinical + economic evidence support reimbursement, and at what price does cost-effectiveness become acceptable?

- **Threshold:** Generally $50,000/QALY referenced but not formally binding; cancer typically accepts higher
- **Key output:** pCODR (oncology) or CDR (non-oncology) Final Recommendation; recently consolidated into "Reimbursement Review"
- **Outcome types:** Reimburse / Reimburse with conditions / Do not reimburse at submitted price
- **Post-CADTH step:** pCPA (pan-Canadian Pharmaceutical Alliance) negotiates confidential price with sponsor; provincial formulary listing follows
- **Re-review:** Available if new evidence emerges

**What to extract:**
1. Reimbursement Review ID + recommendation date
2. Outcome (recommend/conditional/negative)
3. Conditions of reimbursement (starting criteria, stopping criteria, renewal, specialist prescribing requirement)
4. Price reduction required (% range sometimes stated)
5. Confidence in clinical evidence as stated by CADTH methods committee

### G-BA / IQWiG (Germany)

**Core question:** What is the additional benefit (Zusatznutzen) vs appropriate comparator therapy (zweckmäßige Vergleichstherapie, ZVT)?

- **Unique framework:** Germany does NOT use ICER/QALY thresholds. Assessment is **additional benefit classification** against ZVT:
  - Major (erheblich)
  - Considerable (beträchtlich)
  - Minor (gering)
  - Non-quantifiable (nicht quantifizierbar)
  - No additional benefit demonstrated (nicht belegt)
  - Less benefit (geringerer Nutzen)
- **Sequence:** Sponsor submits dossier → IQWiG assesses (typically in German) → G-BA publishes Nutzenbewertung → AMNOG price negotiation with GKV-Spitzenverband based on benefit class
- **Language challenge:** IQWiG dossier assessments are primarily German; G-BA decisions include English summaries but tragende Gründe (supporting rationale) are German. Fetch with translation is often required.
- **Timeline:** 6 months from launch to G-BA decision; AMNOG price takes effect in month 13

**What to extract:**
1. G-BA decision date + Nutzenbewertung ID
2. Additional benefit classification (per subgroup if stratified)
3. ZVT identified (which comparator the sponsor's drug is being judged against)
4. IQWiG-G-BA discordance if any (e.g., IQWiG said "not proven," G-BA upgraded to "minor")
5. Subgroup analyses that drove the classification

### HAS (France — Transparency Commission)

**Core question:** Actual clinical benefit (SMR) + improvement over existing treatments (ASMR)?

- **SMR (Service Médical Rendu):** Major / Important / Moderate / Low / Insufficient — drives reimbursement level (15–65–100%)
- **ASMR (Amélioration du Service Médical Rendu):** I (major) / II (important) / III (moderate) / IV (minor) / V (none)
- **Economic evaluation:** Commission Evaluation Economique (CEESP) conducts for drugs claiming ASMR I–III or with budget impact >€20M/year
- **Publication:** Avis (opinion) published on HAS website; full text, typically French but English abstract sometimes available

**What to extract:**
1. Avis date + reference
2. SMR classification (drives reimbursement %)
3. ASMR classification (drives pricing latitude)
4. Population(s) assessed (often stratified)
5. CEESP opinion (if economic assessment done)
6. Comparator judged (HAS names the reference treatment explicitly)

### PBAC (Australia)

**Core question:** Clinical + cost-effectiveness + opportunity cost at the submitted price?

- **Threshold:** ~AUD 45,000–75,000/QALY commonly observed, varies by disease severity
- **Output:** Public Summary Document (PSD) per meeting
- **Outcome types:** Recommended / Rejected / Deferred / Not Recommended
- **Re-submission:** Common — often takes 2–4 cycles with price and subgroup adjustments
- **Post-PBAC step:** PBS (Pharmaceutical Benefits Scheme) listing with Deed of Agreement (confidential)

**What to extract:**
1. PBAC meeting date + PSD reference
2. Outcome
3. Key committee critique (typically: comparator choice, ICER uncertainty, PBS budget impact)
4. Resubmission count (if not first pass)
5. Listed restriction (PBS streamlined authority, specialist-only, etc.)

---

## Triangulation patterns specific to HTA

### Pattern A — multi-HTA landscape for a single asset

**When used:** T2 Asset Profile with payer/access layer

**Minimum quartet per HTA region:**
1. Agency decision document (FAD, Final Recommendation, Nutzenbewertung, Avis, PSD)
2. Date of decision
3. Outcome classification (per agency's own rubric)
4. One explicit reference to the patient population and restriction language

**Confidence rating:**
- All 4 present from the primary agency document → High
- 3 of 4 (typically missing population granularity because it's in a long confidential appendix) → Medium
- Outcome known only via media coverage without locating agency document → Medium, flag "agency document fetch required"

### Pattern B — NICE TA timeline reconstruction

**When used:** Catalyst watch (T5) for upcoming NICE decisions

- Check NICE "In development" page for the TA number
- Scoping workshop date → first committee meeting date → appraisal consultation document (ACD) date → FAD expected ~6–8 weeks post-ACD
- FAD publication is the catalyst; ACD can also move markets

### Pattern C — cross-HTA discordance analysis

**When used:** H2H T6 comparisons where two agencies reached different outcomes

Common discordance sources:
1. **Comparator choice.** G-BA names ZVT explicitly; NICE/CADTH allow sponsor choice within reason; HAS specifies. An asset compared against placebo at one agency vs active comparator at another will look very different.
2. **Threshold applicability.** NICE £20–30K rigid; PBAC more flexible on disease severity; CADTH consultative; G-BA has none.
3. **Evidence acceptance.** IQWiG famously strict on indirect comparisons; NICE more lenient with good-quality ITC/MAIC.
4. **Timing of decision.** A 2022 NICE decision on the same asset as a 2025 G-BA decision reflects different evidence bases (additional trials, RWE) — age-adjust claims.

---

## Red flags in HTA analysis

1. **Quoting "NICE approved X" without distinguishing full approval vs CDF/IMF vs restricted.** These are very different access realities.
2. **Treating G-BA "not proven" as equivalent to NICE "not recommended."** G-BA "not proven" often triggers AMNOG reference price rather than outright non-reimbursement.
3. **Citing an ICER point estimate without the sensitivity range.** Agencies report ICER ranges with commercial-in-confidence masking; point estimates are often misleading.
4. **Treating HAS SMR "insufficient" as equivalent to a rejection.** SMR insufficient means no reimbursement but does not preclude private market access.
5. **Assuming PBAC reject = market closed.** Resubmission is the norm; 2–4 cycles is typical before listing.
6. **Comparing HTA outcomes across time zones without aging the evidence.** A 2022 rejection on early-phase data vs 2026 re-submission with Phase 3 readout are separate conversations.

---

## Turkey (TİTCK / SGK) — explicitly out of scope

**This reference does NOT cover Turkey's TİTCK regulatory approval or SGK/SUT reimbursement.** These are handled by separate workflows. When a user requests Turkish HTA analysis, route to a dedicated sub-query flagged `[TR-HTA]` — pharmaintel's current global HTA module does not model Türkiye.

This is a known and deliberate scope limitation, noted in `§Limitations` of any HTA-layer output.

---

## Typical output structure when HTA layer is included

```markdown
## HTA Landscape (selected key markets)

### NICE (UK)
> Agency: NICE · Decision: TA[N] · Date: YYYY-MM-DD · Confidence: [H/M/L]
- Outcome: [Recommended / Recommended with restrictions / Not recommended / CDF / IMF]
- Population: [full label / restricted to subgroup X]
- ICER: [£N/QALY or "range published in FAD"]
- Key ERG critiques: [bulleted]
- [URL to FAD]

### CADTH (Canada)
> Agency: CADTH · Decision: pCODR-[ID] · Date: YYYY-MM-DD · Confidence: [H/M/L]
- Outcome: [Reimburse / Reimburse with conditions / Do not reimburse]
- Conditions: [starting criteria / renewal / specialist / price reduction required]
- [URL to recommendation]

### G-BA (Germany)
> Agency: G-BA · Decision: [Nutzenbewertung ID] · Date: YYYY-MM-DD · Confidence: [H/M/L]
- Additional benefit: [Major / Considerable / Minor / Non-quantifiable / Not proven / Less benefit] per subgroup
- ZVT (comparator): [named]
- IQWiG-G-BA discordance: [Y/N; if Y, describe]
- [URL to G-BA page; IQWiG dossier page]

### HAS (France)
> Agency: HAS · Decision: Avis [ref] · Date: YYYY-MM-DD · Confidence: [H/M/L]
- SMR: [Major / Important / Moderate / Low / Insufficient]
- ASMR: [I / II / III / IV / V]
- Population: [...]
- [URL to Avis]

### PBAC (Australia)
> Agency: PBAC · Decision: [meeting date PSD ref] · Confidence: [H/M/L]
- Outcome: [Recommended / Rejected / Deferred]
- Resubmission count: [N]
- Listed restriction: [...]
- [URL to PSD]

## HTA cross-read
- Any cross-agency discordance and probable reason (comparator, threshold, evidence age)
- Implications for multi-market launch sequencing
```

---

## Cross-reference

- `sources-catalog.md §HTA` — full URL catalog
- `triangulation.md §3` — conflict resolution hierarchy (regulatory > HTA > peer-reviewed)
- `task-asset.md §Payer access layer` — asset-level HTA integration
- `task-comparison.md §HTA harmonisation` — H2H comparator HTA framing
