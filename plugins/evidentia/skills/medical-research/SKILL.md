---
name: medical-research
description: >
  Orchestrates 20+ verified MCP connectors for clinical, pharma and Türkiye-market
  research: academic (PubMed/EuropePMC, Consensus, ClinicalTrials.gov, bioRxiv, YÖK
  Tez, Exa), curated intel (AdisInsight, ChEMBL), regulatory+epidemiology (native
  openFDA, ICD-11, WHO GHO), Türkiye native (TİTCK, Mevzuat, TÜRKPATENT), full-text
  (annas-mcp, EuropePMC PMC), NPI — plus OSINT and 10 specialty axes (Onco, Heme,
  Regulatory, HTA, MedAffairs, Immunology, Neurology, Rare, DrugIntel, Epidemiology).
  Use for ANY medical/onco/heme/immuno/neuro/rare/pharma-pipeline/TR-market/HTA query.
  Triggers: evidence, trial, biomarker, guideline, GRADE, CHMP, HTA, ICER, MSL, CAR-T,
  bispecific, ADC, MRD, BTK, myeloma, JAK, MS, SMA, Alzheimer, orphan, pipeline, ilaç
  peyzajı, PDUFA, deal, ODD, MoA, target, biosimilar, LoE, TİTCK, SGK, SUT, geri ödeme,
  ruhsat, biyobenzer, ATC, FAERS, ICD-11, tam metin. When in doubt, USE THIS SKILL.
metadata:
  version: 8.3.0
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
>   **tek-sefer fetch / kanonik artefakt** disiplini (TİTCK tek-sefer kuralı; RegulatoryMCP
>   tekil+retry+skippable; Tavily kota tek-deneme). Adım 1 paralel çağrı listesi bu sözleşmeye
>   tabidir.
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
> **Sürüm/ad değişmez:** Bu skill kanonik adını (`medical-research`) ve sürümünü (**8.3.0**)
> korur (ADR-05). Plugin sürümü (`1.0.0`) ayrıdır.

# ⚠️ MANDATORY EXECUTION PROTOCOL — v8.3.0 (medical-research)

**This block is read and applied before any other Phase structure. It is executed on
every invocation. Sub-sections do not OVERRIDE this block.**

**v8.0 headline:** The connector model moved from abstract names to a **ground-truth
connector registry** (every tool name/parameter verified by live probe). The flagship
**AdisInsight schema bug is fixed** (real `search_drugs`/`get_drug`/`generate_chart`).
New native stacks: **Türkiye** (TİTCK + Mevzuat + TÜRKPATENT), **Regulatory Intelligence**
(native openFDA + ICD-11 + WHO GHO + Health Canada), **Full-Text Retrieval** (annas-mcp +
EPMC PMC + copyright). New principle: **Native-MCP-First.** New axis: **0.5.K
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
- `references/osint-playbook.md` + `benchmark-*.md` — loaded only on OSINT / dev context.
- Specialty layers (`oncology/hematology/regulatory-science/hta/medaffairs-ops/immunology/neurology/rare-disease`) — loaded per Adım 0.5 signal.

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
| **0.5.K Epidemiology / Burden (v8.0 NEW)** | insidans, prevalans, mortalite, hastalık yükü, DALY, epidemiyoloji, GLOBOCAN, "kaç hasta", "Türkiye'de görülme sıklığı", incidence, prevalence, disease burden | `regulatory-intelligence.md` (WHO GHO + ICD-11) | §1.P |

**No signal:** the Core academic + Extended + Türkiye Dörtlüsü + (OSINT if active) flow
runs unchanged.

## Adım 1: Mandatory Parallel Call List (native-MCP-first)

Issued on every query regardless of wording. This is a **required execution order**, not
a menu. Use the **verified tool names** from `connector-registry.md`. Resolve every need
by the **Native-First ladder** (native MCP → Python REST → Exa/Tavily → documented gap).

### A. Academic Core
1. `PubMed/EPMC:search_articles` (`8f314cbe…`) — topic + specific reformulation
2. `bioRxiv:search_preprints` — topic + last 2y
3. `ClinicalTrials:search_trials` (`4cc36ce0…`)
4. `Consensus:search` (natural-language; reproduce usage message)
5. `ScholarGateway:semanticSearch`
6. `PaperSearch:search` (`660e91bd…`)
7. `YÖK Tez:search_yok_tez_detailed` — TR + EN
8. `Exa:web_search_exa` — topic + "clinical trial 2025 2026" (gap-filler, runs late)
9. **AdisInsight `search_drugs`** — GATED by 0.5.I (drug/MoA/target/pipeline signal). Real schema only (`drug-intelligence-layer.md`).

### B. Extended Tier (native MCP first; `requests` fallback)
- **ChEMBL** (`bio-research:chembl`): `drug_search` / `get_mechanism` / `get_admet` / `target_search` — if topic is a drug/target. (Native connector replaces v7.1 Python ChEMBL.)
- **EPMC SR filter**: `search_articles("(topic) AND systematic review[Publication Type]")` — Tier 0.
- **PubChem / OpenAlex / Semantic Scholar Graph / DailyMed / Unpaywall / DOAJ / J-STAGE**: native REST via `bash_tool` (no native MCP) — see `extended-api.md`.
- **openFDA**: **native** `RegulatoryMCP:openfda_search` (NOT Python requests) — drugsfda + label + FAERS.

### C. Multi-Country AFF (MANDATORY, EPMC native)
```
for country in [Turkey, China, Japan, Germany, Brazil, Korea]:
    EPMC:search_articles(f'({topic}) AND AFF:"{country}"')
```
This loop is not skippable.

### D. Türkiye Dörtlüsü (MANDATORY, NATIVE — v8.0)
1. **TİTCK `search_drugs`** (`1a49b1bb…`) — INN + brand (NOT Exa scraping). On stall/timeout → **TİTCK Cache** (`titck-cache-mcp…`) fallback rung (v8.2).
2. **Mevzuat `search_mevzuat`** (`fbf16a1a…`) — SUT/yönetmelik when clinical/reimbursement
3. **YÖK Tez `search_yok_tez_detailed`** — TR + EN
4. **EPMC `AFF:"Turkey"`** (already in C)
→ See `turkiye-layer.md`. Null → "Türkiye Veri Boşluğu" block.

### E. Guidelines & HTA (when clinical)
- `Exa:web_search_exa` → NICE / ESMO / NCCN / Cochrane / Epistemonikos (society PDFs; native APIs preferred where they exist).
- HTA: prefer native (NICE via Exa; IQWiG/HAS/CADTH via Exa) — no native MCP.

### F–P. Specialty + Drug-Intel + Epidemiology packages
Injected per Adım 0.5 signal. Highlights (full lists in each layer file):
- **§1.F Oncology / §1.G Hematology** — NCCN/ESMO/ASCO/ASH/EHA + OncoKB/CIViC + ASCO/ESMO/ASH abstract mining + **TİTCK off-label (native)** + AdisInsight pipeline + Synapse (if auth).
- **§1.I Drug Intelligence** — AdisInsight `search_drugs`/`get_drug`(HyDE)/`search_drug_companies`/`generate_chart` + CT.gov/DailyMed/openFDA cross-ref (`drug-intelligence-layer.md`).
- **§1.I/J/K (Regulatory/HTA/MA)** — **native openFDA** (drugsfda/label/FAERS) + **ICD-11** + EMA(Exa) + TİTCK(native) + Mevzuat(native) + AdisInsight milestone reconstruction.
- **§1.P Epidemiology (v8.0)** — **WHO GHO `who_gho_query`** (burden/incidence/mortality) + **ICD-11 `icd11_search`** (coding) + GLOBOCAN (Exa) → feeds HTA budget-impact + rare-disease prevalence. ⚠️ regulatory MCP is latency-prone: call singly, retry, skippable.

### Full-Text Retrieval (when abstract insufficient — `fulltext-retrieval.md`)
Cascade: EPMC `get_full_text_article` (PMC OA) → `get_copyright_status` → PaperSearch `read_pubmed_paper` → **annas-mcp `article_download`** (DOI, verified) / `book_search` (methodology) → Wiley (auth) → Exa `web_fetch_exa`. **Copyright:** analysis only; no verbatim bulk reproduction; CC-BY (via copyright_status) freely quotable.

## Adım 2: Generosity Principle (UNCAPPED)

Token cycles enable, not constrain. Depth is never reduced for "budget." Minimum depths
per dimension are retained from v7.x (PubMed ≥2 queries ×25, EPMC ×2, 6-country AFF =6
calls, CT.gov ×2, Türkiye Dörtlüsü native, etc.). Specialty packages **add** depth.

Typical call counts: general ~48–60; single specialty ~60–78; two-layer ~72–95; 3+ layer
heavy (e.g., "Casgevy TR erişim" = heme+reg+HTA+rare+drug-intel+Türkiye+epi) ~100–150;
complex strategic ~150–220. **No upper cap.**

Retry generosity: 3× + exponential backoff. Pagination: up to 3 pages. **Regulatory MCP
exception:** call singly (not parallel) due to latency; one retry; mark skippable if it
stalls. **Tavily exception:** on 432/error fall through to Exa.

Mandatory transparency note. **Placement (v8.1):** in **file-based clean-copy reports** this
note is emitted inside the **non-rendering operational annex** (`<!-- OPS: … -->`), NOT in the
reader-facing body (see Adım 5 + `report-presentation.md`). In short interactive (non-file)
answers it may remain visible. Content:
```
---
Cömertlik Garantisi: Bu yanıtın üretiminde [N] API çağrısı yapıldı. Aktif katmanlar: [...].
Native-first çözümleme uygulandı. Hiçbir boyut budget gerekçesiyle atlanmadı.
[Eğer varsa: (Tavily kotası nedeniyle Exa-fallback kullanıldı. / Regulatory MCP gecikmesi
nedeniyle [kaynak] tekil çağrı + retry ile alındı.)]
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
## 21. Epidemiyoloji / Hastalık Yükü (0.5.K — WHO GHO + ICD-11 + GLOBOCAN)  [v8.0]
```
**v8.1 — Internal scaffold vs. clean copy.** The §1–21 contract above governs research
**completeness** (every dimension covered). It is an *internal* scaffold: its tool-annotated
headings (e.g., "(PubMed + EuropePMC)", "(native openFDA…)", "(0.5.I — real AdisInsight)") are
**not** the reader-facing form. For file-based reports, Phase 5 maps this coverage into a
journal-style **clean copy** per `report-presentation.md` (scaffold→heading map there). Tooling
annotations, call telemetry and viz directives never appear in the reader-facing body.

Optional `.data.json` sidecar (v8.0 schema, `output-templates.md`): evidence/trial/
guideline/regulatory/HTA tables + specialty_payload + **pipeline_payload (real AdisInsight
fields)** + **turkey_access_summary (native TİTCK)** + **epidemiology_payload (WHO GHO)** +
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

# medical-research: Multi-Source Scientific Research & Synthesis Engine (v8.3)

You orchestrate 20+ **verified** connectors plus OSINT + 10 specialty axes as a unified
scientific research and intelligence system. Transform a question into a comprehensive,
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
net-new commercial strategy → `pharmaintel`; FTO/IP litigation depth → `pharmapatent`; deep TR
regulatory reform → `lex-sanitas`. OSINT (Tier 6) and FAERS counts are context/reporting, never
clinical evidence or incidence. β-candidate connectors are not wired until probe-verified.

## Core Philosophy
Connectors form a **symbiotic ecosystem**, triangulated, not queried in isolation. v8.0
grounds that ecosystem in real tool schemas (Native-First) so triangulation is built on
calls that actually succeed. A PubMed SR gains context from a bioRxiv preprint; a CT.gov
Phase 3 entry is enriched by an AdisInsight regulatory history; **TİTCK native** gives the
Turkish price/reimbursement/biosimilar reality that determines local practice; **annas-mcp**
+ EPMC PMC open the full text behind a critical abstract; **WHO GHO + ICD-11** give the
epidemiologic denominator behind an HTA budget-impact model.

## Phase 1 — Query Intelligence
1.1 Decompose (PICO + specialty + epidemiology dimension).
1.1b Query-type classifier (priority, not gating — all branches default-active).
1.2 Generate ≥2 query variants per connector (Specific / Broad / Lateral).
1.3 Appraisal depth (formal GRADE vs pragmatic — `evidence-grading.md`).
1.4 Exa/Tavily enrichment planning (Tavily quota-aware).
1.5 OSINT dimension assessment (`osint-playbook.md`).
1.6 Specialty + epidemiology layer assessment (Adım 0.5 documents this).

## Phase 2 — Connector Orchestration
**FIRST read `connector-registry.md`.** Search ALL relevant connectors for EVERY query.
Three-tier architecture: Core academic + OSINT; Extended (native MCP first, REST fallback);
Specialty (per Adım 0.5). Execution order: academic connectors → specialty layer → **AdisInsight
(0.5.I)** → Synapse/OpenTargets (0.5.J, if auth/online) → native Türkiye + Regulatory stacks →
Exa/Tavily gap-fill last. Capture source ID (PMID/DOI/NCT/YÖK/barcode/URL), title, authors,
date, findings, study type, population, n.

## Phase 3 — Evidence Synthesis & Critical Appraisal
Read `evidence-grading.md`. Deduplicate/cross-reference; apply Tier 0–6 hierarchy (Tier 6
OSINT never supports clinical claims); GRADE or pragmatic; convergent/divergent/complementary;
temporal narrative; guideline concordance; **full-text-enriched numerical endpoints** (HR, CI,
p, subgroups, AE) via the full-text cascade with copyright gate; entity/relation/temporal
extraction; specialty-specific appraisal checklists (per active layer).

## Phase 4 — Knowledge Gap Analysis
Evidence / methodological / guideline-regulatory / future-research / OSINT / specialty gaps,
plus **epidemiologic gaps** (registry coverage, Turkish incidence/prevalence data availability).

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
- **OSINT integrity** — OSINT ≠ evidence; source-tagged; >6mo flagged; FAERS = reporting, not
  incidence.
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
| `extended-api.md` | ALWAYS | Native-MCP-first; Python REST fallback (OpenAlex/PubChem/S2/Unpaywall/DOAJ/J-STAGE/DrugBank) |
| `evidence-grading.md` | ALWAYS (Phase 3) | Tier 0–6, GRADE, pragmatic, NER, full-text+copyright integration |
| `output-templates.md` | ALWAYS (Phase 5) | Format A–I, sidecar v8.0, epidemiology block |
| `fulltext-retrieval.md` | ALWAYS | EPMC PMC → copyright → annas → paper-download → Wiley cascade |
| `report-presentation.md` | ALWAYS (Phase 5 / Adım 5) | **v8.1** — clean-copy doctrine: scholarly Turkish, no tooling leakage, journal-style Methods, info boxes, `<!-- VIZ -->`/`<!-- OPS -->` isolation, scaffold→clean-copy map, finalization gate G1–G7 |
| `turkiye-layer.md` | Turkey context / default | TİTCK + Mevzuat + YÖK + TÜRKPATENT native |
| `regulatory-intelligence.md` | 0.5.C/0.5.D/0.5.K | native openFDA + ICD-11 + WHO GHO + Health Canada + Federal Register |
| `drug-intelligence-layer.md` | 0.5.I only | REAL AdisInsight schema (search_drugs/get_drug HyDE/generate_chart) |
| `oncology/hematology/regulatory-science/hta/medaffairs-ops/immunology/neurology/rare-disease-layer.md` | per 0.5.A–H | Clinical deep-dive + appraisal checklist + v8.0 native wiring (**recreated v8.2**) |
| `osint-playbook.md` | OSINT triggers | Competitive/patent/regulatory/PV/market-access/KOL playbooks (social/web signal via Tavily→Exa) |
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

---

## SMP v1.0 Manifest (excerpt — authoritative copy is `skill-manifest.yaml`)

> **v8.3:** the full, machine-readable manifest now lives in **`skill-manifest.yaml`** at the skill
> root (runtime.mcp_servers incl. α-layer + β-candidates, composition.pipe_to + scope_guard,
> verification.gates, constraints). The block below is a human-readable summary; on any conflict,
> the standalone file wins.

```yaml
skill_manifest_protocol: 1.0
skill_name: medical-research
skill_version: 8.3.0
produces:
  - evidence-synthesis-markdown (Format A–I + §21 epidemiology)
  - clean-copy-report (v8.1 — journal-grade reader-facing article; tooling/telemetry/viz
    directives carried only in non-rendering <!-- OPS -->/<!-- VIZ --> annex)
  - data-sidecar-json (evidence/trial/guideline/regulatory/hta tables + specialty_payload
    + pipeline_payload[real AdisInsight] + turkey_access_summary[native TİTCK]
    + epidemiology_payload[WHO GHO] + sources_summary)
  - kol-map | patent-landscape | competitive-intel | pipeline-snapshot
consumes:
  - clinical-question (required) | pmid/nct/drug-name/moa/target/drug-class/gene-variant
    | indication-code(ICD-11) | sponsor-name | barcode(TİTCK) | regulatory-milestone
connectors_used:
  academic: [PubMed/EuropePMC(8f314cbe), Consensus, ScholarGateway, PaperSearch(660e91bd),
    ClinicalTrials(4cc36ce0), bioRxiv, YÖKTez, Exa, Tavily]
  curated_intel: [AdisInsight(6a9fd4a4, real schema), ChEMBL(bio-research), Synapse(auth),
    Wiley(auth), OpenTargets(conditional)]
  regulatory_epi: [RegulatoryMCP(922d7cdc): openFDA+ICD11+WHO-GHO+HealthCanada+FederalRegister+EURLex]
  turkiye: [TİTCK(1a49b1bb), Mevzuat(fbf16a1a), TÜRKPATENT(ded65854), YÖKTez(b2d46b46)]
  fulltext: [EuropePMC PMC, annas-mcp(verified), PaperDownload(660e91bd), Wiley(auth)]
  verification: [NPI(64557ced)]
  native_tier_k_bundled: [OpenAlex(openalex_*), PubMed-EPMC(pubmed_*; EuropePMC+Unpaywall OA), Semantic Scholar(search_papers/get_paper/citations/author)]   # promoted 2026-06-27 from REST
  native_rest_fallback: [PubChem, DailyMed, DOAJ, J-STAGE]
  alpha_layer_v8_2: [TİTCK Cache(cache/fallback), YÖK Akademik(TR KOL), PDF Viewer]
candidate_connectors_unverified:   # β-layer — NOT wired (probe-verified-only principle)
  - drug-interaction-mcp | medical-terminologies-mcp | medical-codes-mcp-server
composes_with:
  - carbon-html-report | carbon-pptx (consume sidecar)
  - onko-erisim | saglik-sigorta | pharmapatent | pharmaintel | rxos | thoughtspot-roche
  - lex-mercator | lex-sanitas | promo-censor (regulatory/legal handoff)
verification:   # executable — evals/check_integrity.py
  gates: [G-REF, G-ALWAYS, G-CONN, G-VERSION, G-REGRESSION, G-COPYRIGHT]
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
