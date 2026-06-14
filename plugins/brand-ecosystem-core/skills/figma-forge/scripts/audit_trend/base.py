"""figma-forge audit-trend — base data shapes.

Compute a longitudinal calibration drift analysis over **N** schema-v1.0
audit reports. While ``audit-diff`` (v0.3.1-alpha.1) compares exactly
two reports, ``audit-trend`` operates on a window of arbitrarily many
reports — typically the rolling 30-day or 90-day audit history of a
single design system bundle — and surfaces:

* **Score trend** — mean, standard deviation, simple-linear-regression
  slope (per audit, per day)
* **Band frequency** — distribution of EXEMPLARY / EXCELLENT / STRONG /
  ACCEPTABLE / WEAK / FAILING bands across the window
* **Per-gate regression frequency** — how often each gate failed across
  the window (proportional to total observations)
* **Mean time to fix (MTTF)** — average number of audits between a
  gate's FAIL appearance and its return to PASS (computed only when a
  fix actually occurred within the window)
* **Calibration drift index (CDI)** — relative standard deviation of
  the score series, σ/μ; flags noisy or unstable calibration

Closes the "v0.3.1 GA" milestone item: trend analysis dashboard
follow-up to ``audit-diff``.

The output schema is **frozen at v1.0** from this release; additive
fields allowed in v1.x, breaking changes deferred to v2.0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

BandLabel = Literal["EXEMPLARY", "EXCELLENT", "STRONG", "ACCEPTABLE", "WEAK", "FAILING"]


# Band ordinal — higher = better. Used for shift detection and per-band counts.
_BAND_ORDINAL: dict[str, int] = {
    "EXEMPLARY":  6,
    "EXCELLENT":  5,
    "STRONG":     4,
    "ACCEPTABLE": 3,
    "WEAK":       2,
    "FAILING":    1,
}


@dataclass
class TimePoint:
    """A single audit observation in the time series."""

    path: str
    timestamp: str          # ISO-8601 UTC
    build_version: str
    score: float
    band: str
    summary: dict[str, int]
    gates: dict[int, dict]  # gate_id → raw payload

    @classmethod
    def from_payload(cls, payload: dict, *, path: str) -> "TimePoint":
        gates = {int(g["id"]): g for g in payload.get("gates", [])}
        return cls(
            path=path,
            timestamp=str(payload.get("audit_timestamp", "")),
            build_version=str(payload.get("build_version", "")),
            score=float(payload.get("score", 0.0)),
            band=str(payload.get("band", "FAILING")),
            summary=dict(payload.get("summary", {})),
            gates=gates,
        )

    def band_ordinal(self) -> int:
        return _BAND_ORDINAL.get(self.band.upper(), 0)


@dataclass
class GateTimeSeries:
    """Per-gate behavior across the audit window."""

    gate_id: int
    name: str
    observations: int = 0          # how many audits saw this gate
    fail_count: int = 0            # how many audits had it FAIL
    pass_count: int = 0
    skip_count: int = 0
    fail_ratio: float = 0.0        # fail_count / observations
    pass_to_fail_transitions: int = 0
    fail_to_pass_transitions: int = 0
    mean_time_to_fix: float | None = None  # in number of audits

    @property
    def stability(self) -> Literal["stable", "flapping", "regressing", "improving", "absent"]:
        """Quick health label for the gate over the window."""
        if self.observations == 0:
            return "absent"
        if self.pass_to_fail_transitions == 0 and self.fail_to_pass_transitions == 0:
            return "stable"
        if self.pass_to_fail_transitions > self.fail_to_pass_transitions:
            return "regressing"
        if self.fail_to_pass_transitions > self.pass_to_fail_transitions:
            return "improving"
        return "flapping"


@dataclass
class TrendReport:
    """End-to-end calibration trend outcome."""

    points: list[TimePoint] = field(default_factory=list)
    gates: dict[int, GateTimeSeries] = field(default_factory=dict)

    # Score series statistics
    score_mean: float = 0.0
    score_stdev: float = 0.0
    score_min: float = 0.0
    score_max: float = 0.0
    score_slope_per_audit: float = 0.0  # simple linear regression slope
    score_slope_per_day: float = 0.0
    calibration_drift_index: float = 0.0  # σ/μ; 0 = perfectly stable

    # Band frequency
    band_frequency: dict[str, int] = field(default_factory=dict)

    # Window
    window_start: str = ""
    window_end: str = ""
    window_days: float = 0.0
    audit_count: int = 0

    @property
    def regressing_gates(self) -> list[GateTimeSeries]:
        return [g for g in self.gates.values() if g.stability == "regressing"]

    @property
    def improving_gates(self) -> list[GateTimeSeries]:
        return [g for g in self.gates.values() if g.stability == "improving"]

    @property
    def flapping_gates(self) -> list[GateTimeSeries]:
        return [g for g in self.gates.values() if g.stability == "flapping"]
