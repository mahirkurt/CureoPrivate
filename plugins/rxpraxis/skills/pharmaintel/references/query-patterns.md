# pharmaintel — Query Patterns (MCP + Free-Tier Tools)

Operational cookbook for how to hit each source class. Paired with `sources-catalog.md` (what is accessible) and `triangulation.md` (how to combine). The patterns below are canonical — deviations should be justified.

---

## 1. Exa (semantic web + full-text)

**Strengths:** meaning-based (keyword-independent) retrieval; full-text extraction from paywall-adjacent pages; good for heterogeneous web (IR pages + press + ecosystem).

### 1.1 Company-universe discovery

```
web_search_exa:
  query: "<company name> pipeline clinical development 2025 2026"
  num_results: 10
```

### 1.2 Ecosystem mapping (find similar)

```
Exa findSimilar (if available via Exa MCP):
  url: "<competitor IR pipeline page>"
  → returns ecosystem of companies with similar asset pages
```

### 1.3 Full-text extraction of a known URL

```
web_fetch_exa:
  url: "<specific IR page, FDA page, or EPAR>"
  → returns clean markdown with content section
```

### 1.4 Category-filtered discovery

Exa supports category filters — use when available:
- `category: "research paper"` for peer-reviewed
- `category: "company"` for corporate sites
- `category: "news"` for news pages
- `category: "pdf"` for PDF documents (FDA reviews, EPARs, investor decks)

### 1.5 Time-bounded semantic queries

```
query: "<concept>"
start_published_date: "YYYY-MM-DD"
end_published_date: "YYYY-MM-DD"
```

**When NOT to use Exa:** structured registry data (ClinicalTrials.gov MCP is better); precise regulatory documents (direct FDA/EMA fetch is authoritative — Exa's cache may be stale).

---

## 2. Tavily (real-time news + finance)

**Strengths:** recency sensitivity; news aggregation; finance topic mode.

### 2.1 Recent-news sweep

```
tavily_search:
  query: "<drug name OR company name> FDA approval OR phase 3 readout"
  topic: "news"
  days: 7  (or 30, 90 depending on scope)
  search_depth: "advanced"
```

### 2.2 Finance-mode queries

```
tavily_search:
  query: "<ticker> earnings guidance pipeline"
  topic: "finance"
  search_depth: "advanced"
```

### 2.3 Domain-scoped pharma-media sweep

```
tavily_search:
  query: "<topic>"
  include_domains:
    - "endpts.com"
    - "statnews.com"
    - "fiercebiotech.com"
    - "fiercepharma.com"
    - "biopharmadive.com"
    - "bioworld.com"
    - "evaluate.com"
  exclude_domains:
    - "reddit.com"
    - "seekingalpha.com"   # use Seeking Alpha only for transcripts, not primary news
  days: 30
```

### 2.4 Catalyst-watch agent pattern

Weekly/daily:
```
Parallel Tavily calls:
  - topic: news, days: 1-7, query: "FDA PDUFA decision"
  - topic: news, days: 1-7, query: "CHMP positive opinion"
  - topic: finance, days: 1, query: "biotech earnings"
  - topic: news, days: 3, query: "phase 3 readout <therapeutic area>"
```

---

## 3. Fetch (direct page retrieval for canonical sources)

Use the `Fetch:fetch` MCP or `web_fetch` tool for:

### 3.1 FDA

```
# Drug approval page:
https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=<APPNO>

# Drug label PDF:
https://www.accessdata.fda.gov/drugsatfda_docs/label/<YEAR>/<APPNO>lbl.pdf

# Medical Review PDF (typically 3-6mo post-approval):
https://www.accessdata.fda.gov/drugsatfda_docs/nda/<YEAR>/<APPNO>Orig1s000MedR.pdf
https://www.accessdata.fda.gov/drugsatfda_docs/bla/<YEAR>/<APPNO>Orig1s000MedR.pdf

# FDA press announcement:
https://www.fda.gov/news-events/press-announcements

# FDA Advisory Committee Calendar:
https://www.fda.gov/advisory-committees/advisory-committee-calendar

# Orange Book search:
https://www.accessdata.fda.gov/scripts/cder/ob/search_product.cfm

# Purple Book search:
https://purplebooksearch.fda.gov/
```

### 3.2 EMA

```
# EPAR search → product page:
https://www.ema.europa.eu/en/medicines/human/EPAR/<product-slug>

# CHMP agendas/minutes:
https://www.ema.europa.eu/en/committees/chmp/chmp-agendas-minutes-highlights

# EMA referrals:
https://www.ema.europa.eu/en/human-regulatory/post-authorisation/referral-procedures
```

### 3.3 SEC EDGAR

```
# Full-text search (JSON response):
https://efts.sec.gov/LATEST/search-index?q=<URL-encoded query>&forms=8-K&dateRange=custom&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD

# Company filings list by CIK:
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<CIK>&type=<form>&dateb=&owner=include&count=40&action=getcompany

# Direct filing access:
https://www.sec.gov/Archives/edgar/data/<CIK>/<accession-no-dashes>/<accession-no-dashes>-index.htm
```

**CIK lookup:** `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=<company-name>&type=10-K`

### 3.4 DailyMed

```
https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=<drug-name>
```

### 3.5 Orange Book / Purple Book direct lookup

Via the Fetch tool, browse the search interfaces; structured entries confirm: NDA/BLA number, applicant, approval date, patents, exclusivity periods, therapeutic equivalence, biosimilar/interchangeable markers.

### 3.6 HTA

```
# NICE TA:
https://www.nice.org.uk/guidance/ta<number>

# ICER:
https://icer.org/assessment/<therapeutic-slug>/

# CADTH:
https://www.cadth.ca/<report-slug>
```

### 3.7 Company IR

Standard pattern: `investors.<company>.com` or `<company>.com/investors` or `ir.<company>.com`. Search for:
- "Pipeline" or "Products" page (current assets)
- "Events" or "Presentations" page (R&D Days, investor days)
- "News" or "Press Releases" feed
- "Financials" → SEC filings link-through

---

## 4. PubMed MCP

**Strengths:** MeSH + Substance Name indexing; structured author + affiliation queries; PMC full-text access.

### 4.1 Substance + condition + study type

```
search_articles:
  query: ("glofitamab"[Substance Name] OR "mosunetuzumab"[Substance Name])
         AND "Lymphoma, B-Cell"[Mesh]
         AND ("2023"[Date - Publication] : "2026"[Date - Publication])
  sort: "date"
  max_results: 20
```

### 4.2 RCT / meta-analysis filter

```
query: "pembrolizumab" AND "non-small cell lung cancer"
       AND ("Randomized Controlled Trial"[Publication Type]
            OR "Meta-Analysis"[Publication Type]
            OR "Systematic Review"[Publication Type])
```

### 4.3 Safety-focused

```
query: "CAR-T cell therapy"
       AND ("cytokine release syndrome"[MeSH Terms] OR "neurotoxicity"[MeSH Terms])
       AND "Adverse Effects"[Subheading]
```

### 4.4 Author / institution network

```
query: "<author surname> <initial>[au] AND <institution>[ad]"
```

### 4.5 Full-text (PMC) retrieval

For open-access articles, PMC-indexed:
```
get_full_text_article:
  pmcid: "PMC<number>"
```

---

## 5. Clinical Trials MCP

**Strengths:** structured sponsor/intervention/phase/endpoint queries; eligibility detail; investigator field.

### 5.1 Sponsor + phase + status

```
search_trials:
  sponsor: "Roche" OR "Genentech"
  phase: ["PHASE3"]
  status: ["RECRUITING", "ACTIVE_NOT_RECRUITING", "COMPLETED"]
```

### 5.2 Intervention + condition + outcome

```
search_trials:
  intervention: "trastuzumab deruxtecan"
  condition: "Breast Neoplasms"
  primary_outcome: "progression-free survival" OR "overall survival"
```

### 5.3 Date-bounded (for catalyst tracking)

```
search_trials:
  phase: "PHASE3"
  primary_completion_date_from: "2026-01-01"
  primary_completion_date_to: "2026-12-31"
  status: "ACTIVE_NOT_RECRUITING"
```

### 5.4 Investigator / site

```
search_investigators:
  investigator_name: "<PI surname>"
  # → returns trials where they appear as PI
```

### 5.5 Cross-registry sweep pattern

For truly global pipeline work, ClinicalTrials.gov alone misses Chinese-origin programs (which register on ChiCTR). Complement with:
- WHO ICTRP meta-search via `trialsearch.who.int`
- CTIS via `euclinicaltrials.eu` (for EU-primary trials post-2023)

---

## 6. bioRxiv / medRxiv MCP

### 6.1 Category-filtered

```
search_preprints:
  category: "clinical trials"   # medRxiv categories
  keyword: "<topic>"
  date_from: "YYYY-MM-DD"
```

### 6.2 Published-state filter

```
search_published_preprints:
  # returns preprints that have become peer-reviewed publications — useful for tracking readout → publication pipeline
```

### 6.3 Funder-scoped

```
search_by_funder:
  ror_id: "<NIH / Wellcome / EU ROR ID>"
```

---

## 7. Consensus MCP

**Strengths:** synthesis of peer-reviewed evidence into yes/no/mixed verdicts with citations.

### 7.1 Natural-language question format

```
search:
  query: "Does CAR-T therapy improve overall survival in relapsed/refractory multiple myeloma?"
  # → returns verdict: Yes / No / Possibly / Mixed, with citation cluster
```

### 7.2 When to use Consensus in pharmaintel

- Rapid evidence check on a pivotal claim (*"does this drug reduce mortality?"*)
- Sanity-checking company positioning (*"is this MoA associated with increased CV risk?"*)
- Building the scientific foundation layer beneath a commercial analysis (often delegate to medsearch for depth)

---

## 8. Paper Search MCP (multi-source academic)

**Strengths:** parallel across arXiv + bioRxiv + CrossRef + Google Scholar + IACR + medRxiv + PubMed + Semantic Scholar — widest coverage.

### 8.1 Broad discovery phase

```
search:
  query: "<topic>"
  # → aggregates across all 8 underlying sources
```

### 8.2 Source-targeted

If only a specific source is wanted:
```
search_semantic / search_pubmed / search_arxiv / search_biorxiv / search_crossref
```

Use `search_semantic` (Semantic Scholar) for **influential citation counts** — useful for identifying seminal papers in a modality landscape.

---

## 9. Scholar Gateway MCP

**Strengths:** semantic search; deep linked citations via Semantic Scholar backend.

### 9.1 Semantic reformulation

When keyword search is imprecise:
```
semanticSearch:
  query: "<natural language description of concept>"
  # → returns semantically related papers even without keyword overlap
```

---

## 10. SEC EDGAR full-text search

### 10.1 Event-focused (8-K)

```
q: "\"<drug name or indication>\""
forms: 8-K
dateRange: custom
startdt: YYYY-MM-DD
enddt: YYYY-MM-DD
```

### 10.2 Pipeline-focused (10-K / 10-Q MD&A)

```
q: "\"breakthrough therapy designation\"" OR "\"priority review\""
forms: 10-K,10-Q
```

### 10.3 Deal-focused

```
q: "<acquirer> <target>"
forms: 8-K,S-4,DEFM14A
```

### 10.4 Insider-activity

Use Form 4 filtered by issuer CIK for insider buy/sell pattern (not for primary fact-finding; for sentiment signal).

---

## 11. Patents — Google Patents / Lens.org / Orange Book

### 11.1 Direct patent lookup (Google Patents)

```
https://patents.google.com/patent/<patent-number>
```

### 11.2 Assignee + date range + keyword (Google Patents Advanced)

```
https://patents.google.com/?assignee=<company>&after=priority:YYYY-MM-DD&q=<keyword>
```

### 11.3 Orange Book → patent resolution

1. Orange Book entry lists patent numbers for an NDA
2. Fetch each number from Google Patents / USPTO
3. Read claims + expiration + family
4. Cross-check PTAB for IPR challenges: `https://ptab.uspto.gov/#/search`

### 11.4 Lens.org patent-scholarly bridge

Lens.org is uniquely useful for linking a patent family to its underlying scientific publications — valuable for modality landscape work where the academic precursor of a clinical candidate matters.

---

## 12. HTA & ICER fetch

```
# NICE: direct TA ID navigation
https://www.nice.org.uk/guidance/ta<NNN>

# ICER: topic-based assessments
https://icer.org/assessment/<topic-slug>/

# CADTH:
https://www.cadth.ca/search?query=<drug-name>&field=reports
```

---

## 13. Industry-media free-tier strategies

Free-tier media hits rate limits or paywalls; pharmaintel uses:

1. **Tavily domain-scoped search** (see §2.3) as the primary aggregator — returns excerpts for most queries
2. **Exa web_fetch** on known article URL — extracts clean text
3. **Google News search via Tavily** — broadest fallback

When an article is paywalled-beyond-excerpt, pharmaintel reports the excerpt + flags "paywall — full-text unavailable."

---

## 14. Earnings call transcripts

1. **Seeking Alpha free tier** — search `seekingalpha.com/earnings/<ticker>`
2. **Fool.com** — `fool.com/earnings-call-transcripts/`
3. **Company IR / 8-K exhibit** — management commentary filed as 8-K exhibit
4. **AlphaStreet** — `alphastreet.com/news/earnings/`

For most biotech/pharma, at least one of these will have the transcript free.

---

## 15. Query construction — cross-cutting principles

### 15.1 Terminology glossary first

Before any query, build the glossary:
- **INN** (International Nonproprietary Name) — e.g., trastuzumab deruxtecan
- **Brand** — Enhertu
- **Development code** — DS-8201, DS-8201a, T-DXd
- **Target** — HER2 ADC

Queries must use **all** relevant synonyms in OR combination.

### 15.2 Time-bound everything

Pharma moves fast. Every recency-sensitive query carries an explicit date filter (last 12-24 months for pipeline; last 90d for news).

### 15.3 Parallel discovery, serial deep-dive

Phase 2 (discovery) runs many parallel calls — don't wait on each. Phase 3 (deep dive) is serial and deliberate — one primary source at a time, carefully read.

### 15.4 Cache canonical IDs

Once a canonical ID is established (NCT, DOI, 8-K accession, patent #, EPAR URL), reuse it throughout the analysis instead of re-searching.

### 15.5 Respect robots / rate limits

The Fetch tool respects robots.txt. For high-volume needs, batch reads and space them.

---

## 16. Anti-pattern checklist

Avoid:
- ❌ Using Exa for authoritative regulatory documents (go direct to FDA/EMA)
- ❌ Using Tavily for peer-reviewed literature (use PubMed / Paper Search)
- ❌ Accepting a press release as cross-verified (it's one source)
- ❌ Treating analyst consensus as primary fact (it's interpretive)
- ❌ Using social-media signal as confidence-raising (it's at most signal for further check)
- ❌ Skipping the glossary step (misses synonym-only mentions)
- ❌ Omitting date bounds (returns stale results as "current")
- ❌ Reporting single-source claims as triangulated (always flag explicitly)

---

## Cross-reference

For *source inventory* (what exists): `sources-catalog.md`
For *how to combine*: `triangulation.md`
For *task-specific flow*: `task-*.md`
