---
description: Append an audit-run entry to the sci-audit JSONL log
argument-hint: <one-line summary of what was audited and the outcome>
allowed-tools: Read, Bash
---

Append one JSON line recording this audit run to
`.claude/sci-audit-log.jsonl` at the project root (create the file if absent).

Build the entry from what happened in this session — do NOT invent fields:

```json
{
  "ts": "<ISO-8601 timestamp>",
  "target": "<file or description of the audited text>",
  "lang": "<tr|en>",
  "type": "<document type or 'unspecified'>",
  "strictness": "<draft|certification>",
  "axes_run": ["A","B","C","D","E","F","G"],
  "scores": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0},
  "blockers": 0, "majors": 0, "minors": 0,
  "gate": "<closes|does not close|n/a>",
  "not_checked": ["<unreachable MCP / skipped provider / sampled sections>"],
  "summary": "$ARGUMENTS"
}
```

Append it with a single `>>` redirect (one line, newline-terminated). Never
write PII, participant data, secrets, or raw source text into the log — only the
derived summary and scores. Confirm the append and echo the entry back.
