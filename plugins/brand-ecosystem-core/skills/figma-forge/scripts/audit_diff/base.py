"""figma-forge audit-diff — base data shapes.

Computes a delta between two schema-v1.0 audit reports produced by
``publish_audit.py --output-format json``. The delta surfaces:

* **Per-gate transitions** — PASS → FAIL (regression), FAIL → PASS
  (improvement), check count drift, severity shifts
* **Score delta** — 0..10 numeric difference + band shift label
* **Sample-level changes** — newly-introduced failure samples,
  resolved failure samples (only available when both reports carry
  samples for the same gate)

The diff is the canonical input for **calibration loops** — automated
CI gates that fail a build when a previously-passing gate regresses,
even if the overall score nominally still passes. This closes Düstur
build lesson L10 (calibration delta).

Schema (frozen at v1.0 from this release):

::

    {
      "schema_version": "1.0",
      "diff_timestamp": "<ISO-8601 UTC>",
      "baseline": {"path": "...", "timestamp": "...", "score": F, "band": "..."},
      "current":  {"path": "...", "timestamp": "...", "score": F, "band": "..."},
      "score_delta": F,                  # current − baseline
      "band_shift": "stable|improved|regressed",
      "summary": {
        "regressions":  N,                # any gate moving toward failure
        "improvements": N,                # any gate moving toward passing
        "no_change":    N,                # gate result unchanged
        "new_gates":    N,                # gate only in current
        "removed_gates": N                # gate only in baseline
      },
      "transitions": [
        {
          "gate_id": INT,
          "name": "...",
          "severity_baseline": "error|warn|info",
          "severity_current":  "error|warn|info",
          "result_baseline":   "PASS|FAIL|SKIP|N_A|MISSING",
          "result_current":    "PASS|FAIL|SKIP|N_A|MISSING",
          "checked_baseline":  INT,
          "checked_current":   INT,
          "classification":    "regression|improvement|no_change|new|removed",
          "samples_resolved":  ["..."],   # in baseline, not in current
          "samples_introduced":["..."]    # in current, not in baseline
        },
        ...
      ]
    }
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Classification = Literal["regression", "improvement", "no_change", "new", "removed"]
BandShift = Literal["stable", "improved", "regressed"]
ResultStatus = Literal["PASS", "FAIL", "SKIP", "N_A", "MISSING"]


# Band ordinal — higher = better. Used for shift detection.
_BAND_ORDINAL = {
    "EXEMPLARY":  6,
    "EXCELLENT":  5,
    "STRONG":     4,
    "ACCEPTABLE": 3,
    "WEAK":       2,
    "FAILING":    1,
}


@dataclass
class AuditSnapshot:
    """Lightweight view of a parsed audit report."""

    path: str
    timestamp: str
    build_version: str
    score: float
    band: str
    summary: dict[str, int]
    gates: dict[int, dict]  # gate_id → raw gate payload dict

    @classmethod
    def from_payload(cls, payload: dict, *, path: str) -> "AuditSnapshot":
        gates = {int(g["id"]): g for g in payload.get("gates", [])}
        return cls(
            path=path,
            timestamp=payload.get("audit_timestamp", ""),
            build_version=payload.get("build_version", ""),
            score=float(payload.get("score", 0.0)),
            band=str(payload.get("band", "FAILING")),
            summary=dict(payload.get("summary", {})),
            gates=gates,
        )


@dataclass
class GateTransition:
    """A single gate's baseline-to-current change."""

    gate_id: int
    name: str
    severity_baseline: str
    severity_current: str
    result_baseline: ResultStatus
    result_current: ResultStatus
    checked_baseline: int
    checked_current: int
    classification: Classification
    samples_resolved: list[str] = field(default_factory=list)
    samples_introduced: list[str] = field(default_factory=list)

    @property
    def is_regression(self) -> bool:
        return self.classification == "regression"

    @property
    def is_improvement(self) -> bool:
        return self.classification == "improvement"


@dataclass
class DiffReport:
    """Aggregated baseline-vs-current outcome."""

    baseline: AuditSnapshot
    current: AuditSnapshot
    transitions: list[GateTransition] = field(default_factory=list)

    @property
    def score_delta(self) -> float:
        return round(self.current.score - self.baseline.score, 2)

    @property
    def band_shift(self) -> BandShift:
        b = _BAND_ORDINAL.get(self.baseline.band.upper(), 0)
        c = _BAND_ORDINAL.get(self.current.band.upper(), 0)
        if c > b:
            return "improved"
        if c < b:
            return "regressed"
        return "stable"

    @property
    def regressions(self) -> list[GateTransition]:
        return [t for t in self.transitions if t.is_regression]

    @property
    def improvements(self) -> list[GateTransition]:
        return [t for t in self.transitions if t.is_improvement]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "regressions":   sum(1 for t in self.transitions if t.classification == "regression"),
            "improvements":  sum(1 for t in self.transitions if t.classification == "improvement"),
            "no_change":     sum(1 for t in self.transitions if t.classification == "no_change"),
            "new_gates":     sum(1 for t in self.transitions if t.classification == "new"),
            "removed_gates": sum(1 for t in self.transitions if t.classification == "removed"),
        }
