#!/usr/bin/env python3
"""audit_diff.py — CLI for figma-forge audit-diff (v0.3.1-alpha).

Compute a calibration delta between two schema-v1.0 audit reports.
Suitable for CI gates that fail on regression even when overall score
nominally passes.

Usage::

    python3 scripts/audit_diff.py \\
        --baseline audit-2026-05-26.json \\
        --current  audit-2026-05-27.json \\
        --output diff.md \\
        --output-format markdown

Exit codes::

    0  No regressions detected (improvements OK)
    1  At least one regression detected
    2  Cannot run (invalid JSON, schema mismatch, file not found)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make package importable regardless of CWD
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from audit_diff import (  # noqa: E402
    compare,
    format_diff_json,
    format_diff_markdown,
    load_snapshot,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audit_diff.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--baseline", type=Path, required=True,
                   help="Baseline schema-v1.0 audit JSON.")
    p.add_argument("--current", type=Path, required=True,
                   help="Current schema-v1.0 audit JSON.")
    p.add_argument("--output", type=Path, default=None,
                   help="Output path (default: stdout).")
    p.add_argument("--output-format", choices=("markdown", "json"),
                   default="markdown",
                   help="Output format (default: markdown).")
    p.add_argument("--fail-on", choices=("regression", "any-change", "never"),
                   default="regression",
                   help="When to exit non-zero. "
                        "'regression' (default) = any regression. "
                        "'any-change' = even improvements trigger exit 1. "
                        "'never' = always exit 0.")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print summary to stderr.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.baseline.exists():
        print(f"❌ Baseline not found: {args.baseline}", file=sys.stderr)
        return 2
    if not args.current.exists():
        print(f"❌ Current not found: {args.current}", file=sys.stderr)
        return 2

    try:
        baseline = load_snapshot(args.baseline)
        current = load_snapshot(args.current)
    except (ValueError, OSError) as e:
        print(f"❌ Cannot load snapshot: {e}", file=sys.stderr)
        return 2

    report = compare(baseline, current)

    if args.output_format == "json":
        rendered = format_diff_json(report)
    else:
        rendered = format_diff_markdown(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        if args.verbose:
            print(f"✓ Diff written → {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)

    summary = report.summary
    if args.verbose:
        print(
            f"  Score:        {baseline.score:.1f} → {current.score:.1f}  "
            f"(Δ {report.score_delta:+.2f})",
            file=sys.stderr,
        )
        print(
            f"  Band:         {baseline.band} → {current.band}  "
            f"({report.band_shift})",
            file=sys.stderr,
        )
        print(
            f"  Gates:        {summary['regressions']} regressions · "
            f"{summary['improvements']} improvements · "
            f"{summary['no_change']} unchanged · "
            f"{summary['new_gates']} new · "
            f"{summary['removed_gates']} removed",
            file=sys.stderr,
        )

    if args.fail_on == "never":
        return 0
    if args.fail_on == "regression":
        return 1 if summary["regressions"] > 0 else 0
    if args.fail_on == "any-change":
        any_change = (
            summary["regressions"]
            + summary["improvements"]
            + summary["new_gates"]
            + summary["removed_gates"]
        )
        return 1 if any_change > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
