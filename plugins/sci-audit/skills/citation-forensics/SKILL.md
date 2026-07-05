---
name: citation-forensics
description: Use when auditing the references of an LLM-generated scientific text for fabricated or hallucinated sources (axis A) — trigger on "are these citations real", "check the DOIs", "verify the references", "did the model make up this paper", "kaynak uydurma kontrolü". Resolves each DOI/PMID/arXiv id against remote scholarly MCPs, matches title/author/year/journal metadata, and checks retraction status.
---

# Citation Forensics (axis A)

Detect fabricated, misattributed, or retracted references. LLMs invent
plausible-looking citations; this axis catches them by resolving each one
against a real bibliographic source.

## Method

1. **Extract references.** Pull every citation, DOI, PMID, arXiv id, and
   reference-list entry from the text. Preserve the exact string as evidence.
2. **Structural pre-screen (deterministic, free).** Before any network call,
   flag structurally impossible identifiers with the
   `hallucination-signals/scripts/hallucination_signals.py` output: DOIs not
   matching `10.NNNN/…`, PMIDs with 9+ digits, "in press" with no venue. These
   are high-confidence fabrication smells.
3. **Resolve against MCP.** For each surviving identifier, use the
   `citation-verifier` agent to resolve it:
   - DOI / general → `openalex`, cross-check `crossref`.
   - PMID / biomedical → `pubmed`, cross-check `semantic-scholar`.
   Compare the resolved title, first author, year, and venue against what the
   text claims. A mismatch on title or author is a **blocker**; a year/venue
   mismatch is a **major**.
4. **Retraction check.** Query `crossref` + `pubmed` for retraction/expression-
   of-concern status. A cited retracted paper used as positive evidence is a
   **blocker**.
5. **Degrade honestly.** If an MCP is unavailable, mark the reference
   `unverified (no MCP)` — not a pass. It can not be a blocker on its own; say
   so in the report.

## Output

A per-reference table: `evidence | id | resolved? | metadata match | retraction
| verdict`. Verdicts: `verified`, `mismatch (blocker/major)`, `not found
(likely fabricated)`, `retracted`, `unverified (no MCP)`.

## Invariant

Never "confirm" a citation you could not resolve. A citation the model recalls
correctly-looking but that no source returns is reported as **not found →
likely fabricated**, with the reasoning shown.
