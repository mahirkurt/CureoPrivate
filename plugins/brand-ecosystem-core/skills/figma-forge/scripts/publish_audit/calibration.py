"""
Calibration framework — v0.2.1.

Heuristic gates (G7, G13, G14, G15) make graded decisions based on
geometric or textual signals with tunable thresholds. Synthetic
fixture tests verify these gates *work*; they cannot verify the
thresholds are calibrated against real-world libraries.

This module provides the data structures and decorator registry for
gates to optionally emit a ``CalibrationProbe`` during an audit run.
When the CLI is invoked with ``--calibration-mode``, the probes are
serialized to a JSON sidecar that the skill maintainer can analyze
offline (see ``tools/calibration_analyzer.py``).

Design properties:

* **Opt-in.** Calibration probes only run when the operator passes
  ``--calibration-mode``. No telemetry is collected during normal
  audit runs.
* **Local-only.** The sidecar JSON is written to the operator's
  filesystem. Nothing is transmitted off-device.
* **Pluggable.** Gates register a calibrator via ``@register_calibrator(N)``.
  The decorator is independent of ``@register_gate(N)`` — a gate may
  expose both a checker and a calibrator, only a checker, or only a
  calibrator (for future probe-only diagnostics).
* **Privacy-conscious.** Raw node IDs and component names are captured
  by the probe, but the companion ``tools/anonymize_calibration.py``
  script strips identifiers before the file is shared.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Iterator


__all__ = [
    "BoundaryDecision",
    "CalibrationProbe",
    "CalibrationReport",
    "register_calibrator",
    "get_calibrator",
    "has_calibrator",
    "run_calibrator",
    "run_all_calibrators",
    "implemented_calibrator_count",
    "serialize_report",
]


# ----------------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------------

@dataclass
class BoundaryDecision:
    """One graded decision that fell within the boundary band of a threshold.

    Boundary decisions are the most valuable calibration signal: they
    show which classifications would have flipped if the threshold were
    moved by 1-2 units. A library with many boundary decisions on a
    given threshold is one where that threshold is poorly tuned.

    Attributes:
        node_id: Figma node identifier (anonymizable).
        node_name: Human-readable node name (anonymizable).
        feature_name: Which threshold the decision is near (e.g. "squareness").
        feature_value: The observed feature value (e.g. 2 px).
        threshold: The current threshold value (e.g. 2).
        verdict: What the gate decided ("pass" / "fail" / "icon" / "decorative" / etc.)
        would_flip_at: Threshold value that would change the verdict.
        gate_role: Optional registry role context ("foundations" / "components" / ...).
    """
    node_id: str
    node_name: str
    feature_name: str
    feature_value: float
    threshold: float
    verdict: str
    would_flip_at: float
    gate_role: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly dict for sidecar serialization."""
        return asdict(self)


@dataclass
class CalibrationProbe:
    """Per-gate calibration metadata captured during an audit run.

    Designed to be both compact (a 50-component library should produce
    <50 KB of probe data per gate) and informative (every boundary
    decision and feature histogram bucket is preserved).
    """
    gate_id: int
    nodes_scanned: int = 0
    candidates_filtered: int = 0
    decisions_made: int = 0
    boundary_decisions: list[BoundaryDecision] = field(default_factory=list)
    feature_distribution: dict[str, dict[str, int]] = field(default_factory=dict)
    skip_reasons: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def add_boundary(self, decision: BoundaryDecision) -> None:
        """Append a boundary decision; idempotent on duplicate node_ids."""
        for existing in self.boundary_decisions:
            if (existing.node_id == decision.node_id
                    and existing.feature_name == decision.feature_name):
                return
        self.boundary_decisions.append(decision)

    def increment_histogram(self, feature: str, bucket: str) -> None:
        """Bump the count for ``feature[bucket]`` by one; create entries as needed."""
        if feature not in self.feature_distribution:
            self.feature_distribution[feature] = {}
        self.feature_distribution[feature][bucket] = (
            self.feature_distribution[feature].get(bucket, 0) + 1
        )

    def increment_skip(self, reason: str) -> None:
        """Bump the count for ``skip_reasons[reason]`` by one."""
        self.skip_reasons[reason] = self.skip_reasons.get(reason, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly dict for sidecar serialization."""
        return {
            "gate_id": self.gate_id,
            "nodes_scanned": self.nodes_scanned,
            "candidates_filtered": self.candidates_filtered,
            "decisions_made": self.decisions_made,
            "boundary_decisions": [d.to_dict() for d in self.boundary_decisions],
            "feature_distribution": self.feature_distribution,
            "skip_reasons": self.skip_reasons,
            "notes": self.notes,
        }


@dataclass
class CalibrationReport:
    """Top-level container serialized as the sidecar JSON.

    Aggregates per-gate probes with library-level context (DS name,
    version, file roles) so the offline analyzer can compare runs
    across libraries.
    """
    schema_version: str = "1.0"
    audit_run: str = ""               # ISO-8601 timestamp
    figma_forge_version: str = ""
    library: dict[str, Any] = field(default_factory=dict)
    totals: dict[str, int] = field(default_factory=dict)
    probes: dict[int, CalibrationProbe] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly dict for sidecar serialization."""
        return {
            "schema_version": self.schema_version,
            "audit_run": self.audit_run,
            "figma_forge_version": self.figma_forge_version,
            "library": self.library,
            "totals": self.totals,
            "probes": {str(gid): probe.to_dict()
                       for gid, probe in self.probes.items()},
        }


# ----------------------------------------------------------------------------
# Calibrator registry — parallel to gates_registry._CHECKERS
# ----------------------------------------------------------------------------
#
# A calibrator is a callable ``(ctx) -> CalibrationProbe`` registered
# under a gate ID. Calibrators are optional — a gate may register a
# checker without a calibrator. The CLI only invokes calibrators when
# ``--calibration-mode`` is set.

# The actual import of MultiFileFigmaContext is deferred to avoid a
# circular import; calibrators are stored as opaque callables.
Calibrator = Callable[[Any], CalibrationProbe]

_CALIBRATORS: dict[int, Calibrator] = {}


def register_calibrator(gate_id: int) -> Callable[[Calibrator], Calibrator]:
    """Decorator: register ``fn`` as the calibrator for ``gate_id``.

    Mirrors ``@register_gate`` in shape but lives in its own registry
    so a gate can independently choose whether to expose calibration.
    """
    def decorator(fn: Calibrator) -> Calibrator:
        """Bind ``fn`` to the enclosing gate_id in the calibrator registry."""
        if gate_id in _CALIBRATORS:
            raise RuntimeError(f"calibrator for gate {gate_id} already registered")
        _CALIBRATORS[gate_id] = fn
        return fn
    return decorator


def has_calibrator(gate_id: int) -> bool:
    """Return True iff a calibrator has been registered for ``gate_id``."""
    return gate_id in _CALIBRATORS


def get_calibrator(gate_id: int) -> Calibrator | None:
    """Return the registered calibrator for ``gate_id``, or None."""
    return _CALIBRATORS.get(gate_id)


def run_calibrator(gate_id: int, ctx: Any) -> CalibrationProbe | None:
    """Execute the calibrator for ``gate_id``; return None if absent."""
    fn = _CALIBRATORS.get(gate_id)
    if fn is None:
        return None
    return fn(ctx)


def run_all_calibrators(ctx: Any) -> dict[int, CalibrationProbe]:
    """Execute every registered calibrator; return {gate_id: probe}."""
    return {gid: fn(ctx) for gid, fn in sorted(_CALIBRATORS.items())}


def implemented_calibrator_count() -> int:
    """How many gates have registered calibrators."""
    return len(_CALIBRATORS)


# ----------------------------------------------------------------------------
# Sidecar I/O
# ----------------------------------------------------------------------------

def serialize_report(report: CalibrationReport, output_path: str | Path) -> Path:
    """Write a CalibrationReport to ``output_path`` as pretty-printed JSON.

    Returns the path written, for caller logging/verification.
    """
    path = Path(output_path)
    payload = report.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    return path


# ----------------------------------------------------------------------------
# Histogram bucketing helpers — useful for calibrators
# ----------------------------------------------------------------------------

def bucket_canonical(value: float, canonical: tuple[int, ...],
                      tolerance: int) -> str:
    """Place ``value`` in a labelled bucket relative to canonical sizes.

    Used by G14/G15: width and height get bucketed into "16", "20", "24",
    "32", "48" (within ±tolerance) or labelled as the range they fall in.
    """
    for c in canonical:
        if abs(value - c) <= tolerance:
            return str(c)
    if value < canonical[0]:
        return f"<{canonical[0]}"
    if value > canonical[-1]:
        return f">{canonical[-1]}"
    # Between two canonical sizes
    for lo, hi in zip(canonical, canonical[1:]):
        if lo < value < hi:
            return f"{lo}-{hi}"
    return "unknown"


def bucket_linear(value: float, *, bin_size: int) -> str:
    """Place ``value`` in a linear bucket of width ``bin_size``."""
    lo = int(value // bin_size) * bin_size
    return f"{lo}-{lo + bin_size - 1}"


def iter_within_band(value: float, threshold: float, *,
                      band: float) -> Iterator[float]:
    """Yield the threshold value if ``value`` is within ``band`` of it.

    Used by calibrators to detect boundary decisions: a decision is a
    boundary when |value - threshold| <= band.
    """
    if abs(value - threshold) <= band:
        yield threshold
