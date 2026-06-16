#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fund_returns.py — NAV serisinden getiri & büyüme metrikleri.

Dönem getirileri (1a/3a/6a/ytd/1y/3y/5y), CAGR/yıllıklama, time-weighted return,
kümülatif eğri, log getiri, getiri ayrıştırma (piyasa vs aktif) ve nominal↔reel
(EVDS TÜFE, Fisher) dönüşümü. NAV birim-fiyatı zaten net-TWR temsil ettiğinden
money-weighted (IRR) için nakit akışı gerekir → varsa not düşülür, uydurulmaz.

Konvansiyon: saf stdlib; EOD; karar-destek (yatırım tavsiyesi değildir); çökmez.
CLI: `--file in.json` ({nav:[{date,price}], cpi?:[{date,value}], benchmark?:[...]}).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER

_WINDOW_DAYS = {"1m": 30, "3m": 91, "6m": 182, "1y": 365, "3y": 1095, "5y": 1825}


def _nearest_idx_on_or_before(dates, target_iso):
    """target tarihine eşit/önceki en yakın index; yoksa 0."""
    chosen = None
    for i, d in enumerate(dates):
        if d <= target_iso:
            chosen = i
        else:
            break
    return chosen if chosen is not None else 0


def period_return(prices, dates, window):
    """window ∈ {1m,3m,6m,ytd,1y,3y,5y}. Tarihli seride takvim-bazlı; tarihsizse None."""
    if not prices or not dates or len(prices) != len(dates):
        return None
    end_iso = dates[-1]
    try:
        end_d = date.fromisoformat(end_iso)
    except (ValueError, TypeError):
        return None
    if window == "ytd":
        start_iso = date(end_d.year, 1, 1).isoformat()
    else:
        days = _WINDOW_DAYS.get(window)
        if not days:
            return None
        start_iso = date.fromordinal(end_d.toordinal() - days).isoformat()
    if dates[0] > start_iso:
        return None  # yetersiz geçmiş
    i0 = _nearest_idx_on_or_before(dates, start_iso)
    p0, p1 = prices[i0], prices[-1]
    if not p0 or p0 <= 0:
        return None
    return p1 / p0 - 1.0


def cagr(prices, dates):
    if not prices or len(prices) < 2 or not dates:
        return None
    try:
        d0 = date.fromisoformat(dates[0])
        d1 = date.fromisoformat(dates[-1])
    except (ValueError, TypeError):
        return None
    years = (d1 - d0).days / 365.25
    if years <= 0 or prices[0] <= 0:
        return None
    return (prices[-1] / prices[0]) ** (1.0 / years) - 1.0


def annualize_from_daily(mean_daily, ppy):
    if mean_daily is None:
        return None
    return (1.0 + mean_daily) ** ppy - 1.0


def cumulative_curve(prices):
    if not prices or prices[0] <= 0:
        return []
    p0 = prices[0]
    return [p / p0 for p in prices]


def time_weighted_return(prices):
    """Birim-fiyat serisi için TWR = P_son/P_ilk - 1 (alt-dönem çarpımı eşdeğeri)."""
    if not prices or len(prices) < 2 or prices[0] <= 0:
        return None
    return prices[-1] / prices[0] - 1.0


def return_decomposition(fund_rets, bench_rets):
    """r_f = α + β r_b + ε ; piyasa katkısı β·mean(r_b), aktif = mean(r_f) - piyasa."""
    cov = fm.covariance(fund_rets, bench_rets)
    var_b = fm.covariance(bench_rets, bench_rets)
    if cov is None or not var_b:
        return None
    beta = cov / var_b
    mf, mb = fm.mean(fund_rets), fm.mean(bench_rets)
    if mf is None or mb is None:
        return None
    market = beta * mb
    return {"beta": fm._round(beta), "market_contribution": fm._round(market),
            "active_contribution": fm._round(mf - market)}


def real_return(nominal_ret, cpi_start, cpi_end):
    """Fisher kesin: 1+r_real = (1+r_nom)/(1+π), π = CPI_end/CPI_start - 1."""
    if nominal_ret is None or not cpi_start or not cpi_end or cpi_start <= 0:
        return None
    infl = cpi_end / cpi_start - 1.0
    return (1.0 + nominal_ret) / (1.0 + infl) - 1.0


def analyze(payload):
    nav = fm.normalize_nav(payload.get("nav", payload) if isinstance(payload, dict) else payload)
    prices, dates = nav["prices"], nav["dates"]
    note = []
    if len(prices) < 2:
        return {"error": "yetersiz NAV serisi (>=2 nokta gerekli)", "disclaimer": DISCLAIMER}

    ppy, basis = fm.trading_days_per_year(dates)
    drs = fm.simple_returns(prices)
    cpi = fm.normalize_nav(payload.get("cpi")) if isinstance(payload, dict) and payload.get("cpi") else None

    returns = {}
    for w in ("1m", "3m", "6m", "ytd", "1y", "3y", "5y"):
        nom = period_return(prices, dates, w)
        entry = {"nominal": fm._round(nom)}
        if cpi and cpi["prices"] and nom is not None and dates:
            # pencere başı/sonu CPI'yi eşle
            entry["real"] = fm._round(real_return(nom, cpi["prices"][0], cpi["prices"][-1]))
        returns[w] = entry

    cg = cagr(prices, dates)
    out = {
        "points": len(prices),
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "ppy": ppy, "ppy_basis": basis,
        "returns": returns,
        "cagr": fm._round(cg),
        "twr": fm._round(time_weighted_return(prices)),
        "annualized_from_daily": fm._round(annualize_from_daily(fm.mean(drs), ppy)),
        "cumulative_growth_of_1": fm._round(cumulative_curve(prices)[-1] if prices else None),
        "basis": "NAV gün-sonu (EOD); intraday modellenmez",
        "disclaimer": DISCLAIMER,
    }
    if isinstance(payload, dict) and payload.get("benchmark"):
        bnav = fm.normalize_nav(payload["benchmark"])
        _, aligned = fm.align_series(nav, bnav)
        if len(aligned) == 2 and len(aligned[0]) >= 3:
            dec = return_decomposition(fm.simple_returns(aligned[0]), fm.simple_returns(aligned[1]))
            if dec:
                out["decomposition"] = dec
    if not cpi:
        note.append("TÜFE verilmedi → reel getiri hesaplanmadı")
    if note:
        out["note"] = "; ".join(note)
    return out


def _run_selftest():
    nav = fm._synthetic_nav(400)
    res = analyze({"nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])],
                   "cpi": [{"date": nav["dates"][0], "value": 100}, {"date": nav["dates"][-1], "value": 140}]})
    assert res["cagr"] is not None
    assert res["returns"]["1y"]["nominal"] is not None
    assert res["returns"]["1y"].get("real") is not None
    short = analyze({"nav": [{"date": "2026-01-01", "price": 1.0}]})
    assert "error" in short
    print("== fund_returns: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "fund_returns", "cagr": res["cagr"], "ret_1y": res["returns"]["1y"],
            "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="NAV getiri & büyüme metrikleri (karar-destek).")
    ap.add_argument("--file", help="{nav:[{date,price}], cpi?, benchmark?} JSON")
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
