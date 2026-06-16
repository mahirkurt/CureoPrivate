#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cost_analysis.py — Gider (TER) etkisi + ücret-adil karşılaştırma.

TER drag, brüt↔net, ücret bileşik etkisi (yıl yıl), düşük-maliyet benchmark'a karşı
başabaş (break-even) alfa ve ücret-düzeltilmiş Sharpe. NAV zaten net-ücret olduğundan
brüt-yeniden-kurulum açıkça işaretlenir.

Girdi: {ter, nav?|net_return?, gross_return?, cheap_alternative_ter?, horizon_years?,
        risk_free?, ppy?}. TER yüzde (2,25) veya ondalık (0.0225) — otomatik algılanır.
Konvansiyon: saf stdlib; karar-destek; çökmez.
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


def _as_decimal(x):
    v = fm.to_float(x)
    if v is None:
        return None
    return v / 100.0 if v > 1.0 else v  # 2.25 → 0.0225 ; 0.0225 → 0.0225


def ter_drag(gross_ann_return, ter):
    if gross_ann_return is None or ter is None:
        return None
    net = gross_ann_return - ter
    drag_bps = ter * 10000.0
    pct_of_return = (ter / gross_ann_return * 100.0) if gross_ann_return else None
    return {"net_return": fm._round(net), "drag_bps": fm._round(drag_bps, 1),
            "drag_pct_of_return": fm._round(pct_of_return, 2)}


def gross_from_net(net_return, ter):
    if net_return is None or ter is None:
        return None
    return net_return + ter


def break_even(ter_fund, ter_cheap, horizon_years):
    if ter_fund is None or ter_cheap is None:
        return None
    annual_gap = ter_fund - ter_cheap
    cumulative = (1.0 + annual_gap) ** (horizon_years or 1) - 1.0
    return {"required_outperformance_annual": fm._round(annual_gap),
            "required_outperformance_annual_bps": fm._round(annual_gap * 10000.0, 1),
            "cumulative_fee_gap_over_horizon": fm._round(cumulative)}


def fee_compounding(initial, gross_ann, ter, years):
    if gross_ann is None or ter is None:
        return []
    rows = []
    wf = wo = initial
    for y in range(1, int(years) + 1):
        wf *= (1.0 + gross_ann - ter)
        wo *= (1.0 + gross_ann)
        rows.append({"year": y, "with_fee": fm._round(wf, 2), "without_fee": fm._round(wo, 2),
                     "cumulative_drag": fm._round(wo - wf, 2)})
    return rows


def fee_adjusted_sharpe(rets, ter, rf_annual, ppy):
    """Artımlı ücreti getiriden düşerek Sharpe (ücret-adil karşılaştırma)."""
    s = fm.stdev(rets)
    m = fm.mean(rets)
    if s is None or m is None or s == 0:
        return None
    ter_d = (ter or 0.0) / ppy
    rf_d = (1.0 + (rf_annual or 0.0)) ** (1.0 / ppy) - 1.0
    return (m - ter_d - rf_d) / s * math.sqrt(ppy)


def analyze(payload):
    if not isinstance(payload, dict):
        return {"error": "geçersiz girdi", "disclaimer": DISCLAIMER}
    ter = _as_decimal(payload.get("ter"))
    if ter is None:
        return {"error": "ter gerekli", "disclaimer": DISCLAIMER}
    cheap = _as_decimal(payload.get("cheap_alternative_ter"))
    horizon = int(fm.to_float(payload.get("horizon_years")) or 5)
    rf = _as_decimal(payload.get("risk_free"))

    gross = fm.to_float(payload.get("gross_return"))
    net = fm.to_float(payload.get("net_return"))
    ppy = 252
    rets = None
    if payload.get("nav"):
        nav = fm.normalize_nav(payload["nav"])
        ppy, _ = fm.trading_days_per_year(nav["dates"])
        rets = fm.simple_returns(nav["prices"])
        if net is None and len(nav["prices"]) >= 2 and nav["prices"][0] > 0:
            net = nav["prices"][-1] / nav["prices"][0] - 1.0
    if gross is None and net is not None:
        gross = gross_from_net(net, ter)

    out = {
        "ter_annual": fm._round(ter), "ter_bps": fm._round(ter * 10000.0, 1),
        "basis": "NAV net-ücret; brüt = net + TER (yeniden-kurulum)", "disclaimer": DISCLAIMER,
    }
    if gross is not None:
        out["ter_drag"] = ter_drag(gross, ter)
        out["fee_compounding"] = fee_compounding(100.0, gross, ter, horizon)
    if cheap is not None:
        out["break_even_vs_cheap"] = break_even(ter, cheap, horizon)
    if rets:
        out["fee_adjusted_sharpe"] = fm._round(fee_adjusted_sharpe(rets, ter, rf, ppy))
    if gross is None and cheap is None and not rets:
        out["note"] = "yalnız TER verildi; gross_return/nav veya cheap_alternative_ter ile zenginleşir"
    return out


def _run_selftest():
    res = analyze({"ter": "2,25", "gross_return": 0.50, "cheap_alternative_ter": 0.50,
                   "horizon_years": 5})
    assert res["ter_annual"] == 0.0225
    assert res["ter_drag"]["net_return"] is not None
    assert res["break_even_vs_cheap"]["required_outperformance_annual_bps"] is not None
    assert len(res["fee_compounding"]) == 5
    nav = fm._synthetic_nav(260)
    res2 = analyze({"ter": 0.0225, "nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])],
                    "risk_free": 0.40})
    assert res2["fee_adjusted_sharpe"] is not None
    print("== cost_analysis: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "cost_analysis", "ter": res["ter_annual"],
            "net_return": res["ter_drag"]["net_return"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gider/TER etkisi (karar-destek).")
    ap.add_argument("--file", help="{ter, nav?|net_return?|gross_return?, cheap_alternative_ter?, horizon_years?} JSON")
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
