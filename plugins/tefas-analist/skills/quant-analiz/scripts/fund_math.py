#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fund_math.py — TEFAS fon analizi kuant motorunun ÇEKİRDEĞİ.

Tüm diğer modüllerin (fund_returns, risk_adjusted, drawdown_var, volatility_beta,
monte_carlo, style_analysis, portfolio_opt, concentration, cost_analysis,
fund_quality_score, fund_monitor) tek numerik katmanı. NAV/getiri ayrıştırma +
istatistik primitifleri + el-yazımı lineer cebir (kovaryans, Cholesky, SPD çözüm,
Gauss-Jordan ters, nearest-PD, simpleks projeksiyonu).

Konvansiyon (bist-analyst betikleriyle birebir):
- Veri GÜN-SONU (EOD) NAV; intraday modellenmez.
- Çıktılar KARAR-DESTEK amaçlıdır; YATIRIM TAVSİYESİ DEĞİLDİR.
- Kısa/eksik/bozuk seride asla çökmez; None + note döner.
- Bağımlılık: yalnız Python standart kütüphanesi (math, json, sys, argparse,
  statistics, datetime).

CLI: `--file nav.json` → seri tanılaması. Argümansız → self-test.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import date

DISCLAIMER = "karar-destek; yatırım tavsiyesi değildir"

# ---------------------------------------------------------------------------
# Numerik yardımcılar (Türkçe-locale toleranslı)
# ---------------------------------------------------------------------------

def to_float(v):
    """None/bool/Türkçe-ondalık/%/sentinel toleranslı float dönüşümü; başarısız → None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    s = str(v).strip()
    if s == "" or s in {"-", "—", "N/A", "n/a", "NA", "null", "None"}:
        return None
    s = s.replace("%", "").replace(" ", "")
    if "," in s and "." in s:        # "1.234,56" → "1234.56"
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                    # "12,3" → "12.3"
        s = s.replace(",", ".")
    try:
        f = float(s)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(f) or math.isinf(f)) else f


def _round(x, n=6):
    if x is None:
        return None
    try:
        if math.isnan(x) or math.isinf(x):
            return None
    except (TypeError, ValueError):
        return None
    return round(float(x), n)


def clamp(x, lo, hi):
    if x is None:
        return None
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# Seri / takvim primitifleri
# ---------------------------------------------------------------------------

def normalize_nav(data):
    """
    NAV serisini esnek girdiden {"dates":[iso...], "prices":[float...]} biçimine getirir.

    Kabul: [{date,price}], {date:[],price:[]}, anahtar varyasyonları
    (nav/fiyat/deger/value/close ; tarih/gun/date). Artan tarihe göre sıralar,
    parse-edilemeyen/<=0 fiyatları atar, aynı-gün tekrarında sonuncuyu tutar.
    """
    pairs = []  # (iso_date, price)

    def add(d, p):
        iso = _to_iso(d)
        pf = to_float(p)
        if iso is not None and pf is not None and pf > 0:
            pairs.append((iso, pf))

    if isinstance(data, dict) and ("price" in data or "prices" in data or "nav" in data):
        dates = data.get("dates") or data.get("date") or data.get("tarih") or []
        prices = (data.get("prices") or data.get("price") or data.get("nav")
                  or data.get("deger") or data.get("value") or [])
        for d, p in zip(dates, prices):
            add(d, p)
    elif isinstance(data, dict) and "nav" in data and isinstance(data["nav"], list):
        for row in data["nav"]:
            if isinstance(row, dict):
                add(row.get("date") or row.get("tarih"), row.get("price") or row.get("nav"))
    elif isinstance(data, (list, tuple)):
        for row in data:
            if isinstance(row, dict):
                d = row.get("date") or row.get("tarih") or row.get("gun")
                p = (row.get("price") if row.get("price") is not None else
                     row.get("nav") if row.get("nav") is not None else
                     row.get("deger") if row.get("deger") is not None else
                     row.get("value") if row.get("value") is not None else
                     row.get("close"))
                add(d, p)
            else:
                pf = to_float(row)
                if pf is not None and pf > 0:
                    pairs.append((None, pf))  # tarihsiz düz seri

    # tarihliyse sırala+dedup; tarihsizse sırayı koru
    if pairs and all(p[0] is not None for p in pairs):
        dedup = {}
        for d, p in pairs:
            dedup[d] = p
        items = sorted(dedup.items(), key=lambda kv: kv[0])
        return {"dates": [k for k, _ in items], "prices": [v for _, v in items]}
    return {"dates": [d for d, _ in pairs], "prices": [p for _, p in pairs]}


def _to_iso(v):
    """epoch-ms / DD.MM.YYYY / ISO → 'YYYY-MM-DD'; başarısız → None."""
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        try:
            from datetime import datetime, timezone
            return datetime.fromtimestamp(float(v) / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
        except (OverflowError, OSError, ValueError):
            return None
    s = str(v).strip()
    for sep in (".", "/"):
        parts = s.split(sep)
        if len(parts) == 3 and len(parts[0]) == 2 and len(parts[2]) == 4:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return None


def simple_returns(prices):
    """r_t = P_t/P_{t-1} - 1. P_{t-1}<=0 adımı atlanır."""
    out = []
    for i in range(1, len(prices)):
        p0, p1 = prices[i - 1], prices[i]
        if p0 and p0 > 0:
            out.append(p1 / p0 - 1.0)
    return out


def log_returns(prices):
    """g_t = ln(P_t/P_{t-1}). P_{t-1}<=0 veya P_t<=0 adımı atlanır."""
    out = []
    for i in range(1, len(prices)):
        p0, p1 = prices[i - 1], prices[i]
        if p0 and p0 > 0 and p1 and p1 > 0:
            out.append(math.log(p1 / p0))
    return out


def align_series(*series):
    """
    Birden çok {"dates","prices"} serisini ortak tarih ekseninde inner-join eder.
    Dönen: (dates, [aligned_prices_1, aligned_prices_2, ...]).
    Tarihsiz seriler için index-hizalaması (en kısa uzunluğa kırpma) uygulanır.
    """
    norm = [s if isinstance(s, dict) and "prices" in s else normalize_nav(s) for s in series]
    have_dates = all(s["dates"] and len(s["dates"]) == len(s["prices"]) for s in norm)
    if have_dates:
        common = set(norm[0]["dates"])
        for s in norm[1:]:
            common &= set(s["dates"])
        dates = sorted(common)
        maps = [dict(zip(s["dates"], s["prices"])) for s in norm]
        aligned = [[m[d] for d in dates] for m in maps]
        return dates, aligned
    n = min((len(s["prices"]) for s in norm), default=0)
    return [], [s["prices"][-n:] for s in norm]


def trading_days_per_year(dates, default=252):
    """Tarih ekseninden yıllıklama faktörünü çıkar (günlük→252, haftalık→52, aylık→12)."""
    if not dates or len(dates) < 3:
        return default, "varsayılan (yetersiz tarih)"
    gaps = []
    for i in range(1, len(dates)):
        try:
            d0 = date.fromisoformat(dates[i - 1])
            d1 = date.fromisoformat(dates[i])
            gaps.append((d1 - d0).days)
        except (ValueError, TypeError):
            continue
    if not gaps:
        return default, "varsayılan (tarih ayrıştırılamadı)"
    med = statistics.median(gaps)
    if med <= 2:
        return 252, "günlük (252)"
    if med <= 10:
        return 52, "haftalık (52)"
    return 12, "aylık (12)"


# ---------------------------------------------------------------------------
# İstatistik primitifleri (None-güvenli, n-korumalı)
# ---------------------------------------------------------------------------

def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def pstdev(xs):
    xs = [x for x in xs if x is not None]
    return statistics.pstdev(xs) if len(xs) >= 2 else None


def stdev(xs):
    xs = [x for x in xs if x is not None]
    return statistics.stdev(xs) if len(xs) >= 2 else None


def covariance(xs, ys):
    pairs = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    n = len(pairs)
    if n < 2:
        return None
    mx = sum(a for a, _ in pairs) / n
    my = sum(b for _, b in pairs) / n
    return sum((a - mx) * (b - my) for a, b in pairs) / (n - 1)


def correlation(xs, ys):
    sx, sy = stdev(xs), stdev(ys)
    cov = covariance(xs, ys)
    if cov is None or not sx or not sy:
        return None
    return cov / (sx * sy)


def downside_deviation(returns, mar=0.0):
    """Aşağı-yön sapması: sqrt(mean(min(r-MAR,0)^2)). MAR aynı periyot biriminde."""
    rs = [r for r in returns if r is not None]
    if len(rs) < 2:
        return None
    sq = [min(r - mar, 0.0) ** 2 for r in rs]
    return math.sqrt(sum(sq) / len(sq))


def percentile(sorted_vals, p):
    """Lineer-interpolasyonlu yüzdebirlik; p ∈ [0,1]. Girdi SIRALI olmalı."""
    n = len(sorted_vals)
    if n == 0:
        return None
    if n == 1:
        return sorted_vals[0]
    idx = p * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def skewness(xs):
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 3:
        return None
    m = sum(xs) / n
    s = math.sqrt(sum((x - m) ** 2 for x in xs) / n)
    if s == 0:
        return None
    return (sum((x - m) ** 3 for x in xs) / n) / (s ** 3)


def kurtosis(xs):
    """Fazla (excess) basıklık."""
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 4:
        return None
    m = sum(xs) / n
    s2 = sum((x - m) ** 2 for x in xs) / n
    if s2 == 0:
        return None
    return (sum((x - m) ** 4 for x in xs) / n) / (s2 ** 2) - 3.0


# ---------------------------------------------------------------------------
# Lineer cebir (saf list-of-lists; küçük N için yeterli)
# ---------------------------------------------------------------------------

def transpose(A):
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


def matvec(A, x):
    return [sum(a * xi for a, xi in zip(row, x)) for row in A]


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def cov_matrix(returns_matrix):
    """returns_matrix: eşit-uzunluklu getiri vektörleri listesi → kovaryans matrisi."""
    k = len(returns_matrix)
    return [[covariance(returns_matrix[i], returns_matrix[j]) or 0.0 for j in range(k)] for i in range(k)]


def corr_matrix(returns_matrix):
    k = len(returns_matrix)
    out = []
    for i in range(k):
        row = []
        for j in range(k):
            if i == j:
                row.append(1.0)
            else:
                c = correlation(returns_matrix[i], returns_matrix[j])
                row.append(c if c is not None else 0.0)
        out.append(row)
    return out


def cholesky(A):
    """Alt-üçgen L: A = L Lᵀ. PD değilse None."""
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                d = A[i][i] - s
                if d <= 0:
                    return None
                L[i][j] = math.sqrt(d)
            else:
                if L[j][j] == 0:
                    return None
                L[i][j] = (A[i][j] - s) / L[j][j]
    return L


def solve_spd(A, b):
    """SPD A için Ax=b'yi Cholesky ileri/geri yerine koymayla çözer. None → çözülemedi."""
    L = cholesky(A)
    if L is None:
        return None
    n = len(A)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x


def inverse_gauss_jordan(A):
    """Kısmi pivotlu Gauss-Jordan ters; tekil → None."""
    n = len(A)
    M = [list(map(float, A[i])) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                factor = M[r][col]
                M[r] = [a - factor * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]


def nearest_pd(A, eps=1e-8):
    """Ridge/jitter: A + c·I ile en küçük c>=0 ekleyerek PD'ye taşı (kısa seri kurtarma)."""
    n = len(A)
    c = 0.0
    bump = eps
    for _ in range(50):
        M = [[A[i][j] + (c if i == j else 0.0) for j in range(n)] for i in range(n)]
        if cholesky(M) is not None:
            return M
        c = bump
        bump *= 10
    # son çare: köşegen
    return [[A[i][j] if i == j else 0.0 for j in range(n)] for i in range(n)]


def simplex_projection(v):
    """
    v'yi Öklid anlamında olasılık simpleksine projekte eder (Duchi 2008):
    w_i >= 0, sum(w_i) = 1. style_analysis ve portfolio_opt (long-only) ortak kullanır.
    """
    n = len(v)
    if n == 0:
        return []
    u = sorted(v, reverse=True)
    css = 0.0
    rho = 0
    theta = 0.0
    for i in range(n):
        css += u[i]
        t = (css - 1.0) / (i + 1)
        if u[i] - t > 0:
            rho = i + 1
            theta = t
    return [max(x - theta, 0.0) for x in v]


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _synthetic_nav(n=260, p0=1.0, drift=0.0003, amp=0.02):
    dates, prices = [], []
    base = date(2025, 1, 1).toordinal()
    p = p0
    for i in range(n):
        p *= (1 + drift + amp * math.sin(i / 9.0))
        prices.append(p)
        dates.append(date.fromordinal(base + i).isoformat())
    return {"dates": dates, "prices": prices}


def _run_selftest():
    nav = _synthetic_nav(260)
    norm = normalize_nav([{"date": d, "price": p} for d, p in zip(nav["dates"], nav["prices"])])
    assert len(norm["prices"]) == 260, "normalize_nav uzunluk"
    rs = simple_returns(norm["prices"])
    assert len(rs) == 259
    ppy, basis = trading_days_per_year(norm["dates"])
    assert ppy == 252, f"ppy {ppy}"

    # lineer cebir round-trip
    A = [[4.0, 1.0, 0.5], [1.0, 3.0, 0.2], [0.5, 0.2, 2.0]]
    L = cholesky(A)
    assert L is not None
    LLt = matmul(L, transpose(L))
    assert all(abs(LLt[i][j] - A[i][j]) < 1e-9 for i in range(3) for j in range(3)), "L Lᵀ ≈ A"
    Ainv = inverse_gauss_jordan(A)
    prod = matmul(A, Ainv)
    assert all(abs(prod[i][j] - (1.0 if i == j else 0.0)) < 1e-9 for i in range(3) for j in range(3)), "A·A⁻¹≈I"
    x = solve_spd(A, [1.0, 2.0, 3.0])
    assert all(abs(v) < 1e6 for v in x)

    # simpleks projeksiyonu
    w = simplex_projection([0.5, 0.3, 10.0])
    assert abs(sum(w) - 1.0) < 1e-9 and all(wi >= 0 for wi in w), "simpleks"

    # istatistik
    assert to_float("1.234,56") == 1234.56
    assert percentile([1, 2, 3, 4], 0.5) == 2.5

    print("== fund_math: ALL TESTS PASSED ==", file=sys.stderr)
    return {
        "selftest": "fund_math",
        "ppy": ppy, "ppy_basis": basis,
        "n_returns": len(rs),
        "cholesky_ok": True, "inverse_ok": True, "simplex_sum": _round(sum(w), 6),
        "disclaimer": DISCLAIMER,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="fund_math çekirdek — NAV tanılaması / self-test.")
    parser.add_argument("--file", help="NAV JSON ([{date,price}] veya {dates,prices}).")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args(argv)

    if not args.file:
        print(json.dumps(_run_selftest(), ensure_ascii=False, indent=args.indent))
        return 0

    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Girdi okunamadı: {exc}", "disclaimer": DISCLAIMER}, ensure_ascii=False))
        return 1

    nav = normalize_nav(data)
    ppy, basis = trading_days_per_year(nav["dates"])
    out = {
        "points": len(nav["prices"]),
        "first_date": nav["dates"][0] if nav["dates"] else None,
        "last_date": nav["dates"][-1] if nav["dates"] else None,
        "ppy": ppy, "ppy_basis": basis,
        "disclaimer": DISCLAIMER,
    }
    print(json.dumps(out, ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
