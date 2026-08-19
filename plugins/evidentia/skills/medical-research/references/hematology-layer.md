# Hematology Layer (0.5.B)

**Optional enrichment module** — loaded only when the question's context enters hematology. NOT
mandatory; the core PRISMA pipeline (P0–P7) runs without it. Output → clearly-labelled enrichment
appendix (not the core SR report).
**Recreated v8.2.0 (UP-003).** Malignant-heme depth; v8.0 native wiring.

**Triggers (full):** lösemi, lenfoma, myelom, AML, ALL, CML, CLL, MDS, MPN, DLBCL, FL, MCL, HL,
multiple myeloma/MM, AL amiloidoz, MRD, ölçülebilir kalıntı hastalık, CAR-T, bispesifik, BiTE,
BCMA, CD19, CD20×CD3, BTK inhibitörü, BCL-2/venetoklaks, FLT3, IDH1/2, JAK2, transplant, GVHD,
WHO-HAEM5, ICC-2022, ELN-2022, IPSS-M, IMWG, Lugano, IWCLL.

---

## 1. Classification & risk (dual where applicable — Tier 1)
- **Dual classification mandatory:** **WHO-HAEM5** ↔ **ICC-2022** (myeloid & lymphoid) — report both
  when they diverge (e.g., AML blast thresholds, MDS categories).
- Risk stratification: **ELN-2022** (AML), **IPSS-M** (MDS, molecular), **R-ISS/R2-ISS** (myeloma),
  **MIPI** (MCL), **IPI/IPS** (lymphoma/HL), **CLL-IPI**.
- Society guidelines: **ASH**, **EHA**, **NCCN** heme, **ESMO** heme; **IMWG** consensus for myeloma.

## 2. Response & disease-monitoring criteria
- **Lugano** (lymphoma, PET-based), **IMWG** response (myeloma incl. sCR/MRD-negativity),
  **ELN/IWG** (AML/MDS), **iwCLL**. State the criterion used.
- **MRD:** specify assay (MFC, NGS, ASO-qPCR, ddPCR) **and** sensitivity threshold (e.g., 10⁻⁵/10⁻⁶);
  MRD-negativity is a surrogate, not an OS substitute — appraise accordingly.

## 3. Evidence + pipeline mining
- Pivotal RCTs (Tier 2): NEJM/Lancet Haematol/Blood/JCO/Leukemia. **ASH/EHA** abstracts = Tier-6 context.
- AdisInsight (`search_drugs`/`get_drug`) for bispecific/CAR-T/ADC pipeline + regulatory history
  (e.g., glofitamab/Columvi STARGLO + ODAC + FDA CRL). CT.gov for active trials by sponsor.
- **TR access (§5):** TİTCK biosimilar/reference group + reimbursement. SUT heme protocols are a documented gap (hand off to `cureolex`).

## 4. Appraisal checklist (heme-specific)
- Transplant-eligibility stratification (consolidation context).
- Crossover & subsequent-therapy contamination in OS.
- Cytogenetic/molecular subgroup credibility (del17p, TP53, complex karyotype).
- For cell/gene therapy: manufacturing/vein-to-vein, bridging therapy, CRS/ICANS grading (ASTCT).

## 5. Output → enrichment appendix (domain-specific guideline placement / pipeline note), never the core SR sections
Feeds the enrichment appendix's guideline-placement note (ELN/IPSS-M/IMWG-anchored) and pipeline
note (heme pipeline), plus the TR access reality note (TR biosimilar + access). Dual-classification
note + MRD assay/threshold recorded in `specialty_payload`.
