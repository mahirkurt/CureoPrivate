#!/usr/bin/env python3
"""
publish_audit.py — CLI for the figma-forge PUBLISH_AUDIT mode (v0.2.0).

Run the 19-gate publish checklist against a Figma library, either as a
single file (v0.1.x-compatible invocation) or as a multi-file library
described by a registry JSON sidecar (v0.2.0 new capability).

Single-file usage (backward compatible):
    python3 scripts/publish_audit.py \
        --file-key <FIGMA_FILE_KEY> \
        --figma-pat "$FIGMA_PAT" \
        --output publish-audit.md
        [--strict]

Multi-file usage (v0.2.0):
    python3 scripts/publish_audit.py \
        --library-registry library-registry.json \
        --figma-pat "$FIGMA_PAT" \
        --output publish-audit.md
        [--strict]

The audit only reads. It never modifies any Figma file.

Exit codes:
    0   audit completed; no error-severity failures (or warn-only with no --strict)
    1   audit completed; at least one error-severity failure (or --strict + any fail)
    2   audit could not run (fetch failure, missing PAT, invalid registry)
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
from pathlib import Path

from publish_audit import (
    CalibrationReport,
    LibraryRegistry,
    MultiFileFigmaContext,
    __version__ as audit_version,
    format_report,
    format_json_report,
    has_checker,
    implemented_calibrator_count,
    implemented_gate_count,
    run_all_calibrators,
    run_all_gates,
    serialize_report,
)


def _parse_args() -> argparse.Namespace:
    """Construct and parse the CLI argument set."""
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--file-key", help="Single Figma file key (v0.1.x-compatible)")
    src.add_argument("--library-registry",
                     help="Path to a multi-file library-registry.json (v0.2.0)")
    parser.add_argument("--figma-pat", default=None,
                        help="Figma personal access token (never logged). "
                             "Required unless --static-only.")
    parser.add_argument("--static-only", action="store_true",
                        help="v0.3.0-rc: run only static checks (no live Figma context required). "
                             "Validates bundle integrity, DTCG alias resolvability, component spec "
                             "schema, SVG correctness, manifest completeness, accessibility "
                             "declarations — the 9 lint dimensions empirically validated against "
                             "the Düstur build. Suitable for CI without secrets.")
    parser.add_argument("--output", default="publish-audit.md",
                        help="Output report path (extension does not affect format; use --output-format)")
    parser.add_argument("--output-format", choices=("markdown", "json"),
                        default="markdown",
                        help="Report output format (default: markdown). "
                             "v0.3.0+: 'json' produces the schema-v1.0 machine-readable form "
                             "consumed by auto_remediate and audit-diff.")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on any error-severity failure")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print progress to stderr")
    parser.add_argument("--calibration-mode", action="store_true",
                        help="Also run heuristic calibration probes "
                             "(opt-in; v0.2.1+)")
    parser.add_argument("--calibration-output",
                        default="calibration.json",
                        help="Path for the calibration sidecar JSON "
                             "(only used with --calibration-mode)")
    return parser.parse_args()


def _build_context(args: argparse.Namespace) -> tuple[MultiFileFigmaContext, str, str] | int:
    """Build a populated MultiFileFigmaContext from ``args``.

    Returns ``(ctx, audit_target, file_label)`` on success, or an integer
    exit code on failure (registry load errors → 2).
    """
    if args.library_registry:
        try:
            registry = LibraryRegistry.from_path(args.library_registry)
        except (FileNotFoundError, ValueError) as e:
            print(f"Failed to load library registry: {e}", file=sys.stderr)
            return 2
        ctx = MultiFileFigmaContext.with_registry(registry, pat=args.figma_pat)
        return ctx, f"{registry.ds_name} v{registry.ds_version} (multi-file)", registry.ds_name
    ctx = MultiFileFigmaContext.single_file(file_key=args.file_key, pat=args.figma_pat)
    return ctx, args.file_key, "<fetching>"


def _fetch_or_fail(ctx: MultiFileFigmaContext, *, verbose: bool) -> int | None:
    """Drive ``ctx.fetch_all()``; return ``None`` on success or exit code 2 on HTTP failure."""
    if verbose:
        print(f"Fetching {len(ctx.files)} file(s)...", file=sys.stderr)
    try:
        ctx.fetch_all()
    except urllib.error.HTTPError as e:
        print(f"Figma API fetch failed: HTTP {e.code} {e.reason}", file=sys.stderr)
        return 2
    return None


def _derive_exit_code(results: list, *, strict: bool, verbose: bool) -> int:
    """Translate gate results into the process exit code.

    Returns 1 if any error-severity gate failed, or if ``strict`` is set
    and any warn-severity gate failed; otherwise 0.
    """
    error_failures = [r for r in results
                      if r.status == "fail" and r.gate.severity == "error"]
    if error_failures:
        if verbose:
            print(f"Audit found {len(error_failures)} error-severity issue(s).",
                  file=sys.stderr)
        return 1
    warn_failures = [r for r in results
                     if r.status == "fail" and r.gate.severity == "warn"]
    if strict and warn_failures:
        if verbose:
            print(f"--strict: {len(warn_failures)} warning(s) blocking release.",
                  file=sys.stderr)
        return 1
    return 0


def _build_calibration_report(args: argparse.Namespace,
                               ctx: MultiFileFigmaContext) -> CalibrationReport:
    """Run every registered calibrator and assemble the report container."""
    from datetime import datetime, timezone
    probes = run_all_calibrators(ctx)
    library_info: dict = {}
    if ctx.registry is not None:
        library_info = {
            "ds_name": ctx.registry.ds_name,
            "ds_version": ctx.registry.ds_version,
            "naming_convention": ctx.registry.naming_convention,
            "files": sorted(ctx.files.keys()),
        }
    else:
        library_info = {
            "ds_name": "<single-file>",
            "ds_version": "n/a",
            "naming_convention": "n/a",
            "files": ["primary"],
        }
    nodes_total = sum(probe.nodes_scanned for probe in probes.values())
    components_total = sum(len(f.components) for f in ctx.files.values())
    styles_total = sum(len(f.styles) for f in ctx.files.values())
    return CalibrationReport(
        schema_version="1.0",
        audit_run=datetime.now(timezone.utc).isoformat(),
        figma_forge_version=audit_version,
        library=library_info,
        totals={
            "nodes_walked": nodes_total,
            "components_scanned": components_total,
            "styles_examined": styles_total,
            "calibrators_run": len(probes),
        },
        probes=probes,
    )


def _emit_startup_banner(args: argparse.Namespace) -> None:
    """Print the v-{x.y.z} startup line when --verbose is set."""
    if not args.verbose:
        return
    print(f"figma-forge publish_audit v{audit_version} — "
          f"{implemented_gate_count()}/19 gates implemented; "
          f"{implemented_calibrator_count()} calibrators registered",
          file=sys.stderr)


def _write_audit_report(args: argparse.Namespace, results: list,
                          file_label: str, audit_target: str) -> None:
    """Render results to the requested format and write to ``args.output``.

    Format is selected by ``--output-format``: ``markdown`` (default) emits the
    human-readable report introduced in v0.1.x; ``json`` emits the schema-v1.0
    machine-readable form introduced in v0.3.0, suitable for auto_remediate
    and audit-diff downstream tools.
    """
    if getattr(args, "output_format", "markdown") == "json":
        report = format_json_report(results,
                                     file_label=file_label,
                                     audit_target=audit_target,
                                     build_version=audit_version)
    else:
        report = format_report(results,
                                file_label=file_label,
                                audit_target=audit_target,
                                build_version=audit_version)
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(report)
    if args.verbose:
        fmt = getattr(args, "output_format", "markdown")
        print(f"Wrote audit report ({fmt}) → {args.output}", file=sys.stderr)


def _run_calibration_if_enabled(args: argparse.Namespace,
                                  ctx: MultiFileFigmaContext) -> None:
    """If ``--calibration-mode`` is set, run calibrators and write sidecar."""
    if not args.calibration_mode:
        return
    if args.verbose:
        print("Running calibration probes...", file=sys.stderr)
    cal_report = _build_calibration_report(args, ctx)
    cal_path = serialize_report(cal_report, args.calibration_output)
    if args.verbose:
        print(f"Wrote calibration sidecar → {cal_path}", file=sys.stderr)


def _run_static_only(args: argparse.Namespace) -> int:
    """Execute the static-only lint pipeline (no live Figma context).

    Closes Düstur build lesson L4: validates bundle integrity, DTCG
    alias resolvability, component spec schema, SVG correctness,
    manifest completeness, and accessibility declarations — the nine
    lint dimensions empirically validated against the Düstur build.

    Suitable for CI runs without secrets and pre-publish offline gates.
    """
    from publish_audit.static_lint import run_static_lint

    if not args.library_registry:
        print("❌ --static-only requires --library-registry (cannot lint a single file).",
              file=sys.stderr)
        return 2

    library_dir = Path(args.library_registry).resolve().parent
    if args.verbose:
        print(f"figma-forge publish_audit (--static-only) "
              f"on {library_dir}", file=sys.stderr)

    results = run_static_lint(library_dir)

    # Reuse the existing report writer; static lint produces compatible GateResult objects
    file_label = library_dir.name
    audit_target = f"{library_dir.name} (static-only, no live Figma)"
    _write_audit_report(args, results, file_label, audit_target)

    return _derive_exit_code(results, strict=args.strict, verbose=args.verbose)


def main() -> int:
    """Run the publish audit CLI end-to-end and return the exit code."""
    args = _parse_args()

    # Static-only short-circuit — bypass live context, fetch, and gate harness
    if args.static_only:
        return _run_static_only(args)

    if not args.figma_pat:
        print("❌ --figma-pat is required unless --static-only is set.", file=sys.stderr)
        return 2

    _emit_startup_banner(args)

    built = _build_context(args)
    if isinstance(built, int):
        return built
    ctx, audit_target, file_label = built

    fetch_failure = _fetch_or_fail(ctx, verbose=args.verbose)
    if fetch_failure is not None:
        return fetch_failure

    if args.library_registry is None:
        file_label = ctx.primary.name or args.file_key

    if args.verbose:
        print("Running gates...", file=sys.stderr)
    results = run_all_gates(ctx)
    _write_audit_report(args, results, file_label, audit_target)
    _run_calibration_if_enabled(args, ctx)

    return _derive_exit_code(results, strict=args.strict, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
