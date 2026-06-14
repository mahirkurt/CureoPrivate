# pharmaintel — Sponsor Sweep Sub-Protocol (Top-30 Pharma Corporate Sites)

## Scope

For any query where a corporate sponsor is named, implied, or where competitive context requires surveying multiple sponsors, pharmaintel MUST conduct a **systematic sweep of sponsor corporate domains**: pipeline pages, investor relations, press releases, and R&D/pipeline day materials. This sub-protocol codifies that sweep.

**Why this exists (v1.2.0 gap):** MCP connectors (Clinical Trials, PubMed, SEC EDGAR full-text) are powerful but do not replace corporate-site depth. A Roche pipeline page carries HCP-facing asset cards that ClinicalTrials.gov does not (mechanism narrative, key-opinion-leader quotes, competitor context). A Novartis Investor Day deck projects five-year revenue by asset class — data unreachable from FDA/EMA. A Lilly press release can disclose a PDUFA date hours before the 8-K is filed. Skipping corporate domains caps the analysis at roughly two-thirds of available public evidence.

**When to load this sub-protocol (trigger rules):**

1. **Named sponsor in query.** "Analyze Roche," "Pfizer's pipeline," "AstraZeneca Q4 2025" → mandatory load
2. **Named asset with known sponsor.** "Profile T-DXd" → load Daiichi Sankyo + AstraZeneca sweeps
3. **Modality landscape (T3).** "ADC landscape" → sweep top 10 ADC-active sponsors from the Top-30 list
4. **Catalyst watch (T5).** "Upcoming PDUFAs in oncology" → sweep every named sponsor; if broad query, sweep Top-10 by oncology portfolio size
5. **Head-to-head (T6).** "X vs Y" → sweep both X's and Y's sponsors
6. **Deal analysis (T4).** "Acquirer X and Target Y" → sweep both sponsor domains for deal-specific press releases and 8-K cross-references
7. **Company deep-dive (T1).** Always load; this IS a corporate-site-centric task

**Do NOT load for:**
- T7 Regulatory Snapshot (too narrow to justify)
- Pure scientific queries routed to medsearch
- Generic methodology questions

---

## The Top-30 list (by 2024–2025 pharmaceutical revenue, global scope)

This list is the default universe for proactive sponsor sweeps when a query is competitive or landscape-oriented. Rank by revenue is approximate and stabilizes year-over-year; use this as a corporate-site inventory, not a strict ranking.

| # | Sponsor | Primary ticker | HQ country | Pipeline URL | IR URL | Press URL | Notes |
|---|---|---|---|---|---|---|---|
| 1 | **Johnson & Johnson (Janssen)** | NYSE: JNJ | US | jnj.com/innovation/pipeline | investor.jnj.com | jnj.com/media-center/press-releases | Strong onco/immuno/neuro |
| 2 | **Roche Group (incl. Genentech, Chugai)** | SIX: ROG | CH | roche.com/solutions/pipeline | roche.com/investors | roche.com/media | Genentech US + Chugai Japan separate releases |
| 3 | **Pfizer** | NYSE: PFE | US | pfizer.com/science/drug-product-pipeline | investors.pfizer.com | pfizer.com/newsroom/press-releases | Large hemo/vaccine franchise |
| 4 | **AbbVie** | NYSE: ABBV | US | abbvie.com/our-science/pipeline | investors.abbvie.com | news.abbvie.com | Post-Humira immunology + onco build |
| 5 | **Merck & Co (MSD ex-US)** | NYSE: MRK | US | merck.com/research/product-pipeline | investors.merck.com | merck.com/news/news-releases | Keytruda cornerstone |
| 6 | **Novartis** | NYSE: NVS | CH | novartis.com/research-development/novartis-research-pipeline | novartis.com/investors | novartis.com/news | Pure-play biopharma post-Sandoz spin |
| 7 | **AstraZeneca** | NASDAQ: AZN / LSE | UK | astrazeneca.com/our-science/pipeline.html | astrazeneca.com/investor-relations.html | astrazeneca.com/media-centre/press-releases.html | Enhertu with Daiichi Sankyo |
| 8 | **Bristol Myers Squibb** | NYSE: BMY | US | bms.com/researchers-and-partners/in-the-pipeline.html | investors.bms.com | bms.com/media/media-library/news-releases.html | Celgene integration legacy |
| 9 | **Eli Lilly** | NYSE: LLY | US | lilly.com/discovery/pipeline | investor.lilly.com | investor.lilly.com/news-releases | GLP-1 dominance; neuro pipeline |
| 10 | **Sanofi** | NASDAQ: SNY / Euronext | FR | sanofi.com/en/science-and-innovation/research-and-development | sanofi.com/en/investors | sanofi.com/en/media-room/press-releases | Dupixent cornerstone |
| 11 | **GSK** | NYSE: GSK / LSE | UK | gsk.com/en-gb/research-and-development/our-pipeline | gsk.com/en-gb/investors | gsk.com/en-gb/media/press-releases | Onco pivot post-Pfizer CH JV |
| 12 | **Takeda** | NYSE: TAK / TSE: 4502 | JP | takeda.com/what-we-do/rd-pipeline | takeda.com/investors | takeda.com/newsroom/newsreleases | Rare disease + onco |
| 13 | **Bayer (Pharma)** | FWB: BAYN | DE | bayer.com/en/pharma/development-pipeline | bayer.com/en/investors | bayer.com/en/media | Post-Kerendia/Nubeqa onco |
| 14 | **Amgen** | NASDAQ: AMGN | US | amgenpipeline.com | investors.amgen.com | amgen.com/newsroom/press-releases | Horizon acquisition integrated |
| 15 | **Boehringer Ingelheim** | private | DE | boehringer-ingelheim.com/science-innovation/human-health-innovation/pipeline | — (private) | boehringer-ingelheim.com/press-release | Private — rely on press + pipeline pages |
| 16 | **Gilead Sciences** | NASDAQ: GILD | US | gilead.com/science-and-medicine/pipeline | investors.gilead.com | gilead.com/news-and-press/press-room | HIV cornerstone + onco build |
| 17 | **Daiichi Sankyo** | TSE: 4568 | JP | daiichisankyo.com/rd/pipeline | daiichisankyo.com/investors | daiichisankyo.com/media | Enhertu + DXd platform with AZ |
| 18 | **Biogen** | NASDAQ: BIIB | US | biogen.com/science/pipeline.html | investors.biogen.com | investors.biogen.com/news-releases | Neuro-focused post-Leqembi |
| 19 | **Regeneron** | NASDAQ: REGN | US | regeneron.com/pipeline | investor.regeneron.com | investor.regeneron.com/news-releases | Dupixent co-dev with Sanofi; Eylea |
| 20 | **Vertex Pharmaceuticals** | NASDAQ: VRTX | US | vrtx.com/our-science/pipeline | investors.vrtx.com | news.vrtx.com | CF cornerstone; pain (Journavx) expansion |
| 21 | **Eisai** | TSE: 4523 | JP | eisai.com/research/products/pipeline.html | eisai.com/ir/ | eisai.com/news/enews | Alzheimer (Leqembi) with Biogen |
| 22 | **Moderna** | NASDAQ: MRNA | US | modernatx.com/research/pipeline | investors.modernatx.com | investors.modernatx.com/news-releases | mRNA platform |
| 23 | **BioNTech** | NASDAQ: BNTX | DE | biontech.com/int/en/home/pipeline-and-products/pipeline.html | investors.biontech.de | biontech.com/int/en/home/media/press-releases | Post-COVID onco pivot |
| 24 | **Otsuka Holdings** | TSE: 4578 | JP | otsuka.co.jp/en/rd/pipeline/ | otsuka.co.jp/en/ir/ | otsuka.co.jp/en/news/ | CNS cornerstone |
| 25 | **Astellas** | TSE: 4503 | JP | astellas.com/en/worldwide/rd/pipeline | astellas.com/en/investors | astellas.com/en/news | Xtandi; Fezolinetant |
| 26 | **Servier** | private | FR | servier.com/en/innovation/research-pipeline | — (private) | servier.com/en/news | Private; onco-focused |
| 27 | **Chugai Pharmaceutical** | TSE: 4519 | JP | chugai-pharm.co.jp/english/profile/rd/pipeline.html | chugai-pharm.co.jp/english/ir/ | chugai-pharm.co.jp/english/news/ | Roche subsidiary, Japan-primary |
| 28 | **Incyte** | NASDAQ: INCY | US | incyte.com/who-we-are/pipeline | investor.incyte.com | investor.incyte.com/press-releases | Jakafi; onco + derm |
| 29 | **Alnylam** | NASDAQ: ALNY | US | alnylam.com/our-science/pipeline | investors.alnylam.com | investors.alnylam.com/press-releases | RNAi platform; ATTR-CM |
| 30 | **BeOne Medicines (ex-BeiGene)** | NASDAQ: ONC | US/CN | beonemedicines.com/pipeline | beonemedicines.com/investors | beonemedicines.com/news | Brukinsa; sonrotoclax |

**Notes on list curation:**
- Private companies (Boehringer, Servier) have no SEC filings; rely on press + pipeline pages + any voluntary annual report
- Japanese sponsors: load `sub-protocol-pmda.md` in parallel when substantive Japan-layer analysis is needed
- Chinese large caps (Jiangsu Hengrui, Sino Biopharm, InnoVent, Junshi) intentionally omitted from the default Top-30 because disclosure depth is inconsistent for free-tier analysis; load on a per-query basis when specifically invoked
- List is a reasonable snapshot for 2025–2026; it will drift. If a query invokes a company that moved into the Top-30 (e.g., post-merger), treat that company as in-scope without requiring list update

---

## The sweep workflow

### Step S1 — Identify sweep set

Given a query, identify which sponsors are in-scope:
- **Named:** sponsors explicitly mentioned
- **Asset-implicated:** sponsors owning/co-owning any asset named
- **Competitor-implicated:** sponsors with Phase 2+ assets in the same mechanism/indication (use Clinical Trials MCP `search_by_sponsor` + `search_trials` with intervention class)
- **Deal-implicated:** sponsors party to a named deal

If the query is a modality landscape (T3) with no specific sponsor, default to "all sponsors from the Top-30 with Phase 2+ activity in the modality" — typically 5–15 sponsors.

### Step S2 — Three-target fetch per sponsor

For each sponsor in the sweep set, fetch three canonical targets in parallel:

1. **Pipeline page** — for current asset inventory + phase transitions + indication scope
2. **Press releases (filtered by topic/date)** — for recent catalysts, data readouts, regulatory events
3. **Investor relations page** — for latest quarterly earnings, investor day decks, guidance updates

Typical fetch pattern:

```
web_fetch(url="<sponsor>/pipeline-page", text_content_token_limit=6000)
web_fetch(url="<sponsor>/press-releases?topic=<query-relevant>", text_content_token_limit=6000)
web_fetch(url="<sponsor>/investors/latest-earnings-or-pipeline-day", text_content_token_limit=6000)
```

**Press release filtering heuristic:** when a sponsor's press releases page lists 100+ items, filter by (a) date window matching the query's time scope, (b) keyword match on the asset/indication. If neither filter is available server-side, fetch the index and extract matching entries inline.

### Step S3 — Extract into a structured sponsor card

For each sponsor, populate:

```markdown
#### [Sponsor name] ([ticker])

**Latest pipeline (data cutoff [YYYY-MM-DD]):**
- [Asset 1]: Phase X in [indication]; key readout [timing]
- [Asset 2]: Phase X in [indication]; key readout [timing]
- ...

**Relevant press releases (filtered by query scope):**
- [YYYY-MM-DD]: [headline]. [1-line summary]. [URL]
- [YYYY-MM-DD]: [headline]. [1-line summary]. [URL]

**Latest IR signal:**
- Earnings / guidance update: [quarter + brief point]
- Investor Day: [date + key slide takeaways if within 12 months]
- [URL]

**Forward catalysts within query window:**
- [Date / quarter]: [event type + asset]
- ...

**Stamp:** Sponsor-primary sources; confidence High for in-market status, Medium-to-High for forward guidance.
```

### Step S4 — Cross-check with MCP primary layer

For every asset-specific claim extracted in S3, verify against MCP primary sources before admitting to High confidence:

- Phase status / enrollment → Clinical Trials MCP
- Approval date / label → fda.gov or EMA EPAR (Fetch)
- PDUFA date → sponsor 8-K via SEC EDGAR (if US-listed)
- Peer-reviewed pivotal readout → PubMed / Paper Search MCP

A claim that appears only in the sponsor's press release but is contradicted by the primary regulatory/statutory/peer-reviewed source must be flagged (triangulation.md §3 hierarchy).

### Step S5 — Integrate into report

Sponsor cards from S3 do NOT appear verbatim in the final report. They serve as an evidence inventory. The final report's prose narrative weaves sponsor findings into the task-specific deliverable template (T1 company profile, T2 asset profile, etc.), with sponsor-site URLs cited in the §References section.

**What DOES appear in the final report:**
- Specific numerical claims + regulatory dates + deal terms extracted from sponsor sites, each inline-cited
- A §Sponsor sweep disclosure block (see below)

---

## The Sponsor Sweep Disclosure Block

Every report invoking this sub-protocol includes this block near the Provenance Disclosure:

```markdown
### Sponsor Sweep Disclosure

**Sweep executed:** [YYYY-MM-DD]
**Sponsors covered:**
- [Name] ([ticker]): pipeline ✓ · press ✓ · IR ✓
- [Name] ([ticker]): pipeline ✓ · press ✓ · IR [partial — subscription required]
- [Name] ([ticker]): pipeline ✓ · press ✓ · IR ✗ (private company, no IR page)

**Sponsors NOT covered (justification):**
- [Name]: [reason — e.g., not in Top-30; private Chinese biotech with no English site]

**Cross-check layer:** MCP primary (Clinical Trials / PubMed / SEC EDGAR / fda.gov) executed per triangulation.md §2 for all asset-specific claims.
```

This block forces the author (Claude) to explicitly enumerate which sponsors were and were not swept, and why. A reader instantly knows the coverage boundary.

---

## Confidence caps for sponsor-primary claims

Per triangulation.md §6.1 and this sub-protocol:

| Claim type | Max confidence from sponsor-only source |
|---|---|
| In-market status (launched, reimbursed, available) | High |
| Completed trial primary endpoint result | Medium (High requires peer-reviewed publication confirmation) |
| Forward-looking PDUFA / readout guidance | Medium (High requires SEC 8-K or official regulatory calendar) |
| Revenue / sales by asset | High (statutory filing — 10-K/10-Q Product Revenue table) |
| Deal terms (upfronts, milestones) | High when in 8-K; Medium when in press release only |
| Pipeline Phase transition | Medium (High requires Clinical Trials MCP registry confirmation) |
| Label wording / indication scope | Medium (High requires FDA/EMA document) |
| Investor day revenue projection | Low-to-Medium (forward-looking, sponsor optimism bias) |

Sponsor press releases are NEVER the only source for a pivotal-trial effect size or p-value; these require peer-reviewed confirmation per triangulation.md §6.1.

---

## Known failure modes

1. **Sponsor site paywall / login:** Biogen's IR page occasionally requires investor login for detailed webcasts. Fetch what's public; note the wall explicitly.
2. **Pipeline page staleness:** Some sponsors update quarterly, others only post-earnings. Check the "last updated" footer — if absent, assume the content matches the most recent earnings release.
3. **Sponsor optimism bias:** Press release phrasing ("positive topline results") can overstate; always cross-check against primary data source when available. Flag phrasing mismatches in the report.
4. **Private company opacity:** Boehringer, Servier, and some Chinese large caps have no IR page. Rely on press releases + any voluntary annual publications + FDA/EMA documents + peer-reviewed publications.
5. **Co-development asset attribution:** Assets like Enhertu (Daiichi Sankyo + AstraZeneca) appear on both sponsors' sites with partially different framing. Fetch both; reconcile.
6. **Archive depth:** Press release archives can truncate beyond ~5 years on some sponsor sites. For historical deep-dive, SEC EDGAR full-text + archive.org supplements.
7. **Chinese/Japanese HQ English-site dilution:** English versions of Takeda, Chugai, Daiichi, Otsuka pipeline pages may lag Japanese-primary pages by weeks. For Japan-critical analysis, combine with `sub-protocol-pmda.md`.

---

## Cross-reference

- `sources-catalog.md §Industry Sources` — extends the corporate-site catalog (not yet comprehensive for all 30; this sub-protocol is authoritative)
- `triangulation.md §6.1` — peer-review precision rule caps pivotal numeric claims from sponsor-only sources
- `task-company.md` — T1 Company Deep-Dive uses sponsor sweep as its primary discovery mechanism
- `task-asset.md §Regulatory history + Commercial trajectory` — single-sponsor or dual-sponsor subset
- `task-modality.md` — 5–15 sponsor sweep is the default discovery pattern
- `task-catalyst.md §PDUFA lookup chain` — sponsor 8-K + IR + press as step 1–3 of the chain
- `task-deal.md` — acquirer + target dual sweep

**Invocation in SKILL.md Step 1b / 1c:** When trigger rules above fire, load this sub-protocol in parallel with the task-specific reference. Execute sweep during Phase 2 (Discovery) alongside MCP parallel activation.
