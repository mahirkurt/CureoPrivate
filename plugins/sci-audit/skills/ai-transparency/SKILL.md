---
name: ai-transparency
description: Use when checking whether an LLM-generated scientific text discloses its AI use (axis F) — trigger on "is AI use disclosed", "check AI transparency", "ICMJE AI statement", "yapay zeka beyanı var mı", "AI disclosure", "undisclosed AI". Scans for a present/absent AI-use disclosure statement (ICMJE/COPE/WAME) and LLM giveaway signals, and flags unfilled placeholders.
---

# AI-Use Transparency (axis F)

Check that the text carries the AI-use disclosure publishers now require, and
surface signals of undisclosed AI assistance.

## Run it

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/ai-transparency/scripts/ai_transparency.py" <file>
# informal draft where a disclosure is not yet expected:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/ai-transparency/scripts/ai_transparency.py" <file> --no-require-disclosure
```

What it flags:
- **missing-ai-disclosure** — no AI-use statement found. **Blocker** when LLM
  giveaway signals are also present; **major** otherwise (the text may be
  human-written). An explicit "no AI was used" counts as a valid disclosure.
- **undisclosed-ai-signal** — verbatim LLM boilerplate left in the text
  ("as an AI language model", "knowledge cutoff", "Certainly! Here's",
  "yapay zeka dil modeli olarak") (**major**).
- **unfilled-placeholder** — `[insert citation]`, `[TODO]`, Lorem ipsum
  (**major**).

## Standards

ICMJE, COPE, and WAME require authors to disclose whether and how generative AI
was used in producing the work (AI cannot be an author; humans are accountable).
Most publishers now mandate a "Use of AI" / "Declaration of generative AI"
statement in the methods or acknowledgements.

## Invariant

This detects the PRESENCE/ABSENCE of a disclosure and LLM giveaway phrasing — it
cannot prove a text was or was not AI-assisted. Absence of signals is not proof
of no AI use; a present disclosure is not verification of its accuracy. Report
findings as a prompt to the author, not an accusation.
