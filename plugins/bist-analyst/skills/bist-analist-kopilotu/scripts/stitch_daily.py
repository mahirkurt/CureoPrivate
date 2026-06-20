#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stitch_daily.py — GÜNLÜK-veri toplayıcı/birleştirici (calibration için).

NEDEN VAR
---------
Borsa `get_historical_data` çözünürlüğü, talep edilen ARALIK uzunluğuyla ölçeklenir:
~≤30 gün → GÜNLÜK, ~3 ay → haftalık, ~1 yıl → aylık bar. Bu yüzden uzun bir GÜNLÜK
seri tek çağrıdan alınamaz; ~30-günlük dilimler halinde çekilip BİRLEŞTİRİLMELİDİR.
Bu betik, bu dilimleri (sembol başına çakışan/sırasız olabilir) tarihe göre
**tekilleştirir + sıralar** ve `walkforward_calibrate`/`backtest_posture`'ın
beklediği frames.json sözleşmesine (`{"symbols":{SYM:[bars]}, "index":[bars]}`)
dönüştürür. Ayrıca bir **kapsam raporu** üretir (SMA50/200 tanımlı mı, bölünme
artefaktı şüphesi var mı).

GİRDİ (--in raw_chunks.json)
----------------------------
Esnek; iki biçim kabul edilir:
  A) {"symbols": {SYM: [bar,...] (çakışabilir)}, "index": [bar,...]}
  B) {"chunks": [ {"symbol": "GARAN", "data": [bar,...]}, ... ],
      "index_symbol": "XU100"}   # ham Borsa yanıtlarının `data` dizileri
bar = {date, open, high, low, close, volume}. `date` "YYYY-MM-DD..." ile başlamalı.

ÇIKTI
-----
--out frames_daily.json yazar; stdout'a kapsam raporu (düzyazı) basar.
Karar-destek; yatırım tavsiyesi DEĞİLDİR. Bağımlılık: yalnız stdlib.
"""

from __future__ import annotations

import argparse
import json
import sys


def _daykey(bar):
    d = bar.get("date") or bar.get("tarih") or ""
    return str(d)[:10]  # YYYY-MM-DD


def dedupe_sort(bars):
    """Tarihe göre tekilleştir (sonraki kazanır) ve kronolojik sırala."""
    by_day = {}
    for b in bars:
        k = _daykey(b)
        if k:
            by_day[k] = b
    return [by_day[k] for k in sorted(by_day)]


def _split_artifacts(bars, hi=2.6, lo=0.38):
    """Ardışık kapanış oranı uç olan barları (muhtemel düzeltilmemiş bölünme) döner."""
    out = []
    cl = [b.get("close") for b in bars]
    for i in range(1, len(cl)):
        a, c = cl[i - 1], cl[i]
        if isinstance(a, (int, float)) and isinstance(c, (int, float)) and a:
            r = c / a
            if r > hi or r < lo:
                out.append((_daykey(bars[i]), round(r, 2)))
    return out


def normalize_input(raw):
    """A/B biçimlerini {symbols, index} (ham, dedupe ÖNCESİ) yapısına indirger."""
    if "symbols" in raw:
        symbols = {s: list(b) for s, b in raw["symbols"].items()}
        index = list(raw.get("index", []))
        return symbols, index
    # B biçimi: chunks listesi
    idx_sym = raw.get("index_symbol")
    symbols = {}
    index = []
    for ch in raw.get("chunks", []):
        sym = ch.get("symbol")
        data = ch.get("data", [])
        if sym == idx_sym:
            index.extend(data)
        else:
            symbols.setdefault(sym, []).extend(data)
    return symbols, index


def stitch(raw):
    symbols_raw, index_raw = normalize_input(raw)
    symbols = {s: dedupe_sort(b) for s, b in symbols_raw.items()}
    index = dedupe_sort(index_raw)
    return {"symbols": symbols, "index": index}


def coverage_report(frames):
    symbols = frames["symbols"]
    index = frames.get("index", [])
    lines = ["GÜNLÜK frames kapsam raporu", "=" * 30]
    counts = {s: len(b) for s, b in symbols.items()}
    if counts:
        mn, mx = min(counts.values()), max(counts.values())
        lines.append(f"Sembol: {len(symbols)} | bar/sembol: min={mn} max={mx} | "
                     f"index bar={len(index)}")
        lines.append(f"Gösterge kapsamı (bar sayısına göre): "
                     f"RSI14/MACD≥35 ✓, SMA50 {'✓' if mn >= 50 else '✗ ('+str(mn)+'<50)'}, "
                     f"SMA200 {'✓' if mn >= 200 else '✗ ('+str(mn)+'<200, low_coverage beklenir)'}")
    # bölünme artefaktı taraması
    susp = {}
    for s, b in symbols.items():
        a = _split_artifacts(b)
        if a:
            susp[s] = a
    lines.append("Bölünme-artefaktı şüphesi: " +
                 (json.dumps(susp, ensure_ascii=False) if susp else "YOK (temiz)"))
    # tarih aralığı
    allbars = [bb for b in symbols.values() for bb in b]
    if allbars:
        days = sorted({_daykey(x) for x in allbars})
        lines.append(f"Tarih aralığı: {days[0]} .. {days[-1]} ({len(days)} ayrı gün)")
    lines.append("Karar-destek; yatırım tavsiyesi değildir.")
    return "\n".join(lines), (not susp)


def main(argv=None):
    p = argparse.ArgumentParser(description="Borsa günlük dilimlerini frames.json'a birleştir.")
    p.add_argument("--in", dest="inp", required=True, help="ham dilim JSON (A/B biçimi)")
    p.add_argument("--out", required=True, help="çıktı frames_daily.json")
    p.add_argument("--json", action="store_true", help="raporu da JSON bas")
    args = p.parse_args(argv)

    with open(args.inp, "r", encoding="utf-8") as f:
        raw = json.load(f)
    frames = stitch(raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(frames, f, ensure_ascii=False)
    report, clean = coverage_report(frames)
    print(report)
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
