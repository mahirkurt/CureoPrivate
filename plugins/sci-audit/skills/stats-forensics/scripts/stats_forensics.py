#!/usr/bin/env python3
"""Deterministic statistical-consistency checks (sci-audit axis C).

Stdlib-only implementation (math only, no scipy/numpy) of:

  * statcheck-style recomputation: extract reported inline test statistics
    (t, F, chi-square, r, z) with their df and reported p, recompute the p from
    the statistic, and flag inconsistencies — especially DECISION-CHANGING ones
    (reported significant but recomputed not, or vice versa). A one-tailed
    reclassification pass downgrades likely one-sided reports to an info note
    instead of a false inconsistency.
  * GRIM (Granularity-Related Inconsistency of Means) and GRIMMER (its variance
    counterpart): a reported mean / SD of an integer-item measure over N
    observations must be achievable; flag values that are arithmetically
    impossible.
  * Confidence-interval consistency: the point estimate must lie within its CI,
    and for a labelled ratio/difference the CI's exclusion of the null must
    agree with a co-reported p-value.
  * Percentage-sum sanity: a set of percentages that should partition 100% but
    does not (allowing a small rounding band).
  * Subgroup-N sanity: subgroup counts that do not sum to the stated total N.
  * Effect-size plausibility: |r|>1, impossible proportions, negative df.

Decimal COMMA (Turkish / APA-TR, e.g. `t(38)=2,50, p=0,02`) is parsed as well
as the decimal point. CDFs are implemented from standard continued-fraction /
series expansions; math.erfc covers the normal tail exactly.

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

# Two number classes so decimal COMMA (Turkish/APA-TR) is parsed without eating
# the value-separating comma in F(df1, df2):
#   _DEC — a single value that may use "." OR "," as the decimal separator.
#   _INT — a df inside F(df1, df2); integer or dot-decimal only, so the comma
#          between the two dfs is never swallowed as a decimal.
_DEC = r"[-+]?\d*[.,]?\d+"
_INT = r"[-+]?\d+(?:\.\d+)?"
_P = rf"(?P<prel>[<=>])\s*(?P<pval>{_DEC})"

STAT_PATTERNS = [
    ("t", re.compile(rf"\bt\s*\(\s*(?P<df>{_DEC})\s*\)\s*=\s*(?P<stat>{_DEC})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("F", re.compile(rf"\bF\s*\(\s*(?P<df1>{_INT})\s*,\s*(?P<df2>{_INT})\s*\)\s*=\s*(?P<stat>{_DEC})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("chi2", re.compile(rf"(?:χ2|χ²|chi2|chi-square|X2)\s*\(\s*(?P<df>{_INT})\s*(?:,\s*N\s*=\s*{_INT}\s*)?\)\s*=\s*(?P<stat>{_DEC})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("r", re.compile(rf"\br\s*\(\s*(?P<df>{_DEC})\s*\)\s*=\s*(?P<stat>{_DEC})\s*,\s*p\s*{_P}", re.IGNORECASE)),
    ("z", re.compile(rf"\bz\s*=\s*(?P<stat>{_DEC})\s*,\s*p\s*{_P}", re.IGNORECASE)),
]


def _norm_decimal(s: str) -> float:
    return float(s.replace(",", "."))


def _relation_holds(prel: str, reported: float, computed: float) -> bool:
    tol = 0.01 + 0.05 * computed  # generous — rounding
    if prel == "=":
        return abs(reported - computed) <= max(tol, 0.02)
    if prel == "<":
        return computed < reported + max(tol, 0.02)
    if prel == ">":
        return computed > reported - max(tol, 0.02)
    return True


def _reported_p_consistent(prel: str, reported: float, computed: float) -> tuple[bool, bool, bool]:
    """Return (consistent, decision_changing, one_tailed_rescues)."""
    consistent = _relation_holds(prel, reported, computed)
    one_tailed_rescues = False
    if not consistent:
        one_tailed_rescues = _relation_holds(prel, reported, computed / 2.0)
    reported_sig = (reported < 0.05) if prel in ("=", "<") else (reported <= 0.05)
    computed_sig = computed < 0.05
    decision_changing = reported_sig != computed_sig
    return consistent, decision_changing, one_tailed_rescues


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
            consistent, decision_changing, one_tailed = _reported_p_consistent(prel, reported_p, computed)
            if not consistent and one_tailed and not decision_changing:
                findings.append(Finding(
                    "info", "statcheck-maybe-one-tailed",
                    f"Reported p {prel} {reported_p:g} does not match the two-sided "
                    f"p={computed:.4g} for {kind}={stat:g}, but matches a one-sided "
                    f"p={computed / 2:.4g}. Confirm the test was one-tailed and stated as such.",
                    m.group(0).strip(),
                    {"kind": kind, "reported_p": reported_p,
                     "computed_two_sided": round(computed, 6), "computed_one_sided": round(computed / 2, 6)},
                ))
                continue
            if not consistent:
                findings.append(Finding(
                    "error" if decision_changing else "warning",
                    "statcheck-inconsistent" + ("-decision" if decision_changing else ""),
                    (f"Reported p {prel} {reported_p:g} is inconsistent with the "
                     f"recomputed two-sided p={computed:.4g} for {kind}={stat:g}."
                     + (" This CHANGES the significance verdict at α=0.05."
                        if decision_changing else "")),
                    m.group(0).strip(),
                    {"kind": kind, "reported_p": reported_p, "computed_p": round(computed, 6),
                     "relation": prel, "decision_changing": decision_changing},
                ))
    return findings


# --- GRIM / GRIMMER --------------------------------------------------------

GRIM_PATTERN = re.compile(
    r"(?:mean|ortalama|M)\s*[=:]?\s*(?P<mean>\d+[.,]\d+)"
    r"[^.\n]{0,80}?\b[nN]\s*[=:]?\s*(?P<n>\d{1,4})\b",
    re.IGNORECASE,
)
# mean ... SD/SS ... n  — for GRIMMER (variance granularity)
GRIMMER_PATTERN = re.compile(
    r"(?:mean|ortalama|M)\s*[=:]?\s*(?P<mean>\d+[.,]\d+)"
    r"[^.\n]{0,40}?(?:SD|SS|std|standart sapma)\s*[=:]?\s*(?P<sd>\d+[.,]\d+)"
    r"[^.\n]{0,60}?\b[nN]\s*[=:]?\s*(?P<n>\d{1,4})\b",
    re.IGNORECASE,
)


def check_grim(text: str, max_items_scale: int = 1) -> list[Finding]:
    findings: list[Finding] = []
    for m in GRIM_PATTERN.finditer(text):
        mean_str = m.group("mean").replace(",", ".")
        n = int(m.group("n"))
        if n == 0 or n > 1000:
            continue
        decimals = len(mean_str.split(".")[1])
        mean = float(mean_str)
        granularity = 1.0 / (n * max_items_scale)
        nearest = round(mean * n * max_items_scale) / (n * max_items_scale)
        if round(abs(mean - nearest), decimals) > 0:
            if abs(mean - nearest) > 0.5 * (10 ** -decimals) + 1e-9 and granularity > 10 ** -decimals:
                findings.append(Finding(
                    "warning", "grim-inconsistent",
                    (f"Mean {m.group('mean')} is not achievable for N={n} single-integer "
                     f"observations (nearest achievable {nearest:.{decimals}f}). "
                     "Verify N, the mean, or whether the measure is multi-item (use --grim-scale)."),
                    m.group(0).strip(),
                    {"mean": mean, "n": n, "nearest_achievable": round(nearest, decimals)},
                ))
    return findings


def check_grimmer(text: str, max_items_scale: int = 1) -> list[Finding]:
    """GRIMMER: is a reported SD achievable given mean, N, integer items?

    For integer data the sum of squared deviations must be an integer, which
    bounds the achievable variance to a discrete grid. We check the reported SD
    against the nearest achievable SD at the reported precision. Conservative:
    only flags when the discrepancy clearly exceeds display rounding.
    """
    findings: list[Finding] = []
    for m in GRIMMER_PATTERN.finditer(text):
        mean = float(m.group("mean").replace(",", "."))
        sd_str = m.group("sd").replace(",", ".")
        sd = float(sd_str)
        n = int(m.group("n"))
        if n < 2 or n > 1000 or sd < 0:
            continue
        decimals = len(sd_str.split(".")[1])
        scale = max_items_scale
        # Total is an integer (sum of integer items); mean*n*scale must be near-integer.
        total = mean * n * scale
        if abs(total - round(total)) > 0.5:
            continue  # GRIM already covers the mean; don't double-flag ambiguous means
        total = round(total)
        # Sum of squares SS is an integer. variance = (SS - total^2/n) / (n-1).
        # Reconstruct the SS implied by the reported SD, and check it is (near) an integer.
        var = sd * sd
        ss = var * (n - 1) + (total * total) / (n * scale * scale)
        # ss should be an integer (in item^2 units). Distance to nearest integer:
        nearest_ss = round(ss)
        # Convert the rounding tolerance on SD into an SS tolerance.
        sd_tol = 0.5 * (10 ** -decimals)
        var_hi = (sd + sd_tol) ** 2
        var_lo = max(0.0, (sd - sd_tol) ** 2)
        ss_hi = var_hi * (n - 1) + (total * total) / (n * scale * scale)
        ss_lo = var_lo * (n - 1) + (total * total) / (n * scale * scale)
        # If no integer SS lies within the rounding band, the SD is GRIMMER-impossible.
        if math.ceil(ss_lo - 1e-9) > math.floor(ss_hi + 1e-9):
            findings.append(Finding(
                "warning", "grimmer-inconsistent",
                (f"SD {m.group('sd')} is not achievable for mean {m.group('mean')}, N={n} "
                 "integer observations (no integer sum-of-squares fits the reported precision). "
                 "Verify SD/mean/N or whether the measure is multi-item (use --grim-scale)."),
                m.group(0).strip(),
                {"mean": mean, "sd": sd, "n": n, "implied_ss": round(ss, 3), "nearest_ss": nearest_ss},
            ))
    return findings


# --- Confidence-interval consistency ---------------------------------------

CI_PATTERN = re.compile(
    r"(?P<label>\b(?:OR|HR|RR|aOR|aHR|IRR|OR\.|odds ratio|hazard ratio|risk ratio|"
    r"mean difference|MD|beta|β|b|d|g|r)\b)?\s*[=:]?\s*(?P<est>-?\d+[.,]?\d*)\s*"
    r"[,;(]?\s*(?:95\s*%\s*(?:CI|Gİ|CI:|güven aral[ıi]ğ[ıi])|CI|Gİ)\s*[:=]?\s*"
    r"\[?\(?\s*(?P<lo>-?\d+[.,]?\d*)\s*(?:-|to|–|,|;|ile)\s*(?P<hi>-?\d+[.,]?\d*)\s*\)?\]?",
    re.IGNORECASE,
)
RATIO_LABELS = {"or", "hr", "rr", "aor", "ahr", "irr", "or.", "odds ratio", "hazard ratio", "risk ratio"}


def check_confidence_intervals(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in CI_PATTERN.finditer(text):
        try:
            est = _norm_decimal(m.group("est"))
            lo = _norm_decimal(m.group("lo"))
            hi = _norm_decimal(m.group("hi"))
        except (ValueError, TypeError):
            continue
        if lo > hi:
            lo, hi = hi, lo
        # Guard against matching year ranges or unrelated numbers: require a
        # plausible CI ordering and a finite width.
        if hi - lo <= 0 or hi - lo > 1e6:
            continue
        if not (lo - 1e-6 <= est <= hi + 1e-6):
            findings.append(Finding(
                "error", "ci-excludes-estimate",
                (f"Point estimate {est:g} lies outside its reported 95% CI "
                 f"[{lo:g}, {hi:g}]. Verify the estimate or the interval."),
                m.group(0).strip(),
                {"estimate": est, "ci_low": lo, "ci_high": hi},
            ))
            continue
        label = (m.group("label") or "").strip().lower()
        if label in RATIO_LABELS:
            null = 1.0
            excludes_null = lo > null or hi < null
            # Look for a co-reported p in the same clause.
            tail = text[m.end(): m.end() + 60]
            pm = re.search(rf"p\s*{_P}", tail, re.IGNORECASE)
            if pm:
                p = _norm_decimal(pm.group("pval"))
                p_sig = p < 0.05
                if excludes_null != p_sig:
                    findings.append(Finding(
                        "warning", "ci-p-significance-mismatch",
                        (f"The 95% CI [{lo:g}, {hi:g}] "
                         + ("excludes" if excludes_null else "includes")
                         + f" the null (1) but the reported p={p:g} says the result is "
                         + ("significant" if p_sig else "non-significant") + ". These disagree."),
                        m.group(0).strip() + " " + pm.group(0).strip(),
                        {"estimate": est, "ci_low": lo, "ci_high": hi, "p": p},
                    ))
    return findings


# --- Percentage-sum + subgroup-N + effect-size plausibility ----------------

def check_percentage_sums(text: str) -> list[Finding]:
    """Flag a comma/'and'-joined list of percentages that should sum to ~100%."""
    findings: list[Finding] = []
    # A run of >=3 percentages joined by separators, allowing ", and"/" and "/
    # ", " combinations (Oxford comma + conjunction).
    for m in re.finditer(
        r"(?P<seq>\d+[.,]?\d*\s*%(?:(?:\s*(?:,|;|/|and|ve|&)\s*)+\d+[.,]?\d*\s*%){2,})", text
    ):
        seq = m.group("seq")
        vals = [_norm_decimal(v) for v in re.findall(r"(\d+[.,]?\d*)\s*%", seq)]
        if len(vals) < 3:
            continue  # 2-value lists are too ambiguous (e.g. "45% vs 55%" pairs are fine)
        total = sum(vals)
        # Band [90, 110]: catches both rounding-band partition slips (99.x) and
        # gross misses (110), while ignoring lists nowhere near a 100% partition
        # (which are likely overlapping categories, not a partition).
        if 90.0 <= total <= 110.0 and abs(total - 100.0) > 1.0 + 0.1 * len(vals):
            findings.append(Finding(
                "warning", "percentage-sum-off",
                (f"These {len(vals)} percentages sum to {total:g}%, not 100% "
                 "(beyond a rounding band). Verify the partition."),
                seq.strip()[:140],
                {"values": vals, "sum": round(total, 2)},
            ))
    return findings


SUBGROUP_PATTERN = re.compile(
    r"\b[nN]\s*=\s*(?P<total>\d{1,5})\b[^.\n]{0,80}?\(\s*(?P<parts>\d{1,5}(?:\s*(?:,|;|and|ve|/)\s*\d{1,5}){1,6})\s*\)",
)


def check_subgroup_sums(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in SUBGROUP_PATTERN.finditer(text):
        total = int(m.group("total"))
        parts = [int(x) for x in re.findall(r"\d{1,5}", m.group("parts"))]
        if len(parts) < 2:
            continue
        s = sum(parts)
        # Only flag when the parts plausibly partition the total (each < total)
        # and the sum misses it by more than rounding.
        if all(p < total for p in parts) and s != total and abs(s - total) <= max(2, total * 0.5):
            findings.append(Finding(
                "warning", "subgroup-sum-mismatch",
                (f"Subgroup counts {parts} sum to {s}, not the stated total N={total}. "
                 "Verify the group sizes."),
                m.group(0).strip()[:140],
                {"total": total, "parts": parts, "parts_sum": s},
            ))
    return findings


# --- SPRITE feasibility bound (mean/SD/N vs scale range) --------------------

# A scale/range declaration near the descriptive triplet, e.g. "(1-5)",
# "1 to 7", "0–100", "range 0-10".
RANGE_TOKEN = re.compile(
    r"(?:range\s*[:=]?\s*|scale\s+(?:of\s+)?|ölçek\s*|aral[ıi][ğg][ıi]\s*[:=]?\s*|[\(\[])?"
    r"(?P<a>\d+(?:[.,]\d+)?)\s*(?:-|–|to|ile)\s*(?P<b>\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)


def check_sprite_bounds(text: str, max_items_scale: int = 1) -> list[Finding]:
    """SPRITE-style feasibility: is a reported SD even possible for the range?

    The maximum variance of any distribution on [a, b] with mean m is
    (b - m)(m - a) (a two-point mass at the extremes). The maximum SAMPLE SD for
    N observations is sqrt(N/(N-1) * (b-m)(m-a)). A reported SD above that bound
    is infeasible regardless of the exact values — a document-internal
    impossibility, not a reproduction. Requires a nearby scale range so it never
    fires on unbounded measures.
    """
    findings: list[Finding] = []
    for m in GRIMMER_PATTERN.finditer(text):
        mean = float(m.group("mean").replace(",", "."))
        sd = float(m.group("sd").replace(",", "."))
        n = int(m.group("n"))
        if n < 2:
            continue
        window = text[max(0, m.start() - 120): m.end() + 120]
        rng = None
        for rm in RANGE_TOKEN.finditer(window):
            a = float(rm.group("a").replace(",", "."))
            b = float(rm.group("b").replace(",", "."))
            if b <= a or b - a > 1000:
                continue
            # A plausible scale range that brackets the mean.
            if a - 1e-9 <= mean <= b + 1e-9:
                rng = (a, b)
                break
        if rng is None:
            continue  # honest skip: no scale bounds → SPRITE not applicable
        a, b = rng
        sd_max = math.sqrt((b - mean) * (mean - a) * n / (n - 1)) if n > 1 else float("inf")
        # rounding tolerance on the reported SD
        decimals = len(m.group("sd").split(",")[-1].split(".")[-1]) if ("," in m.group("sd") or "." in m.group("sd")) else 0
        tol = 0.5 * (10 ** -decimals) if decimals else 0.05
        if sd > sd_max + tol + 1e-9:
            findings.append(Finding(
                "warning", "sprite-infeasible-sd",
                (f"Reported SD {m.group('sd')} exceeds the maximum possible SD "
                 f"{sd_max:.3g} for mean {m.group('mean')} on the scale range "
                 f"[{a:g}, {b:g}] with N={n}. No distribution of values in that range "
                 "can have this mean and SD."),
                m.group(0).strip()[:160],
                {"mean": mean, "sd": sd, "n": n, "range": [a, b], "sd_max": round(sd_max, 4)},
            ))
    return findings


def check_effect_sizes(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in re.finditer(r"\br\s*=\s*(-?\d+[.,]?\d*)", text, re.IGNORECASE):
        try:
            r = _norm_decimal(m.group(1))
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


# Every axis-C run carries this trigger-not-arbiter caveat (replicatio's
# numeric-consistency contract): a flagged inconsistency is a signal to review
# by hand, NOT proof of error or misconduct. Innocent causes include rounding,
# an undisclosed correction, copy-paste slips, or a different N (missing data).
STATS_CAVEAT = (
    "statcheck / GRIM / GRIMMER / SPRITE are TRIGGER signals for manual review, "
    "not a final arbiter. A flag is not proof of error or misconduct — innocent "
    "causes include rounding, an undisclosed multiple-comparison correction "
    "(statcheck does NOT recognise these), copy-paste slips, or a different N due "
    "to missing data. GRIM/GRIMMER/SPRITE apply only to integer-item scales; note "
    "false-positive risk on continuous measures. 'No findings' means 'no "
    "inconsistency in the machine-readable inline statistics', NOT 'scanned clean'."
)


def audit_text(text: str, grim_scale: int = 1) -> dict:
    findings = (
        check_statcheck(text)
        + check_grim(text, grim_scale)
        + check_grimmer(text, grim_scale)
        + check_sprite_bounds(text, grim_scale)
        + check_confidence_intervals(text)
        + check_percentage_sums(text)
        + check_subgroup_sums(text)
        + check_effect_sizes(text)
    )
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "axis": "C-statistics",
        "counts": counts,
        "findings": [asdict(f) for f in findings],
        "checks_run": ["statcheck", "grim", "grimmer", "sprite", "confidence-intervals",
                       "percentage-sums", "subgroup-sums", "effect-size"],
        "caveat": STATS_CAVEAT,
        "scope_note": (
            "Document-internal statistical consistency only — evaluates the numbers "
            "AS PRESENTED, requires no raw data, code, or reproduction. Deterministic "
            "statcheck/GRIM/GRIMMER/SPRITE/CI/percentage/subgroup/effect-size checks."
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
