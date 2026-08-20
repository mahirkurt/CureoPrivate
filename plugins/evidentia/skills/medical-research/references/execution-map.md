# Execution Map — Ordered PRISMA Tool Playbook (v9.0.6)

**Loaded:** before the first MCP call of a review (P1+). Completeness Gate v2 re-reads this
file. **Binding:** which connector fires, in which order, for what purpose is decided
here — not by convenience. Silent skip is a gate failure.

**Fleet SSOT:** `../../fleet.yaml` → **20 servers** (11 gated / 9 public) + **13 companions**
(account-level; not in `.mcp.json`; Cursor may not load them). No mevzuat MCP.

**Claude vs self-host (prefer wired fleet when both exist):**

| Need | Prefer (bundled / operator fleet) | Claude companion when |
|---|---|---|
| PubMed / EPMC / Unpaywall | `pubmed-epmc` (HP self-host) | HCLS PubMed loaded → supplement `search_articles` / `get_full_text_article`; else `pubmed-epmc` alone |
| ClinicalTrials.gov | — (not in `.mcp.json`) | Clinical Trials companion (`search_trials`, …) |
| bioRxiv / medRxiv | Hub stdio `biorxiv-mcp` if rxpraxis/Cursor session wires it | Claude Directory bioRxiv; if HCLS `search_preprints` empty-body bug → stdio Hub drop-in |
| Consensus | `plugin-vekayinuvis-consensus` if session has it | Claude Directory Consensus |
| Elicit / Scite | — | Directory/OAuth companions only; unloaded → `companion_unloaded` |
| AdisInsight | — | OAuth companion; drug-intel (0.5.I) only |
| SNOMED CT | `med-terminologies` (MeSH/ICD-11/ATC primary; SNOMED if Snowstorm creds) | SNOMED CT Terminology companion for validate/expand when Claude connector loaded |
| BioRender | — | P7 visuals only; never evidence retrieval |

**Duty codes**

| Code | Meaning |
|---|---|
| **MUST** | Fire this step. Skip only with a `SKIP-REASON` in the Ops sidecar. |
| **SHOULD** | Fire when the connector is reachable this session. Unreachable → `SKIP-REASON`. |
| **MAY** | Fire only when Adım 0.5 flags the matching enrichment module. No signal → `SKIP-REASON enrichment_off` (logged, not a gap). |
| **OUT** | Out of scope for this phase. Do **not** call. Log `SKIP-REASON out_of_scope` once per server per run if the Completeness Gate asks. |

## Skip-reason template (mandatory when a MUST/SHOULD/MAY step does not run)

```
SKIP-REASON: server=<fleet-or-companion> phase=P<n> duty=<MUST|SHOULD|MAY>
  code=<unreachable|companion_unloaded|enrichment_off|out_of_scope|copyright_gate|auth_required|us_only_mismatch|not_cancer|no_drug_context|already_canonical|operator_oauth|challenge_required>
  note=<one line — queries attempted or why>
```

Do **not** invent a result. `companion_unloaded` is honest (directory/OAuth; not bundled).
`enrichment_off` is a de-skew decision, not a coverage hole.

---

## Fleet → phase map (every server appears)

| # | Server (bundled) | Home phase | Duty | Purpose |
|---|---|---|---|---|
| 1 | `openalex` | P1.1 | MUST | Works/authors/topics discovery + name resolve |
| 2 | `pubmed-epmc` | P1.2 | MUST | MeSH + PubMed/EPMC search; P4 Tier 1/7 full-text |
| 3 | `semantic-scholar` | P1.3 | MUST | Citation graph / influential citations (secondary) |
| 4 | `evidentia-kb` | P0/Adım 0.4 | SHOULD | Skill-routing booster (`kb_search`); never a gate |
| 5 | `marmara-ebsco` | P4.T3 | MUST* | Licensed full-text FIRST (VETİS EBSCOhost; before OpenAthens/annas) |
| 6 | `openathens` | P4.T4 | MUST* | Licensed full-text SECOND (Millet Kütüphanesi; before Wiley/annas) |
| 7 | `annas-reader` | P4.T6 | MUST* | Last-resort grey full-text after licensed band |
| 8 | `anamnesis` | P4+P6 | MUST* | Exclusive-run RAG (`evidentia:run:<id>` + `evrun:`) |
| 9 | `openfda` | P4/P7 | MAY 0.5.C/K | FDA label/FAERS/enforcement + ICD-11 |
| 10 | `ema` | P7 | MAY 0.5.C | EU MA + CHMP/EPAR (native; not a gap) |
| 11 | `titck` | P2/P7 | MAY TR | Türkiye drug index (canonical, gated) |
| 12 | `yok-akademik` | P7 KOL | MAY 0.5.E | TR KOL identity (≠ YÖK Tez) |
| 13 | `pophive` | P7 | MAY 0.5.K | **US-only** surveillance |
| 14 | `who-gho` | P7 | MAY 0.5.K | Global/country burden (incl. `TUR`) |
| 15 | `globocan` | P7 | MAY 0.5.K | Cancer incidence/mortality (modelled + `ui`) |
| 16 | `drugddx` | P4 | MAY 0.5.I | Clinical-DDI label pointer (not a pairwise engine) |
| 17 | `med-terminologies` | P1/P4 | MAY coding | ATC / ICD-10→11 / ICD-11 text (D6 ALLOW) |
| 18 | `nih-clinicaltables` | P4 | MAY coding | `drugs` / `icd10cm` **code→desc** / `conditions` |
| 19 | `nlm-rxnorm` | P4 | MAY 0.5.I | `rxnorm_search` / `rxnorm_get_properties` only |
| 20 | `iuphar-gtopdb` | P4 | MAY 0.5.I | Target/ligand when mechanism is in-question |

\*P4 MUST\* = fire the cascade in order; stop at first success. Later tiers get
`already_canonical`. Anamnesis MUST after any ingested full text (or `SKIP-REASON`
if the Worker is unreachable — then summarise, never dump).

### Companions (13 — not in `.mcp.json`; Cursor may omit them)

| Companion | Home | Duty | Degrade |
|---|---|---|---|
| PubMed (HCLS) | P1.2b | SHOULD | `pubmed-epmc` already covers PubMed/EPMC/Unpaywall |
| Clinical Trials | P1.4 | SHOULD | NCT grey-lit hole → `SKIP-REASON companion_unloaded` |
| bioRxiv / medRxiv | P1.5 | SHOULD | Preprint hole; prefer Hub stdio when wired |
| Consensus | P1.6 | SHOULD | OpenAlex/S2 citation network |
| Paper Search | P1.7 / P4.T2 | SHOULD | EPMC OA + Unpaywall |
| Elicit | P1.8 / P3 | MAY SR-aid | P3 continues native; cross-validate claims |
| Scite | P1.9 / P3 | SHOULD | Primary-source cross-check (DEĞİŞMEZ 4) |
| AdisInsight | P1.10 / P2 / P7 | MAY 0.5.I | drug-intel appendix omitted |
| YÖK Tez | P1.11 | SHOULD | TR thesis hole → Türkiye Veri Boşluğu |
| Wiley | P4.T5 | SHOULD | OAuth; after EBSCO+OpenAthens miss, before annas |
| Literatür | P4 | MAY TR | marmara-ebsco → openathens → annas cascade |
| SNOMED CT Terminology | P4 coding | MAY | `med-terminologies` + `openfda` ICD-11; TİTCK for TR drugs |
| BioRender | P7 visual | MAY | Text-only report; never evidence |

Directory-only (not fleet companions — never invent a prefix): Scholar Gateway, ChEMBL,
NPI, Türk Patent, Synapse, OpenTargets. If present this session, use per
CONNECTORS.md §1.0/§1.2; if absent, `SKIP-REASON companion_unloaded` or documented gap.

---

## P0 — Protocol (no bibliographic fan-out)

1. Classify question type → PICO/PECO/PCC (`prisma-protocol.md`).
2. **SHOULD** `evidentia-kb.kb_search(question, k=8)` and merge sections into
   `coverage_set`. Unreachable → map-only (`SKIP-REASON unreachable`) — **not a gate**.
3. Adım 0.5 enrichment classifier — advisory; default loads **no** domain module.
4. **OUT** for all other 19 bundled servers (protocol does not retrieve).

## P1 — Search strategy + discovery (ordered — do not skip a rung)

**ID-first (context economy):** every discovery call returns **ID + title + year** into the
working-set ledger (`.claude/evidentia-run/<run_id>/ledger.json` + `hits.jsonl`). Do **not**
paste full abstracts/bodies as synthesis input. Prefer small `limit` + field filters; abstract
≤~400 chars only when screening needs it. Bulk dumps ≥8 KB → **synthesis forbidden**
(retrieve-don't-dump) — narrow the query or ingest once.

Execute **in this order**. A later rung may start once the previous rung's first call
is in flight, but the **log order and skip log follow this sequence**. Floor: ≥1 call
per MUST/SHOULD rung (Adım 2 Cömertlik — call or `SKIP-REASON`, not raw-body dump).

| Step | Connector | Tool (verbatim) | Duty |
|---|---|---|---|
| 1.1 | `openalex` | `openalex_resolve_name` → `openalex_search_entities` (+ trends/citation graph if KOL) | MUST |
| 1.2 | `pubmed-epmc` | `pubmed_lookup_mesh` → `pubmed_search_articles` → `pubmed_europepmc_search` | MUST |
| 1.2b | PubMed companion | `search_articles` (+ `get_copyright_status` / `get_full_text_article` when full-text) | SHOULD — else `pubmed-epmc` stands |
| 1.3 | `semantic-scholar` | `search_papers` (then `get_paper` / `get_paper_citations` on keepers) | MUST |
| 1.4 | Clinical Trials companion | `search_trials` | SHOULD |
| 1.5 | bioRxiv / medRxiv companion | `search_preprints` (**preprint flag mandatory**) | SHOULD |
| 1.6 | Consensus | `search` (≤3/batch, usage message verbatim) | SHOULD |
| 1.7 | Paper Search companion | `search` / `search_pubmed` | SHOULD |
| 1.8 | Elicit companion | `search_papers` / `search_trials` (SR-aid; cross-validate DEĞİŞMEZ 4) | MAY |
| 1.9 | Scite companion | Session schema tools (smart citations / evidence sentences) | SHOULD |
| 1.10 | AdisInsight companion | `search_drugs` (real schema — `drug-intelligence-layer.md`) | MAY 0.5.I |
| 1.11 | YÖK Tez companion | `search_yok_tez_detailed` (TR **and** EN) | SHOULD |

**OUT at P1:** `marmara-ebsco`, `openathens`, `annas-reader`, `anamnesis`, `titck`, `yok-akademik`,
`openfda`, `ema`, `pophive`, `who-gho`, `globocan`, `drugddx`, pipeworx trio,
`iuphar-gtopdb` — unless Adım 0.5 already flagged coding/drug and MeSH needs
`med-terminologies.atc_classify` / `map_icd10_to_icd11` (**MAY**, after 1.2).

MeSH/Emtree translation details: `search-strategy.md`.

## P2 — Retrieval & dedup

1. **MUST** execute every P1 `search_strategy.databases[]` row 1:1 (no silent drop).
2. Dedup on PMID/DOI/NCT; write PRISMA `identified` / `deduplicated`.
3. **MAY TR:** `titck.search_drugs` + EPMC `AFF:"Turkey"` when Türkiye module is on.
4. **MAY 0.5.I:** AdisInsight `search_drugs` (real schema — `drug-intelligence-layer.md`).
5. **6-country AFF** (EPMC via pubmed-epmc): Turkey, China, Japan, Germany, Brazil, Korea
   — MUST when geographic breadth is in-question; else `SKIP-REASON out_of_scope`.
6. **OUT:** full-text cascade, RAG, epi/regulatory Workers (those are P4/P7).

Latency: `openfda` never in this parallel burst. Regulatory/FDA calls stay P4/P7, serial.

## P3 — Screening (human-approval checkpoint)

1. Two-stage screen (`screening.md`) against P0 eligibility. **No new bibliographic
   discovery** — use the P2 set.
2. **MAY:** Elicit `search_papers` / `list_reports` and Scite (session schema) as SR-aid only;
   extracted claims are cross-validated (DEĞİŞMEZ 4). Unloaded → `companion_unloaded`.
3. Title/abstract `maybe` → P4 cascade for those records only (not bulk).
4. **OUT:** `evidentia-kb` is Adım 0.4 routing, not paper screening. Do not `kb_search`
   the corpus as if it were MEDLINE.

## P4 — Full-text + extraction (legal-first cascade, stop at first success)

Per included (or `maybe`) record, **in order**:

| Tier | Connector | Tools | Duty |
|---|---|---|---|
| T1 | PubMed / `pubmed-epmc` | `get_copyright_status` / `pubmed_fetch_fulltext` / EPMC `get_full_text_article` | MUST try |
| T2 | Paper Search companion | `read_pubmed_paper` | SHOULD |
| T3 | `marmara-ebsco` | `ebsco_search(query, full_text_only?)` → `ebsco_get(record_id, collection?, doc_id?)` | MUST try |
| T4 | `openathens` | `oa_verify_access` → `oa_fetch_fulltext` (text/RAG; collection?) or `oa_fetch_pdf` | MUST try |
| T5 | Wiley companion | `authenticate` then publisher full-text | SHOULD |
| T6 | `annas-reader` | `article_search`→`read_article`; file: `download_document(id=DOI\|MD5)` | MUST try if T1–T5 failed |
| T7 | `pubmed-epmc` | `pubmed_fetch_fulltext` Unpaywall sweep | MUST try if still empty |

Success at Ti → later tiers `SKIP-REASON already_canonical`. **EBSCO miss/fail/challenge
MUST be logged before OpenAthens** (no silent Tier-3 skip). Copyright gate binds every
tier (`fulltext-retrieval.md`). Do not bulk-download copyrighted PDFs.

**Anamnesis (MUST after any non-short full text):**

```
ingest_document(collection="evidentia:run:<run_id>",
                doc_id="evrun:<run_id>:<PMID|DOI>", text=…, source=<tier>)
hybrid_query(collection="evidentia:run:<run_id>", query=…, queries=[…])
```

Scoped `semantic_search` / `graph_neighbors` / `subgraph` ALLOW. Unscoped hybrid/graph
DENIED (hook). `list_docs(collection=…)` for the working set — **not** `corpus_stats`.
No `doc_scope`. Missing collection → `_legacy` (never use on purpose). Cleanup is the
SessionEnd / next-`/evidentia` hook (`forget_collection`); no Stop-hook forget.

**MAY (only with Adım 0.5 signal), after extraction needs the concept:**

- Coding: `openfda.icd11_search` **or** `med-terminologies.icd11_search` (D6 ALLOW) →
  `med-terminologies.map_icd10_to_icd11` → `nih-clinicaltables.icd10cm` **code→desc only**.
  **SNOMED validate/expand:** SNOMED CT Terminology companion (MAY) when loaded; else
  `med-terminologies` MeSH/ATC + TİTCK SNOMED ids — not a substitute for ICD-11 primary path.
- Drug: `nlm-rxnorm.rxnorm_search` → `rxnorm_get_properties`. **Never** `rxnorm_interactions`
  / `rxnorm_related` (guard D1/D2).
- DDI: `drugddx.normalize_drug` → `interaction_label` (label pointer, not a verdict).
- Mechanism: `iuphar-gtopdb.search_targets`/`search_ligands` + ChEMBL if loaded.
- Pipeworx generics: never (allowlist + PreToolUse guard).

## P5 — Risk of bias (human-approval checkpoint)

1. Pick tool from design (`risk-of-bias.md` matrix). No extra discovery servers.
2. **MUST** if the run corpus is non-empty: `hybrid_query(collection=evidentia:run:<id>,
   queries=["methods","randomisation","blinding","attrition","outcome measurement"])`
   — RoB domains from retrieved methods, not from memory.
3. Empty corpus → extract from abstracts + `SKIP-REASON` (no full text).
4. **OUT:** epi/regulatory/terminology Workers.

## P6 — GRADE

1. Per-outcome certainty from `evidence_table` + P5 (`evidence-grading.md`).
2. **MUST** if corpus non-empty: scoped **multi-query** `hybrid_query` (`queries[]` ≥2) for
   effect estimates / SoF cells (`doc_id::idx` provenance). Single-query synthesis **forbidden**.
3. **MUST before synthesize:** `list_docs(collection=…)` → reconcile with working-set ledger
   (close `missing_extractions`; investigate `orphans`).
4. **OUT:** new bibliographic or regulatory calls (those belong in P1/P2/P7).

## P7 — PRISMA report + optional enrichment appendices

Core report uses artefacts already built. **No new discovery.** Enrichment appendices
only when Adım 0.5 fired:

| Signal | Ordered chain | Duty |
|---|---|---|
| 0.5.C FDA | `openfda.openfda_search` (serial, 1 retry, skippable) | MAY |
| 0.5.C EU | `ema.ema_search_medicines` → `ema_get_medicine` / `ema_filter` | MAY |
| 0.5.K US | `pophive.get_current_status` → trend/map/coverage (**US-only**) | MAY |
| 0.5.K global/TR | `who-gho.who_gho_search_indicators` → `who_gho_query(country=TUR\|GLOBAL)` | MAY |
| 0.5.K cancer | `globocan.gco_resolve_population` → `gco_query` (`ui`+caveat) | MAY |
| TR market | `titck.search_drugs` → `get_drug` → biosimilar/price/off-label | MAY |
| 0.5.E KOL | `openalex` name/graph → `semantic-scholar.get_author` → YÖK Tez → **`yok-akademik.yok_search(term=)`** → NPI if US | MAY |
| 0.5.I DDI | `drugddx` (if not done in P4) | MAY |
| P7 visual | BioRender companion (figure templates — **NOT** evidence) | MAY |

IHME/GBD, society guideline PDFs, Embase/CENTRAL, SUT/legislation: **documented gap**
(no mevzuat MCP — hand off SUT/kanun to `cureolex`). Do not web-scrape.

P7 close: hook prefers `forget_collection`. Do not `forget_document` the world.

---

## Completeness Gate v2 (binds this map)

Before finalising:

1. Every **MUST** row ran **or** has a `SKIP-REASON`.
2. Every bundled server (20) is either used in its home phase, tagged MAY+`enrichment_off`,
   or tagged OUT+`out_of_scope` for that phase. **No silent omission.**
3. Companions: used, or `companion_unloaded` / degrade note.
4. Anamnesis queries (if any ingest happened) used `collection=evidentia:run:<id>`
   and/or `evrun:` `doc_id` — never unscoped hybrid.
5. **Article coverage:** `coverage = cited_or_skipped_with_reason / include_set` from
   `.claude/evidentia-run/<id>/ledger.json`. Floors (Ops): lenient≥0.75, **standard≥0.90**,
   strict≥0.98. Required return block:
   `{n_include, n_cited, n_skipped_reasoned, coverage, uncovered[]}`. Below floor →
   **refuse finalize** (close cites/skips first). Dump used as synth input is a FAIL
   (`dump_used_as_synth_input`). Hook `coverage_gate` advisory; soft DENY only if
   `EVIDENTIA_COVERAGE_ENFORCE=1` (empty include_set never hard-breaks).

Call counts, skip log, and coverage block live in `<!-- OPS -->`, never the clean copy.

## Latency / quota (unchanged)

- `openfda`: serial, 1 retry, skippable.
- OpenAthens batch: defensive pacing (sequential, 20–60 s jitter; per-run 25 / daily 100).
- Consensus: ≤3 calls/batch.
- Bibliographic depth uncapped as **coverage**; raw dump as synth input capped
  (retrieve-don't-dump 3 KB/8 KB; Adım 2).
