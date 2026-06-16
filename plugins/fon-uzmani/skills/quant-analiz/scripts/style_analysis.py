#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
style_analysis.py — Sharpe Returns-Based Style Analysis (RBSA).

Fon getirilerini varlık-sınıfı endeks getirilerine örtük olarak çözer: stil
ağırlıkları w_k >= 0, Σw_k = 1 kısıtıyla SSE minimize edilir (Sharpe 1992 QP).
Saf-stdlib çözüm: simpleks-projeksiyonlu gradyan inişi (Duchi 2008 projeksiyonu
fund_math'tan). Küçük K için kaba ızgara çapraz-doğrulaması notu eklenir.

Girdi: {nav, asset_classes:{label:[{date,price}]}, max_iter?=2000, tol?=1e-8}.
Konvansiyon: saf stdlib; EOD; karar-destek; çökmez.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER


def _sse(fund, classes, w):
    n = len(fund)
    s = 0.0
    for t in range(n):
        pred = sum(w[k] * classes[k][t] for k in range(len(w)))
        s += (fund[t] - pred) ** 2
    return s


def rbsa(fund_rets, class_rets, max_iter=2000, tol=1e-9):
    """class_rets: list of equal-length return vectors. → weights, r2, te."""
    K = len(class_rets)
    n = len(fund_rets)
    if K == 0 or n < K + 2:
        return {"weights": None, "r_squared": None, "converged": False,
                "note": "yetersiz gözlem (n < sınıf sayısı + 2) veya sınıf yok"}
    w = [1.0 / K] * K
    # adım boyu: gradyan ölçeğine göre kaba
    lr = 1.0 / (n * (max(1.0, max(max(abs(x) for x in c) for c in class_rets)) ** 2))
    prev = None
    converged = False
    for it in range(max_iter):
        # gradyan: dSSE/dw_k = -2 Σ_t r_k,t (fund_t - Σ_j w_j r_j,t)
        resid = [fund_rets[t] - sum(w[k] * class_rets[k][t] for k in range(K)) for t in range(n)]
        grad = [-2.0 * sum(class_rets[k][t] * resid[t] for t in range(n)) for k in range(K)]
        w = [w[k] - lr * grad[k] for k in range(K)]
        w = fm.simplex_projection(w)
        cur = _sse(fund_rets, class_rets, w)
        if prev is not None and abs(prev - cur) < tol:
            converged = True
            break
        prev = cur
    # R²
    mf = fm.mean(fund_rets)
    ss_tot = sum((x - mf) ** 2 for x in fund_rets) if mf is not None else None
    ss_res = _sse(fund_rets, class_rets, w)
    r2 = (1.0 - ss_res / ss_tot) if (ss_tot and ss_tot > 0) else None
    te = (ss_res / n) ** 0.5
    return {"weights": [fm._round(x, 4) for x in w], "r_squared": fm._round(r2),
            "tracking_error_daily": fm._round(te), "converged": converged,
            "iterations": it + 1}


def analyze(payload):
    if not isinstance(payload, dict) or "asset_classes" not in payload:
        return {"error": "asset_classes gerekli ({label:[{date,price}]})", "disclaimer": DISCLAIMER}
    nav = fm.normalize_nav(payload.get("nav"))
    classes = payload["asset_classes"]
    labels = list(classes.keys())
    series = [nav] + [fm.normalize_nav(classes[l]) for l in labels]
    _, aligned = fm.align_series(*series)
    if not aligned or len(aligned[0]) < len(labels) + 3:
        return {"error": "ortak tarih ekseninde yetersiz gözlem", "disclaimer": DISCLAIMER}
    fund_rets = fm.simple_returns(aligned[0])
    class_rets = [fm.simple_returns(aligned[i + 1]) for i in range(len(labels))]
    m = min(len(fund_rets), *(len(c) for c in class_rets))
    fund_rets = fund_rets[-m:]
    class_rets = [c[-m:] for c in class_rets]
    res = rbsa(fund_rets, class_rets,
               max_iter=int(fm.to_float(payload.get("max_iter")) or 2000),
               tol=fm.to_float(payload.get("tol")) or 1e-9)
    if res.get("weights") is not None:
        res["style"] = {labels[k]: res["weights"][k] for k in range(len(labels))}
    res["asset_classes"] = labels
    res["basis"] = "NAV gün-sonu (EOD); long-only simpleks RBSA"
    res["disclaimer"] = DISCLAIMER
    return res


def _run_selftest():
    nav = fm._synthetic_nav(260)
    # iki sentetik varlık sınıfı: biri fona benzer (yüksek ağırlık beklenir), biri zıt
    a = nav["prices"]
    b = [p * (1.0 + 0.0001 * i) for i, p in enumerate(nav["prices"])]
    payload = {
        "nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], a)],
        "asset_classes": {
            "A": [{"date": d, "price": p} for d, p in zip(nav["dates"], a)],
            "B": [{"date": d, "price": p} for d, p in zip(nav["dates"], b)],
        },
    }
    res = analyze(payload)
    assert res["weights"] is not None and abs(sum(res["weights"]) - 1.0) < 1e-6, "ağırlık toplamı 1"
    assert res["style"]["A"] >= res["style"]["B"], "fona özdeş sınıf daha ağır"
    print("== style_analysis: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "style_analysis", "style": res["style"], "r_squared": res["r_squared"],
            "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="RBSA stil analizi (karar-destek).")
    ap.add_argument("--file", help="{nav, asset_classes:{label:[{date,price}]}} JSON")
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
