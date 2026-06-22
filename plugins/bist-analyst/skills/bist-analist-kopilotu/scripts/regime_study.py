#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
regime_study.py — Teknik-duruş motorunun BETİMSEL değeri (oynaklık + trend/yatay rejim).

NEDEN VAR
---------
`skill_study` "duruş → ileri GETİRİ (yön)" sordu; cevap: skill yok. Bu betik
FARKLI bir ekseni sınar: duruş kategorilerinin betimsel/yapısal değeri.
  - VOL: aşırı duruşlar, MEVCUT oynaklığın ÖTESİNDE ileri-vol bilgisi taşır mı?
    (Oynaklık otokorele → kontrolsüz test sahte-pozitif; bu yüzden kısmi korelasyon.)
  - REJİM: yönlü duruş, trendli (yüksek efficiency-ratio) vs çalkantılı pencere mi önceliyor?

SIZINTISIZLIK: duruş `bars[:t]`'ten (backtest_posture'a delege; skorlama çoğaltılmaz);
ileri büyüklükler `bars[t-1 … t+h-1]`'ten. Örtüşmeyen bloklar (h-adımlı) → bağımsız.
PARAMETRE: sabit varsayılan (3/13) — skill testi, tuning değil.
Karar-destek; yatırım tavsiyesi DEĞİLDİR. Bağımlılık: stdlib + skill_study + backtest_posture.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict

try:
    from skill_study import (_t_two_sided_p, _mean, _std,
                             nonoverlap_times, _slice)
    from backtest_posture import backtest_posture, _spearman, _ranks
except ImportError:  # pragma: no cover
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from skill_study import (_t_two_sided_p, _mean, _std,
                             nonoverlap_times, _slice)
    from backtest_posture import backtest_posture, _spearman, _ranks


# --------------------------------------------------------------------------- #
# Saf fiyat istatistiği (stdlib)
# --------------------------------------------------------------------------- #

def _log_returns(closes):
    """Ardışık log-getiriler; herhangi bir kapanış ≤0 ise None (geçersiz seri)."""
    if not closes or len(closes) < 2:
        return None
    out = []
    for i in range(1, len(closes)):
        prev, cur = closes[i - 1], closes[i]
        if prev <= 0 or cur <= 0:
            return None
        out.append(math.log(cur / prev))
    return out


def _realized_vol(closes):
    """Log-getiri std'si (ddof=1). <2 getiri veya geçersiz seri → None."""
    rets = _log_returns(closes)
    if rets is None or len(rets) < 2:
        return None
    return _std(rets)


def _efficiency_ratio(closes):
    """|net hareket| / Σ|adım| ∈ [0,1]. 1=saf trend, ~0=çalkantı. Geçersiz → None."""
    if not closes or len(closes) < 2:
        return None
    if any(c <= 0 for c in closes):
        return None
    net = abs(closes[-1] - closes[0])
    path = sum(abs(closes[i] - closes[i - 1]) for i in range(1, len(closes)))
    if path == 0:
        return None
    return net / path


# --------------------------------------------------------------------------- #
# Korelasyon & dağılım istatistikleri (stdlib)
# --------------------------------------------------------------------------- #

def _partial_spearman(x, y, z):
    """Kısmi Spearman ρ(x,y|z). <4 nokta veya kontrol payda ~0 → None."""
    if len(x) < 4 or len(y) != len(x) or len(z) != len(x):
        return None
    rxy = _spearman(x, y)
    rxz = _spearman(x, z)
    ryz = _spearman(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    denom = (1.0 - rxz * rxz) * (1.0 - ryz * ryz)
    if denom <= 1e-12:
        return None
    return (rxy - rxz * ryz) / math.sqrt(denom)


def _gammq(a, x, itmax=200, eps=3e-12):
    """Düzenlenmiş üst eksik gamma Q(a,x)=1-P(a,x) (Numerical Recipes gser/gcf)."""
    if x < 0 or a <= 0:
        return 1.0
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:  # seri → P, sonra Q=1-P
        ap = a
        s = 1.0 / a
        d = s
        for _ in range(itmax):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * eps:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gln)
    # sürekli kesir → Q doğrudan
    b = x + 1.0 - a
    c = 1.0 / 1e-30
    d = 1.0 / b
    h = d
    for i in range(1, itmax + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h * math.exp(-x + a * math.log(x) - gln)


def _chi2_sf(x, df):
    """χ² sağ-kuyruk olasılığı P(X>x) = Q(df/2, x/2)."""
    if df <= 0:
        return None
    if x <= 0:
        return 1.0
    return _gammq(df / 2.0, x / 2.0)


def _kruskal_wallis(groups):
    """Kruskal-Wallis H + η² + χ²-yaklaşık p. <2 dolu grup → None.

    η² = (H - k + 1)/(n - k); k=dolu grup sayısı, n=toplam gözlem.
    Bağ-düzeltmesi uygulanmaz (betimsel sağlamlık ölçütü); küçük etkisi belirtilir.
    """
    nonempty = [g for g in groups if g]
    k = len(nonempty)
    if k < 2:
        return None
    pooled = []
    for g in nonempty:
        pooled.extend(g)
    n = len(pooled)
    if n <= k:
        return None
    ranks = _ranks(pooled)
    idx = 0
    rank_sq_sum = 0.0
    for g in nonempty:
        ng = len(g)
        rg = sum(ranks[idx:idx + ng])
        rank_sq_sum += (rg * rg) / ng
        idx += ng
    H = 12.0 / (n * (n + 1)) * rank_sq_sum - 3.0 * (n + 1)
    eta2 = (H - k + 1.0) / (n - k)
    return {"H": H, "df": k - 1, "eta2": eta2, "n": n, "k": k,
            "p": _chi2_sf(H, k - 1)}


def _sidak(p, m):
    """Šidák düzeltmesi: 1-(1-p)**m, [0,1]. p None → None."""
    if p is None or m <= 0:
        return None
    return max(0.0, min(1.0, 1.0 - (1.0 - p) ** m))
