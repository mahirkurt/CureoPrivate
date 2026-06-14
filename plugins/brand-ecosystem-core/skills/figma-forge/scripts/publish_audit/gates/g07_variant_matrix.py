"""Gate 7 — Every component-set's variant Cartesian product must be fully
populated (or explicitly mark disabled combinations).

This is the most consequential structural gate: a gap in the variant matrix
silently routes consumers to the "closest" variant Figma can find, which
breaks design intent in ways that don't show up in code reviews.

Implementation rides on :class:`VariantMatrixAnalyzer` from
``publish_audit.variants``. The gate iterates every ComponentSet across
every publishable file, parses children, computes the matrix, and reports
the missing combinations.

It additionally surfaces two soft-failure modes as ``notes``:
  * matrix product ≥64 → editor performance warning
  * matrix product ≥256 → publish risk warning
"""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate
from ..variants import (
    HARD_VARIANT_FAIL_THRESHOLD,
    SOFT_VARIANT_WARN_THRESHOLD,
    analyze_component_set,
)


MAX_MISSING_LISTED_PER_SET = 5  # cap finding text length per set


@register_gate(7)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Detect Cartesian-product gaps in each component set's variant matrix."""
    res = GateResult(gate=get_gate(7))
    for role, f in ctx.iter_publishable_files():
        # Pre-group children by their componentSetId for fast lookup.
        children_by_set: dict[str, list[dict]] = {}
        for cid, comp in f.components.items():
            set_id = comp.get("componentSetId")
            if set_id:
                children_by_set.setdefault(set_id, []).append(
                    {**comp, "_id": cid}
                )
        for set_id, set_meta in f.component_sets.items():
            res.checked_count += 1
            children = children_by_set.get(set_id, [])
            matrix = analyze_component_set(set_id, set_meta, children)
            if matrix.exceeds_hard_threshold:
                res.notes.append(
                    f"[{role}] {matrix.component_set_name}: variant count "
                    f"{matrix.expected_count} ≥ {HARD_VARIANT_FAIL_THRESHOLD} "
                    f"(Figma may refuse to publish; consider axis splitting)"
                )
            elif matrix.exceeds_soft_threshold:
                res.notes.append(
                    f"[{role}] {matrix.component_set_name}: variant count "
                    f"{matrix.expected_count} ≥ {SOFT_VARIANT_WARN_THRESHOLD} "
                    f"(editor performance may degrade)"
                )
            if not matrix.is_complete:
                missing = sorted(matrix.missing)
                shown = ", ".join(
                    f"({'/'.join(t)})" for t in missing[:MAX_MISSING_LISTED_PER_SET]
                )
                if len(missing) > MAX_MISSING_LISTED_PER_SET:
                    shown += f" + {len(missing) - MAX_MISSING_LISTED_PER_SET} more"
                axis_summary = ", ".join(
                    f"{k}={len(v)}" for k, v in matrix.axes.items()
                )
                res.add(
                    f"[{role}] {matrix.component_set_name} "
                    f"({axis_summary} → {matrix.expected_count} expected, "
                    f"{len(missing)} missing): {shown}",
                    role=role
                )
            for err in matrix.parse_errors:
                res.notes.append(f"[{role}] {matrix.component_set_name}: {err}")
    res.mark_fail()
    return res


# ----------------------------------------------------------------------------
# Calibration probe — v0.2.1
# ----------------------------------------------------------------------------

from ..calibration import (
    BoundaryDecision,
    CalibrationProbe,
    bucket_linear,
    register_calibrator,
)


@register_calibrator(7)
def calibrate(ctx: MultiFileFigmaContext) -> CalibrationProbe:
    """Capture variant-matrix shape distributions: axis counts, expected
    Cartesian product sizes, coverage ratios, and parse-error frequencies.

    Boundary captures: component sets just below the soft (64) or hard
    (256) variant-count thresholds — operators can use these to see how
    much headroom they have before Figma's editor performance degrades.
    """
    probe = CalibrationProbe(gate_id=7)
    for role, f in ctx.iter_publishable_files():
        children_by_set: dict[str, list[dict]] = {}
        for cid, comp in f.components.items():
            set_id = comp.get("componentSetId")
            if set_id:
                children_by_set.setdefault(set_id, []).append({**comp, "_id": cid})
        for set_id, set_meta in f.component_sets.items():
            probe.nodes_scanned += 1
            children = children_by_set.get(set_id, [])
            matrix = analyze_component_set(set_id, set_meta, children)
            probe.candidates_filtered += 1
            probe.decisions_made += 1
            probe.increment_histogram("axis_count", str(len(matrix.axes)))
            probe.increment_histogram(
                "expected_count_buckets",
                bucket_linear(matrix.expected_count, bin_size=16)
            )
            coverage_pct = int(round(matrix.coverage_ratio * 100))
            probe.increment_histogram(
                "coverage_pct_buckets",
                bucket_linear(coverage_pct, bin_size=10)
            )
            probe.increment_histogram(
                "verdict", "complete" if matrix.is_complete else "incomplete"
            )
            if matrix.parse_errors:
                probe.increment_histogram(
                    "parse_error_count", str(min(len(matrix.parse_errors), 5))
                )
                for err in matrix.parse_errors:
                    probe.notes.append(
                        f"[{role}] {matrix.component_set_name}: parse_error: {err}"
                    )
            # Boundary: within 25% of soft (64) or hard (256) thresholds
            for thresh in (SOFT_VARIANT_WARN_THRESHOLD, HARD_VARIANT_FAIL_THRESHOLD):
                distance = matrix.expected_count - thresh
                # Capture sets that are within ±25% of a threshold
                if abs(distance) <= thresh * 0.25:
                    probe.add_boundary(BoundaryDecision(
                        node_id=str(set_id),
                        node_name=str(matrix.component_set_name),
                        feature_name=f"expected_count_vs_{thresh}",
                        feature_value=float(matrix.expected_count),
                        threshold=float(thresh),
                        verdict=("above" if matrix.expected_count >= thresh
                                  else "below"),
                        would_flip_at=float(thresh),
                        gate_role=role,
                    ))
                    break
    if probe.candidates_filtered == 0:
        probe.notes.append("No component sets evaluated. G7 calibration unavailable.")
    return probe
