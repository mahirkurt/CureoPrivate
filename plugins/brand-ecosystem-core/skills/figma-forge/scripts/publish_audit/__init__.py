"""
figma-forge publish-audit framework, v0.2.0.

Public API:
    GATE_CATALOG              — list of all 19 Gate definitions
    GateResult, Gate          — result + definition data classes
    MultiFileFigmaContext     — audit context (single or multi-file)
    FigmaFile                 — per-file REST payload container
    LibraryRegistry           — multi-file library schema
    run_all_gates(ctx)        — execute every registered gate, returns list[GateResult]
    run_gate(gate_id, ctx)    — execute one gate
    format_report(results, …) — render a Markdown audit report

Example (single-file, v0.1.x-compatible):
    from scripts.publish_audit import MultiFileFigmaContext, run_all_gates, format_report

    ctx = MultiFileFigmaContext.single_file(file_key="abc123", pat=os.environ["FIGMA_PAT"])
    ctx.fetch_all()
    results = run_all_gates(ctx)
    report = format_report(results, file_label=ctx.primary.name, audit_target=ctx.primary.file_key)

Example (multi-file v0.2.0):
    from scripts.publish_audit import LibraryRegistry, MultiFileFigmaContext, run_all_gates

    registry = LibraryRegistry.from_path("library-registry.json")
    ctx = MultiFileFigmaContext.with_registry(registry, pat=os.environ["FIGMA_PAT"])
    ctx.fetch_all()
    results = run_all_gates(ctx)
"""

from __future__ import annotations

from .calibration import (
    BoundaryDecision,
    CalibrationProbe,
    CalibrationReport,
    has_calibrator,
    implemented_calibrator_count,
    run_all_calibrators,
    run_calibrator,
    serialize_report,
)
from .context import FigmaFile, MultiFileFigmaContext
from .gates_registry import (
    GATE_CATALOG,
    get_gate,
    has_checker,
    implemented_gate_count,
    run_all_gates,
    run_gate,
)
from .models import Gate, GateResult, Severity, GateStatus
from .registry import LibraryRegistry, FileInfo
from .reporting import format_report, format_json_report
from .static_lint import run_static_lint

__version__ = "0.2.1"

__all__ = [
    "BoundaryDecision",
    "CalibrationProbe",
    "CalibrationReport",
    "FigmaFile",
    "FileInfo",
    "Gate",
    "GATE_CATALOG",
    "GateResult",
    "GateStatus",
    "LibraryRegistry",
    "MultiFileFigmaContext",
    "Severity",
    "format_report",
    "format_json_report",
    "run_static_lint",
    "get_gate",
    "has_calibrator",
    "has_checker",
    "implemented_calibrator_count",
    "implemented_gate_count",
    "run_all_calibrators",
    "run_all_gates",
    "run_calibrator",
    "run_gate",
    "serialize_report",
]
