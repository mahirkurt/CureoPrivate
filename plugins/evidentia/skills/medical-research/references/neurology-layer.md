# Neurology Layer (0.5.G)

**Optional enrichment module** — loaded only when the question's context enters neurology. NOT
mandatory; the core PRISMA pipeline (P0–P7) runs without it. Output → clearly-labelled enrichment
appendix (not the core SR report).
**Recreated v8.2.0 (UP-003).**

**Triggers (full):** MS/multipl skleroz, NMOSD, MOGAD, MG/miyastenia, SMA/spinal müsküler atrofi,
ALS, Alzheimer, Parkinson, migren, epilepsi, inme/stroke, DMT/hastalık-modifiye edici tedavi,
anti-amiloid, anti-CD20, anti-CGRP, nusinersen, risdiplam, onasemnogen, ARIA, EDSS, ARR, ADAS-Cog,
CDR-SB, motor milestone, HINE, CHOP-INTEND.

---

## 1. Guidelines & criteria (Tier 1)
AAN, ECTRIMS/EAN (MS — McDonald 2024 diagnostic criteria), AANEM, MDS (Parkinson). Disease-specific
diagnostic/response criteria stated explicitly.

## 2. Disease-specific endpoint frameworks
- **MS:** ARR (annualized relapse rate), confirmed disability progression (CDP/EDSS), MRI lesion
  activity, NEDA-3/4; DMT efficacy tiering.
- **Alzheimer:** ADAS-Cog, CDR-SB, amyloid/tau biomarkers; **ARIA-E/-H** monitoring (anti-amyloid
  mAbs) — appraise magnitude vs. safety burden.
- **SMA:** motor-milestone achievement, HINE-2, CHOP-INTEND, event-free survival; **presymptomatic
  treatment window** is decisive — natural-history comparator validity is central (link rare-disease).
- **MG:** MG-ADL, QMG.

## 3. Mechanism & pipeline
anti-CD20, S1P modulators, BTKi (MS); ASO/splice-modifier/gene therapy (SMA: nusinersen intrathecal,
risdiplam oral, onasemnogene gene therapy); anti-amyloid mAbs (Alzheimer); anti-CGRP (migraine).
ChEMBL native + AdisInsight pipeline + CT.gov.

## 4. Appraisal
- Natural-history/registry comparators (SMA, ALS) — Tier 4 validity caveats.
- Open-label-extension durability; functional vs. surrogate endpoints.

## 5. Output → enrichment appendix (domain-specific guideline placement / pipeline note), never the core SR sections
Feeds the enrichment appendix's guideline-placement note, epidemiology note (incidence/newborn-
screening context for SMA — co-fire 0.5.K), and TR access note. Handoff for individual access (e.g.,
SMA SGK) → `onko-erisim`/`saglik-sigorta`.
