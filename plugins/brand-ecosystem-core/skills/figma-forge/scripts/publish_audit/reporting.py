"""
Audit report rendering — produces the Markdown report consumed by humans
and downstream tools (smp-orchestrator audit ingest, CI pipelines).

Backward-compatible with v0.1.x format: section ordering, heading text,
emoji icons, and gate ID schema are preserved. v0.2.0 additions are
limited to:
  * Multi-file breakdowns when ``per_file`` is populated
  * Notes block per gate when present
  * ``Skipped:`` line in summary (was always 0 in v0.1.x because all
    unimplemented gates skipped; now varies by build)
"""

from __future__ import annotations

from datetime import datetime, timezone

from .models import GateResult


SEVERITY_ICON = {"error": "❌", "warn": "⚠️", "info": "ℹ️"}


def _icon_for(result: GateResult) -> str:
    if result.status == "pass":
        return "✅"
    if result.status == "skip":
        return "🔵"
    if result.status == "n_a":
        return "⚫"
    return SEVERITY_ICON.get(result.gate.severity, "❌")


def _summary_counts(results: list[GateResult]) -> dict[str, int]:
    """Group results into the five summary categories used in the header."""
    return {
        "errors": sum(1 for r in results
                       if r.status == "fail" and r.gate.severity == "error"),
        "warns":  sum(1 for r in results
                       if r.status == "fail" and r.gate.severity == "warn"),
        "infos":  sum(1 for r in results
                       if r.status == "fail" and r.gate.severity == "info"),
        "skips":  sum(1 for r in results if r.status in ("skip", "n_a")),
        "passes": sum(1 for r in results if r.status == "pass"),
    }


def _render_summary_header(file_label: str, audit_target: str,
                            build_version: str, results: list[GateResult]) -> list[str]:
    """Return the report's H1 + bullet-list summary block as a list of lines."""
    now = datetime.now(timezone.utc).isoformat()
    c = _summary_counts(results)
    return [
        f"# figma-forge Publish Audit — {file_label}",
        "",
        f"- Audit run: {now}",
        f"- Audit target: `{audit_target}`",
        f"- figma-forge audit framework version: {build_version}",
        f"- Total checks: {len(results)}",
        f"- ✅ Passed: {c['passes']}",
        f"- ❌ Errors: {c['errors']}",
        f"- ⚠️ Warnings: {c['warns']}",
        f"- ℹ️ Info: {c['infos']}",
        f"- 🔵 Skipped/N-A: {c['skips']}",
        "",
    ]


def _render_failure_block(result: GateResult) -> list[str]:
    """Render a gate's failure list + per-file breakdown + remediation."""
    lines: list[str] = []
    if not result.failures:
        return lines
    lines.append("")
    lines.append(f"**Failures ({len(result.failures)}):**")
    lines.append("")
    for fail in result.failures[:25]:
        lines.append(f"- {fail}")
    if len(result.failures) > 25:
        lines.append(f"- … and {len(result.failures) - 25} more")
    if result.per_file and len(result.per_file) > 1:
        lines.append("")
        lines.append("**Failures by file:**")
        for role, msgs in sorted(result.per_file.items()):
            lines.append(f"- `{role}`: {len(msgs)} failure(s)")
    lines.append("")
    lines.append(f"**Remediation:** {result.gate.remediation}")
    return lines


def _render_gate_section(result: GateResult) -> list[str]:
    """Render the full section for one gate (header + status + notes + failures)."""
    icon = _icon_for(result)
    lines = [
        f"### Gate {result.gate.id} — {result.gate.name}",
        "",
        (f"**Status:** {icon} {result.status.upper()}  ·  "
         f"**Severity:** {result.gate.severity}  ·  "
         f"**Checked:** {result.checked_count}"),
        "",
        f"**Description:** {result.gate.description}",
    ]
    if result.notes:
        lines.append("")
        for note in result.notes:
            lines.append(f"> 📝 {note}")
    lines.extend(_render_failure_block(result))
    lines.append("")
    return lines


def format_report(
    results: list[GateResult],
    *,
    file_label: str,
    audit_target: str,
    build_version: str | None = None,
) -> str:
    """Render the audit results as a Markdown document.

    ``build_version`` defaults to the package ``__version__`` so the report
    always reflects the running build without forcing callers to thread the
    string through manually.
    """
    if build_version is None:
        # Local import to avoid a circular import at module load time.
        from . import __version__ as _v
        build_version = _v

    out: list[str] = []
    out.extend(_render_summary_header(file_label, audit_target, build_version, results))
    out.append("## Gate-by-gate results")
    out.append("")
    for r in results:
        out.extend(_render_gate_section(r))

    return "\n".join(out)


# ============================================================================
# JSON report format (v0.3.0)
# ============================================================================

def format_json_report(
    results: list[GateResult],
    *,
    file_label: str,
    audit_target: str,
    build_version: str | None = None,
) -> str:
    """Render the audit results as a v1.0-schema JSON document.

    The JSON form is the canonical machine-readable input for downstream
    automation: ``auto_remediate``'s runner, the (v0.3.1) ``audit-diff``
    delta calculator, and CI pipelines that gate on individual gate ids.

    The schema is **frozen** at v1.0 from this release onward — additive
    fields are allowed in v1.x, but field removals or type changes
    require a major schema bump (v2.0) and CHANGELOG migration notes.

    Schema::

        {
          "schema_version": "1.0",
          "audit_timestamp": "<ISO-8601 UTC>",
          "build_version": "<figma-forge version string>",
          "audit_target": "<descriptive label>",
          "file_label": "<short DS name>",
          "score": <float 0..10>,
          "band": "EXEMPLARY|EXCELLENT|STRONG|ACCEPTABLE|WEAK|FAILING",
          "summary": {"errors": N, "warns": N, "infos": N, "skips": N, "passes": N},
          "gates": [
            {
              "id": 1..19,
              "name": "...",
              "severity": "error|warn|info",
              "result": "PASS|FAIL|SKIP|N_A",
              "checked_count": N,
              "details": {"failure_count": N, "per_file": {...}},
              "samples": [{"message": "..."}, ...],
              "notes": ["..."]
            }, ...
          ]
        }
    """
    import json as _json

    if build_version is None:
        from . import __version__ as _v
        build_version = _v

    summary = _summary_counts(results)
    score, band = _score_and_band(summary, len(results))

    gates_payload: list[dict] = []
    for r in results:
        per_file = {role: lines for role, lines in r.per_file.items() if lines}
        gates_payload.append({
            "id": r.gate.id,
            "name": r.gate.name,
            "severity": r.gate.severity,
            "result": r.status.upper(),
            "checked_count": r.checked_count,
            "details": {
                "failure_count": len(r.failures),
                "per_file": per_file or None,
            },
            "samples": [{"message": f} for f in r.failures],
            "notes": list(r.notes),
        })

    payload = {
        "schema_version": "1.0",
        "audit_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "build_version": build_version,
        "audit_target": audit_target,
        "file_label": file_label,
        "score": score,
        "band": band,
        "summary": summary,
        "gates": gates_payload,
    }
    return _json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _score_and_band(summary: dict[str, int], total_gates: int) -> tuple[float, str]:
    """Derive a 0..10 score + band label from the summary counts.

    Heuristic — matches the band labels used in the Markdown header:

    * +1.0 per passing gate, 0 per skip, −1.5 per error-level fail,
      −0.5 per warn-level fail, −0.1 per info-level fail
    * Normalized to 0..10 range; clamped
    * Band thresholds: 9.0+ EXEMPLARY, 8.0+ EXCELLENT, 7.0+ STRONG,
      6.0+ ACCEPTABLE, 4.0+ WEAK, <4.0 FAILING
    """
    if total_gates == 0:
        return 0.0, "FAILING"
    raw = (
        summary["passes"]
        - summary["errors"] * 1.5
        - summary["warns"] * 0.5
        - summary["infos"] * 0.1
    )
    # Normalize: ideal raw == total_gates (all pass); worst case raw negative
    normalized = max(0.0, min(10.0, (raw / total_gates) * 10.0))
    score = round(normalized, 1)
    if score >= 9.0:
        band = "EXEMPLARY"
    elif score >= 8.0:
        band = "EXCELLENT"
    elif score >= 7.0:
        band = "STRONG"
    elif score >= 6.0:
        band = "ACCEPTABLE"
    elif score >= 4.0:
        band = "WEAK"
    else:
        band = "FAILING"
    return score, band
