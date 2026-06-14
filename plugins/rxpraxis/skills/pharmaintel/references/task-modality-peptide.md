# task-modality-peptide.md

**T3 Modality Template — Peptide Therapeutics (v2.6.0)**

> **Architectural context:** Niche modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when peptide therapeutic modality is in scope. Same layered template pattern as `task-modality-biosimilar.md` (v2.0.0 reference).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5. Peptide modality includes the GLP-1 / GIP class, GnRH analogs, somatostatin analogs, oxytocin analogs, parathyroid hormone analogs, and emerging multi-receptor agonists.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "peptide therapeutic", "therapeutic peptide", "peptit ilaç", "peptide drug", "polypeptide therapy"
- Class terms: "GLP-1", "GLP-1 receptor agonist", "GLP-1/GIP dual agonist", "incretin mimetic", "GnRH analog", "GnRH agonist", "GnRH antagonist", "somatostatin analog", "SSA", "PTH analog", "oxytocin analog"
- Asset names: "Ozempic", "Wegovy", "Rybelsus", "semaglutide", "Mounjaro", "Zepbound", "tirzepatide", "Trulicity", "dulaglutide" (note: Fc-fusion peptide), "Victoza", "liraglutide", "Saxenda", "Byetta", "Bydureon", "exenatide", "Lupron", "leuprolide", "Eligard", "Zoladex", "goserelin", "Trelstar", "triptorelin", "Firmagon", "degarelix", "Sandostatin", "Somatuline", "Signifor", "octreotide", "lanreotide", "pasireotide", "Forteo", "teriparatide", "Tymlos", "abaloparatide"
- Manufacturing / chemistry: "solid-phase peptide synthesis", "SPPS", "Fmoc chemistry", "fatty acid acylation", "albumin binding", "lipidation peptide", "PEGylation peptide"

### 1.2 Implicit semantic triggers
- Type 2 diabetes treatment landscape (incretin class concentration)
- Obesity pharmacotherapy landscape (GLP-1 + GLP-1/GIP)
- Prostate cancer ADT landscape (GnRH analog dominance)
- NET / acromegaly treatment (somatostatin analog territory)
- Osteoporosis anabolic therapy (PTH analog)

### 1.3 NOT triggered by
- ❌ User employer being a peptide developer (Novo Nordisk, Eli Lilly, AbbVie, Ipsen, Recordati Rare Diseases, Amgen, Radius Health/Paratek)
- ❌ Memory-derived endocrinology / oncology specialty interest
- ❌ Memory-derived obesity / diabetes therapeutic area focus

---

## §2. Foundational Conceptual Framework

### 2.1 Peptide vs small molecule vs biologic positioning

| Dimension | Small molecule | **Peptide** | mAb biologic |
|---|---|---|---|
| **Molecular size** | <1 kDa | 0.5-10 kDa typical | ~150 kDa |
| **Synthesis** | Chemical (multi-step) | Solid-phase chemical synthesis (Fmoc / Boc) OR recombinant expression | Mammalian cell culture |
| **Oral bioavailability** | Often high | Generally poor (<1% native peptide) — formulation enables some oral peptides (Rybelsus precedent) | Negligible — IV/SC required |
| **Plasma half-life (native)** | Hours-days | Minutes-hours typical | Days-weeks |
| **Half-life extension** | Less commonly engineered | Fatty acid acylation, PEGylation, Fc-fusion, albumin-binding domain | Native or via Fc engineering |
| **Regulatory pathway** | NDA (FDA) / Article 8 (EMA) | NDA (chemically synthesized) OR BLA (recombinant) | BLA / EMA biologic |
| **Generic / follow-on pathway** | ANDA (Hatch-Waxman) | ANDA possible for chemically synthesized; biosimilar pathway for recombinant | 351(k) biosimilar |

**Key regulatory nuance:** Peptide regulatory classification depends on production method, NOT molecular structure:
- **Chemically synthesized peptides** (≤40 amino acids, FDA threshold) → drug pathway (NDA + ANDA)
- **Recombinant peptides** (or chemically synthesized >40 aa) → biologic pathway (BLA + 351(k))

### 2.2 Half-life extension strategies (the defining innovation)

Native peptides have short half-lives (GLP-1 native t½ ~2 minutes; degraded by DPP-4 enzyme). Modern peptide engineering achieves clinically meaningful pharmacokinetics through:

| Strategy | Mechanism | Examples |
|---|---|---|
| **Fatty acid acylation + albumin binding** | C16/C18 fatty acid attached → reversible binding to serum albumin → protected from clearance | Liraglutide (palmitic acid), semaglutide (octadecanedioic acid via spacer), tirzepatide (C20 fatty diacid) |
| **PEGylation** | Polyethylene glycol attached → increases hydrodynamic radius → reduced renal clearance | Lonapegsomatropin, peginesatide (former) |
| **Fc fusion** | Peptide fused to IgG Fc domain → FcRn-mediated recycling | Dulaglutide (GLP-1 Fc-fusion, weekly), efpeglenatide (former Sanofi) |
| **D-amino acid substitution** | D-isomer residues → resistant to peptidases | Cetrorelix, ganirelix |
| **Cyclic / constrained peptides** | Cyclization → conformational stability + protease resistance | Octreotide (cyclic somatostatin analog) |
| **Backbone modification** | N-methylation, peptide bond replacement → enhanced stability | Various preclinical |

### 2.3 The GLP-1 class — defining contemporary peptide success

GLP-1 receptor agonist class evolution illustrates peptide therapeutic platform maturity:

| Generation | Asset | Half-life | Dosing | Sponsor |
|---|---|---|---|---|
| **1st gen (BID-QD)** | Exenatide (Byetta) | ~2.4 hr | BID injection | AstraZeneca |
| | Liraglutide (Victoza, Saxenda) | ~13 hr | QD injection | Novo Nordisk |
| **2nd gen (weekly)** | Exenatide ER (Bydureon) | weeks (microsphere depot) | Weekly | AstraZeneca |
| | Dulaglutide (Trulicity) | ~5 days | Weekly | Eli Lilly |
| | Albiglutide (Tanzeum, withdrawn) | ~5 days | Weekly | GSK |
| | Semaglutide SC (Ozempic, Wegovy) | ~7 days | Weekly | Novo Nordisk |
| **3rd gen (oral)** | Semaglutide oral (Rybelsus) | ~7 days | Daily oral | Novo Nordisk |
| **4th gen (multi-receptor)** | Tirzepatide (Mounjaro, Zepbound) GLP-1/GIP dual | ~5 days | Weekly | Eli Lilly |
| **5th gen (emerging)** | Retatrutide (GLP-1/GIP/glucagon) | weekly | Weekly (Phase 3) | Eli Lilly |
| | CagriSema (cagrilintide + semaglutide) | weekly | Weekly (Phase 3) | Novo Nordisk |
| | Survodutide (GLP-1/glucagon) | weekly | Weekly (Phase 2/3) | Boehringer Ingelheim |

---

## §3. Approved Peptide Therapeutic Landscape by Class

### 3.1 GLP-1 / incretin class (largest peptide market by revenue)

Beyond GLP-1RA's listed in §2.3:
- **Pramlintide (Symlin)** — amylin analog; T1D + T2D adjunct
- **Cagrilintide** — long-acting amylin analog (combination product CagriSema in Phase 3)

### 3.2 GnRH analog class (oncology + reproductive medicine)

**GnRH agonists (continuous suppression after initial flare):**
- Leuprolide (Lupron Depot, Eligard)
- Goserelin (Zoladex)
- Triptorelin (Trelstar)
- Histrelin (Vantas, Supprelin LA)
- Nafarelin (Synarel)

**GnRH antagonists (immediate suppression, no flare):**
- Degarelix (Firmagon) — injectable
- Relugolix (Orgovyx, Myfembree, Ryeqo) — oral small molecule (not peptide; included for class context)
- Cetrorelix (Cetrotide), Ganirelix (Antagon) — IVF cycles

**Indications:**
- Prostate cancer (androgen deprivation therapy)
- Endometriosis, uterine fibroids (Lupron, Zoladex)
- Central precocious puberty (Lupron, Supprelin LA, Triptodur)
- IVF protocol controlled ovarian stimulation

### 3.3 Somatostatin analog class

| Asset | INN | Sponsor | Indication |
|---|---|---|---|
| **Sandostatin LAR** | Octreotide | Novartis | Acromegaly, NET symptom control |
| **Somatuline Depot / Autogel** | Lanreotide | Ipsen | Acromegaly, GEP-NET (CLARINET) |
| **Signifor / Signifor LAR** | Pasireotide | Recordati Rare Diseases | Cushing's disease, acromegaly |
| **Mycapssa** | Octreotide oral | Chiesi (acquired Amryt) | Acromegaly maintenance (oral SSA precedent) |

### 3.4 PTH analog class (osteoporosis anabolic)

| Asset | INN | Sponsor | Indication |
|---|---|---|---|
| **Forteo** | Teriparatide (PTH 1-34) | Eli Lilly | Postmenopausal osteoporosis high fracture risk |
| **Tymlos** | Abaloparatide (PTHrP analog) | Radius Health (now Paratek) | Postmenopausal osteoporosis |
| **Generic teriparatide** | Multiple ANDA + biosimilar (jurisdictional) | Pfizer (Bonsity), Teva, others | Same as Forteo |

### 3.5 Other notable peptide classes

| Class | Examples |
|---|---|
| **Calcitonin** | Miacalcin (salmon calcitonin) |
| **Insulin analogs** | Glargine (Lantus, Basaglar, Semglee biosimilar), aspart (NovoLog), lispro (Humalog), degludec (Tresiba), detemir (Levemir) |
| **Oxytocin analogs** | Carbetocin (Pabal — uterotonic post-partum) |
| **Vasopressin analogs** | Desmopressin (DDAVP) |
| **ANP / BNP analogs** | Nesiritide (Natrecor — withdrawn 2018) |
| **Glucagon** | Native + Baqsimi (nasal), Gvoke (autoinjector) |
| **Conotoxin-derived** | Ziconotide (Prialt — intrathecal pain) |
| **Other receptor agonists** | Linaclotide (Linzess — guanylate cyclase-C; constipation), Plecanatide (Trulance) |

---

## §4. Manufacturing — SPPS + Recombinant Pathways

### 4.1 Solid-phase peptide synthesis (SPPS)

**Fmoc (9-fluorenylmethyloxycarbonyl) chemistry** dominates contemporary peptide manufacturing:
- Resin-bound C-terminal amino acid → iterative deprotection + coupling cycles → cleavage
- Each cycle ~95-99% efficiency → length-dependent yield drop
- Practical synthesis ceiling ~50-100 amino acids without convergent strategies
- Native chemical ligation (NCL) extends to longer peptides via fragment coupling

**Major SPPS CMOs:**
- Bachem (Switzerland) — largest specialty peptide manufacturer
- PolyPeptide Group (Sweden + multi-site)
- Lonza (Switzerland + multi-site)
- CordenPharma (Italy + multi-site)
- Ajinomoto Bio-Pharma
- Chinese players (Hybio, ChinaPeptides)

### 4.2 Recombinant peptide expression

Larger peptides + complex post-translational modifications often produced recombinantly:
- E. coli expression — most common bacterial host
- Yeast (S. cerevisiae, P. pastoris) — secretory pathway, some PTMs
- Mammalian cell culture — reserved for complex glycosylated peptides

### 4.3 GLP-1 manufacturing capacity as commercial constraint

The **GLP-1 supply crisis (2022-2024)** for semaglutide (Ozempic, Wegovy) + tirzepatide (Mounjaro, Zepbound) demonstrated that peptide manufacturing capacity is a commercial bottleneck:
- Novo Nordisk + Eli Lilly invested >$10B in capacity expansion
- Compounded "GLP-1" preparations from compounding pharmacies emerged in supply gap (FDA shortage list status)
- Specialty peptide CMO capacity limited globally

### 4.4 Fatty acid acylation manufacturing

Modern long-acting GLP-1s require precise fatty acid attachment:
- Side-chain conjugation to lysine residue (semaglutide K26)
- Spacer chemistry (γ-glutamic acid linker for semaglutide)
- IP-protected manufacturing techniques (Novo Nordisk semaglutide acylation)

---

## §5. Regulatory Pathway

### 5.1 FDA framework — chemically synthesized vs recombinant

Per FDA classification:
- **Chemically synthesized peptides ≤40 amino acids** → NDA pathway (drug)
- **Recombinant peptides OR chemically synthesized >40 aa** → BLA pathway (biologic)

This is a **bright-line regulatory distinction** with profound implications:
- Generic pathway: ANDA (drug) vs 351(k) biosimilar (biologic)
- Reference product exclusivity: 5-yr NCE (drug) vs 12-yr (BPCIA)
- Substitution: AB-rated automatic (drug) vs interchangeability designation required (biologic)

### 5.2 Generic peptide ANDA challenges

FDA has issued multiple **product-spesifik bioequivalence guidances** for chemically synthesized peptide generics demonstrating:
- Generic glatiramer acetate (Copaxone) — landmark ANDA approval 2015 (Mylan)
- Generic enfuvirtide, leuprolide, octreotide, calcitonin, teriparatide, liraglutide

For complex peptides, demonstrating "sameness" requires:
- Primary structure identity (peptide mapping)
- Higher-order structure analysis
- Biological activity assays (receptor binding, in vitro potency)
- PK bioequivalence

### 5.3 EMA + other jurisdictions

- **EMA** — similar chemical/recombinant distinction; biosimilar pathway available for recombinant peptides via Article 10(4)
- **PMDA** — established peptide framework; teriparatide biosimilar approved
- **NMPA** — major Chinese GLP-1 + insulin biosimilar developer ecosystem
- **TİTCK** — EMA reliance pathway dominant; jeneriks önemli ölçüde mevcut (octreotide, leuprolide, goserelin, teriparatide)

---

## §6. Class-Spesifik Disciplines

### 6.1 GLP-1 / GIP class effects

**Common GLP-1 RA adverse events:**
- Nausea, vomiting (titrate dose to mitigate)
- Diarrhea
- Injection site reactions
- Acute kidney injury (volume depletion-mediated)
- Pancreatitis (uncertain causal link, FDA labeling caution)
- Gallbladder events (cholelithiasis, cholecystitis — modest signal)
- Thyroid C-cell tumor signal (rodent finding; boxed warning for liraglutide, dulaglutide, semaglutide; clinical relevance debated)
- Diabetic retinopathy worsening signal (semaglutide SUSTAIN-6 secondary finding)

**GLP-1/GIP dual agonist (tirzepatide) class effects:** Similar GI profile; appears more potent for weight loss + glycemic control.

### 6.2 GnRH analog class effects

**GnRH agonists — testosterone flare:**
- Initial paradoxical surge in LH/FSH → testosterone surge → potential tumor flare in metastatic prostate cancer
- Mitigation: anti-androgen pre-treatment for ~14 days
- GnRH antagonists avoid flare (immediate suppression mechanism)

**Class effects across GnRH analogs:**
- Hot flashes
- Decreased libido, erectile dysfunction
- Bone mineral density loss (long-term)
- Cardiovascular events (debated; HERO trial relugolix vs leuprolide CV signal)

### 6.3 Somatostatin analog class effects
- Gallbladder dysfunction (cholelithiasis common with chronic use)
- Hyperglycemia (pasireotide particularly — GLP-1/insulin suppression)
- Steatorrhea / GI symptoms
- Bradycardia, conduction abnormalities

### 6.4 PTH analog class effects
- Osteosarcoma signal (rat carcinogenicity finding) — boxed warning until 2020 removal for teriparatide
- Hypercalcemia
- Orthostatic hypotension

---

## §7. Commercial Trajectory Patterns

### 7.1 GLP-1 class — fastest-growing pharma category in history

**FY2024 sales (~):**
- Ozempic + Wegovy + Rybelsus (Novo Nordisk semaglutide franchise) — ~$30B+ combined
- Mounjaro + Zepbound (Eli Lilly tirzepatide) — ~$15B+ combined
- Trulicity (Eli Lilly dulaglutide) — ~$6B (peak; declining as patients shift to tirzepatide)
- Victoza + Saxenda (Novo Nordisk liraglutide) — ~$2B (declining; LOE proximity)

**Key dynamics:**
- Demand >> supply (continued shortages 2023-2025)
- Capacity expansion gating commercial growth
- Compounded GLP-1 controversy (US compounding pharmacy expanded production during FDA shortage; FDA enforcement actions late 2024)
- Pricing power exceptional ($1,300-2,000/month US WAC for Wegovy/Zepbound)

### 7.2 GnRH analog landscape — mature commodity + premium long-acting

- Leuprolide depot formulations (3-month, 6-month, annual) from Lupron + Eligard + generics
- Significant generic competition for short-acting formulations
- Premium price retention for newer formulations (annual implant, longer-acting depot)

### 7.3 Somatostatin analog landscape

Stable niche (~$2-3B global SSA market): Sandostatin LAR + Somatuline Depot dominant; Signifor for resistant Cushing's; Mycapssa as oral alternative.

### 7.4 PTH analog landscape

Stable niche: Forteo + Tymlos + generic teriparatide. Anabolic bone therapy increasingly displaced by sclerostin inhibitor (romosozumab/Evenity) for severe cases.

---

## §8. Pipeline Dynamics

### 8.1 Multi-receptor agonists (the next frontier)

| Asset | Receptors | Sponsor | Phase |
|---|---|---|---|
| **Retatrutide** | GLP-1 + GIP + glucagon | Eli Lilly | Phase 3 (TRIUMPH program) |
| **CagriSema** | GLP-1 + amylin | Novo Nordisk | Phase 3 |
| **Survodutide** | GLP-1 + glucagon | Boehringer Ingelheim | Phase 2/3 |
| **Pemvidutide** | GLP-1 + glucagon | Altimmune | Phase 2 |
| **Mazdutide** | GLP-1 + glucagon | Innovent + Eli Lilly | Phase 3 (China-led) |
| **Ecnoglutide** | GLP-1 (next-gen) | Sciwind Biosciences | Phase 3 (China) |

### 8.2 Oral peptide platform expansion

Rybelsus precedent (oral semaglutide via SNAC permeation enhancer — Eligen technology from Emisphere acquired 2020) is driving multiple oral peptide programs:
- Oral GLP-1 + multi-receptor agonists in development
- Oral PCSK9 inhibitors (peptide-based)
- Oral teriparatide / PTH analogs

### 8.3 Disease area expansion beyond T2D + obesity

GLP-1 class expanding into:
- **Cardiovascular outcomes** (SELECT, REWIND, LEADER established)
- **Heart failure with preserved EF** (STEP-HFpEF)
- **Sleep apnea** (SURMOUNT-OSA — tirzepatide approved Dec 2024)
- **Chronic kidney disease** (FLOW — semaglutide)
- **Alzheimer's disease** (EVOKE / EVOKE+ — semaglutide; results pending)
- **Substance use disorders** (alcohol, opioid — investigational)
- **Liver disease** (MASH/NASH — semaglutide ESSENCE)

### 8.4 New peptide classes

- **Apelin / elabela analogs** — heart failure
- **Amylin analogs** — obesity (cagrilintide pipeline)
- **Glucagon analogs** — congenital hyperinsulinism
- **NPY / PYY analogs** — appetite regulation (early stage)

---

## §9. Stakeholder-Spesifik Analytical Framework

### 9.1 GLP-1 dominant sponsors (Novo Nordisk + Eli Lilly)
- Manufacturing capacity expansion as commercial moat
- Indication expansion strategy (obesity → CV → CKD → liver → AD)
- Multi-receptor agonist pipeline differentiation
- Pricing power preservation under payer pressure

### 9.2 GLP-1 challenger sponsors
- Differentiation strategy (oral, monthly dosing, novel receptor targeting)
- Capacity-secured launch readiness
- Geographic launch sequencing

### 9.3 Generic peptide developer sponsors
- ANDA filing strategy for chemically synthesized peptides
- Bioequivalence demonstration burden
- AB-rating attainment (regulatory + clinical evidence)

### 9.4 Recombinant peptide biosimilar developer sponsors
- 351(k) BPCIA pathway (vs ANDA for chemically synthesized)
- Reference product exclusivity arithmetic
- Cross-reference with `task-modality-biosimilar.md` for biosimilar disciplines

### 9.5 Payer paydaşları
- GLP-1 obesity coverage policy debates
- Step therapy + prior authorization frameworks
- Outcomes-based contracting for chronic peptide therapy

### 9.6 Klinisyen + hasta paydaşları
- Injection device user experience (autoinjector, prefilled pen)
- Adherence patterns (weekly + monthly improving vs daily)
- Out-of-pocket cost burden for non-covered indications (cosmetic GLP-1 use)

### 9.7 Türk yerli peptit ekosistemi
- Türk yerli GLP-1 üretim kapasitesi gelişmemiş; çoğu peptit ürün Novo Nordisk + Eli Lilly + multinational originatörler ithalat
- Yerli üretim: insulin glargine biosimilar (Sanofi'nin Lantus orijinatörüne karşı), generic leuprolide + octreotide
- TİTCK + SGK SUT geri ödemesinde GLP-1 RA ürünleri T2D endikasyonunda mevcut; obezite endikasyonu için sınırlı erişim (özel ödeme dominant)

---

## §10. Confidence Stamping for Peptide Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy | **High** (peer-reviewed publication) |
| Half-life + receptor binding (publicly disclosed) | **High** (label + publication) |
| Manufacturing capacity (publicly disclosed) | **Medium** (sponsor IR varies) |
| Net pricing after PBM rebates | **Low** (confidential) |
| Real-world adherence | **Medium** (registry quality varies) |
| Compounded peptide quality | **Low** (variable, unregulated) |
| Forward-looking pipeline timing | **Medium** (sponsor guidance subject to slip) |
| Confidential acylation chemistry IP | Should not be claimed |

---

## §11. Forbidden Patterns

- ❌ Treating peptide therapeutic as automatically a "biologic" — chemically synthesized ≤40 aa peptides regulated as drugs (NDA + ANDA)
- ❌ Conflating "peptide" with "small molecule" — peptide engineering disciplines (acylation, PEGylation, Fc-fusion, cyclization) differ fundamentally
- ❌ Generalizing GLP-1 commercial trajectory to all peptide classes
- ❌ Strategic action recommendations for specific peptide sponsors without T6-Defense activation
- ❌ Speculation about confidential GLP-1 manufacturing capacity expansion or pricing strategy
- ❌ Recommending compounded GLP-1 preparations as therapeutic equivalents to FDA-approved versions

---

## §12. Versioning & Changelog

- **v2.6.0 (2026-04-15):** Initial release. Niche modality T3 sub-template covering: peptide vs small molecule vs biologic positioning + FDA chemically synthesized ≤40 aa drug pathway vs >40 aa or recombinant biologic pathway bright-line distinction, half-life extension strategies (fatty acid acylation + albumin binding for GLP-1 class with semaglutide K26 + γ-glutamic acid spacer + tirzepatide C20 fatty diacid; PEGylation; Fc fusion exemplified by dulaglutide; D-amino acid substitution; cyclization), GLP-1 class generation taxonomy (1st gen exenatide BID through 5th gen retatrutide GLP-1/GIP/glucagon triple agonist Phase 3) + GnRH agonist/antagonist class with prostate cancer ADT + IVF disciplines + somatostatin analog class (Sandostatin/Somatuline/Signifor/Mycapssa) + PTH analog (Forteo/Tymlos) + insulin/oxytocin/vasopressin/glucagon/conotoxin/guanylate cyclase peptide families, manufacturing (SPPS Fmoc chemistry with Bachem/PolyPeptide/Lonza/CordenPharma CMOs + recombinant expression + GLP-1 supply crisis 2022-2024 + acylation manufacturing), regulatory pathway (FDA chemically synthesized vs recombinant classification + ANDA generic peptide approvals Copaxone landmark 2015 Mylan + product-spesifik BE guidances + EMA Article 10(4) recombinant biosimilar pathway + PMDA + NMPA + Türkiye), class-spesifik effects (GLP-1 GI/pancreatitis/gallbladder/thyroid C-cell signal; GnRH agonist testosterone flare with anti-androgen pre-treatment; SSA gallbladder + pasireotide hyperglycemia; PTH osteosarcoma boxed warning history), commercial trajectory (GLP-1 fastest-growing pharma category in history with Novo Nordisk semaglutide franchise ~$30B+ + Eli Lilly tirzepatide ~$15B+ + capacity expansion >$10B + compounded GLP-1 controversy + exceptional pricing power), pipeline dynamics (multi-receptor agonist frontier — retatrutide GLP-1/GIP/glucagon + CagriSema GLP-1/amylin + survodutide + mazdutide; oral peptide platform via Rybelsus/SNAC precedent; disease area expansion CV/HFpEF/sleep apnea/CKD/AD/MASH/SUD), stakeholder framework (7 abstract categories including Türk yerli peptit ekosistemi). Compatible with all sub-protocols + companion to task-modality-biosimilar.md for recombinant peptide biosimilars. New manifest gate G31.
