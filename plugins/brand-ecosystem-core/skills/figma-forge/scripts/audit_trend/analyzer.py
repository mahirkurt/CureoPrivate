"""audit_trend analyzer — load audit reports, build time series, compute drift.

Constructs a :class:`TrendReport` from a list of schema-v1.0 audit JSON
paths. The analyzer is **window-agnostic**: it processes whatever
reports the caller provides. Date-range filtering (e.g. "last 30 days")
is the CLI's responsibility — the analyzer just sees an ordered list.

Statistical primitives implemented with only the Python standard
library; no numpy / pandas dependency to keep the skill bundle
embeddable in any environment.
"""

from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .base import GateTimeSeries, TimePoint, TrendReport


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_points(paths: list[Path]) -> list[TimePoint]:
    """Load each audit report at ``paths`` into a :class:`TimePoint`.

    Sorts the result by ISO-8601 timestamp ascending. Skips files that
    fail to parse, raising ``ValueError`` only for schema-version
    mismatches (those are *user* errors, not data hygiene).
    """
    points: list[TimePoint] = []
    for p in paths:
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # silently skip malformed; trend doesn't need every point
        schema = payload.get("schema_version")
        if schema != "1.0":
            raise ValueError(
                f"Unsupported audit schema {schema!r} at {p}. "
                f"Expected 1.0; re-run publish_audit with --output-format json."
            )
        points.append(TimePoint.from_payload(payload, path=str(p)))
    # Sort chronologically (timestamp lexicographic; ISO-8601 is sort-safe)
    points.sort(key=lambda pt: pt.timestamp)
    return points


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(points: list[TimePoint]) -> TrendReport:
    """Compute trend statistics and per-gate series from a sorted point list.

    Returns an empty-but-well-formed :class:`TrendReport` when
    ``points`` is empty, so callers can render a placeholder dashboard
    without special-casing.
    """
    report = TrendReport(points=list(points), audit_count=len(points))
    if not points:
        return report

    # Window bounds + day span
    report.window_start = points[0].timestamp
    report.window_end = points[-1].timestamp
    report.window_days = _days_between(points[0].timestamp, points[-1].timestamp)

    # Score series statistics
    scores = [p.score for p in points]
    report.score_mean = round(statistics.fmean(scores), 3)
    report.score_min = min(scores)
    report.score_max = max(scores)
    report.score_stdev = round(statistics.pstdev(scores), 3) if len(scores) > 1 else 0.0
    report.calibration_drift_index = (
        round(report.score_stdev / report.score_mean, 4)
        if report.score_mean > 0 else 0.0
    )

    # Simple linear regression (slope per audit and per day)
    report.score_slope_per_audit = _slope(list(range(len(scores))), scores)
    if report.window_days > 0:
        days = [_days_between(points[0].timestamp, p.timestamp) for p in points]
        report.score_slope_per_day = _slope(days, scores)

    # Band frequency
    band_freq: dict[str, int] = {}
    for p in points:
        band_freq[p.band] = band_freq.get(p.band, 0) + 1
    report.band_frequency = band_freq

    # Per-gate series
    report.gates = _build_gate_series(points)
    return report


# ---------------------------------------------------------------------------
# Per-gate analysis
# ---------------------------------------------------------------------------

def _build_gate_series(points: list[TimePoint]) -> dict[int, GateTimeSeries]:
    """Roll up each gate's behavior across the window."""
    all_ids: set[int] = set()
    for p in points:
        all_ids |= set(p.gates.keys())

    series: dict[int, GateTimeSeries] = {}
    for gate_id in sorted(all_ids):
        name = ""
        observations = 0
        fail = passed = skip = 0
        p2f = f2p = 0
        # MTTF: track current-fail-streak length when transitioning F→P
        fix_durations: list[int] = []
        current_fail_streak: int | None = None
        prev_result: str | None = None

        for pt in points:
            gate = pt.gates.get(gate_id)
            if gate is None:
                # Gate absent in this audit; doesn't break a streak (treat as no-op)
                continue
            observations += 1
            name = str(gate.get("name") or name)
            result = str(gate.get("result", "")).upper()

            if result == "FAIL":
                fail += 1
                if current_fail_streak is None:
                    current_fail_streak = 1
                else:
                    current_fail_streak += 1
            elif result == "PASS":
                passed += 1
                if current_fail_streak is not None:
                    # F → P transition closes the fail streak; record duration
                    fix_durations.append(current_fail_streak)
                    current_fail_streak = None
            elif result == "SKIP":
                skip += 1

            # Transition counters
            if prev_result and result and prev_result != result:
                if prev_result == "PASS" and result == "FAIL":
                    p2f += 1
                elif prev_result == "FAIL" and result == "PASS":
                    f2p += 1
            prev_result = result

        ratio = (fail / observations) if observations else 0.0
        mttf = (statistics.fmean(fix_durations)) if fix_durations else None

        series[gate_id] = GateTimeSeries(
            gate_id=gate_id,
            name=name,
            observations=observations,
            fail_count=fail,
            pass_count=passed,
            skip_count=skip,
            fail_ratio=round(ratio, 3),
            pass_to_fail_transitions=p2f,
            fail_to_pass_transitions=f2p,
            mean_time_to_fix=round(mttf, 2) if mttf is not None else None,
        )
    return series


# ---------------------------------------------------------------------------
# Numeric primitives
# ---------------------------------------------------------------------------

def _slope(xs: list[float], ys: list[float]) -> float:
    """Simple linear-regression slope. Returns 0 for degenerate input."""
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    return round(num / den, 4) if den else 0.0


def _days_between(start: str, end: str) -> float:
    """Compute the day-delta between two ISO-8601 UTC timestamps.

    Returns ``0.0`` when either input fails to parse — drift analysis
    should still produce a coherent report even with malformed
    timestamps.
    """
    try:
        s = _parse_iso(start)
        e = _parse_iso(end)
        return round((e - s).total_seconds() / 86400.0, 3)
    except (ValueError, TypeError):
        return 0.0


def _parse_iso(s: str) -> datetime:
    """Parse a wide range of ISO-8601 timestamp shapes into UTC datetime."""
    # Trailing Z → +00:00 for fromisoformat compatibility (Python ≥ 3.11
    # accepts Z natively, but we want explicit safety).
    cleaned = s.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
