#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
technical_plus.py — BIST equity-research co-pilot ÜST-DÜZEY teknik okumaları.

`technical_helpers` üzerine inşa edilir. Borsa scanner'ın sunucu tarafında
sunduğu göstergeleri (Supertrend yön, Tillson T3, pivot noktaları) yerelde
yeniden türetir; bunları auditable bir "teknik duruş" puan sistemine ve
çoklu-zaman-dilimi (multi-timeframe) confluence okumasına dönüştürür.

ÖNEMLİ NOTLAR
- Veri tabanı GÜN-SONU (EOD) kapanışlarıdır; intraday mikro-yapı modellenmez.
- Çıktılar KARAR-DESTEK amaçlıdır; YATIRIM TAVSİYESİ DEĞİLDİR.
- "Teknik duruş" şeffaf bir puanlama ile üretilir; her katkı `contributions`
  içinde gerekçeli olarak döner (kara-kutu değil).
- Kısa/eksik seride asla çökmez: hesaplanabileni döndürür + `note`.

Bağımlılık: yalnızca Python standart kütüphanesi + technical_helpers.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

try:
    # paket/aynı-dizin importu
    from technical_helpers import (
        normalize_ohlc, indicator_snapshot, ema, sma, rsi, atr,
        true_range, _to_floats, _round,
    )
except ImportError:  # pragma: no cover - sys.path fallback
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from technical_helpers import (
        normalize_ohlc, indicator_snapshot, ema, sma, rsi, atr,
        true_range, _to_floats, _round,
    )


# ----------------------------------------------------------------------------
# Supertrend (ATR tabanlı, standart)
# ----------------------------------------------------------------------------

def supertrend(highs, lows, closes, period=10, multiplier=3, full=False):
    """
    Standart ATR tabanlı Supertrend.

    Basic bands:
      hl2   = (high + low) / 2
      upper = hl2 + multiplier*ATR
      lower = hl2 - multiplier*ATR
    Final bands trail uygulanır; trend yönü (direction) +1 (yukarı) / -1 (aşağı).

    Dönen (full=False): {"value":.., "direction":+1/-1, "note":..} (son bar).
    Dönen (full=True):  {"series":[{value,direction}...], "last":{...}, "note":..}
    """
    h = _to_floats(highs)
    l = _to_floats(lows)
    c = _to_floats(closes)
    m = min(len(h), len(l), len(c))
    if m == 0:
        empty = {"value": None, "direction": None, "note": "no OHLC data"}
        return ({"series": [], "last": empty, "note": empty["note"]} if full else empty)
    h, l, c = h[-m:], l[-m:], c[-m:]

    atr_res = atr(h, l, c, period, full=True)
    atr_vals = atr_res["values"] if isinstance(atr_res, dict) else []
    if not atr_vals:
        empty = {"value": None, "direction": None,
                 "note": f"insufficient data: need ~{period + 1}, have {m}"}
        return ({"series": [], "last": empty, "note": empty["note"]} if full else empty)

    # ATR ilk değeri TR index = period-1'e denk gelir (Wilder seed).
    # Supertrend'i ATR'nin tanımlı olduğu kuyruğa hizala.
    offset = m - len(atr_vals)  # ATR'nin başladığı bar index'i
    hl2 = [(h[i] + l[i]) / 2.0 for i in range(m)]

    series = []
    final_upper = None
    final_lower = None
    prev_dir = 1  # başlangıçta yukarı varsay
    prev_st = None

    for j, i in enumerate(range(offset, m)):
        a = atr_vals[j]
        basic_upper = hl2[i] + multiplier * a
        basic_lower = hl2[i] - multiplier * a

        if final_upper is None:
            final_upper = basic_upper
            final_lower = basic_lower
        else:
            # Final upper band kuralı
            if basic_upper < final_upper or c[i - 1] > final_upper:
                final_upper = basic_upper
            # Final lower band kuralı
            if basic_lower > final_lower or c[i - 1] < final_lower:
                final_lower = basic_lower

        # Yön ve Supertrend değeri
        if prev_st is None:
            # ilk nokta: kapanış üst banttan büyükse yukarı
            direction = 1 if c[i] > final_upper else -1
        else:
            if prev_st == "upper":
                direction = 1 if c[i] > final_upper else -1
            else:  # prev_st == "lower"
                direction = -1 if c[i] < final_lower else 1

        if direction == 1:
            st_value = final_lower
            prev_st = "lower"
        else:
            st_value = final_upper
            prev_st = "upper"

        prev_dir = direction
        series.append({"value": _round(st_value), "direction": direction})

    last = series[-1] if series else {"value": None, "direction": None}
    last = dict(last)
    last["note"] = None
    if full:
        return {"series": series, "last": last, "note": None}
    return last


# ----------------------------------------------------------------------------
# Tillson T3 (genelleştirilmiş DEMA zinciri)
# ----------------------------------------------------------------------------

def _ema_series(values, n):
    """EMA serisini (seed=SMA) son-hizalı liste olarak döndür."""
    res = ema(values, n, full=True)
    return res["values"] if isinstance(res, dict) and res.get("values") else []


def t3(closes, period=5, vfactor=0.7):
    """
    Tillson T3 (1998). Altı kademeli EMA zinciri (e1..e6) üzerine ağırlıklı kombinasyon.

    c1 = -b^3
    c2 = 3b^2 + 3b^3
    c3 = -6b^2 - 3b - 3b^3
    c4 = 1 + 3b + b^3 + 3b^2
    T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3
    (b = vfactor)

    Her EMA seed nedeniyle kısalır; tüm seriler en kısa kuyruğa hizalanır.
    Dönen: {"last":.., "note":..}.
    """
    s = _to_floats(closes)
    # 6 zincirleme EMA → kabaca 6*period bar gerekir
    need = period * 6
    if len(s) < need:
        return {"last": None,
                "note": f"insufficient data for T3: need ~{need}, have {len(s)}"}

    b = float(vfactor)
    c1 = -(b ** 3)
    c2 = 3 * b * b + 3 * (b ** 3)
    c3 = -6 * b * b - 3 * b - 3 * (b ** 3)
    c4 = 1 + 3 * b + (b ** 3) + 3 * b * b

    e1 = _ema_series(s, period)
    e2 = _ema_series(e1, period)
    e3 = _ema_series(e2, period)
    e4 = _ema_series(e3, period)
    e5 = _ema_series(e4, period)
    e6 = _ema_series(e5, period)

    chains = [e1, e2, e3, e4, e5, e6]
    if any(len(x) == 0 for x in chains):
        return {"last": None, "note": "T3 EMA chain collapsed (seri çok kısa)"}

    # en kısa kuyruğa hizala
    m = min(len(e3), len(e4), len(e5), len(e6))
    e3a, e4a, e5a, e6a = e3[-m:], e4[-m:], e5[-m:], e6[-m:]
    t3_last = c1 * e6a[-1] + c2 * e5a[-1] + c3 * e4a[-1] + c4 * e3a[-1]
    return {"last": _round(t3_last), "note": None}


# ----------------------------------------------------------------------------
# Pivot Points
# ----------------------------------------------------------------------------

def pivot_points(high, low, close, method="classic"):
    """
    Pivot noktaları (önceki periyodun H/L/C'sinden).

    method='classic':
      P  = (H + L + C) / 3
      R1 = 2P - L ; S1 = 2P - H
      R2 = P + (H - L) ; S2 = P - (H - L)
      R3 = H + 2(P - L) ; S3 = L - 2(H - P)

    method='fibonacci':
      P  = (H + L + C) / 3 ; R = H - L
      R1 = P + 0.382R ; S1 = P - 0.382R
      R2 = P + 0.618R ; S2 = P - 0.618R
      R3 = P + 1.000R ; S3 = P - 1.000R
    """
    try:
        h, l, c = float(high), float(low), float(close)
    except (TypeError, ValueError):
        return {"pivot": None, "r1": None, "r2": None, "r3": None,
                "s1": None, "s2": None, "s3": None,
                "note": "invalid H/L/C input", "method": method}

    p = (h + l + c) / 3.0
    rng = h - l

    if method == "fibonacci":
        out = {
            "pivot": p,
            "r1": p + 0.382 * rng, "r2": p + 0.618 * rng, "r3": p + 1.000 * rng,
            "s1": p - 0.382 * rng, "s2": p - 0.618 * rng, "s3": p - 1.000 * rng,
        }
    else:  # classic
        method = "classic"
        out = {
            "pivot": p,
            "r1": 2 * p - l, "r2": p + rng, "r3": h + 2 * (p - l),
            "s1": 2 * p - h, "s2": p - rng, "s3": l - 2 * (h - p),
        }

    out = {k: _round(v) for k, v in out.items()}
    out["method"] = method
    out["note"] = None
    return out


# ----------------------------------------------------------------------------
# Seri eğimi / boşluk maruziyeti / göreli güç (v1.1.0)
# ----------------------------------------------------------------------------

def _series_slope(values, window=3):
    """
    Son `window` değerin basit eğimi (ilk→son farkı). None-güvenli.

    Eğim-duyarlı RSI okuması (mean-reversion düzeltmesi) için kullanılır:
    pozitif = yukarı kıvrılma, negatif = aşağı kıvrılma. < 2 gözlemde None.
    """
    v = _to_floats(values)
    if len(v) < 2:
        return None
    w = v[-window:] if len(v) >= window else v
    if len(w) < 2:
        return None
    return _round(w[-1] - w[0])


def gap_exposure(ohlc, lookback=20):
    """
    Seans-arası boşluk (gap) maruziyeti — EOD sistematiğinin yapısal kör noktası.

    EOD veriyle çalışan bir motor, bir önceki kapanış ile bu açılış arasındaki
    boşluğu ÖNGÖREMEZ; bir Cuma taraması hafta sonu sıçramasını göremez. Bu
    fonksiyon son `lookback` bar için boşluk istatistiği üretir; böylece bir
    kurulumun getirisinin ne kadarının seans-arası boşluğa bağımlı olabileceği
    şeffaflaşır. Karar-destek; ÖNGÖRÜ iddiası taşımaz.

    Dönen: {avg_abs_gap_pct, max_abs_gap_pct, last_gap_pct, gap_up_ratio,
            sample, note}. Kısa/eksik seride çökmez.
    """
    norm = normalize_ohlc(ohlc) if not (isinstance(ohlc, dict) and "open" in ohlc
                                        and "close" in ohlc and "high" in ohlc) else ohlc
    o = _to_floats(norm.get("open", []))
    c = _to_floats(norm.get("close", []))
    m = min(len(o), len(c))
    if m < 2:
        return {"avg_abs_gap_pct": None, "max_abs_gap_pct": None,
                "last_gap_pct": None, "gap_up_ratio": None, "sample": 0,
                "note": "yetersiz veri (gap için >=2 bar gerekir)"}
    o, c = o[-m:], c[-m:]
    gaps = []
    for i in range(1, m):
        prev_c = c[i - 1]
        if prev_c:
            gaps.append((o[i] / prev_c - 1.0) * 100.0)
    if not gaps:
        return {"avg_abs_gap_pct": None, "max_abs_gap_pct": None,
                "last_gap_pct": None, "gap_up_ratio": None, "sample": 0,
                "note": "geçerli kapanış yok"}
    win = gaps[-lookback:]
    abs_win = [abs(g) for g in win]
    up = sum(1 for g in win if g > 0)
    return {
        "avg_abs_gap_pct": _round(sum(abs_win) / len(abs_win), 2),
        "max_abs_gap_pct": _round(max(abs_win), 2),
        "last_gap_pct": _round(gaps[-1], 2),
        "gap_up_ratio": _round(up / len(win), 2),
        "sample": len(win),
        "note": None,
    }


_RS_LEVELS = ["Güçlü Zayıf", "Zayıf", "Nötr", "Üstün", "Güçlü Üstün"]


def relative_strength(stock_closes, index_closes, lookback=13):
    """
    Hisse'nin endekse göreli gücü (relative strength) — EOD, karar-destek.

    "Yükselen dalga" (rising-tide) sorununun panzehiri: bir hissenin hareketinin
    ne kadarının genel piyasayı (endeksi) GERÇEKTEN yendiğini ölçer; rejim
    etkisini hisse-seçim sinyalinden ayırır. Mutlak teknik duruş, herkesin
    yükseldiği bir haftada seçim becerisini ölçemez — göreli güç ölçebilir.

    Hesap (son `lookback` bar, kapanış-kapanışa):
      stock_ret = close[-1]/close[-1-L] - 1
      index_ret = idx[-1]/idx[-1-L]   - 1
      rs_excess = stock_ret - index_ret          (göreli aşırı getiri)
      rs_score  = rs_excess'in -1..+1 ölçeğine sıkıştırılmış hâli (duruş katkısı)
      rs_rating = 5-kademe etiket

    Seriler kuyruktan hizalanır; kısa seride çökmez (note ile).

    Dönen: {rs_excess_pct, stock_ret_pct, index_ret_pct, rs_score, rs_rating,
            lookback, note}.
    """
    s = _to_floats(stock_closes)
    x = _to_floats(index_closes)
    m = min(len(s), len(x))
    if m < lookback + 1:
        return {"rs_excess_pct": None, "stock_ret_pct": None,
                "index_ret_pct": None, "rs_score": None, "rs_rating": None,
                "lookback": lookback,
                "note": f"yetersiz veri: göreli güç için ~{lookback + 1} ortak "
                        f"bar gerekir, {m} var"}
    s, x = s[-(lookback + 1):], x[-(lookback + 1):]
    if s[0] == 0 or x[0] == 0:
        return {"rs_excess_pct": None, "stock_ret_pct": None,
                "index_ret_pct": None, "rs_score": None, "rs_rating": None,
                "lookback": lookback, "note": "sıfır taban fiyatı"}
    stock_ret = s[-1] / s[0] - 1.0
    index_ret = x[-1] / x[0] - 1.0
    rs_excess = stock_ret - index_ret
    # -1..+1 ölçeğine sıkıştır: ±%10 göreli aşırı getiri ≈ ±1.0 doygunluk
    rs_score = max(-1.0, min(1.0, rs_excess / 0.10))
    if rs_excess >= 0.05:
        rating = "Güçlü Üstün"
    elif rs_excess >= 0.01:
        rating = "Üstün"
    elif rs_excess > -0.01:
        rating = "Nötr"
    elif rs_excess > -0.05:
        rating = "Zayıf"
    else:
        rating = "Güçlü Zayıf"
    return {
        "rs_excess_pct": _round(rs_excess * 100, 2),
        "stock_ret_pct": _round(stock_ret * 100, 2),
        "index_ret_pct": _round(index_ret * 100, 2),
        "rs_score": _round(rs_score, 3),
        "rs_rating": rating,
        "lookback": lookback,
        "note": None,
    }


# ----------------------------------------------------------------------------
# Teknik duruş (5 seviyeli, şeffaf puan sistemi)
# ----------------------------------------------------------------------------

_POSTURE_LEVELS = ["Güçlü Aşağı", "Zayıf Aşağı", "Nötr", "Zayıf Yukarı", "Güçlü Yukarı"]


def _score_ma_stack(close, sma20, sma50, sma200):
    """MA dizilimi katkısı (ağırlık 2). (pts|None, available) döner."""
    ma_pts = 0.0
    ma_avail = False
    if close is not None and sma20 is not None:
        ma_avail = True
        ma_pts += 1 if close > sma20 else -1
    if close is not None and sma50 is not None:
        ma_avail = True
        ma_pts += 0.5 if close > sma50 else -0.5
    if close is not None and sma200 is not None:
        ma_avail = True
        ma_pts += 1 if close > sma200 else -1
    # SMA dizilim sırası (20>50>200 = boğa dizilimi)
    if sma20 is not None and sma50 is not None and sma200 is not None:
        if sma20 > sma50 > sma200:
            ma_pts += 0.5
        elif sma20 < sma50 < sma200:
            ma_pts -= 0.5
    if ma_avail:
        return max(-2.0, min(2.0, ma_pts)), True
    return None, False


def _score_rsi_zone(rsi_v, rsi_slope=None):
    """
    RSI bölgesi katkısı (ağırlık 1), EĞİM-DUYARLI. pts|None döner.

    rsi_slope (opsiyonel): son birkaç barın RSI eğimi (>0 yukarı, <0 aşağı).
    Sağlandığında uç bölgelerde mean-reversion düzeltmesi uygulanır — saf
    trend-takipçi okumanın şiddetli ortalamaya-dönüşü ıskalama kör noktasını
    kapatır:
      - Aşırı satım (RSI<=30) + yukarı kıvrılma → saf zayıflık (-1.0) yerine
        erken-dönüş sinyali olarak cezayı nötrle (0.0).
      - Aşırı alım (RSI>=70) + aşağı kıvrılma → tepe-zayıflaması; aşırı-pozitif
        katkıyı kıs (0.0).
    rsi_slope=None iken klasik seviye-temelli davranış AYNEN korunur
    (geriye-uyumlu — dışarıdan eğimsiz çağrılarda davranış değişmez).
    """
    if rsi_v is None:
        return None
    # --- uç-bölge eğim düzeltmeleri (yalnız eğim biliniyorsa) ---
    if rsi_slope is not None:
        if rsi_v <= 30 and rsi_slope > 0:
            return 0.0   # aşırı satımdan dönüş: cezayı nötrle
        if rsi_v >= 70 and rsi_slope < 0:
            return 0.0   # aşırı alımdan dönüş: katkıyı kıs
    # --- klasik seviye-temelli bölgeler ---
    if rsi_v >= 60:
        return 1.0
    elif rsi_v > 50:
        return 0.5
    elif rsi_v > 40:
        return -0.5
    elif rsi_v <= 30:
        return -1.0  # aşırı satım (eğim bilinmiyorsa): zayıflık
    return -0.75


def _score_macd_hist(hist):
    """MACD histogram işaret katkısı (ağırlık 1). pts|None döner."""
    if hist is None:
        return None
    return 1.0 if hist > 0 else (-1.0 if hist < 0 else 0.0)


def _score_supertrend(snapshot):
    """Supertrend yönü katkısı (ağırlık 2). pts|None döner."""
    st = snapshot.get("supertrend") if isinstance(snapshot, dict) else None
    st_dir = st.get("direction") if isinstance(st, dict) else None
    if st_dir in (1, -1):
        return 2.0 if st_dir == 1 else -2.0
    return None


def _score_t3(snapshot, close):
    """T3 konumu katkısı (ağırlık 1) — close vs T3. pts|None döner."""
    t3d = snapshot.get("t3") if isinstance(snapshot, dict) else None
    if isinstance(t3d, dict):
        t3_v = t3d.get("last")
    elif isinstance(t3d, (int, float)):
        t3_v = t3d
    else:
        t3_v = None
    if t3_v is not None and close is not None:
        return 1.0 if close > t3_v else (-1.0 if close < t3_v else 0.0)
    return None


def _score_bollinger(pctb):
    """Bollinger %B konumu katkısı (ağırlık 1). pts|None döner."""
    if pctb is None:
        return None
    if pctb >= 1.0:
        return 1.0
    elif pctb > 0.5:
        return 0.5
    elif pctb <= 0.0:
        return -1.0
    return -0.5


def _score_divergence(snapshot):
    """
    RSI/fiyat ayrışması katkısı (ağırlık 1). pts|None döner.

    methodology.md §2.4 ayrışmayı açıkça bir sinyal girdisi sayar; enrich_snapshot
    bunu `snapshot["divergence"]` içinde zaten üretir. v1.1.0 öncesinde bu sinyal
    HESAPLANIP ATILIYORDU (trend_posture okumuyordu) — belge-kod tutarsızlığı.
    Bu fonksiyon o sinyali nihayet puana bağlar:
      - bullish (fiyat lower-low, RSI higher-low) → +1.0  (dip-dönüş erken sinyali)
      - bearish (fiyat higher-high, RSI lower-high) → -1.0 (tepe-dönüş erken sinyali)
      - none / yok → katkı yok (max_score'a eklenmez).
    """
    if not isinstance(snapshot, dict):
        return None
    div = snapshot.get("divergence")
    d = div.get("divergence") if isinstance(div, dict) else None
    if d == "bullish":
        return 1.0
    if d == "bearish":
        return -1.0
    return None


def _score_relative_strength(snapshot):
    """
    Göreli güç katkısı (ağırlık 1). pts|None döner.

    snapshot['relative_strength']['rs_score'] (-1..+1) varsa duruşa katılır
    (yalnız enrich_snapshot'a endeks serisi verildiğinde dolar). "Yükselen dalga"
    düzeltmesi: hisse endeksi yenmiyorsa mutlak güç şişirilmez. Endeks verisi
    yoksa katkı yok (max_score'a eklenmez) — geriye-uyumlu.
    """
    if not isinstance(snapshot, dict):
        return None
    rs = snapshot.get("relative_strength")
    if not isinstance(rs, dict):
        return None
    score = rs.get("rs_score")
    if isinstance(score, (int, float)):
        return max(-1.0, min(1.0, float(score)))
    return None


def _posture_from_norm(score_norm):
    """Normalize edilmiş skoru (-1..+1) 5 seviyeli duruş etiketine eşler."""
    if score_norm >= 0.5:
        return "Güçlü Yukarı"
    elif score_norm >= 0.15:
        return "Zayıf Yukarı"
    elif score_norm > -0.15:
        return "Nötr"
    elif score_norm > -0.5:
        return "Zayıf Aşağı"
    return "Güçlü Aşağı"


def trend_posture(snapshot):
    """
    indicator_snapshot çıktısını (+ ops. supertrend/t3) 5 seviyeli teknik duruşa indirger.

    Puan sistemi (her bileşen -2..+2 ölçeğinde katkı verir, şeffaf):
      - MA dizilimi (close vs sma20/50/200, sma dizilim sırası)
      - RSI bölgesi
      - MACD histogram işareti
      - Supertrend yönü (snapshot'ta varsa)
      - T3 eğimi/konumu (snapshot'ta varsa)
      - Bollinger %B konumu

    Dönen: {"posture":.., "score":.., "score_norm":.., "contributions":{...}, "note":..}
    """
    ind = snapshot.get("indicators", {}) if isinstance(snapshot, dict) else {}

    contributions = {}
    score = 0.0
    max_score = 0.0
    notes = []

    close = ind.get("close")

    # 1) MA dizilimi (ağırlık 2)
    ma_pts, ma_avail = _score_ma_stack(
        close, ind.get("sma_20"), ind.get("sma_50"), ind.get("sma_200"))
    if ma_avail:
        contributions["ma_stack"] = round(ma_pts, 2)
        score += ma_pts
        max_score += 2.0
    else:
        contributions["ma_stack"] = None
        notes.append("MA dizilimi yok")

    # 2) RSI bölgesi (ağırlık 1) — eğim-duyarlı (v1.1.0)
    rp = _score_rsi_zone(ind.get("rsi_14"), ind.get("rsi_14_slope"))
    if rp is not None:
        contributions["rsi"] = round(rp, 2)
        score += rp
        max_score += 1.0
    else:
        contributions["rsi"] = None
        notes.append("RSI yok")

    # 3) MACD histogram (ağırlık 1)
    mp = _score_macd_hist(ind.get("macd_hist"))
    if mp is not None:
        contributions["macd_hist"] = round(mp, 2)
        score += mp
        max_score += 1.0
    else:
        contributions["macd_hist"] = None
        notes.append("MACD yok")

    # 4) Supertrend yönü (ağırlık 2) — snapshot içinde varsa
    sp = _score_supertrend(snapshot)
    if sp is not None:
        contributions["supertrend"] = round(sp, 2)
        score += sp
        max_score += 2.0
    else:
        contributions["supertrend"] = None

    # 5) T3 konumu (ağırlık 1) — close vs T3
    tp = _score_t3(snapshot, close)
    if tp is not None:
        contributions["t3"] = round(tp, 2)
        score += tp
        max_score += 1.0
    else:
        contributions["t3"] = None

    # 6) Bollinger %B (ağırlık 1)
    bp = _score_bollinger(ind.get("bb_pctb"))
    if bp is not None:
        contributions["bollinger_pctb"] = round(bp, 2)
        score += bp
        max_score += 1.0
    else:
        contributions["bollinger_pctb"] = None
        notes.append("Bollinger %B yok")

    # 7) RSI/fiyat ayrışması (ağırlık 1) — v1.1.0: artık puana giriyor (bulgu B).
    #    methodology.md §2.4'ün öngördüğü sinyal; önceki sürümde hesaplanıp atılıyordu.
    dp = _score_divergence(snapshot)
    if dp is not None:
        contributions["divergence"] = round(dp, 2)
        score += dp
        max_score += 1.0
    else:
        contributions["divergence"] = None

    # 8) Göreli güç (ağırlık 1) — v1.1.0: endeks serisi verilmişse (bulgu E).
    #    "Yükselen dalga"yı hisse-seçim sinyalinden ayırır.
    rsp = _score_relative_strength(snapshot)
    if rsp is not None:
        contributions["relative_strength"] = round(rsp, 2)
        score += rsp
        max_score += 1.0
    else:
        contributions["relative_strength"] = None

    # Normalize → -1..+1 → 5 kova
    if max_score == 0:
        posture = "Nötr"
        score_norm = None
        notes.append("hesaplanabilir gösterge yok → varsayılan Nötr")
    else:
        score_norm = score / max_score  # -1..+1
        posture = _posture_from_norm(score_norm)

    # H (v1.1.0): kapsam-güven bağı. Çekirdek referans ağırlığı 8.0'dır
    # (ma_stack 2 + rsi 1 + macd 1 + supertrend 2 + t3 1 + bollinger 1).
    # Etkin ağırlık bunun belirgin altındaysa duruş az göstergeye dayanır;
    # güven bir kademe düşürülmelidir (kısa seride MACD/T3 düşmesi tipik nedendir).
    _CORE_MAX = 8.0
    _LOW_COVERAGE_FLOOR = 5.0
    low_coverage = max_score < _LOW_COVERAGE_FLOOR
    if low_coverage:
        notes.append(f"düşük kapsam (etkin ağırlık {round(max_score, 1)}/"
                     f"{_CORE_MAX:.0f}) → güveni bir kademe düşür")

    return {
        "posture": posture,
        "score": round(score, 2),
        "max_score": round(max_score, 2),
        "score_norm": (round(score_norm, 3) if score_norm is not None else None),
        "coverage_ratio": round(max_score / _CORE_MAX, 2),
        "low_coverage": low_coverage,
        "contributions": contributions,
        "note": ("; ".join(notes) if notes else None),
        "disclaimer": "karar-destek; yatırım tavsiyesi değildir",
    }


# ----------------------------------------------------------------------------
# RSI / fiyat uyumsuzluğu (divergence)
# ----------------------------------------------------------------------------

def rsi_price_divergence(closes, rsi_series, lookback=20):
    """
    Basit pivot-bazlı uyumsuzluk tespiti son `lookback` bar içinde.

      bullish: fiyat daha düşük dip (lower low) yaparken RSI daha yüksek dip yapar.
      bearish: fiyat daha yüksek tepe (higher high) yaparken RSI daha düşük tepe yapar.
      none:    belirgin uyumsuzluk yok / yetersiz veri.

    closes ve rsi_series kuyruktan hizalanır.
    Dönen: {"divergence": "bullish"|"bearish"|"none", "detail":.., "note":..}
    """
    c = _to_floats(closes)
    r = _to_floats(rsi_series)
    if len(c) < 5 or len(r) < 5:
        return {"divergence": "none", "detail": None,
                "note": "yetersiz veri (divergence için >=5 bar gerekir)"}

    m = min(len(c), len(r), lookback)
    cw = c[-m:]
    rw = r[-m:]

    # Yerel tepe/dip indekslerini bul (basit 1-komşu pivot)
    def pivots(seq, kind):
        idx = []
        for i in range(1, len(seq) - 1):
            if kind == "low" and seq[i] < seq[i - 1] and seq[i] < seq[i + 1]:
                idx.append(i)
            if kind == "high" and seq[i] > seq[i - 1] and seq[i] > seq[i + 1]:
                idx.append(i)
        return idx

    detail = None

    # Bullish: son iki fiyat dibi
    lows = pivots(cw, "low")
    if len(lows) >= 2:
        i1, i2 = lows[-2], lows[-1]
        if cw[i2] < cw[i1] and rw[i2] > rw[i1]:
            detail = {
                "type": "bullish",
                "price": [_round(cw[i1]), _round(cw[i2])],
                "rsi": [_round(rw[i1], 2), _round(rw[i2], 2)],
            }
            return {"divergence": "bullish", "detail": detail, "note": None}

    # Bearish: son iki fiyat tepesi
    highs = pivots(cw, "high")
    if len(highs) >= 2:
        i1, i2 = highs[-2], highs[-1]
        if cw[i2] > cw[i1] and rw[i2] < rw[i1]:
            detail = {
                "type": "bearish",
                "price": [_round(cw[i1]), _round(cw[i2])],
                "rsi": [_round(rw[i1], 2), _round(rw[i2], 2)],
            }
            return {"divergence": "bearish", "detail": detail, "note": None}

    return {"divergence": "none", "detail": None, "note": None}


# ----------------------------------------------------------------------------
# Multi-timeframe confluence
# ----------------------------------------------------------------------------

# Zaman-dilimi ağırlıkları (uzun vade trend çapası ağır basar)
_TF_WEIGHTS = {
    "1M": 4.0, "1mo": 4.0, "monthly": 4.0,
    "1W": 3.0, "1wk": 3.0, "weekly": 3.0,
    "1d": 2.0, "1D": 2.0, "daily": 2.0,
    "4h": 1.0, "1h": 0.8, "60m": 0.8,
    "30m": 0.6, "15m": 0.5, "5m": 0.4,
}

_POSTURE_SCORE = {
    "Güçlü Yukarı": 2, "Zayıf Yukarı": 1, "Nötr": 0,
    "Zayıf Aşağı": -1, "Güçlü Aşağı": -2,
}


def _tf_weight(tf):
    if tf in _TF_WEIGHTS:
        return _TF_WEIGHTS[tf]
    low = str(tf).lower()
    for k, v in _TF_WEIGHTS.items():
        if k.lower() == low:
            return v
    return 1.0  # bilinmeyen dilim → nötr ağırlık


def _frame_posture(val):
    """
    Tek bir frame değerinden duruş etiketini normalize eder.

    val ya doğrudan duruş etiketi (str), ya trend_posture çıktısı, ya
    {"posture": "..."} ya da {"posture": {...}} (dict-şekilli posture), ya da
    ham indicator_snapshot olabilir. Geçerli duruş etiketi veya None döner.
    """
    posture = None
    if isinstance(val, str):
        posture = val  # doğrudan duruş etiketi
    elif isinstance(val, dict):
        pv = val.get("posture")
        if isinstance(pv, dict):
            # posture alanı tam trend_posture çıktısını taşıyor olabilir
            pv = pv.get("posture")
        if isinstance(pv, str) and pv in _POSTURE_SCORE:
            posture = pv
        elif "indicators" in val or "close" in val:  # ham snapshot
            posture = trend_posture(val).get("posture")
    if posture is None or posture not in _POSTURE_SCORE:
        return None
    return posture


def _accumulate_frames(frames):
    """
    Frame'leri duruşa çevirir ve ağırlıklı toplamları biriktirir.

    Dönen: (by_tf, notes, weights) — weights bir dict:
      {total, weighted_sum, bull, bear, neutral}
    """
    by_tf = {}
    notes = []
    w_total = 0.0
    weighted_sum = 0.0
    bull_w = 0.0
    bear_w = 0.0
    neutral_w = 0.0

    for tf, val in frames.items():
        posture = _frame_posture(val)
        if posture is None:
            notes.append(f"{tf}: duruş çıkarılamadı")
            by_tf[tf] = None
            continue

        by_tf[tf] = posture
        w = _tf_weight(tf)
        ps = _POSTURE_SCORE[posture]
        w_total += w
        weighted_sum += w * ps
        if ps > 0:
            bull_w += w
        elif ps < 0:
            bear_w += w
        else:
            neutral_w += w

    weights = {"total": w_total, "weighted_sum": weighted_sum,
               "bull": bull_w, "bear": bear_w, "neutral": neutral_w}
    return by_tf, notes, weights


def _agreement_level(bull_w, bear_w, dominant_w, total_w):
    """Baskın yöndeki ağırlık oranından uyum seviyesi etiketi üretir."""
    directional = bull_w + bear_w
    if directional == 0:
        return "nötr"
    if bull_w > 0 and bear_w > 0:
        # her iki yönde de ağırlık var
        return "baskın" if dominant_w / total_w >= 0.8 else "çatışma"
    # tek yönlü (sadece boğa veya sadece ayı + nötrler)
    return "tam uyum" if (dominant_w / total_w) >= 0.99 else "baskın"


def _confluence_summary(anchor, anchor_posture, weighted_score, agreement,
                        alignment_pct):
    """Confluence için kısa Türkçe özet metnini birleştirir."""
    if weighted_score >= 0.5:
        direction_tr = "yukarı yönlü"
    elif weighted_score > -0.5:
        direction_tr = "yatay/kararsız"
    else:
        direction_tr = "aşağı yönlü"

    parts = []
    parts.append(f"Çapa ({anchor}) duruşu: {anchor_posture or 'belirsiz'}.")
    parts.append(f"Ağırlıklı genel görünüm {direction_tr} "
                 f"(skor {round(weighted_score, 2)}/2).")
    if agreement == "tam uyum":
        parts.append("Tüm zaman dilimleri aynı yönde — yüksek güven.")
    elif agreement == "baskın":
        parts.append(f"Zaman dilimleri büyük ölçüde uyumlu (%{alignment_pct}).")
    elif agreement == "çatışma":
        parts.append("Zaman dilimleri çatışıyor — sinyal zayıf, temkinli ol.")
    else:
        parts.append("Belirgin yön yok; nötr.")
    return " ".join(parts)


def confluence(frames):
    """
    Çoklu-zaman-dilimi confluence.

    Girdi `frames`: {timeframe: snapshot|posture|{"posture":..}} biçiminde dict.
      Her değer ya doğrudan trend_posture çıktısı, ya bir indicator_snapshot
      (içinden posture hesaplanır), ya da {"posture": "..."} olabilir.

    Uzun zaman dilimi trend çapası olarak daha ağır tartılır.

    Dönen: {
      "anchor": en uzun TF,
      "weighted_score": ..,        # -2..+2 ölçeğine normalize
      "agreement": "tam uyum"|"baskın"|"karışık"|"çatışma",
      "alignment_pct": ..,         # baskın yöndeki ağırlık oranı
      "by_timeframe": {tf: posture},
      "summary": kısa Türkçe özet,
      "note": ..
    }
    """
    if not isinstance(frames, dict) or not frames:
        return {"anchor": None, "weighted_score": None, "agreement": None,
                "by_timeframe": {}, "summary": "Zaman dilimi verisi yok.",
                "note": "empty frames"}

    by_tf, notes, weights = _accumulate_frames(frames)
    total_w = weights["total"]

    if total_w == 0:
        return {"anchor": None, "weighted_score": None, "agreement": None,
                "by_timeframe": by_tf,
                "summary": "Hiçbir zaman diliminde duruş hesaplanamadı.",
                "note": "; ".join(notes) if notes else None}

    bull_w = weights["bull"]
    bear_w = weights["bear"]
    neutral_w = weights["neutral"]
    weighted_score = weights["weighted_sum"] / total_w  # -2..+2
    anchor = max(frames.keys(), key=_tf_weight)
    anchor_posture = by_tf.get(anchor)

    # Uyum seviyesi: baskın yöndeki ağırlık oranı
    dominant_w = max(bull_w, bear_w)
    alignment_pct = round((dominant_w / total_w) * 100, 1)
    agreement = _agreement_level(bull_w, bear_w, dominant_w, total_w)

    summary = _confluence_summary(
        anchor, anchor_posture, weighted_score, agreement, alignment_pct)

    return {
        "anchor": anchor,
        "anchor_posture": anchor_posture,
        "weighted_score": round(weighted_score, 3),
        "agreement": agreement,
        "alignment_pct": alignment_pct,
        "by_timeframe": by_tf,
        "bull_weight": round(bull_w, 2),
        "bear_weight": round(bear_w, 2),
        "neutral_weight": round(neutral_w, 2),
        "summary": summary,
        "basis": "EOD; intraday mikro-yapı modellenmez",
        "disclaimer": "karar-destek; yatırım tavsiyesi değildir",
        "note": ("; ".join(notes) if notes else None),
    }


# ----------------------------------------------------------------------------
# Yardımcı: snapshot'ı supertrend + t3 ile zenginleştir
# ----------------------------------------------------------------------------

def enrich_snapshot(ohlc, index_closes=None, rsi_slope_window=3, rs_lookback=13):
    """
    indicator_snapshot + supertrend + t3 + ayrışma + (ops.) göreli güç + boşluk
    maruziyeti + duruş — tek pakette (v1.1.0).

    index_closes (ops.): endeks (ör. XU100) kapanış serisi verilirse, göreli güç
    hesaplanır ve duruş puanına dahil edilir (bulgu E — "yükselen dalga" düzeltmesi).

    rsi_slope_window (vars. 3) ve rs_lookback (vars. 13): RSI eğim penceresi ile
    göreli güç lookback'i; walk-forward kalibrasyonu için imzaya açıldı (v1.1.1).
    Varsayılanlar gömülü değerlerle birebir aynıdır — varsayılan çağrı davranışı
    değişmez.

    KRİTİK SIRALAMA (v1.1.0 kök düzeltmesi): tüm zenginleştirmeler (ayrışma, RSI
    eğimi, göreli güç) duruştan ÖNCE enjekte edilir; böylece bunlar trend_posture
    puanına GERÇEKTEN girer. Önceki sürümde duruş, ayrışma snapshot'a yazılmadan
    hesaplanıyordu — bu yüzden ayrışma sinyali hesaplanıp atılıyordu (bulgu B).
    """
    norm = normalize_ohlc(ohlc)
    snap = indicator_snapshot(norm)
    snap["supertrend"] = supertrend(norm["high"], norm["low"], norm["close"])
    snap["t3"] = t3(norm["close"])

    # RSI serisi + son-bar eğimi (C — eğim-duyarlı RSI okuması için)
    rsi_full = rsi(norm["close"], 14, full=True)
    rsi_vals = rsi_full.get("values", []) if isinstance(rsi_full, dict) else []
    if isinstance(snap.get("indicators"), dict):
        snap["indicators"]["rsi_14_slope"] = _series_slope(rsi_vals, window=rsi_slope_window)

    # Ayrışma (B — artık puana girecek, çünkü posture'dan ÖNCE yazılıyor)
    snap["divergence"] = rsi_price_divergence(norm["close"], rsi_vals)

    # Göreli güç (E — yalnız endeks serisi verilmişse)
    if index_closes is not None:
        snap["relative_strength"] = relative_strength(norm["close"], index_closes, lookback=rs_lookback)

    # Boşluk maruziyeti (F — EOD kör-nokta şeffaflığı)
    snap["gap_exposure"] = gap_exposure(norm)

    # Duruş — TÜM zenginleştirmelerden SONRA hesaplanır
    snap["posture"] = trend_posture(snap)
    return snap


# ----------------------------------------------------------------------------
# Self-test / CLI
# ----------------------------------------------------------------------------

def _synthetic(n=260, slope=0.35, phase=0.0):
    closes, highs, lows = [], [], []
    base = 100.0
    for i in range(n):
        trend = base + i * slope
        wave = 4.0 * math.sin(i / 9.0 + phase) + 1.5 * math.cos(i / 3.0)
        c = trend + wave
        h = c + 1.2 + abs(math.sin(i / 5.0))
        l = c - 1.2 - abs(math.cos(i / 7.0))
        closes.append(round(c, 2))
        highs.append(round(h, 2))
        lows.append(round(l, 2))
    return {"close": closes, "high": highs, "low": lows}


def _run_selftest():
    up = _synthetic(260, slope=0.35)
    down = _synthetic(260, slope=-0.30, phase=1.0)

    snap_up = enrich_snapshot(up)
    snap_down = enrich_snapshot(down)

    # pivot, son barın bir önceki H/L/C ile
    piv_classic = pivot_points(up["high"][-2], up["low"][-2], up["close"][-2], "classic")
    piv_fib = pivot_points(up["high"][-2], up["low"][-2], up["close"][-2], "fibonacci")

    conf = confluence({
        "1W": snap_up,            # uzun vade çapa (yukarı)
        "1d": snap_up,            # günlük (yukarı)
        "1h": snap_down,          # kısa vade (aşağı) → çatışma sinyali test
    })

    return {
        "selftest": "technical_plus",
        "uptrend_posture": snap_up["posture"],
        "uptrend_supertrend": snap_up["supertrend"],
        "uptrend_t3": snap_up["t3"],
        "uptrend_divergence": snap_up["divergence"],
        "downtrend_posture": snap_down["posture"],
        "pivot_classic": piv_classic,
        "pivot_fibonacci": piv_fib,
        "confluence": conf,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="BIST üst-düzey teknik okuma — posture + confluence (karar-destek).")
    parser.add_argument("--file", help="frames JSON: {tf: ohlc|snapshot} "
                                        "veya tek OHLC objesi")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args(argv)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Heuristik: değerleri OHLC ise → her birini zenginleştirip confluence
        if isinstance(data, dict) and all(
            isinstance(v, dict) and ("close" in v or "indicators" in v or "posture" in v)
            for v in data.values()
        ) and not ("close" in data or "indicators" in data):
            frames = {}
            for tf, v in data.items():
                if "indicators" in v or "posture" in v:
                    frames[tf] = v
                else:
                    frames[tf] = enrich_snapshot(v)
            result = {
                "frames": {tf: (s.get("posture") if isinstance(s, dict) else None)
                           for tf, s in frames.items()},
                "confluence": confluence(frames),
            }
        else:
            # tek OHLC serisi
            result = enrich_snapshot(data)
    else:
        result = _run_selftest()

    print(json.dumps(result, ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
