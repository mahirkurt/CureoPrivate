# `orchestrate` — Multi-Stage Pipeline Driver

> Status: v0.3.0-rc.1 and onward · Closes Düstur lesson L8

`orchestrate` sequences SCAFFOLD → TOKENS_IMPORT → FOUNDATIONS_BUILD →
COMPONENTS_BUILD → ICONS_BUILD → PATTERNS_BUILD → CODE_CONNECT →
PUBLISH_AUDIT → PUBLISH (or any subset) from a single
`orchestration.json` manifest. Replaces ad-hoc shell scripts.

## When to use

- **Reproducible builds** — one command rebuilds the entire library
  from source-of-truth bundle
- **CI pipelines** — `orchestrate --dry-run` validates the manifest
  without I/O; full run executes
- **Operator handoff** — design-system maintainer rebuilds the Figma
  library after merging a token PR

## Manifest schema

```json
{
  "library": "Düstur Tasarım Sistemi",
  "version": "0.1.0",
  "pipeline": [
    {
      "stage": 1, "mode": "SCAFFOLD",
      "description": "Create empty Figma files per library-registry.json",
      "command": "figma-forge scaffold --registry library-registry.json",
      "outputs": ["foundations.figma", "components.figma", ...],
      "estimated_time": "1-2 min",
      "pass_criteria": "All 4 file URIs returned"
    },
    ...
  ]
}
```

## Stage classes

| Stage              | Class               | v0.3.0 status                                |
|--------------------|---------------------|----------------------------------------------|
| `SCAFFOLD`         | Live (transport)    | Defer to v0.4.0; announces intent            |
| `TOKENS_IMPORT`    | **Real executor**   | Shells out to `dtcg_to_variables.py`         |
| `FOUNDATIONS_BUILD`| Live (transport)    | Defer to v0.4.0                              |
| `COMPONENTS_BUILD` | Live (transport)    | Defer to v0.4.0                              |
| `ICONS_BUILD`      | Live (transport)    | Defer to v0.4.0                              |
| `PATTERNS_BUILD`   | Live (transport)    | Defer to v0.4.0                              |
| `CODE_CONNECT`     | Live (transport)    | Defer to v0.4.0                              |
| `PUBLISH_AUDIT`    | **Real executor**   | Shells out to `publish_audit.py`             |
| `AUTO_REMEDIATE`   | **Real executor**   | Shells out to `auto_remediate.py`            |
| `PUBLISH`          | Live (transport)    | Defer to v0.4.0                              |

"Live" stages defer to the v0.4.0 transport layer (Anthropic MCP /
Cursor MCP / Codebase MCP / REST). Today they emit a structured "would
have executed: …" log entry and succeed. Real executor stages run
today.

## Execution modes

```bash
# Default: fail-fast pipeline run
python3 scripts/orchestrate.py \
    --manifest orchestration.json \
    --library-dir . \
    --verbose

# Dry-run: plan only, zero I/O
python3 scripts/orchestrate.py --manifest ... --library-dir ... --dry-run

# Resume after a fix (skip stages strictly before the target)
python3 scripts/orchestrate.py --manifest ... --library-dir ... \
    --resume PUBLISH_AUDIT

# Only specific stages
python3 scripts/orchestrate.py --manifest ... --library-dir ... \
    --only "TOKENS_IMPORT,PUBLISH_AUDIT"

# Continue after a failure (useful for batch operations)
python3 scripts/orchestrate.py --manifest ... --library-dir ... \
    --continue-on-failure
```

## Output

- **Console summary** — per-stage status (✓ success / ✗ failed / ↷
  skipped / · dry-run), duration, errors
- **`orchestrate-summary.json`** — machine-readable artifact log
  written alongside the library bundle

## Exit codes

| Code | Meaning                                                |
|------|--------------------------------------------------------|
| 0    | All stages succeeded (or skipped intentionally)        |
| 1    | At least one stage failed                              |
| 2    | Cannot run (invalid manifest, missing library, etc.)   |

## Validation-only mode

```bash
# Sanity-check a manifest without executing anything
python3 scripts/orchestrate.py --manifest ... --library-dir ... --validate-only
```

Reports:
- Each stage's index, mode, description
- Duplicate index errors (manifest rejects two stages with same `stage` int)
- Unknown mode errors (catch typos like `TOKENS_INPORT`)
