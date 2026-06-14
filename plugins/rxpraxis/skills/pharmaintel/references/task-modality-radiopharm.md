# task-modality-radiopharm.md

**T3 Modality Template — Radiopharmaceuticals / Radioligand Therapies (RLT) (v2.5.0)**

> **Architectural context:** Modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when radiopharmaceutical / radioligand therapy modality is in scope. Same layered template pattern as `task-modality-biosimilar.md` (v2.0.0 reference).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5. User's nuclear medicine specialty interest, employer's radiopharm portfolio, or geography (proximity to cyclotron/reactor facilities) are NOT valid triggers.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "radiopharmaceutical", "radioligand therapy", "RLT", "targeted radionuclide therapy", "TRT", "theranostic", "theranostics", "targeted alpha therapy", "TAT", "radyofarmasötik", "radyoligand tedavisi"
- Isotope terms: "Lu-177", "lutetium-177", "lutetium 177", "Ac-225", "actinium-225", "I-131", "iodine-131", "Y-90", "yttrium-90", "Ga-68", "gallium-68", "Cu-67", "copper-67", "Pb-212", "lead-212", "F-18", "fluorine-18"
- Asset terms: "Pluvicto", "Lutathera", "Xofigo", "radium-223", "Zevalin", "Bexxar" (former), "Quadramet", "Metastron", "RayzeBio", "ITM Isotopen", "Curium", "Lantheus"
- Companion/diagnostic terms: "PSMA-PET", "DOTATATE PET", "Ga-68 DOTATATE", "Locametz", "NETSPOT", "Illuccix", "Pylarify", "PSMA imaging"

### 1.2 Implicit semantic triggers
- mCRPC late-line treatment landscape (Pluvicto territory)
- Neuroendocrine tumor (NET) late-line landscape (Lutathera territory)
- Bone metastasis pain palliation (Xofigo territory)

### 1.3 NOT triggered by
- ❌ User employer being a radiopharm developer (Novartis/AAA, Bayer, Bristol Myers Squibb/RayzeBio, ITM, Curium, Lantheus, POINT Biopharma now BMS, Telix Pharmaceuticals, Fusion Pharmaceuticals now AstraZeneca)
- ❌ User memory-derived nuclear medicine or oncology specialty
- ❌ User geography proximity to nuclear infrastructure

---

## §2. Foundational Conceptual Framework

### 2.1 Three-component radiopharmaceutical architecture

```
       ┌─────────────────────────────┐
       │  Targeting Vector           │ ← receptor/antigen binding
       │  (peptide, mAb, small mol)  │
       └───────────┬─────────────────┘
                   │
                   │  Bifunctional Chelator (DOTA, NOTA, DTPA, etc.)
                   │
                   ▼
       ┌─────────────────────────────┐
       │  Radioactive Isotope        │ ← therapeutic emission OR diagnostic emission
       │  (β−, α, γ, β+ emitter)     │
       └─────────────────────────────┘
```

Examples:
- **PSMA-617** = small molecule PSMA-binding ligand + DOTA chelator + Lu-177 (therapeutic) or Ga-68 (diagnostic)
- **DOTATATE** = somatostatin analog peptide + DOTA chelator + Lu-177 (Lutathera) or Ga-68 (NETSPOT diagnostic)
- **Radium-223 dichloride (Xofigo)** = radium ion itself; no chelator; calcium mimetic in bone

### 2.2 Theranostic pair concept

**Theranostic** = same targeting vector with two isotopes:
- **Diagnostic isotope** (typically Ga-68 PET imaging or F-18 PET) for patient selection + dosimetry
- **Therapeutic isotope** (Lu-177 β−, Ac-225 α, Y-90 β−) for tumor treatment

This creates a **biomarker-paired treatment paradigm**:
1. Image patient with diagnostic radiotracer to confirm target expression + tumor distribution
2. If positive → administer therapeutic version of same vector
3. Post-treatment dosimetry confirms tumor uptake

The PSMA-PET / Pluvicto pair is the dominant commercial example: **Locametz (Ga-68 gozetotide, Novartis) or Illuccix (Telix) or Pylarify (Lantheus, F-18 piflufolastat)** for diagnostic imaging → **Pluvicto (Lu-177 vipivotide tetraxetan)** for therapy.

### 2.3 Why radiopharm ≠ targeted therapy and ≠ chemotherapy

Radiopharm occupies a unique niche:
- **Mechanism:** Radioactive decay damages DNA via ionizing radiation (β− particles, α particles, Auger electrons) — physical, not pharmacological
- **Selectivity:** Targeting vector delivers payload; "off-target" radiation = inevitable but constrained by short range of emission
- **Dose-response:** Radiation dose in Gy (Gray) absorbed; pharmacokinetic concept replaced by **dosimetry**
- **Manufacturing:** Combines pharma + nuclear infrastructure (cyclotrons, reactors, radiopharmacy networks)
- **Logistics:** Half-life-constrained delivery — Lu-177 (t½ 6.6 days) requires same-week shipping

---

## §3. Isotope Class Taxonomy

### 3.1 Beta (β−) emitters — current standard

| Isotope | Half-life | Energy | Range in tissue | Commercial use |
|---|---|---|---|---|
| **Lu-177 (lutetium-177)** | 6.65 days | β− 0.5 MeV (max) + low-energy γ for imaging | ~2 mm | Pluvicto, Lutathera; dominant clinical β− |
| **I-131 (iodine-131)** | 8.0 days | β− 0.6 MeV + γ 364 keV | ~2.4 mm | Thyroid cancer; oldest therapeutic isotope |
| **Y-90 (yttrium-90)** | 64.1 hours | β− 2.3 MeV (high energy) | ~12 mm | Zevalin (radioimmunotherapy, lymphoma); SIR-Spheres (HCC) |
| **Sm-153 (samarium-153)** | 1.93 days | β− + γ | ~3 mm | Quadramet (bone pain palliation) |
| **Sr-89 (strontium-89)** | 50.5 days | β− 1.5 MeV | ~7 mm | Metastron (bone pain palliation) |

### 3.2 Alpha (α) emitters — emerging frontier

| Isotope | Half-life | Energy | Range in tissue | Status |
|---|---|---|---|---|
| **Ra-223 (radium-223)** | 11.4 days | α 5.7 MeV | ~70 μm (very short) | Xofigo — approved for mCRPC bone metastases |
| **Ac-225 (actinium-225)** | 9.9 days | α 5.8-7.5 MeV (decay chain) | ~50-100 μm | Investigational; Pluvicto-equivalent + multiple Phase 1/2 |
| **Pb-212 (lead-212)** | 10.6 hours | α via Bi-212 daughter | ~50 μm | Investigational (e.g. AlphaMedix) |
| **Th-227 (thorium-227)** | 18.7 days | α decay chain | ~70 μm | Investigational (Bayer thorium platform) |
| **At-211 (astatine-211)** | 7.2 hours | α 5.9 MeV | ~55-80 μm | Investigational (Telix, Fusion-AstraZeneca) |

**Alpha emitter advantage:** Higher LET (Linear Energy Transfer) → more potent DNA damage per decay; very short range = more focal target cell killing with less collateral damage.
**Alpha emitter challenge:** Limited supply (Ac-225 produced from radioactive decay of Th-229 stockpiles, very scarce); complex daughter decay chains.

### 3.3 Diagnostic positron (β+) emitters

| Isotope | Half-life | Use |
|---|---|---|
| **Ga-68 (gallium-68)** | 67.7 minutes | DOTATATE PET (Locametz, NETSPOT); PSMA PET (Locametz, Illuccix) |
| **F-18 (fluorine-18)** | 110 minutes | Pylarify (PSMA), FDG (oncology), florbetapir (amyloid) |
| **Cu-64 (copper-64)** | 12.7 hours | Detectnet (DOTATATE PET); investigational theranostic pair with Cu-67 |
| **Zr-89 (zirconium-89)** | 78.4 hours | ImmunoPET research (long enough for mAb biodistribution) |

### 3.4 Auger electron emitters — emerging
- **I-125, Tb-161** investigational; very short range (cellular scale); requires nuclear localization for efficacy

---

## §4. Approved Radiopharm Therapeutic Landscape

### 4.1 Approved RLT / radiopharmaceutical therapeutics

| Asset | INN / chemistry | Sponsor | Indication | Approval |
|---|---|---|---|---|
| **I-131 NaI** | Iodine-131 sodium iodide | Multiple generic | Thyroid cancer (post-thyroidectomy ablation) | Standard since 1940s |
| **Quadramet** | Samarium Sm-153 lexidronam | Lantheus / multiple | Bone metastasis pain palliation | FDA 1997 |
| **Metastron** | Strontium Sr-89 chloride | Multiple | Bone metastasis pain palliation | FDA 1993 |
| **Zevalin** | Yttrium Y-90 ibritumomab tiuxetan | Acrotech (former Spectrum) | R/R follicular lymphoma (radioimmunotherapy) | FDA 2002 |
| **Bexxar** (withdrawn) | Iodine I-131 tositumomab | Former GSK | NHL — withdrawn 2014 (commercial) | FDA 2003 |
| **Xofigo** | Radium Ra-223 dichloride | Bayer | mCRPC with symptomatic bone metastases (no visceral) | FDA 2013 |
| **Lutathera** | Lutetium Lu-177 dotatate | Novartis (AAA) | Somatostatin receptor positive GEP-NET | FDA 2018 (BLA based on NETTER-1) |
| **Pluvicto** | Lutetium Lu-177 vipivotide tetraxetan (177Lu-PSMA-617) | Novartis (AAA) | PSMA-positive mCRPC (initially post-taxane; expanded pre-taxane March 2025) | FDA 2022-03-23 (initial); FDA 2025-03-28 (label expansion) |

### 4.2 Approved theranostic diagnostic radiopharmaceuticals

| Asset | INN | Sponsor | Indication |
|---|---|---|---|
| **NETSPOT** | Ga-68 DOTATATE | Curium | NET imaging (paired with Lutathera) |
| **Detectnet** | Cu-64 DOTATATE | RadioMedix / Curium | NET imaging |
| **Locametz** | Ga-68 gozetotide (PSMA-11) | Novartis | PSMA imaging mCRPC (paired with Pluvicto for selection) |
| **Illuccix** | Ga-68 gozetotide (PSMA-11 kit) | Telix Pharmaceuticals | PSMA imaging |
| **Pylarify** | F-18 piflufolastat (PSMA) | Lantheus | PSMA imaging |
| **Posluma** | F-18 flotufolastat (PSMA) | Blue Earth Diagnostics / Bracco | PSMA imaging (FDA 2023) |

### 4.3 Pluvicto trajectory — defining commercial precedent

Per VISION trial (Sartor O et al., NEJM 2021;385:1091-103):
- mPFS hazard ratio 0.40 (95% CI 0.29-0.57) for radiographic PFS
- mOS hazard ratio 0.62 (95% CI 0.52-0.74)
- mCRPC patients post-ARPI + post-taxane

**Lifecycle expansion:**
- FDA 2022-03-23 — initial approval (post-taxane mCRPC)
- 2022-05 — voluntary production halt (quality issues at Ivrea/Millburn) — commercial supply disruption
- 2023 — supply ramp restoration; FDA shortage resolved
- 2024-04-21 — FDA approval for Millburn NJ commercial manufacturing (US-domestic supply)
- 2025-03-28 — FDA label expansion for pre-taxane setting based on PSMAfore (468 patients, ARPI-naive, taxane-naive mCRPC; OS HR 0.59 IPCW-adjusted for crossover)

**Manufacturing footprint (Novartis radioligand network):**
- Ivrea, Italy
- Millburn, NJ, USA
- Indianapolis, IN, USA (commissioned 2023)
- Zaragoza, Spain (under expansion)

---

## §5. Isotope Supply Chain — The Defining Constraint

### 5.1 Lu-177 (no-carrier-added vs carrier-added)

**No-carrier-added (n.c.a.) Lu-177:**
- Produced by neutron irradiation of enriched Yb-176 → Yb-177 → β− decay → Lu-177
- High specific activity (GBq/μmol) — can label small targeting vectors at clinical relevance
- Suppliers: ITM Isotopen Technologien München (primary Pluvicto supplier per long-term Endocyte/Novartis agreement, expanded March 2020), IDB Holland, NorthStar Medical Radioisotopes
- Limited global capacity; major reactor infrastructure required

**Carrier-added (c.a.) Lu-177:**
- Produced by direct neutron irradiation of natural Lu-176
- Lower specific activity; more carrier Lu present
- Used historically; n.c.a. preferred for therapeutic peptide labeling

### 5.2 Ac-225 — global scarcity

**Ac-225 production methods:**
- **Th-229 decay** (legacy stockpile from US DOE) — limited (~1.7 Ci/year globally)
- **Cyclotron production** via Th-232 (p,x) Ac-225 — emerging
- **Linear accelerator** Ra-226 (p,2n) Ac-225 — TerraPower demonstration
- **Reactor-based** Ra-226 (n,2n) Ra-225 → β− → Ac-225 — limited

The Ac-225 supply bottleneck is the **single biggest gating factor** for alpha-emitter therapeutic clinical development.

### 5.3 Ra-223 (Xofigo) supply

Bayer manufactures via Ac-227 → Th-227 → Ra-223 generators; specialized supply chain for Ra-223 distinct from other isotopes.

### 5.4 Ga-68 — generator-based + cyclotron

**Ga-68 generator** (Ge-68/Ga-68): on-site elution at PET centers; 9-12 month generator lifespan; multiple generators per center for clinical workflow.
**Cyclotron-produced Ga-68:** emerging alternative for higher-volume sites.

### 5.5 Half-life-driven logistics

| Isotope | Half-life | Logistics implication |
|---|---|---|
| Lu-177 (6.6 d) | Days | Weekly shipping windows; air freight to clinical sites |
| Ac-225 (9.9 d) | Days | Similar to Lu-177; supply scarcity dominant constraint |
| I-131 (8.0 d) | Days | Established global infrastructure |
| Y-90 (64 hr) | Hours-days | Shorter window; more constrained logistics |
| Ga-68 (68 min) | Minutes | Same-day production at PET center; no shipping |
| F-18 (110 min) | Hours | Local cyclotron production within ~2 hour ground delivery radius |

---

## §6. Dosimetry Discipline

### 6.1 What dosimetry is

**Absorbed dose (Gray, Gy)** = energy absorbed per unit mass of tissue. Replaces "concentration × time AUC" pharmacokinetic concept for radiopharmaceuticals.

**Patient-spesifik dosimetry** quantifies:
- **Tumor-absorbed dose** (target organ — what we want)
- **Critical organ doses** (kidneys, bone marrow, salivary glands — toxicity-limiting)
- **Whole-body dose** (regulatory + radiation safety)

### 6.2 Dose-limiting organs

| RLT | Dose-limiting organ | Mechanism |
|---|---|---|
| **Pluvicto / Lu-177 PSMA** | Salivary glands (xerostomia), kidneys (nephrotoxicity) | PSMA expressed on lacrimal/salivary; renal tubular reabsorption of small peptides |
| **Lutathera / Lu-177 DOTATATE** | Kidneys, bone marrow | Renal reabsorption; hematologic toxicity |
| **Xofigo / Ra-223** | Bone marrow (less so than expected — short range) | Radium accumulates in bone matrix |

### 6.3 Lysine-arginine renal protection

For peptide-based RLTs (Lutathera, Pluvicto), **co-infusion of amino acid solution (lysine + arginine, or commercial amino acid mix)** competitively inhibits renal tubular reabsorption → reduces kidney dose by ~50%.

### 6.4 Theranostic dosimetry workflow

Modern RLT clinical practice increasingly integrates pre-treatment dosimetry:
1. **Scout dose** — administer small dose of therapeutic isotope or surrogate diagnostic
2. **Sequential SPECT/CT or PET imaging** at multiple timepoints (e.g. 4h, 24h, 48h, 7d post-injection)
3. **Time-activity curve fitting** + **dosimetry calculation** (OLINDA/EXM, MIRDcalc, voxel-based methods)
4. **Personalized dose adjustment** to maximize tumor dose while staying below organ tolerance

---

## §7. Regulatory Pathway

### 7.1 FDA framework

Radiopharmaceuticals reviewed by FDA's **Division of Imaging and Radiation Medicine (DIRM)** within OND or **Office of Oncologic Diseases** for therapeutic radiopharms. **NDA pathway (for small molecule chelator + isotope)** more common than BLA. Combination with radiation source classification handled through dedicated regulatory framework.

**Companion diagnostic requirement:** Pluvicto label requires PSMA-positive disease confirmed by FDA-approved PSMA-PET imaging agent (Locametz, Illuccix, Pylarify, Posluma). This makes radiopharm theranostic pair commercially co-dependent.

### 7.2 Radiation safety oversight

Beyond FDA approval, radiopharm clinical use requires:
- **Nuclear Regulatory Commission (NRC)** licensing for institutional use of radioactive materials (US)
- **State radiation control programs** (Agreement States vs Non-Agreement States)
- **Authorized User (AU) physician** training requirements per 10 CFR 35
- **ALARA** (As Low As Reasonably Achievable) radiation safety culture

This adds an institutional barrier to access — RLT cannot be administered at any oncology clinic; requires nuclear medicine infrastructure + AU physicians.

### 7.3 EMA framework

EMA centralized procedure; CHMP review. **EMA Guideline on radiopharmaceuticals** (EMEA/CHMP/QWP/306970/2007 + updates). EU legal framework includes Council Directive 2013/59/Euratom (basic safety standards for radiation protection).

### 7.4 PMDA + NMPA

PMDA: established radiopharm framework; Japan NCC has developed multiple Lu-177 programs. NMPA: emerging Chinese radiopharm developer ecosystem (e.g. Sinotau, China Isotope & Radiation Corporation).

### 7.5 TİTCK + Türkiye

Türkiye TİTCK altında EMA reliance pathway radyofarmasötikler için dominant. SGK SUT geri ödemesinde Lutathera ve Pluvicto henüz tam erişim altında değil (2026 cutoff durumu); özel finansman + Sağlık Bakanlığı erişim programları üzerinden hasta erişimi sınırlı kalabilir. Türkiye'de yerli isotope üretim altyapısı sınırlı (TAEK Çekmece Nükleer Araştırma Merkezi yan kapasitesi); büyük ölçüde ithalat.

---

## §8. Manufacturing — Specialized Infrastructure

### 8.1 Production ecosystem

Radiopharm manufacturing requires intersection of:
- **Reactor or cyclotron infrastructure** (isotope production)
- **Radiochemistry capability** (cold kit + radiolabeling)
- **Pharmaceutical GMP** (final drug product release)
- **Hot cell containment** (radiation worker safety)
- **Logistics network** (qualified couriers + temperature/dose monitoring)

### 8.2 Major commercial radiopharm manufacturers

| Sponsor | Capability |
|---|---|
| **Novartis (AAA + post-acquisition)** | Pluvicto + Lutathera; vertical integration; Ivrea + Millburn + Indianapolis + Zaragoza |
| **Bayer** | Xofigo manufacturing; Th-227 platform development |
| **Bristol Myers Squibb (RayzeBio acq Dec 2023, ~$4.1B)** | Ac-225 actinium platform; pipeline focus |
| **AstraZeneca (Fusion Pharmaceuticals acq 2024, ~$2B)** | Ac-225 + at-211 alpha platform |
| **Eli Lilly (POINT Biopharma acq 2023, ~$1.4B)** | Lu-177 + Ac-225 platform |
| **Curium** | Generic radiopharms + diagnostic agents |
| **Lantheus** | Pylarify + diagnostic radiopharm portfolio |
| **Telix Pharmaceuticals** | Illuccix + therapeutic pipeline |
| **ITM Isotopen Technologien München** | Lu-177 supplier + therapeutic pipeline |

### 8.3 The 2022 Pluvicto supply crisis — case study

Novartis voluntarily suspended Pluvicto + Lutathera production in May 2022 at Ivrea + Millburn due to "potential quality issues in the company's production processes" — 6-week target restart. Real-world supply impact extended into 2023 with FDA shortage classification only resolved late 2023 after weekly capacity doubling. This illustrates the **fragility of single-product / few-facility radiopharm supply chains**.

### 8.4 BD/M&A consolidation arc

2023-2024 saw the **largest radiopharm M&A wave in history**:
- Bristol Myers Squibb / RayzeBio (Dec 2023, ~$4.1B)
- Eli Lilly / POINT Biopharma (Oct 2023, ~$1.4B)
- AstraZeneca / Fusion Pharmaceuticals (Mar 2024, ~$2B)
- Novartis / various tuck-ins post-AAA acquisition (2018 Endocyte $2.1B; 2018 AAA $3.9B)

Strategic rationale: Big Pharma securing alpha-emitter platforms ahead of expected late-2020s clinical readouts.

---

## §9. Commercial Trajectory Patterns

### 9.1 Established radiopharm sales

| Asset | Sponsor | Approx 2024 sales | Trajectory |
|---|---|---|---|
| **Pluvicto** | Novartis | ~$1.4B (FY2024) | Growing rapidly post-supply restoration; pre-taxane label expansion 2025 expected acceleration |
| **Lutathera** | Novartis | ~$700M | Established NET franchise |
| **Xofigo** | Bayer | ~$300M (declining) | Pressure from competing mCRPC therapies |
| **Pylarify** | Lantheus | ~$900M | Diagnostic; patient selection platform |
| **Locametz / Illuccix** | Novartis / Telix | Combined ~$200-400M | Companion diagnostic for Pluvicto |

### 9.2 Pricing benchmarks

| Product | List price (US) |
|---|---|
| Pluvicto (per cycle, 4-6 cycles typical) | ~$42,500/cycle |
| Lutathera (per cycle, 4 cycles) | ~$48,000/cycle |
| Xofigo (per injection, 6 injections) | ~$15,000/injection |
| Ga-68 PSMA PET imaging | ~$3,500-5,000 per scan |

Total Pluvicto course: ~$170,000-260,000 per patient. Combined with required PET imaging and theranostic workup: ~$200,000+ per treated patient.

### 9.3 Commercial growth thesis

- **PSMA platform expansion** beyond mCRPC — pre-mCRPC, hormone-sensitive PC, biochemical recurrence indications in development
- **Alpha-emitter Ac-225 generation** — expected to provide superior efficacy for PSMA, DOTATATE, FAP-targeted therapies
- **New target classes** — FAP (fibroblast activation protein) targeting via ⁶⁸Ga / ¹⁷⁷Lu-FAPI; HER2 immuno-radioconjugates
- **Combinations** — RLT + IO, RLT + DDR inhibitors, RLT + ADT in earlier disease

---

## §10. Stakeholder-Spesifik Analytical Framework

### 10.1 Established radiopharm sponsors
- Manufacturing scale moat (vertical integration like Novartis)
- Supply chain redundancy investment
- Lifecycle expansion strategy (earlier-line indications)

### 10.2 Alpha-emitter platform challenger sponsors
- Ac-225 supply chain securing (alliances with US DOE / TerraPower / partnerships)
- Clinical differentiation packages vs Lu-177 incumbents
- Geographic launch sequencing

### 10.3 Diagnostic radiopharm sponsors
- Theranostic pair commercial co-dependence
- Reimbursement coverage development (CPT codes, Medicare LCD)
- AU physician training network expansion

### 10.4 Isotope supplier sponsors
- Reactor / cyclotron capacity expansion
- Long-term supply agreements with therapeutic developers
- Vertical integration discussion (suppliers becoming developers)

### 10.5 Payer paydaşları
- Per-cycle cost vs total course duration (4-6 cycles for Pluvicto)
- Theranostic workup cost (PET imaging required for selection)
- Outcomes-based contracting for accelerated approvals

### 10.6 Klinisyen + treatment center paydaşları
- AU physician availability constraint
- Hot lab / radiopharmacy infrastructure
- Patient referral pattern from medical oncology to nuclear medicine

### 10.7 Hasta paydaşları
- Travel burden to certified RLT centers
- Multi-cycle treatment course commitment
- Radiation safety post-treatment (close-contact precautions briefly)

---

## §11. Confidence Stamping for Radiopharm Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (NETTER-1, VISION, PSMAfore) | **High** (peer-reviewed) |
| Isotope half-life + emission characteristics | **High** (physical constants) |
| Manufacturing site capacity (publicly disclosed) | **Medium** (sponsor IR varies) |
| Forward isotope supply availability (Ac-225 in particular) | **Low-Medium** (highly uncertain) |
| Real-world dosimetry-personalized outcomes | **Medium** (registry quality varies) |
| Net pricing after rebates | **Low** (confidential) |
| Pipeline timing (alpha-emitter Phase 3 readouts) | **Medium** (sponsor guidance subject to slip) |
| Confidential CMO / isotope supply contracts | Should not be claimed |

---

## §12. Forbidden Patterns

- ❌ Treating "all radiopharms" as equivalent — Lu-177 β−, Ac-225 α, Ga-68 β+ have radically different mechanisms, ranges, doses, manufacturing
- ❌ Conflating diagnostic theranostic isotope (e.g. Ga-68 PSMA) with therapeutic version (Lu-177 PSMA) — different products, different approvals
- ❌ Generalizing Pluvicto commercial trajectory to all radiopharm modalities (target/tumor/competitive context-dependent)
- ❌ Strategic action recommendations for specific radiopharm sponsors without T6-Defense activation
- ❌ Speculation about confidential isotope supply contracts or pricing
- ❌ Treating supply availability as guaranteed (2022 Pluvicto crisis demonstrates fragility)

---

## §13. Versioning & Changelog

- **v2.5.0 (2026-04-15):** Initial release. Radiopharmaceutical / radioligand therapy T3 sub-template covering: 3-component architecture (targeting vector + chelator + isotope), theranostic pair concept (diagnostic Ga-68/F-18 imaging + therapeutic Lu-177/Ac-225/Y-90), isotope class taxonomy (β− emitters Lu-177/I-131/Y-90/Sm-153/Sr-89; α emitters Ra-223/Ac-225/Pb-212/Th-227/At-211; β+ diagnostic Ga-68/F-18/Cu-64/Zr-89; emerging Auger), approved RLT landscape (I-131, Quadramet, Metastron, Zevalin, Bexxar withdrawn, Xofigo, Lutathera, Pluvicto with full lifecycle including 2022-05 production halt + 2025-03-28 PSMAfore label expansion), companion diagnostics (NETSPOT, Locametz, Illuccix, Pylarify, Posluma), Pluvicto commercial precedent (VISION trial NEJM 2021;385:1091-103, mPFS HR 0.40, mOS HR 0.62), isotope supply chain disciplines (Lu-177 n.c.a. vs c.a., ITM Isotopen-Endocyte/Novartis agreement, Ac-225 global scarcity ~1.7 Ci/year from Th-229 decay + emerging cyclotron/accelerator production, Ga-68 generator vs cyclotron), dosimetry discipline (absorbed dose Gy concept, dose-limiting organs salivary/kidneys/bone marrow, lysine-arginine renal protection, theranostic dosimetry workflow), regulatory pathway (FDA DIRM/OND + NRC + Authorized User + ALARA + NDA pathway for small mol radiopharms; EMA Council Directive 2013/59/Euratom + EMA radiopharm guideline; PMDA + NMPA + Türkiye TİTCK + SGK access challenges), manufacturing footprint (Novartis Ivrea + Millburn + Indianapolis + Zaragoza; major commercial manufacturers + 2022 Pluvicto supply crisis case study), 2023-2024 M&A consolidation wave (BMS/RayzeBio $4.1B, Lilly/POINT $1.4B, AstraZeneca/Fusion $2B), commercial trajectory + pricing (~$42-48K/cycle therapeutic; ~$3.5-5K diagnostic PET; total Pluvicto course ~$200K+), stakeholder framework (7 abstract categories), confidence stamping. Compatible with all sub-protocols. New manifest gate G29.
