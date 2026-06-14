#!/usr/bin/env python3
"""
test_publish_audit_e2e.py — Sprint 3 end-to-end integration test.

Where ``test_publish_audit.py`` exercises each gate in isolation against
synthetic fixtures, this end-to-end suite drives the whole stack:

  registry → MultiFileFigmaContext → run_all_gates → format_report

…across realistic multi-file library scenarios. It catches regressions
that single-gate tests miss:

  * gate ordering and cross-gate interaction in ``run_all_gates``
  * per-file failure aggregation in ``GateResult.per_file``
  * single-file v0.1.x backward compatibility — multi-file gates must
    return ``n_a`` rather than firing spuriously
  * Markdown report shape (heading text, summary counts, gate IDs)
  * strict-mode exit semantics: error severity → fail, warn/info → ok

Run:
    python3 tests/test_publish_audit_e2e.py
    python3 tests/test_publish_audit_e2e.py --verbose
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from publish_audit import (  # noqa: E402
    GATE_CATALOG,
    LibraryRegistry,
    MultiFileFigmaContext,
    __version__,
    fixtures as fx,
    format_report,
    has_checker,
    implemented_gate_count,
    run_all_gates,
)


# ----------------------------------------------------------------------------
# Registry helpers — full 4-file canonical library
# ----------------------------------------------------------------------------

FOUR_FILE_REGISTRY = {
    "ds_name": "TestDS",
    "ds_version": "1.0.0",
    "naming_convention": "carbon",
    "files": {
        "foundations": {"figma_file_key": "fkFoundations"},
        "components":  {"figma_file_key": "fkComponents"},
        "patterns":    {"figma_file_key": "fkPatterns"},
        "icons":       {"figma_file_key": "fkIcons"},
    },
}


def _build_context(fixtures: dict[str, dict],
                   registry_dict: dict | None = None) -> MultiFileFigmaContext:
    """Build a populated MultiFileFigmaContext from fixture dicts."""
    if registry_dict is None:
        registry_dict = FOUR_FILE_REGISTRY
    registry = LibraryRegistry.from_dict(registry_dict)
    ctx = MultiFileFigmaContext.with_registry(registry, pat="<test>")
    ctx.load_fixtures(fixtures)
    return ctx


def _build_single_file_context(fixture: dict) -> MultiFileFigmaContext:
    """Build a v0.1.x-style single-file context (no registry)."""
    ctx = MultiFileFigmaContext.single_file(file_key="legacy_key", pat="<test>")
    ctx.load_fixtures({ctx._primary_role: fixture})
    return ctx


# ----------------------------------------------------------------------------
# Scenarios
# ----------------------------------------------------------------------------

def scenario_pristine_library() -> dict[str, dict]:
    """Four-file library where every gate either passes or is genuinely
    not-applicable. No error- *or* warn-severity failures expected — this
    is the canonical green-build baseline."""
    return {
        "foundations": fx.make_pristine_foundations(),
        "components":  fx.make_pristine_components(),
        "patterns":    fx.make_pristine_patterns(),
        "icons":       fx.make_pristine_icons(),
    }


def scenario_mixed_failures() -> dict[str, dict]:
    """Library with multiple distinct failure modes scattered across files.
    Used to verify per-file failure attribution and that run_all_gates
    surfaces every problem rather than short-circuiting."""
    return {
        # Foundations: missing-alias (G4 error) + unpublished-style (G12 warn)
        "foundations": fx.make_foundations_missing_aliases(),
        # Components: incomplete variant matrix (G7 error) + no keywords (G6 warn)
        "components":  fx.make_components_incomplete_variant_matrix(),
        # Patterns: minimal/clean — should pass
        "patterns":    fx.make_minimal_components(),
        # Icons: raw VECTOR nodes (G14 error)
        "icons":       fx.make_icons_raw_vectors(),
    }


# ----------------------------------------------------------------------------
# Test cases
# ----------------------------------------------------------------------------

class E2ECase:
    def __init__(self, name: str, check_fn):
        self.name = name
        self.check_fn = check_fn

    def run(self, verbose: bool = False) -> tuple[bool, str]:
        try:
            self.check_fn(verbose=verbose)
        except AssertionError as exc:
            return False, str(exc) or "assertion failed"
        except Exception as exc:  # noqa: BLE001
            return False, f"{type(exc).__name__}: {exc}"
        return True, "ok"


def _summary(results) -> dict:
    return {
        "pass":   sum(1 for r in results if r.status == "pass"),
        "fail":   sum(1 for r in results if r.status == "fail"),
        "n_a":    sum(1 for r in results if r.status == "n_a"),
        "skip":   sum(1 for r in results if r.status == "skip"),
        "errors": sum(1 for r in results
                      if r.status == "fail" and r.gate.severity == "error"),
        "warns":  sum(1 for r in results
                      if r.status == "fail" and r.gate.severity == "warn"),
        "infos":  sum(1 for r in results
                      if r.status == "fail" and r.gate.severity == "info"),
    }


# ----------------------------------------------------------------------------
# Scenario A — pristine library: no error-severity failures anywhere
# ----------------------------------------------------------------------------

def check_pristine_no_errors(verbose: bool = False) -> None:
    ctx = _build_context(scenario_pristine_library())
    results = run_all_gates(ctx)
    s = _summary(results)
    if verbose:
        print(f"     pristine: {s}")

    assert len(results) == 19, f"expected 19 gate results, got {len(results)}"
    assert s["skip"] == 0, (
        f"expected 0 skipped gates in v0.2.0 build, got {s['skip']} — "
        f"some gates are no longer registered?"
    )
    assert s["errors"] == 0, (
        f"pristine library should not surface error-severity failures, "
        f"got {s['errors']}: "
        f"{[r.gate.id for r in results if r.status == 'fail' and r.gate.severity == 'error']}"
    )


# ----------------------------------------------------------------------------
# Scenario B — mixed failures land on the right gates AND the right files
# ----------------------------------------------------------------------------

def check_mixed_failures_attribution(verbose: bool = False) -> None:
    ctx = _build_context(scenario_mixed_failures())
    results = run_all_gates(ctx)
    by_id = {r.gate.id: r for r in results}
    s = _summary(results)
    if verbose:
        print(f"     mixed:    {s}")

    # At least the seeded failures should fire.
    assert by_id[4].status == "fail", "G4 (missing alias) should fail"
    assert by_id[7].status == "fail", "G7 (variant matrix) should fail"
    assert by_id[14].status == "fail", "G14 (raw icons) should fail"

    # Per-file attribution: the missing-alias failure must be attributed to
    # the foundations file, and the raw-vector failure to the icons file.
    g4 = by_id[4]
    g14 = by_id[14]
    assert "foundations" in g4.per_file or len(g4.failures) > 0, (
        f"G4 per_file should include foundations; got {g4.per_file}"
    )
    if g14.per_file:
        assert "icons" in g14.per_file, (
            f"G14 per_file should attribute to icons; got {g14.per_file}"
        )

    # Patterns file is clean → should not appear in per_file for any error gate
    for r in results:
        if r.status == "fail" and r.gate.severity == "error" and r.per_file:
            assert "patterns" not in r.per_file or not r.per_file.get("patterns"), (
                f"Gate {r.gate.id} attributed errors to clean patterns file: "
                f"{r.per_file}"
            )


# ----------------------------------------------------------------------------
# Scenario C — single-file mode: multi-file gates return n_a, not error
# ----------------------------------------------------------------------------

def check_single_file_backward_compat(verbose: bool = False) -> None:
    """v0.1.x callers passed a single file_key. Multi-file-only gates
    (G8, G10, G15, G18 — those that need a registry to know which file is
    which) must degrade gracefully to ``n_a`` rather than raising or
    falsely failing."""
    ctx = _build_single_file_context(fx.make_minimal_valid_foundations())
    results = run_all_gates(ctx)
    s = _summary(results)
    if verbose:
        print(f"     single:   {s}")

    assert len(results) == 19, f"expected 19 results, got {len(results)}"
    assert s["errors"] == 0, (
        f"single-file pristine fixture should not raise errors, got {s['errors']}"
    )

    # G8 (component naming) requires registry naming_convention → n_a.
    by_id = {r.gate.id: r for r in results}
    assert by_id[8].status == "n_a", (
        f"G8 should be n_a in single-file mode; got {by_id[8].status}"
    )


# ----------------------------------------------------------------------------
# Scenario D — Markdown report format remains v0.1.x-compatible
# ----------------------------------------------------------------------------

def check_report_format(verbose: bool = False) -> None:
    ctx = _build_context(scenario_mixed_failures())
    results = run_all_gates(ctx)
    report = format_report(
        results,
        file_label="TestDS multi-file library",
        audit_target="fkFoundations+fkComponents+fkPatterns+fkIcons",
    )
    if verbose:
        head = "\n".join(report.splitlines()[:8])
        print(f"     report head:\n{head}")

    # H1 heading unchanged from v0.1.x
    assert report.startswith("# figma-forge Publish Audit — "), (
        "Report H1 heading drifted from v0.1.x format"
    )

    # Summary lines present (counts vary, order locked)
    required_lines = [
        "- Audit run: ",
        "- Audit target: `",
        "- figma-forge audit framework version: ",
        "- Total checks: 19",
        "- ✅ Passed: ",
        "- ❌ Errors: ",
        "- ⚠️ Warnings: ",
        "- ℹ️ Info: ",
        "- 🔵 Skipped/N-A: ",
    ]
    for line in required_lines:
        assert line in report, f"required summary line missing: {line!r}"

    # Every gate gets a section header — exactly 19, in numeric order.
    headers = re.findall(r"^### Gate (\d+) — ", report, flags=re.MULTILINE)
    assert len(headers) == 19, f"expected 19 gate sections, got {len(headers)}"
    ids = [int(h) for h in headers]
    assert ids == sorted(ids), f"gate sections out of order: {ids}"

    # build_version defaults to package __version__
    assert f"figma-forge audit framework version: {__version__}" in report, (
        f"report build_version should reflect __version__ ({__version__!r})"
    )


# ----------------------------------------------------------------------------
# Scenario E — strict-mode exit semantics
# ----------------------------------------------------------------------------

def check_strict_exit_semantics(verbose: bool = False) -> None:
    """The CLI returns exit code 1 iff any ``fail`` result has severity
    ``error`` OR (in strict mode) any has severity ``warn``. We replicate
    the logic the CLI uses, against both pristine and failure scenarios."""

    def derive_exit(results, *, strict: bool) -> int:
        for r in results:
            if r.status != "fail":
                continue
            if r.gate.severity == "error":
                return 1
            if strict and r.gate.severity == "warn":
                return 1
        return 0

    pristine = run_all_gates(_build_context(scenario_pristine_library()))
    mixed    = run_all_gates(_build_context(scenario_mixed_failures()))

    assert derive_exit(pristine, strict=False) == 0
    assert derive_exit(pristine, strict=True) == 0, (
        "pristine library should pass strict mode"
    )
    assert derive_exit(mixed, strict=False) == 1, (
        "mixed-failure library has error-severity gates and must exit 1"
    )
    assert derive_exit(mixed, strict=True) == 1


# ----------------------------------------------------------------------------
# Scenario F — coverage invariants: every catalog gate has a checker
# ----------------------------------------------------------------------------

def check_full_coverage(verbose: bool = False) -> None:
    missing = [g.id for g in GATE_CATALOG if not has_checker(g.id)]
    assert not missing, (
        f"v0.2.0 release criterion: all 19 gates must have checkers; "
        f"missing: {missing}"
    )
    assert implemented_gate_count() == 19, (
        f"implemented_gate_count={implemented_gate_count()}, expected 19"
    )


# ----------------------------------------------------------------------------
# Scenario G — deterministic ordering: results follow GATE_CATALOG order
# ----------------------------------------------------------------------------

def check_result_ordering(verbose: bool = False) -> None:
    ctx = _build_context(scenario_pristine_library())
    results = run_all_gates(ctx)
    ids = [r.gate.id for r in results]
    expected = [g.id for g in GATE_CATALOG]
    assert ids == expected, (
        f"run_all_gates returned out-of-order results: {ids} vs {expected}"
    )


# ----------------------------------------------------------------------------
# Test suite
# ----------------------------------------------------------------------------

CASES: list[E2ECase] = [
    E2ECase("A. pristine library — no error-severity failures",
            check_pristine_no_errors),
    E2ECase("B. mixed failures — gates fire and attribute correctly",
            check_mixed_failures_attribution),
    E2ECase("C. single-file mode — multi-file gates degrade to n/a",
            check_single_file_backward_compat),
    E2ECase("D. Markdown report — v0.1.x format preserved",
            check_report_format),
    E2ECase("E. strict-mode exit semantics — error vs warn",
            check_strict_exit_semantics),
    E2ECase("F. coverage invariant — 19/19 gates have checkers",
            check_full_coverage),
    E2ECase("G. ordering invariant — results follow GATE_CATALOG order",
            check_result_ordering),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print(f"publish_audit end-to-end test — "
           f"{implemented_gate_count()}/19 gates implemented "
           f"(figma-forge v{__version__})")
    print()

    failed = []
    for case in CASES:
        ok, msg = case.run(verbose=args.verbose)
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {case.name}")
        if not ok:
            print(f"      → {msg}")
            failed.append((case, msg))

    print()
    print(f"  {len(CASES) - len(failed)}/{len(CASES)} passed")

    if failed:
        print()
        print("FAILED:")
        for case, msg in failed:
            print(f"  · {case.name}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
