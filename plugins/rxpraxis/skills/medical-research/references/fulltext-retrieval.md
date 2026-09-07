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

### Tier 2 — Paper-Download MCP (PMC extraction)
```
PaperSearch: read_pubmed_paper(paper_id="<PMID/PMCID>")   # extracts text
PaperSearch: download_pubmed / download_biorxiv / download_semantic
```

### Tier 3 — annas-reader (paywalled article / methodology book) — ⚠️ NOT WIRED IN THIS PLUGIN
> **Corrected 2026-09-07.** This section described `article_download(doi=…)` and
> `book_download(hash=,format=,title=)` as "verified working". **Neither tool exists.** They
> are the RETIRED tool names of the upstream `iosifache/annas-mcp` Go binary, which wrote
> files to the user's disk; the self-hosted server that replaced it
> (`annas.cureonics.com`, HP Docker) removed them on purpose and returns a short-lived
> opaque `resource_link` instead — it never touches the user's filesystem. The "downloads
> land on the user's computer" note described the Go binary, not this server.
>
> **`plugins/rxpraxis/.mcp.json` also wires no annas server at all**, so this whole tier is
> currently a documented capability the plugin does not have. Skip it and record the skip;
> do not attempt these calls.

To actually enable this tier, add the connector and use the REAL surface (v0.1.0, 11 tools):

```
annas-reader: article_search(query="<DOI or keywords>", limit, page)
              # → {status, reason, rows[], evidence}; status 'empty' is a VERIFIED absence,
              #   'degraded'/'blocked' means DO NOT record an absence
annas-reader: book_search(query="...", language?, format?, min_size_mb?)
annas-reader: read_article(doi=...) / read_document(md5|id, page_start, page_end)
annas-reader: search_in_document(query, md5|id, k)      # BM25, page-referenced
annas-reader: download_document(id="<DOI|32-hex md5>")  # short-lived resource_link
annas-reader: annas_ingest_document(id, collection, doc_id?)   # full text → anamnesis
annas-reader: annas_server_info()                       # liveness / quota / capabilities
```

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

*v8.0 — (superseded 2026-09-07: `article_download` is a retired upstream Go tool name and
annas is not wired in this plugin — see the Tier 3 block above); EPMC
`get_full_text_article`/`get_copyright_status` schemas verified 9 June 2026.*
