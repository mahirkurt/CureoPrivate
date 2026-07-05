---
name: claim-grounding
description: Use when checking whether the numeric and factual claims in an LLM-generated scientific text are actually supported by a cited source (axis B) — trigger on "is this number sourced", "check claim grounding", "does the citation support this", "kaynaksız iddia var mı", "iddia temellendirme". Extracts claims, checks each for a nearby source marker, and escalates to evidence matching against scholarly MCPs.
---

# Claim Grounding (axis B)

A citation existing (axis A) is not the same as a citation *supporting* the
claim next to it. Axis B checks that every quantitative/factual claim is
grounded.

## Method

1. **Deterministic floor (free, no network).** Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/claim-grounding/scripts/claim_grounding.py" <file> --fail-on error
   ```
   It extracts quantitative/factual claims and flags any with no nearby source
   marker (citation, DOI/PMID, URL, table/figure, file path) as
   `unsourced-claim` (blocker). It also reports a grounding rate. This is the
   same contract the Stop hook enforces per-turn.
2. **Evidence matching (escalation).** For grounded claims whose support is
   in doubt, use the `claim-extractor` agent to turn a section into a structured
   claim list, then the `claim-refuter` agent to adversarially test whether the
   cited source actually supports each claim — resolving the source via
   `pubmed` / `semantic-scholar` / `openalex`. A claim contradicted by its own
   cited source is a **blocker**.
3. **Optional RAGAS faithfulness (CI only).** If `ragas` is installed and
   retrieved contexts are supplied, a faithfulness score can be computed in CI.
   The deterministic floor never depends on it (`ragas_available()` probe).

## Output

`claim | source marker present? | source supports it? | verdict`, plus the
grounding rate and the count of unsourced claims. Verdicts: `grounded`,
`unsupported (blocker)`, `contradicted (blocker)`, `unverified (no MCP)`.

## Invariant

An unsourced number is a violation, never rounded away. Absence of a
contradiction is not proof of support — say which claims were resolved against a
source and which were only checked for a marker.
