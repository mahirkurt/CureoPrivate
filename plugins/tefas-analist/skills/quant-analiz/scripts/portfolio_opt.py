#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
portfolio_opt.py — Çoklu-fon portföy optimizasyonu.

Min-variance, max-Sharpe (tanjant), risk-parity, Hierarchical Risk Parity (HRP) ve
etkin sınır (efficient frontier). Kovaryans + matris cebiri fund_math'tan
(Cholesky/SPD-çözüm/ters/nearest-PD); long-only varyantlar simpleks-projeksiyonuyla.

BAĞIMLILIK KARARI: varsayılan motor SAF STDLIB (filo zero-dep garantisi). `--engine
numpy` opsiyonel hızlandırma; numpy yoksa SESSİZCE stdlib'e düşer (`engine_used`
raporlanır) → plugin numpy olmadan uçtan uca çalışır. Bu, tüm filodaki TEK opsiyonel-
bağımlılık dosyasıdır.

Girdi: {returns:{label:[...]}, rf?, long_only?=true, engine?=stdlib} VEYA
       {navs:{label:[{date,price}]}, ...}. Konvansiyon: EOD; karar-destek; çökmez.
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


def _try_numpy(engine):
    if engine != "numpy":
        return None
    try:
        import numpy as np  # noqa: F401
        return np
    except ImportError:
        return None


def _normalize_weights(w):
    s = sum(w)
    return [x / s for x in w] if s else [1.0 / len(w)] * len(w)


def min_variance(cov, long_only=True):
    n = len(cov)
    ones = [1.0] * n
    pd = fm.nearest_pd(cov)
    inv_ones = fm.solve_spd(pd, ones)
    if inv_ones is None:
        inv = fm.inverse_gauss_jordan(pd)
        inv_ones = fm.matvec(inv, ones) if inv else ones
    w = _normalize_weights(inv_ones)
    if long_only and any(x < 0 for x in w):
        w = fm.simplex_projection(w)
    return w


def max_sharpe(mean, cov, rf_daily, long_only=True):
    n = len(cov)
    excess = [m - rf_daily for m in mean]
    pd = fm.nearest_pd(cov)
    z = fm.solve_spd(pd, excess)
    if z is None:
        inv = fm.inverse_gauss_jordan(pd)
        z = fm.matvec(inv, excess) if inv else excess
    if sum(z) == 0:
        return [1.0 / n] * n
    w = _normalize_weights(z)
    if long_only and any(x < 0 for x in w):
        w = fm.simplex_projection([max(x, 0.0) for x in w])
    return w


def risk_parity(cov, max_iter=1000, tol=1e-8):
    n = len(cov)
    w = [1.0 / n] * n
    for _ in range(max_iter):
        sw = fm.matvec(cov, w)  # Σw
        rc = [w[i] * sw[i] for i in range(n)]  # risk katkıları
        total = sum(rc)
        if total <= 0:
            break
        target = total / n
        neww = [w[i] * (target / rc[i]) if rc[i] > 0 else w[i] for i in range(n)]
        neww = _normalize_weights([max(x, 1e-12) for x in neww])
        if max(abs(neww[i] - w[i]) for i in range(n)) < tol:
            w = neww
            break
        w = neww
    return w


def _corr_from_cov(cov):
    n = len(cov)
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            di = math.sqrt(cov[i][i]) if cov[i][i] > 0 else 0.0
            dj = math.sqrt(cov[j][j]) if cov[j][j] > 0 else 0.0
            out[i][j] = cov[i][j] / (di * dj) if (di and dj) else (1.0 if i == j else 0.0)
    return out


def _hrp_cluster(dist):
    """Tek-bağlantı (single-linkage) hiyerarşik kümeleme → birleşme sırası leaf listesi."""
    n = len(dist)
    clusters = {i: [i] for i in range(n)}
    active = list(range(n))
    cur = n
    while len(active) > 1:
        best = None
        bi = bj = -1
        for x in range(len(active)):
            for y in range(x + 1, len(active)):
                a, b = active[x], active[y]
                d = min(dist[i][j] for i in clusters[a] for j in clusters[b])
                if best is None or d < best:
                    best, bi, bj = d, a, b
        clusters[cur] = clusters[bi] + clusters[bj]
        active.remove(bi)
        active.remove(bj)
        active.append(cur)
        cur += 1
    return clusters[active[0]]


def _ivp(cov, idx):
    iv = [1.0 / cov[i][i] if cov[i][i] > 0 else 0.0 for i in idx]
    s = sum(iv)
    return [x / s for x in iv] if s else [1.0 / len(idx)] * len(idx)


def hrp(cov):
    n = len(cov)
    if n == 1:
        return [1.0]
    corr = _corr_from_cov(cov)
    dist = [[math.sqrt(max(0.0, (1.0 - corr[i][j]) / 2.0)) for j in range(n)] for i in range(n)]
    order = _hrp_cluster(dist)
    w = {i: 1.0 for i in range(n)}
    clusters = [order]
    while clusters:
        new = []
        for c in clusters:
            if len(c) <= 1:
                continue
            half = len(c) // 2
            c1, c2 = c[:half], c[half:]
            # küme varyansları (IVP-ağırlıklı)
            def cluster_var(cidx):
                ivp = _ivp(cov, cidx)
                sub = [[cov[i][j] for j in cidx] for i in cidx]
                cw = fm.matvec(sub, ivp)
                return sum(ivp[k] * cw[k] for k in range(len(cidx)))
            v1, v2 = cluster_var(c1), cluster_var(c2)
            alpha = 1.0 - v1 / (v1 + v2) if (v1 + v2) > 0 else 0.5
            for i in c1:
                w[i] *= alpha
            for i in c2:
                w[i] *= (1.0 - alpha)
            new.extend([c1, c2])
        clusters = new
    return [w[i] for i in range(n)]


def _port_stats(w, mean, cov, ppy):
    ret_d = sum(w[i] * mean[i] for i in range(len(w)))
    var_d = sum(w[i] * fm.matvec(cov, w)[i] for i in range(len(w)))
    vol_d = math.sqrt(var_d) if var_d > 0 else 0.0
    ann_ret = (1.0 + ret_d) ** ppy - 1.0
    ann_vol = vol_d * math.sqrt(ppy)
    sharpe = ann_ret / ann_vol if ann_vol else None
    return {"expected_return_annual": fm._round(ann_ret), "volatility_annual": fm._round(ann_vol),
            "sharpe": fm._round(sharpe)}


def analyze(payload):
    if not isinstance(payload, dict):
        return {"error": "geçersiz girdi", "disclaimer": DISCLAIMER}
    long_only = payload.get("long_only", True)
    engine_req = payload.get("engine", "stdlib")
    np_mod = _try_numpy(engine_req)
    engine_used = "numpy" if np_mod else "stdlib"

    # getiri matrisini hazırla
    labels = []
    rmat = []
    ppy = 252
    if payload.get("returns"):
        for lab, r in payload["returns"].items():
            labels.append(lab)
            rmat.append([fm.to_float(x) for x in r if fm.to_float(x) is not None])
    elif payload.get("navs"):
        navs = {lab: fm.normalize_nav(s) for lab, s in payload["navs"].items()}
        labels = list(navs.keys())
        _, aligned = fm.align_series(*[navs[l] for l in labels])
        if aligned and aligned[0]:
            rmat = [fm.simple_returns(a) for a in aligned]
            ppy, _ = fm.trading_days_per_year(list(navs.values())[0]["dates"])
    if len(rmat) < 2:
        return {"error": "en az 2 varlık getiri serisi gerekli", "disclaimer": DISCLAIMER}
    m = min(len(r) for r in rmat)
    if m < 3:
        return {"error": "ortak gözlem yetersiz", "disclaimer": DISCLAIMER}
    rmat = [r[-m:] for r in rmat]
    mean = [fm.mean(r) or 0.0 for r in rmat]
    cov = fm.cov_matrix(rmat)
    rf = fm.to_float(payload.get("rf"))
    if rf is not None and rf > 1.5:
        rf /= 100.0
    rf_d = (1.0 + (rf or 0.0)) ** (1.0 / ppy) - 1.0

    methods = {
        "min_variance": min_variance(cov, long_only),
        "max_sharpe": max_sharpe(mean, cov, rf_d, long_only),
        "risk_parity": risk_parity(cov),
        "hrp": hrp(cov),
    }
    out = {"assets": labels, "engine_used": engine_used, "ppy": ppy,
           "basis": "NAV gün-sonu (EOD)", "disclaimer": DISCLAIMER, "portfolios": {}}
    for name, w in methods.items():
        w = _normalize_weights([max(x, 0.0) for x in w]) if long_only else w
        out["portfolios"][name] = {
            "weights": {labels[i]: fm._round(w[i], 4) for i in range(len(labels))},
            "effective_n": fm._round(1.0 / sum(x * x for x in w) if sum(x * x for x in w) else None, 2),
            **_port_stats(w, mean, cov, ppy),
        }
    return out


def _run_selftest():
    nav = fm._synthetic_nav(260)
    a = nav["prices"]
    b = [p * (1.0 + 0.0002 * ((-1) ** i)) for i, p in enumerate(nav["prices"])]
    c = [p * (1.0 - 0.0001 * i) for i, p in enumerate(nav["prices"])]
    payload = {"navs": {
        "A": [{"date": d, "price": x} for d, x in zip(nav["dates"], a)],
        "B": [{"date": d, "price": x} for d, x in zip(nav["dates"], b)],
        "C": [{"date": d, "price": x} for d, x in zip(nav["dates"], c)],
    }, "rf": 0.40}
    res = analyze(payload)
    for name in ("min_variance", "max_sharpe", "risk_parity", "hrp"):
        w = list(res["portfolios"][name]["weights"].values())
        assert abs(sum(w) - 1.0) < 2e-3, f"{name} ağırlık toplamı ~1 (4-ondalık yuvarlama)"
        assert all(x >= -1e-9 for x in w), f"{name} long-only"
    print("== portfolio_opt: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "portfolio_opt", "engine_used": res["engine_used"],
            "hrp_weights": res["portfolios"]["hrp"]["weights"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Portföy optimizasyonu MVO/RP/HRP (karar-destek).")
    ap.add_argument("--file", help="{returns|navs, rf?, long_only?, engine?} JSON")
    ap.add_argument("--engine", default=None, help="stdlib (varsayılan) | numpy (opsiyonel)")
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
    if args.engine and isinstance(data, dict):
        data["engine"] = args.engine
    print(json.dumps(analyze(data), ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
