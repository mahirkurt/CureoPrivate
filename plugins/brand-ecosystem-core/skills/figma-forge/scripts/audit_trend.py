#!/usr/bin/env python3
"""audit_trend.py — CLI for figma-forge audit-trend (v0.3.1-rc).

Compute a longitudinal calibration drift report over N schema-v1.0
audit JSON files.

Usage::

    # Glob mode: all audits matching a pattern
    python3 scripts/audit_trend.py --glob 'audits/*.json' \\
        --output trend.html --output-format html

    # Explicit list mode
    python3 scripts/audit_trend.py \\
        --inputs audits/2026-05-01.json audits/2026-05-02.json ... \\
        --output trend.md --output-format markdown

    # Window filtering
    python3 scripts/audit_trend.py --glob 'audits/*.json' \\
        --since 2026-04-27 --until 2026-05-27 \\
        --output trend.json --output-format json

Exit codes::

    0   No drift concerns (CDI ≤ moderate threshold)
    1   High drift detected (CDI > 0.10) when --fail-on-high-drift set
    2   Cannot run (no inputs, invalid JSON, schema mismatch)
"""

from __future__ import annotations

import argparse
import glob as _glob
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure the package is importable regardless of CWD
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from audit_trend import (  # noqa: E402
    analyze,
    format_trend_html,
    format_trend_json,
    format_trend_markdown,
    load_points,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audit_trend.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--glob", dest="glob_pattern",
                     help="Glob pattern for audit JSON files (e.g. 'audits/*.json').")
    src.add_argument("--inputs", nargs="+", type=Path,
                     help="Explicit list of audit JSON paths.")
    p.add_argument("--output", type=Path, default=None,
                   help="Output path (default: stdout for markdown/json; "
                        "trend-dashboard.html for html).")
    p.add_argument("--output-format", choices=("markdown", "json", "html"),
                   default="markdown",
                   help="Output format (default: markdown).")
    p.add_argument("--since", type=str, default=None,
                   help="Filter: include only audits at or after this ISO date (UTC).")
    p.add_argument("--until", type=str, default=None,
                   help="Filter: include only audits at or before this ISO date (UTC).")
    p.add_argument("--fail-on-high-drift", action="store_true",
                   help="Exit 1 when calibration drift index exceeds 0.10.")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print summary to stderr.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    # Resolve input paths
    if args.glob_pattern:
        paths = sorted(Path(p) for p in _glob.glob(args.glob_pattern))
    else:
        paths = list(args.inputs or [])
    if not paths:
        print("❌ No input audit reports resolved.", file=sys.stderr)
        return 2

    # Load
    try:
        points = load_points(paths)
    except ValueError as e:
        print(f"❌ Cannot load audits: {e}", file=sys.stderr)
        return 2
    if not points:
        print("❌ No valid audit reports could be parsed from the inputs.",
              file=sys.stderr)
        return 2

    # Window filter
    since = _parse_date(args.since)
    until = _parse_date(args.until)
    if since or until:
        points = [pt for pt in points
                  if _in_window(pt.timestamp, since, until)]
        if not points:
            print("❌ No audits remain after applying --since/--until window.",
                  file=sys.stderr)
            return 2

    report = analyze(points)

    # Render
    if args.output_format == "json":
        rendered = format_trend_json(report)
    elif args.output_format == "html":
        rendered = format_trend_html(report)
    else:
        rendered = format_trend_markdown(report)

    # Default output path for html (binary-ish — don't blast to stdout)
    output_path = args.output
    if output_path is None and args.output_format == "html":
        output_path = Path("trend-dashboard.html")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        if args.verbose:
            print(f"✓ Trend report written → {output_path}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)

    if args.verbose:
        print(
            f"  Audits:       {report.audit_count}",
            file=sys.stderr,
        )
        print(
            f"  Window:       {report.window_start} → {report.window_end} "
            f"({report.window_days:.1f} d)",
            file=sys.stderr,
        )
        print(
            f"  Score:        μ={report.score_mean:.2f}  "
            f"σ={report.score_stdev:.2f}  "
            f"range=[{report.score_min:.1f}, {report.score_max:.1f}]",
            file=sys.stderr,
        )
        print(
            f"  Drift (σ/μ):  {report.calibration_drift_index:.4f}",
            file=sys.stderr,
        )
        print(
            f"  Slope:        {report.score_slope_per_audit:+.4f} /audit · "
            f"{report.score_slope_per_day:+.4f} /day",
            file=sys.stderr,
        )

    if args.fail_on_high_drift and report.calibration_drift_index > 0.10:
        return 1
    return 0


def _parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    cleaned = s.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    # Accept date-only or full datetime
    if "T" not in cleaned and len(cleaned) == 10:
        cleaned += "T00:00:00+00:00"
    try:
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _in_window(ts: str, since: datetime | None, until: datetime | None) -> bool:
    cleaned = ts.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return True  # Don't filter out malformed timestamps; surface them in output
    if since and dt < since:
        return False
    if until and dt > until:
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
