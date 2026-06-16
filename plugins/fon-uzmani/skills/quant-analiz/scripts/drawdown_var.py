#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drawdown_var.py — Geri çekilme (drawdown) anatomisi + kuyruk riski.

Max drawdown (tepe/dip/toparlanma/süre), Ulcer index, Pain index; VaR (historical,
parametrik-normal, Cornish-Fisher modified) ve CVaR (expected shortfall); aşağı/yukarı
yakalama (capture) oranları. İnverse-normal Acklam rasyonel yaklaşımıyla (saf math).

Girdi: {nav:[{date,price}], benchmark?, alpha?=0.95, horizon_days?=1}.
Konvansiyon: saf stdlib; EOD; karar-destek; çökmez.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER


def inv_norm(p):
    """Standart normal kuantil (Acklam). p ∈ (0,1)."""
    if p <= 0.0 or p >= 1.0:
        return None
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def drawdown_curve(prices):
    out, peak = [], prices[0] if prices else 0
    for p in prices:
        if p > peak:
            peak = p
        out.append(p / peak - 1.0 if peak > 0 else 0.0)
    return out


def max_drawdown(prices, dates):
    if not prices:
        return None
    peak = prices[0]
    peak_i = 0
    mdd = 0.0
    mdd_peak_i = mdd_trough_i = 0
    for i, p in enumerate(prices):
        if p > peak:
            peak, peak_i = p, i
        dd = p / peak - 1.0 if peak > 0 else 0.0
        if dd < mdd:
            mdd, mdd_peak_i, mdd_trough_i = dd, peak_i, i
    # toparlanma: dip sonrası tepe-fiyata dönüş
    recovery_i = None
    peak_price = prices[mdd_peak_i]
    for j in range(mdd_trough_i, len(prices)):
        if prices[j] >= peak_price:
            recovery_i = j
            break

    def _d(i):
        return dates[i] if dates and i is not None and i < len(dates) else None

    def _days_between(i, j):
        if not dates or i is None or j is None:
            return None
        try:
            from datetime import date
            return (date.fromisoformat(dates[j]) - date.fromisoformat(dates[i])).days
        except (ValueError, TypeError, IndexError):
            return None

    return {
        "mdd": fm._round(mdd),
        "peak_date": _d(mdd_peak_i), "trough_date": _d(mdd_trough_i),
        "recovery_date": _d(recovery_i),
        "drawdown_days": _days_between(mdd_peak_i, mdd_trough_i),
        "recovery_days": _days_between(mdd_trough_i, recovery_i),
        "underwater": recovery_i is None,
    }


def ulcer_index(prices):
    dd = drawdown_curve(prices)
    if not dd:
        return None
    return math.sqrt(sum((100 * x) ** 2 for x in dd) / len(dd))


def pain_index(prices):
    dd = drawdown_curve(prices)
    if not dd:
        return None
    return sum(abs(x) for x in dd) / len(dd)


def var_historical(rets, alpha=0.95):
    if len(rets) < 5:
        return None
    s = sorted(rets)
    q = fm.percentile(s, 1 - alpha)
    return None if q is None else -q


def var_parametric(rets, alpha=0.95):
    m, sd = fm.mean(rets), fm.stdev(rets)
    if m is None or sd is None:
        return None
    z = inv_norm(alpha)
    if z is None:
        return None
    return -(m - z * sd)  # alt-kuyruk; z(alpha)>0 → -(m - z*sd)


def var_cornish_fisher(rets, alpha=0.95):
    m, sd = fm.mean(rets), fm.stdev(rets)
    S, K = fm.skewness(rets), fm.kurtosis(rets)
    if m is None or sd is None:
        return None
    z = inv_norm(alpha)
    if z is None:
        return None
    S = S or 0.0
    K = K or 0.0
    zcf = (z + (z * z - 1) * S / 6 + (z ** 3 - 3 * z) * K / 24 - (2 * z ** 3 - 5 * z) * S * S / 36)
    return -(m - zcf * sd)


def cvar_historical(rets, alpha=0.95):
    if len(rets) < 5:
        return None
    s = sorted(rets)
    cutoff = fm.percentile(s, 1 - alpha)
    tail = [r for r in s if r <= cutoff]
    if not tail:
        return None
    return -(sum(tail) / len(tail))


def capture_ratios(fund_rets, bench_rets):
    up_f = up_b = dn_f = dn_b = 0.0
    nu = nd = 0
    for a, b in zip(fund_rets, bench_rets):
        if a is None or b is None:
            continue
        if b > 0:
            up_f += a
            up_b += b
            nu += 1
        elif b < 0:
            dn_f += a
            dn_b += b
            nd += 1
    uc = (up_f / up_b) if up_b else None
    dc = (dn_f / dn_b) if dn_b else None
    ratio = (uc / dc) if (uc is not None and dc) else None
    return {"up_capture": fm._round(uc), "down_capture": fm._round(dc), "capture_ratio": fm._round(ratio)}


def analyze(payload):
    nav = fm.normalize_nav(payload.get("nav", payload) if isinstance(payload, dict) else payload)
    prices, dates = nav["prices"], nav["dates"]
    if len(prices) < 5:
        return {"error": "yetersiz NAV serisi (>=5)", "disclaimer": DISCLAIMER}
    alpha = fm.to_float(payload.get("alpha")) if isinstance(payload, dict) else None
    alpha = alpha if alpha and 0 < alpha < 1 else 0.95
    horizon = int(fm.to_float(payload.get("horizon_days")) or 1) if isinstance(payload, dict) else 1
    rets = fm.simple_returns(prices)
    scale = math.sqrt(max(1, horizon))
    out = {
        "alpha": alpha, "horizon_days": horizon,
        "max_drawdown": max_drawdown(prices, dates),
        "ulcer_index": fm._round(ulcer_index(prices)),
        "pain_index": fm._round(pain_index(prices)),
        "var": {
            "historical": fm._round((var_historical(rets, alpha) or 0) * scale) if var_historical(rets, alpha) is not None else None,
            "parametric": fm._round((var_parametric(rets, alpha) or 0) * scale) if var_parametric(rets, alpha) is not None else None,
            "cornish_fisher": fm._round((var_cornish_fisher(rets, alpha) or 0) * scale) if var_cornish_fisher(rets, alpha) is not None else None,
        },
        "cvar_historical": fm._round((cvar_historical(rets, alpha) or 0) * scale) if cvar_historical(rets, alpha) is not None else None,
        "basis": "NAV gün-sonu (EOD); VaR √horizon ile ölçeklendi", "disclaimer": DISCLAIMER,
    }
    bench = payload.get("benchmark") if isinstance(payload, dict) else None
    if bench:
        bnav = fm.normalize_nav(bench)
        _, aligned = fm.align_series(nav, bnav)
        if len(aligned) == 2 and len(aligned[0]) >= 3:
            out["capture"] = capture_ratios(fm.simple_returns(aligned[0]), fm.simple_returns(aligned[1]))
    return out


def _run_selftest():
    nav = fm._synthetic_nav(300)
    res = analyze({"nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])]})
    assert res["max_drawdown"]["mdd"] is not None
    assert res["var"]["historical"] is not None
    assert res["cvar_historical"] is not None
    assert abs(inv_norm(0.975) - 1.959964) < 1e-3, "inv_norm doğruluk"
    # monoton-artan seri → mdd ~ 0
    up = [{"date": d, "price": p} for d, p in zip(nav["dates"], [1.0 + i * 0.01 for i in range(len(nav["dates"]))])]
    assert analyze({"nav": up})["max_drawdown"]["mdd"] == 0.0
    print("== drawdown_var: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "drawdown_var", "mdd": res["max_drawdown"]["mdd"],
            "var95_hist": res["var"]["historical"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Drawdown + VaR/CVaR (karar-destek).")
    ap.add_argument("--file", help="{nav, benchmark?, alpha?, horizon_days?} JSON")
    ap.add_argument("--indent", type=int, default=2)
    args = ap.parse_args(argv)
    if not args.file:
        print(json.dumps(_run_selftest(), ensure_ascii=False, indent=args.indent))
        return 0
    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Girdi okunamadı: {exc}", "disclaimer": DISCLAIMER}, ensure_ascii=False))
        return 1
    print(json.dumps(analyze(data), ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
