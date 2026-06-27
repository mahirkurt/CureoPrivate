# Evidence Grading & Critical Appraisal (v8.2)

**Loaded:** ALWAYS (Phase 3 — Evidence Synthesis & Critical Appraisal).
**Recreated v8.2.0 (UP-001):** this file was referenced as always-load by SKILL.md Adım 0 but
was absent after the v8.0→v8.1 partial migration; reconstructed here from primary
methodological sources. No content is fabricated — every framework below is cited to its
canonical authority.

**Authority basis:** GRADE Working Group (Guyatt et al., *BMJ* 2008; *J Clin Epidemiol* 2011
series) · PRISMA 2020 (Page et al., *BMJ* 2021) · Cochrane Handbook for Systematic Reviews of
Interventions v6.x (Higgins et al.) · OCEBM Levels of Evidence (Oxford CEBM 2011) · AMSTAR-2
(Shea et al., *BMJ* 2017) · RoB 2 / ROBINS-I (Sterne et al., *BMJ* 2016/2019).

---

## 1. The Tier 0–6 Source Hierarchy

medical-research ranks every retrieved source into one of seven tiers. Higher tiers anchor
clinical claims; lower tiers contextualize but **never** override.

| Tier | Source class | Examples | Use |
|---|---|---|---|
| **Tier 0** | Synthesised high-certainty evidence | Cochrane/Campbell SR + meta-analysis, living SRs, NMA with GRADE | Anchor clinical conclusions |
| **Tier 1** | Practice guidelines + HTA appraisals | NCCN, ESMO, ASH/EHA, NICE, CADTH, IQWiG, WHO | Standard-of-care positioning |
| **Tier 2** | Pivotal RCTs (peer-reviewed) | Phase III registration trials in NEJM/Lancet/JAMA/Blood | Efficacy/safety primary data |
| **Tier 3** | Other RCTs + prospective comparative | Phase II RCT, well-designed cohorts | Supportive efficacy signal |
| **Tier 4** | Observational / RWE / registries | retrospective cohorts, claims, REGISTURK-type registries | Generalizability, TR-context |
| **Tier 5** | Mechanistic / preclinical / early-phase | ChEMBL/pharmacology, Phase I, bioRxiv preprints | Plausibility, pipeline-early |
| **Tier 6** | Grey / OSINT / non-peer-reviewed | conference abstracts, vendor decks, news | Context ONLY — never supports a clinical claim |

**Hard rule:** a Tier-6 OSINT item or a Tier-5 preprint may *raise a hypothesis* but may not
*establish* a clinical conclusion; preprints carry a mandatory non-peer-reviewed flag.

---

## 2. GRADE — Certainty of Evidence (per outcome)

Apply formal GRADE when the question is a focused PICO with extractable outcomes; otherwise use
the pragmatic track (§3). Start position by design, then move:

- **Start HIGH** for RCT bodies of evidence; **start LOW** for observational bodies.
- **Rate DOWN** for: risk of bias (RoB 2 / ROBINS-I), inconsistency (I², τ², non-overlapping CIs),
  indirectness (PICO transferability), imprecision (CI crosses MID; optimal information size),
  publication bias (funnel asymmetry, small-study effects).
- **Rate UP** (observational only) for: large effect (RR ≥2 / ≤0.5), dose-response, plausible
  residual confounding working against the observed effect.
- **Final certainty:** ⊕⊕⊕⊕ High · ⊕⊕⊕◯ Moderate · ⊕⊕◯◯ Low · ⊕◯◯◯ Very low.

Report certainty **per critical outcome** (OS, PFS, ORR, Grade ≥3 AE, QoL), not per study, and
summarise in a GRADE Summary-of-Findings frame (absolute + relative effect, n studies, certainty).

---

## 3. Pragmatic Appraisal Track (default when full GRADE is disproportionate)

For landscape/intelligence queries, apply a lighter but explicit appraisal:
1. **Design tier** (§1) + sample size + follow-up.
2. **Directness** to the asked PICO/TR-context.
3. **Consistency** across retrieved sources (convergent / divergent / complementary).
4. **Recency** vs. data cut-off; guideline version + date.
5. **Risk-of-bias headline** (RoB 2 domains for RCT; ROBINS-I for NRSI; AMSTAR-2 for SRs).
State the appraisal track used so the reader can calibrate.

---

## 4. Specialty Appraisal Checklists (per active 0.5 layer)

- **Oncology/Heme** — endpoint hierarchy (OS > PFS/iPFS > ORR/DoR > surrogate); crossover &
  informative censoring; RECIST 1.1 / Lugano / IMWG response criteria; MRD assay + threshold.
- **Immunology** — ACR20/50/70, PASI/EASI, clinical remission definitions; placebo-response drift.
- **Neurology** — ARR, EDSS/CDP for MS; ADAS-Cog/CDR-SB + ARIA for Alzheimer; motor-milestone for SMA.
- **Rare disease** — natural-history comparator validity; registry-endpoint surrogacy; n-of-few caveats.
- **HTA** — ICER/QALY model structure, comparator appropriateness, MAIC/NMA assumptions, budget impact.
Each layer file (`<specialty>-layer.md`) restates the relevant checklist inline.

---

## 5. Full-Text-Enriched Numerical Extraction (with copyright gate)

When the abstract is insufficient, the full-text cascade (`fulltext-retrieval.md`) opens the
paper to extract: HR/OR/RR + 95% CI, median OS/PFS, p-values, pre-specified subgroups, AE rates
by grade, and discontinuation. **Copyright gate (mandatory):** run EPMC `get_copyright_status`
first; CC-BY → quotable; restricted → analysis/extraction only, no verbatim bulk reproduction.

---

## 6. Entity / Relation / Temporal Extraction (NER)

For each appraised source capture a structured record: intervention, comparator, population, n,
endpoint, effect size + CI, study type, phase, status, date. This feeds the `.data.json` sidecar
evidence tables (`output-templates.md`) and the temporal narrative (how the evidence evolved).

---

## 7. Synthesis Stance

Deduplicate across connectors (same PMID/DOI/NCT). Present convergence explicitly; when sources
diverge, state *why* (population, era, design) rather than averaging. Tie every enrichment
sentence to a cited source. Knowledge-gap analysis (Phase 4) names what the evidence does **not**
yet answer — including Turkish incidence/registry-coverage gaps for the epidemiology axis.
