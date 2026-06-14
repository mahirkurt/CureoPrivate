#!/usr/bin/env python3
"""auto_remediate.py — CLI for figma-forge auto-remediation mode (v0.3.0).

Consume a publish_audit report and produce remediation artifacts for each
gate failure. Two output channels are supported:

* ``pr``     — Git-style unified diffs / patches to apply to static-source files
* ``plugin`` — Figma plugin TypeScript scripts to run in Dev Console

Usage::

    python3 scripts/auto_remediate.py \\
        --audit-report audit-report.json \\
        --library-dir ./dustur-figma-library \\
        --output-channel pr \\
        --output-dir ./remediations/

Exit codes::

    0  Remediation succeeded; at least one strategy produced actions
    1  No actionable failures found in the audit report (no-op)
    2  Cannot run (invalid args, missing audit report, etc.)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the package is importable regardless of CWD
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from auto_remediate import all_strategies  # noqa: E402
from auto_remediate.runner import RunnerOptions, run  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="auto_remediate.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--audit-report",
        type=Path,
        help="Path to a publish_audit Markdown or JSON report. Required unless --list-strategies.",
    )
    p.add_argument(
        "--library-dir",
        type=Path,
        help="Root of the design-system library bundle. Required unless --list-strategies.",
    )
    p.add_argument(
        "--output-channel",
        choices=("pr", "plugin"),
        default="pr",
        help="Remediation output channel (default: pr).",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./remediations"),
        help="Directory to write rendered remediations (default: ./remediations/).",
    )
    p.add_argument(
        "--strategies",
        type=str,
        default=None,
        help="Comma-separated list of gate ids to run (e.g. '13,14,17'). Default: all matching.",
    )
    p.add_argument(
        "--calibration-dir",
        type=Path,
        default=None,
        help="Optional calibration sidecar dir (for confidence tuning).",
    )
    p.add_argument(
        "--locale",
        default="en-US",
        help="Output locale (en-US | tr-TR). Default: en-US.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan only; do not write any files.",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="(pr channel only) Attempt to apply patches via `git apply`. Default: false.",
    )
    p.add_argument(
        "--list-strategies",
        action="store_true",
        help="List all registered strategies and exit.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress to stderr.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_strategies:
        regs = all_strategies()
        print(f"Registered strategies ({len(regs)}):", file=sys.stderr)
        for gid in sorted(regs):
            cls = regs[gid]
            channels = ", ".join(cls.output_channels)
            print(f"  G{gid:02d}  {cls.title:40s}  channels: {channels}")
        return 0

    # Required args check after --list-strategies bypass
    if args.audit_report is None or args.library_dir is None:
        print("❌ --audit-report and --library-dir are required (unless --list-strategies).", file=sys.stderr)
        return 2

    if not args.audit_report.exists():
        print(f"❌ Audit report not found: {args.audit_report}", file=sys.stderr)
        return 2

    if not args.library_dir.exists() or not args.library_dir.is_dir():
        print(f"❌ Library directory not found: {args.library_dir}", file=sys.stderr)
        return 2

    strategies_filter = None
    if args.strategies:
        try:
            strategies_filter = [int(s) for s in args.strategies.split(",")]
        except ValueError:
            print(f"❌ Invalid --strategies list: {args.strategies}", file=sys.stderr)
            return 2

    opts = RunnerOptions(
        audit_report=args.audit_report,
        library_dir=args.library_dir,
        output_dir=args.output_dir,
        channel=args.output_channel,
        strategies_filter=strategies_filter,
        calibration_dir=args.calibration_dir,
        locale=args.locale,
        dry_run=args.dry_run,
        apply=args.apply,
    )

    if args.verbose:
        print(f"→ Audit report:  {opts.audit_report}", file=sys.stderr)
        print(f"→ Library dir:   {opts.library_dir}", file=sys.stderr)
        print(f"→ Channel:       {opts.channel}", file=sys.stderr)
        print(f"→ Output dir:    {opts.output_dir}", file=sys.stderr)
        if strategies_filter:
            print(f"→ Strategies:    {strategies_filter}", file=sys.stderr)

    result = run(opts)

    # Report summary
    print("=" * 70)
    print("figma-forge auto-remediate — Summary")
    print("=" * 70)
    print(f"  Strategies run:    {len(result.strategies_run)} ({result.strategies_run})")
    print(f"  Actions planned:   {result.action_count}")
    print(f"  Output files:      {result.file_count}")
    if result.skipped_gates:
        print(f"  Skipped gates:     {len(result.skipped_gates)}")
        for gid, reason in result.skipped_gates[:10]:
            print(f"     - G{gid:02d}: {reason}")
        if len(result.skipped_gates) > 10:
            print(f"     ... and {len(result.skipped_gates) - 10} more")

    if not opts.dry_run and result.file_count > 0:
        print(f"\n✓ Wrote {result.file_count} remediation artifact(s) to {opts.output_dir}")
    elif opts.dry_run:
        print("\n(dry-run) No files written.")

    if result.action_count == 0:
        print("\nNo actionable failures found.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
