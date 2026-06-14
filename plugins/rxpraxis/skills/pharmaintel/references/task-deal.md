# pharmaintel — T4: Deal / M&A Dissection Playbook

## Scope

Analysis of a specific transaction: acquisition, merger, licensing deal, option-to-acquire, research collaboration. Focus on: terms, strategic rationale, valuation sanity check, comparable deals, antitrust / regulatory considerations, post-close signal monitoring.

## Deliverable structure

```
# [Acquirer] + [Target] — Deal Analysis

## 0. Executive summary
  - Transaction type, headline value, structure (cash/stock/earnout)
  - Announcement date, expected close
  - Status (announced / closed / terminated)

## 1. Counterparties
  - Acquirer: scale, rationale, recent deal pattern
  - Target: profile snapshot (see task-company.md if unprofiled)

## 2. Transaction structure
  - Consideration mix (cash / stock / CVR / milestones)
  - Upfront payment
  - Contingent value rights (CVR) structure if any
  - Closing conditions (regulatory, shareholder, financing)

## 3. Strategic rationale
  - Acquirer stated rationale (from press release + investor deck)
  - Target stated rationale (board recommendation, DEF 14A)
  - Fit with acquirer's therapeutic / modality focus
  - Pipeline additions — what assets are acquired

## 4. Valuation
  - Price per share vs target's prior close (premium %)
  - Implied enterprise value
  - Price / revenue or price / NPV inference (from target's pipeline)
  - Fairness opinion excerpt (from DEF 14A or S-4)

## 5. Comparable deals
  - 3-5 recent comparables in the same modality / TA
  - Premium + multiples comparison
  - Notable deviations

## 6. Antitrust / regulatory
  - FTC / EC / CMA expected review
  - Historical precedent for the overlap (if any)
  - Divestiture expectations

## 7. Post-close monitoring (if closed)
  - Initial integration signals
  - Pipeline carryforward
  - Retention / turnover of key target personnel

## 8. Risks & open questions
  - Execution risks
  - Pipeline risks inherited
  - Market dynamics

## 9. Limitations & gaps
```

---

## Phase 2 — Discovery

1. **SEC EDGAR 8-K** search: acquirer CIK, last 180 days, keyword = target name
2. **SEC EDGAR 8-K** search: target CIK, last 180 days
3. **SEC EDGAR S-4** (if stock consideration): search acquirer CIK
4. **SEC EDGAR DEFM14A** (if merger proxy): search target CIK
5. **Tavily** (news, last 90d, domain-scoped to Endpoints, FiercePharma, BioPharma Dive, Reuters)
6. **Company IR** press release for both parties (usually day-of announcement)
7. **Exa** for analyst commentary: `"<acquirer> <target> acquisition analysis"`
8. **ClinicalTrials.gov MCP** for target's registered trials (defines the acquired pipeline)

---

## Phase 3 — Deep-dive

### 3.1 Transaction structure (the crucial primary document layer)

1. **Initial 8-K (announcement)** — filed by both parties usually within 1-4 business days
   - Exhibit 2.1 typically contains the merger agreement
   - Exhibit 99.1 typically contains joint press release
2. **S-4 (if stock or part-stock)** — registration statement for acquirer's shares; contains:
   - Deal rationale narrative
   - Background of the merger (timeline of negotiations)
   - Fairness opinion from banks
   - Projections (both parties'; filed under "Certain Unaudited Prospective Financial Information")
3. **DEF 14A / DEFM14A (target proxy)** — recommendation to target shareholders; contains:
   - Board's rationale
   - Fairness opinion (can differ from acquirer's)
   - Alternative offers considered
4. **Tender offer documents** (if tender structure): SC TO-T + SC 14D9

Extract:
- Upfront cash per share
- Stock exchange ratio (if applicable)
- CVR structure (milestones + per-share amounts)
- Breakup fee (reveals commitment level)
- Non-solicit / go-shop provisions
- Regulatory termination date

### 3.2 Strategic rationale

1. **Joint press release (8-K Exhibit 99.1)** — acquirer's narrative
2. **Investor call following announcement** — usually same day or next morning; webcast on IR site
3. **Investor deck accompanying announcement** — filed as 8-K exhibit
4. **Acquirer's most recent 10-K MD&A** — contextualises this deal within their strategy
5. **Target's board recommendation (in DEFM14A)** — target's narrative

Note the **what's-being-acquired granularity**: the deal might be for one asset (column in 8-K about "rights to [asset]"), a platform, or a whole company.

### 3.3 Valuation

1. **Premium calculation:**
   - Per-share consideration ÷ last unaffected trading day close
   - "Unaffected" = day before first rumor / disclosure (read the S-4 "Background" section)
   - Alternative benchmarks: 30-day VWAP, 52-week high
2. **Enterprise value:** shares × price + debt − cash (from target's latest 10-Q)
3. **Multiples (if product revenue exists):** EV / sales LTM (last twelve months)
4. **Pipeline NPV inference:** for pre-revenue biotech, price implies acquirer's pipeline valuation
5. **Fairness opinion** — S-4 / DEFM14A includes banker analyses (DCF, comparable companies, precedent transactions). Extract ranges but don't overweight (interested-party analysis).

### 3.4 Comparable deals

Free-tier approach (no DealForma, no Cortellis Deals):

1. **SEC EDGAR full-text search** for similar transactions:
   - `q="<modality or TA> acquisition" forms=8-K,S-4 dateRange=<last 3 years>`
2. **Endpoints / FiercePharma / BioPharma Dive** "Deal Tracker" or similar features (free)
3. **Evaluate Vantage free articles** covering major deals — often include comparable-deal context
4. **Reuters Health** M&A coverage

For each comparable, extract headline value + structure; build a summary table.

### 3.5 Antitrust / regulatory

1. **FTC filings / statements** — ftc.gov (free)
2. **European Commission competition case search** — ec.europa.eu/competition (free)
3. **UK CMA**  — gov.uk/cma-cases (free)
4. **Historical overlap precedent** — if acquirer already has an approved asset in the same MoA class
5. **HSR filing** referenced in 8-K (expected antitrust waiting period)
6. **Divestiture signals** — if the acquirer announces planned divestitures in press release
7. **IP overlap** — Orange Book for both parties' relevant products

### 3.6 Post-close monitoring (if closed)

1. Post-close 10-K / 10-Q for integration disclosures
2. Target-as-subsidiary segment (if separately disclosed)
3. Form 4 filings for target executives who rolled forward (insider activity signal)
4. Industry media coverage of retention / departures
5. ClinicalTrials.gov sponsor update for target's trials (sponsorship may migrate)

---

## Phase 4 — Triangulation

- **Deal terms** → §2.3 (8-K + S-4 / DEFM14A + press release + earnings Q&A)
- **Premium** → per-share calculation confirmed from multiple closes (ticker data)
- **Strategic rationale** → company narrative + independent analyst/media interpretation

## Phase 5 — Report

Per `assets/report-template.md`, deal version. Always include a "status as of [date]" line — deals can break, be renegotiated, or face surprise antitrust action.

---

## Edge cases

### Option-to-acquire deals

Common for early-stage biotech acquirer strategies. Structure:
- Upfront collaboration payment
- Option exercise payment (strike when milestone met)
- Post-option milestone / royalty / equity

Read the 8-K Exhibit collaboration agreement carefully; economic terms can be layered.

### CVR (contingent value right) deals

CVRs shift risk to target's legacy shareholders:
- Milestone-triggered cash payments
- Tradeable vs non-tradeable
- Expiration date
- Historical CVR payment success rate is poor — flag as a risk

### License + equity deals

E.g., Company A licenses asset from Company B + takes equity stake:
- License terms (upfront, milestones, royalties)
- Equity investment (size, pricing)
- Board representation (if any)
- Lock-up on equity

### Private-company target

Pre-IPO target = limited disclosure:
- 8-K discloses deal terms (if acquirer is public)
- Target's financials limited to what acquirer chooses to reveal
- Pipeline detail constrained to what target has published / press-released

### Terminated deals

If a deal terminates pre-close:
- 8-K filing Item 1.02 (termination)
- Breakup fee payment disclosure
- Reason for termination (antitrust, material adverse effect, superior proposal)
- Stock reaction analysis from subsequent close data

### Chinese target

NMPA-related deals often lack English primary documents:
- Explicitly flag language gap in §Limitations
- Rely on Reuters / BioPharma Dive English coverage + 8-K from US acquirer
