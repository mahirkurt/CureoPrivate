# `bundle-manifest` — SHA-256 File Inventory

> Status: v0.3.0-rc.1 and onward · Closes Düstur lesson L7

Generates a deterministic, supply-chain-attestable inventory of every
file in a library bundle, keyed by SHA-256 hash and categorized by
canonical path prefix. Input for v1.0.0 Sigstore/Cosign signing.

## When to use

- **Release tagging** — generate a manifest at every release; commit
  it alongside the bundle so consumers can verify integrity
- **Supply-chain audit** — verify a bundle hasn't been tampered with
  between source and deployment
- **Pre-publish gate** — refuse to publish if the on-disk bundle
  disagrees with the manifest (drift indicates uncommitted changes)
- **Forensic incident response** — given a corrupted bundle, surface
  exactly which files diverged from the known-good manifest

## Generate

```bash
python3 scripts/bundle_manifest.py \
    --library-dir /path/to/library \
    --output library/manifest.json
```

The output file is `manifest.json` containing:

```jsonc
{
  "$schema": ".../bundle-manifest.schema.json",
  "bundle_name": "dustur-figma-library",
  "bundle_version": "0.1.0",
  "source_design_system": {
    "name": "Düstur Tasarım Sistemi",
    "version": "0.1.0",
    "url": "https://dustur.example.com/"
  },
  "generated_at": "2026-05-27T03:00:00Z",
  "generator": {
    "tool": "figma-forge bundle-manifest",
    "version": "0.3.0-rc.1"
  },
  "file_count": 103,
  "total_size_bytes": 275438,
  "summary_by_category": {
    "tokens.primitive":     6,
    "tokens.semantic":      4,
    "tokens.merged":        3,
    "components.spec":     17,
    "patterns.spec":       17,
    "code-connect.mapping":17,
    "icons.tier-svg":      14,
    "icons.selcuklu-svg":   6,
    "icons.legal-svg":      6,
    "icons.spec":           7,
    "docs":                 1,
    "root":                 5
  },
  "files": [
    {
      "path": "tokens/dustur.tokens.json",
      "size": 24673,
      "sha256": "a1b2c3...",
      "category": "tokens.merged"
    },
    ...
  ]
}
```

## Categorization rules

First match wins (most specific prefix first):

| Path prefix                     | Category               |
|---------------------------------|------------------------|
| `tokens/primitives/`            | `tokens.primitive`     |
| `tokens/semantic/`              | `tokens.semantic`      |
| `tokens/`                       | `tokens.merged`        |
| `components/`                   | `components.spec`      |
| `patterns/`                     | `patterns.spec`        |
| `code-connect/`                 | `code-connect.mapping` |
| `icons/svg/tier/`               | `icons.tier-svg`       |
| `icons/svg/selcuklu-motif/`     | `icons.selcuklu-svg`   |
| `icons/svg/document/`           | `icons.legal-svg`      |
| `icons/svg/`                    | `icons.generic-svg`    |
| `icons/`                        | `icons.spec`           |
| `docs/`                         | `docs`                 |
| `remediations/`                 | `remediations`         |
| (everything else)               | `root`                 |

## Verify

```bash
python3 scripts/bundle_manifest.py \
    --library-dir /path/to/library \
    --verify
```

The verify mode re-computes the manifest fresh and diffs against the
on-disk version:

| Diff prefix  | Meaning                                            |
|--------------|----------------------------------------------------|
| `ADDED:`     | File on disk, not in manifest (uncommitted change) |
| `REMOVED:`   | File in manifest, not on disk (file deleted)       |
| `CHANGED:`   | File hash mismatches (content modified)            |

Exit code 0 on clean, 1 on any drift.

## Exclusion list

Skipped during manifest generation (build artifacts, VCS, OS metadata):

- Directory names: `__pycache__`, `.pytest_cache`, `.git`, `node_modules`, `.venv`, `.idea`
- File names: `.DS_Store`, `.gitignore`, `Thumbs.db`, `.coverage`
- Extensions: `.pyc`, `.pyo`, `.swp`, `.tmp`

If you need different exclusions for your design system, fork the
`should_skip` function and override the three frozensets at the top
of `bundle_manifest.py`.
