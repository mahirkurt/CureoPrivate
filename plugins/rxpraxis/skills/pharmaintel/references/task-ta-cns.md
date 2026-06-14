# task-ta-cns.md

**T3 Therapeutic Area Template — Central Nervous System (CNS) / Neurology / Neuropsychiatry (v3.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Lecanemab (anti-Aβ mAb) in Alzheimer's disease" invokes Layer 0 generic + Layer 1 generic task-modality.md + Layer 2 CNS. "Nusinersen (intrathecal ASO) in SMA" invokes Layer 0 + Layer 1 task-modality-rna.md + Layer 2 CNS + Layer 2 task-ta-rare-disease.md (multi-TA cross-reference).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "CNS", "central nervous system", "neurology", "nöroloji", "neuropsychiatry", "nöropsikiyatri", "psychiatry", "psikiyatri", "neurodegeneration", "nörodejenerasyon"
- Disease terms — neurodegenerative: "Alzheimer", "Alzheimer's disease", "AD", "Parkinson", "Parkinson's disease", "PD", "Huntington", "Huntington's disease", "HD", "ALS", "amyotrophic lateral sclerosis", "motor neuron disease", "MND", "frontotemporal dementia", "FTD", "Lewy body dementia", "DLB", "multiple system atrophy", "MSA", "progressive supranuclear palsy", "PSP"
- Disease terms — MS + demyelinating: "multiple sclerosis", "MS", "multipl skleroz", "neuromyelitis optica", "NMO", "NMOSD", "MOGAD", "transverse myelitis"
- Disease terms — epilepsy: "epilepsy", "epilepsi", "seizure", "nöbet", "focal seizure", "generalized seizure", "refractory epilepsy", "Dravet", "Lennox-Gastaut", "tuberous sclerosis complex", "TSC"
- Disease terms — stroke: "stroke", "inme", "ischemic stroke", "thrombolysis", "thrombectomy"
- Disease terms — pain + migraine: "migraine", "migren", "CGRP", "chronic migraine", "cluster headache", "neuropathic pain", "nöropatik ağrı"
- Disease terms — psychiatry: "depression", "MDD", "major depressive disorder", "depresyon", "TRD", "treatment-resistant depression", "schizophrenia", "şizofreni", "bipolar", "anxiety", "PTSD", "OCD", "ADHD", "DEHB", "autism", "otizm", "ASD"
- Disease terms — neuromuscular: "SMA", "spinal muscular atrophy", "DMD", "Duchenne", "myasthenia gravis", "MG", "CIDP", "Pompe disease", "ALS"
- Mechanism + asset terms: "anti-Aβ", "lecanemab", "Leqembi", "aducanumab", "Aduhelm", "donanemab", "Kisunla", "GLP-1 Alzheimer", "CGRP inhibitor", "Aimovig", "Ajovy", "Emgality", "Nurtec", "Ubrelvy", "S1P modulator MS", "Gilenya", "Mavenclad", "cladribine", "Ocrevus", "ocrelizumab", "Kesimpta", "Vumerity", "Rebif", "Aubagio", "Copaxone", "tofersen", "Qalsody", "Spinraza", "nusinersen", "Zolgensma", "Evrysdi", "risdiplam", "Radicava", "edaravone", "Rilutek", "riluzole", "Relyvrio", "Amylyx", "Austedo", "Ingrezza", "valbenazine", "Rexulti", "brexpiprazole", "Vraylar", "Caplyta", "ketamine", "esketamine", "Spravato", "psilocybin"

### 1.2 Implicit semantic triggers
- Neurodegenerative biomarker discussions (Aβ, tau, α-synuclein, neurofilament light, DAT-SPECT)
- MS disease-modifying therapy (DMT) platform-vs-high-efficacy strategy
- Alzheimer anti-amyloid class commercial trajectory
- Psychiatric pharmacotherapy paradigm shifts (ketamine, psilocybin, anti-TRD)
- Stroke acute intervention timing windows (alteplase, tenecteplase, thrombectomy)

### 1.3 NOT triggered by
- ❌ User employer with CNS portfolio (Biogen, Roche, Eli Lilly, Eisai, Sage Therapeutics, Axsome, Neurocrine, Acadia, Takeda, Novartis, Merck, Janssen)
- ❌ User memory-derived neurology/psychiatry specialty
- ❌ User geography being a CNS clinical trial site

---

## §2. Foundational CNS Framework

### 2.1 CNS as a TA — distinguishing features

CNS presents unique characteristics that differentiate it from oncology, autoimmune, and metabolic:

| Dimension | CNS-spesifik discipline |
|---|---|
| **Blood-brain barrier (BBB)** | CNS drug delivery constrained — most biologics require intrathecal, intracerebroventricular, or novel CNS delivery systems |
| **Endpoint subjectivity** | Clinical scales (ALSFRS-R, EDSS, ADAS-Cog, MDS-UPDRS, PANSS) more subjective than oncology RECIST — rater training + blinding critical |
| **Placebo response** | CNS indications historically show high placebo response rates (MDD 30-40%, chronic pain 30%+) — trial failure risk elevated |
| **Disease progression variability** | Natural history heterogeneous — SMA vs ALS vs HD progression rates differ dramatically |
| **Regulatory discipline** | FDA Division of Neurology accepts progression-slowing surrogate endpoints (lecanemab CDR-SB vs cognitive decline) |
| **HTA scrutiny** | Expensive CNS therapies (aducanumab $28K/yr initial → $14K/yr; nusinersen $750K load + $375K/yr maintenance) face aggressive HTA assessment |
| **Health economics** | CNS disability burden drives economic modeling via disability-adjusted life years + caregiver burden integration |

### 2.2 Blood-brain barrier (BBB) considerations

BBB-related modality constraints:

| Modality | CNS penetration strategy |
|---|---|
| **Small molecule targeted** | Lipophilic design enables passive BBB diffusion; medicinal chemistry optimization |
| **mAb** | Poor BBB penetration (~0.1-0.3% of plasma) — requires high systemic dose OR intrathecal delivery OR BBB transcytosis engineering (Roche Brainshuttle, Denali TV platform) |
| **ASO** | Intrathecal lumbar puncture dominant (Spinraza, Tofersen); systemic ASO does not cross BBB |
| **Gene therapy AAV** | AAV9 crosses BBB in neonates (Zolgensma); intrathecal for adult delivery (preclinical); intracerebroventricular (ICV) for some indications |
| **Cell therapy** | Intraparenchymal or intrathecal; very limited to investigational |
| **siRNA** | GalNAc does NOT target CNS; brain-targeted conjugates investigational (Alnylam C16-siRNA) |

### 2.3 Biomarker-driven CNS trial paradigm

Modern CNS trials increasingly biomarker-gated:
- **Alzheimer's:** Aβ PET (florbetapir, florbetaben, flutemetamol) + tau PET + CSF Aβ42/Aβ40 + CSF p-tau + plasma p-tau217/pTau231/GFAP for enrollment + response
- **Parkinson's:** DAT-SPECT (ioflupane DaTscan) + α-synuclein CSF RT-QuIC + skin biopsy α-synuclein
- **MS:** MRI T2 lesion + gadolinium-enhancing lesion + brain atrophy + cerebrospinal fluid oligoclonal bands + serum neurofilament light (sNfL)
- **ALS:** CSF + plasma neurofilament light as prognostic + pharmacodynamic (tofersen approval based on sNfL)
- **SMA:** SMN gene dosage + motor function scales (HFMSE, RULM, CHOP-INTEND)
- **DMD:** dystrophin expression (Western blot, mass spec) for gene therapy surrogate endpoints

---

## §3. Endpoint Frameworks by Disease

### 3.1 Alzheimer's disease (AD) endpoints

| Endpoint | Instrument | Use |
|---|---|---|
| **CDR-SB** | Clinical Dementia Rating-Sum of Boxes | Primary efficacy in lecanemab/donanemab Phase 3; integrated cognitive + functional |
| **ADAS-Cog** | Alzheimer's Disease Assessment Scale-Cognitive | Cognitive subscale, historical gold standard |
| **iADRS** | Integrated Alzheimer's Disease Rating Scale | Alternative integrated measure |
| **MMSE** | Mini-Mental State Examination | Bedside cognitive screening |
| **Aβ PET reduction** | Centiloid scale | Biomarker surrogate (supported lecanemab accelerated approval 2023) |
| **Tau PET + plasma p-tau217** | Emerging biomarker | Subgroup analysis + patient selection |

### 3.2 Multiple sclerosis (MS) endpoints

- **Annualized Relapse Rate (ARR)** — primary efficacy in relapsing MS
- **Disability progression** — EDSS (Expanded Disability Status Scale) confirmed at 12 or 24 weeks
- **No Evidence of Disease Activity (NEDA-3 / NEDA-4)** — composite incorporating clinical + MRI
- **Brain atrophy** — MRI volumetric (PBVC)
- **MRI outcomes** — new/enlarging T2 lesions, Gd+ lesions
- **Serum neurofilament light (sNfL)** — emerging pharmacodynamic biomarker

### 3.3 Parkinson's disease (PD) endpoints

- **MDS-UPDRS** — Movement Disorder Society-Unified Parkinson's Disease Rating Scale (Parts I-IV)
- **Off-time reduction** — motor fluctuation levodopa adjuncts
- **Dyskinesia reduction** — UDysRS
- **Hoehn & Yahr staging** — disease stage
- **NMS scale** — non-motor symptoms

### 3.4 ALS endpoints

- **ALSFRS-R** — ALS Functional Rating Scale Revised (48-point composite); historical primary
- **Survival + tracheostomy/ventilation-free survival**
- **Forced Vital Capacity (FVC)** — respiratory function
- **CAFS** — Combined Assessment of Function and Survival
- **Neurofilament light (NfL)** — supported tofersen approval 2023 (first NfL-based approval)

### 3.5 Psychiatric endpoints

| Disease | Primary instrument |
|---|---|
| **MDD** | HAM-D (Hamilton Depression Rating Scale), MADRS (Montgomery-Åsberg) |
| **Schizophrenia** | PANSS (Positive and Negative Syndrome Scale) |
| **Bipolar depression** | MADRS |
| **PTSD** | CAPS-5 (Clinician-Administered PTSD Scale) |
| **ADHD** | ADHD-RS, CGI-I |

### 3.6 Epilepsy endpoints

- Seizure frequency reduction (% change baseline)
- 50% responder rate
- Seizure freedom
- Time-to-second seizure
- Pediatric-spesifik scales (Dravet, LGS)

---

## §4. FDA + Global Regulatory Disciplines for CNS

### 4.1 FDA Division of Neurology (OND)

- **CDER Office of New Drugs (OND) Division of Neurology 1, 2** — review divisions
- **Neurology-specific guidance documents:**
  - Early Alzheimer's Disease (Draft 2018 → Final 2024): accepts surrogate (Aβ clearance) supporting accelerated approval
  - ALS: progression-slowing primary endpoints acceptable
  - MS: ARR + EDSS disability progression
  - Chronic Pain: adequate + well-controlled trials
  - Antidepressant development: two adequate + well-controlled trials traditionally required

### 4.2 FDA accelerated approval precedents for CNS

Several high-profile accelerated approvals + post-marketing considerations:
- **Aducanumab (Aduhelm)** — Biogen/Eisai accelerated approval 2021-06 controversial ODAC 10-0-1 against + 3 resignations; CMS NCD restricted to trial only; Biogen voluntarily discontinued January 2024
- **Lecanemab (Leqembi)** — Biogen/Eisai accelerated approval 2023-01; traditional approval 2023-07 based on Clarity-AD (N=1795; CDR-SB decline slowed by 27%, NEJM 2023;388:9-21); Medicare coverage with CMS registry requirement
- **Donanemab (Kisunla)** — Eli Lilly FDA approval 2024-07 based on TRAILBLAZER-ALZ2 (N=1736; iADRS decline slowed by 22% low/medium tau subgroup, NEJM 2023;389:1753-1764); limited-duration dosing stopping rule
- **Tofersen (Qalsody)** — Biogen/Ionis SOD1-ALS accelerated approval 2023-04 based on NfL reduction; ODAC 9-0 favorable
- **Exondys 51 / Vyondys 53 / Amondys 45 / Viltepso** — Sarepta DMD exon-skipping ASOs (accelerated approval based on dystrophin protein expression surrogate; cross-reference `task-modality-rna.md`)
- **Relyvrio / AMX0035 (Amylyx)** — ALS FDA approval September 2022; Phase 3 PHOENIX failed primary endpoint → withdrawal April 2024

### 4.3 PCNS + PDUFA considerations

CNS approvals frequently invoke:
- Priority Review (6-month clock)
- Breakthrough Therapy designation (Leqembi, tofersen)
- Orphan Drug designation (rare neurological)
- Accelerated Approval Section 506(c) with confirmatory trial obligation

### 4.4 EMA + other jurisdictions

- **EMA CHMP:** Lecanemab EU approval April 2025 restricted to ApoE4 non-carriers/heterozygotes (excluded homozygotes due to ARIA risk); divergence from FDA label
- **MHRA:** post-Brexit reliance + independent decisions; lecanemab approved 2024 but NICE declined routine NHS funding
- **PMDA:** Leqembi Japan approval September 2023 (world-first traditional approval); active neurodegeneration program
- **NMPA:** expanding CNS approval ecosystem
- **Türkiye TİTCK:** EMA reliance; lecanemab erişimi named patient via Sağlık Bakanlığı

---

## §5. MS Disease-Modifying Therapy (DMT) — Dominant CNS Paradigm

### 5.1 MS DMT class landscape

**Platform therapies (moderate efficacy):**
- Interferon β (Avonex, Rebif, Betaferon, Plegridy)
- Glatiramer acetate (Copaxone — cross-reference `task-modality-peptide.md` generic landmark)
- Teriflunomide (Aubagio)
- Dimethyl fumarate (Tecfidera), Diroximel (Vumerity), Monomethyl (Bafiertam)

**Oral high-efficacy (emerging):**
- S1P modulators: Gilenya (fingolimod) + Mayzent (siponimod) + Zeposia (ozanimod) + Ponvory (ponesimod) — cross-reference `task-ta-autoimmune.md`
- Cladribine (Mavenclad) — lymphocyte depletion
- Ocrelizumab + Ofatumumab + Ublituximab + Rituximab (off-label) — anti-CD20 B-cell depletion (cross-reference `task-ta-autoimmune.md`)

**Emerging:**
- BTK inhibitors (oral) — evobrutinib Phase 3 FAILED; tolebrutinib + remibrutinib + fenebrutinib Phase 3 ongoing

### 5.2 Progressive MS challenge

Progressive MS (primary-progressive PPMS + secondary-progressive SPMS) historically difficult target:
- **Ocrevus (ocrelizumab)** — first PPMS-approved DMT (2017)
- **Mayzent (siponimod)** — SPMS approval
- **Remaining unmet need** significant

### 5.3 MS pricing + access

- DMT pricing $60-80K/year in US WAC
- Generic interferon β + glatiramer acetate erosion significant
- Anti-CD20 rising market share; subcutaneous (Kesimpta, Briumvi Q6M) convenience advantage

---

## §6. Alzheimer's Anti-Amyloid Class — Commercial Paradigm Shift

### 6.1 Anti-Aβ class trajectory

Three FDA approvals sequential:
- **Aduhelm** — 2021-06 accelerated; controversial ODAC; CMS NCD restriction; voluntary discontinuation Jan 2024
- **Leqembi** — 2023-01 accelerated → 2023-07 traditional; CMS coverage with registry; commercial trajectory constrained
- **Kisunla** — 2024-07 traditional; limited-duration dosing stopping rule; TRAILBLAZER-ALZ2

### 6.2 ARIA class effect discipline

**Amyloid-Related Imaging Abnormalities (ARIA):**
- ARIA-E (edema) — more common
- ARIA-H (hemorrhage/microhemorrhage)
- **ApoE4 homozygote risk disproportion** — ~32% lecanemab ARIA rate in ApoE4 homozygotes vs ~9% non-carriers
- **EMA lecanemab label** EXCLUDES ApoE4 homozygotes based on ARIA risk-benefit
- MRI monitoring mandatory per label
- Risk factor for intracranial hemorrhage with anticoagulants — relative contraindication

### 6.3 Subcutaneous + home administration evolution

- **Leqembi IQLIK subcutaneous** — approved 2025 Q1 — weekly SC self-administration
- **Donanemab intravenous** initial, SC development ongoing
- Commercial + access implications significant (infusion center capacity bottleneck)

### 6.4 Access + commercial reality

- Anti-Aβ access challenges: PET/CSF biomarker confirmation + MRI monitoring infrastructure + APOE genotyping + specialty infusion center capacity
- CMS coverage via registry requirement shifted to broader coverage through 2024-2025
- Commercial underperformance vs initial projections for lecanemab + donanemab

---

## §7. Emerging CNS Frontiers

### 7.1 GLP-1 in Alzheimer's

- **Semaglutide (Ozempic/Rybelsus)** — EVOKE + EVOKE+ Phase 3 Alzheimer's readouts pending 2026
- Rationale: metabolic-inflammation hypothesis + epidemiologic observation of reduced dementia risk in GLP-1 users

### 7.2 α-synuclein targeting (Parkinson's)

- **Prasinezumab** (Roche) — Phase 3 PADOVA ongoing
- **Cinpanemab** (Biogen) — failed
- **UCB0599 / minzasolmin** — Phase 2 ONGOING
- Small molecule α-synuclein modulators emerging

### 7.3 Psychedelic + novel psychiatry

- **Esketamine (Spravato)** — Johnson & Johnson TRD approval 2019; intranasal SCR
- **MDMA** — Lykos Therapeutics PTSD FDA rejected August 2024 → CRL requires additional Phase 3
- **Psilocybin** — Compass Pathways COMP360 Phase 3 ongoing; Cybin ongoing
- **Brexanolone + Zuranolone** — Sage/Biogen postpartum depression + MDD
- **KarXT (xanomeline-trospium)** — BMS (Karuna acquisition $14B 2024) — muscarinic agonist schizophrenia FDA approved 2024-09

### 7.4 CGRP migraine class

- **Injectable preventive:** Aimovig (erenumab, Amgen+Novartis), Ajovy (fremanezumab, Teva), Emgality (galcanezumab, Lilly), Vyepti (eptinezumab, Lundbeck)
- **Oral gepants:** Ubrelvy (ubrogepant, AbbVie), Qulipta (atogepant, AbbVie), Nurtec ODT (rimegepant, Pfizer)
- Mature class — pricing pressure + generic emergence near

### 7.5 ALS beyond current SOC

- **Riluzole (Rilutek)** — 1995 approval, mild mortality benefit (~3 mo)
- **Edaravone (Radicava + Radicava ORS)** — 2017 IV + 2022 oral suspension; MCI-186 PMDA Japan 2015
- **Tofersen (Qalsody)** — SOD1-ALS 2023 first NfL-based approval
- **AMX0035 (Relyvrio)** — approved 2022 → WITHDRAWN April 2024 after Phase 3 PHOENIX failure
- **Emerging:** Biogen BIIB078 (C9ORF72), QurAlis QRL-201 (STMN2), Wave investigational

---

## §8. Türkiye CNS Ekosistemi

### 8.1 TİTCK + SGK SUT CNS disciplines

- **TİTCK onay** — çoğu CNS ilacı EMA reliance pathway
- **SGK SUT geri ödeme** — CNS ilaçları SUT EK-4C (protokollü) veya EK-4F (rapor + uzman hekim) listelerinde
- **MS ilaçları** — multipl skleroz merkezleri (MS Derneği tarafından akredite edilen 40+ tersiyer merkez) reçete otoritesine sahip; B formu raporu gerekli
- **Anti-Aβ lecanemab erişimi** — TİTCK 2025 değerlendirme aşamasında; SGK listesinde yok (2026 cutoff); özel sağlık sigortası + out-of-pocket + named patient çoğu durumda
- **Nusinersen (Spinraza) + onasemnogene abeparvovec (Zolgensma) + risdiplam (Evrysdi)** — SMA tedavisi; SGK geri ödemesinde özel süreç (pediatri + genetik konsey onayı; Zolgensma 2021+ SGK listesinde)
- **Esketamine (Spravato)** — Türkiye onay sonrası sınırlı erişim; özel psikiyatri klinikleri
- **Psikiyatri ilaçları** — çoğu SUT eşdeğer grup kapsamında; yeni nesil antipsikotik (Caplyta, Rexulti, Vraylar) bazıları SUT kapsamında

### 8.2 Türk CNS klinik araştırma ekosistemi

- Multipl skleroz global Phase 3 trial'larında Türkiye önemli katılımcı (MS insidansı Türkiye'de görece yüksek)
- Alzheimer trials Türkiye'de İstanbul, Ankara, İzmir tersiyer nöroloji merkezleri
- Nöromüsküler hastalık (SMA, DMD) pediatri merkezleri Hacettepe, Gazi, İstanbul Üniversitesi

### 8.3 Türk yerli jenerik CNS ekosistemi

- Antidepresanlar (SSRI, SNRI), antipsikotikler (aripiprazole, risperidone), antiepileptikler (levetiracetam, valproate), gabapentin, pregabalin — Türk jenerik üretim yaygın
- Originatör CNS ilaçları (Leqembi, Spravato, Aimovig) ithalat

---

## §9. Stakeholder-Spesifik Analytical Framework

### 9.1 Neurodegeneration-focused sponsors (Biogen, Roche, Eisai, Lilly, Ionis)
- Pipeline replenishment challenge (high attrition in CNS)
- Biomarker strategy alignment with regulatory expectations
- Payer engagement early + HTA preparation

### 9.2 Psychiatry-focused sponsors (Acadia, Axsome, Neurocrine, Sage)
- Platform vs indication-spesifik positioning
- Innovative mechanism differentiation vs legacy antidepressants
- Real-world effectiveness generation

### 9.3 MS-focused sponsors (Biogen, Roche, Novartis, Sanofi, TG Therapeutics)
- DMT class positioning (platform vs high-efficacy)
- Progressive MS unmet need
- Generic + biosimilar erosion management

### 9.4 Epilepsy-focused sponsors (UCB, SK Biopharm, Takeda, Jazz Pharmaceuticals)
- Refractory epilepsy niche
- Orphan pediatric epilepsy (Dravet, LGS, TSC) — cross-reference `task-ta-rare-disease.md`
- Adult vs pediatric label expansion

### 9.5 Payer paydaşları
- Anti-amyloid coverage policy design (CMS registry → routine)
- Specialty pharmacy high-cost specialty CNS management
- Step therapy for DMT + antidepressants

### 9.6 Klinisyen + CNS specialist paydaşları
- Biomarker infrastructure (PET, MRI, CSF, genotyping) access
- Infusion capacity for anti-Aβ + CAR-T neurology
- Trial referral patterns

### 9.7 Hasta + caregiver paydaşları
- Caregiver burden integration in health economic models
- Clinical trial participation barriers
- Out-of-pocket cost + access disparity

---

## §10. Confidence Stamping for CNS Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA / PMDA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (ARR, CDR-SB, ALSFRS-R, MDS-UPDRS, etc.) | **High** (peer-reviewed) |
| Biomarker surrogate validity | **Medium** (indication-spesifik; context-dependent) |
| Real-world anti-Aβ uptake | **Medium** (registry data immature) |
| ARIA incidence in specific subgroups | **High** (ApoE4-stratified data published) |
| HTA body coverage decisions | **High** when published |
| Psychedelic therapy regulatory trajectory | **Low-Medium** (evolving) |
| Confidential sponsor commercial strategy | Should not be claimed |
| Pipeline Phase 3 readout timing | **Medium** (sponsor guidance subject to slip) |

---

## §11. Forbidden Patterns

- ❌ Treating all CNS endpoints as directly comparable (ARR vs EDSS vs CDR-SB vs ALSFRS-R measure fundamentally different constructs)
- ❌ Generalizing anti-Aβ class efficacy (lecanemab ≠ aducanumab trajectory)
- ❌ Ignoring ApoE4 stratification in anti-Aβ analyses
- ❌ Treating psychedelic therapy as conventional CNS drug development (unique FDA + ethics + REMS considerations)
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Oversimplifying MS DMT platform-vs-high-efficacy positioning as linear hierarchy
- ❌ Extrapolating aducanumab failure to broader anti-amyloid class inevitability

---

## §12. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. Layer 2 CNS/Neurology/Neuropsychiatry TA template covering: BBB + CNS drug delivery considerations per modality (small molecule lipophilic + mAb 0.1-0.3% penetration + ASO intrathecal + AAV9 pediatric + GalNAc non-CNS), biomarker-driven CNS trial paradigm (AD: Aβ PET + tau PET + CSF Aβ42/Aβ40 + p-tau + plasma p-tau217; PD: DAT-SPECT + α-synuclein RT-QuIC; MS: MRI T2 + Gd-enh + atrophy + sNfL; ALS: NfL surrogate; SMA/DMD: gene expression surrogates), endpoint frameworks by disease (AD CDR-SB primary / ADAS-Cog / iADRS / MMSE + Aβ PET centiloid; MS ARR + EDSS + NEDA + brain atrophy + sNfL; PD MDS-UPDRS; ALS ALSFRS-R + survival + FVC + CAFS; MDD HAM-D/MADRS; schizophrenia PANSS; epilepsy seizure frequency), FDA Division of Neurology OND (accelerated approval precedents aducanumab 2021 withdrawn 2024 + lecanemab 2023 traditional via Clarity-AD CDR-SB 27% slowing + donanemab 2024 via TRAILBLAZER-ALZ2 iADRS 22% slowing + tofersen 2023 first NfL-based approval + Sarepta DMD ASOs + Relyvrio AMX0035 approved 2022 withdrawn April 2024 after PHOENIX Phase 3 failure), EMA lecanemab ApoE4 homozygote exclusion vs FDA divergence + PMDA world-first traditional Leqembi approval September 2023 + MHRA + NMPA + Türkiye TİTCK named patient, MS DMT dominant CNS paradigm (platform interferon/glatiramer/teriflunomide/DMF/diroximel + oral high-efficacy S1P modulators Gilenya/Mayzent/Zeposia/Ponvory + cladribine Mavenclad + anti-CD20 Ocrevus/Kesimpta/Briumvi + BTK inhibitors emerging evobrutinib Phase 3 failed + tolebrutinib/remibrutinib/fenebrutinib ongoing + progressive MS challenge with Ocrevus first PPMS approved), anti-Aβ class paradigm shift (3 sequential FDA approvals Aduhelm 2021→2024 withdrawal + Leqembi 2023 + Kisunla 2024 + ARIA class effect discipline with ApoE4 homozygote risk + EMA label stratification + subcutaneous IQLIK approval 2025 + access challenges PET/CSF biomarker + MRI monitoring + APOE genotyping + infusion capacity bottleneck), emerging frontiers (GLP-1 in AD EVOKE/EVOKE+ pending 2026 + α-synuclein PD prasinezumab Phase 3 PADOVA + psychedelic MDMA Lykos CRL August 2024 + psilocybin + brexanolone/zuranolone + KarXT xanomeline-trospium BMS Karuna $14B acquisition 2024 muscarinic schizophrenia 2024-09 approval + CGRP migraine mature class + ALS tofersen + AMX0035 withdrawal teaching moment), Türkiye CNS ekosistemi (TİTCK + SGK SUT EK-4C/4F + MS merkezleri 40+ tertiary + SMA protokollü erişim + psikiyatri SUT + Türk yerli jenerik CNS). New manifest gate G44. Cross-references task-modality-rna.md (intrathecal ASO Spinraza/Tofersen + DMD ASOs), task-modality-cellgene.md (Zolgensma AAV9 SMA), task-ta-autoimmune.md (MS DMT S1P + anti-CD20 overlap), task-ta-rare-disease.md (SMA + DMD + ALS + Dravet + LGS overlap), analytics-framework.md (anti-Aβ commercial NPV + sensitivity), api-integrations.md (FDA AD-ADUFA + ClinicalTrials.gov CNS readouts).
