# pharmaintel — NMPA Sub-Protocol (Chinese Regulatory & NRDL Layer)

## Scope

When a query involves Chinese regulatory decisions, NRDL listing, or label detail, pharmaintel's default English-first workflow is insufficient because:

- NMPA (国家药品监督管理局, National Medical Products Administration) review reports (审评报告) are Mandarin-primary; English summary translations rarely exist or are delayed
- CDE (药品审评中心, Center for Drug Evaluation) technical assessments are Mandarin-only
- NRDL (国家医保目录, National Reimbursement Drug List) negotiations and price disclosure happen in Mandarin
- Provincial reimbursement variations (省级医保目录) and DRG/DIP payment reform impact are tracked in Mandarin source documents
- Ignoring Mandarin primary sources introduces systematic bias for Chinese sponsors (BeOne Medicines, Innovent, Junshi, Hengrui, Sino Biopharm, CSPC, Akeso, RemeGen, Hutchmed, I-Mab) AND for multinational sponsors with material China operations (AstraZeneca, Roche, Pfizer, Novartis, Lilly, J&J — China revenue contributions ranging from 5-15% of global)

This sub-protocol defines the fetch + translation + integration workflow when an NMPA/NRDL layer is required.

## Trigger logic (v1.7.0 — generic-by-default discipline)

Bu sub-protocol **yalnızca query content**'ine göre tetiklenir. Kullanıcının coğrafi konumu, işvereni veya China ile profesyonel ilişkisi **trigger değildir** (bkz. `generic-by-default.md` Article 5).

### (A) Trigger by query keywords (explicit)

NMPA, 国家药品监督管理局, CDE, 药品审评中心, NRDL, 国家医保目录, NHSA, 国家医保局, NRDL negotiation, 医保谈判, 优先审评 (priority review), 突破性治疗药物 (Breakthrough Therapy), 附条件批准 (conditional approval), 仿制药一致性评价 (generic consistency evaluation), 中国上市 (China launch), 国谈 (state negotiation), 双通道 (dual-channel), volume-based procurement (VBP), 集中带量采购, GBA (Greater Bay Area), Boao early access pilot, Hainan free trade port medical pilot.

### (B) Trigger by query content (semantic — query-based, NOT user-based)

**Trigger örnekleri (geçerli):**
- Query'nin analiz konusu olan asset'in **actual sponsor**'ı major Chinese pharma (Çinli sponsor mapping tablosuna bakınız) ve query China regulatory / commercial specificity içeriyor
- Query bir multinational sponsor'ın **China-specific operasyonu** üzerine açıkça odaklanır (örn: "AstraZeneca China revenue", "Roche China R&D footprint")
- Query "China launch", "NMPA approval", "NRDL listing", "VBP exposure" gibi açık China kapsamı çağırır

**Trigger DEĞİLDİR (forbidden — user-identity-based):**
- ❌ Kullanıcının China ile profesyonel ilişkisi
- ❌ Memory-derived "user analyzes Chinese pharma" tarzı user-context tetikleri

**Trigger DEĞİLDİR (forbidden — query language, v6.0.0):**
- ❌ Sorgunun Mandarin (中文) yazılmış olması. **Sorgu dili kendi başına content trigger değildir** — bkz. `generic-by-default.md` Article 5.3. Sadece yukarıdaki (A) veya (B) maddelerindeki **semantic content** tetikleyicidir. Bir Mandarin-yazılı sorgu global bir konuyu sorabilir; aynı şekilde İngilizce-yazılı sorgu NMPA-spesifik olabilir ("What's the NMPA approval status + NRDL listing decision for BeOne's sonrotoclax?"). v5.0.0 production test sonrası v6.0.0'da kodifiye edilmiştir; G61 manifest gate validator seviyesinde pattern detection yapar.

**Sponsor mapping reference (analiz konusu olan asset'in actual developer'ını tanımak için):**

| Sponsor | Mandarin name | Notes |
|---|---|---|
| BeOne Medicines (ex-BeiGene) | 百济神州 | Brukinsa, sonrotoclax leader; dual NASDAQ + HKEX + STAR |
| Innovent Biologics | 信达生物 | Sintilimab + biosimilars + cardiometabolic |
| Junshi Biosciences | 君实生物 | Toripalimab + multi-modality |
| Jiangsu Hengrui | 江苏恒瑞医药 | Largest Chinese pharma by R&D spend; multi-modality |
| Sino Biopharmaceutical | 中国生物制药 | Generics + originator portfolio |
| CSPC Pharmaceutical Group | 石药集团 | Multi-modality, mRNA platform |
| Akeso | 康方生物 | Bispecific antibody platform (cadonilimab, ivonescimab) |
| RemeGen | 荣昌生物 | ADC platform (disitamab vedotin) |
| Hutchmed | 和黄医药 | Fruquintinib (out-licensed to Takeda) + multi-asset |
| I-Mab | 天境生物 | Multi-modality immunotherapy |
| Shanghai Pharmaceuticals | 上海医药 | Distribution + manufacturing |
| WuXi Biologics / WuXi AppTec | 药明生物 / 药明康德 | CDMO/CRO (not asset sponsor but ecosystem critical) |
| Fosun Pharma | 复星医药 | Comirnaty China rights + multi-asset; partnership-heavy |
| Henlius (Shanghai Henlius Biotech) | 上海复宏汉霖 | Biosimilars + originators; Fosun subsidiary |
| Legend Biotech | 传奇生物 | CAR-T (J&J partnership for cilta-cel/Carvykti) |

**Multinational sponsor with material China operations:** Aynı sub-protocol AstraZeneca, Roche, Pfizer, Novartis, Lilly, J&J, Merck, Bayer, Sanofi, Boehringer-Ingelheim, Bristol-Myers Squibb, Takeda, AbbVie China business analizi için tetiklenir — **ancak query'nin China-specific scope çağırması koşuluyla**, sponsor adının query'de geçmesi tek başına yetmez.

---

## Free-tier access map

| Source | URL pattern | Language | What to fetch |
|---|---|---|---|
| **NMPA English** | english.nmpa.gov.cn | English summary | High-level approval announcements, drug listing |
| **NMPA Chinese** | nmpa.gov.cn | Mandarin | Full review reports (审评报告), package inserts (说明书), drug catalog |
| **CDE Drug Approval Inquiry** | cde.org.cn | Mandarin | Submission tracking, technical review documents, communication records, technical guidance documents |
| **CDE Priority Review List** | cde.org.cn/main/news/listpage/95da6cc12c6ce00ed7f2a4d4f86b1408 | Mandarin | 优先审评品种 monthly updates |
| **NHSA (National Healthcare Security Administration)** | nhsa.gov.cn | Mandarin | NRDL annual updates, negotiation results, payment policy |
| **NHSA NRDL search** | fuwu.nhsa.gov.cn | Mandarin | Real-time drug reimbursement status, regional adjustments |
| **NHSA VBP announcements** | nhsa.gov.cn/col/col43 | Mandarin | Centralized procurement results (集采), winning prices |
| **Yaozh.com (drug intelligence platform)** | db.yaozh.com | Mandarin (some EN) | Approval timeline, price tracking, NRDL history (free-tier limited but useful) |
| **Insight by PharmCube** | insight.pharmcube.com | Mandarin (EN translations available for premium) | Pipeline + deal tracking, NMPA submission analytics |
| **Provincial Healthcare Security Bureaus** | per province (e.g., Beijing: rsj.beijing.gov.cn, Shanghai: rsj.sh.gov.cn) | Mandarin | Provincial NRDL supplements, dual-channel pharmacy listing |
| **STAR Market filings (Shanghai Stock Exchange)** | sse.com.cn | Mandarin (some EN) | Chinese-listed biotech disclosures (analogous to SEC EDGAR) |
| **HKEX filings** | hkexnews.hk | English + Chinese | Hong Kong-listed biotech (Innovent, BeOne, Hutchmed, Akeso, etc.) |

**Authoritative hierarchy for Chinese regulatory claims:**
1. NMPA 审评报告 (review report) for the specific approval — primary
2. NHSA NRDL listing announcement — primary for reimbursement
3. CDE technical guidance document — primary for regulatory pathway
4. Provincial Healthcare Security Bureau announcement — primary for regional reimbursement
5. Sponsor Chinese IR / annual report / Stock Exchange filing — primary (company-self-reported)
6. NMPA English summary — summary layer (useful but incomplete)
7. Insight / Yaozh analytical platforms — secondary (aggregator with primary data)
8. English-language sector media (FierceBiotech China, BioSpectrum Asia, Endpoints China) — tertiary

---

## Fetch + translation workflow

### Step C1 — Identify the right Mandarin document

Before attempting translation, pinpoint which document to fetch. Common targets:

- **Approval decision:** 审评报告 (shěn-píng bào-gào) — review report; NMPA-CDE issues for each approval, analogous to FDA Summary Review
- **Label / package insert:** 说明书 (shuō-míng-shū) — analogous to US Prescribing Information; updated with each label revision
- **Submission acceptance:** 受理通知书 (shòu-lǐ tōng-zhī-shū) — equivalent to FDA filing acceptance letter; 受理号 (shòu-lǐ-hào, acceptance number) is the canonical tracking ID
- **Priority review designation:** 优先审评 (yōu-xiān shěn-píng) listing entry; specific category indicated (优先审评-1类, etc.)
- **Breakthrough therapy designation:** 突破性治疗药物 (tū-pò-xìng zhì-liáo yào-wù) — analogous to FDA Breakthrough Therapy
- **Conditional approval:** 附条件批准 (fù-tiáo-jiàn pī-zhǔn) — analogous to FDA Accelerated Approval; 上市后研究承诺 post-marketing study commitments are critical
- **NRDL listing / negotiation result:** 国家医保目录调整结果 — annual update typically published December; 谈判成功 (negotiated successfully) vs 直接挂网 (directly listed without negotiation) vs 被踢出目录 (delisted)
- **VBP (centralized procurement) result:** 集采中标结果 — winning sponsors + winning prices; 国采 (national VBP) vs 省级集采 (provincial VBP) vs 联盟集采 (alliance VBP)
- **Safety update:** 药品不良反应通报 (drug adverse reaction notification) issued by NMPA-CFDA periodic safety reporting

### Step C2 — Fetch with Mandarin character preservation

```
web_fetch(url=<NMPA Mandarin URL>, text_content_token_limit=8000)
```

Do NOT strip Mandarin characters; the fetched text will arrive as UTF-8 mixed Mandarin-Latin. pharmaintel relies on Claude's native Mandarin comprehension at this step — no external translation API required for standard regulatory phrasing. For supplementary Mandarin context, query Insight or Yaozh aggregator.

For complex CDE technical guidance documents (often 50+ pages), fetch the full PDF where possible and use semantic chunking; the Wěi-yuán-huì (委员会, committee) opinions section is typically the most critical and warrants full extraction.

### Step C3 — Extract structured fields

From the Mandarin text, extract into this schema:

- **Product (商品名 / 通用名):** brand name (商品名) / INN (通用名)
- **Sponsor / Marketing Authorization Holder (上市许可持有人 / MAH):** applicant — note that under Chinese MAH system since 2019, this may differ from the manufacturer (生产企业)
- **Acceptance number (受理号):** canonical tracking ID; format CXSL/CXHB/CXSS for biologics, JXHB/JXSL for chemical drugs, with year + serial
- **Approval date (批准日期):** YYYY-MM-DD
- **Drug Approval Number (批准文号):** marketing license number (e.g., 国药准字H20234567)
- **Indication (适应症 / 功能主治):** indication text (quote Mandarin, provide faithful English rendering)
- **Dosage (用法用量):** dosing schedule (quote Mandarin, provide English rendering)
- **Route of administration (给药途径):** route
- **Specifications (规格):** strength + presentation
- **Storage (贮藏):** storage conditions (often material for cold-chain)
- **Expedited designations:** 优先审评 (Priority Review with category number) / 突破性治疗 (Breakthrough Therapy) / 附条件批准 (Conditional Approval) / 罕见病用药 (Orphan/Rare Disease)
- **Key review opinions (审评结论):** summary of CDE's assessment — this is where regulatory concerns get flagged
- **Post-marketing study commitments (上市后研究承诺):** for conditional approvals, the studies committed to support full approval
- **Comparator drug for negotiation (比价品种):** for NRDL negotiations, the reference drug used for pricing benchmark

### Step C4 — Translate faithfully, flag uncertainty

For each Mandarin quoted field, provide:

- **Original Mandarin:** (preserved exactly with appropriate Pinyin annotation for first-use of technical terms)
- **English rendering:** (faithful, not embellished)
- **Confidence:** [Direct / Nuanced / Uncertain]

"Nuanced" applies when Mandarin medical-regulatory terminology has no one-to-one English equivalent. Examples:

- 适应症 vs 功能主治 — first is for chemical/biologic drugs, second is for traditional Chinese medicine (TCM); the regulatory pathway and label structure differ
- 一致性评价 (consistency evaluation) — refers specifically to generic equivalence framework introduced in 2016; no direct US analog
- 双通道 (dual-channel) — refers to the policy where high-cost NRDL drugs can be dispensed by both designated retail pharmacies AND hospital pharmacies; affects access
- 1类新药 vs 5类化学药品 — Chinese drug classification scheme has different numbering than FDA
- 国谈 (guó-tán) — abbreviation for 国家医保谈判, the annual NRDL price negotiation; carries political weight

"Uncertain" applies when Claude's Mandarin comprehension produces multiple plausible renderings, especially for:
- Provincial idiomatic regulatory language
- Pre-2017 historical terminology that has been superseded but still appears in legacy documents
- Technical TCM terminology mixed with conventional drug regulatory text

If confidence is "Uncertain," stamp the claim at Medium in triangulation.md §6 terms, and flag as `[translation-dependent]`.

### Step C5 — Cross-check with English summary

NMPA publishes English summary pages for major approvals — but coverage is incomplete and lagged 2-8 weeks vs Mandarin primary. After extracting from the Mandarin primary, fetch the English summary (if it exists) and compare:

- If English summary corroborates the Mandarin extraction → upgrade confidence to High
- If English summary conflicts with or omits detail from the Mandarin → defer to Mandarin primary, flag the English summary as "summary-level, lagged"
- If no English summary exists → Mandarin primary is the only source; cap confidence at Medium-High pending independent triangulation (sponsor IR, peer-reviewed publication, etc.)

For Hong Kong-listed sponsors (Innovent, BeOne, Hutchmed, Akeso, RemeGen, Henlius), HKEX filings provide bilingual disclosure — Mandarin primary + English official translation. This is a higher-confidence triangulation point than NMPA English summary.

---

## NRDL pricing — the negotiation framework

China's NRDL (National Reimbursement Drug List) is the single most important access mechanism for any drug in China. The list is updated annually (usually October announcement, December finalization, March effective date for negotiated drugs). Understanding the structure is essential for any commercial analysis.

### NRDL categories

| Category | Mandarin | Mechanism | Notes |
|---|---|---|---|
| **甲类 (Category A)** | jiǎ-lèi | 100% reimbursed; no co-pay | Primarily essential medicines, generics |
| **乙类 (Category B)** | yǐ-lèi | Partial reimbursement (typically 70-80%); patient co-pays balance | Most originator drugs land here |
| **协议期内 (Negotiated Drugs, time-limited)** | xié-yì-qī-nèi | Price negotiated; reimbursement applies for 2-year contract; renegotiation at end of term | Rapidly growing category for innovative drugs |
| **限定支付范围 (Restricted Reimbursement)** | xiàn-dìng zhī-fù fàn-wéi | Reimbursed only for specified indications / patient populations / line of therapy | Critical for narrow approved drugs |
| **不予支付 (Not Reimbursed)** | bù-yǔ zhī-fù | Excluded from NRDL; full self-pay | High-cost rare disease drugs that fail negotiation |

### NRDL annual negotiation (国谈) cycle

- **April-June:** Sponsor application + dossier submission to NHSA
- **July-September:** NHSA expert review + cost-effectiveness assessment + budget impact analysis
- **October-November:** Bilateral negotiation with sponsor
- **December:** Annual NRDL announcement with confirmed negotiated drugs + prices
- **March of following year:** Effective date for newly negotiated/renegotiated drugs

### Negotiation outcomes

| Outcome | Mandarin | Implication |
|---|---|---|
| **谈判成功** | tán-pàn chéng-gōng | Negotiated successfully; listed at agreed price for 2-year term |
| **谈判失败** | tán-pàn shī-bài | Negotiation failed; not listed in NRDL; full self-pay or alternative access (commercial insurance, patient assistance) |
| **续约成功** | xù-yuē chéng-gōng | Renewal successful at end of 2-year term; typical further price reduction 5-15% |
| **未通过形式审查** | wèi-tōng-guò xíng-shì shěn-chá | Did not pass formal review; pricing or evidence dossier insufficient |
| **主动放弃** | zhǔ-dòng fàng-qì | Sponsor voluntarily withdrew (often signals refusal of NHSA's price target) |

### Typical price reduction in NRDL negotiation

- **First-time negotiation (first listing):** 50-70% off original China launch price; can reach 80%+ for high-cost specialty drugs
- **Renewal negotiation:** 5-15% additional reduction typical
- **VBP (集采) impact:** for off-patent drugs included in centralized procurement, additional price collapse can reach 90% off original; this often happens 3-5 years post-LoE in China

**A pharmaintel NMPA-layer report should state which NRDL category the drug holds (A/B/Negotiated/Restricted/Not Listed), the negotiation cycle year, the price reduction percentage achieved, and the renewal outlook.** These are the Chinese equivalents of NICE TA decision + price; they reveal NHSA's own assessment of asset value and access boundary.

---

## VBP (Volume-Based Procurement, 集中带量采购)

For off-patent originators and post-LoE drugs, China's VBP program is critical:

- **National VBP (国采):** Administered by NHSA; ~10 batches conducted since 2018, covering chemical drugs + biologics + medical devices
- **Provincial / Alliance VBP:** Provincial collaborations; covers TCM + non-national-batch drugs
- **Mechanism:** Sponsors compete for procurement contracts on price; lowest 3-5 winning bids share national volume; non-winning sponsors typically excluded from designated public hospitals
- **Price impact:** Average 50-70% price reduction on entry; some agents (statins, PPIs) saw 90%+ reductions
- **Strategic implication:** Multinational pharma typically loses VBP bids vs domestic generic manufacturers; this triggers loss of hospital channel and forces shift to retail / private hospital channels

### VBP relevance for innovative drugs

- Newly-launched innovative drugs typically NOT VBP-eligible during patent life
- Post-LoE entry into VBP is a major commercial inflection
- Strategic question for any China-launched drug: "How long until VBP?" — typically 3-7 years post-LoE depending on therapeutic area saturation

---

## Conditional approval (附条件批准) framework

Introduced in 2017, expanded since. Critical mechanism for accelerated access in oncology + rare disease.

### Approval route

- Based on Phase 2 single-arm / surrogate endpoint data
- Typically requires confirmatory Phase 3 within 2-4 years
- Failure to deliver post-marketing commitments → withdrawal of conditional approval (precedent: several conditional approvals withdrawn 2022-2024)

### Notable users

- BeOne Brukinsa (Chinese conditional approval before US approval)
- Innovent Sintilimab (multiple cancer indications via conditional path)
- Most Chinese-developed PD-1/PD-L1 antibodies
- ~40-50% of NMPA innovative drug approvals 2020-2024 used conditional pathway

### Strategic implication

Conditional approval enables faster commercial launch but creates a "data risk overhang" — sponsor must deliver confirmatory evidence or face delisting. NHSA NRDL negotiations factor this risk into pricing.

---

## Greater Bay Area (GBA) + Hainan early access pilots

For Mahir's typical multinational sponsor analysis, two China sub-jurisdictions matter:

### Greater Bay Area Hong Kong-Macao Drug Connect (粤港澳大湾区药品连接)

- Designated hospitals in Guangdong province (Greater Bay Area cities) can prescribe drugs approved in Hong Kong or Macao but not yet approved in mainland China
- Operational since 2020
- Mechanism for early access to drugs awaiting NMPA approval
- Sponsor must establish supply chain through GBA-designated hospitals

### Hainan Boao Lecheng International Medical Tourism Pilot Zone (海南博鳌乐城)

- Designated medical institutions can use drugs/devices approved in major regulated markets (FDA/EMA/PMDA/MHRA) but not yet in mainland China
- Operational since 2013, expanded since 2018
- Generates real-world evidence that can support subsequent NMPA submission
- Affects launch sequencing — some sponsors use Boao as bridging access mechanism

### Hainan Free Trade Port medical pilots

- Expansion of Boao model under broader Free Trade Port policy
- Includes telemedicine integration

For pharmaintel reports analyzing China launch strategy, mention GBA and Hainan pathways where they materially affect access timing or evidence generation.

---

## Known gaps and limitations

1. **Translation confidence degrades for:**
   - TCM (traditional Chinese medicine) regulatory terminology mixed with conventional drug text
   - Provincial idiomatic phrasing in regional reimbursement notices
   - Pre-2017 legacy regulatory terminology that has been superseded but still appears in historical documents
2. **NHSA negotiation outcome opacity:** Exact negotiated prices for specialty drugs are sometimes redacted; what's published is "negotiated successfully" + general price band rather than exact price
3. **Provincial reimbursement variance:** 31 provinces + 4 directly-governed municipalities each have supplementary NRDL lists; provincial coverage of a national-listed drug can differ in restriction language
4. **VBP cycle unpredictability:** New batches announced every 6-9 months; specific drug inclusion is not predictable until 60-90 days before bidding
5. **CDE technical guidance density:** Some CDE guidance documents are 100+ pages; full extraction is impractical, semantic chunking is required
6. **Bilingual disclosure asymmetry:** Hong Kong-listed Chinese biotech file in both English and Chinese, but Mandarin filings are typically more detailed and earlier
7. **Not a substitute for native Mandarin-speaking regulatory affairs specialist** for high-stakes decisions (NRDL negotiation strategy, conditional approval defense, post-marketing commitment management)

---

## Output template (when NMPA layer included in larger report)

```markdown
### China (NMPA / NHSA) regulatory & access status

> Agency: NMPA + NHSA · Approval date: YYYY-MM-DD · Confidence: [H/M/L]
> Source: NMPA 审评报告 (Mandarin primary) — URL
> Cross-check: NMPA English approved drugs summary (if available) — URL
> NRDL status: [Category A / B / Negotiated / Restricted / Not Listed]

- **商品名 / Brand:** [original ZH] / [English]
- **通用名 / INN:** [original ZH] / [English]
- **批准文号 / License Number:** [国药准字...]
- **MAH / 上市许可持有人:** [Chinese sponsor name in ZH] / [English]
- **适应症 / Indication:** [original ZH] / [English rendering, confidence level]
- **用法用量 / Dosing:** [original ZH] / [English rendering]
- **Approval pathway:** [优先审评/突破性治疗/附条件批准/标准审评 — specify in ZH + EN]
- **Post-marketing study commitments (if conditional):** [...]
- **CDE review summary (审评结论):** [key concerns + approvability rationale, English rendering, confidence level]
- **NRDL listing:** [year, category, negotiated price reduction %, renewal status]
- **VBP exposure:** [batch number + winning sponsors + price if affected; or "not yet VBP-eligible"]
- **GBA / Hainan early access:** [if applicable; pre-NMPA pathway used]

[If translation confidence is not all High, explicit §Translation notes paragraph follows:]

> **Translation notes:** Mandarin regulatory phrasing for [specific field] admits [alternative English rendering]. The rendering chosen reflects [which Chinese medical-regulatory convention]. A bilingual regulatory affairs specialist should verify before use in external-facing material.
```

---

## Cross-reference

- `sources-catalog.md §NMPA + NHSA + STAR Market` — URL catalog
- `triangulation.md §3` — conflict hierarchy; NMPA Mandarin primary ranks above English summary
- `triangulation.md §10` — Geography Verification Guard (China site participation in pivotal trials)
- `task-asset.md §Regional regulatory layer` — asset-level integration point
- `task-modality.md §8.7 Launch sequence` — China launch timing tier
- `task-catalyst.md` — NMPA approval events as catalysts
- `task-hta.md` — NRDL framework parallels HTA logic but with distinct mechanics
- `sub-protocol-pmda.md` — Japanese parallel; same translation-fidelity discipline applies

**When to load this sub-protocol:** SKILL.md Step 1g (semantic auto-trigger) detects "Major Chinese sponsor named" or "China launch / NMPA / NRDL / VBP" content and loads `sub-protocol-nmpa.md` in parallel with task-specific reference. This is an additive layer.
