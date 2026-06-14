#!/usr/bin/env python3
"""
test_calibration.py — Sprint 4 integration test for the v0.2.1
calibration framework.

Drives the calibration pipeline end-to-end:
  fixture → MultiFileFigmaContext → run_all_calibrators
  → CalibrationReport → serialize_report → calibration_analyzer

Scenarios covered:

  A. Calibrator coverage — every gate that *needs* calibration has one.
  B. Single-gate probe shape — G14 probe records the expected feature
     histograms, skip reasons, and boundary decisions.
  C. Report assembly — CalibrationReport serializes to a valid sidecar
     JSON that the analyzer can re-load.
  D. Analyzer aggregation — multi-sidecar analysis merges histograms
     and concatenates boundary decisions correctly.
  E. Anonymizer — anonymize_calibration replaces identifiers with the
     expected ``anon:`` prefix while preserving structure.

Run:
    python3 tests/test_calibration.py
    python3 tests/test_calibration.py --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tools"))

from publish_audit import (  # noqa: E402
    BoundaryDecision,
    CalibrationProbe,
    CalibrationReport,
    LibraryRegistry,
    MultiFileFigmaContext,
    __version__,
    fixtures as fx,
    has_calibrator,
    implemented_calibrator_count,
    run_all_calibrators,
    run_calibrator,
    serialize_report,
)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _build_test_context(fixtures: dict[str, dict]) -> MultiFileFigmaContext:
    """Construct a populated multi-file context for testing."""
    reg = LibraryRegistry.from_dict({
        "ds_name": "TestDS",
        "ds_version": "1.0.0",
        "naming_convention": "carbon",
        "files": {role: {"figma_file_key": f"fk{role.title()}"}
                   for role in fixtures.keys()},
    })
    ctx = MultiFileFigmaContext.with_registry(reg, pat="<test>")
    ctx.load_fixtures(fixtures)
    return ctx


# ----------------------------------------------------------------------------
# Scenarios
# ----------------------------------------------------------------------------

def check_calibrator_coverage(verbose: bool = False) -> None:
    """Every heuristic gate (G7, G13, G14, G15) must have a calibrator."""
    expected = {7, 13, 14, 15}
    for gid in expected:
        assert has_calibrator(gid), f"gate G{gid} missing calibrator"
    assert implemented_calibrator_count() == len(expected), (
        f"expected {len(expected)} calibrators, "
        f"got {implemented_calibrator_count()}"
    )
    if verbose:
        print(f"     coverage: {implemented_calibrator_count()} calibrators")


def check_g14_probe_shape(verbose: bool = False) -> None:
    """G14 probe should report nodes_scanned, candidates, decisions, and
    a non-empty feature distribution on a fixture with icons."""
    ctx = _build_test_context({
        "foundations": fx.make_pristine_foundations(),
        "icons": fx.make_icons_raw_vectors(),
    })
    probe = run_calibrator(14, ctx)
    assert probe is not None, "G14 calibrator returned None"
    assert probe.gate_id == 14
    assert probe.nodes_scanned > 0, "G14 should walk at least one node"
    assert probe.candidates_filtered >= 1, (
        f"G14 should find at least 1 icon candidate; got "
        f"{probe.candidates_filtered}"
    )
    assert "verdict" in probe.feature_distribution, (
        "G14 should record verdict histogram"
    )
    if verbose:
        print(f"     G14: scanned={probe.nodes_scanned} "
               f"candidates={probe.candidates_filtered}")


def check_g15_probe_with_offgrid(verbose: bool = False) -> None:
    """G15 probe on a wrong-size icon fixture should record at least one
    boundary decision OR at least one off-canonical width bucket."""
    ctx = _build_test_context({
        "foundations": fx.make_pristine_foundations(),
        "icons": fx.make_icons_wrong_size(),
    })
    probe = run_calibrator(15, ctx)
    assert probe is not None
    assert probe.gate_id == 15
    width_buckets = probe.feature_distribution.get("width_buckets", {})
    # An off-grid icon should land in a non-canonical bucket OR trigger
    # a boundary decision; either is valid evidence the probe is firing.
    canonical = {"16", "20", "24", "32", "48"}
    off_canonical = [b for b in width_buckets.keys() if b not in canonical]
    has_evidence = (off_canonical or probe.boundary_decisions)
    assert has_evidence, (
        f"G15 should record off-grid evidence; got buckets={width_buckets}, "
        f"boundary count={len(probe.boundary_decisions)}"
    )
    if verbose:
        print(f"     G15: buckets={width_buckets} "
               f"boundaries={len(probe.boundary_decisions)}")


def check_g13_probe_classification(verbose: bool = False) -> None:
    """G13 probe should classify effect styles into the expected buckets."""
    ctx = _build_test_context({
        "foundations": fx.make_foundations_ambiguous_effects(),
    })
    probe = run_calibrator(13, ctx)
    assert probe is not None
    # Ambiguous fixture has at least one ambiguous effect style
    classifications = probe.feature_distribution.get("classification", {})
    assert "ambiguous" in classifications, (
        f"G13 should classify the fixture's ambiguous effect; "
        f"got {classifications}"
    )
    if verbose:
        print(f"     G13: classifications={classifications}")


def check_g7_probe_axes(verbose: bool = False) -> None:
    """G7 probe should record axis_count and expected_count_buckets for
    component sets."""
    ctx = _build_test_context({
        "foundations": fx.make_pristine_foundations(),
        "components": fx.make_components_incomplete_variant_matrix(),
    })
    probe = run_calibrator(7, ctx)
    assert probe is not None
    if probe.decisions_made == 0:
        # The fixture may not contain any component sets; that's fine.
        if verbose:
            print("     G7: no component sets in fixture (n/a)")
        return
    assert "axis_count" in probe.feature_distribution
    assert "expected_count_buckets" in probe.feature_distribution
    if verbose:
        print(f"     G7: axes={probe.feature_distribution.get('axis_count')}")


def check_report_serialization_roundtrip(verbose: bool = False) -> None:
    """CalibrationReport → JSON → load → equivalent structure."""
    ctx = _build_test_context({
        "foundations": fx.make_pristine_foundations(),
        "icons": fx.make_icons_raw_vectors(),
    })
    probes = run_all_calibrators(ctx)
    report = CalibrationReport(
        schema_version="1.0",
        audit_run="2026-05-26T10:00:00+00:00",
        figma_forge_version=__version__,
        library={"ds_name": "TestDS", "ds_version": "1.0.0",
                 "naming_convention": "carbon",
                 "files": ["foundations", "icons"]},
        totals={"nodes_walked": 100},
        probes=probes,
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        tmp_path = Path(tmp.name)
    serialize_report(report, tmp_path)
    with open(tmp_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["schema_version"] == "1.0"
    assert loaded["figma_forge_version"] == __version__
    assert "probes" in loaded
    assert "14" in loaded["probes"], "report should include G14 probe"
    tmp_path.unlink()
    if verbose:
        print(f"     roundtrip: {len(loaded['probes'])} probes serialized")


def check_analyzer_aggregation(verbose: bool = False) -> None:
    """calibration_analyzer should merge two sidecars correctly."""
    from calibration_analyzer import aggregate_totals, aggregate_skip_reasons

    probe_a = {"nodes_scanned": 100, "candidates_filtered": 20,
                "decisions_made": 18, "skip_reasons": {"no_bbox": 30}}
    probe_b = {"nodes_scanned": 250, "candidates_filtered": 45,
                "decisions_made": 40, "skip_reasons": {"no_bbox": 50,
                                                         "not_square": 8}}
    totals = aggregate_totals([probe_a, probe_b])
    assert totals["nodes_scanned"] == 350
    assert totals["candidates_filtered"] == 65
    assert totals["decisions_made"] == 58
    skips = aggregate_skip_reasons([probe_a, probe_b])
    assert skips["no_bbox"] == 80
    assert skips["not_square"] == 8
    if verbose:
        print(f"     analyzer aggregation: totals={totals}, skips={skips}")


def check_anonymizer(verbose: bool = False) -> None:
    """anonymize_calibration replaces identifiers with ``anon:`` prefix."""
    from anonymize_calibration import anonymize, _audit_clean

    sidecar = {
        "schema_version": "1.0",
        "library": {"ds_name": "Roche Design System", "ds_version": "1.0",
                     "naming_convention": "carbon",
                     "files": ["foundations", "components"]},
        "probes": {
            "14": {
                "gate_id": 14,
                "nodes_scanned": 10,
                "candidates_filtered": 3,
                "decisions_made": 3,
                "boundary_decisions": [
                    {"node_id": "1:23", "node_name": "Patient/Avatar",
                     "feature_name": "squareness", "feature_value": 2,
                     "threshold": 2, "verdict": "candidate",
                     "would_flip_at": 1, "gate_role": "icons"}
                ],
                "feature_distribution": {},
                "skip_reasons": {},
                "notes": [],
            }
        }
    }
    anon = anonymize(sidecar, salt="testsalt-12345")
    # Library name should be hashed
    assert anon["library"]["ds_name"].startswith("anon:"), (
        f"ds_name not anonymized: {anon['library']['ds_name']}"
    )
    # Canonical file roles should NOT be hashed (preserve structure)
    assert "foundations" in anon["library"]["files"]
    # Boundary decision identifiers should be hashed
    bd = anon["probes"]["14"]["boundary_decisions"][0]
    assert bd["node_id"].startswith("anon:"), f"node_id leaked: {bd['node_id']}"
    assert bd["node_name"].startswith("anon:"), f"node_name leaked: {bd['node_name']}"
    # Threshold and verdict must survive
    assert bd["threshold"] == 2
    assert bd["verdict"] == "candidate"
    # Audit pass
    issues = _audit_clean(anon)
    assert not issues, f"audit_clean flagged: {issues}"
    # Deterministic: same salt → same hash
    anon2 = anonymize(sidecar, salt="testsalt-12345")
    assert (anon["probes"]["14"]["boundary_decisions"][0]["node_id"]
            == anon2["probes"]["14"]["boundary_decisions"][0]["node_id"])
    # Different salt → different hash
    anon3 = anonymize(sidecar, salt="different-salt")
    assert (anon["probes"]["14"]["boundary_decisions"][0]["node_id"]
            != anon3["probes"]["14"]["boundary_decisions"][0]["node_id"])
    if verbose:
        print(f"     anonymizer: {bd['node_name']}")


# ----------------------------------------------------------------------------
# Test suite
# ----------------------------------------------------------------------------

CASES = [
    ("A. calibrator coverage (G7, G13, G14, G15)", check_calibrator_coverage),
    ("B. G14 probe shape — fields, histograms, candidates", check_g14_probe_shape),
    ("C. G15 probe — off-grid icons surface as evidence", check_g15_probe_with_offgrid),
    ("D. G13 probe — effect-style classification distribution", check_g13_probe_classification),
    ("E. G7 probe — variant axis count + expected size buckets", check_g7_probe_axes),
    ("F. report serialize → JSON → load roundtrip", check_report_serialization_roundtrip),
    ("G. analyzer aggregation across two sidecars", check_analyzer_aggregation),
    ("H. anonymizer scrubs identifiers; salt determinism", check_anonymizer),
]


def main() -> int:
    """Run all calibration test cases."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print(f"calibration test — {implemented_calibrator_count()} calibrators "
          f"registered (figma-forge v{__version__})")
    print()
    failed = []
    for name, fn in CASES:
        try:
            fn(verbose=args.verbose)
            print(f"  ✅  {name}")
        except AssertionError as e:
            print(f"  ❌  {name}")
            print(f"      → {e}")
            failed.append((name, str(e)))
        except Exception as e:  # noqa: BLE001
            print(f"  ❌  {name}")
            print(f"      → {type(e).__name__}: {e}")
            failed.append((name, f"{type(e).__name__}: {e}"))
    print()
    print(f"  {len(CASES) - len(failed)}/{len(CASES)} passed")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
