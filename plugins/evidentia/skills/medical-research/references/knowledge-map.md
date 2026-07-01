# Knowledge Map — medical-research semantic coverage index (v8.3)

> Adım 0.4 (Semantic Scope Scan) reads this to build `coverage_set` by MEANING, not keywords.
> G-COVERAGE asserts this map is exhaustive vs. the real corpus. Keep in sync with the layer files.
> Axis IDs covered: 0.5.A · 0.5.B · 0.5.C · 0.5.D · 0.5.E · 0.5.F · 0.5.G · 0.5.H · 0.5.I · 0.5.J · 0.5.K

---

## Forward Map (file → sections → concepts → cross-links)

### SKILL.md  — [ALWAYS]
- Sections: Adım 0 (Mandatory Loading), Adım 0.5 (Domain Classifier — 10-Axis Signal Detection), Adım 1 (Mandatory Parallel Call List), Adım 2 (Generosity Principle), Adım 3 (Output Contract), Adım 4 (User Interaction), Adım 5 (Nihai Sunum Sözleşmesi), Reference Files Progressive Disclosure, Version History, SMP v1.0 Manifest
- Axis table: 0.5.A Oncology, 0.5.B Hematology, 0.5.C Regulatory, 0.5.D HTA, 0.5.E Medical Affairs, 0.5.F Immunology, 0.5.G Neurology, 0.5.H Rare Disease, 0.5.I Drug Intelligence, 0.5.J (Synapse/OpenTargets, auth-conditional), 0.5.K Epidemiology/Burden
- Concepts: skill protocol, axis signal detection, native-MCP-first principle, always-load files, output contract, Cömertlik Garantisi, clean-copy doctrine, §1–21 scaffold, two-output model, tool loading via ToolSearch, Phase 1–5 pipeline
- Synonyms: akış protokolü, araştırma sırası, kural seti, beceri yönergesi, methodology, protocol
- Cross-links: every axis 0.5.A–0.5.K, connector-registry.md (tool resolution), output-templates.md (§1–21 scaffold), report-presentation.md (clean-copy doctrine), evidence-grading.md (GRADE), all specialty layers

### connector-registry.md  — [ALWAYS]
- Sections: §0 Native-First Resolution Principle, §1 Tool Loading via ToolSearch, §2 Verified Connector Table (§2.1 Academic literature core, §2.2 Curated intelligence + mechanism, §2.3 Regulatory + epidemiology + Türkiye + IP, §2.4 Output / compose / visualize, §2.5 α-layer operator-connected high-trust), §3 Per-Connector Usage Notes (§3.1 AdisInsight schema, §3.2 TİTCK structural Turkey data, §3.3 Regulatory MCP native openFDA, §3.4 web research REMOVED v1.4.0, §3.5 annas-mcp full-text, §3.6 EPMC copyright gate), §4 Web Retrieval REMOVED v1.4.0, §5 Zero-Result Recovery Protocol, §6 Known Limitations & Workarounds, §6.3P third-party academic-MCP trust posture, §7 Domain Registry
- Concepts: tool selection, connector routing, native-first ladder, rate limits, fallback chains, α-layer (operator-connected: TİTCK-cache, YÖK Akademik, PDF Viewer), verified connector table, quota budgeting, zero-result recovery, documented gap (no web tier)
- Synonyms: araç seçimi, bağlayıcı yönlendirme, connector seçimi, API yönlendirme, tool routing
- Cross-links: every axis depends on this for tool resolution; turkiye-layer.md (§3.2 TİTCK); fulltext-retrieval.md (§3.5 annas-mcp); regulatory-intelligence.md (§3.3 openFDA); extended-api.md (§2.1 OpenAlex/S2)

### evidence-grading.md  — [ALWAYS]
- Sections: §1 The Tier 0–6 Source Hierarchy, §2 GRADE — Certainty of Evidence (per outcome), §3 Pragmatic Appraisal Track, §4 Specialty Appraisal Checklists (per active 0.5 layer), §5 Full-Text-Enriched Numerical Extraction (with copyright gate), §6 Entity / Relation / Temporal Extraction (NER), §7 Synthesis Stance
- Concepts: GRADE certainty, RoB (risk of bias), Tier 0 (Cochrane/SR), Tier 1–6 hierarchy, CONSORT/PRISMA, NER extraction, endpoint appraisal, certainty downgrading, NMA/MAIC appraisal, pragmatic track, full-text numerical extraction
- Synonyms: kanıt kalitesi, kanıt derecelendirmesi, evidence quality, certainty of evidence, kaynak hiyerarşisi, meta-analysis appraisal, RCT appraisal
- Cross-links: all specialty layers for their appraisal checklists (0.5.A–0.5.H); fulltext-retrieval.md (§5 numerical extraction); output-templates.md (§7 Tier 0 Sentez); hta-layer.md (economic model appraisal)

### extended-api.md  — [ALWAYS]
- Sections: §1 When this file applies, §2 OpenAlex (works, authors, institutions, citations), §3 PubChem PUG-REST (chemistry, identifiers), §4 Semantic Scholar Graph API (citations, influential citations), §5 Open-access determination — Unpaywall + DOAJ, §6 J-STAGE (Japanese scientific literature — 6-country coverage), §7 DailyMed (US Structured Product Labeling), §8 DrugBank (license-gated conditional), §9 Failure & rate-limit discipline
- Concepts: OpenAlex citation graph, academic institutions, Semantic Scholar, PubChem identifiers, InChI/SMILES, Unpaywall OA status, DOAJ, DailyMed SPL, DrugBank interactions, 6-country AFF coverage, J-STAGE Japan literature
- Synonyms: akademik kütüphane, atıf analizi, citation network, kimyasal kimlik, chemical structure, açık erişim belirleme, open access determination
- Cross-links: fulltext-retrieval.md (open-access); drug-intelligence-layer.md (PubChem, DailyMed, DrugBank); medaffairs-ops-layer.md (KOL via OpenAlex); output-templates.md (§8 KOL Haritası, §6 Çok Dilli Kapsama)

### output-templates.md  — [ALWAYS]
- Sections: §1 Section Contract (research completeness scaffold), §1 Küresel Literatür (PubMed + EuropePMC), §2 Klinik Pipeline (ClinicalTrials.gov v2), §3 Mekanizma & Farmakoloji (ChEMBL + PubChem), §4 Ruhsat & Etiket (openFDA + DailyMed + EMA), §5 Türkiye Verileri (TİTCK + Mevzuat + YÖK + AFF:"Turkey"), §6 Çok Dilli Kapsama (6-ülke AFF matriksi), §7 Tier 0 Sentez (SR + Cochrane + Epistemonikos), §8 KOL Haritası (OpenAlex → S2 → EPMC → NPI + YÖK Akademik), §9 Kılavuz Yerleşimi (NICE + ESMO + NCCN), §10 Açık Erişim & Tam Metin, §11–18 Specialty extended sections, §19 Drug Intelligence Pipeline Snapshot (0.5.I), §20 Cross-Layer Integration Notes, §21 Epidemiyoloji / Hastalık Yükü (0.5.K), §2 Format Classes A–I adaptive, §3 §21 Epidemiology Block, §4 .data.json Sidecar Schema, §5 Emission discipline
- Concepts: §1–21 research scaffold, clean-copy section mapping, adaptive format classes A–I, sidecar schema, emission discipline, pipeline snapshot, KOL map, multi-country AFF, systematic review synthesis
- Synonyms: çıktı şablonu, bölüm sözleşmesi, rapor iskeleti, output scaffold, report structure, section contract
- Cross-links: ALL axes and layers (this is the universal scaffold); report-presentation.md (clean-copy mapping); evidence-grading.md (Tier 0 synthesis); turkiye-layer.md (§5 Türkiye data); drug-intelligence-layer.md (§19 pipeline)

### report-presentation.md  — [ALWAYS]
- Sections: §0 İki-Çıktı Modeli (Temiz Kopya + Açıklama Katmanı), İlke 1 Temiz Türkçe ve Bilimsel Üslup, İlke 2 Teknik/İşletme Sızıntısı Yasağı, İlke 3 Anlatı Akışı ve Okunabilirlik, İlke 4 Bilgi Kutuları, İlke 5 Görselleştirme Direktifleri, İlke 6+ Hizalı İyileştirmeler, Clean-Copy İskeleti, İç Scaffold→Clean-Copy Başlık Eşlemesi, Nihai Doğrulama Kapısı, Renderleyiciye Devir Notu
- Concepts: two-output model, clean-copy doctrine, anti-leakage, methods-journal style, VIZ/OPS comment isolation, finalization gate G1–G7, carbon-html-report handoff, reader-facing body, Ops sidecar, visualization directives, Turkish scientific register
- Synonyms: sunum doktrini, temiz kopya, clean copy, presentation rules, output formatting, sızıntı yasağı, leakage ban, bilimsel yazım
- Cross-links: output-templates.md (scaffold→clean-copy mapping); evidence-grading.md (finalization gate references GRADE); all specialty layers (their §1.X output blocks feed the clean copy)

### oncology-layer.md  — [axis 0.5.A]
- Sections: §1 Guideline authorities (Tier 1), §2 Molecular / biomarker knowledge bases, §3 Evidence mining, §4 Appraisal checklist (oncology-specific), §5 Output → §1.F / §9 / §19
- Concepts: solid tumours, NSCLC, breast cancer, CRC, melanoma, ADC (antibody-drug conjugate), IO/PD-(L)1, checkpoint inhibitors, RECIST, NCCN, ESMO, ASCO, OS/PFS/ORR, biomarkers (KRAS/EGFR/HER2/MSI/TMB), staging, OncoKB, CIViK, TİTCK off-label oncology
- Synonyms: kanser, tümör, malignite, neoplazi, solid tumor, onkoloji, akciğer kanseri, meme kanseri
- Cross-links: hematology-layer.md (heme-onc overlap); drug-intelligence-layer.md (onco pipeline, 0.5.I); turkiye-layer.md (TR onco reimbursement, SGK SUT); hta-layer.md (oncology cost-effectiveness); regulatory-science-layer.md (oncology approval pathways); evidence-grading.md (oncology appraisal checklist §4)

### hematology-layer.md  — [axis 0.5.B]
- Sections: §1 Classification & risk (dual where applicable — Tier 1), §2 Response & disease-monitoring criteria, §3 Evidence + pipeline mining, §4 Appraisal checklist (heme-specific), §5 Output → §1.G / §9 / §19
- Concepts: leukemia (AML/CLL/ALL), lymphoma (DLBCL/FL/MCL), myeloma (MM), MRD (minimal residual disease), CAR-T therapy, bispecific antibodies, WHO-HAEM5 classification, ELN-2022 risk stratification, IPSS-M, flow cytometry, allogeneic/autologous SCT
- Synonyms: lösemi, lenfoma, myelom, kan kanseri, hematoloji, bone marrow, kemik iliği, CAR-T, bispecific
- Cross-links: oncology-layer.md (overlap solid/liquid tumors); drug-intelligence-layer.md (CAR-T/bispecific pipeline, 0.5.I); regulatory-science-layer.md (accelerated approval pathways); hta-layer.md (CAR-T cost-effectiveness); evidence-grading.md (heme-specific appraisal §4)

### regulatory-science-layer.md  — [axis 0.5.C]
- Sections: §1 Agency pathways & milestones (Tier 1 / primary), §2 Designation flags, §3 Appraisal checklist, §4 Output → §1.I / §4
- Concepts: FDA approval (NDA/BLA/sNDA), EMA (MAA/CHMP/CAT), TİTCK ruhsat, AdCom, accelerated approval, BTD (Breakthrough Therapy Designation), PRIME (EMA), REMS, conditional MA, withdrawal/suspension, biosimilar, labeling/SPC
- Synonyms: ruhsat, onay, piyasaya çıkış, marketing authorization, drug approval, izin belgesi, EMA onayı, FDA onayı, ruhsat iptali, withdrawal
- Cross-links: regulatory-intelligence.md (native openFDA + multi-jurisdiction); turkiye-layer.md (TİTCK native stack); drug-intelligence-layer.md (regulatory milestones, 0.5.I); hta-layer.md (regulatory→HTA pathway); rare-disease-layer.md (ODD/OMP designations)

### hta-layer.md  — [axis 0.5.D]
- Sections: §1 HTA bodies (Tier 1), §2 Economic-model appraisal, §3 Epidemiologic denominator (co-fire with 0.5.K), §4 Output → §1.J / §F-format
- Concepts: NICE (England/Wales), CADTH (Canada), PBAC (Australia), IQWiG (Germany), HAS (France), ICER, QALY, cost-utility analysis, budget impact model, MAIC (Matching-Adjusted Indirect Comparison), NMA (network meta-analysis), cost-effectiveness threshold, payer/reimbursement decision, value dossier
- Synonyms: maliyet etkililik, fiyatlandırma, geri ödeme, sağlık teknolojisi değerlendirme, HTA, payer, budget impact, karşılaştırmalı etkinlik
- Cross-links: regulatory-science-layer.md (regulatory→HTA sequencing); turkiye-layer.md (SGK SUT, TR geri ödeme); regulatory-intelligence.md (epidemiology denominator, 0.5.K); evidence-grading.md (NMA/MAIC appraisal); drug-intelligence-layer.md (pipeline intelligence for HTA)

### medaffairs-ops-layer.md  — [axis 0.5.E]
- Sections: §1 Standards & codes (Tier 1 / primary), §2 Operational artifacts, §3 KOL identification wiring (§8), §4 Boundary / handoff
- Concepts: MSL (Medical Science Liaison), KOL (Key Opinion Leader), advisory board, GPP3 (Good Publication Practice 3), ICMJE authorship, EFPIA/IFPMA codes, İEİS (Turkish pharma industry code), IIS/ISR (investigator-initiated studies), MLR (Medical Legal Review), FCPA, Transfer of Value (ToV), evidence generation planning, congress abstracts
- Synonyms: tıbbi bilim uzmanı, KOL, kilit kanaat önderi, akademisyen, medical education, yayın planlama, MSL
- Cross-links: fulltext-retrieval.md (KOL publication retrieval); extended-api.md (OpenAlex/S2 for KOL mapping); connector-registry.md §2.1 (native openalex/semantic-scholar for KOL); output-templates.md (§8 KOL Haritası); turkiye-layer.md (TR KOL via YÖK Akademik)

### immunology-layer.md  — [axis 0.5.F]
- Sections: §1 Guidelines (Tier 1), §2 Mechanism & class, §3 Endpoint appraisal, §4 Output → §1.L / §3 / §9
- Concepts: rheumatoid arthritis (RA), psoriatic arthritis (PsA), SLE (lupus), IBD (Crohn's/UC), psoriasis, atopic dermatitis (AD), asthma, anti-TNF biologics, IL-17/IL-23 inhibitors, JAK inhibitors, TYK2 inhibitors, ACR20/50/70, PASI, CDAI, biologics switching
- Synonyms: romatoloji, otoimmün hastalık, inflamatuar hastalık, immunoloji, biyolojik ajan, JAK inhibitörü, romatoid artrit, lupus, sedef
- Cross-links: drug-intelligence-layer.md (biologic/immunology pipeline, 0.5.I); regulatory-science-layer.md (JAK safety label updates); hta-layer.md (biologics cost-effectiveness); evidence-grading.md (immunology endpoint appraisal §4)

### neurology-layer.md  — [axis 0.5.G]
- Sections: §1 Guidelines & criteria (Tier 1), §2 Disease-specific endpoint frameworks, §3 Mechanism & pipeline, §4 Appraisal & output → §1.M / §9 / §21
- Concepts: multiple sclerosis (MS/RRMS/SPMS), NMOSD, myasthenia gravis (MG), SMA (spinal muscular atrophy), ALS, Alzheimer's disease, Parkinson's disease, migraine, epilepsy, stroke, DMT (disease-modifying therapy), anti-amyloid (aducanumab/lecanemab), ARIA, CGRP inhibitors, gene therapy (SMA), EDSS
- Synonyms: nöroloji, sinir sistemi, beyin hastalığı, multipl skleroz, Alzheimer, demans, inme, nörodejeneratif
- Cross-links: drug-intelligence-layer.md (CNS pipeline, 0.5.I); regulatory-science-layer.md (accelerated approval ARIA risk); rare-disease-layer.md (SMA/ALS rare-disease crossover); hta-layer.md (neurology cost models); evidence-grading.md (neurology endpoint appraisal §4)

### rare-disease-layer.md  — [axis 0.5.H]
- Sections: §1 Reference resources (Tier 1 / primary), §2 Evidence specifics (small-n methodology), §3 Epidemiology denominator (co-fire 0.5.K), §4 Output → §1.N / §21 / §F
- Concepts: orphan disease, ODD (Orphan Drug Designation), OMP (EMA Orphan Medicinal Product), Orphanet, OMIM, natural history study, registry endpoint, gene therapy, CFTR modulators (CF), enzyme replacement therapy, expanded access, single-arm trial, historical control, Bayesian methodology
- Synonyms: nadir hastalık, yetim hastalık, orphan, ender görülen, Orphanet, doğumsal hastalık, genetic disease, genetik hastalık
- Cross-links: regulatory-science-layer.md (ODD pathways, accelerated/conditional approval); drug-intelligence-layer.md (rare disease pipeline, 0.5.I); hta-layer.md (orphan HTA, NICE Highly Specialised Technologies); regulatory-intelligence.md (epidemiology/burden 0.5.K); neurology-layer.md (SMA/ALS crossover); evidence-grading.md (small-n methodology)

### drug-intelligence-layer.md  — [axis 0.5.I]
- Sections: §1 The Real AdisInsight Tool Surface (verified 9 Jun 2026), §2 What search_drugs Returns (real profile shape), §3 Use-Case Patterns (§3.1 Drug Profile Lookup, §3.2 MoA/Target Landscape competitor set, §3.3 Company Portfolio, §3.4 Regulatory Milestone Reconstruction, §3.5 Trial/Conference/Deal Intelligence), §4 Cross-Reference Protocol, §5 Zero-Result Fallback Chain, §6 pipeline_payload Sidecar, §7 Composition with Sister Skills, §8 Known Pitfalls
- Concepts: INN (International Nonproprietary Name), brand name, MoA (Mechanism of Action), molecular target, drug class, pipeline (Phase 1/2/3/launch), PDUFA date, deal/licensing, LoE (Loss of Exclusivity), patent cliff, first-in-class, AdisInsight search_drugs/get_drug/HyDE, competitor landscape, company portfolio
- Synonyms: ilaç adayı, aktif madde, etken madde, boru hattı, geliştirme hattı, drug pipeline, klinik aşama, moleküler hedef, MoA, etki mekanizması
- Cross-links: connector-registry.md §3.1 (AdisInsight schema); oncology-layer.md (onco drugs); hematology-layer.md (heme drugs); immunology-layer.md (biologics/JAK); neurology-layer.md (CNS pipeline); rare-disease-layer.md (orphan pipeline); extended-api.md (PubChem/DailyMed/DrugBank cross-ref); turkiye-layer.md (TR pipeline access)

### prisma-protocol.md  — [PHASE P0]
- Sections: §1 Soru-tipi sınıflaması, §2 PICO/PECO/PICOTS, §3 Uygunluk kriterleri, §4 Derleme tipi (sistematik/kapsam/hızlı), §5 Protokol çıktısı, §6 P1 devir
- Concepts: PICO, PECO, PCC, eligibility criteria, question type (therapy/diagnosis/prognosis/etiology/prevention), scoping review, PRISMA-ScR, protocol pre-specification
- Synonyms: protokol, soru çerçevesi, dahil hariç kriterleri, araştırma sorusu, review protocol
- Cross-links: search-strategy.md (P1); screening.md (eligibility → screening); prisma-reporting.md (protocol → checklist)

### regulatory-intelligence.md  — [axis 0.5.C / 0.5.D / 0.5.K]
- Sections: §1 Native openFDA (replaces Python requests), §2 WHO ICD-11 — indication coding, §3 WHO GHO — disease burden / epidemiology (axis 0.5.K), §4 Multi-jurisdiction regulatory cross-reference, §5 How this layer feeds the clinical layers, §6 Output — epidemiology_payload sidecar, §7 Known limitations
- Concepts: openFDA (drug events/recalls/labels/enforcement), ICD-11 coding, WHO GHO (Global Health Observatory), GLOBOCAN cancer incidence, disease burden, DALY, Federal Register, Health Canada (CADTH/HC), EUR-Lex, multi-jurisdiction approval tracking, epidemiology payload sidecar
- Synonyms: FDA veri tabanı, ilaç güvenliği, hastalık yükü, epidemiyoloji, prevalans, insidans, düzenleyici zeka, regulatory intelligence, ICD kodu
- Cross-links: regulatory-science-layer.md (agency pathways); hta-layer.md (epidemiology denominator for cost models); turkiye-layer.md (TR regulatory cross-ref); rare-disease-layer.md (epidemiology for rare diseases); output-templates.md (§21 epidemiology block)

### turkiye-layer.md  — [axis: Türkiye cross-cutting]
- Sections: §1 The v8.0 Türkiye Stack (replaces Dörtlüsü web-scraping), §2 TİTCK — Structured Drug Queries (§2.1 Core lookup chain, §2.2 Specialized TİTCK tools, §2.3 Data caveats), §3 Mevzuat — Native Legislation (SUT, yönetmelik, kararname), §4 TÜRKPATENT — Turkey IP (jenerik/biyobenzer), §5 Türkiye Output Block (turkey_access_summary sidecar), §6 Composition, §7 Mandatory Türkiye Dörtlüsü (every query)
- Concepts: TİTCK drug registry, SGK (Sosyal Güvenlik Kurumu), SUT (Sağlık Uygulama Tebliği), reimbursement list, Mevzuat legislation, TÜRKPATENT (patent/generic/biosimilar), YÖK Akademik (TR KOL), Türkiye Dörtlüsü (TİTCK+Mevzuat+TÜRKPATENT+YÖK), fiyat (drug price), geri ödeme (reimbursement), ruhsat TR, AFF:"Turkey" literature
- Synonyms: Türkiye, TR, Türkiye ilaç, SGK geri ödeme, SUT listesi, Sağlık Bakanlığı, Türk mevzuatı, TİTCK, Turkish reimbursement, Turkish market access
- Cross-links: regulatory-science-layer.md (TİTCK ruhsat); regulatory-intelligence.md (TR multi-jurisdiction cross-ref); hta-layer.md (TR HTA/SGK decisions); oncology-layer.md (TR onco off-label TİTCK); medaffairs-ops-layer.md (TR KOL via YÖK Akademik); drug-intelligence-layer.md (TR drug intelligence, 0.5.I)

### fulltext-retrieval.md  — [axis: full-text/KOL cross-cutting]
- Sections: §1 When to retrieve full text, §2 The Cascade (Tier 1 EuropePMC PMC, Tier 2 Paper Search download, Tier 3 annas-mcp paywalled, Tier 4 Wiley OAuth-gated, Tier 5 pubmed-epmc Unpaywall legal-OA last resort), §3 Copyright Gate (MANDATORY), §4 Methodology Grounding (annas book layer), §5 Output integration, §6 Known limitations
- Concepts: open access, PMC full-text, EPMC copyright_status, paywalled article retrieval, Anna's Archive, Wiley publisher full text, methodology books, Unpaywall, DOAJ, copyright gate, verbatim prohibition, CC-BY license
- Synonyms: tam metin, açık erişim, full text, article download, PDF erişim, makale indirme, copyright, telif hakkı
- Cross-links: connector-registry.md §3.5–3.6 (annas-mcp + EPMC copyright gate); extended-api.md §5 (Unpaywall/DOAJ); medaffairs-ops-layer.md (KOL publication retrieval); output-templates.md (§10 açık erişim); evidence-grading.md §5 (full-text numerical extraction)

### Process/tooling (not question-routed, listed for coverage completeness)
- benchmark-suite.md — deterministic integrity gates (check_integrity.py), regression queries (benchmark-queries.json), pass criteria (release gate)
- benchmark-protocol.md — integrity gate definitions, regression procedure, what each query guards, provenance & honesty
- composition-runbook.md — downstream handoffs (pipe_to), scope guard (what medical-research does NOT do), sidecar as the contract
- execution-map.md — order of operations (Adım 1), latency & quota budgeting, call-count expectations (no upper cap)
- v8-wiring-patch.md — global find/replace patch (ALL reference files), extended-api.md rewrite to native-first, evidence-grading.md update, output-templates.md update, specialty layer wiring inserts, infrastructure files, files NOT needing change
- skill-manifest.yaml — SMP v1.0 manifest (runtime.mcp_servers, composition, verification gates, constraints)

---

## Inverted Map (concept → file#section)

### Disease / Indication

- **Oncology / solid tumours / NSCLC / breast cancer / melanoma / CRC** → oncology-layer.md (all) · drug-intelligence-layer.md#§3.2 (competitor landscape) · hematology-layer.md (heme-onc crossover) · turkiye-layer.md#§2.2 (TİTCK off-label oncology) · hta-layer.md#§1 (NICE oncology HST)
- **Hematology / leukemia / lymphoma / myeloma / AML / DLBCL / MRD / CAR-T** → hematology-layer.md (all) · drug-intelligence-layer.md#§3 (CAR-T/bispecific pipeline) · oncology-layer.md (crossover) · regulatory-science-layer.md#§1 (accelerated approval)
- **Immunology / RA / PsA / SLE / IBD / psoriasis / atopic dermatitis / asthma** → immunology-layer.md (all) · drug-intelligence-layer.md#§3.2 (biologic/JAK pipeline) · regulatory-science-layer.md#§2 (JAK label updates) · hta-layer.md#§2 (biologics economic models)
- **Neurology / MS / NMOSD / Alzheimer / Parkinson / migraine / SMA / ALS** → neurology-layer.md (all) · drug-intelligence-layer.md#§3 (CNS pipeline) · rare-disease-layer.md (SMA/ALS crossover) · hta-layer.md#§2 (neurology economic models)
- **Rare disease / orphan / nadir hastalık / ODD / OMP** → rare-disease-layer.md (all) · regulatory-science-layer.md#§2 (ODD designation) · regulatory-intelligence.md#§3 (GLOBOCAN/GHO for rare epi) · hta-layer.md#§1 (NICE HST, CADTH rare)
- **Epidemiology / incidence / prevalence / disease burden / hastalık yükü / GLOBOCAN / GBD** → regulatory-intelligence.md#§3 (WHO GHO + GLOBOCAN) · regulatory-intelligence.md#§6 (epidemiology_payload sidecar) · hta-layer.md#§3 (epidemiologic denominator) · rare-disease-layer.md#§3 (rare epi co-fire 0.5.K) · output-templates.md#§21 (0.5.K block)

### Drug / INN / Brand / MoA / Target / Class

- **Drug by INN or brand name** → drug-intelligence-layer.md#§1 (AdisInsight search_drugs/get_drug) · drug-intelligence-layer.md#§3.1 (Drug Profile Lookup) · turkiye-layer.md#§2 (TİTCK lookup) · regulatory-intelligence.md#§1 (openFDA label)
- **MoA / mechanism of action / molecular target / drug class** → drug-intelligence-layer.md#§3.2 (MoA landscape) · drug-intelligence-layer.md#§2 (search_drugs profile) · extended-api.md#§3 (PubChem) · extended-api.md#§8 (DrugBank)
- **Pipeline / PDUFA / Phase 1–3 / deal / LoE / patent cliff / first-in-class** → drug-intelligence-layer.md (all) · drug-intelligence-layer.md#§6 (pipeline_payload sidecar) · regulatory-science-layer.md#§1 (milestone reconstruction) · turkiye-layer.md#§4 (TÜRKPATENT, generic/biosimilar) · connector-registry.md#§3.1 (AdisInsight schema)
- **Biosimilar / generic / jenerik / biyobenzer** → turkiye-layer.md#§4 (TÜRKPATENT) · regulatory-science-layer.md#§1 (biosimilar pathways) · drug-intelligence-layer.md#§3.4 (regulatory milestones)
- **Drug-drug interaction / DDI** → extended-api.md#§8 (DrugBank conditional) · regulatory-intelligence.md#§1 (openFDA FAERS)

### Specialty Axis

- **0.5.A Oncology axis** → oncology-layer.md (all) · drug-intelligence-layer.md (0.5.I) · turkiye-layer.md (TR onco) · hta-layer.md (onco cost-effectiveness)
- **0.5.B Hematology axis** → hematology-layer.md (all) · drug-intelligence-layer.md (0.5.I) · regulatory-science-layer.md (approval pathways)
- **0.5.C Regulatory axis** → regulatory-science-layer.md (all) · regulatory-intelligence.md (openFDA + multi-jurisdiction) · turkiye-layer.md (TİTCK)
- **0.5.D HTA / access axis** → hta-layer.md (all) · regulatory-intelligence.md (epidemiology denominator) · turkiye-layer.md (SGK SUT) · evidence-grading.md (NMA/MAIC)
- **0.5.E Medical Affairs axis** → medaffairs-ops-layer.md (all) · fulltext-retrieval.md (publication retrieval) · extended-api.md (OpenAlex/S2 KOL mapping) · connector-registry.md §2.1 (native openalex/semantic-scholar)
- **0.5.F Immunology axis** → immunology-layer.md (all) · drug-intelligence-layer.md (0.5.I biologic pipeline)
- **0.5.G Neurology axis** → neurology-layer.md (all) · drug-intelligence-layer.md (0.5.I CNS) · rare-disease-layer.md (SMA/ALS crossover)
- **0.5.H Rare Disease axis** → rare-disease-layer.md (all) · regulatory-science-layer.md (ODD) · hta-layer.md (NICE HST) · regulatory-intelligence.md (0.5.K epidemiology co-fire)
- **0.5.I Drug Intelligence axis** → drug-intelligence-layer.md (all) · connector-registry.md#§3.1 (AdisInsight real schema) · extended-api.md (PubChem/DrugBank) · turkiye-layer.md (TR drug stack)
- **0.5.J Synapse / OpenTargets (auth-conditional)** → SKILL.md (pipeline mention) · drug-intelligence-layer.md#§7 (composition with sister skills) · connector-registry.md#§2.2 (curated intelligence)
- **0.5.K Epidemiology / Burden axis** → regulatory-intelligence.md#§3 (WHO GHO) · regulatory-intelligence.md#§6 (epidemiology_payload) · hta-layer.md#§3 (epidemiology denominator) · rare-disease-layer.md#§3 (rare epi) · output-templates.md#§21 (0.5.K block)

### Geography

- **Türkiye / TR ruhsat / SGK / SUT / fiyat / geri ödeme** → turkiye-layer.md (all) · regulatory-science-layer.md#§4 (TR regulatory context) · hta-layer.md#§1 (SGK reimbursement) · regulatory-intelligence.md#§4 (multi-jurisdiction includes TR)
- **EU / EMA / CHMP / PRIME / conditional MA / EUR-Lex** → regulatory-science-layer.md#§1 (EMA pathways) · regulatory-intelligence.md#§4 (EUR-Lex) · hta-layer.md#§1 (EMA→HTA sequencing)
- **US / FDA / NDA / BLA / AdCom / Federal Register / REMS** → regulatory-science-layer.md#§1 (FDA pathways) · regulatory-intelligence.md#§1 (openFDA native) · regulatory-intelligence.md#§4 (Federal Register)
- **Canada / Health Canada / CADTH** → regulatory-intelligence.md#§4 (Health Canada) · hta-layer.md#§1 (CADTH)
- **Australia / PBAC / TGA** → hta-layer.md#§1 (PBAC) · regulatory-intelligence.md#§4 (multi-jurisdiction)
- **UK / NICE / MHRA** → regulatory-science-layer.md#§1 (MHRA) · hta-layer.md#§1 (NICE) · regulatory-intelligence.md#§4 (UK)
- **Germany / IQWiG / G-BA** → hta-layer.md#§1 (IQWiG/G-BA) · regulatory-intelligence.md#§4
- **Japan / J-STAGE / PMDA** → extended-api.md#§6 (J-STAGE) · regulatory-intelligence.md#§4 (multi-jurisdiction)
- **6-country multi-language coverage / AFF matrix** → output-templates.md#§6 (Çok Dilli Kapsama) · extended-api.md#§6 (J-STAGE) · extended-api.md#§2 (OpenAlex AFF filter)

### Regulatory Angle

- **Approval / marketing authorization / ruhsat onayı** → regulatory-science-layer.md#§1 (agency pathways) · turkiye-layer.md#§2 (TİTCK) · regulatory-intelligence.md#§4 (multi-jurisdiction)
- **Accelerated approval / BTD / PRIME / ODD / conditional MA** → regulatory-science-layer.md#§1–§2 · rare-disease-layer.md#§1 (ODD/OMP) · drug-intelligence-layer.md#§3.4 (milestone reconstruction)
- **Withdrawal / recall / suspension / güvenlik** → regulatory-intelligence.md#§1 (openFDA enforcement/events) · regulatory-science-layer.md#§2–§3 (appraisal of withdrawal risk)
- **Label / SPC / package insert / KÜB / etiket** → regulatory-science-layer.md#§1 (labeling) · regulatory-intelligence.md#§1 (openFDA label) · extended-api.md#§7 (DailyMed SPL) · turkiye-layer.md#§2 (TİTCK KÜB)
- **Patent / IP / generic entry / biosimilar** → turkiye-layer.md#§4 (TÜRKPATENT) · drug-intelligence-layer.md#§3.5 (deal/LoE) · regulatory-science-layer.md#§1 (biosimilar pathway)

### HTA / Access / Health Economics

- **Cost-effectiveness / ICER / QALY / budget impact** → hta-layer.md#§2 (economic model appraisal) · regulatory-intelligence.md#§3 (epidemiology denominator) · evidence-grading.md#§2–§3 (GRADE/NMA appraisal)
- **NICE / CADTH / PBAC / IQWiG / HAS / HTA body** → hta-layer.md#§1 (HTA bodies) · hta-layer.md#§2 (body-specific model requirements)
- **MAIC / NMA / indirect comparison** → hta-layer.md#§2 (economic model) · evidence-grading.md#§3 (pragmatic appraisal track) · evidence-grading.md#§4 (specialty checklists)
- **Reimbursement listing / payer decision / access / geri ödeme** → hta-layer.md (all) · turkiye-layer.md#§3 (SUT/Mevzuat) · turkiye-layer.md#§5 (turkey_access_summary sidecar)
- **Value dossier / submission / dosya** → hta-layer.md#§2 (economic appraisal) · regulatory-science-layer.md#§4 (output §1.I)

### Evidence Type

- **RCT / randomized controlled trial / Phase 3** → evidence-grading.md#§1–§2 (Tier hierarchy + GRADE) · output-templates.md#§1 (Küresel Literatür scaffold) · evidence-grading.md#§4 (specialty appraisal)
- **Systematic review / meta-analysis / SR / Cochrane** → evidence-grading.md#§1 (Tier 0 hierarchy) · output-templates.md#§7 (Tier 0 Sentez) · evidence-grading.md#§2 (GRADE per outcome)
- **Real-world evidence / RWE / registry / observational** → evidence-grading.md#§3 (pragmatic track) · rare-disease-layer.md#§2 (registry endpoint) · regulatory-intelligence.md#§6 (epidemiology payload)
- **Case series / single-arm / small-n** → rare-disease-layer.md#§2 (evidence specifics small-n) · evidence-grading.md#§3 (pragmatic track) · evidence-grading.md#§4 (specialty checklist)
- **Preprint / bioRxiv / medRxiv** → evidence-grading.md#§1 (Tier 6 preprint) · connector-registry.md#§2.1 (academic literature core)
- **GRADE / certainty / RoB / downgrading** → evidence-grading.md#§2 (GRADE per outcome) · evidence-grading.md#§4 (specialty checklists) · output-templates.md#§7 (Tier 0 synthesis)
- **Full text / PMC / open access / copyright** → fulltext-retrieval.md (all) · connector-registry.md#§3.5–§3.6 (annas-mcp + EPMC copyright gate) · extended-api.md#§5 (Unpaywall/DOAJ)

### Full-Text / KOL / Pipeline

- **Full-text retrieval / PMC / annas-mcp / Wiley / paywalled** → fulltext-retrieval.md (all) · extended-api.md#§5 (Unpaywall) · connector-registry.md#§3.5–§3.6
- **KOL / Key Opinion Leader / kilit kanaat önderi / author network** → medaffairs-ops-layer.md#§3 (KOL identification wiring §8) · output-templates.md#§8 (KOL Haritası) · extended-api.md#§2 (OpenAlex) · extended-api.md#§4 (Semantic Scholar) · turkiye-layer.md (TR KOL via YÖK Akademik)
- **Pipeline snapshot / AdisInsight / drug development / Phase 1–3 clinical** → drug-intelligence-layer.md (all) · drug-intelligence-layer.md#§6 (pipeline_payload sidecar) · connector-registry.md#§3.1 (AdisInsight real schema) · output-templates.md#§19 (drug intelligence snapshot)
- **Competitive set / pipeline landscape (structured only)** → drug-intelligence-layer.md#§3.2 (competitor set, AdisInsight/CT.gov) · output-templates.md#§20 (cross-layer notes). (OSINT/web competitive intelligence removed v1.4.0 → out of scope; external `pharmaintel`.)

### Connector / Tool Routing

- **PubMed / MEDLINE / EuropePMC / EPMC / Unpaywall / açık-erişim tam-metin** → connector-registry.md#§2.1 (academic literature core + bundled `pubmed-epmc`: `pubmed_europepmc_search`/`pubmed_fetch_fulltext` Unpaywall legal-OA) · output-templates.md#§1 (Küresel Literatür) · evidence-grading.md#§1 (Tier 2 primary sources)
- **ClinicalTrials.gov / CT.gov / NCT** → connector-registry.md#§2.1 · output-templates.md#§2 (Klinik Pipeline) · drug-intelligence-layer.md#§3.5 (trial intelligence)
- **AdisInsight / search_drugs / get_drug / HyDE / generate_chart** → drug-intelligence-layer.md#§1–§3 (real schema) · connector-registry.md#§3.1 (AdisInsight corrected schema)
- **TİTCK / TİTCK-cache / barcode lookup** → turkiye-layer.md#§2 (TİTCK structured queries) · connector-registry.md#§2.5 (α-layer) · connector-registry.md#§3.2 (TİTCK structural Turkey data)
- **openFDA / FDA drug / FAERS / enforcement** → regulatory-intelligence.md#§1 (native openFDA) · connector-registry.md#§3.3 (regulatory MCP)
- **Mevzuat / SUT / kararname / kanun** → turkiye-layer.md#§3 (Mevzuat native legislation) · regulatory-intelligence.md#§4 (multi-jurisdiction)
- **web research / gap-fill / no-API source (EMA, guideline PDF, GLOBOCAN)** → NONE — web tier (Exa/Tavily) removed v1.4.0; report as documented gap (connector-registry.md#§0 tier 3, #§5 zero-result recovery), never web-scraped/fabricated
- **YÖK Akademik / Turkish academics / TR KOL** → turkiye-layer.md (TR KOL) · medaffairs-ops-layer.md#§3 (KOL wiring §8) · connector-registry.md#§2.5 (α-layer)
- **OpenAlex / Semantic Scholar / citation graph / atıf-ağı / kurum-yazar disambiguasyon** → connector-registry.md#§2.1 (native Tier-K bundled: `openalex_*`, `search_papers`/`get_paper_citations`) · extended-api.md#§2–§4 (REST fallback) · medaffairs-ops-layer.md#§3 (KOL via OpenAlex) · output-templates.md#§8 (KOL Haritası)
- **ChEMBL / PubChem / chemical structure** → extended-api.md#§3 (PubChem PUG-REST) · drug-intelligence-layer.md#§4 (cross-reference)
- **WHO GHO / ICD-11 / GLOBOCAN / disease burden** → ICD-11 via `openfda` `icd11_search` (connector-registry.md#§3.3) · hta-layer.md#§3 (epidemiology denominator) · output-templates.md#§21 (0.5.K block). (WHO GHO/GLOBOCAN native-API not bundled → documented gap.)

### Output / Presentation

- **Clean copy / temiz kopya / journal-style report / bilimsel rapor** → report-presentation.md (all) · output-templates.md#§5 (emission discipline) · SKILL.md Adım 5
- **Sidecar / OPS annex / data.json / coverage_set** → report-presentation.md#§0 (two-output model) · output-templates.md#§4 (sidecar schema) · composition-runbook.md#§3 (sidecar as contract)
- **Visualization / VIZ directive / chart / görselleştirme** → report-presentation.md#İlke 5 (visualization directives) · connector-registry.md#§2.4 (output/compose/visualize) · drug-intelligence-layer.md (generate_chart)
- **Format class A–I / adaptive format** → output-templates.md#§2 (format classes A–I) · report-presentation.md (clean-copy skeleton)
- **carbon-html-report / renderer handoff** → report-presentation.md (renderleyiciye devir notu) · composition-runbook.md#§1 (downstream handoffs)
