#!/usr/bin/env python3
"""evidentia PostToolUse — bibliographic working-set ledger (context-economy P0).

Tracks PMID|DOI|NCT coverage across a PRISMA run so Completeness Gate v2 can
measure ``cited_or_skipped_with_reason / include_set`` instead of only connector
call counts. Artefacts live under ``.claude/evidentia-run/<run_id>/``:

  * ``ledger.json`` — id → status / sources / skip_reason / anamnesis_doc_id
  * ``hits.jsonl``  — append-only raw ID sightings (optional audit trail)

Distinct from ``evidentia-anamnesis-run.json`` (Anamnesis doc_id exclusivity).
Fail-open. Advisory ``additionalContext`` only — never blocks.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (  # noqa: E402
    ensure_ledger,
    load_ledger,
    run_dir,
    tool_base,
)

# Bibliographic discovery / metadata tools → upsert status=identified.
SEARCH_TOOLS = {
    "pubmed_search_articles",
    "pubmed_europepmc_search",
    "pubmed_fetch_articles",
    "search_articles",
    "find_related_articles",
    "openalex_search_entities",
    "openalex_resolve_name",
    "search_papers",
    "get_paper",
    "get_paper_citations",
    "search_trials",
    "search_preprints",
    "search_published_preprints",
    "article_search",
    "book_search",
    "search",               # Consensus / generic search surfaces
    "web_search_exa",       # should not fire in fleet; harmless if present
    "oa_resolve",
    "ebsco_search",
    "kb_search",
}

# Full-text / body tools — still extract IDs (identified); model advances status.
FULLTEXT_TOOLS = {
    "oa_fetch_fulltext",
    "oa_fetch_pdf",
    "pubmed_fetch_fulltext",
    "pubmed_europepmc_fetch",
    "read_document",
    "read_article",
    "search_in_document",
    "download_document",
    "get_full_text_article",
    "read_pubmed_paper",
    "read_semantic_paper",
    "read_biorxiv_paper",
    "read_medrxiv_paper",
    "read_crossref_paper",
    "read_arxiv_paper",
    "ebsco_get",
}

STATUSES = (
    "identified",
    "screened",
    "included",
    "extracted",
    "cited",
    "skipped",
)
# Monotonic rank for upsert — never demote without an explicit skip.
_STATUS_RANK = {s: i for i, s in enumerate(STATUSES)}

PMID_RE = re.compile(
    r"(?:\"(?:pmid|PMID|pubmed_id|pubmedId)\"\s*:\s*\"?|"
    r"\bPMID[:\s#]*)(\d{5,9})\b",
    re.IGNORECASE,
)
DOI_RE = re.compile(
    r"(?:\"(?:doi|DOI)\"\s*:\s*\"?|"
    r"\b(?:doi\.org/|DOI[:\s]*))"
    r"(10\.\d{4,9}/[^\s\"'<>\]\},]+)",
    re.IGNORECASE,
)
NCT_RE = re.compile(r"\b(NCT\d{8})\b", re.IGNORECASE)
TITLE_NEAR_ID_RE = re.compile(
    r"\"(?:title|Title|display_name|displayName)\"\s*:\s*\"([^\"]{8,240})\"",
)
# Bare DOI / PMID / NCT that may appear as Anamnesis doc_id suffixes.
BARE_DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"'<>\]\},]+)", re.IGNORECASE)
BARE_PMID_RE = re.compile(r"\b(\d{5,9})\b")
RECORD_ID_KEY_RE = re.compile(
    r"\"(?:record_id|recordId)\"\s*:\s*\"([^\"]{4,128})\"",
)
DOC_ID_FIELD_RE = re.compile(
    r"\"(?:doc_id|docId)\"\s*:\s*\"([^\"]+)\"",
)

COVERAGE_FLOORS = {
    "lenient": 0.75,
    "standard": 0.90,
    "strict": 0.98,
}

_TITLE_KEYS = ("title", "Title", "display_name", "displayName")
_PMID_KEYS = ("pmid", "PMID", "pubmed_id", "pubmedId")
_DOI_KEYS = ("doi", "DOI")
_NCT_KEYS = ("nct", "NCT", "nct_id", "nctId", "clinical_trial_id")
_RECORD_KEYS = ("record_id", "recordId")


def _result_text(data: dict) -> str:
    r = data.get("tool_result", data.get("tool_response", ""))
    if isinstance(r, str):
        return r
    try:
        return json.dumps(r, ensure_ascii=False)
    except Exception:
        return str(r or "")


def _norm_id(kind: str, raw: str) -> str:
    rid = str(raw or "").strip().rstrip(").,;")
    if kind == "doi":
        return rid.lower()
    if kind == "nct":
        return rid.upper()
    return rid


def _title_from_mapping(obj: dict) -> str:
    for k in _TITLE_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v.strip()) >= 8:
            return v.strip()[:240]
    return ""


def _ids_from_mapping(obj: dict) -> list[tuple[str, str]]:
    """Bibliographic ids from one hit-like object (never from sibling hits)."""
    found: list[tuple[str, str]] = []
    for k in _PMID_KEYS:
        v = obj.get(k)
        if v is not None and str(v).strip():
            s = str(v).strip()
            if re.fullmatch(r"\d{5,9}", s):
                found.append(("pmid", _norm_id("pmid", s)))
    for k in _DOI_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            m = BARE_DOI_RE.search(v)
            if m:
                found.append(("doi", _norm_id("doi", m.group(1))))
    for k in _NCT_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            m = NCT_RE.search(v)
            if m:
                found.append(("nct", _norm_id("nct", m.group(1))))
    # Generic ``id`` only when it is clearly NCT / DOI (not EBSCO record_id).
    generic = obj.get("id")
    if isinstance(generic, str) and generic.strip():
        g = generic.strip()
        if NCT_RE.fullmatch(g):
            found.append(("nct", _norm_id("nct", g)))
        elif BARE_DOI_RE.fullmatch(g) or g.lower().startswith("10."):
            m = BARE_DOI_RE.search(g)
            if m:
                found.append(("doi", _norm_id("doi", m.group(1))))
        elif re.fullmatch(r"\d{5,9}", g) and any(k in obj for k in _PMID_KEYS):
            found.append(("pmid", _norm_id("pmid", g)))
    return found


def _record_id_from_mapping(obj: dict) -> str:
    for k in _RECORD_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v.strip()) >= 4:
            return v.strip()
    return ""


def _merge_hit(
    hits: dict[str, dict],
    *,
    kind: str,
    rid: str,
    title: str,
    source: str,
    record_id: str = "",
    anamnesis_doc_id: str = "",
) -> None:
    key = f"{kind}:{rid}"
    if key in hits:
        row = hits[key]
        if source and source not in row["sources"]:
            row["sources"].append(source)
        # Prefer a non-empty title over empty; never overwrite a set title with "".
        if title and (not row.get("title") or title != row.get("title")):
            # Structured per-object titles win over earlier empty/placeholder.
            if not row.get("title"):
                row["title"] = title
        if record_id and not row.get("record_id"):
            row["record_id"] = record_id
        if anamnesis_doc_id and not row.get("anamnesis_doc_id"):
            row["anamnesis_doc_id"] = anamnesis_doc_id
        return
    hits[key] = {
        "id": rid,
        "id_kind": kind,
        "title": title or "",
        "sources": [source] if source else [],
        "record_id": record_id or "",
        "anamnesis_doc_id": anamnesis_doc_id or "",
    }


def _walk_json_hits(node: object, source: str, hits: dict[str, dict]) -> None:
    """Walk JSON; bind each object's title only to ids found on that object."""
    if isinstance(node, dict):
        title = _title_from_mapping(node)
        record_id = _record_id_from_mapping(node)
        doc_id = ""
        for k in ("doc_id", "docId"):
            v = node.get(k)
            if isinstance(v, str) and v.strip():
                doc_id = v.strip()
                break
        local_ids = _ids_from_mapping(node)
        # EBSCO record_id alone is not a bibliographic key, but attach it to
        # sibling DOI/PMID/NCT on the same hit for later reconcile.
        for kind, rid in local_ids:
            _merge_hit(
                hits,
                kind=kind,
                rid=rid,
                title=title,
                source=source,
                record_id=record_id,
                anamnesis_doc_id=doc_id,
            )
        for v in node.values():
            _walk_json_hits(v, source, hits)
    elif isinstance(node, list):
        for item in node:
            _walk_json_hits(item, source, hits)


def _enclosing_object_slice(text: str, pos: int) -> str:
    """Return the nearest ``{...}`` slice containing ``pos`` (best-effort)."""
    start = text.rfind("{", 0, pos + 1)
    if start < 0:
        start = max(0, pos - 400)
    depth = 0
    end = len(text)
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return text[start:end]


def _title_near_span(text: str, pos: int) -> str:
    """Title from the same JSON object as ``pos`` — never the batch's first title."""
    chunk = _enclosing_object_slice(text, pos)
    titles = TITLE_NEAR_ID_RE.findall(chunk)
    if titles:
        return titles[0].strip()[:240]
    return ""


def _extract_hits_regex(text: str, source: str) -> list[dict]:
    """Regex fallback with per-match local title binding (no title broadcast)."""
    hits: dict[str, dict] = {}
    # Build record_id → nearest title map from the same object slices.
    record_near: dict[str, str] = {}
    for m in RECORD_ID_KEY_RE.finditer(text):
        rid = m.group(1).strip()
        record_near[rid] = _title_near_span(text, m.start())

    def upsert(kind: str, raw: str, pos: int) -> None:
        rid = _norm_id(kind, raw)
        if not rid:
            return
        title = _title_near_span(text, pos)
        # If this object also has a record_id, attach it.
        chunk = _enclosing_object_slice(text, pos)
        rec_m = RECORD_ID_KEY_RE.search(chunk)
        record_id = rec_m.group(1).strip() if rec_m else ""
        if not title and record_id:
            title = record_near.get(record_id, "")
        doc_m = DOC_ID_FIELD_RE.search(chunk)
        doc_id = doc_m.group(1).strip() if doc_m else ""
        _merge_hit(
            hits,
            kind=kind,
            rid=rid,
            title=title,
            source=source,
            record_id=record_id,
            anamnesis_doc_id=doc_id,
        )

    for m in PMID_RE.finditer(text):
        upsert("pmid", m.group(1), m.start())
    for m in DOI_RE.finditer(text):
        upsert("doi", m.group(1), m.start())
    for m in NCT_RE.finditer(text):
        upsert("nct", m.group(1), m.start())
    return list(hits.values())


def extract_hits(text: str, source: str) -> list[dict]:
    """Pull PMID / DOI / NCT ids from a tool result blob.

    Each id gets the title from **its own** hit object. Never broadcast the
    first title in a batch onto every id (Marmara EBSCO QA regression).
    """
    if not text:
        return []
    hits: dict[str, dict] = {}
    # Prefer structured JSON walk when the blob parses.
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = None
    if parsed is not None:
        _walk_json_hits(parsed, source, hits)
        if hits:
            return list(hits.values())
    # Partial / MCP-wrapped text: regex with per-object title binding.
    return _extract_hits_regex(text, source)


def empty_working_set(run_id: str) -> dict:
    return {
        "run_id": run_id,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "records": {},
        "schema": "evidentia.working_set.v1",
    }


def working_set_path(run_id: str | None = None) -> Path:
    return run_dir(run_id) / "ledger.json"


def hits_path(run_id: str | None = None) -> Path:
    return run_dir(run_id) / "hits.jsonl"


def load_working_set(run_id: str | None = None) -> dict:
    path = working_set_path(run_id)
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("records"), dict):
                return data
    except Exception:
        pass
    rid = run_id
    if not rid:
        led = load_ledger() or ensure_ledger()
        rid = led["run_id"]
    return empty_working_set(rid)


def save_working_set(ws: dict) -> None:
    try:
        path = working_set_path(ws.get("run_id"))
        path.parent.mkdir(parents=True, exist_ok=True)
        ws["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(ws, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        tmp.replace(path)
    except Exception:
        pass


def append_hits(run_id: str, rows: list[dict], tool: str) -> None:
    if not rows:
        return
    try:
        path = hits_path(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "tool": tool,
                    "id": row.get("id"),
                    "id_kind": row.get("id_kind"),
                    "title": row.get("title") or "",
                    "source": (row.get("sources") or [""])[0],
                }, ensure_ascii=False) + "\n")
    except Exception:
        pass


def upsert_identified(
    ws: dict,
    hit: dict,
    *,
    phase: str = "P1",
    source: str = "",
    overwrite_title: bool = False,
) -> bool:
    """Insert or merge a bibliographic hit. Returns True if ledger changed.

    ``overwrite_title=True`` (ebsco_get / fulltext success) is last-write-wins
    for title + metadata so a corrected get response fixes search-batch drift.
    """
    rid = str(hit.get("id") or "").strip()
    if not rid:
        return False
    kind = str(hit.get("id_kind") or "id").lower()
    key = f"{kind}:{rid}" if kind != "id" else rid
    recs = ws.setdefault("records", {})
    src = source or ((hit.get("sources") or [""])[0])
    changed = False
    if key not in recs:
        recs[key] = {
            "id": rid,
            "id_kind": kind,
            "title": hit.get("title") or "",
            "sources": [src] if src else [],
            "phase_seen": [phase],
            "status": "identified",
            "skip_reason": None,
            "anamnesis_doc_id": hit.get("anamnesis_doc_id") or None,
            "record_id": hit.get("record_id") or None,
            "cited_chunks": [],
        }
        return True
    rec = recs[key]
    if src and src not in (rec.get("sources") or []):
        rec.setdefault("sources", []).append(src)
        changed = True
    if phase and phase not in (rec.get("phase_seen") or []):
        rec.setdefault("phase_seen", []).append(phase)
        changed = True
    new_title = (hit.get("title") or "").strip()
    if new_title:
        if overwrite_title or not (rec.get("title") or "").strip():
            if rec.get("title") != new_title:
                rec["title"] = new_title
                changed = True
    rec_id = (hit.get("record_id") or "").strip()
    if rec_id and rec.get("record_id") != rec_id:
        rec["record_id"] = rec_id
        changed = True
    aid = (hit.get("anamnesis_doc_id") or "").strip()
    if aid and rec.get("anamnesis_doc_id") != aid:
        rec["anamnesis_doc_id"] = aid
        changed = True
    # Do not demote status on re-sight.
    return changed


def set_status(
    ws: dict,
    record_key: str,
    status: str,
    *,
    skip_reason: str | None = None,
    anamnesis_doc_id: str | None = None,
    cited_chunk: str | None = None,
    phase: str | None = None,
) -> bool:
    if status not in _STATUS_RANK:
        return False
    rec = (ws.get("records") or {}).get(record_key)
    if not rec:
        return False
    cur = rec.get("status") or "identified"
    # Allow skip from any state; otherwise only promote.
    if status != "skipped" and _STATUS_RANK[status] < _STATUS_RANK.get(cur, 0):
        return False
    rec["status"] = status
    if skip_reason is not None:
        rec["skip_reason"] = skip_reason
    if anamnesis_doc_id:
        rec["anamnesis_doc_id"] = anamnesis_doc_id
    if cited_chunk:
        chunks = rec.setdefault("cited_chunks", [])
        if cited_chunk not in chunks:
            chunks.append(cited_chunk)
    if phase and phase not in (rec.get("phase_seen") or []):
        rec.setdefault("phase_seen", []).append(phase)
    return True


def coverage_stats(ws: dict, gate: str = "standard") -> dict:
    """Completeness Gate v2 metric over the include_set.

    ``coverage = cited_or_skipped_with_reason / include_set``
    include_set = status ∈ {included, extracted, cited, skipped} OR
                  explicitly status=included|extracted|cited.
    Records still at identified/screened are NOT in the denominator until
    screening promotes them.
    """
    recs = list((ws.get("records") or {}).values())
    include = [
        r for r in recs
        if (r.get("status") or "") in {"included", "extracted", "cited", "skipped"}
    ]
    cited_or_skipped = []
    for r in include:
        st = r.get("status") or ""
        if st == "cited":
            cited_or_skipped.append(r)
        elif st == "skipped" and (r.get("skip_reason") or "").strip():
            cited_or_skipped.append(r)
        elif st in {"included", "extracted"}:
            # Still open work — not yet cited/skipped.
            pass
    n_inc = len(include)
    n_ok = len(cited_or_skipped)
    ratio = (n_ok / n_inc) if n_inc else 1.0
    floor = COVERAGE_FLOORS.get(
        (gate or "standard").lower(), COVERAGE_FLOORS["standard"]
    )
    return {
        "include_set": n_inc,
        "cited_or_skipped_with_reason": n_ok,
        "coverage": round(ratio, 4),
        "floor": floor,
        "gate": gate,
        "pass": ratio >= floor,
        "identified": sum(1 for r in recs if r.get("status") == "identified"),
        "total_records": len(recs),
    }


def coverage_block(ws: dict, gate: str = "standard") -> dict:
    """Synthesizer-required Completeness Gate v2 return block (P2 contract)."""
    stats = coverage_stats(ws, gate=gate)
    recs = ws.get("records") or {}
    n_cited = sum(1 for r in recs.values() if (r.get("status") or "") == "cited")
    n_skipped = sum(
        1 for r in recs.values()
        if (r.get("status") or "") == "skipped" and (r.get("skip_reason") or "").strip()
    )
    uncovered = []
    for key, r in recs.items():
        st = r.get("status") or ""
        if st not in {"included", "extracted", "cited", "skipped"}:
            continue
        if st == "cited":
            continue
        if st == "skipped" and (r.get("skip_reason") or "").strip():
            continue
        uncovered.append({
            "key": key,
            "id": r.get("id"),
            "id_kind": r.get("id_kind"),
            "status": st,
            "title": (r.get("title") or "")[:120],
        })
    return {
        "n_include": stats["include_set"],
        "n_cited": n_cited,
        "n_skipped_reasoned": n_skipped,
        "coverage": stats["coverage"],
        "floor": stats["floor"],
        "gate": stats["gate"],
        "pass": stats["pass"],
        "uncovered": uncovered,
        # Backward-compatible aliases used by P0 prose / Ops sidecar.
        "include_set": stats["include_set"],
        "cited_or_skipped_with_reason": stats["cited_or_skipped_with_reason"],
    }


def _strip_evrun_prefix(doc_id: str, run_id: str) -> str:
    """Peel ``evrun:<run_id>:`` / any ``evrun:<12hex>:`` prefix from a doc_id."""
    from anamnesis_run import PREFIX_RE, prefix_for
    s = str(doc_id or "").strip()
    if not s:
        return s
    if run_id:
        want = prefix_for(run_id)
        if s.startswith(want):
            return s[len(want):]
    m = PREFIX_RE.match(s)
    if m:
        return s[m.end():]
    return s


def _bibliographic_tokens(raw: str) -> list[tuple[str, str]]:
    """DOI / PMID / NCT tokens embedded in a doc_id or suffix."""
    s = str(raw or "").strip()
    if not s:
        return []
    out: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(kind: str, rid: str) -> None:
        key = f"{kind}:{rid}"
        if key in seen:
            return
        seen.add(key)
        out.append((kind, rid))

    doi_m = BARE_DOI_RE.search(s)
    if doi_m:
        add("doi", _norm_id("doi", doi_m.group(1)))
    nct_m = NCT_RE.search(s)
    if nct_m:
        add("nct", _norm_id("nct", nct_m.group(1)))
    # PMID only when the whole suffix (or trailing segment) is digits — avoid
    # chewing random numbers out of DOIs / record hashes.
    if re.fullmatch(r"\d{5,9}", s):
        add("pmid", _norm_id("pmid", s))
    else:
        tail = s.rsplit(":", 1)[-1]
        if re.fullmatch(r"\d{5,9}", tail):
            add("pmid", _norm_id("pmid", tail))
    return out


def _match_ledger_key(ws: dict, suffix: str) -> str | None:
    """Map an anamnesis doc suffix (PMID|DOI|record|bare) onto a working-set key."""
    raw = str(suffix or "").strip()
    if not raw:
        return None
    # Skip collection names mistaken for doc ids.
    if raw.startswith(("evidentia:run:", "evidentia:sess:", "cureolex:",
                       "marmara:fetch:")) and "/" not in raw and "10." not in raw:
        # marmara:fetch:<sha> has no bibliographic payload — not a ledger key.
        if raw.startswith("marmara:fetch:"):
            return None
        if raw.startswith(("evidentia:", "cureolex:")):
            return None
    recs = ws.get("records") or {}
    candidates = [
        f"doi:{raw.lower()}",
        f"pmid:{raw}",
        f"nct:{raw.upper()}",
        raw,
        raw.lower(),
    ]
    for kind, rid in _bibliographic_tokens(raw):
        candidates.append(f"{kind}:{rid}")
    for c in candidates:
        if c in recs:
            return c
    # Soft match: key ends with :suffix or id equals suffix (casefold for DOI).
    low = raw.lower()
    for key, rec in recs.items():
        rid = str(rec.get("id") or "")
        if rid == raw or rid.lower() == low:
            return key
        if key.endswith(":" + raw) or key.endswith(":" + low):
            return key
        # EBSCO ingest often stores doc_id = record_id when caller omits
        # evrun:/DOI; match via search-time record_id attachment.
        rec_id = str(rec.get("record_id") or "").strip()
        if rec_id and (rec_id == raw or rec_id.lower() == low):
            return key
    # Token soft-match: doc_id contains a ledger DOI/PMID/NCT.
    for kind, rid in _bibliographic_tokens(raw):
        key = f"{kind}:{rid}"
        if key in recs:
            return key
    return None


def parse_list_docs_ids(text: str) -> list[str]:
    """Extract doc_id values from a list_docs tool result blob.

    Anamnesis ``list_docs`` returns SQL rows with field ``id`` (not ``doc_id``).
    Prefer explicit ``doc_id`` / ``docId``; also accept ``id`` when it is not a
    collection name.
    """
    if not text:
        return []
    out, seen = [], set()

    def _keep(s: str) -> None:
        s = s.strip()
        if not s or s in seen:
            return
        # Collection names are not documents.
        if re.match(
            r"^(?:evidentia|cureolex|historia|vekayinuvis):"
            r"(?:run|sess|lib|scratch):",
            s,
        ):
            return
        seen.add(s)
        out.append(s)

    for m in re.finditer(r"\"(?:doc_id|docId)\"\s*:\s*\"([^\"]+)\"", text):
        _keep(m.group(1))
    # Anamnesis list_docs row primary key is ``id``.
    for m in re.finditer(r"\"id\"\s*:\s*\"([^\"]+)\"", text):
        _keep(m.group(1))
    return out


def reconcile_anamnesis_ledger(
    ws: dict,
    anamnesis_doc_ids: list[str],
    *,
    run_id: str | None = None,
    phase: str = "P4",
    promote_extracted: bool = True,
) -> dict:
    """Reconcile Anamnesis working memory with the bibliographic ledger (P1).

    * Links matching ``evrun:<run_id>:<PMID|DOI>`` / bare DOI|PMID|NCT /
      EBSCO ``record_id`` → set ``anamnesis_doc_id``; optionally promote to
      ``extracted``.
    * ``missing_extractions`` — include_set rows still without a live Anamnesis doc.
    * ``orphans`` — Anamnesis docs with no matching ledger record.

    Does **not** invent Worker API calls — caller supplies ``list_docs`` ids
    (or the Anamnesis doc_id ledger as a proxy). Mutates ``ws`` in place.
    """
    rid = run_id or ws.get("run_id") or ""
    docs = [str(d).strip() for d in (anamnesis_doc_ids or []) if str(d).strip()]
    linked = 0
    changed = False
    matched_keys: set[str] = set()
    orphans: list[str] = []

    for doc in docs:
        suffix = _strip_evrun_prefix(doc, rid) if rid else _strip_evrun_prefix(doc, "")
        key = _match_ledger_key(ws, suffix)
        if not key:
            # Retry with the raw doc_id (record_id / DOI without peel).
            key = _match_ledger_key(ws, doc)
        if not key:
            orphans.append(doc)
            continue
        matched_keys.add(key)
        rec = (ws.get("records") or {}).get(key) or {}
        if rec.get("anamnesis_doc_id") != doc:
            rec["anamnesis_doc_id"] = doc
            changed = True
        if promote_extracted:
            cur = rec.get("status") or "identified"
            if cur in {"identified", "screened", "included"}:
                if set_status(ws, key, "extracted", anamnesis_doc_id=doc, phase=phase):
                    changed = True
            elif phase and phase not in (rec.get("phase_seen") or []):
                rec.setdefault("phase_seen", []).append(phase)
                changed = True
        linked += 1

    missing: list[dict] = []
    for key, rec in (ws.get("records") or {}).items():
        st = rec.get("status") or ""
        if st not in {"included", "extracted", "cited", "skipped"}:
            continue
        if st == "skipped":
            continue  # reasoned skip — no extraction expected
        aid = (rec.get("anamnesis_doc_id") or "").strip()
        if aid and aid in docs:
            continue
        if key in matched_keys:
            continue
        missing.append({
            "key": key,
            "id": rec.get("id"),
            "id_kind": rec.get("id_kind"),
            "status": st,
            "title": (rec.get("title") or "")[:120],
        })
        if not rec.get("extraction_gap"):
            rec["extraction_gap"] = True
            changed = True

    # Clear gap flag on linked rows.
    for key in matched_keys:
        rec = (ws.get("records") or {}).get(key)
        if rec and rec.pop("extraction_gap", None):
            changed = True

    return {
        "linked": linked,
        "missing_extractions": missing,
        "orphans": orphans,
        "changed": changed,
        "n_anamnesis": len(docs),
        "n_ledger": len(ws.get("records") or {}),
    }


def reconcile_advisory(report: dict, ws: dict) -> str:
    miss = report.get("missing_extractions") or []
    orph = report.get("orphans") or []
    miss_ids = ", ".join(
        (m.get("key") or m.get("id") or "?") for m in miss[:8]
    ) or "(yok)"
    orph_ids = ", ".join(orph[:8]) or "(yok)"
    more_m = f" +{len(miss) - 8}" if len(miss) > 8 else ""
    more_o = f" +{len(orph) - 8}" if len(orph) > 8 else ""
    return (
        "[evidentia] anamnesis↔ledger reconcile (P1): "
        "linked={linked}/{n_ana}; missing_extractions={n_miss} [{miss}{more_m}]; "
        "orphans={n_orph} [{orph}{more_o}]. "
        "P4 extract / P6 synthesize öncesi: eksikleri ingest veya skip_reason ile kapat; "
        "yetim doc_id'leri ledger'a bağla veya forget. "
        "Scratch: `.claude/evidentia-run/{rid}/ledger.json`."
    ).format(
        linked=report.get("linked") or 0,
        n_ana=report.get("n_anamnesis") or 0,
        n_miss=len(miss),
        miss=miss_ids,
        more_m=more_m,
        n_orph=len(orph),
        orph=orph_ids,
        more_o=more_o,
        rid=ws.get("run_id") or "?",
    )


def advisory_message(ws: dict, n_new: int, tool: str) -> str:
    stats = coverage_stats(ws)
    return (
        "[evidentia] working-set ledger: '{tool}' → +{n} ID "
        "(toplam {total}; identified={identified}; include_set={inc}; "
        "coverage={cov} floor={floor}). "
        "P1/P2: yalnız ID+title+year bağlama al — ham gövde sentez girdisi değil. "
        "Scratch: `.claude/evidentia-run/{rid}/ledger.json` (+ hits.jsonl). "
        "Anamnesis doc_id ledger ayrı kalır (münhasırlık)."
    ).format(
        tool=tool,
        n=n_new,
        total=stats["total_records"],
        identified=stats["identified"],
        inc=stats["include_set"],
        cov=stats["coverage"],
        floor=stats["floor"],
        rid=ws.get("run_id") or "?",
    )


def _handle_list_docs_reconcile(data: dict, rid: str) -> int:
    """PostToolUse list_docs → reconcile Anamnesis SoT with bibliographic ledger."""
    text = _result_text(data)
    if len(text) > 200_000:
        text = text[:100_000] + "\n" + text[-100_000:]
    docs = parse_list_docs_ids(text)
    # Prefer live list_docs; fall back to Anamnesis doc_id ledger (exclusive set).
    if not docs:
        led = load_ledger() or {}
        docs = list(led.get("doc_ids") or [])
    ws = load_working_set(rid)
    ws["run_id"] = rid
    report = reconcile_anamnesis_ledger(ws, docs, run_id=rid, phase="P4")
    if report.get("changed"):
        save_working_set(ws)
    # Always surface reconcile when list_docs fires (even empty) so P4/P6 see gaps.
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reconcile_advisory(report, ws),
        }
    }))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    tool = str(data.get("tool_name", ""))
    if not tool.startswith("mcp__"):
        return 0
    base = tool_base(tool)

    try:
        led = load_ledger() or ensure_ledger()
        rid = led["run_id"]

        # P1: list_docs → reconcile working-set ledger with Anamnesis collection.
        if base == "list_docs" and "anamnesis" in tool.lower():
            return _handle_list_docs_reconcile(data, rid)

        if base not in SEARCH_TOOLS and base not in FULLTEXT_TOOLS:
            return 0

        text = _result_text(data)
        # Cap parse cost on huge dumps — IDs usually appear in the head/tail.
        if len(text) > 200_000:
            text = text[:100_000] + "\n" + text[-100_000:]
        phase = "P4" if base in FULLTEXT_TOOLS else "P1"
        hits = extract_hits(text, source=base)
        if not hits:
            return 0
        ws = load_working_set(rid)
        ws["run_id"] = rid
        # ebsco_get / fulltext: last-write-wins title + link anamnesis_doc_id
        # from the get envelope when present.
        overwrite = base in FULLTEXT_TOOLS
        n_new = 0
        for hit in hits:
            before = len(ws.get("records") or {})
            upsert_identified(
                ws, hit, phase=phase, source=base, overwrite_title=overwrite,
            )
            if len(ws.get("records") or {}) > before:
                n_new += 1
            # Immediate link when get response carries anamnesis doc_id.
            aid = (hit.get("anamnesis_doc_id") or "").strip()
            if aid and overwrite:
                kind = str(hit.get("id_kind") or "id").lower()
                hrid = str(hit.get("id") or "").strip()
                key = f"{kind}:{hrid}" if kind != "id" else hrid
                rec = (ws.get("records") or {}).get(key)
                if rec is not None:
                    if rec.get("anamnesis_doc_id") != aid:
                        rec["anamnesis_doc_id"] = aid
                    cur = rec.get("status") or "identified"
                    if cur in {"identified", "screened", "included"}:
                        set_status(
                            ws, key, "extracted",
                            anamnesis_doc_id=aid, phase=phase,
                        )
        save_working_set(ws)
        append_hits(rid, hits, tool=base)
        if n_new or hits:
            sys.stdout.write(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": advisory_message(ws, n_new or len(hits), base),
                }
            }))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
