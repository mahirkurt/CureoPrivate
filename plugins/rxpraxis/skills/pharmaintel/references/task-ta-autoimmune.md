# task-ta-autoimmune.md

**T3 Therapeutic Area Template — Autoimmune / Immunology / Inflammation (v3.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Anti-TNF biosimilar landscape in RA" = Layer 0 generic + Layer 1 biosimilar + Layer 1 fusion protein (Enbrel) + Layer 2 autoimmune.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "autoimmune", "immunology", "immunoinflammatory", "I&I", "otoimmün", "inflamasyon", "inflammation"
- Disease terms: "rheumatoid arthritis", "RA", "romatoid artrit", "psoriasis", "sedef", "psoriatic arthritis", "PsA", "ankylosing spondylitis", "AS", "axial SpA", "ulcerative colitis", "UC", "Crohn's disease", "CD", "inflammatory bowel disease", "IBD", "multiple sclerosis", "MS", "systemic lupus erythematosus", "SLE", "lupus", "atopic dermatitis", "AD", "atopik dermatit", "ekzema", "asthma", "severe asthma", "COPD", "hidradenitis suppurativa", "HS", "vitiligo", "alopecia areata"
- Mechanism terms: "anti-TNF", "TNF inhibitor", "IL-17 inhibitor", "IL-23 inhibitor", "IL-6 inhibitor", "JAK inhibitor", "BTK inhibitor", "S1P modulator", "anti-CD20", "anti-IgE", "anti-IL-4/IL-13", "anti-IL-5", "BAFF inhibitor", "T cell costimulation"
- Asset names: "Humira", "adalimumab", "Enbrel", "etanercept", "Remicade", "infliximab", "Simponi", "golimumab", "Cimzia", "certolizumab", "Cosentyx", "secukinumab", "Taltz", "ixekizumab", "Skyrizi", "risankizumab", "Tremfya", "guselkumab", "Stelara", "ustekinumab", "Dupixent", "dupilumab", "Xeljanz", "tofacitinib", "Rinvoq", "upadacitinib", "Olumiant", "baricitinib", "Bimzelx", "bimekizumab"

### 1.2 Implicit triggers
- Biologic-vs-biosimilar landscape in autoimmune
- Post-Humira LOE dynamics (adalimumab biosimilar wave 2023+)
- Cross-indication portfolio analysis (single biologic across RA/PsA/AS/PsO/IBD/HS)

### 1.3 NOT triggered by
- ❌ User employer with immunology portfolio (AbbVie, JNJ, UCB, Amgen, Novartis, Eli Lilly, Pfizer)
- ❌ User rheumatology/dermatology/gastroenterology specialty interest

---

## §2. Foundational I&I Framework

### 2.1 Disease spectrum

Autoimmune/inflammatory diseases cluster into patho-physiological families:

| Family | Examples | Dominant cytokine axis |
|---|---|---|
| **Th1-driven** | RA (partly), MS (partly) | IFN-γ, TNF |
| **Th2-driven** | Atopic dermatitis, asthma, EoE, allergic rhinitis | IL-4/IL-13/IL-5 |
| **Th17-driven** | Psoriasis, PsA, AS, HS | IL-17/IL-23 |
| **Mixed / TNF-driven** | RA, IBD (UC+CD), HS | TNF-α dominant |
| **B-cell-driven** | SLE, MS, RA subset | BAFF, CD20-positive B cells |
| **Type 1 IFN-driven** | SLE, cutaneous lupus, dermatomyositis | IFN-α/β |

Mechanism-targeted biologics have transformed treatment algorithms by matching drug to cytokine axis.

### 2.2 Line of therapy / step edit framework

Unlike oncology linear line-of-therapy, autoimmune treatment typically:
1. **Conventional synthetic DMARDs (csDMARDs)** — MTX, SSZ, HCQ, leflunomide (RA); 5-ASA, thiopurines (IBD)
2. **Targeted synthetic DMARDs (tsDMARDs)** — JAK inhibitors, PDE4
3. **Biologic DMARDs (bDMARDs)** — TNF-α inhibitors, IL-6, IL-17, IL-23, anti-CD20
4. **Advanced biologics** — emerging mechanisms (BTK, TYK2, etc.)

Payer step edit policy typically requires csDMARD failure before biologic access; some jurisdictions require TNF-i failure before non-TNF-i biologic.

### 2.3 Endpoint frameworks by disease

| Disease | Primary endpoints |
|---|---|
| **RA** | ACR20/50/70 response; DAS28 remission/low disease activity; SDAI/CDAI; radiographic progression (mTSS) |
| **PsO** | PASI 75/90/100; IGA clear/almost clear; BSA reduction |
| **PsA** | ACR20/50/70; PASI; MDA (minimal disease activity) composite |
| **AS** | ASAS20/40; BASDAI; MRI inflammation |
| **UC** | Mayo score remission; mucosal healing endoscopy; fecal calprotectin |
| **CD** | CDAI remission; endoscopic healing; SES-CD; TNF trough levels |
| **AD** | EASI 75/90; IGA clear; pruritus NRS reduction |
| **MS** | ARR (annualized relapse rate); EDSS progression; MRI new/enlarging lesions |
| **SLE** | SRI-4; BICLA; flare reduction |

---

## §3. Dominant Mechanism Classes + Landscape

### 3.1 TNF-α inhibitor class (foundational biologic class)

| Asset | Type | Indications | LOE US | LOE EU |
|---|---|---|---|---|
| **Humira (adalimumab)** | mAb | RA/PsA/AS/PsO/CD/UC/HS/noninfectious uveitis | 2023 (biosimilars since Jan 2023) | 2018 |
| **Enbrel (etanercept)** | Fc-fusion (see task-modality-fusion.md) | RA/PsA/AS/PsO | 2029 (patent thicket) | 2015 |
| **Remicade (infliximab)** | mAb | RA/CD/UC/PsA/AS/PsO | 2016 (biosimilars since 2016) | 2015 |
| **Simponi (golimumab)** | mAb | RA/PsA/AS/UC | 2024 | 2024 |
| **Cimzia (certolizumab)** | PEGylated Fab | RA/PsA/AS/PsO/CD | 2024 | 2024 |

**Humira post-LOE dynamics 2023+:** Major biosimilar wave including Amjevita (Amgen), Cyltezo (Boehringer — interchangeable), Hyrimoz (Sandoz), Hadlima (Samsung Bioepis), Abrilada (Pfizer), Idacio (Fresenius Kabi), Yusimry (Coherus), Simlandi (Alvotech interchangeable), many more. Biosimilar uptake slower than expected due to PBM rebate dynamics + formulation differences (citrate-free vs citrate).

See `task-modality-biosimilar.md` for biosimilar disciplines.

### 3.2 IL-17 / IL-23 class (PsO/PsA/AS)

- **IL-17A:** Cosentyx (secukinumab), Taltz (ixekizumab)
- **IL-17A + IL-17F dual:** Bimzelx (bimekizumab) — EMA 2021, FDA 2023 (delayed by deficiency letter)
- **IL-17 receptor A:** Siliq (brodalumab)
- **IL-23 p19:** Tremfya (guselkumab), Skyrizi (risankizumab), Ilumya (tildrakizumab)
- **IL-12/23 p40:** Stelara (ustekinumab) — transitioning to IL-23p19 specificity as preferred
- **Stelara biosimilars 2025+:** multiple approvals (Wezlana Amgen, Selarsdi Alvotech, Pyzchiva Samsung Bioepis, Otulfi Fresenius+Cimerli partner)

### 3.3 JAK inhibitor class

Small molecule mechanism — cross-reference `task-modality-smallmol.md`:
- **Xeljanz (tofacitinib)** — RA/PsA/UC/JIA/AS
- **Rinvoq (upadacitinib)** — RA/PsA/AS/UC/CD/AD/HS
- **Olumiant (baricitinib)** — RA/alopecia areata/COVID-19
- **Cibinqo (abrocitinib)** — AD
- **Jyseleca (filgotinib)** — RA (EU; no US approval after FDA CRL)

**FDA 2021 JAK black box warning** — cardiovascular + malignancy signal per ORAL Surveillance post-marketing trial (tofacitinib vs TNF-i). Class effect conclusion applied to entire JAK inhibitor class (Xeljanz, Rinvoq, Olumiant labels updated).

### 3.4 Th2 axis (AD, asthma)

- **Dupixent (dupilumab)** — IL-4Rα (blocks both IL-4 + IL-13): AD/asthma/EoE/CRSwNP/PN
- **IL-5 axis:** Nucala (mepolizumab), Fasenra (benralizumab), Cinqair (reslizumab) — eosinophilic asthma
- **Anti-IgE:** Xolair (omalizumab) — asthma/CSU/food allergy (first food allergy biologic 2024)
- **Anti-TSLP:** Tezspire (tezepelumab) — asthma

### 3.5 B-cell-targeted (SLE, MS, RA)

- **Anti-CD20:** Rituxan (rituximab) — RA/GPA-MPA/pemphigus; Ocrevus (ocrelizumab) MS; Kesimpta (ofatumumab) MS; Briumvi (ublituximab) MS
- **BAFF:** Benlysta (belimumab) — SLE + lupus nephritis
- **Anti-CD19:** Uplizna (inebilizumab) — NMOSD
- **CAR-T in autoimmune:** emerging (SLE, myasthenia gravis investigational — Bristol/2seventy, Kyverna, Cabaletta — Phase 1/2)

### 3.6 S1P modulators (MS, UC)

- **Gilenya (fingolimod)** — MS (generic 2020)
- **Mayzent (siponimod)** — MS
- **Zeposia (ozanimod)** — MS + UC
- **Ponvory (ponesimod)** — MS

### 3.7 Emerging mechanisms
- **TYK2:** Sotyktu (deucravacitinib) PsO + PsA development
- **BTK (oral):** multiple MS investigational (evobrutinib — fail; remibrutinib, tolebrutinib ongoing)
- **AhR modulators:** investigational AD (e.g. tapinarof Vtama topical approved)
- **FcRn antagonists:** Vyvgart (efgartigimod) myasthenia gravis, CIDP; Rystiggo (rozanolixizumab) MG

---

## §4. Regional Autoimmune Market Disciplines

### 4.1 US market
- Step therapy + prior authorization ubiquitous
- PBM rebate warfare drives net prices (Humira net price post-LOE much lower than list; ~40-60% rebate typical)
- Specialty pharmacy channel dominant
- Express Scripts National Preferred Formulary changes major share-shifter

### 4.2 EU market
- Biosimilar uptake aggressive (>90% for mature anti-TNF biosimilar classes)
- Tender-based procurement in many countries (UK NHS, Nordic countries, Italy regional)
- Cost-containment driven substitution policies

### 4.3 Türkiye autoimmune ekosistemi
- **TİTCK onay** — EMA reliance dominant
- **SGK SUT geri ödeme** — autoimmune biologics için SUT EK-4C listesinde; step therapy zorunlu (en az 6 ay csDMARD/cDMARD başarısızlığı)
- **Biyobenzer otomatik geçiş** — SGK biyoeşdeğer grup içinde en düşük fiyatlı ürün üzerinden ödeme (bkz. `task-modality-biosimilar.md`)
- **Romatoloji + gastroenteroloji + dermatoloji + nöroloji + immunoloji + pulmonoloji multidisipliner** uzman onay gerekebilir; hastane bazlı protokol
- **Yerli biyobenzer üreticiler:** Em Pharma (rituximab, trastuzumab — onkoloji ağırlıklı ama TNF-i denemeleri Ar-Ge'de), Abdi İbrahim (AbdiBio etanercept biosimilar adayı), Atabay, Nobel İlaç
- **Yerli jenerik (small molecule autoimmune):** metotreksat + HCQ + SSZ + leflunomide yerli üretim mevcut; tofacitinib/Rinvoq henüz patent altında

---

## §5. Confidence Stamping for Autoimmune Claims

| Claim type | Confidence |
|---|---|
| FDA / EMA approval + indication | **High** |
| Pivotal trial efficacy per published trials | **High** |
| Real-world biosimilar switching outcomes | **Medium-High** (multiple RWE datasets now mature) |
| Net pricing post-rebate | **Low** |
| JAK cardiovascular/malignancy class-effect extrapolation | **Medium** (ORAL Surveillance was tofacitinib-spesifik; class attribution debated) |
| Future indication extrapolation | **Low-Medium** |

---

## §6. Forbidden Patterns

- ❌ Treating JAK class cardiovascular signal as universal to all JAKis without trial-spesifik evidence
- ❌ Conflating IL-17A-only with IL-17A/F dual inhibitors (different mechanism profile)
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Speculating on confidential Humira biosimilar rebate structures
- ❌ Oversimplifying Th1/Th2/Th17 taxonomy as discrete (significant overlap + plasticity)
- ❌ Ignoring citrate-vs-citrate-free Humira biosimilar formulation differences affecting switching dynamics

---

## §7. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. Layer 2 autoimmune TA template covering: disease pathophysiology family taxonomy (Th1/Th2/Th17/TNF/B-cell/Type 1 IFN), step therapy framework (csDMARD → tsDMARD → bDMARD), endpoint frameworks by disease (ACR RA, PASI psoriasis, DAS28 RA, CDAI Crohn's, Mayo UC, EASI AD, ARR MS, SRI-4 SLE), TNF-α inhibitor class with Humira LOE 2023 biosimilar wave + Enbrel US patent thicket through 2029 + cross-ref to fusion template, IL-17/IL-23 class with bimekizumab FDA CRL-delayed approval + Stelara biosimilar wave 2025, JAK inhibitor class with FDA 2021 CV/malignancy black box warning per ORAL Surveillance + class extrapolation debate, Th2 axis dupilumab franchise expansion, B-cell-targeted + emerging CAR-T in autoimmune, S1P modulators for MS/UC, emerging TYK2/BTK/FcRn antagonists (Sotyktu, Vyvgart), regional markets with US PBM rebate dynamics + EU tender-based biosimilar uptake + Türkiye TİTCK + SGK SUT EK-4C + step therapy + multidisipliner konsey + yerli biosimilar/jenerik ekosistemi. New manifest gate G42. Cross-references task-modality-biosimilar.md (biosimilar landscape), task-modality-fusion.md (Enbrel), task-modality-smallmol.md (JAK inhibitors).
