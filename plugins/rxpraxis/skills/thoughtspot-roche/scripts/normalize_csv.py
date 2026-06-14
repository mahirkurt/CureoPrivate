#!/usr/bin/env python3
"""
thoughtspot-roche — CSV Normalization Helper
=============================================

Programmatic helper for the CSV normalization steps defined in
SKILL.md §4 Step 6 and references/csv-normalization-guide.md.

Provides:
- skip_header_rows()       — Strip the three-row Roche extract preamble
- format_chf()             — Convert scientific notation to Turkish-formatted CHF
- add_percent_column()     — Append Pay (%) column to top-N tables
- normalize_thoughtspot()  — One-shot full pipeline

Stdlib only (no external dependencies).

Usage as CLI:
    python3 normalize_csv.py <raw_thoughtspot_csv_file> [--output <markdown|csv>]

Usage as library:
    from normalize_csv import normalize_thoughtspot
    table = normalize_thoughtspot(raw_data_string)
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ============================================================================
# Constants
# ============================================================================

EXTRACT_NOTE_PREFIX = "Data extract produced by"
CONFIDENTIAL_LABEL = "You are downloading Roche confidential material"

THRESHOLD_TRILLION = 1e12
THRESHOLD_BILLION = 1e9
THRESHOLD_MILLION = 1e6


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class NormalizedRow:
    """Single normalized data row with original + formatted values."""
    label: str
    raw_value: float
    formatted: str
    percent_of_topn: Optional[float] = None


@dataclass
class NormalizedTable:
    """Full normalized table from a getAnswer payload."""
    column_label: str       # e.g., "ATC1 Description"
    metric_label: str       # e.g., "Total Swiss Franc"
    rows: List[NormalizedRow] = field(default_factory=list)
    extract_user: Optional[str] = None
    extract_timestamp: Optional[str] = None
    is_confidential: bool = True


# ============================================================================
# Header Skip
# ============================================================================

def skip_header_rows(raw_data: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Strip the three-row Roche extract preamble, returning the actual CSV
    body plus the extracted user identity and timestamp metadata.

    Returns:
        (csv_body, extract_user_identity, extract_timestamp)

    The first row is parsed for provenance even though it's stripped
    from the body.
    """
    lines = raw_data.splitlines()
    if not lines:
        return "", None, None

    extract_user = None
    extract_timestamp = None

    # Row 1: extract note
    first = lines[0].strip().strip('"')
    if first.startswith(EXTRACT_NOTE_PREFIX):
        # Format: "Data extract produced by Mahir Kurt (kurtm1) on MM/DD/YYYY HH:MM UTC"
        try:
            after_by = first.split("by ", 1)[1]
            user_part, _, ts_part = after_by.partition(" on ")
            extract_user = user_part.strip()
            extract_timestamp = ts_part.strip()
        except (IndexError, ValueError):
            pass

    # Skip three rows (extract note + confidential label + blank)
    body_lines = lines[3:] if len(lines) >= 3 else []
    return "\n".join(body_lines), extract_user, extract_timestamp


# ============================================================================
# Number Formatting
# ============================================================================

def format_chf(value: float | str, precision: int = 2) -> str:
    """
    Convert a numeric value (float or scientific-notation string) to a
    Turkish-formatted CHF representation following csv-normalization-guide.md §3.

    >>> format_chf("2.8204218045255586E12")
    '2,82 trilyon CHF'
    >>> format_chf("1.5432691542370734E11")
    '154,33 milyar CHF'
    >>> format_chf(91902700167.0)
    '91,90 milyar CHF'
    >>> format_chf(847.5)
    '848 CHF'
    """
    if isinstance(value, str):
        try:
            val = float(value)
        except ValueError:
            return value  # Pass through non-numeric labels unchanged
    else:
        val = float(value)

    if val >= THRESHOLD_TRILLION:
        formatted = f"{val/THRESHOLD_TRILLION:.{precision}f} trilyon CHF"
    elif val >= THRESHOLD_BILLION:
        formatted = f"{val/THRESHOLD_BILLION:.{precision}f} milyar CHF"
    elif val >= THRESHOLD_MILLION:
        formatted = f"{val/THRESHOLD_MILLION:.{precision}f} milyon CHF"
    else:
        formatted = f"{val:,.0f} CHF".replace(",", ".")

    # Convert decimal point to comma (Turkish convention)
    return formatted.replace(".", ",", 1) if "trilyon" in formatted or "milyar" in formatted or "milyon" in formatted else formatted


# ============================================================================
# Magnitude Sanity Check (G8)
# ============================================================================

def magnitude_interpretation(grand_total: float) -> str:
    """
    Apply Gate G8 (currency unit verification) magnitude interpretation
    per csv-normalization-guide.md §6.

    >>> magnitude_interpretation(13.3e12)
    'Çok yıl + çok manufacturer (tüm-pazar audited sales kümülasyonu)'
    """
    if grand_total < 1e11:
        return "Tek yıl + tek manufacturer veya alt-segment"
    elif grand_total < 1e12:
        return "Çok yıl tek manufacturer veya tek yıl çok manufacturer"
    elif grand_total < 2e13:
        return "Çok yıl + çok manufacturer (tüm-pazar audited sales kümülasyonu)"
    else:
        return "OLAĞANDIŞI mertebe — veri çıkarma hatası şüphesi (G8 alarm)"


# ============================================================================
# Percentage Column
# ============================================================================

def add_percent_column(rows: List[NormalizedRow]) -> List[NormalizedRow]:
    """
    Compute Pay (%) for each row relative to the sum of provided rows
    (Top-N içi pay, csv-normalization-guide.md §4.1).
    """
    total = sum(r.raw_value for r in rows)
    if total == 0:
        return rows
    for r in rows:
        r.percent_of_topn = (r.raw_value / total) * 100
    return rows


# ============================================================================
# Full Pipeline
# ============================================================================

def normalize_thoughtspot(raw_data: str) -> NormalizedTable:
    """
    One-shot normalization of a getAnswer CSV payload.
    """
    csv_body, extract_user, extract_ts = skip_header_rows(raw_data)

    reader = csv.reader(io.StringIO(csv_body))
    rows = list(reader)
    if not rows:
        return NormalizedTable(
            column_label="",
            metric_label="",
            rows=[],
            extract_user=extract_user,
            extract_timestamp=extract_ts,
        )

    header = rows[0]
    column_label = header[0] if len(header) >= 1 else ""
    metric_label = header[1] if len(header) >= 2 else ""

    normalized_rows = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        try:
            raw_value = float(row[1])
        except ValueError:
            continue
        normalized_rows.append(NormalizedRow(
            label=row[0],
            raw_value=raw_value,
            formatted=format_chf(raw_value),
        ))

    # Sort descending by raw_value (top-N convention)
    normalized_rows.sort(key=lambda r: r.raw_value, reverse=True)
    add_percent_column(normalized_rows)

    return NormalizedTable(
        column_label=column_label,
        metric_label=metric_label,
        rows=normalized_rows,
        extract_user=extract_user,
        extract_timestamp=extract_ts,
    )


# ============================================================================
# Output Renderers
# ============================================================================

def render_markdown(table: NormalizedTable) -> str:
    """Render a NormalizedTable as a Markdown table with provenance footer."""
    lines = []
    lines.append(f"## {table.column_label} Bazında {table.metric_label}\n")
    lines.append(f"| Sıra | {table.column_label} | {table.metric_label} | Pay (%) — Top-{len(table.rows)} içi |")
    lines.append("|---|---|---|---|")

    for i, r in enumerate(table.rows, start=1):
        pct = f"{r.percent_of_topn:.1f} %".replace(".", ",") if r.percent_of_topn is not None else "—"
        lines.append(f"| {i} | {r.label} | {r.formatted} | {pct} |")

    grand_total = sum(r.raw_value for r in table.rows)
    lines.append(f"| | **TOPLAM (Top-{len(table.rows)})** | **{format_chf(grand_total)}** | **100,0 %** |")

    lines.append("")
    lines.append(f"**Mertebe yorumu (G8):** {magnitude_interpretation(grand_total)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Provenance**")
    lines.append("")
    lines.append(f"- **Extract:** {table.extract_user or 'unknown'} · {table.extract_timestamp or 'unknown'}")
    lines.append("- **Classification:** Roche confidential — internal use only")
    return "\n".join(lines)


def render_csv(table: NormalizedTable) -> str:
    """Render a NormalizedTable as a clean CSV (header rows stripped)."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([table.column_label, table.metric_label, "Pay_pct_topN"])
    for r in table.rows:
        pct = f"{r.percent_of_topn:.4f}" if r.percent_of_topn is not None else ""
        writer.writerow([r.label, r.raw_value, pct])
    return out.getvalue()


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Normalize a ThoughtSpot getAnswer CSV payload."
    )
    parser.add_argument(
        "input",
        help="Path to raw CSV file from getAnswer (or '-' for stdin).",
    )
    parser.add_argument(
        "--output",
        choices=["markdown", "csv"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    args = parser.parse_args()

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            raw = f.read()

    table = normalize_thoughtspot(raw)

    if args.output == "markdown":
        print(render_markdown(table))
    else:
        print(render_csv(table))


if __name__ == "__main__":
    main()
