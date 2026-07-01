# Drug Intelligence Layer (v8.0 — corrected AdisInsight schema)

**Optional enrichment module** — loaded only when the question's context calls for
drug-intelligence data. NOT mandatory; the core PRISMA pipeline (P0–P7) runs without it.
Output → enrichment appendix.
**Primary connector:** AdisInsight MCP (server `6a9fd4a4…`).
**⚠️ v8.0 CORRECTION:** v7.1 documented a fictional *Springer Pharma API Bundle* schema (`organisations`/`phases`/`indications`/`moas`/`drugClass`/`locations`/`fromDate`/`toDate`). **That schema does not exist on the connected MCP.** This file documents the **real, probe-verified** interface. Any call using the old parameters will fail.

**Companion connectors:** Clinical Trials v2, DailyMed (extended-api), regulatory MCP `openfda_search` (FAERS), EPMC, ChEMBL, `pharmaintel` skill (deeper commercial handoff).

---

## 1. The Real AdisInsight Tool Surface (verified 9 Jun 2026)

| Tool | Purpose | Key parameters (real) |
|---|---|---|
| `search_drugs` | Find drugs + return rich profiles | `drug_name` (PRIMARY), `compound_name`, `brand_name`, `developers`/`developers_any`/`developers_all`, `originators`, `dev_phase`/`dev_phase_any`, `mechanism`/`mechanism_any`, `targets`/`targets_any`/`targets_all`, `drug_class`/`_any`/`_all`, `therapeutic_area`/`_any`, `indication` (via dev_indication), booleans: `is_active`, `is_small_molecule`, `is_biological_class`, `orphan_drug_status`, `fast_track_status`, `btt_status`, `prime_status`, `rmat_status`, `new_molecular_entity`, `is_research_program`; `per_page` (≤100), `page`, `order_by` |
| `get_drug` | Deep single-drug + HyDE chunks | `drug_name` (REQUIRED), `query_text` (HyDE, repeat key terms 8–10×), `resources` (csv), `limit` (10), `min_similarity` (0.2); disambiguation: `developers`, `therapeutic_area`, `dev_phase`, `compound_name` |
| `search_trials` | AdisInsight trial records | `trial_name`, `acronym`, `compound`/`_any`, `indication`/`_any`, `sponsor`/`_any`, `phase`, `status`, `locations`, date ranges (`actual_initiation_start`…), `has_results`, `is_industry_associated` |
| `search_drug_companies` | Companies by drug portfolio | `indication`, `therapeutic_area`, `dev_phase`, `mechanism`, `targets`, `company_name`, `role`, `is_large_pharma` |
| `search_trial_companies` | Companies by trial sponsorship | (trial-perspective analogue) |
| `generate_chart` | Chart.js viz | `entity` ("drugs"/"trials"), `chart.dimensions[]`, `chart.metric{field,aggregation}`, `filters{}`, `limit` |

`get_drug` `resources` vocabulary: `classes, organisations, brand_names, adverse_events, cas_numbers, codes, development_phases, development_history, future_events, licensing_options, orphan_designations`.

**Workflow rule (from MCP instructions):** SEARCH BEFORE GET — `search_drugs` first to get `doc_id`, then `get_drug` for depth. For HyDE you MUST pass `query_text` or you get only basic info (no document chunks).

---

## 2. What `search_drugs` Returns (real profile shape)

One `search_drugs(drug_name="glofitamab")` call returned (verified):
- `doc_id`, `title` ("Glofitamab - Roche"), `compound_name`, `alternative_names` (RG6026, CD20-TCB…).
- `highest_phases[]` — per indication (DLBCL: Marketed; MCL: Phase III; CLL/FL/NHL: Phase II).
- `development_phases[]` — **per-country, per-indication, with `event_date`, `company`, `route`, `patient_segments`** (e.g., Registered DLBCL EU 2025-04-14).
- `history_events[]` — **regulatory milestones**: "ODAC discusses sBLA … 2025-05-20", "Genentech receives **CRL** from FDA … 2025-07-18", STARGLO readout, EU registration. Each `is_significant`/`is_publishable`.
- `brand_names[]` (Columvi, per country/company), `drug_classes[]` (Bispecific antibodies, Recombinant fusion proteins…), `target[]` (CD20, CD3, Cytotoxic T lymphocyte), `mechanism_of_action[]`.
- `organizations[]` — roles: Owner/Originator (Roche), Licensee (Chugai) with `type_is_large_pharma`.
- Flags: `is_orphan_drug`, `is_btt`, `is_prime`, `new_molecular_entity`, `is_biological_class`.
- `adis_insight_profile_url` (canonical link), `modification_date`.

→ The profile already contains regulatory trajectory (CRL, ODAC, registrations) and competitor-relevant class/target metadata **without** the old `fromDate`/`phases` filters. You filter by passing `dev_phase_any`, `mechanism`, `targets`, `therapeutic_area` to `search_drugs`.

---

## 3. Use-Case Patterns (real calls)

### 3.1 Drug Profile Lookup
**Trigger:** query names a specific drug (INN/brand).
```
AdisInsight: search_drugs(drug_name="<INN or brand>", per_page=3)
   → pick doc_id of best match
AdisInsight: get_drug(drug_name="<INN>",
   query_text="<indication> <MoA> efficacy safety regulatory ... (repeat 8-10×)",
   resources="development_phases,development_history,organisations,adverse_events",
   limit=10, min_similarity=0.2,
   developers="<sponsor if known>")
```
Cross-ref: `history_events` PMIDs → EPMC `get_article_metadata`; trial NCTs → CT.gov `get_trial_details`.
Output → `pipeline_payload.drug_profile`.

### 3.2 MoA / Target Landscape (competitor set)
**Trigger:** query names a mechanism or target (BTK, CD20×CD3, GLP-1 RA, KRAS G12C…).
```
AdisInsight: search_drugs(mechanism="<MoA>", dev_phase_any="Phase II,Phase III,Pre-registration,Registered,Marketed",
   therapeutic_area="<TA>", per_page=50)
# OR by target:
AdisInsight: search_drugs(targets="<target>", indication="<indication>", per_page=50)
```
Build a sponsor × phase × latest-milestone × indication table. For oncology, attach ESMO-MCBS/ASCO-VF where available (from oncology-layer).
Output → `pipeline_payload.competitor_landscape`. Optional `generate_chart(entity="drugs", dimensions=["dev_phase"], metric={field:"drug_count",aggregation:"count"}, filters={"mechanism_contains":"<MoA>"})`.

### 3.3 Company Portfolio
**Trigger:** query names a company.
```
AdisInsight: search_drug_companies(indication="<indication>", dev_phase="Phase III", is_large_pharma=true)
AdisInsight: search_drugs(developers="<company>", is_active=true, per_page=100)
```
Cross-use with `pharmaintel` (wider commercial: SEC, earnings, catalysts).

### 3.4 Regulatory Milestone Reconstruction
**Trigger:** "PDUFA", "CHMP opinion", "AA conversion", "withdrawal", "ODD", "approval timeline".
AdisInsight does NOT take a date-range filter on the public MCP. Instead: `search_drugs(drug_name=…)` → read `history_events[]` (already timestamped: CRL, ODAC, registration, withdrawal) and `development_phases[]` (`event_date` per country). Then verify each against the primary source.
Output → `pipeline_payload.regulatory_milestones`.

### 3.5 Trial / Conference / Deal Intelligence
```
AdisInsight: search_trials(compound="<INN>", phase="Phase III", status="Recruiting")
AdisInsight: search_drug_companies(...) # for partnership inference
```
Deal/conference depth on the public MCP is thinner than the curated web product → cross-ref with `pharmaintel` (SEC 8-K, press). If still not recovered, report the deal/conference dimension as a gap (VERİ YOK) — do NOT fabricate. Document gaps explicitly.

---

## 4. Cross-Reference Protocol (unchanged principle, real sources)

| AdisInsight field | Verify with | Method |
|---|---|---|
| `history_events` PMIDs | EPMC `get_article_metadata` | title/authors/journal match |
| trial NCTs | CT.gov `get_trial_details` | phase + sponsor + dates |
| FDA approval/CRL | regulatory MCP `openfda_search(endpoint="drug/drugsfda")` + DailyMed | approval/letter date |
| EMA CHMP/registration | EMA has no native API in this build → not retrievable; report as a gap (VERİ YOK), do NOT fabricate | — |
| Türkiye status | **TİTCK `search_drugs`** (native) | ruhsat + reimbursement |
| AE profile | regulatory MCP `openfda_search(endpoint="drug/event", count=...)` | FAERS PT frequencies (NOT incidence) |
| Mechanism/target | ChEMBL `get_mechanism` / `target_search` | action_type + UniProt |

**Conflict rule:** primary record wins (CT.gov > AdisInsight; FDA drugsfda > AdisInsight; TİTCK > AdisInsight for Türkiye). Flag in output: `discrepancy_notes`.

---

## 5. Zero-Result Fallback Chain

1. **Direct:** `search_drugs(drug_name=…)` / `(mechanism=…)` / `(targets=…)`.
2. **Reformulate:** brand↔INN; mechanism parent class; `search_drug_companies` by indication.
3. **Synthesize from primaries:** CT.gov `search_by_sponsor` + DailyMed + openFDA FAERS + `pharmaintel` skill. (EMA has no native API in this build → EPAR not retrievable; report as a gap, do NOT fabricate.)
4. **Document gap:** "AdisInsight returned no curated pipeline data; reconstructed from CT.gov + DailyMed + FAERS — EMA/EPAR and deals/conference dimensions not recovered (VERİ YOK), not fabricated."

---

## 6. `pipeline_payload` Sidecar (v8.0 — real fields)

```json
{
  "pipeline_payload": {
    "schema_version": "v8.0",
    "trigger_axis": "0.5.I",
    "primary_source": "AdisInsight",
    "adis_profile_url": "https://adisinsight.springer.com/drugs/<doc_id>",
    "fallback_used": null,
    "drug_profile": {
      "drug_name": "<INN>", "doc_id": "<id>", "brand_names": ["..."],
      "sponsor": "<Owner/Originator>", "drug_class": ["..."],
      "moa": ["..."], "target": ["..."],
      "highest_phases_by_indication": [{"indication":"...","phase":"..."}],
      "regulatory_history": [{"type":"CRL|ODAC|Registered|Withdrawal","date":"YYYY-MM-DD","comment":"...","country":"..."}],
      "flags": {"orphan":true,"breakthrough":true,"prime":false,"nme":true},
      "approval_status": {"fda":{...},"ema":{...},"titck":{"approved":false,"source":"TİTCK native"}},
      "verification": "cross-validated | AdisInsight only"
    },
    "competitor_landscape": [{"drug_name":"...","sponsor":"...","phase":"...","moa":"...","target":"...","indication_match":"exact|adjacent","esmo_mcbs":"...","verification":"..."}],
    "regulatory_milestones": [{"drug_name":"...","agency":"FDA|EMA|TİTCK","milestone_type":"...","date":"YYYY-MM-DD","outcome":"...","verification":"..."}],
    "deals": [{"date":"...","deal_type":"...","parties":["..."],"asset":"...","value_usd_millions":0,"verification":"SEC 8-K|press|AdisInsight only"}],
    "conference_coverage": [{"conference":"ASCO|ESMO|ASH|EHA|...","year":2026,"drug_name":"...","abstract_count":0,"key_themes":["..."],"kol_authors":["..."]}],
    "charts": [{"type":"adisinsight_generate_chart","spec":"<chart.js config>"}],
    "data_gaps": ["..."]
  }
}
```

---

## 7. Composition with Sister Skills
- **pharmaintel** — AdisInsight = curated subset; pharmaintel adds SEC/earnings/catalyst breadth. Sequence: medical-research (evidence + curated intel) → pharmaintel (commercial layer).
- **pharmapatent** — `competitor_landscape` → FTO/invalidity/biosimilar-entry (Markush, SPC). Use TÜRKPATENT for TR IP.
- **onko-erisim** — oncology pipeline + `drug_profile.approval_status` → SGK ödeme petition (NCCN/ESMO + Anayasa 17/56). Pull TİTCK reimbursement natively.
- **saglik-sigorta** — label/indication + TİTCK price → tıbbi gereklilik defense.
- **carbon-html-report / carbon-pptx** — `pipeline_payload` + `generate_chart` → enrichment appendix Pipeline Snapshot + milestone timeline.
- **talent-praetor** — `conference_coverage.kol_authors` → KOL graph → senior MSL/RWE Lead competency model.

---

## 8. Known Pitfalls (v8.0)
1. **Never use the v7.1 parameters** (`organisations`/`phases`/`moas`/`drugClass`/`locations`/`fromDate`/`toDate`). They do not exist.
2. `get_drug` without `query_text` → no document chunks (basic info only).
3. AdisInsight public MCP has no date-range filter — read timestamps from `history_events`/`development_phases` instead.
4. Türkiye data thin in AdisInsight → **TİTCK native is authoritative** for TR.
5. Deal/conference depth thinner than the curated web product → cross-ref pharmaintel; if not recovered, report as a gap (VERİ YOK), do NOT fabricate; document gaps.
6. `search_drugs` `per_page` ≤ 100; paginate for large MoA landscapes.
7. Disambiguate generics with `developers`/`therapeutic_area`/`dev_phase` on `get_drug`.

---

*v8.0 — schema verified against live `search_drugs("glofitamab")` and `get_drug`/`search_drug_companies`/`generate_chart` tool definitions, 9 June 2026.*
