# Evidence Grading & Critical Appraisal (v9.0)

**Loaded:** ALWAYS (P6 — GRADE Certainty; no dedicated phase file, this is P6's home).
**v9.0.0 (Task 13, PRISMA refactor):** GRADE + Summary-of-Findings (SoF) are made **central** —
§1 Tier hierarchy and §2 GRADE core mechanics are preserved verbatim in spirit, but §2 now
states per-outcome GRADE domains as an **explicit, structured input** fed by `risk-of-bias.md`
(not a prose aside), and a new §8 gives the SoF table spec **consumed by `prisma-reporting.md`
§5** (the canonical `grade_sof` shape — this file supplies the reasoning that fills it, it does
not re-specify or diverge from its shape).

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
the pragmatic track (§3). Certainty is rated **per outcome**, never per study — each critical/
important outcome (OS, PFS, ORR, Grade ≥3 AE, QoL, …) gets its own independent rating, its own
row in the SoF table (§8), and its own set of downgrade/upgrade reasons; a single body of
evidence can be "High" for one outcome and "Low" for another. Start position by design, then
move through the five domains (§2.1) systematically — not as a holistic gestalt impression.

**Final certainty:** ⊕⊕⊕⊕ High · ⊕⊕⊕◯ Moderate · ⊕⊕◯◯ Low · ⊕◯◯◯ Very low. Start HIGH for RCT
bodies of evidence; start LOW for observational bodies (each rate-down step below moves one
level; two or more domains rated "serious" for the same outcome may compound to a two-level
drop when the Cochrane Handbook ch. 14 guidance so indicates).

### 2.1 The five GRADE domains — each an explicit, structured input

Every domain below is rated **per outcome**, not per study, and the rating is recorded with an
explicit reason string (feeds `grade_sof[].downgrade_reasons`, §8) — a bare "Moderate" without
a stated reason is not an acceptable GRADE output.

| Domain | What is rated down | **Structured input source** |
|---|---|---|
| **Risk of bias (RoB)** | The proportion of the outcome's contributing evidence at high/serious/critical risk of bias, weighted by the outcome's information size | **`risk-of-bias.md` §5** — explicitly: "a body of evidence for outcome X is downgraded one level (serious limitation) if the majority of contributing studies carry a `high`/`serious`/`critical` `overall_judgement`; two levels (very serious) if that majority is pervasive and unmitigated by sensitivity analysis excluding the high-RoB studies." Only `human_approved:true` `rob_assessments` rows count toward this majority (`risk-of-bias.md` §3 human-approval gate) — a draft judgement never drives a downgrade. |
| **Inconsistency** | Unexplained heterogeneity across studies contributing to the same outcome | I², τ², visual overlap of point estimates/CIs, and — critically — whether `data-extraction.md` §3's outcome-based pooling flagged a **unit/definition mismatch** ("birim uyumsuz — sentezlenemez"); an unresolved unit mismatch is itself a serious-inconsistency signal, not silently averaged away |
| **Indirectness** | Mismatch between the retrieved evidence's PICO and the review's PICO (`prisma-protocol.md` §2) | Population/intervention/comparator/outcome/setting transferability check against the pre-specified `protocol` block; surrogate outcomes used in place of the pre-specified `outcome_primary` are an automatic indirectness flag |
| **Imprecision** | Wide confidence intervals relative to a minimally important difference (MID), or a small total information size | CI width vs. MID; total `n_participants` (from `evidence_table` — `data-extraction.md` §5) relative to optimal information size; a single small trial driving a critical outcome is a canonical imprecision downgrade |
| **Publication bias** | Suspected selective non-publication of unfavourable results | Funnel-plot asymmetry (when ≥10 studies), discrepancy between registered outcomes (CT.gov via `search-strategy.md` §4 grey-literature/registry search) and published outcomes, and industry-funding concentration noted in `evidence_table[].funding`/`coi` |

**Rate UP** (observational bodies only, §3 pragmatic-track equivalents apply analogously) for:
large effect (RR ≥2 / ≤0.5), dose-response gradient, or plausible residual confounding working
*against* the observed effect (would have biased the estimate toward the null, yet an effect was
still observed).

### 2.2 Aggregation discipline

`rob_assessments` (per-study) and `grade_sof[].downgrade_reasons` (per-outcome) are related but
**not the same granularity** — the mapping from many per-study RoB judgements to one per-outcome
RoB-domain rating is itself a judgement call made **at P6**, and the rationale (which studies,
what proportion, what weight) is recorded in `grade_sof[].plain_language_summary` or an adjacent
note, never left implicit. GRADE certainty is **never recomputed** downstream — `prisma-reporting.md`
§5 relays the P6 output into the SoF table verbatim; if a P7 reviewer disagrees with a rating,
the correction happens here at P6, not by silently editing the reporting-stage table.

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

## 4. Specialty Appraisal Checklists (per active enrichment module)

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
sentence to a cited source. Knowledge-gap analysis (P4/P7) names what the evidence does **not**
yet answer — including Turkish incidence/registry-coverage gaps for the epidemiology enrichment module.

---

## 8. Summary-of-Findings (SoF) Table Spec — consumed by `prisma-reporting.md` §5

The SoF table is the GRADE Working Group's standard vehicle for communicating per-outcome
certainty alongside effect estimates (Guyatt et al.); it is the artefact that makes §1's Tier
hierarchy and §2's per-outcome domain ratings **legible to the reader** in ⑥ of the SR report
(`output-templates.md` §1). **This file authors the reasoning; `prisma-reporting.md` §5 owns and
defines the canonical `grade_sof` JSON shape** — the two are kept in lockstep and this section
is written to match that shape field-for-field (no divergent key names are introduced here).

### 8.1 Row construction (one row per critical/important outcome)

For every outcome carried in `evidence_table` (`data-extraction.md` §5) that the P0 protocol
marked `outcome_primary` or `outcome_secondary` (`prisma-protocol.md` §5), or that P4's
outcome-based pooling (`data-extraction.md` §3) aggregated, construct one SoF row:

- **`outcome_name`** — verbatim from the protocol/extraction outcome name (no rewording that
  could obscure which pre-specified outcome this is).
- **`n_studies` / `n_participants`** — summed directly from the `human_approved:true`
  `evidence_table` rows contributing to this outcome; never estimated or rounded up when a
  study's `n_total` is `"VERİ BULUNAMADI"` (that study is excluded from the sum, not
  approximated).
- **`effect_measure` / `effect_size` / `ci_95`** — the pooled (if meta-analyzed) or the single
  representative (if narrative synthesis only, clearly noted as such) effect estimate.
- **`certainty`** — the §2 per-outcome GRADE rating (⊕⊕⊕⊕/⊕⊕⊕◯/⊕⊕◯◯/⊕◯◯◯), never defaulted.
- **`downgrade_reasons`** — the explicit subset of the five §2.1 domains that were rated down (or
  empty array if none) — always the *reason strings*, never a bare certainty level without its
  justification.
- **`importance`** — `critical` / `important` / `not_important`, per the protocol's outcome
  hierarchy (primary outcomes are `critical` by default unless the protocol states otherwise).
- **`plain_language_summary`** — one or two reader-facing sentences translating the effect +
  certainty into plain Turkish (e.g., "Tedavi, genel sağkalımı muhtemelen artırmaktadır (orta
  düzey kesinlik); etkinin büyüklüğü hakkında kesinlik sınırlıdır çünkü …") — this is what
  populates ⑥'s narrative gloss in the clean copy (`report-presentation.md`).

### 8.2 No-fabrication discipline (identical to phase-file norm)

A blank/`null` field is **never** filled with a plausible-looking default (e.g. defaulting an
unrated outcome to "Moderate"); it is written as `"raporlanmadı"` and the gap is carried into
⑦ Kısıtlılıklar. This mirrors `prisma-reporting.md` §5's own no-fabrication clause and
`screening.md`/`data-extraction.md`/`risk-of-bias.md`'s identical norm — GRADE ratings are as
subject to the "no silent estimation" doctrine as any PRISMA flow count.

### 8.3 Presentation

⑥ in the reader-facing report (`output-templates.md` §1, `report-presentation.md`'s Clean-Copy
İskeleti) renders the SoF table with a visible "**Tablo N.**" caption and an accompanying
`<!-- VIZ -->` directive when a graphical certainty-by-effect display is warranted
(`report-presentation.md` İlke 5). The GRADE symbol legend (⊕⊕⊕⊕ High … ⊕◯◯◯ Very low) is
defined once, near the table, in plain Turkish — never left as an unexplained glyph run.
