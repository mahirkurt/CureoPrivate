# Calibration Methodology — figma-forge v0.2.1

This reference documents the **calibration framework** introduced in v0.2.1 and the **methodology** for using it to tune heuristic gate thresholds against real-world Figma libraries.

## Why calibration matters

The 19-gate PUBLISH_AUDIT framework includes four gates with **graded, threshold-dependent decisions**:

| Gate | What it decides | Threshold-dependent parameters |
|------|-----------------|-------------------------------|
| **G7** | Is the variant matrix complete? | Soft-fail threshold (64 variants), hard-fail threshold (256 variants), axis delimiter conventions |
| **G13** | Is this effect style an elevation token, decorative effect, or ambiguous? | Elevation-name regex pattern, decorative-hint vocabulary |
| **G14** | Is this raw VECTOR/GROUP node an icon that should be a component? | Canonical sizes {16, 20, 24, 32, 48}, ±1 px size tolerance, ±2 px squareness tolerance, decorative-name vocabulary |
| **G15** | Does this icon component follow the size/grid convention? | Same canonical sizes and tolerances as G14 |

Synthetic fixture tests (`tests/test_publish_audit.py`, `tests/test_publish_audit_e2e.py`) verify these gates **work correctly** against expected-shape inputs. They cannot verify the **thresholds are well-tuned** against the real distribution of nodes in production Figma libraries.

Without calibration, the v0.2.0 gate stack ships with thresholds that are **author's-best-guess** values. They are sensible — derived from IBM Carbon, Material 3, and Roche Design System conventions — but unvalidated. A library with 47 different decorative vector patterns might trigger false positives on G14 at a 30% rate; a library that uses `e1`/`e2` instead of `elevation/1` for its elevation tokens will see every elevation style classified as ambiguous by G13.

The calibration framework is the **measurement layer** that closes this gap.

## Design principles

### 1. Opt-in, never automatic
The calibration probe runs **only** when the operator passes `--calibration-mode` to the CLI. Normal audit runs are unaffected. No data is ever transmitted off the operator's machine.

### 2. Local-only sidecar
The probe output is written to a JSON file (default: `calibration.json`) on the operator's filesystem. The file is never uploaded, never sent to Anthropic, never sent to the figma-forge maintainer unless the operator explicitly chooses to share it.

### 3. Anonymizable by design
The companion `tools/anonymize_calibration.py` script transforms identifiers (component names, node IDs, design-system names) into deterministic salted hashes. The same node hashes to the same anonymous handle on repeat runs (preserving longitudinal analysis), but cannot be reversed by anyone without the salt.

### 4. No personal data
The probe captures: geometric properties (bounding box dimensions, squareness), text metadata (effect style names, component descriptions for keyword extraction), and statistical aggregates (histograms, counts). It does NOT capture: image pixels, raster previews, operator emails (except as may appear inside cover-page text — which the anonymizer purges), or any access tokens.

### 5. Privacy governance
- Default `.gitignore` should exclude `calibration*.json` and `*.salt` files
- The skill maintainer must never publish a non-anonymized sidecar
- Roche internal calibration data MUST pass through anonymization before any sharing

## Probe data shape

A calibration sidecar JSON file has this top-level structure (schema_version: 1.0):

```json
{
  "schema_version": "1.0",
  "audit_run": "<ISO-8601 UTC timestamp>",
  "figma_forge_version": "0.2.1",
  "library": {
    "ds_name": "<DS name OR anon:hash>",
    "ds_version": "<version string>",
    "naming_convention": "carbon|material|bem|custom",
    "files": ["foundations", "components", "patterns", "icons"]
  },
  "totals": {
    "nodes_walked": <int>,
    "components_scanned": <int>,
    "styles_examined": <int>,
    "calibrators_run": <int>
  },
  "probes": {
    "<gate_id_as_string>": {
      "gate_id": <int>,
      "nodes_scanned": <int>,
      "candidates_filtered": <int>,
      "decisions_made": <int>,
      "boundary_decisions": [BoundaryDecision...],
      "feature_distribution": {"<feature>": {"<bucket>": <count>}},
      "skip_reasons": {"<reason>": <count>},
      "notes": ["<free-form annotations>"]
    }
  }
}
```

`BoundaryDecision`:

```json
{
  "node_id": "<Figma ID OR anon:hash>",
  "node_name": "<component name OR anon:hash>",
  "feature_name": "squareness_pixels",
  "feature_value": 2,
  "threshold": 2,
  "verdict": "candidate",
  "would_flip_at": 1,
  "gate_role": "icons"
}
```

The **boundary decision** is the most actionable signal. It says: "for this node, the gate's verdict is X, but if the threshold moved to Y the verdict would be Z." A library with many boundary decisions on the same threshold is one where that threshold is operating at its breaking point.

## Operator workflow

1. **Run the audit with calibration enabled.**
   ```bash
   python3 scripts/publish_audit.py \
       --library-registry library-registry.json \
       --figma-pat $FIGMA_PAT \
       --output publish-audit.md \
       --calibration-mode \
       --calibration-output calibration-2026-05.json
   ```

2. **Inspect the sidecar locally.** Look for unexpected boundary-decision counts or skip-reason imbalances. The `calibration_analyzer.py` tool below can be run on a single sidecar too.

3. **Anonymize before sharing.**
   ```bash
   python3 tools/anonymize_calibration.py calibration-2026-05.json
   ```
   This produces `calibration-2026-05.json.anon.json` and `calibration-2026-05.json.anon.salt`. Share the `.anon.json`; keep the `.salt` private.

4. **Optionally share with the maintainer** for incorporation into future threshold tuning.

## Maintainer workflow

1. **Aggregate sidecars from multiple operators.**
   ```bash
   python3 tools/calibration_analyzer.py \
       --inputs calibration-roche.anon.json calibration-hemantix.anon.json \
       --gate 14 \
       --output references/calibration-data-g14.md
   ```

2. **Inspect the produced Markdown report.** Look for:
   * **Boundary density** — if >20% of decisions are boundary cases, the threshold is poorly tuned
   * **Skip-reason imbalance** — disproportionately frequent skip reasons indicate gate-scope issues
   * **Feature distribution shape** — bimodal distributions suggest the heuristic is conflating two distinct populations

3. **Propose threshold adjustments** with quantitative justification (e.g. "raise `ICON_SQUARENESS_TOLERANCE_PX` from 2 to 3 — would eliminate 4/6 boundary cases observed in Roche RDS without introducing new false negatives in Hemantix").

4. **Update fixtures and tests** to defend the new threshold value (every threshold change must come with at least one test that would fail at the old value).

5. **Document the change** in an ADR-style entry in this file.

## v0.2.1 release status — synthetic-corpus demonstration only

The v0.2.1 release ships the calibration **framework** (probes, analyzer, anonymizer, tests) but does **not** ship any real-world threshold adjustments. The current thresholds (canonical sizes, ±1 / ±2 tolerances, elevation regex, soft/hard variant limits) carry over from v0.2.0 unchanged.

This is by intent. Real-world calibration requires access to production design-system libraries (e.g. Roche RDS internal, IBM Carbon's public Figma file, Material 3's public file) and the calibration runs performed against them. That work is scoped for **v0.2.2** as a follow-up patch release with the explicit deliverable: "at least one threshold adjusted based on calibration evidence, with ADR documenting the before/after distribution shift."

The v0.2.1 framework provides:
- ✅ Calibration probes for all 4 heuristic gates (G7, G13, G14, G15)
- ✅ `--calibration-mode` CLI flag with `--calibration-output` sidecar path
- ✅ Sidecar JSON schema v1.0 with stable field semantics
- ✅ Offline analyzer (`tools/calibration_analyzer.py`)
- ✅ Privacy-conscious anonymizer (`tools/anonymize_calibration.py`)
- ✅ 8 integration tests (`tests/test_calibration.py`)
- ✅ This methodology documentation

The v0.2.1 framework does NOT yet ship:
- ❌ Real-world calibration runs against production Figma libraries (deferred to v0.2.2)
- ❌ Calibration-driven threshold adjustments (deferred to v0.2.2)
- ❌ Bundled reference sidecars from any specific library (intentional — operators run their own)

## Future calibration sprints

| Sprint | Focus | Expected outcome |
|--------|-------|-----------------|
| **v0.2.2** | First real-world calibration run | At least one threshold adjusted with documented evidence |
| **v0.3.0** | Auto-tuning mode | `--auto-tune` flag proposes threshold changes inline |
| **v0.3.1** | Cross-library benchmarking | Reference sidecars from IBM Carbon + Material 3 + Tailwind as baseline |
| **v1.0.0** | Calibration data v2 schema | Stable schema commitment for third-party consumers |
