#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
volatility_beta.py — Volatilite + piyasa duyarlılığı.

Yıllık/rolling volatilite, aşağı-yön sapması, beta + Jensen alfa + R², up/down beta,
ve fon–endeks–FX–akran korelasyon matrisi. Benchmark/FX/akran serileri ortak tarih
ekseninde inner-join edilir.

Girdi: {nav, benchmark?, risk_free?:{annual}, fx?, peers?:{label:[{date,price}]},
        rolling_window?=21}. Konvansiyon: saf stdlib; EOD; karar-destek; çökmez.
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


def annualized_vol(rets, ppy):
    s = fm.stdev(rets)
    return None if s is None else s * math.sqrt(ppy)


def rolling_vol(rets, window, ppy):
    if len(rets) < window or window < 2:
        return []
    out = []
    for i in range(window, len(rets) + 1):
        s = fm.stdev(rets[i - window:i])
        out.append(fm._round(s * math.sqrt(ppy)) if s is not None else None)
    return out


def beta_alpha(fund_rets, bench_rets, rf_annual, ppy):
    pairs = [(a, b) for a, b in zip(fund_rets, bench_rets) if a is not None and b is not None]
    if len(pairs) < 3:
        return {"beta": None, "alpha_jensen": None, "r_squared": None, "correlation": None}
    fr = [a for a, _ in pairs]
    br = [b for _, b in pairs]
    cov = fm.covariance(fr, br)
    var_b = fm.covariance(br, br)
    beta = cov / var_b if (cov is not None and var_b) else None
    corr = fm.correlation(fr, br)
    rf_d = (1.0 + (rf_annual or 0.0)) ** (1.0 / ppy) - 1.0
    mf, mb = fm.mean(fr), fm.mean(br)
    alpha = None
    if beta is not None and mf is not None and mb is not None:
        # günlük Jensen alfa → yıllıklandır
        a_d = (mf - rf_d) - beta * (mb - rf_d)
        alpha = (1.0 + a_d) ** ppy - 1.0
    return {"beta": fm._round(beta), "alpha_jensen": fm._round(alpha),
            "r_squared": fm._round(corr * corr if corr is not None else None),
            "correlation": fm._round(corr)}


def up_down_beta(fund_rets, bench_rets):
    upf, upb, dnf, dnb = [], [], [], []
    for a, b in zip(fund_rets, bench_rets):
        if a is None or b is None:
            continue
        if b > 0:
            upf.append(a)
            upb.append(b)
        elif b < 0:
            dnf.append(a)
            dnb.append(b)

    def _beta(fr, br):
        cov = fm.covariance(fr, br)
        var = fm.covariance(br, br)
        return cov / var if (cov is not None and var) else None

    return {"up_beta": fm._round(_beta(upf, upb)), "down_beta": fm._round(_beta(dnf, dnb))}


def correlation_matrix(named_returns):
    labels = list(named_returns.keys())
    mat = fm.corr_matrix([named_returns[l] for l in labels])
    return {"labels": labels, "matrix": [[fm._round(x) for x in row] for row in mat]}


def analyze(payload):
    nav = fm.normalize_nav(payload.get("nav", payload) if isinstance(payload, dict) else payload)
    prices, dates = nav["prices"], nav["dates"]
    if len(prices) < 3:
        return {"error": "yetersiz NAV serisi", "disclaimer": DISCLAIMER}
    ppy, basis = fm.trading_days_per_year(dates)
    rets = fm.simple_returns(prices)
    rf = None
    if isinstance(payload, dict) and isinstance(payload.get("risk_free"), dict):
        rf = fm.to_float(payload["risk_free"].get("annual"))
        if rf is not None and rf > 1.5:
            rf /= 100.0
    window = int(fm.to_float(payload.get("rolling_window")) or 21) if isinstance(payload, dict) else 21

    out = {
        "points": len(prices), "ppy": ppy, "ppy_basis": basis,
        "annualized_volatility": fm._round(annualized_vol(rets, ppy)),
        "downside_deviation_annual": fm._round((fm.downside_deviation(rets, 0.0) or 0) * math.sqrt(ppy)) if fm.downside_deviation(rets, 0.0) is not None else None,
        "rolling_volatility_last": (rolling_vol(rets, window, ppy)[-1] if rolling_vol(rets, window, ppy) else None),
        "rolling_window": window,
        "basis": "NAV gün-sonu (EOD)", "disclaimer": DISCLAIMER,
    }

    bench = payload.get("benchmark") if isinstance(payload, dict) else None
    named = {"fund": rets}
    if bench:
        bnav = fm.normalize_nav(bench)
        _, aligned = fm.align_series(nav, bnav)
        if len(aligned) == 2 and len(aligned[0]) >= 3:
            fr, br = fm.simple_returns(aligned[0]), fm.simple_returns(aligned[1])
            out["market_sensitivity"] = beta_alpha(fr, br, rf, ppy)
            out["up_down_beta"] = up_down_beta(fr, br)
            named["benchmark"] = br[-len(fr):]
            named["fund"] = fr
    if isinstance(payload, dict) and payload.get("fx"):
        fxnav = fm.normalize_nav(payload["fx"])
        _, al = fm.align_series(nav, fxnav)
        if len(al) == 2 and len(al[0]) >= 3:
            named["fx"] = fm.simple_returns(al[1])
            named["fund"] = fm.simple_returns(al[0])
    if isinstance(payload, dict) and isinstance(payload.get("peers"), dict):
        for lab, series in payload["peers"].items():
            pnav = fm.normalize_nav(series)
            _, al = fm.align_series(nav, pnav)
            if len(al) == 2 and len(al[1]) >= 3:
                named[f"peer:{lab}"] = fm.simple_returns(al[1])
    if len(named) >= 2:
        # ortak uzunluğa kırp
        m = min(len(v) for v in named.values())
        named = {k: v[-m:] for k, v in named.items()}
        out["correlation_matrix"] = correlation_matrix(named)
    return out


def _run_selftest():
    nav = fm._synthetic_nav(300)
    payload = {
        "nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])],
        "benchmark": [{"date": d, "price": p * 1.01} for d, p in zip(nav["dates"], nav["prices"])],
        "risk_free": {"annual": 0.40},
    }
    res = analyze(payload)
    assert res["annualized_volatility"] is not None
    assert res["market_sensitivity"]["beta"] is not None
    assert "correlation_matrix" in res
    print("== volatility_beta: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "volatility_beta", "vol": res["annualized_volatility"],
            "beta": res["market_sensitivity"]["beta"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Volatilite + beta/alfa + korelasyon (karar-destek).")
    ap.add_argument("--file", help="{nav, benchmark?, fx?, peers?, risk_free?, rolling_window?} JSON")
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
