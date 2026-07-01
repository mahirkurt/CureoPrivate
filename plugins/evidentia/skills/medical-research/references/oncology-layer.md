# Oncology Layer (0.5.A)

**Optional enrichment module** — loaded only when the question's context enters oncology. NOT
mandatory; the core PRISMA pipeline (P0–P7) runs without it. Output → clearly-labelled enrichment
appendix (not the core SR report).
**Recreated v8.2.0 (UP-003):** clinical body grounded in current oncology authorities; connector
wiring is v8.0 native.

**Triggers (full):** kanser, tümör, karsinom, neoplazi, solid tumor, NSCLC, SCLC, breast/meme,
kolorektal, prostat, melanom, RCC, HCC, over, pankreas, baş-boyun, mesane, ADC, antikor-ilaç
konjugatı, checkpoint, PD-1/PD-L1, CTLA-4, TKI, KRAS G12C, EGFR, ALK, HER2, BRCA, MSI-H/dMMR,
TMB, RECIST, irRECIST, neoadjuvan, adjuvan, metastatik, OS, PFS, ORR, DoR, biomarker.

---

## 1. Guideline authorities (Tier 1)
- **NCCN** Clinical Practice Guidelines in Oncology (category of evidence/consensus 1–3).
- **ESMO** Clinical Practice Guidelines + **ESMO-MCBS** (magnitude of clinical benefit) + ESCAT
  (tumor-agnostic actionability of molecular targets).
- **ASCO** guidelines + **ASCO Value Framework**.
- TR layer: **TİTCK off-label** list (`find_off_label_uses_for_drug`, native) + SUT onkoloji
  protokolleri (Mevzuat) — often determinative for Turkish practice.

## 2. Molecular / biomarker knowledge bases
- **OncoKB** (levels of evidence 1–4, R1–R2) and **CIViC** — **no native MCP/API → documented gap**
  (not web-scraped, v1.4.0); when level/variant is unavailable natively, report the gap. **ChEMBL**
  native + **iuphar-gtopdb** (Tier-K) for target pharmacology; **PubChem** REST for structure.
- Companion-diagnostic status when a biomarker gates therapy.

## 3. Evidence mining
- Pivotal RCTs (Tier 2): NEJM/Lancet Oncol/JAMA Oncol/JCO. Conference abstracts (Tier 6 context
  only): **ASCO / ESMO / AACR** — flag as non-peer-reviewed, never anchor a claim.
- AdisInsight (`search_drugs`) for asset pipeline + regulatory history; CT.gov for active trials.

## 4. Appraisal checklist (oncology-specific)
- **Endpoint hierarchy:** OS > PFS/iPFS > ORR/DoR > pathologic/surrogate (pCR, MRD). Treat PFS/ORR
  as surrogate; demand OS where mature.
- **Crossover & informative censoring** — interpret PFS/OS with crossover adjustment caveats.
- **RECIST 1.1** (solid) / iRECIST (immunotherapy pseudo-progression); confirm response criteria.
- **Subgroup credibility** (pre-specified vs. post-hoc; interaction test).
- **ESMO-MCBS / ESCAT grade** when positioning benefit or a molecular target.

## 5. Output → enrichment appendix (domain-specific guideline placement / pipeline note), never the core SR sections
Feeds the enrichment appendix's guideline-placement note (NCCN/ESMO line-of-therapy) and pipeline
note (AdisInsight/CT.gov), plus the TR access reality note (TİTCK off-label + SUT). Endpoint table +
biomarker-actionability note in the `.data.json` `specialty_payload`.
