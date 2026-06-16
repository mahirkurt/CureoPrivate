#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monte_carlo.py — İleri NAV simülasyonu (TAM DETERMİNİSTİK).

İki motor: (1) bootstrap — tarihsel günlük getirilerin yerine-koymalı yeniden
örneklemesi (opsiyonel blok-bootstrap ile otokorelasyon korunur); (2) GBM —
log-getirilerden μ,σ kestirip geometrik Brownian hareket. Çıktı: ufuk boyunca
yüzdebirlik konileri (P5/P25/P50/P75/P95), terminal dağılım, kayıp olasılığı,
hedef olasılığı.

DETERMİNİZM: yalnız `random.Random(seed)` (sabit varsayılan seed=20260616) kullanılır;
seed çıktıda raporlanır → aynı girdi+seed bit-bit aynı sonucu verir. Date.now/global
random YOK.

Girdi: {nav, horizon_days?=252, n_paths?=2000, engine?=both, target_return?, seed?}.
Konvansiyon: saf stdlib; EOD; karar-destek; çökmez.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER
DEFAULT_SEED = 20260616
MAX_PATHS = 20000


def _cone(paths_by_step):
    """paths_by_step: her adım için terminal-katsayı listesi → yüzdebirlik konisi."""
    cone = []
    for step_vals in paths_by_step:
        s = sorted(step_vals)
        cone.append({
            "p5": fm._round(fm.percentile(s, 0.05)),
            "p25": fm._round(fm.percentile(s, 0.25)),
            "p50": fm._round(fm.percentile(s, 0.50)),
            "p75": fm._round(fm.percentile(s, 0.75)),
            "p95": fm._round(fm.percentile(s, 0.95)),
        })
    return cone


def _simulate(rets, horizon, n_paths, seed, engine, block_len=1):
    rng = random.Random(seed)
    n_paths = max(1, min(n_paths, MAX_PATHS))
    mu = fm.mean([math.log(1 + r) for r in rets if r > -1]) or 0.0
    sigma = fm.pstdev([math.log(1 + r) for r in rets if r > -1]) or 0.0
    # her adımda tüm patikaların değerleri (growth-of-1)
    step_vals = [[] for _ in range(horizon)]
    terminals = []
    pool = [r for r in rets if r > -1]
    for _ in range(n_paths):
        val = 1.0
        for t in range(horizon):
            if engine == "gbm":
                z = rng.gauss(0.0, 1.0)
                step = math.exp((mu - 0.5 * sigma * sigma) + sigma * z)
            else:  # bootstrap
                if block_len > 1 and pool:
                    start = rng.randrange(len(pool))
                    step = 1.0
                    for k in range(block_len):
                        step *= (1.0 + pool[(start + k) % len(pool)])
                    step = step ** (1.0 / block_len)
                else:
                    step = 1.0 + (rng.choice(pool) if pool else 0.0)
            val *= step
            step_vals[t].append(val)
        terminals.append(val)
    return step_vals, terminals


def analyze(payload):
    nav = fm.normalize_nav(payload.get("nav", payload) if isinstance(payload, dict) else payload)
    prices = nav["prices"]
    if len(prices) < 20:
        return {"error": "yetersiz NAV serisi (>=20 getiri gerekli)", "disclaimer": DISCLAIMER,
                "note": "dağılımı karakterize etmek için en az ~20 nokta önerilir"}
    rets = fm.simple_returns(prices)
    horizon = int(fm.to_float(payload.get("horizon_days")) or 252) if isinstance(payload, dict) else 252
    horizon = max(1, min(horizon, 1260))
    n_paths = int(fm.to_float(payload.get("n_paths")) or 2000) if isinstance(payload, dict) else 2000
    seed = int(fm.to_float(payload.get("seed")) or DEFAULT_SEED) if isinstance(payload, dict) else DEFAULT_SEED
    engine = (payload.get("engine") if isinstance(payload, dict) else None) or "both"
    target = fm.to_float(payload.get("target_return")) if isinstance(payload, dict) else None

    engines = ["bootstrap", "gbm"] if engine == "both" else [engine]
    result = {"horizon_days": horizon, "n_paths": min(n_paths, MAX_PATHS), "seed": seed,
              "basis": "günlük getiri; growth-of-1; deterministik (seed sabit)", "disclaimer": DISCLAIMER}
    for eng in engines:
        steps, terminals = _simulate(rets, horizon, n_paths, seed, eng)
        st = sorted(terminals)
        prob_loss = sum(1 for t in terminals if t < 1.0) / len(terminals)
        prob_target = None
        if target is not None:
            thr = 1.0 + target
            prob_target = sum(1 for t in terminals if t >= thr) / len(terminals)
        result[eng] = {
            "terminal": {
                "p5": fm._round(fm.percentile(st, 0.05)), "p50": fm._round(fm.percentile(st, 0.50)),
                "p95": fm._round(fm.percentile(st, 0.95)), "mean": fm._round(fm.mean(terminals)),
            },
            "prob_loss": fm._round(prob_loss),
            "prob_target": fm._round(prob_target),
            "cone_last": _cone(steps)[-1] if steps else None,
        }
    return result


def _run_selftest():
    nav = fm._synthetic_nav(300)
    payload = {"nav": [{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])],
               "horizon_days": 60, "n_paths": 500, "target_return": 0.10, "seed": 42}
    r1 = analyze(payload)
    r2 = analyze(payload)
    # determinizm: aynı seed → aynı P50
    assert r1["gbm"]["terminal"]["p50"] == r2["gbm"]["terminal"]["p50"], "determinizm GBM"
    assert r1["bootstrap"]["terminal"]["p50"] == r2["bootstrap"]["terminal"]["p50"], "determinizm bootstrap"
    assert r1["gbm"]["prob_loss"] is not None
    print("== monte_carlo: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "monte_carlo", "gbm_p50": r1["gbm"]["terminal"]["p50"],
            "bootstrap_p50": r1["bootstrap"]["terminal"]["p50"], "deterministic": True,
            "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monte Carlo ileri simülasyon (deterministik; karar-destek).")
    ap.add_argument("--file", help="{nav, horizon_days?, n_paths?, engine?, target_return?, seed?} JSON")
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
