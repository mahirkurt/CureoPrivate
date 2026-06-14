# task-modality-rna.md

**T3 Modality Template — RNA Therapeutics (mRNA / siRNA / ASO / miRNA / saRNA) (v2.5.0)**

> **Architectural context:** Modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when RNA-based modality is in scope.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "mRNA therapy", "mRNA vaccine", "siRNA", "small interfering RNA", "ASO", "antisense oligonucleotide", "antisens oligonükleotid", "RNAi", "RNA interference", "self-amplifying RNA", "saRNA", "circRNA", "miRNA mimic", "miRNA inhibitor", "RNA editing", "ADAR editing"
- Delivery system terms: "LNP", "lipid nanoparticle", "GalNAc", "GalNAc conjugate", "intrathecal ASO", "intravitreal RNA"
- Asset names: "Comirnaty", "Spikevax", "Patisiran", "Onpattro", "Givlaari", "Oxlumo", "Leqvio", "inclisiran", "Amvuttra", "vutrisiran", "Spinraza", "nusinersen", "Tegsedi", "inotersen", "Eteplirsen", "Exondys", "Trikafta", "Fomivirsen"

### 1.2 Implicit semantic triggers
- Liver-targeted gene silencing (GalNAc-siRNA territory)
- Rare neurologic disease (intrathecal ASO territory: SMA, ALS, Huntington)
- Cardiovascular cholesterol lowering (Leqvio/inclisiran territory)
- Rare metabolic disease (porphyria, hereditary ATTR, primary hyperoxaluria)
- Pandemic vaccine development (mRNA platform)

### 1.3 NOT triggered by
- ❌ User employer being an RNA-platform developer (Moderna, BioNTech, Alnylam, Ionis, Sarepta, etc.)
- ❌ Memory-derived COVID-19 vaccine interest

---

## §2. Foundational Conceptual Framework

### 2.1 RNA modality taxonomy

| Class | Mechanism | Approved examples |
|---|---|---|
| **mRNA** | Encodes a protein in patient cells | Comirnaty (BNT162b2), Spikevax (mRNA-1273) — both COVID-19 vaccines |
| **siRNA** | RISC-mediated mRNA cleavage; gene silencing | Onpattro (patisiran), Givlaari (givosiran), Oxlumo (lumasiran), Leqvio (inclisiran), Amvuttra (vutrisiran) |
| **ASO (Gapmer)** | RNase H-mediated mRNA degradation | Spinraza (nusinersen), Kynamro (mipomersen), Tegsedi (inotersen), Waylivra (volanesorsen) |
| **ASO (steric block / splice modulator)** | Splice-switching ASOs (SSO) | Eteplirsen (Exondys 51), Casimersen (Amondys 45), Golodirsen (Vyondys 53), Viltolarsen (Viltepso) |
| **miRNA mimic / inhibitor** | Modulates microRNA function | None approved (multiple in development) |
| **saRNA (self-amplifying)** | RNA replicon delivers + amplifies template | None approved (COVID-19 vaccines in development; Arcturus, GSK) |
| **circRNA** | Circular RNA for sustained protein expression | None approved (preclinical/early clinical) |
| **In vivo CRISPR mRNA** | mRNA-encoded Cas9 + guide RNA | None approved (Intellia NTLA-2001 ATTR-CM, NTLA-2002 HAE — Phase 1/2/3) |

### 2.2 Why RNA therapy ≠ small molecule and ≠ traditional protein biologic

RNA therapy occupies a unique modality niche:
- **Specificity:** Watson-Crick base pairing → exquisite target sequence specificity
- **Druggable target expansion:** Can address "undruggable" proteins by silencing the encoding mRNA
- **Manufacturing:** Chemical synthesis (synthetic oligonucleotide) vs cell culture (biologic)
- **Delivery challenge:** Nucleic acids face cellular uptake barriers — delivery technology is often the rate-limiting innovation
- **Half-life modulation:** Chemical modifications (2'-O-methyl, phosphorothioate, GalNAc) determine PK

---

## §3. Delivery Systems — The Defining Innovation

### 3.1 Lipid Nanoparticle (LNP)

**LNP** = ionizable lipid + cholesterol + PEG-lipid + helper lipid (DSPC). Encapsulates mRNA or siRNA payload.

**Use cases:**
- **mRNA vaccines** (Comirnaty, Spikevax) — IM injection, transient liver+muscle uptake, immune cell uptake
- **mRNA gene editing** (Intellia NTLA-2001) — IV systemic, hepatocyte-predominant
- **siRNA hepatic** (Onpattro/patisiran) — IV systemic, hepatocyte-predominant

**Notable LNP IP:**
- Acuitas Therapeutics (BNT162b2 license)
- Genevant (former Arbutus)
- Moderna proprietary LNPs
- Multiple ongoing patent disputes (Alnylam vs Moderna, Acuitas vs Pfizer/BioNTech)

### 3.2 GalNAc (N-acetylgalactosamine) conjugation

**Mechanism:** GalNAc tri-antennary ligand binds asialoglycoprotein receptor (ASGPR) on hepatocytes → receptor-mediated endocytosis → highly selective hepatic delivery.

**Use cases:**
- All Alnylam-approved siRNAs since Onpattro (Givlaari, Oxlumo, Leqvio, Amvuttra)
- Subcutaneous administration possible due to potency (vs IV LNP requirement)

**Half-life advantage:** Q3M or Q6M dosing achievable for chronic conditions (Leqvio Q6M for cardiovascular).

### 3.3 ASO chemistry — phosphorothioate + 2'-modifications

**Backbone modifications:**
- Phosphorothioate (PS) — protease resistance + protein binding
- 2'-O-methoxyethyl (MOE) — second-gen Ionis chemistry
- 2'-O-methyl (OMe) — common modification

**Delivery routes:**
- **Subcutaneous** — Tegsedi, Waylivra (systemic, hepatic predominance)
- **Intrathecal** — Spinraza, Tofersen, Tominersen (CNS access)
- **Intravitreal** — Fomivirsen (former; CMV retinitis)

### 3.4 Other emerging delivery systems
- **GalNAc-LNP combinations** — extending GalNAc to mRNA payloads
- **Receptor-targeted LNPs** — CD3 LNPs for in vivo CAR-T (research-stage)
- **Polymer nanoparticles** — alternative to LNPs
- **Conjugates beyond GalNAc** — antibody-RNA conjugates (ARCs), cell-penetrating peptides

---

## §4. Approved RNA Therapeutic Landscape

### 4.1 ASO landscape (oldest RNA modality with approved drugs)

| Asset | Sponsor | Indication | Approval |
|---|---|---|---|
| **Fomivirsen (Vitravene)** | Ionis | CMV retinitis | FDA 1998 (first ASO approval; later withdrawn — niche) |
| **Mipomersen (Kynamro)** | Ionis + Genzyme | HoFH | FDA 2013 (REMS, withdrawn 2018) |
| **Eteplirsen (Exondys 51)** | Sarepta | DMD exon 51 skipping | FDA 2016 (accelerated; controversial AdComm) |
| **Nusinersen (Spinraza)** | Biogen + Ionis | SMA (intrathecal) | FDA 2016 |
| **Inotersen (Tegsedi)** | Akcea/Ionis | hATTR polyneuropathy | FDA 2018 |
| **Golodirsen (Vyondys 53)** | Sarepta | DMD exon 53 skipping | FDA 2019 |
| **Viltolarsen (Viltepso)** | NS Pharma (Nippon Shinyaku) | DMD exon 53 skipping | FDA 2020 |
| **Casimersen (Amondys 45)** | Sarepta | DMD exon 45 skipping | FDA 2021 |
| **Tofersen (Qalsody)** | Biogen + Ionis | SOD1-ALS (intrathecal) | FDA 2023 (accelerated) |

### 4.2 siRNA landscape (Alnylam-dominated)

| Asset | Sponsor | Indication | Approval |
|---|---|---|---|
| **Patisiran (Onpattro)** | Alnylam | hATTR polyneuropathy | FDA 2018 (LNP delivery — first siRNA approval) |
| **Givosiran (Givlaari)** | Alnylam | Acute hepatic porphyria | FDA 2019 (GalNAc) |
| **Lumasiran (Oxlumo)** | Alnylam | Primary hyperoxaluria type 1 | FDA 2020 (GalNAc) |
| **Inclisiran (Leqvio)** | Novartis (acquired The Medicines Company) | Heterozygous familial hypercholesterolemia + ASCVD | FDA 2021 (GalNAc, Q6M dosing) |
| **Vutrisiran (Amvuttra)** | Alnylam | hATTR polyneuropathy + ATTR-CM | FDA 2022 (GalNAc, Q3M) |
| **Nedosiran (Rivfloza)** | Novo Nordisk | Primary hyperoxaluria type 1 | FDA 2023 |

### 4.3 mRNA vaccine landscape

| Asset | Sponsor | Indication | Approval |
|---|---|---|---|
| **Comirnaty (BNT162b2 / tozinameran)** | Pfizer + BioNTech | COVID-19 | FDA EUA Dec 2020 → BLA 125742 Aug 2021 |
| **Spikevax (mRNA-1273 / elasomeran)** | Moderna | COVID-19 | FDA EUA Dec 2020 → BLA 125752 Jan 2022 |
| **mRESVIA (mRNA-1345)** | Moderna | RSV (60+ years) | FDA 2024 |

mRNA cancer vaccines (Moderna mRNA-4157 + pembrolizumab in melanoma) and rare disease mRNA (Moderna mRNA-3704 propionic acidemia, mRNA-3927 methylmalonic acidemia) in late-stage clinical development.

### 4.4 Therapeutic mRNA — non-vaccine

No therapeutic mRNA (replacement protein) approved as of data cutoff. Multiple in development for inherited metabolic diseases, hemophilia, etc.

---

## §5. Class-Spesifik Disciplines

### 5.1 ASO class effects
- **Injection site reactions** (subcutaneous ASOs)
- **Thrombocytopenia** (PS-MOE chemistry can affect platelets — particularly Tegsedi, Waylivra)
- **Renal toxicity** (high-dose systemic ASOs)
- **Hepatotoxicity** (LFT elevations with some ASOs)

### 5.2 siRNA class effects
- **Injection site reactions** (subcutaneous GalNAc)
- **Liver enzyme elevations** (modest)
- **Hepatotoxicity rare** with current GalNAc generation
- **Anti-PEG antibodies** (LNP siRNAs) — clinical relevance debated

### 5.3 mRNA vaccine class effects
- **Reactogenicity** — fever, fatigue, headache, injection site pain (immunogenicity-driven, expected)
- **Myocarditis/pericarditis** — class-spesifik signal in young males (BNT162b2 + mRNA-1273), boxed warning consideration in some jurisdictions
- **Anaphylaxis** — rare; PEG-LNP component implicated

### 5.4 Off-target hybridization (ASO/siRNA)
Sequence-spesifik off-target effects: imperfect pairing with non-target mRNAs. Modern in silico screening + 3'UTR matching analysis mitigates but does not eliminate.

---

## §6. Regulatory Pathway

### 6.1 FDA framework

RNA therapeutics regulated based on classification:
- **mRNA vaccines** — CBER (vaccines + related biologics)
- **mRNA therapeutic protein replacement** — CBER (gene therapy classification typically)
- **siRNA + ASO** — CDER (chemically synthesized oligonucleotides classified as drugs)

This creates a unique cross-CBER/CDER coordination requirement for sponsor pipelines spanning multiple RNA modalities.

### 6.2 Accelerated approval discipline

Frequently used for ASO and siRNA in rare diseases:
- Surrogate endpoints (e.g. transthyretin reduction for ATTR; LDL-C reduction for hypercholesterolemia)
- Confirmatory trials post-approval
- Sarepta DMD ASOs (Eteplirsen, Vyondys 53, Amondys 45) are notable accelerated approval cases with controversial efficacy debate

### 6.3 Pandemic preparedness — mRNA platform implications

Post-COVID, FDA + EMA + WHO have developed **platform technology** considerations for mRNA vaccines: when a sponsor demonstrates platform comparability (e.g. across multiple mRNA vaccines using same LNP and similar manufacturing), abbreviated regulatory pathways may apply for new antigen targets.

### 6.4 EMA + PMDA + NMPA

- **EMA** — Standard centralized procedure; CHMP review
- **PMDA** — Standard review; Sakigake possible for breakthrough RNA therapies
- **NMPA** — Multiple Chinese-developed mRNA platforms (CanSino, Walvax, RNACure)
- **TİTCK** — EMA reliance pathway predominant

---

## §7. Manufacturing Considerations

### 7.1 Synthetic oligonucleotide manufacturing (siRNA, ASO)

Solid-phase synthesis on automated synthesizers:
- Phosphoramidite chemistry (3' to 5' coupling)
- Each base addition cycle ~95-99% efficiency → length-dependent yield
- Post-synthesis modifications (GalNAc conjugation, phosphorothioate oxidation)
- Purification (HPLC, anion exchange)

**CMO landscape:** Limited specialized capacity globally:
- Agilent (Boulder, CO)
- Avecia / Nitto Denko
- Ajinomoto Bio-Pharma
- Bachem
- Hongene Biotech (China)

### 7.2 mRNA manufacturing

In vitro transcription (IVT) + LNP encapsulation:
- Linear DNA template → T7 RNA polymerase → mRNA + capping (CleanCap or co-transcriptional)
- mRNA purification (oligo-dT, HPLC)
- LNP encapsulation via microfluidics
- Final vialing

**Capacity expansion post-COVID:**
- Pfizer/BioNTech: Marburg, Andover MA, multiple
- Moderna: Norwood MA, Lonza (Visp Switzerland), Resilience (Mississauga Canada)
- CureVac, Arcturus, Translate Bio expansions

### 7.3 LNP manufacturing IP barriers

LNP composition + process IP highly contested:
- Alnylam vs Moderna lawsuit (LNP composition patents, settled)
- Acuitas vs Pfizer/BioNTech (BNT162b2 LNP licensing)
- Patent landscape complexity drives some sponsors to develop proprietary alternatives

---

## §8. Commercial Trajectory Patterns

### 8.1 mRNA vaccines — pandemic-era unprecedented scale

| Asset | Peak revenue | Sponsor |
|---|---|---|
| Comirnaty | ~$37B (2022) → declining | Pfizer + BioNTech |
| Spikevax | ~$18B (2022) → declining | Moderna |

Post-pandemic decline reflects endemic vaccination patterns. mRNA platform commercial validation achieved at unprecedented scale.

### 8.2 siRNA — Alnylam franchise

Alnylam siRNA franchise approaching $2B+ FY2024:
- Onpattro declining as Amvuttra (next-gen) takes share
- Givlaari, Oxlumo growing in rare indications
- Leqvio (Novartis-marketed) cardiovascular potential blockbuster trajectory

### 8.3 ASO — Spinraza dominant

Spinraza historically peak-of-class ASO (~$1.5B at peak); SMA franchise pressure from Zolgensma + Risdiplam erosion.

### 8.4 Pricing patterns
- **Rare disease RNA therapeutics:** $300K-$700K annually
- **Cardiovascular siRNA (Leqvio):** ~$3,250/dose × 2/yr after loading
- **mRNA vaccines:** Pandemic pricing $20-30/dose contract → endemic $80-130/dose commercial

---

## §9. Pipeline Dynamics

### 9.1 RNA editing (ADAR-based)

Emerging modality: ADAR (adenosine deaminase acting on RNA) recruits to edit specific bases on mRNA. Avoids permanent DNA change.
- Wave Life Sciences AIMer platform
- Korro Bio
- ProQR Therapeutics

### 9.2 mRNA therapeutics expansion

Beyond vaccines:
- **Cancer vaccines** (Moderna mRNA-4157 + pembro melanoma — KEYNOTE-942 Phase 2 positive; Phase 3 ongoing)
- **Rare metabolic disease** (Moderna mRNA-3704, mRNA-3927)
- **Cystic fibrosis** (Vertex VX-522 inhaled mRNA)
- **In vivo CAR-T** (mRNA-LNP delivering CAR to T cells in vivo — Moderna, Capstan, others)

### 9.3 In vivo gene editing (mRNA-Cas9)

- Intellia NTLA-2001 (TTR knockout, ATTR-CM Phase 3 MAGNITUDE)
- Intellia NTLA-2002 (KLKB1 knockout, hereditary angioedema)
- Verve VERVE-101 (PCSK9 base editing)

### 9.4 miRNA mimic / inhibitor

Multiple Phase 2 programs; no approvals yet.

---

## §10. Stakeholder-Spesifik Analytical Framework

### 10.1 RNA platform pioneer sponsors
- Platform extensibility narrative
- Multiple-target portfolio strategy
- Manufacturing scale moat

### 10.2 LNP / GalNAc IP holder sponsors
- Licensing revenue stream
- Litigation + cross-licensing dynamics
- Next-gen delivery platform R&D

### 10.3 Generic / follow-on RNA developer sponsors
- Limited regulatory framework for "biosimilar siRNA" (no specific abbreviated pathway)
- Manufacturing capacity barrier
- Process IP barriers

### 10.4 Payer paydaşları
- Rare disease pricing acceptance vs cardiovascular siRNA mass-market pricing
- Outcomes-based contracting opportunities (e.g. Leqvio cardiovascular outcomes)

### 10.5 Klinisyen + hasta paydaşları
- Administration burden (intrathecal LP for Spinraza, IV infusion for Onpattro)
- Long-term safety monitoring requirements
- Subcutaneous self-injection convenience for newer GalNAc-siRNAs

### 10.6 Regulatory + public health paydaşları
- mRNA platform pandemic preparedness implications
- ADAR / in vivo gene editing oversight frameworks emerging

---

## §11. Confidence Stamping

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy | **High** (peer-reviewed) |
| LNP composition (publicly disclosed) | **Medium** (often proprietary detail withheld) |
| GalNAc conjugation chemistry | **High** (published) |
| Off-target hybridization risk | **Medium** (in silico prediction + clinical observation) |
| LNP IP litigation status when public | **High** (court records) |
| Real-world myocarditis incidence (mRNA vaccines) | **Medium** (epidemiologic study quality varies) |
| Forward-looking sponsor pipeline timing | **Medium** |
| Confidential CMO contracts | Should not be claimed |

---

## §12. Forbidden Patterns

- ❌ Treating "mRNA therapy" and "DNA gene therapy" as equivalent (mRNA is transient; DNA is persistent)
- ❌ Conflating ASO Gapmer (RNase H mechanism) with steric block ASO (splice modulation) — different mechanisms
- ❌ Treating GalNAc-siRNA hepatic delivery as evidence for non-hepatic GalNAc-siRNA potential (currently liver-only)
- ❌ Generalizing mRNA vaccine class safety to therapeutic mRNA (different dose, route, exposure)
- ❌ Strategic action recommendations for specific RNA sponsors without T6-Defense activation
- ❌ Speculation about confidential LNP composition

---

## §13. Versioning & Changelog

- **v2.5.0 (2026-04-15):** Initial release. RNA therapeutics T3 sub-template covering: 7-class taxonomy (mRNA, siRNA, ASO Gapmer, ASO splice modulator, miRNA, saRNA, circRNA, in vivo CRISPR mRNA), delivery system disciplines (LNP composition + GalNAc conjugation + ASO PS-MOE chemistry + intrathecal/intravitreal routes), approved landscape (9 ASO + 6 siRNA + 3 mRNA vaccines), class-spesifik effects (ASO PS-related thrombocytopenia, siRNA hepatic safety, mRNA vaccine reactogenicity + myocarditis signal), regulatory pathway (CBER vs CDER classification crosswalk + accelerated approval discipline + post-COVID platform technology framework + Sarepta DMD ASO controversy reference), manufacturing (oligonucleotide solid-phase synthesis + IVT mRNA + LNP encapsulation + IP barriers including Alnylam-Moderna and Acuitas-Pfizer disputes), commercial trajectory (mRNA vaccine pandemic-era $55B peak + siRNA Alnylam franchise + ASO Spinraza dominance), pipeline dynamics (RNA editing ADAR + mRNA therapeutics expansion + in vivo gene editing CRISPR-mRNA + miRNA), stakeholder framework (6 abstract categories), confidence stamping. Compatible with all sub-protocols. New manifest gate G28.
