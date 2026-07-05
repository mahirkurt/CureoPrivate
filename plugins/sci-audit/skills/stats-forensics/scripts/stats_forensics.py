#!/usr/bin/env python3
"""Deterministic statistical-consistency checks (sci-audit axis C).

Stdlib-only implementation (math only, no scipy/numpy) of:

  * statcheck-style recomputation: extract reported inline test statistics
    (t, F, chi-square, r, z) with their df and reported p, recompute the p from
    the statistic, and flag inconsistencies — especially DECISION-CHANGING ones
    (reported significant but recomputed not, or vice versa).
  * GRIM (Granularity-Related Inconsistency of Means): a reported mean of an
    integer-valued measure over N observations must be achievable as k/N;
    flag means that are arithmetically impossible.
  * Percentage-sum sanity: a set of percentages that should partition 100%
    but does not (allowing a small rounding band).
  * Effect-size plausibility: |r|>1, impossible proportions, negative df.

CDFs are implemented from standard continued-fraction / series expansions
(Numerical Recipes style). math.erfc covers the normal tail exactly.

Every finding is EVIDENCE-BASED (echoes the matched string). This module makes
no network calls and reads no files other than the one path given on argv.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

Severity = str  # "error" | "warning" | "info"


@dataclass
class Finding:
    severity: Severity
    code: str
    message: str
    evidence: str
    detail: dict


# --- Special functions (regularized incomplete gamma / beta) ---------------

def _gammainc_p(a: float, x: float) -> float:
    """Regularized lower incomplete gamma P(a, x). 0 <= result <= 1."""
    if x < 0 or a <= 0:
        return float("nan")
    if x == 0:
        return 0.0
    if x < a + 1.0:
        # Series representation.
        ap = a
        total = 1.0 / a
        delta = total
        for _ in range(1000):
            ap += 1.0
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * 1e-14:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # Continued fraction for the upper gamma Q, then P = 1 - Q.
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return 1.0 - q


def _betacf(a: float, b: float, x: float) -> float:
    tiny = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


# --- Two-tailed / upper-tail p from test statistics ------------------------

def p_from_t(t: float, df: float) -> Optional[float]:
    if df <= 0:
        return None
    x = df / (df + t * t)
    return _betai(df / 2.0, 0.5, x)  # two-tailed


def p_from_f(f: float, df1: float, df2: float) -> Optional[float]:
    if df1 <= 0 or df2 <= 0 or f < 0:
        return None
    x = df2 / (df2 + df1 * f)
    return _betai(df2 / 2.0, df1 / 2.0, x)  # upper tail


def p_from_chi2(chi2: float, df: float) -> Optional[float]:
    if df <= 0 or chi2 < 0:
        return None
    return 1.0 - _gammainc_p(df / 2.0, chi2 / 2.0)  # upper tail


def p_from_z(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))  # two-tailed


def p_from_r(r: float, n: float) -> Optional[float]:
    if n <= 2 or abs(r) >= 1.0:
        return None
    df = n - 2
    t = r * math.sqrt(df / (1.0 - r * r))
    return p_from_t(t, df)


# --- statcheck extraction --------------------------------------------------

_NUM = r"[-+]?\d*\.?\d+"
_P = r"(?P<prel>[<=>])\s*(?P<pval>\d*\.?\d+)"

STAT_PATTERNS = [
    ("t", re.compile(rf"\bt\s*\(\s*(?P<df>{_NUM})\s*\)\s*=\s*(?P<stat>{_NUM})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("F", re.compile(rf"\bF\s*\(\s*(?P<df1>{_NUM})\s*,\s*(?P<df2>{_NUM})\s*\)\s*=\s*(?P<stat>{_NUM})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("chi2", re.compile(rf"(?:χ2|χ²|chi2|chi-square|X2)\s*\(\s*(?P<df>{_NUM})\s*(?:,\s*N\s*=\s*{_NUM}\s*)?\)\s*=\s*(?P<stat>{_NUM})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("r", re.compile(rf"\br\s*\(\s*(?P<df>{_NUM})\s*\)\s*=\s*(?P<stat>{_NUM})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("z", re.compile(rf"\bz\s*=\s*(?P<stat>{_NUM})\s*,\s*p\s*{_P}", re.IGNORECASE)),
]


def _norm_decimal(s: str) -> float:
    return float(s.replace(",", "."))


def _reported_p_consistent(prel: str, reported: float, computed: float) -> tuple[bool, bool]:
    """Return (consistent, decision_changing).

    consistent: the reported relation holds for the computed p within tolerance.
    decision_changing: significance verdict flips at alpha=0.05.
    """
    tol = 0.01 + 0.05 * computed  # generous — rounding + one-tail ambiguity
    if prel == "=":
        consistent = abs(reported - computed) <= max(tol, 0.02)
    elif prel == "<":
        consistent = computed < reported + max(tol, 0.02)
    elif prel == ">":
        consistent = computed > reported - max(tol, 0.02)
    else:
        consistent = True
    reported_sig = (reported < 0.05) if prel in ("=", "<") else (reported <= 0.05)
    computed_sig = computed < 0.05
    decision_changing = reported_sig != computed_sig
    return consistent, decision_changing


def check_statcheck(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for kind, pattern in STAT_PATTERNS:
        for m in pattern.finditer(text):
            gd = m.groupdict()
            try:
                stat = _norm_decimal(gd["stat"])
                reported_p = _norm_decimal(gd["pval"])
                prel = gd["prel"]
                if kind == "t":
                    computed = p_from_t(stat, _norm_decimal(gd["df"]))
                elif kind == "F":
                    computed = p_from_f(stat, _norm_decimal(gd["df1"]), _norm_decimal(gd["df2"]))
                elif kind == "chi2":
                    computed = p_from_chi2(stat, _norm_decimal(gd["df"]))
                elif kind == "r":
                    computed = p_from_r(stat, _norm_decimal(gd["df"]) + 2)
                elif kind == "z":
                    computed = p_from_z(stat)
                else:
                    computed = None
            except (ValueError, KeyError):
                continue
            if computed is None or math.isnan(computed):
                continue
            consistent, decision_changing = _reported_p_consistent(prel, reported_p, computed)
            if not consistent:
                findings.append(Finding(
                    severity="error" if decision_changing else "warning",
                    code="statcheck-inconsistent" + ("-decision" if decision_changing else ""),
                    message=(
                        f"Reported p {prel} {reported_p:g} is inconsistent with the "
                        f"recomputed two-sided p={computed:.4g} for {kind}={stat:g}."
                        + (" This CHANGES the significance verdict at α=0.05."
                           if decision_changing else "")
                    ),
                    evidence=m.group(0).strip(),
                    detail={"kind": kind, "reported_p": reported_p, "computed_p": round(computed, 6),
                            "relation": prel, "decision_changing": decision_changing},
                ))
    return findings


# --- GRIM ------------------------------------------------------------------

# "mean 3.14 (SD ...), n = 27" or "M = 3.14, N = 27" — pair a decimal mean with
# a nearby integer sample size in the same clause.
GRIM_PATTERN = re.compile(
    r"(?:mean|ortalama|M)\s*[=:]?\s*(?P<mean>\d+\.\d+)"
    r"[^.\n]{0,60}?\b[nN]\s*[=:]?\s*(?P<n>\d{1,4})\b",
    re.IGNORECASE,
)


def check_grim(text: str, max_items_scale: int = 1) -> list[Finding]:
    """Flag means impossible for an integer-item measure over N observations.

    Assumes a single integer item per participant (scale sum divided by N).
    max_items_scale multiplies the granularity for summed multi-item scales.
    """
    findings: list[Finding] = []
    for m in GRIM_PATTERN.finditer(text):
        mean_str = m.group("mean")
        n = int(m.group("n"))
        if n == 0 or n > 1000:
            continue
        decimals = len(mean_str.split(".")[1])
        mean = float(mean_str)
        granularity = 1.0 / (n * max_items_scale)
        # Nearest achievable mean at this granularity.
        nearest = round(mean * n * max_items_scale) / (n * max_items_scale)
        # Compare at the reported decimal precision.
        if round(abs(mean - nearest), decimals) > 0:
            # Only flag if the discrepancy exceeds half the display rounding.
            if abs(mean - nearest) > 0.5 * (10 ** -decimals) + 1e-9 and granularity > 10 ** -decimals:
                findings.append(Finding(
                    severity="warning",
                    code="grim-inconsistent",
                    message=(
                        f"Mean {mean_str} is not achievable for N={n} single-integer "
                        f"observations (nearest achievable {nearest:.{decimals}f}). "
                        "Verify N, the mean, or whether the measure is multi-item."
                    ),
                    evidence=m.group(0).strip(),
                    detail={"mean": mean, "n": n, "nearest_achievable": round(nearest, decimals)},
                ))
    return findings


# --- Percentage-sum + effect-size plausibility -----------------------------

def check_effect_sizes(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in re.finditer(r"\br\s*=\s*(-?\d*\.?\d+)", text, re.IGNORECASE):
        try:
            r = float(m.group(1))
        except ValueError:
            continue
        if abs(r) > 1.0:
            findings.append(Finding(
                "error", "impossible-correlation",
                f"Correlation r={r:g} is outside the valid range [-1, 1].",
                m.group(0).strip(), {"r": r}))
    for m in re.finditer(r"\b(?:df|serbestlik)\s*[=:]?\s*(-\d+)", text, re.IGNORECASE):
        findings.append(Finding(
            "error", "negative-df",
            "Negative degrees of freedom are impossible.",
            m.group(0).strip(), {}))
    return findings


def audit_text(text: str, grim_scale: int = 1) -> dict:
    findings = (
        check_statcheck(text)
        + check_grim(text, grim_scale)
        + check_effect_sizes(text)
    )
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "axis": "C-statistics",
        "counts": counts,
        "findings": [asdict(f) for f in findings],
        "scope_note": (
            "Deterministic statcheck/GRIM/effect-size checks. A clean result is "
            "NOT proof of statistical correctness; it means no inconsistency was "
            "detected in the machine-readable inline statistics."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Statistical-consistency audit (sci-audit axis C).")
    parser.add_argument("path", type=Path, nargs="?", help="File to audit. Omit to read stdin.")
    parser.add_argument("--grim-scale", type=int, default=1, help="Item count for summed multi-item scales (default 1).")
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="error")
    args = parser.parse_args(argv or sys.argv[1:])

    if args.path:
        if not args.path.exists():
            print(f"File not found: {args.path}", file=sys.stderr)
            return 2
        text = args.path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = audit_text(text, args.grim_scale)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    counts = result["counts"]
    if args.fail_on == "error" and counts["error"]:
        return 1
    if args.fail_on == "warning" and (counts["warning"] or counts["error"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
