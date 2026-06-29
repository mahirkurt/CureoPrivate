# Output Templates & Data Sidecar Schema (v8.2)

**Loaded:** ALWAYS (Phase 5 — Output Generation).
**Recreated v8.2.0 (UP-001):** referenced as always-load but absent after the v8.0→v8.1 partial
migration; reconstructed from the SKILL.md §3 Output Contract and the manifest `produces` block.

**Scope split (v8.1):** this file governs **scope & format** (which sections, which format
class). `report-presentation.md` governs **presentation** (clean-copy doctrine, anti-leakage,
VIZ/OPS isolation). Both are always-loaded; read both before emitting a file-based report.

---

## 1. Section Contract (research completeness — internal scaffold)

All applicable sections present; missing data = **"VERİ BULUNAMADI"** (never silently omitted).
Core §1–10 always; specialty §11–18 when a 0.5 axis is active; §19 (0.5.I); §20 cross-layer;
§21 (0.5.K).

```
## 1. Küresel Literatür (PubMed + Europe PMC)
## 2. Klinik Pipeline (ClinicalTrials.gov v2)
## 3. Mekanizma & Farmakoloji (ChEMBL + PubChem)              ← drug axis
## 4. Ruhsat & Etiket (openFDA drugsfda/label + DailyMed + EMA) ← drug axis
## 5. Türkiye Verileri (TİTCK + Mevzuat + YÖK + AFF:"Turkey")
## 6. Çok Dilli Kapsama — 6 ülke AFF matriksi
## 7. Tier 0 Sentez (SR + Cochrane + Epistemonikos)
## 8. KOL Haritası (OpenAlex → S2 → EPMC → NPI [US] + YÖK Akademik [TR])
## 9. Kılavuz Yerleşimi (NICE + ESMO + NCCN + specialty societies)
## 10. Açık Erişim & Tam Metin (EPMC copyright_status + annas + Unpaywall + DOAJ)
## 11–18. Specialty extended sections (per active 0.5 layer)
## 19. Drug Intelligence Pipeline Snapshot (0.5.I)
## 20. Cross-Layer Integration Notes
## 21. Epidemiyoloji / Hastalık Yükü (0.5.K — ICD-11 via openfda + US surveillance via PopHIVE; global/TR burden = documented gap)
```

> The tool-annotated headings above are the **internal scaffold**. For file-based reports,
> Phase 5 maps this coverage into a journal-style **clean copy** per `report-presentation.md`
> (scaffold→heading map there); tooling annotations never reach the reader-facing body.

---

## 2. Format Classes A–I (adaptive)

Select the format that matches the query intent; sections from §1 may be reordered to fit.

| Class | Intent | Lead structure |
|---|---|---|
| **A** Evidence synthesis | "what does the evidence say about X" | IMRaD-thematic; GRADE SoF table |
| **B** Drug profile | single drug/asset | mechanism → trials → regulatory → TR access → pipeline |
| **C** Comparative / head-to-head | X vs Y | matched-endpoint comparison + indirect-comparison caveats |
| **D** Landscape / competitive intel | indication or class peyzajı | pipeline table + positioning |
| **E** Regulatory dossier | ruhsat/approval status | milestone timeline (FDA/EMA/TİTCK) |
| **F** HTA / access | reimbursement, ICER | model summary + budget impact + SUT status |
| **G** KOL map | who are the experts | ranked author table + network note (US NPI + TR YÖK Akademik) |
| **H** Patent / IP | FTO, landscape | claims + family + SPC (Türk Patent) — handoff to pharmapatent |
| **I** Epidemiology | incidence/prevalence/burden | §21 block as the spine |

---

## 3. §21 Epidemiology Block (0.5.K)

When the epidemiology axis fires, emit a dedicated block:
- **US surveillance (v8.5)** — `PopHIVE` (`get_current_status`/`get_trend`/`get_map`/`get_coverage`/`compare`):
  US disease activity (ED/hospitalization/wastewater/lab) + childhood vaccination coverage. **Relay the
  precomputed evidence verbatim — never re-derive the numbers. US-ONLY.**
- **Global / Türkiye burden** — **no native API → documented gap (VERİ YOK)**, never web-scraped or
  fabricated. TR substitutes: TİTCK + EPMC `AFF:"Turkey"` + YÖK Tez. (Legacy `who_gho_query` and
  `GLOBOCAN via Exa` are removed — web tier gone v1.4.0.)
- **Coding** — ICD-11 via **`openfda:icd11_search`** for the condition code(s) (D6: never `med-terminologies.icd11_search`).
- **Denominator role** — explicitly connect the epidemiologic denominator to HTA budget-impact
  (§F) and rare-disease prevalence (§ rare-disease-layer) when those axes co-fire.
- **Gap note** — Turkish incidence/registry-coverage availability (feeds Phase 4 gap analysis).

---

## 4. `.data.json` Sidecar Schema (v8.0)

Optional machine-readable sidecar consumed by carbon-html-report / carbon-pptx / pharmaintel /
pharmapatent / onko-erisim / saglik-sigorta. Top-level keys:

```jsonc
{
  "schema": "medical-research.sidecar.v8",
  "query": "<original question>",
  "axes_active": ["0.5.A", "0.5.I", "..."],
  "evidence_table":   [ /* {source_id, type, n, endpoint, effect, ci, tier, grade} */ ],
  "trial_table":      [ /* {nct, phase, status, sponsor, arms, primary_endpoint} */ ],
  "guideline_table":  [ /* {society, version, date, recommendation, class, loe} */ ],
  "regulatory_table": [ /* {agency, milestone, date, status, source} */ ],
  "hta_table":        [ /* {body, decision, icer, qaly, date} */ ],
  "specialty_payload":   { /* per active layer */ },
  "pipeline_payload":    { /* REAL AdisInsight fields: development_phases[], history_events[],
                              brand_names[], organizations[], is_orphan_drug, adis_insight_profile_url */ },
  "turkey_access_summary": { /* native TİTCK: barcode, atc, reimbursement_status, reference_status,
                               price{firm,depot,pharmacy,retail,eur,valid_from}, biosimilar_group[] */ },
  "epidemiology_payload":  { /* PopHIVE US surveillance (relayed) + ICD-11 codes (openfda); global/TR burden = documented gap */ },
  "sources_summary":     { "connectors_used": [ /* verified connector names */ ],
                            "n_calls": 0, "gaps": [ /* sources that returned null + queries */ ] }
}
```

**Field integrity:** `pipeline_payload` uses the REAL AdisInsight schema (never the deprecated
Springer-API fields). `turkey_access_summary` uses the TİTCK master record as authoritative
(note ATC duality master vs. detailed_price_list). `connectors_used` lists only connectors that
actually returned data, with a `gaps[]` array for those that did not.

---

## 5. Emission discipline
- File-based report → Markdown `.md` in outputs; run `report-presentation.md` finalization gate
  G1–G7 first; carry all viz directives in `<!-- VIZ -->` and all telemetry in `<!-- OPS -->`.
- carbon-html-report consumes-and-strips VIZ/OPS comments and maps info-box labels to Carbon
  callouts; it does **not** re-author content.
- Turkish number locale (decimal comma); Vancouver references (PMID/DOI/NCT + access date).
