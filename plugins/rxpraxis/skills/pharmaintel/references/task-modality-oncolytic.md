# task-modality-oncolytic.md

**T3 Modality Template — Oncolytic Viruses (v2.6.0)**

> **Architectural context:** Niche modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when oncolytic virus modality is in scope.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "oncolytic virus", "oncolytic viral therapy", "oncolytic viroterapy", "OV", "viral immunotherapy", "onkolitik virüs", "onkolitik viroterapi"
- Vector class terms: "HSV-1 oncolytic", "adenoviral oncolytic", "vaccinia oncolytic", "reovirus oncolytic", "Newcastle disease virus", "NDV", "vesicular stomatitis virus", "VSV", "measles virus oncolytic", "coxsackievirus oncolytic"
- Asset names: "T-VEC", "talimogene laherparepvec", "Imlygic", "nadofaragene firadenovec", "Adstiladrin", "teserpaturev", "Delytact", "G47Δ", "RP-1", "vusolimogene oderparepvec", "Oncorine", "H101", "Pexa-Vec", "JX-594", "Reolysin", "pelareorep", "CG0070", "cretostimogene grenadenorepvec"

### 1.2 Implicit semantic triggers
- Melanoma intralesional therapy
- Non-muscle invasive bladder cancer (NMIBC) BCG-unresponsive
- Glioblastoma combination immunotherapy
- Combination therapy with immune checkpoint inhibitors (anti-PD-1)

### 1.3 NOT triggered by
- ❌ User employer being an oncolytic virus developer (Amgen — T-VEC; Ferring — Adstiladrin; Daiichi Sankyo — Delytact in Japan; Replimune — RP-1; Oncolytics Biotech; SillaJen — Pexa-Vec; CG Oncology)
- ❌ User memory-derived oncology / dermatology specialty

---

## §2. Foundational Conceptual Framework

### 2.1 Oncolytic virus dual mechanism

Oncolytic viruses combine **two complementary anticancer mechanisms**:

1. **Direct oncolysis** — preferential viral replication in tumor cells → cell lysis → tumor debulking
2. **Immune activation** — release of tumor-associated antigens + danger signals (DAMPs/PAMPs) + viral antigens → "cold" tumor → "hot" tumor conversion → systemic anti-tumor immune response

This dual mechanism positions oncolytic viruses as a **bridge between targeted therapy + immunotherapy**.

### 2.2 Tumor selectivity strategies

Engineered oncolytic viruses achieve tumor selectivity through:

| Strategy | Mechanism | Example |
|---|---|---|
| **Natural tumor tropism** | Wild-type virus exploits cancer cell defects (e.g. defective IFN response) | Reovirus (Reolysin), VSV |
| **Genetic deletion of virulence factors** | Removing virulence genes → replication only in cells lacking equivalent host pathway | T-VEC (deleted ICP34.5 + ICP47 from HSV-1) |
| **Tissue-specific promoter** | Viral replication driven by tumor-active promoter | CG0070 (E2F-1 promoter for retinoblastoma-defective tumors) |
| **Receptor retargeting** | Modified viral envelope binds tumor-spesifik receptor | Investigational |
| **Suicide gene insertion** | Conditional cell death gene activated in tumor | Various preclinical |

### 2.3 Immune-stimulating gene insertion ("armed" oncolytic viruses)

Modern oncolytic viruses are commonly **engineered with immune-stimulating transgenes**:

| Transgene | Function | Example |
|---|---|---|
| **GM-CSF** | Recruits + activates dendritic cells, monocytes | T-VEC, RP-1, Pexa-Vec |
| **IL-12** | Promotes Th1 / NK / cytotoxic T cell response | Multiple investigational |
| **anti-CTLA-4** | Local checkpoint inhibition | RP-2 (Replimune; melanoma) |
| **Multiple cytokines** | Combinatorial immune activation | RP-1 (GM-CSF + anti-CTLA-4 ICOS-L) |

---

## §3. Approved Oncolytic Virus Landscape

### 3.1 FDA-approved oncolytic viruses

| Asset | INN | Vector | Sponsor | Indication | Approval |
|---|---|---|---|---|---|
| **Imlygic** | Talimogene laherparepvec (T-VEC) | HSV-1 (deleted ICP34.5 + ICP47, GM-CSF inserted) | Amgen | Unresectable melanoma (intralesional) | FDA 2015-10-27; EMA 2015-12 |
| **Adstiladrin** | Nadofaragene firadenovec-vncg | Non-replicating recombinant adenovirus serotype 5 (interferon alfa-2b transgene) | Ferring | BCG-unresponsive high-risk NMIBC with carcinoma in situ ± Ta/T1 papillary tumors | FDA 2022-12-16 |

### 3.2 Other regional approvals

| Asset | INN | Vector | Sponsor | Region | Indication | Approval |
|---|---|---|---|---|---|---|
| **Oncorine** | H101 (recombinant adenovirus type 5, E1B-55kD-deleted) | Adenovirus | Shanghai Sunway Biotech | China only | Head and neck cancer (combination with chemotherapy) | NMPA 2005 (first oncolytic virus globally approved) |
| **Delytact** | Teserpaturev (G47Δ) | HSV-1 (triple-mutant, deleted γ34.5 + ICP47 + ICP6) | Daiichi Sankyo | Japan only | Malignant glioma | PMDA 2021 (conditional approval, Sakigake-designated) |
| **Rigvir** | ECHO-7 (non-genetically modified) | Echovirus | Riga Cytogenetic Lab (former) | Latvia (withdrawn 2019) | Melanoma | National authority Latvia 2004 (controversial; lacks Western pivotal trial evidence) |

### 3.3 Pivotal trial data — T-VEC (OPTiM)

**OPTiM trial (Andtbacka RH et al. J Clin Oncol 2015;33:2780-8):**
- Phase 3 randomized open-label
- T-VEC vs subcutaneous GM-CSF in unresectable Stage IIIB-IV melanoma
- N=436
- **Primary endpoint:** durable response rate (DRR) — partial or complete response lasting ≥6 months
- T-VEC DRR: 16.3% vs GM-CSF DRR: 2.1% (p<0.001)
- ORR: 26.4% vs 5.7%
- Trend toward OS benefit (HR 0.79, not statistically significant primary OS comparison)
- Approval based on durable response benefit despite OS finding

### 3.4 Adstiladrin pivotal — KEYNOTE-2032 / Phase 3

Single-arm Phase 3 study in BCG-unresponsive NMIBC with CIS:
- N=157
- **Primary endpoint:** complete response (CR) at 3 months
- CR: 51% with median duration 9.7 months
- 24% durable CR ≥12 months
- Q3-monthly intravesical instillation (4 doses, then maintenance)

---

## §4. Combination Therapy Paradigm

### 4.1 Oncolytic virus + immune checkpoint inhibitor combinations

Strong scientific rationale: oncolytic virus → "hot" tumor → enhanced ICI response.

**Notable T-VEC + ICI combinations:**
- T-VEC + pembrolizumab in melanoma (KEYNOTE-034 → MASTERKEY-265 Phase 3 final analysis: did NOT meet PFS or OS primary endpoints — combination did not improve outcomes vs pembrolizumab alone in advanced melanoma)
- Negative MASTERKEY-265 outcome dampened enthusiasm but did not eliminate combination interest

**Replimune RP-1 + nivolumab:**
- IGNYTE-3 Phase 3 ongoing in advanced melanoma
- Earlier Phase 2 data positive (60%+ ORR in checkpoint-naive cohort)

### 4.2 Oncolytic virus + chemotherapy

Pexa-Vec (JX-594) + sorafenib in HCC (PHOCUS Phase 3) — failed primary endpoint, program discontinued 2019.

H101 + chemotherapy is China standard combination per Oncorine label.

---

## §5. Manufacturing — Specialized Viral Vector Production

### 5.1 Viral vector manufacturing complexity

Oncolytic virus manufacturing shares features with AAV gene therapy + vaccine viral vector production:
- **Producer cell line** (typically Vero, HeLa, HEK293, BHK depending on virus)
- **Bioreactor cultivation** — adherent or suspension
- **Viral propagation + harvest** — cell lysis or budding
- **Purification** — TFF, chromatography, ultrafiltration
- **Formulation + cryopreservation** — most products require frozen storage

### 5.2 Major oncolytic virus manufacturing footprint

| Sponsor | Manufacturing |
|---|---|
| Amgen (T-VEC) | Internal facilities |
| Ferring (Adstiladrin) | Multiple facilities including Parsippany NJ |
| Replimune (RP-1, RP-2) | Framingham MA |
| Daiichi Sankyo (Delytact) | Japan facilities |

### 5.3 Cold chain logistics

T-VEC and most oncolytic viruses require **frozen shipment** (-90°C to -70°C typical) + thawing protocol at point of administration. Cold chain logistics + administration center training requirements limit accessibility.

---

## §6. Regulatory Pathway

### 6.1 FDA framework — CBER OTP review

Oncolytic viruses regulated by FDA **CBER Office of Therapeutic Products** (formerly Office of Tissues and Advanced Therapies). BLA pathway under PHSA §351(a). Commonly receive:
- **Breakthrough Therapy** designation
- **Regenerative Medicine Advanced Therapy (RMAT)** designation
- **Priority Review**
- **Orphan Drug** designation

### 6.2 EMA framework — ATMP

Oncolytic viruses qualify as **Advanced Therapy Medicinal Products (ATMPs)** under EU Regulation (EC) No 1394/2007 — specifically as **gene therapy medicinal products (GTMPs)**:
- Committee for Advanced Therapies (CAT) scientific opinion
- CHMP marketing authorization recommendation
- Cross-reference with `task-modality-cellgene.md` for ATMP framework

### 6.3 PMDA + Sakigake — Japan early approval pathway

Delytact (teserpaturev) received **conditional and time-limited approval** under Japan's **Sakigake (先駆け)** designation pathway in 2021 — innovative therapy expedited review. Requires post-approval clinical evidence generation.

### 6.4 Biosafety considerations

Oncolytic viruses raise unique regulatory considerations beyond standard biologics:
- **Shedding** — viral release from treated patients (urine, saliva, lesion exudate)
- **Healthcare worker safety** — administration personnel exposure
- **Household contact safety** — immunocompromised contact precautions
- **Environmental release** — biosafety classification (typically BSL-2)

Patient + HCP education protocols mandatory.

### 6.5 NMPA + Türkiye

NMPA: Oncorine (H101) approved 2005 — first oncolytic virus approved globally; multiple Chinese-developed oncolytic viruses in Phase 1/2/3 development. TİTCK: T-VEC (Imlygic) erişimi sınırlı kompasyonlu kullanım üzerinden; Adstiladrin yaklaşımı henüz değerlendirme aşamasında.

---

## §7. Commercial Trajectory + Market Reality

### 7.1 Commercial reality vs scientific potential

Oncolytic virus modality has **persistently underperformed initial commercial expectations**:
- **Imlygic (T-VEC)** — 2024 sales modest (~$60-80M); never achieved blockbuster status despite first-in-class melanoma approval
- **Adstiladrin** — early launch trajectory (2023-2024); access expansion + adoption uneven

**Reasons for commercial underperformance:**
- Procedural complexity (intralesional T-VEC for melanoma; Q3-monthly intravesical Adstiladrin for NMIBC)
- Limited indication scope (most approvals indication-specific)
- Combination therapy expectations not fully realized (MASTERKEY-265 negative)
- Infrastructure requirements (cold chain + administration training)
- Competing modalities (anti-PD-1 for melanoma; pembrolizumab/nadofaragene comparison NMIBC)

### 7.2 Current pricing benchmarks

- **Imlygic:** ~$16,000-50,000 per treatment course (volume-dependent for intralesional dosing)
- **Adstiladrin:** ~$60,000 per dose; ~$240,000 per induction + maintenance year

### 7.3 RP-1 commercial expectations

Replimune RP-1 (vusolimogene oderparepvec) — pending Phase 3 IGNYTE-3 outcomes for melanoma; potential differentiated commercial trajectory if successful as cold tumor → hot tumor conversion strategy in checkpoint-experienced patients.

---

## §8. Pipeline Dynamics

### 8.1 HSV-1 platform (Replimune dominant)

| Asset | Sponsor | Modifications | Indication | Phase |
|---|---|---|---|---|
| **RP-1 (vusolimogene oderparepvec)** | Replimune | HSV-1 + GM-CSF + GALV-GP R(-) fusogenic protein | Melanoma + multiple solid tumors | Phase 3 IGNYTE-3 (melanoma); registration enabling skin SCC ARTACUS |
| **RP-2** | Replimune | HSV-1 + GM-CSF + anti-CTLA-4 antibody | Multiple solid tumors | Phase 1/2 |
| **RP-3** | Replimune | HSV-1 + GM-CSF + anti-CTLA-4 + ICOS-L | Multiple solid tumors | Phase 1 |

### 8.2 Adenovirus platform

| Asset | Sponsor | Indication | Phase |
|---|---|---|---|
| **CG0070 / cretostimogene grenadenorepvec** | CG Oncology | NMIBC BCG-unresponsive | Phase 3 BOND-003 + CORE-008 |
| **Enadenotucirev / NG-350A** | Akamis Bio (formerly PsiOxus) | Multiple solid tumors | Phase 1/2 |
| **Pexa-Vec (JX-594)** | SillaJen / Transgene | Multiple solid tumors | Various; PHOCUS HCC failed; ongoing |

### 8.3 Other vector platforms

- **Vaccinia oncolytic** (Pexa-Vec, JX-594; Voyager VV1)
- **Reovirus** (pelareorep — Reolysin, Oncolytics Biotech; Phase 2/3 multiple)
- **Newcastle disease virus** (oncolytic NDV — multiple investigational)
- **Vesicular stomatitis virus** (VSV-IFNβ-NIS; Voyager Therapeutics, Vyriad)
- **Coxsackievirus A21** (Cavatak / V937 — Merck via Viralytics acquisition; melanoma + bladder)
- **Maraba virus** (Turnstone Biologics)
- **Measles virus** (oncolytic MV; multiple academic + biotech)

---

## §9. Stakeholder-Spesifik Analytical Framework

### 9.1 Established oncolytic virus sponsors
- Indication expansion strategy
- Combination + sequencing positioning vs ICI standard of care
- Manufacturing scale + administration network expansion
- Patient/HCP education investment

### 9.2 Next-generation oncolytic virus sponsors (Replimune, CG Oncology)
- Differentiation positioning (multi-armed transgene cassettes, tumor selectivity, vector platform)
- Phase 3 trial design optimization
- Cold tumor → hot tumor positioning vs ICI alone

### 9.3 China-developed oncolytic virus sponsors
- Domestic market validation
- Combination with chemotherapy
- Out-licensing for ex-Asia development

### 9.4 Klinisyen paydaşları
- Procedural training for intralesional / intravesical / intratumoral administration
- Imaging-guided injection for non-cutaneous tumors
- Adverse event management (cytokine release, viral symptoms)

### 9.5 Payer paydaşları
- Cost-effectiveness vs comparator therapy
- Bundled payment for combination regimens
- Coverage policy for combination IO + oncolytic

### 9.6 Hasta paydaşları
- Administration logistics (clinic visits, schedule)
- Household contact precautions for shedding period
- Post-injection adverse events (fever, flu-like symptoms)

---

## §10. Confidence Stamping for Oncolytic Virus Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA / PMDA / NMPA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (OPTiM, KEYNOTE-2032, etc.) | **High** (peer-reviewed) |
| Vector engineering details (publicly disclosed) | **High** (label + publication) |
| Combination with ICI Phase 3 outcomes | **High** when published (MASTERKEY-265 negative noted) |
| Manufacturing capacity | **Medium** (sponsor IR varies) |
| Real-world adoption + sales | **Medium** (sponsor IR varies) |
| Forward-looking pipeline timing | **Medium** (sponsor guidance subject to slip) |
| Confidential vector engineering IP | Should not be claimed |
| Shedding / biosafety incident data | **Low-Medium** (rarely publicly summarized) |

---

## §11. Forbidden Patterns

- ❌ Treating oncolytic virus as equivalent to gene therapy (different mechanism — replicating vs non-replicating, oncolytic intent vs gene replacement)
- ❌ Generalizing T-VEC + pembrolizumab MASTERKEY-265 negative outcome to ALL oncolytic + ICI combinations
- ❌ Strategic action recommendations for specific oncolytic sponsors without T6-Defense activation
- ❌ Speculation about confidential combination trial outcomes pre-readout
- ❌ Treating Rigvir Latvia approval as Western-equivalent regulatory validation (limited trial evidence)
- ❌ Recommending oncolytic virus use outside approved label (most uses indication-spesifik per intratumoral or intravesical route)

---

## §12. Versioning & Changelog

- **v2.6.0 (2026-04-15):** Initial release. Niche modality T3 sub-template covering: dual mechanism (direct oncolysis + immune activation cold→hot tumor conversion), tumor selectivity strategies (natural tropism reovirus + genetic deletion T-VEC ICP34.5/ICP47 + tissue-specific promoter CG0070 E2F-1 + receptor retargeting + suicide gene), immune-stimulating transgene "armed" oncolytic viruses (GM-CSF in T-VEC/RP-1/Pexa-Vec; IL-12; anti-CTLA-4 in RP-2; multi-cytokine RP-3), FDA-approved landscape (Imlygic talimogene laherparepvec T-VEC HSV-1+GM-CSF Amgen FDA 2015-10-27 + EMA 2015-12 unresectable melanoma intralesional via OPTiM trial Andtbacka et al. JCO 2015;33:2780-8 DRR 16.3% vs 2.1%; Adstiladrin nadofaragene firadenovec non-replicating adenovirus 5 + IFN alfa-2b Ferring FDA 2022-12-16 BCG-unresponsive NMIBC CIS via Phase 3 N=157 CR 51%), regional approvals (Oncorine H101 NMPA 2005 first globally + Delytact teserpaturev G47Δ HSV-1 Daiichi Sankyo PMDA Japan 2021 conditional Sakigake malignant glioma + Rigvir ECHO-7 Latvia 2004 withdrawn 2019 controversial), combination paradigm (T-VEC + pembrolizumab MASTERKEY-265 Phase 3 NEGATIVE for PFS/OS dampening enthusiasm; RP-1 + nivolumab IGNYTE-3 ongoing; Pexa-Vec + sorafenib PHOCUS HCC failed 2019), manufacturing (specialized viral vector production with producer cell lines + bioreactor + purification + cryopreservation cold chain -90 to -70°C), regulatory pathway (FDA CBER OTP + Breakthrough/RMAT/Priority Review/Orphan; EMA ATMP via Regulation 1394/2007 GTMP classification; PMDA Sakigake; biosafety considerations including shedding + HCP safety + household contacts + BSL-2; NMPA + Türkiye limited compassionate use), commercial trajectory (Imlygic ~$60-80M underperforming initial blockbuster expectations + Adstiladrin early uneven launch + procedural complexity + competing ICI modalities + MASTERKEY-265 dampener), pipeline dynamics (HSV-1 platform Replimune RP-1/RP-2/RP-3; adenovirus CG Oncology cretostimogene Phase 3 BOND-003 + CORE-008 + Akamis Bio + SillaJen Pexa-Vec; vaccinia + reovirus pelareorep + NDV + VSV + coxsackievirus Cavatak Merck + maraba Turnstone + measles vector platforms), stakeholder framework (6 abstract categories), confidence stamping. Compatible with all sub-protocols + cross-reference task-modality-cellgene.md for ATMP framework. New manifest gate G34.
