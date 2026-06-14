"""audit-diff comparator — classify per-gate transitions.

The classification logic encodes a **severity-aware ordering** over
result statuses. The base ordinal (higher = healthier) is:

* ``PASS``    → 5
* ``N_A``     → 4    (gate didn't apply; neutral)
* ``SKIP``    → 3    (gate skipped explicitly; neutral)
* ``FAIL``    → varies by severity (error: 0, warn: 1, info: 2)
* ``MISSING`` → 0    (gate not present in current report — treat as regression)

Sample-level diffs are computed when both snapshots provide ``samples``
arrays for the gate. The diff is set-based on the sample message
strings; we don't try to parse structured fields out of the human-
readable failure lines.
"""

from __future__ import annotations

import json
from pathlib import Path

from .base import AuditSnapshot, DiffReport, GateTransition


# Result ordinals — higher = healthier
_RESULT_BASE = {
    "PASS":    5,
    "N_A":     4,
    "SKIP":    3,
    "FAIL":    None,  # computed from severity
    "MISSING": 0,
}

# Severity penalty applied to FAIL
_SEVERITY_PENALTY = {
    "error": 0,
    "warn":  1,
    "info":  2,
}


def _result_ordinal(result: str, severity: str) -> int:
    base = _RESULT_BASE.get(result.upper())
    if base is None:  # FAIL
        return _SEVERITY_PENALTY.get(severity.lower(), 0)
    return base


def load_snapshot(path: Path) -> AuditSnapshot:
    """Read a schema-v1.0 audit JSON and convert to AuditSnapshot."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = payload.get("schema_version")
    if schema != "1.0":
        raise ValueError(
            f"Unsupported audit schema version: {schema!r} (expected 1.0). "
            f"Re-run publish_audit with --output-format json."
        )
    return AuditSnapshot.from_payload(payload, path=str(path))


def compare(baseline: AuditSnapshot, current: AuditSnapshot) -> DiffReport:
    """Compute a DiffReport over two snapshots.

    Iterates the union of gate ids; classifies each transition;
    extracts sample-level resolved / introduced lines when both sides
    have samples.
    """
    report = DiffReport(baseline=baseline, current=current)

    all_ids = sorted(set(baseline.gates) | set(current.gates))
    for gate_id in all_ids:
        b_gate = baseline.gates.get(gate_id)
        c_gate = current.gates.get(gate_id)

        if b_gate is None and c_gate is not None:
            report.transitions.append(_transition_for_new_gate(gate_id, c_gate))
            continue
        if c_gate is None and b_gate is not None:
            report.transitions.append(_transition_for_removed_gate(gate_id, b_gate))
            continue
        # Both present
        report.transitions.append(_transition_for_existing_gate(gate_id, b_gate, c_gate))

    return report


# ---------------------------------------------------------------------------
# Per-case builders
# ---------------------------------------------------------------------------

def _transition_for_existing_gate(
    gate_id: int, b_gate: dict, c_gate: dict
) -> GateTransition:
    b_result = str(b_gate.get("result", "MISSING")).upper()
    c_result = str(c_gate.get("result", "MISSING")).upper()
    b_sev = str(b_gate.get("severity", "info")).lower()
    c_sev = str(c_gate.get("severity", "info")).lower()

    b_ord = _result_ordinal(b_result, b_sev)
    c_ord = _result_ordinal(c_result, c_sev)

    if c_ord < b_ord:
        classification = "regression"
    elif c_ord > b_ord:
        classification = "improvement"
    else:
        classification = "no_change"

    b_samples = _samples_of(b_gate)
    c_samples = _samples_of(c_gate)

    return GateTransition(
        gate_id=gate_id,
        name=str(c_gate.get("name") or b_gate.get("name") or ""),
        severity_baseline=b_sev,
        severity_current=c_sev,
        result_baseline=b_result,  # type: ignore[arg-type]
        result_current=c_result,   # type: ignore[arg-type]
        checked_baseline=int(b_gate.get("checked_count", 0) or 0),
        checked_current=int(c_gate.get("checked_count", 0) or 0),
        classification=classification,  # type: ignore[arg-type]
        samples_resolved=sorted(b_samples - c_samples),
        samples_introduced=sorted(c_samples - b_samples),
    )


def _transition_for_new_gate(gate_id: int, gate: dict) -> GateTransition:
    return GateTransition(
        gate_id=gate_id,
        name=str(gate.get("name", "")),
        severity_baseline="info",
        severity_current=str(gate.get("severity", "info")).lower(),
        result_baseline="MISSING",
        result_current=str(gate.get("result", "MISSING")).upper(),  # type: ignore[arg-type]
        checked_baseline=0,
        checked_current=int(gate.get("checked_count", 0) or 0),
        classification="new",
        samples_resolved=[],
        samples_introduced=sorted(_samples_of(gate)),
    )


def _transition_for_removed_gate(gate_id: int, gate: dict) -> GateTransition:
    return GateTransition(
        gate_id=gate_id,
        name=str(gate.get("name", "")),
        severity_baseline=str(gate.get("severity", "info")).lower(),
        severity_current="info",
        result_baseline=str(gate.get("result", "MISSING")).upper(),  # type: ignore[arg-type]
        result_current="MISSING",
        checked_baseline=int(gate.get("checked_count", 0) or 0),
        checked_current=0,
        classification="removed",
        samples_resolved=sorted(_samples_of(gate)),
        samples_introduced=[],
    )


def _samples_of(gate: dict) -> set[str]:
    """Extract the set of sample message strings from a gate payload."""
    samples = gate.get("samples") or []
    out: set[str] = set()
    for s in samples:
        if isinstance(s, dict) and "message" in s:
            out.add(str(s["message"]).strip())
        elif isinstance(s, str):
            out.add(s.strip())
    return out
