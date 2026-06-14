# pharmaintel — T1: Company Deep-Dive Playbook

## Scope

Full commercial-regulatory profile of a listed pharma / biotech (Big Pharma or small/mid-cap). For private companies, see §Private-Company Adaptation.

## Deliverable structure

```
# [Company Name] — Deep-Dive Profile

## 0. Snapshot
  - Ticker, market cap band, HQ, CEO, employee count
  - Therapeutic focus + modality mix

## 1. Financial foundation
  - Latest FY revenue + trend (3yr CAGR)
  - Cash position + burn rate + runway (biotech) or dividend/FCF (Big Pharma)
  - Segment / franchise breakdown

## 2. Revenue drivers
  - Top 3–5 marketed products with revenue, growth, LOE (loss of exclusivity) horizon
  - Geographic split (if disclosed)

## 3. Pipeline
  - Phase 3 assets (most near-term catalysts)
  - Phase 2 assets (next wave)
  - Early-stage platform (IND / Phase 1, modality focus)

## 4. Regulatory standing
  - Recent approvals (last 24mo)
  - Pending submissions / PDUFA / CHMP opinions
  - Any CRLs, warnings, or referral procedures

## 5. Business development
  - Major deals (last 36mo) — acquisitions, in-licensing, out-licensing
  - Partnership architecture (discovery collaborations, option deals)

## 6. IP position
  - Loss-of-exclusivity calendar for top products
  - Paragraph IV / biosimilar challenges active
  - Major patent litigation

## 7. Leadership & governance
  - CEO + key R&D leadership tenure
  - Recent turnover signals

## 8. Limitations & gaps
  - Standard free-tier gaps (per sources-catalog.md §12)
  - Company-specific gaps (e.g., private subsidiary not disclosed)
```

---

## Phase 2 — Discovery (parallel MCP sweep)

Launch in parallel:

1. **Tavily** (news, last 90d, advanced): `"<company> FDA approval OR pipeline OR acquisition OR earnings"`
2. **Tavily** (finance, last 30d): `"<ticker> earnings guidance"`
3. **Exa** (category=company): `"<company> pipeline"`
4. **Clinical Trials MCP**: `sponsor=<company> AND (PHASE2 OR PHASE3) AND status IN (RECRUITING, ACTIVE_NOT_RECRUITING, COMPLETED)`
5. **SEC EDGAR full-text (via Fetch)**: `q=<company> forms=8-K dateRange=last 180 days`
6. **Paper Search** (if scientific credentialing needed): `"<company> [lead asset INN]"`

## Phase 3 — Deep-dive (primary sources)

### 3.1 Financial foundation

1. Fetch latest **10-K** from SEC EDGAR (CIK lookup first)
   - Read §Risk Factors (reveals management's own view of pipeline risk, LOE exposure)
   - Read §MD&A → Segment / Product disclosures (revenue granularity)
   - Read §Consolidated Statements of Operations (P&L)
2. Fetch latest **10-Q** (more current)
3. Fetch most recent **earnings call transcript** (Seeking Alpha free tier or Fool.com)
4. Fetch **latest investor presentation** from IR site (under "Events" or "Presentations")

Cross-check:
- 10-K product revenue ↔ earnings-call Q&A on same products (look for directional alignment)
- Cash / runway explicitly stated in 10-Q balance sheet + MD&A

### 3.2 Pipeline

1. Fetch **IR pipeline page** (authoritative internal view of assets)
2. Fetch latest **R&D Day deck** (usually annual; richer than pipeline page)
3. Query **Clinical Trials MCP** for all active sponsor-name trials (cross-check against IR)
4. Cross-check for *ghosted* assets: on IR page but no active trial in registry → likely quietly deprioritised
5. Fetch **10-K §Pipeline** section (annual rollup, slightly less current than IR)

### 3.3 Regulatory standing

1. For each marketed product: FDA Drugs@FDA + DailyMed SPL + EMA EPAR
2. For pending: 8-K search for "FDA" or "PDUFA" or "CHMP" in last 24mo
3. For CRLs: SEC EDGAR 8-K search for "Complete Response Letter" in company's filings
4. For warnings: FDA Warning Letters search for company name
5. For EMA referrals: ema.europa.eu referral search

### 3.4 Business development

1. SEC EDGAR full-text: `q=<company> AND ("acquisition" OR "license")` forms=8-K,S-4,DEFM14A (last 36 months)
2. For each identified deal: retrieve the 8-K, read the Exhibit (often a form of deal summary), and — if stock deal — read the S-4 for detailed valuation
3. Industry-media layer (Tavily domain-scoped): Endpoints + FiercePharma + BioPharma Dive for commentary

### 3.5 IP position

1. For top 3 products: Orange Book patent listing + Purple Book (if biologic)
2. For biosimilar threats: Purple Book interchangeability status + Paragraph IV list
3. For active litigation: PTAB IPR search + PACER (if needed, via news proxy)

### 3.6 Leadership

1. 10-K §Directors and Executive Officers
2. DEF 14A (proxy) — compensation + tenure
3. Recent 8-Ks under Item 5.02 (departure / appointment of officers)
4. IR leadership page (public bios)

---

## Phase 4 — Triangulation checkpoints

Apply `triangulation.md §2` templates:
- Clinical readout claims → §2.1
- Regulatory status claims → §2.2
- Deal claims → §2.3
- Sales claims → §2.4
- Pipeline assets → §2.5

## Phase 5 — Report synthesis

Follow `assets/report-template.md`. Every material fact carries the four-part provenance stamp. The §Limitations block surfaces any gaps encountered.

---

## Private-Company Adaptation

For private biotech (pre-IPO), statutory disclosure is absent. Substitute:

- **S-1 / F-1 if recently filed** — if pre-IPO in registration, the S-1 is a goldmine
- **Patent filings (USPTO, EPO)** — reveal platform technology
- **Peer-reviewed publications by founding team** — scientific grounding
- **ClinicalTrials.gov** — any registered trials show the pipeline
- **Press releases** — IR equivalent, single-source
- **CB Insights / Crunchbase free tier** — funding rounds
- **LinkedIn** (manual) — team composition signal

Limitations flag is louder: "Private-company analysis; most claims resting on single source (press release or patent). Confidence defaults to Medium or Low."

---

## Specific Big-Pharma adaptations

For large diversified pharma (Roche, Pfizer, J&J, Novartis, etc.):

- Segment reporting is essential — read the segment footnote carefully
- Top-20 product list probably captures >90% of revenue; no need to enumerate all
- Franchises may span multiple listed products; group by franchise first
- Consumer health / generics may be separately disclosed — state scope
- Vaccines franchise + Rx pharma franchise may be separately disclosed

## Specific small-cap biotech adaptations

For single-asset or platform biotechs:

- Single-asset biotechs: entire valuation rests on the lead asset. Profile depth skews toward asset characterization (see task-asset.md).
- Platform biotechs: revenue is primarily partnership milestones; read MDA carefully for partnership structure.
- Cash runway is a first-order risk — explicit calculation: (cash + equivalents) / (quarterly burn) × 3 = months of runway
- Insider-activity: Form 4 filings reveal management sentiment (note: interpretation only, not fact)
