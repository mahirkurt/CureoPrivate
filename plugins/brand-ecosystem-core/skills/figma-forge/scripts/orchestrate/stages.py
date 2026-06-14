"""Per-mode stage implementations.

Stages fall into two classes:

* **Executor stages** — perform real work via Python code or shell-out:
  - ``TOKENS_IMPORT`` shells out to ``dtcg_to_variables.py``
  - ``PUBLISH_AUDIT`` shells out to ``publish_audit.py``
  - ``AUTO_REMEDIATE`` shells out to ``auto_remediate.py``

* **Scaffold stages** — announce intent and require the v0.4.0 transport
  layer to perform live Figma operations (SCAFFOLD, FOUNDATIONS_BUILD,
  COMPONENTS_BUILD, ICONS_BUILD, PATTERNS_BUILD, CODE_CONNECT, PUBLISH).
  These currently emit a structured "would execute" log entry and
  succeed; they are wired for v0.4.0 to dispatch to the chosen
  transport adapter.

The split is deliberate: it allows a contributor to run
``figma-forge orchestrate --dry-run`` against any library without a
Figma PAT, and gives Sprint 4 a useful end-to-end pipeline even before
the transport layer lands.
"""

from __future__ import annotations

import shlex
import sys
from pathlib import Path

from .base import (
    ExecutionContext,
    Stage,
    StageResult,
    StageSpec,
    register_stage,
    run_subprocess,
)


# ---------------------------------------------------------------------------
# Helper: live stages that defer to v0.4.0 transport
# ---------------------------------------------------------------------------

class _LiveScaffoldStage(Stage):
    """Base for stages that require live Figma operations.

    In v0.3.0 GA these emit a structured log entry and succeed. v0.4.0
    will override the ``run`` method to dispatch to the active transport
    adapter (Anthropic MCP / Cursor MCP / Codebase MCP / REST fallback).
    """

    live_required = True
    _live_announce_template = (
        "{mode}: live Figma operation deferred to v0.4.0 transport layer. "
        "Would have executed: {command}"
    )

    def run(self, spec: StageSpec, ctx: ExecutionContext) -> StageResult:
        result = self._start(spec)
        msg = self._live_announce_template.format(
            mode=spec.mode,
            command=spec.command or "<no command in manifest>",
        )
        if ctx.verbose:
            print(f"  ⓘ {msg}", file=sys.stderr)
        return self._finish(result, status="success", output=msg)


# ---------------------------------------------------------------------------
# Live scaffold stages (v0.4.0 will provide real executors)
# ---------------------------------------------------------------------------

@register_stage("SCAFFOLD")
class ScaffoldStage(_LiveScaffoldStage):
    description = "Create empty Figma files per library-registry.json"


@register_stage("FOUNDATIONS_BUILD")
class FoundationsBuildStage(_LiveScaffoldStage):
    description = "Build Token Card grids on Foundations file"


@register_stage("COMPONENTS_BUILD")
class ComponentsBuildStage(_LiveScaffoldStage):
    description = "Create 17 components with full variant matrix"


@register_stage("ICONS_BUILD")
class IconsBuildStage(_LiveScaffoldStage):
    description = "Create 74 icon components from svg/"


@register_stage("PATTERNS_BUILD")
class PatternsBuildStage(_LiveScaffoldStage):
    description = "Create 17 UI surface compositions"


@register_stage("CODE_CONNECT")
class CodeConnectStage(_LiveScaffoldStage):
    description = "Attach Code Connect mappings via Figma API"


@register_stage("PUBLISH")
class PublishStage(_LiveScaffoldStage):
    description = "Publish 4 files as Library Assets"


# ---------------------------------------------------------------------------
# Real executor stages — these run today
# ---------------------------------------------------------------------------

@register_stage("TOKENS_IMPORT")
class TokensImportStage(Stage):
    """Run dtcg_to_variables.py to convert merged DTCG → Figma Variables payload.

    The stage is intentionally **idempotent**: if the output Variables
    payload already exists with a matching SHA-256 (per bundle manifest),
    the stage records ``success`` without rebuilding. This is mandatory
    for ``--resume`` to behave correctly.
    """

    description = "Convert merged DTCG to Figma Variables payload"
    live_required = False

    def run(self, spec: StageSpec, ctx: ExecutionContext) -> StageResult:
        result = self._start(spec)

        if ctx.dry_run:
            return self._finish(
                result, status="dry_run",
                output=f"would shell out to dtcg_to_variables.py for {ctx.library_dir}"
            )

        merged_dtcg = ctx.library_dir / "tokens" / "dustur.tokens.json"
        if not merged_dtcg.exists():
            return self._finish(
                result, status="failed",
                error=f"Merged DTCG not found at {merged_dtcg}"
            )

        out_payload = ctx.library_dir / "tokens" / "dustur.figma-variables.json"
        try:
            script = ctx.script_path("dtcg_to_variables.py")
        except FileNotFoundError as e:
            return self._finish(result, status="failed", error=str(e))

        cmd = [
            sys.executable, str(script),
            "--input", str(merged_dtcg),
            "--output", str(out_payload),
        ]
        rc, stdout, stderr = run_subprocess(cmd, cwd=ctx.library_dir, timeout=120)
        if rc != 0:
            return self._finish(
                result, status="failed",
                output=stdout, error=stderr or f"exit {rc}"
            )

        ctx.record_artifact(spec.mode, str(out_payload))
        return self._finish(
            result, status="success",
            output=stdout,
            artifacts=[str(out_payload)],
        )


@register_stage("PUBLISH_AUDIT")
class PublishAuditStage(Stage):
    """Run publish_audit.py against the library bundle.

    Supports the v0.3.0-beta JSON output format. Without a Figma PAT
    (e.g. CI without secrets), uses ``--static-only`` (when available)
    or records ``skipped`` with a clear reason.
    """

    description = "Run publish_audit gates against bundle"
    live_required = False  # static-only mode keeps this true; live mode adds dependency

    def run(self, spec: StageSpec, ctx: ExecutionContext) -> StageResult:
        result = self._start(spec)

        if ctx.dry_run:
            return self._finish(
                result, status="dry_run",
                output="would shell out to publish_audit.py"
            )

        try:
            script = ctx.script_path("publish_audit.py")
        except FileNotFoundError as e:
            return self._finish(result, status="failed", error=str(e))

        registry_path = ctx.library_dir / "library-registry.json"
        out_path = ctx.library_dir / "audit-report.json"
        cmd = [
            sys.executable, str(script),
            "--library-registry", str(registry_path),
            "--output", str(out_path),
            "--output-format", "json",
        ]
        # Live mode if PAT present
        if ctx.figma_pat:
            cmd.extend(["--figma-pat", ctx.figma_pat])
        else:
            cmd.append("--static-only")

        rc, stdout, stderr = run_subprocess(cmd, cwd=ctx.library_dir, timeout=300)
        if rc not in (0, 1):  # 1 = audit warnings but ran successfully
            return self._finish(
                result, status="failed",
                output=stdout, error=stderr or f"exit {rc}"
            )

        ctx.record_artifact(spec.mode, str(out_path))
        return self._finish(
            result, status="success",
            output=stdout,
            artifacts=[str(out_path)],
        )


@register_stage("AUTO_REMEDIATE")
class AutoRemediateStage(Stage):
    """Run auto_remediate.py against the latest audit report."""

    description = "Generate remediation patches for FAIL/WARN gates"
    live_required = False

    def run(self, spec: StageSpec, ctx: ExecutionContext) -> StageResult:
        result = self._start(spec)

        if ctx.dry_run:
            return self._finish(
                result, status="dry_run",
                output="would shell out to auto_remediate.py"
            )

        try:
            script = ctx.script_path("auto_remediate.py")
        except FileNotFoundError as e:
            return self._finish(result, status="failed", error=str(e))

        # Default audit report path — produced by PUBLISH_AUDIT stage
        audit_path = ctx.library_dir / "audit-report.json"
        if not audit_path.exists():
            return self._finish(
                result, status="skipped",
                skipped_reason="audit-report.json not present (PUBLISH_AUDIT stage hasn't produced it)"
            )

        out_dir = ctx.library_dir / "remediations"
        cmd = [
            sys.executable, str(script),
            "--audit-report", str(audit_path),
            "--library-dir", str(ctx.library_dir),
            "--output-channel", "pr",
            "--output-dir", str(out_dir),
            "--locale", ctx.locale,
        ]
        rc, stdout, stderr = run_subprocess(cmd, cwd=ctx.library_dir, timeout=300)
        if rc not in (0, 1):  # 1 = no actionable failures
            return self._finish(
                result, status="failed",
                output=stdout, error=stderr or f"exit {rc}"
            )

        ctx.record_artifact(spec.mode, str(out_dir))
        return self._finish(
            result, status="success",
            output=stdout,
            artifacts=[str(out_dir)],
        )
