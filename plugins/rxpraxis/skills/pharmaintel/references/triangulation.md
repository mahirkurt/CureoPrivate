# pharmaintel — Triangulation & Provenance

## 1. The "Two Independent Sources" rule

No **material claim** (clinical readout, regulatory status, financial figure, deal term, pipeline asset, KOL assignment) is reported at **High confidence** unless verified by **two independent sources**.

"Independent" excludes chains of derivative reporting: a company press release + 50 media articles derived from it is **one** source. Independence requires that the sources could have produced contradictory information if the underlying fact were different.

If only one source is available, the claim is reported at **Medium** or **Low** confidence with explicit single-source flagging.

---

## 2. Canonical triangulation templates

### 2.1 Clinical readout

```
Company 8-K or IR press release
    +
ClinicalTrials.gov results posting (mandatory for US trials within 1 year of primary completion)
    +
Peer-reviewed publication (for effect-size granularity)
    +
Conference presentation (if embargo lifted)
```

**Dissonance signals** (must investigate before reporting):
- Press release claims endpoint hit, but ClinicalTrials.gov shows non-significant p-value → likely peer-reviewed publication pending; flag discrepancy
- Press release gives mITT effect; registration gives ITT → note analysis-set difference
- Late-breaker oral gives richer subgroup data than press release → prefer oral + abstract

### 2.2 Regulatory status

```
FDA Drugs@FDA (approval letter + Medical Review)
    OR
EMA EPAR (central authorisation)
    +
Company 8-K / IR press release (announcement with action date)
    +
DailyMed current SPL (to confirm indication language)
```

For approval-status questions, the primary regulatory document is **definitive** — company press releases occasionally overstate (e.g., claiming "approved" for something that received only a narrow accelerated approval). Always read the primary label.

### 2.3 Deal terms

```
SEC 8-K (upfront + milestones + royalty structure)
    +
S-4 (if stock consideration — detailed valuation analysis)
    +
DEF 14A (target shareholder proxy — fairness opinion)
    +
IR press release (strategic rationale)
    +
Earnings-call commentary (management Q&A on deal)
```

Private-company deals where no US party is public: only the press release is available. Report as **Low** or **Medium** confidence per §11.2.

### 2.4 Sales figure

```
Company 10-K / 10-Q segment or product disclosure (primary)
    +
Earnings-call Q&A management commentary (secondary — for trend + forward guide)
    +
Industry free-tier commentary (FiercePharma / Evaluate Vantage — tertiary sanity check)
```

Approximation-only when:
- Segment reporting aggregates ("Other oncology")
- Product is < 5% of revenue (not separately disclosed)
- Company is private (no statutory disclosure)

### 2.5 Pipeline asset

```
ClinicalTrials.gov (current trial registrations by sponsor)
    +
Company IR pipeline page + latest R&D Day deck
    +
Recent 10-K MD&A pipeline section (latest annual rollup)
    +
Peer-reviewed publications on the asset (for mechanism credibility)
```

Discrepancy between IR page and ClinicalTrials.gov is common and informative:
- Newly added assets appear on IR first (internal decisions)
- Deprioritised assets may linger on IR but show no active trials → likely quietly shelved
- Active trials without IR mention → possibly out-licensed or sub-deprioritised

### 2.6 Patent status

```
FDA Orange Book (for NDA drugs) or Purple Book (for biologics)
    +
USPTO Patent Public Search or Google Patents (patent family + legal status)
    +
Lens.org (cross-office family resolution)
    +
Paragraph IV certifications (FDA — generic challenges)
    +
PTAB IPR filings (USPTO — challenges in force)
```

---

## 3. Conflict resolution hierarchy

When two or more sources contradict on a material claim, pharmaintel applies the following ranking and reports **both** sources with explicit preference statement:

1. **Regulatory agency primary document** (FDA Medical Review, EMA EPAR, label) — highest authority
2. **Peer-reviewed publication** — peer review filter applies
3. **Mandatory statutory filing** (SEC 8-K, 10-K; legal accuracy obligation)
4. **Clinical trial registry results posting** (legally required in US)
5. **Conference late-breaker presentation** — signals before peer review; preliminary
6. **Company press release** — possible positive spin; read carefully
7. **Analyst note** — interpretive; used as triangulation input, not authority
8. **Industry media commentary** — usually derivative of (1)-(4)
9. **Social media / blog** — signal only, not for verification

### Standard conflict-disclosure format

```
CLAIM: [text]
PRIMARY SOURCE (preferred): [source A] — [what A says]
ALTERNATIVE SOURCE: [source B] — [what B says]
RESOLUTION: [A preferred because it ranks higher per §3 hierarchy (reason)]
CONFIDENCE: Medium (conflicting primaries)
```

---

## 4. The "Single-Source" disclosure

Some claims genuinely have only one source:
- Private-company preclinical assertions (company website only)
- Very small product lines in Big Pharma (aggregated in "Other")
- Confidential HTA submissions
- Pre-submission FDA feedback (known only from company paraphrase)
- Private-company deal terms (press release only)

Report format:
```
[Claim] — Single-source: [name of source]. No independent verification available from free-tier sources. Confidence: Low.
```

Never silently report single-source claims as if triangulated.

---

## 5. Provenance stamp — the canonical four-part format

Every material claim in a pharmaintel output carries this stamp, placed either inline after the claim or in a dedicated references block:

```
— Source: [name + type]
— ID/URL: [canonical identifier]
— Accessed: YYYY-MM-DD
— Confidence: [High | Medium | Low | Unknown]
```

**Source type taxonomy (use exactly these labels):**

| Type label | Examples |
|-----------|----------|
| Primary Regulatory | FDA Drugs@FDA, EMA EPAR, DailyMed SPL, FDA Warning Letter |
| Statutory Filing | SEC 10-K/10-Q/8-K, S-1, S-4, DEF 14A, Form 4 |
| Clinical Registry | ClinicalTrials.gov, WHO ICTRP, CTIS, ChiCTR |
| Peer-Reviewed | Journal publication (include DOI) |
| Preprint | bioRxiv, medRxiv, Research Square (flag not peer-reviewed) |
| Patent | USPTO, EPO, Google Patents, Orange Book entry |
| HTA / Payer | NICE TA, ICER report, CADTH review, CMS LCD |
| Pharmacovigilance | FAERS Dashboard, EudraVigilance, VigiAccess |
| IR Communication | Company press release, earnings-call transcript, R&D Day deck |
| Conference | Abstract + oral/poster (flag embargo status) |
| Industry Media | Endpoints, FiercePharma, BioPharma Dive, Reuters Health |
| Professional Reference | Tufts CSDD, IQVIA Institute, WHO TRS |

**Canonical IDs to use:**
- DOI for publications: `10.xxxx/...`
- NCT ID for trials: `NCT04839484`
- ISRCTN / EUCTR for non-US: `ISRCTN12345678`, `EudraCT 2020-001234-56`
- SEC accession number: `0001193125-25-123456`
- FDA application number: `BLA 761069` or `NDA 215090`
- Patent number: `US10,123,456 B2` or `EP3456789`
- EPAR: full URL to EMA page

---

## 6. Confidence rubric

| Level | Criterion |
|-------|-----------|
| **High** | Primary source (regulatory / peer-reviewed / statutory filing) + cross-verified by ≥1 independent second primary |
| **Medium** | Single authoritative primary; OR two concordant secondaries |
| **Low** | Only secondary/media source; OR conflicting primaries (preferred stated per §3) |
| **Unknown** | Cannot be verified from free-tier sources (state why: subscription-only, private company, confidential) |

**Automatic confidence caps:**
- A claim resting **only** on industry media → max Medium
- A claim resting **only** on a preprint → max Medium (unless triangulated with an independent primary)
- A claim resting on analyst notes with no primary underneath → max Low
- A claim resting on social media / blog → Unknown
- A claim contradicting a regulatory primary → Low regardless of secondary volume
- **A pivotal-trial effect size / p-value / CI cited from sponsor PR or industry media, without a located peer-reviewed publication → max Medium, flag "peer-review pending"**
- **A PDUFA date cited from secondary media without attempted sponsor 8-K verification → max Medium**

### 6.1 Peer-review precision rule

When a peer-reviewed primary publication is located for a pivotal readout, **its numerical precision and framing override** the sponsor press release / industry media formulations. Specifically:

- **P-value precision:** use the precision the peer-reviewed paper uses. If the paper reports "P<0.001" and an industry article reports "P=.00002" or "P<.00001", use the paper's form. Industry articles frequently report pre-submission sponsor briefing figures that do not survive peer-review.
- **Hazard ratios:** peer-reviewed HR + 95% CI is authoritative. If a PR says "HR 0.19" for a metric the peer-reviewed paper reports as "cumulative incidence 12.6% vs 44.0%, Gray test P<0.001", use the paper's metric and framing (the PR may have reported a different or misremembered statistic).
- **Sample size:** peer-reviewed n treated vs n randomized distinction must be honored; do not merge.
- **OS / secondary endpoint significance:** if the peer-reviewed paper reports P=0.12, do NOT upgrade to "statistically significant" based on an industry article's different phrasing. If not significant, state so explicitly.

**Operational trigger:** After locating any peer-reviewed primary via PubMed MCP / Paper Search MCP, re-read any previously drafted section that cited a sponsor PR for the same trial and rewrite the stamps.

---

## 7. Embargo and ethical handling

- **Conference embargo:** late-breakers typically embargoed until presentation time. If encountered pre-embargo, pharmaintel declines to analyze until release.
- **Insider information (MNPI):** never used. Leaked documents, expert-network disclosures suggesting MNPI, or unverified Twitter claims from anonymous sources are excluded.
- **Earnings-call quiet periods:** typical US quiet period = last 2-3 weeks of quarter through earnings release. Rumors during quiet periods flagged with explicit note.

---

## 8. Freshness

Every pharmaintel output includes a **Data cutoff: YYYY-MM-DD** line. Claims dated after this line are not reflected. Pharma pipelines shift within hours (8-K filings, press releases) — this is non-optional.

Additionally, each cited source carries its **Accessed: YYYY-MM-DD** individually, so readers can tell *which* sources might be stale relative to cutoff.

---

## 9. Worked example — applying this protocol

**Task:** "Has Roche received FDA approval for glofitamab in DLBCL?"

**Phase 3 sources gathered:**
1. FDA Drugs@FDA page for Columvi (glofitamab) — approval letter, label (Primary Regulatory)
2. Roche press release from approval date (IR Communication)
3. DailyMed SPL for Columvi (Primary Regulatory)
4. NEJM pivotal phase 2 publication (Peer-Reviewed)
5. ClinicalTrials.gov NCT03075696 results posting (Clinical Registry)

**Triangulation applied (§2.2 Regulatory status + §2.1 Clinical readout):**
- FDA approval + Roche 8-K + DailyMed SPL concordant → approval status **High**
- NEJM + ClinicalTrials.gov results concordant on ORR → efficacy claim **High**

**Output stamp example:**
```
Glofitamab (Columvi) received FDA accelerated approval for relapsed/refractory DLBCL after ≥2 prior lines of systemic therapy on June 15, 2023, with a converted full approval on [date] based on [trial].
— Source: FDA Drugs@FDA (Primary Regulatory)
— ID: BLA 761309
— URL: https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2023/761309Orig1s000ltr.pdf
— Accessed: 2026-04-14
— Confidence: High (primary regulatory + cross-verified by DailyMed SPL + Roche 8-K)
```

---

## 10. Geography Verification Guard (v1.5.0 — global cross-task)

For any claim about regional access, regional pivotal trial participation, or regional regulatory implication, Claude MUST verify the geographic dimension against primary registry data before asserting. This guard, originally introduced in v1.1.0 task-catalyst.md §Geography verification with T5-only scope, is **promoted to global cross-task applicability** in v1.5.0.

**Scope (v1.5.0):** Applicable to T2 Asset Profile, T3 Modality Landscape, T5 Catalyst Watch, T6 Head-to-Head Comparison. Optional but recommended for T1 Company Deep-Dive and T4 Deal/M&A.

### Trigger conditions

The guard fires when any of these statements about a geographic region appear in (or are about to appear in) the report:

1. "[Asset/trial] available/launched in [region]"
2. "[Region] participated in [pivotal trial] with N centers"
3. "[Asset] expected early access in [region]"
4. "[Region]-specific regulatory pathway / pricing premium / launch sequence"
5. Any claim involving Türkiye / TR-context interpretation of a globally-developed asset
6. Any claim about LMIC access for a high-cost asset
7. Any claim about EU country-by-country tier (DE / FR / IT / ES / UK pricing precedence)
8. Any claim about APAC country-specific approval timing

### Verification protocol

For each geographic claim, Claude MUST:

1. **Verify trial site participation** via `Clinical Trials:get_trial_details(nct_id=...)` and inspect the `locations` field. Count sites per country, list facility names if material.
2. **Verify regulatory status per region** via FDA Drugs@FDA / EMA EPAR / PMDA / NMPA database (per region) — never infer from sponsor narrative alone.
3. **Verify launch availability** via sponsor IR commercial update slides + country-specific reimbursement listings (where free-tier accessible).
4. **Stamp every regional claim** with provenance and confidence per §6.

### Phrasing templates by verification outcome

When trial **has** Turkish sites:
> "[Trial] programına Türkiye [N] merkezle katıldı ([merkez listesi: Hacettepe, İstanbul Üniversitesi, ...])."

When trial **has no** Turkish sites:
> "[Trial] çalışmasında Türk klinik merkezi yer almadı; Türkiye'ye erişim post-approval mekanizmalara veya ayrı regional çalışmalara bağımlıdır."

When trial is **single-region**:
> "[Trial] [region]-only ([N] site); ex-[region] erişim post-approval mekanizmalara veya partner-driven regional çalışmalara bağımlıdır."

When **EU country tier** is invoked:
> "[Asset] EU launch tier: Almanya (önce, AMNOG 6-mo + reference price), Fransa (HAS Avis ortalama 4-8 mo post-EMA), İtalya (AIFA 8-14 mo), İspanya (12-18 mo), UK (NICE TA 18-24 mo). [Asset]-spesifik kararlar HTA layer'ında detaylı."

When **LMIC access** is claimed:
> "Yüksek-fiyat tedavinin LMIC erişim gerçeği: Zolgensma örneği gibi tek-doz milyon-dolar tedaviler için outcomes-based veya tiered-pricing özel program olmadan kaynak-kısıtlı sağlık sistemlerinde pratik erişim sıfıra yakındır. [Asset] için ilgili partnership/access program: [...] / [yok ise: kamu disclosure'ı yok]."

### Common failure modes (avoid)

1. **Generic regional inference without registry verification.** "Türkiye için erken erişim paterni beklenir" — bu cümle pivotal çalışmanın site listesi kontrol edilmeden yazılmamalı.
2. **EU-as-monolith treatment.** "EMA onayından sonra EU pazarında launch" — EU launch ülkeden ülkeye 6-24 ay arasında değişen launch tier ile gerçekleşir; bu nüans atlanmamalı.
3. **APAC/LMIC over-aggregation.** "Asya pazarı" gibi ifadeler Japan / Korea / China / India / SE Asia farklılığını gizler; her biri ayrı regulatuar ve pricing dünyasıdır.
4. **Türkiye TİTCK/SGK varsayımı.** Bu skill global scope'tadır; Türk regulatuar/reimbursement işleyişi açıkça T7-TR sub-query ile çağrılmadıkça yapılmamalı.

### Integration with task playbooks

- **task-asset.md** §2 Regulatory status — regional registry verification each region claim
- **task-modality.md** §2 Approved assets + §8.7 Launch sequence — per-region launch tier verification
- **task-catalyst.md** §Geography verification — orijinal protokol; v1.5.0 sonrası bu §10'a refer eder
- **task-comparison.md** §Regional access delta — H2H'da regional tier comparison
- **task-hta.md** — HTA agency kararları otomatik regional layer

### Confidence implications

- Regional claim with primary registry verification (ClinicalTrials.gov locations, FDA/EMA database) → **High**
- Regional claim with sponsor IR + secondary media → **Medium**
- Regional inference without explicit verification → **Low** (cap mandatory until verified)
- Regional claim contradicted by registry/regulatory primary → claim is wrong; remove or correct

---

## 11. History-sensitive chronological claims (v7.0.0)

### Problem statement

"Nth-of-class" or "first/second/third X in history" claims are a recurring factual blind spot in pharmacointelligence reporting. These claims are **deceptively easy to make** (the analyst's memory often feels certain) and **uniquely difficult to triangulate** (they require exhaustive enumeration of all prior instances, not just verification of the specific claim).

**Documented failure cascade:** In pharmaintel production tests, the claim "T-DXd received FDA's Nth tumor-agnostic accelerated approval" was incorrect in **three consecutive versions**: v2.0.0 reported "second" → v5.0.0 reported "third" → both wrong (actual: at least seventh, following pembrolizumab MSI-H 2017, larotrectinib NTRK 2018, entrectinib NTRK 2019, pembrolizumab TMB-H 2020, dostarlimab dMMR 2021, selpercatinib RET 2022). Each version partially corrected the previous error without achieving accuracy. This demonstrates that **self-correction without systematic verification amplifies rather than resolves Nth-of-class errors.**

### Rule: Mandatory primary-database enumeration for chronological claims

**Trigger condition:** Any claim in draft that asserts a temporal ordering relationship — "first", "second", "third", "Nth" — combined with a regulatory/clinical/commercial class category.

**Detection patterns (claim surface):**

| Language | Pattern examples |
|---|---|
| English | "first X to Y", "second/third X", "Nth X", "the only X", "first-ever X", "first-in-class X to achieve Y" |
| Turkish | "ilk X olan", "ikinci/üçüncü X", "ilk kez X", "X'in ilki", "tek X", "tarihindeki ilk/ikinci/üçüncü" |

**Claim categories requiring enumeration (non-exhaustive):**

| Claim class | Required verification source | Enumeration method |
|---|---|---|
| "Nth tumor-agnostic FDA approval" | FDA Drugs@FDA + FDA press releases | List ALL prior tissue-agnostic/tumor-agnostic approvals chronologically |
| "First ADC approved for X" | FDA Drugs@FDA + EMA EPAR | List ALL ADC approvals for that indication/class |
| "First bispecific to achieve X" | Same | Same enumeration |
| "Nth accelerated approval withdrawal" | FDA accelerated approval tracker | Full withdrawal chronology |
| "First CRISPR-based X" | FDA + EMA + PMDA | Full CRISPR approval chronology |
| "Largest pharma M&A in history" | SEC EDGAR + Bloomberg free-tier | List top-10 by deal value |
| "First SUT-listed X in Turkey" | TİTCK + SGK SUT gazette | SUT gazette chronological search |

### Verification protocol

1. **STOP before writing.** If draft contains an Nth-of-class claim, do NOT emit it yet.
2. **Enumerate.** Use primary database (FDA Drugs@FDA, EMA EPAR, ClinicalTrials.gov, SEC EDGAR, etc.) to list ALL known instances of the class category, sorted chronologically.
3. **Count.** Determine the actual ordinal position of the claimed asset/event.
4. **Cross-verify.** Use a second independent source (peer-reviewed review article, authoritative news recap, or a separate regulatory database) to confirm the enumeration is complete.
5. **Emit with ordinal or rephrase.** If ordinal is confirmed with high confidence → use it (e.g., "seventh tumor-agnostic FDA approval"). If enumeration is uncertain → **rephrase to avoid ordinal** (e.g., "T-DXd received the first ADC-based tumor-agnostic FDA approval" — avoids ordinal for total count, uses ordinal only for the specific differentiator "ADC-based" which IS verifiably first).

### Safe rephrasing patterns (when ordinal is uncertain)

| Unsafe (ordinal-dependent) | Safe (differentiator-focused) |
|---|---|
| "Second tumor-agnostic accelerated approval" | "First ADC-based tumor-agnostic approval" |
| "Third CAR-T approval" | "First allogeneic CAR-T approval" (if true) |
| "Largest pharma deal of the decade" | "Among the largest pharma deals (>$X billion)" |
| "First-ever treatment for X" | "First FDA-approved treatment specifically indicated for X" |

The safe pattern **narrows the claim to a verifiable differentiator** rather than asserting a position in an enumeration the analyst may not have fully compiled.

### Confidence implications

- Nth-of-class claim with full primary-database enumeration + cross-verification → **High**
- Nth-of-class claim with partial enumeration (e.g., "at least seventh" phrasing) → **Medium**
- Nth-of-class claim based on analyst memory alone → **Low** (MUST verify before emitting; if verification impossible, rephrase to safe pattern)
- Nth-of-class claim that has been wrong in prior versions → **Mandatory re-enumeration** from primary database; prior version's ordinal is disqualified as evidence

### Known FDA tumor-agnostic approval chronology (reference table, v7.0.0 baseline)

This table is provided as a **built-in reference** to prevent the specific T-DXd tumor-agnostic error from recurring. For other Nth-of-class categories, the analyst must compile the equivalent table from primary sources at query time.

| # | Drug | Biomarker/target | FDA approval date | Pathway |
|---|---|---|---|---|
| 1 | Pembrolizumab (Keytruda) | MSI-H/dMMR | 23 May 2017 | Accelerated |
| 2 | Larotrectinib (Vitrakvi) | NTRK fusion | 26 Nov 2018 | Accelerated |
| 3 | Entrectinib (Rozlytrek) | NTRK fusion | 15 Aug 2019 | Accelerated |
| 4 | Pembrolizumab (Keytruda) | TMB-H ≥10 mut/Mb | 16 Jun 2020 | Accelerated |
| 5 | Dostarlimab (Jemperli) | dMMR | 17 Aug 2021 | Accelerated |
| 6 | Selpercatinib (Retevmo) | RET fusion | 21 Sep 2022 | Full (label expansion) |
| 7 | **Trastuzumab deruxtecan (Enhertu)** | **HER2 IHC 3+** | **5 Apr 2024** | **Accelerated** |

> **Maintenance note:** This table must be updated when new tumor-agnostic approvals occur. As of April 2026 data cutoff, repotrectinib (Augtyro) NTRK/ROS1 may have received tumor-agnostic label language — verify before citing. Future tumor-agnostic candidates in pipeline: datopotamab deruxtecan TROP2-high, sacituzumab govitecan TROP2-high (both speculative).

---

## Cross-reference

For *tool-specific* query patterns that feed the sources being triangulated, see `query-patterns.md`. For *which* sources to hit for a given task type, see `task-*.md`.
