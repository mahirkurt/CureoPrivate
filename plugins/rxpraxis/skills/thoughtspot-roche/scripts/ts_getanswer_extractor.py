#!/usr/bin/env python3
"""
ts_getanswer_extractor.py
=========================
Vendor-neutral pharmaceutical market-intelligence extractor for the
ThoughtSpot REST API v2.0 (getAnswer / searchdata path).

It reproduces, OUTSIDE the MCP connector, the query:

    Top 10 molecules by total Swiss Franc (CHF), ATC2 = 'l1'
    (antineoplastic agents), last 12 months, all countries.

The MCP `send_session_message` / `get_session_updates` surface returns only
an NLG summary + a rendered iframe; it does NOT expose raw result cells.
This script closes that gap by calling the documented REST data endpoint,
which returns the underlying `column_names` / `data_rows` arrays, and then
normalizes them to the target CSV schema:

    rank,molecule,total_chf,share_of_class_pct

`share_of_class_pct` is derived from a second searchdata call that returns the
ATC2='l1' grand total (sum across ALL molecules), so the share is correct
rather than a share-of-top-10.

Reference (ThoughtSpot Developer docs, verified 2026-06):
  - POST /api/rest/2.0/auth/token/full           (username + secret_key)
  - POST /api/rest/2.0/metadata/search           (resolve LOGICAL_TABLE GUID)
  - POST /api/rest/2.0/searchdata                (query_string + logical_table_identifier)
  - Response envelope: data["contents"][0]["column_names" | "data_rows"]
  - Defaults: data_format=COMPACT, record_offset=0, record_size=10
              (use record_size=-1 for the complete result set)

Nothing here is fabricated: the actual CHF figures come from the live API
response. If the API is unreachable, the script fails loudly rather than
inventing numbers.

Configuration is via environment variables (no secrets in code):
    TS_HOST        e.g. analytics.example.com   (no scheme)
    TS_USER        service-account username
    TS_SECRET_KEY  trusted-auth secret key
    TS_SOURCE      data source / worksheet name  (default: "Midas Monthly")

Usage:
    pip install requests
    export TS_HOST=... TS_USER=... TS_SECRET_KEY=...
    python ts_getanswer_extractor.py > top10_antineoplastics.csv
"""

from __future__ import annotations

import csv
import os
import sys
from typing import Any

import requests

# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #
TS_HOST = os.environ.get("TS_HOST", "").rstrip("/")
TS_USER = os.environ.get("TS_USER", "")
TS_SECRET_KEY = os.environ.get("TS_SECRET_KEY", "")
TS_SOURCE = os.environ.get("TS_SOURCE", "Midas Monthly")

# Generic, vendor-neutral query parameters -- edit freely for other cuts.
METRIC_COL = "Swiss Franc"        # measure
DIMENSION_COL = "Molecule List"   # most granular active-ingredient level
ATC2_FILTER = "l1"                # antineoplastic agents (lowercase code)
TIME_WINDOW = "last 12 months"
TOP_N = 10

TIMEOUT = 120  # seconds; large cross-country aggregations can be slow
HEADERS_JSON = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "market-intel/1.0",  # required for code-based REST calls
}


def _require_config() -> None:
    missing = [k for k, v in {
        "TS_HOST": TS_HOST, "TS_USER": TS_USER, "TS_SECRET_KEY": TS_SECRET_KEY
    }.items() if not v]
    if missing:
        sys.exit(f"[FATAL] Missing environment variables: {', '.join(missing)}")


def _url(path: str) -> str:
    return f"https://{TS_HOST}{path}"


# --------------------------------------------------------------------------- #
# Step 0 - Authentication                                                     #
# --------------------------------------------------------------------------- #
def get_token() -> str:
    resp = requests.post(
        _url("/api/rest/2.0/auth/token/full"),
        headers=HEADERS_JSON,
        json={
            "username": TS_USER,
            "secret_key": TS_SECRET_KEY,
            "validity_time_in_sec": 3600,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    token = resp.json().get("token")
    if not token:
        sys.exit("[FATAL] No token returned by auth endpoint.")
    return token


# --------------------------------------------------------------------------- #
# Step 1 - Resolve worksheet / data source GUID                               #
# --------------------------------------------------------------------------- #
def resolve_source_guid(token: str) -> str:
    resp = requests.post(
        _url("/api/rest/2.0/metadata/search"),
        headers={**HEADERS_JSON, "Authorization": f"Bearer {token}"},
        json={
            "metadata": [{"type": "LOGICAL_TABLE", "name_pattern": TS_SOURCE}],
            "record_size": 10,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        sys.exit(f"[FATAL] Data source '{TS_SOURCE}' not found.")
    # Prefer an exact (case-insensitive) name match; else take the first hit.
    for item in results:
        name = (item.get("metadata_name") or item.get("name") or "")
        if name.strip().lower() == TS_SOURCE.strip().lower():
            return item.get("metadata_id") or item["id"]
    first = results[0]
    return first.get("metadata_id") or first["id"]


# --------------------------------------------------------------------------- #
# Step 2 - searchdata (getAnswer raw cells)                                   #
# --------------------------------------------------------------------------- #
def search_data(token: str, source_guid: str, query_string: str) -> dict[str, Any]:
    resp = requests.post(
        _url("/api/rest/2.0/searchdata"),
        headers={**HEADERS_JSON, "Authorization": f"Bearer {token}"},
        json={
            "query_string": query_string,
            "logical_table_identifier": source_guid,
            "data_format": "COMPACT",
            "record_offset": 0,
            "record_size": -1,  # -1 => complete result set
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    contents = data.get("contents")
    if not contents:
        sys.exit("[FATAL] Empty 'contents' in searchdata response.")
    return contents[0]


def _measure_index(column_names: list[str]) -> int:
    """Find the numeric measure column (Swiss Franc) defensively."""
    for i, c in enumerate(column_names):
        if "franc" in c.lower():
            return i
    # Fallback: assume last column is the measure.
    return len(column_names) - 1


def _dimension_index(column_names: list[str]) -> int:
    for i, c in enumerate(column_names):
        if "molecule" in c.lower():
            return i
    return 0


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #
def build_top_n_query() -> str:
    return (
        f"[{METRIC_COL}] [{DIMENSION_COL}] "
        f"[ATC2] = '{ATC2_FILTER}' [Date] = '{TIME_WINDOW}' "
        f"sort by [{METRIC_COL}] descending top {TOP_N}"
    )


def build_class_total_query() -> str:
    # Grand total across ALL molecules in the class -> correct denominator.
    return (
        f"[{METRIC_COL}] [ATC2] = '{ATC2_FILTER}' [Date] = '{TIME_WINDOW}'"
    )


def main() -> None:
    _require_config()
    token = get_token()
    guid = resolve_source_guid(token)

    # Primary: top-N molecules.
    top = search_data(token, guid, build_top_n_query())
    cols = top["column_names"]
    rows = top["data_rows"]
    di, mi = _dimension_index(cols), _measure_index(cols)

    # Denominator: class grand total (single-cell or single-row result).
    total_block = search_data(token, guid, build_class_total_query())
    total_rows = total_block["data_rows"]
    total_mi = _measure_index(total_block["column_names"])
    class_total = float(total_rows[0][total_mi]) if total_rows else 0.0

    writer = csv.writer(sys.stdout)
    writer.writerow(["rank", "molecule", "total_chf", "share_of_class_pct"])
    for rank, row in enumerate(rows, start=1):
        molecule = row[di]
        chf = float(row[mi])
        share = round(100.0 * chf / class_total, 2) if class_total else ""
        writer.writerow([rank, molecule, int(chf), share])


if __name__ == "__main__":
    main()
