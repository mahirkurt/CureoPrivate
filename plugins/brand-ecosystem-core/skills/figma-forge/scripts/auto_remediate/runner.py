"""auto_remediate runner — orchestrates strategy execution.

Workflow:
    1. Parse audit report (Markdown or JSON) → list[GateFailure]
    2. For each FAIL/WARN gate, look up registered strategy
    3. strategy.plan(failure, ctx) → actions
    4. strategy.render(action, channel) → output text
    5. Persist outputs to ``remediations/`` directory (one file per action)
    6. Emit summary report

The runner is pure-functional except for the final filesystem write step;
``--dry-run`` skips that step entirely.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .base import (
    Channel,
    GateFailure,
    RemediationAction,
    RemediationContext,
    RemediationResult,
    UnsupportedChannelError,
    get_strategy,
)


# ---------------------------------------------------------------------------
# Audit-report parsing
# ---------------------------------------------------------------------------

_MD_GATE_HEADER_RE = re.compile(
    r"^##+\s*Gate\s+G(\d+)\s*—\s*(.*?)\s*\(\s*(PASS|FAIL|WARN)\s*\)",
    re.IGNORECASE,
)


def parse_audit_report(path: Path) -> list[GateFailure]:
    """Parse a publish_audit report from Markdown or JSON form.

    Returns the list of FAIL/WARN gate failures (PASS gates are filtered
    out — they have no remediation work).
    """
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".json" or raw.lstrip().startswith("{"):
        return _parse_json_report(json.loads(raw))
    return _parse_markdown_report(raw)


def _parse_json_report(data: dict) -> list[GateFailure]:
    out: list[GateFailure] = []
    for g in data.get("gates", []):
        result = g.get("result", "").upper()
        if result not in ("FAIL", "WARN"):
            continue
        out.append(
            GateFailure(
                gate_id=int(g["id"]),
                gate_name=g.get("name", f"Gate G{g['id']}"),
                result=result,
                severity=g.get("severity", "MAJOR").upper(),
                details=g.get("details", {}) or {},
                samples=g.get("samples", []) or [],
            )
        )
    return out


def _parse_markdown_report(md: str) -> list[GateFailure]:
    """Best-effort parser for the legacy Markdown report format."""
    out: list[GateFailure] = []
    for line in md.splitlines():
        m = _MD_GATE_HEADER_RE.match(line)
        if not m:
            continue
        gid = int(m.group(1))
        name = m.group(2).strip()
        result = m.group(3).upper()
        if result not in ("FAIL", "WARN"):
            continue
        out.append(
            GateFailure(
                gate_id=gid,
                gate_name=name,
                result=result,
                severity="MAJOR",  # MD parser cannot recover severity reliably
                details={},
                samples=[],
            )
        )
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

@dataclass
class RunnerOptions:
    audit_report: Path
    library_dir: Path
    output_dir: Path
    channel: Channel = "pr"
    strategies_filter: list[int] | None = None  # None = run all matching
    calibration_dir: Path | None = None
    locale: str = "en-US"
    dry_run: bool = False
    apply: bool = False


def run(opts: RunnerOptions) -> RemediationResult:
    """Execute the full remediation pipeline for ``opts``."""
    failures = parse_audit_report(opts.audit_report)

    ctx = RemediationContext(
        library_dir=opts.library_dir,
        calibration_dir=opts.calibration_dir,
        locale=opts.locale,
        preferred_channel=opts.channel,
        dry_run=opts.dry_run,
    )

    result = RemediationResult(
        audit_report_path=opts.audit_report,
        library_dir=opts.library_dir,
    )

    for failure in failures:
        if opts.strategies_filter and failure.gate_id not in opts.strategies_filter:
            continue

        strategy_cls = get_strategy(failure.gate_id)
        if strategy_cls is None:
            result.skipped_gates.append((failure.gate_id, "no registered strategy"))
            continue

        strategy = strategy_cls()
        if opts.channel not in strategy.output_channels:
            result.skipped_gates.append(
                (failure.gate_id, f"strategy doesn't support channel {opts.channel!r}")
            )
            continue

        try:
            actions = list(strategy.plan(failure, ctx))
        except Exception as exc:  # noqa: BLE001
            result.skipped_gates.append((failure.gate_id, f"plan failed: {exc!r}"))
            continue

        if not actions:
            result.skipped_gates.append((failure.gate_id, "no actions produced"))
            continue

        result.strategies_run.append(failure.gate_id)
        for idx, action in enumerate(actions):
            try:
                rendered = strategy.render(action, opts.channel)
            except UnsupportedChannelError as exc:
                result.skipped_gates.append((failure.gate_id, str(exc)))
                continue

            result.actions.append(action)
            # PR channel: one file per action. Plugin channel writes a single
            # consolidated script later (no per-action files).
            if opts.channel == "pr":
                sanitized = re.sub(r"[^a-zA-Z0-9._-]+", "_", action.target_path)
                out_name = f"g{failure.gate_id:02d}_{idx:03d}_{sanitized}.patch"
                result.rendered_outputs[out_name] = rendered

    if not opts.dry_run:
        opts.output_dir.mkdir(parents=True, exist_ok=True)

        if opts.channel == "plugin":
            # Plugin channel: render all actions into one consolidated TS file
            from .plugin_writer import render_plugin_script

            if result.actions:
                consolidated = render_plugin_script(result.actions, ctx, header_locale=opts.locale)
                ts_name = "figma-forge-remediations.ts"
                (opts.output_dir / ts_name).write_text(consolidated, encoding="utf-8")
                result.rendered_outputs[ts_name] = consolidated
        else:
            # PR channel: one patch file per action (already rendered above)
            for name, content in result.rendered_outputs.items():
                (opts.output_dir / name).write_text(content, encoding="utf-8")

        # Emit a summary JSON for downstream tooling
        summary = {
            "audit_report": str(opts.audit_report),
            "library_dir": str(opts.library_dir),
            "channel": opts.channel,
            "strategies_run": result.strategies_run,
            "action_count": result.action_count,
            "output_files": list(result.rendered_outputs.keys()),
            "skipped_gates": [
                {"gate_id": gid, "reason": reason}
                for gid, reason in result.skipped_gates
            ],
        }
        (opts.output_dir / "_summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return result
