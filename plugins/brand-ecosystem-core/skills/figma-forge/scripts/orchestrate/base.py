"""figma-forge orchestrate framework — base abstractions.

Defines :class:`Stage` ABC, :class:`StageResult` dataclass, and
:class:`ExecutionContext` runtime container. Each pipeline stage from
the manifest (SCAFFOLD, TOKENS_IMPORT, FOUNDATIONS_BUILD,
COMPONENTS_BUILD, ICONS_BUILD, PATTERNS_BUILD, CODE_CONNECT,
PUBLISH_AUDIT, PUBLISH) is implemented as a :class:`Stage` subclass and
self-registers via :func:`@register_stage(mode_name)` decorator.

The orchestrator separates concerns:

* **manifest.py** — parses ``orchestration.json``, validates against
  the v1.0 schema, returns a typed list of :class:`StageSpec` records.
* **runner.py** — executes stages in declared order, handles
  ``--dry-run`` and ``--resume`` flags, and aggregates results.
* **stages/** — per-mode :class:`Stage` implementations. Some are full
  executors (TOKENS_IMPORT shells out to ``dtcg_to_variables.py``;
  PUBLISH_AUDIT shells out to ``publish_audit.py``); others are
  scaffolds that announce intent and require the v0.4.0 transport
  layer to perform live Figma operations.

The framework is **execution-mode-aware**:

* ``--dry-run`` — every stage prints its plan but performs no I/O
* ``--resume <stage>`` — skip stages strictly before the named one
* default — execute every stage, fail-fast on first error
"""

from __future__ import annotations

import json
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

StageStatus = Literal["pending", "running", "success", "failed", "skipped", "dry_run"]


@dataclass
class StageSpec:
    """A single stage row parsed from ``orchestration.json``.

    Mirrors the manifest schema fields directly. Carries the executor
    name (``mode``), the original command string from the manifest, and
    arbitrary metadata (estimated_time, prerequisites, outputs).
    """

    index: int
    mode: str  # SCAFFOLD | TOKENS_IMPORT | ... | PUBLISH
    description: str
    command: str | None = None
    outputs: list[str] = field(default_factory=list)
    estimated_time: str | None = None
    pass_criteria: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass
class StageResult:
    """Per-stage execution outcome."""

    stage_index: int
    mode: str
    status: StageStatus
    started_at: float = 0.0
    ended_at: float = 0.0
    output: str = ""
    error: str | None = None
    artifacts: list[str] = field(default_factory=list)
    skipped_reason: str | None = None

    @property
    def duration_seconds(self) -> float:
        if self.ended_at and self.started_at:
            return round(self.ended_at - self.started_at, 2)
        return 0.0


@dataclass
class ExecutionContext:
    """Runtime context handed to every stage's ``run`` method.

    Carries the library bundle root, the running figma-forge version,
    operator preferences (locale, verbosity, dry-run flag), and a
    cumulative artifact registry that successor stages can consult.
    """

    library_dir: Path
    manifest_path: Path
    locale: str = "en-US"
    dry_run: bool = False
    verbose: bool = False
    figma_pat: str | None = None
    artifacts: dict[str, list[str]] = field(default_factory=dict)
    # Path to the figma-forge installation root (for shelling out to scripts)
    forge_root: Path | None = None

    def script_path(self, name: str) -> Path:
        """Resolve a sibling script path for shelling out."""
        if self.forge_root is None:
            raise RuntimeError("forge_root not set on ExecutionContext")
        candidate = self.forge_root / "scripts" / name
        if not candidate.exists():
            raise FileNotFoundError(f"Sibling script missing: {candidate}")
        return candidate

    def record_artifact(self, stage_mode: str, path: str) -> None:
        self.artifacts.setdefault(stage_mode, []).append(path)


@dataclass
class ExecutionResult:
    """End-to-end pipeline outcome aggregator."""

    manifest_path: Path
    library_dir: Path
    started_at: float = 0.0
    ended_at: float = 0.0
    stages: list[StageResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for s in self.stages if s.status == "success")

    @property
    def failed_count(self) -> int:
        return sum(1 for s in self.stages if s.status == "failed")

    @property
    def skipped_count(self) -> int:
        return sum(1 for s in self.stages if s.status == "skipped")

    @property
    def duration_seconds(self) -> float:
        if self.ended_at and self.started_at:
            return round(self.ended_at - self.started_at, 2)
        return 0.0


# ---------------------------------------------------------------------------
# Stage ABC + registry
# ---------------------------------------------------------------------------

class Stage(ABC):
    """Abstract base for a single pipeline-stage executor.

    Subclasses declare :attr:`mode` (the manifest's ``mode`` field
    value, e.g. ``"TOKENS_IMPORT"``) and implement :meth:`run`. The
    framework discovers subclasses via the
    :func:`@register_stage(mode)` decorator.
    """

    mode: ClassVar[str]
    live_required: ClassVar[bool] = False  # True if stage talks to live Figma
    description: ClassVar[str] = ""

    @abstractmethod
    def run(self, spec: StageSpec, ctx: ExecutionContext) -> StageResult:
        """Execute the stage and return a populated :class:`StageResult`."""

    def _start(self, spec: StageSpec) -> StageResult:
        """Helper: build the initial StageResult before work begins."""
        return StageResult(
            stage_index=spec.index,
            mode=spec.mode,
            status="running",
            started_at=time.time(),
        )

    def _finish(self, result: StageResult, *, status: StageStatus, **fields) -> StageResult:
        """Helper: finalize a StageResult."""
        result.status = status
        result.ended_at = time.time()
        for k, v in fields.items():
            setattr(result, k, v)
        return result


class StageRegistrationError(ValueError):
    """Raised when a stage class registers under an already-bound mode."""


_REGISTRY: dict[str, type[Stage]] = {}


def register_stage(mode: str):
    """Decorator: bind a stage class to its manifest mode name."""

    def _deco(cls: type[Stage]) -> type[Stage]:
        if mode in _REGISTRY:
            raise StageRegistrationError(
                f"Mode {mode!r} already bound to {_REGISTRY[mode].__name__}"
            )
        cls.mode = mode
        _REGISTRY[mode] = cls
        return cls

    return _deco


def get_stage(mode: str) -> type[Stage] | None:
    return _REGISTRY.get(mode)


def all_stages() -> dict[str, type[Stage]]:
    return dict(_REGISTRY)


# ---------------------------------------------------------------------------
# Subprocess helper (used by executor-style stages)
# ---------------------------------------------------------------------------

def run_subprocess(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 600,
) -> tuple[int, str, str]:
    """Thin subprocess.run wrapper used by executor stages.

    Returns ``(returncode, stdout, stderr)``. Captures both streams as
    text and never raises on non-zero exit — the caller decides whether
    to fail the stage.
    """
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr
