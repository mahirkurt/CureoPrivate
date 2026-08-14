#!/usr/bin/env python3
"""evidentia PostToolUse advisory — retrieve-don't-dump guard.

When an MCP tool returns a big body, this hook reminds the model NOT to reason over the raw dump
(which overflows the context window and yields incomplete/inconsistent appraisal) but to index it
once into the anamnesis RAG substrate and pull bounded, provenance-stamped slices — the
evidence_index discipline (CONNECTORS.md §3 / canonical-cache-contract.md).

SIZE IS THE TRIGGER, NOT THE TOOL NAME (fixed 2026-08-07). Until then this hook fired only for a
hardcoded list of ~10 full-text tool names, so it stayed silent for every large response from a
tool nobody had enumerated — which is exactly the failure it exists to prevent. Measured on the
live fleet the same day:

    openfda.openfda_search(endpoint="drug/label", limit=2)  → 254,891 chars   (hook silent)
    titck.search_drugs(query="varfarin")                    →  78,837 chars   (hook silent)
    anamnesis.semantic_search(k=3)                          →  50,444 chars   (hook silent)
    annas-reader.article_search(limit=3)                    →     438 chars   (correctly quiet)

A single openFDA label pair therefore delivered ~250 KB into the window with no advisory at all.
The name list is kept — but only to pick the MESSAGE (full-text → ingest-once; anything else →
narrow the query), never to decide whether to look.

Advisory only: never blocks; emits a systemMessage when the result exceeds the threshold.
Fail-open on any error. Thresholds overridable via EVIDENTIA_DUMP_THRESHOLD (full-text tools) and
EVIDENTIA_BULK_THRESHOLD (every other MCP tool).
"""
import json
import os
import sys

# Tools whose output is full-text / large bibliographic bodies (basename match). These get the
# ingest-once message; everything else gets the narrow-the-query message. Names verified against
# the live fleet inventory 2026-08-14. The original-file tools normally return only compact link
# metadata, but remain classified here so an unexpectedly embedded body is still diverted to RAG.
FULLTEXT_TOOLS = {
    "oa_fetch_fulltext",            # openathens Tier 3 licensed
    "oa_fetch_pdf",                 # openathens original PDF resource link
    "pubmed_fetch_fulltext",        # pubmed-epmc, Unpaywall legal-OA
    "pubmed_europepmc_fetch",       # pubmed-epmc, Europe PMC body
    "read_document", "read_article", "search_in_document",   # annas-reader
    "download_document",            # annas original-file resource link
    "get_full_text_article",        # claude.ai PubMed connector (operator-connected)
    "read_pubmed_paper", "read_semantic_paper", "read_biorxiv_paper",
    "read_medrxiv_paper", "read_crossref_paper", "read_arxiv_paper",  # Paper Search (operator)
}

DEFAULT_THRESHOLD = 6000    # chars — full-text tools: a body this size belongs in the RAG substrate
BULK_THRESHOLD = 25000      # chars — any other MCP tool: a result this size is a bulk dump


def result_len(data):
    """Best-effort length of the tool result across shapes (str / dict / content-blocks)."""
    r = data.get("tool_result", data.get("tool_response", ""))
    try:
        if isinstance(r, str):
            return len(r)
        return len(json.dumps(r, ensure_ascii=False))
    except Exception:
        return 0


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = str(data.get("tool_name", ""))
    if not tool.startswith("mcp__"):
        sys.exit(0)
    base = tool.split("__")[-1]
    fulltext = base in FULLTEXT_TOOLS

    env_var = "EVIDENTIA_DUMP_THRESHOLD" if fulltext else "EVIDENTIA_BULK_THRESHOLD"
    default = DEFAULT_THRESHOLD if fulltext else BULK_THRESHOLD
    try:
        threshold = int(os.environ.get(env_var, default))
    except Exception:
        threshold = default

    n = result_len(data)
    if n <= threshold:
        sys.exit(0)

    kb = round(n / 1024, 1)
    if fulltext:
        msg = (
            "[evidentia] retrieve-don't-dump: '{base}' ~{kb} KB tam-metin/büyük çıktı döndürdü. "
            "Bunu HAM olarak işleme (bağlam-penceresi taşması → eksik/tutarsız değerlendirme). "
            "anamnesis.ingest_document(doc_id=<DOI>) ile BİR KEZ indeksle → "
            "semantic_search / hybrid_query(queries=[...]) ile sınırlı, provenance-damgalı, "
            "graph-temelli dilim çek (evidence_index; CONNECTORS.md §3). Aynı doc_id iki kez ingest edilmez."
        ).format(base=base, kb=kb)
    else:
        msg = (
            "[evidentia] retrieve-don't-dump: '{base}' ~{kb} KB döndürdü — tam-metin aracı değil, "
            "yani bu ÇOK GENİŞ bir sorgu sonucu. Ham dökümü akıl yürütme girdisi yapma. "
            "Önce sorguyu DARALT (daha dar `search`/filtre, daha küçük `limit`, `count` toplaması, "
            "gerekli alanları seç); yine de büyükse anamnesis.ingest_document ile BİR KEZ indeksle → "
            "hybrid_query(queries=[...]) ile sınırlı dilim çek (evidence_index; CONNECTORS.md §3). "
            "Not: openfda `drug/label` tek kayıtta ~100 KB'dır — `limit=1` + dar `search` kullan."
        ).format(base=base, kb=kb)
    sys.stdout.write(json.dumps({"systemMessage": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
