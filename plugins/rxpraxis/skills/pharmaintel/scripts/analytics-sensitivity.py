#!/usr/bin/env python3
"""
analytics-sensitivity.py — One-way sensitivity (tornado) analysis
Part of pharmaintel v3.0.0 analytics framework

Usage:
    python3 analytics-sensitivity.py input.json
    python3 analytics-sensitivity.py --example

For rNPV sensitivity analysis: takes base case rNPV + list of perturbable inputs,
returns ΔrNPV per input perturbed, sorted by |ΔrNPV| (tornado order).

Input schema (see references/analytics-framework.md §3):
{
    "base_case": { ... full input for analytics-npv.py ... },
    "perturbations": [
        {
            "variable": "wacc",
            "low_value": 0.08,
            "high_value": 0.12,
            "label": "WACC"
        },
        {
            "variable": "pos",
            "low_value": 0.40,
            "high_value": 0.70,
            "label": "Probability of Success"
        },
        {
            "variable": "revenue_multiplier",
            "low_value": 0.70,
            "high_value": 1.30,
            "label": "Peak Sales ±30%",
            "apply_to": "all_cash_flows_revenue"
        }
    ]
}
"""

import argparse
import copy
import json
import sys
from typing import Any, Dict, List

# Embed NPV calculator
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
_npv_module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics-npv.py")


def _load_npv_module():
    """Load analytics-npv.py as a module (handles hyphen in filename)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("analytics_npv", _npv_module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXAMPLE_INPUT: Dict[str, Any] = {
    "base_case": {
        "asset_name": "Example Oncology Asset",
        "sponsor": "Example Co",
        "wacc": 0.10,
        "pos": 0.55,
        "base_year": 2026,
        "cash_flows": [
            {"year": 2028, "revenue": 50_000_000, "cogs_pct": 0.15, "sga_pct": 1.2, "rd_expense": 120_000_000, "capex": 20_000_000, "change_wc": 15_000_000},
            {"year": 2030, "revenue": 800_000_000, "cogs_pct": 0.15, "sga_pct": 0.35, "rd_expense": 80_000_000, "capex": 10_000_000, "change_wc": 40_000_000},
            {"year": 2032, "revenue": 1_700_000_000, "cogs_pct": 0.15, "sga_pct": 0.28, "rd_expense": 50_000_000, "capex": 10_000_000, "change_wc": 30_000_000},
            {"year": 2034, "revenue": 2_200_000_000, "cogs_pct": 0.15, "sga_pct": 0.25, "rd_expense": 50_000_000, "capex": 10_000_000, "change_wc": 20_000_000}
        ],
        "terminal": {"final_year": 2040, "terminal_value": 4_000_000_000},
        "tax_rate": 0.20
    },
    "perturbations": [
        {"variable": "wacc", "low_value": 0.08, "high_value": 0.12, "label": "WACC ±2pp"},
        {"variable": "pos", "low_value": 0.40, "high_value": 0.70, "label": "PoS 40-70%"},
        {"variable": "revenue_multiplier", "low_value": 0.70, "high_value": 1.30, "label": "Peak Sales ±30%"},
        {"variable": "sga_multiplier", "low_value": 0.80, "high_value": 1.20, "label": "SG&A ±20%"},
        {"variable": "tax_rate", "low_value": 0.15, "high_value": 0.25, "label": "Tax Rate 15-25%"}
    ]
}


def apply_perturbation(base: Dict[str, Any], variable: str, value: float) -> Dict[str, Any]:
    """Apply a single variable perturbation and return perturbed copy."""
    perturbed = copy.deepcopy(base)

    if variable == "wacc":
        perturbed["wacc"] = value
    elif variable == "pos":
        perturbed["pos"] = value
    elif variable == "tax_rate":
        perturbed["tax_rate"] = value
    elif variable == "revenue_multiplier":
        for cf in perturbed["cash_flows"]:
            cf["revenue"] = cf["revenue"] * value
        if "terminal" in perturbed:
            perturbed["terminal"]["terminal_value"] = perturbed["terminal"]["terminal_value"] * value
    elif variable == "sga_multiplier":
        for cf in perturbed["cash_flows"]:
            cf["sga_pct"] = cf["sga_pct"] * value
    elif variable == "cogs_multiplier":
        for cf in perturbed["cash_flows"]:
            cf["cogs_pct"] = cf["cogs_pct"] * value
    elif variable == "rd_multiplier":
        for cf in perturbed["cash_flows"]:
            cf["rd_expense"] = cf["rd_expense"] * value
    else:
        raise ValueError(f"Unknown perturbation variable: {variable}")

    return perturbed


def run_sensitivity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    npv_module = _load_npv_module()
    base_case = input_data["base_case"]
    base_result = npv_module.compute_rnpv(base_case)
    base_rnpv = base_result["rnpv"]

    sensitivities: List[Dict[str, Any]] = []
    for pert in input_data["perturbations"]:
        var = pert["variable"]
        low = pert["low_value"]
        high = pert["high_value"]
        label = pert.get("label", var)

        low_case = apply_perturbation(base_case, var, low)
        high_case = apply_perturbation(base_case, var, high)
        low_rnpv = npv_module.compute_rnpv(low_case)["rnpv"]
        high_rnpv = npv_module.compute_rnpv(high_case)["rnpv"]

        delta_low = low_rnpv - base_rnpv
        delta_high = high_rnpv - base_rnpv
        range_size = abs(delta_high - delta_low)

        sensitivities.append({
            "variable": var,
            "label": label,
            "low_value": low,
            "high_value": high,
            "base_rnpv": base_rnpv,
            "low_rnpv": low_rnpv,
            "high_rnpv": high_rnpv,
            "delta_low": delta_low,
            "delta_high": delta_high,
            "range": range_size,
            "range_pct_of_base": range_size / abs(base_rnpv) * 100 if base_rnpv != 0 else None
        })

    # Sort descending by range (widest first — tornado top)
    sensitivities.sort(key=lambda x: x["range"], reverse=True)

    return {
        "base_rnpv": base_rnpv,
        "sensitivities": sensitivities,
        "disclaimer": "One-way sensitivity only — does not capture correlated inputs. Confidence = minimum of input confidences."
    }


def main():
    parser = argparse.ArgumentParser(description="Sensitivity (tornado) analysis for rNPV (pharmaintel v3.0.0)")
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

    result = run_sensitivity(input_data)
    print(json.dumps(result, indent=args.indent))


if __name__ == "__main__":
    main()
