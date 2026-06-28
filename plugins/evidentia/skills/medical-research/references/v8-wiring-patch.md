# v8.0 Wiring Patch — Existing Reference Files

**Purpose:** The 8 specialty layers + `extended-api.md` / `evidence-grading.md` /
`output-templates.md` / `execution-map.md` / `composition-runbook.md` /
`benchmark-*.md` contain **sound clinical/operational content that is retained.** Only their
**connector wiring** changes for v8.0. This patch specifies the exact transformations so the
full rewrite is complete and applicable, without re-pasting ~8,000 lines verbatim.

Apply as find→replace + targeted insertions. Each file keeps its structure, headings, and
clinical body; only the calls change.

---

## A. Global find→replace (ALL reference files)

| Find (v7.1 pattern) | Replace (v8.0) |
|---|---|
| `OpenFDA … via bash_tool` / `api.fda.gov` Python block | `openfda:openfda_search(endpoint=..., search=..., count=...)` (native); Python only as fallback |
| `ChEMBL … requests` (`extended-api §6`) | `ChEMBL(bio-research):drug_search/get_mechanism/get_admet/target_search` (native); requests fallback |
| `Europe PMC … requests` for search | `EPMC(8f314cbe):search_articles` (native); `get_full_text_article`+`get_copyright_status` for full text |
| TR drug-status web scraping | `TİTCK:search_drugs/get_atc_class_summary/...` (native — `turkiye-layer.md`) |
| SGK / Resmî Gazete web scraping | `Mevzuat:search_mevzuat/get_mevzuat_text` (native) |
| AdisInsight `organisations`/`phases`/`indications`/`moas`/`drugClass`/`locations`/`fromDate`/`toDate` | **DELETE** — real schema `search_drugs(drug_name/developers/dev_phase/mechanism/targets/...)` + `get_drug`(HyDE) (`drug-intelligence-layer.md`) |
| "AdisInsight MCP (`adisinsight-mcp.springer.com/mcp`)" | "AdisInsight MCP (server `6a9fd4a4…`, real schema)" |
| `connector-api.md` references | `connector-registry.md` |

---

## B. `extended-api.md` (rewrite to native-first)
- **§ openFDA** → remove Python block; point to `regulatory-intelligence.md` (native `openfda_search`).
- **§6 ChEMBL** → native `bio-research:chembl` primary; `requests` (ChEMBL REST) fallback only.
- **§1 Europe PMC** → native `EPMC:search_articles` primary; `requests` (EBI REST) fallback.
- **§13.2 Unpaywall / §13.3 DOAJ / §1.x OpenAlex / §5 PubChem / §7 Semantic Scholar Graph / §13.1 J-STAGE / §12.3 DrugBank** → **retain Python `requests`** (no native MCP) — these are the legitimate Tier-2 of the native-first ladder.
- Add a header note: "Native-First ladder — see `connector-registry.md §0`. This file = Tier 2 (native REST) only; Tier 1 (native MCP) lives in connector-registry + turkiye + regulatory-intelligence + drug-intelligence."
- Retain rate-limit/backoff (§11), multi-country AFF (§13.4), honesty record (§14.3).

## C. `evidence-grading.md` (update)
- Tier 5/6: add `EPMC:get_copyright_status` for OA determination; add annas methodology grounding (GRADE/Cochrane Handbook) per `fulltext-retrieval.md`.
- §5 Pattern A (FAERS PRR): source data from native `openfda_search(count=...)`, not Python.
- Add one line: "Full-text-derived numbers (HR/CI/n) are facts (citable); see `fulltext-retrieval.md` copyright gate before quoting prose."
- Tier 6 curated-intel note: AdisInsight `history_events` (real) is curated intel (Tier 6 context), never clinical-claim support.

## D. `output-templates.md` (update)
- Sidecar bump `medical_research_sidecar_version: "8.0"`.
- `connectors_used` → replace with verified list: `["PubMed/EuropePMC(8f314cbe)","Consensus","ScholarGateway","PaperSearch(660e91bd)","ClinicalTrials(4cc36ce0)","bioRxiv","YÖKTez","AdisInsight(6a9fd4a4)","ChEMBL(bio-research)","openfda(self-host)","TİTCK(1a49b1bb)","Mevzuat(fbf16a1a)","TÜRKPATENT(ded65854)","NPI(64557ced)","annas-mcp","Synapse(auth)","Wiley(auth)"]`.
- `pipeline_payload` → replace with v8.0 real-field schema (`drug-intelligence-layer.md §6`): `doc_id`, `adis_profile_url`, `regulatory_history[]` from `history_events`, `highest_phases_by_indication[]`.
- `turkey_access_summary` → replace with native-TİTCK fields (`turkiye-layer.md §5`): `titck_products[]`, `price_try{}`, `biosimilar_landscape[]`, `off_label_oncology[]`, `reference_status`, `essential_drug_list`.
- **Add** `epidemiology_payload` block (`regulatory-intelligence.md §6`).
- **Add Format J — Epidemiology/Burden block (§21)** appended to any format when 0.5.K active:
  ```markdown
  ## 21. Epidemiyoloji / Hastalık Yükü
  | Gösterge | Kaynak | Coğrafya | Yıl | Değer (CI) | Birim |
  |---|---|---|---|---|---|
  | İnsidans | GLOBOCAN/WHO GHO/TÜİK | TR/Global | — | — | per 100k / mutlak |
  - ICD-11 kod(lar)ı: [icd11_search]
  - Not: FAERS=raporlama (insidans değil); GHO gecikirse GLOBOCAN/SEER ikamesi.
  ```

## E. Specialty layers (8 files) — wiring inserts

Each retains its full clinical body. Apply Global find→replace (§A) + the per-file insert:

| File | v8.0 insert |
|---|---|
| `oncology-layer.md` | TİTCK `find_off_label_uses_for_drug` (native onko off-label) replaces SGK onko web scraping; AdisInsight real `search_drugs(mechanism=..., targets=..., therapeutic_area="Cancer")` for ADC/bispecific/CAR-T landscape; GLOBOCAN via `regulatory-intelligence` 0.5.K; OncoKB/CIViC have no native connector in this build → not retrievable, report as a gap (VERİ YOK), do NOT fabricate |
| `hematology-layer.md` | AdisInsight real schema for CAR-T/bsAb/ADC landscape; TİTCK native for TR heme reimbursement; ASH/EHA abstracts have no native connector → not retrievable, report as a gap (VERİ YOK), do NOT fabricate; full-text via `fulltext-retrieval.md` |
| `regulatory-science-layer.md` | native `openfda_search(drug/drugsfda, drug/label, drug/enforcement)` + ICD-11 + AdisInsight `history_events` (CRL/ODAC/registration) + TİTCK native; EMA has no native API in this build → not retrievable, report as a gap (VERİ YOK), do NOT fabricate; withdrawal pool = enforcement + AdisInsight discontinued |
| `hta-layer.md` | WHO GHO burden (0.5.K) for budget-impact; TİTCK price + Mevzuat SUT (native) for §14.f; NICE/CADTH/IQWiG/HAS have no native connector in this build → not retrievable, report as a gap (VERİ YOK), do NOT fabricate; AdisInsight competitor set (real schema) for comparator |
| `medaffairs-ops-layer.md` | NPI `npi_search` for ABD KOL/PI verification; AdisInsight `conference_coverage` (real) + OpenAlex KOL graph; EFPIA/IFPMA/İEİS have no native connector → not retrievable, report as a gap (VERİ YOK), do NOT fabricate |
| `immunology-layer.md` | AdisInsight real schema for JAK/TYK2/IL-17/23 landscape (`mechanism=...`); TİTCK native for TR biologic reimbursement; ACR/EULAR have no native connector → not retrievable, report as a gap (VERİ YOK), do NOT fabricate |
| `neurology-layer.md` | AdisInsight real schema (anti-amyloid/gene therapy/CGRP); TİTCK native for TR MS/SMA reimbursement; Synapse AD Knowledge Portal (auth, conditional); AAN/ECTRIMS have no native connector → not retrievable, report as a gap (VERİ YOK), do NOT fabricate |
| `rare-disease-layer.md` | Orphanet/OMIM have no native connector in this build → not retrievable, report as a gap (VERİ YOK), do NOT fabricate; WHO GHO + ICD-11 (0.5.K) for prevalence; AdisInsight orphan flags (`is_orphan_drug`, real) ; TİTCK Madde-23/import (native); Synapse natural-history (auth, conditional) |

## F. Infrastructure files
- `execution-map.md` — add native-first batching: native MCP calls parallel-safe **except** regulatory MCP (single + retry). Update wallclock with latency caveat.
- `composition-runbook.md` — update connector names; add TİTCK/Mevzuat/TÜRKPATENT to `onko-erisim`/`saglik-sigorta`/`pharmapatent`/`rxos` pipelines; AdisInsight real schema in pharmaintel handoff.
- `benchmark-suite.md` / `benchmark-protocol.md` — add v8.0 regression gate: (1) every connector reference resolves to a real tool in `connector-registry.md`; (2) 10 probes incl. "trastuzumab TR fiyat+biyobenzer (TİTCK native)", "glofitamab pipeline+ODAC (AdisInsight real)", "DLBCL ESMO + Cochrane full-text (cascade)", "Türkiye yaşam beklentisi (WHO GHO)".

---

## G. Files NOT needing change
`output-templates.md` Format A–I structure (only sidecar + §21 added); the clinical
appraisal checklists in SKILL.md Phase 3.7 (logic unchanged; data sources native).

---

*Applying §A–F yields a complete v8.0 with zero loss of clinical content. This patch is the
P2/P3 work item; P0 (plan, SKILL.md, connector-registry, drug-intelligence-layer,
turkiye-layer) and P1 (regulatory-intelligence, fulltext-retrieval) are delivered as full files.*
