# task-ta-dermatology.md

**T3 Therapeutic Area Template — Dermatology (v4.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Dupixent dupilumab in atopic dermatitis" invokes Layer 0 + Layer 1 generic biologic + Layer 2 task-ta-dermatology.md + Layer 2 task-ta-autoimmune.md (Th2 axis overlap).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "dermatology", "dermatoloji", "skin disease", "deri hastalığı", "cutaneous"
- Disease terms — inflammatory derm: "atopic dermatitis", "AD", "atopik dermatit", "eczema", "egzama", "psoriasis", "sedef", "plaque psoriasis", "psoriatic arthritis" (cross-reference `task-ta-autoimmune.md`), "hidradenitis suppurativa", "HS", "hidradenit", "vitiligo", "alopecia areata", "alopesi areata", "pemphigus", "pemfigus", "bullous pemphigoid", "büllöz pemfigoid", "epidermolysis bullosa", "EB", "epidermoliz bülloza"
- Disease terms — acne + rosacea: "acne", "akne", "acne vulgaris", "rosacea", "rosasea", "hyperhidrosis", "seborrheic dermatitis", "seboreik dermatit"
- Disease terms — skin cancer: "melanoma", "melanom", "basal cell carcinoma", "BCC", "bazal hücreli", "squamous cell carcinoma", "cSCC", "skuamöz hücreli", "Merkel cell carcinoma", "CTCL", "cutaneous T-cell lymphoma", "mycosis fungoides", "Sézary syndrome" (cross-reference `task-ta-oncology.md`)
- Disease terms — photoaging + aesthetic: "actinic keratosis", "AK", "aktinik keratoz", "photoaging", "melasma", "hyperpigmentation"
- Mechanism terms: "IL-4Rα", "IL-13", "IL-17", "IL-23", "IL-36", "JAK inhibitor topical/oral dermatology", "TYK2", "PDE4 inhibitor", "AhR modulator", "aryl hydrocarbon receptor", "retinoid", "hedgehog pathway", "BRAF + MEK melanoma" (cross-reference `task-ta-oncology.md`)
- Asset names: "Dupixent", "dupilumab", "Adbry", "tralokinumab", "Ebglyss", "lebrikizumab", "Nemluvio", "nemolizumab", "Cibinqo", "abrocitinib", "Rinvoq", "upadacitinib", "Olumiant", "baricitinib", "Litfulo", "ritlecitinib", "Leqselvi", "deuruxolitinib", "Opzelura", "ruxolitinib topical", "Vtama", "tapinarof", "Zoryve", "roflumilast", "Sotyktu", "deucravacitinib", "Cosentyx", "secukinumab", "Taltz", "ixekizumab", "Bimzelx", "bimekizumab", "Tremfya", "guselkumab", "Skyrizi", "risankizumab", "Ilumya", "tildrakizumab", "Stelara", "ustekinumab", "Otezla", "apremilast", "Humira", "adalimumab", "Aklief", "trifarotene", "Epsolay", "encapsulated BPO", "Twyneo", "tretinoin + BPO", "Odomzo", "sonidegib", "Erivedge", "vismodegib", "Keytruda", "Opdivo", "Tafinlar", "Mekinist", "Braftovi", "Mektovi", "Adtralza"

### 1.2 Implicit semantic triggers
- Atopic dermatitis biologic + JAK class competition
- Psoriasis IL-17/IL-23 paradigm
- Topical novel mechanism (AhR, PDE4, JAK)
- Alopecia JAK-driven paradigm shift
- Melanoma BRAF/MEK + ICI paradigm
- Skin of color dermatology considerations

### 1.3 NOT triggered by
- ❌ User employer with derm portfolio (Sanofi, Regeneron, Eli Lilly, Pfizer, AbbVie, JNJ, Novartis, UCB, LEO Pharma, Galderma, Almirall, Incyte, Dermavant)
- ❌ User memory-derived dermatology specialty
- ❌ User being derm patient

---

## §2. Foundational Dermatology Framework

### 2.1 Dermatology as a TA — distinguishing features

- **Visible disease burden** — cosmetic/psychosocial impact distinct from internal organ disease
- **Topical-first paradigm** — most diseases treated topically before systemic
- **Specialist + primary care split** — dermatologist workforce constrained; PCP role expanding
- **Biomarker paucity** — most inflammatory derm diseases lack validated biomarkers
- **Clinical endpoint reliance** — physician-reported (IGA, PASI, EASI) + patient-reported (itch NRS, DLQI)
- **Aesthetic + medical overlap** — regulatory differentiation (FDA-approved drug vs cosmetic)
- **Photomedicine + device overlap** — phototherapy, laser, energy-based devices
- **Rapid biologic adoption** — AD + psoriasis transformed 2010s-2020s

### 2.2 Dermatology endpoint frameworks

| Indication | Primary endpoints |
|---|---|
| **Atopic dermatitis** | EASI-75/90 (75%/90% reduction in Eczema Area + Severity Index); IGA 0/1 (clear/almost clear); pruritus NRS ≥4-point reduction |
| **Plaque psoriasis** | PASI 75/90/100 (Psoriasis Area Severity Index); sPGA/IGA 0/1 |
| **HS** | HiSCR (HS Clinical Response — ≥50% reduction in AN count, no ↑ abscess/draining fistulas) |
| **Vitiligo** | F-VASI 75/50 (Facial Vitiligo Area Scoring Index); T-VASI |
| **Alopecia areata** | SALT score ≤20/≤10 (Severity of Alopecia Tool) |
| **Acne** | IGA 0/1 + total lesion count reduction |
| **Rosacea** | IGA 0/1 + inflammatory lesion count |
| **BCC/cSCC** | ORR (objective response rate) locally advanced/metastatic |
| **Melanoma** | OS/PFS (cross-reference `task-ta-oncology.md`) |

---

## §3. Atopic Dermatitis — Biologic + JAK Paradigm

### 3.1 Dupixent (dupilumab) — franchise anchor

**Regeneron + Sanofi** — IL-4Rα mAb blocking IL-4/IL-13 signaling:
- **FDA 2017-03-28** — adult AD
- Subsequent expansions: adolescent AD 2019 → pediatric 6-11y 2020 → 6m-5y 2022
- Also approved: asthma 2018 + CRSwNP 2019 + eosinophilic esophagitis 2022 + prurigo nodularis 2022 + COPD Type 2 2024 (first biologic COPD)
- **~$14B FY2024** — largest AD biologic, dermatology flagship
- Subcutaneous Q2W administration

### 3.2 Dupixent competitor IL-13 mAbs

- **Adbry (tralokinumab)** — LEO Pharma; anti-IL-13; FDA 2021-12 AD
- **Ebglyss (lebrikizumab)** — Eli Lilly; anti-IL-13; FDA 2024-09 AD

### 3.3 IL-31 mAb — Nemluvio

- **Nemluvio (nemolizumab)** — Galderma + Maruho; anti-IL-31; FDA 2024-08 prurigo nodularis + 2024-12 AD
- IL-31 = "itch cytokine"; differentiated mechanism vs IL-4/IL-13

### 3.4 JAK Inhibitors — AD oral class

- **Rinvoq (upadacitinib)** — AbbVie; JAK1 selective; AD 2022-01 (cross-reference `task-ta-autoimmune.md`)
- **Cibinqo (abrocitinib)** — Pfizer; JAK1 selective; AD 2022-01
- Black box per ORAL Surveillance class effect (cross-reference `task-ta-autoimmune.md`)
- **Olumiant (baricitinib)** — Eli Lilly; JAK1/2; AD EU + Japan (not US AD)

### 3.5 Topical JAK — Opzelura

- **Opzelura (ruxolitinib 1.5%)** — Incyte; topical JAK1/2
- **FDA 2021-09 AD** + **2022-07 vitiligo** (first FDA-approved vitiligo repigmentation)
- Boxed warning class effect (topical systemic absorption concern)

---

## §4. Psoriasis — IL-17/IL-23 Paradigm + Topical Innovation

Cross-reference `task-ta-autoimmune.md` for systemic biologic class landscape (Cosentyx, Taltz, Bimzelx, Tremfya, Skyrizi, Stelara + Stelara biosimilars 2025, Humira LOE, Sotyktu TYK2).

### 4.1 Topical innovation — AhR + PDE4

**Vtama (tapinarof 1%)** — Dermavant/Organon
- **FDA 2022-05 plaque psoriasis**
- **FDA 2024-12 AD expansion** (adult + pediatric 2+)
- Aryl hydrocarbon receptor (AhR) modulator — novel first-in-class topical mechanism
- Non-steroidal, no ongoing monitoring requirements

**Zoryve (roflumilast 0.3% cream + 0.15% foam)** — Arcutis Biotherapeutics
- **FDA 2022-07 plaque psoriasis** + **2023-12 seborrheic dermatitis foam** + **2024-07 AD cream**
- PDE4 inhibitor topical — Otezla oral mechanism retargeted topically
- Non-steroidal, once-daily

### 4.2 TYK2 inhibitor — Sotyktu

- **Sotyktu (deucravacitinib)** — Bristol Myers Squibb
- **FDA 2022-09 plaque psoriasis**
- First allosteric TYK2 inhibitor (pseudokinase domain binding)
- Oral once-daily
- Positioned between conventional + biologic
- NOT in JAK class black box (TYK2-selective mechanism)

### 4.3 Humira biosimilar wave impact

Psoriasis/PsA first-line biologic historically Humira → post-2023 LOE biosimilar wave (cross-reference `task-ta-autoimmune.md`) has shifted economic calculus.

---

## §5. Hidradenitis Suppurativa (HS)

### 5.1 Biologic evolution

- **Humira (adalimumab)** — first biologic FDA 2015 HS
- **Cosentyx (secukinumab)** — IL-17A; FDA 2023-10 HS
- **Bimzelx (bimekizumab)** — UCB; IL-17A/F dual; **FDA 2024-10 HS** (+ plaque psoriasis 2023-10, PsA 2024, axSpA 2024)
- Povorcitinib (Incyte) — JAK1; Phase 3

### 5.2 HS clinical framework

- Hurley stage + IHS4 (International HS Severity Score System)
- HiSCR response criteria
- Chronic relapsing inflammatory skin disease
- Historically limited therapeutic options

---

## §6. Alopecia Areata — JAK-Driven Paradigm Shift

### 6.1 Olumiant (baricitinib) — first systemic AA approval

- **Eli Lilly + Incyte** — JAK1/2
- **FDA 2022-06 severe alopecia areata** — first systemic therapy approved
- BRAVE-AA1 + BRAVE-AA2 pivotal
- Daily oral; black box class effect

### 6.2 Litfulo (ritlecitinib)

- **Pfizer** — JAK3 + TEC family selective
- **FDA 2023-06** — severe alopecia areata 12+ (first pediatric AA approval)
- ALLEGRO pivotal
- Oral once-daily

### 6.3 Leqselvi (deuruxolitinib)

- **Sun Pharma** (acquired from Concert) — JAK1/2
- **FDA 2024-07** — severe alopecia areata adults
- Third oral JAK for AA

### 6.4 Topical JAK for AA

- Opzelura off-label
- Topical ritlecitinib exploring

---

## §7. Vitiligo — First Approved Repigmentation

- **Opzelura (ruxolitinib topical)** — Incyte; **FDA 2022-07** first FDA-approved vitiligo repigmentation
- TRuE-V1 + TRuE-V2 pivotal — F-VASI75 primary
- Non-segmental vitiligo 12+
- Previously vitiligo treated with off-label steroids/calcineurin inhibitors/phototherapy

---

## §8. Acne — Novel Topicals

### 8.1 Aklief (trifarotene) — Galderma

- **FDA 2019-10** — fourth-generation retinoid
- Truncal + facial acne
- Pump delivery with large surface area coverage

### 8.2 Twyneo — IRCA + Sol-Gel

- **Twyneo (tretinoin + BPO)** — Sun Pharma; encapsulated formulation; FDA 2021
- Stabilizes retinoid + BPO combination despite incompatibility

### 8.3 Epsolay — encapsulated BPO for rosacea

- **Epsolay (5% microencapsulated BPO)** — Galderma; FDA 2022-04 papulopustular rosacea
- First BPO for rosacea (traditionally contraindicated)
- Silica shell prevents immediate oxidative skin contact

### 8.4 Legacy isotretinoin + REMS

- **Claravis + Accutane historical + Absorica + Myorisan** — isotretinoin
- **iPLEDGE REMS program** — teratogenicity mitigation
- 2021 iPLEDGE portal controversy; 2024 modernization

---

## §9. Skin Cancer — Dermatology/Oncology Interface

Cross-reference `task-ta-oncology.md` for full oncology framework.

### 9.1 Basal cell carcinoma — Hedgehog pathway

- **Erivedge (vismodegib)** — Roche; first Hh inhibitor; FDA 2012
- **Odomzo (sonidegib)** — Sun Pharma (Novartis→Sun); Hh inhibitor; FDA 2015
- Locally advanced + metastatic BCC
- PTCH1 mutation dependency

### 9.2 cSCC — cemiplimab

- **Libtayo (cemiplimab)** — Regeneron + Sanofi; anti-PD-1; FDA 2018-09 advanced cSCC
- First checkpoint inhibitor FDA-approved for cSCC
- Pembrolizumab Keytruda also cSCC

### 9.3 Melanoma — mature ICI + BRAF/MEK class

- **BRAF + MEK combinations:** Tafinlar + Mekinist (Novartis); Braftovi + Mektovi (Pfizer/Array)
- **ICI:** Keytruda (pembrolizumab), Opdivo (nivolumab), Yervoy (ipilimumab), Opdualag (nivolumab + relatlimab LAG-3)
- Adjuvant + metastatic
- Iovance's Amtagvi lifileucel — first TIL therapy 2024

### 9.4 Merkel cell carcinoma

- **Bavencio (avelumab)** — Merck KGaA + Pfizer; anti-PD-L1; FDA 2017 first MCC approval
- **Keytruda** also MCC

### 9.5 CTCL

- **Poteligeo (mogamulizumab)** — anti-CCR4; FDA 2018 MF/SS
- **Adcetris (brentuximab vedotin)** — CD30 ADC; CTCL
- **Targretin (bexarotene)** — retinoid; CTCL

---

## §10. Pemphigus + Rare Bullous Diseases

Cross-reference `task-ta-rare-disease.md`.

### 10.1 Pemphigus vulgaris

- Rituxan rituximab — FDA 2018 PV (off-label prior standard)
- Cross-reference `task-modality-biosimilar.md` for rituximab biosimilars
- FcRn antagonists investigational (Vyvgart cross-reference `task-ta-autoimmune.md`)

### 10.2 Epidermolysis bullosa

- **Vyjuvek (beremagene geperpavec)** — Krystal Biotech; HSV-1 vector topical gene therapy; **FDA 2023-05 dystrophic EB** — first topical gene therapy
- Cross-reference `task-modality-cellgene.md`
- Filsuvez (birch triterpenes topical gel) — Amryt/Chiesi; EB 2024

### 10.3 Bullous pemphigoid

- Systemic corticosteroids standard
- Rituxan off-label
- Dupilumab investigational + BP pipeline

---

## §11. Türkiye Dermatoloji Ekosistemi

### 11.1 TİTCK + SGK SUT dermatoloji

- **TİTCK onay** — çoğu dermatoloji ilacı EMA reliance
- **SGK SUT dermatoloji geri ödeme:** SUT EK-4C/E topikal + biyolojik psoriasis/AD için uzman raporu + dermatoloji imzası gerekli
- **Biyolojik tedavi başlangıç** — dermatoloji uzman konseyi onayı, önceden konvansiyonel tedavi başarısızlığı belgesi
- **Humira biyobenzer geçiş** — SGK'da otomatik; yerli Abdi İbrahim + Deva + Em-Pharma biyobenzerleri mevcut
- **Dupixent AD** — SGK'da onaylı, dermatoloji uzmanı raporu ile erişim
- **JAK oral inhibitörleri (Rinvoq, Cibinqo)** — SGK listesinde dermatoloji endikasyonunda sınırlı; kardiyak + malignensi risk izlem protokollü
- **Opzelura, Vtama, Zoryve, Sotyktu** — TİTCK değerlendirme aşamasında (2026 cutoff); SUT listesinde değil (özel ödeme gerekli)

### 11.2 Türk yerli dermatoloji jenerik ekosistemi

- **Topikal jenerik yaygın:** betametazon + mometazon + takrolimus + pimekrolimus + retinoid (adapalene, tretinoin) + BPO + antifungal + antibakteriyel yerli üretim
- **Oral isotretinoin:** yerli jenerik + iPLEDGE muadili takip
- **Biyobenzer:** Humira biyobenzer yerli üretim, Stelara biyobenzer ithalat
- **Yerli sponsor ekosistemi:** Abdi İbrahim, Deva Holding, Sanovel, Bilim İlaç, Pharmactive, Mustafa Nevzat-Pfizer, Eczacıbaşı

### 11.3 Türkiye dermatoloji epidemiyoloji

- Psoriasis prevalans %1-2 Türkiye
- AD çocukluk %10-15 prevalans
- Akne adölesan %80+ insidans
- Melanoma insidansı Türkiye'de Kuzey Avrupa'ya göre düşük (koyu ten fototipi dağılımı)
- BCC + cSCC yaşlı popülasyonda artan insidans

### 11.4 Türkiye dermatoloji merkezleri

- Tertiary dermatoloji: Hacettepe, Gazi, Ankara Üniversitesi, İstanbul Üniversitesi, Ege, Dokuz Eylül, Marmara, Çukurova, Akdeniz
- Özel dermatoloji kliniklerinde lazer + fototerapi + aesthetic dermatoloji yaygın
- Türk Dermatoloji Derneği — ulusal rehber + sürekli eğitim

---

## §12. Stakeholder-Spesifik Analytical Framework

### 12.1 Big Pharma dermatology sponsors (Regeneron/Sanofi, Eli Lilly, AbbVie, Pfizer, JNJ, Novartis, UCB, LEO Pharma, Galderma, Almirall)
- AD biologic + JAK franchise defense
- Psoriasis IL-17/IL-23 lifecycle management
- Humira + Stelara biosimilar response strategy
- Topical novel mechanism differentiation

### 12.2 Biotech dermatology sponsors (Dermavant, Arcutis, Incyte, Krystal, Moonlake, Evommune)
- Novel topical mechanism (AhR, PDE4, JAK) commercial scaling
- Specialty + PCP education
- Sample + patient access programs
- Rare dermatology gene therapy (Vyjuvek precedent)

### 12.3 Payer dermatology paydaşları
- Biologic tier placement + step therapy
- Topical novel mechanism coverage
- iPLEDGE REMS isotretinoin
- Skin cancer expensive systemic coverage

### 12.4 Klinisyen paydaşları
- Dermatologist workforce constraints
- PCP expanded role in AD + psoriasis biologic initiation
- Aesthetic + medical practice boundary
- Skin of color dermatology training emphasis

### 12.5 Hasta paydaşları
- National Psoriasis Foundation
- National Eczema Association
- Alopecia Areata Foundation
- Skin Cancer Foundation
- Türkiye: Psoriazis Derneği + Türk Dermatoloji Vakfı

---

## §13. Confidence Stamping for Dermatology Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (EASI-75, PASI 90, IGA 0/1) | **High** (peer-reviewed) |
| Biologic commercial sales (Dupixent $14B+ FY2024) | **High** (sponsor IR) |
| Topical novel mechanism commercial trajectory | **Medium** (early post-launch) |
| Humira biosimilar uptake Türkiye dermatoloji | **Medium** (SGK policy variable) |
| Real-world skin cancer ICI outcomes | **Medium** (registry + claims heterogeneous) |
| Aesthetic dermatology market size | **Medium** (private payment opaque) |
| Türkiye SGK SUT dermatoloji raporlu erişim | **High** (SUT tablo primary) |
| Confidential launch plans Türk dermatoloji | Should not be claimed |

---

## §14. Forbidden Patterns

- ❌ Treating all AD patients as biologic candidates (mild-moderate topical appropriate)
- ❌ Conflating psoriasis + eczema therapeutic paradigms (distinct biology + endpoints)
- ❌ Assuming JAK class uniform risk profile (TYK2 Sotyktu distinct regulatory)
- ❌ Oversimplifying vitiligo as cosmetic vs medical (Opzelura FDA approval precedent)
- ❌ Generalizing Hedgehog BCC response to all skin cancers
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Assuming skin cancer ICI efficacy transfers across skin of color (data gaps)
- ❌ Treating topical novel mechanisms as equivalent (AhR, PDE4, JAK have distinct scopes)

---

## §15. Versioning & Changelog

- **v4.0.0 (2026-04-16):** Initial release. Layer 2 Dermatology TA template covering: distinguishing features (visible disease burden + topical-first paradigm + specialist workforce constraints + biomarker paucity + clinical endpoint reliance IGA/PASI/EASI + aesthetic-medical overlap + photomedicine + rapid biologic adoption); endpoint frameworks (EASI-75/90 + IGA 0/1 + pruritus NRS AD; PASI 75/90/100 + sPGA psoriasis; HiSCR HS; F-VASI 75/50 vitiligo; SALT ≤20/≤10 alopecia; IGA + lesion count acne/rosacea; ORR BCC/cSCC); **Atopic Dermatitis biologic + JAK paradigm** (Dupixent dupilumab Regeneron+Sanofi IL-4Rα FDA 2017-03-28 AD → multi-indication expansion COPD 2024 first biologic COPD + ~$14B FY2024 franchise anchor; Adbry tralokinumab LEO IL-13 2021-12 + Ebglyss lebrikizumab Lilly IL-13 2024-09; Nemluvio nemolizumab Galderma+Maruho IL-31 itch cytokine 2024-08 PN + 2024-12 AD; Rinvoq upadacitinib JAK1 2022-01 + Cibinqo abrocitinib JAK1 Pfizer 2022-01 with ORAL Surveillance class black box cross-reference task-ta-autoimmune.md; Olumiant baricitinib JAK1/2 AD EU/Japan; **Opzelura ruxolitinib 1.5% topical Incyte FDA 2021-09 AD + 2022-07 vitiligo first FDA-approved repigmentation**); **Psoriasis topical innovation** (Vtama tapinarof 1% Dermavant/Organon FDA 2022-05 psoriasis + 2024-12 AD 2+ AhR modulator novel first-in-class + non-steroidal; Zoryve roflumilast Arcutis 0.3% cream + 0.15% foam FDA 2022-07 psoriasis + 2023-12 seborrheic foam + 2024-07 AD PDE4 topical; Sotyktu deucravacitinib BMS FDA 2022-09 first allosteric TYK2 NOT in JAK black box; cross-reference task-ta-autoimmune.md for IL-17/IL-23 systemic biologic class Cosentyx/Taltz/Bimzelx/Tremfya/Skyrizi/Stelara + biosimilars 2025 + Humira LOE impact); **HS biologic evolution** (Humira 2015 first + Cosentyx 2023-10 IL-17A + **Bimzelx bimekizumab UCB IL-17A/F dual FDA 2024-10 HS** + povorcitinib JAK1 Phase 3; Hurley + IHS4 + HiSCR frameworks); **Alopecia areata JAK-driven paradigm shift** (Olumiant baricitinib Lilly+Incyte JAK1/2 FDA 2022-06 severe AA first systemic approval + BRAVE-AA1/AA2; **Litfulo ritlecitinib Pfizer JAK3+TEC FDA 2023-06 severe AA 12+ first pediatric** + ALLEGRO; **Leqselvi deuruxolitinib Sun Pharma JAK1/2 FDA 2024-07** third oral JAK); **Vitiligo Opzelura 2022-07 first FDA-approved repigmentation** TRuE-V1/V2 F-VASI75 primary non-segmental 12+; acne novel topicals (Aklief trifarotene Galderma 2019-10 fourth-gen retinoid + Twyneo Sun Pharma tretinoin+BPO encapsulated 2021 + **Epsolay Galderma microencapsulated BPO 2022-04 first BPO for rosacea silica shell**; legacy isotretinoin iPLEDGE REMS + 2024 modernization); **Skin cancer dermatology-oncology interface** cross-reference task-ta-oncology.md (BCC Hedgehog Erivedge vismodegib Roche 2012 first + Odomzo sonidegib Sun Pharma 2015 PTCH1-dependent; cSCC Libtayo cemiplimab Regeneron+Sanofi 2018-09 first ICI cSCC + Keytruda; melanoma BRAF+MEK Tafinlar+Mekinist Novartis + Braftovi+Mektovi Pfizer/Array + ICI Keytruda/Opdivo/Yervoy/Opdualag LAG-3 + **Iovance Amtagvi lifileucel 2024 first TIL melanoma**; Merkel Bavencio avelumab 2017 first; CTCL Poteligeo mogamulizumab 2018 + Adcetris + Targretin); **Pemphigus + rare bullous** cross-reference task-ta-rare-disease.md (Rituxan FDA 2018 PV + FcRn antagonists investigational Vyvgart cross-reference task-ta-autoimmune.md; **Vyjuvek beremagene geperpavec Krystal HSV-1 topical gene therapy FDA 2023-05 DEB first topical gene therapy** cross-reference task-modality-cellgene.md + Filsuvez Amryt/Chiesi birch triterpenes EB 2024); Türkiye dermatoloji ekosistemi (TİTCK + SGK SUT EK-4C/E topikal + biyolojik dermatoloji uzman raporu + biyolojik başlangıç konsey onayı + Humira biyobenzer otomatik yerli Abdi İbrahim/Deva/Em-Pharma + Dupixent AD SGK onaylı + JAK oral sınırlı risk protokollü + Opzelura/Vtama/Zoryve/Sotyktu SUT dışı özel ödeme; yerli topikal jenerik yaygın tüm klas + oral isotretinoin yerli + psoriasis prevalans %1-2 + AD çocukluk %10-15 + akne adölesan %80+ + melanoma düşük fototipe göre + BCC/cSCC yaşlı artış; tertiary Hacettepe/Gazi/İstanbul/Ege + aesthetic + Türk Dermatoloji Derneği). New manifest gate G49. Cross-references task-modality-biosimilar.md (Humira + Stelara biosimilar), task-modality-smallmol.md (JAK + TYK2 + PDE4 + AhR topical), task-modality-cellgene.md (Vyjuvek topical gene therapy), task-ta-autoimmune.md (Th2 overlap AD + psoriasis IL-17/IL-23 + JAK black box + HS Bimzelx), task-ta-oncology.md (skin cancer BCC/cSCC/melanoma/Merkel/CTCL), task-ta-rare-disease.md (rare bullous diseases EB/pemphigus), task-ta-pediatric.md (pediatric AD + acne + pediatric alopecia areata Litfulo).
