# task-ta-metabolic.md

**T3 Therapeutic Area Template — Metabolic / Cardiovascular / Renal (Cardiometabolic) (v3.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Semaglutide in T2D + obesity + CV outcomes + CKD" invokes Layer 0 generic + Layer 1 task-modality-peptide.md + Layer 2 task-ta-metabolic.md. "Inclisiran in ASCVD" invokes Layer 0 + Layer 1 task-modality-rna.md + Layer 2 task-ta-metabolic.md.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "metabolic", "metabolik", "cardiometabolic", "kardiyometabolik", "endocrinology", "endokrinoloji", "diabetology", "cardiology", "kardiyoloji", "nephrology", "nefroloji", "hepatology", "hepatoloji", "obesity medicine", "obezite"
- Disease terms — diabetes + obesity: "type 2 diabetes", "T2D", "diyabet", "tip 2 diyabet", "type 1 diabetes", "T1D", "obesity", "obezite", "overweight", "prediabetes", "gestational diabetes", "MODY"
- Disease terms — cardiovascular: "atherosclerosis", "ateroskleroz", "ASCVD", "coronary artery disease", "CAD", "koroner arter hastalığı", "heart failure", "kalp yetmezliği", "HFrEF", "HFpEF", "HFmEF", "hypertension", "hipertansiyon", "HTN", "hyperlipidemia", "hiperlipidemi", "dyslipidemia", "familial hypercholesterolemia", "FH", "HoFH", "HeFH", "Lp(a)", "lipoprotein(a)", "atrial fibrillation", "AFib", "atriyal fibrilasyon"
- Disease terms — renal: "chronic kidney disease", "CKD", "kronik böbrek hastalığı", "diabetic kidney disease", "DKD", "IgA nephropathy", "FSGS", "hyperkalemia", "hiperkalemi"
- Disease terms — liver: "MASH", "NASH", "nonalcoholic steatohepatitis", "MAFLD", "NAFLD", "cirrhosis", "siroz", "hepatitis B", "hepatitis C", "HBV", "HCV"
- Disease terms — other: "gout", "gut", "hyperuricemia", "osteoporosis", "osteoporoz", "acromegaly", "Cushing", "thyroid", "hypothyroidism", "hyperthyroidism"
- Class terms: "GLP-1 RA", "GLP-1/GIP", "SGLT2 inhibitor", "DPP-4 inhibitor", "statin", "PCSK9 inhibitor", "ezetimibe", "bempedoic acid", "ARB", "ACE inhibitor", "ARNI", "SGLT2i", "MRA", "mineralocorticoid receptor antagonist", "finerenone", "non-steroidal MRA", "insulin analog", "insulin glargine", "insulin degludec", "anti-Lp(a)"
- Asset names: "Ozempic", "Wegovy", "Rybelsus", "semaglutide", "Mounjaro", "Zepbound", "tirzepatide", "Trulicity", "dulaglutide", "Jardiance", "empagliflozin", "Invokana", "canagliflozin", "Farxiga", "dapagliflozin", "Steglatro", "ertugliflozin", "Januvia", "sitagliptin", "Tradjenta", "Linagliptin", "Onglyza", "Repatha", "evolocumab", "Praluent", "alirocumab", "Leqvio", "inclisiran", "Lipitor", "atorvastatin", "Crestor", "rosuvastatin", "Entresto", "sacubitril/valsartan", "Kerendia", "finerenone", "Rezdiffra", "resmetirom", "Wainua", "eplontersen", "Amvuttra", "vutrisiran", "Tzield", "teplizumab"

### 1.2 Implicit semantic triggers
- CV outcome trial (CVOT) design discussions
- FDA 2008 T2D CV safety guidance + 2018 relaxation history
- Incretin class commercial dominance + pipeline
- SGLT2 class cardiorenal indication expansion
- Post-statin LDL-C lowering landscape (PCSK9 + bempedoic acid + inclisiran)
- MASH NIT/biomarker-based trial design paradigm

### 1.3 NOT triggered by
- ❌ User employer with metabolic portfolio (Novo Nordisk, Eli Lilly, Boehringer Ingelheim, AstraZeneca, Merck, Sanofi, Amgen, Regeneron, Madrigal)
- ❌ User memory-derived endocrinology/cardiology/nephrology specialty
- ❌ User geography being a diabetes trial hub

---

## §2. Foundational Cardiometabolic Framework

### 2.1 Cardiometabolic as an integrated TA

Modern cardiometabolic medicine recognizes profound interconnection:
- **T2D ↔ ASCVD** — T2D ~2× CV risk; CV death is leading T2D mortality cause
- **T2D ↔ CKD** — diabetic kidney disease is leading CKD cause globally
- **T2D ↔ HF** — T2D 2-5× HF risk; HF worsens glycemic control
- **Obesity ↔ all of above** — visceral adiposity drives shared pathophysiology
- **MASH/NAFLD** — hepatic manifestation of cardiometabolic disease

This integration is reshaping:
- Indication expansion trajectories (single molecule crossing T2D → obesity → HF → CKD → MASH → dementia)
- Trial design (cardiorenal composite endpoints)
- Commercial strategy (lifecycle across therapeutic areas)
- Regulatory expectations (beyond single-disease primary endpoint)

### 2.2 Cardiovascular outcome trial (CVOT) history

**FDA 2008 T2D CV safety guidance** (post-rosiglitazone Avandia controversy):
- Required CVOT for all new T2D drugs demonstrating no CV harm
- Hazard ratio upper 95% CI <1.3 (non-inferiority against placebo + background therapy)
- Resulted in decade of large CVOT trials (EMPA-REG, LEADER, SUSTAIN-6, DECLARE-TIMI 58, REWIND, CANVAS)

**FDA 2018 guidance revision + 2020 final guidance:**
- Removed mandatory CVOT for all T2D drugs
- Replaced with case-by-case CV safety assessment
- Opened door to regulatory approval without dedicated CVOT (pipeline reshape)

**Unintended consequence:** CVOTs became commercial asset beyond regulatory floor — positive CVOT results drive label expansion + guidelines + payer coverage

### 2.3 Guideline ecosystem

**Diabetes:**
- **ADA (American Diabetes Association) Standards of Care** — annual update, US-dominant
- **EASD (European Association for the Study of Diabetes)** — joint ADA-EASD consensus reports
- **AACE / ACE (American Association of Clinical Endocrinology)** — alternative US framework
- **IDF (International Diabetes Federation)** — global

**Cardiovascular:**
- **ACC/AHA (American College of Cardiology / American Heart Association)** — US joint guidelines
- **ESC (European Society of Cardiology)** — European
- **HFSA (Heart Failure Society of America)** — HF-spesifik

**Lipids:**
- **AHA/ACC Cholesterol Management Guideline**
- **ESC/EAS (European Atherosclerosis Society)** — LDL-C targets typically more aggressive
- **NLA (National Lipid Association)** — US

**Renal:**
- **KDIGO (Kidney Disease Improving Global Outcomes)** — international
- **NKF (National Kidney Foundation)** — US

**MASH:**
- **AASLD (American Association for the Study of Liver Diseases)** — US
- **EASL (European Association for the Study of the Liver)** — European
- **APASL** — Asia-Pacific

### 2.4 Endpoint frameworks

| Endpoint class | Indication | Examples |
|---|---|---|
| **Glycemic** | T2D | HbA1c reduction (%), time-in-range (TIR), fasting glucose |
| **Weight** | Obesity | % body weight loss, BMI reduction, waist circumference |
| **Lipid** | ASCVD prevention | LDL-C %, ApoB, non-HDL-C, Lp(a) |
| **Cardiovascular** | ASCVD/HF | MACE (3-point: CV death + nonfatal MI + nonfatal stroke; 4-point: +hospitalization for HF), all-cause mortality |
| **Renal** | CKD | eGFR slope, UACR reduction, ESRD, kidney failure composite |
| **Liver** | MASH | NASH resolution + no worsening fibrosis; fibrosis improvement ≥1 stage no NASH worsening (histologic) → accelerated approval surrogate; liver enzymes + MRI-PDFF + NITs non-invasive |
| **Composite** | Cardiorenal | Cardiovascular + renal + all-cause death composite (e.g. FIDELIO-DKD primary) |

---

## §3. GLP-1 / Incretin Class — Dominant Metabolic Paradigm

Cross-reference `task-modality-peptide.md` for peptide-spesifik GLP-1 disciplines. This TA template covers cardiometabolic disease context.

### 3.1 GLP-1 CV outcome trial landmark results

| Trial | Asset | Population | Result |
|---|---|---|---|
| **LEADER (2016)** | Liraglutide | T2D CV-risk | MACE HR 0.87 p=0.01 (superiority) |
| **SUSTAIN-6 (2016)** | Semaglutide SC | T2D CV-risk | MACE HR 0.74 p<0.001 (superiority) |
| **EXSCEL (2017)** | Exenatide ER | T2D CV-risk | MACE HR 0.91 p=0.06 (non-inferior, not superior) |
| **REWIND (2019)** | Dulaglutide | T2D CV-risk (primary prevention permitted) | MACE HR 0.88 p=0.026 (superiority) |
| **PIONEER 6 (2019)** | Semaglutide oral | T2D CV-risk | MACE HR 0.79 non-inferior (underpowered for superiority) |
| **SELECT (2023)** | Semaglutide | Obesity with established CV disease WITHOUT T2D | MACE HR 0.80 p<0.001 — FIRST OBESITY CV OUTCOME TRIAL WITH POSITIVE RESULT |
| **SURPASS-CVOT (ongoing)** | Tirzepatide vs dulaglutide | T2D CV-risk | Readout expected |
| **SUMMIT (2024)** | Tirzepatide | HFpEF with obesity | Positive — first GLP-1/GIP HFpEF readout |
| **SURMOUNT-MMO (ongoing)** | Tirzepatide | Obesity CV outcomes | Confirmatory obesity CVOT |

### 3.2 GLP-1 indication expansion trajectory

Current + pipeline GLP-1 label expansions:
- T2D (original indication)
- Obesity / weight management (Wegovy, Zepbound)
- CV outcomes (SELECT-confirmed for semaglutide in obesity + CV disease)
- HFpEF (tirzepatide SUMMIT positive)
- CKD (FLOW semaglutide positive — indication submission pending)
- Sleep apnea (SURMOUNT-OSA tirzepatide approved 2024-12)
- MASH (ESSENCE semaglutide positive 2024 Phase 3)
- Alzheimer's (EVOKE/EVOKE+ pending 2026)
- PAD (STRIDE semaglutide positive)
- Addiction / substance use disorder (investigational)

### 3.3 Commercial dominance

Per `task-modality-peptide.md`:
- Novo Nordisk semaglutide franchise ~$30B+ FY2024
- Eli Lilly tirzepatide ~$15B+ FY2024
- Supply constraint historical (2022-2024)
- Capacity expansion >$10B
- Compounded GLP-1 controversy FDA enforcement late 2024

### 3.4 Multi-receptor agonist pipeline

Per `task-modality-peptide.md`:
- **Retatrutide** (Lilly) — GLP-1/GIP/glucagon triple agonist Phase 3 TRIUMPH
- **CagriSema** (Novo Nordisk) — GLP-1/amylin combination Phase 3
- **Survodutide** (BI) — GLP-1/glucagon Phase 2/3 (SYNCHRONIZE MASH)
- **Pemvidutide** (Altimmune) — GLP-1/glucagon Phase 2
- **Mazdutide** (Innovent+Lilly) — GLP-1/glucagon Phase 3 China-led

---

## §4. SGLT2 Inhibitor Class — Cardiorenal Paradigm Shift

### 4.1 SGLT2 inhibitor CVOT + cardiorenal trajectory

| Trial | Asset | Population | Primary result |
|---|---|---|---|
| **EMPA-REG OUTCOME (2015)** | Empagliflozin | T2D + CV disease | CV death HR 0.62 + first SGLT2 CV benefit |
| **CANVAS (2017)** | Canagliflozin | T2D CV-risk | 3P-MACE HR 0.86 |
| **DECLARE-TIMI 58 (2018)** | Dapagliflozin | T2D CV-risk (broader primary prevention) | HHF + CV death HR 0.83 |
| **DAPA-HF (2019)** | Dapagliflozin | HFrEF (WITHOUT requiring T2D) | CV death or HHF HR 0.74 |
| **EMPEROR-Reduced (2020)** | Empagliflozin | HFrEF | CV death or HHF HR 0.75 |
| **CREDENCE (2019)** | Canagliflozin | T2D + CKD | ESRD composite HR 0.70 |
| **DAPA-CKD (2020)** | Dapagliflozin | CKD (T2D AND non-T2D) | Composite renal/CV HR 0.61 |
| **EMPEROR-Preserved (2021)** | Empagliflozin | HFpEF | HHF HR 0.79 — FIRST HFpEF POSITIVE |
| **DELIVER (2022)** | Dapagliflozin | HFmEF + HFpEF | Composite HR 0.82 |
| **EMPA-KIDNEY (2022)** | Empagliflozin | CKD (broad) | Composite HR 0.72 |
| **FIDELIO-DKD (2020) / FIGARO-DKD (2021)** | Finerenone (non-steroidal MRA, not SGLT2) | CKD + T2D | Cardiorenal composite positive |

### 4.2 SGLT2 class positioning evolution

- **Original T2D glucose-lowering** — 2013+ approvals
- **T2D CV outcome expansion** — 2016-2018
- **HFrEF approval** (non-diabetic) — 2020 dapagliflozin, empagliflozin
- **HFpEF approval** — 2021+ empagliflozin/dapagliflozin class
- **CKD approval** (non-diabetic) — 2021+ dapagliflozin, empagliflozin
- **Net positioning:** foundational cardiorenal therapy + T2D add-on

### 4.3 SGLT2 commercial trajectory

- **Jardiance (empagliflozin)** — BI + Lilly; ~$8B+ FY2024 (approaching top-10 pharma)
- **Farxiga/Forxiga (dapagliflozin)** — AstraZeneca; ~$7B+ FY2024
- **Invokana (canagliflozin)** — JNJ; declining (amputation risk label + late-gen competition)
- **Generic LOE** — approaching for dapagliflozin + canagliflozin (US 2027-2030 range)

---

## §5. Lipid-Lowering Therapy Landscape Evolution

### 5.1 Statin baseline + add-on architecture

**Statin class** — foundational (atorvastatin, rosuvastatin, simvastatin, pravastatin, pitavastatin, etc.)
- Generic-dominated (atorvastatin generic 2011, rosuvastatin 2016)
- Tolerability issues ~10-20% (statin-associated muscle symptoms, hepatic)

**Ezetimibe** — generic; cholesterol absorption inhibitor add-on

### 5.2 PCSK9 inhibitor class

**mAb PCSK9 inhibitors:**
- **Repatha (evolocumab)** — Amgen; FOURIER CVOT positive
- **Praluent (alirocumab)** — Sanofi/Regeneron; ODYSSEY OUTCOMES positive
- **Both Q2W-Q4W SC injection; pricing $14K+/yr historically; substantial price cuts post-uptake challenge**

**siRNA PCSK9 inhibitor:**
- **Leqvio (inclisiran)** — Novartis acquired The Medicines Company 2019 ($9.7B); cross-reference `task-modality-rna.md`
- GalNAc-siRNA liver delivery → PCSK9 synthesis inhibition
- **Q6M dosing** (after loading) — administration convenience advantage
- ORION-11 + ORION-10 pivotal; CVOT ORION-4 + VICTORION-2P ongoing

### 5.3 Novel LDL-C lowering approaches

- **Bempedoic acid (Nexletol)** — Esperion; ACLY inhibitor; CLEAR Outcomes CVOT positive 2023
- **Obicetrapib** — NewAmsterdam; CETP inhibitor Phase 3
- **Muvalaplin** — Lilly; oral Lp(a) Phase 2
- **Olpasiran** — Amgen; siRNA Lp(a); Phase 3

### 5.4 Lp(a) targeting frontier

Lp(a) elevation — genetic cardiovascular risk factor; no approved targeted therapy yet:
- **Pelacarsen / TQJ230** (Novartis+Ionis) — ASO; Lp(a)-HORIZON Phase 3 CVOT ongoing; readout 2025-2026
- **Olpasiran** (Amgen) — siRNA; Phase 3 OCEAN(a)-Outcomes ongoing
- **Lepodisiran** (Lilly) — siRNA; Phase 3
- **Muvalaplin** (Lilly) — oral small molecule inhibitor of Lp(a) assembly; Phase 2 positive
- **Significant commercial potential** — estimated 1 in 5 globally elevated Lp(a) with no current treatment

---

## §6. MASH (Metabolic-dysfunction Associated Steatohepatitis)

### 6.1 Renaming NAFLD → MAFLD → MASLD → MASH

2023 multi-society consensus renamed:
- **MASLD** (Metabolic-dysfunction Associated Steatotic Liver Disease) replacing NAFLD
- **MASH** (Metabolic-dysfunction Associated Steatohepatitis) replacing NASH
- Reflects metabolic pathogenesis emphasis

### 6.2 FDA-approved MASH landscape

**Rezdiffra (resmetirom)** — Madrigal Pharmaceuticals
- **FDA 2024-03-14 accelerated approval** — first MASH-specific FDA approval
- **Thyroid hormone receptor β (THR-β) agonist** — liver-selective
- **MAESTRO-NASH Phase 3** pivotal (N=966; MASH resolution + no worsening fibrosis; fibrosis improvement ≥1 stage + no MASH worsening)
- Confirmatory OS trial ongoing per accelerated approval obligation

### 6.3 GLP-1 + multi-receptor in MASH

- **Semaglutide ESSENCE Phase 3** — 2024 positive (MASH resolution + fibrosis improvement); NDA pending
- **Tirzepatide SYNERGY-NASH Phase 2** — positive; Phase 3 pending
- **Survodutide + pemvidutide** — Phase 2 positive MASH readouts

### 6.4 MASH trial design discipline

- **Biopsy-based primary endpoint** historical — invasive, variable
- **Non-invasive tests (NITs):** VCTE (FibroScan), MRE, MRI-PDFF, serum biomarkers (ELF, ProC3, FIB-4)
- FDA evolving acceptance of NIT-based Phase 3 primary endpoints (pending formal guidance)

### 6.5 Pipeline

- **Efruxifermin (Akero)** — FGF21 analog; Phase 3
- **Pegozafermin (89bio)** — FGF21; Phase 3
- **Tirzepatide + other multi-receptor agonists**
- **Seladelpar (Livdelzi)** — PPARδ agonist; approved for PBC 2024 (liver, not MASH)

---

## §7. Heart Failure Landscape

### 7.1 HFrEF "four pillars" paradigm

Contemporary HFrEF SOC = **four foundational therapies**:
1. **ACE-I / ARB / ARNI (sacubitril-valsartan, Entresto)** — RAS blockade
2. **β-blocker**
3. **MRA (mineralocorticoid receptor antagonist)** — spironolactone, eplerenone, finerenone (non-steroidal)
4. **SGLT2 inhibitor** — dapagliflozin or empagliflozin

### 7.2 HFpEF — emerging treatment paradigm

Historically no HFpEF-approved therapies; 2021+ paradigm shift:
- **Empagliflozin (EMPEROR-Preserved 2021)** + **dapagliflozin (DELIVER 2022)** — first HFpEF-positive trials
- **Tirzepatide SUMMIT (2024)** — first GLP-1/GIP HFpEF positive
- **Finerenone FINEARTS-HF (2024)** — non-steroidal MRA HFpEF positive

### 7.3 Amyloidosis + TTR cardiomyopathy

Separate pathophysiology but frequently enters HF differential:
- **Tafamidis (Vyndaqel/Vyndamax)** — Pfizer; ATTR-CM
- **Patisiran (Onpattro) + Vutrisiran (Amvuttra)** — Alnylam siRNA ATTR
- **Inotersen (Tegsedi) + Eplontersen (Wainua)** — Ionis ASO ATTR
- **Acoramidis (Attruby)** — BridgeBio; stabilizer; FDA 2024-11
- **NTLA-2001** (Intellia) — in vivo CRISPR TTR knockout; Phase 3 MAGNITUDE

Cross-reference `task-modality-rna.md` for TTR-targeted ASO/siRNA.

---

## §8. Other Notable Cardiometabolic Therapeutics

### 8.1 Insulin landscape

- **Rapid-acting analogs:** aspart (NovoLog), lispro (Humalog), glulisine (Apidra)
- **Long-acting analogs:** glargine (Lantus, Basaglar biosimilar, Semglee interchangeable biosimilar), degludec (Tresiba), detemir (Levemir)
- **Ultra-long-acting weekly:** **Awiqli / icodec (Novo Nordisk)** — FDA approval delayed CRL 2024; Phase 3 ongoing
- **Inhaled insulin:** Afrezza (MannKind) — niche

### 8.2 Type 1 diabetes landscape

- **Tzield (teplizumab)** — Provention/Sanofi; anti-CD3 mAb; **first disease-modifying T1D therapy** FDA 2022-11; delays T1D onset in at-risk stage 2 patients
- **Islet cell therapy:** Lantidra (donislecel — CellTrans) — first allogeneic pancreatic islet cell therapy FDA 2023-06

### 8.3 Novel hypertension

- **Baxdrostat (AstraZeneca)** — aldosterone synthase inhibitor; Phase 3 BaxHTN + Bax24 ongoing
- **Zilebesiran (Alnylam)** — siRNA angiotensinogen; Phase 2 positive
- **Lorundrostat (Mineralys)** — aldosterone synthase inhibitor

### 8.4 IgA nephropathy (IgAN)

- **Tarpeyo (budesonide delayed-release, Calliditas)** — FDA 2021 accelerated → 2023-12 traditional
- **Filspari (sparsentan, Travere)** — ETA + ARB dual; FDA 2023-02
- **Iptacopan (Fabhalta, Novartis)** — complement factor B inhibitor; FDA 2024-08

### 8.5 Hyperkalemia

- **Veltassa (patiromer)** — CSL Vifor
- **Lokelma (sodium zirconium cyclosilicate)** — AstraZeneca
- Increasingly relevant as MRA + finerenone use expands (MRAs cause hyperkalemia)

---

## §9. HTA + Access Patterns for Cardiometabolic

### 9.1 US payer dynamics

- **Commercial + Medicare Part D** — GLP-1 obesity coverage highly restrictive (most commercial plans exclude obesity; Medicare Part D statute excluded weight loss drugs until 2024 CMS proposed rule)
- **Inflation Reduction Act (IRA) 2022** — Medicare Part D negotiation began 2024; first 10 drugs include diabetes (Jardiance + Xarelto + Januvia); more cardiometabolic on subsequent lists
- **PBM formulary dynamics** — Express Scripts + CVS Caremark + Optum Rx shape access
- **GLP-1 obesity coverage expanding 2024+** — some employer plans, Medicaid state-by-state, Medicare Part D under consideration

### 9.2 EU + UK + NICE

- **NICE TA pathway** — cost-effectiveness focused; sometimes restricts GLP-1 obesity to BMI thresholds
- **G-BA AMNOG Germany** — additional benefit assessment
- **HAS ASMR France** — innovation rating
- **Typical price cuts vs US list:** 40-70% off US WAC

### 9.3 Türkiye cardiometabolic ekosistemi

- **TİTCK + SGK SUT** — çoğu DM + KV + renal ilaç SUT EK-4C listesinde; raporlu ilaç + uzman hekim şart
- **SGK GLP-1 erişimi** — T2D endikasyonu geri ödeme mevcut (endikasyon tanı kodu ile); **obezite endikasyonu SGK geri ödemesinde DEĞİL** — özel ödeme dominant
- **SGLT2i geri ödeme** — T2D + HF + CKD genişleyen endikasyonlara göre güncellenmekte
- **Biyobenzer insülin** — insulin glargine biosimilar (Sanofi Lantus'un biyobenzeri) Türk yerli üretim mevcut (cross-reference `task-modality-biosimilar.md`)
- **Türk jenerik kardiometabolik ekosistemi** — atorvastatin, rosuvastatin, metformin, sitagliptin, losartan, amlodipin, valsartan çoğu molekül yerli jenerik (cross-reference `task-modality-smallmol.md`)

### 9.4 China NMPA + NRDL

- Major GLP-1 price negotiations recent (tirzepatide Mounjaro ~75% price cut for NRDL inclusion rumored)
- VBP cycles include cardiometabolic molecules
- Chinese multi-receptor agonists (mazdutide — Innovent+Lilly) domestic Phase 3 advantage

---

## §10. Stakeholder-Spesifik Analytical Framework

### 10.1 GLP-1 dominant sponsors (Novo Nordisk + Eli Lilly)
- Multi-indication lifecycle strategy (T2D → obesity → CV → HFpEF → CKD → MASH → AD)
- Capacity as strategic moat
- Multi-receptor agonist differentiation
- Pricing power vs emerging payer pressure

### 10.2 SGLT2 sponsors (BI+Lilly, AstraZeneca, JNJ, Merck)
- Cardiorenal indication expansion
- LOE approach + defensive strategy
- Combination opportunities (SGLT2i + GLP-1 in T2D; SGLT2i + finerenone in CKD)

### 10.3 Lipid-focused sponsors (Amgen, Sanofi/Regeneron, Novartis, Ionis, Alnylam, Esperion, Lilly)
- Lp(a) commercial opportunity development
- LOE management for statin mature markets
- Combination strategy with emerging agents

### 10.4 MASH + liver sponsors (Madrigal, Akero, 89bio, Intercept)
- First-mover commercial execution (Madrigal Rezdiffra)
- GLP-1 MASH disruption risk
- Biomarker-based trial design optimization

### 10.5 Payer paydaşları
- GLP-1 obesity coverage policy evolution
- IRA Part D negotiation impact on cardiometabolic
- Outcomes-based contracting for cardiorenal

### 10.6 Klinisyen paydaşları
- PCP vs specialist prescriber dynamics (cardiometabolic = PCP-heavy)
- Guideline alignment (ADA, ESC, ACC/AHA, KDIGO, AASLD)
- Step therapy compliance

### 10.7 Hasta paydaşları
- Adherence challenges in chronic cardiometabolic therapy
- Injection acceptability for GLP-1 + PCSK9 mAb
- Out-of-pocket cost for non-covered obesity indication

---

## §11. Confidence Stamping for Cardiometabolic Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| CVOT pivotal trial efficacy (HR, p-value, CI) | **High** (peer-reviewed) |
| Guideline recommendation (ADA, ESC, KDIGO) | **High** (guideline primary) |
| Real-world GLP-1 uptake | **Medium** (registry quality varies) |
| GLP-1 net pricing after PBM rebates | **Low** (confidential) |
| Pipeline Phase 3 readout timing | **Medium** (sponsor guidance) |
| IRA Part D negotiated prices | **High** when published (CMS) |
| MASH NIT-based endpoint regulatory acceptance | **Medium** (evolving) |
| Compounded GLP-1 quality | **Low** |
| Confidential sponsor strategy | Should not be claimed |

---

## §12. Forbidden Patterns

- ❌ Treating GLP-1 obesity indication as commercial certainty where not payer-covered
- ❌ Generalizing one SGLT2 trial to entire class (some within-class trial differences exist)
- ❌ Conflating T2D glycemic benefit with CV outcome benefit (HbA1c reduction ≠ MACE reduction inherently)
- ❌ Overstating MASH NIT acceptance pre-FDA formal guidance
- ❌ Treating SELECT obesity CV benefit as generalizable to all GLP-1 (SELECT was semaglutide-spesifik; other GLP-1s CV outcome in obesity not established)
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Speculation about confidential PBM rebate structures for GLP-1
- ❌ Recommending compounded GLP-1 as therapeutic equivalents

---

## §13. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. Layer 2 Cardiometabolic (Metabolic / Cardiovascular / Renal / Hepatic) TA template covering: integrated cardiometabolic epistemology (T2D↔ASCVD↔CKD↔HF↔obesity↔MASH interconnection driving lifecycle expansion strategies), CVOT history (FDA 2008 T2D CV safety guidance post-rosiglitazone Avandia → 2018/2020 revision removing mandatory CVOT → CVOT becomes commercial asset beyond regulatory floor), guideline ecosystem (ADA Standards of Care + EASD + AACE + IDF for diabetes; ACC/AHA + ESC + HFSA cardiovascular; AHA/ACC + ESC/EAS lipids; KDIGO + NKF renal; AASLD + EASL MASH), endpoint frameworks (glycemic HbA1c/TIR; weight %BW loss/BMI/waist; lipid LDL-C/ApoB/non-HDL/Lp(a); CV 3P-MACE + 4P-MACE; renal eGFR slope + UACR + ESRD composite; MASH resolution histology → NIT evolution; cardiorenal composite), GLP-1 class as dominant paradigm (LEADER semaglutide + REWIND + SUSTAIN-6 + EXSCEL + PIONEER 6 + SELECT 2023 first obesity CVOT + SUMMIT tirzepatide HFpEF 2024 + SURMOUNT-MMO + FLOW CKD + ESSENCE MASH + SURMOUNT-OSA sleep apnea 2024-12 + EVOKE Alzheimer pending 2026; commercial dominance Novo semaglutide ~$30B+ + Lilly tirzepatide ~$15B+; multi-receptor agonist pipeline retatrutide + CagriSema + survodutide + pemvidutide + mazdutide), SGLT2 cardiorenal paradigm shift (EMPA-REG 2015 first positive CVOT + CANVAS + DECLARE + DAPA-HF 2019 first non-diabetic HFrEF + EMPEROR-Reduced + CREDENCE + DAPA-CKD + EMPEROR-Preserved 2021 first HFpEF positive + DELIVER + EMPA-KIDNEY + FIDELIO/FIGARO finerenone non-steroidal MRA; Jardiance ~$8B + Farxiga ~$7B FY2024; generic LOE approaching), lipid landscape evolution (statin baseline + ezetimibe + PCSK9 mAb Repatha FOURIER + Praluent ODYSSEY OUTCOMES; inclisiran Leqvio siRNA Q6M cross-reference task-modality-rna.md + Novartis Medicines Company $9.7B 2019; bempedoic acid Nexletol CLEAR Outcomes 2023; Lp(a) frontier pelacarsen Lp(a)-HORIZON + olpasiran + lepodisiran + muvalaplin), MASH landscape (NAFLD→MAFLD→MASLD/MASH 2023 renaming; Rezdiffra resmetirom Madrigal FDA 2024-03-14 first MASH approval via MAESTRO-NASH THR-β; GLP-1 MASH competition ESSENCE + SYNERGY-NASH + survodutide + pemvidutide; FGF21 analogs efruxifermin + pegozafermin Phase 3; NIT-based trial evolution VCTE MRE MRI-PDFF ELF), HF landscape (HFrEF four pillars ACE-I/ARB/ARNI + β-blocker + MRA + SGLT2i foundational; HFpEF emerging SGLT2 class + tirzepatide SUMMIT + finerenone FINEARTS-HF; ATTR cardiomyopathy tafamidis + patisiran + vutrisiran + inotersen + eplontersen + acoramidis + NTLA-2001 in vivo CRISPR), other notable (insulin weekly icodec Awiqli CRL 2024; T1D Tzield teplizumab anti-CD3 + Lantidra islet cell; novel HTN baxdrostat + zilebesiran siRNA + lorundrostat; IgAN Tarpeyo budesonide + Filspari sparsentan + Fabhalta iptacopan; hyperkalemia Veltassa + Lokelma), HTA + access (US IRA 2022 Part D negotiation 2024 first 10 drugs include Jardiance + Xarelto + Januvia; GLP-1 obesity coverage evolving + Medicare Part D 2024 proposed rule; NICE + G-BA AMNOG + HAS ASMR typical 40-70% price cuts; Türkiye SGK SUT EK-4C GLP-1 T2D covered + obesity NOT covered + SGLT2 expanding + biyobenzer insülin yerli + Türk jenerik kardiometabolik ekosistemi; China NMPA NRDL negotiations + VBP + domestic multi-receptor Innovent mazdutide). New manifest gate G45. Cross-references task-modality-peptide.md (GLP-1 class disciplines), task-modality-rna.md (inclisiran + olpasiran + pelacarsen + eplontersen + NTLA-2001 + zilebesiran), task-modality-smallmol.md (SGLT2i + statin + finerenone generics), task-modality-biosimilar.md (insulin glargine biosimilar), task-ta-rare-disease.md (ATTR cardiomyopathy overlap + FH cross-reference), analytics-framework.md (GLP-1 commercial NPV + SGLT2 cardiorenal sensitivity), api-integrations.md (FDA + CT.gov + ADA Scientific Sessions catalysts).
