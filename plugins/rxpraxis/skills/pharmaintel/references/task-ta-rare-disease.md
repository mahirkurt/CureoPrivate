# task-ta-rare-disease.md

**T3 Therapeutic Area Template — Rare Disease / Orphan Indications (v3.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality + Layer 0 generic. Rare disease TA spans many modalities (gene therapy Casgevy/Zolgensma/Elevidys, RNA therapy Spinraza/Onpattro, enzyme replacement, small molecule).

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "rare disease", "orphan drug", "nadir hastalık", "orphan indication", "ultra-rare", "ultra-orphan", "orphan designation", "ODD"
- Disease categories: "inherited metabolic disease", "IMD", "lysosomal storage disease", "LSD", "hemoglobinopathy", "hemophilia A", "hemophilia B", "sickle cell disease", "SCD", "transfusion-dependent β-thalassemia", "TDT", "muscular dystrophy", "Duchenne", "DMD", "SMA", "Pompe disease", "Fabry disease", "Gaucher disease", "MPS", "Batten disease", "hereditary angioedema", "HAE", "hereditary ATTR amyloidosis", "hATTR", "ATTR-CM", "primary hyperoxaluria", "PH1", "acute hepatic porphyria", "AHP", "cystic fibrosis", "CF", "pulmonary arterial hypertension", "PAH", "idiopathic pulmonary fibrosis", "IPF", "amyotrophic lateral sclerosis", "ALS"
- Framework terms: "pediatric rare disease", "rare pediatric disease voucher", "RPD PRV", "priority review voucher", "ultra-rare exclusivity", "compassionate use", "expanded access", "right-to-try", "conditional marketing authorization"

### 1.2 Implicit triggers
- Gene therapy / gene editing landscape (most are rare disease)
- Enzyme replacement therapy portfolio
- Novel pathway disease biology (small molecule targeted mechanisms)

### 1.3 NOT triggered by
- ❌ Sponsor rare disease portfolio affiliation (Vertex, BioMarin, Sarepta, Alnylam, Ultragenyx, Ionis, etc.)
- ❌ User memory-derived rare disease interest

---

## §2. Rare Disease Definition + Epidemiology

### 2.1 Regional rare disease thresholds

| Jurisdiction | Threshold | Reference population |
|---|---|---|
| **US (Orphan Drug Act 1983)** | <200,000 patients in US | Fixed threshold |
| **EU (Orphan Regulation 141/2000)** | <5 per 10,000 population | Prevalence-based |
| **Japan (Orphan Drug Act 1993)** | <50,000 patients in Japan | Fixed threshold |
| **Türkiye** | EMA orphan designation recognized; no separate TİTCK definition |

**Ultra-rare:** informal category <1 in 50,000 prevalence or <1,000-10,000 US patients.

### 2.2 Prevalence hierarchy examples

| Disease | Approximate US prevalence |
|---|---|
| **Cystic fibrosis** | ~30,000 |
| **Sickle cell disease** | ~100,000 |
| **PAH** | ~30,000 |
| **Hemophilia A** | ~20,000 |
| **Hemophilia B** | ~5,000 |
| **SMA (all types)** | ~10,000-25,000 |
| **DMD** | ~15,000 |
| **hATTR** | ~10,000 |
| **Pompe (LOPD)** | ~5,000-10,000 |
| **MPS type II (Hunter)** | ~500 (male only) |
| **MPS type I (Hurler)** | ~500 |
| **PKU** | ~30,000 |
| **Batten disease (NCL)** | few hundred |

---

## §3. Regulatory Pathway — Rare Disease Spesifik

### 3.1 Orphan Drug Designation (ODD)

**FDA Orphan Drug Act 1983:**
- 7-year market exclusivity (same molecule, same indication)
- Tax credits for clinical trial expenses
- FDA fee waivers
- Eligible for Rare Pediatric Disease Priority Review Voucher (if pediatric)

**EMA Orphan Regulation (EC) No 141/2000:**
- 10-year market exclusivity
- Scientific advice fee reductions
- Direct centralized authorization

### 3.2 Rare Pediatric Disease (RPD) Priority Review Voucher

Per FDA Safety and Innovation Act 2012:
- Sponsor of rare pediatric disease drug approval receives voucher
- Voucher redeemable for 6-month priority review on subsequent (any) NDA/BLA
- **Voucher market value:** $50-500M historically; secondary market transactions reported
- RPD PRV program had sunset extensions; status requires periodic verification per IRA updates

### 3.3 Accelerated Approval + Surrogate Endpoints

Rare disease frequently uses FDA accelerated approval based on surrogate endpoints:
- Serum transthyretin reduction for hATTR (Vyndamax, vutrisiran)
- Dystrophin expression for DMD (Exondys 51, Vyondys 53, Amondys 45, Elevidys)
- HbF induction for sickle cell disease (voxelotor, Casgevy, Lyfgenia)
- Glucosylceramide reduction for Gaucher

**Confirmatory trial requirement** post-AA; FDA increasingly willing to withdraw if confirmatory fails (withdrawn oncology precedents).

### 3.4 Expedited development pathways

Rare disease uses all expedited pathways heavily:
- **Breakthrough Therapy** designation
- **Fast Track**
- **Priority Review**
- **Regenerative Medicine Advanced Therapy (RMAT)** — gene/cell therapy
- **PRIME** — EU equivalent of Breakthrough

### 3.5 Small N clinical trials

Rare disease N often <100 for pivotal:
- Single-arm trials common
- Natural history comparators acceptable in some settings
- Master protocols + platform trials (CDISC master protocols)
- External control arms from registries
- Bayesian adaptive designs

### 3.6 FDA Rare Disease team engagement

FDA Office of Rare Diseases in CBER + dedicated OCE / CDER divisions; proactive sponsor engagement for pre-IND + milestone discussions. Patient advocacy group input increasingly formalized through patient-focused drug development (PFDD) meetings.

---

## §4. Modality Distribution in Rare Disease

Rare disease portfolio spans many modalities — high density of advanced therapies:

### 4.1 Gene therapy (one-shot curative)

Cross-reference `task-modality-cellgene.md`:
- Luxturna (RPE65-mediated IRD)
- Zolgensma (SMA)
- Hemgenix (hemophilia B)
- Roctavian (hemophilia A)
- Elevidys (DMD)
- Casgevy (SCD + TDT) — first CRISPR gene editing therapy
- Lyfgenia (SCD)
- Skysona (CALD)
- Beqvez (hemophilia B, approved 2024 later withdrawn due to commercial challenges — Pfizer)

### 4.2 RNA therapeutics

Cross-reference `task-modality-rna.md`:
- **ASO:** Spinraza (SMA intrathecal), Tofersen (SOD1-ALS), Kynamro (HoFH withdrawn), Exondys 51 + Vyondys 53 + Amondys 45 (DMD — controversial accelerated approvals)
- **siRNA:** Onpattro (hATTR), Amvuttra (hATTR + ATTR-CM), Givlaari (AHP), Oxlumo (PH1)

### 4.3 Enzyme replacement therapy (ERT)

| Disease | Enzyme | Product |
|---|---|---|
| Gaucher type 1 | Glucocerebrosidase | Cerezyme, VPRIV, Elelyso |
| Pompe (LOPD) | Acid α-glucosidase | Myozyme, Lumizyme, Nexviazyme (AAT-spesifik) |
| Fabry | α-galactosidase A | Fabrazyme, Replagal, Elfabrio |
| MPS type I | α-L-iduronidase | Aldurazyme |
| MPS type II | Iduronate sulfatase | Elaprase |
| MPS type IVA | N-acetylgalactosamine 6-sulfatase | Vimizim |
| Hypophosphatasia | Alkaline phosphatase | Strensiq |

### 4.4 Chaperone therapy

- Galafold (migalastat) — Fabry disease (responsive GLA mutations)
- Kalydeco / Orkambi / Symdeko / Trikafta — CFTR modulators for cystic fibrosis

### 4.5 Small molecule targeted (rare disease)

- Vyndamax / Vyndaqel (tafamidis) — hATTR-CM stabilizer
- Lumakras (sotorasib), Krazati (adagrasib) — KRAS G12C solid tumors (rare subsets)
- Bonus: enzyme inhibitors (e.g. Uplizna for NMOSD B cell depleting)

### 4.6 Factor concentrates + engineered proteins

Cross-reference `task-modality-fusion.md`:
- Factor VIII / IX conventional recombinant
- Long-acting Fc-fusions (Eloctate, Alprolix)
- PEGylated (Adynovate, Jivi)
- Subcutaneous prophylactic emicizumab (Hemlibra) — hemophilia A bispecific

---

## §5. Commercial + Access Dynamics

### 5.1 Ultra-high pricing

Rare disease pricing spans widest range in pharma:
- **Gene therapies:** $850K (Luxturna single eye) → $3.5M (Hemgenix)
- **ERT annual cost:** $200K-$500K+ per year lifetime
- **Small molecule (e.g. Trikafta, tafamidis):** $200K-$400K annually
- **Ultra-orphan:** some exceed $1M annually for lifetime therapy

### 5.2 Payer mechanisms

- **Outcomes-based contracting** — increasingly common for one-shot gene therapies
- **Annuity-based payments** — amortizing $1-3M upfront over multiple years
- **Orkambi precedent (NICE UK)** — multi-year patient access schemes
- **Rare disease fund** (Germany) — dedicated rare disease reimbursement carve-out
- **Medicare / Medicaid carve-outs** — state Medicaid variation significant for rare pediatric

### 5.3 Small patient populations drive commercial realities

- High per-patient revenue enables orphan viability with N=500-5000 patients globally
- Commercial team sizes much smaller than mass-market pharma
- Patient identification + referral networks critical (center-of-excellence model)
- Natural history registries often sponsor-funded (FDA partnership expectation)

### 5.4 Global market sequence

Rare disease launch sequence often follows:
1. US (largest pharma market, Orphan Drug Act incentives)
2. EU (centralized authorization)
3. Japan (Sakigake potential, Orphan Drug Act 1993)
4. Canada, Australia, Switzerland (high-income small markets)
5. Brazil, Middle East, larger emerging markets with expanded access programs
6. Türkiye — çoğu rare disease ilacı TİTCK üzerinden EMA reliance + SGK yurt dışı ilaç dairesi üzerinden ithal (uzun süreç)

---

## §6. Türkiye Rare Disease Market

### 6.1 Regulatory + access framework
- **TİTCK onay** — EMA reliance pathway rare disease ilaçları için standart
- **EMA orphan designation** — TİTCK tarafından tanınır
- **SGK geri ödeme** — SUT EK-4D rare disease ilaçları için çoğunlukla özel onay mekanizmaları; yurt dışı ilaç dairesi üzerinden ithal yaygın
- **Kompasyonlu kullanım (compassionate use)** — TİTCK özel onay gerekli; onaylı endikasyon dışı kullanım için

### 6.2 Tertiary merkez + konsey yapısı
- Rare disease hasta yönetimi: Hacettepe Üni., İstanbul Üni. Çapa, Ankara Üni., Dokuz Eylül, Ege Üni. gibi referans merkezler
- Pediatrik nadir hastalıklar: metabolik hastalıklar bölümleri aktif (PKU, Gaucher, Pompe)
- Hemoglobinopati: Akdeniz (Antalya), Çukurova (Adana), Doğu Anadolu çoklu merkez

### 6.3 Türkiye rare disease yük
- **Hemoglobinopati yüksek insidans** — β-thalassemia taşıyıcılık %2-6 bölgeye göre; SCD özellikle Doğu Akdeniz
- **Akraba evlilik oranı yüksek** — otozomal resesif hastalıklar için artmış risk (MPS, LSD, PKU)
- **Aile öyküsü yönetimi** + genetik danışmanlık altyapısı gelişmekte

---

## §7. Confidence Stamping for Rare Disease Claims

| Claim type | Confidence |
|---|---|
| FDA/EMA/PMDA approval + orphan status | **High** |
| Prevalence estimates | **Medium** (varies by source; NIH GARD vs Orphanet differ) |
| Pivotal trial efficacy (small N) | **Medium-High** (smaller statistical power than mass-market) |
| Real-world durability (one-shot gene therapy) | **Low-Medium** (immature follow-up for most products) |
| Net pricing after outcomes-based rebates | **Low** |
| Patient count globally | **Medium** (Orphanet + patient advocacy estimates) |

---

## §8. Forbidden Patterns

- ❌ Generalizing Casgevy gene therapy trajectory to all rare diseases
- ❌ Applying mass-market commercial benchmarks to <5,000-patient populations
- ❌ Treating accelerated approval surrogate endpoints as equivalent to clinical outcomes (particularly Sarepta DMD ASO controversy precedent)
- ❌ Strategic recommendations for specific rare disease sponsors without T6-Defense activation
- ❌ Speculating on confidential outcomes-based contract structures
- ❌ Conflating orphan designation with approval (designation is pre-approval; exclusivity conferred on approval)
- ❌ Ignoring natural history context for single-arm pivotal interpretation

---

## §9. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. Layer 2 Rare Disease TA template covering: regional orphan thresholds (US <200,000 per Orphan Drug Act 1983 / EU <5 per 10,000 per Regulation 141/2000 / Japan <50,000 per Orphan Drug Act 1993 / Türkiye EMA reliance), ultra-rare informal category + prevalence hierarchy examples (CF 30K / SCD 100K / hemophilia A 20K / SMA 10-25K / DMD 15K / hATTR 10K / MPS subtype hundreds), regulatory pathways (7-yr US exclusivity vs 10-yr EU + fee waivers + tax credits; RPD PRV $50-500M market value; accelerated approval with surrogate endpoints serum TTR for hATTR + dystrophin expression DMD + HbF induction SCD; small N trial design with single-arm + natural history + master protocols + external controls + Bayesian adaptive; FDA Office of Rare Diseases engagement with patient-focused drug development), modality distribution (gene therapy Luxturna-Zolgensma-Hemgenix-Roctavian-Elevidys-Casgevy-Lyfgenia-Skysona-Beqvez withdrawal; RNA therapeutics Spinraza + Tofersen + Exondys 51 + Onpattro + Amvuttra + Givlaari + Oxlumo; ERT for Gaucher/Pompe/Fabry/MPS/hypophosphatasia; chaperone + CFTR modulator Trikafta; small molecule targeted; factor concentrates + Hemlibra bispecific), commercial dynamics (ultra-high pricing $850K-$3.5M gene therapy + $200-500K annual ERT + outcomes-based contracting + annuity payments + rare disease fund Germany), Türkiye market (TİTCK EMA reliance + SGK yurt dışı ilaç dairesi + tertiary merkez konsey + hemoglobinopati yüksek insidans + akraba evlilik faktörü). New manifest gate G43. Cross-references task-modality-cellgene.md (gene therapies), task-modality-rna.md (ASO + siRNA rare disease), task-modality-fusion.md (factor Fc-fusions), analytics-framework.md (rare disease NPV with small-population sensitivity).
