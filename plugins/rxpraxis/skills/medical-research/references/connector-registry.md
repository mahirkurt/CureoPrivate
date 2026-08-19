# Connector Registry & Operational Guide (v8.0)

**Replaces:** `connector-api.md` (v7.1).
**Loaded:** ALWAYS, before any `tool_search` / connector call (Adım 0).
**Status:** Every tool name and parameter below was **verified by live MCP probe on 9 June 2026.** Where a connector was probed and behaved differently from prior documentation, the verified behavior is authoritative.

---

## 0. Native-First Resolution Principle (v8.0 CORE RULE)

For every data need, resolve in this order. Do **not** skip to a lower tier when a higher tier is available.

1. **Native MCP tool** — a connected MCP exposing a structured tool (TİTCK, AdisInsight, openFDA via regulatory MCP, EPMC, ChEMBL, CT.gov, etc.). Fastest, typed, server-managed rate limits.
2. **Native REST via `bash_tool` + Python `requests`** — only when no native MCP tool exists (e.g., OpenAlex, PubChem, Unpaywall, DOAJ, J-STAGE, DrugBank). See `extended-api.md`.
3. **Web retrieval** — Exa (`web_search_exa` / `web_fetch_exa`) or Tavily (`tavily_*`) for guideline PDFs, society pages, regulatory documents with no API.
4. **Documented gap** — explicit "VERİ BULUNAMADI" with the queries attempted.

> v7.1 inverted this for several connectors (Python `requests` for EuropePMC/ChEMBL/openFDA even though native MCP exists). v8.0 corrects it: **native MCP wins.**

---

## 1. Tool Loading via ToolSearch

MCP tools are **deferred** — their schemas load only after `ToolSearch`. Load in bulk, by exact name, before first use:

```
ToolSearch  select:<exact_tool_name_1>,<exact_tool_name_2>,...
```

Keyword search also works for discovery (`ToolSearch "adisinsight drug pipeline"`). Server IDs below are stable within a session. Multiple servers may expose the same logical connector (e.g., two PubMed servers); the registry marks the **primary**.

---

## 2. Verified Connector Table

### 2.1 Academic literature core

| Connector | Server | Verified primary tools | Notes |
|---|---|---|---|
| **PubMed / Europe PMC** | `8f314cbe…` (primary) · `bio-research:pubmed` (mirror) | `search_articles` (PubMed syntax + `date_from/date_to` + `sort`), `get_full_text_article` (PMC IDs), `get_copyright_status` (license/OA), `convert_article_ids`, `find_related_articles`, `lookup_article_by_citation`, `get_article_metadata` | Native full-text + copyright = backbone of evidence + full-text cascade |
| **Consensus** | `b2afd737…` · `bio-research:consensus` | `search` | MUST cite inline `[n]` + reproduce the tool's sign-up/usage message verbatim; max 3 calls/batch; no filters unless user asks |
| **Scholar Gateway** | `0db119cc…` | `semanticSearch` (`query`, `start_year`/`end_year`, `topN`≤20, `includeRetractedContent`) | Natural-language semantic reformulation |
| **Paper Search / Download** | `660e91bd…` | `search`, `search_pubmed`, `search_semantic`, `search_biorxiv`, `search_google_scholar`, `read_pubmed_paper`, `download_pubmed/biorxiv/semantic` | Aggregator + **full-text read** (full-text cascade tier 2) |
| **Clinical Trials v2** | `4cc36ce0…` (primary) · `bio-research:c-trials` | `search_trials`, `get_trial_details`, `search_by_sponsor`, `search_investigators`, `analyze_endpoints`, `search_by_eligibility` | NIH/NLM CT.gov v2; sponsor pipeline + endpoint comparison |
| **bioRxiv / medRxiv** | Hub stdio `CureoHub/mcp-servers/biorxiv-mcp` (eski Anthropic HCLS `4e673875…` emekli — `/details` boş gövde) | `search_preprints` (+ ops. `query`), `get_preprint`, `search_published_preprints`, `search_by_funder` | ⚠️ Preprint = non-peer-reviewed flag mandatory |
| **YÖK Tez** | `b2d46b46…` | `search_yok_tez_detailed`, `get_yok_tez_document_markdown`, `get_yok_tez_thesis_details`, `search_yok_tez_by_anabilim_dali` | Türkçe + İngilizce terim; tez tam metni sayfa-sayfa Markdown |
| **Exa** | `b2b8051d…` | `web_search_exa` (`query`, `numResults`≤20), `web_fetch_exa` (`urls[]`, `maxCharacters`) | NO `includeDomains`/`freshness` — embed in query text. Gap-filler, runs LAST |
| **Tavily** | `30203133…` | `tavily_search` (REAL `include_domains`/`exclude_domains`, `time_range`, `search_depth`, `country`), `tavily_research` (autonomous), `tavily_extract`, `tavily_crawl`, `tavily_map` | ⚠️ **Quota-limited (HTTP 432 observed) — always Exa-fallback.** When live, superior to Exa for domain-scoped + deep research |

### 2.2 Curated intelligence + mechanism

| Connector | Server | Verified primary tools | Notes |
|---|---|---|---|
| **AdisInsight** | `6a9fd4a4…` | `search_drugs`, `get_drug` (HyDE), `search_trials`, `search_drug_companies`, `search_trial_companies`, `generate_chart` | **Real schema — see `drug-intelligence-layer.md`.** Drug intelligence axis 0.5.I |
| **ChEMBL** | `bio-research:chembl` | `drug_search`, `compound_search`, `get_mechanism`, `get_admet` (QED/Lipinski/Veber/hERG), `get_bioactivity`, `target_search` (gene→UniProt) | Native — replaces Python ChEMBL in extended-api |
| **Synapse** | `bio-research:synapse` | `authenticate` → multi-omics portals | OAuth-gated; conditional (0.5.J). Graceful skip if unauth |
| **OpenTargets** | `bio-research:ot` | (not surfaced as of probe) | ⚠️ Offline at last check — load conditionally; fallback ChEMBL `target_search` + EPMC |
| **Wiley** | `bio-research:wiley` | `authenticate` → publisher full-text | OAuth-gated; full-text cascade tier 4 |

### 2.3 Regulatory + epidemiology + Türkiye + IP

| Connector | Server | Verified primary tools | Notes |
|---|---|---|---|
| **Regulatory MCP** | `922d7cdc…` | `openfda_search` (endpoint enum: `drug/event`, `drug/label`, `drug/drugsfda`, `drug/enforcement`, device/*; `search` Lucene + `count` aggregation), `icd11_search`, `who_gho_query`, `health_canada_dpd`, `federal_register_search`, `eurlex_expert_search` | ⚠️ **Latency-prone (180 s timeout observed)** — call singly, retry, treat as skippable if non-critical |
| **TİTCK** | `1a49b1bb…` | `search_drugs`, `get_drug`, `get_atc_class_summary`, `find_off_label_uses_for_drug`, `find_biosimilar_group`, `find_reference_prices_for_drug`, `compare_drug_to_alternatives`, `find_equivalent_products_by_substance`, `search_regulation_article23`, `find_authorization_cancellations_for_drug`, `get_price_history`, `get_withdrawal_trend`, `get_atc_hierarchy`, `search_off_label_uses` | **See `turkiye-layer.md`.** Türkiye Dörtlüsü now structural |
| **Türk Mevzuat** | `fbf16a1a…` | `search_mevzuat` (needs `tur` code for `baslik` search), `get_mevzuat_text`, `get_mevzuat_content`, `get_anayasa`, `get_mevzuat_madde_tree`, `get_mevzuat_madde_diff` | SUT, yönetmelik, fiyat kararnamesi — native legislation |
| **TÜRKPATENT** | `ded65854…` | `search_patents` (title/applicant/IPC/CPC), `search_trademarks`, `search_designs`, `get_patent_details` | Turkey IP — pharmapatent composition |
| **NPI Registry** | `64557ced…` | `npi_search`, `npi_lookup`, `npi_validate` | US PI/KOL verification (NPI-1 individual, NPI-2 org). US-only |
| **annas-mcp** | `annas-mcp` | `article_search` (DOI/keywords), `book_search`, `article_download` (by DOI — **verified working**), `book_download` (MD5 hash + format) | Full-text cascade tier 3. ⚠️ Copyright: analysis only, no verbatim bulk reproduction |

### 2.4 Output / compose / visualize
- **AdisInsight `generate_chart`** — Chart.js inline (phase distribution, competitor landscape).
- **carbon-html-report / carbon-pptx** — consume `.data.json` sidecar.
- **mevzuat + TÜRKPATENT** — feed `onko-erisim` / `saglik-sigorta` / `pharmapatent` / `rxos` skill compositions.

---

## 3. Per-Connector Usage Notes (from live probes)

### 3.1 AdisInsight — the corrected schema (CRITICAL)
`search_drugs(drug_name="…")` returns a **complete curated profile in one call**: `development_phases` (per-country, per-indication, with `event_date`), `history_events` (regulatory milestones: ODAC, CRL, registration, trial readouts), `brand_names`, `drug_classes`, `target`, `mechanism_of_action`, `organizations` (Owner/Originator/Licensee roles), `is_orphan_drug`/`is_btt`/`is_prime` flags, `adis_insight_profile_url`. Use `get_drug` with `query_text` (HyDE, 8–10× key terms) + `resources` for document chunks. **Never** use `organisations`/`phases`/`moas`/`drugClass` parameters — they do not exist on this MCP. Full cookbook: `drug-intelligence-layer.md`.

### 3.2 TİTCK — structural Turkey data
`search_drugs(query="trastuzumab")` returns barcode, ATC, marketing-authorization holder, `reimbursement_status` (GERİ ÖDEMELİ / GERİ ÖDEMESİZ), `reference_status`, lifecycle, manufacture origin, and a typed `price` block (firm/depot/pharmacy/retail TRY + source-country EUR + valid-from date). Chain: `search_drugs` → `get_drug(record_id=barcode)` → `find_biosimilar_group` / `find_reference_prices_for_drug` / `compare_drug_to_alternatives` / `find_off_label_uses_for_drug`. ⚠️ ATC may differ between master (`L01FD01`, current) and `detailed_price_list` sub-field (`L01XC03`, legacy) — **master record is authoritative.** ⚠️ `find_drug_drug_interactions` is a deprecated alias for substance-overlap (NOT clinical DDI) — prefer `find_shared_substance_peers` and never present as interaction data.

### 3.3 Regulatory MCP — native openFDA + epidemiology
`openfda_search(endpoint="drug/event", search='patient.drug.medicinalproduct:"X"', count="patient.reaction.reactionmeddrapt.exact")` for FAERS PT-level signal counts (NOT incidence — spontaneous reporting). `endpoint="drug/drugsfda"` for approval data, `drug/label` for labeling, `drug/enforcement` for recalls. `icd11_search` for indication coding; `who_gho_query(indicator=..., filter="SpatialDim eq 'TUR'")` for disease burden. ⚠️ Server is slow — issue these singly, allow retry, and mark as skippable if a query stalls.

### 3.4 Tavily — quota-aware web research
When live, `tavily_search` supports **real** `include_domains`/`exclude_domains` (Exa cannot), `time_range`, `search_depth: advanced`, `country` boosting; `tavily_research` is an autonomous multi-source agent; `tavily_extract` pulls clean markdown from URLs. **Currently quota-limited (432).** Pattern: attempt Tavily for domain-scoped/deep tasks → on 432/error, **fall through to Exa** and note the fallback in output.

### 3.5 annas-mcp — full-text retrieval (verified)
`article_search(DOI)` resolves metadata + SciDB handle; `article_download(doi=…)` downloads the PDF (verified: GRADE 2008 → `…/Downloads`). `book_search` finds methodology references (Cochrane Handbook 2nd ed., GRADE guidance). Downloads land on the **user's machine**, not the sandbox. **Copyright discipline:** retrieve for analysis/extraction only; never reproduce large verbatim blocks; prefer CC-BY items (check EPMC `get_copyright_status`).

### 3.6 EPMC copyright gate
`get_copyright_status(pmids=[…])` distinguishes open-access (CC-BY → free quotation) from restricted. Run before quoting; complements Unpaywall/DOAJ for OA determination.

---

## 4. Exa Orchestration (retained — gap-filler, runs last)

Exa accepts only `query` (string) + `numResults` (≤20). No domain/freshness params — embed in query text:
- Guidelines: `"ESMO or NCCN clinical practice guideline for {condition} on esmo.org or nccn.org"`
- Regulatory: `"{drug} FDA prescribing information on accessdata.fda.gov"` (when no native API)
- Turkish: `"{konu} TİTCK SGK Resmî Gazete tedavi protokolü"` (only as fallback; prefer TİTCK + Mevzuat native)
- Freshness: include `"2025 2026 latest"`.

`web_fetch_exa(urls[], maxCharacters)`: max 5 URLs/call; prefer DOI/journal URLs; on paywall, note + fall back to full-text cascade (`fulltext-retrieval.md`).

**Exa role in v8.0 shrinks:** native TİTCK/Mevzuat/openFDA/EPMC now cover what Exa scraping approximated. Exa remains for society guideline PDFs, conference pages, EMA (no native API), and adaptive gap-filling.

---

## 5. Zero-Result Recovery Protocol (MANDATORY)

If any connector returns zero:
1. Reformulate (synonyms, mechanism-level, broader category).
2. Decompose by PICO component.
3. **Switch tier per native-first ladder** (native MCP empty → Python REST → Exa/Tavily).
4. bioRxiv/Paper Search: mechanism terms instead of drug names; source-specific tools individually.
5. YÖK: try Türkçe AND İngilizce; broader anabilim dalı.
6. AdisInsight empty: `search_drug_companies` → Exa `site:adisinsight.springer.com` → CT.gov+DailyMed synthesis.
7. TİTCK empty: try active-ingredient (INN) instead of brand; ATC prefix via `get_atc_class_summary`.
8. Tavily 432: fall through to Exa.
9. Regulatory MCP timeout: retry once; if still stalling, mark skippable and proceed.

Only after exhausting these, report "VERİ BULUNAMADI" and **list the queries attempted**.

---

## 6. Known Limitations & Workarounds (v8.0)

| Limitation | Impact | Workaround |
|---|---|---|
| Regulatory MCP latency (180 s timeout seen) | Slow openFDA/WHO-GHO | Single (non-parallel) calls; retry+backoff; skippable flag |
| Tavily quota (432) | Tavily not live | Always Exa-fallback |
| OAuth connectors (Wiley/Synapse/Owkin/BioRender) | Need `authenticate` | Conditional; graceful skip + note |
| OpenTargets offline | No target-disease assoc | ChEMBL `target_search` + EPMC fallback |
| Exa no `includeDomains`/`freshness` | Approximate targeting | Embed in query text |
| TİTCK ATC duality | L01FD01 vs L01XC03 | Master record authoritative |
| TİTCK `find_drug_drug_interactions` misnomer | Not clinical DDI | Use `find_shared_substance_peers`; never present as interactions |
| Dual connectors (EPMC, CT.gov) | Which to use | Primary = `8f314cbe`/`4cc36ce0`; mirror = bio-research as fallback |
| annas/Wiley copyright | Verbatim risk | Analysis only; `get_copyright_status` gate |
| Consensus usage message | Must reproduce verbatim | Always append the tool's sign-up/usage line |

---

## 7. Domain Registry (query-construction guidance for Exa/Tavily)

Guidelines/societies: `esmo.org, nccn.org, asco.org, hematology.org, ehaweb.org, nice.org.uk, who.int, cochrane.org, epistemonikos.org, acr.org, eular.org, aan.com, ectrims.eu, ecco-ibd.eu, ginasthma.org, orpha.net`.
Regulatory (prefer native first): `fda.gov, accessdata.fda.gov, ema.europa.eu, titck.gov.tr, sgk.gov.tr, resmigazete.gov.tr, pmda.go.jp`.
Journals: `nejm.org, thelancet.com, jamanetwork.com, bmj.com, nature.com, bloodjournal.org, ascopubs.org, haematologica.org, annals.org`.
HTA: `nice.org.uk, iqwig.de, has-sante.fr, cadth.ca, cda-amc.ca, pbac.pbs.gov.au, icer.org, tlv.se`.
Türkiye: `titck.gov.tr, sgk.gov.tr, resmigazete.gov.tr, mevzuat.gov.tr, thd.org.tr, kanser.gov.tr, dergipark.org.tr, trdizin.gov.tr`.

---

*v8.0 — All tool names/parameters verified by live probe 9 June 2026. When a documented capability conflicts with observed behavior, observed behavior is authoritative.*
