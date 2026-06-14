"""figma-forge audit-trend package — longitudinal calibration analysis.

Compute statistics over **N** schema-v1.0 audit reports (typically a
30-day or 90-day rolling window):

* Score series — mean, stdev, min/max, slope (per-audit, per-day)
* Calibration Drift Index (CDI) = σ/μ — relative score volatility
* Band frequency distribution
* Per-gate stability (stable / improving / regressing / flapping / absent)
* Mean time to fix (MTTF) — audits between FAIL appearance and return to PASS

Public API:
    TimePoint, GateTimeSeries, TrendReport
    load_points(paths), analyze(points)
    format_trend_json(report), format_trend_markdown(report), format_trend_html(report)
"""

from .analyzer import analyze, load_points
from .base import GateTimeSeries, TimePoint, TrendReport
from .reporting import format_trend_html, format_trend_json, format_trend_markdown

__version__ = "0.3.1"

__all__ = [
    "GateTimeSeries",
    "TimePoint",
    "TrendReport",
    "analyze",
    "format_trend_html",
    "format_trend_json",
    "format_trend_markdown",
    "load_points",
    "__version__",
]
