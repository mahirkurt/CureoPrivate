---
name: pharmaintel
description: >
  Global pharma commercial, regulatory, pipeline, catalyst intel. Free-tier sources (FDA, Orange/
  Purple Book, FAERS, EMA, ClinicalTrials.gov, SEC EDGAR, NICE, ICER) + MCPs (PubMed, Clinical
  Trials, bioRxiv, Consensus, Exa, Tavily, AdisInsight, TİTCK, ThoughtSpot/IQVIA MIDAS).
  Two-source triangulation, provenance-stamped output. v8.0.0 adds Türkiye Ürün Geliştirme:
  4-channel stack (TİTCK + MIDAS 36-country + AdisInsight + openFDA) with 7 modules — generic
  feasibility, fiyat tavanı, cross-country sizing, eşdeğer grup, biowaiver/BCS, withdrawal,
  Reliance target. USE for: şirket analizi, asset profile, modalite (ADC, CAR-T, bispecific, RNA,
  gene therapy, GLP-1), M&A/licensing, catalyst watch (PDUFA, CHMP, readouts, AdComm, earnings),
  head-to-head, patent landscape, FDA/EMA/TİTCK durumu, ürün geliştirme fizibilitesi, jenerik/
  biyobenzer fizibilitesi, IQVIA MIDAS pazar kıyası, fiyat tavanı, eşdeğer grup, in-licensing,
  market access, Reliance target ID, biowaiver. Complements medsearch + pharmapatent.
---

# pharmaintel v1.0 — Pharmaceutical Commercial & Regulatory Intelligence Orchestrator

> **Plugin entegrasyon notu (rxpraxis).** Bu skill rxpraxis süiti altında çalışırken connector envanteri, fallback zincirleri ve tek-sefer TİTCK/MIDAS disiplini için [../../CONNECTORS.md](../../CONNECTORS.md) ve [../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md) **NORMATİFTİR**. Aşağıdaki 4-kanal stack (Channel A TİTCK · B ThoughtSpot/MIDAS · C AdisInsight · D openFDA) ve `references/sources-catalog.md`, standalone kullanım için korunmuştur; süit bağlamında çakışma hâlinde plugin sözleşmesi üstündür.


## Raison d'être

`medsearch` orchestrates **scientific/clinical evidence**: what does the hakemli literatür söylüyor. `pharmaintel` orchestrates **commercial, regulatory, pipeline, and catalyst intelligence**: who owns the asset, where does it stand regulatorily, what is the pipeline, what are the deal terms, when is the next readout, what does the competitive landscape look like. The two are complementary — in a typical deep-dive the pharmaintel layer establishes *the question's commercial/regulatory frame*, while medsearch answers *the scientific evidence base underneath it*.

This skill is **claude.ai-native** and strictly **free-tier**: it does NOT depend on Bloomberg, Citeline, Cortellis, Evaluate Pharma Premium, IQVIA MIDAS, Patsnap, Refinitiv, FactSet, AlphaSense, STAT Plus, or any paid enterprise platform. Those are catalogued as "inaccessible (subscription)" in `references/sources-catalog.md` for explicit acknowledgement of limitations.

---

## Mandatory Execution Protocol

### Step 0 — Load the routing layer

Before any tool call, read:

```
view /home/claude/pharmaintel/references/sources-catalog.md
view /home/claude/pharmaintel/references/triangulation.md
view /home/claude/pharmaintel/references/query-patterns.md
```

These three are **always loaded** — they define the source universe, the triangulation contract, and the MCP/tool query templates. Subsequent task-specific references are loaded on demand per §Task Routing.

### Step 1 — Classify the query into a Task Type

Read the opening user message and match it against the eight canonical task types:

| Task ID | Trigger pattern | Load next |
|---------|----------------|-----------|
| **T1 — Company Deep-Dive** | "analyze Roche / Pfizer / Vertex / [ticker]", "profile this biotech", "company analysis", "şirket analizi" | `references/task-company.md` |
| **T2 — Asset/Molecule Profile** | "profile pembrolizumab / trastuzumab deruxtecan / [INN]", "status of [drug]", "molekül profili" | `references/task-asset.md` |
| **T3 — Modality Landscape** | "ADC landscape", "CAR-T pipeline", "bispecific antibodies", "GLP-1 competitive", "modalite peyzajı" | `references/task-modality.md` |
| **T4 — Deal/M&A Dissection** | "[Acquirer] acquisition of [Target]", "license deal between X and Y", "deal analizi" | `references/task-deal.md` |
| **T5 — Catalyst Watch** | "upcoming PDUFA", "Q3 readouts", "AdComm schedule", "katalizör takvimi" | `references/task-catalyst.md` |
| **T6 — Head-to-Head Comparison** | "X vs Y", "head-to-head", "competitive benchmark", "hangisi daha iyi" | `references/task-comparison.md` |
| **T6-Defense — Sponsor-Specific Competitive Defense Sub-Mode** | "[Sponsor X] cephesinden", "[Sponsor X] için competitive defense", "from [Sponsor X]'s perspective", "defense playbook for [Sponsor X]", "T6-Defense:" task tag prefix, "biz [Sponsor X] olarak" | `references/task-comparison-defense.md` (sub-mode of T6; selective 2-of-8 G22 override; mandatory symmetric framing; activation EXPLICIT only) |
| **T7 — Regulatory Status Snapshot** | "is X FDA-approved in Y indication", "EMA status of Z", "FDA/EMA durumu" | inline (SKILL.md §T7) |
| **T8 — Pipeline Inventory** | "list all [sponsor] assets in phase 2+", "pipeline of [company]", "pipeline haritası" | `references/task-company.md` §Pipeline |

**Layer triggers (additive — load alongside task-specific reference):**

Layer'lar iki farklı yoldan tetiklenir: **(A) Explicit triggers** — kullanıcının query'sinde keyword görünür; **(B) Semantic auto-triggers** — task içeriği belirli bir profili karşılarsa Claude proaktif olarak yükler. Her iki yol da geçerlidir; ikisi paralel değerlendirilmelidir.

**(A) Explicit triggers (keyword-based):**

| Layer | Trigger pattern | Load additionally |
|---|---|---|
| **HTA deep-dive** | "NICE", "CADTH", "G-BA", "IQWiG", "HAS SMR/ASMR", "PBAC", "reimbursement", "payer", "ICER threshold", "cost-effectiveness", "geri ödeme" | `references/task-hta.md` |
| **PMDA (Japanese regulatory)** | "PMDA", "MHLW", "Chuikyo", "中医協", "薬価", "Sakigake", "Japan approval", "Japanese label", "承認", "審査報告書" | `references/sub-protocol-pmda.md` |
| **NMPA (Chinese regulatory)** | "NMPA", "CDE", "国家药品监督管理局", "药品审评中心", "NRDL", "国家医保目录", "NHSA", "国家医保局", "国谈", "VBP", "集中带量采购", "集采", "优先审评", "突破性治疗", "附条件批准", "China launch", "中国上市", "GBA Hong Kong-Macao Drug Connect", "Hainan Boao Lecheng" | `references/sub-protocol-nmpa.md` |
| **Türkiye (TİTCK + SGK)** | "TİTCK", "SGK", "SUT", "Sağlık Uygulama Tebliği", "Türk farmasötik", "EK-4A", "EK-4D", "kullanım protokolü", "MEDULA", "Reliance Pathway Türkiye", "Hızlı Erken Erişim Programı", "şahsi ithalat", "isimsel ithalat", "Türk yerli sponsor analizi", "AİFD", "TİSD", "Türk RWE registry", "Türkiye launch" | `references/sub-protocol-turkey.md` |
| **Türkiye Ürün Geliştirme (Product Development)** | "ürün geliştirme fizibilitesi", "jenerik fizibilite", "biyobenzer fizibilitesi", "Türkiye ürün giriş kararı", "in-licensing değerlendirmesi", "eşdeğer grup analizi", "fiyat tavanı simülasyonu", "5-ülke fiyat referansı", "ATC sınıf doygunluğu", "withdrawal trend", "ruhsat iptal trendi", "IQVIA MIDAS Türkiye", "IQVIA MIDAS 36 ülke", "Türkiye pazar büyüklüğü", "ülkeler-arası pazar kıyaslaması", "biowaiver", "BCS sınıflandırması", "dissolution profile", "Q1/Q2", "Reliance hedef analizi", "TR-PD feasibility", "generic feasibility scorecard", "Türkiye Reliance pathway candidate", "TİTCK barkod analizi", "openFDA + TİTCK bridge" | `references/sub-protocol-product-development-tr.md` (composes with sub-protocol-turkey.md) |
| **Catalyst Watch** | "PDUFA", "PDUFA goal date", "FDA action date", "FDA decision", "CHMP opinion", "EC adoption", "AdComm", "AdCom", "ODAC", "Advisory Committee", "readout", "topline", "primary completion", "earnings call", "guidance", "analyst day", "investor day", "katalist", "milestone", "katalizör", "Type II variation", "RTOR", "Priority Review", "Breakthrough Therapy", "Sakigake", "BTD", "background package", "briefing document" | `references/sub-protocol-catalyst-watch.md` |
| **Biosimilar / Follow-on Biologics (T3 modality template)** | "biosimilar", "biosimilars", "biyobenzer", "follow-on biologic", "FOB", "subsequent entry biologic", "SEB", "351(k)", "BPCIA", "Purple Book", "interchangeability designation", "interchangeable biological product", "patent dance", "first interchangeable exclusivity", "biosimilar uptake", "biosimilar erosion", "biosimilar discount", "EMA biosimilar guideline", "MHRA biosimilar", "tailored clinical approach biosimilar", "biyoeşdeğer grup", "biyobenzer SUT" | `references/task-modality-biosimilar.md` (layers onto generic task-modality.md) |
| **Antibody-Drug Conjugates (T3 modality template)** | "ADC", "ADCs", "antibody-drug conjugate", "antikor-ilaç konjugatı", "DAR", "drug-antibody ratio", "linker chemistry", "cleavable linker", "non-cleavable linker", "payload class", "DM1", "DM4", "MMAE", "MMAF", "deruxtecan", "DXd", "calicheamicin", "PBD", "exatecan", "TOP1 inhibitor payload", "tubulin inhibitor payload", "ILD ADC", "bystander effect", "Enhertu", "Kadcyla", "Trodelvy", "Polivy", "Padcev", "Adcetris", "Tivdak", "Elahere", "Datroway", "Blenrep" | `references/task-modality-adc.md` (layers onto generic task-modality.md) |
| **Cell & Gene Therapy (T3 modality template)** | "CAR-T", "CAR T", "kimerik antijen reseptör", "TCR-T", "T cell receptor therapy", "NK cell therapy", "TIL", "tumor infiltrating lymphocyte", "gene therapy", "gen tedavisi", "gene editing", "CRISPR therapy", "base editing", "prime editing", "lentiviral", "AAV", "ATMP", "advanced therapy medicinal product", "RMAT", "Regenerative Medicine Advanced Therapy", "ATMP regulation", "Regulation (EC) 1394/2007", "Office of Therapeutic Products", "OTP", "Yescarta", "Kymriah", "Tecartus", "Breyanzi", "Abecma", "Carvykti", "Casgevy", "Lyfgenia", "Luxturna", "Zolgensma", "Hemgenix", "Roctavian", "Elevidys" | `references/task-modality-cellgene.md` (layers onto generic task-modality.md) |
| **RNA Therapeutics (T3 modality template)** | "mRNA therapy", "mRNA vaccine", "siRNA", "small interfering RNA", "ASO", "antisense oligonucleotide", "antisens oligonükleotid", "RNAi", "RNA interference", "self-amplifying RNA", "saRNA", "circRNA", "miRNA mimic", "RNA editing", "ADAR editing", "LNP", "lipid nanoparticle", "GalNAc", "GalNAc conjugate", "intrathecal ASO", "Comirnaty", "Spikevax", "Patisiran", "Onpattro", "Givlaari", "Oxlumo", "Leqvio", "inclisiran", "Amvuttra", "vutrisiran", "Spinraza", "nusinersen", "Tofersen", "Eteplirsen" | `references/task-modality-rna.md` (layers onto generic task-modality.md) |
| **Radiopharmaceuticals / Radioligand Therapy (T3 modality template)** | "radiopharmaceutical", "radioligand therapy", "RLT", "targeted radionuclide therapy", "TRT", "theranostic", "theranostics", "targeted alpha therapy", "TAT", "radyofarmasötik", "radyoligand tedavisi", "Lu-177", "lutetium-177", "Ac-225", "actinium-225", "I-131", "Y-90", "Ga-68", "F-18", "PSMA-PET", "DOTATATE PET", "Pluvicto", "Lutathera", "Xofigo", "radium-223", "Zevalin", "NETSPOT", "Locametz", "Illuccix", "Pylarify", "Posluma", "RayzeBio", "ITM Isotopen", "Curium", "Lantheus" | `references/task-modality-radiopharm.md` (layers onto generic task-modality.md) |
| **Small Molecule Generic Ecosystem (T3 modality template)** | "small molecule", "küçük molekül", "NCE", "new chemical entity", "Hatch-Waxman", "ANDA", "abbreviated new drug application", "Orange Book", "Paragraph IV", "Para IV", "ANDA exclusivity", "180-day exclusivity", "first-to-file", "FTF", "NCE exclusivity", "5-year exclusivity", "3-year exclusivity", "orphan exclusivity", "pediatric exclusivity", "GAIN Act", "AB-rated", "AA-rated", "therapeutic equivalence", "DAW", "dispense as written", "automatic substitution", "30-month stay", "patent challenge", "authorized generic", "AG launch", "505(b)(2)", "VBP", "volume-based procurement", "eşdeğer grup jenerik" | `references/task-modality-smallmol.md` (layers onto generic task-modality.md) |
| **Peptide Therapeutics (T3 niche modality template)** | "peptide therapeutic", "therapeutic peptide", "peptit ilaç", "GLP-1", "GLP-1 receptor agonist", "GLP-1/GIP dual agonist", "incretin mimetic", "GnRH analog", "GnRH agonist", "GnRH antagonist", "somatostatin analog", "SSA", "PTH analog", "Ozempic", "Wegovy", "Rybelsus", "semaglutide", "Mounjaro", "Zepbound", "tirzepatide", "Trulicity", "dulaglutide", "liraglutide", "exenatide", "leuprolide", "goserelin", "octreotide", "lanreotide", "pasireotide", "teriparatide", "abaloparatide", "fatty acid acylation", "lipidation peptide", "SPPS", "Fmoc chemistry", "solid-phase peptide synthesis", "retatrutide", "CagriSema", "survodutide" | `references/task-modality-peptide.md` (layers onto generic task-modality.md) |
| **Microbiome Therapeutics / Live Biotherapeutic Products (T3 niche modality template)** | "microbiome therapeutic", "microbiome-based therapeutic", "MBT", "live biotherapeutic product", "LBP", "fecal microbiota transplant", "FMT", "fekal mikrobiyota nakli", "designed microbial consortium", "rationally defined consortium", "Rebyota", "RBX2660", "Vowst", "SER-109", "VE303", "NTCD-M3", "ADS024", "MET-2", "rCDI", "recurrent C. difficile", "OpenBiome", "stool bank" | `references/task-modality-microbiome.md` (layers onto generic task-modality.md) |
| **Photodynamic Therapy / PDT (T3 niche modality template)** | "photodynamic therapy", "PDT", "fotodinamik tedavi", "photochemotherapy", "photodynamic diagnosis", "PDD", "fluorescence-guided surgery", "FGS", "porfimer sodium", "Photofrin", "5-aminolevulinic acid", "5-ALA", "Levulan", "Ameluz", "methyl aminolevulinate", "MAL", "Metvix", "verteporfin", "Visudyne", "temoporfin", "Foscan", "padeliporfin", "Tookad", "Gleolan", "talaporfin", "intraoperative photodiagnosis", "photodynamic ablation", "photoimmunotherapy", "Akalux" | `references/task-modality-pdt.md` (layers onto generic task-modality.md) |
| **Oncolytic Viruses (T3 niche modality template)** | "oncolytic virus", "oncolytic viral therapy", "oncolytic viroterapy", "OV", "viral immunotherapy", "onkolitik virüs", "T-VEC", "talimogene laherparepvec", "Imlygic", "nadofaragene firadenovec", "Adstiladrin", "teserpaturev", "Delytact", "G47Δ", "RP-1", "vusolimogene oderparepvec", "Oncorine", "H101", "Pexa-Vec", "JX-594", "Reolysin", "pelareorep", "CG0070", "cretostimogene grenadenorepvec", "HSV-1 oncolytic", "adenoviral oncolytic", "vaccinia oncolytic", "reovirus oncolytic", "Newcastle disease virus" | `references/task-modality-oncolytic.md` (layers onto generic task-modality.md) |
| **Fusion Proteins (T3 niche modality template)** | "fusion protein", "Fc-fusion", "Fc fusion", "Fc-Ig", "Fc-fusion biologic", "füzyon protein", "trap protein", "decoy receptor", "Enbrel", "etanercept", "Orencia", "abatacept", "Nulojix", "belatacept", "Eylea", "aflibercept", "Eylea HD", "Zaltrap", "Trulicity", "dulaglutide", "Adynovate", "Eloctate", "efmoroctocog alfa", "Alprolix", "eftrenonacog alfa", "Arcalyst", "rilonacept", "Nplate", "romiplostim", "VEGF trap", "TNF receptor decoy", "IL-1 trap", "CTLA-4-Ig", "peptibody", "FcRn-mediated half-life", "-cept INN suffix" | `references/task-modality-fusion.md` (layers onto generic task-modality.md) |
| **Oncology TA (T3 Layer-2 therapeutic area template)** | "oncology", "cancer", "onkoloji", "kanser", "tumor", "tümör", "solid tumor", "hematologic malignancy", "NCCN", "ESMO", "ASCO", "ODAC", "Project Optimus", "Project FrontRunner", "OCE", "Oncology Center of Excellence", "OS", "PFS", "ORR", "DoR", "DFS", "RFS", "MRD", "pCR", "RECIST", "iRECIST", "Lugano", "IMWG", "ICI", "checkpoint inhibitor", "anti-PD-1", "anti-PD-L1", "anti-CTLA-4", "MSI-H", "dMMR", "TMB-H", "tumor-agnostic", "accelerated approval oncology", "NSCLC", "mBC", "TNBC", "HER2+", "HER2-low", "mCRC", "mCRPC", "mUC", "DLBCL", "multiple myeloma" | `references/task-ta-oncology.md` (layers onto generic task-modality.md + applicable modality template — ORTHOGONAL TO modality layer) |
| **Autoimmune / Immunology TA (T3 Layer-2 therapeutic area template)** | "autoimmune", "immunology", "I&I", "otoimmün", "inflammation", "RA", "psoriasis", "PsA", "AS", "UC", "Crohn's", "IBD", "MS", "SLE", "lupus", "AD", "atopik dermatit", "asthma", "severe asthma", "HS", "alopecia areata", "vitiligo", "anti-TNF", "IL-17 inhibitor", "IL-23 inhibitor", "JAK inhibitor", "BTK inhibitor", "S1P modulator", "anti-CD20", "anti-IgE", "Humira", "Enbrel", "Remicade", "Cosentyx", "Taltz", "Skyrizi", "Tremfya", "Stelara", "Dupixent", "Rinvoq", "Xeljanz", "Bimzelx", "ORAL Surveillance", "ACR", "EULAR", "PASI", "DAS28", "Mayo score" | `references/task-ta-autoimmune.md` (layers onto generic task-modality.md + applicable modality template — ORTHOGONAL TO modality layer) |
| **Rare Disease / Orphan TA (T3 Layer-2 therapeutic area template)** | "rare disease", "orphan drug", "orphan indication", "nadir hastalık", "ultra-rare", "Orphan Drug Act", "ODA", "7-year exclusivity", "orphan exclusivity", "PRV", "priority review voucher", "rare pediatric disease", "RPD", "Orphan Designation EMA", "5 per 10000", "200000 ODA", "natural history", "external control", "single-arm", "Bayesian adaptive", "Gaucher", "Fabry", "Pompe", "MPS", "DMD", "SMA", "hATTR", "HoFH", "PKU", "acromegaly", "Wilson disease", "homocystinuria", "hypophosphatasia", "Trikafta", "Kaftrio", "CFTR modulator", "rare blood disorder", "hemoglobinopathy" | `references/task-ta-rare-disease.md` (layers onto generic task-modality.md + applicable modality template — ORTHOGONAL TO modality layer) |
| **CNS / Neurology TA (T3 Layer-2 therapeutic area template)** | "CNS", "central nervous system", "neurology", "nöroloji", "neuropsychiatry", "psychiatry", "psikiyatri", "neurodegeneration", "Alzheimer", "AD", "Parkinson", "Huntington", "ALS", "FTD", "MS", "multiple sclerosis", "epilepsy", "migraine", "CGRP", "stroke", "depression", "MDD", "TRD", "schizophrenia", "bipolar", "SMA", "DMD", "myasthenia gravis", "MG", "CIDP", "Leqembi", "lecanemab", "Aduhelm", "Kisunla", "donanemab", "Spinraza", "nusinersen", "Zolgensma", "risdiplam", "tofersen", "Qalsody", "Ocrevus", "Kesimpta", "Spravato", "esketamine", "CDR-SB", "ADAS-Cog", "ALSFRS-R", "EDSS", "MDS-UPDRS", "PANSS", "HAM-D", "MADRS", "ARIA", "ApoE4" | `references/task-ta-cns.md` (layers onto generic task-modality.md + applicable modality template — ORTHOGONAL TO modality layer) |
| **Cardiometabolic (Metabolic / CV / Renal) TA (T3 Layer-2 therapeutic area template)** | "metabolic", "cardiometabolic", "kardiyometabolik", "endocrinology", "endokrinoloji", "cardiology", "kardiyoloji", "nephrology", "T2D", "type 2 diabetes", "T1D", "obesity", "obezite", "ASCVD", "HFrEF", "HFpEF", "heart failure", "hypertension", "hyperlipidemia", "FH", "HoFH", "Lp(a)", "CKD", "MASH", "NASH", "NAFLD", "MASLD", "GLP-1 RA", "GLP-1/GIP", "SGLT2i", "SGLT2 inhibitor", "DPP-4", "statin", "PCSK9", "CVOT", "MACE", "CV outcome trial", "Ozempic", "Wegovy", "Mounjaro", "Zepbound", "Trulicity", "Jardiance", "Farxiga", "Rezdiffra", "resmetirom", "Leqvio", "inclisiran", "Repatha", "Praluent", "Entresto", "Kerendia", "finerenone", "Tzield", "teplizumab" | `references/task-ta-metabolic.md` (layers onto generic task-modality.md + applicable modality template — ORTHOGONAL TO modality layer) |
| **Sponsor Sweep (Top-30 corporate sites)** | Any named sponsor, named asset with known sponsor, competitive landscape, deal analysis, catalyst watch for specific sponsors — see sub-protocol §Trigger rules for full list | `references/sub-protocol-sponsor-sweep.md` |
| **Label & Post-Marketing Safety** | Any approved asset in scope (T2/T3/T5/T6/T7); medical affairs / clinician briefing / KOL engagement use case; label revision event; FAERS signal inquiry | `references/sub-protocol-label.md` |
| **BD Due Diligence (v5.0.0)** | "BD due diligence", "target assessment", "acquisition target", "licensing evaluation", "option agreement", "royalty financing", "co-development", "pre-LOI assessment", "ticaret DD", "risk register", "M&A due diligence", "hedef şirket değerlendirmesi", "lisanslama değerlendirmesi" | `references/sub-protocol-bd-dd.md` (auto-activates sub-protocol-provenance) |
| **Forensic Provenance (v5.0.0)** | "forensic-grade report", "evidence bundle", "chain-of-custody", "UBO walkthrough", "beneficial ownership verification", "kanıt zinciri", "provenance-verified analysis", "sanctions screening with documentation", "TİTCK defense forensic", "historical claim archive", "deleted pipeline documentation" | `references/sub-protocol-provenance.md` (consumes `provenance-engine.md` + `evidence-object-schema.md` + `ubo-source-hierarchy.md` + `scripts/provenance-engine/`) |

**(B) Semantic auto-triggers (content-based, applied during Step 1g):**

Aşağıdaki tablo, task içeriğinin doğal özelliklerinden hangi layer'ların **otomatik yüklenmesi gerektiğini** kodlar. Bu kullanıcının layer-tetik kelimesi hatırlamasını gerektirmez.

| Semantic profile | Auto-load layers | Rationale |
|---|---|---|
| **Rare disease** (orphan indication; prevalence <200K US OR <5/10K EU) | task-hta.md | Ultra-rare assets her zaman HTA tartışmalıdır; ICER/QALY thresholds özel uygulanır (NICE HST, end-of-life, PBAC severity premium). Fiyatlandırma profili payer-sensitive. |
| **Gene therapy** (AAV, lentivirus, ex-vivo CRISPR, in-vivo editing) | task-hta.md + sponsor-sweep + label | Tek-doz milyon-dolar fiyat zorunlu HTA + outcome-based contract analizi gerektirir; uzun-dönem güvenlik label monitorizasyonu kritik; sponsor-spesifik IR commercial detay vital. |
| **Cell therapy** (CAR-T, NK, TIL, allogeneic, autologous) | task-hta.md + label (REMS focus) | Production capacity + REMS mandatory program + site-of-care kısıtlamaları → HTA + label ortak gerekli. |
| **Major Japanese sponsor named as the asset's actual developer** (Takeda, Chugai, Daiichi Sankyo, Eisai, Astellas, Otsuka) AND query has Japan regulatory/commercial scope — NOT triggered by user's relationship to Japan | sub-protocol-pmda | Bu sponsorların pivotal asset'leri PMDA-primer dokümante edilir; English summary yetersiz. Trigger source: query content (asset's actual sponsor + Japan scope). |
| **Major Chinese sponsor named as the asset's actual developer** (BeOne, Innovent, Junshi, Hengrui, Sino Biopharm, Akeso, RemeGen, Hutchmed, etc.) AND query has China regulatory/commercial scope, OR query explicitly focuses on a multinational sponsor's China operation | `sub-protocol-nmpa.md` | NMPA review reports + NRDL listing decisions + VBP exposure are Mandarin-primary; English summary lagged 2-8 weeks. Trigger source: query content (asset's developer + China scope OR explicit China-focus query). |
| **Türkiye query content** — query explicitly contains Turkish regulatory terms (TİTCK, SGK, SUT, EK-4D, etc.), names a Turkish domestic sponsor, OR explicitly scopes a topic to Türkiye | `sub-protocol-turkey.md` | TİTCK + SGK / SUT framework FDA / EMA / NICE'tan farklı bir mantık taşır. Default OFF. **NOT triggered by user identity** (user's location, employer, role, specialty are NOT valid triggers per generic-by-default.md Article 5). Trigger source: query content only. |
| **Türkiye product development intent** — query content combines Türkiye scope with product development decision-making intent (jenerik fizibilite, in-licensing eval, ATC class scan, fiyat tavanı, biowaiver eligibility, eşdeğer grup mapping, Reliance target ID, cross-country MIDAS comparison) | `sub-protocol-product-development-tr.md` (composes with `sub-protocol-turkey.md`) | Türkiye'de ilaç geliştirme/in-licensing/portföy seçimi kararları 4-kanallı veri triangülasyonu (TİTCK MCP + ThoughtSpot IQVIA MIDAS + AdisInsight + openFDA Orange/Purple Book) gerektirir. Tek-kanallı analiz feasibility kararı için yetersizdir. Default OFF; query content'e bağlı tetiklenir. **NOT triggered by user identity** per Article 5. |
| **Asset has scheduled regulatory action / readout / earnings event within 12 months** OR query explicitly mentions catalyst-watch terminology (PDUFA, CHMP, AdComm, readout, earnings, guidance, milestone) | `sub-protocol-catalyst-watch.md` | 5 catalyst types (PDUFA, CHMP, readout, AdComm, earnings) have event-spesifik discipline frames; date precision tiers, source hierarchy, hit-vs-miss interpretation, sequential endpoint hierarchy disipliniyle hatalı yorumlama önlenir. **NOT triggered by user investment portfolio inferences or user-employer competitive interest** per generic-by-default.md Article 5. Trigger source: query content (catalyst terminology) OR asset state (scheduled near-term catalyst per public sponsor disclosure). |
| **Modality under T3 analysis is biosimilar/follow-on biologics** OR query content explicitly invokes biosimilar terminology OR analysis explicitly addresses post-LOE landscape of a biological reference product | `task-modality-biosimilar.md` (layers onto generic task-modality.md) | Biosimilar modality has unique disciplines (BPCIA exclusivity arithmetic, abbreviated 351(k) pathway, totality-of-evidence framework, manufacturing CQA characterization, immunogenicity comparability, FDA 4-letter suffix naming, jurisdiction-spesifik discount bands, tender-vs-rebate market dynamics) that generic T3 cannot cover. Sub-template loads in addition to generic task-modality.md, not instead. **NOT triggered by user employer being a biosimilar manufacturer (e.g. Em Pharma, Sandoz, Celltrion) or user geography being a biosimilar manufacturing hub (Türkiye, India, South Korea)** per generic-by-default.md Article 5. Trigger source: query content (modality terminology) OR analytical scope (post-LOE biological landscape). |
| **Modality under T3 analysis is antibody-drug conjugate (ADC)** OR query content explicitly invokes ADC terminology OR analysis addresses HER2/TROP2/Nectin-4/B7-H4/CEACAM5/FRα target landscape (ADC-rich target classes) | `task-modality-adc.md` (layers onto generic task-modality.md) | ADC modality has unique disciplines (3-component architecture mAb+linker+payload, DAR distribution, payload class taxonomy with microtubule inhibitor / DNA-damaging / TOP1 inhibitor classes, cleavable vs non-cleavable linker chemistry + bystander effect, DXd-spesifik ILD ~10-15% class effect with mandatory monitoring discipline, BLA pathway with companion diagnostic complexity, conjugation chemistry manufacturing complexity, blockbuster ADC commercial trajectories Enhertu $3.5B+ etc.) that generic T3 cannot cover. **NOT triggered by user employer being an ADC developer (Daiichi Sankyo, AstraZeneca, Roche, Pfizer/Seagen, Gilead, ImmunoGen/AbbVie)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is cell or gene therapy (CAR-T/TCR-T/NK/AAV/lentiviral/CRISPR/in vivo CRISPR)** OR query content explicitly invokes cell/gene therapy terminology OR analysis addresses ATMP regulatory framework | `task-modality-cellgene.md` (layers onto generic task-modality.md) | Cell/gene modality has unique disciplines (cell vs gene therapy distinction, autologous vs allogeneic, EMA ATMP framework Regulation (EC) 1394/2007, patient=product autologous CAR-T complication, CRS+ICANS class effects with ASTCT grading, REMS programs, vein-to-vein 3-5 week manufacturing logistics, AAV serotype tropism, AAV class limitations including pre-existing immunity + hepatotoxicity + TMA, gene editing CRISPR class with Casgevy first-in-class precedent, $850K-$3.5M pricing with outcomes-based contracting) that generic T3 cannot cover. **NOT triggered by user employer being a cell/gene therapy developer (Gilead/Kite, BMS, Novartis, Vertex, BluebirdBio, Sarepta, BioMarin)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is RNA therapeutic (mRNA/siRNA/ASO/miRNA/saRNA/circRNA/in vivo CRISPR mRNA)** OR query content explicitly invokes RNA modality terminology OR analysis addresses LNP/GalNAc delivery system disciplines | `task-modality-rna.md` (layers onto generic task-modality.md) | RNA modality has unique disciplines (7-class taxonomy, delivery system disciplines LNP composition + GalNAc-ASGPR hepatic + ASO PS-MOE chemistry + intrathecal/intravitreal routes, ASO PS-related thrombocytopenia class effect, siRNA hepatic safety, mRNA vaccine reactogenicity + myocarditis signal, CBER vs CDER classification crosswalk, post-COVID platform technology framework, oligonucleotide solid-phase synthesis manufacturing, IVT mRNA + LNP encapsulation IP litigation Alnylam-Moderna and Acuitas-Pfizer) that generic T3 cannot cover. **NOT triggered by user employer being an RNA platform developer (Moderna, BioNTech, Alnylam, Ionis, Sarepta)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is radiopharmaceutical / radioligand therapy** OR query content explicitly invokes radiopharm terminology (Lu-177/Ac-225/Ga-68/PSMA-PET/theranostic) OR analysis addresses isotope supply chain dynamics | `task-modality-radiopharm.md` (layers onto generic task-modality.md) | Radiopharm modality has unique disciplines (3-component architecture targeting vector + chelator + isotope, theranostic pair concept Ga-68/F-18 diagnostic + Lu-177/Ac-225 therapeutic, isotope class taxonomy β−/α/β+ with distinct half-lives + ranges + supply chains, dosimetry as PK replacement with absorbed dose Gy concept + dose-limiting organs salivary/kidneys/bone marrow + lysine-arginine renal protection, FDA DIRM + NRC + Authorized User + ALARA radiation safety, isotope supply scarcity especially Ac-225 ~1.7 Ci/year global, 2022 Pluvicto supply crisis case study, 2023-2024 BD wave BMS/RayzeBio + Lilly/POINT + AstraZeneca/Fusion) that generic T3 cannot cover. **NOT triggered by user employer being a radiopharm developer (Novartis/AAA, Bayer, BMS/RayzeBio, AstraZeneca/Fusion, Lilly/POINT, Curium, ITM, Lantheus, Telix)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is small molecule (NCE) generic ecosystem** OR query content explicitly invokes Hatch-Waxman / ANDA / Orange Book / Para IV terminology OR analysis addresses post-LOE small molecule landscape | `task-modality-smallmol.md` (layers onto generic task-modality.md) | Small molecule generic ecosystem has unique disciplines distinct from biosimilars (Hatch-Waxman 1984 framework with NCE 5-year + clinical study 3-year + orphan 7-year + pediatric +6 months exclusivity arithmetic, ANDA pathway with bioequivalence 80-125% 90% CI standard + Paragraph IV certification + 30-month stay + 180-day FTF exclusivity + forfeiture events, Orange Book + AB-rated automatic substitution at pharmacy, Para IV settlement landscape with FTC v. Actavis 2013 antitrust scrutiny, authorized generic strategy, 505(b)(2) hybrid pathway, EMA 8+2+1 generic framework, NMPA VBP system with 80-95% price reductions, Türk jenerik framework with %40 statutory discount + eşdeğer grup SUT mechanic, brand LOE erosion curves typically 90-95% net revenue erosion within 24 months) that generic T3 cannot cover. **NOT triggered by user employer being a generics manufacturer (Teva, Sandoz, Mylan/Viatris, Sun Pharma, Aurobindo) or user geography being a generics manufacturing hub (India, Türkiye)** per generic-by-default.md Article 5. Trigger source: query content. Companion to `task-modality-biosimilar.md` — together cover the dominant follow-on modalities. |
| **Modality under T3 analysis is peptide therapeutic** (GLP-1, GLP-1/GIP dual agonist, GnRH analog, somatostatin analog, PTH analog, etc.) OR query content explicitly invokes peptide modality terminology OR analysis addresses obesity/T2D incretin landscape | `task-modality-peptide.md` (layers onto generic task-modality.md) | Peptide modality has unique disciplines (FDA chemically synthesized ≤40 aa drug pathway vs >40 aa or recombinant biologic pathway bright-line distinction; half-life extension strategies including fatty acid acylation + albumin binding for GLP-1 class with semaglutide K26 + γ-glutamic acid spacer + tirzepatide C20 fatty diacid, PEGylation, Fc fusion exemplified by dulaglutide, D-amino acid substitution, cyclization; GLP-1 class generation taxonomy 1st gen exenatide BID through 5th gen retatrutide GLP-1/GIP/glucagon Phase 3; SPPS Fmoc chemistry manufacturing; ANDA generic peptide pathway including Copaxone landmark 2015 Mylan precedent; GLP-1 supply crisis 2022-2024 + capacity expansion >$10B + compounded GLP-1 controversy) that generic T3 cannot cover. **NOT triggered by user employer being a peptide developer (Novo Nordisk, Eli Lilly, AbbVie, Ipsen, Recordati, Amgen)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is microbiome therapeutic / live biotherapeutic product** OR query content explicitly invokes LBP / FMT / microbiome therapeutic terminology OR analysis addresses recurrent C. difficile prevention landscape | `task-modality-microbiome.md` (layers onto generic task-modality.md) | Microbiome modality has unique disciplines (FDA LBP regulatory category under CBER OTP + BLA pathway distinct from food/supplement probiotics; 3 architectural classes donor-derived traditional FMT vs donor-derived standardized LBP vs designed rationally defined LBP; FDA-approved Rebyota Ferring 2022-11-30 first-in-class via PUNCH CD3 trial Bayesian primary analysis 70.6% vs 57.5% placebo + Vowst Seres+Nestlé 2023-04-26 first oral LBP via ECOSPOR III 88% vs 60% placebo; donor screening framework with FDA evolving guidance per 2019 ESBL E. coli transmission incident; FDA enforcement discretion for locally-prepared FMT in CDI indications without IND; EMA non-equivalent regulatory framework with member state heterogeneity) that generic T3 cannot cover. **NOT triggered by user employer being a microbiome developer (Ferring/Rebiotix, Seres, Vedanta, Pendulum)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is photodynamic therapy / PDT** OR query content explicitly invokes PDT/PDD/FGS terminology OR analysis addresses dermatology AK/BCC field treatment OR glioma fluorescence-guided surgery | `task-modality-pdt.md` (layers onto generic task-modality.md) | PDT modality has unique disciplines (3-component mechanism photosensitizer + light + oxygen with dual selectivity; photosensitizer class taxonomy 1st gen porfimer sodium Photofrin with 4-6 week skin photosensitivity + 2nd gen ALA-prodrug Levulan/Ameluz/Metvix + Gleolan oral 5-ALA for FGS + 3rd gen verteporfin Visudyne/Foscan/Tookad; FDA combination drug-device CDER+CDRH coordination per indication; antibody-photosensitizer conjugates Akalux PMDA Japan 2020) that generic T3 cannot cover. **NOT triggered by user employer being a PDT developer (Sun Pharma/DUSA, Biofrontera, Bausch+Lomb, Pinnacle, Rakuten Medical)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is oncolytic virus** OR query content explicitly invokes OV/oncolytic immunotherapy terminology OR analysis addresses melanoma intralesional or NMIBC BCG-unresponsive landscape | `task-modality-oncolytic.md` (layers onto generic task-modality.md) | Oncolytic virus modality has unique disciplines (dual mechanism direct oncolysis + immune activation cold→hot tumor; tumor selectivity strategies; immune-stimulating transgene "armed" oncolytic viruses GM-CSF/IL-12/anti-CTLA-4; FDA-approved Imlygic T-VEC Amgen 2015 melanoma via OPTiM trial + Adstiladrin Ferring 2022 NMIBC via Phase 3 N=157 CR 51%; T-VEC + pembrolizumab MASTERKEY-265 Phase 3 NEGATIVE dampening enthusiasm; Delytact PMDA Japan 2021 conditional Sakigake glioma; FDA CBER OTP + RMAT/Breakthrough/Priority Review/Orphan; EMA ATMP via Regulation 1394/2007 GTMP classification; biosafety considerations including viral shedding + HCP safety + household contacts + BSL-2; commercial underperformance of initial blockbuster expectations Imlygic ~$60-80M) that generic T3 cannot cover. **NOT triggered by user employer being an oncolytic virus developer (Amgen, Ferring, Daiichi Sankyo, Replimune, CG Oncology, Oncolytics Biotech, SillaJen)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Modality under T3 analysis is fusion protein / Fc-fusion biologic** OR query content explicitly invokes fusion protein / decoy receptor / VEGF trap / TNF receptor decoy terminology OR analysis addresses anti-TNF or anti-VEGF or CTLA-4-Ig landscape | `task-modality-fusion.md` (layers onto generic task-modality.md) | Fusion protein modality has unique disciplines (genetic fusion at DNA level vs ADC chemical conjugation; Fc-fusion as dominant architecture with FcRn-mediated half-life extension + bivalent presentation + Protein A purification; "-cept" INN suffix convention; approved landscape including Etanercept Enbrel Amgen+Pfizer 1998 with US biosimilar entry blocked through 2029 vs EU launch + Abatacept Orencia BMS 2005 + Belatacept Nulojix 2011 transplant with EBV-PTLD boxed warning + Aflibercept Eylea Regeneron+Bayer 2011 + Eylea HD 2023 Q12-16 week + Yesafili/Opuviz biosimilars 2024 + Rilonacept Arcalyst 2008 + 2021 pericarditis expansion + Dulaglutide Trulicity Lilly 2014 + Eloctate/Alprolix Sanofi 2014 hemophilia + Romiplostim Nplate ITP peptibody; biosimilar 351(k) pathway with cross-reference biosimilar template; Enbrel patent thicket lifecycle defense precedent) that generic T3 cannot cover. **NOT triggered by user employer being a fusion protein developer (Amgen, BMS, Regeneron, Bayer, Eli Lilly, Sanofi/Sobi, Pfizer)** per generic-by-default.md Article 5. Trigger source: query content. |
| **Therapeutic Area under T3 analysis is oncology** OR query content invokes oncology terminology (cancer, tumor, NCCN, ESMO, OS/PFS/ORR endpoints, ICI, MSI-H/dMMR/TMB, tumor-spesifik keywords) OR analytical scope addresses cancer drug landscape | `task-ta-oncology.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Oncology TA has unique disciplines that modality template cannot cover: (a) MDT epistemic framework + NCCN/ESMO/ASCO guideline ecosystem with Category 1/2A/2B/3 + ESMO-MCBS magnitude of benefit + Project Orbis international concurrent review; (b) FDA Oncology Center of Excellence (OCE) initiatives (Project Optimus dose optimization 2021 launch → 2024 final guidance + Project FrontRunner 2023 earlier-line migration + Project Renewal + Project Patient Voice + Project Equity + Project Facilitate + Project Community + Project Inclusion + Project Pragmatica); (c) accelerated approval discipline with 2021-2024 withdrawal wave (Keytruda/Opdivo SCLC + Tecentriq 2L bladder + Blenrep MM + Farydak + Istodax + Ukoniq); (d) ODAC advisory; (e) oncology-spesifik endpoint hierarchy OS gold standard / PFS / ORR / DoR / DFS / RFS / MRD / pCR / RECIST 1.1 / iRECIST / Lugano / IMWG; (f) ICI class paradigm — anti-PD-1/PD-L1/CTLA-4/LAG-3/TIGIT — with companion diagnostic stratification PD-L1 IHC + MSI-H/dMMR + TMB-H; (g) combination paradigm dominance post-2020. Layer 2 TA template provides orthogonal discipline to Layer 1 modality — complete analysis often invokes Layer 0 generic + Layer 1 modality (e.g. ADC) + Layer 2 oncology TA simultaneously. **NOT triggered by user employer being oncology-focused sponsor (Roche Genentech, Merck KGaA, Merck & Co, BMS, AstraZeneca, Pfizer Oncology, Novartis Oncology, AbbVie Oncology, Amgen, Johnson & Johnson, Bayer, Gilead, Daiichi Sankyo) or user memory-derived oncology specialty interest or user geography being an oncology trial hub** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is autoimmune / immunology / inflammation** OR query content invokes autoimmune terminology (RA, PsO, PsA, AS, UC, CD, IBD, MS, SLE, AD, asthma, HS) OR analytical scope addresses I&I drug landscape | `task-ta-autoimmune.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Autoimmune TA has unique disciplines: (a) disease pathophysiology family taxonomy (Th1/Th2/Th17/TNF/B-cell/Type 1 IFN); (b) step therapy framework csDMARD → tsDMARD → bDMARD with payer-imposed hierarchy; (c) disease-spesifik endpoint frameworks (ACR RA, PASI psoriasis, DAS28 RA, CDAI Crohn's, Mayo UC, EASI AD, ARR MS, SRI-4 SLE); (d) TNF-α inhibitor class with Humira LOE 2023 biosimilar wave dynamics + Enbrel US patent thicket through 2029; (e) IL-17/IL-23 class with Stelara biosimilar wave 2025; (f) JAK inhibitor class with FDA 2021 CV/malignancy black box warning per ORAL Surveillance; (g) Th2 axis dupilumab franchise + IL-5 + anti-IgE + anti-TSLP; (h) emerging TYK2/BTK/FcRn antagonists. Layer 2 TA template provides orthogonal discipline — "Humira biosimilar landscape" invokes Layer 0 + Layer 1 biosimilar + Layer 2 autoimmune. **NOT triggered by user employer with immunology portfolio (AbbVie, JNJ, UCB, Amgen, Novartis, Eli Lilly, Pfizer) or user specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is rare disease / orphan indication** OR query content invokes rare disease / orphan drug terminology / Orphan Drug Act / PRV / specific rare disease names | `task-ta-rare-disease.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Rare disease TA has unique disciplines: (a) regional orphan thresholds (US <200,000 per Orphan Drug Act 1983; EU <5 per 10,000 per Regulation 141/2000; Japan <50,000 per Orphan Drug Act 1993); (b) 7-year US orphan exclusivity vs 10-year EU + fee waivers + tax credits; (c) Rare Pediatric Disease Priority Review Voucher ($50-500M tradeable market); (d) accelerated approval with surrogate endpoints (serum TTR for hATTR; dystrophin expression DMD; HbF induction SCD); (e) small-N trial design with single-arm + natural history + master protocols + external controls + Bayesian adaptive; (f) ultra-high pricing $850K-$3.5M gene therapy + $200-500K annual ERT + outcomes-based contracting + annuity payment structures; (g) modality distribution concentrated in gene therapy + RNA therapeutics + ERT; (h) patient-focused drug development + FDA Office of Rare Diseases engagement. Layer 2 TA template provides orthogonal discipline — "Zolgensma SMA landscape" invokes Layer 0 + Layer 1 cellgene + Layer 2 rare-disease; "Casgevy SCD" invokes Layer 0 + Layer 1 cellgene + Layer 2 rare-disease. **NOT triggered by user employer being rare disease sponsor (BioMarin, Alexion/AstraZeneca Rare Disease, Sanofi Genzyme, Ultragenyx, Vertex, Sarepta) or user specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is CNS / neurology / neuropsychiatry** OR query content invokes CNS terminology (Alzheimer's, Parkinson's, MS, ALS, epilepsy, migraine, depression, schizophrenia, SMA, DMD, MG) OR analytical scope addresses brain/nervous system drug landscape | `task-ta-cns.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | CNS TA has unique disciplines: (a) blood-brain barrier (BBB) considerations per modality with CNS delivery strategies (small molecule lipophilic + mAb 0.1-0.3% penetration + ASO intrathecal + AAV9 pediatric + GalNAc non-CNS); (b) biomarker-driven trial paradigm (Aβ PET + tau PET + CSF biomarkers for AD; DAT-SPECT + α-synuclein for PD; MRI + sNfL for MS; NfL for ALS; gene expression for SMA/DMD); (c) disease-spesifik endpoint frameworks (CDR-SB + ADAS-Cog + iADRS for AD; ARR + EDSS + NEDA for MS; MDS-UPDRS for PD; ALSFRS-R for ALS; MADRS/HAM-D for MDD; PANSS for schizophrenia); (d) FDA Division of Neurology accelerated approval precedents (aducanumab 2021→2024 withdrawal + lecanemab 2023 traditional + donanemab 2024 + tofersen 2023 NfL-based + Sarepta DMD ASOs + Relyvrio 2022→2024 withdrawal); (e) MS DMT platform-vs-high-efficacy paradigm; (f) anti-Aβ class ARIA discipline with ApoE4 homozygote risk; (g) emerging psychedelic + KarXT muscarinic schizophrenia + GLP-1 in AD. Layer 2 TA provides orthogonal discipline — "Spinraza SMA" invokes Layer 0 + Layer 1 RNA + Layer 2 CNS + Layer 2 rare-disease (multi-TA); "lecanemab AD" invokes Layer 0 + Layer 1 generic + Layer 2 CNS. **NOT triggered by user employer with CNS portfolio (Biogen, Roche, Eli Lilly, Eisai, Sage, Axsome, Neurocrine, Acadia, Takeda, Novartis, Merck, Janssen) or user specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is cardiometabolic (metabolic / CV / renal / hepatic)** OR query content invokes T2D / obesity / ASCVD / HF / CKD / MASH terminology / CVOT / GLP-1 RA / SGLT2i | `task-ta-metabolic.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Cardiometabolic TA has unique disciplines: (a) integrated cardiometabolic epistemology (T2D↔ASCVD↔CKD↔HF↔obesity↔MASH interconnection driving lifecycle expansion strategies across therapeutic areas); (b) CVOT history (FDA 2008 T2D CV safety guidance post-rosiglitazone Avandia → 2018/2020 revision removing mandatory CVOT); (c) guideline ecosystem (ADA Standards of Care + EASD + ESC + ACC/AHA + KDIGO + AASLD/EASL); (d) endpoint frameworks (HbA1c/TIR for glycemic; %BW for obesity; LDL-C/ApoB/Lp(a) for lipid; 3P-MACE/4P-MACE for CV; eGFR slope/UACR for renal; MASH resolution histologic → NIT evolution); (e) GLP-1 class as dominant paradigm with LEADER/SUSTAIN-6/REWIND/SELECT 2023 first obesity CVOT + SUMMIT 2024 HFpEF + FLOW CKD + SURMOUNT-OSA + ESSENCE MASH multi-indication trajectory; (f) SGLT2 cardiorenal paradigm shift (EMPA-REG 2015 + DAPA-HF 2019 first non-diabetic HFrEF + EMPEROR-Preserved 2021 first HFpEF); (g) lipid landscape evolution (statin baseline + PCSK9 mAb + inclisiran siRNA + bempedoic acid + Lp(a) frontier); (h) MASH Rezdiffra 2024 first approval + GLP-1 MASH disruption + FGF21 pipeline; (i) HFrEF four pillars + HFpEF emerging paradigm + ATTR cardiomyopathy; (j) US IRA 2022 Part D negotiation 2024 first 10 drugs cardiometabolic-heavy (Jardiance + Xarelto + Januvia). Layer 2 TA provides orthogonal discipline — "semaglutide MASH" invokes Layer 0 + Layer 1 peptide + Layer 2 metabolic; "inclisiran ASCVD" invokes Layer 0 + Layer 1 RNA + Layer 2 metabolic. **NOT triggered by user employer with metabolic portfolio (Novo Nordisk, Eli Lilly, Boehringer Ingelheim, AstraZeneca, Merck, Sanofi, Amgen, Regeneron, Madrigal) or user specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is infectious disease / antimicrobial therapeutics** OR query content invokes ID terminology (antibiotic, antiviral, antifungal, vaccine, AMR, MRSA, VRE, CRE, MDRO, HIV, HCV, HBV, COVID, RSV, influenza, TB, mpox) OR analytical scope addresses antimicrobial / vaccine / pandemic preparedness landscape | `task-ta-infectious.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Infectious disease TA has unique disciplines: (a) population health externalities (AMR + pandemic preparedness public good dimension absent in most TAs); (b) stewardship constraint as commercial economics inversion (approved use deliberately restricted); (c) WHO 2024 priority pathogen framework (critical CRAB/CR Pseudomonas/CR Enterobacterales/rifampicin-R Mtb; high VRE/MRSA/resistant Neisseria); (d) GAIN Act 2012 + QIDP designation 5-year exclusivity extension + Priority Review + Fast Track + 21 CFR 317.2 qualifying pathogens (NOT for biologics/vaccines); (e) LPAD pathway 21st Century Cures 2016 (Arikayce 2018 first); (f) PRV stack (Tropical Disease §524 + Material Threat MCM §565A + RPD §529); (g) BARDA + Project BioShield 2004 + Operation Warp Speed COVID; (h) HIV Gilead Biktarvy ~$14B+ dominant + Apretude LA PrEP + Sunlenca PURPOSE-1 2024; (i) HCV cure era Sovaldi 2013 → market collapse $22B → $4-5B; (j) RSV vaccine boom Arexvy/Abrysvo/mRESVIA 2023+; (k) antibacterial commercial reality Achaogen/Melinta/Tetraphase bankruptcies despite QIDP; (l) subscription/pull incentive UK NHS dalbavancin 2022. Layer 2 TA provides orthogonal discipline — "Paxlovid COVID" invokes Layer 0 + Layer 1 smallmol + Layer 2 infectious; "mRESVIA RSV" invokes Layer 0 + Layer 1 RNA + Layer 2 infectious. **NOT triggered by user employer with ID portfolio (GSK, Pfizer, Merck, Gilead, ViiV Healthcare, AbbVie, Shionogi, Moderna, BioNTech, Novavax, Sanofi Vaccines) or user specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is women's health / reproductive medicine** OR query content invokes women's health terminology (contraception, HRT, menopause, VMS, postpartum depression, PPD, endometriosis, uterine fibroids, fertility, IVF, gynecologic oncology) | `task-ta-womens-health.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Women's health TA has unique disciplines: (a) historical underinvestment + post-1993 NIH Revitalization Act reversal + Organon 2021 divestment era; (b) FDA Pregnancy and Lactation Labeling Rule (PLLR) 2015 effective replacing A/B/C/D/X; (c) endpoint frameworks (Pearl Index contraception + menstrual blood loss HMB/endometriosis + VMS frequency-severity + HAMD-17 PPD + fracture/BMD osteoporosis + ongoing pregnancy/live birth ART); (d) PPD paradigm shift Zulresso brexanolone 2019 IV → Zurzuvae zuranolone Sage+Biogen FDA 2023-08-04 first oral PPD NAS GABA-A PAM 50mg×14d + DEA Schedule IV + WAC $15,900 + MDD CRL + EC 2025 + MHRA 2025; (e) menopause non-hormonal Veozah fezolinetant Astellas FDA 2023-05-12 first NK3R + FDA Boxed Warning 2024 hepatotoxicity + Lynkuet elinzanetant Bayer 2025 NK1/NK3 dual; (f) GnRH antagonist class Orilissa 2018 + Oriahnn 2020 + Myfembree 2021/2022 + Ryeqo EMA; (g) OTC contraception revolution Opill norgestrel Perrigo FDA 2023-07 first OTC OC; (h) novel OC Nextstellis estetrol 2021; (i) postmenopausal osteoporosis Prolia biosimilar 2025 + Evenity romosozumab; (j) gynecologic oncology overlap (PARP + ADC). Layer 2 provides orthogonal discipline — "Zurzuvae PPD" invokes Layer 0 + Layer 1 smallmol + Layer 2 women's health + Layer 2 CNS (multi-TA). **NOT triggered by user employer with women's health portfolio (Organon, Pfizer Women's Health, Bayer, AbbVie, Astellas, Myovant/Sumitomo, Besins) or user OB/GYN specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is pediatric therapeutics / pediatric drug development** OR query content invokes pediatric terminology (PREA, BPCA, pediatric exclusivity, RPD PRV, neonatal, infant, child, adolescent, pediatric oncology, pediatric rare, SMA, DMD, Dravet, pediatric obesity) | `task-ta-pediatric.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Pediatric TA has unique disciplines: (a) age sub-populations neonate/infant/child/adolescent each with distinct PK/PD/safety; (b) ethical constraints + 45 CFR §46 Subpart D + assent + parental permission; (c) FDA PREA-BPCA structure (PREA 2003 mandatory iPSP within 60 days EOP2 + waivers/deferrals; BPCA 2002 voluntary FDA Written Request → 6-month pediatric exclusivity stackable with orphan/NCE/QIDP — Lipitor ~$2.5B precedent); (d) RPD PRV §529 FDCA FDASIA 2012 prevalence <200K + primary pediatric + tradeable $50-500M historical + ~$100-150M current; (e) RACE for Children Act 2017 effective Aug 2020 eliminating orphan exemption pediatric oncology molecular target; (f) FDA Pediatric Extrapolation Guidance 2024 final full/partial/none framework; (g) EMA PIP Regulation 1901/2006; (h) pediatric oncology approvals (larotrectinib NTRK + selumetinib NF1 + Kymriah pediatric CAR-T 2017 + tovorafenib Ojemda 2024 first-in-class type II RAF); (i) SMA three-modality paradigm Spinraza/Zolgensma $2.1M/Evrysdi; (j) DMD Sarepta ASOs + Elevidys AAV74 micro-dystrophin 2023→2024 expansion; (k) pediatric obesity Wegovy 12+ 2022-12 + AAP 2023 guidelines; (l) Tzield T1D 8+; (m) growth hormone Ngenla/Sogroya/Skytrofa weekly; (n) pediatric vaccines + Beyfortus nirsevimab RSV 2023-07. Layer 2 provides orthogonal discipline — "Zolgensma SMA" invokes Layer 0 + Layer 1 cellgene + Layer 2 pediatric + Layer 2 rare-disease + Layer 2 CNS (multi-TA). **NOT triggered by user employer with pediatric portfolio (Sarepta, Biogen, Roche SMA, BioMarin, PTC, Novartis AveXis, Novo Nordisk pediatric obesity) or user pediatric specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is dermatology** OR query content invokes derm terminology (atopic dermatitis, AD, psoriasis, hidradenitis suppurativa, HS, vitiligo, alopecia areata, acne, rosacea, BCC, cSCC, melanoma, EB, pemphigus, JAK derm, PDE4 topical, AhR) | `task-ta-dermatology.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Dermatology TA has unique disciplines: (a) visible disease burden + topical-first paradigm + specialist workforce constraints + biomarker paucity + clinical endpoint reliance IGA/PASI/EASI; (b) endpoint frameworks (EASI-75/90 + IGA 0/1 + pruritus NRS AD; PASI 75/90/100 + sPGA psoriasis; HiSCR HS; F-VASI 75/50 vitiligo; SALT ≤20/≤10 alopecia; IGA + lesion count acne/rosacea); (c) AD biologic + JAK paradigm (Dupixent dupilumab Regeneron+Sanofi IL-4Rα FDA 2017-03-28 → multi-indication COPD 2024 first biologic + ~$14B FY2024 + Adbry tralokinumab + Ebglyss lebrikizumab IL-13 + Nemluvio nemolizumab IL-31 itch cytokine + Rinvoq/Cibinqo JAK1 + Olumiant baricitinib EU/Japan + Opzelura ruxolitinib topical + first vitiligo); (d) psoriasis topical innovation (Vtama tapinarof Dermavant AhR + Zoryve roflumilast Arcutis PDE4 + Sotyktu deucravacitinib BMS allosteric TYK2); (e) HS biologic (Humira 2015 + Cosentyx 2023 + Bimzelx UCB IL-17A/F dual 2024); (f) alopecia areata JAK-driven Olumiant 2022-06 first systemic + Litfulo Pfizer JAK3+TEC 2023-06 first pediatric + Leqselvi Sun Pharma 2024-07; (g) vitiligo Opzelura 2022-07 first repigmentation; (h) acne novel topicals Aklief trifarotene + Twyneo + Epsolay BPO encapsulated rosacea; (i) skin cancer Hedgehog BCC + Libtayo cSCC ICI + melanoma BRAF/MEK/ICI/Amtagvi TIL 2024 + Merkel Bavencio + CTCL Poteligeo; (j) Vyjuvek Krystal first topical gene therapy DEB 2023-05. Layer 2 provides orthogonal discipline — "Dupixent AD" invokes Layer 0 + Layer 1 biologic + Layer 2 derm + Layer 2 autoimmune. **NOT triggered by user employer with derm portfolio (Sanofi, Regeneron, Eli Lilly, Pfizer, AbbVie, JNJ, Novartis, UCB, LEO, Galderma, Almirall, Incyte, Dermavant) or user derm specialty interest** per generic-by-default.md Article 5. |
| **Therapeutic Area under T3 analysis is ophthalmology / retinal + anterior segment** OR query content invokes ophth terminology (wet AMD, nAMD, dry AMD, geographic atrophy, GA, DME, DR, RVO, dry eye, glaucoma, presbyopia, retinal gene therapy, RPE65, LCA, RP, TED, anti-VEGF, complement C3/C5) | `task-ta-ophthalmology.md` (Layer 2; layers ORTHOGONALLY on top of Layer 1 modality template) | Ophthalmology TA has unique disciplines: (a) target organ accessibility + IVT/topical local delivery + injection-based chronic therapy + BCVA ETDRS letter primary endpoint + OCT/FAF/angiography imaging biomarker + Medicare Part B buy-and-bill + 2024 biosimilar wave; (b) endpoint frameworks (BCVA letter gain wet AMD/DME/RVO; GA lesion area growth FAF NOT BCVA; IOP glaucoma; Schirmer+staining+OSDI dry eye; Luxturna mobility maze RP); (c) anti-VEGF durability paradigm (Lucentis Genentech/Roche 2006 + Eylea Regeneron+Bayer Fc-fusion 2011 ~$8B+ + Eylea HD aflibercept 8mg 2023 Q12-16W + Vabysmo faricimab Roche bispecific VEGF+Ang-2 2022 Q16W ~$3-4B + Susvimo PDS Q6M); (d) anti-VEGF biosimilar wave (Byooviz/Cimerli ranibizumab 2021/2022 + Yesafili/Opuviz aflibercept 2024-05); (e) GA complement paradigm 2023 first approvals (Syfovre pegcetacoplan Apellis FDA 2023-02-17 C3 OAKS+DERBY GALE extension + EMA REJECTED 2024 + retinal vasculitis post-launch; Izervay avacincaptad pegol Astellas/Iveric Bio FDA 2023-08-04 C5 RNA aptamer GATHER1+GATHER2; neither BCVA improvement only lesion growth slowing 14-20%); (f) glaucoma novel rho kinase Rhopressa/Rocklatan Alcon + NO-prostaglandin Vyzulta + Durysta SR implant + iDose TR Glaukos 2023-12; (g) dry eye Miebo perfluorohexyloctane 2023-05 first anti-evaporative + Tyrvaya nasal spray + Vuity presbyopia 2021-10; (h) retinal gene therapy Luxturna voretigene neparvovec Spark/Roche 2017-12-19 first FDA-approved directly administered gene therapy + EDIT-101 CRISPR + RGX-314 + 4D-150; (i) Xipere first suprachoroidal 2021-10; (j) Tepezza teprotumumab Horizon/Amgen $28B 2023 acquisition first TED 2020-01. Layer 2 provides orthogonal discipline — "Syfovre GA" invokes Layer 0 + Layer 1 peptide + Layer 2 ophth; "Luxturna LCA" invokes Layer 0 + Layer 1 cellgene + Layer 2 ophth + Layer 2 rare-disease. **NOT triggered by user employer with ophth portfolio (Regeneron, Bayer, Roche/Genentech, Novartis, Apellis, Astellas, Alcon, Bausch+Lomb, Santen, Allergan/AbbVie) or user ophth specialty interest** per generic-by-default.md Article 5. |
| **Boxed warning likely** (CAR-T, hepatotoxic small molecules, immune checkpoint with severe AE class) | label sub-protocol (FAERS focus) | Label boxed warning + FAERS disproportionality kontrol zorunlu; medical affairs use case. |
| **Pediatric or rare pediatric indication** (FDA RPDD/pediatric voucher, EMA PIP) | task-hta.md + sponsor-sweep (voucher monetization) | Rare pediatric voucher monetization commercial signal; pediatric label restrictions HTA-specific. |
| **Specialty oncology with combination paradigm** (e.g., ADC + IO, bispecific + CAR-T, multi-modality regimen) | sponsor-sweep (multi-sponsor) + label (interaction warnings) | Combination requires multi-sponsor coordination + drug-drug interaction label review. |
| **First-in-class FDA approval** within trailing 24 months | label + FAERS (post-marketing surveillance critical) + sponsor-sweep (launch trajectory) | Yeni-onaylı FIC asset için post-marketing güvenlik aktif izlemde olmalı; ticari trajectory belirsiz, sponsor IR commercial update vital. |
| **High-cost rare disease** (>$500K/year list price OR one-time gen tx) | task-hta.md (mandatory) + label (REMS/restriction analysis) | Ultra-yüksek fiyat tüm major HTA agency tartışmasını otomatik tetikler. |
| **BD due diligence context (v5.0.0)** — query content invokes licensing / M&A / option / royalty financing / co-development evaluation terminology OR analytical scope is pre-LOI / pre-term-sheet target assessment | `sub-protocol-bd-dd.md` + automatically chains `sub-protocol-provenance.md` (forensic-grade mode) + `ubo-source-hierarchy.md` (P0-P3 cascade) + `provenance-engine.md` (capability) + `evidence-object-schema.md` (schema) + `scripts/provenance-engine/` (runtime) | BD DD is inherently forensic-grade — UBO + sanctions + regulatory history + litigation + patent + commercial + scientific + deal structure assessments all require immutable evidence chain for post-close audit + regulatory defense + litigation support. 7-dimensional assessment framework (A Corporate+UBO + B Sanctions+PEP + C Regulatory + D Litigation+IP + E Commercial + F Scientific + G Deal Structure) + structured YAML risk register + Evidence Bundle ZIP deliverable. **NOT triggered by user employer engaging in BD alone** (Roche/Pfizer/Merck employee asking about a company ≠ DD activation) per `generic-by-default.md` Article 5. Trigger source: query content (transaction evaluation context). |
| **Forensic-grade claim content (v5.0.0)** — claim types in draft ∈ {beneficial_ownership, sanctions_hit, regulatory_action, deleted_pipeline_claim, historical_label, titck_opponent_claim, litigation_exhibit} OR parent sub-protocol in {bd-dd, turkey TİTCK defense mode} | `sub-protocol-provenance.md` + `provenance-engine.md` + k-redundant 3-path capture (Wayback SPN2 + Archive.is + local Playwright WARC) + RFC 3161 TSA (DigiCert + FreeTSA) + sigstore cosign + Evidence Bundle ZIP | Forensic-grade claim types all require immutable chain-of-custody attestation: content hash (SHA-256 + BLAKE3) + RFC 3161 pre-existence timestamp + sigstore operator identity signing + 3-path archive redundancy per G53/G-PROV-03. TİTCK defense of opponent historical claims (e.g. deleted 2023 pipeline pages) + OFAC sanctions screening of UBO chains + litigation exhibit preservation all share this forensic substrate. 10 gates G51-G60 with baseline vs forensic-grade severity differentiation. **NOT triggered by user identity alone** per `generic-by-default.md` Article 5. Trigger source: claim content types OR parent sub-protocol chaining. |

If the query **hybridizes** tasks (common — e.g., "profile glofitamab and compare to epcoritamab"), load multiple references.

If the query is primarily **scientific** (mechanism, biomarkers, RCT efficacy/safety synthesis, guideline recommendations), **defer to medsearch** rather than pharmaintel. Invoke medsearch upstream, then wrap the commercial/regulatory frame around its output.

### Step 1b — Mandatory Parallel MCP Activation

Before Phase 2 discovery begins, Claude MUST invoke `tool_search` to activate the MCP connectors declared in `skill-manifest.yaml` §runtime.mcp_connectors.required:

```
tool_search(query="clinical trials")   → activates Clinical Trials MCP
tool_search(query="pubmed")            → activates PubMed MCP
tool_search(query="exa")               → activates Exa MCP
tool_search(query="tavily")            → activates Tavily MCP
tool_search(query="fetch")             → activates Fetch MCP
```

Optional connectors activated on a per-task-type basis:
- T2 Asset Profile / T3 Modality Landscape / T5 Catalyst Watch (pivotal-backed) → activate Paper Search + Consensus
- Scientific-evidence-adjacent queries → activate bioRxiv + Scholar Gateway

**Rationale:** `web_search` alone returns secondary media layers; structured registry data (ClinicalTrials.gov results posting fields, PubMed MeSH + Substance Name queries, SEC EDGAR full-text) require MCP-native calls. Skipping this step caps the analysis at "industry media" confidence rather than "primary registry" confidence.

**Failure mode observed (v1.0.1 post-mortem):** A Claude instance may interpret "5-phase pipeline" as license to start web_search immediately, skipping tool_search. **This is a protocol violation.** If no tool_search call appears before Phase 2, the downstream report cannot claim MCP-native provenance, and every pivotal-trial claim stamp must be capped at Medium confidence.

### Step 1c — Scope Guards (three checks before writing any entry)

Before admitting any asset/catalyst/deal/readout into the output tables, Claude MUST silently verify:

1. **Window check.** Is the event date within the query's declared time window? If the user asked "next 90 days" and the event is Q4 of last year, it does not belong in the main tables. Place it in §Context (if recently resolved and within trailing-30-day bubble) or drop it. Do NOT park out-of-window items in §Uncertainties as a hedge.
2. **Resolution check.** For any "Recently resolved" entry (§IV in catalyst outputs), the outcome must be known (approval, CRL, withdrawal). A PDUFA date that has passed without a public outcome announcement is NOT "resolved" — it is pending-with-unknown-outcome and belongs in §Uncertainties, with a specific follow-up action.
3. **Peer-review check (pivotal readouts).** Before stamping any pivotal clinical readout at High confidence from a sponsor press release or an industry media article, Claude MUST run `Paper Search:search_pubmed` or `Consensus:search` with the trial acronym + the key modality/indication. If a peer-reviewed primary publication is found, **its numbers override the PR numbers** for effect sizes, CIs, p-values, and sample sizes. If no peer-reviewed publication is found, cap the confidence at Medium and flag "peer-review pending."

### Step 1d — Statutory Filing Layer (always-on for PDUFA, deals, and sales figures)

For three claim classes, Claude MUST add an explicit SEC EDGAR / statutory filing check regardless of task type:

- **PDUFA dates** → search the sponsor's most recent 8-K for the action-date disclosure; if not found, check the most recent 10-K / 10-Q forward guidance section
- **Deal terms** (upfronts, milestones, royalties) → search 8-K within 4 business days of announcement
- **Sales figures** (quarterly / annual revenue by medicine) → Product Revenue table in latest 10-K / 10-Q / Form 20-F; never cite sales figures from an aggregator if the statutory filing is available

This layer is NOT optional. If a Claude instance reports a PDUFA date or sales figure without at least attempting the statutory filing lookup, the resulting stamp must be downgraded to Medium.

### Step 1e — Sponsor Sweep (corporate-site depth layer)

For any query where a corporate sponsor is named, implied, or where competitive context requires surveying multiple sponsors, Claude MUST load `sub-protocol-sponsor-sweep.md` and execute the three-target fetch per sponsor (pipeline page + press releases filtered to query scope + investor relations page).

Trigger rules (see sub-protocol §Trigger rules for full detail):

1. Named sponsor in query → mandatory sweep of that sponsor
2. Named asset → sweep all sponsors holding/co-holding the asset
3. Modality landscape (T3) → sweep 5–15 Top-30 sponsors active in that modality
4. Catalyst watch (T5) with named sponsors → sweep each
5. Head-to-head (T6) → sweep both sides
6. Deal analysis (T4) → sweep acquirer + target
7. Company deep-dive (T1) → sweep is the primary discovery mechanism

**Rationale:** MCP primary sources (Clinical Trials, PubMed, SEC EDGAR) do not replace corporate-site depth. Sponsor pipeline pages carry HCP-facing asset cards with indication scope + mechanism narrative that registries do not. Sponsor press releases can disclose PDUFA dates, deal terms, and readouts hours before 8-K filings. Investor Day decks project revenue by asset class — data unreachable from regulatory sources. Skipping corporate-site sweeps caps available public evidence at roughly two-thirds.

**Integration point:** The sweep executes during Phase 2 Discovery in parallel with MCP connector calls. Each sponsor produces a structured "sponsor card" (see sub-protocol §Step S3) that serves as evidence inventory for the task-specific report. Sponsor cards are NOT verbatim report sections — they are input to the narrative.

**Disclosure requirement:** Every report invoking sponsor sweep MUST include a §Sponsor Sweep Disclosure block listing sponsors covered, sponsors NOT covered (with justification), and the cross-check layer applied (per sub-protocol §Disclosure Block template).

### Step 1f — Label & Post-Marketing Safety (v1.4.0)

For any task that includes at least one **approved asset** in scope, Claude MUST load `sub-protocol-label.md` and execute label fetch + FAERS check during Phase 3 Deep-Dive.

Trigger rules:

1. T2 Asset Profile → mandatory for the asset under analysis
2. T3 Modality Landscape → mandatory if ≥1 approved asset in landscape (pipeline-only landscapes exempt)
3. T5 Catalyst Watch → mandatory for any newly approved asset or post-marketing safety event
4. T6 Head-to-Head Comparison → mandatory for every approved comparator
5. T7 Regulatory Status Snapshot → inherent task
6. Medical affairs / clinician briefing / KOL engagement use case flagged → mandatory

**What gets captured per approved asset:**
- FDA DailyMed Structured Product Labeling (indication, dosing, boxed warning, contraindications, monitoring)
- EMA SmPC equivalent
- PMDA tenpu bunsho where Japanese layer is active
- FAERS disproportionality signals (OpenFDA API or Public Dashboard)
- Post-approval regulatory actions (safety communications, REMS modifications, label updates)

**Rationale:** Medical affairs use cases (KOL briefing, clinician education, payer discussion) require operational label detail that approval date + indication summary alone cannot supply. Dosing, boxed warnings, restriction criteria, REMS burden, monitoring requirements, drug-drug interactions — these are the fields clinicians and payers actually ask about. Post-marketing signal detection (FAERS) completes the safety picture that pivotal trial AE rates underrepresent.

**Integration point:** Label sub-protocol output populates either the report's §Label & Post-Marketing Context section (T3 new §9; T2 §2 + §4 expansions) or task-comparison.md's label delta matrix (T6).

**Disclosure:** Every report invoking this sub-protocol adds a label-level stamp per approved asset: `Source: DailyMed SPL / EMA SmPC · Latest revision: YYYY-MM-DD · Accessed: YYYY-MM-DD · Confidence: High`.

### Step 1g — Semantic Auto-Trigger evaluation (v1.5.0)

After Step 1 (task classification) and Step 1a (explicit layer triggers from keywords), Claude MUST run a **content-based semantic profile check** against the §Task Routing Layer triggers (B) Semantic auto-triggers table. Each profile that matches the task content additionally loads its declared layer(s).

**Process:**

1. Identify in-scope assets, indications, modalities, sponsors from the user query and Phase 1 scope definition.
2. For each row in the (B) Semantic auto-triggers table, evaluate whether the profile matches.
3. For each match, load the declared layer(s) — even if user did NOT use the explicit keyword.
4. **Disclose all auto-triggered layers** in §Auto-Trigger Disclosure block of the final report (G17 requirement).

**Worked example:**

User query: "Apitegromab profilini çıkar."

- Step 1 task classification: T2 Asset Profile.
- Step 1a explicit triggers: none (user used no HTA / PMDA / Sponsor Sweep keyword).
- Step 1f: Label sub-protocol mandatory because asset is approved (well, BLA-pending; awaits approval).
- **Step 1g semantic evaluation:**
  - "Apitegromab" → Spinal Muscular Atrophy → **rare disease profile** matches → auto-load `task-hta.md`
  - "Apitegromab" → likely high-cost rare disease (~analyst projects ~$1.8B peak with rare disease premium pricing) → auto-load `task-hta.md` (already loaded above; idempotent) + label REMS focus (already loaded by 1f)
  - "Apitegromab" → first-in-class muscle-targeting SMA → **first-in-class FDA approval profile** matches → auto-load FAERS deep dive + sponsor-sweep launch trajectory (sponsor-sweep already loaded by 1e)
- Final layer set: T2 task-asset.md + sub-protocol-sponsor-sweep.md + sub-protocol-label.md + task-hta.md
- §Auto-Trigger Disclosure must list: task-hta.md (rare disease + high-cost), label (boxed warning + first-in-class FAERS focus)

**Why this exists:** Users — especially senior medical/commercial professionals — should not be required to know which keywords trigger which layers. The skill's protocol must read content semantically and infer the correct depth. v1.4.0 SMA report missed HTA layer entirely because user did not say "NICE / CADTH"; the rare disease + high-cost gene therapy profile should have auto-triggered HTA without user prompting.

**Idempotency:** If a layer is loaded by both Step 1a (explicit) and Step 1g (semantic), it is loaded once. The §Auto-Trigger Disclosure shows both sources to give the reader full visibility into routing rationale.

**Conservative principle:** If semantic match is ambiguous (e.g., "rare disease" boundary is fuzzy for some indications), Claude **errs toward loading the layer**. False-positive layer load is cheap (extra context); false-negative is costly (missing analytical depth). The §Auto-Trigger Disclosure makes this transparent — the reader can see the inference and challenge it.

**Critical user-context separation (v1.7.0):** Per `references/generic-by-default.md` Article 5, semantic auto-triggers may NEVER fire based on user identity (user's location, employer, role, specialty, memory-derived context). Triggers fire only on **query content** — the asset's actual sponsor mentioned or known, query keyword match, asset characteristics (modality / indication / cost class), geographic mention in query. Loading a layer because "user works in [region]" or "user works at [employer]" is a v1.6.0-era bug that v1.7.0 fixes. If Claude finds itself reasoning "user is X so load layer Y", that reasoning is invalid and must be rejected.

### Step 1h — Generic-By-Default audit (v1.7.0)

Before proceeding to Phase 2 Discovery, Claude executes the G22 Generic-By-Default audit. This is the **forward-looking** audit (catching contamination before it propagates); the **backward-looking** audit (catching contamination in the finished report) runs as Step 5b before delivery.

**Forward audit — Step 1h checks:**

1. Are auto-triggered layers (from Step 1a + 1g) all backed by query-content rationales? Any user-identity-based load → revoke.
2. Will the planned report scope frame analysis sponsor-agnostically? Any planned "[user employer] perspective" framing → reframe.
3. Will the planned multi-audience executive summary variants (if applicable) discuss strategic implications without naming user's employer's strategic actions? Any planned "Strategic action signal ([user employer]): ..." → reframe.
4. Does the planned audience framing use generic terminology (medical affairs, business development, market access) rather than user-employer-internal terminology? Any planned "[user employer]-internal stakeholder" → reframe.

If any check fails, restart Step 1g with corrected logic and re-evaluate Step 1h. Do NOT proceed to Phase 2 with bugged auto-triggers or planned customization leaks.

**Backward audit — Step 5b checks:** See Step 5b below (executed before report delivery).

### Step 1i — Proactive forensic-grade activation suggestion (v7.0.0)

After Step 1h PASS, Claude scans the accumulated query content + auto-triggered layer set for **forensic-grade affinity signals** — content patterns that strongly correlate with use cases where the v5.0.0 Forensic Provenance Layer would add material value.

**Forensic-grade affinity signals (any 1 sufficient for suggestion):**

| Signal pattern | Example query content | Why forensic-grade adds value |
|---|---|---|
| Regulatory defense keywords | "TİTCK savunması", "regulatory defense", "ODAC defense", "TİTCK komisyon", "itiraz" | Claims need immutable chain-of-custody for commission submissions |
| Litigation/legal context | "mahkeme kararı", "emsal", "ihtiyati tedbir", "patent litigation", "citizen petition", "Paragraph IV" | Court-admissible evidence standard |
| BD due diligence context | "BD due diligence", "acquisition target", "licensing evaluation", "M&A assessment", "LOI" | UBO + sanctions + IP + regulatory history require audit-grade provenance |
| Forensic explicit request | "forensic-grade", "evidence bundle", "chain-of-custody", "kanıt zinciri", "provenance-verified" | Direct user request |
| Historical claim preservation | "deleted pipeline page", "silinen sayfa", "geri çekilen onay", "withdrawn approval", "archived claim" | Temporal evidence requires Wayback/Archive.is capture |
| Sanctions/compliance context | "OFAC", "sanctions screening", "MASAK", "PEP", "beneficial ownership", "UBO" | Compliance deliverables need attestation |

**Behavior when signal detected:**

If forensic-grade affinity signal is detected AND `sub-protocol-provenance.md` is NOT already loaded, Claude emits a **one-time suggestion block** before proceeding to Phase 2:

```
> **Forensic-grade mode suggestion (v7.0.0):** Query content contains [signal description].
> sub-protocol-provenance.md activation would add Evidence Bundle ZIP deliverable
> with RFC 3161 timestamping + SHA-256 content attestation — suitable for
> [TİTCK commission / BD data room / litigation discovery] use.
> Activate? (user confirms or declines; decline = proceed without forensic layer)
```

**Discipline constraints:**
- Suggestion is **one-time per session** — if user declines, do NOT re-suggest.
- Suggestion is **query-content-based** (not user-identity-based) — same Article 5 discipline applies.
- If user declines, proceed normally in baseline mode; no degradation of report quality.
- If user confirms, activate `sub-protocol-provenance.md` (and chain `sub-protocol-bd-dd.md` if BD DD context present) and re-run Step 1h with expanded layer set.
- Manifest gate **G63** audits that the suggestion block appeared when affinity signal was present (WARNING if omitted; not BLOCKER because suggestion is advisory, not mandatory).

### Step 2 — Execute the 5-phase pipeline

Every pharmaintel task runs through five phases (the exact tool invocations per phase are task-specific; see the task reference files):

```
Phase 1 — SCOPE DEFINITION
  └─ Terminology glossary (INN + brand + dev code; e.g., "trastuzumab deruxtecan / Enhertu / DS-8201 / T-DXd")
  └─ Time window + geographic scope
  └─ Primary comparators (if applicable)

Phase 2 — DISCOVERY (broad net, parallel MCP calls + sponsor sweep)
  └─ Paper Search (multi-source academic sweep)
  └─ Tavily (search_depth=advanced, last 90-180d, topic=news|finance)
  └─ Exa (semantic + category-filtered)
  └─ Clinical Trials MCP (pipeline/landscape sweep)
  └─ Sponsor Sweep (per Step 1e): pipeline page + press releases + IR for each in-scope sponsor

Phase 3 — DEEP DIVE (authoritative primary sources)
  └─ Fetch: FDA Drugs@FDA labels + Medical Reviews (accessdata.fda.gov)
  └─ Fetch: FDA DailyMed Structured Product Labeling (per Step 1f, mandatory for approved assets)
  └─ Fetch: EMA EPARs (ema.europa.eu)
  └─ Fetch: FAERS disproportionality (per Step 1f, for approved assets with post-marketing concern)
  └─ Fetch: SEC EDGAR full-text (efts.sec.gov/LATEST/search-index)
  └─ Fetch: IR portals, earnings call transcripts (Seeking Alpha free, Fool)
  └─ PubMed MCP: MeSH-precise pivotal publications
  └─ Consensus MCP: evidence synthesis for specific claims

Phase 4 — TRIANGULATION
  └─ Apply triangulation.md §2 templates per claim
  └─ Resolve conflicts via §3 hierarchy
  └─ Flag single-source claims explicitly

Phase 5 — SYNTHESIS + VALIDATION + PRESENTATION
  └─ Load references/report-presentation.md (Reader-Facing Clean-Copy Standard, v8.1.0)
  └─ Draft markdown report from assets/report-template.md, applying the two-layer output model:
       • Layer A (okur-yüzlü temiz kopya): journal-quality Turkish prose + info boxes +
         glossary + numbered citations + Kaynaklar — NO internal-process machinery
       • Layer B (iç denetim ve sağlama kaydı): per-claim provenance stamps + confidence
         table + triangulation notes + G22 audit line — render-excluded (sentinel-wrapped)
  └─ Embed visualization directives as HTML comments (<!-- VIZ: ... -->) adjacent to data;
     these never render and are stripped by the design pipeline
  └─ Explicit "not knowable from free sources" callouts (reader-facing prose)
  └─ Optional downstream handoff: carbon-html-report (publication) or carbon-pptx (briefing)
     — both strip VIZ comments + the render-excluded Layer B per report-presentation.md §8
```

### Step 5b — Backward Generic-By-Default audit (v1.7.0)

Before delivering any report, Claude executes the G22 backward audit on the finalized draft. This is the failsafe for any contamination that escaped Step 1h.

**8 programmatic checks (per `references/generic-by-default.md` Article 6):**

1. Does the document body contain the user's name (memory-derived)? **Pass criterion: NO occurrences.**
2. Does the document body contain the user's employer name AND that employer is NOT explicitly mentioned in the user query? **Pass criterion: NO occurrences.**
3. Does any auto-trigger rationale cite "user profile", "sponsor profile" (when "sponsor" actually means user's employer), user role, or user location? **Pass criterion: ZERO such rationales.**
4. Does any executive summary variant include strategic action recommendation directed at a specific named sponsor (other than mechanically-required incumbent identification)? **Pass criterion: ZERO recommendations.**
5. Does the intended-use declaration name the user's employer or contain employer-internal terminology? **Pass criterion: NO.**
6. Does the coverage statement contain region exclusion-as-mention asymmetry, or region/sponsor inclusion anchor asymmetry? **Pass criterion: NEITHER.**
7. Does the document scope note align analytical frame with user employer's competitive setting? **Pass criterion: NO.**
8. Do any disclosure blocks (Triangulation Notes, Provenance Disclosure, Confidence Disclosure) contain user-context references beyond what is methodologically required? **Pass criterion: NO.**

If any check fails: revise the offending content to a generic equivalent, re-run the full 8-check audit. Do NOT deliver until all 8 checks pass.

**Programmatic enforcement (v1.7.1 — mandatory automation):** Step 5b execution is now **automated via mandatory script invocation**, not manual self-audit. Before report delivery, Claude MUST execute the validator script and parse its output:

```bash
python3 scripts/validate-report-discipline.py /path/to/draft-report.md \
  --user-name "${USER_NAME}" \
  --user-employer "${USER_EMPLOYER}" \
  --query "${ORIGINAL_QUERY}" \
  --json
```

Where `USER_NAME`, `USER_EMPLOYER`, and `ORIGINAL_QUERY` are populated from:
- `USER_NAME`: Claude's user-context awareness (memory or in-conversation disclosure); empty string if unknown
- `USER_EMPLOYER`: Same source; empty string if unknown
- `ORIGINAL_QUERY`: The literal user prompt that initiated this report

**Outcome handling:**
- **All 8 checks PASS:** Report passes G22 backward audit; proceed to delivery
- **Any check FAIL:** Claude MUST revise the offending content per validator's `advice` field, re-run validator, and continue iterating until all checks PASS. Do NOT deliver a report with any failed G22 check.
- **Validator script unavailable** (e.g., script missing from build): Fall back to manual self-audit per `references/generic-by-default.md` Article 6 checklist; explicitly document fallback in §Provenance Disclosure.

**False positive handling:** The validator can produce false positives in legitimate cases — for example, mentioning "Roche Kadcyla" as an incumbent product in a competitive landscape when "Roche" also happens to be the user's employer. In such cases:
1. Verify the mention is **methodologically necessary** (not gratuitous reference to user employer)
2. If necessary, document the methodological justification in §Triangulation Notes (e.g., "Roche named as incumbent product sponsor, not as user-context reference")
3. Override the failed check with a `# G22-OVERRIDE` annotation in the report at the relevant line, plus rationale
4. Re-run validator; the next iteration of the validator (v1.7.x) will support `--accept-overrides` flag to honor documented exceptions

This false-positive handling preserves audit transparency while allowing legitimate sponsor identification in competitive landscapes.

**Disclosure requirement:** Every report's §Provenance Disclosure MUST include a one-line G22 audit result statement of the form:
> G22 Generic-By-Default audit (forward + backward) sonucu: Tüm 8 kontrol PASS (validator: scripts/validate-report-discipline.py invocation 2026-MM-DD).

Or, in case of any documented overrides:
> G22 Generic-By-Default audit: 7/8 kontrol PASS, 1 override (G22.X — methodological justification: [reason], see §Triangulation Notes).

### Step 3 — Produce the output

Default output is a **provenance-stamped markdown report** per `assets/report-template.md`, rendered according to the **Reader-Facing Clean-Copy Standard** (`references/report-presentation.md`, v8.1.0). The report is organized in **two layers**:

- **Layer A — okur-yüzlü temiz kopya (the default deliverable):** a journal-article-quality Turkish document. Complete-sentence scientific prose; logical narrative flow; **info boxes** (`Bilgi Kutusu` / `Yöntem Notu` / `Dikkat`) and a front-matter **Kısaltmalar ve Tanımlar** glossary so no term goes undefined; **journal-style numbered citations** (`[n]`) resolving to a consolidated **Kaynaklar** section; a reader-friendly **Yöntem ve Kapsam** paragraph. Layer A contains **no internal-process technical quotations** — no "validator", "G22", "gate", "kontrol PASS", "hiyerarşi rütbesi", or per-claim blockquote provenance stamps in the visible body.
- **Layer B — iç denetim ve sağlama kaydı (render-excluded):** the gate-mandated machinery (per-claim 4-part provenance stamps → G4; Confidence Disclosure Table → G13; Triangulation Notes → G3; G22 audit result line + validator invocation → G22/G61; Auto-Trigger / Sponsor Sweep Disclosure → G17). Layer B is wrapped in render-exclusion sentinels (`<!-- RENDER:EXCLUDE-FROM-HERE -->` … `<!-- RENDER:EXCLUDE-TO-HERE -->`) **or** emitted as a companion file. It is present in the raw markdown (so the validator scans it and the disclosure-block headings remain findable) but **never appears in the rendered clean copy**.

**Visualization directives** are embedded inline as HTML comments (`<!-- VIZ: ... -->` / `<!-- VIZ-BLOCK ... -->`) immediately adjacent to the data they concern. HTML comments never render in HTML output and are stripped by the design pipeline (`report-presentation.md` §5 + §8) — this guarantees, with defense-in-depth, that production instructions never enter the final report text.

**Validator unchanged:** Step 5b's mandatory `validate-report-discipline.py` invocation runs on the combined Layer A + Layer B document (or the union of clean-copy + companion file). Generic-by-default scanning covers the whole file including VIZ comments and the render-excluded appendix.

If the user requests publication-grade HTML/PDF or a presentation deck, hand off downstream per §Composition; downstream skills strip the VIZ comments and the render-excluded Layer B per the render-pipeline contract.

---

## Nihai Rapor Sunum Disiplini (v8.1.0 — özet; tam standart: `references/report-presentation.md`)

Faz 5'te taslak oluşturulurken `references/report-presentation.md` yüklenir ve aşağıdaki altı ilke uygulanır. Bu ilkeler, skill'in kanıt-toplama ve provenans disiplinini **değiştirmez**; yalnızca çıktının *sunulan* hâlini yönetir.

1. **Temiz Türkçe bilimsel dil + açık referanslar.** Rapor, eksiksiz cümle yapısıyla, yüksek nitelikli bir bilimsel rapor diliyle yazılır. Her maddi iddia numaralı atıfla (`[n]`) desteklenir ve tam künyeler sondaki **Kaynaklar** bölümünde açıkça verilir. Ulaşılamayan veya tek/ikincil kaynağa dayanan bulgular metinde açıkça bu sınırlılıkla sunulur.

2. **İç süreç kotasyonları yok — dergi makalesi gibi temiz nihai kopya.** Sunulan rapor (Katman A), iç çalışma mekaniğine dair **hiçbir teknik kotasyon içermez** ("validator", "G22", "gate", "kontrol PASS", "hiyerarşi rütbesi", "scripts/...", "override", blok-alıntı provenans damgaları). Yalnızca genel ve anlaşılır metodolojik ayrıntılar, okuyucu-dostu **Yöntem ve Kapsam** düzyazısıyla verilir. Tüm kapı-zorunlu makine, render-dışı **Katman B'ye** (iç denetim ve sağlama kaydı) taşınır.

3. **Optimize anlatı akışı + zenginleştirme.** Makro yapı okuyucu için kurulur (Yönetici Özeti → Arka Plan → bulgu bölümleri → Sentez → Sınırlılıklar → Kaynaklar). Her bölüm bir lede cümlesiyle açılır; tablolar çerçeveleme cümleleriyle sunulur; bölümler köprü cümleleriyle bağlanır. Anlatım, bulguların **anlamını** açıklayacak şekilde detaylandırılır (yalın veri dökümü değil).

4. **Bilgi kutuları + kısaltmalar dizini.** Okuyucunun anlamadığı detay kalmaması için: rapor başında bir **Kısaltmalar ve Tanımlar Dizini**; metin içinde, terimlerin ilk geçtiği yerde **Bilgi Kutusu** (tanım), **Yöntem Notu** (genel metodolojik açıklama) ve **Dikkat** (uyarı) etiketli satır-içi kutular.

5. **Görselleştirme talimatları — metne girmeden.** Markdown sonradan görselleştirileceğinden, tasarım aşamasına yönlendirmeler metinde bulunur; ancak **tüm görselleştirme talimatları HTML yorumu** (`<!-- VIZ: ... -->`) olarak yazılır. HTML yorumları render'da **hiçbir koşulda görünmez** ve tasarım boru hattı bunları üretimden önce siler — böylece talimatlar nihai rapor metnine **girmez** (savunma-derinliği: görünmezlik + ayıklama). Talimatlar ilgili verinin yanına konur, okuyucu-bağımsızdır ve görünür düzyazıda yankılanmaz.

6. **Render-dışı denetim kaydının yalıtımı + sözleşme.** Katman B, render-dışı sentinel çiftiyle (`<!-- RENDER:EXCLUDE-FROM-HERE -->` … `<!-- RENDER:EXCLUDE-TO-HERE -->`) sarmalanır veya ayrı refakat dosyasına alınır. Açıklama bloklarının başlıkları (`## Provenance Disclosure` vb.) gerçek `##` markdown başlığı olarak korunur (validator uyumu). Downstream render skill'leri (carbon-html-report, carbon-pptx) hem VIZ yorumlarını hem render-dışı Katman B'yi nihai üründen çıkarır.

**Sunum öncesi kontrol:** Teslimden önce `references/report-presentation.md` §9'daki kontrol listesi yürütülür (G66 katman ayrımı + G67 görselleştirme talimatı yalıtımı + G68 bilgi kutusu/kısaltma kapsaması).

---

## Free-Tier Source Priority (the "T0→T2 only" rule)

When a datum is available at multiple tiers, the skill **always** prefers the freest + most primary option. The canonical tier hierarchy:

**T0 — Fully Open (preferred):**
FDA Drugs@FDA · FDA Orange Book · FDA Purple Book · FAERS Dashboard · FDA Calendar · FDA Warning Letters · DailyMed · EMA EPAR · EMA CHMP highlights · EMA referrals · ClinicalTrials.gov · WHO ICTRP · CTIS · ChiCTR · JapicCTI · SEC EDGAR (10-K, 10-Q, 8-K, S-1, S-4, DEF 14A, Form 4) · PubMed/MEDLINE · bioRxiv · medRxiv · Google Patents · Lens.org · USPTO · EPO Espacenet · WIPO PATENTSCOPE · WHO GHO · CDC WONDER · SEER · NICE TA · ICER reports · IQVIA Institute free reports · Evaluate Vantage (free tier — ad-supported articles and charts)

**T1 — Free with registration:**
Semantic Scholar API · OpenAlex · Dimensions (academic free tier) · FDA FAERS Public Dashboard · Seeking Alpha free transcripts · BioPharma Catalyst free · company IR newsletters

**T2 — Freemium (free tier used, premium deferred):**
FiercePharma / FierceBiotech (ad-supported) · BioPharma Dive (free email) · Endpoints News free articles · STAT News free articles · Axios Vitals · PharmaTimes · Nature news features

**T3+ (paid) — explicitly excluded from primary workflow. If encountered as a secondary reference (e.g., "per Reuters citing Bloomberg"), attribute as "reported via [secondary source]" with confidence-degrading note.

---

## T7 — Regulatory Status Snapshot (inline handler)

For simple "is X approved in Y indication by Z agency?" queries, the skill does not need a full deep-dive reference. Execute:

1. **Fetch FDA:** `https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=BasicSearch.process` — search INN or brand
2. **Fetch EMA:** `https://www.ema.europa.eu/en/medicines` — search INN or brand; retrieve EPAR
3. **Fetch DailyMed:** `https://dailymed.nlm.nih.gov/dailymed/` — current SPL/label
4. **Cross-check:** company 10-K "product" section (SEC EDGAR) — confirms commercial status
5. **Triangulate** per `triangulation.md §2.2`

Report format:
```
[INN / Brand] — [indication]
├─ FDA: [status + approval date + label link]
├─ EMA: [status + opinion date + EPAR link]
├─ Other major: [Japan PMDA, China NMPA, Health Canada, MHRA — only if known]
├─ Key label nuances: [boxed warnings, restrictions]
└─ Confidence: High (primary regulatory sources, cross-verified)
```

---

## Composition & Handoffs (SMP v1.0)

**Upstream (pipe_from) — pharmaintel receives from:**
- `medsearch` → pharmaintel (markdown): medsearch delivers the scientific evidence base; pharmaintel wraps commercial/regulatory frame around it

**Downstream (pipe_to) — pharmaintel feeds into:**
- pharmaintel → `carbon-html-report` (markdown → print-ready HTML): for publication-grade deliverables
- pharmaintel → `carbon-pptx` (markdown → slide deck): for briefings (medical affairs, KOL, investor committees)
- pharmaintel → `smp-orchestrator` (via skill-manifest.yaml discovery)

See `skill-manifest.yaml` for the SMP v1.0 composability contract.

---

## Provenance & Confidence Standards

Every material claim in every pharmaintel output carries a four-part stamp:

```
[Claim]
— Source: [name + type (Primary Regulatory / Peer-Reviewed / Statutory Filing / Industry Media / Analyst / IR Statement)]
— ID/URL: [DOI, NCT ID, 8-K accession, EPAR URL, patent number, or canonical URL]
— Accessed: YYYY-MM-DD
— Confidence: High | Medium | Low | Unknown
```

**Confidence rubric** (see `triangulation.md §6` for full):
- **High** — primary source + cross-verified by independent second primary
- **Medium** — single authoritative primary OR two concordant secondaries
- **Low** — only secondary/media OR conflicting primaries (per `§3` hierarchy, preferred stated)
- **Unknown** — not verifiable from free sources; flagged with rationale (e.g., "private company, pre-IPO")

**Inline citation discipline (v1.0.1):** Beyond the section-level agrege stamp, the following claim classes REQUIRE inline `[^n]` footnote-style citation attached to the numeric value itself:

- Primary endpoint effect sizes (HR, OR, RR, absolute difference) + 95% CI
- p-values for primary and key secondary endpoints
- Sample size (n) for pivotal trials
- Regulatory dates (approval date, PDUFA date, CHMP opinion date)
- Financial figures (reported sales, deal values, upfront/milestone amounts)
- Safety rates for boxed-warning categories (e.g., ILD incidence, fatal event rate)

Agrege section-level stamps remain required but are not a substitute for inline cite on the classes above. This enforces defense-in-depth: a reviewer must be able to trace any single critical number to its primary source without scrolling.

**Reports always include a "Data cutoff" line** — the date beyond which new developments are not reflected. Pharma pipelines shift hourly; this is non-optional.

### Confidence Disclosure Table (G13 — required in every multi-claim report)

Every pharmaintel report of non-trivial size (more than ~10 material claims) MUST conclude with an explicit **Confidence Disclosure Table** summarizing the H/M/L/U distribution across the report's material claims. This exists to:

1. Surface protocol compliance transparently — a reader can instantly see whether the analysis rests predominantly on primary (High) or secondary (Medium) sources
2. Allow downstream reviewers / KOLs / compliance to weight the analysis appropriately
3. Prevent a report from appearing more authoritative than its provenance actually supports

**Required format (markdown):**

```markdown
## Confidence Disclosure

| Confidence | Material claims | Proportion | Representative examples |
|---|---|---|---|
| **High** | [N] | [X%] | [1–2 brief representative claim summaries] |
| **Medium** | [N] | [X%] | [1–2 brief representative claim summaries] |
| **Low** | [N] | [X%] | [1–2 brief representative claim summaries, if any] |
| **Unknown** | [N] | [X%] | [1–2 brief representative claim summaries, if any] |
| **Total** | [N] | 100% | — |

**Interpretation:** [One sentence summarizing what the distribution means for the report's usability — e.g., "This report rests on a High-confidence primary-source foundation suitable for regulatory-defense material" or "Medium-confidence predominance reflects unresolved peer-review pending status for DG04, flagged throughout."]

**Caps applied (if any):** [List any claims that were downgraded by the automatic confidence caps per triangulation.md §6 — e.g., "Sonrotoclax PDUFA date capped at Medium pending sponsor 8-K disclosure"]
```

**What counts as a "material claim":** A numerical value, regulatory status, date, or factual statement on which a decision or strategic conclusion in the report depends. Not every sentence is a material claim — glossary definitions, general mechanism-of-action background, and transitional prose are not counted.

**Minimum size threshold:** Reports with fewer than 10 material claims may elide this table and instead provide a single-sentence confidence summary in §Provenance Disclosure. Reports covering multiple assets, multiple catalysts, or multi-source financial analysis are always above threshold.

**Failure mode observed in sibling-skill reviews:** Reports that skip this table can visually "look High confidence throughout" even when 40%+ of claims are Medium or Low. The table forces the author (Claude) to confront the actual distribution before shipping.

---

## The "Two-Independent-Sources" Rule

No material claim (clinical readout, regulatory status, financial figure, deal term) is reported at **High confidence** unless verified by **two independent sources**. "Independent" excludes: a press release plus 50 media articles derived from it (that is *one* source). See `triangulation.md §1`.

Canonical triangulation quartets:

| Claim type | Triangulation shape |
|-----------|---------------------|
| Clinical readout | Company 8-K + ClinicalTrials.gov results posting + peer-reviewed publication + conference presentation |
| Regulatory status | FDA Drugs@FDA / EMA EPAR + company 8-K + DailyMed SPL |
| Deal terms | 8-K + S-4 (if stock) + IR press release + (optionally) DEF 14A fairness opinion |
| Sales figure | Company 10-K/10-Q segment disclosure + (proxy) analyst consensus via Seeking Alpha / Fool transcripts |

---

## Ethical & Compliance Guardrails

- **MNPI (material non-public information):** pharmaintel operates only on public-domain sources. Leaked documents, insider-sourced data, or unverified Twitter/X rumors are *not* used as evidentiary.
- **Embargo respect:** conference late-breakers embargo'd until presentation time — if pharmaintel sees a pre-embargo leak, it declines to analyze until embargo lifts.
- **Copyright:** analyst reports (even if accessible) are not reproduced verbatim. Peer-reviewed full-text is paraphrased under fair-use; quotes stay under 15 words per source (see skill-wide citation rules).
- **No promotional output:** pharmaintel produces *intelligence* reports, not promotional/HCP-detailing content. Different regulatory framework (FDA OPDP, EMA Art. 87) applies to promotion — out of scope.

---

## What pharmaintel does NOT do

- Does not produce stock recommendations ("buy / sell / hold"). It produces evidence inventories; interpretation is the reader's.
- Does not synthesize private company preclinical pipelines beyond what preprints + patents + conference posters disclose.
- Does not access paid analyst NPV models. Consensus estimates are approximated via aggregated earnings-call commentary from free sources.
- Does not replace medsearch for scientific evidence synthesis. If the user asks "does drug X reduce mortality in condition Y," that is a medsearch question.

---

## Quick Reference — Source-to-Question Map

(Full catalogue in `references/sources-catalog.md`.)

| Question | Go here first |
|----------|--------------|
| Is X FDA-approved? | Drugs@FDA + Orange Book |
| Is X a biologic, and is there a biosimilar? | Purple Book |
| Is there a registered trial for X? | ClinicalTrials.gov + WHO ICTRP + CTIS + ChiCTR |
| What did company Y announce at earnings? | SEC EDGAR 10-Q + IR transcript |
| What are the deal terms of this acquisition? | SEC EDGAR 8-K + S-4 |
| What does the peer-reviewed pivotal paper say? | PubMed (MeSH + Substance Name filter) |
| What adverse events are reported? | FDA label + FAERS Public Dashboard + EudraVigilance (adrreports.eu) |
| Did NICE recommend this drug? | nice.org.uk Technology Appraisals |
| What does ICER say about value? | icer.org evidence reports |
| When does the patent expire? | Orange Book + USPTO + Google Patents |
| Has this facility had GMP issues? | FDA Warning Letters + Form 483 list |
| What's happening in biotech this week? | Tavily (news, 7d) + FiercePharma + BioPharma Dive + Endpoints News free |
| Is there a modality/landscape review? | IQVIA Institute free reports + Nature Reviews Drug Discovery + Evaluate Vantage free |

---

## Known Gaps (explicitly surfaced in every output)

Pharmaintel output always includes a §Limitations block. Standard gaps:

- Private company preclinical detail (only preprints + patents + conference posters accessible)
- Confidential HTA negotiation terms (only redacted public opinions accessible)
- Paid analyst NPV models (consensus approximated via free transcripts)
- IQVIA MIDAS global sales granularity (inferred from company segment disclosures only)
- Chinese-language regulatory detail (NMPA detail often Chinese-only; pharmaintel flags)
- Japanese PMDA review depth (Japanese-language; English summaries only)

---

## Versioning

- **Current version:** 8.1.0 (2026-06-12)
- **Release summary (last 3 releases — full history in `references/changelog.md`):**
  - **v8.1.0 (2026-06-12)** — MINOR Reader-Facing Clean-Copy Standard (nihai rapor sunum disiplini). New reference `references/report-presentation.md` codifying a **two-layer output model**: Layer A (okur-yüzlü temiz kopya — journal-quality Turkish prose, info boxes, Kısaltmalar ve Tanımlar glossary, journal-style numbered citations + Kaynaklar, reader-friendly Yöntem ve Kapsam) and Layer B (iç denetim ve sağlama kaydı — per-claim provenance stamps, Confidence Disclosure Table, Triangulation Notes, G22 audit line, render-excluded via `<!-- RENDER:EXCLUDE-... -->` sentinels or companion file). Six presentation principles: (1) clean Turkish scientific register + explicit references; (2) zero internal-process technical quotations in the presented report — machinery relocated to render-excluded Layer B; (3) optimized narrative flow + enrichment; (4) info boxes (Bilgi Kutusu / Yöntem Notu / Dikkat) + abbreviations glossary; (5) visualization directives embedded as HTML comments (`<!-- VIZ: ... -->`) that never render and are stripped by the design pipeline; (6) audit-ledger isolation + render-pipeline contract. `assets/report-template.md` rewritten to embody the standard. SKILL.md Phase 5 + Step 3 updated; new §"Nihai Rapor Sunum Disiplini". New manifest gates **G66** (two-layer separation — no machinery in reader-facing body), **G67** (visualization-directive containment — HTML-comment only, render-stripped), **G68** (info-box + abbreviations-glossary coverage). Validator (`validate-report-discipline.py`) **unchanged** — it scans the combined Layer A + Layer B document; disclosure-block headings preserved as real `##` headings for Check 8/9 compatibility. **No breaking changes.** Backward-compatible with v1.0.x through v8.0.0; presentation-layer refinement only — evidence-gathering, triangulation, and provenance discipline untouched.
  - **v8.0.0 (2026-04-29)** — MAJOR Türkiye Ürün Geliştirme + 4-Channel Integrated Data Stack. New sub-protocol `sub-protocol-product-development-tr.md` introducing 7 decision-support modules (M1 Generic Feasibility Scorecard with 7-dimension weighted scoring, M2 Price Ceiling Simulation with TİTCK Fiyat Değerlendirme Komisyonu logic + 5-country reference + Ek-4B mandatory discount, M3 Cross-Country Market Sizing across 36 IQVIA MIDAS countries with structural-peer gap analysis, M4 Equivalent Group Mapping & Saturation, M5 Biowaiver/BCS Eligibility with TİTCK position, M6 Withdrawal Trend & Market Exit Risk, M7 Reliance Pathway Target Identification). New companion `api-integrations.md` v4.0.0 sections: §15 ThoughtSpot MCP (IQVIA MIDAS analytical layer with 4 canonical patterns), §16 TİTCK MCP (Tier-0 Türkiye regulatory primary, 25+ tool catalogue), §17 AdisInsight MCP (curated pipeline intelligence, 4 canonical patterns), §18 expanded openFDA Orange Book + Purple Book + biowaiver framework with full TE rating + exclusivity code reference + BCS biowaiver decision tree. New SKILL.md explicit trigger row "Türkiye Ürün Geliştirme (Product Development)" + new semantic auto-trigger "Türkiye product development intent" composing with sub-protocol-turkey.md. New manifest gates G64 (4-channel triangulation discipline) + G65 (MIDAS panel coverage acknowledgement mandatory). TR-PD Feasibility Report standard deliverable template (§6 of new sub-protocol). 4 cross-source triangulation patterns P1-P4. Backward-compatible with v1.0.x through v7.0.0; no breaking changes.
  - **v7.0.0 (2026-04-16)** — MAJOR Factual Verification Discipline + Proactive Forensic-Grade Activation. Two features: (A) triangulation.md §11 "History-sensitive chronological claims" — codifies verification protocol for Nth-of-class ordinal claims (first/second/third X) that caused persistent factual errors across v2.0.0→v5.0.0 production tests. Built-in FDA tumor-agnostic approval chronology reference table. Validator `check_10_historical_claim_verification()` with known-wrong pattern blocklist + general Nth-claim WARNING detection. New manifest gate **G62**. (B) SKILL.md Step 1i "Proactive forensic-grade activation suggestion" — when query content contains forensic-affinity signals (TİTCK savunması, BD DD, litigation, sanctions, deleted pages) and forensic layer is not loaded, one-time suggestion block prompts user to activate sub-protocol-provenance. New manifest gate **G63** (advisory). **No breaking changes.** Backward-compatible with v1.0.x through v6.0.0.
- **Full version history:** `references/changelog.md` (loaded lazily on demand — contains all releases v1.0.0 → v6.0.0 with substantive detail per release; do NOT load for routine invocations)
- **Skill metadata:**
  - SMP manifest: `./skill-manifest.yaml` (authoritative — skill-runtime reads version + gates + references from here)
  - Reference files (`references/*.md`): loaded on demand per Step 1 task routing
  - Report template: `./assets/report-template.md`
  - Report presentation standard: `./references/report-presentation.md` (Reader-Facing Clean-Copy Standard — loaded at Phase 5 synthesis; governs the two-layer output model, info boxes, visualization-directive containment, and journal-style citation discipline)

---

Start every pharmaintel invocation by:
1. Loading `sources-catalog.md`, `triangulation.md`, `query-patterns.md`
2. Classifying the query into a Task Type (T1–T8)
3. Loading the task-specific reference
4. Running the 5-phase pipeline
5. At Phase 5, loading `references/report-presentation.md` and emitting a provenance-stamped markdown report per `assets/report-template.md` — in the two-layer model (Layer A reader-facing clean copy + render-excluded Layer B audit ledger), with info boxes, abbreviations glossary, journal-style citations, and HTML-comment visualization directives
