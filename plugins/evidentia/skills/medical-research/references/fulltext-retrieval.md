# Full-Text Retrieval Cascade (v9.0.3)

**Loaded:** P4 (and P2 when abstract is insufficient). Feeds **P4 Data Extraction**
(`data-extraction.md`): full text is retrieved here, then extracted into the `evidence_table`
— never dumped raw into context. **Playbook:** `execution-map.md` P4 T1–T7 (MUST* cascade;
stop at first success; later tiers `already_canonical`). After ingest: Anamnesis exclusive-run
`collection=evidentia:run:<id>` + `evrun:` dual-write; scoped `hybrid_query` MUST if corpus
non-empty. Do not invent `doc_scope`.

## Legal-first positioning (read this first)

Full text is resolved in **descending order of legal cleanliness**, and the ladder stops at
the first tier that delivers:

1. **Free open-access** (Tier 1–2, Tier 7 sweep) — CC-BY/CC0 or legal-OA; freely quotable.
2. **Licensed institutional access** (Tier 3 **Marmara EBSCO** → Tier 4 **OpenAthens/Millet
   Kütüphanesi** → Tier 5 **Wiley**) — the operator's *own legitimate subscription*; analysis/
   extraction only. **User-mandated licensed order:** EBSCO → OpenAthens → (Wiley) → Annas.
3. **Grey-area shadow library** (Tier 6 **annas-reader**) — **LAST RESORT**, entered only when the
   licensed band (Tier 3 + Tier 4 + Tier 5) cannot supply the item.

> **Marmara EBSCO is tried before OpenAthens; OpenAthens before annas.** A legitimate licensed
> copy is always tried before the grey-area annas (Tier 6). EBSCO miss/fail/challenge MUST be
> recorded as `SKIP-REASON` before falling through — never a silent skip of Tier 3.

**Connectors:** EuropePMC (`8f314cbe…`), Paper Search/Download (`660e91bd…`), **marmara-ebsco**
(HP category server — target `ebsco.cureonics.com/mcp`, §Tier 3), **openathens**
(HP self-host — **LIVE** `openathens.cureonics.com/mcp`, §Tier 4), Wiley (`bio-research:wiley`, OAuth), **annas-reader**
(verified, last-resort), **pubmed-epmc** (`pubmed_fetch_fulltext` — EuropePMC + Unpaywall legal-OA).

---

## 1. When to retrieve full text
Trigger during **P4** when the abstract is insufficient for extraction/appraisal:
- Pivotal RCT: subgroup data, secondary endpoints, safety tables, HR/CI/p.
- SR/meta-analysis: forest-plot data, GRADE/SoF tables, heterogeneity (I²).
- RoB (P5): the methods/limitations section a design-specific tool (RoB2/ROBINS-I/QUADAS-2) needs.
- Methodology grounding (GRADE, Cochrane Handbook, PRISMA, AMSTAR-2).
Limit to the **top 3–5 most decision-relevant** items; do not bulk-fetch (§Tier 3–4 pacing).

---

## 2. The Cascade (in order — stop at first success)

### Tier 1 — EuropePMC PMC (free open access, native)
```
EPMC: get_copyright_status(pmids=[...])          # determine OA / license FIRST
EPMC: convert_article_ids(...)                   # PMID → PMCID if needed
EPMC: get_full_text_article(pmc_ids=["PMC..."])  # ~6M OA articles
```
CC-BY/CC0 → free to quote (attribution). Not OA here → Tier 2.

### Tier 2 — Paper Search download (PMC extraction)
```
PaperSearch: read_pubmed_paper(paper_id="<PMID/PMCID>")   # extracts text
PaperSearch: download_pubmed / download_biorxiv / download_semantic
```

### Tier 3 — Marmara EBSCO (LICENSED institutional — FIRST paywall gate)
**Status:** connector `marmara-ebsco` — HP category server over shared VETİS session
(`ebsco.cureonics.com/mcp`, port 8222; `MARMARA_EBSCO_MCP_API_KEY`). Live (2026-08-19):
HP systemd + tunnel + DNS; `/health` + `tools/list` (4 tools). Wired in fleet `.mcp.json`
(Claude Code `${VAR}`) and `.cursor-plugin/mcp.json` (Cursor `${env:VAR}`). Unreachable /
missing key → `SKIP-REASON unreachable` then Tier 4 (never silent skip). Distinct from
`marmara-clinical` (ClinicalKey/UTD).

**Coverage:** Marmara Üniversitesi VETİS → EBSCOhost (`db_id=426`); default search spans **all**
subscribed databases discovered at landing. Full text only when `downloadLinks` expose PDF/HTML
(never constructed URLs).

```
marmara-ebsco: ebsco_server_info()                 # version, opid, database_count, caveat
marmara-ebsco: ebsco_list_databases(filter?="…")   # discovered subscribed DB codes/names
marmara-ebsco: ebsco_search(query="<DOI|title|keywords>", full_text_only=true, max_results=5)
                                                   # → results[].record_id (+ metadata)
marmara-ebsco: ebsco_get(record_id="…", prefer="pdf",
                         collection="evidentia:run:<run_id>",
                         doc_id="evrun:<run_id>:<DOI|record_id>")
                                                   # PDF/HTML extract → anamnesis or short quote
```
- **Check then fetch:** always `ebsco_search` first; no hit / `no_results` / `no_fulltext_link` /
  `manual_required` / `session_invalid` / `landing_incomplete` → record `SKIP-REASON` with the
  envelope reason, then Tier 4. Do **not** invent a `record_id`.
- **Anamnesis:** pass `collection` + `doc_id` into `ebsco_get` when available; omitted collection
  mints `marmara:run:<sha1-8>`. Prefer Evidentia exclusive-run identity so P4/P6 hybrid stays
  scoped. Raw verbatim is never dumped to context.
- **Pacing:** human-jitter delay is server-side; keep per-run volume modest (same spirit as
  OpenAthens caps — protect the institutional account).

### Tier 4 — OpenAthens / Millet Kütüphanesi (LICENSED institutional — second paywall gate)
**Status:** connector `openathens` — HP self-host **LIVE** (`openathens.cureonics.com/mcp`, hardened
OAuth 2.1 + Bearer; `openathens-mcp` deployed 2026-07-03, real OpenAthens SP-initiated SAML
federation via Millet Kütüphanesi). Tried **after** Marmara EBSCO (Tier 3). If the connector is
NOT bound in the session, **skip Tier 4 → Tier 5/6** (graceful degrade, no silent skip of the
ladder). **Live coverage reality (anti-bot v2, 2026-07-13):** fetches run a
**headed** Chromium under Xvfb with a persistent profile (real browser fingerprint + a stored
`cf_clearance`). Publishers without a browser anti-bot wall extract **real full text** (e.g. Springer
`link.springer.com`, Nature `nature.com`); publishers behind a Cloudflare/JS wall (Wiley,
Elsevier/ScienceDirect, OUP, Sage, Taylor & Francis) now **wait out the non-interactive managed
challenge** (it self-clears → most yield full text). Only an **interactive** challenge
(reCAPTCHA/Turnstile) that will not self-clear returns the new **`challenge_required`** envelope
(host + operator-noVNC hint; **distinct from `manual_required`**, body-less — no fabrication): the
operator solves it once via `deploy/oa-vnc.sh up` on HP, the `cf_clearance` persists in the profile,
and subsequent fetches pass unattended. On `challenge_required`, tell the user an operator noVNC
solve is needed and degrade to Tier 5/6 (never silently skip). Bind via `OPENATHENS_MCP_API_KEY`.

**Coverage:** OpenAthens federation via Cumhurbaşkanlığı Millet Kütüphanesi → ProQuest, EBSCO,
Gale, ScienceDirect/Elsevier, Wiley, Springer, Nature, JSTOR, Scopus, Web of Science, IEEE,
Taylor & Francis, Oxford, Cambridge, Emerald, OVID, Cochrane, … (legitimate campus-off access
via stored SAML session; no relay needed).

```
openathens: oa_server_info()                              # logged_in bool, institution, coverage, caveat
openathens: oa_list_databases(filter?="oncology")         # licensed DB list (name · redirector URL · category)
openathens: oa_verify_access(probe_doi="10.xxxx/…")       # ask BEFORE fetch when possible
openathens: oa_resolve(doi="10.xxxx/…" | pmid="…" | title="…")
                                                          # → target URL + OpenAthens redirector URL(s) + covering DB/publisher (mcp_verified:false)
openathens: oa_fetch_fulltext(doi="10.xxxx/…", ingest=true,
                              collection="evidentia:run:<run_id>",
                              doc_id="evrun:<run_id>:<DOI>")
                                                          # copyright-gated delivery; long text → anamnesis
openathens: oa_fetch_pdf(doi="10.xxxx/…" | url="https://publisher.example/…")
                                                          # provider-neutral original PDF → short-lived opaque resource_link
openathens: oa_session_status()                           # session warmth / pending_challenge
```
- **Delivery (retrieve-don't-dump):** use `oa_fetch_fulltext` for excerpt/search/RAG delivery and
  `oa_fetch_pdf` only when the original provider PDF is actually needed. Pass `collection`/`doc_id`
  when the tool accepts them. Long (≳1–2 pages) →
  anamnesis `ingest_document(collection=evidentia:run:<run_id>, doc_id=evrun:<run_id>:<DOI>, source="openathens:<db>")`
  → manifest, then `hybrid_query(collection=aynı)` or `semantic_search(…, collection=aynı / doc_id=önekli)`.
- **Defensive pacing:** `oa_batch_submit` → `oa_batch_result`; sequential, jittered 20–60 s, per-run
  cap 25, daily cap 100.
- **Failure** → `manual_required` / **interactive anti-bot** → `challenge_required` — never fabricated.

### Tier 5 — Wiley (publisher full text, OAuth-gated)
`Wiley:authenticate` → publisher full text (Cochrane Library, Wiley journals) for publishers the
EBSCO/OpenAthens tiers do not cover. Graceful skip if unauthenticated. (Still inside the
**licensed band**, after OpenAthens, before annas — does not invert the user-mandated
EBSCO → OpenAthens → Annas spine.)

### Tier 6 — annas-reader (shadow library — LAST RESORT, after the licensed band)
**Entered only when the licensed band (Tier 3 Marmara EBSCO + Tier 4 OpenAthens + Tier 5 Wiley)
cannot supply the item.** Grey-area; legal-first doctrine keeps it last.
⚠️ **Re-measured 2026-08-14:** the wired `annas-reader` exposes nine tools. Its bounded
reader remains the preferred analysis path; `download_document` adds original-file delivery when
PDF/EPUB/MOBI/AZW/DjVu/FB2/CBZ/CBR/XPS is genuinely required. The old names
`article_download`/`book_download` still do not exist.

```
# ARTICLES — by DOI
annas: article_search(query="<DOI or keywords>", limit=3)   # → rows with title/authors/DOI
annas: read_article(doi="10.xxxx/…", max_chars=…)           # → ephemeral full text (token-budgeted)

# BOOKS — md5 handle, then bounded retrieval (NEVER read the whole book)
annas: book_search(query="Cochrane Handbook …", limit=3)    # → rows with [md5: …]
annas: get_document_info(md5="…")                           # → format/pages/ocr/text_quality/TOC
annas: search_in_document(md5="…", query="risk of bias", k=3)  # → top-k PAGE-REFERENCED passages
annas: read_document(md5="…", page_start=…, page_end=…, max_chars=…)  # → only the pages you need

# ORIGINAL FILE — DOI or exact 32-hex MD5; consume the short-lived link promptly
annas: download_document(id="10.xxxx/…" | "<32-hex-md5>")
                                                              # → opaque resource_link + format/size/SHA-256
```
For DOI input the server applies Crossref/content-identity gates. Record the DOI or MD5 together
with the returned SHA-256 and format; never preserve the opaque link as a durable citation. For
long-file analysis, ingest the consumed file into anamnesis and query bounded slices.
**Verified 2026-08-07 (live, end-to-end):** `article_search("10.1136/bmj.39489.470347.AD")` resolved
the GRADE 2008 paper and `read_article` returned its body (1,252 chars at `max_chars=800`, header
included); `book_search("Cochrane Handbook …")` → md5 `47cbf17d…`; `get_document_info` → 680 pages,
`text_quality=ok`; `search_in_document(md5, "risk of bias", k=2)` → `[page 232 · score 5.705]` from
CH 08 "Assessing risk of bias in included studies".

**Fidelity guard (do not strip it).** `read_article` prepends the Crossref citation with *"Confirm
the body below matches this citation — Anna's Archive does not guarantee DOI↔content fidelity."*
Anna's SciDB can return the WRONG article for a DOI; check the returned body against the citation
before extracting anything from it. Copyright-gated (§3): analysis only, no verbatim bulk reproduction.

**Order of operations for books is mandatory:** `get_document_info` → `search_in_document` →
`read_document(page_start, page_end)`. A 680-page handbook must never be pulled whole — that is the
exact context-overflow the retrieve-don't-dump hook exists to prevent.

### Tier 7 — pubmed-epmc Unpaywall legal-OA (final legal-OA sweep)
`pubmed-epmc:pubmed_fetch_fulltext(...)` resolves legal open-access full text via NCBI PMC →
EuropePMC fullTextXML → **Unpaywall** (DOI/PMID/PMCID). Free/legal (overlaps Tier 1–2; kept as a
last legal-OA sweep). If still no legal copy exists, **note the gap and stop** — never fabricate.

---

## 3. Copyright Gate (MANDATORY — G-COPYRIGHT)
Applies identically to Tier 3 (Marmara EBSCO), Tier 4 (OpenAthens), Tier 5 (Wiley), Tier 6 (annas):
- **Always** run EPMC `get_copyright_status` before quoting any article at length.
- **Open access (CC-BY/CC0):** quotation with attribution permitted.
- **Licensed / shadow full text (EBSCO · OpenAthens · Wiley · annas):** use for **analysis, extraction of
  facts and numbers, and paraphrase only**. Do **NOT** reproduce large verbatim blocks, whole
  figures, or whole tables. Extracted data points (HR, CI, n, endpoints) are **facts, not
  copyrightable expression** — report them with citation.
- Licensed access is the operator's **own legitimate subscription**, used for personal/analytic
  purposes, server-side; credentials live only in Doppler, never in output or logs.
- Methodology books (Cochrane Handbook, GRADE): cite and paraphrase the method; never paste chapters.

---

## 4. Methodology Grounding (book layer — Tier 4 DB or Tier 6 annas)
For appraisal rigor, retrieve and consult (analysis only) authoritative methodology when a query
demands formal grading or SR methods:
- **GRADE** (Guyatt et al., BMJ 2008; GRADE handbook) — certainty domains.
- **Cochrane Handbook 2nd ed.** (Higgins et al., 2019/2020) — RoB2, meta-analysis, GRADE.
- **PRISMA 2020 / PRISMA-ScR**, **AMSTAR-2**, **RoB2 / ROBINS-I / QUADAS-2** guidance, **CHEERS-2022**.
These ground `evidence-grading.md` (P6) and `risk-of-bias.md` (P5) in the primary literature
rather than memory. Prefer the licensed DB (Tier 4, e.g. Cochrane Library via OpenAthens) over
annas (Tier 6).

---

## 5. Output integration (→ P4/P6/P7)
Extracted full-text data points feed the **`evidence_table`** (P4 `data-extraction.md`: effect
size + 95% CI, N, outcomes), the **GRADE/SoF** synthesis (P6), and the study-characteristics table
(P7). Tag each extracted value with citation + access path
`[tam metin: PMC OA | Marmara-EBSCO:<db> | OpenAthens:<db> | Wiley | annas analiz | Unpaywall OA]` +
license note + the anamnesis `doc_id::idx` provenance where ingested.

---

## 6. Known limitations
1. **File delivery is link-based** — `oa_fetch_pdf` and `download_document` return validated,
   short-lived opaque resource links plus checksum/provenance metadata. Consume promptly; context
   sees only the anamnesis-indexed, provenance-stamped slice, never a base64 dump. Marmara EBSCO
   delivers extracted text (PDF/HTML) via `ebsco_get` + anamnesis, not a client-side resource_link.
2. **Copyright** — the dominant constraint; default to paraphrase + data extraction.
3. **Marmara EBSCO key / reachability** — endpoint live (`ebsco.cureonics.com`); host process
   must expose `MARMARA_EBSCO_MCP_API_KEY` (Doppler `cureohub/dev_personal`). Missing key or
   unreachable → Tier 4.
4. **OpenAthens LIVE, partial publisher coverage** — `openathens-mcp` is deployed
   (`openathens.cureonics.com/mcp`) with working OpenAthens SP-initiated SAML federation. Full-text
   extraction succeeds for federation publishers *without* a browser anti-bot wall (Springer,
   Nature, …); anti-bot publishers usually clear non-interactive CF; interactive challenge →
   `challenge_required`.
5. **Anna's DOI↔content fidelity is not guaranteed** — always reconcile the Crossref header with
   the returned body before extraction.
6. **No mevzuat in this cascade** — legislation is out of Evidentia scope (hand off to cureolex).
7. **`collection` / `doc_id` pass-through matrix (P1 verified):**
   - **OpenAthens `oa_fetch_fulltext`** — **PASS** (`collection` + `doc_id` optional; omit →
     mint `openathens:run:<sha1-8>`). Evidentia MUST pass `evidentia:run:<id>` + `evrun:…`.
   - **Marmara EBSCO `ebsco_get`** — **PASS** (same contract; omit → `marmara:run:<sha1-8>`).
   - **annas `read_article` / `download_document` / `read_document`** — **GAP**: schemas accept
     only `doi`/`id`/`md5` (+ page bounds). No `collection`/`doc_id`. After ephemeral read,
     **MUST** `anamnesis.ingest_document(collection=evidentia:run:<id>, doc_id=evrun:<id>:<DOI>)`
     before synthesis. Do not invent Worker API changes.
