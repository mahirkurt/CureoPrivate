#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
concentration.py — Yoğunlaşma + örtüşme (overlap) analizi.

Herfindahl-Hirschman Index (HHI) + etkin-N, top-N yoğunlaşma, active share
(fon vs benchmark), fon–fon örtüşmesi ve dağılım drift/turnover. TEFAS holdings /
allocation çıktısından beslenir.

Girdi: {holdings:[{name|isin, weight}], benchmark_holdings?, other_fund_holdings?,
        allocation_history?:[{date, allocations:[{asset_class, percent}]}]}.
Konvansiyon: saf stdlib; karar-destek; çökmez.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER


def _norm(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _to_weights(holdings):
    """[{name|isin, weight|percent}] → {key: weight} (decimal, normalize)."""
    raw = {}
    for h in holdings or []:
        if not isinstance(h, dict):
            continue
        key = h.get("isin") or h.get("name") or h.get("asset_class") or h.get("instrument")
        w = fm.to_float(h.get("weight"))
        if w is None:
            w = fm.to_float(h.get("percent"))
        if w is None:
            w = fm.to_float(h.get("weight_pct"))
        if key is None or w is None:
            continue
        raw[str(key)] = raw.get(str(key), 0.0) + w
    total = sum(raw.values())
    if total <= 0:
        return {}, 0.0
    # yüzde mi ondalık mı? toplam ~100 ise /100
    scale = 100.0 if 50 <= total <= 1000 else (total if abs(total - 1.0) > 1e-6 else 1.0)
    return {k: v / scale for k, v in raw.items()}, total


def hhi(weights):
    if not weights:
        return None
    w = list(weights.values())
    h = sum(x * x for x in w)
    n = len(w)
    hn = (h - 1.0 / n) / (1.0 - 1.0 / n) if n > 1 else 1.0
    return {"hhi": fm._round(h, 4), "hhi_normalized": fm._round(hn, 4),
            "effective_n": fm._round(1.0 / h if h else None, 2)}


def top_n(weights, ns=(5, 10)):
    sw = sorted(weights.values(), reverse=True)
    out = {}
    for n in ns:
        out[f"top{n}_pct"] = fm._round(sum(sw[:n]) * 100.0, 2)
    return out


def active_share(fund_w, bench_w):
    keys = set(fund_w) | set(bench_w)
    return fm._round(0.5 * sum(abs(fund_w.get(k, 0.0) - bench_w.get(k, 0.0)) for k in keys), 4)


def overlap(a_w, b_w):
    keys = set(a_w) | set(b_w)
    return fm._round(sum(min(a_w.get(k, 0.0), b_w.get(k, 0.0)) for k in keys), 4)


def allocation_drift(history):
    """history: [{date, allocations:[{asset_class, percent}]}] → sınıf-bazlı Δ + turnover."""
    if not history or len(history) < 2:
        return None
    def to_map(point):
        m = {}
        for a in point.get("allocations", []):
            k = a.get("asset_class")
            v = fm.to_float(a.get("percent"))
            if k is not None and v is not None:
                m[k] = v
        return m
    first = to_map(history[0])
    last = to_map(history[-1])
    keys = set(first) | set(last)
    by_class = {k: fm._round(last.get(k, 0.0) - first.get(k, 0.0), 2) for k in keys}
    turnover = fm._round(0.5 * sum(abs(last.get(k, 0.0) - first.get(k, 0.0)) for k in keys), 2)
    return {"by_class": by_class, "turnover_pct": turnover}


def _concentration_block(fund_w, total):
    """Yoğunlaşma bloğu: HHI + etkin-N + top-N + (normalize notu)."""
    block = {"concentration": {**(hhi(fund_w) or {}), **top_n(fund_w)}, "holdings_count": len(fund_w)}
    if abs(total - 100.0) > 5 and abs(total - 1.0) > 0.05:
        block["note"] = f"ağırlık toplamı ~{round(total, 1)} (normalize edildi)"
    return block


def analyze(payload):
    """holdings/benchmark/other/allocation_history girdisinden yoğunlaşma+overlap+drift raporu."""
    if not isinstance(payload, dict):
        return {"error": "geçersiz girdi", "disclaimer": DISCLAIMER}
    out = {"basis": "TEFAS holdings / allocation", "disclaimer": DISCLAIMER}
    fund_w, total = _to_weights(payload.get("holdings"))
    if fund_w:
        out.update(_concentration_block(fund_w, total))
    # _to_weights(None) → ({}, 0.0), bu yüzden ayrı 'if payload.get(...)' guard'ı gereksiz.
    bench_w = _to_weights(payload.get("benchmark_holdings"))[0]
    if fund_w and bench_w:
        out["active_share"] = active_share(fund_w, bench_w)
    other_w = _to_weights(payload.get("other_fund_holdings"))[0]
    if fund_w and other_w:
        out["overlap_with_other"] = overlap(fund_w, other_w)
    drift = allocation_drift(payload.get("allocation_history") or [])
    if drift:
        out["allocation_drift"] = drift
    if "concentration" not in out and "allocation_drift" not in out:
        out["error"] = "holdings veya allocation_history gerekli"
    return out


def _run_selftest():
    payload = {
        "holdings": [
            {"name": "THYAO", "weight": 30}, {"name": "ASELS", "weight": 25},
            {"name": "GARAN", "weight": 20}, {"name": "EREGL", "weight": 15},
            {"name": "KCHOL", "weight": 10},
        ],
        "benchmark_holdings": [
            {"name": "THYAO", "weight": 20}, {"name": "ASELS", "weight": 20},
            {"name": "BIMAS", "weight": 60},
        ],
        "allocation_history": [
            {"date": "2026-01-01", "allocations": [{"asset_class": "Hisse Senedi", "percent": 80}, {"asset_class": "Ters Repo", "percent": 20}]},
            {"date": "2026-06-01", "allocations": [{"asset_class": "Hisse Senedi", "percent": 90}, {"asset_class": "Ters Repo", "percent": 10}]},
        ],
    }
    res = analyze(payload)
    assert res["concentration"]["effective_n"] is not None
    assert 0 <= res["active_share"] <= 1
    assert res["allocation_drift"]["turnover_pct"] == 10.0
    print("== concentration: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "concentration", "hhi": res["concentration"]["hhi"],
            "active_share": res["active_share"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Yoğunlaşma + örtüşme (karar-destek).")
    ap.add_argument("--file", help="{holdings, benchmark_holdings?, other_fund_holdings?, allocation_history?} JSON")
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
