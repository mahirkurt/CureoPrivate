# pharmaintel — T3: Modality / Therapeutic Landscape Playbook

## Scope

Landscape of a **modality** (ADC, CAR-T, bispecific antibody, RNAi, mRNA vaccine, gene therapy, small-molecule class like KRAS G12C, PROTAC, etc.) or a **therapeutic class by MoA** (GLP-1 receptor agonists, TKIs, IL-23 inhibitors). Produces an evidence-stamped peyzaj map for stakeholders (business development scouting, medical affairs briefing, investor deep-dive).

## Deliverable structure

```
# [Modality / Class] — Landscape Report

## 0. Definition & scope
  - Modality definition (biological / chemical basis)
  - Boundary decisions (what is in, what is out)
  - Therapeutic areas covered

## 1. Scientific foundation
  - Mechanism overview (ref high-impact review)
  - Key enabling technologies
  - Unsolved scientific challenges

## 2. Approved assets
  | INN / Brand | Sponsor | Target | First approval | Indications |
  (table of ALL approved products in the modality)

## 3. Late-stage pipeline (Phase 2b / 3)
  | Asset | Sponsor | Target | Indication | Trial NCT | PCD |
  (table; PCD = primary completion date)

## 4. Early-stage pipeline (Phase 1 / 1b)
  | Asset | Sponsor | Target / novelty | Indication |

## 5. Preclinical / discovery
  (narrative — patents + preprints reveal emerging candidates)

## 6. Competitive dynamics
  - Who are the leading players
  - Platform vs single-asset strategies
  - Recent deals / M&A activity in the modality

## 7. Regulatory & guideline posture
  - FDA / EMA designations trend (Breakthrough, PRIME)
  - Class-wide regulatory guidance
  - HTA positioning

## 8. Commercial & Payer Context
  - 8.1 Aggregate modality revenue (sponsor 10-K Product Revenue sums)
  - 8.2 Per-asset revenue + launch trajectory
  - 8.3 Pricing architecture (list price; net of rebates where disclosed)
  - 8.4 Analyst peak sales consensus (attribution-explicit, cap Medium)
  - 8.5 Payer & access reality (specialty vs buy-and-bill, PA/REMS burden)
  - 8.6 Market share + cannibalization dynamics
  - 8.7 Launch sequence + geographic rollout

## 9. Label & Post-Marketing Context (sub-protocol-label.md)
  - 9.1 Approved asset labels (dosing, indication scope, boxed warnings)
  - 9.2 Label comparison matrix across class
  - 9.3 FAERS disproportionality signals
  - 9.4 Regulatory actions post-approval (safety communications, REMS modifications)

## 9. Key scientific + clinical debates
  - Active controversies (e.g., durability of response, biomarker selection)
  - Guideline committee positions

## 10. Near-term catalysts (modality-level)
  - Readouts in 12mo
  - PDUFA / CHMP within 12mo
  - Key conferences where late-breakers expected

## 11. Limitations & gaps
```

---

## Phase 1 — Scope definition

Most important step for modality work. Explicit decisions:

- **Definition boundary:** e.g., "ADC" includes antibody-drug conjugates with cytotoxic payloads; excludes radioconjugates (RLT) and immunoconjugates unless specified
- **Generation cut-off:** first-generation vs latest vs emerging (e.g., 1st-gen ADCs with MMAE payload vs 2nd-gen with more potent payloads)
- **Geographic scope:** global default; or restricted
- **Indication scope:** all indications or a specific TA (oncology, hematology, solid tumors, etc.)

Document these decisions in §0 of the report.

---

## Phase 2 — Discovery (broad parallel sweep)

1. **Paper Search MCP** (broad): `<modality keyword>` across all sources
2. **PubMed MCP** (narrowed, recent): `"<modality>"[Title/Abstract] AND ("Clinical Trials"[Publication Type] OR "Review"[Publication Type])` last 3 years
3. **Clinical Trials MCP**: broad intervention type or MoA filter
4. **bioRxiv MCP**: preprints in relevant categories for preclinical signal
5. **Google Patents / Lens.org**: class-keyword search (assignee-agnostic) — surfaces all developing companies
6. **Tavily** (news, 180d): `"<modality> FDA OR phase 3 OR approval"`
7. **IQVIA Institute** (Fetch): search for modality-level reports (free; high-quality when available)
8. **Nature Reviews Drug Discovery** (Fetch): class review articles typically well-indexed; use for grounding

---

## Phase 3 — Deep-dive

### 3.1 Scientific foundation

Identify and read 2-3 high-impact recent reviews:
- **Nature Reviews Drug Discovery** (class reviews)
- **Cell Chemical Biology** (for chemical modalities)
- **Nature Reviews Cancer / Immunology** (TA-specific reviews)
- **Annual Review of Medicine / Pharmacology**

From the review(s), extract:
- Mechanism taxonomy
- Key enabling technologies
- Recognised scientific challenges

### 3.2 Approved assets

1. **FDA Drugs@FDA**: search by modality keyword where possible; supplement with manual list from review articles
2. **EMA EPARs**: cross-check for EU-approved assets not yet in US
3. **Purple Book** (biologics) for relevant modalities

For each approved asset, extract: INN, sponsor, target, first approval date, current indications.

### 3.3 Late-stage pipeline (Phase 2b / 3)

1. **ClinicalTrials.gov MCP**: all Phase 2 + Phase 3 trials with the modality keyword in intervention or as a filter
2. Cross-check **WHO ICTRP** for non-US Phase 3 (captures Chinese programs)
3. Cross-check **CTIS** for EU-primary trials
4. For each asset identified: confirm sponsor + target + indication + current status
5. IR pipeline pages for top 10 sponsors provide sanity check

### 3.4 Early-stage + preclinical

1. **Clinical Trials MCP**: Phase 1 / 1b trials
2. **bioRxiv / medRxiv**: preclinical publications in last 24 months
3. **Google Patents / Lens.org**: filings in last 3 years with class-keywords → surfaces candidates before they enter clinic
4. **Conference abstracts** (AACR, ASGCT, ESGCT, ESMO preclinical sessions)

### 3.5 Competitive dynamics

1. Rank sponsors by: number of assets × advancement stage × indication breadth
2. For top 5-10 players: pull recent deals (SEC EDGAR 8-K search + Endpoints deal coverage)
3. Identify platforms vs single-asset players
4. Recent M&A in the modality: SEC full-text `q="<modality keyword>" forms=8-K,S-4` last 24mo

### 3.6 Regulatory posture

1. FDA designation history: Breakthrough Therapy, Fast Track, Orphan, RMAT (for cell/gene), Accelerated Approval — count + trend
2. EMA PRIME designations for the modality
3. Relevant FDA guidance documents (e.g., "Considerations for the Design and Conduct of Externally Controlled Trials for Drug and Biological Products")
4. ICH harmonisation relevant to the modality

### 3.7 Commercial scale

For approved assets, aggregate from sponsor 10-Ks:
- Sum reported segment/product revenue
- Calculate year-over-year growth
- Identify the modality's share of sponsor total revenue

Free-tier context:
- IQVIA Institute class reports (when available)
- Evaluate Vantage free articles on modality trends
- Analyst-stamped market size figures in industry media — approximate only, attribute carefully

### 3.8 Scientific debates

Surface from:
- Recent NRDD / JCO / Blood / Nature Med **editorial** pieces
- Guideline committee discussions (NCCN panels sometimes publish discussion)
- Letter-and-reply exchanges in major journals
- Consensus MCP on specific controversial claims

### 3.9 Catalysts

1. **ClinicalTrials.gov**: primary completion dates in next 12 months for Phase 3 assets
2. **FDA AdComm Calendar**: any AdComm scheduled for modality-class topic
3. **CHMP agenda**: look-ahead on pending opinions
4. Major conferences in next 12mo + likely late-breakers (sponsors typically announce their presentations 2-4 weeks out)

---

## Phase 4 — Triangulation

- **Approved-asset count** → cross-check FDA Drugs@FDA + EMA EPAR list + trusted class-review tables
- **Pipeline count** → ClinicalTrials.gov + WHO ICTRP + each major sponsor's IR page
- **Commercial aggregates** → sum of sponsor 10-K disclosures; flag any estimate
- **Scientific claims** → peer-reviewed review + primary publications

## Phase 5 — Report

Per `assets/report-template.md`, landscape version. Typical output length: 6-15 pages of markdown, dense tables + narrative. When the user wants a print-ready deliverable or briefing deck, hand off to `carbon-html-report` / `carbon-pptx`.

---

## Modality-specific additions

### ADCs (antibody-drug conjugates)

- Payload classes (MMAE, DM1, DXd, exatecan) — important for differentiation
- DAR (drug-to-antibody ratio) — key technical parameter
- Linker chemistry
- Bystander effect expectations

### CAR-T / cell therapies

- Autologous vs allogeneic
- Manufacturing considerations (vein-to-vein time)
- REMS requirements
- Capacity constraints across sponsors

### Bispecific antibodies

- Format diversity (BiTE, DART, DuoBody, etc.)
- T-cell engager vs blocker vs other mechanism
- CRS / ICANS safety profile comparison

### RNAi / ASO

- Delivery platform (GalNAc, LNP, naked)
- Liver vs extrahepatic tissue targeting

### mRNA

- Delivery (LNP composition)
- Vaccine vs therapeutic distinction

### Gene therapy

- AAV serotype landscape
- Payload size constraints
- Durability data maturity

### KRAS G12C / small-molecule oncogene inhibitors

- G12C vs pan-RAS
- Resistance mechanisms
- Combination strategies

---

## Commercial & Payer Context — detailed workflow (v1.4.0)

task-modality.md'nin §8 çıktısı için bu alt-protokol, sponsor sweep ve label sub-protocol'leriyle entegre çalışır. Amaç: landscape raporunun sadece klinik değil **ticari ve erişim** boyutlarını da yakalamak. Medical Affairs + Business Unit karar destekleri için materyal detay gerekir.

### C1 — Aggregate modality revenue

**Kaynak:** Top-30 sponsor sweep sırasında toplanan 10-K Product Revenue tablosu.

Her modality'de yer alan onaylı ajanların son takvim yılı satış rakamları toplanır. **Sadece onaylı ve ticari olarak pazarlanan** ajanlar sayılır; klinik aşamadakiler ayrı §3.

**Format:**

```markdown
**Modality aggregate revenue ([latest FY]):**

| Asset | Sponsor | FY [year] revenue | Source |
|---|---|---|---|
| [Brand] | [Sponsor] | $XXX M | [10-K ref, page] |
| ... | ... | ... | ... |
| **Modality total** | | **$X.X B** | |

**Y/Y trajectory:** [+/- %], drivers: [launch, LoE, competitive entry]
```

**Confidence:** High (statutory filing). Tek kaynak cap'i uygulanmaz çünkü 10-K primary'dir.

### C2 — Per-asset revenue + launch trajectory

Onaylı her ajan için çeyreklik revenue run-rate grafiği — 8-çeyrek tarihsel serisi + sponsor guidance.

- **Launch trajectory archetypes** (sınıflandırma):
  - Fast uptake (>$1B in year 2, Keytruda-pattern)
  - Gradual build (rare disease, pediatric)
  - Slow / stalled (failed launch signals)
  - Cannibalizing (ürün portföyü içinden ikame)

Bu sınıflandırma sonraki ajanların launch projeksiyonunu calibrate eder.

### C3 — Pricing architecture

Her onaylı ajan için **list price** ve **net of rebates** where disclosed:

- **US list price:** WAC (Wholesale Acquisition Cost), red book veya sponsor disclosure
- **Annual cost of therapy:** weight-based veya flat-dose
- **Net pricing:** sponsor 10-K'da gross-to-net disclosure oranı ve sebebi
- **Specialty vs buy-and-bill vs pharmacy benefit** — reimbursement channel
- **340B / Medicaid tiering:** varsa

**Caution:** Net pricing genellikle gizlidir; list + gross-to-net oranının uygulanması ile inferred net tahmin edilebilir ancak Medium confidence cap'lenir.

**Pharmacoeconomic pricing for rare disease:** Ultra-rare indikasyonlarda tedavi başına USD 500K-2M+ aralığı standart — bu aralık alıştığımız dışında "high" değil "peer-accepted" olarak okunmalı. Karşılaştırma için ICER threshold analizi task-hta.md'ye bağlanır.

### C4 — Analyst peak sales consensus (attribution-explicit)

Analyst notları (Jefferies, Morgan Stanley, BMO, Truist, SVB, Piper Sandler, vb.) **primary değildir** ancak konsensüs sinyali için kullanılabilir.

**Format:**

```markdown
**Peak sales consensus (risk-adjusted):**

| Asset | Peak estimate | Timing | Analyst | Date |
|---|---|---|---|---|
| [Brand] | $X.X B | 20XX | [Firm] | YYYY-MM-DD |
| ... | | | | |

**Range (from published analyst coverage):** $X.X B – $Y.Y B
**Sponsor-implied guidance (10-K management discussion):** [if disclosed]
```

**Confidence cap:** Medium. Birden fazla bağımsız analyst benzer rakam veriyorsa Medium-High. Tek kaynak = Medium. "Unpublished analyst note" = Low.

### C5 — Payer & access reality

Her onaylı ajan için aşağıdaki operasyonel ticari parametreler:

| Parameter | Operasyonel anlamı |
|---|---|
| **Specialty vs oral pharmacy vs buy-and-bill** | Reimbursement channel + site-of-care restriction |
| **Prior authorization burden** | Prescriber friction; PA denial rate sponsor IR'da nadiren paylaşılır |
| **REMS / monitoring overhead** | Additional cost; adherence risk |
| **Infusion site-of-care** | HOPD vs ambulatory vs home; reimbursement tier |
| **Copay assistance program scope** | Commercial insured coverage gap management |
| **Medicare Part B vs D coverage** | Injectable vs oral delineation; 2026 Medicare negotiation impact |

**Bu verilerin kaynağı:** sponsor IR deck'leri (commercial update slides), third-party specialty pharmacy reports (CVS Health, Express Scripts drug trend reports), ICER Evidence Reports.

### C6 — Market share + cannibalization

Onaylı ajanlar arasında pazar dağılımı:

- **TRx / NRx market share** (IQVIA Institute free reports; specialty pharmacy vendor disclosures; sponsor 10-K unit volumes)
- **Cannibalization patterns:** yeni ajanın eski ajanın hasta havuzundan ne kadarını aldığı
- **Switch dynamics:** prior therapy failure → next-line patterns

Bu kısım rare disease modalitelerinde zordur çünkü hasta havuzu küçük, IQVIA verileri toplanamayabilir. Rare disease için **patient advocacy group reports + registry RWE** alternatif source.

### C7 — Launch sequence + geographic rollout

**Her onaylı ajan için:**

```
US launch: YYYY-MM (approval) → YYYY-MM (commercial availability)
EU launch: YYYY-MM (CHMP positive) → YYYY-MM (per-country EMA MA + country pricing negotiation)
Japan launch: YYYY-MM (PMDA approval) → YYYY-MM (NHI price listing)
China launch: YYYY-MM (NMPA approval) → YYYY-MM (NRDL listing, if applicable)
Other key markets: ...
```

**Key insight:** EU launch'un US launch'tan 12-24 ay sonra gelmesi olağan; country-by-country access tier gerçeği (Almanya önce, Fransa ve İtalya ortada, İspanya ve UK en sonra) explicit belirtilmeli.

### C8 — Integration with other layers

- **Label sub-protocol (L4)** → restrictive population, boxed warning, REMS direkt ticari parametrelere bağlanır
- **HTA layer (task-hta.md)** → NICE / CADTH / G-BA kararları pricing ve access reality'sini şekillendirir
- **PMDA sub-protocol** → Japan premium (kasan) kategorilerine giriş C3 pricing analizini genişletir

### Confidence caps for Commercial & Payer Context

| Data type | Max confidence |
|---|---|
| Sponsor 10-K revenue figures | High |
| Sponsor guidance (forward-looking) | Medium |
| Analyst peak sales (single source) | Medium |
| Analyst peak sales (multi-source consensus) | Medium-High |
| Market share from IQVIA or specialty pharmacy (aggregate) | Medium-High |
| Inferred net pricing | Medium |
| Sponsor investor day revenue projection | Medium |
| Competitor cannibalization qualitative read | Medium |
| Rumored pricing from industry media | Low |

### Known gaps for Commercial context

1. **Net pricing** confidential by policy design — free-tier analysis always infers, never confirms
2. **Rebate architecture** Private Manufacturer Rebate agreements not disclosed
3. **Specialty pharmacy channel concentration** disclosed quarterly but lag 30-60 days
4. **Account-level wins/losses** not public; analyst notes anecdotal
5. **Real-world effectiveness** separate from efficacy; requires registry RWE access
6. **ICER threshold opinion for specific region** requires ICER Evidence Report fetch for that specific asset

---

## Cross-reference (updated for v1.4.0)

- `sources-catalog.md §Industry Sources + Statutory Filings` — primary filing URL catalog
- `sub-protocol-sponsor-sweep.md` — per-sponsor IR + 10-K + press fetch workflow
- `sub-protocol-label.md` — onaylı asset label fetch + FAERS signal workflow
- `triangulation.md §6` — confidence caps
- `task-asset.md §Payer access layer` — single-asset commercial paralleli
- `task-hta.md` — HTA layer integration point
- `task-comparison.md` — H2H commercial delta matrisleri
