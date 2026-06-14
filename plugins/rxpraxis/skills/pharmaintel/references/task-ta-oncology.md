# task-ta-oncology.md

**T3 Therapeutic Area Template — Oncology (v3.0.0, Layer 2)**

> **Architectural context:** First Layer 2 (Therapeutic Area) T3 template. Layers ON TOP OF Layer 1 modality templates + Layer 0 generic. Provides oncology-spesifik disciplines orthogonal to modality. Example: "T-DXd in HER2+ mBC" invokes all three layers — Layer 0 generic + Layer 1 ADC template + Layer 2 oncology TA.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5. User employer's oncology portfolio, user's oncology specialty, or user's institution being an NCI Comprehensive Cancer Center are NOT valid triggers.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Therapeutic area terms: "oncology", "cancer", "onkoloji", "kanser", "tumor", "neoplasm", "malignancy", "carcinoma", "sarcoma", "lymphoma", "leukemia", "myeloma"
- Tumor types: "breast cancer", "NSCLC", "SCLC", "mCRC", "mUC", "mCRPC", "RCC", "HCC", "gastric", "pancreatic", "ovarian", "endometrial", "cervical", "glioblastoma", "melanoma", "DLBCL", "FL", "CLL", "MCL", "AML", "MDS", "MM", "NHL", "HL"
- Framework terms: "TNM staging", "tumor staging", "metastatic", "advanced", "locally advanced", "adjuvant", "neoadjuvant", "first-line", "1L", "second-line", "2L", "later-line", "5L+", "refractory", "relapsed", "R/R"
- Biomarker terms: "HER2+", "HER2-", "HER2-low", "HR+", "ER+", "PR+", "EGFR mutation", "ALK", "ROS1", "RET", "NTRK", "BRAF", "KRAS G12C", "MSI-H", "dMMR", "TMB", "PD-L1", "BRCA", "HRD", "HRR"
- Endpoint terms: "OS", "PFS", "DFS", "EFS", "ORR", "DOR", "DCR", "CR", "PR", "SD", "PD", "RECIST", "iRECIST", "LYRIC", "IWG", "Lugano"

### 1.2 Implicit semantic triggers
- FDA oncology AdComm discussions
- NCCN guideline reference
- ESMO guideline reference
- ASCO Annual Meeting / ESMO Congress / SABCS / ASH Annual Meeting context

### 1.3 NOT triggered by
- ❌ User employer having oncology portfolio (any major pharma)
- ❌ User memory-derived oncology specialty
- ❌ User institution being NCI Comprehensive Cancer Center / MSKCC / MDACC / Dana-Farber

---

## §2. Foundational Oncology Framework

### 2.1 Disease state classification

Oncology analyses typically segment by:
1. **Primary tumor type** (breast, lung, colorectal, etc. — per ICD-O, SEER, WHO classifications)
2. **Stage** (I-IV per TNM; or early/locally advanced/metastatic per common usage)
3. **Biomarker status** (receptor, mutation, expression level)
4. **Line of therapy** (1L, 2L, 3L, later)
5. **Prior therapy profile** (IO-experienced, chemo-experienced, post-taxane, post-anthracycline, etc.)

### 2.2 Endpoint hierarchy in oncology

| Endpoint | Description | Regulatory weight |
|---|---|---|
| **Overall Survival (OS)** | Time to death from any cause | Gold standard; required for most early-line approvals; confirmatory for accelerated approvals |
| **Progression-Free Survival (PFS)** | Time to progression or death | Common primary endpoint; surrogate for OS in many tumor types |
| **Disease-Free Survival (DFS)** | Time to recurrence post-adjuvant treatment | Adjuvant trial standard |
| **Event-Free Survival (EFS)** | Composite endpoint | Hematology trials commonly |
| **Objective Response Rate (ORR)** | CR + PR per RECIST | Accelerated approval basis (e.g. single-arm studies in rare/refractory indications) |
| **Duration of Response (DOR)** | How long responders stay responding | Response durability assessment |
| **Disease Control Rate (DCR)** | CR + PR + SD | Broader response measure |
| **pCR (pathologic complete response)** | Complete tumor absence post-neoadjuvant | Breast + rectal cancer adjuvant |
| **Minimal Residual Disease (MRD)** | Very small disease amount | Hematology adjuvant (CLL, MM, CML) |
| **Health-Related Quality of Life (HRQoL)** | Patient-reported outcomes | Increasingly required for HTA |

### 2.3 Response criteria frameworks

| Framework | Tumor types | Core concept |
|---|---|---|
| **RECIST 1.1** | Solid tumors | Target + non-target lesion measurement; unidimensional (longest diameter) |
| **iRECIST** | Immunotherapy solid tumors | Accounts for pseudoprogression; confirmed progression requires follow-up scan |
| **Cheson / Lugano criteria** | Lymphoma | Staging + response criteria for NHL/HL |
| **IWG criteria** | MDS, AML, CLL | Hematologic response definitions |
| **IMWG response criteria** | Multiple myeloma | CR/VGPR/PR/MR framework |
| **mRECIST for HCC** | Hepatocellular carcinoma | Modified criteria accounting for liver imaging |
| **RANO** | Glioma / brain tumors | Specific CNS imaging response |

---

## §3. Regulatory Pathway — Oncology-Spesifik

### 3.1 FDA Oncology Center of Excellence (OCE)

OCE coordinates oncology drug + biologic + device review across CDER (drugs + some biologics), CBER (cell/gene therapy + some biologics), and CDRH (companion diagnostics). Established 2017 under 21st Century Cures Act.

**Project Orbis** — OCE-led parallel review initiative enabling simultaneous oncology drug review with international partners (FDA + Health Canada + MHRA + TGA Australia + Swissmedic + ANVISA Brazil + HSA Singapore + Israel MoH).

### 3.2 Accelerated approval discipline

Oncology most common AA pathway user:
- Single-arm study with ORR + DOR in refractory / orphan populations
- Confirmatory trial required post-approval to verify clinical benefit
- **FDA authority to withdraw accelerated approvals** if confirmatory evidence inadequate (e.g. Makena 2023, multiple oncology withdrawals per OCE)

**AA → full approval conversion discipline:** Post-approval confirmatory trial must demonstrate benefit; trial design matters (active comparator, appropriate endpoint, adequate power).

### 3.3 Breakthrough Therapy + Priority Review + Orphan Drug

Oncology-heavy usage of all expedited pathways:
- Breakthrough Therapy: ~50% of designations are oncology
- Priority Review (6-month): standard for oncology NDA/BLA
- Orphan Drug: common for rare oncology subsets (cholangiocarcinoma, GIST, uveal melanoma, etc.)
- Real-Time Oncology Review (RTOR) — OCE pilot for rolling submission

### 3.4 Companion diagnostic (CDx) co-approval

Biomarker-driven oncology drugs typically require co-approved CDx:
- Keytruda + PD-L1 testing (22C3, SP263, SP142, 28-8)
- Enhertu + HER2 IHC/ISH
- Vitrakvi + NTRK fusion testing
- Pluvicto + PSMA-PET imaging (not traditional IHC CDx but same concept)

FDA CDRH reviews CDx; co-development timeline coordination complex.

### 3.5 AdComm (Oncologic Drugs Advisory Committee — ODAC)

ODAC reviews controversial oncology approvals. Post-2021 ODAC has been increasingly critical of:
- Accelerated approvals without robust confirmatory trials
- Subset analyses driving approvals
- Dosing approval without optimization (Project Optimus)

**Project Optimus (OCE 2021):** Push for dose optimization before pivotal trials — reducing "highest tolerable dose" paradigm in favor of lowest effective dose.

---

## §4. Clinical Practice Standards + Guidelines

### 4.1 Guideline hierarchy

| Guideline | Scope | Update frequency |
|---|---|---|
| **NCCN (National Comprehensive Cancer Network)** | US clinical practice, consensus-based | Multiple updates per year per tumor type |
| **ESMO Clinical Practice Guidelines** | European clinical practice | 2-3 year cycle per tumor type |
| **ASCO Guidelines** | Specific topic recommendations (sequencing, biomarker testing, supportive care) | Topic-specific |
| **EHA / EBMT guidelines** | Hematology-focused | Topic-specific |

NCCN has become de facto global reference even outside US due to frequency + detail.

### 4.2 Line of therapy framework

For most metastatic solid tumors, treatment paradigm follows:
```
1L (first-line)  — standard-of-care regimen, often most aggressive option
2L (second-line) — post-progression, often different mechanism
3L (third-line)  — further salvage options
4L+              — limited options, often clinical trial considered
```

Hematology: different framework (induction → consolidation → maintenance → salvage).

### 4.3 Biomarker testing algorithms

Modern oncology requires comprehensive biomarker testing at diagnosis:
- NSCLC: EGFR, ALK, ROS1, BRAF, MET, RET, KRAS G12C, NTRK, PD-L1
- mCRC: RAS, BRAF, MSI/MMR, HER2, NTRK
- Breast cancer: ER, PR, HER2 (IHC + ISH if indeterminate), HRD (if triple-negative)
- Multiple myeloma: FISH for cytogenetic risk (del17p, t(4;14), amp1q)

**Next-generation sequencing (NGS)** increasingly replaces sequential single-gene testing — Foundation Medicine, Caris, Tempus, Guardant360 (liquid biopsy).

---

## §5. Oncology-Spesifik Market Dynamics

### 5.1 High-cost specialty market characterization

Oncology is the **largest global specialty pharma market** (~$250B+ globally 2024):
- Price points $100K-$500K+ per treatment course
- Payer access tightly managed via prior authorization + step therapy
- 340B program impact on hospital procurement economics
- Medicare Part B vs Part D dynamics (physician-administered vs self-administered)

### 5.2 Clinical pathway + payer-clinician alignment

- **US:** PBM rebate-based competition; Medicare Part B Inflation Reduction Act (2022) price negotiation — first oncology drugs in negotiation from 2026 (Imbruvica, others)
- **EU:** HTA agency evaluations (NICE UK, G-BA/IQWiG Germany, HAS France, AIFA Italy); significant price heterogeneity
- **Japan:** PMDA approval + Chuikyo price-setting
- **China:** NMPA approval + National Reimbursement Drug List (NRDL) annual negotiation
- **Türkiye:** TİTCK approval + SGK SUT reimbursement + SGK quota system for oncology

### 5.3 Pipeline concentration patterns

Contemporary oncology pipeline concentrates on:
- **Validated targets** (HER2, EGFR, PD-1/L1, BCMA, CD19, CD20) — dense competition
- **Emerging targets** (TROP2, Nectin-4, B7-H4, CLDN18.2, DLL3, KRAS G12C, multiple AML targets) — first-mover advantage
- **Mechanism expansion** (new payloads, bispecifics, novel IO combinations, ADC platforms)

### 5.4 IO combination era

Post-Keytruda dominance, oncology pipeline defined by **combination strategies**:
- Anti-PD-(L)1 + chemotherapy
- Anti-PD-(L)1 + ADC (e.g. Padcev + pembro in mUC — EV-302 established 1L)
- Anti-PD-(L)1 + anti-CTLA-4 (ipi+nivo melanoma, HCC)
- Anti-PD-(L)1 + targeted therapy (atezo+bev HCC)
- Anti-PD-(L)1 + novel IO (LAG-3, TIGIT, others)

---

## §6. Tumor-Spesifik Clinical Sub-domains

### 6.1 Breast cancer (HR+/HER2- / HER2+ / TNBC)

- **HR+/HER2- (largest subset):** CDK4/6i + endocrine 1L; post-progression ER/PR pathway disruption (fulvestrant, elacestrant, inavolisib etc.); HR+/HER2-low now includes T-DXd; PALOMA/MONALEESA/MONARCH CDK4/6i class
- **HER2+:** trastuzumab-based combinations 1L; T-DXd 2L (DESTINY-Breast03); tucatinib combos 3L+ (HER2CLIMB)
- **TNBC:** chemotherapy + IO (pembro + chemo neoadjuvant KEYNOTE-522); sacituzumab govitecan Trodelvy post-chemo; PARP inhibitors for BRCA+

### 6.2 Lung cancer (NSCLC / SCLC)

- **NSCLC — driver mutation-positive:** matched TKI (osimertinib EGFR, alectinib/lorlatinib ALK, entrectinib/repotrectinib ROS1, capmatinib/tepotinib MET, etc.)
- **NSCLC — non-driver / PD-L1 high:** IO monotherapy (pembro KEYNOTE-024)
- **NSCLC — non-driver / PD-L1 low:** IO + chemotherapy combinations
- **SCLC:** IO + platinum etoposide (IMpower133 atezolizumab, CASPIAN durvalumab); tarlatamab BiTE for extensive-stage post-chemo (DeLLphi-304)
- **NSCLC ADC era:** T-DXd HER2-mutant NSCLC, HER3-DXd (Patritumab deruxtecan) in development

### 6.3 Colorectal cancer

- **MSS (85% of mCRC):** chemotherapy (FOLFOX / FOLFIRI) ± bevacizumab / cetuximab / panitumumab; BRAF V600E = encorafenib + cetuximab; KRAS G12C emerging (adagrasib, sotorasib); HER2+ mCRC (T-DXd DESTINY-CRC02, tucatinib+trastuzumab MOUNTAINEER)
- **MSI-H (5% of mCRC):** pembrolizumab KEYNOTE-177 1L standard; nivolumab ± ipilimumab alternatives

### 6.4 Prostate cancer (mHSPC / nmCRPC / mCRPC)

- **mHSPC:** ADT backbone + androgen receptor pathway inhibitor (abiraterone, enzalutamide, apalutamide, darolutamide) + selected chemo
- **nmCRPC:** apalutamide / enzalutamide / darolutamide
- **mCRPC:** ARPI progression → docetaxel → cabazitaxel → Pluvicto (PSMA-PET-positive VISION + PSMAfore now pre-taxane); olaparib / niraparib for HRR-positive
- See `task-modality-radiopharm.md` for Pluvicto-spesifik disciplines

### 6.5 Melanoma

- **Advanced / metastatic:** IO-first era — nivolumab ± ipilimumab (CheckMate 067 landmark) or pembrolizumab monotherapy; BRAF+ patients may start with BRAF+MEK (dabrafenib+trametinib, encorafenib+binimetinib); T-VEC intralesional for some
- **Adjuvant:** pembrolizumab or nivolumab post-resection; dabrafenib+trametinib for BRAF+

### 6.6 Hematologic malignancies

- **DLBCL:** R-CHOP or Polivy+R-CHP (POLARIX) 1L; CAR-T (Yescarta 2L per ZUMA-7; Breyanzi); glofitamab + bispecific CD20xCD3 + polatuzumab-GemOx
- **Multiple myeloma:** induction (4-drug Dara-VRd/Isa-VRd) → ASCT → maintenance (lenalidomide); R/R: daratumumab-based → BCMA-directed (CAR-T Abecma/Carvykti, bispecific teclistamab/elranatamab; GPRC5D talquetamab)
- **Acute leukemia:** AML emerging targeted options (midostaurin FLT3, gilteritinib, ivosidenib IDH1, enasidenib IDH2, venetoclax + HMA low-intensity); B-ALL (blinatumomab BiTE, Inotuzumab ADC, CAR-T Aucatzyl/Tecartus/Kymriah)

---

## §7. Regional Oncology Market Disciplines

### 7.1 US market
- Medicare Part B drug pricing (IRA 2022 negotiation from 2026)
- 340B covered entity procurement
- Commercial payer PBM rebate dynamics
- NCCN Compendium coverage → Medicare Part D mandatory coverage
- Medicaid drug rebate program

### 7.2 EU / UK markets
- NICE (UK) — cost-per-QALY £20,000-£30,000 threshold; end-of-life supplement for oncology
- G-BA / IQWiG (Germany) — benefit assessment drives price negotiation
- HAS (France) — ASMR rating + CEESP cost-effectiveness
- AIFA (Italy) — innovation rating + managed entry agreements
- EMA centralized + parallel HTA consultations

### 7.3 Asia-Pacific
- Japan PMDA + Chuikyo foreign average price reference
- China NMPA + NRDL annual negotiation — dramatic oncology price cuts since 2018
- Korea HIRA benefit assessment
- Taiwan NHI
- Australia PBS

### 7.4 Türkiye oncology market
- **TİTCK onay pathway** — EMA reliance yaygın
- **SGK SUT geri ödeme** — oncology için SUT EK-4D + SUT EK-4H (hastane protokolleri) listelerinde kabul gerekir
- **Endikasyon dışı kullanım (off-label)** — SGK özel onay gerekli; TİTCK endikasyon dışı komisyonu
- **Yurt dışı ilaç** — SGK yurt dışı ilaç dairesi üzerinden access (uzun prosedür)
- **Oncology konsey raporu** — çoğu ileri onkoloji ilacı için multidisipliner konsey raporu SGK reimbursement şartı
- **Kanser Ağı (Cancer Network)** — Sağlık Bakanlığı tarafından koordine edilen onkoloji referans merkezleri
- **SUT kısıtlamaları** — bazı ilaçlar ileri basamak (2L+), biomarker pozitiflik, klinik evre şartına tabi geri ödenir
- **Üretici yerli payı (yüksek fiyatlı onkoloji):** TİTCK + SGK pazarlığı sonrası indirim bantları %20-40 iskonto tipik

---

## §8. Multi-Layer T3 Integration

### 8.1 Oncology + modality template stacking examples

```
"HER2+ mBC treatment landscape"
  Layer 0: task-modality.md (generic)
  Layer 1: task-modality-adc.md (because T-DXd + Kadcyla are ADCs)
  Layer 2: task-ta-oncology.md (breast cancer sub-domain §6.1)
  → synthesis: ADC disciplines + oncology line-of-therapy + biomarker framework

"CAR-T landscape in DLBCL"
  Layer 0: task-modality.md
  Layer 1: task-modality-cellgene.md
  Layer 2: task-ta-oncology.md (hematology sub-domain §6.6)
  → synthesis: CAR-T disciplines + DLBCL line-of-therapy

"Pluvicto in mCRPC"
  Layer 0: task-modality.md
  Layer 1: task-modality-radiopharm.md
  Layer 2: task-ta-oncology.md (prostate sub-domain §6.4)
  → synthesis: radiopharm disciplines + mCRPC line-of-therapy
```

### 8.2 Ordering discipline

Layers load in parallel (no temporal dependency between layers). Synthesis phase combines all three into report. Confidence = minimum of layer source confidences.

---

## §9. Confidence Stamping for Oncology Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval dates + oncology indication | **High** (statutory) |
| Pivotal trial efficacy (HR, p-value, mPFS, mOS) | **High** (peer-reviewed + FDA briefing documents) |
| NCCN / ESMO guideline recommendations | **High** (authoritative guideline primary) |
| Real-world oncology outcomes | **Medium** (registry quality varies) |
| Biomarker prevalence (%) by tumor type | **Medium** (varies by population studied) |
| Sequencing preferences (clinician survey-based) | **Low-Medium** (proprietary surveys typically) |
| Net pricing after payer rebates | **Low** (confidential) |
| Forward-looking competitive share | **Low-Medium** |
| Confidential sponsor-internal trial data | Should not be claimed |

---

## §10. Forbidden Patterns

- ❌ Strategic recommendations for specific sponsors' oncology portfolios without T6-Defense activation
- ❌ Treating single-arm accelerated approvals as equivalent evidence to randomized Phase 3
- ❌ Speculating on confidential IQVIA oncology market data
- ❌ Ignoring biomarker subset size when making landscape claims
- ❌ Conflating ORR (accelerated approval basis) with OS (definitive survival benefit)
- ❌ Using pre-Project Optimus dosing as rationale for current regulatory strategy
- ❌ Generalizing one tumor type's dynamics to others (NSCLC biomarker complexity ≠ TNBC; mCRC MSI dynamics ≠ solid tumors generally)

---

## §11. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. First Layer 2 (Therapeutic Area) T3 template — establishes Layer 2 architectural pattern. Oncology TA covers: disease state classification (tumor type × stage × biomarker × line of therapy × prior therapy), endpoint hierarchy (OS gold standard / PFS common primary / DFS adjuvant / ORR + DOR accelerated approval basis / pCR neoadjuvant / MRD hematology / HRQoL HTA), response criteria frameworks (RECIST 1.1 / iRECIST for IO / Cheson-Lugano lymphoma / IWG MDS/AML/CLL / IMWG myeloma / mRECIST HCC / RANO glioma), FDA oncology-spesifik regulatory (OCE coordination + Project Orbis international parallel review + accelerated approval discipline with withdrawal authority + Breakthrough + Priority Review + Orphan + RTOR + companion diagnostic co-approval + ODAC post-2021 increased criticality + Project Optimus dose optimization paradigm shift), guideline hierarchy (NCCN US / ESMO EU / ASCO topic-specific / EHA EBMT hematology), line of therapy framework + biomarker testing algorithms (NSCLC comprehensive panel, mCRC RAS/BRAF/MSI/HER2/NTRK, breast ER/PR/HER2/HRD, MM FISH cytogenetic) + NGS vs sequential, market dynamics (~$250B global specialty pharma largest segment + IRA 2022 Part B negotiation from 2026 + 340B + NCCN Compendium mandatory coverage + IO combination era post-Keytruda dominance), tumor-spesifik sub-domains (breast HR+/HER2+/TNBC + NSCLC driver-positive/PD-L1 + SCLC + mCRC MSS/MSI + prostate mHSPC/nmCRPC/mCRPC + melanoma + hematology DLBCL/MM/AML/ALL), regional oncology market disciplines (US Medicare Part B + EU NICE/IQWiG/HAS/AIFA + Japan PMDA+Chuikyo + China NMPA+NRDL + Türkiye TİTCK+SGK SUT EK-4D+EK-4H + off-label komisyonu + kanser ağı referans merkezleri), multi-layer T3 integration pattern with examples (HER2+ mBC = generic + ADC + oncology; DLBCL CAR-T = generic + cell/gene + oncology; mCRPC Pluvicto = generic + radiopharm + oncology), confidence stamping. New manifest gate G41. Cross-references: task-modality-{adc, cellgene, rna, radiopharm}.md for modality disciplines, sub-protocol-turkey.md for Türkiye disciplines, analytics-framework.md for cannibalization + tumor-spesifik NPV, api-integrations.md for FDA + ClinicalTrials.gov + NCCN + SEC primary sources.
