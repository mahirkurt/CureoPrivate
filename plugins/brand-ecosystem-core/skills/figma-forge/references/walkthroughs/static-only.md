# `publish_audit --static-only` — Offline Bundle Lint

> Status: v0.3.0-rc.1 and onward · Closes Düstur lesson L4

The `--static-only` flag bypasses live Figma context and runs **nine
static lint dimensions** against the source-of-truth bundle. Suitable
for CI runs without secrets and offline pre-publish gates.

## When to use

- **CI without Figma PAT** — public open-source DS without
  organizational tokens
- **Pre-publish gate** — last sanity check before promoting a bundle
  to publishable state
- **Style-guide enforcement** — catch DTCG alias typos, malformed
  SVGs, missing Code Connect mappings before they reach reviewers
- **Bundle handoff QA** — receiving a bundle from a contractor;
  validate before merging

## Run

```bash
python3 scripts/publish_audit.py \
    --library-registry library-registry.json \
    --static-only \
    --output-format json \
    --output audit.json
```

No PAT, no fetch, no live network calls.

## The nine dimensions

| #  | Gate id | Name                                         | What it checks                                    |
|----|---------|----------------------------------------------|---------------------------------------------------|
| L1 | G100    | JSON validity                                | Every `*.json` parses cleanly                     |
| L2 | G101    | Primitive token count                        | Color families × declared step count              |
| L3 | G102    | DTCG alias resolvability                     | Every `{alias}` literal resolves                  |
| L4 | G103    | Component spec schema                        | Required fields + `variants.expected_count` set   |
| L5 | G104    | Pattern → component referential integrity    | Every `uses_components` target exists             |
| L6 | G105    | SVG validity                                 | Envelope present + `viewBox` declared             |
| L7 | G106    | Code Connect completeness                    | One mapping per component spec                    |
| L8 | G107    | Manifest completeness                        | `manifest.json` agrees with on-disk file set      |
| L9 | G108    | Accessibility coverage declaration           | `library-registry.accessibility` block complete   |

## Synthetic gate IDs

Static lint uses gate IDs `100–108`, which coexist with live gate IDs
`1–19` in the schema-v1.0 audit report. Downstream tooling
(`auto-remediate`, `audit-diff`, `audit-trend`) handles both ranges
uniformly without special-casing.

## Merged DTCG discovery

The lint resolves the merged DTCG file in this order:

1. `library-registry.json:merged_dtcg` (explicit override)
2. `library-registry.json:ds_name` slugified + `.tokens.json`
   (e.g. `Düstur Tasarım Sistemi` → `tokens/dusturtasarimsistemi.tokens.json`)
3. First `*.tokens.json` under `tokens/`

If none of these resolve, L2 and L3 record a `notes` line and skip;
they do not fail.

## Empirical validation

| Bundle              | Score | Band       | Notes                              |
|---------------------|-------|------------|------------------------------------|
| **Düstur**          | 10.0  | EXEMPLARY  | 7 family × 12 step                 |
| **Material 3 Stub** | 10.0  | EXEMPLARY  | 2 family × 12 step (M3 baseline)   |
| **Carbon Stub**     | 10.0  | EXEMPLARY  | 2 family × 10 step (declared in registry) |

Static lint is **DS-agnostic** when `library-registry.color_families`
declares the per-family expected step counts. Default fallback is 12
(Düstur's LCH ramp size).

## Exit codes

Same as the live audit:

- 0 — no errors
- 1 — at least one error-severity gate failed (use `--strict` to also
  fail on warns)
- 2 — cannot run (missing inputs, schema mismatch)
