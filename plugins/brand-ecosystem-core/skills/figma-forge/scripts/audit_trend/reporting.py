"""audit_trend reporting — render TrendReport in JSON, Markdown, HTML.

JSON is the canonical machine-readable artifact for v0.4.0+ dashboards
(time series tooling can consume the same schema). Markdown is the PR
comment / docs surface. HTML is an inline-SVG dashboard ready to drop
into a CI artifact server or GitHub Pages — no JavaScript, no external
fonts, no CDN dependencies.

All three renderers share a single source of truth and follow the
same field ordering.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone

from .base import GateTimeSeries, TimePoint, TrendReport


# ---------------------------------------------------------------------------
# JSON render
# ---------------------------------------------------------------------------

def format_trend_json(report: TrendReport, *, indent: int = 2) -> str:
    """Serialize TrendReport as schema-v1.0 JSON."""
    payload = {
        "schema_version": "1.0",
        "report_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": {
            "start": report.window_start,
            "end": report.window_end,
            "days": report.window_days,
            "audit_count": report.audit_count,
        },
        "score_series": {
            "mean": report.score_mean,
            "stdev": report.score_stdev,
            "min": report.score_min,
            "max": report.score_max,
            "slope_per_audit": report.score_slope_per_audit,
            "slope_per_day": report.score_slope_per_day,
        },
        "calibration_drift_index": report.calibration_drift_index,
        "band_frequency": report.band_frequency,
        "points": [
            {
                "timestamp": p.timestamp,
                "build_version": p.build_version,
                "score": p.score,
                "band": p.band,
            }
            for p in report.points
        ],
        "gates": [
            {
                "gate_id": g.gate_id,
                "name": g.name,
                "observations": g.observations,
                "fail_count": g.fail_count,
                "pass_count": g.pass_count,
                "skip_count": g.skip_count,
                "fail_ratio": g.fail_ratio,
                "pass_to_fail_transitions": g.pass_to_fail_transitions,
                "fail_to_pass_transitions": g.fail_to_pass_transitions,
                "mean_time_to_fix": g.mean_time_to_fix,
                "stability": g.stability,
            }
            for g in sorted(report.gates.values(), key=lambda x: x.gate_id)
        ],
    }
    return json.dumps(payload, indent=indent, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def format_trend_markdown(report: TrendReport) -> str:
    """Render TrendReport as a Markdown dashboard document."""
    lines: list[str] = []
    lines.extend(_md_header(report))
    lines.append("")
    lines.extend(_md_score_summary(report))
    lines.append("")
    lines.extend(_md_band_distribution(report))
    lines.append("")
    lines.extend(_md_gate_stability_table(report))
    lines.append("")
    lines.extend(_md_per_audit_series(report))
    return "\n".join(lines) + "\n"


def _md_header(report: TrendReport) -> list[str]:
    return [
        "# figma-forge audit-trend",
        "",
        f"**Audit count:**   {report.audit_count}",
        f"**Window:**        {report.window_start or '—'} → {report.window_end or '—'}",
        f"**Window length:** {report.window_days:.1f} day(s)",
    ]


def _md_score_summary(report: TrendReport) -> list[str]:
    drift_label = _classify_drift(report.calibration_drift_index)
    slope_arrow = _slope_arrow(report.score_slope_per_audit)
    return [
        "## Score summary",
        "",
        f"- **Mean:** {report.score_mean:.2f} · "
        f"**Stdev:** {report.score_stdev:.2f} · "
        f"**Range:** [{report.score_min:.1f}, {report.score_max:.1f}]",
        f"- **Slope:** {slope_arrow} {report.score_slope_per_audit:+.4f} per audit · "
        f"{report.score_slope_per_day:+.4f} per day",
        f"- **Calibration Drift Index (σ/μ):** {report.calibration_drift_index:.4f}  "
        f"({drift_label})",
    ]


def _md_band_distribution(report: TrendReport) -> list[str]:
    if not report.band_frequency:
        return ["## Band distribution", "", "_No data._"]
    total = sum(report.band_frequency.values()) or 1
    lines = ["## Band distribution", ""]
    band_order = ["EXEMPLARY", "EXCELLENT", "STRONG", "ACCEPTABLE", "WEAK", "FAILING"]
    for band in band_order:
        count = report.band_frequency.get(band, 0)
        if count == 0:
            continue
        pct = round(100 * count / total, 1)
        bar = "█" * int(round(pct / 5)) or "·"
        lines.append(f"- `{band:10s}`  {count:3d} ({pct:5.1f}%)  {bar}")
    return lines


def _md_gate_stability_table(report: TrendReport) -> list[str]:
    if not report.gates:
        return ["## Gate stability", "", "_No gate observations._"]
    lines = [
        "## Gate stability",
        "",
        "| Gate | Name | Obs | Fail | Fail % | P→F | F→P | MTTF | Stability |",
        "|------|------|-----|------|--------|-----|-----|------|-----------|",
    ]
    for g in sorted(report.gates.values(), key=lambda x: (-x.fail_ratio, x.gate_id)):
        mttf = f"{g.mean_time_to_fix:.1f}" if g.mean_time_to_fix is not None else "—"
        label_sym = {
            "stable": "✓ stable",
            "improving": "↗ improving",
            "regressing": "↘ regressing",
            "flapping": "⇄ flapping",
            "absent": "— absent",
        }[g.stability]
        lines.append(
            f"| G{g.gate_id:03d} | {g.name[:32]:32s} | {g.observations} | "
            f"{g.fail_count} | {g.fail_ratio*100:.1f}% | "
            f"{g.pass_to_fail_transitions} | {g.fail_to_pass_transitions} | "
            f"{mttf} | {label_sym} |"
        )
    return lines


def _md_per_audit_series(report: TrendReport) -> list[str]:
    if not report.points:
        return []
    lines = ["## Per-audit score series", ""]
    lines.append("| # | Timestamp | Build | Score | Band |")
    lines.append("|---|-----------|-------|-------|------|")
    for i, p in enumerate(report.points, start=1):
        ts = p.timestamp[:19].replace("T", " ")
        lines.append(
            f"| {i:2d} | {ts} | {p.build_version[:14]:14s} | "
            f"{p.score:5.2f} | {p.band} |"
        )
    return lines


# ---------------------------------------------------------------------------
# HTML render — single-file, no external deps, inline SVG sparkline
# ---------------------------------------------------------------------------

def format_trend_html(report: TrendReport) -> str:
    """Render TrendReport as a single-file HTML dashboard.

    Embeds an inline SVG sparkline (score over time), per-gate
    table, and band distribution bars. No JavaScript, no external
    fonts, no CDN dependencies — works as a CI artifact or GitHub
    Pages drop-in.
    """
    sparkline = _svg_sparkline(report.points, width=720, height=160)
    band_bars = _band_bars_html(report)
    gate_rows = _gate_rows_html(report)
    drift_label = _classify_drift(report.calibration_drift_index)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>figma-forge audit-trend — {report.audit_count} audit(s)</title>
<style>
  :root {{
    --bg: #0b0e14;
    --panel: #161b22;
    --fg: #e6edf3;
    --muted: #8b949e;
    --good: #3fb950;
    --warn: #d29922;
    --bad:  #f85149;
    --line: #30363d;
  }}
  body {{
    margin: 0; padding: 2rem;
    font: 14px/1.5 -apple-system, BlinkMacSystemFont, "SF Pro Text",
                  "Helvetica Neue", Arial, sans-serif;
    background: var(--bg); color: var(--fg);
  }}
  h1 {{ font-weight: 600; font-size: 1.5rem; margin: 0 0 1.5rem; }}
  h2 {{ font-weight: 600; font-size: 1.1rem; margin: 1.5rem 0 0.5rem;
        color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
  .panel {{ background: var(--panel); border: 1px solid var(--line);
            border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem; }}
  .stat {{ display: inline-block; margin-right: 2rem; }}
  .stat-label {{ color: var(--muted); font-size: 0.8rem; text-transform: uppercase;
                 letter-spacing: 0.05em; }}
  .stat-value {{ font-size: 1.4rem; font-weight: 600; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ padding: 0.4rem 0.75rem; text-align: left;
            border-bottom: 1px solid var(--line); font-size: 0.85rem; }}
  th {{ color: var(--muted); font-weight: 500; text-transform: uppercase;
        letter-spacing: 0.05em; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .band-bar {{ display: flex; align-items: center; gap: 0.75rem; margin: 0.25rem 0; }}
  .band-bar-label {{ width: 6rem; color: var(--muted); font-size: 0.85rem; }}
  .band-bar-track {{ flex: 1; background: var(--line); height: 14px; border-radius: 4px;
                     overflow: hidden; }}
  .band-bar-fill {{ height: 100%; background: var(--good); }}
  .band-bar-count {{ width: 4rem; text-align: right; font-variant-numeric: tabular-nums; }}
  .stability-stable     {{ color: var(--good); }}
  .stability-improving  {{ color: var(--good); }}
  .stability-regressing {{ color: var(--bad);  }}
  .stability-flapping   {{ color: var(--warn); }}
  .stability-absent     {{ color: var(--muted); }}
  svg.spark {{ display: block; max-width: 100%; height: auto; }}
  .footer {{ margin-top: 2rem; color: var(--muted); font-size: 0.75rem; }}
</style>
</head>
<body>

<h1>figma-forge audit-trend</h1>

<div class="panel">
  <span class="stat">
    <div class="stat-label">Audits</div>
    <div class="stat-value">{report.audit_count}</div>
  </span>
  <span class="stat">
    <div class="stat-label">Window</div>
    <div class="stat-value">{report.window_days:.1f} d</div>
  </span>
  <span class="stat">
    <div class="stat-label">Score mean</div>
    <div class="stat-value">{report.score_mean:.2f}</div>
  </span>
  <span class="stat">
    <div class="stat-label">σ / μ (drift)</div>
    <div class="stat-value">{report.calibration_drift_index:.3f}<br>
      <span style="font-size: 0.7rem; color: var(--muted);">{drift_label}</span>
    </div>
  </span>
  <span class="stat">
    <div class="stat-label">Slope / audit</div>
    <div class="stat-value">{report.score_slope_per_audit:+.4f}</div>
  </span>
</div>

<h2>Score trend</h2>
<div class="panel">
{sparkline}
</div>

<h2>Band distribution</h2>
<div class="panel">
{band_bars}
</div>

<h2>Gate stability</h2>
<div class="panel">
<table>
<thead><tr>
  <th>Gate</th><th>Name</th>
  <th class="num">Obs</th><th class="num">Fail</th><th class="num">Fail %</th>
  <th class="num">P→F</th><th class="num">F→P</th><th class="num">MTTF</th>
  <th>Stability</th>
</tr></thead>
<tbody>
{gate_rows}
</tbody>
</table>
</div>

<div class="footer">
Generated by figma-forge audit-trend · schema v1.0 ·
{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}
</div>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _svg_sparkline(points: list[TimePoint], *, width: int, height: int) -> str:
    """Render an inline SVG sparkline of score over time."""
    if not points:
        return f'<svg class="spark" viewBox="0 0 {width} {height}"></svg>'

    pad = 12
    inner_w = width - 2 * pad
    inner_h = height - 2 * pad

    scores = [p.score for p in points]
    smin = min(scores)
    smax = max(scores)
    span = max(smax - smin, 0.1)

    coords: list[tuple[float, float]] = []
    n = len(points)
    if n == 1:
        coords.append((pad + inner_w / 2, pad + inner_h / 2))
    else:
        for i, p in enumerate(points):
            x = pad + (inner_w * i) / (n - 1)
            y = pad + inner_h - (inner_h * (p.score - smin) / span)
            coords.append((x, y))

    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    circles = "\n  ".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#3fb950"/>'
        for x, y in coords
    )
    # Reference line at score=8 (STRONG threshold), if in range
    ref_line = ""
    if smin <= 8.0 <= smax:
        ref_y = pad + inner_h - (inner_h * (8.0 - smin) / span)
        ref_line = (
            f'<line x1="{pad}" y1="{ref_y:.1f}" x2="{width-pad}" y2="{ref_y:.1f}" '
            f'stroke="#d29922" stroke-dasharray="3,3" stroke-width="1" opacity="0.6"/>'
        )

    return f"""<svg class="spark" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{width}" height="{height}" fill="transparent"/>
  {ref_line}
  <polyline fill="none" stroke="#3fb950" stroke-width="2" points="{poly}"/>
  {circles}
  <text x="{pad}" y="{height-2}" fill="#8b949e" font-size="10">
    score: {smin:.1f} – {smax:.1f}
  </text>
</svg>"""


def _band_bars_html(report: TrendReport) -> str:
    if not report.band_frequency:
        return '<p style="color: var(--muted);">No data.</p>'
    total = sum(report.band_frequency.values()) or 1
    out: list[str] = []
    band_order = ["EXEMPLARY", "EXCELLENT", "STRONG", "ACCEPTABLE", "WEAK", "FAILING"]
    band_color = {
        "EXEMPLARY":  "#3fb950",
        "EXCELLENT":  "#56d364",
        "STRONG":     "#a5d6a7",
        "ACCEPTABLE": "#d29922",
        "WEAK":       "#f0883e",
        "FAILING":    "#f85149",
    }
    for band in band_order:
        count = report.band_frequency.get(band, 0)
        if count == 0:
            continue
        pct = 100 * count / total
        color = band_color.get(band, "#3fb950")
        out.append(
            f'<div class="band-bar">'
            f'<span class="band-bar-label">{band}</span>'
            f'<div class="band-bar-track">'
            f'<div class="band-bar-fill" style="width: {pct:.1f}%; background: {color};"></div>'
            f'</div>'
            f'<span class="band-bar-count">{count} ({pct:.1f}%)</span>'
            f'</div>'
        )
    return "\n".join(out)


def _gate_rows_html(report: TrendReport) -> str:
    if not report.gates:
        return '<tr><td colspan="9" style="color: var(--muted);">No gate observations.</td></tr>'
    rows: list[str] = []
    for g in sorted(report.gates.values(), key=lambda x: (-x.fail_ratio, x.gate_id)):
        mttf = f"{g.mean_time_to_fix:.1f}" if g.mean_time_to_fix is not None else "—"
        css = f"stability-{g.stability}"
        label = {
            "stable": "✓ stable",
            "improving": "↗ improving",
            "regressing": "↘ regressing",
            "flapping": "⇄ flapping",
            "absent": "— absent",
        }[g.stability]
        rows.append(
            f"<tr>"
            f"<td>G{g.gate_id:03d}</td>"
            f"<td>{_html_escape(g.name)}</td>"
            f'<td class="num">{g.observations}</td>'
            f'<td class="num">{g.fail_count}</td>'
            f'<td class="num">{g.fail_ratio*100:.1f}%</td>'
            f'<td class="num">{g.pass_to_fail_transitions}</td>'
            f'<td class="num">{g.fail_to_pass_transitions}</td>'
            f'<td class="num">{mttf}</td>'
            f'<td class="{css}">{label}</td>'
            f"</tr>"
        )
    return "\n".join(rows)


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Shared classifiers
# ---------------------------------------------------------------------------

def _classify_drift(cdi: float) -> str:
    """Label the calibration drift index."""
    if cdi == 0:
        return "perfectly stable"
    if cdi < 0.02:
        return "stable"
    if cdi < 0.05:
        return "minor drift"
    if cdi < 0.10:
        return "moderate drift"
    return "high drift"


def _slope_arrow(slope: float) -> str:
    if slope > 0.05:
        return "↗"
    if slope < -0.05:
        return "↘"
    return "▶"
