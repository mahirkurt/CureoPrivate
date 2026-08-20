---
name: medical-research
description: >
  General-purpose medical literature review engine. Runs an end-to-end PRISMA 2020 /
  PRISMA-ScR systematic or scoping review across all of medicine and every question type
  (therapy, diagnosis, prognosis, etiology, prevention): protocol + PICO/PECO, search
  strategy (MeSH/Emtree), retrieval + dedup, title/abstract + full-text screening, data
  extraction, risk of bias (RoB2/ROBINS-I/QUADAS-2), GRADE certainty, and a clean Turkish
  PRISMA report (flow diagram + Summary-of-Findings). Optional, context-triggered
  enrichment modules (therapeutic-area, drug/regulatory, HTA, Türkiye market, epidemiology)
  fire only on in-question context, never the default. Pure structured evidence; no
  web/OSINT tier; no fabrication. Use for ANY literature review, systematic review, scoping
  review, evidence synthesis, or PICO request. Triggers: literatür derleme, sistematik
  derleme, kapsam derleme, PRISMA, PICO, PECO, screening, risk of bias, GRADE, kanıt
  sentezi, meta-analiz, dahil hariç kriterleri.
metadata:
  version: 9.0.7
---

> ## 🧩 Plugin entegrasyon notu (evidentia)
>
> Bu skill, **`evidentia`** plugin'inin flagship'i olarak paketlenir. Süit bağlamında
> aşağıdaki iki dosya **normatiftir** ve connector/orkestrasyon kararlarını **bağlar**:
> - [`../../CONNECTORS.md`](../../CONNECTORS.md) — connector envanteri, native-first fallback
>   merdivenleri, güven katmanı ve **claude.ai ⇄ Claude Code yüzey ayrımı** için **tek doğruluk
>   kaynağı**. Skill içi `references/connector-registry.md` standalone kullanım için korunur;
>   çakışmada `CONNECTORS.md` üstündür.
> - [`../../shared/canonical-cache-contract.md`](../../shared/canonical-cache-contract.md) —
>   **tek-sefer fetch / kanonik artefakt** disiplini (TİTCK tek-sefer kuralı; openfda
>   tekil+retry+skippable; **working_set_ledger** + `hits.jsonl`). Connector **sırası**>   `references/execution-map.md` playbook'udur.
>
> **Sürüm/ad:** Skill kanonik adını (`medical-research`) korur (ADR-05); sürüm **9.0.7**
> (v9 = 10-eksen zorunlu yükleyici → **P0–P7 PRISMA hattı + opsiyonel zenginleştirme sınıflandırıcısı**;
> web tier / OSINT ekseni kaldırılmıştı — saf yapısal-kanıt korunur; 9.0.5 = P0 ledger/dump;
> 9.0.6 = Anamnesis reconcile + multi-query hybrid + coverage gate; 9.0.7 = working-set ledger per-hit title binding + EBSCO/reconcile anamnesis_doc_id fix).
> Plugin sürümü skill'den ayrıdır.

# ⚠️ MANDATORY EXECUTION PROTOCOL — v9.0.7 (medical-research)

**This block is read and applied before any other structure. It runs on every invocation.**

**v9 headline:** The core is a **PRISMA 2020 / PRISMA-ScR pipeline (P0→P7)**. Every review runs
the same eight phases regardless of subject. The former "10-axis" domain matrix is now an
**OPTIONAL, context-triggered enrichment layer** (Adım 0.5) — **the default review path loads NO
domain layer.** Backbone doctrines are preserved and rewired onto the phases:
**native-MCP-first** resolution (native MCP → Python REST → documented gap; no web tier),
**clean-copy** presentation, **retrieve-don't-dump** (surface every loaded detail — never as
raw synth input over the dump threshold), **no-fabrication** (no-API sources → documented gap),
**Cömertlik** (depth ≠ dump; MUST = call or `SKIP-REASON`), and the
**tek-sefer / kanonik-önbellek** contract.

## Adım 0: Mandatory Loading

Every invocation FIRST loads these always-load reference files (progressive disclosure DISABLED
for them):
```
view references/knowledge-map.md         # semantic coverage index — drives Adım 0.4 routing
view references/connector-registry.md    # verified tool table + native-first ladder
view references/evidence-grading.md      # GRADE / Tier 0–6 — used at P6
view references/output-templates.md      # SR/ScR output structure + sidecar — used at P7
view references/report-presentation.md   # clean-copy doctrine — used at P7
view references/prisma-reporting.md       # PRISMA flow diagram + SoF + checklist — P7
```
Phase files `prisma-protocol.md` (P0), `search-strategy.md` (P1), `execution-map.md` (P2
ordered tool playbook — **load before the first MCP call**), `screening.md` (P3),
`data-extraction.md` (P4), `risk-of-bias.md` (P5) are loaded **per-phase**. Optional
enrichment modules load only per Adım 0.5.

## Adım 0.1: Project Settings (if present)

If a `.claude/evidentia.local.md` file exists in the project root, **Read it** and apply its
YAML frontmatter before proceeding:
- `enabled: false` → ignore the settings file; run with defaults.
- `known_connected: [...]` → treat these connectors as available; do not re-probe them in P2.
- `default_modules` → if non-empty, seed these OPTIONAL enrichment modules into the Adım 0.4
  routing set (the scan may add more; the user's explicit intent overrides). This is a
  per-run enrichment hint — it does **not** make any module mandatory.
- `fulltext_tier: off` → skip the annas-reader full-text rung in P2/P4; `copyright_gated`
  (default) keeps the copyright gate on the cascade (`fulltext-retrieval.md`).
- `completeness_gate: lenient|standard|strict` → tune the Completeness/G-COVERAGE strictness.
- `auto_ingest_rag: true` → ingest long fetched documents into the `anamnesis` RAG substrate
  before synthesis. **Exclusive working set (dual-write):** `collection=evidentia:run:<run_id>`
  AND prefix every `doc_id` `evrun:<run_id>:` (SessionStart injects both). Scoped
  `hybrid_query`/`semantic_search`/`graph_*` are allowed; unscoped hybrid/graph/global search
  is denied. Hooks prefer `forget_collection` on SessionEnd / next `/evidentia` (no Stop-hook forget).

Absent the file, behave with defaults (no enrichment module active).

## Adım 0.4: Semantic Scope Scan (MANDATORY — runs before 0.5)

Using `references/knowledge-map.md`, scan the question by MEANING, not keywords, and route it:

1. Decompose the question into its concept set: population/condition · intervention/exposure ·
   comparator · outcome · study-design · geography · evidence-type · full-text/KOL need.
2. **Route to PHASE files first** — every review maps to the P0–P7 spine below; the map's phase
   block resolves which phase reference files the question needs.
3. **Then map OPTIONAL enrichment modules** — for each concept, resolve any relevant enrichment
   section via the knowledge-map Inverted Map (module-index). A concept maps by semantic
   relatedness even when its trigger words are absent. These are candidates for Adım 0.5, not
   auto-loads.
4. (Booster, optional) If `kb_search` is reachable, call `kb_search(question, k=8)` and merge
   its returned sections into the routing set. If unreachable, continue map-only.
5. Emit `coverage_set` = phases + candidate modules into the invisible Ops/Layer-B sidecar
   (NOT the clean copy). This is the auditable coverage trail.

## Adım 0.5: Optional Enrichment Classifier (NON-mandatory)

> **No enrichment module is mandatory or always-on; the core PRISMA pipeline (P0–P7) runs
> regardless.** This step is a context scan that MAY activate enrichment modules when — and only
> when — the question's context calls for them. The **default review path loads NO domain layer.**

Query text is scanned (full-word + stem match) against the enrichment module dictionaries. A
signal is **advisory**: it flags the module as a candidate and injects its extra retrieval into
the P2 list *only if the reviewer confirms the context genuinely needs it*. Modules are
independent; a question may activate several or none. Full keyword dictionaries live in each
module file (progressive disclosure).

| Enrichment module (optional) | Representative context triggers | Module file |
|---|---|---|
| Oncology (0.5.A) | tümör-specific staging/response criteria, oncology guideline placement | `oncology-layer.md` |
| Hematology (0.5.B) | heme malignancy classification/risk-stratification specifics | `hematology-layer.md` |
| Regulatory (0.5.C) | approval/label/regulatory-milestone questions | `regulatory-science-layer.md` (+`regulatory-intelligence.md`) |
| HTA / access (0.5.D) | cost-effectiveness, ICER/QALY, reimbursement | `hta-layer.md` (+`regulatory-intelligence.md`) |
| Medical Affairs (0.5.E) | MSL/KOL/advisory-board/compliance framing | `medaffairs-ops-layer.md` |
| Immunology (0.5.F) | immune-mediated disease endpoint/target specifics | `immunology-layer.md` |
| Neurology (0.5.G) | neuro disease-modifying / endpoint specifics | `neurology-layer.md` |
| Rare Disease (0.5.H) | orphan/natural-history/registry-endpoint specifics | `rare-disease-layer.md` |
| Drug Intelligence (0.5.I) | drug/MoA/target/pipeline/deal landscape | `drug-intelligence-layer.md` |
| Türkiye market | TR reimbursement/SUT/native-registry context | `turkiye-layer.md` |
| Epidemiology / Burden (0.5.K) | incidence/prevalence/mortality/disease-burden, US/global/TR | `regulatory-intelligence.md` (ICD-11 via openfda; US = PopHIVE; global/TR = who-gho; cancer = globocan; IHME/GBD still gap) |

**No signal:** the pure PRISMA pipeline runs with the academic core only — no enrichment loaded.

---

## PRISMA Pipeline — Phases P0–P7

The spine of every review. Each phase points at its reference file (progressive disclosure).
P3 and P5 carry a **human-approval checkpoint**.

### P0 — Protocol & PICO/PECO
Frame the review question as PICO/PECO (or PCC for scoping), fix the review type (systematic
vs scoping), eligibility criteria, and pre-register the protocol intent. **`view references/prisma-protocol.md`**.

### P1 — Search Strategy
Build a comprehensive, reproducible search: MeSH/Emtree + free-text, Boolean structure, per-database
translation, date/language limits, grey-literature plan. **`view references/search-strategy.md`**.
Discovery **order** (OpenAlex → pubmed-epmc → Semantic Scholar → CT.gov → bioRxiv →
Consensus/Paper Search → YÖK Tez) is binding in **`references/execution-map.md`**.

### P2 — Retrieval & Deduplication
Execute the P1 strategy **in playbook order** (`execution-map.md`; native-MCP-first;
`connector-registry.md`), capture records with IDs (PMID/DOI/NCT/…), deduplicate, and record
counts for the PRISMA flow. Subject to the **tek-sefer / kanonik-önbellek** contract. Optional
enrichment retrieval (Adım 0.5) is injected here only when a module is active. A MUST/SHOULD
connector that does not run needs a `SKIP-REASON` — never a silent skip.

### P3 — Screening (Title/Abstract → Full-Text)
Two-stage screening against eligibility criteria; log include/exclude with reasons; resolve
conflicts. **`view references/screening.md`**. **Human-approval checkpoint:** surface the
include/exclude set and exclusion reasons for reviewer confirmation before proceeding to P4.

### P4 — Data Extraction
Extract study characteristics + numerical outcomes (effect estimates, CI, p, subgroups, AE) into
a structured extraction table; full-text-enriched where abstract is insufficient (copyright-gated
cascade). **`view references/data-extraction.md`**. When an optional drug/terminology module is
active, the Extended-Tier recipes below fire (each with a cross-validation gate).

### P5 — Risk of Bias
Apply the design-appropriate tool: **RoB2** (RCT), **ROBINS-I** (non-randomized), **QUADAS-2**
(diagnostic accuracy), **Newcastle-Ottawa** (observational). **`view references/risk-of-bias.md`**.
**Human-approval checkpoint:** surface per-study RoB judgments (and domain rationale) for reviewer
confirmation before grading.

### P6 — GRADE Certainty
Rate certainty of evidence per outcome (GRADE / Tier 0–6), downgrade/upgrade with reasons.
**`view references/evidence-grading.md`**.

### P7 — PRISMA Reporting
Assemble the PRISMA 2020 flow diagram, Summary-of-Findings table, and PRISMA/PRISMA-ScR checklist;
render the clean Turkish report. **`view references/prisma-reporting.md`** (+ `output-templates.md`,
`report-presentation.md`).

### Multi-Source Retrieval (P2 — ordered playbook)

Resolve every need by the **Native-First ladder** (native MCP → Python REST → documented gap;
**no web tier**). **Order, duty (MUST/SHOULD/MAY/OUT), and skip codes** live in
`references/execution-map.md` — that file is binding. Use verified tool names from
`connector-registry.md`. De-skew applies ONLY to Adım 0.5 enrichment, NEVER to core discovery.

**A. Academic Core — ALWAYS-ON, ordered (execution-map P1.1→P1.11).** Floor ≥1 call per
MUST/SHOULD rung; unreachable/unloaded → `SKIP-REASON` in OPS, never a silent drop:
`openalex` (resolve_name → search_entities) → `pubmed-epmc` (lookup_mesh → search_articles →
europepmc_search) → `semantic-scholar.search_papers` → PubMed HCLS companion (`search_articles`)
→ Clinical Trials companion `search_trials` → bioRxiv companion `search_preprints` (preprint flag)
→ Consensus `search` (usage message verbatim) → Paper Search → Elicit companion (MAY SR-aid) →
Scite companion (SHOULD; cross-validate) → AdisInsight (MAY 0.5.I) → YÖK Tez. Prefer bundled
`pubmed-epmc` over HCLS PubMed when both loaded (execution-map Claude vs self-host table).

**B. Extended (native MCP first; `requests` fallback)** — ChEMBL (`bio-research:chembl`), EPMC SR
filter (`… AND systematic review[Publication Type]`), PubChem/OpenAlex/DailyMed/Unpaywall/DOAJ/
J-STAGE via REST (`extended-api.md`), native `openfda:openfda_search` (drugsfda + label + FAERS).

**Extended Tier-K — first-class, signal-gated (tool whitelist + cross-validation per `connector-registry.md §2.6`).** Loaded only when an optional drug/terminology module (Adım 0.5) fires (progressive disclosure preserved); each recipe **ends at a cross-validation gate** — patient-impacting output is confirmed against an authoritative source before it is presented (DEĞİŞMEZ 4):
- **Terminology / coding** — `med-terminologies:atc_classify` (drug→ATC) + `med-terminologies:map_icd10_to_icd11` (ICD-10→ICD-11, WHO 2025-01) + `nih-clinicaltables:icd10cm` (**code→description ONLY**) + `nih-clinicaltables:conditions`/`drugs`. **ICD-11 text search** → `openfda:icd11_search` (operator-owned) **or** `med-terminologies:icd11_search` (D6 retired 2026-08-17, live 3B10.0). `nih.icd10cm` name-search still returns 0 (D3). → cross-validate any patient-impacting code against the authoritative coder.
- **Drug normalization / RxCUI** — `nlm-rxnorm:rxnorm_search` (name→SBD/SCD) + `nlm-rxnorm:rxnorm_get_properties`. Brand↔generic → **TİTCK `find_equivalent_products_by_substance`** or `med-terminologies:atc_classify` (D2/D4: `rxnorm_related` 400). **Never call** `rxnorm_interactions` (D1: 404). → cross-validate the normalized concept against TİTCK/DailyMed.
- **Clinical DDI** — `drugddx:normalize_drug` → `drugddx:interaction_label` (DailyMed SPL interaction-section pointer) + DailyMed REST. ⚠️ **label text, NOT a computed pairwise verdict** → confirm interactions with a licensed source (Lexicomp/UpToDate/DrugBank); **TİTCK `find_drug_drug_interactions` is substance-overlap, NOT clinical DDI** — never present as interaction data. → cross-validation gate is mandatory before any DDI statement.
- **Mechanism / target** — `iuphar-gtopdb:search_targets`/`search_ligands` (+`target_interactions`/`ligand_interactions`) **complements** ChEMBL `get_mechanism`/`target_search`; second source when OpenTargets is offline. → ground mechanism claims in ChEMBL/EPMC (cross-validate).
- **Out-of-whitelist (never call):** pipeworx **generic** tools (`ask_pipeworx`, `discover_tools`, `remember`/`recall`/`forget`, `polymarket_*`, `scan_*`, `subscribe`, `validate_claim`) — least-privilege, tool-level (G-WHITELIST). **Runtime-enforced:** the plugin's PreToolUse guard hook (`hooks/guard_tool_call.py`) DENIES anything outside the §2.6 allowlist on pipeworx gateways + the D1/D2 broken tools at call time and redirects — you should not reach for them, but the guard is the backstop.

**C. Multi-Country AFF (EPMC native)** — `for country in [Turkey, China, Japan, Germany, Brazil, Korea]: EPMC:search_articles(f'({topic}) AND AFF:"{country}"')`. Run when geographic breadth matters.

**D. Türkiye native (when TR context/enrichment active)** — TİTCK `search_drugs` (`titck.cureonics.com`, gated — the cache-fallback rung was retired 2026-07-31; call it directly), YÖK Tez, EPMC `AFF:"Turkey"`. SUT/legislation text is **out of scope** (no mevzuat MCP in this plugin → `cureolex`). Null → "Türkiye Veri Boşluğu" block. See `turkiye-layer.md`.

**E. Guidelines & HTA / Epidemiology** — society-guideline PDFs (NICE/ESMO/NCCN/Cochrane) and HTA bodies have **no native MCP** → **documented gap (VERİ YOK)**, never web-scraped. Epidemiology (MAY, Adım 0.5.K): ICD-11 via `openfda` or `med-terminologies.icd11_search`; US via **PopHIVE** (**US-ONLY**); global/TR burden via **`who-gho`**; cancer via **`globocan`** (modelled + `ui`); **IHME/GBD** still a gap. Operator-supplied PDFs → anamnesis ingest.

**Full-Text Retrieval (when abstract insufficient — `fulltext-retrieval.md`; legal-first 7-tier)** — EPMC `get_full_text_article`/`get_copyright_status` (Tier 1 PMC OA) → PaperSearch `read_pubmed_paper` (Tier 2) → **marmara-ebsco `ebsco_search` → `ebsco_get(record_id, collection?, doc_id?)` (Tier 3 — LICENSED VETİS EBSCOhost, FIRST paywall gate; miss → SKIP-REASON then continue)** → **openathens `oa_verify_access`/`oa_resolve` + `oa_fetch_fulltext` or `oa_fetch_pdf` (Tier 4 — Millet Kütüphanesi, SECOND licensed gate)** → Wiley (auth, Tier 5) → **annas-reader reader flow or `download_document(id=DOI|MD5)` (Tier 6 — LAST RESORT after licensed band)** → pubmed-epmc `pubmed_fetch_fulltext` (Unpaywall legal-OA, Tier 7). Pass `collection=evidentia:run:<id>` + `evrun:` doc_id into Hub fetch tools when accepted. File tools' opaque `resource_link`s: consume promptly. Copyright: analysis only; CC-BY freely quotable; no web scraping.

## Adım 2: Generosity Principle (depth ≠ dump)

Token cycles enable, not constrain. **Depth** means every phase/rung is attempted (call **or**
`SKIP-REASON`) — it does **not** mean dumping unbounded raw bodies into the context window.
Depth is spent **across all phases** (P0 protocol/PICO → P1 ID-first search → P2 retrieval →
P3/P4/P5/P6 appraisal → P7 reporting). Minimum retrieval floors remain (PubMed ≥2 queries ×25,
EPMC ×2, 6-country AFF, CT.gov ×2, Türkiye native when active) **plus a ≥1-discovery-call floor
for every other always-on core connector** (Consensus, Paper Search, bioRxiv/medRxiv, YÖK Tez,
OpenAlex, Semantic Scholar, pubmed-epmc) — unreachable = `SKIP-REASON` in OPS, never a silent
skip (`execution-map.md`). Active enrichment modules **add** depth. **No upper cap on
bibliographic coverage**; **hard cap on raw dump as synth input** (retrieve-don't-dump;
fulltext ≥3 KB / bulk ≥8 KB → **synthesis forbidden** — ingest + `hybrid_query` / PICO card only).

**MUST = call or `SKIP-REASON`**, never “paste the full tool body into context.” P1/P2 keep
ID+title+year (abstract ≤400 chars when needed); full bodies go to Anamnesis
(`collection=evidentia:run:<id>`). Screening tables live in
`.claude/evidentia-run/<id>/screening_table.jsonl` — context gets counts + a small sample.

**Ops phase token budgets (guidance, not hard host limits):** P1 dump ≤~40 K tokens of raw
connector text; P4 ≤~15 hybrid packages; companions prefer summary/ID fields. Exceeding a
budget → scratch + Anamnesis, never silent truncation of the include set.

Retry generosity: 3× + exponential backoff; pagination up to 3 pages. **openfda (FDA/ICD-11)
exception:** call singly (not parallel), one retry, mark skippable if it stalls.

Mandatory transparency note (**Cömertlik Garantisi**). **Placement:** in file-based clean-copy
reports this note lives inside the **non-rendering operational annex** (`<!-- OPS: … -->`), NOT the
reader-facing body (Adım 5 + `report-presentation.md`). In short interactive answers it may be visible.
```
---
Cömertlik Garantisi: Bu yanıtın üretiminde [N] API çağrısı yapıldı. Aktif fazlar: P0–P7.
Aktif zenginleştirme modülleri: [... veya "yok — çekirdek PRISMA hattı"]. Native-first çözümleme
uygulandı (web tier yok). Hiçbir faz/kaynak sınıfı atlanmadı (çağrı veya SKIP-REASON);
ham gövde sentez girdisi yapılmadı (retrieve-don't-dump / working-set ledger).
[Eğer varsa: (openfda gecikmesi nedeniyle tekil çağrı + retry. / Native-API'siz kaynak(lar) dürüstçe VERİ YOK olarak işaretlendi — web-scraping yok.)]
```

## Adım 3: Output Contract

The reader-facing structure and section scaffold live in **`references/output-templates.md`**
(SR/ScR structure, adaptive formats, `.data.json` sidecar) — no inline §1–21 scaffold. Rule:
every element the review type requires is present; missing data = "VERİ BULUNAMADI" (never silently
omitted). **Full-detail discipline:** every section loaded into `coverage_set` is surfaced in
reasoning/output — a loaded KB section is never silently summarised away (retrieve-don't-dump).

## Adım 5: Nihai Sunum Sözleşmesi — Temiz Kopya Doktrini

Research depth (P0–P7) is unchanged; this governs the **form the reader receives**. For every
**file-based report**, the deliverable is a clean, journal-grade Turkish article. **FIRST read
`references/report-presentation.md`**, then enforce its doctrine. Two-layer output:
- **Layer A — Clean Copy (visible/rendered):** finished reader-facing article — clean Turkish, full
  sentences, scholarly register, explicit Vancouver references (PMID/DOI/NCT + access date),
  executive summary + key findings, abbreviations index + info boxes, reader-facing Methods/Limitations,
  a PRISMA flow diagram + Summary-of-Findings table.
- **Layers B/C — Viz + Ops (invisible):** carried only inside `<!-- VIZ: … -->` and `<!-- OPS: … -->`
  HTML comments; never rendered. **No internal-process leakage** — connector/tool names, function
  signatures, MCP, phase/module codes, call counts, sidecar refs **never** in the visible body; the
  Methods section names public databases only (no tooling log).

Telemetry (the Cömertlik note + all operational trace) relocates to the `<!-- OPS -->` annex.
Run the **finalization gate G1–G7** (`report-presentation.md`) before emitting; fix any failure
first. Renderer handoff: carbon-html-report consumes-and-strips VIZ/OPS comments.

## Completeness Gate v2 (MANDATORY — immediately before finalising)

Re-scan `references/knowledge-map.md` against the question and the work done. Strictness tuned by
Adım 0.1 `completeness_gate: lenient|standard|strict`. **Four** mandatory sub-checks:

1. **Always-on core fired in playbook order** — confirm every MUST/SHOULD rung in
   `execution-map.md` ran, or carries a `SKIP-REASON`. A silently-skipped core connector is a
   gate failure. All 20 bundled servers are used, MAY+`enrichment_off`, or OUT+`out_of_scope`.
2. **De-skew decision log** — reconcile the `coverage_set`: a domain enrichment module NOT run
   because it was judged irrelevant is a LOGGED de-skew decision (Ops sidecar), NOT a gap; a module
   that IS relevant but was missed by keyword signals IS a gap → load it.
3. **Semantic re-scan** — "Is there any phase, section, or connector relevant to this question that
   was NOT consulted?" (Booster: if `kb_search` reachable, run it once more.)
4. **Article coverage (working-set ledger)** — read
   `.claude/evidentia-run/<run_id>/ledger.json` (hook-maintained; separate from the Anamnesis
   `evidentia-anamnesis-run.json` doc_id ledger):
   ```
   coverage = cited_or_skipped_with_reason / include_set
   floors: lenient ≥0.75 · standard ≥0.90 · strict ≥0.98
   ```
   `include_set` = records with status ∈ {included, extracted, cited, skipped}. A record counts
   toward the numerator only if `cited` **or** `skipped` with a non-empty `skip_reason`
   (`abstract_only`, `copyright_gate`, `not_retrieved`, …). **Refuse P6/P7 finalize** (skill:
   do not emit the clean copy) when coverage &lt; floor — close gaps (cite, skip-with-reason, or
   extract) first. Required Ops/`coverage` block:
   `{n_include, n_cited, n_skipped_reasoned, coverage, uncovered[]}`. Hook
   `coverage_gate.py` emits the same as advisory (soft DENY only if
   `EVIDENTIA_COVERAGE_ENFORCE=1`; empty include_set → advisory only).
5. **Anamnesis reconcile (P1 — before P4 extract / P6 synthesize)** —
   `list_docs(collection=evidentia:run:<id>)` ↔ working-set ledger via
   `reconcile_anamnesis_ledger` (hook on list_docs / hybrid PreToolUse / SessionStart resume).
   Links `evrun:` / bare DOI|PMID|NCT / EBSCO `record_id` → `anamnesis_doc_id` (search titles are per-hit; `ebsco_get` overwrites). Close `missing_extractions`; investigate `orphans`. **Multi-query MUST:**
   `hybrid_query(collection=…, query=…, queries=[≥2])` — single-query synthesis forbidden
   (PreToolUse advisory).
- Produce a gap list (Ops sidecar). If non-empty: load + address each gap, then re-check.
- Finalise only when connector gaps are empty **and** article coverage ≥ floor.

## Important Principles
- **Scientific integrity** — never fabricate; preprints flagged; no-API sources → documented gap.
- **Native-First integrity** — prefer the verified native tool; a referenced connector MUST resolve
  to a real tool in `connector-registry.md`.
- **No web tier / no fabrication** — Exa/Tavily/OSINT removed; no-API sources (guideline PDFs,
  IHME/GBD) are a documented gap. EMA → `ema`; GLOBOCAN → `globocan`; WHO GHO → `who-gho`.
- **Copyright** — full text for analysis only; no verbatim bulk reproduction; CC-BY quotable.
- **Türkiye relevance** — when TR context is active, TİTCK reimbursement/SUT is often determinative.
- **Connector failure** — never silently omit; report the gap + queries attempted.
- **Clean-copy / sunum bütünlüğü** — file reports read like a peer-reviewed article; no tooling,
  connector names, phase/module codes or telemetry in the reader-facing body (`report-presentation.md`).
- **Anamnesis is ephemeral scratch for THIS PRISMA run** — not a long-lived library. Dual-write
  `collection=evidentia:run:<run_id>` and `doc_id=evrun:<run_id>:…`. Flagship:
  `hybrid_query(collection=…, queries[≥2])` (single-query forbidden for synthesis).
  Unscoped hybrid/graph/global search stays denied. `corpus_stats` is not the working set
  (`list_docs`). Before P4/P6: reconcile `list_docs` ↔ ledger. Hooks prefer `forget_collection`
  on SessionEnd or a new `/evidentia` — they never wipe another tenant's docs. No Stop-hook forget.

## Limitations / Out-of-Scope
This skill provides the evidence-synthesis layer; it hands off, never absorbs: individual SGK
appeal / litigation → `onko-erisim` / `saglik-sigorta`; promotional MLR review → `promo-censor`;
net-new commercial strategy + OSINT/web competitive intelligence → `pharmaintel`; FTO/IP litigation
depth → `pharmapatent`; deep TR regulatory reform → `cureolex`. FAERS counts are context, never
clinical evidence or incidence. β-candidate connectors are not wired until probe-verified.

---

## Reference Files — Progressive Disclosure

| File | When | Contents |
|---|---|---|
| `knowledge-map.md` | ALWAYS (Adım 0/0.4) | Semantic coverage index; phase + module routing |
| `connector-registry.md` | ALWAYS (Adım 0) | Verified tool table, native-first ladder, §2.6 whitelist, §8 Probe Log |
| `evidence-grading.md` | ALWAYS / P6 | GRADE, Tier 0–6, NER, full-text+copyright integration |
| `output-templates.md` | ALWAYS / P7 | SR/ScR output structure, formats, sidecar |
| `report-presentation.md` | ALWAYS / P7 | Clean-copy doctrine, VIZ/OPS isolation, finalization gate G1–G7 |
| `prisma-reporting.md` | ALWAYS / P7 | PRISMA 2020 flow diagram, SoF table, PRISMA/ScR checklist |
| `prisma-protocol.md` | P0 | Protocol + PICO/PECO/PCC, eligibility, pre-registration |
| `search-strategy.md` | P1 | MeSH/Emtree, Boolean, per-database translation, grey literature |
| `screening.md` | P3 | Two-stage screening, exclusion logging, conflict resolution |
| `data-extraction.md` | P4 | Extraction tables, numerical outcome capture, Extended-Tier recipes |
| `risk-of-bias.md` | P5 | RoB2 / ROBINS-I / QUADAS-2 / Newcastle-Ottawa |
| `execution-map.md` | P1/P2 (before first MCP call) | Ordered MUST/SHOULD/MAY/OUT playbook for all 20 bundled servers + 13 companions; skip-reason template |
| `extended-api.md` | P2 (as needed) | Native-MCP-first + Python REST fallback (PubChem/DOAJ/J-STAGE/…) |
| `fulltext-retrieval.md` | P2/P4 (as needed) | Legal-first 7-tier: EPMC PMC OA → Paper Search → Marmara EBSCO (Tier 3) → OpenAthens/Millet (Tier 4) → Wiley (Tier 5) → annas-reader (Tier 6 last resort) → pubmed-epmc Unpaywall (Tier 7) |
| Optional enrichment layers (`oncology/hematology/regulatory-science/hta/medaffairs-ops/immunology/neurology/rare-disease/drug-intelligence-layer.md`, `regulatory-intelligence.md`, `turkiye-layer.md`) | per Adım 0.5 | Domain deep-dive + appraisal checklist + native wiring (NON-mandatory) |
| `skill-manifest.yaml` | tooling / audit | Standalone SMP manifest (runtime.mcp_servers, composition, verification gates) |
| `composition-runbook.md` / `benchmark-suite.md` / `benchmark-protocol.md` / `v8-wiring-patch.md` | large query / cross-skill / dev / historical | Pipelines, eval harness, wiring history |
| `evals/check_integrity.py` + `evals/benchmark-queries.json` | dev / pre-release | Executable integrity gates + regression queries |

---

## Version History (recent)

| Version | Date | Changes |
|---|---|---|
| **9.0.7** | **Aug 2026** | Working-set ledger QA fix (Marmara EBSCO): per-hit title binding (no batch title broadcast); `ebsco_get` last-write-wins title + `anamnesis_doc_id`; `reconcile_anamnesis_ledger` matches bare DOI/PMID/NCT, `evrun:` peel, and EBSCO `record_id` when collection-scoped ingest omits prefix; list_docs `id` field. |
| **9.0.6** | **Aug 2026** | Context-economy P1+P2: `reconcile_anamnesis_ledger` (list_docs↔ledger; missing_extractions/orphans); multi-query `hybrid_query` mandatory (advisory); `coverage_gate` auto Completeness Gate (soft DENY via `EVIDENTIA_COVERAGE_ENFORCE=1`); synthesizer required `coverage` block (`n_include`/`n_cited`/`n_skipped_reasoned`/`uncovered[]`); OpenAthens/EBSCO pass-through vs annas gap documented. **P3 eval (no doctrine bump):** offline synthetic 40-paper harness `evals/context_economy_synth.py` — `skip_silent_rate=0` on correct ledger; Gate surfaces uncovered; RDD dump proxy (see `evals/CONTEXT-ECONOMY-P3.md`). |
| **9.0.5** | **Aug 2026** | Context-economy P0: working-set ledger (PMID\|DOI\|NCT) under `.claude/evidentia-run/<id>/`; retrieve-don't-dump floors 3 KB/8 KB + **synthesis forbidden**; Completeness Gate v2 article coverage (standard ≥0.90); ID-first P1/P2; Cömertlik = depth≠dump; screening scratch file. |
| **9.0.4** | **Aug 2026** | Claude Directory companions wired (bioRxiv, Scite, BioRender, SNOMED CT Terminology) + ordered P1 discovery (OpenAlex→pubmed-epmc→S2→PubMed→CT→bioRxiv→Consensus→Paper Search→Elicit→Scite→AdisInsight→YÖK Tez); Claude vs self-host preference table; 13 companions. |
| **9.0.3** | **Aug 2026** | Full-text cascade inserts **Marmara EBSCO** as Tier 3 (FIRST licensed institutional attempt): EBSCO → OpenAthens → Wiley → Annas → Unpaywall (7-tier). Fleet +1 gated server (`marmara-ebsco`). EBSCO miss MUST `SKIP-REASON` before OpenAthens. Anamnesis `collection`/`doc_id` pass-through on `ebsco_get`. |
| **9.0.2** | **Aug 2026** | Ordered P0–P7 tool playbook (`execution-map.md`): MUST/SHOULD/MAY/OUT + `SKIP-REASON` for all 19 bundled servers + 9 companions. Completeness Gate requires skip reasons. who-gho/globocan/ema native (IHME still gap). Anamnesis exclusive-run hybrid is P4/P6 MUST after ingest. |
| **8.3** | Jun 2026 | Semantic coverage mechanism: Adım 0.4 + knowledge-map + Completeness Gate + G-COVERAGE; optional evidentia-kb booster. |
| **8.4** | Jun 2026 | Structured-Authoritative Refocus — Exa/Tavily web tier + OSINT axis removed; 3 keyless Tier-K academic connectors added (OpenAlex/PubMed-EPMC/Semantic Scholar). |
| **8.5** | Jun 2026 | Extended-Tier promotion (med-terminologies/nih-clinicaltables/nlm-rxnorm/iuphar-gtopdb first-class + tool whitelists + cross-validation gates); drugddx Tier-O live; openfda D-α; PopHIVE US epidemiology; gates G-PROBE/G-XVAL/G-WHITELIST. |
| **9.0.0** | **Jul 2026** | **MAJOR — PRISMA pipeline rewrite + de-skew.** The mandatory **10-axis** domain matrix was replaced by an end-to-end **PRISMA 2020 / PRISMA-ScR pipeline P0–P7** (P0 protocol/PICO → P1 search-strategy → P2 retrieval+dedup → P3 screening → P4 data-extraction → P5 risk-of-bias → P6 GRADE → P7 PRISMA-reporting), each pointing at its phase reference file (`prisma-protocol`/`search-strategy`/`screening`/`data-extraction`/`risk-of-bias`/`evidence-grading`/`prisma-reporting`). **Adım 0.5 changed from a MANDATORY axis loader into an OPTIONAL, context-triggered enrichment classifier** — the default review path loads **NO domain layer** (de-skew invariant). Description rewritten to a general systematic/scoping-review engine (PRISMA/PICO/PECO/screening/RoB/GRADE triggers; therapeutic-area/commercial triggers no longer dominate). Adım 0.1 `default_axis`→`default_modules`; Adım 0.4 reframed to route to PHASE files + optional modules; P3/P5 carry human-approval checkpoints. Preserved backbone doctrines (native-MCP-first, clean-copy, retrieve-don't-dump, no-fabrication, uncapped depth, tek-sefer cache) and the Extended-Tier cross-validation recipes (moved under P4). Additive/ADR-05-safe: research depth, connector wiring, clean-copy doctrine, and all reference files unchanged. |

---

## SMP v1.0 Manifest (excerpt — authoritative copy is `skill-manifest.yaml`)

> The full, machine-readable manifest lives in **`skill-manifest.yaml`** at the skill root
> (runtime.mcp_servers, composition.pipe_to + scope_guard, verification.gates, constraints). The
> block below is a human-readable summary; on any conflict, the standalone file wins.

```yaml
skill_manifest_protocol: 1.0
skill_name: medical-research
skill_version: 9.0.7
produces:
  - prisma-systematic-review-markdown (P0–P7; PRISMA flow diagram + Summary-of-Findings)
  - clean-copy-report (journal-grade reader-facing article; tooling/telemetry/viz carried
    only in non-rendering <!-- OPS -->/<!-- VIZ --> annex)
  - data-sidecar-json (evidence/screening/extraction/RoB/GRADE tables + optional
    enrichment_payload + sources_summary)
consumes:
  - clinical-question (required) | PICO/PECO | pmid/nct/doi | drug-name/moa/target
core_pipeline: [P0 protocol, P1 search, P2 retrieval, P3 screening, P4 extraction,
  P5 risk-of-bias, P6 GRADE, P7 PRISMA-reporting]   # v9 — runs for EVERY review
optional_enrichment_modules:   # NON-mandatory; load only per Adım 0.5 context
  - oncology | hematology | regulatory | hta | medaffairs | immunology | neurology
  - rare-disease | drug-intelligence | turkiye-market | epidemiology
connectors_used:
  academic: [PubMed/EuropePMC, Consensus, ScholarGateway, PaperSearch, ClinicalTrials,
    bioRxiv, YÖKTez, OpenAlex(keyless), SemanticScholar(keyless), PubMed-EPMC(keyless)]
  extended_tier_k: [med-terminologies, nih-clinicaltables, nlm-rxnorm, iuphar-gtopdb]   # TOOL-whitelisted (§2.6); cross-validated
  clinical_ddi: [drugddx]   # NOT a pairwise engine — cross-validate
  regulatory_epi: [openfda(openFDA+ICD11), PopHIVE(US), who-gho(global/TR), globocan(cancer), ema(EU); IHME/GBD = documented gap]
  turkiye: [TİTCK, TÜRKPATENT, YÖKTez]
  fulltext: [EuropePMC PMC, PaperDownload, MarmaraEBSCO(Tier3 licensed first), OpenAthens(Tier4 licensed), Wiley(auth Tier5), annas-reader(Tier6 last-resort), pubmed-epmc(Unpaywall Tier7)]   # legal-first 7-tier; order EBSCO→OA→Wiley→Annas
composes_with:
  - carbon-html-report | carbon-pptx (consume sidecar)
  - onko-erisim | saglik-sigorta | pharmapatent | pharmaintel | cureolex | promo-censor
verification:   # executable — evals/check_integrity.py
  gates: [G-REF, G-CONN, G-ALWAYS, G-VERSION, G-COVERAGE, G-PROBE, G-XVAL, G-WHITELIST, G-SIZE, G-DESC, G-PHASES, G-PLAYBOOK]
constraints:
  native_first: true
  enrichment_optional: true   # v9 — no domain module is mandatory; core PRISMA runs regardless
  copyright_limits: enforced (no verbatim bulk; CC-BY via copyright_status)
  clean_copy_doctrine: true
  no_tooling_leakage: true
  viz_directive_isolation: true
  probe_verified_only: true
  languages: [Turkish primary, English technical terms preserved]
```

*Ground-truth principle (unchanged) — every connector reference resolves to a probe-verified tool.
`evals/check_integrity.py` fails the release if any cited reference file or registry connector does
not resolve. v9 is additive/ADR-05-safe: it rewires the orchestration spine onto PRISMA phases and
makes the domain layer optional; research depth and connector wiring are unchanged.*
