"""figma-forge audit-diff package — calibration delta computation.

Compare two schema-v1.0 audit reports produced by
``publish_audit.py --output-format json`` and surface:

* Per-gate transitions (PASS → FAIL regressions, FAIL → PASS
  improvements, severity shifts, count drift)
* Score delta and band shift
* Sample-level resolved / introduced failures

Closes Düstur build lesson L10 (calibration delta).

Public API:
    AuditSnapshot, GateTransition, DiffReport
    load_snapshot(path), compare(baseline, current)
    format_diff_json(report), format_diff_markdown(report)
"""

from .base import AuditSnapshot, DiffReport, GateTransition
from .comparator import compare, load_snapshot
from .reporting import format_diff_json, format_diff_markdown

__version__ = "0.3.1"

__all__ = [
    "AuditSnapshot",
    "DiffReport",
    "GateTransition",
    "compare",
    "format_diff_json",
    "format_diff_markdown",
    "load_snapshot",
    "__version__",
]
