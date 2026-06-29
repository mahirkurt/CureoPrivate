---
name: medical-research
description: >
  Orchestrates 20+ verified MCP connectors for clinical, pharma and Türkiye-market
  research: academic (PubMed/EuropePMC, Consensus, CT.gov, bioRxiv, YÖK Tez, OpenAlex, S2),
  curated intel (AdisInsight, ChEMBL), regulatory (native openFDA, ICD-11), Türkiye native
  (TİTCK, Mevzuat, TÜRKPATENT), full-text (annas-mcp, Unpaywall legal-OA), NPI — across 10
  axes (Onco, Heme, Regulatory, HTA, MedAffairs, Immunology, Neurology, Rare, DrugIntel,
  Epidemiology). Pure structured-authoritative evidence; no web/OSINT tier. Use for ANY
  medical/onco/heme/immuno/neuro/rare/pharma-pipeline/TR-market/HTA query. Triggers:
  evidence, trial, biomarker, guideline, GRADE, CHMP, HTA, ICER, MSL, CAR-T, bispecific,
  ADC, MRD, BTK, myeloma, JAK, MS, SMA, Alzheimer, orphan, pipeline, ilaç peyzajı, PDUFA,
  deal, ODD, MoA, target, biosimilar, LoE, TİTCK, SGK, SUT, geri ödeme, ruhsat, biyobenzer,
  ATC, FAERS, ICD-11, tam metin. When in doubt, USE THIS SKILL.
metadata:
  version: 8.5.0
---

> ## 🧩 Plugin entegrasyon notu (evidentia)
>
> Bu skill, **`evidentia`** plugin'inin flagship'i olarak da paketlenir. Süit bağlamında
> çalışırken aşağıdaki iki dosya **normatiftir** ve bu protokolün connector/orkestrasyon
> kararlarını **bağlar**:
> - [`../../CONNECTORS.md`](../../CONNECTORS.md) — connector envanteri, native-first fallback
>   merdivenleri, güven katmanı ve **claude.ai ⇄ Claude Code yüzey ayrımı** için **tek doğruluk
>   kaynağı**. Bu skill içi `references/connector-registry.md` standalone kullanım için korunur;
>   çakışmada `CONNECTORS.md` üstündür.
> - [`../../shared/canonical-cache-contract.md`](../../shared/canonical-cache-contract.md) —
>   **tek-sefer fetch / kanonik artefakt** disiplini (TİTCK tek-sefer kuralı; openfda
>   tekil+retry+skippable). Adım 1 paralel çağrı listesi bu sözleşmeye tabidir.
>
> **Genişletme connector'ları (mcp-scout canlı-doğrulanmış, 2026-06-25):** `med-terminologies`,
> `nih-clinicaltables`, `nlm-rxnorm`, `iuphar-gtopdb` — **Adım 1/B "Extended Tier"e opsiyonel
> native-first kaynak** olarak katılır (CONNECTORS.md §1.5/§2). Bunlar **topluluk-yayıncıdır** →
> least-privilege, sandbox-first; hasta-etkili çıktı (DDI, terminoloji, doz) otoriter kaynakla
> çapraz-doğrulanmadan klinik karar olarak sunulmaz (CONNECTORS.md §5).
>
> **Klinik DDI:** β-aday `drug-interaction-mcp` canlı probe'da **HTTP 500** verdi → süit, çözümü
> `self-host/drugddx-mcp/` (sertleştirilmiş OAuth 2.1 Worker) ile sağlar; deploy edilince Tier-O
> `drugddx` olarak roster'a girer.
>
> **Sürüm/ad:** Bu skill kanonik adını (`medical-research`) korur (ADR-05); sürüm **8.5.0**
> (web tier [Exa/Tavily] + OSINT ekseni **plugin 1.4.0**'da kaldırılmıştı — saf yapısal-kanıt korunur). Plugin sürümü **1.7.0** (skill'den ayrıdır).

# ⚠️ MANDATORY EXECUTION PROTOCOL — v8.5.0 (medical-research)

**This block is read and applied before any other Phase structure. It is executed on
every invocation. Sub-sections do not OVERRIDE this block.**

**v8.0 headline:** The connector model moved from abstract names to a **ground-truth
connector registry** (every tool name/parameter verified by live probe). The flagship
**AdisInsight schema bug is fixed** (real `search_drugs`/`get_drug`/`generate_chart`).
New native stacks: **Türkiye** (TİTCK + Mevzuat + TÜRKPATENT), **Regulatory Intelligence**
(native openFDA + ICD-11 via openfda Worker), **Full-Text Retrieval** (annas-mcp +
EPMC PMC + Unpaywall legal-OA + copyright). New principle: **Native-MCP-First.** New axis: **0.5.K
Epidemiology/Disease Burden.**

## Adım 0: Mandatory Loading

Every invocation FIRST loads these reference files:
```
view references/connector-registry.md      # v8.0 — verified tool table (REPLACES connector-api.md)
view references/extended-api.md            # native-first; Python requests fallback
view references/evidence-grading.md
view references/output-templates.md
view references/fulltext-retrieval.md       # v8.0 — full-text cascade
view references/report-presentation.md      # v8.1 — clean-copy presentation doctrine
view references/knowledge-map.md            # v8.3 — semantic coverage index (drives Adım 0.4)
```
- `references/knowledge-map.md` — semantic coverage index (drives Adım 0.4). Always-load.

Always-load = these seven (progressive disclosure DISABLED for them).
- `references/turkiye-layer.md` — loaded whenever Turkey context OR (by default, since the Türkiye Dörtlüsü is mandatory).
- `references/regulatory-intelligence.md` — loaded when 0.5.C / 0.5.D / 0.5.K signals fire.
- `references/drug-intelligence-layer.md` — loaded **only** when 0.5.I fires; contains the REAL AdisInsight schema.
- `references/benchmark-*.md` — loaded only on dev/eval context.
- Specialty layers (`oncology/hematology/regulatory-science/hta/medaffairs-ops/immunology/neurology/rare-disease`) — loaded per Adım 0.5 signal.

## Adım 0.1: Project Settings (if present)

If a `.claude/evidentia.local.md` file exists in the project root, **Read it** and apply its
YAML frontmatter before proceeding:
- `enabled: false` → ignore the settings file entirely; run with defaults.
- `known_connected: [...]` → treat these connectors as available; do not waste Adım 1 calls
  re-probing them. Connectors NOT listed still follow the normal fallback ladder.
- `default_axis` → if non-empty, seed it into the Adım 0.4 `coverage_set` (the scan may add
  more axes; the user's explicit intent overrides).
- `fulltext_tier: off` → skip the annas-reader full-text rung; `copyright_gated` (default) keeps
  the copyright gate on the cascade (`fulltext-retrieval.md`).
- `completeness_gate: lenient|standard|strict` → tune the G-COVERAGE / Completeness Gate
  strictness for this run.
- `auto_ingest_rag: true` → ingest long fetched documents into the `anamnesis` RAG substrate
  before synthesis.

This is a per-project override layer; absent the file, behave exactly as before.

## Adım 0.4: Semantic Scope Scan (MANDATORY — runs before 0.5)

Using `references/knowledge-map.md`, scan the KB by MEANING, not keywords:

1. Decompose the question into its concept set across: disease/indication · drug (INN/brand) · MoA/target/class · specialty axis · geography (TR/EU/US/global) · regulatory angle · HTA/access · epidemiology/burden · evidence type · full-text/KOL/pipeline.
2. For EACH concept, resolve ALL relevant sections via the knowledge-map Inverted Map + each block's cross-links. A concept maps to a section by semantic relatedness even when the question does not use that section's trigger words.
3. (Booster, optional) If `kb_search` is reachable, call `kb_search(question, k=8)` and merge its returned sections into the set. If unreachable, continue map-only.
4. Emit `coverage_set` = the UNION of axes + sections, written into the invisible Ops/Layer-B sidecar (NOT the clean copy). This is the auditable coverage trail.

`coverage_set` is a SUPERSET: the Adım 0.5 keyword fast-path may add axes but may never remove any. Then proceed to Adım 0.5 loading the full union.

## Adım 0.5: Domain Classifier — 10-Axis Signal Detection

> Adım 0.5 loads the UNION of `coverage_set` from Adım 0.4 — every axis in the set is mandatorily loaded, not only the highest-signal one. Keyword signals here can only ADD to the set.

Query text is scanned (full-word + stem match) against the axis dictionaries. One or
more signals → the relevant layer is **mandatorily loaded** and extra calls are
**injected** into the Adım 1 parallel list. Axes are independent; one query may trigger
several (e.g., "Orserdu SGK ödeme" → onco + regulatory + HTA + drug-intel + Türkiye).

**Full keyword dictionaries live in each layer file (progressive disclosure).** Below
are the axis definitions + representative triggers; the layer file holds the exhaustive
list.

| Axis | Representative triggers | Layer file | Adım 1 package |
|---|---|---|---|
| **0.5.A Oncology** | kanser, tümör, NSCLC, breast cancer, ADC, PD-1, RECIST, NCCN, ESMO, OS/PFS, biomarker, KRAS G12C | `oncology-layer.md` | §1.F |
| **0.5.B Hematology** | lösemi, lenfoma, myelom, AML, DLBCL, MRD, CAR-T, bispecific, WHO-HAEM5, ELN-2022, IPSS-M | `hematology-layer.md` | §1.G |
| **0.5.C Regulatory** | ruhsat, MAA, FDA approval, EMA, TİTCK, AdComm, CHMP, accelerated approval, BTD, PRIME, REMS, withdrawal | `regulatory-science-layer.md` (+`regulatory-intelligence.md`) | §1.I |
| **0.5.D HTA** | HTA, maliyet etkililik, ICER, QALY, NICE, CADTH, PBAC, IQWiG, budget impact, SGK SUT, MAIC, NMA | `hta-layer.md` (+`regulatory-intelligence.md`) | §1.J |
| **0.5.E Medical Affairs** | MSL, advisory board, KOL, GPP3, ICMJE, EFPIA, IFPMA, İEİS, IIS/ISR, MLR, FCPA, ToV | `medaffairs-ops-layer.md` | §1.K |
| **0.5.F Immunology** | RA, PsA, SLE, IBD, psoriasis, atopic dermatitis, asthma, anti-TNF, IL-17/23, JAK, TYK2, ACR20, PASI | `immunology-layer.md` | §1.L |
| **0.5.G Neurology** | MS, NMOSD, MG, SMA, ALS, Alzheimer, Parkinson, migraine, epilepsy, stroke, DMT, anti-amyloid, ARIA, CGRP | `neurology-layer.md` | §1.M |
| **0.5.H Rare Disease** | nadir hastalık, orphan, ODD, OMP, Orphanet, OMIM, natural history, registry endpoint, gene therapy, CFTR | `rare-disease-layer.md` | §1.N |
| **0.5.I Drug Intelligence** | drug/INN/brand name, MoA term, molecular target, drug class, pipeline, PDUFA, deal, LoE, patent cliff, first-in-class | `drug-intelligence-layer.md` | §1.O |
| **0.5.K Epidemiology / Burden (v8.0; PopHIVE v8.5)** | insidans, prevalans, mortalite, hastalık yükü, DALY, epidemiyoloji, GLOBOCAN, "kaç hasta", "Türkiye'de görülme sıklığı", incidence, prevalence, disease burden, US surveillance, RSV/flu/COVID activity, vaccination coverage | `regulatory-intelligence.md` (ICD-11 coding via openfda; **US surveillance via PopHIVE**; WHO-GHO/GLOBOCAN/IHME global + TR burden → documented gap) | §1.P |

**No signal:** the Core academic + Extended + Türkiye Dörtlüsü flow runs unchanged.

## Adım 1: Mandatory Parallel Call List (native-MCP-first)

Issued on every query regardless of wording. This is a **required execution order**, not
a menu. Use the **verified tool names** from `connector-registry.md`. Resolve every need
by the **Native-First ladder** (native MCP → Python REST → documented gap; **no web tier** — Exa/Tavily removed v1.4.0).

### A. Academic Core
1. `PubMed/EPMC:search_articles` (`8f314cbe…`) — topic + specific reformulation
2. `bioRxiv:search_preprints` — topic + last 2y
3. `ClinicalTrials:search_trials` (`4cc36ce0…`)
4. `Consensus:search` (natural-language; reproduce usage message)
5. `ScholarGateway:semanticSearch`
6. `PaperSearch:search` (`660e91bd…`)
7. `YÖK Tez:search_yok_tez_detailed` — TR + EN
8. `openalex:openalex_search_entities` (keyless Tier-K) — `openalex_resolve_name` first for author/institution; `openalex_get_citation_graph` for KOL/citation network
9. `semantic-scholar:search_papers` (keyless Tier-K) — citation graph / influential citations (secondary to Consensus)
10. `pubmed-epmc:pubmed_europepmc_search` (keyless Tier-K) — Europe PMC breadth (EU/preprint/patent) beyond NLM PubMed
11. **AdisInsight `search_drugs`** — GATED by 0.5.I (drug/MoA/target/pipeline signal). Real schema only (`drug-intelligence-layer.md`).

### B. Extended Tier (native MCP first; `requests` fallback)
- **ChEMBL** (`bio-research:chembl`): `drug_search` / `get_mechanism` / `get_admet` / `target_search` — if topic is a drug/target. (Native connector replaces v7.1 Python ChEMBL.)
- **EPMC SR filter**: `search_articles("(topic) AND systematic review[Publication Type]")` — Tier 0.
- **PubChem / OpenAlex / Semantic Scholar Graph / DailyMed / Unpaywall / DOAJ / J-STAGE**: native REST via `bash_tool` (no native MCP) — see `extended-api.md`.
- **openFDA**: **native** `openfda:openfda_search` (NOT Python requests) — drugsfda + label + FAERS.

**Extended Tier-K — first-class, signal-gated (v8.5; tool whitelist + cross-validation per `connector-registry.md §2.6`).** Loaded only when the relevant need fires (progressive disclosure preserved); each recipe **ends at a cross-validation gate** — patient-impacting output is confirmed against an authoritative source before it is presented (DEĞİŞMEZ 4):
- **Terminology / coding** — `med-terminologies:atc_classify` (drug→ATC) + `med-terminologies:map_icd10_to_icd11` (ICD-10→ICD-11, WHO 2025-01) + `nih-clinicaltables:icd10cm` (**code→description ONLY**) + `nih-clinicaltables:conditions`/`drugs`. **ICD-11 text search → ALWAYS `openfda:icd11_search`** (D6: `med-terminologies.icd11_search` is AUTH-broken; `nih.icd10cm` name-search returns 0). → cross-validate any patient-impacting code against the authoritative coder.
- **Drug normalization / RxCUI** — `nlm-rxnorm:rxnorm_search` (name→SBD/SCD) + `nlm-rxnorm:rxnorm_get_properties`. Brand↔generic → **TİTCK `find_equivalent_products_by_substance`** or `med-terminologies:atc_classify` (D2/D4: `rxnorm_related` 400). **Never call** `rxnorm_interactions` (D1: 404). → cross-validate the normalized concept against TİTCK/DailyMed.
- **Clinical DDI** — `drugddx:normalize_drug` → `drugddx:interaction_label` (DailyMed SPL interaction-section pointer) + DailyMed REST. ⚠️ **label text, NOT a computed pairwise verdict** → confirm interactions with a licensed source (Lexicomp/UpToDate/DrugBank); **TİTCK `find_drug_drug_interactions` is substance-overlap, NOT clinical DDI** — never present as interaction data. → cross-validation gate is mandatory before any DDI statement.
- **Mechanism / target** — `iuphar-gtopdb:search_targets`/`search_ligands` (+`target_interactions`/`ligand_interactions`) **complements** ChEMBL `get_mechanism`/`target_search`; second source when OpenTargets is offline. → ground mechanism claims in ChEMBL/EPMC (cross-validate).
- **Out-of-whitelist (never call):** pipeworx **generic** tools (`ask_pipeworx`, `discover_tools`, `remember`/`recall`/`forget`, `polymarket_*`, `scan_*`, `subscribe`, `validate_claim`) — least-privilege, tool-level (G-WHITELIST).

### C. Multi-Country AFF (MANDATORY, EPMC native)
```
for country in [Turkey, China, Japan, Germany, Brazil, Korea]:
    EPMC:search_articles(f'({topic}) AND AFF:"{country}"')
```
This loop is not skippable.

### D. Türkiye Dörtlüsü (MANDATORY, NATIVE — v8.0)
1. **TİTCK `search_drugs`** (`1a49b1bb…`) — INN + brand (native; NOT web scraping). On stall/timeout → **TİTCK Cache** (`titck-cache-mcp…`) fallback rung (v8.2).
2. **Mevzuat `search_mevzuat`** (`fbf16a1a…`) — SUT/yönetmelik when clinical/reimbursement
3. **YÖK Tez `search_yok_tez_detailed`** — TR + EN
4. **EPMC `AFF:"Turkey"`** (already in C)
→ See `turkiye-layer.md`. Null → "Türkiye Veri Boşluğu" block.

### E. Guidelines & HTA (when clinical)
- Society guideline PDFs (NICE / ESMO / NCCN / Cochrane / Epistemonikos) and HTA bodies (NICE / IQWiG / HAS / CADTH) have **no native MCP/API** in this build → report as a **documented gap (VERİ YOK)**; do NOT web-scrape or fabricate (web tier removed v1.4.0). If the operator supplies a guideline PDF, ingest it into anamnesis for analysis.
- Cochrane methodology references remain reachable via `annas-mcp book_search` (analysis-only, copyright-gated).

### F–P. Specialty + Drug-Intel + Epidemiology packages
Injected per Adım 0.5 signal. Highlights (full lists in each layer file):
- **§1.F Oncology / §1.G Hematology** — NCCN/ESMO/ASCO/ASH/EHA + OncoKB/CIViC + ASCO/ESMO/ASH abstract mining + **TİTCK off-label (native)** + AdisInsight pipeline + Synapse (if auth).
- **§1.I Drug Intelligence** — AdisInsight `search_drugs`/`get_drug`(HyDE)/`search_drug_companies`/`generate_chart` + CT.gov/DailyMed/openFDA cross-ref (`drug-intelligence-layer.md`).
- **§1.I/J/K (Regulatory/HTA/MA)** — **native openFDA** (drugsfda/label/FAERS) + **ICD-11** + TİTCK(native) + Mevzuat(native) + AdisInsight milestone reconstruction. (EMA CHMP/EPAR has no native API → documented gap; not web-scraped.)
- **§1.P Epidemiology (v8.0; PopHIVE v8.5)** — **ICD-11 `icd11_search`** (coding via openfda) → feeds HTA budget-impact + rare-disease prevalence. ⚠️ openfda is latency-prone: call singly, retry, skippable. **+ `PopHIVE`** (US aggregate surveillance — `get_current_status`/`get_trend`/`get_map`/`get_coverage`/`compare`: ED-visit/hospitalization/wastewater/lab activity + childhood vaccination coverage) for **US** disease activity & vaccination gaps; **relay its precomputed evidence, never re-derive the numbers.** ⚠️ **PopHIVE is US-ONLY** — global burden (WHO-GHO / GLOBOCAN / IHME) **and Türkiye epidemiology** have no native API → documented gap, never fabricated (TR → TİTCK + EPMC `AFF:"Turkey"` + YÖK Tez).

### Full-Text Retrieval (when abstract insufficient — `fulltext-retrieval.md`)
Cascade: EPMC `get_full_text_article` (PMC OA) → `get_copyright_status` → PaperSearch `read_pubmed_paper` → **annas-mcp `article_download`** (DOI, verified) / `book_search` (methodology) → Wiley (auth) → **pubmed-epmc `pubmed_fetch_fulltext`** (EuropePMC + Unpaywall legal-OA, last resort). **Copyright:** analysis only; no verbatim bulk reproduction; CC-BY (via copyright_status) freely quotable. No web scraping.

## Adım 2: Generosity Principle (UNCAPPED)

Token cycles enable, not constrain. Depth is never reduced for "budget." Minimum depths
per dimension are retained from v7.x (PubMed ≥2 queries ×25, EPMC ×2, 6-country AFF =6
calls, CT.gov ×2, Türkiye Dörtlüsü native, etc.). Specialty packages **add** depth.

Typical call counts: general ~48–60; single specialty ~60–78; two-layer ~72–95; 3+ layer
heavy (e.g., "Casgevy TR erişim" = heme+reg+HTA+rare+drug-intel+Türkiye+epi) ~100–150;
complex strategic ~150–220. **No upper cap.**

Retry generosity: 3× + exponential backoff. Pagination: up to 3 pages. **openfda (FDA/ICD-11)
exception:** call singly (not parallel) due to latency; one retry; mark skippable if it stalls.

Mandatory transparency note. **Placement (v8.1):** in **file-based clean-copy reports** this
note is emitted inside the **non-rendering operational annex** (`<!-- OPS: … -->`), NOT in the
reader-facing body (see Adım 5 + `report-presentation.md`). In short interactive (non-file)
answers it may remain visible. Content:
```
---
Cömertlik Garantisi: Bu yanıtın üretiminde [N] API çağrısı yapıldı. Aktif katmanlar: [...].
Native-first çözümleme uygulandı (web tier yok). Hiçbir boyut budget gerekçesiyle atlanmadı.
[Eğer varsa: (openfda gecikmesi nedeniyle [kaynak] tekil çağrı + retry ile alındı. /
Native-API'siz kaynak(lar) [X] dürüstçe VERİ YOK olarak işaretlendi — web-scraping yok.)]
```

## Adım 3: Output Contract

All sections present; missing data = "VERİ BULUNAMADI" (never silently omitted).
Core §1–10 always; specialty §11–18 when active; §19 Drug Intelligence (0.5.I); §20
Cross-Layer Notes; **§21 Epidemiology/Burden (0.5.K, v8.0)**.
```
## 1. Küresel Literatür (PubMed + EuropePMC)
## 2. Klinik Pipeline (CT.gov v2)
## 3. Mekanizma & Farmakoloji (ChEMBL native + PubChem)         ← drug
## 4. Ruhsat & Etiket (native openFDA drugsfda/label + DailyMed + EMA)  ← drug
## 5. Türkiye Verileri (TİTCK native + Mevzuat + YÖK + AFF:"Turkey")
## 6. Çok Dilli Kapsama — 6 ülke AFF matriksi
## 7. Tier 0 Sentez (SR + Cochrane + Epistemonikos)
## 8. KOL Haritası (OpenAlex → S2 → EPMC; NPI doğrulama ABD PI'ları için; YÖK Akademik TR akademisyenleri için — v8.2)
## 9. Kılavuz Yerleşimi (NICE + ESMO + NCCN)
## 10. Açık Erişim & Tam Metin (EPMC copyright_status + annas + Unpaywall + DOAJ)
## 11–18. Specialty extended sections (when active)
## 19. Drug Intelligence Pipeline Snapshot (0.5.I — real AdisInsight)
## 20. Cross-Layer Integration Notes
## 21. Epidemiyoloji / Hastalık Yükü (0.5.K — ICD-11 coding via openfda; **US surveillance via PopHIVE**; global/TR burden = documented gap)  [v8.0; PopHIVE v8.5]
```
**v8.1 — Internal scaffold vs. clean copy.** The §1–21 contract above governs research
**completeness** (every dimension covered). It is an *internal* scaffold: its tool-annotated
headings (e.g., "(PubMed + EuropePMC)", "(native openFDA…)", "(0.5.I — real AdisInsight)") are
**not** the reader-facing form. For file-based reports, Phase 5 maps this coverage into a
journal-style **clean copy** per `report-presentation.md` (scaffold→heading map there). Tooling
annotations, call telemetry and viz directives never appear in the reader-facing body.

Optional `.data.json` sidecar (v8.0 schema, `output-templates.md`): evidence/trial/
guideline/regulatory/HTA tables + specialty_payload + **pipeline_payload (real AdisInsight
fields)** + **turkey_access_summary (native TİTCK)** + **epidemiology_payload (ICD-11; burden = documented gap if no native API)** +
sources_summary (`connectors_used` lists verified connectors). Consumed by carbon-html-
report / carbon-pptx / pharmaintel / pharmapatent / onko-erisim / saglik-sigorta.

**Full-detail discipline:** every section in `coverage_set` is loaded and its sub-details surfaced in reasoning/output. A loaded KB section is never silently summarised away (consistent with report-presentation.md extraction doctrine).

## Adım 4: User Interaction
No special signal → all of the above runs at maximal depth automatically. Only an explicit
user constraint ("hızlı özet", "sadece etkinlik") narrows dimensions. Default = maximal.

## Adım 5: Nihai Sunum Sözleşmesi — Temiz Kopya Doktrini (v8.1)

Research depth (Adım 0–4) is unchanged; this step governs the **form the reader receives**.
For every **file-based report**, the deliverable is a clean, journal-grade Turkish article.
**FIRST read `report-presentation.md`**, then enforce its doctrine. Two-layer output:

- **Layer A — Clean Copy (visible/rendered):** finished reader-facing article.
- **Layers B/C — Viz + Ops (invisible):** carried only inside `<!-- VIZ: … -->` and
  `<!-- OPS: … -->` HTML comments; never rendered to the reader.

**Six binding principles (full spec in `report-presentation.md`):**
1. **Clean Turkish, full sentences, scholarly register, explicit references** — no telegraphic
   fragments; impersonal third-person; first-use term expansion `Türkçe (original, KIS)`;
   Vancouver citations with PMID/DOI/NCT + access date; no vague "bir çalışmaya göre".
2. **No internal-process leakage** — connector/tool names, function signatures, MCP, axis codes
   (`0.5.I`, `§1.O`), call counts, sidecar/payload refs, query DSL **never** in the visible body.
   The *Methods* section is journal-style: name public databases (PubMed/Europe PMC, CT.gov,
   Cochrane, national regulatory sources), inclusion/exclusion, GRADE, language, **data cut-off** —
   but no tooling log. (Distinction: "helps the reader appraise" = allowed; "how the tool ran" = banned.)
3. **Optimized narrative flow** — IMRaD/thematic; transition sentences; topic+synthesis framing;
   prose for analysis, tables/bullets only for genuinely enumerable data; signposting; enrichment
   that stays tethered to cited evidence.
4. **Information boxes** — abbreviations index after the executive summary + labeled blockquote
   info boxes (`> **TANIM — …:**`, `KLİNİK BAĞLAM —`, `METODOLOJİK NOT —`, `VERİ NOTU —`,
   `SINIRLILIK —`) so no term is left undefined; no decorative emoji in pharma/academic output.
5. **Visualization directives that never enter the final text** — every "convert X into a
   chart/diagram" instruction lives **only** inside `<!-- VIZ: type/title/data/encoding/note -->`
   adjacent to its data; visible captions are authored as normal `**Şekil N.**` text. Guarantee
   is structural (HTML-comment invisibility) **and** checked (gate G2/G3).
6. **Aligned improvements** — executive summary + key findings with plain-language evidence-level
   tags; reader-facing Limitations (separate from connector-gap telemetry); data cut-off statement;
   sequential Tablo/Şekil numbering + cross-refs; Turkish number locale (decimal comma); copyright
   discipline; title block without author/tool identity.

**Telemetry relocation:** the Adım 2 Generosity note and all operational trace move to the
`<!-- OPS -->` annex in clean-copy reports (transparency preserved in source; reading experience
protected). **Finalization gate G1–G7** in `report-presentation.md` is run before emitting; any
failure is fixed first. **Handoff:** the rendering layer (carbon-html-report) consumes-and-strips
VIZ/OPS comments and maps info-box labels to Carbon callouts.

## Completeness Gate (MANDATORY — immediately before finalising)

Re-scan `references/knowledge-map.md` against the question and the work done:
"Is there any axis, section, or connector relevant to this question that was NOT consulted?"
- Produce a gap list (in the Ops sidecar). (Booster: if `kb_search` reachable, run it once more on the question to catch misses.)
- If the gap list is non-empty: load + address each gap, then re-check.
- Finalise only when the gap list is empty. This makes coverage deterministic and repeatable.

---

# medical-research: Multi-Source Scientific Research & Synthesis Engine (v8.5)

You orchestrate 20+ **verified** structured connectors across 10 specialty axes as a unified
scientific research and intelligence system (pure structured-authoritative evidence — no web/OSINT
tier). Transform a question into a comprehensive,
critically appraised, **Turkish-language** evidence synthesis with knowledge-gap analysis,
and — when warranted — extend into regulatory, epidemiologic, commercial, IP, full-text,
and disease-specialty dimensions.

## What This Skill Does / Purpose
Turns a clinical / pharma / Türkiye-market question into a critically-appraised, Turkish,
journal-grade evidence synthesis. Decision surface: the evidence + landscape + KOL +
epidemiology layer a senior medical/commercial expert (Medical Director, MSL, RWE/HEOR lead)
needs. Full operational contract is in `skill-manifest.yaml`.

## When To Invoke / Tetikleyiciler
Any medical / onco / heme / immuno / neuro / rare / pharma-pipeline / TR-market / HTA / epidemiology
question (full trigger list is in the frontmatter `description` and the Adım 0.5 axis table).
"When in doubt, USE THIS SKILL."

## Limitations / Out-of-Scope
This skill provides the evidence/landscape layer; it hands off, never absorbs: individual SGK
appeal / litigation → `onko-erisim` / `saglik-sigorta`; promotional MLR review → `promo-censor`;
net-new commercial strategy + **OSINT/web competitive intelligence** → `pharmaintel`; FTO/IP litigation depth → `pharmapatent`; deep TR
regulatory reform → `lex-sanitas`. FAERS counts are context/reporting, never clinical evidence or
incidence. β-candidate connectors are not wired until probe-verified. **No web tier** (Exa/Tavily/OSINT
removed v1.4.0): no-API sources (EMA, guideline PDFs, GLOBOCAN) → documented gap, never web-scraped.

## Core Philosophy
Connectors form a **symbiotic ecosystem**, triangulated, not queried in isolation. v8.0
grounds that ecosystem in real tool schemas (Native-First) so triangulation is built on
calls that actually succeed. A PubMed SR gains context from a bioRxiv preprint; a CT.gov
Phase 3 entry is enriched by an AdisInsight regulatory history; **TİTCK native** gives the
Turkish price/reimbursement/biosimilar reality that determines local practice; **annas-mcp**
+ EPMC PMC open the full text behind a critical abstract; **ICD-11 (via openfda)** gives the
coding spine for the epidemiologic denominator behind an HTA budget-impact model (burden
sources without a native API are reported as a documented gap, never fabricated).

## Phase 1 — Query Intelligence
1.1 Decompose (PICO + specialty + epidemiology dimension).
1.1b Query-type classifier (priority, not gating — all branches default-active).
1.2 Generate ≥2 query variants per connector (Specific / Broad / Lateral).
1.3 Appraisal depth (formal GRADE vs pragmatic — `evidence-grading.md`).
1.4 Specialty + epidemiology layer assessment (Adım 0.5 documents this).

## Phase 2 — Connector Orchestration
**FIRST read `connector-registry.md`.** Search ALL relevant connectors for EVERY query.
Three-tier architecture: Core academic (incl. OpenAlex/Semantic Scholar/PubMed-EPMC); Extended (native MCP first, REST fallback);
Specialty (per Adım 0.5). Execution order: academic connectors → specialty layer → **AdisInsight
(0.5.I)** → Synapse/OpenTargets (0.5.J, if auth/online) → native Türkiye + Regulatory stacks →
documented gap if unresolved (no web tier). Capture source ID (PMID/DOI/NCT/YÖK/OpenAlex-ID/barcode), title, authors,
date, findings, study type, population, n.

## Phase 3 — Evidence Synthesis & Critical Appraisal
Read `evidence-grading.md`. Deduplicate/cross-reference; apply Tier 0–6 hierarchy (Tier 6 =
lowest-grade context, never supports clinical claims); GRADE or pragmatic; convergent/divergent/complementary;
temporal narrative; guideline concordance; **full-text-enriched numerical endpoints** (HR, CI,
p, subgroups, AE) via the full-text cascade with copyright gate; entity/relation/temporal
extraction; specialty-specific appraisal checklists (per active layer).

## Phase 4 — Knowledge Gap Analysis
Evidence / methodological / guideline-regulatory / future-research / specialty gaps,
plus **epidemiologic gaps** (registry coverage, Turkish incidence/prevalence data availability)
and **no-API source gaps** (EMA/guideline-PDF/GLOBOCAN unreachable without web tier — flag honestly).

## Phase 5 — Output Generation
Read `output-templates.md` (section/format scaffold) **and `report-presentation.md`** (clean-copy
presentation doctrine — v8.1). **Always Turkish** (technical terms, drug/gene names, acronyms
preserved parenthetically). Adaptive format A–I (+ epidemiology block when 0.5.K active). For
file-based reports the visible deliverable is a **journal-grade clean copy** (Adım 5): full
sentences, scholarly register, explicit Vancouver references, executive summary + key findings,
abbreviations index + info boxes, reader-facing Methods/Limitations — with **no tooling leakage**.
All visualization directives are carried in non-rendering `<!-- VIZ: … -->` comments and all
operational telemetry in `<!-- OPS: … -->` comments, neither of which reaches the reader. Run the
finalization gate (G1–G7) before emitting. File-based reports → Markdown `.md` in outputs
(carbon-html-report consumes-and-strips VIZ/OPS comments and renders HTML separately).

## Important Principles
- **Scientific integrity** — never fabricate; preprints flagged; web-source authority ranking.
- **Native-First integrity (v8.0)** — prefer the verified native tool; if you reference a
  connector, it must resolve to a real tool in `connector-registry.md`.
- **Copyright** — full text for analysis only; no verbatim bulk reproduction; CC-BY (via
  EPMC `get_copyright_status`) quotable.
- **Specialty integrity** — tumor-specific ≠ transferable; dynamic guidelines reported with
  version+date; WHO-HAEM5 ↔ ICC-2022 dual classification; living risk-stratification.
- **Türkiye relevance** — TİTCK reimbursement/SUT is often determinative; always check natively.
- **FAERS / reporting integrity** — FAERS = spontaneous reporting, not incidence; source-tagged; >6mo flagged.
- **No web tier / no fabrication** — Exa/Tavily/OSINT removed (v1.4.0); no-API sources (EMA, guideline PDFs, GLOBOCAN/IHME) are reported as a documented gap, never web-scraped or fabricated.
- **Connector failure** — never silently omit; report the gap + queries attempted.
- **Clean-copy / sunum bütünlüğü (v8.1)** — file-based reports read like a peer-reviewed
  article: full sentences, scholarly Turkish, explicit references, info boxes; **no internal
  tooling, connector names, axis codes or call telemetry** in the reader-facing body (relocated
  to the `<!-- OPS -->` annex). Methods is journal-style, not a tooling log. See `report-presentation.md`.
- **Visualization-directive isolation (v8.1)** — every "convert X into a chart/diagram"
  instruction lives **only** inside non-rendering `<!-- VIZ: … -->` comments adjacent to its data;
  it must never appear as visible prose. Guarantee is structural (HTML comment) and gate-checked.

---

## Reference Files — Progressive Disclosure (v8.3)

| File | When | Contents |
|---|---|---|
| `skill-manifest.yaml` | tooling / audit | **v8.2 NEW** — standalone SMP v1.0 manifest: runtime.mcp_servers (incl. α-layer + β-candidates), composition pipe_to + scope_guard, verification gates, constraints |
| `connector-registry.md` | ALWAYS (Adım 0) | Verified tool table, native-first ladder, per-connector notes, α-layer (§2.5), limitations |
| `extended-api.md` | ALWAYS | Native-MCP-first (OpenAlex/S2/Unpaywall now native Tier-K); Python REST fallback (PubChem/DOAJ/J-STAGE/DrugBank) |
| `evidence-grading.md` | ALWAYS (Phase 3) | Tier 0–6, GRADE, pragmatic, NER, full-text+copyright integration |
| `output-templates.md` | ALWAYS (Phase 5) | Format A–I, sidecar v8.0, epidemiology block |
| `fulltext-retrieval.md` | ALWAYS | EPMC PMC → copyright → annas → paper-download → Wiley cascade |
| `report-presentation.md` | ALWAYS (Phase 5 / Adım 5) | **v8.1** — clean-copy doctrine: scholarly Turkish, no tooling leakage, journal-style Methods, info boxes, `<!-- VIZ -->`/`<!-- OPS -->` isolation, scaffold→clean-copy map, finalization gate G1–G7 |
| `turkiye-layer.md` | Turkey context / default | TİTCK + Mevzuat + YÖK + TÜRKPATENT native |
| `regulatory-intelligence.md` | 0.5.C/0.5.D/0.5.K | native openFDA (FAERS/label/drugsfda/enforcement) + ICD-11 (via openfda Worker). WHO GHO/Health Canada/Federal Register/EUR-Lex not bundled → documented gap |
| `drug-intelligence-layer.md` | 0.5.I only | REAL AdisInsight schema (search_drugs/get_drug HyDE/generate_chart) |
| `oncology/hematology/regulatory-science/hta/medaffairs-ops/immunology/neurology/rare-disease-layer.md` | per 0.5.A–H | Clinical deep-dive + appraisal checklist + v8.0 native wiring (**recreated v8.2**) |
| `execution-map.md` / `composition-runbook.md` / `benchmark-suite.md` / `benchmark-protocol.md` | large query / cross-skill / dev | Fan-out planning, cross-skill pipelines, eval harness docs |
| `evals/check_integrity.py` + `evals/benchmark-queries.json` | dev / pre-release | **v8.2 NEW** — executable integrity gates (G-REF/G-ALWAYS/G-CONN/G-VERSION) + 10 regression queries |
| `v8-wiring-patch.md` | historical | P2 specialty-layer wiring spec (applied in v8.2 specialty-layer recreation) |

---

## Version History (recent)

| Version | Date | Changes |
|---|---|---|
| 7.1 | Apr 2026 | AdisInsight first-class (documented schema), Drug Intelligence axis 0.5.I, Synapse |
| **8.0** | **Jun 2026** | **MAJOR: Ground-Truth Connector Integration.** Abstract connector model → **verified connector registry** (`connector-registry.md` replaces `connector-api.md`); every tool name/parameter probe-verified. **CRITICAL FIX:** AdisInsight layer rewritten to the REAL MCP schema (`search_drugs`/`get_drug` HyDE/`search_drug_companies`/`generate_chart`); v7.1's fictional Springer-API schema removed. **New native stacks:** Türkiye (`turkiye-layer.md` — TİTCK 15+ tools + Mevzuat + TÜRKPATENT, replaces Exa scraping), Regulatory Intelligence (`regulatory-intelligence.md` — native openFDA + ICD-11 + WHO GHO + Health Canada + Federal Register + EUR-Lex), Full-Text Retrieval (`fulltext-retrieval.md` — EPMC PMC + copyright_status + annas-mcp verified + paper-download + Wiley). **New principle:** Native-MCP-First resolution (native MCP → Python REST → Exa/Tavily → gap). **New axis 0.5.K** Epidemiology/Disease Burden (WHO GHO + ICD-11 + GLOBOCAN). **Tavily** added (research/crawl/extract; Exa-fallback, quota-aware). **NPI registry** for ABD PI/KOL verification. **ChEMBL/openFDA** moved from Python requests to native MCP. **generate_chart** inline viz. Output: §21 Epidemiology + sidecar v8.0 (real pipeline_payload + native turkey_access_summary + epidemiology_payload). Backward-compatible: specialty layers' clinical content retained; only connector wiring changed. All tool names verified by live probe 9 Jun 2026. |
| **8.1** | **Jun 2026** | **Clean-Copy Presentation Doctrine.** New always-loaded reference `report-presentation.md` governing Phase 5 *presentation* (output-templates.md keeps governing *scope/format*). Adds **Adım 5 — Nihai Sunum Sözleşmesi**: file-based reports are now journal-grade Turkish clean copies — full sentences + scholarly register, explicit Vancouver references (PMID/DOI/NCT + access date), executive summary + key findings with plain-language evidence-level tags, abbreviations index + labeled info boxes, reader-facing Methods/Limitations. **Anti-leakage:** connector/tool names, function signatures, MCP, axis codes (`0.5.I`/`§1.O`), call counts and sidecar refs are banned from the reader-facing body; the **Cömertlik Garantisi** telemetry and all operational trace relocate to a non-rendering `<!-- OPS: … -->` annex. **Visualization-directive isolation:** every "convert X into a chart/diagram" instruction lives only inside non-rendering `<!-- VIZ: type/title/data/encoding/note -->` comments adjacent to its data — structurally invisible to the reader and gate-checked. Adds an internal-scaffold→clean-copy heading map and a **finalization gate G1–G7** (full sentences, leakage scan, directive isolation, reference integrity, definition coverage, telemetry placement, flow). Renderer handoff: carbon-html-report consumes-and-strips VIZ/OPS and maps info-box labels to Carbon callouts. Backward-compatible: research depth (Adım 0–4) and connector wiring unchanged; only the output *form* is upgraded. |
| **8.3** | **Jun 2026** | **v8.3.0 — semantic coverage mechanism: Adım 0.4 + knowledge-map + Completeness Gate + G-COVERAGE; optional evidentia-kb booster.** New always-load file `references/knowledge-map.md` (semantic index). New mandatory step Adım 0.4 (Semantic Scope Scan): decomposes question into concept set, resolves sections via knowledge-map Inverted Map, optionally calls `kb_search` booster, emits auditable `coverage_set` into Ops sidecar. Adım 0.5 now loads the UNION of coverage_set (keyword signals only add, never shrink). Full-detail discipline: loaded KB sections never silently summarised away. New Completeness Gate (MANDATORY before finalising): re-scans map for unconsulted axes, loads gaps, re-checks until empty. `G-COVERAGE` gate added to check_integrity.py. Booster (`evidentia-kb` Worker, `kb_search`) optional + graceful-degrade. Additive (ADR-05): all existing Adım 0/0.5/layer content unchanged. |
| **8.2** | **Jun 2026** | **Reference-Integrity & Operability Release (skill-upgrader UPGRADE Faz 5).** Closes the v8.0/8.1 incomplete-migration gap: SKILL.md had cited **22** reference files of which only **6** existed (3 of them always-load). **UP-001:** recreated the 3 missing always-load files (`evidence-grading.md`, `extended-api.md`, `output-templates.md`, primary-source-grounded) + the 8 specialty layers + `osint-playbook.md` + 4 infra files — **all 22 references now resolve.** **UP-002:** promoted the SKILL.md-embedded SMP excerpt to a standalone, parseable **`skill-manifest.yaml`** (runtime.mcp_servers + composition + verification + constraints) — lifts D1/D6/D7/D8 by giving the auditor structured data. **UP-004:** added an **executable** verification harness (`evals/check_integrity.py` — G-REF/G-ALWAYS/G-CONN/G-VERSION + `benchmark-queries.json` 10 regression queries) — verification is now runnable, not merely documented. **UP-005 (α-layer):** wired the operator-connected, high-trust connectors **TİTCK Cache** (Türkiye-Dörtlüsü latency fallback), **YÖK Akademik** (Turkish-KOL identification, §8), PDF Viewer, Social Listening (OSINT backing). **UP-006:** added canonical navigational headings (When-To-Invoke / Limitations) to remove D4 false-positives. **UP-007 (β-layer):** documented — but did **NOT** wire — registry-discovered clinical-DDI + terminology candidates (community/unverified) in `candidate_connectors_unverified`, honoring the v8.0 probe-verified-only principle. Backward-compatible: research depth + native-first wiring unchanged; this release makes the skill **operable and gate-passing**. |
| **8.4** | **Jun 2026** | **v8.4.0 — Structured-Authoritative Refocus (web tier + OSINT removed).** The **Exa/Tavily web-retrieval tier and the entire OSINT axis** (incl. `osint-playbook.md`, social-listening) were **removed** — evidentia is now a pure structured-authoritative evidence engine. Native-First ladder ends at **documented gap** (no web fallback); sources with no native API (EMA CHMP/EPAR, ESMO/NCCN/NICE guideline PDFs, GLOBOCAN/IHME/WHO-GHO burden) are reported as an unreachable gap, **never web-scraped or fabricated**. Full-text cascade Tier 5 (was Exa) → **pubmed-epmc Unpaywall legal-OA**. **Added 3 keyless Tier-K academic connectors** (probe-verified 2026-06-27): **OpenAlex** (KOL/citation-network/institution disambiguation), **PubMed-EPMC** (Europe PMC breadth + Unpaywall legal-OA full text), **Semantic Scholar** (citation graph) — promoted from native_rest_fallback. OSINT/web competitive intelligence now hands off to external `pharmaintel`. Security: 3P-untrusted academic-MCP trust posture documented (connector-registry §6.3P; keyless ⇒ no secret leak). Additive/ADR-05-safe for all clinical specialty content. |
| **8.5** | **Jun 2026** | **v8.5.0 — Extended-Tier Promotion & Epidemiology Wiring.** Extended **Tier-K** (`med-terminologies`, `nih-clinicaltables`, `nlm-rxnorm`, `iuphar-gtopdb`) promoted to **first-class** with **tool-level whitelists + cross-validation gates** (`connector-registry.md §2.6`; broken tools D1/D2/D3/D6 routed to working alternatives; pipeworx generics out-of-whitelist). **drugddx** Tier-O **live** (D-β: promoted from self-host block into `runtime.mcp_servers`). **D-α fixed:** legacy "Regulatory MCP 922d7cdc" → **`openfda`** (openFDA + WHO ICD-11; `who_gho_query`/`health_canada_dpd`/`federal_register_search`/`eurlex_expert_search` not bundled → documented gap). **PopHIVE** wired for **US** epidemiology (axis 0.5.K / §1.P / §21 — `get_current_status`/`get_trend`/`get_map`/`get_coverage`/`compare`; **US-ONLY**, global + Türkiye burden stays a documented gap). **Mevzuat Bilgisi** secondary cross-check (primacy = primary Mevzuat); **Elicit** secondary/conditional (OAuth, claude.ai-connected; tools probe-verified 2026-06-28). All probe-verified by **live re-probe 2026-06-28** (`connector-registry.md §8` Probe Log). New executable gates **G-PROBE / G-XVAL / G-WHITELIST**. Additive/ADR-05-safe: clinical specialty content, research depth (Adım 0–5), clean-copy doctrine, and the native-first ladder are unchanged — only connector wiring + metadata + gates. |

---

## SMP v1.0 Manifest (excerpt — authoritative copy is `skill-manifest.yaml`)

> **v8.3:** the full, machine-readable manifest now lives in **`skill-manifest.yaml`** at the skill
> root (runtime.mcp_servers incl. α-layer + β-candidates, composition.pipe_to + scope_guard,
> verification.gates, constraints). The block below is a human-readable summary; on any conflict,
> the standalone file wins.

```yaml
skill_manifest_protocol: 1.0
skill_name: medical-research
skill_version: 8.5.0
produces:
  - evidence-synthesis-markdown (Format A–I + §21 epidemiology)
  - clean-copy-report (v8.1 — journal-grade reader-facing article; tooling/telemetry/viz
    directives carried only in non-rendering <!-- OPS -->/<!-- VIZ --> annex)
  - data-sidecar-json (evidence/trial/guideline/regulatory/hta tables + specialty_payload
    + pipeline_payload[real AdisInsight] + turkey_access_summary[native TİTCK]
    + epidemiology_payload[ICD-11] + sources_summary)
  - kol-map | patent-landscape | pipeline-snapshot
consumes:
  - clinical-question (required) | pmid/nct/drug-name/moa/target/drug-class/gene-variant
    | indication-code(ICD-11) | sponsor-name | barcode(TİTCK) | regulatory-milestone
connectors_used:
  academic: [PubMed/EuropePMC(8f314cbe), Consensus, ScholarGateway, PaperSearch(660e91bd),
    ClinicalTrials(4cc36ce0), bioRxiv, YÖKTez, OpenAlex(keyless), SemanticScholar(keyless), PubMed-EPMC(keyless)]
  curated_intel: [AdisInsight(6a9fd4a4, real schema), ChEMBL(bio-research), Synapse(auth),
    Wiley(auth), OpenTargets(conditional)]
  regulatory_epi: [openfda(self-host): openFDA+ICD11; PopHIVE(Tier-K-epi): US surveillance axis 0.5.K; WHO-GHO/HealthCanada/FederalRegister/EURLex + global/TR burden = belgeli boşluk]
  turkiye: [TİTCK(1a49b1bb), Mevzuat(fbf16a1a), TÜRKPATENT(ded65854), YÖKTez(b2d46b46)]
  fulltext: [EuropePMC PMC, annas-mcp(verified), PaperDownload(660e91bd), Wiley(auth)]
  verification: [NPI(64557ced)]
  native_tier_k_bundled: [OpenAlex(openalex_*), PubMed-EPMC(pubmed_*; EuropePMC+Unpaywall OA), Semantic Scholar(search_papers/get_paper/citations/author)]   # promoted 2026-06-27 from REST
  extended_tier_k: [med-terminologies(atc_classify/map_icd10_to_icd11), nih-clinicaltables(drugs/icd10cm-code), nlm-rxnorm(rxnorm_search/get_properties), iuphar-gtopdb(search_targets/ligands)]   # v8.5 first-class; TOOL-whitelisted (connector-registry §2.6); broken D1/D2/D3/D6 routed away
  clinical_ddi: [drugddx(normalize_drug/interaction_label, Tier-O live)]   # v8.5 D-β; NOT a pairwise engine — cross-validate
  native_rest_fallback: [PubChem, DailyMed, DOAJ, J-STAGE]
  alpha_layer_v8_2: [TİTCK Cache(cache/fallback), YÖK Akademik(TR KOL), PDF Viewer]
candidate_connectors_unverified:   # β-layer — NOT wired (probe-verified-only principle)
  - drug-interaction-mcp | medical-terminologies-mcp | medical-codes-mcp-server
composes_with:
  - carbon-html-report | carbon-pptx (consume sidecar)
  - onko-erisim | saglik-sigorta | pharmapatent | pharmaintel | rxos | thoughtspot-roche
  - lex-mercator | lex-sanitas | promo-censor (regulatory/legal handoff)
verification:   # executable — evals/check_integrity.py
  gates: [G-REF, G-CONN, G-ALWAYS, G-VERSION, G-REGRESSION, G-COVERAGE, G-RAG, G-COPYRIGHT, G-PROBE, G-XVAL, G-WHITELIST]
constraints:
  native_first: true
  drug_intel_gating: §1.O fires only on 0.5.I
  copyright_limits: enforced (no verbatim bulk; CC-BY via copyright_status)
  clean_copy_doctrine: true   # v8.1 — file reports are journal-grade; report-presentation.md
  no_tooling_leakage: true    # connector names/axis codes/call telemetry banned from visible body
  viz_directive_isolation: true  # "convert to chart" instructions only inside <!-- VIZ --> comments
  probe_verified_only: true   # v8.0 — a referenced tool MUST resolve to a real probe-verified tool
  languages: [Turkish primary, English technical terms preserved]
```

*v8.0 ground-truth principle (unchanged) — every connector reference resolves to a tool verified by
live MCP probe (9 Jun 2026; α-layer added 19 Jun 2026). If a reference cannot be resolved to a real
tool, it is a defect. v8.2 makes this **enforceable**: `evals/check_integrity.py` fails the release
if any cited reference file or registry connector does not resolve.*

*v8.1 — the presentation layer (`report-presentation.md` + Adım 5) is additive and
backward-compatible: it changes only the reader-facing **form** of file-based reports
(clean copy + non-rendering VIZ/OPS annex), not research depth or connector wiring.*
