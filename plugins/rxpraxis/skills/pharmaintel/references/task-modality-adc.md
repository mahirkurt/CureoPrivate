# task-modality-adc.md

**T3 Modality Template — Antibody-Drug Conjugates (ADCs) (v2.5.0)**

> **Architectural context:** Modality-spesifik T3 sub-template. Layers onto generic `task-modality.md` when ADC modality is in scope. Same layered template pattern as `task-modality-biosimilar.md` (v2.0.0 reference implementation).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5. User employer's ADC portfolio interest, user's therapeutic area (oncology preference), or memory-derived sponsor affiliation are NOT valid triggers.

---

## §1. Activation Triggers

### 1.1 Explicit query-content triggers
- Modality terms: "ADC", "ADCs", "antibody-drug conjugate", "antibody drug conjugate", "imminoconjugate", "antikor-ilaç konjugatı"
- Component terms: "DAR", "drug-antibody ratio", "linker chemistry", "cleavable linker", "non-cleavable linker", "payload class"
- Payload class terms: "DM1", "DM4", "MMAE", "MMAF", "deruxtecan", "DXd", "calicheamicin", "PBD", "exatecan", "camptothecin payload", "TOP1 inhibitor payload", "tubulin inhibitor payload"
- Class effect terms: "ILD ADC", "interstitial lung disease ADC", "ocular toxicity ADC", "thrombocytopenia ADC", "neutropenia ADC", "bystander effect"
- Asset-spesifik: "Enhertu", "Kadcyla", "Trodelvy", "Polivy", "Padcev", "Adcetris", "Tivdak", "Elahere", "Datroway", "Blenrep"

### 1.2 Implicit semantic triggers
- HER2 / TROP2 / Nectin-4 / B7-H4 / CEACAM5 / FRα target landscape analysis (ADC-rich target classes)
- Solid tumor late-line treatment paradigm analysis
- Heavily pretreated mCRC / NSCLC / mBC / mUC competitive landscape

### 1.3 NOT triggered by
- ❌ User's employer being an ADC developer (e.g. Daiichi Sankyo, AstraZeneca, Roche, Pfizer/Seagen, Gilead, ImmunoGen acquired by AbbVie, ADC Therapeutics, Mersana)
- ❌ Memory-derived professional context indicating ADC interest

---

## §2. Foundational Conceptual Framework

### 2.1 ADC architecture — three components

```
       ┌────────────────────────────────┐
       │  Monoclonal Antibody (mAb)     │ ← target binding + immune effector
       │  (typically IgG1, ~150 kDa)    │
       └───────────┬────────────────────┘
                   │
                   │  Linker (cleavable vs non-cleavable)
                   │
                   ▼
       ┌────────────────────────────────┐
       │  Cytotoxic Payload             │ ← cell killing
       │  (small molecule, ~1 kDa)      │
       └────────────────────────────────┘
```

Discipline: An ADC is NOT a biosimilar candidate, NOT a small molecule, NOT a pure biologic — it is a **conjugated molecular entity** with hybrid regulatory and analytical considerations.

### 2.2 Drug-Antibody Ratio (DAR)

DAR = average number of payload molecules per antibody. Critical quality attribute.

| DAR range | Characterization | Examples |
|---|---|---|
| **DAR 2-4** | Low; classical first-gen ADCs | Kadcyla (T-DM1, DAR ~3.5), Adcetris (DAR 4) |
| **DAR ~4-6** | Moderate; second-gen optimization | Polivy (DAR ~3.5), Padcev (DAR ~3.8) |
| **DAR 7-8** | High; third-gen "hyperloaded" | Enhertu (T-DXd, DAR ~8), Trodelvy (DAR ~7.6), Datroway (Dato-DXd, DAR ~4) |

**Discipline:** Higher DAR enables more payload delivery per antibody but may compromise PK (faster clearance, aggregation) and increase off-target toxicity. The DAR optimization is a tradeoff, not a maximization.

### 2.3 The "totality of conjugate" considerations

Unlike biosimilars (where reference comparability is the primary lens), ADCs are characterized as **novel composite entities** — even when sharing antibody backbone with another product. Trastuzumab deruxtecan ≠ trastuzumab emtansine in any meaningful regulatory or clinical sense; the linker-payload combination defines the molecular identity.

---

## §3. Payload Class Taxonomy

### 3.1 Microtubule inhibitors

**Mechanism:** Disrupt mitosis by binding tubulin / preventing microtubule polymerization.

| Payload | ADC examples | Sponsor |
|---|---|---|
| **DM1 (mertansine, maytansinoid)** | Kadcyla (T-DM1), Elahere (mirvetuximab soravtansine — DM4 actually) | Roche, ImmunoGen/AbbVie |
| **DM4 (ravtansine, maytansinoid)** | Elahere | ImmunoGen/AbbVie |
| **MMAE (monomethyl auristatin E)** | Adcetris (BV), Polivy, Padcev, Tivdak, Blenrep, Aidix | Pfizer/Seagen, Roche, Pfizer/Seagen-Astellas, Pfizer/Seagen-Genmab, GSK, vd. |
| **MMAF (monomethyl auristatin F)** | Blenrep | GSK |

### 3.2 DNA-damaging agents

**Mechanism:** Bind DNA → strand break, alkylation, replication arrest.

| Payload | ADC examples | Sponsor |
|---|---|---|
| **Calicheamicin** | Mylotarg (gemtuzumab ozogamicin), Besponsa (inotuzumab ozogamicin) | Pfizer |
| **PBD (pyrrolobenzodiazepine) dimers** | Zynlonta (loncastuximab tesirine), former Vadastuximab talirine | ADC Therapeutics, former Seattle Genetics |

### 3.3 Topoisomerase I inhibitors (third-gen "DXd" class)

**Mechanism:** TOP1 inhibition → DNA-protein crosslink → replication fork collapse.

| Payload | ADC examples | Sponsor |
|---|---|---|
| **DXd (deruxtecan, exatecan derivative)** | Enhertu (T-DXd), Datroway (Dato-DXd), DS-7300 (HER3-DXd ifinatamab deruxtecan) | Daiichi Sankyo + AstraZeneca |
| **SN-38 (irinotecan active metabolite)** | Trodelvy (sacituzumab govitecan) | Gilead |
| **Other camptothecin analogs** | Multiple Phase 1/2 ADCs in development | Various |

**DXd platform clinical resonance:** DESTINY-Breast03 (T-DXd vs T-DM1, NEJM 2022;386:1143-1154) demonstrated mPFS 28.8 vs 6.8 ay (HR 0.33) — class-shifting result. DXd platform increasingly defines third-generation ADC standard.

### 3.4 Emerging payload classes
- **Topoisomerase II inhibitors** (limited clinical use)
- **RNA polymerase inhibitors** (amanitin-conjugates — investigational)
- **Bcl-xL inhibitors** (fusion approach)
- **Immune agonist payloads** (TLR agonists, STING agonists — "immune-stimulating ADCs" / iADCs)

---

## §4. Linker Chemistry

### 4.1 Cleavable linkers

Released payload at target site (lysosomal protease, acidic pH, glutathione reduction):
- **Valine-citrulline (Vc)** — cathepsin B-cleavable; predominant for MMAE conjugates
- **Hydrazone** — pH-cleavable (acidic lysosomal); historical (Mylotarg withdrawn-then-reapproved with reformulation)
- **Disulfide** — glutathione-reducible; tisotumab vedotin (Tivdak)

**Bystander effect:** Cleavable linkers release membrane-permeable payload that can diffuse into neighboring cells — important for heterogeneous target expression tumors. DXd and MMAE both bystander-active.

### 4.2 Non-cleavable linkers

Payload remains attached to amino acid residue post-internalization and lysosomal proteolysis:
- **Thioether (SMCC)** — Kadcyla (T-DM1)
- **Maleimidocaproyl (mc)** — research/investigational

Non-cleavable linkers: less bystander effect, theoretically lower off-target toxicity but reduced efficacy in heterogeneous tumors.

### 4.3 Stability discipline

Linker stability in plasma is a critical quality attribute. Premature release in circulation = systemic payload exposure = off-target toxicity. Stability characterization includes:
- In vitro plasma stability (typically 7-14 day incubation at 37°C)
- In vivo PK comparison of conjugated mAb vs free payload
- Dissociation constant Kd of payload-linker bond

---

## §5. Class Toxicity Profile

### 5.1 Common ADC class effects

| Toxicity | Mechanism | Clinical management |
|---|---|---|
| **Hematologic** (neutropenia, thrombocytopenia, anemia) | On-target/off-tumor + bystander effect on bone marrow | Standard supportive care, dose reduction |
| **Peripheral neuropathy** | Microtubule inhibitor payload (MMAE, DM1) accumulation in peripheral nerves | Dose reduction; eventual discontinuation |
| **Ocular toxicity** | Off-target conjunctival/corneal effects (Blenrep keratitis particularly) | Eye drops, ophthalmology monitoring; Blenrep withdrawn from US 2022 due in part to keratitis severity |
| **Hepatotoxicity** | Hepatic uptake of conjugate | LFT monitoring |
| **Infusion reactions** | mAb component | Premedication, slowed infusion |

### 5.2 ILD / pneumonitis class effect (DXd-spesifik but broader)

**Interstitial Lung Disease (ILD) / Pneumonitis** is a **defining class-effect concern for DXd-class ADCs** (Enhertu, Datroway). Per Enhertu boxed warning:
- ILD/pneumonitis incidence ~10-15% across DESTINY trials
- Grade ≥3 events 1-2%
- Fatalities reported (~1.5% across pooled analysis)
- Mechanism unclear: possibly target-independent uptake by pneumocytes, hypothesized to be DXd payload-specific

**Mandatory monitoring:** Patient education on respiratory symptoms; baseline + periodic chest CT; pulmonary function testing; immediate discontinuation for grade 2+ ILD.

### 5.3 Class-spesifik discipline for HER2 ADCs

T-DM1 (Kadcyla) class effects: thrombocytopenia, hepatotoxicity, peripheral neuropathy
T-DXd (Enhertu) class effects: nausea/vomiting (highly emetogenic), neutropenia, ILD, alopecia

These are **not interchangeable safety profiles** despite shared antibody backbone. DXd payload + higher DAR + cleavable linker + bystander effect = different toxicity signature.

---

## §6. Regulatory Pathway

### 6.1 FDA framework

ADCs reviewed under **BLA pathway (PHS Act §351(a))** because mAb component dominates the regulatory classification. CDER (Center for Drug Evaluation and Research) Office of Hematology and Oncology Products (OHOP) typical review division for oncology ADCs.

**Combination product complexity:** Some ADCs may invoke FDA combination product review if companion diagnostic is co-developed (e.g. HER2 IHC for T-DM1, T-DXd, both with co-approved IVD). Companion diagnostic typically reviewed by CDRH (Center for Devices and Radiological Health).

**Accelerated approval:** Common for ADCs targeting rare or refractory tumors. Examples:
- Blenrep (5L+ multiple myeloma, accelerated 2020 → withdrawn 2022 after DREAMM-3 negative)
- Tivdak (recurrent/metastatic cervical cancer)
- Enhertu HER2-low BC (DESTINY-Breast04)

### 6.2 EMA framework

EMA centralized procedure; Committee for Medicinal Products for Human Use (CHMP). ADC-spesifik scientific guidance: EMA "Guideline on the development of new medicinal products for the treatment of acute lymphoblastic leukaemia" and ADC-mention in oncology guidance documents. No standalone "biosimilar"-equivalent abbreviated pathway for ADCs (each ADC is a novel composite).

### 6.3 PMDA framework

Daiichi Sankyo's home regulator; PMDA has reviewed multiple ADCs. Sakigake (先駆け) breakthrough designation applicable to first-in-class ADC modalities. Japanese AdComm-equivalent: 薬事・食品衛生審議会 (Yakuji shokuhin eisei shingikai).

### 6.4 NMPA + Türkiye

NMPA has approved several global ADCs (Enhertu, Kadcyla, Adcetris) plus emerging Chinese-developed ADCs (RemeGen disitamab vedotin, Akeso-developed candidates). TİTCK reliance pathway via EMA used for most multinational ADCs reaching Türkiye.

---

## §7. Manufacturing Considerations

### 7.1 Three-step manufacturing complexity

1. **mAb production** — mammalian cell culture (CHO, NS0); identical to standalone biologic manufacturing
2. **Payload synthesis** — small molecule chemical synthesis; high-potency containment required (OEB 5 typical)
3. **Conjugation** — covalent linker-mediated coupling; stoichiometry control is the DAR-determining step

### 7.2 Conjugation chemistry

- **Lysine conjugation** — random coupling to lysine residues; produces heterogeneous DAR distribution (Kadcyla, Adcetris)
- **Cysteine conjugation** — partial reduction of inter-chain disulfides; controlled DAR (Polivy)
- **Site-specific conjugation** — engineered cysteine, glutamine, or unnatural amino acid; uniform DAR (newer platforms)

### 7.3 CMC analytical complexity

Critical quality attributes for ADC release:
- DAR distribution (mass spectrometry, HIC-HPLC)
- Free payload content (residual unconjugated drug)
- Aggregation (SEC-HPLC)
- Conjugated mAb identity (peptide mapping)
- Bioactivity (target binding, in vitro cytotoxicity bioassay)

---

## §8. Commercial Trajectory Patterns

### 8.1 Blockbuster ADCs (>$1B annual)

| Asset | Sponsor | 2024 sales (~) | Indication scope |
|---|---|---|---|
| **Enhertu** | Daiichi Sankyo + AstraZeneca | ~$3.5B+ | HER2+ mBC, HER2-low mBC, gastric, NSCLC HER2m, colorectal HER2 |
| **Adcetris** | Pfizer/Seagen + Takeda (ex-US) | ~$2B | Hodgkin lymphoma, T-cell lymphoma frontline + relapsed |
| **Padcev** | Pfizer/Seagen + Astellas | ~$1.5B+ | mUC monotherapy + Padcev+pembro 1L |
| **Trodelvy** | Gilead | ~$1.2B | mTNBC, HR+/HER2- mBC |
| **Kadcyla** | Roche | ~$2B (declining post-T-DXd erosion) | HER2+ adjuvant, HER2+ mBC 2L+ |
| **Polivy** | Roche | ~$1B | DLBCL frontline (POLARIX), R/R DLBCL |

### 8.2 Therapeutic area concentration

Oncology dominates ADC clinical development (>95% pipeline); limited non-oncology ADCs (some autoimmune in development).

### 8.3 Pricing dynamics

ADCs price in the $200K-$500K+/year range typically. List price inflation steady; payer pushback on real-world effectiveness vs trial expectations a recurring theme. HTA debate often centers on ICER given high cost vs marginal OS extension in mature lines.

---

## §9. Pipeline Dynamics

### 9.1 Target landscape concentration

Active ADC clinical development concentrated on a relatively small number of validated targets:
- **HER2** (T-DXd dominance + Disitamab vedotin + multiple followers)
- **TROP2** (Trodelvy + Datroway + multiple followers)
- **Nectin-4** (Padcev + multiple followers)
- **B7-H4, CEACAM5, FRα, PTK7, CDH6, GPRC5D** (next-wave ADC targets in Phase 1/2)

### 9.2 Competitive arc patterns

Typical ADC competitive arc:
1. **First-in-class ADC** — proves target validity, reaps premium pricing
2. **Best-in-class follower** — improves DAR / payload / linker / safety; may take share
3. **Geography-spesifik entrants** — Chinese-developed ADCs targeting same epitopes (e.g. RemeGen disitamab vedotin HER2)
4. **Combination strategy entrants** — ADC + IO combos (Padcev + pembro precedent)

### 9.3 Bispecific ADCs

Emerging architectural direction: bispecific antibody (two target binding domains) + payload conjugation. Example: zanidatamab-DXd in development. Adds combinatorial complexity to characterization.

---

## §10. Stakeholder-Spesifik Analytical Framework

For a biosimilar-style abstract stakeholder framework (per `generic-by-default.md` Article 3.2):

### 10.1 First-in-class ADC sponsors
- Premium pricing window
- Geographic launch sequencing
- Lifecycle expansion (indication broadening)
- Trial-vs-RWE divergence management

### 10.2 Best-in-class follower ADC sponsors
- Differentiation strategy (DAR, linker, payload, safety)
- Head-to-head trial design vs incumbent
- Combination differentiation

### 10.3 Geographic-entrant ADC sponsors (Chinese, Korean developers)
- Domestic market validation strategy
- Out-licensing strategy for ex-Asia markets
- Cost manufacturing advantage

### 10.4 Reference product sponsors facing ADC erosion
- Same-class lifecycle management
- Adjacent-target diversification
- Combination strategy with own portfolio

### 10.5 Payer paydaşları
- ICER assessment frameworks for high-cost specialty oncology
- Indication-specific access restrictions
- Outcomes-based contracting

### 10.6 Klinisyen paydaşları
- Sequencing decisions (ADC-vs-ADC, ADC-vs-IO, ADC-vs-chemo)
- Toxicity management protocols (ILD monitoring discipline for DXd class)

---

## §11. Confidence Stamping for ADC Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA / PMDA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (HR, p-value, mPFS, mOS) | **High** (peer-reviewed publication) |
| DAR + linker + payload chemistry | **High** (label / publication) |
| Real-world ILD incidence | **Medium** (RWE depends on registry quality) |
| Off-target toxicity mechanism | **Medium** (often hypothetical) |
| Confidential manufacturing process detail | Should not be claimed |
| Forward-looking sponsor pipeline timing | **Medium** (sponsor guidance, may slip) |
| Net pricing after rebates | **Low** (confidential) |

---

## §12. Forbidden Patterns

- ❌ Treating an ADC as a "biosimilar" of its antibody backbone (Trastuzumab biosimilars ≠ T-DXd)
- ❌ Conflating two ADCs sharing antibody backbone (T-DM1 ≠ T-DXd ≠ T-DM4)
- ❌ Strategic action recommendations for specific ADC sponsors without T6-Defense activation
- ❌ Speculation about confidential conjugation chemistry IP
- ❌ Overstating DXd-class ILD as "uniquely toxic" without RWE comparison to other ADC classes

---

## §13. Versioning & Changelog

- **v2.5.0 (2026-04-15):** Initial release. ADC-spesifik T3 sub-template covering ADC architecture (3-component), DAR (low/moderate/high categories), payload class taxonomy (microtubule inhibitors / DNA-damaging / TOP1 inhibitors / emerging), linker chemistry (cleavable vs non-cleavable + bystander effect), class toxicity profile (common ADC class effects + DXd-spesifik ILD discipline + HER2 ADC class differentiation), regulatory pathway (FDA BLA + companion diagnostic complexity + EMA + PMDA + NMPA + Türkiye), manufacturing (3-step complexity + conjugation chemistry + CMC analytical), commercial trajectory (blockbuster ADCs + therapeutic area concentration + pricing dynamics), pipeline dynamics (target landscape + competitive arc + bispecific ADCs), stakeholder framework (6 abstract categories), confidence stamping. Compatible with all sub-protocols. New manifest gate G26 (ADC T3 template execution conditional on ADC modality query content).
