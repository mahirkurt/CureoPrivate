# Output Templates & Data Sidecar Schema (v9.0)

**Loaded:** ALWAYS (P7 — PRISMA Reporting / Output Generation).
**v9.0.0 (Task 13, PRISMA refactor):** the former internal §1–21 intelligence-report scaffold
is retired. The reader-facing structure is now the **SR (systematic-review) report** — a PRISMA
2020 / PRISMA-ScR–conformant article skeleton with eight numbered top-level sections (①–⑧,
§1 below). This is a **structure change, not a scope reduction**: every axis the former scaffold
covered (global literature, clinical pipeline, mechanism, regulatory, Türkiye, guidelines,
KOL, epidemiology, drug-intelligence…) still surfaces — but as **Bulgular (Findings) sub-sections**
or **labelled optional appendices**, never as a standalone tool-annotated heading.

**Scope split (unchanged from v8.1):** this file governs **scope & structure** (which sections,
which format class, the sidecar schema). `report-presentation.md` governs **presentation**
(clean-copy doctrine, anti-leakage, VIZ/OPS isolation). `prisma-reporting.md` governs the **P7
artefact mechanics** (flow-diagram box-by-box mapping, checklist-to-section mapping, study-
characteristics table, RoB summary figure, SoF table construction). All three are always-loaded;
read all before emitting a file-based report.

---

## 1. SR Report Structure (①–⑧) — reader-facing section contract

Every file-based systematic/scoping-review report contains the following eight sections, in
this order. Missing data = **"VERİ BULUNAMADI"** (never silently omitted); an optional
sub-element that genuinely does not apply to the review type (e.g. RoB summary in a scoping
review — `prisma-protocol.md` §4) is explicitly noted as not-applicable, not deleted silently.

```
① Arka Plan (Background)
② Amaç + PICO/PECO + Derleme Tipi (Objectives, framework, review type)
③ Yöntem (Methods)
    ③.1 Uygunluk kriterleri (eligibility)              ← prisma-protocol.md §3
    ③.2 Kaynaklar / bilgi kaynakları (information sources) ← search-strategy.md §3
    ③.3 Arama stratejisi (search strategy)              ← search-strategy.md §1–5
    ③.4 Seçim süreci (selection process)                ← screening.md §1–4
    ③.5 Veri çıkarım süreci (data extraction)           ← data-extraction.md §1–4
    ③.6 Yanlılık riski değerlendirmesi (risk of bias)   ← risk-of-bias.md §1–3
    ③.7 Sentez yöntemleri (synthesis methods)           ← evidence-grading.md §7
    ③.8 Kanıt derecelendirmesi (GRADE)                  ← evidence-grading.md §2
    ③.9 Veri kesim tarihi (data cut-off)                ← search-strategy.md §5 run_date
④ PRISMA Akış Diyagramı (flow diagram)                  ← prisma-reporting.md §1
⑤ Bulgular (Findings)
    ⑤.1 Çalışma özellikleri tablosu (study characteristics) ← prisma-reporting.md §3
    ⑤.2 Yanlılık riski özeti (RoB summary)               ← prisma-reporting.md §4
    ⑤.3 Sonuç-bazlı bulgular (outcome-by-outcome results) ← data-extraction.md §3
⑥ Summary-of-Findings / GRADE Tablosu                    ← prisma-reporting.md §5, evidence-grading.md §8
⑦ Tartışma · Kısıtlılıklar · Sonuç (Discussion, limitations, conclusion)
⑧ Kaynaklar (References, Vancouver + PMID/DOI/NCT) + Dahil/Dışlanan Listeleri (included/excluded lists)
```

> The numbered tags above (③.1…③.9, ⑤.1…⑤.3) are a **navigation aid for authors**, not a
> literal reader-facing heading style requirement — `report-presentation.md`'s clean-copy
> heading map (İç SR Bölüm → Clean-Copy Başlık Eşlemesi) renders each as a natural-language
> Turkish heading. The tool-annotated arrows (`← prisma-protocol.md §3`) are **authoring
> provenance only** and never reach the reader-facing body.

**Optional enrichment appendices** (therapeutic-area/drug/regulatory/HTA/Türkiye/KOL/
epidemiology — Adım 0.5 modules) are **not** part of ①–⑧. When a module fires, its output is
appended **after** ⑧ as a clearly labelled, separately headed appendix (e.g. "Ek A — İlaç
İstihbaratı ve Ticari Görünüm (0.5.I)"), so the core SR report remains PRISMA-conformant and
comparable across reviews regardless of which optional modules happened to fire. Never
splice enrichment content into ①–⑧ as if it were core PRISMA machinery.

---

## 2. Format Classes A–I (adaptive — inflects ⑤ Bulgular, not the ①–⑧ skeleton)

The eight-section skeleton (§1) is invariant; the *emphasis within* ⑤ Bulgular and which
optional appendices are likely adapts to query intent. Select the class that matches intent;
sub-sections of ⑤ may be reordered/weighted to fit, but ①–④/⑥–⑧ retain their SR shape.

| Class | Intent | ⑤ Bulgular emphasis |
|---|---|---|
| **A** Evidence synthesis | "what does the evidence say about X" | Outcome-by-outcome results lead; ⑥ SoF table is the centerpiece |
| **B** Drug profile | single drug/asset | Mechanism → trials → regulatory → TR access, inside ⑤; drug-intelligence appendix likely |
| **C** Comparative / head-to-head | X vs Y | Matched-endpoint comparison sub-section + indirect-comparison caveat in ⑤ |
| **D** Landscape / competitive intel | indication or class peyzajı | Pipeline/positioning sub-section in ⑤; drug-intelligence appendix |
| **E** Regulatory dossier | ruhsat/approval status | Milestone timeline sub-section in ⑤; regulatory appendix |
| **F** HTA / access | reimbursement, ICER | Economic-model sub-section in ⑤; HTA appendix |
| **G** KOL map | who are the experts | KOL/network sub-section in ⑤ (optional appendix, not core) |
| **H** Patent / IP | FTO, landscape | Out of scope for the SR core — handoff note to `pharmapatent` in ⑦ |
| **I** Epidemiology | incidence/prevalence/burden | Epidemiology/burden sub-section anchors ⑤; epidemiology appendix |

---

## 3. Epidemiology sub-section (0.5.K, when the axis fires)

When the epidemiology enrichment module fires, its content lands inside **⑤ Bulgular** as a
named sub-section ("Epidemiyoloji ve Hastalık Yükü") and/or the labelled epidemiology
appendix (§1) — never as a standalone numbered core section:
- **US surveillance (v8.5)** — `PopHIVE` (`get_current_status`/`get_trend`/`get_map`/`get_coverage`/`compare`):
  US disease activity (ED/hospitalization/wastewater/lab) + childhood vaccination coverage. **Relay
  the precomputed evidence verbatim — never re-derive the numbers. US-ONLY.**
- **Global / Türkiye burden** — **no native API → documented gap (VERİ YOK)**, never web-scraped or
  fabricated. TR substitutes: TİTCK + EPMC `AFF:"Turkey"` + YÖK Tez.
- **Coding** — ICD-11 via **`openfda:icd11_search`** for the condition code(s) (never
  `med-terminologies.icd11_search`).
- **Denominator role** — explicitly connect the epidemiologic denominator to HTA budget-impact
  (§F) and rare-disease prevalence (`rare-disease-layer.md`) when those axes co-fire.
- **Gap note** — Turkish incidence/registry-coverage availability feeds ⑦ Kısıtlılıklar.

---

## 4. `.data.json` Sidecar Schema (v9.0 — PRISMA union schema)

Machine-readable sidecar consumed by carbon-html-report / carbon-pptx / pharmaintel /
pharmapatent / onko-erisim / saglik-sigorta / the Task-18 eval harness. The schema is the
**union of every phase artefact** already defined in the P0–P7 phase files — key names below
are copied **verbatim** from their defining file; this file does not re-specify or diverge from
those shapes, it only assembles them.

```jsonc
{
  "schema": "medical-research.sidecar.v9",
  "query": "<original question>",
  "review_type": "systematic | scoping | rapid",
  "modules_active": ["0.5.A", "0.5.I", "..."],   // optional enrichment modules that fired

  "prisma_flow_counts": {           /* == screening_log, restated as PRISMA flow-diagram
                                        box counts — see prisma-reporting.md §1 */
    "identified": 0, "identified_other_sources": null, "deduplicated": 0,
    "title_abstract_screened": 0, "excluded_title_abstract": [ {"reason_category": "", "count": 0} ],
    "full_text_assessed": 0, "excluded_full_text": [ {"reason_category": "", "count": 0} ],
    "maybe_resolved_to_include": 0, "maybe_resolved_to_exclude": 0,
    "included": 0 },

  "eligibility_criteria": { /* verbatim from prisma-protocol.md §5 `protocol.eligibility_criteria` */
    "design": { "include": [], "exclude": [] },
    "population": { "include": [], "exclude": [] },
    "language": { "include": [], "exclude": [] },
    "year": { "include": "YYYY-YYYY", "exclude": "" },
    "publication_type": { "include": [], "exclude": [] } },

  "search_strategy": { /* verbatim from search-strategy.md §5 */
    "concepts": {}, "databases": [ { "name": "", "tool": "", "query_string": "",
      "filters_applied": [], "run_date": "YYYY-MM-DD", "result_count": 0 } ],
    "gaps": [] },

  "screening_log": { /* verbatim from screening.md §5 — canonical source of prisma_flow_counts above */
    "identified": 0, "deduplicated": 0, "title_abstract_screened": 0,
    "excluded_title_abstract": [ {"reason_category": "", "count": 0} ],
    "full_text_assessed": 0,
    "excluded_full_text": [ {"reason_category": "", "count": 0} ],
    "maybe_resolved_to_include": 0, "maybe_resolved_to_exclude": 0,
    "included": 0 },

  "evidence_table": [ /* verbatim from data-extraction.md §5 */
    { "study_id": "", "citation": { "author": "", "year": 0, "pmid": "", "doi": "", "nct": null },
      "design": "RCT|cohort|case-control|diagnostic-accuracy|cross-sectional",
      "n_total": 0, "n_arms": [], "population": "", "intervention": "", "comparator": "",
      "outcomes": [ { "outcome_name": "", "effect_measure": "", "effect_size": null,
        "ci_95": [null, null], "unit": "", "source_chunk": {"doc_id": "", "idx": 0, "score": 0.0},
        "verified": false, "note": "" } ],
      "follow_up": "", "funding": "", "coi": "", "human_approved": false } ],

  "rob_assessments": [ /* verbatim from risk-of-bias.md §4 */
    { "study_id": "", "design": "", "tool": "RoB2|ROBINS-I|QUADAS-2|NOS|PROBAST|AMSTAR-2",
      "domains": [ { "domain_name": "", "judgement": "", "signalling_notes": "",
        "source_citation": "", "human_approved": false } ],
      "nos_stars": { "selection": 0, "comparability": 0, "outcome_exposure": 0, "total": 0 },
      "overall_judgement": "", "overall_rationale": "", "human_approved": false } ],

  "grade_sof": [ /* verbatim from prisma-reporting.md §5 — the canonical grade_sof shape;
                     evidence-grading.md §8 defines the per-outcome domain reasoning that
                     populates it, but does not re-specify the shape */
    { "outcome_name": "", "n_studies": 0, "n_participants": 0,
      "effect_measure": "HR|OR|RR|MD|...", "effect_size": null, "ci_95": [null, null],
      "certainty": "⊕⊕⊕⊕ High|⊕⊕⊕◯ Moderate|⊕⊕◯◯ Low|⊕◯◯◯ Very low",
      "downgrade_reasons": ["risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias"],
      "importance": "critical|important|not_important",
      "plain_language_summary": "" } ],

  "enrichment_payloads": {    /* only keys for modules that actually fired (Adım 0.5) are present */
    "therapeutic": { /* per active specialty layer, e.g. oncology-layer.md §5 output block */ },
    "drug":        { /* REAL AdisInsight fields: development_phases[], history_events[],
                         brand_names[], organizations[], is_orphan_drug, adis_insight_profile_url */ },
    "regulatory":  { /* agency milestone timeline: {agency, milestone, date, status, source} */ },
    "hta":         { /* {body, decision, icer, qaly, date} rows */ },
    "turkiye":     { /* native TİTCK: barcode, atc, reimbursement_status, reference_status,
                         price{firm,depot,pharmacy,retail,eur,valid_from}, biosimilar_group[] */ },
    "kol":         { /* ranked author/network table: OpenAlex → S2 → EPMC → NPI/YÖK Akademik */ },
    "epidemiology":{ /* PopHIVE US surveillance (relayed) + ICD-11 codes (openfda);
                         global/TR burden = documented gap */ }
  },

  "sources_summary": { "connectors_used": [ /* verified connector names */ ],
                        "n_calls": 0, "gaps": [ /* sources that returned null + queries */ ] }
}
```

**Field integrity / no-divergence rule:** every top-level key above is **owned** by its
defining phase file (`eligibility_criteria` → `prisma-protocol.md` §5; `search_strategy` →
`search-strategy.md` §5; `screening_log` → `screening.md` §5; `evidence_table` →
`data-extraction.md` §5; `rob_assessments` → `risk-of-bias.md` §4; `grade_sof` →
`prisma-reporting.md` §5). This file assembles the union and must **never** introduce a
divergent key name, field, or shape for a key that already has a canonical definition
elsewhere — if a phase file changes its schema, this file's copy is updated to match, not
the other way around. `prisma_flow_counts` is a display-oriented restatement of
`screening_log` for direct flow-diagram consumption (`prisma-reporting.md` §1); the two are
kept identical — `screening_log` is the phase-owned canonical record.

`enrichment_payloads.drug` uses the REAL AdisInsight schema (never the deprecated
Springer-API fields). `enrichment_payloads.turkiye` uses the TİTCK master record as
authoritative (note ATC duality master vs. detailed_price_list). `sources_summary.connectors_used`
lists only connectors that actually returned data, with a `gaps[]` array for those that did not.

---

## 5. Emission discipline

- File-based report → Markdown `.md` in outputs; run `report-presentation.md` finalization gate
  G1–G8 first (G8 = PRISMA-checklist completeness pass, `report-presentation.md` Nihai Doğrulama
  Kapısı); carry all viz directives in `<!-- VIZ -->` and all telemetry in `<!-- OPS -->`.
- carbon-html-report consumes-and-strips VIZ/OPS comments and maps info-box labels to Carbon
  callouts; it does **not** re-author content.
- Turkish number locale (decimal comma); Vancouver references (PMID/DOI/NCT + access date).
- The included/excluded reference lists required by ⑧ are generated from `screening_log`
  (`included` studies get full Vancouver entries; a representative sample or full list of
  full-text–excluded studies is given with their `reason_category`, per PRISMA 2020 item 9's
  reporting expectation) — never fabricated or silently truncated without a "see full exclusion
  list in Ops annex" note when very large.
