"""figma-forge — Design-System-to-Figma Library Operationalization Protocol.

Stable public API surface, v1.0.0.

This package is the **single entry point** for downstream code that
embeds figma-forge as a library. All identifiers exported here are
covered by the v1.x API stability contract — see ``api/STABILITY.md``
in the skill bundle for the full guarantee.

Usage::

    import figma_forge as ff

    # Audit comparison (calibration delta)
    baseline = ff.load_audit_snapshot("baseline.json")
    current  = ff.load_audit_snapshot("current.json")
    diff     = ff.compare_audits(baseline, current)
    print(ff.format_diff_markdown(diff))

    # Longitudinal trend
    points = ff.load_audit_points(["a.json", "b.json", "c.json"])
    report = ff.analyze_trend(points)
    print(ff.format_trend_html(report))

    # Supply-chain manifest
    manifest = ff.build_bundle_manifest(library_dir)
    ff.sign_manifest(manifest, identity="release-bot@example.com")

    # Static lint
    results = ff.run_static_lint(library_dir)

Stability tiers (see ``api/STABILITY.md`` for the full contract):

    - **stable** — covered by SemVer; breaking changes are a major
      version bump only.
    - **experimental** — may evolve in minor versions; marked with
      a leading underscore or an explicit deprecation warning.
    - **internal** — packages prefixed with ``_``; never use.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Version constants (canonical source: VERSION file at repo root)
# ---------------------------------------------------------------------------

from pathlib import Path as _Path

_VERSION_FILE = _Path(__file__).resolve().parent.parent.parent / "VERSION"
try:
    __version__ = _VERSION_FILE.read_text(encoding="utf-8").strip()
except OSError:
    __version__ = "1.0.0"

API_VERSION = "1.0"
"""The public-API contract version. Locked at 1.0 in v1.0.0.

The figma-forge public API follows SemVer. Identifiers re-exported
here remain stable across all v1.x minor and patch releases.
"""


# ---------------------------------------------------------------------------
# Audit comparison (calibration delta) — Mode 11 AUDIT_DIFF
# ---------------------------------------------------------------------------

from audit_diff.base import (
    AuditSnapshot,
    DiffReport,
    GateTransition,
)
from audit_diff.comparator import (
    compare as compare_audits,
    load_snapshot as load_audit_snapshot,
)
from audit_diff.reporting import (
    format_diff_json,
    format_diff_markdown,
)


# ---------------------------------------------------------------------------
# Audit trend (longitudinal drift) — Mode 12 AUDIT_TREND
# ---------------------------------------------------------------------------

from audit_trend.base import (
    GateTimeSeries,
    TimePoint,
    TrendReport,
)
from audit_trend.analyzer import (
    analyze as analyze_trend,
    load_points as load_audit_points,
)
from audit_trend.reporting import (
    format_trend_html,
    format_trend_json,
    format_trend_markdown,
)


# ---------------------------------------------------------------------------
# Static lint — Mode 7 PUBLISH_AUDIT (--static-only flag)
# ---------------------------------------------------------------------------

from publish_audit.static_lint import (
    run_static_lint,
)


# ---------------------------------------------------------------------------
# Auto-remediate strategies — Mode 8 AUTO_REMEDIATE
# ---------------------------------------------------------------------------

from auto_remediate.base import (
    RemediationAction,
    RemediationContext,
)
from auto_remediate.runner import (
    RunnerOptions as RemediationOptions,
    run as run_remediation,
)


# ---------------------------------------------------------------------------
# Transport layer (v1.1.0-alpha — append-only addition to the v1.0 contract)
# ---------------------------------------------------------------------------

from .transport.protocol import TransportAdapter
from .transport.errors import (
    AuthenticationError,
    CapabilityUnsupportedError,
    TransportError,
)
from .transport.stub import StubTransport
from .transport.plugin_capture import PluginCaptureTransport
from .transport.rest import RestTransport
from .transport.mcp_cursor import McpCursorTransport
from .transport.backoff import BackoffPolicy
from .transport.batch_policy import BatchPolicy
from .transport.adaptive_concurrency import AdaptiveConcurrency, ConcurrencyObservation
from .transport.observation_log import ObservationLog
from .transport.concurrency import ConcurrencyReport, check_concurrency
from .transport.plan_validation import PlanValidationReport, PriorState, validate_mcp_plan
from .transport.plan_runner import PlanRunner, PlanRunResult, StepResult, DispatchResponse
from .transport.plan_graph import plan_execution_layers
from .transport.router import TransportRouter
from .pipeline import PipelineResult, run_pipeline


# ---------------------------------------------------------------------------
# Public API surface — explicit ``__all__`` for re-export contract
# ---------------------------------------------------------------------------

__all__ = [
    # Version / contract
    "__version__",
    "API_VERSION",
    # Audit-diff (Mode 11)
    "AuditSnapshot",
    "DiffReport",
    "GateTransition",
    "compare_audits",
    "load_audit_snapshot",
    "format_diff_json",
    "format_diff_markdown",
    # Audit-trend (Mode 12)
    "GateTimeSeries",
    "TimePoint",
    "TrendReport",
    "analyze_trend",
    "load_audit_points",
    "format_trend_json",
    "format_trend_markdown",
    "format_trend_html",
    # Static lint (Mode 7)
    "run_static_lint",
    # Auto-remediate (Mode 8)
    "RemediationAction",
    "RemediationContext",
    "RemediationOptions",
    "run_remediation",
    # Transport layer (v1.1.0-alpha)
    "TransportAdapter",
    "TransportError",
    "AuthenticationError",
    "CapabilityUnsupportedError",
    "StubTransport",
    "PluginCaptureTransport",
    "RestTransport",
    "McpCursorTransport",
    "BackoffPolicy",
    "BatchPolicy",
    "AdaptiveConcurrency",
    "ConcurrencyObservation",
    "ObservationLog",
    "ConcurrencyReport",
    "check_concurrency",
    "PlanValidationReport",
    "PriorState",
    "validate_mcp_plan",
    "PlanRunner",
    "PlanRunResult",
    "StepResult",
    "DispatchResponse",
    "plan_execution_layers",
    "TransportRouter",
    "PipelineResult",
    "run_pipeline",
]


# ---------------------------------------------------------------------------
# Lazy-loaded supply-chain submodule (heavy deps: sigstore, pyOpenSSL)
# ---------------------------------------------------------------------------

def __getattr__(name: str):
    """PEP 562 lazy attribute loader for supply-chain helpers.

    The supply-chain module (``figma_forge.supply_chain``) is imported
    lazily so that downstream users who don't sign or verify don't pay
    the ``sigstore`` and ``pyOpenSSL`` import cost. Triggered on first
    access::

        import figma_forge as ff
        ff.sign_manifest(...)   # loads supply_chain on first call

    Raises ``AttributeError`` for unknown attributes, per PEP 562.
    """
    if name in {
        "build_bundle_manifest",
        "sign_manifest",
        "verify_manifest",
        "BundleManifest",
        "ProvenanceAttestation",
    }:
        from . import supply_chain as _sc
        attr = getattr(_sc, name)
        globals()[name] = attr  # cache for subsequent access
        return attr
    raise AttributeError(f"module 'figma_forge' has no attribute {name!r}")
