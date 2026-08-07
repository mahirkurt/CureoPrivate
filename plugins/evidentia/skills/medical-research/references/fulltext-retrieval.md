# Full-Text Retrieval Cascade (v9.0)

**Loaded:** ALWAYS (Adım 0). Feeds **P4 Data Extraction** (`data-extraction.md`): full text is
retrieved here, then extracted into the `evidence_table` — never dumped raw into context.
**Purpose:** open the full text needed for extraction/appraisal when the abstract is
insufficient, along a **legal-first, copyright-gated** ladder. No web scraping (v1.4.0).

## Legal-first positioning (read this first)

Full text is resolved in **descending order of legal cleanliness**, and the ladder stops at
the first tier that delivers:

1. **Free open-access** (Tier 1–2, Tier 6 sweep) — CC-BY/CC0 or legal-OA; freely quotable.
2. **Licensed institutional access** (Tier 3 **OpenAthens/Millet Kütüphanesi** + Tier 4
   **Wiley**) — the operator's *own legitimate subscription* via federated SAML; analysis/
   extraction only.
3. **Grey-area shadow library** (Tier 5 **annas-reader**) — **LAST RESORT**, entered only when the
   licensed band (Tier 3 + Tier 4) cannot supply the item.

> **OpenAthens is preferred over annas by design.** A legitimate licensed copy (Tier 3) is
> always tried before the grey-area annas (Tier 5). annas is never the primary paywall gate.

**Connectors:** EuropePMC (`8f314cbe…`), Paper Search/Download (`660e91bd…`), **openathens**
(HP self-host — **LIVE** `openathens.cureonics.com/mcp`, §Tier 3), Wiley (`bio-research:wiley`, OAuth), **annas-reader**
(verified, last-resort), **pubmed-epmc** (`pubmed_fetch_fulltext` — EuropePMC + Unpaywall legal-OA).

---

## 1. When to retrieve full text
Trigger during **P4** when the abstract is insufficient for extraction/appraisal:
- Pivotal RCT: subgroup data, secondary endpoints, safety tables, HR/CI/p.
- SR/meta-analysis: forest-plot data, GRADE/SoF tables, heterogeneity (I²).
- RoB (P5): the methods/limitations section a design-specific tool (RoB2/ROBINS-I/QUADAS-2) needs.
- Methodology grounding (GRADE, Cochrane Handbook, PRISMA, AMSTAR-2).
Limit to the **top 3–5 most decision-relevant** items; do not bulk-fetch (§Tier 3 pacing).

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

### Tier 3 — OpenAthens / Millet Kütüphanesi (LICENSED institutional — primary paywall gate)
**Status:** connector `openathens` — HP self-host **LIVE** (`openathens.cureonics.com/mcp`, hardened
OAuth 2.1 + Bearer; `openathens-mcp` deployed 2026-07-03, real OpenAthens SP-initiated SAML
federation via Millet Kütüphanesi). It is the **primary paywall gate** and takes precedence over
annas (legal-first). If the connector is NOT bound in the session, **skip Tier 3 → Tier 4/5**
(graceful degrade, no error). **Live coverage reality (anti-bot v2, 2026-07-13):** fetches run a
**headed** Chromium under Xvfb with a persistent profile (real browser fingerprint + a stored
`cf_clearance`). Publishers without a browser anti-bot wall extract **real full text** (e.g. Springer
`link.springer.com`, Nature `nature.com`); publishers behind a Cloudflare/JS wall (Wiley,
Elsevier/ScienceDirect, OUP, Sage, Taylor & Francis) now **wait out the non-interactive managed
challenge** (it self-clears → most yield full text). Only an **interactive** challenge
(reCAPTCHA/Turnstile) that will not self-clear returns the new **`challenge_required`** envelope
(host + operator-noVNC hint; **distinct from `manual_required`**, body-less — no fabrication): the
operator solves it once via `deploy/oa-vnc.sh up` on HP, the `cf_clearance` persists in the profile,
and subsequent fetches pass unattended. On `challenge_required`, tell the user an operator noVNC
solve is needed and degrade to Tier 4/5 (never silently skip). Bind via `OPENATHENS_MCP_API_KEY`.

**Coverage:** OpenAthens federation via Cumhurbaşkanlığı Millet Kütüphanesi → ProQuest, EBSCO,
Gale, ScienceDirect/Elsevier, Wiley, Springer, Nature, JSTOR, Scopus, Web of Science, IEEE,
Taylor & Francis, Oxford, Cambridge, Emerald, OVID, Cochrane, … (legitimate campus-off access
via stored SAML session; no relay needed).

```
openathens: oa_server_info()                              # logged_in bool, institution, coverage, caveat
openathens: oa_list_databases(filter?="oncology")         # licensed DB list (name · redirector URL · category)
openathens: oa_resolve(doi="10.xxxx/…" | pmid="…" | title="…")
                                                          # → target URL + OpenAthens redirector URL(s) + covering DB/publisher (mcp_verified:false)
openathens: oa_fetch_fulltext(doi="10.xxxx/…", ingest=true)
                                                          # copyright-gated delivery; long text → anamnesis manifest + provenance-stamped slices; short → cited quote; reports which DB served it
openathens: oa_session_status()                           # session warmth: validated, session_age_s, headless, pending_challenge{host,age_s} — check before/after an anti-bot fetch
```
- **Delivery (retrieve-don't-dump):** the download happens server-side on HP, so the server reads
  the text. Long (≳1–2 pages) → anamnesis `ingest_document(doc_id=<DOI>, source="openathens:<db>")`
  → manifest, then `semantic_search`/`hybrid_query` for query-bounded, provenance-stamped slices
  (`evidence_index`). Short → reasoned short quote. **Raw verbatim is never dumped to context.**
  anamnesis unreachable → summary (not verbatim) + "full text landed on HP" note.
- **Defensive pacing (account protection — MANDATORY for lists):** batch via
  `oa_batch_submit(refs[])` → `oa_batch_result(job_id)`; sequential (concurrency = 1), jittered
  20–60 s delay, per-run cap 25, daily cap 100. Goal: never trip a publisher anti-bot and suspend
  the whole institutional account. Over-cap items are `deferred` (not a gap), reported in the caveat.
- **Failure** (auth/fetch/SAML) → `manual_required` (redirector deep-link + echoed identifier);
  **unsolvable interactive anti-bot** → `challenge_required` (host + operator-noVNC hint, body-less,
  distinct from `manual_required`) — never fabricated. Every output carries a robots/ToS + copyright caveat.

### Tier 4 — Wiley (publisher full text, OAuth-gated)
`Wiley:authenticate` → publisher full text (Cochrane Library, Wiley journals) for publishers the
OpenAthens tier does not cover. Graceful skip if unauthenticated. (Still inside the **licensed band**.)

### Tier 5 — annas-reader (shadow library — LAST RESORT, after the licensed band)
**Entered only when the licensed band (Tier 3 OpenAthens + Tier 4 Wiley) cannot supply the item.**
Grey-area; legal-first doctrine keeps it last.
⚠️ **Re-measured 2026-08-07 — this rung was documented against an API the bundled connector does
not have.** The wired server is `annas-reader` (`annas.cureonics.com`, v3.4.5): an **ephemeral
reader**, not a downloader. `article_download` and `book_download` **do not exist on it** — every
call to those names fails. Nothing lands on the user's machine; text is extracted on demand and not
retained. The real surface is better suited to this plugin anyway: `search_in_document` is a bounded,
page-referenced RAG primitive, i.e. retrieve-don't-dump native.

```
# ARTICLES — by DOI
annas: article_search(query="<DOI or keywords>", limit=3)   # → rows with title/authors/DOI
annas: read_article(doi="10.xxxx/…", max_chars=…)           # → ephemeral full text (token-budgeted)

# BOOKS — md5 handle, then bounded retrieval (NEVER read the whole book)
annas: book_search(query="Cochrane Handbook …", limit=3)    # → rows with [md5: …]
annas: get_document_info(md5="…")                           # → format/pages/ocr/text_quality/TOC
annas: search_in_document(md5="…", query="risk of bias", k=3)  # → top-k PAGE-REFERENCED passages
annas: read_document(md5="…", page_start=…, page_end=…, max_chars=…)  # → only the pages you need
```
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

### Tier 6 — pubmed-epmc Unpaywall legal-OA (final legal-OA sweep)
`pubmed-epmc:pubmed_fetch_fulltext(...)` resolves legal open-access full text via NCBI PMC →
EuropePMC fullTextXML → **Unpaywall** (DOI/PMID/PMCID). Free/legal (overlaps Tier 1–2; kept as a
last legal-OA sweep). If still no legal copy exists, **note the gap and stop** — never fabricate.

---

## 3. Copyright Gate (MANDATORY — G-COPYRIGHT)
Applies identically to Tier 3 (OpenAthens), Tier 4 (Wiley), Tier 5 (annas):
- **Always** run EPMC `get_copyright_status` before quoting any article at length.
- **Open access (CC-BY/CC0):** quotation with attribution permitted.
- **Licensed / shadow full text (OpenAthens · Wiley · annas):** use for **analysis, extraction of
  facts and numbers, and paraphrase only**. Do **NOT** reproduce large verbatim blocks, whole
  figures, or whole tables. Extracted data points (HR, CI, n, endpoints) are **facts, not
  copyrightable expression** — report them with citation.
- Licensed access is the operator's **own legitimate subscription**, used for personal/analytic
  purposes, server-side; credentials live only in Doppler, never in output or logs.
- Methodology books (Cochrane Handbook, GRADE): cite and paraphrase the method; never paste chapters.

---

## 4. Methodology Grounding (book layer — Tier 3 DB or Tier 5 annas)
For appraisal rigor, retrieve and consult (analysis only) authoritative methodology when a query
demands formal grading or SR methods:
- **GRADE** (Guyatt et al., BMJ 2008; GRADE handbook) — certainty domains.
- **Cochrane Handbook 2nd ed.** (Higgins et al., 2019/2020) — RoB2, meta-analysis, GRADE.
- **PRISMA 2020 / PRISMA-ScR**, **AMSTAR-2**, **RoB2 / ROBINS-I / QUADAS-2** guidance, **CHEERS-2022**.
These ground `evidence-grading.md` (P6) and `risk-of-bias.md` (P5) in the primary literature
rather than memory. Prefer the licensed DB (Tier 3, e.g. Cochrane Library) over annas (Tier 5).

---

## 5. Output integration (→ P4/P6/P7)
Extracted full-text data points feed the **`evidence_table`** (P4 `data-extraction.md`: effect
size + 95% CI, N, outcomes), the **GRADE/SoF** synthesis (P6), and the study-characteristics table
(P7). Tag each extracted value with citation + access path
`[tam metin: PMC OA | OpenAthens:<db> | Wiley | annas analiz | Unpaywall OA]` + license note +
the anamnesis `doc_id::idx` provenance where ingested.

---

## 6. Known limitations
1. **Downloads are host-side** — annas → user machine; OpenAthens → HP (server reads it). The
   pipeline validates retrieval; context sees only the anamnesis-indexed, provenance-stamped slice.
2. **Copyright** — the dominant constraint; default to paraphrase + data extraction.
3. **OpenAthens LIVE, partial publisher coverage** — `openathens-mcp` is deployed
   (`openathens.cureonics.com/mcp`) with working OpenAthens SP-initiated SAML federation. Full-text
   extraction succeeds for federation publishers *without* a browser anti-bot wall (Springer,
   Nature verified); anti-bot-walled publishers (Wiley, Elsevier, OUP, Sage, T&F) return
   `manual_required` + redirector deep-link (not defeated, by doctrine → open manually or Tier 4/5).
   If the connector isn't bound in the session, Tier 3 is skipped and the ladder falls to Tier 4/5.
   Bind with `OPENATHENS_MCP_API_KEY`. (anamnesis unbound on HP → excerpt-only delivery; full text
   is still retrieved server-side.)
4. **Publisher anti-bot / account suspension** — the main Tier-3 risk; mitigated by defensive
   pacing (sequential, jitter, per-run + daily caps, personal-use discipline). Persistent risk.
5. **annas availability** — mirror/SciDB dependent; if a DOI fails, the licensed band + Tier 1/2/6
   are the alternatives.
6. **Wiley/annas/OpenAthens auth** — graceful skip if unauthenticated/unconnected.
7. **No web fallback** (Exa/Tavily removed v1.4.0) — if nothing across Tier 1–6 resolves, note the
   gap; never web-scrape or fabricate.

---

*v9.0 — OpenAthens/Millet Kütüphanesi licensed tier added as Tier 3 (legal-first, before annas);
annas moved to Tier 5 last-resort. openathens-mcp design `docs/superpowers/specs/2026-07-01-
openathens-fulltext-evidentia-design.md` (CureoHub); deploy-pending. annas `article_search`/
`read_article`/`book_search`/`search_in_document` + EPMC `get_full_text_article`/`get_copyright_status` verified
(tool names re-measured 2026-08-07: the bundled `annas-reader` has no `*_download` tools).*
