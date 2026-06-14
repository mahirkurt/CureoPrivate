"""orchestrate runner — execute the pipeline from a manifest.

The runner sequences stages from a parsed manifest, dispatching each
to its registered :class:`Stage` executor, and aggregating per-stage
:class:`StageResult` records into a final :class:`ExecutionResult`.

Three execution modes:

* **default** — fail-fast; first stage failure halts the pipeline
* ``--dry-run`` — every stage prints its plan, no I/O
* ``--resume <STAGE>`` — skip stages before the named one (by mode name
  or 1-indexed stage number); useful for re-running after a fix
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

from .base import (
    ExecutionContext,
    ExecutionResult,
    Stage,
    StageResult,
    StageSpec,
    get_stage,
)
from .manifest import ManifestError, parse_manifest


@dataclass
class RunnerOptions:
    manifest_path: Path
    library_dir: Path
    forge_root: Path
    dry_run: bool = False
    verbose: bool = False
    locale: str = "en-US"
    figma_pat: str | None = None
    resume_from: str | None = None  # mode name or stringified int
    only: list[str] | None = None   # restrict to these mode names
    continue_on_failure: bool = False  # default: fail-fast


def run_pipeline(opts: RunnerOptions) -> ExecutionResult:
    """Execute the full pipeline declared in ``opts.manifest_path``."""
    _, specs = parse_manifest(opts.manifest_path)

    ctx = ExecutionContext(
        library_dir=opts.library_dir,
        manifest_path=opts.manifest_path,
        forge_root=opts.forge_root,
        locale=opts.locale,
        dry_run=opts.dry_run,
        verbose=opts.verbose,
        figma_pat=opts.figma_pat,
    )

    result = ExecutionResult(
        manifest_path=opts.manifest_path,
        library_dir=opts.library_dir,
        started_at=time.time(),
    )

    resume_idx = _resolve_resume_index(opts.resume_from, specs)
    only_modes = set(opts.only) if opts.only else None

    for spec in specs:
        if resume_idx is not None and spec.index < resume_idx:
            result.stages.append(_skipped_stage(spec, reason="before --resume target"))
            continue
        if only_modes is not None and spec.mode not in only_modes:
            result.stages.append(_skipped_stage(spec, reason="not in --only filter"))
            continue

        stage_cls = get_stage(spec.mode)
        if stage_cls is None:
            stage_result = StageResult(
                stage_index=spec.index,
                mode=spec.mode,
                status="failed",
                error=f"No registered executor for mode {spec.mode!r}",
            )
            result.stages.append(stage_result)
            if not opts.continue_on_failure:
                break
            continue

        stage: Stage = stage_cls()
        if opts.verbose:
            print(
                f"▶ Stage {spec.index}: {spec.mode} — {spec.description[:80]}",
                file=sys.stderr,
            )

        try:
            stage_result = stage.run(spec, ctx)
        except Exception as exc:  # noqa: BLE001
            stage_result = StageResult(
                stage_index=spec.index,
                mode=spec.mode,
                status="failed",
                error=f"Uncaught exception: {exc!r}",
            )
        result.stages.append(stage_result)

        if opts.verbose:
            sym = _status_symbol(stage_result.status)
            print(
                f"  {sym} Stage {spec.index}: {stage_result.status.upper()} "
                f"({stage_result.duration_seconds}s)",
                file=sys.stderr,
            )

        if stage_result.status == "failed" and not opts.continue_on_failure:
            break

    result.ended_at = time.time()
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skipped_stage(spec: StageSpec, *, reason: str) -> StageResult:
    return StageResult(
        stage_index=spec.index,
        mode=spec.mode,
        status="skipped",
        skipped_reason=reason,
    )


def _resolve_resume_index(resume_from: str | None, specs: list[StageSpec]) -> int | None:
    """Map ``--resume`` value (mode name or int) to the integer stage index."""
    if not resume_from:
        return None
    try:
        return int(resume_from)
    except ValueError:
        for s in specs:
            if s.mode == resume_from:
                return s.index
        raise ValueError(
            f"--resume target {resume_from!r} matches neither a stage index "
            f"nor a mode name in the manifest"
        )


def _status_symbol(status: str) -> str:
    return {
        "success": "✓",
        "failed":  "✗",
        "skipped": "↷",
        "dry_run": "·",
        "running": "▷",
        "pending": "○",
    }.get(status, "?")
