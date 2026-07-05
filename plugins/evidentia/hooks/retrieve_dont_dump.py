#!/usr/bin/env python3
"""evidentia PostToolUse advisory — retrieve-don't-dump guard.

When a full-text / large-output MCP tool returns a big body, this hook reminds the model NOT to
reason over the raw dump (which overflows the context window and yields incomplete/inconsistent
appraisal) but to index it once into the anamnesis RAG substrate and pull bounded, provenance-
stamped slices — the evidence_index discipline (CONNECTORS.md §3 / canonical-cache-contract.md).

Advisory only: never blocks; emits a systemMessage when the result exceeds the size threshold.
Fail-open on any error. Size threshold overridable via EVIDENTIA_DUMP_THRESHOLD (chars).
"""
import json
import os
import sys

# Tools whose output is full-text / large bibliographic bodies (basename match).
FULLTEXT_TOOLS = {
    "oa_fetch_fulltext",            # openathens Tier 3 licensed
    "get_full_text_article",       # EuropePMC PMC OA
    "pubmed_fetch_fulltext",       # Unpaywall legal-OA
    "read_pubmed_paper", "read_semantic_paper", "read_biorxiv_paper",
    "read_medrxiv_paper", "read_crossref_paper", "read_arxiv_paper",
    "article_download", "book_download",   # annas full text
    "get_document_text",           # large document bodies
}

DEFAULT_THRESHOLD = 6000  # chars


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
    if base not in FULLTEXT_TOOLS:
        sys.exit(0)

    try:
        threshold = int(os.environ.get("EVIDENTIA_DUMP_THRESHOLD", DEFAULT_THRESHOLD))
    except Exception:
        threshold = DEFAULT_THRESHOLD

    n = result_len(data)
    if n <= threshold:
        sys.exit(0)

    msg = (
        "[evidentia] retrieve-don't-dump: '{base}' ~{kb} KB tam-metin/büyük çıktı döndürdü. "
        "Bunu HAM olarak işleme (bağlam-penceresi taşması → eksik/tutarsız değerlendirme). "
        "anamnesis.ingest_document(doc_id=<DOI>) ile BİR KEZ indeksle → "
        "semantic_search / hybrid_query(queries=[...]) ile sınırlı, provenance-damgalı, "
        "graph-temelli dilim çek (evidence_index; CONNECTORS.md §3). Aynı doc_id iki kez ingest edilmez."
    ).format(base=base, kb=round(n / 1024, 1))
    sys.stdout.write(json.dumps({"systemMessage": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
