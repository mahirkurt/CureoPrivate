# task-modality-cellgene.md

**T3 Modality Template — Cell & Gene Therapy (CAR-T / TCR-T / NK / Gene Therapy / Gene Editing) (v2.5.0)**

> **Architectural context:** Modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when cell or gene therapy modality is in scope. Same layered template pattern as `task-modality-biosimilar.md` (v2.0.0 reference).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "CAR-T", "CAR T", "kimerik antijen reseptör", "TCR-T", "T cell receptor therapy", "NK cell therapy", "TIL", "tumor infiltrating lymphocyte", "gene therapy", "gen tedavisi", "gene editing", "CRISPR therapy", "base editing", "prime editing", "lentiviral", "AAV", "ATMP", "advanced therapy medicinal product", "regenerative medicine"
- Regulatory frame: "RMAT", "Regenerative Medicine Advanced Therapy", "ATMP regulation", "Regulation (EC) 1394/2007", "Office of Therapeutic Products", "OTP", "CBER"
- Asset names: "Yescarta", "Kymriah", "Tecartus", "Breyanzi", "Abecma", "Carvykti", "Casgevy", "Lyfgenia", "Luxturna", "Zolgensma", "Hemgenix", "Roctavian", "Skysona", "Elevidys"

### 1.2 Implicit semantic triggers
- Hematologic malignancy late-line (B-ALL, DLBCL, MM 5L+, FL)
- Inherited monogenic disease curative-intent intervention
- Manufacturing logistics complexity in oncology pipeline analysis

### 1.3 NOT triggered by
- ❌ User employer being a CAR-T or gene therapy developer (Gilead/Kite, Bristol Myers Squibb/Juno-Celgene, Novartis, Pfizer, Vertex, BluebirdBio, Sarepta, BioMarin, etc.)
- ❌ User memory-derived hematology specialty
- ❌ User memory-derived rare disease focus

---

## §2. Foundational Conceptual Framework

### 2.1 Cell vs gene therapy distinction

| Class | Mechanism | Examples |
|---|---|---|
| **Autologous cell therapy** (CAR-T, TIL) | Patient's own cells modified ex vivo | Yescarta, Kymriah, Carvykti |
| **Allogeneic cell therapy** | Healthy donor cells (off-the-shelf) | Investigational allogeneic CAR-T (P-BCMA-ALLO1, ALLO-501A) |
| **In vivo gene therapy (AAV)** | Recombinant adeno-associated virus delivers gene to patient cells | Luxturna, Zolgensma, Hemgenix, Elevidys, Roctavian |
| **Ex vivo gene therapy (lentivirus)** | Hematopoietic stem cells modified ex vivo with lentiviral vector | Lyfgenia, Skysona |
| **Gene editing (in vivo or ex vivo)** | CRISPR/Cas9 / TALEN / ZFN-mediated targeted DNA modification | Casgevy (ex vivo CRISPR) |
| **mRNA-based gene editing** (in vivo CRISPR) | Direct delivery of CRISPR machinery as mRNA-LNP | Verve VERVE-101 (Phase 1) |

### 2.2 The "ATMP" framework (EMA-spesifik)

Per **Regulation (EC) No 1394/2007**, the EU defines **Advanced Therapy Medicinal Products (ATMPs)** in three categories:
- **Gene Therapy Medicinal Products (GTMPs)**
- **Somatic Cell Therapy Medicinal Products (sCTMPs)**
- **Tissue Engineered Products (TEPs)**

EMA Committee for Advanced Therapies (CAT) provides scientific opinion on ATMP applications, then forwarded to CHMP for marketing authorization recommendation.

### 2.3 The "patient = product" complication

Autologous cell therapies cannot be manufactured at scale in the conventional sense — each patient's cells are the starting material for each individual product. This creates:
- Vein-to-vein time as a critical commercial KPI (typically 3-5 weeks)
- Manufacturing slot allocation as a real commercial constraint
- Cell viability and engineered phenotype variability across batches
- Out-of-specification (OOS) failure rate as a commercial loss mechanism

---

## §3. CAR-T Therapy — Specific Disciplines

### 3.1 Construct architecture

```
Antigen recognition → CD3ζ activation → Costimulation → Signaling
   (scFv)              (TCR signal)    (4-1BB or CD28)   → T cell proliferation/killing
```

**Generation hierarchy:**
- **1st gen:** scFv + CD3ζ only (poor persistence)
- **2nd gen:** scFv + CD3ζ + ONE costimulatory domain (4-1BB or CD28)
- **3rd gen:** scFv + CD3ζ + TWO costimulatory domains
- **4th gen ("TRUCKs"):** Armored CAR-T with cytokine secretion or other modifications

All currently approved CAR-Ts are 2nd generation. CD28 costimulation (Yescarta, Tecartus): rapid expansion, shorter persistence. 4-1BB costimulation (Kymriah, Breyanzi, Abecma): slower expansion, longer persistence.

### 3.2 Approved CAR-T landscape

| Asset | Sponsor | Target | Indication | Approval |
|---|---|---|---|---|
| **Kymriah (tisagenlecleucel)** | Novartis | CD19 | B-ALL pediatric, R/R DLBCL, FL | FDA 2017-08; EMA 2018 |
| **Yescarta (axicabtagene ciloleucel)** | Gilead/Kite | CD19 | R/R DLBCL, R/R FL, 2L LBCL | FDA 2017-10 |
| **Tecartus (brexucabtagene autoleucel)** | Gilead/Kite | CD19 | MCL, B-ALL adult | FDA 2020-07 |
| **Breyanzi (lisocabtagene maraleucel)** | Bristol Myers Squibb | CD19 | R/R LBCL, 2L LBCL | FDA 2021-02 |
| **Abecma (idecabtagene vicleucel)** | Bristol Myers Squibb + 2seventy bio | BCMA | R/R MM 5L+ | FDA 2021-03 |
| **Carvykti (ciltacabtagene autoleucel)** | Janssen + Legend Biotech | BCMA | R/R MM 4L+, 2L MM (post-CARTITUDE-4) | FDA 2022-02 |
| **Aucatzyl (obecabtagene autoleucel)** | Autolus | CD19 | R/R B-ALL adult | FDA 2024-11 |

### 3.3 CAR-T class effect: Cytokine Release Syndrome (CRS)

CRS = systemic inflammatory response from CAR-T expansion and cytokine cascade. Universal CAR-T safety event:
- Grading per ASTCT consensus (2019): Grade 1 (fever) → Grade 4 (life-threatening organ dysfunction)
- Onset typically 1-7 days post-infusion, peaks within 1-2 weeks
- Mediators: IL-6, IFN-γ, TNF-α
- Management: tocilizumab (anti-IL-6R) is standard; corticosteroids for refractory; anakinra for severe

### 3.4 CAR-T class effect: ICANS (Immune effector Cell-Associated Neurotoxicity Syndrome)

ICANS = neurologic manifestation of CAR-T inflammation:
- Encephalopathy, dysphasia, tremor, seizures
- Grading per ASTCT (ICE score for cognition assessment)
- Management: corticosteroids (NOT tocilizumab — IL-6R blockade does not cross BBB and may worsen)
- Mortality: rare but reported

### 3.5 REMS programs

All CAR-T therapies require FDA REMS (Risk Evaluation and Mitigation Strategy):
- Certified treatment centers only
- Monitoring requirements (CRS/ICANS protocols)
- Clinician training documentation

### 3.6 Manufacturing logistics — vein-to-vein

Typical autologous CAR-T workflow:
1. **Apheresis** — patient T cells collected (Day 0)
2. **Cryopreservation + shipment** to manufacturing facility (Day 0-2)
3. **Activation + transduction** — viral vector delivers CAR construct (Day 2-7)
4. **Expansion** — T cell amplification (Day 7-14)
5. **QC release testing** — sterility, identity, potency (Day 14-21)
6. **Shipment back to treatment center** + **lymphodepletion** + **infusion** (Day 21-35)

**Manufacturing failure rate:** historically 5-15%; improving with platform maturity.

**Bridging therapy:** Patients often require bridging chemotherapy during the 3-5 week vein-to-vein interval to control disease progression.

---

## §4. AAV Gene Therapy — Specific Disciplines

### 4.1 Vector biology

Adeno-associated virus (AAV): non-pathogenic, single-stranded DNA virus. Multiple serotypes (AAV2, AAV5, AAV8, AAV9) with distinct tissue tropism:
- **AAV2** — historical first-line; broad tropism but immunogenic
- **AAV5** — liver/CNS; some hepatic delivery use
- **AAV8** — strong liver tropism (Hemgenix)
- **AAV9** — CNS crossing capability, broad systemic (Zolgensma)

### 4.2 Approved AAV gene therapy landscape

| Asset | Sponsor | Disease | Vector | Approval |
|---|---|---|---|---|
| **Glybera (alipogene tiparvovec)** | uniQure | Lipoprotein lipase deficiency | AAV1 | EMA 2012 (withdrawn 2017 — first AAV approval) |
| **Luxturna (voretigene neparvovec)** | Spark Therapeutics (Roche) | RPE65-mediated inherited retinal dystrophy | AAV2 | FDA 2017-12; EMA 2018 |
| **Zolgensma (onasemnogene abeparvovec)** | Novartis (AveXis) | Spinal muscular atrophy <2 yr | AAV9 | FDA 2019-05; EMA 2020 |
| **Hemgenix (etranacogene dezaparvovec)** | CSL Behring + uniQure | Hemophilia B | AAV5 | FDA 2022-11; EMA 2023 |
| **Roctavian (valoctocogene roxaparvovec)** | BioMarin | Hemophilia A | AAV5 | FDA 2023-06; EMA 2022 |
| **Elevidys (delandistrogene moxeparvovec)** | Sarepta + Roche | Duchenne muscular dystrophy | AAVrh74 | FDA 2023-06 (accelerated) |

### 4.3 AAV class limitations
- **Pre-existing immunity** — neutralizing antibodies to AAV serotypes in 30-70% of population (varies by serotype and geography)
- **One-shot administration** — repeat dosing precluded by anti-AAV antibody response
- **Hepatotoxicity** — class effect, especially high-dose systemic AAV
- **Thrombotic microangiopathy (TMA)** — reported with Zolgensma; black box warning
- **Episomal persistence** — gene therapy is not integrated; persistence in non-dividing cells, declines in dividing cells

### 4.4 Pricing — gene therapy "list price" ranges

| Product | List price (US, USD) |
|---|---|
| Luxturna | $850,000 (single eye; bilateral ~$1.7M) |
| Zolgensma | $2.125M |
| Hemgenix | $3.5M |
| Roctavian | $2.9M |
| Elevidys | $3.2M |
| Casgevy | $2.2M |
| Lyfgenia | $3.1M |

**Outcomes-based contracting** is increasingly common to manage payer risk on these one-shot expensive therapies.

---

## §5. Gene Editing — CRISPR Class

### 5.1 First approved CRISPR therapies

**Casgevy (exagamglogene autotemcel — exa-cel)** is the first FDA-approved CRISPR/Cas9 gene-editing therapy:
- **Mechanism:** Ex vivo CRISPR/Cas9 editing of patient HSCs at BCL11A erythroid-specific enhancer → increased fetal hemoglobin (HbF) → suppresses sickling
- **Sponsors:** Vertex Pharmaceuticals + CRISPR Therapeutics (60/40 economic split per amended collaboration)
- **MHRA approval:** 16 November 2023 (first CRISPR approval globally)
- **FDA SCD approval:** 8 December 2023 (BLA 125782; Priority Review + Orphan Drug + Fast Track + RMAT designations)
- **EMA approval:** 15 December 2023 (SCD + transfusion-dependent β-thalassemia)
- **FDA TDT approval:** 16 January 2024 (PDUFA goal was March 30, 2024 — early action)

**Lyfgenia (lovotibeglogene autotemcel — lovo-cel)** approved same day (8 December 2023) by Bluebird Bio — lentiviral gene addition (NOT CRISPR), boxed warning for hematologic malignancy.

### 5.2 Emerging gene editing platforms

| Platform | Mechanism | Notable developer |
|---|---|---|
| **Base editing** | Single-base substitution without double-strand break | Beam Therapeutics, Verve Therapeutics |
| **Prime editing** | Targeted insertion/deletion via reverse transcriptase | Prime Medicine |
| **In vivo CRISPR** | LNP-delivered Cas9 mRNA + guide RNA | Intellia (NTLA-2001 ATTR-CM, NTLA-2002 HAE), Verve VERVE-101 |
| **TALEN** | Transcription Activator-Like Effector Nucleases | Cellectis, Allogene |
| **Zinc Finger Nucleases** | First-gen targeted DNA editing | Sangamo (declined commercially) |

### 5.3 Off-target editing concern

Critical safety consideration: unintended edits at sites with sequence similarity to target. Assessment:
- In silico prediction (CRISPRme, CRISPOR algorithms)
- Cellular off-target assays (GUIDE-seq, CIRCLE-seq, DISCOVER-seq)
- Long-term follow-up in clinical patients

FDA AdComm (October 2023) for Casgevy specifically addressed off-target analysis and judged Vertex's package adequate.

---

## §6. Regulatory Pathway

### 6.1 FDA — CBER + Office of Therapeutic Products (OTP)

Cell and gene therapies regulated by **Center for Biologics Evaluation and Research (CBER)**, specifically the **Office of Therapeutic Products (OTP)** (formerly Office of Tissues and Advanced Therapies).

**Special designations available:**
- **Regenerative Medicine Advanced Therapy (RMAT)** — established by 21st Century Cures Act 2016; expedited pathway analogous to Breakthrough Therapy
- **Priority Review** — 6-month review
- **Orphan Drug** — exclusivity + tax credits for rare diseases
- **Fast Track** — rolling submission

**Accelerated approval** widely used (Casgevy, Carvykti, Skysona, Elevidys).

### 6.2 EMA — CAT + ATMP framework

- **Committee for Advanced Therapies (CAT)** — scientific opinion specifically for ATMPs
- **PRIME (PRIority MEdicines)** scheme — equivalent to FDA Breakthrough
- **Conditional marketing authorization** — common for cell/gene therapies (Casgevy in EU)
- **EMA fee waivers** — applicable for SME-developed ATMPs

### 6.3 PMDA + Sakigake

Japan unique pathway: **Sakigake (先駆け) designation** for breakthrough cell/gene therapies. Tetsushi Tanaka-led restructuring of regenerative medicine pathway via Pharmaceuticals and Medical Devices Act amendments.

### 6.4 NMPA + Türkiye

NMPA has approved Asian-developed CAR-Ts (e.g. JW Therapeutics axicabtagene ciloleucel licensed from Kite for China). Türkiye: TİTCK reliance pathway via EMA for multinational cell/gene therapies; SGK reimbursement complex given price levels.

---

## §7. Manufacturing — The Defining Constraint

### 7.1 Process complexity

Cell/gene therapy manufacturing is the **commercial bottleneck**:
- **Vector production** (lentivirus or AAV) — bioreactor + purification + titration
- **Cell processing** (autologous CAR-T) — patient-spesifik, no scale economies
- **QC release** — extensive sterility, identity, potency, viability testing
- **Cold chain logistics** — cryopreservation requirements + qualified shipper network

### 7.2 Capacity expansion patterns

Major sponsors investing heavily in capacity:
- Novartis CAR-T manufacturing: Morris Plains NJ, Stein Switzerland, Les Ulis France
- Gilead/Kite: El Segundo CA, Frederick MD, Hoofddorp Netherlands
- Bristol Myers Squibb: Summit NJ, Bothell WA, Devens MA, Leiden Netherlands
- Vertex/CRISPR (Casgevy): authorized treatment center model with multiple ATCs nationwide

### 7.3 Allogeneic alternative

Several sponsors developing **allogeneic ("off-the-shelf") CAR-T** to address manufacturing/access constraints:
- Allogene Therapeutics (ALLO-501, ALLO-715)
- Caribou Biosciences (CB-010)
- Precision Biosciences (PBCAR0191)
- Cellectis (UCART19, UCART22)

Tradeoff: shorter vein-to-vein vs persistence and graft-versus-host disease (GvHD) risk from allogeneic source.

---

## §8. Commercial Trajectory Patterns

### 8.1 Approved CAR-T sales (FY2024 ~)

| Asset | Sponsor | FY2024 sales (~) |
|---|---|---|
| **Yescarta** | Gilead/Kite | ~$1.4B |
| **Tecartus** | Gilead/Kite | ~$400M |
| **Carvykti** | Janssen + Legend | ~$1B+ (rapid growth post-CARTITUDE-4 2L approval) |
| **Breyanzi** | Bristol Myers Squibb | ~$700M |
| **Abecma** | Bristol Myers Squibb | ~$400M (declining post-CARTITUDE-4 competition) |
| **Kymriah** | Novartis | ~$300M (oldest, slowest growth) |

### 8.2 Gene therapy sales reality

Single-shot pricing makes traditional sales metrics complex:
- **Patient counts low** (rare disease populations)
- **Revenue lumpy** (per-patient $1-3M)
- **Manufacturing slot allocation** as a leading indicator
- **Outcomes-based contracting** affects revenue recognition timing

### 8.3 Pipeline horizon

Solid tumor CAR-T (claudin 18.2, GPC3, mesothelin): largely investigational. Commercial validation pending. Hematologic CAR-T continues to expand into earlier lines and indication extensions.

---

## §9. Stakeholder-Spesifik Analytical Framework

### 9.1 Cell/gene therapy first-mover sponsors
- Manufacturing capacity as strategic moat
- Authorized treatment center network expansion
- Long-term outcomes generation strategy

### 9.2 Allogeneic / off-the-shelf challenger sponsors
- Manufacturing scale advantage
- Persistence + GvHD safety package required
- Geographic launch flexibility

### 9.3 Academic + nonprofit cell therapy stakeholders
- Hospital-developed CAR-T (e.g. NHS England academic CAR-T)
- Cost-effective alternative model

### 9.4 Payer paydaşları
- Outcomes-based contracting design
- One-shot reimbursement amortization mechanisms
- Cell/gene therapy carve-outs in employer coverage

### 9.5 Klinisyen + treatment center paydaşları
- REMS certification burden
- ICU capacity for CRS/ICANS management
- Patient referral pattern dynamics

### 9.6 Hasta paydaşları
- Travel burden to authorized treatment centers
- Bridging therapy management
- Long-term registry follow-up commitments

---

## §10. Confidence Stamping

| Claim type | Default confidence |
|---|---|
| FDA approval date + indication scope | **High** (FDA primary) |
| EMA / CAT positive opinion + EC adoption | **High** (EMA primary) |
| Pivotal trial efficacy | **High** (peer-reviewed publication) |
| Vein-to-vein time benchmarks | **Medium** (sponsor disclosure varies) |
| Manufacturing failure rate | **Low-Medium** (rarely fully disclosed) |
| Real-world CRS incidence | **Medium** (registry depends on quality) |
| Long-term safety (>5 years) | **Low** (immature for many newer products) |
| Confidential manufacturing IP | Should not be claimed |
| Off-target editing in patient (research-stage) | Should not be claimed |

---

## §11. Forbidden Patterns

- ❌ Treating allogeneic CAR-T as direct equivalent of autologous (different efficacy, persistence, GvHD risk)
- ❌ Conflating "gene therapy" (additive) with "gene editing" (modificative) — different mechanisms, different IP, different competitive landscape
- ❌ Strategic action recommendations for specific cell/gene sponsors without T6-Defense activation
- ❌ Speculation about confidential manufacturing yields or OOS rates
- ❌ Treating "one-time curative therapy" as equivalent to chronic therapy revenue model

---

## §12. Versioning & Changelog

- **v2.5.0 (2026-04-15):** Initial release. Cell/gene therapy T3 sub-template covering: cell vs gene therapy distinction (autologous CAR-T, allogeneic, in vivo AAV, ex vivo lentivirus, CRISPR gene editing), EMA ATMP framework (Regulation (EC) 1394/2007 + CAT), patient = product complication for autologous, CAR-T construct architecture (4 generations + CD28 vs 4-1BB costimulation), 7 approved CAR-T landscape (Kymriah through Aucatzyl), CRS + ICANS class effects with ASTCT grading, REMS programs, vein-to-vein manufacturing logistics, 6 approved AAV gene therapy landscape (Luxturna through Elevidys), AAV serotype tropism, AAV class limitations (immunogenicity, hepatotoxicity, TMA), gene editing CRISPR class (Casgevy December 2023 milestone — first CRISPR/Cas9 therapy globally; Vertex+CRISPR 60/40 collaboration), emerging gene editing platforms (base editing, prime editing, in vivo CRISPR), regulatory pathway (FDA CBER OTP + RMAT designation; EMA CAT; PMDA Sakigake; NMPA + Türkiye), manufacturing as commercial bottleneck, allogeneic CAR-T pipeline, commercial trajectory patterns including FY2024 sales for 6 approved CAR-Ts, pricing $850K-$3.5M per dose with outcomes-based contracting, stakeholder framework (6 abstract categories). Compatible with all sub-protocols. New manifest gate G27.
