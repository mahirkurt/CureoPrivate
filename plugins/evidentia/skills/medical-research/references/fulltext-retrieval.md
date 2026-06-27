# Full-Text Retrieval Cascade (v8.0 — NEW)

**Loaded:** ALWAYS (Adım 0).
**Purpose:** v7.1 could only reach full text via `Exa:web_fetch_exa` — blind at paywalls.
v8.0 adds a **verified multi-tier cascade** that opens open-access, PMC, and (for analysis
only) paywalled full text, with an explicit **copyright gate**.

**Connectors:** EuropePMC (`8f314cbe…`), Paper Search/Download (`660e91bd…`), **annas-mcp**
(verified), Wiley (`bio-research:wiley`, OAuth), Exa (last resort).

---

## 1. When to retrieve full text
Trigger full-text retrieval when the abstract is insufficient for the synthesis:
- Pivotal Phase 3 RCT: subgroup data, secondary endpoints, safety tables, HR/CI/p.
- SR/meta-analysis: forest-plot data, GRADE tables, heterogeneity (I²).
- Guideline/methodology grounding (GRADE, Cochrane Handbook, ESMO-MCBS, PRISMA).
- Discordant findings needing the methods/limitations section.
Limit to the **top 3–5 most decision-relevant** items; do not bulk-fetch.

---

## 2. The Cascade (in order)

### Tier 1 — EuropePMC PMC (open access, native)
```
EPMC: get_copyright_status(pmids=[...])      # determine OA / license FIRST
EPMC: convert_article_ids(...)               # PMID → PMCID if needed
EPMC: get_full_text_article(pmc_ids=["PMC..."])   # ~6M OA articles
```
If CC-BY/CC0 → free to quote (with attribution). If not OA here → Tier 2.

### Tier 2 — Paper Search download (PMC extraction)
```
PaperSearch: read_pubmed_paper(paper_id="<PMID/PMCID>")   # extracts text
PaperSearch: download_pubmed / download_biorxiv / download_semantic
```

### Tier 3 — annas-mcp (paywalled article / methodology book) — VERIFIED
```
annas: article_search(query="<DOI or keywords>")   # → metadata + SciDB handle
annas: article_download(doi="10.xxxx/...")          # VERIFIED: downloads PDF to user machine
annas: book_search(query="Cochrane Handbook ...")   # methodology references
annas: book_download(hash="<md5>", format="pdf", title="...")
```
**Verified 9 Jun 2026:** `article_search("10.1136/bmj.39489.470347.AD")` resolved the GRADE
2008 paper; `article_download` succeeded (file → user's Downloads). `book_search("Cochrane
Handbook ...")` returned the 2019/2020 2nd edition.
**Note:** downloads land on the **user's computer**, not the sandbox — they are for the
user + for your analysis of the retrieved content, not re-upload.

### Tier 4 — Wiley (publisher full text, OAuth-gated)
`Wiley:authenticate` → publisher full text (Cochrane Library, Wiley journals). Graceful
skip if unauthenticated.

### Tier 5 — Exa (last resort)
`Exa:web_fetch_exa(urls=[...], maxCharacters=...)` — when no API path exists. On paywall,
note and stop.

---

## 3. Copyright Gate (MANDATORY)
- **Always** run EPMC `get_copyright_status` before quoting any article at length.
- **Open access (CC-BY/CC0):** quotation with attribution permitted.
- **Restricted / annas / Wiley full text:** use for **analysis, extraction of facts and
  numbers, and paraphrase only**. Do **NOT** reproduce large verbatim blocks, full figures,
  or full tables. Report extracted data points (HR, CI, n, endpoints) — these are facts, not
  copyrightable expression — with citation.
- Methodology books (Cochrane Handbook, GRADE): cite and paraphrase the method; never paste
  chapters.

---

## 4. Methodology Grounding (annas book layer)
For appraisal rigor, retrieve and consult (analysis only) authoritative methodology when a
query demands formal grading or SR methods:
- **GRADE** (Guyatt et al., BMJ 2008; GRADE handbook) — quality-of-evidence domains.
- **Cochrane Handbook 2nd ed.** (Higgins et al., 2019/2020) — RoB 2, meta-analysis, GRADE.
- **PRISMA 2020**, **AMSTAR-2**, **ESMO-MCBS** scoring guide, **CHEERS-2022** (HTA).
These ground `evidence-grading.md` and the specialty appraisal checklists in the primary
literature rather than memory.

---

## 5. Output integration
Extracted full-text data points feed: §1 (numerical endpoints), §7 (Tier-0 GRADE tables),
evidence-table sidecar (`result_summary`, HR/CI), and the relevant specialty section.
Tag each: citation + `[tam metin: PMC OA | annas analiz | Wiley | Exa]` + license note.

---

## 6. Known limitations
1. **Downloads are user-side** (not sandbox-readable) — pipeline validates retrieval; content
   analysis uses the metadata/abstract + what the tool returns.
2. **Copyright** — the dominant constraint; default to paraphrase + data extraction.
3. **annas availability** — mirror/SciDB dependent; if a DOI fails, try Tier 1/2 first.
4. **Wiley/Synapse auth** — graceful skip if unauthenticated.
5. **Exa paywall blindness** — last resort only.

---

*v8.0 — annas-mcp `article_search`/`article_download`/`book_search` verified working; EPMC
`get_full_text_article`/`get_copyright_status` schemas verified 9 June 2026.*
