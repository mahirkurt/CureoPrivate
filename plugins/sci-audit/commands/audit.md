---
description: Full seven-axis scientific-integrity audit of an LLM-generated text
argument-hint: <file-or-paste> [--lang tr|en] [--strictness draft|certification] [--type prisma|consort|strobe|coreq|srqr|jars|tripod]
allowed-tools: Read, Bash, Grep, Glob, Task
---

Run the complete sci-audit over the target text in `$ARGUMENTS` (a file path,
pasted text, or "the current diff").

Load the `sci-audit-orchestrator` skill and follow its workflow:

1. Read the target. Do NOT read participant data, PII, transcripts, or
   `.env`/credential files — the PreToolUse hook enforces this.
2. Detect language. Turkish (or `--lang tr`) makes axis G required; otherwise
   note G as not applicable.
3. Detect or accept (`--type`) the document type and pick the axis-E guideline.
4. Section long text and fan out to subagents so each section fits a clean
   context window.
5. Run the deterministic cores (no network, never fabricate):
   - axis B — `skills/claim-grounding/scripts/claim_grounding.py`
   - axis C — `skills/stats-forensics/scripts/stats_forensics.py`
   - axis D — `skills/hallucination-signals/scripts/hallucination_signals.py`
   - axis G (if Turkish) — `skills/turkish-sci-style/scripts/tr_sciaudit.py`
     with `--strictness` from `$ARGUMENTS` (default draft).
6. Escalate axes A and B to the `citation-verifier`, `claim-extractor`, and
   `claim-refuter` subagents + scholarly MCPs. Map axis E with `guideline-mapper`
   and axis G register with `style-judge`. Deterministic findings beat the judge
   on conflict.
7. Score each axis (100 − 15/blocker − 5/major − 1/minor, floored at 0), merge
   with `references/report-template.md`, and state the gate outcome for
   `certification` + `--fail-on error`.

Report in the user's language with EN+TR paired section titles. Every finding
must quote its evidence. State clearly what was NOT checked (unreachable MCP,
skipped provider, sampled sections) — absence is not proof of correctness.

After presenting the report, offer to append it to the audit log with
`/sci-audit:ai-log`.
