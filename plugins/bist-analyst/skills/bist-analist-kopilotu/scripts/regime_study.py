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
