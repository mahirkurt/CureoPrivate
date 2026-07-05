# sci-audit report template (7 axes)

Fill this shell. Keep every finding evidence-based (quote the matched text).
Report language follows the user; section titles are EN + TR paired.

---

# Scientific Integrity Audit — <document name>
# Bilimsel Bütünlük Denetimi — <belge adı>

- **Document type / Belge türü:** <systematic review | RCT | observational | qualitative | model | general>
- **Language / Dil:** <en | tr>  (axis G active: <yes/no>)
- **Strictness / Sıkılık:** <draft | certification>
- **Gate (--fail-on <level>):** <closes | does not close | n/a>
- **Overall / Genel:** <0–100> — <one-line verdict>

## Axis scores / Eksen skorları

| Axis | Eksen | Score | Blockers | Majors | Minors | Status |
|---|---|---:|---:|---:|---:|---|
| A | Reference integrity / Referans bütünlüğü | | | | | |
| B | Claim grounding / İddia temellendirme | | | | | |
| C | Statistical consistency / İstatistik tutarlılığı | | | | | |
| D | Hallucination signals / Halüsinasyon sinyalleri | | | | | |
| E | Reporting-guideline / Raporlama kılavuzu | | | | | |
| F | AI-use transparency / AI şeffaflığı | | | | | |
| G | Turkish writing / Türkçe yazım | | | | | |

Status ∈ {ran, not run, not applicable, unverified (no MCP)}.

## Blockers / Bloklayıcılar
<numbered list; each: axis, evidence quote, why it blocks, fix>

## Majors / Önemli bulgular
<numbered list>

## Minors / Küçük bulgular
<condensed list or count>

## What was NOT checked / Denetlenmeyenler
<scope notes per axis: unreachable MCP, skipped provider, sampled sections, etc.
Absence of a finding is not proof of correctness.>

## Provider / MCP status
<one line per helper: ok | error | unavailable | not run — and the effect>

## Evidence ledger / Kanıt defteri
<for a defensible audit: each resolved claim/citation with its source id,
checked-via (abstract | pubmed-epmc fulltext | crossref | …), verdict, and the
SHA-256 source-content hash from scripts/evidence_ledger.py. Omit if no external
resolution was performed.>
