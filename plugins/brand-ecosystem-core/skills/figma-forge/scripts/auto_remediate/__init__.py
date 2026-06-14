"""figma-forge auto-remediation framework, v0.3.0.

Public API:
    GateFailure              — single FAIL row from a publish_audit JSON report
    RemediationAction        — proposed concrete fix
    RemediationContext       — runtime container (library_dir, calibration, locale)
    RemediationStrategy      — abstract base class for per-gate remediations
    RemediationResult        — end-to-end result aggregator
    register_strategy(N)     — decorator (mirrors @register_gate)
    get_strategy(N)          — registry lookup
    all_strategies()         — registry introspection

Composition:
    The auto-remediation pipeline runs in parallel to publish_audit. It
    never modifies the live Figma file directly; output is either a
    static-source diff (PR channel) or a Figma plugin TypeScript script
    (plugin channel) that an operator runs explicitly.

Quality guarantees:
    * Every strategy is independent (zero cross-strategy state)
    * Plans are idempotent (running twice = equivalent actions)
    * Output is deterministic (same inputs → byte-identical outputs)
    * Conservative defaults: ``--destructive`` opt-in required for deletions
"""

from .base import (
    Channel,
    GateFailure,
    RemediationAction,
    RemediationContext,
    RemediationResult,
    RemediationStrategy,
    Severity,
    UnsupportedChannelError,
    all_strategies,
    get_strategy,
    register_strategy,
)

# Import strategies so their @register_strategy decorators fire
from .strategies import (  # noqa: F401  (side-effect: register strategies)
    g02_composite_typography,
    g07_variant_matrix,
    g08_component_naming,
    g13_alias_resolution,
    g14_icons_are_components,
    g15_icon_size_grid,
    g17_code_connect_badges,
)

# Plugin channel writer (v0.3.0-beta)
from .plugin_writer import render_plugin_script, render_single_action  # noqa: F401

__version__ = "0.3.0-rc.1"

__all__ = [
    "Channel",
    "GateFailure",
    "RemediationAction",
    "RemediationContext",
    "RemediationResult",
    "RemediationStrategy",
    "Severity",
    "UnsupportedChannelError",
    "all_strategies",
    "get_strategy",
    "register_strategy",
    "render_plugin_script",
    "render_single_action",
    "__version__",
]
