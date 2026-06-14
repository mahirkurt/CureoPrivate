"""figma-forge auto-remediation framework — base abstractions.

Defines :class:`RemediationStrategy` ABC, :class:`RemediationAction` data
class, and :class:`RemediationContext` runtime container. Every strategy
inherits from :class:`RemediationStrategy` and registers itself via
:func:`register_strategy` decorator (mirrors the publish_audit
:func:`register_gate` pattern).

The auto-remediation lifecycle:

    1. CLI parses an audit report (Markdown → structured failures)
    2. For each FAIL gate, look up registered strategy
    3. Strategy.plan(failure, ctx) → list[RemediationAction]
    4. For each action: Strategy.render(action, channel) → str
    5. Output channel writes to disk (PR patch / plugin TS)

The framework is **side-effect-free** by default: rendering produces
strings; only the CLI's apply step touches the filesystem. This keeps
strategies pure-functional and trivially unit-testable.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, Sequence

Channel = Literal["pr", "plugin"]
Severity = Literal["CRITICAL", "MAJOR", "MINOR", "INFO"]


# ----------------------------------------------------------------------------
# Data classes — audit failure input + remediation action output
# ----------------------------------------------------------------------------

@dataclass
class GateFailure:
    """A single FAIL/WARN row parsed from a publish_audit JSON report.

    Mirrors the structure produced by ``publish_audit.py --output-format
    json``. Carries enough context (samples, file paths, node IDs) that a
    strategy can reconstruct the original violation without re-running
    the audit.
    """

    gate_id: int
    gate_name: str
    result: Literal["PASS", "FAIL", "WARN"]
    severity: Severity
    details: dict[str, Any] = field(default_factory=dict)
    samples: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RemediationAction:
    """A single concrete fix proposed by a strategy.

    The ``action_type`` discriminates the rendering path:

    * ``patch_file`` — change to an existing file (unified diff via ``new_content``)
    * ``create_file`` — new file with ``new_content``
    * ``delete_file`` — file removal (only with ``--destructive``)
    * ``plugin_op`` — Figma plugin TS operation (live-document mutation)

    Each action is self-describing — it carries the strategy id that
    produced it, the file path (for patch_file/create_file/delete_file),
    and a human-readable rationale that appears in PR descriptions.
    """

    strategy_id: int
    action_type: Literal["patch_file", "create_file", "delete_file", "plugin_op"]
    target_path: str
    rationale: str
    old_content: str | None = None        # for patch_file
    new_content: str | None = None        # for patch_file / create_file
    plugin_ops: list[dict] = field(default_factory=list)  # for plugin_op
    confidence: Literal["high", "medium", "low"] = "high"


@dataclass
class RemediationContext:
    """Runtime context handed to every strategy.

    Carries the library bundle root (so strategies can read source files),
    optional calibration sidecar directory (for confidence tuning), and
    operator preferences (locale, channel preference).
    """

    library_dir: Path
    calibration_dir: Path | None = None
    locale: str = "en-US"
    preferred_channel: Channel = "pr"
    dry_run: bool = False

    def read_json(self, rel_path: str) -> dict:
        """Helper: load a JSON file relative to ``library_dir``."""
        return json.loads((self.library_dir / rel_path).read_text(encoding="utf-8"))

    def read_text(self, rel_path: str) -> str:
        return (self.library_dir / rel_path).read_text(encoding="utf-8")

    def load_calibration(self, gate_id: int) -> dict | None:
        """Helper: load a single calibration sidecar if present."""
        if self.calibration_dir is None:
            return None
        cand = self.calibration_dir / f"gate_{gate_id:02d}_calibration.json"
        return json.loads(cand.read_text(encoding="utf-8")) if cand.exists() else None


# ----------------------------------------------------------------------------
# Strategy ABC
# ----------------------------------------------------------------------------

class RemediationStrategy(ABC):
    """Abstract base for a per-gate remediation.

    Subclasses must declare :attr:`gate_id` (matches the publish_audit
    gate number), a human-readable :attr:`title`, and the
    :attr:`output_channels` tuple — typically ``("pr",)`` for changes to
    static source files, ``("plugin",)`` for live Figma mutations only,
    or ``("pr", "plugin")`` when both channels are meaningful.
    """

    # — Class-level metadata (must be overridden)
    gate_id: ClassVar[int]
    title: ClassVar[str]
    output_channels: ClassVar[tuple[Channel, ...]] = ("pr",)

    @abstractmethod
    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        """Examine the gate failure; return the (possibly empty) action list.

        Implementations should be **idempotent** — running ``plan`` twice
        on the same failure should produce equivalent actions.
        """

    @abstractmethod
    def render(self, action: RemediationAction, channel: Channel) -> str:
        """Convert a single action into channel-specific output text.

        Raises :class:`UnsupportedChannelError` if the channel is not in
        :attr:`output_channels`.
        """


class UnsupportedChannelError(ValueError):
    """Raised when a strategy is asked to render to a channel it doesn't support."""


# ----------------------------------------------------------------------------
# Strategy registry
# ----------------------------------------------------------------------------

_REGISTRY: dict[int, type[RemediationStrategy]] = {}


def register_strategy(gate_id: int):
    """Decorator: bind a strategy class to a gate id.

    Mirrors the :func:`scripts.publish_audit.gates_registry.register_gate`
    pattern. Re-registration on the same ``gate_id`` raises
    :class:`ValueError` to surface accidental double-binding.
    """

    def _deco(cls: type[RemediationStrategy]) -> type[RemediationStrategy]:
        if gate_id in _REGISTRY:
            raise ValueError(
                f"Gate {gate_id} already has a registered strategy: "
                f"{_REGISTRY[gate_id].__name__}"
            )
        cls.gate_id = gate_id
        _REGISTRY[gate_id] = cls
        return cls

    return _deco


def get_strategy(gate_id: int) -> type[RemediationStrategy] | None:
    """Look up a strategy by gate id; returns ``None`` if unregistered."""
    return _REGISTRY.get(gate_id)


def all_strategies() -> dict[int, type[RemediationStrategy]]:
    """Return a copy of the strategy registry for introspection."""
    return dict(_REGISTRY)


# ----------------------------------------------------------------------------
# Result aggregator (used by CLI / runner)
# ----------------------------------------------------------------------------

@dataclass
class RemediationResult:
    """End-to-end result of running ``auto_remediate`` on an audit report."""

    audit_report_path: Path
    library_dir: Path
    strategies_run: list[int] = field(default_factory=list)
    actions: list[RemediationAction] = field(default_factory=list)
    skipped_gates: list[tuple[int, str]] = field(default_factory=list)  # (gate_id, reason)
    rendered_outputs: dict[str, str] = field(default_factory=dict)        # path → content

    @property
    def action_count(self) -> int:
        return len(self.actions)

    @property
    def file_count(self) -> int:
        return len(self.rendered_outputs)
