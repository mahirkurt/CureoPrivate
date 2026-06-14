# task-modality-pdt.md

**T3 Modality Template — Photodynamic Therapy (PDT) (v2.6.0)**

> **Architectural context:** Niche modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when photodynamic therapy modality is in scope.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "photodynamic therapy", "PDT", "fotodinamik tedavi", "photochemotherapy", "photodynamic diagnosis", "PDD", "fluorescence-guided surgery", "FGS"
- Photosensitizer terms: "porfimer sodium", "Photofrin", "5-aminolevulinic acid", "5-ALA", "Levulan", "Ameluz", "methyl aminolevulinate", "MAL", "Metvix", "verteporfin", "Visudyne", "temoporfin", "Foscan", "padeliporfin", "Tookad", "talaporfin"
- Asset terms: "Gleolan" (5-ALA neurosurgery), "Ameluz", "Levulan Kerastick", "BLU-U" (light source), "Aktilite" (LED light source)
- Application terms: "intraoperative photodiagnosis", "photodynamic ablation", "photobiomodulation"

### 1.2 Implicit semantic triggers
- High-grade glioma surgical resection (5-ALA fluorescence)
- Actinic keratosis treatment (5-ALA + MAL)
- Basal cell carcinoma non-surgical (MAL + ALA)
- Wet AMD subfoveal CNV (verteporfin historical, displaced by anti-VEGF)
- Bile duct + esophageal cancer palliation (porfimer sodium)

### 1.3 NOT triggered by
- ❌ User employer being a PDT developer (Pinnacle Biologics — porfimer sodium; Sun Pharmaceutical / DUSA — Levulan; NovaBay; Biofrontera — Ameluz; Bausch + Lomb — Visudyne)
- ❌ User memory-derived dermatology / neurosurgery / ophthalmology specialty interest

---

## §2. Foundational Conceptual Framework

### 2.1 Three-component PDT mechanism

```
                  ┌──────────────────┐
                  │  Photosensitizer │ ← drug administered systemically or topically
                  │  (PS)            │
                  └────────┬─────────┘
                           │
                           │  Selective accumulation in target tissue
                           │  (tumor, neoplastic, neovascular)
                           ▼
                  ┌──────────────────┐
                  │  Light delivery  │ ← specific wavelength matched to PS absorption
                  │  (laser / LED)   │
                  └────────┬─────────┘
                           │
                           │  Photoactivation
                           ▼
                  ┌──────────────────┐
                  │  Reactive Oxygen │ ← singlet oxygen (¹O₂) primarily
                  │  Species (ROS)   │
                  └────────┬─────────┘
                           │
                           ▼
              Cell death + vascular damage + immune activation
```

### 2.2 The three pillars and their independence

PDT requires three coordinated components:
1. **Photosensitizer (PS)** — chromophore drug
2. **Light** — specific wavelength matching PS absorption maximum
3. **Oxygen** — present in tissue (PDT impotent in hypoxic tissue)

Removing any pillar = no therapeutic effect. This creates **dual selectivity**: PS preferentially accumulates in target tissue, AND light is delivered only to target area.

### 2.3 Type I vs Type II photochemistry

**Type I reactions:** PS + substrate → radical species + ROS (hydroxyl, superoxide)
**Type II reactions:** PS + ³O₂ → ¹O₂ singlet oxygen (dominant for clinical PDT)

Singlet oxygen has very short diffusion distance (~10-100 nm in cells) → focal damage at site of generation → spatially precise.

### 2.4 PDT vs photodynamic diagnosis (PDD)

| Concept | Mechanism | Examples |
|---|---|---|
| **PDT** | Therapeutic — destroys target tissue | Photofrin esophageal cancer, Ameluz AK |
| **PDD / FGS** | Diagnostic — visualizes target tissue via fluorescence | Gleolan glioma, Cysview NMIBC |

5-ALA is the unique photosensitizer used in BOTH modalities (FGS for glioma + PDT for skin) — depends on light wavelength applied.

---

## §3. Photosensitizer Class Taxonomy

### 3.1 First-generation: porfimer sodium

**Photofrin (porfimer sodium)** — Concordia/Pinnacle Biologics
- Mixture of hematoporphyrin oligomers
- IV administration
- Peak absorption ~630 nm (red light)
- FDA approvals: esophageal cancer (1995), endobronchial NSCLC, Barrett's esophagus high-grade dysplasia, ampullary cholangiocarcinoma
- Limitation: prolonged skin photosensitivity (4-6 weeks; patients must avoid sunlight)

### 3.2 Second-generation: ALA-based prodrug class

**Aminolevulinic acid (5-ALA)** = endogenous heme synthesis precursor; PRODRUG that intracellularly converts to protoporphyrin IX (PpIX), the active photosensitizer.

**Topical 5-ALA preparations:**
- **Levulan Kerastick** (Sun Pharma / DUSA) — actinic keratosis (face/scalp); typically photoactivated with BLU-U (417 nm) or red light (~635 nm)
- **Ameluz** (Biofrontera) — actinic keratosis, basal cell carcinoma, field cancerization

**Methyl aminolevulinate (MAL):**
- **Metvix / Metvixia** (Galderma) — actinic keratosis, BCC

**Oral 5-ALA:**
- **Gleolan** (NX Development Corp) — FDA approved 2017 for fluorescence-guided surgery of high-grade gliomas (intraoperative visualization, NOT therapeutic PDT)

### 3.3 Third-generation: novel photosensitizers

| Asset | INN | Sponsor | Indication |
|---|---|---|---|
| **Visudyne** | Verteporfin | Bausch + Lomb (formerly QLT / Novartis) | Wet AMD (largely displaced by anti-VEGF; some niche use polypoidal choroidal vasculopathy) |
| **Foscan** | Temoporfin | Biolitec | Head and neck squamous cell carcinoma palliation |
| **Tookad** | Padeliporfin (palladium-based, vascular-targeted) | STEBA Biotech | Localized prostate cancer (EU approval 2017; not US-approved) |

### 3.4 Wavelength engineering principle

PS absorption peaks determine light source selection:
- **Red light (~630 nm)** — porfimer sodium, MAL, ALA-PpIX peak; deepest tissue penetration (~5-10 mm)
- **Blue light (~400-410 nm)** — alternative ALA-PpIX activation (BLU-U); shallow penetration (~1-2 mm); ideal for superficial dermatologic targets
- **Near-infrared (700-800 nm)** — emerging 3rd-gen photosensitizers; deeper penetration

---

## §4. Approved PDT Indication Landscape

### 4.1 Oncology indications

| Indication | Photosensitizer | Approval |
|---|---|---|
| Esophageal cancer (palliation) | Photofrin | FDA 1995 (oldest PDT approval) |
| Barrett's esophagus high-grade dysplasia | Photofrin | FDA 2003 (largely displaced by RFA) |
| Endobronchial non-small cell lung cancer | Photofrin | FDA |
| Ampullary cholangiocarcinoma | Photofrin | FDA 2017 |
| Head and neck SCC palliation (primary, recurrent) | Foscan | EMA |
| Localized prostate cancer (low-risk, intermediate-risk) | Tookad | EMA 2017 |
| High-grade glioma (FGS, NOT therapeutic PDT) | Gleolan (5-ALA) | FDA 2017, EMA earlier |

### 4.2 Dermatology indications

| Indication | Photosensitizer | Approval |
|---|---|---|
| Actinic keratosis (face, scalp) | Levulan Kerastick (5-ALA) + BLU-U | FDA 1999 (DUSA) |
| Actinic keratosis (severe/widespread) | Ameluz (5-ALA gel) + Aktilite/BF-RhodoLED | FDA 2016 (Biofrontera) |
| Actinic keratosis | Metvix (MAL) + Aktilite | EMA + various; limited US |
| Basal cell carcinoma (superficial, nodular) | Ameluz, Metvix | EMA |
| Field cancerization | Ameluz + Aktilite | EMA |

### 4.3 Ophthalmology — Visudyne

**Verteporfin (Visudyne):**
- FDA 2000 for choroidal neovascularization (CNV) due to wet AMD
- Largely displaced by anti-VEGF therapy (ranibizumab Lucentis 2006, aflibercept Eylea 2011, faricimab Vabysmo 2022)
- Niche current use: polypoidal choroidal vasculopathy (Asian patient population particularly), combination with anti-VEGF

---

## §5. Procedural + Clinical Disciplines

### 5.1 Drug-light interval (DLI)

Time between PS administration and light delivery — varies by PS pharmacokinetics:
- **Photofrin:** 40-50 hours post-IV (peak tumor selectivity)
- **5-ALA topical (Levulan):** 14-18 hours incubation under occlusion before light
- **Verteporfin (Visudyne):** 5-15 minutes post-IV (vascular-targeted PDT for CNV)
- **5-ALA oral (Gleolan):** 3-4 hours pre-surgery for FGS

### 5.2 Light delivery technology

| Light source | Application | Wavelengths |
|---|---|---|
| **Diode laser** (Ceralas, ML7710) | Endoscopic, interstitial | Tunable, often 630/689 nm |
| **LED arrays** (BLU-U, Aktilite, BF-RhodoLED) | Topical dermatology | Blue 417 nm, red 632 nm |
| **Optical fiber** | Endoscopic / cavity / interstitial | Coupled to laser source |
| **Endoscopic balloon diffuser** | Esophageal, bronchial | Cylindrical light distribution |

### 5.3 Skin photosensitivity precautions

Systemic PS-treated patients (Photofrin particularly) require **strict avoidance of bright light + sunlight** for extended periods (Photofrin: 4-6 weeks). Indoor lighting + filtered windows generally permitted. This is a major patient burden + adherence challenge limiting clinical adoption.

Topical 5-ALA + MAL require shorter precautions (24-48 hours occlusion → light delivery → photosensitivity declines rapidly).

### 5.4 Adverse event profile

**Common PDT adverse events:**
- Pain during light exposure (variable by site, severity, light dose)
- Erythema, edema at treatment site (expected response)
- Skin photosensitivity reactions (sunburn-like)
- Tissue necrosis at treatment area (intended effect; magnitude management)
- Strictures (esophageal Photofrin PDT)
- Photosensitivity-mediated burns from sunlight exposure

---

## §6. Regulatory Pathway

### 6.1 FDA framework — combination drug-device classification

PDT products typically reviewed as **combination products**:
- **Drug component** (photosensitizer) → CDER review
- **Device component** (light source) → CDRH review
- Lead center designated based on primary mode of action (typically CDER for systemic PS)

This creates regulatory complexity — both components must be approved + co-labeled. Light source devices often require 510(k) clearance separate from drug NDA.

### 6.2 Per-indication approvals

PDT approvals are **highly indication-specific**:
- Photofrin: separate NDA approvals for each indication (esophageal cancer, NSCLC, Barrett's, ampullary cholangiocarcinoma)
- Each approval requires dedicated clinical evidence + light source compatibility data

### 6.3 EMA + other jurisdictions

- **EMA:** centralized procedure for novel PSs (Foscan, Tookad); national approvals for some
- **MHRA:** post-Brexit handling
- **PMDA:** limited PDT approvals; some Asian-spesifik PDT use (Laserphyrin/talaporfin for HCC)
- **NMPA:** emerging Chinese PDT framework
- **TİTCK:** Photofrin + Levulan + Visudyne EMA reliance pathway; Gleolan FGS yetkisi tertiary nöroşirurji merkezleri

---

## §7. Commercial Trajectory + Market Dynamics

### 7.1 Mature market characterization

PDT remains a **niche modality** despite 30+ years of clinical use. Reasons:
- Indication-specific applications limit market size
- Procedural complexity (PS administration + light delivery + DLI management)
- Adverse event profile (especially skin photosensitivity) limits patient acceptance
- Specialist training requirements
- Anti-VEGF displaced verteporfin in main wet AMD use case

### 7.2 Approximate market size

Global PDT market estimated at $2-3B annually (combined PS + devices), growing modestly. Sub-segments:
- Dermatology PDT (Levulan, Ameluz, Metvix) — largest growing segment
- Oncology PDT (Photofrin, Foscan, Tookad) — niche
- FGS / PDD (Gleolan) — growing niche

### 7.3 Pricing benchmarks

- **Photofrin:** ~$5,000-7,000 per treatment
- **Levulan Kerastick:** ~$300-400 per stick (single AK lesion / area)
- **Ameluz:** ~$500-700 per gram (covers larger field treatment)
- **Gleolan:** ~$5,000-10,000 per surgical case (oral suspension)

---

## §8. Pipeline Dynamics

### 8.1 Next-generation photosensitizers

Active development:
- **Antibody-photosensitizer conjugates** (Akalux/cetuximab sarotalocan — Rakuten Medical; head and neck cancer; PMDA approved 2020 Japan)
- **Nanoparticle-encapsulated PSs** (preclinical / early clinical)
- **Conditional / activatable PSs** (tumor-specific protease activation)

### 8.2 Cetuximab sarotalocan — antibody-targeted PDT precedent

**Akalux (cetuximab saratolocan)** = EGFR-targeted PDT (also called "photoimmunotherapy"):
- IV cetuximab-IR700 dye conjugate
- Near-infrared light (~690 nm) activation
- PMDA-approved Japan 2020 for unresectable locally advanced/recurrent head and neck cancer
- US development discontinued 2024 (Phase 3 LUZERA-301 trial)

### 8.3 PDT + immunotherapy combinations

Investigation of PDT-induced immunogenic cell death + checkpoint inhibitor synergy. Multiple Phase 1/2 trials evaluating PDT + anti-PD-1 combinations.

### 8.4 PDT for hospital-acquired infections

Antimicrobial PDT (aPDT) for resistant infections — MRSA wound treatment, periodontal disease, oral candidiasis. Limited approved products; mostly off-label or research use.

---

## §9. Stakeholder-Spesifik Analytical Framework

### 9.1 Established PDT photosensitizer sponsors
- Indication expansion strategy
- Combination with light source partner
- Clinician training network maintenance

### 9.2 Light source / device sponsors
- Multi-PS platform compatibility positioning
- Outpatient procedure workflow optimization
- Reimbursement coding (CPT codes)

### 9.3 Antibody-targeted PDT challenger sponsors (Rakuten Medical etc.)
- Precision targeting positioning vs traditional PS broad localization
- Combination PD-(L)1 strategy

### 9.4 Klinisyen paydaşları (procedural specialists)
- Dermatology (AK + BCC field treatment) — dominant volume
- Pulmonology (endobronchial)
- Gastroenterology (esophageal palliation, cholangiocarcinoma)
- Neurosurgery (Gleolan FGS for glioma)
- Urology (prostate Tookad — EU only)
- Ophthalmology (residual verteporfin use)

### 9.5 Payer paydaşları
- Per-procedure reimbursement framework
- AK field treatment cost-effectiveness vs cryotherapy / topical agents
- Bundled payment for combined drug + light + procedure

### 9.6 Hasta paydaşları
- Skin photosensitivity precautions burden
- Treatment session scheduling (DLI + light delivery + recovery)
- Pain management during light exposure

---

## §10. Confidence Stamping for PDT Claims

| Claim type | Default confidence |
|---|---|
| FDA/EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy | **High** (peer-reviewed) |
| PS absorption spectra + photochemistry | **High** (physical/chemical constants) |
| Drug-light interval recommendations | **High** (label primary) |
| Real-world adoption rates | **Medium** (registry quality varies) |
| Light source utilization patterns | **Medium** (proprietary device data) |
| Combination PDT + IO efficacy | **Low** (early clinical) |
| Net pricing | **Low** (confidential) |

---

## §11. Forbidden Patterns

- ❌ Treating PDT as equivalent to phototherapy (UVB/UVA1/PUVA — different mechanism, different applications)
- ❌ Conflating photodynamic therapy (therapeutic) with photodynamic diagnosis / fluorescence-guided surgery (visualization)
- ❌ Assuming PDT can treat hypoxic tissue (mechanism requires oxygen)
- ❌ Strategic action recommendations for specific PDT sponsors without T6-Defense activation
- ❌ Recommending PDT in indications outside approved label (most uses indication-specific)
- ❌ Speculation about confidential photoimmunotherapy clinical data

---

## §12. Versioning & Changelog

- **v2.6.0 (2026-04-15):** Initial release. Niche modality T3 sub-template covering: 3-component PDT mechanism (photosensitizer + light + oxygen with dual selectivity creating spatial precision via singlet oxygen ~10-100 nm diffusion distance), Type I vs Type II photochemistry (Type II singlet oxygen dominant clinical mechanism), PDT vs PDD/FGS distinction (5-ALA used in both depending on light wavelength), photosensitizer class taxonomy (1st gen porfimer sodium Photofrin with prolonged 4-6 week skin photosensitivity / 2nd gen ALA-prodrug class with topical Levulan + Ameluz + MAL Metvix and oral Gleolan / 3rd gen verteporfin Visudyne + temoporfin Foscan + padeliporfin Tookad), wavelength engineering principle (red 630 nm deeper / blue 417 nm shallow / NIR 700-800 nm emerging), approved indication landscape (oncology Photofrin esophageal/NSCLC/Barrett's/ampullary + Foscan H&N + Tookad EU prostate + Gleolan FGS glioma; dermatology Levulan AK + Ameluz AK/BCC/field + Metvix; ophthalmology Visudyne wet AMD largely displaced by anti-VEGF), procedural disciplines (drug-light interval per PS varying 5 minutes Visudyne to 40-50 hours Photofrin + light delivery via diode laser/LED arrays/optical fiber/endoscopic balloon diffuser + skin photosensitivity precautions especially Photofrin systemic + adverse event profile), regulatory pathway (FDA combination drug-device CDER+CDRH coordination + per-indication NDA approvals + EMA centralized + PMDA Laserphyrin Asian-spesifik), commercial trajectory (~$2-3B niche market with dermatology fastest growing + indication-spesifik market sizes + pricing benchmarks $5-10K Photofrin + $300-400 Levulan + $500-700 Ameluz + $5-10K Gleolan), pipeline (antibody-photosensitizer conjugates with Akalux cetuximab saratolocan PMDA Japan 2020 H&N approval but US development discontinued 2024 Phase 3 LUZERA-301 + nanoparticle encapsulated + conditional activatable PSs + PDT + IO combinations + antimicrobial aPDT), stakeholder framework (6 abstract categories with procedural specialist subdivision dermatology/pulmonology/gastroenterology/neurosurgery/urology/ophthalmology), confidence stamping. Compatible with all sub-protocols. New manifest gate G33.
