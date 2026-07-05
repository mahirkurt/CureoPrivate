---
name: hallucination-signals
description: Use when scanning an LLM-generated scientific text for hallucination and confabulation signals (axis D) — trigger on "does this sound made up", "check for hallucination", "over-certainty language", "invented method names", "halüsinasyon sinyalleri", "aşırı kesinlik". Flags over-certainty absolutes, universal quantifiers, malformed identifiers, and uncited named methods; optionally runs semantic entropy with a sampling backend.
---

# Hallucination Signals (axis D)

Surface the textual tells that correlate with LLM confabulation. This axis does
not decide truth; it raises signals for human or MCP verification.

## Deterministic signals (free, no network)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/hallucination-signals/scripts/hallucination_signals.py" <file>
```

Flags:
- **Over-certainty** — "proves", "definitively", "100% accurate", "kesin olarak
  kanıtlar". Empirical claims carry uncertainty (**major**).
- **Universal quantifiers** — "all studies show", "no study has ever", "her
  zaman", "hiçbir çalışma" (**major**).
- **Malformed identifiers** — DOI not matching `10.NNNN/…` (**blocker**), PMID
  with 9+ digits (**major**), "in press" with no venue (**minor**).
- **Uncited named methods** — an ALL-CAPS acronym presented as an established
  algorithm/framework with no nearby citation (**minor**) — a common invented-
  tool shape; confirm it exists.

## Consistency signal (semantic entropy)

`scripts/semantic_entropy.py` implements Farquhar et al. (Nature 2024):
sample N answers to the same question, cluster by meaning via bidirectional
entailment, and compute entropy over meaning-clusters. High entropy → the model
is unsure of the *meaning* → confabulation risk.

It is backend-agnostic (stdlib only). Wire `generate` (a temperature>0 sampler)
and `entails` (an NLI judge) — in-plugin, drive both with a Claude subagent; in
CI, plug any backend. Honest cost: ~5–10× compute (must sample several
generations) — reserve it for high-stakes claims, not every line.

## Invariant

A signal is a prompt to verify, not a verdict. Escalate flagged claims to axis A
(citation-forensics) or axis B (claim-grounding). Absence of signals is not
proof the text is not confabulated.
