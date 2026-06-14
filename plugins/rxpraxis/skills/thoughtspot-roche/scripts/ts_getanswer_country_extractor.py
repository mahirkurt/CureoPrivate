#!/usr/bin/env python3
"""
ts_getanswer_country_extractor.py  (v2)
=======================================
Vendor-neutral pharmaceutical market-intelligence extractor for the
ThoughtSpot REST API v2.0 (getAnswer / searchdata path).

EXTENDS v1 (ts_getanswer_extractor.py) by adding a geographic layer:

  1. Top-N molecules by total Swiss Franc, ATC2='l1' (antineoplastic agents),
     last 12 months, aggregated across all countries.           [primary]
  2. ATC2='l1' grand total across ALL molecules.                [denominator]
  3. For EACH top molecule, a Country x Swiss Franc breakdown.   [geo layer]

From the geo layer it derives, per molecule:
  - n_countries            : number of countries with positive sales (footprint)
  - top_country            : highest-grossing country for that molecule
  - top_country_share_pct  : top-1 country concentration (%)
  - hhi_country            : Herfindahl-Hirschman Index of country shares
                             (0 = perfectly dispersed, 1 = single-country)

OUTPUTS (two artifacts):
  A) Summary CSV -> stdout (pipe with '>'):
       rank,molecule,total_chf,share_of_class_pct,
       n_countries,top_country,top_country_share_pct,hhi_country
  B) Long-format country breakdown CSV -> file (TS_LONG_CSV, default
     ./molecule_country_breakdown.csv):
       molecule,country,chf,pct_of_molecule_total

Nothing is fabricated: every figure comes from the live API response. If the
API is unreachable the script fails loudly rather than inventing numbers.

Reference (ThoughtSpot Developer docs, verified 2026-06):
  POST /api/rest/2.0/auth/token/full     (username + secret_key)
  POST /api/rest/2.0/metadata/search     (resolve LOGICAL_TABLE GUID)
  POST /api/rest/2.0/searchdata          (query_string + logical_table_identifier)
  Response envelope: data["contents"][0]["column_names" | "data_rows"]
  Defaults: data_format=COMPACT, record_offset=0, record_size=10
            (record_size=-1 => complete result set; <=100000 rows/call)

Configuration (environment variables; no secrets in code):
  TS_HOST        e.g. analytics.example.com   (no scheme)
  TS_USER        service-account username
  TS_SECRET_KEY  trusted-auth secret key
  TS_SOURCE      data source / worksheet name  (default: "Midas Monthly")
  TS_LONG_CSV    path for the long-format country CSV
                 (default: ./molecule_country_breakdown.csv)
  TS_CALL_DELAY  seconds to sleep between per-molecule calls (default: 0)

Usage:
  pip install requests
  export TS_HOST=... TS_USER=... TS_SECRET_KEY=...
  python ts_getanswer_country_extractor.py > top10_summary.csv
"""

from __future__ import annotations

import csv
import os
import sys
import time
from typing import Any

import requests

# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #
TS_HOST = os.environ.get("TS_HOST", "").rstrip("/")
TS_USER = os.environ.get("TS_USER", "")
TS_SECRET_KEY = os.environ.get("TS_SECRET_KEY", "")
TS_SOURCE = os.environ.get("TS_SOURCE", "Midas Monthly")
TS_LONG_CSV = os.environ.get("TS_LONG_CSV", "molecule_country_breakdown.csv")
TS_CALL_DELAY = float(os.environ.get("TS_CALL_DELAY", "0"))

# Generic, vendor-neutral query parameters -- edit freely for other cuts.
METRIC_COL = "Swiss Franc"        # measure
DIMENSION_COL = "Molecule List"   # most granular active-ingredient level
COUNTRY_COL = "Country"           # geography dimension
ATC2_FILTER = "l1"                # antineoplastic agents (lowercase code)
TIME_WINDOW = "last 12 months"
TOP_N = 10

TIMEOUT = 120  # seconds; cross-country aggregations can be slow
HEADERS_JSON = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "market-intel/2.0",  # required for code-based REST calls
}


def _require_config() -> None:
    missing = [k for k, v in {
        "TS_HOST": TS_HOST, "TS_USER": TS_USER, "TS_SECRET_KEY": TS_SECRET_KEY
    }.items() if not v]
    if missing:
        sys.exit(f"[FATAL] Missing environment variables: {', '.join(missing)}")


def _url(path: str) -> str:
    return f"https://{TS_HOST}{path}"


def _log(msg: str) -> None:
    print(f"[ts-extract] {msg}", file=sys.stderr)


def _q(value: str) -> str:
    """Single-quote a literal for the TS query language, escaping inner quotes."""
    return value.replace("'", "\\'")


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


def _col_index(column_names: list[str], *needles: str, fallback: int = 0) -> int:
    """Return index of the first column whose name contains any needle."""
    lowered = [c.lower() for c in column_names]
    for needle in needles:
        for i, c in enumerate(lowered):
            if needle in c:
                return i
    return fallback


# --------------------------------------------------------------------------- #
# Query builders                                                              #
# --------------------------------------------------------------------------- #
def q_top_n() -> str:
    return (
        f"[{METRIC_COL}] [{DIMENSION_COL}] "
        f"[ATC2] = '{ATC2_FILTER}' [Date] = '{TIME_WINDOW}' "
        f"sort by [{METRIC_COL}] descending top {TOP_N}"
    )


def q_class_total() -> str:
    return f"[{METRIC_COL}] [ATC2] = '{ATC2_FILTER}' [Date] = '{TIME_WINDOW}'"


def q_country_for(molecule: str) -> str:
    return (
        f"[{COUNTRY_COL}] [{METRIC_COL}] "
        f"[{DIMENSION_COL}] = '{_q(molecule)}' [Date] = '{TIME_WINDOW}' "
        f"sort by [{METRIC_COL}] descending"
    )


# --------------------------------------------------------------------------- #
# Derivation helpers                                                          #
# --------------------------------------------------------------------------- #
def derive_geo_metrics(country_rows: list[list[Any]], ci: int, mi: int
                       ) -> dict[str, Any]:
    """Compute n_countries, top-country concentration, and HHI from
    Country x measure rows for a single molecule."""
    pairs = []
    for r in country_rows:
        try:
            val = float(r[mi])
        except (TypeError, ValueError):
            continue
        if val > 0:  # presence = positive audited sales
            pairs.append((str(r[ci]), val))

    n_countries = len(pairs)
    if n_countries == 0:
        return {
            "n_countries": 0, "top_country": "", "top_country_chf": 0,
            "top_country_share_pct": "", "hhi_country": "",
        }

    total = sum(v for _, v in pairs)
    pairs.sort(key=lambda p: p[1], reverse=True)
    top_country, top_chf = pairs[0]
    shares = [v / total for _, v in pairs]
    hhi = round(sum(s * s for s in shares), 4)  # 0..1
    return {
        "n_countries": n_countries,
        "top_country": top_country,
        "top_country_chf": int(top_chf),
        "top_country_share_pct": round(100.0 * top_chf / total, 2),
        "hhi_country": hhi,
    }


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #
def main() -> None:
    _require_config()
    token = get_token()
    guid = resolve_source_guid(token)
    _log(f"data source '{TS_SOURCE}' -> {guid}")

    # 1) Top-N molecules.
    top = search_data(token, guid, q_top_n())
    cols = top["column_names"]
    rows = top["data_rows"]
    di = _col_index(cols, "molecule", fallback=0)
    mi = _col_index(cols, "franc", fallback=len(cols) - 1)
    _log(f"top-{TOP_N} molecules retrieved ({len(rows)} rows)")

    # 2) Class grand total (correct denominator).
    total_block = search_data(token, guid, q_class_total())
    t_mi = _col_index(total_block["column_names"], "franc",
                      fallback=len(total_block["column_names"]) - 1)
    t_rows = total_block["data_rows"]
    class_total = float(t_rows[0][t_mi]) if t_rows else 0.0
    _log(f"ATC2='{ATC2_FILTER}' class total = {int(class_total)}")

    # 3) Per-molecule country breakdown + derivations.
    summary_writer = csv.writer(sys.stdout)
    summary_writer.writerow([
        "rank", "molecule", "total_chf", "share_of_class_pct",
        "n_countries", "top_country", "top_country_share_pct", "hhi_country",
    ])

    with open(TS_LONG_CSV, "w", newline="", encoding="utf-8") as fh:
        long_writer = csv.writer(fh)
        long_writer.writerow(
            ["molecule", "country", "chf", "pct_of_molecule_total"])

        for rank, row in enumerate(rows, start=1):
            molecule = str(row[di])
            mol_total = float(row[mi])
            share_class = (round(100.0 * mol_total / class_total, 2)
                           if class_total else "")

            geo = search_data(token, guid, q_country_for(molecule))
            g_cols = geo["column_names"]
            g_ci = _col_index(g_cols, "country", fallback=0)
            g_mi = _col_index(g_cols, "franc", fallback=len(g_cols) - 1)
            g_rows = geo["data_rows"]

            metrics = derive_geo_metrics(g_rows, g_ci, g_mi)
            summary_writer.writerow([
                rank, molecule, int(mol_total), share_class,
                metrics["n_countries"], metrics["top_country"],
                metrics["top_country_share_pct"], metrics["hhi_country"],
            ])

            # Long-format rows (positive-sales countries only).
            denom = mol_total if mol_total else 0.0
            for gr in g_rows:
                try:
                    val = float(gr[g_mi])
                except (TypeError, ValueError):
                    continue
                if val <= 0:
                    continue
                pct = round(100.0 * val / denom, 2) if denom else ""
                long_writer.writerow([molecule, str(gr[g_ci]), int(val), pct])

            _log(f"  [{rank}] {molecule}: {metrics['n_countries']} countries")
            if TS_CALL_DELAY:
                time.sleep(TS_CALL_DELAY)

    _log(f"long-format country breakdown written -> {TS_LONG_CSV}")


if __name__ == "__main__":
    main()
