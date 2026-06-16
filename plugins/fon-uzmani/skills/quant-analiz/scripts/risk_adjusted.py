#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
risk_adjusted.py — Riske göre düzeltilmiş performans oranları.

Sharpe, Sortino (aşağı-yön sapması + MAR), Calmar, Information ratio (+ tracking
error), Treynor, Omega. Türkiye risksiz oranı (gösterge tahvil / O-N) ve günlük-NAV
yıllıklama konvansiyonu açıkça raporlanır.

Girdi: {nav:[{date,price}], benchmark?, risk_free?:{annual} | {series:[{date,value}]},
        mar_annual?, max_drawdown?}. risk_free yıllık ondalık (0.45 = %45) veya yüzde.
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


def _rf_daily(rf_annual, ppy):
    if rf_annual is None:
        return 0.0
    return (1.0 + rf_annual) ** (1.0 / ppy) - 1.0


def sharpe(rets, rf_annual, ppy):
    s = fm.stdev(rets)
    m = fm.mean(rets)
    if s is None or m is None or s == 0:
        return None
    return (m - _rf_daily(rf_annual, ppy)) / s * math.sqrt(ppy)


def sortino(rets, mar_annual, ppy):
    m = fm.mean(rets)
    mar_d = _rf_daily(mar_annual, ppy)
    dd = fm.downside_deviation(rets, mar_d)
    if m is None or dd is None or dd == 0:
        return None
    return (m - mar_d) / dd * math.sqrt(ppy)


def calmar(cagr, max_drawdown):
    if cagr is None or max_drawdown is None or max_drawdown == 0:
        return None
    return cagr / abs(max_drawdown)


def information_ratio(fund_rets, bench_rets, ppy):
    pairs = [(a, b) for a, b in zip(fund_rets, bench_rets) if a is not None and b is not None]
    if len(pairs) < 2:
        return None, None
    active = [a - b for a, b in pairs]
    te = fm.stdev(active)
    ma = fm.mean(active)
    if te is None or te == 0 or ma is None:
        return None, (fm._round(te * math.sqrt(ppy)) if te else None)
    return ma / te * math.sqrt(ppy), te * math.sqrt(ppy)


def treynor(rets, beta, rf_annual, ppy):
    m = fm.mean(rets)
    if m is None or beta is None or beta == 0:
        return None
    ann = (1.0 + m) ** ppy - 1.0
    return (ann - (rf_annual or 0.0)) / beta


def omega(rets, threshold_daily=0.0):
    gains = sum(max(r - threshold_daily, 0.0) for r in rets if r is not None)
    losses = sum(max(threshold_daily - r, 0.0) for r in rets if r is not None)
    if losses == 0:
        return None
    return gains / losses


def _resolve_rf(payload, ppy):
    rf = payload.get("risk_free") if isinstance(payload, dict) else None
    if rf is None:
        return None, "verilmedi (rf=0 varsayıldı)"
    if isinstance(rf, (int, float)):
        v = float(rf)
    elif isinstance(rf, dict) and rf.get("annual") is not None:
        v = fm.to_float(rf["annual"])
    elif isinstance(rf, dict) and rf.get("series"):
        vals = [fm.to_float(x.get("value")) for x in rf["series"] if isinstance(x, dict)]
        vals = [x for x in vals if x is not None]
        v = sum(vals) / len(vals) if vals else None
    else:
        v = fm.to_float(rf)
    if v is None:
        return None, "ayrıştırılamadı (rf=0)"
    if v > 1.5:  # yüzde verilmiş (örn. 45) → ondalık
        v /= 100.0
    return v, "yıllık ondalık"


def analyze(payload):
    nav = fm.normalize_nav(payload.get("nav", payload) if isinstance(payload, dict) else payload)
    prices, dates = nav["prices"], nav["dates"]
    if len(prices) < 3:
        return {"error": "yetersiz NAV serisi", "disclaimer": DISCLAIMER}
    ppy, basis = fm.trading_days_per_year(dates)
    rets = fm.simple_returns(prices)
    rf_annual, rf_src = _resolve_rf(payload, ppy)
    mar_annual = fm.to_float(payload.get("mar_annual")) if isinstance(payload, dict) else None
    if mar_annual is not None and mar_annual > 1.5:
        mar_annual /= 100.0
    if mar_annual is None:
        mar_annual = rf_annual

    # beta & cagr & mdd: gerekirse içeride türet
    cg = (prices[-1] / prices[0]) ** (365.25 / max(1, _days(dates))) - 1.0 if prices[0] > 0 else None
    mdd = payload.get("max_drawdown") if isinstance(payload, dict) else None
    if mdd is None:
        mdd = _max_drawdown(prices)
    beta = None
    ir = te = None
    bench = payload.get("benchmark") if isinstance(payload, dict) else None
    if bench:
        bnav = fm.normalize_nav(bench)
        _, aligned = fm.align_series(nav, bnav)
        if len(aligned) == 2 and len(aligned[0]) >= 3:
            fr, br = fm.simple_returns(aligned[0]), fm.simple_returns(aligned[1])
            cov = fm.covariance(fr, br)
            var_b = fm.covariance(br, br)
            beta = cov / var_b if (cov is not None and var_b) else None
            ir, te = information_ratio(fr, br, ppy)

    n = len(rets)
    conf = "düşük (n<30)" if n < 30 else ("orta (n<120)" if n < 120 else "yüksek")
    out = {
        "points": len(prices), "ppy": ppy, "ppy_basis": basis, "n_returns": n, "confidence": conf,
        "sharpe": fm._round(sharpe(rets, rf_annual, ppy)),
        "sortino": fm._round(sortino(rets, mar_annual, ppy)),
        "calmar": fm._round(calmar(cg, mdd)),
        "information_ratio": fm._round(ir),
        "tracking_error_annual": fm._round(te),
        "treynor": fm._round(treynor(rets, beta, rf_annual, ppy)),
        "omega": fm._round(omega(rets, _rf_daily(rf_annual, ppy))),
        "conventions": {"risk_free_annual": fm._round(rf_annual), "risk_free_source": rf_src,
                        "mar_annual": fm._round(mar_annual), "annualization_ppy": ppy,
                        "beta_used": fm._round(beta), "max_drawdown_used": fm._round(mdd)},
        "basis": "NAV gün-sonu (EOD)", "disclaimer": DISCLAIMER,
    }
    notes = []
    if rf_annual is None:
        notes.append("risksiz oran verilmedi → Sharpe/Sortino rf=0 ile hesaplandı")
    if not bench:
        notes.append("benchmark verilmedi → IR/Treynor hesaplanamadı")
    if notes:
        out["note"] = "; ".join(notes)
    return out


def _days(dates):
    from datetime import date as _d
    try:
        return max(1, (_d.fromisoformat(dates[-1]) - _d.fromisoformat(dates[0])).days)
    except (ValueError, TypeError, IndexError):
        return max(1, len(dates))


def _max_drawdown(prices):
    if not prices:
        return None
    peak = prices[0]
    mdd = 0.0
    for p in prices:
        if p > peak:
            peak = p
        if peak > 0:
            dd = p / peak - 1.0
            if dd < mdd:
                mdd = dd
    return mdd


def _run_selftest():
    nav = fm._synthetic_nav(300)
    res = analyze({
        "nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])],
        "risk_free": {"annual": 0.40},
        "benchmark": [{"date": d, "price": p * 0.99} for d, p in zip(nav["dates"], nav["prices"])],
    })
    assert res["sharpe"] is not None, "sharpe"
    assert res["sortino"] is not None, "sortino"
    assert res["information_ratio"] is not None, "IR"
    # rf yüzde-formatı normalize
    rf, _ = _resolve_rf({"risk_free": 45}, 252)
    assert abs(rf - 0.45) < 1e-9
    print("== risk_adjusted: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "risk_adjusted", "sharpe": res["sharpe"], "sortino": res["sortino"],
            "information_ratio": res["information_ratio"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Riske göre düzeltilmiş performans (karar-destek).")
    ap.add_argument("--file", help="{nav, risk_free?, benchmark?, mar_annual?, max_drawdown?} JSON")
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
