# task-ta-infectious.md

**T3 Therapeutic Area Template — Infectious Disease / Antimicrobial Therapeutics (v4.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Paxlovid nirmatrelvir/ritonavir in COVID-19" invokes Layer 0 + Layer 1 task-modality-smallmol.md + Layer 2 infectious. "mRESVIA RSV mRNA vaccine" invokes Layer 0 + Layer 1 task-modality-rna.md + Layer 2 infectious.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "infectious disease", "enfeksiyon hastalıkları", "enfeksiyon", "antimicrobial", "antimikrobiyal", "antibacterial", "antibiyotik", "antifungal", "antifungal", "antiviral", "antiviral", "antiparasitic", "antiparaziter", "antimycobacterial", "vaccine", "aşı", "immunization"
- Disease terms — bacterial: "MRSA", "VRE", "CRE", "ESBL", "carbapenem-resistant", "MDRO", "Clostridioides difficile", "C. diff", "cUTI", "complicated urinary tract infection", "cIAI", "complicated intra-abdominal infection", "CAP", "community-acquired pneumonia", "HAP", "VAP", "hospital-acquired pneumonia", "ventilator-associated pneumonia", "ABSSSI", "acute bacterial skin infection", "tuberculosis", "TB", "Mycobacterium", "MDR-TB", "XDR-TB", "NTM", "nontuberculous mycobacteria", "gonorrhea", "syphilis", "sepsis"
- Disease terms — viral: "COVID-19", "SARS-CoV-2", "influenza", "grip", "influenza A/B", "RSV", "respiratory syncytial virus", "HIV", "HIV-1", "AIDS", "HCV", "hepatitis C", "HBV", "hepatitis B", "CMV", "cytomegalovirus", "HSV", "herpes", "VZV", "varicella-zoster", "shingles", "HPV", "human papillomavirus", "Ebola", "Marburg", "monkeypox", "mpox", "dengue", "Zika", "yellow fever", "West Nile"
- Disease terms — fungal: "invasive aspergillosis", "Aspergillus", "Candida auris", "mucormycosis", "cryptococcosis", "Pneumocystis"
- Disease terms — parasitic: "malaria", "sıtma", "Plasmodium", "Chagas", "leishmaniasis", "toxoplasmosis", "onchocerciasis", "schistosomiasis", "helminthiasis"
- Mechanism/class terms: "β-lactam", "carbapenem", "cephalosporin", "fluoroquinolone", "macrolide", "aminoglycoside", "glycopeptide", "lipopeptide", "oxazolidinone", "polymyxin", "azole antifungal", "echinocandin", "polyene", "NRTI", "NNRTI", "protease inhibitor", "integrase strand transfer inhibitor", "INSTI", "direct-acting antiviral", "DAA", "NS5A inhibitor", "NS5B inhibitor", "neuraminidase inhibitor", "mRNA vaccine", "adjuvant"
- Regulatory terms: "QIDP", "Qualified Infectious Disease Product", "GAIN Act", "Generating Antibiotic Incentives Now", "LPAD pathway", "Limited Population Pathway for Antibacterial and Antifungal Drugs", "material threat medical countermeasure", "MCM", "BARDA", "PREP Act", "Priority Review Voucher infectious", "tropical disease PRV"
- Asset names (illustrative subset): "Paxlovid", "nirmatrelvir/ritonavir", "Lagevrio", "molnupiravir", "Veklury", "remdesivir", "Tamiflu", "oseltamivir", "Xofluza", "baloxavir", "Mavyret", "Epclusa", "Harvoni", "Sovaldi", "sofosbuvir", "Vosevi", "Biktarvy", "Descovy", "Truvada", "Genvoya", "Triumeq", "Tivicay", "dolutegravir", "Apretude", "cabotegravir", "Cabenuva", "Sunlenca", "lenacapavir", "Lenmeldy", "Zepzelca", "Arexvy", "Abrysvo", "mRESVIA", "Beyfortus", "nirsevimab", "Shingrix", "Gardasil 9", "Comirnaty", "Spikevax", "Novavax", "Vabysmo", "Tecartus", "Dalvance", "dalbavancin", "Orbactiv", "oritavancin", "Sivextro", "tedizolid", "Xerava", "eravacycline", "Vabomere", "meropenem/vaborbactam", "Recarbrio", "imipenem/cilastatin/relebactam", "Fetroja", "cefiderocol", "Zemdri", "plazomicin", "Nuzyra", "omadacycline", "Baxdela", "delafloxacin", "Pretomanid", "Sirturo", "bedaquiline", "Cresemba", "isavuconazole", "Brexafemme", "ibrexafungerp", "Rezzayo", "rezafungin", "Prevymis", "letermovir", "Livtencity", "maribavir"

### 1.2 Implicit semantic triggers
- Antimicrobial resistance (AMR) discussion
- WHO priority pathogen list invocation
- Antibiotic stewardship programs
- Post-pandemic vaccine / antiviral landscape
- HIV prevention (PrEP/PEP) + treatment paradigm
- HCV cure era commercial trajectory

### 1.3 NOT triggered by
- ❌ User employer with ID portfolio (GSK, Pfizer, Merck & Co, Gilead, ViiV Healthcare, AbbVie, Shionogi, Moderna, BioNTech, Novavax, Sanofi Vaccines, Sarepta, Cipla, Sun Pharma, Indian generic ID manufacturers)
- ❌ User memory-derived infectious diseases / epidemiology specialty
- ❌ User geography being an ID trial hub

---

## §2. Foundational ID Framework

### 2.1 ID as a TA — distinguishing features

Infectious disease occupies a unique regulatory + commercial position:
- **Population health externalities** — AMR + pandemic preparedness → public good dimension absent in most TAs
- **Stewardship constraint** — approved use deliberately restricted to preserve effectiveness (opposite of typical commercial maximization)
- **Pandemic wildcard** — COVID-19 demonstrated 2-year vaccine+antiviral value creation cycles
- **Cure paradigm in specific indications** — HCV DAAs cured disease, collapsed market
- **Vaccine vs therapeutic distinction** — prophylactic vaccines follow different regulatory + pricing + payer framework
- **Government procurement dominance** — BARDA, SNS, Gavi, GF shape development economics
- **Resistance clock** — all antimicrobials deliver declining efficacy over time as resistance emerges

### 2.2 AMR (Antimicrobial Resistance) as global priority

**WHO priority pathogens list (2024 update):**
- **Critical priority:** Acinetobacter baumannii carbapenem-resistant (CRAB), Pseudomonas aeruginosa CR, Enterobacterales 3rd-gen cephalosporin + carbapenem-resistant, Mycobacterium tuberculosis rifampicin-resistant
- **High priority:** Salmonella Typhi, Shigella, Enterococcus faecium VRE, Staphylococcus aureus methicillin-resistant (MRSA), Neisseria gonorrhoeae resistant
- **Medium priority:** Streptococcus pneumoniae penicillin-non-susceptible, Haemophilus influenzae ampicillin-resistant

**Economic anomaly:** AMR generates public health catastrophe risk but private sector R&D is underfunded due to:
- Stewardship-limited use
- Resistance-related short market life
- Generic-dominated legacy market pricing anchors
- Comparator arm ambiguity in clinical trials

### 2.3 ID endpoint frameworks

| Category | Primary endpoints |
|---|---|
| **Acute bacterial infection** | Clinical cure rate (end-of-treatment + test-of-cure); microbiological cure |
| **HIV** | HIV RNA <50 copies/mL at Week 48/96; CD4 reconstitution |
| **HCV** | Sustained virologic response (SVR12) — undetectable HCV RNA 12 weeks post-treatment |
| **HBV** | HBeAg/HBsAg seroconversion; HBV DNA suppression |
| **Influenza / RSV** | Time to symptom resolution; viral shedding reduction |
| **COVID-19** | Hospitalization/death composite; time to symptom resolution |
| **TB** | Sputum culture conversion; relapse-free cure at 2 years |
| **Invasive fungal** | Global response at end-of-treatment + 6-week mortality |
| **Vaccine efficacy** | Case reduction vs placebo in primary endpoint (disease-spesifik severity definitions) |

---

## §3. FDA Regulatory Pathway Disciplines for Antimicrobials

### 3.1 GAIN Act (2012) + QIDP Designation — Core Antibiotic Incentive

**Generating Antibiotic Incentives Now (GAIN) Act** enacted as part of Food and Drug Administration Safety and Innovation Act (FDASIA 2012), Section 801-805 codified at 21 USC §355f:

**QIDP (Qualified Infectious Disease Product) designation:**
- **Scope:** "an antibacterial or antifungal drug for human use intended to treat serious or life-threatening infections" including resistant pathogens
- **Qualifying pathogens list:** FDA codified in 21 CFR 317.2 (final rule June 2014)
- **Benefits:**
  - 5-year extension added to end of nonpatent exclusivities (NCE 5-yr/Clinical 3-yr/Orphan 7-yr)
  - Automatic Priority Review eligibility
  - Automatic Fast Track eligibility

**Example arithmetic:** QIDP + NCE → 10 years exclusivity + 9-year Hatch-Waxman litigation immunity

**Critical limitations:**
- QIDP not available for biologics (vaccines, mAbs) — only small molecules + combination products under FDCA §505(b)
- Antivirals + antiparasitics NOT QIDP-eligible (antibacterial + antifungal only)
- Critics argue GAIN rewards modifications over novel drugs due to time-value discount
- 147 QIDP designations 2012-2017; 25 antimicrobial approvals 2012-2022, 20 with QIDP designation

### 3.2 LPAD (Limited Population Pathway for Antibacterial and Antifungal Drugs)

**Pathway (21st Century Cures Act 2016):**
- Streamlined regulatory pathway for drugs addressing serious/life-threatening infections in **limited patient populations** with unmet need
- Allows approval with smaller/more targeted clinical data packages
- Requires labeling acknowledging limited-population indication
- First approval: Arikayce (amikacin liposome inhalation) 2018 for MAC lung disease
- Fetroja (cefiderocol) + Recarbrio + Xenleta partial LPAD framework utilization

### 3.3 FDA Priority Review Vouchers for Infectious Disease

Two separate PRV programs create overlapping incentives:

| PRV type | Eligibility | Commercial value |
|---|---|---|
| **Tropical Disease PRV** (§524 FDCA, 2007) | Approved drug for 21 listed tropical diseases (dengue, Ebola, chikungunya, Chagas, malaria, TB, etc.) | $50-500M market; tradeable |
| **Material Threat Medical Countermeasure PRV** (§565A FDCA, 2016) | Approved drug for material biosecurity threat per DHS list | Similar market value |
| **Rare Pediatric Disease PRV** (§529 FDCA, 2012) | Not ID-spesifik but applicable to rare pediatric ID conditions | Same market (cross-reference `task-ta-rare-disease.md`) |

### 3.4 BARDA + Project BioShield

**Biomedical Advanced Research and Development Authority (BARDA)** — HHS entity providing:
- Development funding for medical countermeasures
- Advance purchase commitments (AMC) for pandemic/biosecurity threats
- Project BioShield Act 2004 authorized Strategic National Stockpile procurement

**Post-COVID implications:**
- Massive BARDA + Operation Warp Speed investment 2020-2021 (~$18B+) transformed mRNA vaccine platforms (Moderna, Pfizer-BioNTech)
- Post-pandemic BARDA funding normalization creates boom-bust cycle
- Domestic manufacturing resilience emphasis

### 3.5 Accelerated Approval for infectious diseases

Historically limited use but expanding:
- HIV drugs (indinavir, ritonavir era — accelerated approval via surrogate markers)
- HCV DAAs (SVR12 accepted as clinical benefit surrogate)
- Some TB drugs (pretomanid + bedaquiline)
- Generally uncommon vs oncology dominance

---

## §4. Major Therapeutic Sub-Landscapes

### 4.1 HIV — Mature franchise ecosystem

**Regimen architecture:**
- Integrase strand transfer inhibitor (INSTI) backbone: dolutegravir (Tivicay), bictegravir (component of Biktarvy)
- NRTI backbone: TAF (tenofovir alafenamide)/FTC — core
- PI-based regimens (older paradigm, declining)

**Commercial landscape (Gilead-dominated):**
- **Biktarvy** (bictegravir/FTC/TAF) — ~$14B+ FY2024, market leader
- **Descovy** (FTC/TAF) — backbone + PrEP
- **Truvada** (FTC/TDF) — generic post-2020 for PrEP
- **Genvoya** — Stribild replacement

**PrEP evolution:**
- Truvada (oral daily) — generic
- Descovy (oral daily)
- Apretude (cabotegravir LA IM Q2M) — ViiV Healthcare; first long-acting injectable PrEP
- **Sunlenca (lenacapavir)** — Gilead; capsid inhibitor; FDA 2022 for HIV-1 treatment-experienced; **PURPOSE-1 Phase 3** (2024) demonstrated 100% PrEP efficacy twice-yearly SC — pending PrEP approval submission

**Long-acting treatment:**
- **Cabenuva** (cabotegravir + rilpivirine LA) — monthly/Q2M IM injection
- **Sunlenca + islatravir** (Merck, clinical) — investigational oral once-weekly + LA

### 4.2 HCV — Cure era commercial trajectory

**Historical paradigm shift:**
- 2011 telaprevir/boceprevir — first-wave DAAs (triple therapy with IFN/RBV)
- **2013 Sovaldi (sofosbuvir)** — Gilead acquired from Pharmasset for $11B; ~$28B peak 2015
- 2014 Harvoni (sofosbuvir/ledipasvir) — Gilead
- 2016 Epclusa (sofosbuvir/velpatasvir pan-genotypic) — Gilead
- 2017 Mavyret (glecaprevir/pibrentasvir) — AbbVie; 8-week pan-genotypic
- 2017 Vosevi (sofosbuvir/velpatasvir/voxilaprevir) — retreatment

**Market collapse dynamic:**
- SVR12 rates >95% → cure converted chronic HCV to time-limited market
- Payer patient queue exhaustion 2015-2018
- Global HCV market ~$4-5B 2024 (vs ~$22B peak 2015)

**Contemporary landscape:** Mavyret + Epclusa dominant; <$25K/course US; ~$150-300/course NHS tender

### 4.3 COVID-19 therapeutics

**Therapeutic landscape mature:**
- **Paxlovid (nirmatrelvir/ritonavir)** — Pfizer; oral antiviral; ~$27B FY2022 peak → declining
- **Lagevrio (molnupiravir)** — Merck/Ridgeback; oral; modest efficacy
- **Veklury (remdesivir)** — Gilead; IV antiviral
- mAb therapies (Evusheld, bamlanivimab, casirivimab/imdevimab) largely obsolete due to variant evolution

### 4.4 Antibacterial landscape

**Recently approved novel antibacterials:**
| Asset | Class | Sponsor | Indication | Approval |
|---|---|---|---|---|
| **Dalvance (dalbavancin)** | Lipoglycopeptide | AbbVie | ABSSSI | 2014 (QIDP) |
| **Sivextro (tedizolid)** | Oxazolidinone | Merck | ABSSSI | 2014 (QIDP) |
| **Avycaz (ceftazidime/avibactam)** | BL/BLI | AbbVie/Pfizer | cUTI/cIAI + HAP/VAP | 2015 |
| **Vabomere (meropenem/vaborbactam)** | BL/BLI | Melinta | cUTI | 2017 |
| **Xerava (eravacycline)** | Tetracycline | Tetraphase/La Jolla | cIAI | 2018 |
| **Zemdri (plazomicin)** | Aminoglycoside | Achaogen (bankrupt) | cUTI | 2018 |
| **Nuzyra (omadacycline)** | Tetracycline | Paratek | ABSSSI/CAP | 2018 |
| **Recarbrio (imipenem/cilastatin/relebactam)** | BL/BLI | Merck | HAP/VAP | 2019 |
| **Fetroja (cefiderocol)** | Siderophore cephalosporin | Shionogi | cUTI/HAP/VAP/CR pathogens | 2019 |
| **Zerbaxa (ceftolozane/tazobactam)** | BL/BLI | Merck | cUTI/cIAI/HAP/VAP | 2014 |
| **Exblifep (cefepime/enmetazobactam)** | BL/BLI | Allecra/Innoviva | cUTI | 2024 |
| **Orlynvah (sulopenem)** | Penem + probenecid | Iterion/Hikma | uUTI oral | 2024 |

**Commercial reality:** Despite QIDP designation, many have underperformed commercially:
- Achaogen (Zemdri developer) bankrupt 2019 post-approval
- Melinta bankrupt 2019
- Tetraphase acquired by La Jolla at distressed valuation
- Paratek went private at low valuation

### 4.5 Antifungal landscape

- **Cresemba (isavuconazole)** — Astellas/Basilea; broad-spectrum triazole; 2015
- **Noxafil (posaconazole)** — Merck; triazole
- **Brexafemme (ibrexafungerp)** — SCYNEXIS; first-in-class glucan synthase inhibitor; VVC 2021
- **Rezzayo (rezafungin)** — Cidara/Mundipharma; long-acting echinocandin; 2023
- **Olorofim** (F2G) — Phase 3 invasive mold; novel orotomide class
- **Candida auris** driving urgent antifungal development

### 4.6 TB landscape

- **Sirturo (bedaquiline)** — Janssen/JNJ; first novel TB drug in ~40 years; 2012
- **Pretomanid** — TB Alliance; 2019 (BPaL regimen with bedaquiline + linezolid)
- **Sutezolid, delpazolid, sanfetrinem** — Phase 2/3 investigational
- **Drug-resistant TB** priority; BPaL regimen transforming XDR-TB treatment

### 4.7 Antiviral — specific indications

- **Prevymis (letermovir)** — Merck; CMV prophylaxis HSCT + expanded kidney transplant 2024
- **Livtencity (maribavir)** — Takeda; refractory CMV 2021
- **Arexvy (RSVPreF3)** — GSK; RSV vaccine ≥60 2023 (first RSV vaccine adult)
- **Abrysvo (RSVpreF)** — Pfizer; RSV vaccine adult + maternal 2023
- **mRESVIA (mRNA-1345)** — Moderna; RSV mRNA vaccine 2024 (first mRNA RSV approval)
- **Beyfortus (nirsevimab)** — AstraZeneca/Sanofi; RSV prophylaxis infants mAb; 2023

### 4.8 Vaccine landscape (preventive + therapeutic)

**Pediatric routine:** ACIP schedule-driven; Prevnar class (PCV13/PCV15/PCV20) + MMR + varicella + DTaP + Hib + HepB + rotavirus

**Adult routine:** Shingrix (zoster) + PCV20 + Arexvy/Abrysvo/mRESVIA (RSV) + influenza annual + COVID-19 updated + Tdap

**HPV:** Gardasil 9 + Cervarix — cancer prevention

**Therapeutic vaccines:** limited approvals (Provenge sipuleucel-T prostate oncology historical; current pipeline includes cancer vaccines per `task-ta-oncology.md`)

---

## §5. Pandemic Preparedness + Biosecurity

### 5.1 COVID-19 lessons

- mRNA platform validation: ~11 months from sequence to EUA
- Operation Warp Speed federal coordination
- Post-pandemic vaccine/antiviral demand normalization challenged manufacturer valuations
- Future pandemic preparedness ongoing BARDA + HHS investments

### 5.2 Biosecurity programs

- **Strategic National Stockpile (SNS)** — HHS
- **Project BioShield Act 2004**
- **Material threat countermeasures PRV** — incentive for biosecurity assets
- **Ebola vaccines** — Ervebo (Merck, 2019) + Zabdeno/Mvabea (JNJ, 2020)

### 5.3 Monkeypox (mpox) response

- **Jynneos** (Bavarian Nordic) — mpox/smallpox vaccine
- **TPOXX (tecovirimat)** — SIGA Technologies; mpox + smallpox antiviral
- 2022 mpox outbreak + 2024 clade I response demonstrated stockpile-activation paradigm

---

## §6. Antimicrobial Stewardship + Health System Infrastructure

### 6.1 Stewardship programs — commercial tension

Antimicrobial Stewardship Programs (ASPs) designed to restrict inappropriate antimicrobial use:
- Joint Commission requires ASP for hospital accreditation since 2017
- CMS Conditions of Participation for stewardship
- Restrictive formulary + prior authorization + audit-and-feedback common

**Commercial implication:** Stewardship is antithetical to typical volume-maximization sales strategy. Novel antimicrobial commercial models increasingly discussed:
- Subscription / pull incentive (UK NHS dalbavancin subscription 2022+)
- De-linkage of revenue from volume
- Advance market commitments (AMCs)

### 6.2 Diagnostics + rapid testing

- Rapid diagnostic tests (RDT) for influenza, COVID-19, strep, gonorrhea
- Nucleic acid amplification tests (NAAT)
- Phenotypic susceptibility testing (AST)
- Host response biomarkers (procalcitonin, viral/bacterial signatures)
- Companion diagnostics for narrow-spectrum antimicrobials increasingly required

---

## §7. Türkiye Infectious Disease Ekosistemi

### 7.1 TİTCK + SGK SUT infectious disease access

- **TİTCK onay** — çoğu antimikrobiyal EMA/FDA reliance pathway
- **SGK SUT geri ödeme** — antibakteriyel/antiviral ürünler SUT EK-4/G "Enfeksiyon hastalıkları ilaçları" listesinde
- **Kısıtlı kullanım raporlu** — geniş-spektrumlu antibiyotikler (karbapenem, linezolid, vankomisin, daptomisin, seftolozan-tazobaktam, seftazidim-avibaktam) enfeksiyon hastalıkları uzmanı imzası + kültür-antibiyogram gerekli
- **HIV tedavisi** — SGK EK-4C psikotropik/özel ilaç grubu altında, enfeksiyon hastalıkları uzmanı imzalı; Biktarvy + Triumeq + Genvoya + Dovato + jenerik emtricitabine/tenofovir geri ödemede
- **HCV tedavisi** — Mavyret + Epclusa + Harvoni SGK geri ödemesinde, gastroenteroloji/enfeksiyon uzmanı imzası + fibrosis evresi raporu; yerli jenerik ledipasvir-sofosbuvir + velpatasvir-sofosbuvir mevcut
- **HBV tedavisi** — tenofovir (yerli jenerik) + entekavir (yerli jenerik) birinci basamak

### 7.2 Türk yerli jenerik antimikrobiyal ekosistemi

- **Antibakteriyel:** tüm major klaslar (penisilin, sefalosporin, karbapenem, fluorokinolon, makrolid, aminoglikozit, glikopeptid) yerli jenerik üretim yaygın
- **Antiviral:** oseltamivir + acyclovir + valacyclovir + ganciclovir + tenofovir + emtricitabine + dolutegravir (jenerik) + sofosbuvir-ledipasvir + sofosbuvir-velpatasvir yerli üretim
- **Antifungal:** flukonazol + itrakonazol + vorikonazol + kaspofungin + mikafungin yerli üretim
- **Yerli sponsor ekosistemi:** Deva Holding (antibakteriyel + antiviral), Abdi İbrahim, Bilim İlaç, Sanovel, Pharmactive, Eczacıbaşı, Mustafa Nevzat-Pfizer

### 7.3 Türkiye aşı ekosistemi

- **COVID-19 aşıları:** TURKOVAC (Erciyes + Kayseri inaktif; TİTCK 2021 acil kullanım); BioNTech Comirnaty ithalat; Sinovac CoronaVac ithalat (pandemi dönemi)
- **Çocukluk aşı takvimi:** Sağlık Bakanlığı protokolü — ücretsiz uygulanır; genelde Sanofi/GSK/Pfizer/Merck ithalat
- **TÜSEB** — Türkiye Sağlık Enstitüleri Başkanlığı; aşı + biyoteknoloji Ar-Ge koordinasyonu

### 7.4 AMR Türkiye spesifik

- Türkiye'de **hastane enfeksiyonu MRSA + ESBL + CRE yüksek prevalans** — dirençli patojenler için tertiary merkezlerde sık başvuru
- SAGEM (Sağlık Bakanlığı Sağlık Hizmetleri Genel Müdürlüğü) AMR izlem programı
- Ulusal Antibiyotik Stewardship Programı yürütülmekte

---

## §8. Stakeholder-Spesifik Analytical Framework

### 8.1 Big Pharma ID sponsors (GSK, Pfizer, Merck, Gilead, ViiV, Sanofi)
- HIV + vaccine franchise defense
- Novel antibacterial portfolio ROI challenges
- Pandemic preparedness partnership
- BARDA/Gavi/UNICEF procurement dynamics

### 8.2 Biotech antimicrobial sponsors
- Financial sustainability post-approval (Achaogen/Melinta/Tetraphase precedents)
- Licensing vs indep. commercialization
- GAIN + LPAD + PRV incentive maximization
- Specialty sales force economics

### 8.3 Vaccine developer sponsors (Moderna, BioNTech, Novavax)
- mRNA platform monetization beyond COVID
- Global health partnerships (Gavi, CEPI)
- Emergent pandemic response capacity

### 8.4 Payer + public health paydaşları
- AMR long-term systemic risk vs short-term budget
- Antimicrobial subscription model evaluation
- Vaccine ACIP-driven mandatory coverage (US)
- HCV elimination programs

### 8.5 Klinisyen paydaşları
- ID specialist vs non-ID prescriber dynamics
- Stewardship program integration
- Rapid diagnostic workflow
- Outpatient parenteral antimicrobial therapy (OPAT)

### 8.6 Global health paydaşları
- Gavi + Global Fund + Unitaid procurement
- WHO Model List of Essential Medicines inclusion
- Generic/biosimilar access arrangements
- Voluntary licensing (MPP Medicines Patent Pool)

---

## §9. Confidence Stamping for ID Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (SVR12, clinical cure rate, VE%) | **High** (peer-reviewed) |
| QIDP designation + exclusivity arithmetic | **High** (FDA public) |
| Real-world resistance rate | **Medium** (surveillance varies) |
| BARDA contract value | **Medium** (some public, some redacted) |
| Novel antibiotic commercial sales | **Medium** (sponsor IR + IQVIA) |
| Gavi/Global Fund negotiated pricing | **Medium** (some public) |
| Future pandemic scenario | **Low** |
| Confidential advance purchase commitments | Should not be claimed |
| Türkiye SGK SUT enfeksiyon kodları | **High** (SUT tablo primary) |

---

## §10. Forbidden Patterns

- ❌ Treating antimicrobial market as standard volume-maximization (stewardship fundamentally alters commercial economics)
- ❌ Generalizing COVID mRNA vaccine commercial trajectory to other infectious disease vaccines
- ❌ Conflating HCV cure-era pricing with ongoing HIV suppression pricing
- ❌ Assuming QIDP designation guarantees commercial success (Achaogen + Melinta + Tetraphase precedents)
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Overstating pandemic preparedness commercial value post-COVID normalization
- ❌ Ignoring antimicrobial resistance clock when projecting long-term antibiotic revenue

---

## §11. Versioning & Changelog

- **v4.0.0 (2026-04-16):** Initial release. Layer 2 Infectious Disease TA template covering: AMR framework with WHO 2024 priority pathogen list (critical CRAB/CR Pseudomonas/CR Enterobacterales/rifampicin-R Mtb; high Salmonella Typhi/Shigella/VRE faecium/MRSA/resistant Neisseria gonorrhoeae; medium S. pneumoniae/H. influenzae); ID endpoint frameworks (clinical cure + microbiological cure bacterial; HIV RNA <50 + CD4; SVR12 HCV; HBsAg seroconversion HBV; time-to-symptom-resolution influenza/RSV/COVID; sputum culture conversion + relapse-free TB; global response invasive fungal; case reduction vaccine); FDA regulatory pathway disciplines (GAIN Act 2012 + QIDP designation 5-year exclusivity extension + Priority Review + Fast Track with NCE/Orphan/Clinical 3-yr stacking, qualifying pathogens 21 CFR 317.2 final rule 2014-06, 147 QIDP designations 2012-2017 + 25 antimicrobial approvals 2012-2022 + 20 QIDP-designated; QIDP NOT available for biologics/vaccines and antivirals/antiparasitics excluded; LPAD 21st Century Cures Act 2016 with Arikayce MAC 2018 first + Fetroja + Recarbrio + Xenleta utilization; Tropical Disease PRV §524 + Material Threat MCM PRV §565A + RPD PRV §529 overlapping incentives; BARDA + Project BioShield 2004 with COVID Operation Warp Speed $18B+ mRNA platform transformation + post-pandemic boom-bust normalization); major sub-landscapes (HIV Gilead Biktarvy ~$14B+ dominant + INSTI backbone paradigm + Apretude first LA-injectable PrEP + Sunlenca lenacapavir FDA 2022 HIV-1 treatment-experienced + PURPOSE-1 Phase 3 100% PrEP efficacy Q6M SC readout 2024 + Cabenuva LA treatment; HCV cure era Sovaldi 2013 Gilead Pharmasset $11B acquisition $28B peak 2015 + Harvoni + Epclusa pan-genotypic + Mavyret AbbVie 8-week + Vosevi retreatment + SVR12 >95% collapsing market to ~$4-5B vs $22B peak; COVID-19 Paxlovid Pfizer $27B FY2022 peak + Lagevrio Merck + Veklury Gilead IV + mAbs obsolete via variants; antibacterial Dalvance + Sivextro QIDP + Avycaz + Vabomere + Xerava + Zemdri Achaogen bankrupt + Nuzyra Paratek + Recarbrio + Fetroja Shionogi CR-pathogens + Zerbaxa + Exblifep 2024 + Orlynvah 2024 oral uUTI + commercial reality Achaogen/Melinta/Tetraphase bankruptcies despite QIDP; antifungal Cresemba + Noxafil + Brexafemme first-in-class glucan synthase + Rezzayo LA echinocandin 2023 + olorofim Phase 3 + Candida auris urgency; TB Sirturo bedaquiline Janssen 2012 first novel in 40yr + Pretomanid TB Alliance 2019 BPaL regimen XDR-TB; antiviral Prevymis letermovir CMV + Livtencity maribavir refractory CMV + Arexvy GSK first RSV ≥60 2023 + Abrysvo Pfizer RSV adult+maternal 2023 + mRESVIA Moderna first mRNA RSV 2024 + Beyfortus nirsevimab infant RSV prophylaxis mAb 2023); vaccine landscape (ACIP pediatric + adult schedules + Shingrix + Prevnar class + Gardasil 9 + mRNA COVID/RSV); pandemic preparedness (COVID mRNA 11-month sequence-to-EUA + Operation Warp Speed + SNS + BioShield + Ervebo/Zabdeno Ebola + Jynneos mpox + TPOXX tecovirimat 2022 mpox outbreak 2024 clade I); AMR stewardship commercial tension (Joint Commission ASP 2017 + CMS CoP + subscription/pull incentives UK NHS dalbavancin 2022+ + RDT/NAAT/phenotypic AST/procalcitonin infrastructure); Türkiye ekosistemi (TİTCK EMA/FDA reliance + SGK SUT EK-4/G + HIV SUT EK-4C + HCV yerli jenerik + yerli antimikrobiyal Deva/Abdi İbrahim/Bilim/Sanovel + TURKOVAC COVID aşısı Erciyes + TÜSEB + AMR yüksek prevalans + SAGEM izlem). New manifest gate G46. Cross-references task-modality-rna.md (mRNA vaccines Comirnaty/Spikevax/mRESVIA + Arexvy mRNA candidates), task-modality-smallmol.md (DAA HCV + oral antivirals), task-modality-biosimilar.md (vaccine conjugate biosimilarity), task-ta-rare-disease.md (PRV §529 overlap), task-ta-pediatric.md (vaccine pediatric coverage + nirsevimab).
