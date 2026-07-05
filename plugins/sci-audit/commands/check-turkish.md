---
description: Axis G solo — Turkish scientific writing & orthography audit
argument-hint: <file-or-paste> [--strictness draft|certification] [--enable-tdk] [--enable-zemberek] [--enable-gecturk --gecturk-url URL] [--abbreviations FILE] [--terms a,b,c]
allowed-tools: Read, Bash, Task
---

Run axis G (Turkish scientific writing) over the text in `$ARGUMENTS`.

Load the `turkish-sci-style` skill and run the deterministic core, passing
through any provider flags from `$ARGUMENTS` (the `tr_sciaudit` CLI contract is
preserved verbatim):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/turkish-sci-style/scripts/tr_sciaudit.py" <file> \
  --strictness <draft|certification> --format md --fail-on error \
  [--enable-tdk --terms "..."] [--enable-zemberek] \
  [--enable-gecturk --gecturk-url http://127.0.0.1:8765/check] \
  [--abbreviations project-abbr.txt]
```

Rules:
- The deterministic G1–G6 core runs everywhere with no network. Report its
  findings mapped to severities: `error → blocker`, `warning → major`,
  `info → minor`.
- Providers degrade safely: a TDK HTTP error is provider status `error` (the
  core audit still stands); GECTurk with no URL and Zemberek with no package
  are `unavailable` and never block. Show the provider status table.
- The English decimal-dot p-value in Turkish text is a **blocker** (G5).
- For register/fluency/terminology nuance, optionally invoke the `style-judge`
  subagent — but if it disagrees with the deterministic core, the deterministic
  finding wins.

If the text is not Turkish, say so and stop; axis G does not apply.
