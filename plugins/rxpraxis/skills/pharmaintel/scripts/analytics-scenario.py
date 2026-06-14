#!/usr/bin/env python3
"""
analytics-scenario.py — Scenario forecasting (base/bull/bear) + Monte Carlo primitive
Part of pharmaintel v3.0.0 analytics framework

Usage:
    python3 analytics-scenario.py input.json
    python3 analytics-scenario.py --example

Input schema (see references/analytics-framework.md §4):
{
    "base_case": { ... full input for analytics-npv.py ... },
    "scenarios": {
        "base": {"weight": 0.50, "revenue_mult": 1.0, "pos_override": null, "wacc_override": null},
        "bull": {"weight": 0.25, "revenue_mult": 1.8, "pos_override": null, "wacc_override": null},
        "bear": {"weight": 0.25, "revenue_mult": 0.45, "pos_override": null, "wacc_override": null}
    },
    "monte_carlo": {
        "enabled": false,
        "iterations": 10000,
        "distributions": {
            "pos": {"type": "triangular", "low": 0.35, "mode": 0.55, "high": 0.75},
            "wacc": {"type": "triangular", "low": 0.08, "mode": 0.10, "high": 0.13},
            "revenue_mult": {"type": "triangular", "low": 0.60, "mode": 1.00, "high": 1.60}
        }
    }
}
"""

import argparse
import copy
import json
import os
import random
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_npv_module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics-npv.py")


def _load_npv_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("analytics_npv", _npv_module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXAMPLE_INPUT: Dict[str, Any] = {
    "base_case": {
        "asset_name": "Example Asset",
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
    "scenarios": {
        "base": {"weight": 0.50, "revenue_mult": 1.0, "pos_override": None, "wacc_override": None},
        "bull": {"weight": 0.25, "revenue_mult": 1.8, "pos_override": 0.65, "wacc_override": None},
        "bear": {"weight": 0.25, "revenue_mult": 0.45, "pos_override": 0.35, "wacc_override": 0.12}
    },
    "monte_carlo": {
        "enabled": True,
        "iterations": 10000,
        "seed": 42,
        "distributions": {
            "pos": {"type": "triangular", "low": 0.35, "mode": 0.55, "high": 0.75},
            "wacc": {"type": "triangular", "low": 0.08, "mode": 0.10, "high": 0.13},
            "revenue_mult": {"type": "triangular", "low": 0.60, "mode": 1.00, "high": 1.60}
        }
    }
}


def apply_scenario(base_case: Dict[str, Any], scenario_params: Dict[str, Any]) -> Dict[str, Any]:
    perturbed = copy.deepcopy(base_case)
    rev_mult = scenario_params.get("revenue_mult", 1.0)
    if rev_mult != 1.0:
        for cf in perturbed["cash_flows"]:
            cf["revenue"] = cf["revenue"] * rev_mult
        if "terminal" in perturbed:
            perturbed["terminal"]["terminal_value"] = perturbed["terminal"]["terminal_value"] * rev_mult
    if scenario_params.get("pos_override") is not None:
        perturbed["pos"] = scenario_params["pos_override"]
    if scenario_params.get("wacc_override") is not None:
        perturbed["wacc"] = scenario_params["wacc_override"]
    return perturbed


def run_scenarios(input_data: Dict[str, Any], npv_module) -> Dict[str, Any]:
    base_case = input_data["base_case"]
    scenarios = input_data.get("scenarios", {})
    results: Dict[str, Any] = {}
    weighted = 0.0
    total_weight = 0.0
    for scenario_name, params in scenarios.items():
        scenario_case = apply_scenario(base_case, params)
        scenario_result = npv_module.compute_rnpv(scenario_case)
        scenario_rnpv = scenario_result["rnpv"]
        weight = params.get("weight", 0)
        results[scenario_name] = {
            "weight": weight,
            "rnpv": scenario_rnpv,
            "inputs": {
                "revenue_mult": params.get("revenue_mult", 1.0),
                "pos": scenario_case["pos"],
                "wacc": scenario_case["wacc"]
            },
            "weighted_contribution": scenario_rnpv * weight
        }
        weighted += scenario_rnpv * weight
        total_weight += weight

    return {
        "scenarios": results,
        "probability_weighted_rnpv": weighted,
        "total_weight_check": total_weight
    }


def sample_triangular(dist: Dict[str, Any]) -> float:
    return random.triangular(dist["low"], dist["high"], dist["mode"])


def sample_lognormal(dist: Dict[str, Any]) -> float:
    # mean and sigma of underlying normal
    import math
    return random.lognormvariate(dist["mu"], dist["sigma"])


def sample_distribution(dist: Dict[str, Any]) -> float:
    t = dist["type"]
    if t == "triangular":
        return sample_triangular(dist)
    elif t == "lognormal":
        return sample_lognormal(dist)
    elif t == "uniform":
        return random.uniform(dist["low"], dist["high"])
    elif t == "normal":
        return random.gauss(dist["mean"], dist["sigma"])
    else:
        raise ValueError(f"Unknown distribution type: {t}")


def run_monte_carlo(input_data: Dict[str, Any], npv_module) -> Dict[str, Any]:
    mc_config = input_data.get("monte_carlo", {})
    if not mc_config.get("enabled", False):
        return {"enabled": False}

    iterations = mc_config.get("iterations", 10000)
    distributions = mc_config.get("distributions", {})
    seed = mc_config.get("seed")
    if seed is not None:
        random.seed(seed)

    base_case = input_data["base_case"]
    rnpvs: List[float] = []

    for _ in range(iterations):
        perturbed = copy.deepcopy(base_case)
        for var, dist in distributions.items():
            sampled = sample_distribution(dist)
            if var == "pos":
                perturbed["pos"] = sampled
            elif var == "wacc":
                perturbed["wacc"] = sampled
            elif var == "revenue_mult":
                for cf in perturbed["cash_flows"]:
                    cf["revenue"] = cf["revenue"] * sampled
                if "terminal" in perturbed:
                    perturbed["terminal"]["terminal_value"] = perturbed["terminal"]["terminal_value"] * sampled
            elif var == "tax_rate":
                perturbed["tax_rate"] = sampled
        rnpv = npv_module.compute_rnpv(perturbed)["rnpv"]
        rnpvs.append(rnpv)

    sorted_rnpvs = sorted(rnpvs)
    n = len(sorted_rnpvs)

    def percentile(p):
        idx = int(p / 100 * (n - 1))
        return sorted_rnpvs[idx]

    mean = sum(sorted_rnpvs) / n
    variance = sum((x - mean) ** 2 for x in sorted_rnpvs) / n
    stdev = variance ** 0.5
    prob_positive = sum(1 for x in sorted_rnpvs if x > 0) / n

    return {
        "enabled": True,
        "iterations": iterations,
        "mean": mean,
        "stdev": stdev,
        "min": sorted_rnpvs[0],
        "max": sorted_rnpvs[-1],
        "p5": percentile(5),
        "p25": percentile(25),
        "p50": percentile(50),
        "p75": percentile(75),
        "p95": percentile(95),
        "probability_positive_rnpv": prob_positive
    }


def main():
    parser = argparse.ArgumentParser(description="Scenario + Monte Carlo rNPV forecasting (pharmaintel v3.0.0)")
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

    npv_module = _load_npv_module()
    scenarios_result = run_scenarios(input_data, npv_module)
    mc_result = run_monte_carlo(input_data, npv_module)

    output = {
        "scenarios": scenarios_result,
        "monte_carlo": mc_result,
        "disclaimer": "Scenario assumptions and MC distributions are illustrative. Confidence = minimum of input confidences. Not investment advice."
    }
    print(json.dumps(output, indent=args.indent))


if __name__ == "__main__":
    main()
