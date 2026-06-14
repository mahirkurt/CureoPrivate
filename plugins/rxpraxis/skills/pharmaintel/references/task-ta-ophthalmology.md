# task-ta-ophthalmology.md

**T3 Therapeutic Area Template — Ophthalmology / Retinal + Anterior Segment (v4.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Syfovre pegcetacoplan in geographic atrophy" invokes Layer 0 + Layer 1 task-modality-peptide.md + Layer 2 task-ta-ophthalmology.md. "Luxturna voretigene neparvovec" invokes Layer 0 + Layer 1 task-modality-cellgene.md + Layer 2 task-ta-ophthalmology.md + Layer 2 task-ta-rare-disease.md.
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "ophthalmology", "oftalmoloji", "göz hastalığı", "retinal", "retina", "vitreoretinal", "ocular", "oküler"
- Disease terms — retinal: "wet AMD", "nAMD", "neovascular AMD", "yaş AMD", "age-related macular degeneration", "yaşa bağlı makula dejenerasyonu", "dry AMD", "kuru AMD", "geographic atrophy", "GA", "coğrafik atrofi", "DME", "diabetic macular edema", "diyabetik maküler ödem", "diabetic retinopathy", "DR", "diyabetik retinopati", "RVO", "retinal vein occlusion", "retinal ven oklüzyonu", "myopic CNV", "retinitis pigmentosa", "RP", "Leber congenital amaurosis", "LCA", "Stargardt"
- Disease terms — anterior segment: "dry eye", "DED", "kuru göz", "glaucoma", "glokom", "presbyopia", "prespiyopi", "cataract", "katarakt", "uveitis", "üveit", "keratitis", "keratit", "allergic conjunctivitis", "alerjik konjonktivit", "MGD", "meibomian gland dysfunction"
- Disease terms — pediatric (cross-reference `task-ta-pediatric.md`): "ROP", "retinopathy of prematurity"
- Disease terms — orbital + lid: "thyroid eye disease", "TED", "tiroid oftalmopati"
- Mechanism terms: "anti-VEGF", "anti-VEGF bispecific", "Ang-2", "complement C3", "complement C5", "RNA aptamer", "prostaglandin analogue", "rho kinase inhibitor", "ROCK", "immunosuppressant topical", "voretigene"
- Asset names — retinal: "Eylea", "aflibercept", "Eylea HD", "Lucentis", "ranibizumab", "Vabysmo", "faricimab", "Susvimo", "Byooviz", "Cimerli", "Opuviz", "Yesafili", "Syfovre", "pegcetacoplan", "Izervay", "avacincaptad pegol", "Beovu", "brolucizumab"
- Asset names — dry eye + anterior: "Xiidra", "lifitegrast", "Restasis", "cyclosporine", "Miebo", "perfluorohexyloctane", "Tyrvaya", "varenicline nasal", "Vuity", "pilocarpine", "Rhopressa", "netarsudil", "Rocklatan", "netarsudil+latanoprost", "Vyzulta", "latanoprostene bunod", "Tepezza", "teprotumumab"
- Asset names — rare: "Luxturna", "voretigene neparvovec", "Xipere", "triamcinolone suprachoroidal", "Oxervate", "cenegermin"

### 1.2 Implicit semantic triggers
- Anti-VEGF durability paradigm (Q8W → Q16W → Susvimo PDS)
- Anti-VEGF biosimilar wave 2024+
- Geographic atrophy therapeutic paradigm breakthrough 2023
- Ophthalmic gene therapy pioneering
- Dry eye novel mechanism pipeline
- Glaucoma novel mechanism

### 1.3 NOT triggered by
- ❌ User employer with ophth portfolio (Regeneron, Bayer, Roche/Genentech, Novartis, Apellis, Astellas, Iveric Bio, Alcon, Bausch+Lomb, Santen, Horizon Therapeutics/Amgen, Allergan/AbbVie)
- ❌ User memory-derived ophthalmology specialty
- ❌ User being patient with vision disorder

---

## §2. Foundational Ophthalmology Framework

### 2.1 Ophthalmology as a TA — distinguishing features

- **Target organ accessibility** — local (intravitreal, topical) delivery dominant; systemic only select cases
- **Injection-based chronic therapy** — monthly-to-Q4M IVT anti-VEGF; procedural burden
- **BCVA (best-corrected visual acuity)** as primary endpoint — ETDRS letters gold standard
- **Imaging biomarkers** — OCT (optical coherence tomography) + fundus autofluorescence + angiography increasingly primary endpoint surrogate
- **Demographic concentration** — AMD/DR/DME primarily elderly + diabetic populations
- **Retinal specialist workforce constraints** — supply vs demand imbalance driving extended-interval paradigms
- **Medicare Part B** — primary US reimbursement for IVT agents; buy-and-bill model
- **Biosimilar wave arrived 2024** (Lucentis + aflibercept biosimilars) — commercial disruption

### 2.2 Ophthalmology endpoint frameworks

| Indication | Primary endpoints |
|---|---|
| **Wet AMD/DME/RVO** | BCVA ETDRS letter change vs baseline at week 52/96; proportion ≥15-letter gain |
| **Geographic atrophy** | GA lesion area growth rate (fundus autofluorescence) — NOT BCVA historically |
| **Glaucoma** | IOP reduction from baseline |
| **Dry eye** | Schirmer test + fluorescein staining + symptom scores (SANDE, VAS) + OSDI |
| **Retinitis pigmentosa** | ETDRS BCVA + mobility maze navigation + full-field stimulus testing (Luxturna precedent) |
| **TED** | Proptosis reduction + CAS (Clinical Activity Score) + diplopia |
| **Uveitis** | Vitreous haze grading + BCVA |

---

## §3. Wet AMD / DME / RVO — Anti-VEGF Durability Paradigm

### 3.1 Foundational anti-VEGF class

**Lucentis (ranibizumab)** — Genentech/Roche (+ Novartis ex-US)
- **FDA 2006-06** wet AMD; DME 2012; RVO 2010
- First widely-used IVT anti-VEGF
- Q4W pivotal dosing burden
- Biosimilar competition 2024+ (Byooviz Samsung Bioepis + Cimerli Coherus 2022)

**Eylea (aflibercept 2mg)** — Regeneron (US) + Bayer (ex-US)
- **FDA 2011-11** — VEGF-A + VEGF-B + PlGF multi-target
- Fc-fusion cross-reference `task-modality-fusion.md`
- Q8W maintenance after loading doses
- Market leader ~$8B+ combined FY2024

**Bevacizumab (Avastin) off-label IVT** — compounded; widely used cost-effective alternative (not FDA-approved for ophthalmology); CATT trial equivalence

### 3.2 Second-generation durability advances

**Eylea HD (aflibercept 8mg)** — Regeneron
- **FDA 2023-08** wet AMD + DME + DR
- **Q12-16W dosing** — significant durability improvement
- PULSAR + PHOTON Phase 3 pivotal

**Vabysmo (faricimab)** — Genentech/Roche
- **FDA 2022-01** wet AMD + DME; 2023 RVO
- Bispecific VEGF + Ang-2 — first dual-pathway inhibitor
- **Q16W** maintenance in responders
- TENAYA + LUCERNE + YOSEMITE + RHINE pivotal
- ~$3-4B FY2024 early

### 3.3 Port Delivery System — Susvimo

**Susvimo (ranibizumab port delivery)** — Genentech
- **FDA 2021-10** wet AMD
- **Refillable surgical port** — Q6M refill → 6-month dosing interval
- **2022 voluntary recall** for septum leakage; re-entered market 2023
- 2024 DME + DR label expansion
- Represents "device-sparing paradigm" — IVT injection frequency reduction

### 3.4 Anti-VEGF biosimilar wave 2024+

**Ranibizumab biosimilars:**
- **Byooviz (SB11)** — Samsung Bioepis / Biogen; FDA 2021-09 + EMA
- **Cimerli (ranibizumab-eqrn)** — Coherus BioSciences; FDA 2022-08 + interchangeable 2022
- **Rimmyrah** — China NMPA 2022

**Aflibercept biosimilars (2024):**
- **Yesafili (aflibercept-jbvf)** — Biocon + Mylan; FDA 2024-05 wet AMD
- **Opuviz (aflibercept-yszy)** — Samsung Bioepis; FDA 2024-05
- Patent litigation Regeneron vs biosimilars ongoing
- Biosimilar launch tied to various patent expirations

### 3.5 Geographic Atrophy — complement paradigm breakthrough 2023

**Critical anchor — first GA approvals:**

**Syfovre (pegcetacoplan)** — Apellis Pharmaceuticals
- **FDA 2023-02-17** — first-ever FDA-approved GA treatment
- C3 inhibitor pegylated peptide
- IVT injection monthly or Q2M (18-25 injections/year)
- **OAKS Phase 3 N=637** met primary (21% GA lesion growth reduction monthly)
- **DERBY Phase 3 N=621** missed primary (12% reduction, non-statistical)
- FDA approved despite DERBY miss based on combined treatment effect increasing over time + GALE extension
- **GALE extension 24-36 months:** increasing efficacy up to 35% monthly + 24% Q2M; non-subfoveal subgroup 42% monthly
- **Safety concerns post-launch:** 14+ retinal vasculitis cases reported to ASRS ReST committee (rare but severe; anti-PEG antibody hypothesis); wet AMD conversion dose-dependent 19.5% monthly vs 8.6% Q2M at 36mo
- **EMA REJECTED 2024** — CHMP noted clinically meaningful benefit not demonstrated
- 24,000+ vials distributed as of 2024

**Izervay (avacincaptad pegol)** — Astellas (acquired Iveric Bio July 2023 for $5.9B)
- **FDA 2023-08-04** — second GA approval
- C5 inhibitor pegylated RNA aptamer
- IVT injection monthly
- **GATHER1 Phase 2/3 N=286** met primary (27% GA lesion growth reduction at 12 months)
- **GATHER2 Phase 3 N=448** met primary (14% reduction)
- Different safety profile vs Syfovre — lower retinal vasculitis signal
- EMA review pending

**Commercial + clinical reality:**
- Neither drug demonstrates BCVA improvement — all slowing lesion growth anatomic surrogate
- Modest 14-20% slowing → risk-benefit debate intense
- Monthly injections for years — procedural + patient burden
- Market size potential large (1.5M US GA patients + 75% undiagnosed) but uptake tempered by safety + efficacy modest nature

### 3.6 Pipeline wet AMD + GA

- **ANX007 (ANX007)** — Annexon; C1q inhibitor; Phase 3 ARCHER GA
- **GT005** — Gyroscope/Novartis; AAV CFB gene therapy GA; Phase 3 HORIZON terminated 2023
- **ABBV-RGX-314** — AbbVie/REGENXBIO; AAV anti-VEGF gene therapy wet AMD
- **KSI-301 (tarcocimab)** — Kodiak; BEACON + GLEAM/GLIMMER failed 2024
- **4D-150** — 4D Molecular Therapeutics; AAV gene therapy
- **OPT-302 (sozinibercept)** — Opthea; VEGF-C/D inhibitor + anti-VEGF combo; Phase 3 COAST+ShORe

---

## §4. Glaucoma — IOP Reduction Paradigm

### 4.1 Topical drop classes

**Prostaglandin analogues (first-line):**
- Latanoprost (generic) + Xalatan + Monopost
- Travoprost + Travatan
- Bimatoprost + Lumigan
- Tafluprost + Zioptan

**β-blockers:**
- Timolol + generic
- Betoptic betaxolol

**α-2 agonists:**
- Brimonidine + Alphagan
- Combigan (brimonidine + timolol)

**Carbonic anhydrase inhibitors:**
- Dorzolamide + Trusopt
- Brinzolamide + Azopt
- Cosopt (dorzolamide + timolol)

**Miotics (historical):**
- Pilocarpine — minimal contemporary glaucoma use

### 4.2 Novel mechanism glaucoma drops

**Rho kinase inhibitors:**
- **Rhopressa (netarsudil)** — Alcon (from Aerie); FDA 2017-12
- **Rocklatan (netarsudil + latanoprost)** — Alcon; FDA 2019-03 combination

**Nitric oxide-donating prostaglandin:**
- **Vyzulta (latanoprostene bunod)** — Bausch+Lomb; FDA 2017-11

### 4.3 Preservative-free + sustained delivery

- **Iyuzeh (latanoprost PF)** — Théa; FDA 2022-12 preservative-free
- **Durysta (bimatoprost SR implant)** — Allergan/AbbVie; FDA 2020-03; biodegradable intracameral implant; months-long IOP reduction
- **iDose TR (travoprost SR)** — Glaukos; FDA 2023-12 first FDA-approved intraocular glaucoma drug implant

### 4.4 MIGS (Minimally Invasive Glaucoma Surgery) devices

- iStent, iStent inject (Glaukos)
- Hydrus (Alcon)
- Xen Gel Stent (Allergan/AbbVie)
- OMNI surgical canaloplasty
- Most combined with cataract surgery

---

## §5. Dry Eye Disease (DED)

### 5.1 Established therapy

- **Restasis (cyclosporine 0.05%)** — Allergan/AbbVie; FDA 2003; generic 2022
- **Xiidra (lifitegrast 5%)** — Bausch+Lomb (from Novartis/Takeda); FDA 2016; LFA-1 antagonist
- **Cequa (cyclosporine 0.09%)** — Sun Pharma; FDA 2018

### 5.2 Novel mechanism recent approvals

**Miebo (perfluorohexyloctane)** — Bausch+Lomb
- **FDA 2023-05** — first anti-evaporative DED Rx
- Perfluorobutylpentane preserves tear film
- MGD-related DED

**Tyrvaya (varenicline nasal spray)** — Oyster Point Pharma/Viatris
- **FDA 2021-10** — first nasal spray DED
- Targets trigeminal nerve → reflex tear production

**Vuity (pilocarpine 1.25%)** — Allergan/AbbVie
- **FDA 2021-10** — first pharmacological presbyopia treatment
- Pupil constriction "pinhole effect"
- Q6-hour dosing
- Presbyopia (not dry eye but aging-related anterior segment)

### 5.3 Pipeline DED

- Reproxalap (Aldeyra) — RASP inhibitor; FDA CRL 2023 + 2025 resubmission
- Tivanisiran (Sylentis) — siRNA DED
- Many investigational

---

## §6. Ophthalmic Gene Therapy — Rare Retinal Dystrophy

Cross-reference `task-modality-cellgene.md` + `task-ta-rare-disease.md`.

### 6.1 Luxturna — pioneering ophthalmic gene therapy

**Luxturna (voretigene neparvovec)** — Spark Therapeutics (Roche-acquired 2019)
- **FDA 2017-12-19** — first FDA-approved directly administered gene therapy + first for inherited retinal disease
- AAV2 vector delivering RPE65 cDNA
- RPE65-associated LCA (biallelic RPE65 mutation Leber congenital amaurosis + retinitis pigmentosa)
- Subretinal injection bilateral
- $850K list price (both eyes)

### 6.2 Pipeline retinal gene therapy

- **EDIT-101 (brilliance)** — Editas; CRISPR in vivo LCA10 CEP290; BRILLIANCE Phase 1/2 reported mixed
- **4D-150** — 4D Molecular Therapeutics; AAV wet AMD
- **ABBV-RGX-314 (REGENXBIO + AbbVie)** — AAV anti-VEGF wet AMD
- **Ocugen OCU400, OCU410** — AAV multi-modal
- **Kodiak KSI-301 (tarcocimab)** — anti-VEGF biologic (not gene therapy) failed

### 6.3 Suprachoroidal delivery

**Xipere (triamcinolone acetonide suprachoroidal)** — Clearside Biomedical
- **FDA 2021-10** — first suprachoroidal delivery; uveitic ME
- Novel anatomic compartment

---

## §7. Thyroid Eye Disease (TED)

### 7.1 Tepezza — paradigm breakthrough

**Tepezza (teprotumumab)** — Horizon Therapeutics (Amgen-acquired 2023 for $28B)
- **FDA 2020-01** — first FDA-approved TED treatment
- IGF-1R inhibitor mAb
- 8 infusions Q3W
- ~$400K/course
- Boxed warnings hearing loss + hyperglycemia
- Led Amgen $28B Horizon acquisition — cross-reference `task-ta-autoimmune.md` (inflammation axis)

---

## §8. Uveitis + Ocular Inflammation

- **Humira (adalimumab)** — FDA 2016 non-infectious uveitis (biosimilar wave 2023+)
- **Ozurdex (dexamethasone implant)** — Allergan/AbbVie; ME + uveitis
- **Retisert (fluocinolone implant)** — Bausch+Lomb
- **Yutiq (fluocinolone implant)** — EyePoint
- **Xipere** — suprachoroidal uveitic ME

---

## §9. Neurotrophic Keratitis

- **Oxervate (cenegermin)** — Dompé; FDA 2018-08 — first NK treatment
- Recombinant human nerve growth factor
- Topical eye drop × 8 weeks
- Rare disease designation

---

## §10. Türkiye Oftalmoloji Ekosistemi

### 10.1 TİTCK + SGK SUT oftalmoloji

- **TİTCK onay** — çoğu oftalmoloji ilacı EMA reliance
- **SGK SUT IVT anti-VEGF erişim:** SUT EK-4/F oftalmoloji uzman imzası + raporlu + retina uzmanı konseyi onayı + OCT belgeli; Lucentis + Eylea SGK'da geri ödeme; Vabysmo TİTCK onayı + SGK değerlendirme
- **Eylea HD, Susvimo** — TİTCK değerlendirme aşamasında (2026 cutoff)
- **Syfovre + Izervay GA** — TİTCK onay değerlendirmesi; SGK SUT'ta değil (özel ödeme)
- **Anti-VEGF biyobenzer** — ranibizumab biyobenzer (Byooviz ithalat) SGK SUT'ta, aflibercept biyobenzer TİTCK değerlendirmesi
- **Glokom damlaları** — prostaglandin + timolol + brimonidine + dorzolamide + netarsudil yerli jenerik + ithalat kombinasyon SUT geniş geri ödeme
- **Restasis + Xiidra + Miebo** — kuru göz ilaçları sınırlı SUT, çoğu özel ödeme
- **Luxturna gene therapy** — SGK yurt dışı ilaç dairesi süreci (cross-reference `task-ta-rare-disease.md`)

### 10.2 Türk yerli oftalmoloji jenerik ekosistemi

- Glokom damlaları: tüm klas jenerik yerli (latanoprost + timolol + bimatoprost + travoprost + brimonidine + dorzolamide + brinzolamide + kombinasyonlar)
- Dry eye OTC: yerli yapay gözyaşı + karmellose + hyaluronic acid + sodium hyaluronate jenerik yaygın
- Anti-VEGF: yerli biyobenzer üretim sınırlı; çoğunlukla ithalat
- **Yerli sponsor ekosistemi:** Abdi İbrahim, Sanovel (Vitofer göz damlaları), Bilim İlaç, Deva, Pharmactive, Abdi İbrahim Ilaç-Otsuka, Nobel İlaç

### 10.3 Türkiye oftalmoloji epidemiyoloji

- Diyabetik retinopati insidansı Türkiye'de T2DM prevalansı yüksekliği nedeniyle artmış (~%30-40 DR T2DM hastalarında)
- AMD prevalansı Türkiye'de %10 >65 yaş
- Glokom prevalansı ~%2-3 yetişkin
- Kuru göz prevalansı %15-20 yetişkin
- Retinitis pigmentosa Türkiye'de akraba evlilik nedeniyle daha yaygın; genetik çeşitlilik yüksek (cross-reference `task-ta-rare-disease.md` + `task-ta-pediatric.md`)

### 10.4 Türkiye oftalmoloji merkezleri

- Tertiary retina merkezleri: Hacettepe, Gazi, Ankara Üniversitesi, İstanbul Üniversitesi + Cerrahpaşa, Ege, Dokuz Eylül, Marmara, Çukurova, Akdeniz
- Özel göz hastanesi zinciri: Dünya Göz, Kudret Göz, Medipol Göz
- Türk Oftalmoloji Derneği — ulusal rehber + sürekli eğitim
- Retina ve Vitreus Derneği — subspecialty

---

## §11. Stakeholder-Spesifik Analytical Framework

### 11.1 Big Pharma ophth sponsors (Regeneron, Bayer, Roche/Genentech, Novartis, Apellis, Astellas, Allergan/AbbVie, Bausch+Lomb, Santen, Alcon)
- Anti-VEGF franchise defense (Eylea vs biosimilar)
- GA paradigm capture (Apellis vs Astellas)
- Durability-based differentiation (Eylea HD, Vabysmo, Susvimo)
- Dry eye portfolio expansion

### 11.2 Biotech ophth sponsors (Apellis, Iveric→Astellas, Clearside, Aldeyra, Opthea, Kodiak, 4D, Annexon, Spark→Roche)
- Specialty retina commercial scaling
- Safety signal management (Apellis retinal vasculitis)
- Narrow indication launch
- Gene therapy specialty infrastructure

### 11.3 Biosimilar sponsors (Samsung Bioepis, Coherus, Biocon, Celltrion)
- Ranibizumab + aflibercept biosimilar launch
- Interchangeability designation strategy
- Tender + Part B buy-and-bill dynamics

### 11.4 Payer ophth paydaşları
- Part B buy-and-bill IVT agent coverage
- GA coverage decisions (risk-benefit debate)
- Biosimilar formulary tier placement
- Gene therapy outcomes-based contracting

### 11.5 Klinisyen paydaşları
- Retinal specialist workforce constraints
- Extended-interval dosing practice adoption
- Safety event management (Syfovre retinal vasculitis)
- Comprehensive ophthalmologist vs specialist boundaries

### 11.6 Hasta + advocacy paydaşları
- American Macular Degeneration Foundation
- Foundation Fighting Blindness
- Glaucoma Research Foundation
- Türkiye: Retina Hastaları Derneği + Glokom Derneği

---

## §12. Confidence Stamping for Ophthalmology Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (BCVA letter gain, GA growth reduction) | **High** (peer-reviewed) |
| Eylea + Lucentis sales (sponsor IR disclosed) | **High** |
| Syfovre post-market safety signal (retinal vasculitis) | **High** (ASRS ReST committee + FDA safety) |
| GA long-term real-world efficacy | **Medium** (early post-launch) |
| Biosimilar uptake trajectory | **Medium** (early market) |
| Luxturna real-world durability | **Medium** (limited follow-up) |
| Aflibercept biosimilar patent clearance timeline | **Medium** (litigation-dependent) |
| Türkiye SGK SUT IVT retina protokollü erişim | **High** (SUT tablo primary) |
| Confidential launch pricing negotiations | Should not be claimed |

---

## §13. Forbidden Patterns

- ❌ Conflating wet AMD (anti-VEGF) with dry AMD/GA (complement inhibitor) — distinct pathways
- ❌ Treating GA treatment as visual acuity improvement (only lesion growth slowing demonstrated)
- ❌ Generalizing Syfovre retinal vasculitis to all complement inhibitors prematurely
- ❌ Assuming anti-VEGF biosimilars immediate market penetration (Medicare Part B dynamics complex)
- ❌ Treating IVT injection as minor procedure (endophthalmitis + RD risk real)
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Overstating gene therapy durability (Luxturna long-term efficacy still emerging)
- ❌ Assuming extended-interval anti-VEGF effective for all patients (responder heterogeneity)

---

## §14. Versioning & Changelog

- **v4.0.0 (2026-04-16):** Initial release. Layer 2 Ophthalmology TA template covering: distinguishing features (target organ accessibility local delivery dominant + injection-based chronic therapy + BCVA ETDRS letter primary + OCT/FAF/angiography imaging biomarker + demographic concentration elderly/diabetic + retinal specialist workforce constraints + Medicare Part B buy-and-bill + 2024 biosimilar wave arrival); endpoint frameworks (BCVA ETDRS letter + ≥15-letter gain wet AMD/DME/RVO; GA lesion area growth rate FAF NOT BCVA; IOP reduction glaucoma; Schirmer+staining+SANDE/OSDI dry eye; Luxturna precedent BCVA+mobility maze+FST RP; CAS+proptosis TED; vitreous haze+BCVA uveitis); **Wet AMD/DME/RVO anti-VEGF durability paradigm** (Lucentis ranibizumab Genentech/Roche+Novartis FDA 2006-06 wet AMD + DME 2012 + RVO 2010 Q4W first IVT anti-VEGF + Byooviz Samsung 2021 + Cimerli Coherus interchangeable 2022 biosimilars; Eylea aflibercept Regeneron+Bayer Fc-fusion FDA 2011-11 VEGF-A/B/PlGF Q8W maintenance ~$8B+ combined FY2024; Avastin bevacizumab off-label IVT widely used CATT equivalence; **Eylea HD aflibercept 8mg Regeneron FDA 2023-08 wet AMD+DME+DR Q12-16W** PULSAR+PHOTON; **Vabysmo faricimab Genentech/Roche bispecific VEGF+Ang-2 FDA 2022-01 first dual-pathway** wet AMD+DME + 2023 RVO Q16W TENAYA+LUCERNE+YOSEMITE+RHINE ~$3-4B FY2024; **Susvimo ranibizumab port delivery Genentech FDA 2021-10 refillable surgical port Q6M** 2022 voluntary recall septum + 2023 re-entry + 2024 DME/DR expansion device-sparing paradigm); **anti-VEGF biosimilar wave 2024** (ranibizumab Byooviz/Cimerli/Rimmyrah; aflibercept Yesafili Biocon+Mylan FDA 2024-05 + Opuviz Samsung Bioepis FDA 2024-05 patent litigation ongoing); **Geographic Atrophy complement paradigm breakthrough 2023** (**Syfovre pegcetacoplan Apellis Pharmaceuticals FDA 2023-02-17 first-ever GA approval C3 inhibitor pegylated peptide monthly/Q2M IVT** OAKS N=637 met 21% reduction monthly + **DERBY N=621 MISSED primary 12% non-statistical** but FDA approved based on combined effect + GALE extension 35% monthly/24% Q2M + 42% non-subfoveal monthly; **post-market safety concerns 14+ retinal vasculitis ASRS ReST committee anti-PEG antibody hypothesis** + dose-dependent wet AMD conversion 19.5% monthly vs 8.6% Q2M 36mo; **EMA REJECTED 2024 CHMP clinically meaningful benefit not demonstrated** + 24,000+ vials distributed; **Izervay avacincaptad pegol Astellas acquired Iveric Bio July 2023 $5.9B FDA 2023-08-04 second GA approval C5 inhibitor pegylated RNA aptamer monthly** GATHER1 N=286 27% reduction + GATHER2 N=448 14% reduction + lower retinal vasculitis signal + EMA pending; commercial+clinical reality NEITHER BCVA improvement only lesion growth slowing + modest 14-20% + risk-benefit intense debate + 1.5M US GA patients 75% undiagnosed + uptake tempered); pipeline wet AMD+GA (ANX007 Annexon C1q Phase 3 ARCHER GA + GT005 Gyroscope/Novartis AAV CFB terminated 2023 + ABBV-RGX-314 AbbVie/REGENXBIO AAV anti-VEGF + KSI-301 Kodiak failed 2024 + 4D-150 + OPT-302 Opthea VEGF-C/D); **glaucoma IOP reduction** (prostaglandin latanoprost/travoprost/bimatoprost/tafluprost first-line + β-blocker timolol + α-2 brimonidine/Combigan + CAI dorzolamide/Cosopt + miotic pilocarpine historical; **rho kinase novel** Rhopressa netarsudil Alcon 2017-12 + Rocklatan netarsudil+latanoprost 2019-03 combination; **NO-donating prostaglandin** Vyzulta latanoprostene bunod Bausch+Lomb 2017-11; preservative-free Iyuzeh Théa 2022-12 + **Durysta bimatoprost SR implant Allergan/AbbVie 2020-03 biodegradable intracameral** + **iDose TR travoprost SR Glaukos FDA 2023-12 first intraocular glaucoma drug implant**; MIGS iStent/Hydrus/Xen/OMNI cataract-combined); **Dry Eye** (established Restasis cyclosporine generic 2022 + Xiidra lifitegrast LFA-1 Bausch+Lomb 2016 + Cequa Sun Pharma 2018; **novel Miebo perfluorohexyloctane Bausch+Lomb FDA 2023-05 first anti-evaporative Rx** MGD-related + **Tyrvaya varenicline nasal spray Oyster Point/Viatris FDA 2021-10 first nasal spray DED trigeminal reflex tear** + **Vuity pilocarpine 1.25% Allergan/AbbVie FDA 2021-10 first pharmacological presbyopia pinhole effect Q6-hour**; pipeline reproxalap Aldeyra CRL 2023+2025 resubmission); **ophthalmic gene therapy rare retinal dystrophy** cross-reference task-modality-cellgene.md + task-ta-rare-disease.md (**Luxturna voretigene neparvovec Spark/Roche FDA 2017-12-19 first FDA-approved directly administered gene therapy + first inherited retinal disease** AAV2 RPE65 cDNA subretinal bilateral $850K both eyes + LCA RPE65 biallelic; pipeline EDIT-101 Editas CRISPR in vivo LCA10 CEP290 BRILLIANCE mixed + Ocugen OCU400/OCU410 + **Xipere triamcinolone suprachoroidal Clearside FDA 2021-10 first suprachoroidal delivery uveitic ME**); **TED Tepezza** (teprotumumab **Horizon Therapeutics Amgen-acquired 2023 $28B FDA 2020-01 first TED treatment** IGF-1R mAb 8 infusions Q3W ~$400K/course boxed warning hearing loss + hyperglycemia); uveitis Humira+biosimilar + Ozurdex + Retisert + Yutiq EyePoint + Xipere; **Oxervate cenegermin Dompé FDA 2018-08 first NK treatment** rhNGF topical 8 weeks; Türkiye oftalmoloji ekosistemi (TİTCK + SGK SUT EK-4/F retina uzmanı konsey + OCT belgeli + Lucentis+Eylea SGK geri ödeme + Vabysmo TİTCK onay+SGK değerlendirme + Eylea HD/Susvimo TİTCK değerlendirme + Syfovre+Izervay TİTCK değerlendirme özel ödeme + ranibizumab biyobenzer ithalat SGK + aflibercept biyobenzer TİTCK değerlendirme + glokom damlaları yerli jenerik yaygın + dry eye yapay gözyaşı yerli OTC + Luxturna SGK yurt dışı ilaç dairesi + Türkiye T2DM yüksek → DR artmış + AMD %10 >65 + glokom %2-3 + dry eye %15-20 + RP akraba evlilik yaygın; tertiary Hacettepe/Gazi/İstanbul/Ege + Dünya Göz/Kudret Göz özel hastane zinciri + Türk Oftalmoloji Derneği + Retina Vitreus Derneği). New manifest gate G50. Cross-references task-modality-fusion.md (Eylea aflibercept Fc-fusion), task-modality-biosimilar.md (ranibizumab+aflibercept biosimilar wave 2024), task-modality-cellgene.md (Luxturna AAV2 + EDIT-101 CRISPR in vivo + ABBV-RGX-314 AAV anti-VEGF + 4D-150), task-modality-rna.md (pegcetacoplan pegylated peptide/Syfovre + avacincaptad pegol pegylated RNA aptamer/Izervay — boundary modality classification), task-ta-rare-disease.md (Luxturna + Oxervate + RPE65 LCA), task-ta-pediatric.md (ROP retinopathy of prematurity + pediatric retinal gene therapy), task-ta-autoimmune.md (TED Tepezza inflammation axis + uveitis Humira biosimilar + Th2 allergy anterior conjunctivitis), task-ta-metabolic.md (DR/DME T2DM cardiorenal axis cross-link).
