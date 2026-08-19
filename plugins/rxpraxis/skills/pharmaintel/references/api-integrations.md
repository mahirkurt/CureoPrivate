# api-integrations.md

**Real-time API Integration Reference (v4.0.0)**

> **Architectural role:** Cross-cutting capability reference. Upgrades pharmaintel from web_search-only source acquisition to **MCP-first + API-first + web-fetch-fallback** discipline, replacing unreliable free-tier search with structured primary data calls where available. **v4.0.0:** Adds ThoughtSpot MCP (IQVIA MIDAS analytical layer), TİTCK MCP (Türkiye regulatory primary), AdisInsight MCP (curated pipeline intelligence), and expanded openFDA Orange Book + Purple Book + biowaiver framework. Companion reference for `sub-protocol-product-development-tr.md`.

---

## §1. Source Acquisition Priority Hierarchy

When gathering information for any task (T1-T6), Claude MUST attempt sources in this order:

```
Priority 1: MCP tool if available
            └─> Clinical Trials MCP, PubMed MCP, bioRxiv MCP, Consensus MCP
Priority 2: Public REST API if available
            └─> openFDA, ClinicalTrials.gov v2, SEC EDGAR, PMC E-Utilities
Priority 3: web_fetch on primary source URL
            └─> FDA documents, EMA EPAR PDFs, sponsor IR pages, Orange/Purple Book
Priority 4: web_search
            └─> ONLY when primary source URL unknown; never for verifiable facts
```

**Discipline:** web_search should be treated as a **discovery mechanism** (finding URLs), not a **knowledge mechanism** (citing claims). All claims requiring Tier-0 confidence must resolve to a primary source via Priority 1-3.

---

## §2. FDA — openFDA REST API

**Base URL:** `https://api.fda.gov`
**Auth:** None required for basic rate (240 req/min, 1000 req/day); higher rates require free API key
**Format:** JSON

### 2.1 Drugs@FDA endpoint
```
GET https://api.fda.gov/drug/drugsfda.json?search={query}&limit={n}
```
Queries: approval history, NDA/BLA numbers, active ingredients, sponsor, submission class codes.

**Example — find all BLAs for a sponsor:**
```
https://api.fda.gov/drug/drugsfda.json?search=sponsor_name:"VERTEX+PHARMACEUTICALS"+AND+submissions.submission_class_code:BLA&limit=50
```

### 2.2 Drug Label endpoint
```
GET https://api.fda.gov/drug/label.json?search=openfda.brand_name:{brand}
```
Returns current label sections (INDICATIONS_AND_USAGE, DOSAGE_AND_ADMINISTRATION, CONTRAINDICATIONS, WARNINGS_AND_PRECAUTIONS, ADVERSE_REACTIONS, BOXED_WARNING, etc.) as structured JSON.

### 2.3 Adverse Events (FAERS) endpoint
```
GET https://api.fda.gov/drug/event.json?search=patient.drug.openfda.generic_name:{inn}&count=patient.reaction.reactionmeddrapt.exact
```
Returns signal-detection-friendly aggregated FAERS reports (adverse event count by MedDRA PT per drug).

**Cautions:**
- FAERS is a spontaneous reporting system — counts ≠ incidence
- Signal detection requires denominators (utilization data not in openFDA)
- Duplicate reporting not fully deduplicated

### 2.4 Recall enforcement endpoint
```
GET https://api.fda.gov/drug/enforcement.json?search=recall_initiation_date:[{YYYYMMDD}+TO+{YYYYMMDD}]
```
Returns FDA drug recall records with classification (I/II/III), reason, distribution pattern.

### 2.5 NDC (National Drug Code) endpoint
```
GET https://api.fda.gov/drug/ndc.json?search=brand_name:{brand}
```
Returns product-level data (dosage form, strength, route, marketing status).

---

## §3. FDA — Orange Book (Approved Drug Products)

**URL:** `https://www.accessdata.fda.gov/scripts/cder/ob/`
**API:** No official REST API
**Method:** Monthly cumulative ZIP files with tab-delimited text (products.txt, patent.txt, exclusivity.txt)

### 3.1 Orange Book monthly download
```
https://www.fda.gov/media/{id}/download  (products data file)
```

**Fields:**
- `products.txt` — all approved products + TE rating + RLD flag + applicant + strength/dosage form
- `patent.txt` — Orange Book patent listings per product
- `exclusivity.txt` — exclusivity periods (NCE, clinical study, orphan, pediatric, GAIN)

### 3.2 Practical workflow for post-LOE analysis

Pharmaintel analytical pattern:
1. Fetch latest products.txt monthly
2. Filter by active ingredient / application holder
3. Cross-reference patent.txt for patent thicket depth
4. Cross-reference exclusivity.txt for regulatory exclusivity overlay
5. Identify LOE landing date = latest of (last patent expiry, last exclusivity expiry, authorized generic launch)

See `task-modality-smallmol.md` §5 for Orange Book TE rating framework.

---

## §4. FDA — Purple Book (Biologics)

**URL:** `https://purplebooksearch.fda.gov/`
**API:** No official REST API
**Method:** Web search interface + downloadable Excel export

### 4.1 Purple Book content structure

- CDER list — biologics other than vaccines + allergenics
- CBER list — vaccines + blood products + cell/gene therapy + allergenics

Each entry: license number (BLA), proper name, proprietary name, license date, marketing status, interchangeability designation (biosimilar/interchangeable flag), reference product crosswalk.

### 4.2 Practical workflow for biosimilar analysis

1. Fetch Purple Book Excel export (Monthly)
2. Filter reference products vs biosimilars
3. Cross-reference BPCIA exclusivity arithmetic per `task-modality-biosimilar.md` §3.3
4. Check for interchangeability designation per `task-modality-biosimilar.md` §3.5

---

## §5. EMA — European Public Assessment Reports (EPAR)

**URL:** `https://www.ema.europa.eu/en/medicines`
**API:** Limited — no comprehensive REST API; EMA provides SPOR (Substance/Product/Organization/Referential) master data
**Method:** Web-fetch on individual EPAR landing pages + PDF extraction for full scientific discussion

### 5.1 EPAR per-product URL structure
```
https://www.ema.europa.eu/en/medicines/human/EPAR/{product-slug}
```

Each EPAR landing page includes:
- Authorization dates (first + renewal)
- CHMP opinion history + variations
- Risk Management Plan status
- EPAR full scientific discussion PDF
- Product information SmPC PDF (current + historical)
- Public Assessment Report for variation applications

### 5.2 EMA variations + referrals

For post-authorization discipline:
- Type IA/IB/II variations (manufacturing, labeling, indication)
- Article 20 referrals (safety-driven reviews)
- Article 31 referrals (public interest reviews)

### 5.3 SPOR master data
```
https://spor.ema.europa.eu/rmswi/
```
Standardized references for substances/products/organizations/referentials. Useful for INN+EMA product harmonization.

---

## §6. ClinicalTrials.gov v2 API (MCP available)

**MCP:** Clinical Trials MCP (preferred)
**Base URL:** `https://clinicaltrials.gov/api/v2/studies`
**Format:** JSON

### 6.1 MCP-first discipline

When Clinical Trials MCP is available in tool context, use MCP tools:
- `search_trials` — generic NCT discovery
- `get_trial_details` — single NCT deep dive
- `search_by_sponsor` — company pipeline
- `search_by_eligibility` — patient-trial matching
- `search_investigators` — KOL discovery
- `analyze_endpoints` — endpoint pattern analysis

See `sub-protocol-catalyst-watch.md` for readout timing discipline using MCP-mediated data.

### 6.2 REST API fallback
```
GET https://clinicaltrials.gov/api/v2/studies?query.cond={cond}&query.intr={intr}&pageSize={n}
```
Fields of interest: NCTId, BriefTitle, Phase, OverallStatus, PrimaryCompletionDate, EnrollmentCount, LeadSponsorName, CollaboratorsList, PrimaryOutcome, SecondaryOutcome, EligibilityCriteria.

### 6.3 Key fields for pharmaintel analysis

| Field | Use |
|---|---|
| `PrimaryCompletionDate` | Readout catalyst timing |
| `OverallStatus` | Active/Completed/Terminated/Suspended filtering |
| `StudyType` | Interventional vs Observational (RWE) |
| `Phase` | Clinical development stage |
| `PrimaryOutcome` | Endpoint framework analysis |
| `LeadSponsorName + CollaboratorsList` | Sponsor + collab mapping |

---

## §7. SEC EDGAR — Corporate Filings

**Base URL:** `https://data.sec.gov/`
**Auth:** None required; User-Agent header mandatory
**Format:** JSON + XBRL

### 7.1 Company facts endpoint
```
GET https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit-zero-padded}.json
```
Returns structured financial data (revenue, R&D expense, earnings, cash position) by XBRL taxonomy concept.

### 7.2 Filings index
```
GET https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=40
```
Returns list of 10-K / 10-Q / 8-K / DEF 14A filings.

### 7.3 Practical pharmaintel use cases

- **Revenue disaggregation** — 10-K revenue by product from segment reporting
- **R&D guidance** — forward-looking R&D pipeline narrative from MD&A
- **Risk factors** — regulatory/competitive/IP risk disclosures
- **Clinical catalyst calendars** — 8-K materiality filings for trial results, regulatory milestones, BD announcements
- **Proxy disclosure** — executive compensation, related party transactions (BD deal structuring)

See `task-company.md` §3 for 10-K analytical framework.

---

## §8. PubMed / PMC (MCP available)

**MCP:** PubMed MCP (preferred)
**Base URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

### 8.1 MCP-first discipline

When PubMed MCP is available:
- `search_articles` — keyword query
- `get_article_metadata` — PMID-based fetch
- `get_full_text_article` — PMCID-based full-text
- `find_related_articles` — similar articles / full-text availability / gene crosslinks
- `convert_article_ids` — PMID ↔ PMCID ↔ DOI

### 8.2 E-Utilities fallback
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text
```

---

## §9. bioRxiv / medRxiv (MCP available)

**MCP:** bioRxiv MCP (preferred) — Hub stdio `CureoHub/mcp-servers/biorxiv-mcp`, not Anthropic HCLS
**Base URL:** `https://api.biorxiv.org/` (details host fallback: `https://api.medrxiv.org/`)

MCP provides `search_preprints`, `get_preprint`, `get_categories`, `search_by_funder`, `search_published_preprints`, `get_content_statistics`, `get_usage_statistics`.

---

## §10. Consensus / Scholar Gateway / Exa (MCP available)

MCP tools:
- **Consensus MCP** — peer-reviewed papers with journal quality filter
- **Scholar Gateway MCP** — semantic search
- **Exa MCP** — web crawl + neural search + full-page fetch

These supplement rather than replace primary sources. Use for discovery when specific paper/company unknown.

---

## §11. Rate Limit + Caching Discipline

### 11.1 Per-API rate limits (free tier, 2026)

| API | Free tier limit | Key-required tier |
|---|---|---|
| openFDA | 240 req/min, 1000 req/day | 120,000 req/day with free key |
| ClinicalTrials.gov v2 | No documented limit (courtesy use) | — |
| SEC EDGAR | 10 req/sec | — |
| PubMed E-Utilities | 3 req/sec w/o key, 10 req/sec with key | NCBI API key free |
| Orange Book download | Monthly refresh (no realtime) | — |

### 11.2 Caching strategy

For repeated pharmaintel runs, cache acceptable time windows:
- Drugs@FDA approval data — 24 hours
- Orange Book data — monthly refresh
- Purple Book data — monthly refresh
- ClinicalTrials.gov — 6 hours (catalysts may shift)
- FAERS adverse event counts — weekly
- SEC filings — 24 hours (new 8-Ks emerge daily)
- EMA EPAR — weekly
- PubMed abstracts — 7 days

See `orchestration.md` §5 for cache invalidation discipline.

### 11.3 User-Agent discipline

All API calls should identify requester. For pharmaintel:
```
User-Agent: pharmaintel-claude-skill/3.0.0 (query@example.org)
```

---

## §12. Cross-API Triangulation Patterns

Key pharmaintel triangulation opportunities enabled by API layer:

### 12.1 Post-LOE small molecule pattern
```
openFDA Drugs@FDA (NDA metadata)
  ↓
Orange Book (patents + exclusivity)
  ↓
ClinicalTrials.gov (ANDA bioequivalence studies)
  ↓
FAERS (post-marketing surveillance context)
```

### 12.2 Biosimilar pattern
```
Purple Book (BLA + biosimilar/interchangeable status)
  ↓
openFDA Drug Label (current SmPC)
  ↓
ClinicalTrials.gov (comparative/switching studies)
  ↓
EMA EPAR (EU biosimilar positioning)
```

### 12.3 Pipeline catalyst pattern
```
ClinicalTrials.gov (PrimaryCompletionDate + Status)
  ↓
SEC EDGAR 8-K (sponsor announcement)
  ↓
Sponsor IR press release (web-fetch)
  ↓
Peer-reviewed publication if positive (PubMed)
```

---

## §15. ThoughtSpot MCP — IQVIA MIDAS Analytical Layer (v4.0.0)

**MCP server:** `https://agent.thoughtspot.app/mcp` (or `/bearer/mcp` for bearer-token clients, `/openai/mcp` for OpenAI MCP/Responses API)
**Auth:** OAuth via the user's ThoughtSpot tenant (which must be IQVIA MIDAS-bound for this skill's use case)
**Tier:** Tier-1 commercial primary (sponsor-licensed third-party panel)

> **Architectural note:** ThoughtSpot is a **plug-and-play analytics layer** over the user's licensed ThoughtSpot tenant. pharmaintel itself does NOT redistribute IQVIA MIDAS data; it queries the user's authorized ThoughtSpot session, which enforces RLS/CLS automatically. This complements (not replaces) `sources-catalog.md §IQVIA Institute (free tier)` — the free Institute reports remain the no-license fallback.

### §15.1 Tool catalogue

| Tool | Use case | When to call |
|---|---|---|
| `ping` | Health check | First call in any ThoughtSpot session |
| `getDataSourceSuggestions` | Identify available data models | Before formulating analytical question — discover what MIDAS scope is exposed |
| `getRelevantQuestions` | Decompose high-level prompt into schema-aware sub-questions | After data source selected; produces 4-7 actionable analytical questions |
| `getAnswer` | Execute one analytical question; returns preview data + frame_url + session_identifier + generation_number | Per sub-question; parallel-safe |
| `createLiveboard` | Persist conversation analyses into a shareable Liveboard | End of session; OPTIONAL (only if user wants persistent artifact) |

### §15.2 Canonical pharmaintel query patterns

**Pattern 1 — Türkiye + 5-country reference monthly trend (36-month):**

```
getRelevantQuestions(
  prompt: "Show monthly TRx volume and EUR value sales for [INN/ATC]
           in Turkey, France, Spain, Italy, Greece, Portugal, Germany, UK
           over last 36 months, broken by molecule and corporation",
  data_source: "MIDAS Monthly Sales by Country"
)
→ Decomposes into 4-7 sub-questions
→ Each getAnswer returns ~200-row preview + frame_url
→ Optional: createLiveboard for sharing
```

**Pattern 2 — 36-country ATC class snapshot:**

```
getRelevantQuestions(
  prompt: "Market share by molecule within ATC [code] for latest month
           across all 36 MIDAS countries, ranked by USD value sales",
  data_source: "MIDAS Sales by ATC Class"
)
→ Output feeds Module M3 (Cross-Country Market Sizing) in
  sub-protocol-product-development-tr
```

**Pattern 3 — Genericization trajectory pre/post LOE:**

```
getRelevantQuestions(
  prompt: "For [INN], monthly volume and value by brand/generic flag in
           Turkey vs EU5 vs US over 24 months pre/post first generic entry",
  data_source: "MIDAS Brand vs Generic Trajectory"
)
→ Output feeds Module M1 (Generic Feasibility Scorecard) cross-country
  uptake reference dimension
```

**Pattern 4 — Cross-country ex-manufacturer pricing:**

```
getRelevantQuestions(
  prompt: "Ex-manufacturer EUR price for [INN/strength/dosage form] across
           France, Spain, Italy, Greece, Portugal, Germany, UK, Turkey for
           latest month",
  data_source: "MIDAS Ex-Manufacturer Pricing"
)
→ Output feeds Module M2 (Price Ceiling Simulation) — 5-country reference
  base for TİTCK Fiyat Değerlendirme Komisyonu calculation
```

### §15.3 Discipline rules

1. **Provenance stamping:** Every ThoughtSpot-derived claim must record `(data_source, session_identifier, generation_number, retrieved_at_iso)` in §Provenance Disclosure.
2. **No raw row redistribution:** Pharmaintel reports may include AGGREGATE figures and trend narratives, but must NOT include raw row-level MIDAS exports. IQVIA license terms prohibit redistribution.
3. **Currency normalization for TR:** TL-denominated MIDAS values must be normalized to EUR/USD with kur tarihi documented; aksi halde TL deprecation yanılsama yaratır.
4. **MIDAS panel limitations** (mandatory acknowledgement in every report):
   - Panel-projected estimates, not unit-level shipping data
   - Hospital-only product coverage variable across countries
   - OTC product panel asymmetric (especially in Turkey vs EU)
   - Compounding pharmacies + parallel imports under-reported
   - Data refresh lag typically 30-60 days for newest month
5. **RLS/CLS respect:** ThoughtSpot tenant'ında uygulanan row/column-level security MCP üzerinden de geçerlidir. Erişilemeyen veri "data-redacted" olarak raporlanır.
6. **Liveboard creation OPSIYONEL:** Default `getAnswer` preview ile rapor üret; `createLiveboard` ancak kullanıcı kalıcı paylaşılabilir analiz isterse.
7. **Tenant configuration dependency:** Bu protokol IQVIA MIDAS data feed'li bir ThoughtSpot tenant varsayar. Tenant farklı veri seti barındırıyorsa (yerel panel, sponsor primary research) sorgu pattern'leri buna göre adapte edilmelidir.
8. **OAuth session refresh:** Long-running pharmaintel sessions için ThoughtSpot OAuth token expiration kontrol edilmeli; expired session "data-unavailable" olarak handle edilir.

### §15.4 ThoughtSpot setup precondition

User must have:
- Active ThoughtSpot Enterprise / Embedded license
- ThoughtSpot instance ≥10.11.0.cl
- IQVIA MIDAS data feed loaded into the tenant's worksheets/models
- OAuth client registered (DCR or manual via `https://agent.thoughtspot.app/clients`)
- MCP client (Claude.ai connector / Claude Desktop / Claude Code) configured per `https://developers.thoughtspot.com/docs/connect-mcp-server-to-clients`

If precondition is not met, pharmaintel falls back to free-tier IQVIA Institute reports + national reference price registries (CEPS, AIFA, EOF, INFARMED, BotPlus) via web_fetch — with degraded confidence Tier-2 (aggregate published only, no monthly granularity).

---

## §16. TİTCK MCP — Türkiye Regulatory Primary (v4.0.0)

**MCP server:** `https://titck.cureonics.com/mcp` (self-host; `titck-origin.cureonics.com` aynı servisin ikinci adı)
**Auth:** Bearer ZORUNLU — uç 2026-08-02'den beri kapılı (`${TITCK_MCP_API_KEY}`); anahtarsız çağrı 401 döner
**Tier:** Tier-0 primary (Türkiye regulatuar zemin gerçeği)

> **Architectural note:** TİTCK MCP, Türkiye İlaç ve Tıbbi Cihaz Kurumu'nun açık kayıt verilerini (master drug records, fiyat zinciri, eşdeğer grup, withdrawal, ATC sınıf, holder portföy, KÜB/KT dokümanları) yapısal MCP arayüzü üzerinden açar. `sources-catalog.md §Türkiye sources` web URL'leri yerine MCP tool calls önerilir — daha hızlı, schema-aware, machine-readable.

### §16.1 Tool catalogue (full)

Bkz. `sub-protocol-product-development-tr.md` §3.1 — tüm 25+ tool listesi. Pharmaintel'in primary çağrı kalıpları:

| Use case | Recommended tool sequence |
|---|---|
| "Bu INN Türkiye'de var mı?" | `search_drugs` (INN bazlı) |
| Tek-ürün full deep-dive | `search_drugs` → `get_drug_snomed_profile` |
| Eşdeğer grup mapping | `find_equivalent_products_by_substance` |
| Biyobenzer ilk-onay verifikasyonu | `find_biosimilar_group` |
| First-in-class authorization | `find_first_in_class` |
| ATC sınıf snapshot | `get_atc_class_summary` + `get_atc_hierarchy` |
| Holder portföy | `get_holder_portfolio` + `compare_holders` |
| Fiyat zinciri + history | `get_price_history` |
| Referans fiyat | `find_reference_prices_for_drug` |
| Withdrawal/iptal | `find_authorization_cancellations_for_drug` + `get_withdrawal_trend` |
| Madde 23 başvuru | `find_regulation_article23_for_drug` |
| Off-label onkoloji | `find_off_label_uses_for_drug` |
| KÜB/KT/scientific PDF | `find_documents_for_drug` + `get_document` |
| Yeni-onay watch | `find_new_authorizations_since` |
| Veri kalite gap awareness | `list_unmapped_ingredients` + `get_dataset_overlap` |

### §16.2 Discipline rules

1. **Tier-0 primary:** TİTCK MCP, Türkiye regulatuar/fiyat claim'leri için Tier-0'dır. Web search ile çelişiyorsa **TİTCK MCP'ye uy** — TİTCK kendi veri tabanının primary kaynağıdır.
2. **SNOMED substance harmonization:** Multi-INN combination ürünler için "eşdeğer grup" çıkarımı yapmadan önce `find_equivalent_products_by_substance` ile substance-level mapping doğrula.
3. **Withdrawal trend ≠ tek iptal:** Tek bir cancellation trend değildir; `get_withdrawal_trend` aggregate veriyi kullan.
4. **Document content access:** KÜB/KT/scientific assessment PDF/DOCX'leri `find_documents_for_drug` ile bul, `get_document` ile full text al — bu, hekim bilgi metni katmanı için Tier-0 sağlar.
5. **Holder name canonicalization:** TİTCK MCP `find_holder_by_alias` ile spelling variant → canonical mapping yapar; sponsor analizinde her zaman canonicalize et (örn. "ROCHE", "Roche Müstahzarları", "F. Hoffmann-La Roche" → tek holder_id).
6. **Cache TTL:** TİTCK ruhsat data 24 saat; fiyat data 7 gün (TL deprecation periyodlarında daha kısa); withdrawal trend aylık.

### §16.3 Cross-API triangulation (TİTCK ↔ openFDA ↔ EMA)

Tipik üç-kaynak indication harmonization:

```
TİTCK get_drug → KÜB indication text (Türkçe)
  ↓
openFDA Drug Label → INDICATIONS_AND_USAGE (English RLD)
  ↓
EMA EPAR SmPC → SmPC indication (English EU)
  ↓
Triangulation: tüm üçü hizalanmalı; KÜB indication darsa
"Türkiye-spesifik label trimming" tag'le
```

Bu pattern `sub-protocol-product-development-tr.md §5.1 P1` ile koordineli.

---

## §17. AdisInsight MCP — Curated Pipeline Intelligence (v4.0.0)

**MCP server:** `https://adisinsight-mcp.springer.com/mcp`
**Auth:** AdisInsight subscription required (Springer Nature)
**Tier:** Tier-1 curated (Springer Adis editorial team manual curation)

> **Architectural note:** AdisInsight, ClinicalTrials.gov / openFDA / EMA EPAR'da bulunan structured data'yı **enriched metadata + manual editorial overlay** ile sunar. Pipeline data (preclinical → marketed), drug class taxonomy, indication mapping, M&A trail, sponsor company portfolios. Pharmaintel'de "global pipeline scan" + "sponsor portfolio diligence" + "modality landscape" use case'leri için primary discovery layer.

### §17.1 Tool catalogue

| Tool | Use case |
|---|---|
| `search_drugs` | Filter by INN, brand, dev_phase, therapeutic area, drug_class, mechanism, target |
| `get_drug` | Single-drug deep dive — dev_phase, dev_company, indications, mechanisms, targets, formulations, brand list, organizational role |
| `search_trials` | Trial discovery (curated metadata > ClinicalTrials.gov raw) |
| `get_trial` | Trial deep dive — eligibility, endpoints, sites, sponsor |
| `search_drug_companies` | Company portfolio analysis (drug development emphasis) |
| `search_trial_companies` | Company trial sponsorship analysis |
| `analyze_endpoints` | Primary/secondary endpoint pattern across trial set |
| `generate_chart` | Hızlı pipeline visualization (phase/sponsor/indication/TA breakdown) |

### §17.2 Canonical pharmaintel patterns

**Pattern 1 — In-licensable asset shortlist:**

```
search_drugs(
  filters: {
    therapeutic_area_contains: "[TA]",
    dev_phase: ["Phase III", "Pre-registration", "Marketed"],
    available_for_licensing: true
  }
)
→ Returns ranked shortlist
→ Followed by get_drug per top candidate for deep dive
→ Cross-reference with TİTCK to identify TR market presence (Module M7)
```

**Pattern 2 — Modality landscape with patent-cliff filter:**

```
search_drugs(
  filters: {
    drug_class_type: "biological",
    dev_phase: "Marketed",
    has_patent_data: true
  }
)
→ Sort externally by years-to-LOE (cross-reference openFDA + Orange/Purple)
→ Pharmaintel uses for biosimilar feasibility prioritization
```

**Pattern 3 — Endpoint pattern analysis:**

```
analyze_endpoints(
  therapeutic_area: "[TA]",
  phase: "Phase III"
)
→ Identifies endpoint trends — natural history controls, external
  comparators, single-arm + Bayesian, surrogate endpoints
→ Feasibility input for Türkiye RWE-driven dossier strategy
```

**Pattern 4 — Sponsor pipeline diligence:**

```
search_drug_companies(filters: { name: "[Sponsor]" })
→ Returns company-level aggregates (asset count by phase, TA mix)

For each top sponsor's portfolio drug:
  get_drug(...) → enriched metadata
```

### §17.3 Discipline rules

1. **Tier-1, not Tier-0:** AdisInsight curated subset'tir. Primary FDA/EMA/TİTCK + ClinicalTrials.gov ile triangüle edilmelidir (`triangulation.md` §2).
2. **Absence ≠ confirmation:** AdisInsight'ta bir asset olmaması confirmed non-existence değildir, özellikle Çinli/Hintli/erken-evre asset'ler için. Negative claim için multi-source verification gerekir.
3. **License attribution:** AdisInsight-derived claims must attribute "per AdisInsight (Springer Nature)" in footnotes.
4. **Editorial lag:** Curated data has 1-4 week editorial lag vs raw clinicaltrials.gov; for breaking events use ClinicalTrials.gov MCP first.
5. **Composability:** AdisInsight `get_drug` zenginleştirilmiş metadata için pharmaintel default first-call'dır pipeline scan'lerde — `search_drugs` shortlist'ini followed by `get_drug` ile derinleştir.

### §17.4 Cross-API triangulation (AdisInsight ↔ TİTCK ↔ ClinicalTrials.gov)

```
AdisInsight search_drugs → "[Sponsor] has Phase III asset in [TA]"
  ↓
TİTCK search_holders + get_holder_portfolio → sponsor TR pazarda mı
  ↓
ClinicalTrials.gov MCP search_trials with location:Turkey
  → Sponsor active TR trial site varsa highest-confidence
  "true Turkish development engagement"
```

Bu pattern `sub-protocol-product-development-tr.md §5.3 P3` ile koordineli.

---

## §18. openFDA Orange Book + Purple Book + Biowaiver — Generic Development Bridge (v4.0.0)

`api-integrations.md` §2-4 zaten openFDA + Orange Book + Purple Book temellerini kodlar. Bu bölüm Türkiye **product development** bağlamında özel sorgu örüntülerini ekler.

### §18.1 Generic eligibility decision tree (US Orange Book → TR feasibility bridge)

```
Step 1: openFDA Drugs@FDA — RLD identification
  GET /drug/drugsfda.json?
       search=openfda.generic_name:"[INN]"+
              AND submissions.submission_class_code:NDA
  → Identifies pioneer NDA(s) for [INN]
  → Returns NDA number, sponsor, approval date

Step 2: Orange Book products.txt + patent.txt + exclusivity.txt
  → Filter products.txt by Application Number = NDA
  → TE rating per strength/dosage form:
    AA — pharmaceutical equivalents (no biowaiver — full BE required)
    AB — therapeutic equivalents with bioequivalence demonstrated
    AB1, AB2, AB3 — multiple bioequivalence subgroups
    AN — solutions/parenterals (BE assumed)
    AO — injectable oil
    AP — injectable aqueous
    AT — topical
    BC — controlled-release (no biowaiver; specific guidance)
    BD — active ingredients with documented bioequivalence problems
    BE — delayed-release products
    BN — non-bioequivalent products (FDA decision)
    BP — potential bioequivalence problem (limited generic FDA approval)
    BR — suppositories, enemas
    BS — tested standards
    BT — topical products with bioequivalence issue
    BX — insufficient data (FDA holds judgment)
  → patent.txt: Filter by Application Number; collect patent expiry dates,
    Use Codes (U-XXXX = indication-specific)
  → exclusivity.txt: Filter by Application Number; collect exclusivity codes
    (NCE = 5y; NPP = 3y; ODE = 7y; PED = +6mo; GAIN = +5y; M = 3y; D = 3y;
     I = 3y; PI = 5y; NS = 3y)

Step 3: BCS classification
  → openFDA does NOT directly expose BCS class
  → Source A: WHO Essential Medicines BCS list (web_fetch)
  → Source B: EMA biowaiver assessment in EPARs (web_fetch + PDF parse)
  → Source C: FDA biowaiver list (limited; periodic publications)
  → Source D: Peer-reviewed literature (PubMed via medsearch handoff
    using "[INN] BCS classification" or "[INN] solubility permeability")

Step 4: Biowaiver decision
  BCS Class I (high sol + high perm) + IR oral solid → BIOWAIVER eligible
    (FDA + EMA both accept)
  BCS Class III (high sol + low perm) + IR oral solid + Q1/Q2 excipients
    → BIOWAIVER possible (FDA 2017 guidance + EMA 2010 amendment;
       requires excipient justification + dissolution similarity f2≥50)
  BCS Class II (low sol + high perm) → No biowaiver; full BE required
  BCS Class IV (low sol + low perm) → No biowaiver; full BE required
  Modified-release → No BCS biowaiver; full BE required
  Solutions/IV/IM aqueous → BE assumed; no clinical study (Orange AN/AP)

Step 5: TR equivalent group bridging
  TİTCK find_equivalent_products_by_substance(barcode) →
    existing TR generic count + holder map
  → If TR equivalent group is empty → first-mover opportunity
  → If TR equivalent group has 5+ active members → saturation; differentiation
    needed (XR, combination, alternative dosage form)

Step 6: TR Reliance pathway eligibility
  If FDA + EMA + WHO PQ all approved → TR Reliance eligible
  → Compressed TİTCK pathway (4-6 months typical)

Output: feasibility verdict for sub-protocol-product-development-tr Module M1
```

### §18.2 Biosimilar candidate scan (Purple Book → TR biyobenzer durum)

```
Step 1: Purple Book monthly Excel export
  https://purplebooksearch.fda.gov/
  → Filter by reference product holders + biosimilar/interchangeable flags

Step 2: BPCIA exclusivity arithmetic
  - Reference product 12-year exclusivity floor
  - 4-year biosimilar application bar
  - Effective LOE = max(patent expiry, 12y RP exclusivity)
  - Interchangeable designation requires additional study

Step 3: TİTCK biyobenzer durum
  → find_biosimilar_group(barcode of TR-marketed innovator)
  → Returns SNOMED-substance peers ordered oldest-first
  → Identifies TR biyobenzer ilk-onay yılı (if any)

Step 4: Cross-country biosimilar uptake (ThoughtSpot MIDAS Pattern 3)
  → EU5 post-biosimilar share trajectory
  → Project TR uptake under analogous conditions

Step 5: Synthesis feeds Module M1 (biosimilar feasibility variant)
```

### §18.3 BCS biowaiver — Türkiye TİTCK position

TİTCK, BCS biowaiver kabulünde EMA Bioequivalence Guideline (CPMP/EWP/QWP/1401/98 Rev. 1/Corr **) ile uyumludur. Pharmaintel `sub-protocol-product-development-tr.md §4.5 Module M5` üzerinden bu degerlendirmeyi otomatize eder. Anahtar TR-spesifik notlar:

1. TİTCK biowaiver dossier'da **f2 dissolution similarity** kalkülasyonu zorunludur (12-tablet × 3 media: pH 1.2, 4.5, 6.8)
2. Excipient Q1/Q2 sameness için EMA standardı kullanılır
3. BCS Class III biowaiver TİTCK'da **vakaya-özel** kabul edilir (otomatik değil); detaylı excipient justification gerektirir
4. Biowaiver başvuru maliyeti tipik 30-60K USD vs full BE study 150-300K USD — Türkiye CRO maliyetlerinde tasarruf önemli (örn. Çiğli/İzmir, ABDI, Sansa Bio)

### §18.4 Patent + exclusivity Türkiye perspective

`sub-protocol-product-development-tr.md` Orange Book patent landscape'i **US ayna** olarak kullanır. Türkiye patent perspectivesi (SMK 6769, Yargıtay 11.HD, FSHHM, Bolar exemption, supplementary protection certificate analog, biyobenzer veri imtiyazı 6 yıl) için `pharmapatent` skill'ine handoff yapılır. Pharmaintel'de tek-skill ortamında, TR patent durumu için `web_fetch turkpatent.gov.tr` ve [`Espacenet`] PCT/EPO tracking yapılır — bu durumda confidence Tier-2'ye düşer.

---

## §13. Forbidden API Use Patterns

- ❌ Scraping protected data (IQVIA MIDAS direct, Clarivate Cortellis, GlobalData, SEC-paywalled) — pharmaintel is free-tier-only **EXCEPT** for licensed third-party data accessed through user's own MCP-authenticated session (e.g., ThoughtSpot tenant with IQVIA MIDAS feed; AdisInsight via Springer subscription). User-authenticated MCP access respects the user's existing license and is permitted.
- ❌ Using API responses to claim compounded metrics without explicit API-derived support (e.g. "market share" from openFDA — openFDA has no utilization data)
- ❌ Replacing primary source citation with API URL only — always name the authoritative document + API URL is secondary locator
- ❌ Ignoring API rate limits (may get blocked + undermines skill reliability for future users)
- ❌ Submitting PII or patient identifiable data to APIs (FAERS field access, etc. has PII considerations)
- ❌ Using API data for claims outside its design scope (e.g. FAERS counts ≠ incidence rates)

---

## §14. Versioning & Changelog

- **v4.0.0 (2026-04-29):** MAJOR. Adds §15 ThoughtSpot MCP (IQVIA MIDAS analytical layer with 4 canonical pharmaintel query patterns + RLS/CLS discipline + tenant precondition spec), §16 TİTCK MCP (Tier-0 Türkiye regulatory primary with 25+ tool catalogue + cross-API triangulation pattern with openFDA + EMA), §17 AdisInsight MCP (Tier-1 curated pipeline intelligence with 4 canonical patterns including in-licensable shortlist + modality landscape with patent-cliff filter + endpoint pattern analysis + sponsor pipeline diligence), §18 expanded openFDA Orange Book + Purple Book + biowaiver framework (full TE rating + exclusivity code reference + BCS biowaiver decision tree + TR Reliance bridge + biosimilar candidate scan with BPCIA exclusivity arithmetic + TR biyobenzer durum integration). New manifest gate G64. Companion to new sub-protocol `sub-protocol-product-development-tr.md`.
- **v3.0.0 (2026-04-15):** Initial release. Cross-cutting API integration reference replacing pure web_search-based source acquisition with structured MCP-first + REST API-first + web-fetch-fallback discipline. Coverage: source acquisition priority hierarchy (MCP > REST API > web_fetch > web_search), openFDA (Drugs@FDA + Label + FAERS + Recall + NDC endpoints), Orange Book + Purple Book monthly download patterns, EMA EPAR web-fetch + SPOR master data, ClinicalTrials.gov v2 MCP-first + REST fallback, SEC EDGAR company facts + filings, PubMed E-Utilities MCP-first + fallback, bioRxiv MCP, Consensus + Scholar Gateway + Exa supplementary MCPs, rate limit + caching discipline (per-API limits + cache invalidation windows), cross-API triangulation patterns (post-LOE small mol, biosimilar, pipeline catalyst), forbidden API use patterns. New manifest gate G36. Used by all T1-T6 tasks as cross-cutting infrastructure.
