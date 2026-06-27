# Extended Tier — Native-First with REST Fallback (v8.2)

**Loaded:** ALWAYS (Adım 0).
**Recreated v8.2.0 (UP-001):** referenced as always-load but absent after the v8.0→v8.1 partial
migration; reconstructed here. Endpoints below are public, documented APIs; call patterns are
illustrative templates, not verbatim vendor copy.

**Core rule (inherited from `connector-registry.md` §0):** resolve every data need on the
**Native-First ladder** — native MCP → native REST via `bash_tool`+`requests` → Exa/Tavily →
documented gap. This file covers **rung 2**: the sources that have **no native MCP** and must be
reached by REST. Where a native MCP now exists (EuropePMC, ChEMBL, openFDA), use it instead — v7.1
wrongly used REST for those; v8.x corrects it.

---

## 1. When this file applies

Use REST fallback **only** for sources without a native MCP tool:

| Source | Native MCP? | Reach by |
|---|---|---|
| OpenAlex | no | REST (§2) |
| PubChem (PUG-REST) | no | REST (§3) |
| Semantic Scholar Graph | no | REST (§4) |
| Unpaywall | no | REST (§5) — OA determination |
| DOAJ | no | REST (§5) — OA journal check |
| J-STAGE | no | REST (§6) — Japanese literature |
| DailyMed | no | REST (§7) — US SPL labeling |
| DrugBank | no (license-gated) | REST (§8) — if keyed |
| EuropePMC / ChEMBL / openFDA | **yes** | **use native MCP** (connector-registry.md) |

All calls go through `bash_tool` with Python `requests`; respect rate limits, set a descriptive
`User-Agent` (and `mailto` where the API rewards it with the polite pool), and fail loud.

---

## 2. OpenAlex (works, authors, institutions, citations)
Base: `https://api.openalex.org`. Polite pool: add `?mailto=<contact>`.
- Works by topic: `GET /works?search={topic}&filter=from_publication_date:2024-01-01&per-page=25`
- Author disambiguation (KOL map §8): `GET /authors?search={name}` → take `id`, then
  `GET /works?filter=author.id:{id}` for output + `cited_by_count` + `h_index` (in author object).
- Institution rollups for the 6-country coverage cross-check.

## 3. PubChem PUG-REST (chemistry, identifiers)
Base: `https://pubchem.ncbi.nlm.nih.gov/rest/pug`.
- Name → CID: `GET /compound/name/{drug}/cids/JSON`
- CID → properties: `GET /compound/cid/{cid}/property/MolecularFormula,CanonicalSMILES,IUPACName/JSON`
- Use for structure/identifier resolution feeding §3 Mechanism (complement ChEMBL native).

## 4. Semantic Scholar Graph API (citations, influential citations)
Base: `https://api.semanticscholar.org/graph/v1`. Optional `x-api-key` header raises limits.
- Paper lookup: `GET /paper/DOI:{doi}?fields=title,year,citationCount,influentialCitationCount,authors`
- Citation graph for KOL influence and reference chaining (§8).

## 5. Open-access determination — Unpaywall + DOAJ
- **Unpaywall:** `GET https://api.unpaywall.org/v2/{doi}?email=<contact>` → `is_oa`, `best_oa_location.url_for_pdf`.
- **DOAJ:** `GET https://doaj.org/api/search/journals/{issn}` → fully-OA journal confirmation.
- Both complement EPMC `get_copyright_status` in §10 Açık Erişim. Prefer the native EPMC gate; use
  these to widen OA coverage and locate a legal PDF for the full-text cascade.

## 6. J-STAGE (Japanese scientific literature — 6-country coverage)
Base: `https://api.jstage.jst.go.jp/searchapi/do`.
- `GET ?service=3&material=...&text={topic}` (Atom/XML). Supports the mandatory Japan arm of the
  multi-country AFF matrix when EPMC `AFF:"Japan"` is thin.

## 7. DailyMed (US Structured Product Labeling)
Base: `https://dailymed.nlm.nih.gov/dailymed/services/v2`.
- `GET /spls.json?drug_name={drug}` → setid; then `GET /spls/{setid}.json` for label sections.
- Feeds §4 Ruhsat & Etiket alongside **native** openFDA `drug/label` (openFDA primary; DailyMed
  for full SPL text/cross-check).

## 8. DrugBank (license-gated — conditional)
Base: `https://api.drugbank.com` (commercial key required). If unkeyed → **skip**, fall back to
ChEMBL native (`get_mechanism`/`get_admet`) + openFDA. Never fabricate DrugBank fields.

---

## 9. Failure & rate-limit discipline
- 429/5xx → exponential backoff (3×), then mark the rung exhausted and **descend the ladder**
  (REST empty → Exa/Tavily → "VERİ BULUNAMADI" with queries listed).
- Never silently omit a failed source; the Generosity note (`<!-- OPS -->` annex) records it.
- Keep all REST output structured (JSON) for the `.data.json` sidecar (`output-templates.md`).
