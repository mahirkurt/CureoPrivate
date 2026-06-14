#!/usr/bin/env python3
"""
analytics-npv.py — Risk-adjusted NPV (rNPV) calculator
Part of pharmaintel v3.0.0 analytics framework

Usage:
    python3 analytics-npv.py input.json
    python3 analytics-npv.py --stdin < input.json
    python3 analytics-npv.py --example    # prints example input JSON to stdout

Input schema (see references/analytics-framework.md §2 + §7.1):
{
    "asset_name": "Example Asset",
    "sponsor": "Example Co",
    "wacc": 0.10,                          # discount rate (decimal)
    "pos": 0.55,                           # cumulative probability of success to launch
    "base_year": 2026,                     # year 0 for discounting
    "cash_flows": [
        {
            "year": 2026,
            "revenue": 0,
            "cogs_pct": 0.15,
            "sga_pct": 0.30,
            "rd_expense": 150000000,       # absolute dollars
            "capex": 0,
            "change_wc": 0
        },
        ...
    ],
    "terminal": {
        "final_year": 2040,
        "terminal_value": 500000000        # post-final-year residual NPV
    },
    "tax_rate": 0.20,
    "confidence_notes": "PoS benchmark P3→approval 55% per BIO 2020-2024"
}

Output: JSON to stdout with per-year discounted cash flows + aggregate rNPV.
"""

import argparse
import json
import sys
from typing import Any, Dict, List


EXAMPLE_INPUT: Dict[str, Any] = {
    "asset_name": "Example Phase 3 Oncology Asset",
    "sponsor": "Example Co",
    "wacc": 0.10,
    "pos": 0.55,
    "base_year": 2026,
    "cash_flows": [
        {"year": 2026, "revenue": 0, "cogs_pct": 0.0, "sga_pct": 0.0, "rd_expense": 180_000_000, "capex": 20_000_000, "change_wc": 0},
        {"year": 2027, "revenue": 0, "cogs_pct": 0.0, "sga_pct": 0.0, "rd_expense": 160_000_000, "capex": 30_000_000, "change_wc": 0},
        {"year": 2028, "revenue": 50_000_000, "cogs_pct": 0.15, "sga_pct": 1.2, "rd_expense": 120_000_000, "capex": 20_000_000, "change_wc": 15_000_000},
        {"year": 2029, "revenue": 350_000_000, "cogs_pct": 0.15, "sga_pct": 0.45, "rd_expense": 100_000_000, "capex": 10_000_000, "change_wc": 30_000_000},
        {"year": 2030, "revenue": 800_000_000, "cogs_pct": 0.15, "sga_pct": 0.35, "rd_expense": 80_000_000, "capex": 10_000_000, "change_wc": 40_000_000},
        {"year": 2031, "revenue": 1_300_000_000, "cogs_pct": 0.15, "sga_pct": 0.30, "rd_expense": 60_000_000, "capex": 10_000_000, "change_wc": 40_000_000},
        {"year": 2032, "revenue": 1_700_000_000, "cogs_pct": 0.15, "sga_pct": 0.28, "rd_expense": 50_000_000, "capex": 10_000_000, "change_wc": 30_000_000},
        {"year": 2033, "revenue": 2_000_000_000, "cogs_pct": 0.15, "sga_pct": 0.26, "rd_expense": 50_000_000, "capex": 10_000_000, "change_wc": 20_000_000},
        {"year": 2034, "revenue": 2_200_000_000, "cogs_pct": 0.15, "sga_pct": 0.25, "rd_expense": 50_000_000, "capex": 10_000_000, "change_wc": 20_000_000},
        {"year": 2035, "revenue": 2_250_000_000, "cogs_pct": 0.15, "sga_pct": 0.25, "rd_expense": 40_000_000, "capex": 10_000_000, "change_wc": 10_000_000},
    ],
    "terminal": {
        "final_year": 2040,
        "terminal_value": 4_000_000_000
    },
    "tax_rate": 0.20,
    "confidence_notes": "PoS benchmark P3→approval 55% per BIO 2020-2024 oncology average."
}


def compute_year_cashflow(cf: Dict[str, Any], tax_rate: float) -> Dict[str, Any]:
    revenue = cf["revenue"]
    cogs = revenue * cf["cogs_pct"]
    gross_profit = revenue - cogs
    sga = revenue * cf["sga_pct"]
    rd = cf["rd_expense"]
    ebitda = gross_profit - sga - rd
    tax = max(0, ebitda * tax_rate)  # no tax benefit on losses (simplification)
    atcf = ebitda - tax - cf["capex"] - cf["change_wc"]
    return {
        "year": cf["year"],
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "sga": sga,
        "rd_expense": rd,
        "ebitda": ebitda,
        "tax": tax,
        "capex": cf["capex"],
        "change_wc": cf["change_wc"],
        "after_tax_cash_flow": atcf
    }


def compute_rnpv(input_data: Dict[str, Any]) -> Dict[str, Any]:
    wacc = input_data["wacc"]
    pos = input_data["pos"]
    base_year = input_data["base_year"]
    tax_rate = input_data.get("tax_rate", 0.20)

    discounted_cashflows: List[Dict[str, Any]] = []
    total_rnpv = 0.0

    for cf in input_data["cash_flows"]:
        year_result = compute_year_cashflow(cf, tax_rate)
        t = year_result["year"] - base_year
        discount_factor = 1 / ((1 + wacc) ** t)
        atcf = year_result["after_tax_cash_flow"]
        risk_adjusted = atcf * pos
        discounted = risk_adjusted * discount_factor

        year_result["t"] = t
        year_result["discount_factor"] = discount_factor
        year_result["risk_adjusted_cashflow"] = risk_adjusted
        year_result["discounted_cashflow"] = discounted
        discounted_cashflows.append(year_result)
        total_rnpv += discounted

    # Terminal value
    terminal = input_data.get("terminal", {})
    terminal_value = terminal.get("terminal_value", 0)
    terminal_year = terminal.get("final_year", base_year)
    terminal_t = terminal_year - base_year
    terminal_discount_factor = 1 / ((1 + wacc) ** terminal_t)
    terminal_rnpv = terminal_value * pos * terminal_discount_factor
    total_rnpv += terminal_rnpv

    return {
        "asset_name": input_data.get("asset_name", "Unnamed Asset"),
        "sponsor": input_data.get("sponsor", "Unknown"),
        "inputs": {
            "wacc": wacc,
            "pos": pos,
            "base_year": base_year,
            "tax_rate": tax_rate
        },
        "year_by_year": discounted_cashflows,
        "terminal": {
            "year": terminal_year,
            "t": terminal_t,
            "terminal_value_undiscounted": terminal_value,
            "risk_adjusted": terminal_value * pos,
            "discounted": terminal_rnpv
        },
        "rnpv": total_rnpv,
        "confidence_notes": input_data.get("confidence_notes", ""),
        "disclaimer": "Model-derived projection. Confidence = minimum of input confidences. Not investment advice."
    }


def main():
    parser = argparse.ArgumentParser(description="Risk-adjusted NPV calculator (pharmaintel v3.0.0)")
    parser.add_argument("input_file", nargs="?", help="Path to input JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read input JSON from stdin")
    parser.add_argument("--example", action="store_true", help="Print example input JSON")
    parser.add_argument("--indent", type=int, default=2, help="JSON output indent")
    args = parser.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE_INPUT, indent=args.indent))
        return

    if args.stdin:
        input_data = json.load(sys.stdin)
    elif args.input_file:
        with open(args.input_file) as f:
            input_data = json.load(f)
    else:
        parser.print_help()
        sys.exit(1)

    result = compute_rnpv(input_data)
    print(json.dumps(result, indent=args.indent))


if __name__ == "__main__":
    main()
