#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fund_quality_score.py — Kategori-normalize 0-100 fon kalite kompoziti.

bist-analyst financial_quality_score.py mimarisini fona uyarlar: beş alt-skor
(riske-göre-düzeltilmiş getiri · tutarlılık · maliyet · AUM stabilitesi · drawdown
kontrolü), kategori-akran normalizasyonu, ağırlıklı kompozit (eksik alt-skorda
ağırlık yeniden ölçeklenir), şeffaf drivers/caveats + coverage/confidence + bant.
Ayrıca yüzdebirlik/quintile rank ve stil-drift tespiti.

Girdi: {metrics:{sharpe,sortino,max_drawdown,ulcer,ter,aum,aum_cv,volatility,...},
        category?, peers?:[{...same metrics...}]}.
Konvansiyon: saf stdlib; karar-destek; çökmez.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER

WEIGHTS = {
    "risk_adjusted": 0.32,
    "consistency": 0.18,
    "cost": 0.18,
    "aum_stability": 0.12,
    "drawdown_control": 0.20,
}

BANDS = [(75, "Yüksek"), (60, "İyi"), (40, "Orta"), (0, "Zayıf")]


def _band(score):
    if score is None:
        return None
    for thr, label in BANDS:
        if score >= thr:
            return label
    return "Zayıf"


def _percentile_rank(value, peer_values, higher_better=True):
    vals = [v for v in peer_values if v is not None]
    if value is None or len(vals) < 2:
        return None
    below = sum(1 for v in vals if (v < value) == higher_better)
    eq = sum(1 for v in vals if v == value)
    return 100.0 * (below + 0.5 * eq) / len(vals)


def percentile_rank(value, peer_values, higher_better=True):
    return _percentile_rank(value, peer_values, higher_better)


def quintile(rank):
    if rank is None:
        return None
    return min(5, int(rank // 20) + 1)


def _abs_score(value, lo, hi, higher_better=True):
    """Akran yoksa mutlak bantlama: [lo,hi] aralığını 0-100'e lineer eşle."""
    if value is None:
        return None
    x = fm.clamp((value - lo) / (hi - lo), 0.0, 1.0) if hi != lo else 0.5
    return 100.0 * (x if higher_better else 1.0 - x)


def _subscore(metrics, peers, key, higher_better, abs_lo, abs_hi):
    val = fm.to_float(metrics.get(key))
    if peers:
        pr = _percentile_rank(val, [fm.to_float(p.get(key)) for p in peers], higher_better)
        if pr is not None:
            return pr
    return _abs_score(val, abs_lo, abs_hi, higher_better)


def style_drift(weights_t0, weights_t1, threshold=0.10):
    """İki stil/ağırlık vektörü (dict) arasındaki kayma; L1/2 büyüklüğü + değişen sınıflar."""
    if not isinstance(weights_t0, dict) or not isinstance(weights_t1, dict):
        return None
    keys = set(weights_t0) | set(weights_t1)
    mag = 0.5 * sum(abs(fm.to_float(weights_t1.get(k, 0)) - fm.to_float(weights_t0.get(k, 0)) or 0.0) for k in keys)
    changed = [k for k in keys
               if abs((fm.to_float(weights_t1.get(k, 0)) or 0.0) - (fm.to_float(weights_t0.get(k, 0)) or 0.0)) >= threshold]
    return {"drift_magnitude": fm._round(mag, 4), "drift": mag >= threshold, "changed_classes": changed}


def fund_quality(metrics, category=None, peers=None):
    if not isinstance(metrics, dict):
        return {"error": "metrics dict gerekli", "disclaimer": DISCLAIMER}
    subs = {
        "risk_adjusted": _subscore(metrics, peers, "sharpe", True, -0.5, 2.0),
        "consistency": _subscore(metrics, peers, "consistency", True, 0.0, 1.0)
        if metrics.get("consistency") is not None
        else _subscore(metrics, peers, "sortino", True, -0.5, 2.5),
        "cost": _subscore(metrics, peers, "ter", False, 0.005, 0.04),
        "aum_stability": _subscore(metrics, peers, "aum", True, 1e7, 5e9),
        "drawdown_control": _subscore(metrics, peers, "max_drawdown", True, -0.6, 0.0),
    }
    # ağırlıkları mevcut alt-skorlara yeniden ölçekle
    present = {k: v for k, v in subs.items() if v is not None}
    total_w = sum(WEIGHTS[k] for k in present)
    composite = None
    if present and total_w > 0:
        composite = sum(present[k] * WEIGHTS[k] for k in present) / total_w
    coverage = len(present) / len(subs)
    conf = "yüksek" if coverage >= 0.8 else ("orta" if coverage >= 0.5 else "düşük")
    drivers = sorted(present.items(), key=lambda kv: kv[1], reverse=True)
    caveats = []
    if not peers:
        caveats.append("akran verisi yok → mutlak bantlama (güven düşer)")
    missing = [k for k in subs if subs[k] is None]
    if missing:
        caveats.append("eksik alt-skor: " + ", ".join(missing))
    return {
        "composite": fm._round(composite, 1),
        "band": _band(composite),
        "subscores": {k: fm._round(v, 1) for k, v in subs.items()},
        "weights_used": {k: WEIGHTS[k] for k in present},
        "top_drivers": [k for k, _ in drivers[:2]],
        "coverage": fm._round(coverage, 2),
        "confidence": conf,
        "caveats": caveats,
        "category": category,
        "basis": "kategori-akran normalize; EOD metrikleri",
        "disclaimer": DISCLAIMER,
    }


def analyze(payload):
    if not isinstance(payload, dict):
        return {"error": "geçersiz girdi", "disclaimer": DISCLAIMER}
    metrics = payload.get("metrics", payload)
    res = fund_quality(metrics, payload.get("category"), payload.get("peers"))
    if payload.get("peers"):
        res["sharpe_percentile"] = fm._round(
            _percentile_rank(fm.to_float(metrics.get("sharpe")),
                             [fm.to_float(p.get("sharpe")) for p in payload["peers"]], True), 1)
        res["sharpe_quintile"] = quintile(res["sharpe_percentile"])
    if payload.get("style_t0") and payload.get("style_t1"):
        res["style_drift"] = style_drift(payload["style_t0"], payload["style_t1"])
    return res


def _run_selftest():
    peers = [
        {"sharpe": 0.5, "sortino": 0.7, "ter": 0.03, "aum": 1e8, "max_drawdown": -0.4},
        {"sharpe": 1.5, "sortino": 2.0, "ter": 0.015, "aum": 2e9, "max_drawdown": -0.2},
        {"sharpe": 0.9, "sortino": 1.2, "ter": 0.022, "aum": 5e8, "max_drawdown": -0.3},
    ]
    res = analyze({"metrics": {"sharpe": 1.4, "sortino": 1.9, "ter": 0.016, "aum": 1.8e9, "max_drawdown": -0.22},
                   "category": "Hisse Senedi Fonu", "peers": peers})
    assert res["composite"] is not None and 0 <= res["composite"] <= 100
    assert res["band"] in {"Yüksek", "İyi", "Orta", "Zayıf"}
    assert res["sharpe_percentile"] is not None
    # akransız mutlak yol
    res2 = analyze({"metrics": {"sharpe": 1.0, "ter": 0.02, "max_drawdown": -0.25, "aum": 5e8}})
    assert res2["composite"] is not None
    drift = style_drift({"Hisse": 0.8, "Repo": 0.2}, {"Hisse": 0.6, "Repo": 0.4})
    assert drift["drift"] is True
    print("== fund_quality_score: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "fund_quality_score", "composite": res["composite"], "band": res["band"],
            "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fon kalite kompoziti 0-100 (karar-destek).")
    ap.add_argument("--file", help="{metrics, category?, peers?, style_t0?, style_t1?} JSON")
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
