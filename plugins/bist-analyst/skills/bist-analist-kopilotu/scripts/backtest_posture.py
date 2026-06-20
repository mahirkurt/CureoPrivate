#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backtest_posture.py — BIST teknik-duruş motorunun GERİYE-DÖNÜK (look-ahead'siz)
öz-denetimi. Karar-destek; yatırım tavsiyesi DEĞİLDİR.

NEDEN VAR
---------
Bir duruş motorunun değeri, kendi öngörü gücünü ölçen bir geri-besleme döngüsü
olmadan bilinemez. Bu betik, `technical_plus.enrich_snapshot`'ın ürettiği teknik
duruşu, SIZINTISIZ biçimde gelecekteki gerçekleşen getiriyle karşılaştırır ve
motorun ampirik isabetini raporlar:

  - Spearman sıra korelasyonu (ρ)  : duruş skoru ↔ gerçekleşen getiri
  - Bilgi katsayısı (IC, Pearson)  : aynı ilişkinin doğrusal ölçüsü
  - İsabet oranı (hit-rate)        : mutlak (>0) ve benchmark-göreli (endeksi geçti mi)
  - Benchmark-göreli getiri        : "yükselen dalga" etkisini ayırmak için
  - Boşluk ayrıştırması (gap)      : getirinin ne kadarı seans-arası boşluktan

SIZINTISIZLIK (look-ahead-free)
-------------------------------
Her sembol için duruş, `bars[:-horizon]` ile (yani sonuç penceresi DIŞLANARAK)
hesaplanır. Gerçekleşen getiri, kurulum-kapanışından sonuç-kapanışına ölçülür:
    realized = close[-1] / close[-1-horizon] - 1
horizon=1 için: duruş = bars[:-1]; getiri = close[-1]/close[-2]-1.

VERİ KONVANSİYONU
-----------------
`bars` = [{date, open, high, low, close, volume}, ...] kronolojik. Borsa
bağlayıcısının haftalık serisinde her bar Pazar-tarihli olup ilgili haftanın
Cuma kapanışını taşır; bu betik tarihe değil yalnızca SIRAYA dayanır.

Bağımlılık: yalnızca Python standart kütüphanesi + technical_plus (+ technical_helpers).
"""

from __future__ import annotations

import argparse
import json
import math
import sys

try:
    from technical_plus import enrich_snapshot
except ImportError:  # pragma: no cover
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from technical_plus import enrich_snapshot


# ----------------------------------------------------------------------------
# Saf-Python istatistik yardımcıları (determinist, bağımlılıksız)
# ----------------------------------------------------------------------------

def _ranks(vals):
    """Ortalama-bağ (average-tie) sıralaması döndürür."""
    n = len(vals)
    order = sorted(range(n), key=lambda i: vals[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # 1-tabanlı ortalama
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def _pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((x - mb) ** 2 for x in b))
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def _spearman(a, b):
    if len(a) < 2:
        return None
    return _pearson(_ranks(a), _ranks(b))


# ----------------------------------------------------------------------------
# Çekirdek backtest
# ----------------------------------------------------------------------------

def _bars_field(bars, field):
    return [b[field] for b in bars if field in b]


def backtest_posture(symbols_bars, horizon=1, index_bars=None,
                     include_relative_strength=True, min_setup_bars=20):
    """
    Sembol bazında sızıntısız duruş-vs-getiri denetimi.

    Parametreler
    ------------
    symbols_bars : {sym: [bar,...]}  her sembolün kronolojik OHLCV barları
    horizon      : sonuç penceresi (bar). 1 = bir sonraki bar.
    index_bars   : [bar,...] benchmark (ör. XU100) — verilirse benchmark-göreli
                   metrikler ve (include_relative_strength ise) göreli-güç
                   katkısı devreye girer.
    include_relative_strength : duruş hesaplanırken endeks serisi enrich_snapshot'a
                   verilsin mi (göreli-güç katkısı dahil/hariç A/B testi için).
    min_setup_bars : duruş için gereken asgari kurulum-barı; altındakiler atlanır.

    Dönen: {rows, metrics, benchmark, params, disclaimer}.
    """
    idx_close = _bars_field(index_bars, "close") if index_bars else None
    bench_ret = None
    if idx_close and len(idx_close) > horizon:
        bench_ret = (idx_close[-1] / idx_close[-1 - horizon] - 1.0) * 100.0

    rows = []
    for sym, bars in symbols_bars.items():
        if len(bars) < min_setup_bars + horizon:
            rows.append({"symbol": sym, "skipped": True,
                         "note": f"yetersiz bar ({len(bars)})"})
            continue

        setup = bars[:-horizon]  # SIZINTISIZ: sonuç penceresi dışlanır
        closes = _bars_field(bars, "close")
        opens = _bars_field(bars, "open")
        c_setup = closes[-1 - horizon]   # kurulum-kapanışı (= setup'ın son barı)
        c_final = closes[-1]
        if c_setup == 0:
            rows.append({"symbol": sym, "skipped": True, "note": "sıfır taban"})
            continue
        realized = (c_final / c_setup - 1.0) * 100.0

        # gap (kurulum-kapanışı → sonuç-penceresi açılışı) vs intra
        o_next = opens[-horizon] if len(opens) >= horizon else None
        gap = ((o_next / c_setup - 1.0) * 100.0) if o_next else None
        intra = ((c_final / o_next - 1.0) * 100.0) if o_next else None

        idx_for_rs = idx_close[:-horizon] if (idx_close and include_relative_strength) else None
        snap = enrich_snapshot(setup, index_closes=idx_for_rs)
        post = snap.get("posture", {})
        sn = post.get("score_norm")

        rows.append({
            "symbol": sym,
            "skipped": False,
            "posture": post.get("posture"),
            "score_norm": sn,
            "low_coverage": post.get("low_coverage"),
            "realized_ret_pct": round(realized, 2),
            "gap_pct": (round(gap, 2) if gap is not None else None),
            "intra_pct": (round(intra, 2) if intra is not None else None),
            "beat_benchmark": (realized > bench_ret if bench_ret is not None else None),
            "rs_rating": (snap.get("relative_strength", {}) or {}).get("rs_rating"),
        })

    scored = [r for r in rows if not r["skipped"] and r["score_norm"] is not None]
    s_scores = [r["score_norm"] for r in scored]
    s_rets = [r["realized_ret_pct"] for r in scored]

    rho = _spearman(s_scores, s_rets)
    ic = _pearson(s_scores, s_rets)

    # isabet oranları: pozitif duruş → pozitif sonuç hizalaması
    abs_hits = sum(1 for r in scored
                   if (r["score_norm"] > 0) == (r["realized_ret_pct"] > 0))
    abs_hit_rate = (abs_hits / len(scored)) if scored else None
    rel_hit_rate = None
    if bench_ret is not None and scored:
        rel_hits = sum(1 for r in scored
                       if (r["score_norm"] > 0) == bool(r["beat_benchmark"]))
        rel_hit_rate = rel_hits / len(scored)

    metrics = {
        "n_scored": len(scored),
        "spearman_rho": (round(rho, 3) if rho is not None else None),
        "information_coeff": (round(ic, 3) if ic is not None else None),
        "hit_rate_absolute": (round(abs_hit_rate, 3) if abs_hit_rate is not None else None),
        "hit_rate_vs_benchmark": (round(rel_hit_rate, 3) if rel_hit_rate is not None else None),
        "include_relative_strength": include_relative_strength,
    }
    benchmark = {"benchmark_ret_pct": (round(bench_ret, 2) if bench_ret is not None else None),
                 "horizon": horizon}

    return {
        "rows": rows,
        "metrics": metrics,
        "benchmark": benchmark,
        "params": {"horizon": horizon, "min_setup_bars": min_setup_bars},
        "basis": "EOD; intraday mikro-yapı modellenmez",
        "disclaimer": "karar-destek; geçmiş performans gelecek getirinin garantisi değildir",
    }


def render_report(result):
    """İnsan-okunur kısa metin raporu (düzyazı; ham JSON sızdırmaz)."""
    m = result["metrics"]
    b = result["benchmark"]
    lines = []
    lines.append("BIST Teknik-Duruş Geriye-Dönük Denetimi (look-ahead'siz)")
    lines.append("=" * 56)
    lines.append(f"Ufuk: {b['horizon']} bar | Skorlanan sembol: {m['n_scored']} | "
                 f"Göreli-güç dahil: {'evet' if m['include_relative_strength'] else 'hayır'}")
    if b["benchmark_ret_pct"] is not None:
        lines.append(f"Benchmark getirisi: %{b['benchmark_ret_pct']}")
    lines.append("")
    lines.append(f"Spearman ρ (duruş ↔ getiri) : {m['spearman_rho']}")
    lines.append(f"Bilgi katsayısı (IC)        : {m['information_coeff']}")
    lines.append(f"İsabet (mutlak, yön)        : {m['hit_rate_absolute']}")
    lines.append(f"İsabet (benchmark-göreli)   : {m['hit_rate_vs_benchmark']}")
    lines.append("")
    hdr = f"{'SEMBOL':8}{'DURUŞ':16}{'skor':>7}{'getiri%':>9}{'gap%':>7}{'içHafta%':>9}{'GG':>14}"
    lines.append(hdr)
    lines.append("-" * len(hdr))
    srt = sorted([r for r in result["rows"] if not r["skipped"]],
                 key=lambda r: (r["score_norm"] if r["score_norm"] is not None else -9),
                 reverse=True)
    for r in srt:
        sn = f"{r['score_norm']:7.2f}" if r["score_norm"] is not None else f"{'—':>7}"
        gp = f"{r['gap_pct']:7.1f}" if r["gap_pct"] is not None else f"{'—':>7}"
        it = f"{r['intra_pct']:9.1f}" if r["intra_pct"] is not None else f"{'—':>9}"
        gg = r.get("rs_rating") or "—"
        lines.append(f"{r['symbol']:8}{str(r['posture']):16}{sn}"
                     f"{r['realized_ret_pct']:9.2f}{gp}{it}{gg:>14}")
    lines.append("")
    lines.append("Karar-destek; yatırım tavsiyesi değildir. Veriler EOD/gecikmeli olabilir.")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Self-test / CLI
# ----------------------------------------------------------------------------

def _synthetic_bars(n=40, slope=0.5, noise_phase=0.0, base=100.0):
    bars = []
    for i in range(n):
        c = base + i * slope + 3.0 * math.sin(i / 5.0 + noise_phase)
        o = c - slope
        h = max(o, c) + 1.0
        l = min(o, c) - 1.0
        bars.append({"date": f"T{i:03d}", "open": round(o, 2), "high": round(h, 2),
                     "low": round(l, 2), "close": round(c, 2), "volume": 1_000_000})
    return bars


def _run_selftest():
    syms = {
        "UPSTRONG": _synthetic_bars(40, slope=0.8, noise_phase=0.0),
        "UPWEAK": _synthetic_bars(40, slope=0.2, noise_phase=1.0),
        "DOWN": _synthetic_bars(40, slope=-0.5, noise_phase=2.0),
        "FLAT": _synthetic_bars(40, slope=0.02, noise_phase=0.5),
    }
    idx = _synthetic_bars(40, slope=0.3, noise_phase=0.0)
    return backtest_posture(syms, horizon=1, index_bars=idx)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="BIST teknik-duruş geriye-dönük denetimi (karar-destek).")
    p.add_argument("--file", help='JSON: {"symbols":{sym:[bars]}, "index":[bars]}')
    p.add_argument("--horizon", type=int, default=1)
    p.add_argument("--no-rs", action="store_true",
                   help="göreli-güç katkısını kapat (A/B testi)")
    p.add_argument("--json", action="store_true", help="ham JSON çıktı")
    args = p.parse_args(argv)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        symbols = data.get("symbols", data)
        index_bars = data.get("index")
        result = backtest_posture(symbols, horizon=args.horizon,
                                  index_bars=index_bars,
                                  include_relative_strength=not args.no_rs)
    else:
        result = _run_selftest()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
