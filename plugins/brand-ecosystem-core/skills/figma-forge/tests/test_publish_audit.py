#!/usr/bin/env python3
"""
test_publish_audit.py — Sprint 1 integration test for the v0.2.0
publish-audit framework.

Exercises each implemented gate against (a) a passing fixture and (b) a
failing fixture, asserting expected status. Designed to run without a
live Figma connection — all data is synthesized via the fixture
generators in ``publish_audit/fixtures.py``.

Usage:
    python3 tests/test_publish_audit.py            # run all assertions
    python3 tests/test_publish_audit.py --verbose  # show every gate's status
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the scripts/ package importable
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from publish_audit import (  # noqa: E402
    LibraryRegistry,
    MultiFileFigmaContext,
    fixtures as fx,
    has_checker,
    implemented_gate_count,
    run_all_gates,
    run_gate,
)


# ----------------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------------

class TestCase:
    def __init__(self, name: str, gate_id: int, expected_status: str,
                 fixture_loader, registry: dict | None = None,
                 min_failures: int = 0):
        self.name = name
        self.gate_id = gate_id
        self.expected_status = expected_status
        self.fixture_loader = fixture_loader   # callable → fixtures dict
        self.registry = registry
        self.min_failures = min_failures

    def run(self, verbose: bool = False) -> tuple[bool, str]:
        fixtures = self.fixture_loader()
        if self.registry is None:
            # Single-file path: take the first fixture as primary
            primary_fixture = next(iter(fixtures.values()))
            ctx = MultiFileFigmaContext.single_file(file_key="test_key", pat="<test>")
            ctx.load_fixtures({ctx._primary_role: primary_fixture})
        else:
            registry = LibraryRegistry.from_dict(self.registry)
            ctx = MultiFileFigmaContext.with_registry(registry, pat="<test>")
            ctx.load_fixtures(fixtures)

        if not has_checker(self.gate_id):
            return False, f"gate {self.gate_id} has no registered checker"
        result = run_gate(self.gate_id, ctx)
        if result.status != self.expected_status:
            return False, (f"expected status={self.expected_status}, "
                            f"got status={result.status}, "
                            f"failures={result.failures[:3]}")
        if self.expected_status == "fail" and len(result.failures) < self.min_failures:
            return False, (f"expected ≥{self.min_failures} failures, "
                            f"got {len(result.failures)}")
        if verbose:
            print(f"     status={result.status}  checked={result.checked_count}  "
                   f"failures={len(result.failures)}")
        return True, "ok"


# ----------------------------------------------------------------------------
# Fixture helpers (lambdas-as-callables for the test cases)
# ----------------------------------------------------------------------------

def foundations_only(fixture_fn):
    """Wrap a single-file fixture into a single-file context."""
    return lambda: {"primary": fixture_fn()}


def multi_file(foundations_fn, components_fn):
    """Build a multi-file fixture dict with the canonical role names."""
    return lambda: {
        "foundations": foundations_fn(),
        "components": components_fn(),
    }


CANONICAL_REGISTRY = {
    "ds_name": "TestDS",
    "ds_version": "1.0.0",
    "naming_convention": "carbon",
    "files": {
        "foundations": {"figma_file_key": "fkFoundations"},
        "components":  {"figma_file_key": "fkComponents"},
    }
}


# ----------------------------------------------------------------------------
# The test suite
# ----------------------------------------------------------------------------

TEST_CASES = [
    # G1 — bound paints
    TestCase("G1 pass: valid foundations",
             1, "pass", foundations_only(fx.make_minimal_valid_foundations)),

    # G2 — text styles
    TestCase("G2 pass: valid foundations",
             2, "pass", foundations_only(fx.make_minimal_valid_foundations)),

    # G3 — orphan styles
    TestCase("G3 pass: valid foundations",
             3, "pass", foundations_only(fx.make_minimal_valid_foundations)),
    TestCase("G3 fail: orphan style present",
             3, "fail", foundations_only(fx.make_foundations_orphan_styles),
             min_failures=1),

    # G4 — missing variable refs
    TestCase("G4 pass: valid foundations",
             4, "pass", foundations_only(fx.make_minimal_valid_foundations)),
    TestCase("G4 fail: broken alias",
             4, "fail", foundations_only(fx.make_foundations_missing_aliases),
             min_failures=1),

    # G5 — component descriptions
    TestCase("G5 pass: minimal components",
             5, "pass", foundations_only(fx.make_minimal_components)),

    # G10 — cover page (multi-file)
    TestCase("G10 pass: multi-file with cover",
             10, "pass",
             multi_file(fx.make_minimal_valid_foundations, fx.make_minimal_components),
             registry=CANONICAL_REGISTRY),
    TestCase("G10 fail: no cover page",
             10, "fail",
             multi_file(fx.make_foundations_no_cover, fx.make_minimal_components),
             registry=CANONICAL_REGISTRY,
             min_failures=1),

    # G12 — published styles
    TestCase("G12 pass: all styles published",
             12, "pass", foundations_only(fx.make_minimal_valid_foundations)),
    TestCase("G12 fail: unpublished style outside Candidates",
             12, "fail", foundations_only(fx.make_foundations_unpublished_style),
             min_failures=1),

    # G16 — modes per collection
    TestCase("G16 pass: valid foundations",
             16, "pass", foundations_only(fx.make_minimal_valid_foundations)),

    # G17 — Code Connect badges
    TestCase("G17 pass: components badged",
             17, "pass", foundations_only(fx.make_components_with_cc_badges)),
    TestCase("G17 fail: no badges",
             17, "fail", foundations_only(fx.make_components_no_cc_badges),
             min_failures=1),

    # G18 — cover metadata (multi-file)
    TestCase("G18 pass: cover has version+license+contact",
             18, "pass",
             multi_file(fx.make_minimal_valid_foundations, fx.make_minimal_components),
             registry=CANONICAL_REGISTRY),
    TestCase("G18 fail: cover page missing",
             18, "fail",
             multi_file(fx.make_foundations_no_cover, fx.make_minimal_components),
             registry=CANONICAL_REGISTRY,
             min_failures=1),

    # ----- Sprint 2 -----
    # G7 — variant matrix
    TestCase("G7 pass: complete 2×2 matrix",
             7, "pass",
             foundations_only(fx.make_components_complete_variant_matrix)),
    TestCase("G7 fail: 1 missing combination",
             7, "fail",
             foundations_only(fx.make_components_incomplete_variant_matrix),
             min_failures=1),
    TestCase("G7 pass: missing combo explicitly Disabled",
             7, "pass",
             foundations_only(fx.make_components_disabled_marker)),

    # G8 — component naming
    TestCase("G8 pass: Carbon-style names",
             8, "pass",
             multi_file(fx.make_minimal_valid_foundations, fx.make_minimal_components),
             registry=CANONICAL_REGISTRY),
    TestCase("G8 fail: snake_case names with Carbon convention",
             8, "fail",
             multi_file(fx.make_minimal_valid_foundations,
                         fx.make_components_bad_naming_carbon),
             registry=CANONICAL_REGISTRY,
             min_failures=1),
    TestCase("G8 n/a: single-file mode skips",
             8, "n_a",
             foundations_only(fx.make_minimal_components)),

    # G9 — variant property naming
    TestCase("G9 fail: PascalCase variant keys with Carbon convention",
             9, "fail",
             multi_file(fx.make_minimal_valid_foundations,
                         fx.make_components_bad_variant_property_carbon),
             registry=CANONICAL_REGISTRY,
             min_failures=1),

    # G11 — section headers
    TestCase("G11 pass: page has section header at top",
             11, "pass",
             foundations_only(fx.make_components_with_section_header)),
    TestCase("G11 fail: page lacks section header",
             11, "fail",
             foundations_only(fx.make_components_no_section_header),
             min_failures=1),

    # G19 — clean instance overrides
    TestCase("G19 pass: text + variant override only",
             19, "pass",
             foundations_only(fx.make_components_clean_instance)),
    TestCase("G19 fail: paint override detected",
             19, "fail",
             foundations_only(fx.make_components_detached_instance),
             min_failures=1),

    # ----- Sprint 3 -----
    # G14 — icons must be components
    TestCase("G14 pass: all icons are components",
             14, "pass",
             foundations_only(fx.make_icons_all_components)),
    TestCase("G14 fail: raw VECTOR icons",
             14, "fail",
             foundations_only(fx.make_icons_raw_vectors),
             min_failures=1),

    # G15 — icon size convention
    TestCase("G15 pass: 24×24 canonical icons",
             15, "pass",
             foundations_only(fx.make_icons_all_components)),
    TestCase("G15 fail: 22×22 off-grid icon",
             15, "fail",
             foundations_only(fx.make_icons_wrong_size),
             min_failures=1),
    TestCase("G15 n/a: no icons in file",
             15, "n_a",
             foundations_only(fx.make_minimal_components)),

    # G6 — component keywords
    TestCase("G6 pass: keyword line present with ≥4 tokens",
             6, "pass",
             foundations_only(fx.make_components_with_keywords)),
    TestCase("G6 fail: no keyword line",
             6, "fail",
             foundations_only(fx.make_components_no_keywords),
             min_failures=1),

    # G13 — effect styles to elevation tokens
    TestCase("G13 pass: elevation-named effect styles",
             13, "pass",
             foundations_only(fx.make_foundations_with_elevation_effects)),
    TestCase("G13 fail: ambiguous effect style name",
             13, "fail",
             foundations_only(fx.make_foundations_ambiguous_effects),
             min_failures=1),
    TestCase("G13 n/a: no effect styles in file",
             13, "n_a",
             foundations_only(fx.make_minimal_components)),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print(f"publish_audit integration test — "
           f"{implemented_gate_count()}/19 gates implemented")
    print()

    failed = []
    for tc in TEST_CASES:
        ok, msg = tc.run(verbose=args.verbose)
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {tc.name}")
        if not ok:
            print(f"      → {msg}")
            failed.append((tc, msg))

    print()
    print(f"  {len(TEST_CASES) - len(failed)}/{len(TEST_CASES)} passed")

    if failed:
        print()
        print("FAILED:")
        for tc, msg in failed:
            print(f"  · {tc.name}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
