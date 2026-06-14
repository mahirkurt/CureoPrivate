# pharmaintel — Sources Catalog (Free-Tier)

This catalogue is the **canonical source universe** for pharmaintel. Every source listed is either fully open (T0) or free-tier accessible (T1–T2). Enterprise/paid sources are explicitly marked **[INACCESSIBLE]** for transparency — pharmaintel never attempts to use them and always flags the resulting gap in reports.

---

## 1. Regulatory (Primary Authority Layer)

### 1.1 US FDA

| Source | URL | Fetch method | Content |
|--------|-----|-------------|---------|
| **Drugs@FDA** | `accessdata.fda.gov/scripts/cder/daf` | Fetch (browse or direct ID) | All approved drugs; labels; approval letters; Medical Reviews; Clinical Pharmacology Reviews |
| **Orange Book** | `fda.gov/drugs/drug-approvals-and-databases/orange-book` | Fetch | NDA patents + therapeutic equivalence + exclusivity |
| **Purple Book** | `purplebooksearch.fda.gov` | Fetch | BLA (biologics) + biosimilar/interchangeable designations |
| **FAERS Public Dashboard** | `fis.fda.gov/extensions/FPD-QDE-FAERS` | Fetch | Adverse event reports; signal detection |
| **DailyMed** | `dailymed.nlm.nih.gov` | Fetch | Current structured product labels (SPLs); RxNorm mapping |
| **FDA Calendar (AdComm)** | `fda.gov/advisory-committees/advisory-committee-calendar` | Fetch | AdComm meetings + briefing documents |
| **FDA Press Announcements** | `fda.gov/news-events/fda-newsroom/press-announcements` | Fetch / RSS | Approvals, warnings, safety communications |
| **Warning Letters** | `fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters` | Fetch | GMP + clinical inspection violations |
| **Form 483 observations** | FDA FOIA reading room | Fetch (redacted) | Facility-specific GMP findings |
| **Drug Shortages** | `accessdata.fda.gov/scripts/drugshortages` | Fetch | Current shortages + resolution dates |
| **FDA Guidance Documents** | `fda.gov/regulatory-information/search-fda-guidance-documents` | Fetch | Regulatory expectations; therapeutic area guidance |
| **Paragraph IV Certifications** | `fda.gov/drugs/abbreviated-new-drug-application-anda/paragraph-iv-patent-certifications` | Fetch | Generic challenges to NDA patents |

**Canonical FDA fetch pattern (drug label):**
```
https://www.accessdata.fda.gov/drugsatfda_docs/label/[YEAR]/[APPNO]lbl.pdf
```
Medical Reviews typically released 3-6 months post-approval at a similar path (`...[APPNO]_med_review.pdf`).

### 1.2 EU EMA

| Source | URL | Content |
|--------|-----|---------|
| **EPAR search** | `ema.europa.eu/en/medicines` | Full scientific assessment per centrally-approved product |
| **CHMP Meeting Highlights** | `ema.europa.eu/en/committees/chmp/chmp-agendas-minutes-highlights` | Monthly positive/negative/withdrawn opinions |
| **PRIME scheme** | `ema.europa.eu/en/human-regulatory/research-development/prime-priority-medicines` | EU equivalent of FDA Breakthrough |
| **Orphan designations** | `ec.europa.eu/health/documents/community-register` | Community Register of orphan medicinal products |
| **EudraVigilance (public)** | `adrreports.eu` | Limited public view of EU adverse event database |
| **CTIS (Clinical Trial Information System)** | `euclinicaltrials.eu` | Mandatory EU trials registry since Jan 2023 (replaced EU-CTR) |
| **Referrals** | `ema.europa.eu/en/human-regulatory/post-authorisation/referral-procedures` | Safety/benefit-risk re-evaluations |

### 1.3 Other regulators (English-language accessible)

| Authority | Region | Key free resource |
|-----------|--------|-------------------|
| **MHRA** | UK | ILAP pathway decisions; post-Brexit independent approvals at `gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency` |
| **Health Canada** | Canada | NOC database, Drug Product Database at `hc-sc.gc.ca` |
| **TGA** | Australia | ARTG at `tga.gov.au` |
| **Swissmedic** | Switzerland | English summaries at `swissmedic.ch` |
| **PMDA** | Japan | Limited English summaries; package inserts often Japanese — **flag as gap** |
| **NMPA** | China | CDE approvals; Chinese-language primary — **flag as gap** |
| **ANVISA** | Brazil | `gov.br/anvisa` |
| **WHO Prequalification** | Global/LMIC | `extranet.who.int/prequal` |
| **ICH** | Global | `ich.org` — E6/E8/E9/E9(R1)/M13/Q8-Q12 guidelines |

### 1.4 Clinical trial registries

| Registry | Scope | Access |
|----------|-------|--------|
| **ClinicalTrials.gov** | Global, NIH-hosted; largest | Clinical Trials MCP + web fetch |
| **WHO ICTRP** | Meta-search of 17 primary registries | `trialsearch.who.int` |
| **CTIS** | EU mandatory since 2023 | `euclinicaltrials.eu` |
| **ISRCTN** | UK-based, global acceptance | `isrctn.com` |
| **ChiCTR** | China (Chinese-language primary) | `chictr.org.cn/en` |
| **JapicCTI** | Japan | `clinicaltrials.jp` |
| **ANZCTR** | Australia/New Zealand | `anzctr.org.au` |
| **CTRI** | India | `ctri.nic.in` |
| **REBEC** | Brazil | `ensaiosclinicos.gov.br` |

---

## 2. Financial Filings & IR (Commercial Layer)

### 2.1 US — SEC EDGAR (T0, fully open)

| Form | Content |
|------|---------|
| **10-K** | Annual comprehensive report; risk factors, pipeline in MD&A, segment disclosures |
| **10-Q** | Quarterly financials + pipeline update |
| **8-K** | Material event disclosure — **the critical category** for catalyst tracking (clinical data, licensing, CRL, AdComm outcomes) |
| **S-1 / F-1** | IPO prospectus — richest first detailed disclosure for private biotechs |
| **DEF 14A (Proxy)** | Executive comp, CEO milestone structure |
| **S-4** | M&A registration statement — full deal terms |
| **Form 4** | Insider trading real-time |
| **13D / 13G** | Activist + >5% shareholder disclosures |

**EDGAR full-text search:**
```
https://efts.sec.gov/LATEST/search-index?q=<query>&forms=8-K&dateRange=custom&startdt=<YYYY-MM-DD>&enddt=<YYYY-MM-DD>
```

**Filing fetch pattern:**
```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<CIK>&type=<form>&dateb=&owner=include&count=40
```

EDGAR provides an RSS feed per CIK per form type — useful for catalyst monitoring.

### 2.2 Non-US filings (free tier)

| Region | Platform | Access |
|--------|----------|--------|
| UK (LSE) | National Storage Mechanism | `data.fca.org.uk/nsm` + RNS announcements |
| Japan (TSE) | EDINET | `disclosure.edinet-fsa.go.jp` |
| Hong Kong (HKEX) | HKEXnews | `hkexnews.hk` |
| Switzerland (SIX) | SIX Exchange Regulation | `ser-ag.com` |
| EU | OAM (country-specific) | Varies |
| China (SSE/SZSE) | CNINFO | `cninfo.com.cn` — **Chinese-language, flag as gap** |

### 2.3 Investor Relations & earnings

- **Company IR portals:** typically `investors.<company>.com` — webcast archives, presentations, SEC link-through
- **Earnings call transcripts:**
  - Seeking Alpha free tier (most transcripts)
  - Fool.com / Motley Fool transcript section
  - Company IR (often as 8-K exhibit)
- **Major conferences:**
  - JPMorgan Healthcare Conference (January) — **the** biotech presentation event; webcasts on company IR
  - Analyst Days / R&D Days — webcast + slides on company IR

---

## 3. Scientific Literature (via MCPs)

### 3.1 Peer-reviewed (MCP-accessible)

| Platform | MCP | Use case |
|----------|-----|----------|
| **PubMed / MEDLINE** | PubMed MCP | MeSH-indexed biomedical literature; 37M+ records |
| **Semantic Scholar** | Scholar Gateway MCP | Semantic search + influential citation metric |
| **CrossRef** | Paper Search MCP | DOI resolution + metadata |
| **Google Scholar** | Paper Search MCP | Broadest coverage (quality variable) |
| **Cochrane Library** | Web fetch | Systematic reviews + CENTRAL trial DB (partially open) |
| **PROSPERO** | Web fetch | Prospective systematic review register |

### 3.2 Preprints (MCP-accessible)

| Server | MCP | Focus |
|--------|-----|-------|
| **bioRxiv** | bioRxiv MCP + Paper Search | Biology preprints — early mechanism signals |
| **medRxiv** | bioRxiv MCP + Paper Search | Medical preprints — clinical early signals |
| **ChemRxiv** | Web fetch | Chemistry + drug discovery |
| **Research Square** | Web fetch | Multidisciplinary, Nature-integrated |
| **SSRN (Health Economics)** | Web fetch | HEOR preprints |
| **arXiv (q-bio)** | Paper Search | Computational biology, AI/ML drug discovery |

### 3.3 High-impact journals (accessible abstracts; full-text sometimes open)

NEJM · Lancet family · JAMA family · BMJ (BMJ Open is full open) · Nature family (Nature Medicine, Nature Reviews Drug Discovery) · Cell family · Science (+ Science Translational Medicine) · Blood · JCO · European Heart Journal · Annals of Oncology · Haematologica · Clinical Cancer Research.

### 3.4 Evidence synthesis (MCP)

- **Consensus MCP** — yes/no/mixed evidence verdict on clinical questions
- **Cochrane Library (web)** — gold-standard systematic reviews + CENTRAL

---

## 4. Patent & IP (Free-Tier)

| Source | URL | Note |
|--------|-----|------|
| **USPTO Patent Public Search** | `ppubs.uspto.gov/pubwebapp` | US patents + published applications |
| **EPO Espacenet** | `worldwide.espacenet.com` | European + global multi-office |
| **WIPO PATENTSCOPE** | `patentscope.wipo.int` | PCT applications |
| **Google Patents** | `patents.google.com` | Free, multi-office, strong Boolean + semantic |
| **Lens.org** | `lens.org` | Patent + scholarly linked, fully free |
| **FDA Orange Book** | (see §1.1) | NDA patents + exclusivity |
| **FDA Purple Book** | (see §1.1) | BLA patents + biosimilar interchangeability |
| **PTAB** | `ptab.uspto.gov` | IPR (Inter Partes Review) filings |
| **EPO Register** | `register.epo.org` | European opposition registry |

**[INACCESSIBLE]:** Patsnap, Derwent Innovation, PatBase — enterprise only. Gap impact: advanced analytics (family clustering, semantic clustering at scale) unavailable; manual Boolean on Lens/Google Patents compensates for most CI needs.

---

## 5. Health Technology Assessment (HTA) & Payer

### 5.1 HTA agencies (public reports — T0)

| Agency | Country | Output accessed |
|--------|---------|-----------------|
| **NICE** | UK | TA (Technology Appraisal), HST, cost-effectiveness | `nice.org.uk` |
| **SMC** | Scotland | Scottish appraisals | `scottishmedicines.org.uk` |
| **AWMSG** | Wales | Welsh-specific | `awmsg.nhs.wales` |
| **CADTH** | Canada (federal) | Reimbursement Reviews | `cadth.ca` |
| **INESSS** | Quebec | French-language primary | `inesss.qc.ca` |
| **PBAC** | Australia | PBS listing recommendations | `pbs.gov.au/info/industry/listing/elements/pbac-meetings` |
| **PHARMAC** | New Zealand | | `pharmac.govt.nz` |
| **ICER** | US (non-governmental) | Evidence Reports, value-based benchmark | `icer.org` |
| **G-BA / IQWiG** | Germany | AMNOG early benefit assessment (English summaries) | `g-ba.de/english`, `iqwig.de/en` |
| **HAS** | France | Transparency Commission opinions (French primary) | `has-sante.fr` |
| **AIFA** | Italy | Innovativeness rating, prezzo | `aifa.gov.it` |
| **TLV** | Sweden | Dental/Pharmaceutical Benefits | `tlv.se` |
| **ZIN** | Netherlands | Zorginstituut | `zorginstituutnederland.nl` |

### 5.2 US payer

- **CMS National Coverage Determinations + Local Coverage Determinations** — `cms.gov`
- **Medicare Part B/D dashboards** — `data.cms.gov`
- **IRA negotiation lists** — CMS annual release
- **340B Program data** — `hrsa.gov/opa`

### 5.3 Professional methodology

- **ISPOR** — `ispor.org` Good Practices Reports (open)
- **EUnetHTA / JCA** — `hta.lv` (EU-wide HTA coordination, mandatory for oncology + ATMPs from 2025)

---

## 6. Pharmacovigilance (Free-Tier)

| Source | Region | Access |
|--------|--------|--------|
| **FAERS Dashboard** | US | `fis.fda.gov` — fully public |
| **EudraVigilance (adrreports.eu)** | EU | Public — limited |
| **VigiAccess (WHO UMC VigiBase public view)** | Global | `vigiaccess.org` |
| **JADER (PMDA)** | Japan | Japanese-language primary |
| **Yellow Card (UK)** | UK | `yellowcard.mhra.gov.uk` |
| **Canada Vigilance** | Canada | Health Canada database |
| **OpenVigil** | FAERS-based disproportionality | `openvigil.pharmacology.uni-kiel.de` |

**[INACCESSIBLE]:** PharmaPendium (Elsevier), Vigilyze (Uppsala) — enterprise.

---

## 7. Real-World Evidence & Epidemiology (Free-Tier)

### 7.1 Open epidemiology

| Source | Coverage |
|--------|----------|
| **GBD (Global Burden of Disease, IHME)** | `ghdx.healthdata.org` — disease burden, DALY, mortality |
| **WHO GHO** | `who.int/data/gho` — global health observatory |
| **SEER (NCI)** | `seer.cancer.gov` — US cancer epidemiology |
| **CDC WONDER** | `wonder.cdc.gov` — mortality/birth/infectious |
| **ECDC** | `ecdc.europa.eu` — EU infectious + AMR |
| **OECD Health Statistics** | `oecd.org/health/health-data` |
| **Eurostat Health** | `ec.europa.eu/eurostat/web/health` |

### 7.2 Open-methodology RWE

- **OHDSI (Observational Health Data Sciences and Informatics)** — `ohdsi.org`; OMOP Common Data Model; federated network; published papers accessible

**[INACCESSIBLE]:** Aetion, Flatiron, Tempus, TriNetX, Optum, IQVIA E360, Merative Truven — enterprise RWE platforms. Gap impact: proprietary patient-level RWE unavailable; approximate via published RWE studies indexed in PubMed.

---

## 8. Industry Media (Free-Tier — T2)

| Source | Access | Focus |
|--------|--------|-------|
| **FiercePharma** | Ad-supported free | Daily pharma news |
| **FierceBiotech** | Ad-supported free | Daily biotech news + analyses |
| **FierceCRO** | Ad-supported free | Contract research |
| **BioPharma Dive** | Free email + web | Daily news + features |
| **Endpoints News free tier** | Free articles (premium gated) | Clinical readouts, deal flow |
| **STAT News free** | Free articles (STAT+ gated) | Biotech + policy journalism |
| **Evaluate Vantage (free)** | `evaluate.com/vantage` — free ad-supported | Analyst-style commentary + charts |
| **BioPharma Catalyst** | `biopharmcatalyst.com` free | PDUFA calendar, catalyst tracker |
| **Reuters Health** | Free articles (paywall some) | Wire service |
| **Axios Vitals / Pro Rata (free)** | Free newsletter | US health policy + deals |
| **PharmaTimes** | Free ad-supported | UK-based industry |
| **PMLive** | Free | European industry |
| **Pharmaceutical Executive** | Free | US commercial pharma |
| **Nature news** | Free ad-supported | Top-tier science + policy |

**[INACCESSIBLE]:** STAT Plus, Endpoints Premium, BioCentury, FirstWord, Scrip, Pink Sheet, In Vivo — subscription. Gap impact: premium deal analysis unavailable; approximate via 8-K + free-tier commentary triangulation.

---

## 9. Conferences & KOL (Free-Tier)

### 9.1 Conference abstract access

Every major society publishes a free searchable abstract library:

- **ASCO Meeting Library** — `meetings.asco.org`
- **ASH Publications** — `ashpublications.org`
- **AACR Meeting Library** — `aacrjournals.org`
- **ESMO library** — `oncologypro.esmo.org`
- **AAN** — `aan.com`
- **AHA Scientific Sessions** — `professional.heart.org`
- **ACC** — `accscientificsession.acc.org`
- **ERS / ATS** — society websites
- **EULAR / ACR** — society websites
- **ESC** — `escardio.org`
- **ADA Scientific Sessions** — `professional.diabetes.org`

### 9.2 Conference coverage media (free)

- **OncLive** — oncology/hematology
- **CancerNetwork** — oncology
- **Healio** — multi-TA
- **MedPage Today** — cross-therapeutic
- **Medscape** — cross-therapeutic

### 9.3 KOL intelligence — open-source approach

pharmaintel builds KOL maps from open data rather than paid platforms:
- **PubMed author co-authorship networks** (MCP-accessible)
- **Dimensions.ai** (free academic tier) — grants + publications + trial roles
- **ORCID** — `orcid.org` — author disambiguation
- **ClinicalTrials.gov investigator field** — PI networks
- **Guideline panel member lists** — NCCN, ESMO, ACC, AHA, ADA public panels
- **Society fellowship/board rosters** — public on society websites

**[INACCESSIBLE]:** H1, Within3, Veeva OpenData, Definitive Healthcare, Komodo Health, ZoomRx — enterprise KOL platforms. Gap impact: engagement/digital-savviness scoring unavailable; replaced by publication+trial+guideline footprint scoring (open-source).

---

## 10. Deal & Licensing (Free-Tier)

**Primary (always use first):**
- **SEC EDGAR 8-K** — mandatory material event disclosure for US-listed acquirers/targets
- **SEC EDGAR S-4** — full M&A registration, fairness opinion
- **SEC EDGAR DEF 14A** — target shareholder proxy with deal rationale
- **Company IR press releases** — terms summary (usually less detailed than 8-K exhibits)

**Secondary (free media layer):**
- Endpoints News free deal coverage
- FiercePharma / FierceBiotech M&A sections
- BioPharma Dive deal tracker
- Evaluate Vantage deal commentary

**[INACCESSIBLE]:** DealForma, Cortellis Deals, GlobalData Deals, PitchBook, CB Insights, Mergermarket — enterprise. Gap impact: private-private deal granularity unavailable; US-listed deals are covered adequately via SEC.

---

## 11. Reference Framework Publications (Free-Tier)

These are authoritative free-tier reference publications used across pharmaintel reports:

- **Tufts CSDD Impact Reports** — `tuftscsdd.com` — drug dev cost/duration benchmarks
- **IQVIA Institute reports** — `iqvia.com/institute` — free thematic reports (oncology outlook, biosimilars, gene therapy)
- **WHO Technical Reports Series**
- **EMA Annual Reports**
- **FDA CDER Annual Novel Drug Approvals report**
- **Tufts White Papers**
- **DiMasi JA et al., "Innovation in the pharmaceutical industry" J Health Econ (2016)** — classic R&D cost estimate
- **Scannell JW et al., "Diagnosing the decline in pharmaceutical R&D efficiency" Nat Rev Drug Discov (2012)** — Eroom's Law
- **Wong CH et al., "Estimation of clinical trial success rates" Biostatistics (2019)** — phase transition benchmarks
- **ICH E9(R1) Addendum on Estimands** — endpoint interpretation
- **Cochrane Handbook** — evidence synthesis methodology
- **ISPOR Good Practices Reports** — ITC/MAIC, RWE, value assessment

---

## 12. Explicit Gaps (always disclose)

Pharmaintel reports **must** include a §Limitations section naming which free-tier gaps affected the analysis. Standard language for each:

| Gap | Standard disclosure |
|-----|--------------------|
| No IQVIA MIDAS | "Global ex-US sales granularity unavailable; approximated via company segment disclosures in 10-K/10-Q where reported." |
| No enterprise pipeline DB | "Pipeline completeness limited to ClinicalTrials.gov + WHO ICTRP + CTIS + published preprints; early preclinical not in public registries may be missed." |
| No paid KOL DB | "KOL map built from open sources (PubMed co-authorship, trial PI roles, guideline panels); engagement/digital signals unavailable." |
| No paid analyst research | "Consensus estimates approximated from free-tier earnings-call commentary; precision of sell-side NPV models unavailable." |
| No private-company detail | "Private companies covered only insofar as preprints, patents, and conference posters disclose; confidential pipeline not accessible." |
| Chinese/Japanese language | "NMPA / PMDA detail often primary-language; English summaries only." |
| No enterprise RWE | "Patient-level RWE not accessible; approximated via published studies indexed in PubMed." |

---

## Cross-reference

For *how* to query these sources, see `query-patterns.md`. For *triangulation* across sources, see `triangulation.md`. For *task-specific* playbooks, see `task-*.md`.
