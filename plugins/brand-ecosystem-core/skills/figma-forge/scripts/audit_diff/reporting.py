"""audit-diff reporting — render DiffReport in JSON and Markdown.

The JSON form is the canonical machine-readable artifact consumed by
CI pipelines (gate on ``summary.regressions > 0``); the Markdown form
is the human-readable PR-comment surface.

The two renderers share a single source of truth and follow the same
field ordering, so a CI bot can ingest both side by side.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .base import DiffReport, GateTransition


def format_diff_json(report: DiffReport, *, indent: int = 2) -> str:
    """Serialize DiffReport as schema-v1.0 JSON."""
    payload = {
        "schema_version": "1.0",
        "diff_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "baseline": {
            "path": report.baseline.path,
            "timestamp": report.baseline.timestamp,
            "build_version": report.baseline.build_version,
            "score": report.baseline.score,
            "band": report.baseline.band,
            "summary": report.baseline.summary,
        },
        "current": {
            "path": report.current.path,
            "timestamp": report.current.timestamp,
            "build_version": report.current.build_version,
            "score": report.current.score,
            "band": report.current.band,
            "summary": report.current.summary,
        },
        "score_delta": report.score_delta,
        "band_shift": report.band_shift,
        "summary": report.summary,
        "transitions": [
            {
                "gate_id": t.gate_id,
                "name": t.name,
                "severity_baseline": t.severity_baseline,
                "severity_current": t.severity_current,
                "result_baseline": t.result_baseline,
                "result_current": t.result_current,
                "checked_baseline": t.checked_baseline,
                "checked_current": t.checked_current,
                "classification": t.classification,
                "samples_resolved": t.samples_resolved,
                "samples_introduced": t.samples_introduced,
            }
            for t in report.transitions
        ],
    }
    return json.dumps(payload, indent=indent, ensure_ascii=False) + "\n"


def format_diff_markdown(report: DiffReport) -> str:
    """Render DiffReport as a Markdown PR-comment-friendly document."""
    lines: list[str] = []
    lines.extend(_render_header(report))
    lines.append("")
    lines.extend(_render_score_block(report))
    lines.append("")
    lines.extend(_render_regressions_section(report))
    lines.append("")
    lines.extend(_render_improvements_section(report))
    lines.append("")
    lines.extend(_render_unchanged_summary(report))
    lines.append("")
    lines.extend(_render_new_or_removed_section(report))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_header(report: DiffReport) -> list[str]:
    return [
        "# figma-forge audit-diff",
        "",
        f"**Baseline:**  `{report.baseline.path}`  ({report.baseline.timestamp})",
        f"**Current:**   `{report.current.path}`  ({report.current.timestamp})",
    ]


def _render_score_block(report: DiffReport) -> list[str]:
    delta_sym = _delta_symbol(report.score_delta)
    shift_sym = _band_shift_symbol(report.band_shift)
    summary = report.summary
    lines = [
        "## Headline",
        "",
        f"- Score:  **{report.baseline.score:.1f}** → "
        f"**{report.current.score:.1f}**   "
        f"(Δ {delta_sym}{report.score_delta:+.1f})",
        f"- Band:   **{report.baseline.band}** → **{report.current.band}**   "
        f"({shift_sym} {report.band_shift})",
        f"- Gates:  {summary['regressions']} regression · "
        f"{summary['improvements']} improvement · "
        f"{summary['no_change']} unchanged · "
        f"{summary['new_gates']} new · "
        f"{summary['removed_gates']} removed",
    ]
    return lines


def _render_regressions_section(report: DiffReport) -> list[str]:
    if not report.regressions:
        return ["## Regressions", "", "_No gates regressed._"]
    out = ["## Regressions ❌", ""]
    for t in report.regressions:
        out.extend(_render_transition(t))
    return out


def _render_improvements_section(report: DiffReport) -> list[str]:
    if not report.improvements:
        return ["## Improvements", "", "_No gates improved._"]
    out = ["## Improvements ✅", ""]
    for t in report.improvements:
        out.extend(_render_transition(t))
    return out


def _render_unchanged_summary(report: DiffReport) -> list[str]:
    unchanged = [t for t in report.transitions if t.classification == "no_change"]
    if not unchanged:
        return []
    fmt = ", ".join(
        f"G{t.gate_id:02d} ({t.result_current})" for t in unchanged
    )
    return [
        "## Unchanged",
        "",
        f"{len(unchanged)} gate(s) held position: {fmt}",
    ]


def _render_new_or_removed_section(report: DiffReport) -> list[str]:
    new = [t for t in report.transitions if t.classification == "new"]
    removed = [t for t in report.transitions if t.classification == "removed"]
    if not new and not removed:
        return []
    out = ["## Catalog changes"]
    if new:
        out.append("")
        out.append(f"**Newly introduced gates ({len(new)}):**")
        out.append("")
        for t in new:
            out.append(f"- G{t.gate_id:02d} **{t.name}** — {t.result_current}")
    if removed:
        out.append("")
        out.append(f"**Removed gates ({len(removed)}):**")
        out.append("")
        for t in removed:
            out.append(f"- G{t.gate_id:02d} **{t.name}** — was {t.result_baseline}")
    return out


def _render_transition(t: GateTransition) -> list[str]:
    """Render a single gate transition block."""
    sev_change = ""
    if t.severity_baseline != t.severity_current:
        sev_change = f" (severity: {t.severity_baseline} → {t.severity_current})"
    header = (
        f"### G{t.gate_id:02d} — {t.name}: "
        f"**{t.result_baseline}** → **{t.result_current}**{sev_change}"
    )
    lines = [header, ""]
    if t.checked_baseline != t.checked_current:
        lines.append(
            f"- Checked count: {t.checked_baseline} → {t.checked_current}"
        )
    if t.samples_introduced:
        lines.append("")
        lines.append("**New failure samples:**")
        for sample in t.samples_introduced[:8]:
            lines.append(f"- `{sample}`")
        if len(t.samples_introduced) > 8:
            lines.append(f"- … and {len(t.samples_introduced) - 8} more")
    if t.samples_resolved:
        lines.append("")
        lines.append("**Resolved samples:**")
        for sample in t.samples_resolved[:8]:
            lines.append(f"- `{sample}`")
        if len(t.samples_resolved) > 8:
            lines.append(f"- … and {len(t.samples_resolved) - 8} more")
    lines.append("")
    return lines


def _delta_symbol(delta: float) -> str:
    if delta > 0:
        return "🔼"
    if delta < 0:
        return "🔽"
    return "▶"


def _band_shift_symbol(shift: str) -> str:
    return {"improved": "🔼", "regressed": "🔽", "stable": "▶"}.get(shift, "▶")
