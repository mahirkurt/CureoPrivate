#!/usr/bin/env python3
"""
calibration_analyzer.py — offline analysis of calibration sidecars.

Consumes one or more ``calibration-*.json`` sidecars (produced by
``scripts/publish_audit.py --calibration-mode``) and emits a Markdown
report summarizing per-gate threshold tuning recommendations.

Designed for the skill maintainer (not the operator). The operator runs
the audit, generates the sidecar locally, optionally anonymizes it via
``tools/anonymize_calibration.py``, and shares it with the maintainer.
The maintainer aggregates one or more sidecars here.

Usage:
    python3 tools/calibration_analyzer.py \\
        --inputs calibration-roche.json calibration-hemantix.json \\
        --gate 14 \\
        --output references/calibration-data-g14.md

    # Multi-gate run:
    python3 tools/calibration_analyzer.py \\
        --inputs calibration-*.json \\
        --output calibration-summary.md

Output sections per gate:
  * Summary statistics (n libraries, totals)
  * Skip reason aggregation
  * Feature distribution histograms (merged across libraries)
  * Boundary decision audit — which thresholds are firing on edge cases
  * Recommended threshold adjustments (rule-based, conservative)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------

def load_sidecar(path: Path) -> dict:
    """Load a calibration sidecar JSON from ``path`` with validation."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    schema = data.get("schema_version")
    if schema != "1.0":
        raise ValueError(
            f"{path}: unsupported schema_version={schema!r}; expected '1.0'"
        )
    if "probes" not in data:
        raise ValueError(f"{path}: missing 'probes' field")
    return data


def load_all(paths: list[Path]) -> list[dict]:
    """Load every sidecar; skip + warn on individual failures."""
    sidecars: list[dict] = []
    for path in paths:
        try:
            sidecars.append(load_sidecar(path))
        except (ValueError, json.JSONDecodeError, OSError) as e:
            print(f"WARNING: skipping {path}: {e}", file=sys.stderr)
    return sidecars


# ----------------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------------

def aggregate_skip_reasons(probes: list[dict]) -> dict[str, int]:
    """Sum skip_reason counts across probes."""
    total: dict[str, int] = defaultdict(int)
    for probe in probes:
        for reason, count in (probe.get("skip_reasons") or {}).items():
            total[reason] += count
    return dict(total)


def aggregate_feature_distribution(probes: list[dict]) -> dict[str, dict[str, int]]:
    """Sum feature_distribution counts across probes, feature-by-bucket."""
    total: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for probe in probes:
        for feature, buckets in (probe.get("feature_distribution") or {}).items():
            for bucket, count in buckets.items():
                total[feature][bucket] += count
    return {f: dict(b) for f, b in total.items()}


def aggregate_boundary_decisions(probes: list[dict]) -> list[dict]:
    """Concatenate boundary_decisions from every probe."""
    out: list[dict] = []
    for probe in probes:
        out.extend(probe.get("boundary_decisions") or [])
    return out


def aggregate_totals(probes: list[dict]) -> dict[str, int]:
    """Sum nodes_scanned + candidates + decisions across probes."""
    return {
        "nodes_scanned":      sum(p.get("nodes_scanned", 0) for p in probes),
        "candidates_filtered": sum(p.get("candidates_filtered", 0) for p in probes),
        "decisions_made":     sum(p.get("decisions_made", 0) for p in probes),
        "boundary_count":     sum(len(p.get("boundary_decisions") or []) for p in probes),
    }


# ----------------------------------------------------------------------------
# Reporting helpers
# ----------------------------------------------------------------------------

def _format_histogram(buckets: dict[str, int], *, max_rows: int = 20) -> list[str]:
    """Render a histogram dict as a Markdown table sorted by bucket label."""
    if not buckets:
        return ["_(empty)_"]
    total = sum(buckets.values()) or 1
    items = sorted(buckets.items(), key=lambda kv: kv[0])[:max_rows]
    lines = ["| Bucket | Count | % of total |", "|---|---:|---:|"]
    for bucket, count in items:
        pct = count / total * 100
        lines.append(f"| `{bucket}` | {count} | {pct:.1f}% |")
    if len(buckets) > max_rows:
        lines.append(f"| _… and {len(buckets) - max_rows} more rows_ | | |")
    return lines


def _format_boundary_table(decisions: list[dict], *, max_rows: int = 25) -> list[str]:
    """Render boundary decisions as a Markdown table grouped by feature."""
    if not decisions:
        return ["_No boundary decisions recorded._"]
    by_feature: dict[str, list[dict]] = defaultdict(list)
    for d in decisions:
        by_feature[d.get("feature_name", "<unknown>")].append(d)
    lines: list[str] = []
    for feature in sorted(by_feature.keys()):
        feature_decisions = by_feature[feature]
        lines.append(f"#### `{feature}` — {len(feature_decisions)} boundary case(s)")
        lines.append("")
        lines.append("| Node | Value | Threshold | Verdict | Would-flip-at |")
        lines.append("|---|---:|---:|---|---:|")
        for d in feature_decisions[:max_rows]:
            lines.append(
                f"| `{d.get('node_name', d.get('node_id', '?'))}` "
                f"| {d.get('feature_value', '?')} "
                f"| {d.get('threshold', '?')} "
                f"| {d.get('verdict', '?')} "
                f"| {d.get('would_flip_at', '?')} |"
            )
        if len(feature_decisions) > max_rows:
            lines.append(
                f"_… and {len(feature_decisions) - max_rows} more decisions._"
            )
        lines.append("")
    return lines


def _derive_recommendations(gate_id: int, totals: dict, skip_reasons: dict,
                             feature_dist: dict, boundary_decisions: list) -> list[str]:
    """Produce conservative threshold recommendations from aggregated data."""
    recs: list[str] = []
    if totals["candidates_filtered"] == 0:
        recs.append(
            "**No candidates evaluated.** Skipping recommendations: the gate's "
            "preconditions were not met in any of the supplied libraries. "
            "Consider expanding the calibration corpus or verifying the gate's "
            "scope assumptions."
        )
        return recs
    # Boundary density: high → threshold poorly tuned
    boundary_density = totals["boundary_count"] / max(totals["decisions_made"], 1)
    if boundary_density > 0.20:
        recs.append(
            f"**High boundary density ({boundary_density*100:.1f}%):** more "
            f"than 1 in 5 decisions sit within the boundary band. The current "
            f"threshold is likely poorly tuned for these libraries; review the "
            f"boundary-decision table below and consider adjusting."
        )
    elif boundary_density > 0.10:
        recs.append(
            f"**Moderate boundary density ({boundary_density*100:.1f}%):** "
            f"some borderline decisions present; review for systemic patterns."
        )
    else:
        recs.append(
            f"**Low boundary density ({boundary_density*100:.1f}%):** "
            f"threshold appears well-tuned for the supplied libraries."
        )
    # Gate-specific heuristics
    if gate_id == 14:
        # Look for skip-reason imbalance — too many "not_canonical_size" hints
        # at large library scale → tolerance may be too narrow
        nc = skip_reasons.get("not_canonical_size", 0)
        ns = skip_reasons.get("not_square", 0)
        if nc > 50:
            recs.append(
                f"**G14: {nc} `not_canonical_size` skips.** Many vector "
                f"nodes were ignored because their dimensions fell outside "
                f"the ±1 px tolerance of canonical sizes. If these are "
                f"legitimate icons, consider increasing ICON_SIZE_TOLERANCE_PX "
                f"to 2 — but only after manually verifying a sample."
            )
        if ns > 30:
            recs.append(
                f"**G14: {ns} `not_square` skips.** Square test removed "
                f"{ns} candidates. Investigate whether these are non-square "
                f"icons (legitimate edge case) or rounding artifacts (raise "
                f"ICON_SQUARENESS_TOLERANCE_PX from 2 to 3)."
            )
    elif gate_id == 7:
        # Variant matrix specifically: high parse_error rate → axis-delimiter
        # convention mismatch
        pe_buckets = feature_dist.get("parse_error_count") or {}
        if any(int(k) > 0 for k in pe_buckets.keys()):
            recs.append(
                "**G7: parse errors detected.** Some component sets failed "
                "variant-name parsing. Check whether the library uses a "
                "non-default axis delimiter (e.g. `|` instead of `,`)."
            )
    elif gate_id == 13:
        # Near-miss boundaries → elevation regex too strict
        near_misses = [d for d in boundary_decisions
                       if d.get("feature_name") == "elevation_regex_distance"]
        if len(near_misses) >= 3:
            recs.append(
                f"**G13: {len(near_misses)} elevation-token near-misses.** "
                f"Names containing 'elevation' or 'elev' that fail the strict "
                f"regex. Consider relaxing ELEVATION_NAME_RE or adopting "
                f"name normalization upstream."
            )
    return recs


# ----------------------------------------------------------------------------
# Per-gate section
# ----------------------------------------------------------------------------

def render_gate_section(gate_id: int, sidecars: list[dict]) -> list[str]:
    """Render the full per-gate analysis section as Markdown lines."""
    probes = [s["probes"].get(str(gate_id)) for s in sidecars]
    probes = [p for p in probes if p is not None]
    if not probes:
        return [
            f"## Gate {gate_id}",
            "",
            f"_No probe data found for G{gate_id} in any supplied sidecar._",
            "",
        ]
    totals = aggregate_totals(probes)
    skip_reasons = aggregate_skip_reasons(probes)
    feature_dist = aggregate_feature_distribution(probes)
    boundary_decisions = aggregate_boundary_decisions(probes)

    lines: list[str] = [
        f"## Gate {gate_id}",
        "",
        f"**Libraries with probe data:** {len(probes)}  ",
        f"**Total nodes scanned:** {totals['nodes_scanned']}  ",
        f"**Candidates filtered:** {totals['candidates_filtered']}  ",
        f"**Decisions made:** {totals['decisions_made']}  ",
        f"**Boundary decisions:** {totals['boundary_count']}",
        "",
        "### Skip-reason breakdown",
        "",
    ]
    lines.extend(_format_histogram(skip_reasons))
    lines.append("")
    lines.append("### Feature distributions")
    lines.append("")
    if not feature_dist:
        lines.append("_No feature distributions recorded._")
    for feature in sorted(feature_dist.keys()):
        lines.append(f"#### `{feature}`")
        lines.append("")
        lines.extend(_format_histogram(feature_dist[feature]))
        lines.append("")
    lines.append("### Boundary decisions")
    lines.append("")
    lines.extend(_format_boundary_table(boundary_decisions))
    lines.append("")
    lines.append("### Recommendations")
    lines.append("")
    for rec in _derive_recommendations(gate_id, totals, skip_reasons,
                                         feature_dist, boundary_decisions):
        lines.append(f"- {rec}")
    lines.append("")
    return lines


# ----------------------------------------------------------------------------
# Report assembly
# ----------------------------------------------------------------------------

def render_report(sidecars: list[dict], gate_filter: int | None) -> str:
    """Assemble the full Markdown calibration analysis."""
    if not sidecars:
        return "# Calibration Analysis\n\n_No sidecars provided._\n"
    header = ["# figma-forge — Calibration Analysis", ""]
    header.append(f"**Sidecars analyzed:** {len(sidecars)}  ")
    libraries = sorted({
        f"{s.get('library', {}).get('ds_name', '?')} "
        f"v{s.get('library', {}).get('ds_version', '?')}"
        for s in sidecars
    })
    header.append(f"**Libraries:** {', '.join(libraries)}  ")
    versions = sorted({s.get("figma_forge_version", "?") for s in sidecars})
    header.append(f"**figma-forge versions:** {', '.join(versions)}")
    header.append("")
    gate_ids_present: set[int] = set()
    for s in sidecars:
        for gid_str in (s.get("probes") or {}).keys():
            try:
                gate_ids_present.add(int(gid_str))
            except (TypeError, ValueError):
                continue
    if gate_filter is not None:
        gate_ids = [gate_filter]
    else:
        gate_ids = sorted(gate_ids_present)
    body: list[str] = []
    for gid in gate_ids:
        body.extend(render_gate_section(gid, sidecars))
    return "\n".join(header + body) + "\n"


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main() -> int:
    """Parse CLI arguments and write the analysis report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", required=True,
                        help="Calibration sidecar JSON paths (one or more)")
    parser.add_argument("--gate", type=int, default=None,
                        help="Limit analysis to a single gate ID (default: all)")
    parser.add_argument("--output", default=None,
                        help="Path for Markdown output (default: stdout)")
    args = parser.parse_args()

    paths = [Path(p) for p in args.inputs]
    sidecars = load_all(paths)
    report = render_report(sidecars, args.gate)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Wrote calibration analysis → {args.output}", file=sys.stderr)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
