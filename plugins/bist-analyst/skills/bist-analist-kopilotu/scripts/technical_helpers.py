#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
technical_helpers.py — BIST equity-research co-pilot çekirdek teknik göstergeleri.

Bu modül, `borsa` MCP `get_historical_data` tarafından çekilmiş EOD (gün-sonu)
OHLCV serileri üzerinde standart teknik göstergeleri SAF Python ile yeniden türetir.
Amaç: skill'in sunucu tarafında (Borsa scanner) kullandığı göstergeleri yerelde
RE-DERIVE edip CROSS-CHECK edebilmesi — RSI(14), MACD(12,26,9), SMA(5/20/50/200),
EMA(20), Bollinger(20,2), ATR(14).

ÖNEMLİ NOTLAR
- Veri tabanı GÜN-SONU (EOD) kapanışlarıdır; intraday mikro-yapı (gün-içi tik,
  spread, hacim profili) MODELLENMEZ. Sinyaller bar-kapanışı bazlıdır.
- Çıktılar KARAR-DESTEK amaçlıdır; YATIRIM TAVSİYESİ DEĞİLDİR.
- Wilder yumuşatması RSI ve ATR için kullanılır (klasik formül).
- Kısa/eksik seride asla çökmez: hesaplanabileni döndürür + `note` + `coverage`.

Bağımlılık: yalnızca Python standart kütüphanesi (math, json, sys, argparse, statistics).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys

# ----------------------------------------------------------------------------
# Yardımcı / normalizasyon
# ----------------------------------------------------------------------------

def _to_floats(seq):
    """Bir diziyi float listesine çevir; None/boş/parse-edilemez değerleri at."""
    out = []
    if not seq:
        return out
    for v in seq:
        if v is None:
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if math.isnan(f) or math.isinf(f):
            continue
        out.append(f)
    return out


def normalize_ohlc(data):
    """
    Esnek girdi normalizasyonu.

    Kabul edilen biçimler:
      1) dict: {"close":[...], "high":[...], "low":[...], "open":[...], "volume":[...]}
      2) bar-dict listesi: [{"close":.., "high":.., "low":.., "volume":..}, ...]
         (anahtar varyasyonları tolere edilir: Close/c/kapanis, High/h/yuksek, ...)

    Dönen: {"open":[...], "high":[...], "low":[...], "close":[...], "volume":[...]}
    Listeler eşit uzunlukta olmayabilir; hesaplayıcılar bunu tolere eder.
    """
    # 1) Zaten kolon-dict ise
    if isinstance(data, dict):
        def pick(*keys):
            for k in keys:
                if k in data and data[k] is not None:
                    return _to_floats(data[k])
            return []
        return {
            "open": pick("open", "Open", "o", "acilis"),
            "high": pick("high", "High", "h", "yuksek"),
            "low": pick("low", "Low", "l", "dusuk"),
            "close": pick("close", "Close", "c", "kapanis", "adjclose", "adj_close"),
            "volume": pick("volume", "Volume", "v", "hacim"),
        }

    # 2) Bar-dict listesi ise
    if isinstance(data, (list, tuple)):
        o, h, l, c, vol = [], [], [], [], []

        def grab(bar, *keys):
            for k in keys:
                if k in bar and bar[k] is not None:
                    return bar[k]
            return None

        all_dicts = all(isinstance(b, dict) for b in data) and len(data) > 0
        if all_dicts:
            for bar in data:
                o.append(grab(bar, "open", "Open", "o", "acilis"))
                h.append(grab(bar, "high", "High", "h", "yuksek"))
                l.append(grab(bar, "low", "Low", "l", "dusuk"))
                c.append(grab(bar, "close", "Close", "c", "kapanis", "adjclose", "adj_close"))
                vol.append(grab(bar, "volume", "Volume", "v", "hacim"))
            return {
                "open": _to_floats(o),
                "high": _to_floats(h),
                "low": _to_floats(l),
                "close": _to_floats(c),
                "volume": _to_floats(vol),
            }
        # Düz sayı listesi → yalnızca close varsay
        return {"open": [], "high": [], "low": [], "close": _to_floats(data), "volume": []}

    return {"open": [], "high": [], "low": [], "close": [], "volume": []}


def _round(x, n=4):
    if x is None:
        return None
    try:
        if math.isnan(x) or math.isinf(x):
            return None
    except (TypeError, ValueError):
        return None
    return round(float(x), n)


# ----------------------------------------------------------------------------
# Hareketli ortalamalar
# ----------------------------------------------------------------------------

def sma(series, n, full=False):
    """
    Basit hareketli ortalama (SMA).
    full=False → son değer (float|None) ; full=True → tam liste + son.
    """
    s = _to_floats(series)
    if n <= 0:
        return {"last": None, "values": [], "note": "n must be > 0"} if full else None
    if len(s) < n:
        note = f"insufficient data: need {n}, have {len(s)}"
        return {"last": None, "values": [], "note": note} if full else None

    values = []
    running = sum(s[:n])
    values.append(running / n)
    for i in range(n, len(s)):
        running += s[i] - s[i - n]
        values.append(running / n)
    last = values[-1]
    if full:
        return {"last": last, "values": values, "note": None}
    return last


def ema(series, n, full=False):
    """
    Üssel hareketli ortalama (EMA). İlk değer SMA(n) ile başlatılır (seed).
    full=False → son değer ; full=True → tam liste + son.
    """
    s = _to_floats(series)
    if n <= 0:
        return {"last": None, "values": [], "note": "n must be > 0"} if full else None
    if len(s) < n:
        note = f"insufficient data: need {n}, have {len(s)}"
        return {"last": None, "values": [], "note": note} if full else None

    k = 2.0 / (n + 1.0)
    seed = sum(s[:n]) / n  # ilk EMA = SMA seed
    values = [seed]
    prev = seed
    for i in range(n, len(s)):
        prev = (s[i] - prev) * k + prev
        values.append(prev)
    last = values[-1]
    if full:
        return {"last": last, "values": values, "note": None}
    return last


# ----------------------------------------------------------------------------
# RSI (Wilder)
# ----------------------------------------------------------------------------

def rsi(closes, n=14, full=False):
    """
    Wilder RSI(14). İlk ortalama kazanç/kayıp ilk n periyodun basit ortalaması,
    sonrası Wilder yumuşatması ((prev*(n-1) + current)/n).
    Dönen son değer 0..100 aralığında.
    """
    s = _to_floats(closes)
    if n <= 0:
        return {"last": None, "values": [], "note": "n must be > 0"} if full else None
    # n fark için n+1 fiyat gerekir
    if len(s) < n + 1:
        note = f"insufficient data: need {n + 1}, have {len(s)}"
        return {"last": None, "values": [], "note": note} if full else None

    gains, losses = [], []
    for i in range(1, len(s)):
        ch = s[i] - s[i - 1]
        gains.append(max(ch, 0.0))
        losses.append(max(-ch, 0.0))

    avg_gain = sum(gains[:n]) / n
    avg_loss = sum(losses[:n]) / n

    def _rsi_val(ag, al):
        if al == 0:
            return 100.0 if ag > 0 else 50.0
        rs = ag / al
        return 100.0 - (100.0 / (1.0 + rs))

    values = [_rsi_val(avg_gain, avg_loss)]
    for i in range(n, len(gains)):
        avg_gain = (avg_gain * (n - 1) + gains[i]) / n
        avg_loss = (avg_loss * (n - 1) + losses[i]) / n
        values.append(_rsi_val(avg_gain, avg_loss))

    last = values[-1]
    if full:
        return {"last": last, "values": values, "note": None}
    return last


# ----------------------------------------------------------------------------
# MACD
# ----------------------------------------------------------------------------

def macd(closes, fast=12, slow=26, signal=9):
    """
    MACD = EMA(fast) - EMA(slow); Signal = EMA(MACD, signal); Hist = MACD - Signal.
    Dönen: {"macd":.., "signal":.., "hist":.., "note":..} (son değerler).
    EMA seed nedeniyle fast ve slow listeleri farklı uzunlukta olur; kuyruktan hizalanır.
    """
    s = _to_floats(closes)
    need = slow + signal
    if len(s) < need:
        return {"macd": None, "signal": None, "hist": None,
                "note": f"insufficient data: need ~{need}, have {len(s)}"}

    ef = ema(s, fast, full=True)["values"]
    es = ema(s, slow, full=True)["values"]
    if not ef or not es:
        return {"macd": None, "signal": None, "hist": None, "note": "ema unavailable"}

    # slow EMA daha kısadır; ikisini kuyruktan hizala
    m = min(len(ef), len(es))
    ef_al = ef[-m:]
    es_al = es[-m:]
    macd_line = [a - b for a, b in zip(ef_al, es_al)]

    sig = ema(macd_line, signal, full=True)
    if sig["last"] is None:
        return {"macd": _round(macd_line[-1]), "signal": None, "hist": None,
                "note": f"signal needs {signal} macd points, have {len(macd_line)}"}

    macd_last = macd_line[-1]
    signal_last = sig["last"]
    hist_last = macd_last - signal_last
    return {
        "macd": _round(macd_last),
        "signal": _round(signal_last),
        "hist": _round(hist_last),
        "note": None,
    }


# ----------------------------------------------------------------------------
# Bollinger Bands
# ----------------------------------------------------------------------------

def bollinger(closes, n=20, k=2):
    """
    Bollinger Bands(20, 2).
      mid   = SMA(n)
      upper = mid + k*stddev (population std, son n bar)
      lower = mid - k*stddev
      pctb  = (close - lower) / (upper - lower)   # %B
      bandwidth = (upper - lower) / mid
    Dönen son değerler.
    """
    s = _to_floats(closes)
    if n <= 0:
        return {"mid": None, "upper": None, "lower": None, "pctb": None,
                "bandwidth": None, "note": "n must be > 0"}
    if len(s) < n:
        return {"mid": None, "upper": None, "lower": None, "pctb": None,
                "bandwidth": None, "note": f"insufficient data: need {n}, have {len(s)}"}

    window = s[-n:]
    mid = sum(window) / n
    # nüfus standart sapması (Bollinger geleneği)
    sd = statistics.pstdev(window)
    upper = mid + k * sd
    lower = mid - k * sd
    close = s[-1]
    width = upper - lower
    pctb = ((close - lower) / width) if width != 0 else None
    bandwidth = (width / mid) if mid != 0 else None
    return {
        "mid": _round(mid),
        "upper": _round(upper),
        "lower": _round(lower),
        "pctb": _round(pctb),
        "bandwidth": _round(bandwidth),
        "note": None,
    }


# ----------------------------------------------------------------------------
# True Range / ATR (Wilder)
# ----------------------------------------------------------------------------

def true_range(highs, lows, closes, full=False):
    """
    True Range serisi:
      TR_i = max(high-low, |high-prev_close|, |low-prev_close|)
    İlk bar için prev_close yoktur → TR_0 = high_0 - low_0.
    full=True → tam TR listesi döndürür.
    """
    h = _to_floats(highs)
    l = _to_floats(lows)
    c = _to_floats(closes)
    m = min(len(h), len(l), len(c))
    if m == 0:
        return {"values": [], "last": None, "note": "no OHLC data"} if full else None
    h, l, c = h[-m:], l[-m:], c[-m:]

    tr = []
    for i in range(m):
        if i == 0:
            tr.append(h[i] - l[i])
        else:
            prev_close = c[i - 1]
            tr.append(max(h[i] - l[i], abs(h[i] - prev_close), abs(l[i] - prev_close)))
    if full:
        return {"values": tr, "last": tr[-1] if tr else None, "note": None}
    return tr[-1] if tr else None


def atr(highs, lows, closes, n=14, full=False):
    """
    Wilder ATR(14). İlk ATR = ilk n TR'nin basit ortalaması,
    sonrası ATR_i = (ATR_{i-1}*(n-1) + TR_i)/n.
    """
    tr = true_range(highs, lows, closes, full=True)
    trv = tr["values"] if isinstance(tr, dict) else (tr or [])
    if n <= 0:
        return {"last": None, "values": [], "note": "n must be > 0"} if full else None
    if len(trv) < n:
        note = f"insufficient data: need {n} TR, have {len(trv)}"
        return {"last": None, "values": [], "note": note} if full else None

    first = sum(trv[:n]) / n
    values = [first]
    prev = first
    for i in range(n, len(trv)):
        prev = (prev * (n - 1) + trv[i]) / n
        values.append(prev)
    last = values[-1]
    if full:
        return {"last": last, "values": values, "note": None}
    return last


# ----------------------------------------------------------------------------
# Snapshot
# ----------------------------------------------------------------------------

def _rsi_zone(value):
    if value is None:
        return None
    if value < 30:
        return "aşırı satım"
    if value > 70:
        return "aşırı alım"
    return "nötr"


def _pos(close, ref):
    """close referans MA'ya göre üstte/altta/None."""
    if close is None or ref is None:
        return None
    if close > ref:
        return "üstünde"
    if close < ref:
        return "altında"
    return "eşit"


def indicator_snapshot(ohlc):
    """
    Tam gösterge seti — son bar için.

    Girdi: {"close":[...], "high":[...], "low":[...], "volume":[...]} VEYA bar-dict listesi.
    Çıktı: göstergeler + konum bayrakları + coverage (0..1) + note.

    coverage = başarıyla hesaplanan ana gösterge oranı.
    """
    norm = normalize_ohlc(ohlc)
    closes = norm["close"]
    highs = norm["high"]
    lows = norm["low"]
    vols = norm["volume"]

    notes = []
    n_close = len(closes)
    close = closes[-1] if closes else None

    if n_close == 0:
        return {
            "ok": False,
            "coverage": 0.0,
            "note": "no close data",
            "bar_count": 0,
            "indicators": {},
            "flags": {},
        }

    # Göstergeler
    sma5 = sma(closes, 5)
    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    sma200 = sma(closes, 200)
    ema20 = ema(closes, 20)
    rsi14 = rsi(closes, 14)
    macd_d = macd(closes)
    bb = bollinger(closes, 20, 2)
    atr14 = atr(highs, lows, closes, 14)

    indicators = {
        "close": _round(close),
        "sma_5": _round(sma5),
        "sma_20": _round(sma20),
        "sma_50": _round(sma50),
        "sma_200": _round(sma200),
        "ema_20": _round(ema20),
        "rsi_14": _round(rsi14, 2),
        "macd": macd_d.get("macd"),
        "macd_signal": macd_d.get("signal"),
        "macd_hist": macd_d.get("hist"),
        "bb_mid": bb.get("mid"),
        "bb_upper": bb.get("upper"),
        "bb_lower": bb.get("lower"),
        "bb_pctb": bb.get("pctb"),
        "bb_bandwidth": bb.get("bandwidth"),
        "atr_14": _round(atr14),
    }

    # Bollinger içi konum
    bb_position = None
    if close is not None and bb.get("upper") is not None and bb.get("lower") is not None:
        if close >= bb["upper"]:
            bb_position = "üst banda temas/aşım"
        elif close <= bb["lower"]:
            bb_position = "alt banda temas/aşım"
        else:
            bb_position = "bantlar arası"

    macd_hist_sign = None
    if indicators["macd_hist"] is not None:
        macd_hist_sign = "pozitif" if indicators["macd_hist"] > 0 else (
            "negatif" if indicators["macd_hist"] < 0 else "nötr")

    flags = {
        "close_vs_sma_20": _pos(close, sma20),
        "close_vs_sma_50": _pos(close, sma50),
        "close_vs_sma_200": _pos(close, sma200),
        "close_vs_ema_20": _pos(close, ema20),
        "rsi_zone": _rsi_zone(rsi14),
        "macd_hist_sign": macd_hist_sign,
        "bollinger_position": bb_position,
        "above_all_smas": (
            None if (sma20 is None or sma50 is None or sma200 is None or close is None)
            else (close > sma20 and close > sma50 and close > sma200)
        ),
    }

    # coverage: ana 9 gösterge
    core = [sma5, sma20, sma50, sma200, ema20, rsi14,
            macd_d.get("macd"), bb.get("mid"), atr14]
    available = sum(1 for x in core if x is not None)
    coverage = round(available / len(core), 3)

    # not toplama
    for label, d in (("rsi", rsi14), ("sma200", sma200), ("ema20", ema20), ("atr", atr14)):
        if d is None:
            notes.append(f"{label} hesaplanamadı (yetersiz seri)")
    if macd_d.get("note"):
        notes.append("macd: " + str(macd_d["note"]))
    if bb.get("note"):
        notes.append("bollinger: " + str(bb["note"]))
    if not highs or not lows:
        notes.append("high/low yok → ATR ve TR atlanmış olabilir")

    return {
        "ok": True,
        "basis": "EOD (gün-sonu); intraday mikro-yapı modellenmez",
        "disclaimer": "karar-destek; yatırım tavsiyesi değildir",
        "bar_count": n_close,
        "has_volume": len(vols) > 0,
        "coverage": coverage,
        "indicators": indicators,
        "flags": flags,
        "note": "; ".join(notes) if notes else None,
    }


# ----------------------------------------------------------------------------
# Self-test / CLI
# ----------------------------------------------------------------------------

def _synthetic_series(n=260):
    """Yükselen sentetik bir OHLC serisi üret (deterministik, kütüphanesiz)."""
    closes, highs, lows = [], [], []
    base = 100.0
    for i in range(n):
        # yumuşak trend + deterministik salınım (random yok)
        trend = base + i * 0.35
        wave = 4.0 * math.sin(i / 9.0) + 1.5 * math.cos(i / 3.0)
        c = trend + wave
        h = c + 1.2 + abs(math.sin(i / 5.0))
        l = c - 1.2 - abs(math.cos(i / 7.0))
        closes.append(round(c, 2))
        highs.append(round(h, 2))
        lows.append(round(l, 2))
    return {"close": closes, "high": highs, "low": lows,
            "volume": [1_000_000 + (i % 50) * 1000 for i in range(n)]}


def _run_selftest():
    ohlc = _synthetic_series(260)
    snap = indicator_snapshot(ohlc)
    # kısa seri davranışı
    short = indicator_snapshot({"close": [10, 11, 12], "high": [10, 11, 12], "low": [9, 10, 11]})
    out = {
        "selftest": "technical_helpers",
        "full_series": snap,
        "short_series_coverage": short["coverage"],
        "short_series_note": short.get("note"),
    }
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="BIST teknik göstergeleri — EOD OHLCV snapshot (karar-destek).")
    parser.add_argument("--file", help="OHLC JSON dosyası (kolon-dict veya bar listesi)")
    parser.add_argument("--indent", type=int, default=2, help="JSON girinti")
    args = parser.parse_args(argv)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = indicator_snapshot(data)
    else:
        result = _run_selftest()

    print(json.dumps(result, ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
