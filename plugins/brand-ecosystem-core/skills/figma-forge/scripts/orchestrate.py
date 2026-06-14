#!/usr/bin/env python3
"""orchestrate.py — CLI for figma-forge orchestrate mode (v0.3.0-rc).

Consume an ``orchestration.json`` manifest and execute every stage in
order, dispatching to the appropriate :class:`Stage` executor.

Usage::

    python3 scripts/orchestrate.py \\
        --manifest ./dustur-figma-library/orchestration.json \\
        --library-dir ./dustur-figma-library \\
        --dry-run

Exit codes::

    0  All stages succeeded (or all skipped intentionally)
    1  At least one stage failed
    2  Cannot run (invalid manifest, missing library, etc.)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Make package importable regardless of CWD
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from orchestrate import (  # noqa: E402
    ManifestError,
    RunnerOptions,
    all_stages,
    parse_manifest,
    run_pipeline,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="orchestrate.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--manifest", type=Path,
                   help="Path to orchestration.json. Required unless --list-stages.")
    p.add_argument("--library-dir", type=Path,
                   help="Library bundle root. Required unless --list-stages.")
    p.add_argument("--dry-run", action="store_true",
                   help="Plan only; no I/O.")
    p.add_argument("--resume", type=str, default=None,
                   help="Resume from STAGE (mode name or 1-indexed integer).")
    p.add_argument("--only", type=str, default=None,
                   help="Comma-separated list of mode names to run; others skipped.")
    p.add_argument("--continue-on-failure", action="store_true",
                   help="Continue running subsequent stages after a failure.")
    p.add_argument("--locale", default="en-US",
                   help="Output locale propagated to per-stage executors.")
    p.add_argument("--figma-pat", default=os.environ.get("FIGMA_TOKEN"),
                   help="Figma PAT (live operations). Reads FIGMA_TOKEN env if unset.")
    p.add_argument("--list-stages", action="store_true",
                   help="List all registered stage executors and exit.")
    p.add_argument("--validate-only", action="store_true",
                   help="Parse the manifest and report issues; do not execute.")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print per-stage progress to stderr.")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_stages:
        regs = all_stages()
        print(f"Registered stages ({len(regs)}):", file=sys.stderr)
        for mode in sorted(regs):
            cls = regs[mode]
            live = "[live]" if cls.live_required else "[exec]"
            print(f"  {mode:24s} {live}  {cls.description}")
        return 0

    if args.manifest is None or args.library_dir is None:
        print("❌ --manifest and --library-dir are required.", file=sys.stderr)
        return 2

    if not args.manifest.exists():
        print(f"❌ Manifest not found: {args.manifest}", file=sys.stderr)
        return 2
    if not args.library_dir.is_dir():
        print(f"❌ Library directory not found: {args.library_dir}", file=sys.stderr)
        return 2

    try:
        top, specs = parse_manifest(args.manifest)
    except ManifestError as e:
        print(f"❌ Manifest validation failed: {e}", file=sys.stderr)
        return 2

    if args.validate_only:
        print(f"✓ Manifest valid: {len(specs)} stage(s) declared")
        for s in specs:
            print(f"  Stage {s.index}: {s.mode} — {s.description[:80]}")
        return 0

    forge_root = _SCRIPT_DIR.parent  # figma-forge/

    opts = RunnerOptions(
        manifest_path=args.manifest,
        library_dir=args.library_dir,
        forge_root=forge_root,
        dry_run=args.dry_run,
        verbose=args.verbose,
        locale=args.locale,
        figma_pat=args.figma_pat,
        resume_from=args.resume,
        only=[m.strip() for m in args.only.split(",")] if args.only else None,
        continue_on_failure=args.continue_on_failure,
    )

    if args.verbose:
        ds_name = top.get("library", "Library")
        ds_version = top.get("version", "?")
        mode_descr = "DRY RUN" if args.dry_run else "EXECUTE"
        print(f"figma-forge orchestrate — {ds_name} v{ds_version} ({mode_descr})", file=sys.stderr)
        print(f"  Manifest:    {args.manifest}", file=sys.stderr)
        print(f"  Library:     {args.library_dir}", file=sys.stderr)
        print(f"  Stages:      {len(specs)}", file=sys.stderr)

    result = run_pipeline(opts)

    print("=" * 70)
    print(f"figma-forge orchestrate — Summary  ({result.duration_seconds}s)")
    print("=" * 70)
    print(f"  Total stages:   {len(result.stages)}")
    print(f"  ✓ Success:      {result.success_count}")
    print(f"  ✗ Failed:       {result.failed_count}")
    print(f"  ↷ Skipped:      {result.skipped_count}")
    print()
    for s in result.stages:
        sym = {"success": "✓", "failed": "✗", "skipped": "↷",
               "dry_run": "·", "running": "▷"}.get(s.status, "?")
        print(f"  {sym} Stage {s.stage_index:2d}: {s.mode:20s} "
              f"{s.status.upper():8s} ({s.duration_seconds}s)")
        if s.error:
            print(f"      Error: {s.error[:200]}")
        if s.skipped_reason:
            print(f"      Reason: {s.skipped_reason}")

    # Write a machine-readable summary alongside the manifest
    if not args.dry_run:
        summary_path = args.library_dir / "orchestrate-summary.json"
        summary_path.write_text(
            json.dumps({
                "manifest": str(args.manifest),
                "library_dir": str(args.library_dir),
                "duration_seconds": result.duration_seconds,
                "totals": {
                    "stages": len(result.stages),
                    "success": result.success_count,
                    "failed": result.failed_count,
                    "skipped": result.skipped_count,
                },
                "stages": [
                    {
                        "index": s.stage_index,
                        "mode": s.mode,
                        "status": s.status,
                        "duration_seconds": s.duration_seconds,
                        "error": s.error,
                        "skipped_reason": s.skipped_reason,
                        "artifacts": s.artifacts,
                    }
                    for s in result.stages
                ],
            }, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if args.verbose:
            print(f"\n✓ Summary written to {summary_path}", file=sys.stderr)

    return 0 if result.failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
