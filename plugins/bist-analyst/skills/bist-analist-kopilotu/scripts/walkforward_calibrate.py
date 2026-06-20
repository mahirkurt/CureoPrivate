#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
walkforward_calibrate.py — BIST teknik-duruş motorunun iki kalibrasyon
parametresini (RSI eğim penceresi, göreli güç lookback) walk-forward,
SIZINTISIZ (look-ahead-free) biçimde tarar.

NEDEN VAR
---------
v1.1.1 yaması `enrich_snapshot` imzasına `rsi_slope_window` (vars. 3) ve
`rs_lookback` (vars. 13) parametrelerini açtı. Bu betik, bu iki değeri bir
ızgarada ({2,3,5} × {8,13,21}) tarayıp her hücrenin ampirik öngörü gücünü
(`backtest_posture` üzerinden Spearman ρ / IC / isabet) ölçer. Amaç, varsayılan
3/13 değerinin SAVUNULABİLİR olup olmadığına çok-rejimli kanıtla karar vermektir.

SIZINTISIZLIK
-------------
Tüm hesaplama `backtest_posture`'a delege edilir; o da duruşu `bars[:-horizon]`
ile (sonuç penceresi DIŞLANARAK) üretir. Bu betik yalnızca parametre ızgarasını
ve çok-rejim havuzlamasını yönetir; skorlama mantığını ÇOĞALTMAZ (tek kaynak:
backtest_posture → enrich_snapshot → trend_posture).

ÇOK-REJİM
---------
Tek bir backtest penceresi (özellikle gap-baskın bir hafta) motor kalitesinin
zayıf bir testidir (bkz. methodology.md §4 ve v1.1.0 yükseltme raporu §4). Bu
yüzden betik ya birden çok `frames.json`'u (`--multi`) ya da tek serinin farklı
bitiş indekslerinde dilimlenmiş pencerelerini (`--windows N`) havuzlar ve her
hücrenin metriklerini rejimler arası toplulaştırır (ortalama/medyan ρ, sıra
kararlılığı). Karar bu topluluğa dayanır, tek pencereye değil.

VERİ
----
frames.json = {"symbols": {sym: [bar,...]}, "index": [bar,...]} (kronolojik
OHLCV; backtest_posture ile aynı sözleşme). bar = {date, open, high, low,
close, volume}.

Karar-destek; yatırım tavsiyesi DEĞİLDİR. Geçmiş performans gelecek getirinin
garantisi değildir.
Bağımlılık: yalnızca Python standart kütüphanesi + backtest_posture (+ zinciri).
"""

from __future__ import annotations

import argparse
import json
import math
import sys

try:
    from backtest_posture import backtest_posture, _spearman, _pearson
except ImportError:  # pragma: no cover - sys.path fallback
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from backtest_posture import backtest_posture, _spearman, _pearson

# Kalibrasyon ızgarası (görev tanımı): RSI eğim penceresi × göreli güç lookback.
RSI_SLOPE_WINDOWS = (2, 3, 5)
RS_LOOKBACKS = (8, 13, 21)
DEFAULT_CELL = (3, 13)  # mevcut üretim varsayılanı (kıyas çapası)


# --------------------------------------------------------------------------- #
# Tek hücre değerlendirmesi
# --------------------------------------------------------------------------- #

def evaluate_cell(symbols_bars, index_bars, horizon, rsi_slope_window,
                  rs_lookback, include_relative_strength=True,
                  min_setup_bars=20):
    """Tek (rsi_slope_window, rs_lookback) hücresini değerlendirir.

    Asla istisna fırlatmaz; backtest çökerse hücre `error` ile işaretlenir.
    `errors` = skorlanması beklenirken score_norm=None kalan satır sayısı
    (anahtar-uyuşmazlığı / motor başarısızlığı yakalayıcısı). skipped = yetersiz
    bar nedeniyle (beklenen, hata değil) atlanan sembol sayısı.
    """
    cell = {"rsi_slope_window": rsi_slope_window, "rs_lookback": rs_lookback}
    try:
        res = backtest_posture(
            symbols_bars, horizon=horizon, index_bars=index_bars,
            include_relative_strength=include_relative_strength,
            min_setup_bars=min_setup_bars,
            rsi_slope_window=rsi_slope_window, rs_lookback=rs_lookback,
        )
    except Exception as exc:  # bütün-hücre hatası
        cell.update({"n": 0, "skipped": None, "errors": len(symbols_bars),
                     "spearman": None, "ic": None, "hit_abs": None,
                     "hit_rel": None, "note": f"backtest hatası: {exc}"})
        return cell

    rows = res["rows"]
    m = res["metrics"]
    skipped = sum(1 for r in rows if r.get("skipped"))
    errors = sum(1 for r in rows
                 if not r.get("skipped") and r.get("score_norm") is None)
    cell.update({
        "n": m["n_scored"],
        "skipped": skipped,
        "errors": errors,
        "spearman": m["spearman_rho"],
        "ic": m["information_coeff"],
        "hit_abs": m["hit_rate_absolute"],
        "hit_rel": m["hit_rate_vs_benchmark"],
        "note": None,
    })
    return cell


# --------------------------------------------------------------------------- #
# Tek-rejim ızgara taraması
# --------------------------------------------------------------------------- #

def run_grid(frames, horizon=1, include_relative_strength=True,
             min_setup_bars=20):
    """Tek bir frames penceresinde tüm ızgarayı tarar; hücre listesi döner."""
    symbols = frames.get("symbols", frames)
    index_bars = frames.get("index")
    cells = []
    for w in RSI_SLOPE_WINDOWS:
        for L in RS_LOOKBACKS:
            cells.append(evaluate_cell(
                symbols, index_bars, horizon, w, L,
                include_relative_strength, min_setup_bars))
    return cells


# --------------------------------------------------------------------------- #
# Çok-rejim havuzlama
# --------------------------------------------------------------------------- #

def _slice_frames(frames, end_idx):
    """frames'i [:end_idx]'e dilimler (her sembol + endeks). Bir rejim kesiti."""
    symbols = frames.get("symbols", frames)
    index_bars = frames.get("index")
    sliced_syms = {s: b[:end_idx] for s, b in symbols.items()}
    sliced = {"symbols": sliced_syms}
    if index_bars is not None:
        sliced["index"] = index_bars[:end_idx]
    return sliced


def _window_end_indices(frames, n_windows, horizon, min_setup_bars):
    """Seriyi n_windows rejim penceresine bölen bitiş indekslerini üretir.

    En küçük geçerli pencere = min_setup_bars + horizon. En büyük = tam seri.
    Aralığa eşit yayılmış (deterministik) bitiş indeksleri döner.
    """
    symbols = frames.get("symbols", frames)
    full = min(len(b) for b in symbols.values()) if symbols else 0
    lo = min_setup_bars + horizon
    if full < lo:
        return []
    if n_windows <= 1:
        return [full]
    step = (full - lo) / float(n_windows - 1)
    idxs = sorted({int(round(lo + i * step)) for i in range(n_windows)})
    return [i for i in idxs if lo <= i <= full]


def run_multiregime(regime_frames, horizon=1, include_relative_strength=True,
                    min_setup_bars=20):
    """Birden çok rejim-frames'i tarar, hücreleri rejimler arası toplulaştırır.

    regime_frames : [frames, ...] her biri bağımsız bir rejim kesiti.
    Dönen: {per_regime, aggregate} — aggregate her hücre için ρ/IC/isabet
    ortalama+medyan+std ve sıra kararlılığı (top-1/top-3 sayımı, ortalama sıra).
    """
    per_regime = []
    for rf in regime_frames:
        per_regime.append(run_grid(rf, horizon, include_relative_strength,
                                   min_setup_bars))

    # hücre anahtarı → rejimler arası metrik listeleri
    keys = [(w, L) for w in RSI_SLOPE_WINDOWS for L in RS_LOOKBACKS]
    acc = {k: {"spearman": [], "ic": [], "hit_abs": [], "n": [],
               "errors": 0, "ranks": []} for k in keys}

    for cells in per_regime:
        # bu rejimde hücreleri ρ'ya göre sırala (yüksek = iyi sıra 1).
        # BERABERLİK: aynı ρ'ya sahip hücreler AYNI (min-competition, '1224')
        # sırayı alır — yoksa ızgara ekleme sırası varsayılan hücreyi haksızca
        # cezalandırır (beraberlikler bu taramada çok yaygındır).
        valid = [(c["rsi_slope_window"], c["rs_lookback"], c["spearman"])
                 for c in cells if c["spearman"] is not None]
        valid.sort(key=lambda t: t[2], reverse=True)
        rank_of = {}
        i = 0
        while i < len(valid):
            j = i
            while j + 1 < len(valid) and valid[j + 1][2] == valid[i][2]:
                j += 1
            rank = i + 1  # grup içindeki en iyi (minimum) sıra
            for k_ in range(i, j + 1):
                w_, L_, _ = valid[k_]
                rank_of[(w_, L_)] = rank
            i = j + 1
        for c in cells:
            k = (c["rsi_slope_window"], c["rs_lookback"])
            if c["spearman"] is not None:
                acc[k]["spearman"].append(c["spearman"])
            if c["ic"] is not None:
                acc[k]["ic"].append(c["ic"])
            if c["hit_abs"] is not None:
                acc[k]["hit_abs"].append(c["hit_abs"])
            if c["n"] is not None:
                acc[k]["n"].append(c["n"])
            acc[k]["errors"] += (c["errors"] or 0)
            if k in rank_of:
                acc[k]["ranks"].append(rank_of[k])

    def _stats(xs):
        if not xs:
            return {"mean": None, "median": None, "std": None, "n": 0}
        xs2 = sorted(xs)
        n = len(xs2)
        mean = sum(xs2) / n
        median = xs2[n // 2] if n % 2 else (xs2[n // 2 - 1] + xs2[n // 2]) / 2.0
        var = sum((x - mean) ** 2 for x in xs2) / n
        return {"mean": round(mean, 4), "median": round(median, 4),
                "std": round(math.sqrt(var), 4), "n": n}

    aggregate = []
    for k in keys:
        a = acc[k]
        ranks = a["ranks"]
        aggregate.append({
            "rsi_slope_window": k[0],
            "rs_lookback": k[1],
            "is_default": (k == DEFAULT_CELL),
            "spearman": _stats(a["spearman"]),
            "ic": _stats(a["ic"]),
            "hit_abs": _stats(a["hit_abs"]),
            "mean_n": (round(sum(a["n"]) / len(a["n"]), 1) if a["n"] else None),
            "errors_total": a["errors"],
            "mean_rank": (round(sum(ranks) / len(ranks), 2) if ranks else None),
            "top1_count": sum(1 for r in ranks if r == 1),
            "top3_count": sum(1 for r in ranks if r <= 3),
            "regimes": len(ranks),
        })
    # ortalama ρ'ya göre sırala (yüksek iyi); None'lar sona.
    # `or` KULLANMA: 0.0 ortalaması (sıfır korelasyon — gerçekçi sonuç) falsy
    # olduğundan negatiflerin altına düşerdi. Sentinel -inf, gerçek değeri korur.
    aggregate.sort(
        key=lambda c: (c["spearman"]["mean"] is not None,
                       c["spearman"]["mean"] if c["spearman"]["mean"] is not None
                       else float("-inf")),
        reverse=True)
    return {"per_regime": per_regime, "aggregate": aggregate,
            "n_regimes": len(per_regime), "horizon": horizon}


# --------------------------------------------------------------------------- #
# Raporlama (düzyazı; ham JSON sızdırmaz)
# --------------------------------------------------------------------------- #

def render_grid(cells, title="Tek-rejim ızgara taraması"):
    lines = [title, "=" * len(title)]
    hdr = f"{'win':>4}{'look':>6}{'n':>5}{'skip':>6}{'err':>5}{'ρ':>9}{'IC':>9}{'hitAbs':>9}"
    lines.append(hdr)
    lines.append("-" * len(hdr))
    srt = sorted(cells,
                 key=lambda c: (c["spearman"] is not None,
                                c["spearman"] if c["spearman"] is not None
                                else float("-inf")),
                 reverse=True)
    for c in srt:
        mark = " *" if (c["rsi_slope_window"], c["rs_lookback"]) == DEFAULT_CELL else ""
        rho = f"{c['spearman']:9.3f}" if c["spearman"] is not None else f"{'—':>9}"
        ic = f"{c['ic']:9.3f}" if c["ic"] is not None else f"{'—':>9}"
        ha = f"{c['hit_abs']:9.3f}" if c["hit_abs"] is not None else f"{'—':>9}"
        sk = c["skipped"] if c["skipped"] is not None else "—"
        lines.append(f"{c['rsi_slope_window']:>4}{c['rs_lookback']:>6}{c['n']:>5}"
                     f"{str(sk):>6}{c['errors']:>5}{rho}{ic}{ha}{mark}")
    lines.append("")
    lines.append("(* = mevcut varsayılan 3/13)  ρ=Spearman, IC=bilgi katsayısı")
    lines.append("Karar-destek; yatırım tavsiyesi değildir.")
    return "\n".join(lines)


def render_multiregime(result):
    agg = result["aggregate"]
    lines = [f"Çok-rejim kalibrasyon ({result['n_regimes']} rejim, "
             f"ufuk={result['horizon']})",
             "=" * 52]
    hdr = (f"{'win':>4}{'look':>6}{'ρ̄':>9}{'ρ~':>9}{'ρσ':>8}"
           f"{'mRank':>7}{'top1':>6}{'top3':>6}{'err':>5}")
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for c in agg:
        mark = " *" if c["is_default"] else ""
        sm = c["spearman"]
        mean = f"{sm['mean']:9.3f}" if sm["mean"] is not None else f"{'—':>9}"
        med = f"{sm['median']:9.3f}" if sm["median"] is not None else f"{'—':>9}"
        std = f"{sm['std']:8.3f}" if sm["std"] is not None else f"{'—':>8}"
        mr = f"{c['mean_rank']:7.2f}" if c["mean_rank"] is not None else f"{'—':>7}"
        lines.append(f"{c['rsi_slope_window']:>4}{c['rs_lookback']:>6}{mean}{med}{std}"
                     f"{mr}{c['top1_count']:>6}{c['top3_count']:>6}{c['errors_total']:>5}{mark}")
    lines.append("")
    lines.append("ρ̄=ortalama Spearman, ρ~=medyan, ρσ=std, mRank=ortalama sıra "
                 "(1=en iyi), top1/top3=rejimlerde ilk-1/ilk-3 sayısı")
    lines.append("(* = mevcut varsayılan 3/13)")
    lines.append("Karar-destek; yatırım tavsiyesi değildir. Tek pencere zayıf "
                 "testtir; karar rejim topluluğuna dayanır.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Smoke / self-test / CLI
# --------------------------------------------------------------------------- #

def smoke(frames, horizon=1):
    """Yalnızca varsayılan (3,13) hücresini koşar; errors=0 olmalı.

    Tam ızgarayı koşmadan parametre-bağlanması ve anahtar-uyumunu saniyeler
    içinde doğrular. Dönen: (ok, cell).
    """
    w, L = DEFAULT_CELL
    symbols = frames.get("symbols", frames)
    index_bars = frames.get("index")
    cell = evaluate_cell(symbols, index_bars, horizon, w, L)
    # Smoke ANCAK en az bir satır skorlandıysa geçer; hepsi atlanırsa (n=0)
    # motor bağlanması hiç çalıştırılmamış demektir — vacuous yeşil engellenir.
    ok = (cell["errors"] == 0) and (cell["note"] is None) and ((cell["n"] or 0) > 0)
    return ok, cell


def _synthetic_frames(n_symbols=6, n_bars=48):
    """backtest_posture'ın sentetik üreticisinden çok-sembollü frames kurar."""
    from backtest_posture import _synthetic_bars
    slopes = [0.8, 0.5, 0.2, 0.02, -0.3, -0.6, 0.4, 0.1]
    syms = {}
    for i in range(n_symbols):
        sl = slopes[i % len(slopes)]
        syms[f"S{i:02d}"] = _synthetic_bars(n_bars, slope=sl, noise_phase=i * 0.7)
    idx = _synthetic_bars(n_bars, slope=0.3, noise_phase=0.0)
    return {"symbols": syms, "index": idx}


def _run_selftest():
    frames = _synthetic_frames()
    ok, cell = smoke(frames)
    grid = run_grid(frames)
    total_err = sum(c["errors"] for c in grid)
    wins = _window_end_indices(frames, 4, 1, 20)
    multi = run_multiregime([_slice_frames(frames, e) for e in wins])
    out = {
        "self_test": True,
        "smoke_ok": ok,
        "smoke_cell": cell,
        "grid_cells": len(grid),
        "grid_total_errors": total_err,
        "multiregime_n": multi["n_regimes"],
        "ok": ok and total_err == 0 and len(grid) == 9,
    }
    return out


def main(argv=None):
    p = argparse.ArgumentParser(
        description="BIST teknik-duruş walk-forward kalibrasyonu (karar-destek).")
    p.add_argument("--file", help='frames.json: {"symbols":{sym:[bars]},"index":[bars]}')
    p.add_argument("--multi", nargs="+",
                   help="birden çok rejim frames.json (her biri bir rejim)")
    p.add_argument("--windows", type=int, default=0,
                   help="tek --file serisini N rejim penceresine dilimle (>1)")
    p.add_argument("--horizon", type=int, default=1)
    p.add_argument("--min-setup", type=int, default=20)
    p.add_argument("--no-rs", action="store_true",
                   help="göreli-güç katkısını kapat (A/B)")
    p.add_argument("--smoke", action="store_true",
                   help="yalnız varsayılan (3,13) hücresi; errors=0 doğrula")
    p.add_argument("--json", action="store_true", help="ham JSON çıktı")
    args = p.parse_args(argv)
    inc_rs = not args.no_rs

    # Girdi yoksa: self-test. (--smoke verildiyse self-test'e DÜŞME — aşağıdaki
    # smoke bloğu --file eksikliğini açık hata ile bildirsin; sessiz yeşil olmasın.)
    if not args.file and not args.multi and not args.smoke:
        out = _run_selftest()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out["ok"] else 1

    # --smoke (tek --file gerektirir)
    if args.smoke:
        if not args.file:
            print("[smoke] HATA — --smoke için --file gerekir", file=sys.stderr)
            return 2
        with open(args.file, "r", encoding="utf-8") as f:
            frames = json.load(f)
        ok, cell = smoke(frames, horizon=args.horizon)
        line = (f"[smoke] varsayılan (3,13) — n={cell['n']}, "
                f"skipped={cell['skipped']}, errors={cell['errors']}, "
                f"Spearman={cell['spearman']}, IC={cell['ic']}")
        print(line)
        if not ok:
            print(f"[smoke] BAŞARISIZ — {cell.get('note') or 'errors>0'}",
                  file=sys.stderr)
        return 0 if ok else 1

    # Çok-rejim: --multi dosyaları VEYA --windows ile tek seriyi dilimle
    regime_frames = None
    if args.multi:
        regime_frames = []
        for path in args.multi:
            with open(path, "r", encoding="utf-8") as f:
                regime_frames.append(json.load(f))
    elif args.file and args.windows and args.windows > 1:
        with open(args.file, "r", encoding="utf-8") as f:
            frames = json.load(f)
        ends = _window_end_indices(frames, args.windows, args.horizon, args.min_setup)
        regime_frames = [_slice_frames(frames, e) for e in ends]
        if not regime_frames:
            print("[windows] HATA — yetersiz seri: --windows için en az "
                  "(min_setup+horizon) bar gerekir; 0 rejim üretildi.",
                  file=sys.stderr)
            return 2
        if len(ends) < args.windows:
            print(f"[windows] UYARI — istenen {args.windows} pencereden "
                  f"{len(ends)} benzersiz pencere üretildi (yuvarlama çakışması).",
                  file=sys.stderr)

    if regime_frames is not None:
        result = run_multiregime(regime_frames, horizon=args.horizon,
                                 include_relative_strength=inc_rs,
                                 min_setup_bars=args.min_setup)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(render_multiregime(result))
        return 0

    # Tek-rejim tam ızgara
    with open(args.file, "r", encoding="utf-8") as f:
        frames = json.load(f)
    cells = run_grid(frames, horizon=args.horizon,
                     include_relative_strength=inc_rs,
                     min_setup_bars=args.min_setup)
    if args.json:
        print(json.dumps(cells, ensure_ascii=False, indent=2))
    else:
        print(render_grid(cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
