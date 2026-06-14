# task-ta-womens-health.md

**T3 Therapeutic Area Template — Women's Health / Reproductive Medicine (v4.0.0, Layer 2)**

> **Architectural context:** Layer 2 (Therapeutic Area) T3 template. Layers onto Layer 1 modality template + Layer 0 generic. Example: "Zurzuvae zuranolone in PPD" invokes Layer 0 + Layer 1 task-modality-smallmol.md + Layer 2 task-ta-womens-health.md + Layer 2 task-ta-cns.md (multi-TA: women's health + CNS/psychiatry overlap).
>
> **Trigger logic query-content-based** per `generic-by-default.md` Article 5.

---

## §1. Activation Triggers

### 1.1 Explicit triggers
- TA terms: "women's health", "kadın sağlığı", "reproductive medicine", "üreme tıbbı", "obstetrics", "gynecology", "kadın-doğum", "maternal health", "anne sağlığı"
- Disease/indication terms — contraception + reproductive: "contraception", "kontrasepsiyon", "birth control", "hormonal contraceptive", "oral contraceptive", "OC", "IUD", "RİA", "intrauterine device", "emergency contraception", "abortion", "kürtaj", "medical abortion", "mifepristone", "Mifeprex", "misoprostol"
- Disease terms — menstrual + reproductive: "heavy menstrual bleeding", "HMB", "menorrhagia", "endometriosis", "endometriozis", "uterine fibroids", "uterin fibroid", "myom", "leiomyoma", "adenomyosis", "PCOS", "polycystic ovary syndrome", "polikistik over", "dysmenorrhea", "PMS", "PMDD"
- Disease terms — menopause + HRT: "menopause", "menopoz", "perimenopause", "perimenopoz", "vasomotor symptoms", "VMS", "hot flashes", "sıcak basması", "HRT", "hormone replacement therapy", "hormon replasman tedavisi", "estrogen therapy", "MHT", "menopausal hormone therapy", "vaginal atrophy", "GSM", "genitourinary syndrome of menopause"
- Disease terms — pregnancy + peripartum: "postpartum depression", "PPD", "doğum sonrası depresyon", "peripartum depression", "preeclampsia", "eclampsia", "preterm labor", "preterm delivery", "gestational diabetes", "GDM", "fertility", "fertilite", "IVF", "in vitro fertilization", "ovulation induction", "ART", "assisted reproductive technology"
- Disease terms — gynecologic oncology (partially — cross-reference `task-ta-oncology.md`): "endometrial cancer", "ovarian cancer", "cervical cancer", "serviks kanseri", "HPV-related", "BRCA", "BRCA1/2"
- Disease terms — breast: "breast cancer", "mBC" (cross-reference oncology), "dense breasts", "osteoporosis postmenopausal", "postmenopozal osteoporoz"
- Mechanism terms: "GnRH antagonist", "SERM", "selective estrogen receptor modulator", "SERD", "PARP", "aromatase inhibitor", "NK3R antagonist", "neurokinin 3 receptor antagonist", "oxytocin receptor", "progestin", "estrogen-progestin", "neuroactive steroid"
- Asset names: "Zurzuvae", "zuranolone", "Zulresso", "brexanolone", "Veozah", "fezolinetant", "Lynkuet", "elinzanetant", "Myfembree", "Oriahnn", "relugolix", "Orilissa", "elagolix", "Ryeqo", "Orgovyx", "Nextstellis", "estetrol", "Annovera", "segesterone acetate/EE", "Opill", "norgestrel OTC", "Evenity", "romosozumab", "Prolia", "denosumab", "Forteo", "teriparatide", "Tymlos", "abaloparatide", "Menopur", "Gonal-F", "Follistim", "Pergoveris", "Ovidrel", "Cetrotide", "Orgalutran", "Mifeprex", "mifepristone", "Imvexxy", "estradiol"

### 1.2 Implicit semantic triggers
- Menopause pharmacotherapy paradigm shift (non-hormonal VMS)
- Endometriosis/uterine fibroid GnRH antagonist class
- Postpartum depression treatment revolution
- Postmenopausal osteoporosis anabolic therapy
- Fertility + ART treatment protocols
- Contraceptive access + OTC transitions

### 1.3 NOT triggered by
- ❌ User employer with women's health portfolio (Organon, Pfizer Women's Health, Ferring Reproductive Health, Bayer, Myovant/Sumitomo, Astellas, AbbVie, Besins Healthcare)
- ❌ User memory-derived OB/GYN specialty
- ❌ User being female (non-sequitur trigger)

---

## §2. Foundational Women's Health Framework

### 2.1 Women's health as a TA — distinguishing features

Women's health occupies a distinctive position:
- **Historical underinvestment** — regulatory + clinical trial historical exclusion of women (reversed post-1993 NIH Revitalization Act, FDA 2021 guidance)
- **Regulatory complexity** — pregnancy categorization, breastfeeding, teratogenicity discipline
- **Cyclical biology** — menstrual cycle + pregnancy + peripartum + menopause create distinct pharmacokinetic + treatment contexts
- **Divestment era** — Pfizer spin-off Organon (2021), Haleon Women's Health categories, many Big Pharma exits
- **Payer dynamics** — contraception coverage political; menopause therapy coverage variable; ART often not covered
- **Pregnancy label "black box" discipline** — Category X historical; 2014 PLLR replacement

### 2.2 FDA Pregnancy and Lactation Labeling Rule (PLLR)

**2015 effective PLLR replaced A/B/C/D/X categories:**
- Pregnancy subsection with narrative summary + risk data
- Lactation subsection
- Females and Males of Reproductive Potential subsection
- Dose adjustment recommendations during pregnancy when relevant

### 2.3 Women's health endpoint frameworks

| Indication | Primary endpoints |
|---|---|
| **Contraception** | Pearl Index (pregnancies per 100 women-years), perfect-use + typical-use failure rates |
| **HMB / endometriosis** | Menstrual blood loss reduction; pain VAS; dysmenorrhea NRS |
| **Uterine fibroids** | Menstrual blood loss + fibroid volume |
| **Menopause VMS** | VMS frequency reduction + severity (mean daily moderate-severe VMS) |
| **Postpartum depression** | HAMD-17 change from baseline (Zurzuvae precedent) |
| **Osteoporosis** | Fracture reduction + BMD change |
| **ART / fertility** | Ongoing pregnancy rate + live birth rate; mature oocytes retrieved |
| **Preterm labor** | Gestational age at delivery |

---

## §3. Postpartum Depression — Paradigm Shift

### 3.1 Pre-2019 landscape

- Off-label SSRIs/SNRIs — no PPD-specific approvals
- Stigma + underdiagnosis
- ~1 in 7 U.S. women affected

### 3.2 Zulresso (brexanolone) — 2019 first PPD approval

- **Sage Therapeutics** FDA 2019-03-19
- IV infusion 60 hours continuous
- REMS program required (administration in certified facility)
- Sedation risk
- ~$34K/course WAC
- Commercial underperformance due to administration burden

### 3.3 Zurzuvae (zuranolone) — oral paradigm shift

**Pivotal anchor:**
- **Sage Therapeutics + Biogen** FDA 2023-08-04
- **First and only oral PPD treatment**
- Neuroactive steroid (NAS) + GABA-A receptor positive allosteric modulator (PAM)
- 50 mg once daily × 14 days (2-week treatment course)
- Rapid onset — efficacy by Day 3, primary endpoint Day 15
- DEA Schedule IV (October 2023)
- **Pivotal trials:** SKYLARK + ROBIN (NEST program); HAMD-17 primary endpoint
- **WAC:** $15,900 for 14-day course
- Commercial launch December 14, 2023
- **MDD indication:** CRL 2023-08 (simultaneous CRL for MDD, PPD approved; needed additional study)
- **Boxed warning:** driving impairment (12-hour post-dose)
- **Breastfeeding data limited:** trial participants forgo breastfeeding
- **EC EU approval:** September 2025; MHRA UK approval August 2025

### 3.4 Pipeline peripartum psychiatry

- Esketamine (Spravato) off-label PPD investigational
- Novel NAS analogs Sage Pipeline

---

## §4. Menopause Pharmacotherapy Revolution

### 4.1 Historical HRT paradigm + Women's Health Initiative (WHI)

- **WHI (2002)** — landmark finding of increased breast cancer + CV events with estrogen-progestin therapy → massive HRT market contraction
- Subsequent re-analysis showed age-dependent risk (younger postmenopausal different risk profile)
- HRT rehabilitation ongoing but baseline cautious

### 4.2 Non-hormonal VMS — NK3R antagonist class

**Veozah (fezolinetant)** — Astellas
- **FDA 2023-05-12** — first NK3R antagonist for VMS
- Oral daily; non-hormonal mechanism
- **SKYLIGHT 1 + 2 + 4 Phase 3** pivotal
- **Hepatotoxicity signal** — FDA Boxed Warning 2024 post-marketing (liver enzyme monitoring required)
- Commercial trajectory initially strong → hepatotoxicity concerns tempering uptake

**Lynkuet (elinzanetant)** — Bayer
- **FDA 2025** approval — NK1/NK3 dual receptor antagonist
- OASIS 1/2/3 Phase 3 pivotal
- Positioned as alternative non-hormonal VMS therapy

### 4.3 Traditional HRT continuing

- **Estradiol transdermal** (Climara, Vivelle-Dot, Minivelle, Divigel) — most Menopause Society-recommended hormonal option
- **Bijuva** (estradiol/progesterone) — single-pill bioidentical 2018
- **Duavee** (bazedoxifene/conjugated estrogens) — tissue-selective estrogen complex
- **Imvexxy, Intrarosa, Estrace, Premarin** — vaginal atrophy
- **Prasterone (Intrarosa)** — DHEA vaginal

### 4.4 Vasomotor symptom non-hormonal off-label
- Paroxetine (Brisdelle — only low-dose SSRI FDA-approved for VMS)
- Gabapentin
- Clonidine
- Oxybutynin
- These largely displaced by NK3R antagonists for those who prefer non-hormonal

---

## §5. GnRH Antagonist Class — Endometriosis + Uterine Fibroids

Cross-reference `task-modality-peptide.md` for injectable GnRH analogs; this section covers oral GnRH antagonist innovation.

### 5.1 Orilissa (elagolix) — AbbVie/Neurocrine

- **FDA 2018-07-23** — first oral GnRH antagonist
- Endometriosis-associated pain (Orilissa)
- Uterine fibroids — **Oriahnn** (elagolix + estradiol + norethindrone acetate) 2020 add-back combination

### 5.2 Myfembree (relugolix combination) — Myovant/Pfizer

- **Myfembree (relugolix + estradiol + norethindrone acetate)** FDA 2021 (HMB + uterine fibroids) + 2022 endometriosis
- **Ryeqo** EMA 2021 equivalent
- Once-daily oral (simpler than elagolix BID)
- Commercial positioning vs elagolix

### 5.3 Orgovyx (relugolix) — prostate cancer

- Relugolix monotherapy (Orgovyx) FDA 2020 for advanced prostate cancer (cross-reference `task-ta-oncology.md`)

---

## §6. Contraception Landscape

### 6.1 OTC contraception revolution

**Opill (norgestrel 0.075 mg)** — Perrigo/HRA Pharma
- **FDA 2023-07 OTC approval** — first OTC oral contraceptive in US
- Progestin-only ("mini-pill")
- Available nationwide 2024
- Expanded contraceptive access particularly for uninsured + rural

### 6.2 Novel oral contraceptives

- **Nextstellis (drospirenone/estetrol)** — Mayne Pharma; first estetrol-based OC 2021
- **Slynd (drospirenone 4 mg)** — Exeltis; progestin-only with longer window
- **Lo Loestrin Fe** — continuing mature market

### 6.3 Long-acting reversible contraception (LARC)

- **Copper IUD:** ParaGard — up to 10 years
- **Hormonal IUD:** Mirena, Kyleena, Liletta, Skyla — LNG-releasing
- **Implant:** Nexplanon etonogestrel — 3 years
- **Injectable:** Depo-Provera medroxyprogesterone acetate

### 6.4 Vaginal ring

- **NuvaRing** — generic
- **Annovera (segesterone/EE)** — Population Council; 1-year reusable ring

### 6.5 Emergency contraception

- **Plan B** (levonorgestrel OTC)
- **Ella (ulipristal acetate)** — Rx only
- **Copper IUD** — most effective EC

---

## §7. Fertility + ART Landscape

### 7.1 Recombinant gonadotropins

- **Gonal-F (follitropin alfa)** — Merck KGaA/EMD Serono
- **Follistim (follitropin beta)** — Organon
- **Pergoveris (follitropin/lutropin)** — Merck KGaA
- **Menopur (menotropins)** — Ferring

### 7.2 Ovulation trigger + support

- **Ovidrel (choriogonadotropin alfa)** — trigger
- **Pregnyl** — hCG
- **Crinone, Endometrin** — progesterone luteal support

### 7.3 GnRH antagonists for IVF (cross-reference `task-modality-peptide.md`)

- **Cetrotide (cetrorelix)** — Merck KGaA
- **Orgalutran/Antagon (ganirelix)** — Organon

### 7.4 Expanding access

- State-level IVF insurance mandates (21 states US as of 2024)
- Employer coverage expansion
- Single embryo transfer (SET) trending
- PGT-A preimplantation genetic testing routine

---

## §8. Postmenopausal Osteoporosis — Partial Overlap with `task-modality-peptide.md`

Cross-reference `task-modality-peptide.md` for teriparatide/abaloparatide PTH analogs; this section adds women's-health framing.

### 8.1 Anti-resorptive

- **Bisphosphonates:** alendronate (Fosamax — generic), risedronate (Actonel), ibandronate (Boniva), zoledronic acid (Reclast — annual IV)
- **RANKL inhibitor:** Prolia (denosumab) — Amgen; biosimilar competition beginning 2025

### 8.2 Anabolic agents

- **Forteo (teriparatide)** — PTH 1-34; generic + biosimilar competition
- **Tymlos (abaloparatide)** — PTHrP analog
- **Evenity (romosozumab)** — Amgen + UCB; sclerostin mAb; severe osteoporosis

### 8.3 SERMs

- **Evista (raloxifene)** — generic
- **Duavee** — conjugated estrogens/bazedoxifene
- **Osphena (ospemifene)** — dyspareunia indication

---

## §9. Gynecologic Oncology Intersection (cross-reference `task-ta-oncology.md`)

### 9.1 PARP inhibitors in ovarian cancer
- Lynparza (olaparib), Zejula (niraparib), Rubraca (rucaparib), Talzenna (talazoparib)
- Breast cancer extension (BRCA+ mBC)

### 9.2 Endometrial cancer
- Jemperli (dostarlimab) + carboplatin/paclitaxel — dMMR endometrial Phase 3 RUBY 2023
- Keytruda + lenvatinib (Lenvima)
- mirvetuximab soravtansine (Elahere) — FRα+ ovarian ADC

### 9.3 Cervical cancer
- HPV vaccine primary prevention (Gardasil 9)
- Tisotumab vedotin (Tivdak) — TF ADC cervical 2021
- Pembrolizumab combinations

---

## §10. Türkiye Kadın Sağlığı Ekosistemi

### 10.1 TİTCK + SGK SUT

- **TİTCK onay** — çoğu kadın sağlığı ilacı EMA reliance pathway
- **SGK SUT** — kontrasepsiyon + HRT + endometriozis ilaçları SUT EK-4/C listelerinde
- **Oral kontraseptif geri ödeme** — endikasyon spesifik (kontrasepsiyon olarak değil, menoraji/endometriozis vs. tanılar ile); OTC olarak da satılmakta
- **HRT** — menopozal VMS için sınırlı SUT; Veozah + Lynkuet henüz SUT dışı (özel ödeme)
- **Endometriozis/myom GnRH antagonisti** — Orilissa + Myfembree TİTCK değerlendirmesi; SUT listesinde değil
- **PPD için Zurzuvae** — TİTCK değerlendirme aşamasında (2026 cutoff); SUT dışı

### 10.2 Türk yerli kadın sağlığı jenerik ekosistemi

- Oral kontraseptif (drospirenone-EE, desogestrel-EE, levonorgestrel-EE) yerli jenerik yaygın
- HRT estradiol/progesterone jenerik + transdermal yerli üretim
- Mifepristone + misoprostol SGK'da prosedür bazlı
- IVF ilaçları Merck KGaA/Organon/Ferring ithalat dominant (rekombinant ürünler yerli üretim sınırlı)
- **Yerli sponsor ekosistemi:** Abdi İbrahim, Deva, Sanovel, Bilim İlaç, Pharmactive, Mustafa Nevzat-Pfizer, Eczacıbaşı

### 10.3 Türkiye üreme sağlığı sistemi

- **IVF SGK geri ödeme:** evli çiftler, sınırlı sayıda deneme (3 deneme + yaş şartları)
- **Kordon kanı + embriyo saklama:** özel kliniklerde özel ödeme
- **Kadın doğum uzmanı + üreme endokrinolojisi** merkezleri: tertiary üniversite hastaneleri + büyük özel IVF merkezleri

### 10.4 Türkiye kadın sağlığı epidemiyoloji

- Doğurganlık hızı 2024 ~1.5 (yenileme düzeyi altında)
- Preterm doğum oranı ~10-11% (gelişmiş ülkelerle benzer)
- Postpartum depresyon yaygınlığı Türkiye'de %15-25 tahmin (çalışmalar heterojen)
- HPV aşısı Sağlık Bakanlığı programında değil (2024 cutoff), özel ödeme (Gardasil 9)
- Meme kanseri + serviks kanseri tarama programları mevcut

---

## §11. Stakeholder-Spesifik Analytical Framework

### 11.1 Big Pharma women's health sponsors (Organon, Pfizer, Bayer, AbbVie, Astellas, Myovant/Sumitomo)
- Post-divestiture category positioning
- Novel mechanism commercialization (NK3R, NAS)
- Specialty vs primary care targeting

### 11.2 Biotech women's health sponsors (Sage, Mayne, Perrigo OTC)
- Narrow indication commercial execution
- Payer coverage pathway for novel mechanism
- Direct-to-consumer + advocacy engagement

### 11.3 Fertility specialty sponsors (Merck KGaA, Ferring, Organon)
- Specialty clinic channel
- Patient journey support
- International market access

### 11.4 Payer paydaşları
- Contraception coverage political dynamics
- PPD access coverage evolution
- Menopause non-hormonal therapy coverage
- IVF mandate expansion

### 11.5 Klinisyen paydaşları
- OB/GYN vs PCP prescriber dynamics
- Menopause Society (NAMS) guideline alignment
- ACOG practice bulletins

### 11.6 Hasta paydaşları
- Stigma (PPD, menopause, endometriosis)
- OTC access expansion (Opill)
- Out-of-pocket cost for non-covered

### 11.7 Advocacy + policy paydaşları
- National Women's Health Resource Center
- Society for Women's Health Research
- March of Dimes (maternal/infant health)
- Planned Parenthood access advocacy

---

## §12. Confidence Stamping for Women's Health Claims

| Claim type | Default confidence |
|---|---|
| FDA / EMA approval date + indication | **High** (statutory) |
| Pivotal trial efficacy (Pearl Index, VMS reduction, HAMD-17) | **High** (peer-reviewed) |
| PLLR pregnancy/lactation labeling | **High** (label primary) |
| Fezolinetant hepatotoxicity FDA Boxed Warning | **High** (FDA safety communication) |
| Real-world fertility treatment success rates | **Medium** (SART registry) |
| Menopause HRT risk-benefit | **Medium** (WHI context-dependent) |
| PPD underdiagnosis rates | **Medium** (varying estimates) |
| Confidential contraceptive generic pricing | **Low** |

---

## §13. Forbidden Patterns

- ❌ Treating WHI findings as universal contraindication (age + duration + formulation matter)
- ❌ Conflating PPD with MDD (different endpoint framework, different regulatory approval)
- ❌ Generalizing fezolinetant hepatotoxicity to entire non-hormonal VMS class prematurely
- ❌ Assuming all PPD patients require Zurzuvae (SSRI remains first-line in many algorithms)
- ❌ Strategic recommendations for specific sponsors without T6-Defense activation
- ❌ Oversimplifying contraceptive effectiveness (perfect-use vs typical-use distinction critical)
- ❌ Extrapolating US Opill OTC transition globally (other jurisdictions differ)

---

## §14. Versioning & Changelog

- **v4.0.0 (2026-04-16):** Initial release. Layer 2 Women's Health / Reproductive Medicine TA template covering: distinguishing features (historical underinvestment + 1993 NIH Revitalization Act reversal + pregnancy teratogenicity discipline + divestment era Organon 2021 + payer political dynamics); FDA Pregnancy and Lactation Labeling Rule (PLLR) 2015 effective replacing A/B/C/D/X categories with narrative Pregnancy + Lactation + Females/Males of Reproductive Potential subsections; women's health endpoint frameworks (Pearl Index contraception + menstrual blood loss HMB/endometriosis + VMS frequency-severity + HAMD-17 PPD + Pearl Index; fracture + BMD osteoporosis; ongoing pregnancy + live birth ART); postpartum depression paradigm shift (pre-2019 off-label SSRI + Zulresso brexanolone Sage FDA 2019-03-19 IV 60h infusion REMS + commercial underperformance; **Zurzuvae zuranolone Sage+Biogen FDA 2023-08-04 first oral PPD neuroactive steroid GABA-A PAM 50mg QD × 14 days rapid onset Day 3 primary Day 15 HAMD-17 + DEA Schedule IV October 2023 + SKYLARK + ROBIN pivotal + WAC $15,900 14-day course + commercial launch Dec 14 2023 + MDD CRL simultaneous + boxed warning driving 12hr + limited breastfeeding data + EC EU approval September 2025 + MHRA UK August 2025**); menopause pharmacotherapy revolution (WHI 2002 CVD/breast cancer HRT market contraction + age-dependent re-analysis; **Veozah fezolinetant Astellas FDA 2023-05-12 first NK3R antagonist for VMS + SKYLIGHT 1/2/4 pivotal + FDA Boxed Warning 2024 hepatotoxicity liver enzyme monitoring**; Lynkuet elinzanetant Bayer FDA 2025 NK1/NK3 dual + OASIS 1/2/3 pivotal; traditional HRT estradiol transdermal Menopause Society-recommended + Bijuva bioidentical 2018 + Duavee tissue-selective); GnRH antagonist class endometriosis + uterine fibroids (Orilissa elagolix AbbVie+Neurocrine FDA 2018-07-23 first oral + Oriahnn add-back combination 2020 uterine fibroids; Myfembree Myovant+Pfizer relugolix+E2+NETA FDA 2021 HMB+fibroids + 2022 endometriosis + Ryeqo EMA 2021); contraception landscape (**Opill norgestrel Perrigo/HRA Pharma FDA 2023-07 OTC approval first OTC oral contraceptive US + nationwide 2024 access**; Nextstellis drospirenone/estetrol Mayne Pharma 2021 first estetrol OC; Slynd progestin-only longer window; LARC Mirena/Kyleena/Liletta/Skyla/Nexplanon/Depo-Provera; Annovera 1-yr reusable ring Population Council; Plan B + Ella emergency); fertility + ART (rGT Gonal-F + Follistim + Pergoveris + Menopur; trigger Ovidrel; GnRH antag Cetrotide + Orgalutran IVF protocols cross-reference task-modality-peptide.md; state IVF mandates 21 states US 2024 + employer coverage + SET + PGT-A routine); postmenopausal osteoporosis (bisphosphonate generic + Prolia denosumab biosimilar 2025 + Forteo biosimilar + Tymlos + **Evenity romosozumab** Amgen+UCB severe osteoporosis); gynecologic oncology cross-reference task-ta-oncology.md (PARP in ovarian + Jemperli dMMR endometrial RUBY 2023 + Tivdak tisotumab vedotin TF ADC cervical 2021 + Elahere mirvetuximab FRα ovarian ADC); Türkiye ekosistemi (TİTCK EMA reliance + SGK SUT EK-4C kadın sağlığı + OC endikasyon-bazlı geri ödeme + HRT sınırlı SUT + Veozah/Lynkuet/Orilissa/Myfembree/Zurzuvae SUT dışı özel ödeme + yerli jenerik OC/HRT + IVF SGK çift + sınırlı deneme + TFR 1.5 2024 + PPD prevalans %15-25 + HPV aşısı Sağlık Bakanlığı programı dışı özel ödeme). New manifest gate G47. Cross-references task-modality-peptide.md (GnRH analog class + teriparatide/abaloparatide + fertility peptides), task-modality-smallmol.md (oral contraceptive + zuranolone + fezolinetant small molecule), task-ta-oncology.md (gynecologic oncology + PARP + ADC), task-ta-cns.md (PPD neuroactive steroid overlap + psychiatry), task-ta-rare-disease.md (rare peripartum conditions), analytics-framework.md (women's health NPV), api-integrations.md (FDA women's health labeling + ACOG guidelines).
