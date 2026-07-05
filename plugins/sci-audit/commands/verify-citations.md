---
description: Axis A only — detect fabricated, misattributed, or retracted references
argument-hint: <file-or-paste>
allowed-tools: Read, Bash, Grep, Task
---

Run axis A (reference integrity) over the text in `$ARGUMENTS`.

Load the `citation-forensics` skill and follow it:

1. Extract every citation, DOI, PMID, arXiv id, and reference-list entry;
   preserve each exact string as evidence.
2. Deterministic pre-screen with
   `skills/hallucination-signals/scripts/hallucination_signals.py` for
   structurally impossible identifiers (malformed DOI, over-long PMID).
3. For each surviving id, use the `citation-verifier` subagent to resolve it
   against the scholarly MCPs (`openalex`+`crossref` for DOIs,
   `pubmed`+`semantic-scholar` for PMIDs), matching title/author/year/venue.
4. Check retraction status via `crossref`+`pubmed`.
5. If an MCP is unavailable, mark the reference `unverified (no MCP)` — never a
   pass, never a lone blocker.

Output a per-reference table: `evidence | id | resolved? | metadata match |
retraction | verdict`. Never confirm a citation you could not resolve; report
an unresolvable one as "not found → likely fabricated" with the reasoning.
