# pharmaintel — PMDA Sub-Protocol (Japanese Regulatory Layer)

## Scope

When a query involves Japanese regulatory decisions, pricing, or label detail, pharmaintel's default English-first workflow is insufficient because:

- PMDA review reports (審査報告書) are Japanese-primary; official English translations rarely exist
- MHLW price listings (薬価基準収載) are in Japanese
- PMDA's English website is a summary layer; decision granularity lives in Japanese-only documents
- Ignoring Japanese primary sources introduces a systematic bias in any analysis involving Daiichi Sankyo, Takeda, Chugai, Eisai, Astellas, or any multinational filing for Japan

This sub-protocol defines the fetch + translation workflow when a PMDA layer is required.

## Trigger logic (v1.7.0 — generic-by-default discipline)

Bu sub-protocol **yalnızca query content**'ine göre tetiklenir. Kullanıcının coğrafi konumu, işvereni, Japonya ile profesyonel ilişkisi **trigger değildir** (bkz. `generic-by-default.md` Article 5).

### (A) Trigger by query keywords (explicit)

PMDA, MHLW, Chuikyo, 中医協, 薬価, Sakigake, 先駆け審査指定, Japan approval, 承認, Japanese label, 添付文書, 審査報告書, NHI price, Japanese regulator, 厚労省.

### (B) Trigger by query content (semantic — query-based, NOT user-based)

**Trigger örnekleri (geçerli):**
- Query'nin analiz konusu olan asset'in **actual sponsor**'ı major Japanese pharma (Daiichi Sankyo, Takeda, Chugai, Eisai, Astellas, Otsuka, vb.) ve query Japonya regulatory / commercial specificity içeriyor — örn: "Daiichi Sankyo'nun T-DXd asset'inin PMDA durumu"
- Query "Japan launch", "PMDA approval", "Japanese label" gibi açık Japonya kapsamı çağırır
- Query Japonya pricing / NHI listing / Chuikyo decision gibi spesifik Japonya regulatory mechanism mention eder

**Trigger DEĞİLDİR (forbidden — user-identity-based):**
- ❌ Kullanıcının Japonya ile profesyonel ilişkisi
- ❌ Kullanıcının Japan-licensed asset üzerinde çalışıyor olması (memory'den)
- ❌ "User works at company that licenses from Daiichi Sankyo" tarzı user-context tetikleri

**Trigger DEĞİLDİR (forbidden — query language, v6.0.0):**
- ❌ Sorgunun Japonca (日本語) yazılmış olması. **Sorgu dili kendi başına content trigger değildir** — bkz. `generic-by-default.md` Article 5.3. Sadece yukarıdaki (A) veya (B) maddelerindeki **semantic content** tetikleyicidir. Bir Japonca-yazılı sorgu global bir konuyu sorabilir (örn. FDA Drugs@FDA durumu); aynı şekilde İngilizce-yazılı sorgu PMDA-spesifik olabilir ("What's the PMDA approval status for T-DXd?"). v5.0.0 production test sonrası v6.0.0'da kodifiye edilmiştir; G61 manifest gate validator seviyesinde pattern detection yapar.

**Önemli ayrım:** "Major Japanese sponsor named" trigger'ı **query'nin analiz konusu olan asset'in actual developer'ı** Japonya merkezli pharma ise geçerlidir; kullanıcının işvereniyle hiçbir ilişkisi yoktur. Örnek: bir T-DXd query'si Daiichi Sankyo asset'i olduğu için PMDA layer tetikler — kullanıcı kim olursa olsun.

---

## Free-tier access map

| Source | URL pattern | Language | What to fetch |
|---|---|---|---|
| PMDA English — approved drugs | `pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html` | English summary | High-level list, product name, sponsor, approval date |
| PMDA Japanese — 新薬の承認審査情報 | `pmda.go.jp/PmdaSearch/iyakuSearch/` | Japanese | Full review reports (審査報告書), package inserts (添付文書), Risk Management Plans |
| MHLW (厚生労働省) | `mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iyakuhin/index.html` | Japanese | Policy, NHI listing, price revisions |
| NHI drug price database (薬価基準) | `iyakuhin.info` (third-party index) or MHLW | Japanese | Yakka (NHI price), listing date, price revision history |
| Chuikyo (中医協) decisions | `mhlw.go.jp/stf/shingi/shingi-chuo_128154.html` | Japanese | Pricing deliberations, premium assignments |
| Sakigake designations | PMDA notices + MHLW announcements | Japanese + English (lists) | Breakthrough-like expedited review designations |

**Authoritative hierarchy for Japanese regulatory claims:**
1. PMDA 審査報告書 (review report) for the specific approval — primary
2. MHLW Chuikyo minutes for price deliberations — primary
3. Sponsor Japanese IR page for in-market performance — primary (company-self-reported)
4. PMDA English summary — summary layer (useful but incomplete)
5. English-language sector media (BioPharma Dive, FiercePharma) — tertiary

---

## Fetch + translation workflow

### Step J1 — Identify the right Japanese document

Before attempting translation, pinpoint which document to fetch. Common targets:
- **Approval decision:** 審査報告書 (shinsa hōkoku-sho) — review report, analogous to FDA Summary Review
- **Label:** 添付文書 (tenpu bunsho) — package insert
- **Pricing:** 中医協資料 (Chuikyo shiryō) — pricing deliberation documents; 薬価収載 (yakka shūsai) — price listing announcement
- **Safety update:** 安全性情報 (anzensei jōhō) — drug safety communications, DSU

### Step J2 — Fetch with Japanese term preservation

```
web_fetch(url=<PMDA Japanese URL>, text_content_token_limit=6000)
```

Do NOT strip Japanese characters; the fetched text will arrive as UTF-8 mixed Japanese-Latin. pharmaintel relies on Claude's native Japanese comprehension at this step — no external translation API required for standard regulatory phrasing.

### Step J3 — Extract structured fields

From the Japanese text, extract into this schema:
- **Product (商品名 / 一般名):** brand name / INN
- **Sponsor (申請者):** applicant
- **Approval date (承認年月日):** YYYY-MM-DD
- **Indication (効能・効果):** indication text (quote Japanese, provide faithful English rendering)
- **Dosage (用法・用量):** dosing schedule (quote Japanese, provide English rendering)
- **Expedited designations:** 先駆け審査 (Sakigake) / 希少疾病用医薬品 (Orphan) / 条件付き早期承認 (Conditional Early Approval)
- **Key review comments (総合評価):** summary of PMDA's own assessment — this is where regulatory concerns get flagged

### Step J4 — Translate faithfully, flag uncertainty

For each Japanese quoted field, provide:
- **Original Japanese:** (preserved exactly)
- **English rendering:** (faithful, not embellished)
- **Confidence:** [Direct / Nuanced / Uncertain]

"Nuanced" applies when Japanese medical terminology has no one-to-one English equivalent (e.g., 再発難治性 vs R/R — close but the Japanese phrasing carries "difficult to treat" emphasis). "Uncertain" applies when Claude's Japanese comprehension produces multiple plausible renderings.

If confidence is "Uncertain," stamp the claim at Medium in triangulation.md §6 terms, and flag as `[translation-dependent]`.

### Step J5 — Cross-check with English summary

PMDA publishes English summary pages for most major approvals. After extracting from the Japanese primary, fetch the English summary (if it exists) and compare:
- If the English summary corroborates the Japanese extraction → upgrade confidence to High
- If the English summary conflicts with or omits detail from the Japanese → defer to Japanese primary, flag the English summary as "summary-level"

---

## NHI pricing — the Chuikyo premium framework

Japan's NHI drug pricing rewards innovation via premiums (加算, kasan). When a report cites Japanese pricing, these are the premium categories:

| Premium | Japanese | Magnitude | Trigger |
|---|---|---|---|
| Usefulness Premium I | 有用性加算(I) | 35–60% | Breakthrough clinical utility |
| Usefulness Premium II | 有用性加算(II) | 5–30% | Meaningful improvement |
| Market Size Premium | 市場性加算 | 10–20% | Small market, unmet need |
| Orphan Premium | 希少疾病加算 | 5–20% | Orphan designation |
| Pediatric Premium | 小児加算 | 5–20% | Pediatric indication |
| Sakigake Premium | 先駆け審査加算 | 10% | Sakigake designation carried into price |

**A pharmaintel PMDA-layer report should state which premiums (if any) were granted, not just the final yakka (price).** Premiums are the Japanese equivalent of NICE's "innovation premium" signal and reveal MHLW's own assessment of asset value.

---

## Known gaps and limitations

1. **Translation confidence degrades for:**
   - Proprietary clinical terminology unique to Japanese oncology literature
   - Abbreviated bureaucratic phrases that compress complex regulatory meaning
   - Context-dependent negation (Japanese double-negative constructions)
2. **Chuikyo minute redaction:** Confidential pricing negotiations are not in public minutes
3. **Risk Management Plan (RMP) granularity:** Japanese RMPs are detailed but Japanese-only; English versions may be delayed or unavailable
4. **Re-examination (再審査) outcomes:** Japan's post-marketing review (typically 4–8 years post-approval) produces extensive Japanese-only assessments that can trigger label changes
5. **Regional hospital formulary variation:** Japan has national NHI but hospitals influence in-practice access; not in public documents
6. **Not a substitute for a native Japanese-speaking regulatory affairs specialist** for high-stakes decisions

---

## Output template (when PMDA layer included in larger report)

```markdown
### Japan (PMDA) regulatory status

> Agency: PMDA · Approval date: YYYY-MM-DD · Confidence: [H/M/L]
> Source: PMDA 審査報告書 (Japanese primary) — URL
> Cross-check: PMDA English approved drugs summary — URL

- **商品名 / Brand:** [original JP] / [English]
- **効能・効果 / Indication:** [original JP] / [English rendering, confidence level]
- **用法・用量 / Dosing:** [original JP] / [English rendering]
- **Expedited designations:** [Sakigake / Orphan / Conditional Early Approval — specify in JP + EN]
- **PMDA review summary (総合評価):** [key concerns + approvability rationale, English rendering, confidence level]
- **NHI price (薬価) / Premiums:** [yakka + premium categories granted, if published]

[If translation confidence is not all High, explicit §Translation notes paragraph follows:]

> **Translation notes:** Japanese regulatory phrasing for [specific field] admits [alternative English rendering]. The rendering chosen reflects [which Japanese medical convention]. A bilingual regulatory affairs specialist should verify before use in external-facing material.
```

---

## Cross-reference

- `sources-catalog.md §PMDA` — URL catalog (to be added if not present)
- `triangulation.md §3` — conflict hierarchy; PMDA Japanese primary ranks above English summary
- `task-asset.md §Regional regulatory layer` — asset-level integration point
- `task-catalyst.md` — PMDA approval events as catalysts

**When to load this sub-protocol:** SKILL.md Step 1b / 1c should detect trigger keywords and load `sub-protocol-pmda.md` in parallel with the task-specific reference. This is an additive layer, not a replacement for the standard 5-phase pipeline.
