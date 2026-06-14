"""figma-forge orchestrate framework, v0.3.0-rc.1.

Drives a multi-stage pipeline (SCAFFOLD → TOKENS_IMPORT → ... →
PUBLISH) from a single ``orchestration.json`` manifest. Replaces the
ad-hoc multi-command shell scripts that the Düstur build required.

Public API:
    StageSpec, StageResult, ExecutionContext, ExecutionResult
    Stage (ABC)
    register_stage(mode), get_stage(mode), all_stages()
    parse_manifest(path)
    RunnerOptions, run_pipeline(opts)

Three execution modes:
    default       — fail-fast pipeline run
    --dry-run     — plan only, zero I/O
    --resume STAGE — skip stages strictly before STAGE
"""

from .base import (
    ExecutionContext,
    ExecutionResult,
    Stage,
    StageResult,
    StageSpec,
    all_stages,
    get_stage,
    register_stage,
    run_subprocess,
)
from .manifest import ManifestError, parse_manifest
from .runner import RunnerOptions, run_pipeline

# Import stages so their @register_stage decorators fire
from . import stages  # noqa: F401

__version__ = "0.3.0-rc.1"

__all__ = [
    "ExecutionContext",
    "ExecutionResult",
    "ManifestError",
    "RunnerOptions",
    "Stage",
    "StageResult",
    "StageSpec",
    "all_stages",
    "get_stage",
    "parse_manifest",
    "register_stage",
    "run_pipeline",
    "run_subprocess",
    "__version__",
]
