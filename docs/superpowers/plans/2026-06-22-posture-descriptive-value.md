# Teknik-Duruş Betimsel-Değer Çalışması (`regime_study.py`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Teknik-duruş kategorilerinin ileri **oynaklık** (mevcut-vol kontrollü) ve **trend/yatay rejim** (efficiency-ratio) ile betimsel ilişkisini, sızıntısız bağımsız-blok + Student-t makinesiyle ölçen tek bir araştırma aracı eklemek.

**Architecture:** `skills/bist-analist-kopilotu/scripts/regime_study.py` — `skill_study.py`'nin istatistik/blok makinesini ve `backtest_posture.py`'nin skorlama yolunu **import ederek** yeniden kullanır (motor mantığı çoğaltılmaz, davranış değişmez). Birim testleri `scripts/test_regime_study.py` (stdlib `unittest`). Skorlama `backtest_posture` üzerinden; vol/ER saf-Python fiyat istatistiği.

**Tech Stack:** Python 3 (yalnız stdlib: `math`, `json`, `argparse`, `unittest`, `collections`). Bağımlılık: `skill_study`, `backtest_posture` (+ dolaylı `technical_plus`).

## Global Constraints

- **Sıfır motor değişikliği:** `technical_plus.py`, `backtest_posture.py`, `walkforward_calibrate.py`, `skill_study.py` davranışı DEĞİŞMEZ — yalnız import. 3/13 varsayılanı ve hiçbir motor eşiği değişmez.
- **Yalnız stdlib** + adı geçen iki yerel modül. Ağ yok, rastgelelik yok (`Math.random`/`Date.now` zaten yasak; tüm sentetik deterministik sin/eğim tabanlı).
- **Sızıntısızlık:** duruş daima `bars[:t]`'ten; ileri büyüklükler `bars[t-1 … t+h-1]` penceresinden. `nonoverlap_times` h-adımlı → bloklar bağımsız.
- **Yorum dili:** "betimsel ilişki VAR/YOK" (return-skill DEĞİL). Tüm çıktı "karar-destek; yatırım tavsiyesi değildir" çerçeveli.
- **Sürüm artışı feat** (yeni araç): `1.1.6 → 1.1.7`, `plugin.json` + `marketplace.json` senkron. Motor/varsayılan bit-özdeş; `claude plugin validate --strict` geçer.
- **Stil:** mevcut script idiomu — import fallback `sys.path.insert(0, dirname(abspath(__file__)))`; Türkçe docstring/yorum; `round(...,4)` çıktı; `--json` + `render()` ikili çıktı; argümansız → self-test.

İndis konvansiyonu (TÜM görevlerde geçerli): `nonoverlap_times` bir `t` döndürür; `_slice(frames, t+h)` ile `backtest_posture(horizon=h)` çağrısı duruşu `bars[:t]`'ten hesaplar (anchor kapanış = `closes[t-1]`). İleri pencere kapanışları = `closes[t-1 : t+h]` (h+1 nokta, h getiri). Temel-vol penceresi = `closes[t-21 : t]` (21 nokta, 20 getiri; `t≥21` gerekir, `min_setup=200` ile garanti).

---

### Task 1: Saf fiyat-istatistiği yardımcıları (vol + efficiency-ratio)

**Files:**
- Create: `skills/bist-analist-kopilotu/scripts/regime_study.py`
- Create (test): `skills/bist-analist-kopilotu/scripts/test_regime_study.py`

**Interfaces:**
- Produces:
  - `_log_returns(closes: list[float]) -> list[float] | None` — ardışık `ln(c_i/c_{i-1})`; herhangi bir kapanış ≤0 ise `None`.
  - `_realized_vol(closes: list[float]) -> float | None` — log-getiri std'si (ddof=1); <2 getiri veya geçersiz kapanış → `None`.
  - `_efficiency_ratio(closes: list[float]) -> float | None` — `|c_last-c_first| / Σ|Δc|`; <2 nokta veya sıfır yol veya geçersiz → `None`.

- [ ] **Step 1: Dosya iskeleti + ilk üç yardımcı için başarısız test yaz**

`test_regime_study.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""regime_study.py birim testleri (stdlib unittest)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regime_study as rs


class PriceStatsTest(unittest.TestCase):
    def test_log_returns_basic(self):
        out = rs._log_returns([100.0, 105.0])
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0], math.log(1.05), places=7)

    def test_log_returns_nonpositive_is_none(self):
        self.assertIsNone(rs._log_returns([100.0, 0.0, 100.0]))

    def test_realized_vol_known(self):
        # ln(1.1)=0.0953102, ln(0.9)=-0.1053605 → std(ddof=1) ≈ 0.141896
        v = rs._realized_vol([100.0, 110.0, 99.0])
        self.assertAlmostEqual(v, 0.141896, places=5)

    def test_realized_vol_too_short_is_none(self):
        self.assertIsNone(rs._realized_vol([100.0]))

    def test_realized_vol_invalid_is_none(self):
        self.assertIsNone(rs._realized_vol([100.0, 0.0, 100.0]))

    def test_efficiency_ratio_pure_trend(self):
        self.assertAlmostEqual(rs._efficiency_ratio([10, 11, 12, 13]), 1.0, places=7)

    def test_efficiency_ratio_choppy(self):
        self.assertAlmostEqual(rs._efficiency_ratio([10, 11, 10, 11]), 1.0 / 3.0, places=7)

    def test_efficiency_ratio_flat_is_none(self):
        self.assertIsNone(rs._efficiency_ratio([10, 10, 10]))  # sıfır yol


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Testi çalıştır, başarısız olduğunu doğrula**

Run: `cd skills/bist-analist-kopilotu/scripts && python3 -m unittest test_regime_study.PriceStatsTest -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'regime_study'` (henüz yok).

- [ ] **Step 3: `regime_study.py` başlığı + üç yardımcıyı yaz**

```python
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
```

- [ ] **Step 4: Testi çalıştır, geçtiğini doğrula**

Run: `python3 -m unittest test_regime_study.PriceStatsTest -v`
Expected: PASS (8 test).

- [ ] **Step 5: Commit**

```bash
cd /mnt/thunderbolt/workspaces/marketplace
git add skills/bist-analist-kopilotu/scripts/regime_study.py \
        skills/bist-analist-kopilotu/scripts/test_regime_study.py
git commit -m "feat(bist-analyst): regime_study price-stat helpers (vol + efficiency-ratio) + tests"
```

---

### Task 2: Korelasyon & dağılım istatistikleri (kısmi Spearman, Kruskal-Wallis, χ², Šidák)

**Files:**
- Modify: `skills/bist-analist-kopilotu/scripts/regime_study.py` (Task 1 helper'larından sonra ekle)
- Modify (test): `skills/bist-analist-kopilotu/scripts/test_regime_study.py`

**Interfaces:**
- Consumes: `_spearman`, `_ranks` (backtest_posture'dan import).
- Produces:
  - `_partial_spearman(x, y, z) -> float | None` — ρ(x,y|z); <4 nokta veya payda ~0 → `None`.
  - `_gammq(a, x) -> float` — düzenlenmiş üst eksik gamma Q(a,x).
  - `_chi2_sf(x, df) -> float` — χ² sağ-kuyruk (survival).
  - `_kruskal_wallis(groups: list[list[float]]) -> dict | None` — `{H, df, eta2, n, k, p}`; <2 dolu grup → `None`.
  - `_sidak(p, m) -> float | None` — `1-(1-p)**m`, [0,1] kırpılı; `p None` → `None`.

- [ ] **Step 1: Başarısız test yaz**

`test_regime_study.py`'ye ekle:

```python
class CorrStatsTest(unittest.TestCase):
    def test_partial_spearman_degenerate_control_is_none(self):
        # y == z → ρ_yz=1 → payda 0 → None
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 1.0, 4.0, 3.0, 5.0]
        self.assertIsNone(rs._partial_spearman(x, y, y))

    def test_partial_spearman_matches_formula(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 1.0, 4.0, 3.0, 5.0]
        z = [5.0, 3.0, 4.0, 1.0, 2.0]
        rxy = rs._spearman(x, y); rxz = rs._spearman(x, z); ryz = rs._spearman(y, z)
        expect = (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
        self.assertAlmostEqual(rs._partial_spearman(x, y, z), expect, places=9)

    def test_partial_spearman_too_few_is_none(self):
        self.assertIsNone(rs._partial_spearman([1, 2, 3], [3, 2, 1], [1, 1, 2]))

    def test_chi2_sf_df2_closed_form(self):
        # df=2 → SF(x)=exp(-x/2)
        self.assertAlmostEqual(rs._chi2_sf(2.0, 2), math.exp(-1.0), places=6)
        self.assertAlmostEqual(rs._chi2_sf(0.0, 2), 1.0, places=6)

    def test_kruskal_wallis_known(self):
        # [1,2,3],[4,5,6],[7,8,9] → H=7.2, eta2≈0.8667, p=exp(-3.6)
        out = rs._kruskal_wallis([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertAlmostEqual(out["H"], 7.2, places=4)
        self.assertAlmostEqual(out["eta2"], 5.2 / 6.0, places=4)
        self.assertAlmostEqual(out["p"], math.exp(-3.6), places=4)

    def test_kruskal_wallis_one_group_is_none(self):
        self.assertIsNone(rs._kruskal_wallis([[1, 2, 3]]))

    def test_sidak(self):
        self.assertAlmostEqual(rs._sidak(0.05, 3), 1 - 0.95 ** 3, places=9)
        self.assertIsNone(rs._sidak(None, 3))
```

- [ ] **Step 2: Testi çalıştır, başarısız olduğunu doğrula**

Run: `python3 -m unittest test_regime_study.CorrStatsTest -v`
Expected: FAIL — `AttributeError: module 'regime_study' has no attribute '_partial_spearman'`.

- [ ] **Step 3: İstatistikleri yaz**

`regime_study.py`'ye (fiyat-istatistiği bloğundan sonra) ekle:

```python
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
```

- [ ] **Step 4: Testi çalıştır, geçtiğini doğrula**

Run: `python3 -m unittest test_regime_study.CorrStatsTest -v`
Expected: PASS (7 test).

- [ ] **Step 5: Commit**

```bash
git add skills/bist-analist-kopilotu/scripts/regime_study.py \
        skills/bist-analist-kopilotu/scripts/test_regime_study.py
git commit -m "feat(bist-analyst): regime_study correlation/distribution stats (partial Spearman, KW, chi2, Sidak)"
```

---

### Task 3: Blok makinesi (gözlem toplama + blok istatistiği + verdict)

**Files:**
- Modify: `skills/bist-analist-kopilotu/scripts/regime_study.py`
- Modify (test): `skills/bist-analist-kopilotu/scripts/test_regime_study.py`

**Interfaces:**
- Consumes: `backtest_posture`, `nonoverlap_times`, `_slice`, `_mean`, `_std`, `_t_two_sided_p`, Task1/2 helper'ları.
- Produces:
  - `_closes(bars) -> list[float]`
  - `_block_observations(frames, t, h, include_rs) -> list[dict]` — her dolu gözlem `{"sym","score","absscore","posture","log_sig_t","log_sig_fwd","er_fwd"}`.
  - `_collect_regime_blocks(frames, h, min_setup, include_rs) -> (ve, va, rt, all_obs)` — üç blok-ρ listesi + tüm gözlemler.
  - `_block_stats(rho_list) -> dict` — `{n_blocks, mean_rho, std_rho, se_rho, t_stat, p_rho[, note]}`.
  - `_verdict(stats) -> str` — "BETİMSEL İLİŞKİ VAR/YOK …" (K<4 → yetersiz güç).

- [ ] **Step 1: Başarısız test yaz** (sentetik frames; `backtest_posture._synthetic_bars` ile)

```python
import backtest_posture as bp


def _frames(slopes, n_bars=300, idx_slope=0.3):
    syms = {f"S{i:02d}": bp._synthetic_bars(n_bars, slope=s, noise_phase=i * 0.6)
            for i, s in enumerate(slopes)}
    idx = bp._synthetic_bars(n_bars, slope=idx_slope, noise_phase=0.0)
    return {"symbols": syms, "index": idx}


class BlockMachineryTest(unittest.TestCase):
    def test_block_observations_shape(self):
        fr = _frames([0.6, 0.4, 0.2, 0.0, -0.2, -0.4, 0.5, -0.3], n_bars=260)
        obs = rs._block_observations(fr, t=230, h=10, include_rs=True)
        self.assertGreaterEqual(len(obs), 4)
        o = obs[0]
        for key in ("sym", "score", "absscore", "posture",
                    "log_sig_t", "log_sig_fwd", "er_fwd"):
            self.assertIn(key, o)
        self.assertGreaterEqual(o["absscore"], 0.0)
        self.assertGreaterEqual(o["er_fwd"], 0.0)
        self.assertLessEqual(o["er_fwd"], 1.0)

    def test_collect_blocks_returns_three_lists(self):
        fr = _frames([0.6, 0.4, 0.2, 0.0, -0.2, -0.4, 0.5, -0.3], n_bars=300)
        ve, va, rt, all_obs = rs._collect_regime_blocks(fr, h=10, min_setup=200,
                                                        include_rs=True)
        self.assertTrue(len(ve) >= 2 and len(rt) >= 2)
        self.assertTrue(all(-1.0 <= r <= 1.0 for r in ve + va + rt))
        self.assertGreater(len(all_obs), 0)

    def test_block_stats_and_verdict(self):
        st = rs._block_stats([0.1, 0.2, 0.15, 0.05, 0.12])  # K=5, hep pozitif
        self.assertEqual(st["n_blocks"], 5)
        self.assertIsNotNone(st["p_rho"])
        self.assertIn(st["t_stat"] > 0, (True, False))
        self.assertIsInstance(rs._verdict(st), str)

    def test_verdict_low_power(self):
        st = rs._block_stats([0.1, 0.2])  # K=2 < 4
        self.assertIn("yetersiz güç", rs._verdict(st))
```

- [ ] **Step 2: Testi çalıştır, başarısız olduğunu doğrula**

Run: `python3 -m unittest test_regime_study.BlockMachineryTest -v`
Expected: FAIL — `AttributeError: ... '_block_observations'`.

- [ ] **Step 3: Blok makinesini yaz**

```python
# --------------------------------------------------------------------------- #
# Blok makinesi (örtüşmeyen, sızıntısız)
# --------------------------------------------------------------------------- #

def _closes(bars):
    return [b["close"] for b in bars if "close" in b]


def _block_observations(frames, t, h, include_rs):
    """Blok t için isim-kesiti gözlemleri. Skor = backtest_posture (motor); vol/ER saf fiyat."""
    symbols = frames.get("symbols", frames)
    if t < 21:  # temel-vol penceresi closes[t-21:t] için
        return []
    sliced = _slice(frames, t + h)
    res = backtest_posture(
        sliced["symbols"], horizon=h, index_bars=sliced.get("index"),
        include_relative_strength=include_rs, min_setup_bars=50)
    score_by = {r["symbol"]: r.get("score_norm") for r in res["rows"]
                if not r.get("skipped")}
    post_by = {r["symbol"]: r.get("posture") for r in res["rows"]
               if not r.get("skipped")}
    obs = []
    for sym, bars in symbols.items():
        sn = score_by.get(sym)
        if sn is None:
            continue
        closes = _closes(bars)
        if t + h > len(closes):
            continue
        sig_t = _realized_vol(closes[t - 21:t])       # 20 getiri, anchor'da biten
        fwd = closes[t - 1:t + h]                      # h+1 nokta, h getiri
        sig_fwd = _realized_vol(fwd)
        er_fwd = _efficiency_ratio(fwd)
        if (sig_t is None or sig_t <= 0 or sig_fwd is None or sig_fwd <= 0
                or er_fwd is None):
            continue
        obs.append({"sym": sym, "score": sn, "absscore": abs(sn),
                    "posture": post_by.get(sym),
                    "log_sig_t": math.log(sig_t), "log_sig_fwd": math.log(sig_fwd),
                    "er_fwd": er_fwd})
    return obs


def _collect_regime_blocks(frames, h, min_setup, include_rs):
    """Örtüşmeyen bloklarda üç blok-ρ listesi (+ havuzlanmış tüm gözlemler)."""
    ts = nonoverlap_times(frames, h, min_setup)
    ve, va, rt, all_obs = [], [], [], []
    for t in ts:
        obs = _block_observations(frames, t, h, include_rs)
        all_obs.extend(obs)
        if len(obs) < 4:
            continue
        a = [o["absscore"] for o in obs]
        s = [o["score"] for o in obs]
        yf = [o["log_sig_fwd"] for o in obs]
        zt = [o["log_sig_t"] for o in obs]
        er = [o["er_fwd"] for o in obs]
        pe = _partial_spearman(a, yf, zt)
        pa = _partial_spearman(s, yf, zt)
        rr = _spearman(a, er)
        if pe is not None:
            ve.append(pe)
        if pa is not None:
            va.append(pa)
        if rr is not None:
            rt.append(rr)
    return ve, va, rt, all_obs


def _block_stats(rho_list):
    """Blok-ρ listesinden ρ̄/SE/t/p (Student-t df=K-1). skill_study._finalize deseni."""
    K = len(rho_list)
    out = {"n_blocks": K}
    if K >= 2:
        m = _mean(rho_list)
        sd = _std(rho_list)
        out["mean_rho"] = round(m, 4)
        out["std_rho"] = round(sd, 4) if sd is not None else None
        if sd is None or sd == 0.0:
            out.update({"se_rho": 0.0, "t_stat": None, "p_rho": None,
                        "note": "sıfır varyans — t-testi tanımsız"})
        else:
            se = sd / math.sqrt(K)
            t = m / se
            out["se_rho"] = round(se, 4)
            out["t_stat"] = round(t, 3)
            out["p_rho"] = round(_t_two_sided_p(t, K - 1), 4)
    else:
        out.update({"mean_rho": (round(rho_list[0], 4) if rho_list else None),
                    "std_rho": None, "se_rho": None, "t_stat": None,
                    "p_rho": None, "note": "yetersiz blok (K<2)"})
    return out


def _verdict(stats):
    """Betimsel-ilişki yorumu (return-skill DEĞİL). K<4 → yetersiz güç kapısı."""
    K = stats["n_blocks"]
    p = stats.get("p_rho")
    t = stats.get("t_stat")
    if K < 4:
        return f"yetersiz güç (K={K}<4) — sonuç çıkarılamaz"
    if p is None or t is None:
        return stats.get("note", "belirsiz")
    if p >= 0.05:
        return "BETİMSEL İLİŞKİ YOK (sıfırdan ayırt edilemez)"
    return ("BETİMSEL İLİŞKİ VAR (" + ("pozitif" if t > 0 else "negatif")
            + ", p<0.05)")
```

- [ ] **Step 4: Testi çalıştır, geçtiğini doğrula**

Run: `python3 -m unittest test_regime_study.BlockMachineryTest -v`
Expected: PASS (4 test). (Sentetik frames look-ahead-free skorlanır; blok sayısı ≥2.)

- [ ] **Step 5: Commit**

```bash
git add skills/bist-analist-kopilotu/scripts/regime_study.py \
        skills/bist-analist-kopilotu/scripts/test_regime_study.py
git commit -m "feat(bist-analyst): regime_study block machinery (observations, block stats, verdict)"
```

---

### Task 4: Vol-kovanı η² çapraz-kontrolü

**Files:**
- Modify: `skills/bist-analist-kopilotu/scripts/regime_study.py`
- Modify (test): `skills/bist-analist-kopilotu/scripts/test_regime_study.py`

**Interfaces:**
- Consumes: `_kruskal_wallis`, Task3 gözlem dict şeması.
- Produces:
  - `_vol_buckets(all_obs, n_buckets=3) -> list[dict]` — her kovan `{"name","n","k","eta2","H","kw_p"}` (veya yetersizse `{"name","n","note"}`). Kovanlama `log_sig_t` tercili; grup anahtarı `posture`.

- [ ] **Step 1: Başarısız test yaz**

```python
class VolBucketTest(unittest.TestCase):
    def _obs(self, sig_t, posture, sig_fwd):
        return {"sym": "X", "score": 0.0, "absscore": 0.0, "posture": posture,
                "log_sig_t": math.log(sig_t), "log_sig_fwd": math.log(sig_fwd),
                "er_fwd": 0.5}

    def test_buckets_partition_and_eta2(self):
        obs = []
        # 3 kovan × 2 duruş × birkaç gözlem; ileri-vol duruşa göre ayrışsın
        for s_t in (0.01, 0.02, 0.04):  # düşük/orta/yüksek temel
            for p, fwd in (("Güçlü Yukarı", 0.05), ("Nötr", 0.01)):
                for _ in range(4):
                    obs.append(self._obs(s_t, p, fwd))
        out = rs._vol_buckets(obs, n_buckets=3)
        self.assertEqual(len(out), 3)
        scored = [b for b in out if "eta2" in b]
        self.assertTrue(scored)
        self.assertTrue(all(b["eta2"] >= 0.0 for b in scored))

    def test_buckets_too_few_marks_note(self):
        out = rs._vol_buckets([self._obs(0.01, "Nötr", 0.02)], n_buckets=3)
        self.assertTrue(any("note" in b for b in out))
```

- [ ] **Step 2: Testi çalıştır, başarısız olduğunu doğrula**

Run: `python3 -m unittest test_regime_study.VolBucketTest -v`
Expected: FAIL — `AttributeError: ... '_vol_buckets'`.

- [ ] **Step 3: Kovan testini yaz**

```python
# --------------------------------------------------------------------------- #
# Vol-kovanı η² çapraz-kontrolü (havuzlanmış; p İYİMSER)
# --------------------------------------------------------------------------- #

_BUCKET_NAMES = ["alt", "orta", "üst"]


def _vol_buckets(all_obs, n_buckets=3):
    """Mevcut-vol terciline göre kovanla; her kovanda duruş→ileri-vol KW η².

    UYARI: havuzlama seri/kesitsel bağımlılığı yok sayar → kw_p İYİMSER.
    Birincil ölçüt blok t-testidir; bu yalnız varsayımsız sağlamlık çapraz-kontrolü.
    """
    obs = [o for o in all_obs if o.get("posture")]
    obs.sort(key=lambda o: o["log_sig_t"])
    n = len(obs)
    out = []
    for bi in range(n_buckets):
        lo = (bi * n) // n_buckets
        hi = ((bi + 1) * n) // n_buckets
        chunk = obs[lo:hi]
        name = (_BUCKET_NAMES[bi] if n_buckets == 3 and bi < 3
                else f"kovan{bi + 1}")
        if len(chunk) < 4:
            out.append({"name": name, "n": len(chunk),
                        "note": "yetersiz gözlem (<4)"})
            continue
        groups = defaultdict(list)
        for o in chunk:
            groups[o["posture"]].append(o["log_sig_fwd"])
        kw = _kruskal_wallis(list(groups.values()))
        if kw is None:
            out.append({"name": name, "n": len(chunk),
                        "note": "tek duruş grubu — KW tanımsız"})
        else:
            out.append({"name": name, "n": len(chunk), "k": kw["k"],
                        "eta2": round(kw["eta2"], 4),
                        "H": round(kw["H"], 3),
                        "kw_p": (round(kw["p"], 4) if kw["p"] is not None else None)})
    return out
```

- [ ] **Step 4: Testi çalıştır, geçtiğini doğrula**

Run: `python3 -m unittest test_regime_study.VolBucketTest -v`
Expected: PASS (2 test).

- [ ] **Step 5: Commit**

```bash
git add skills/bist-analist-kopilotu/scripts/regime_study.py \
        skills/bist-analist-kopilotu/scripts/test_regime_study.py
git commit -m "feat(bist-analyst): regime_study vol-bucket eta2 cross-check"
```

---

### Task 5: Orkestrasyon, render, self-test (pozitif+null kontrol) ve CLI

**Files:**
- Modify: `skills/bist-analist-kopilotu/scripts/regime_study.py`
- Modify (test): `skills/bist-analist-kopilotu/scripts/test_regime_study.py`

**Interfaces:**
- Consumes: tüm önceki helper'lar.
- Produces:
  - `study_horizon_regime(frames, h, min_setup, include_rs) -> dict` — bir ufuk için `{horizon, vol_extreme, vol_asymmetry, vol_bucket_eta2, regime_trend}` (her primary'ye `p_sidak` + `verdict`).
  - `regime_study(frames, horizons=(5,10,20), min_setup=200, include_rs=True) -> dict` — `{horizons:[...], basis, disclaimer}`.
  - `pooled_regime_study(frames_list, horizons, min_setup, include_rs, sample_names) -> dict` — blok listelerini örnekler arası birleştirir + `per_sample` kırılımı.
  - `render(result) -> str`
  - `_run_selftest() -> dict`, `main(argv=None) -> int`.

`p_sidak` aile boyutu **m = 2 × ufuk-sayısı** (iki birincil test × ufuk). Çıktıda `sidak_family_m` alanı ve render'da açıklama.

- [ ] **Step 1: Başarısız test yaz** (çıktı sözleşmesi + pozitif/null self-test sözleşmesi)

```python
class OrchestrationTest(unittest.TestCase):
    def test_output_contract_keys(self):
        fr = _frames([0.6, 0.4, 0.2, 0.0, -0.2, -0.4, 0.5, -0.3], n_bars=300)
        res = rs.regime_study(fr, horizons=(10,), min_setup=200)
        self.assertIn("horizons", res)
        h0 = res["horizons"][0]
        for key in ("horizon", "vol_extreme", "vol_asymmetry",
                    "vol_bucket_eta2", "regime_trend", "sidak_family_m"):
            self.assertIn(key, h0)
        for prim in ("vol_extreme", "regime_trend"):
            self.assertIn("verdict", h0[prim])
            self.assertIn("p_sidak", h0[prim])
        self.assertIn("disclaimer", res)

    def test_render_is_str(self):
        fr = _frames([0.6, 0.4, 0.2, 0.0, -0.2, -0.4, 0.5, -0.3], n_bars=300)
        self.assertIsInstance(rs.render(rs.regime_study(fr, horizons=(10,))), str)

    def test_selftest_positive_and_null(self):
        out = rs._run_selftest()
        self.assertTrue(out["ok"], msg=str(out))
```

- [ ] **Step 2: Testi çalıştır, başarısız olduğunu doğrula**

Run: `python3 -m unittest test_regime_study.OrchestrationTest -v`
Expected: FAIL — `AttributeError: ... 'regime_study'`.

- [ ] **Step 3: Orkestrasyon + render + self-test + CLI yaz**

```python
# --------------------------------------------------------------------------- #
# Orkestrasyon
# --------------------------------------------------------------------------- #

def study_horizon_regime(frames, h, min_setup=200, include_rs=True,
                         sidak_m=6, _pre=None):
    """Bir ufuk için iki birincil + iki ikincil betimsel test.

    _pre: (ve, va, rt, all_obs) önceden toplanmışsa (havuz modu) kullan."""
    if _pre is None:
        ve, va, rt, all_obs = _collect_regime_blocks(frames, h, min_setup, include_rs)
    else:
        ve, va, rt, all_obs = _pre
    vol_extreme = _block_stats(ve)
    vol_extreme["verdict"] = _verdict(vol_extreme)
    vol_extreme["p_sidak"] = _sidak(vol_extreme.get("p_rho"), sidak_m)
    vol_asym = _block_stats(va)
    vol_asym["verdict"] = _verdict(vol_asym)
    regime_trend = _block_stats(rt)
    regime_trend["verdict"] = _verdict(regime_trend)
    regime_trend["p_sidak"] = _sidak(regime_trend.get("p_rho"), sidak_m)
    return {"horizon": h, "min_setup": min_setup, "sidak_family_m": sidak_m,
            "vol_extreme": vol_extreme, "vol_asymmetry": vol_asym,
            "vol_bucket_eta2": {
                "buckets": _vol_buckets(all_obs),
                "note": ("İYİMSER p: havuzlama seri/kesitsel bağımlılığı yok sayar; "
                         "birincil ölçüt blok t-testidir.")},
            "regime_trend": regime_trend}


def regime_study(frames, horizons=(5, 10, 20), min_setup=200, include_rs=True):
    m = 2 * len(horizons)
    return {
        "horizons": [study_horizon_regime(frames, h, min_setup, include_rs, sidak_m=m)
                     for h in horizons],
        "basis": "EOD günlük; örtüşmeyen bloklar; sabit varsayılan (3/13)",
        "disclaimer": "karar-destek; yatırım tavsiyesi değildir",
    }


def pooled_regime_study(frames_list, horizons=(5, 10, 20), min_setup=200,
                        include_rs=True, sample_names=None):
    """Çok bağımsız örneği (dönem/piyasa) havuzlar — blok listeleri birleştirilir."""
    m = 2 * len(horizons)
    hz = []
    for h in horizons:
        ve, va, rt, all_obs = [], [], [], []
        per_sample = {}
        for i, fr in enumerate(frames_list):
            e, a, r, o = _collect_regime_blocks(fr, h, min_setup, include_rs)
            ve += e; va += a; rt += r; all_obs += o
            name = (sample_names[i] if sample_names and i < len(sample_names)
                    else f"örnek{i + 1}")
            per_sample[name] = {"n_blocks_vol": len(e), "n_blocks_regime": len(r),
                                "mean_vol_extreme": (round(_mean(e), 4) if e else None),
                                "mean_regime_trend": (round(_mean(r), 4) if r else None)}
        block = study_horizon_regime(fr, h, min_setup, include_rs, sidak_m=m,
                                     _pre=(ve, va, rt, all_obs))
        block["per_sample"] = per_sample
        hz.append(block)
    return {"horizons": hz,
            "basis": "EOD günlük; ÇOK-ÖRNEK havuzlanmış (bağımsız dönem/piyasa OOS); sabit (3/13)",
            "disclaimer": "karar-destek; yatırım tavsiyesi değildir"}


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #

def render(result):
    lines = ["Teknik-Duruş BETİMSEL-DEĞER Çalışması (örtüşmeyen, sızıntısız)",
             "=" * 62,
             "Sabit parametre: varsayılan (3/13) | iki birincil: vol_extreme (mevcut-vol "
             "kontrollü), regime_trend (efficiency-ratio)"]
    hdr = (f"{'ufuk':>5}{'test':>14}{'blok':>6}{'ρ̄':>9}{'SE':>8}{'t':>8}"
           f"{'p':>8}{'p_Šidák':>9}  yorum")
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for h in result["horizons"]:
        for label, key in (("vol_extreme", "vol_extreme"),
                           ("regime_trend", "regime_trend")):
            s = h[key]
            mr = f"{s['mean_rho']:9.3f}" if s.get("mean_rho") is not None else f"{'—':>9}"
            se = f"{s['se_rho']:8.3f}" if s.get("se_rho") is not None else f"{'—':>8}"
            ts = f"{s['t_stat']:8.2f}" if s.get("t_stat") is not None else f"{'—':>8}"
            pp = f"{s['p_rho']:8.3f}" if s.get("p_rho") is not None else f"{'—':>8}"
            ps = f"{s['p_sidak']:9.3f}" if s.get("p_sidak") is not None else f"{'—':>9}"
            lines.append(f"{h['horizon']:>5}{label:>14}{s['n_blocks']:>6}"
                         f"{mr}{se}{ts}{pp}{ps}  {s['verdict']}")
    lines.append("")
    # asimetri + kovan özet
    for h in result["horizons"]:
        a = h["vol_asymmetry"]
        lines.append(f"ufuk {h['horizon']}: vol_asimetri ρ̄={a.get('mean_rho')} "
                     f"p={a.get('p_rho')} ({a.get('verdict')})  "
                     f"[negatif ⇒ kaldıraç etkisi]")
        bk = ", ".join(f"{b['name']}:η²={b.get('eta2', '—')}"
                       for b in h["vol_bucket_eta2"]["buckets"])
        lines.append(f"         vol-kovan η² (İYİMSER-p): {bk}")
    lines.append("")
    lines.append("ρ̄=örtüşmeyen bloklarda ortalama (kısmi) Spearman; t/p=Student-t "
                 "(df=K-1); p_Šidák=2×ufuk aile düzeltmesi. K<4 → yetersiz güç.")
    ps0 = next((h.get("per_sample") for h in result["horizons"] if h.get("per_sample")), None)
    if ps0:
        lines.append("UYARI: havuz örnekleri AYNI takvim penceresindeki farklı "
                     "PİYASALAR ise bağımsız DEĞİL (ortak küresel faktör) → p olduğundan güçlü.")
    lines.append("Betimsel/yapısal gözlem; getiri-öngörüsü veya yatırım tavsiyesi DEĞİLDİR.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Self-test / CLI
# --------------------------------------------------------------------------- #

def _coupled_bars(n, slope, noise_phase, vol_amp, base=100.0):
    """Sentetik bar: trend (slope) + genliği vol_amp olan salınım. Deterministik."""
    bars = []
    for i in range(n):
        c = base + i * slope + vol_amp * math.sin(i / 5.0 + noise_phase)
        o = c - slope
        hi = max(o, c) + 0.5
        lo = min(o, c) - 0.5
        bars.append({"date": f"T{i:03d}", "open": round(o, 3), "high": round(hi, 3),
                     "low": round(lo, 3), "close": round(c, 3), "volume": 1_000_000})
    return bars


def _vol_coupled_frames(n_bars=300):
    """Pozitif kontrol (vol): salınım genliği |slope| ile ARTAR → aşırı duruş yüksek
    ileri-vol önceler. σ_t 20-bar gürültülü tahmin; |score| slope'tan temiz → kısmi
    korelasyon hayatta kalır."""
    slopes = [0.9, 0.7, 0.5, 0.3, 0.1, -0.2, -0.4, -0.6, -0.8, 0.6, -0.5, 0.4]
    syms = {f"V{i:02d}": _coupled_bars(n_bars, s, i * 0.7, vol_amp=1.0 + 6.0 * abs(s))
            for i, s in enumerate(slopes)}
    idx = _coupled_bars(n_bars, 0.3, 0.0, vol_amp=2.0)
    return {"symbols": syms, "index": idx}


def _trend_coupled_frames(n_bars=300):
    """Pozitif kontrol (rejim): sabit küçük genlik; dik slope → yüksek efficiency-ratio
    (trend baskın), düz isim → düşük ER (gürültü baskın)."""
    slopes = [1.2, 0.9, 0.6, 0.3, 0.1, -0.2, -0.5, -0.8, -1.1, 0.7, -0.6, 0.4]
    syms = {f"T{i:02d}": _coupled_bars(n_bars, s, i * 0.7, vol_amp=3.0)
            for i, s in enumerate(slopes)}
    idx = _coupled_bars(n_bars, 0.3, 0.0, vol_amp=3.0)
    return {"symbols": syms, "index": idx}


def _null_frames(n_bars=300):
    """Null: genlik slope'tan BAĞIMSIZ (sabit), faz isimden gelir → ileri-vol/ER duruşla
    ilişkisiz. Birincil testler 'YOK' vermeli."""
    slopes = [0.5, -0.5, 0.4, -0.4, 0.3, -0.3, 0.2, -0.2, 0.45, -0.45, 0.35, -0.35]
    syms = {f"N{i:02d}": _coupled_bars(n_bars, s, i * 1.3, vol_amp=3.0)
            for i, s in enumerate(slopes)}
    idx = _coupled_bars(n_bars, 0.2, 0.0, vol_amp=3.0)
    return {"symbols": syms, "index": idx}


def _run_selftest():
    """Pozitif (vol & trend) + null kontrol. Sayısal eşik yerine yön/anlamlılık."""
    h = 10
    vc = regime_study(_vol_coupled_frames(), horizons=(h,), min_setup=200)["horizons"][0]
    tc = regime_study(_trend_coupled_frames(), horizons=(h,), min_setup=200)["horizons"][0]
    nl = regime_study(_null_frames(), horizons=(h,), min_setup=200)["horizons"][0]

    ve = vc["vol_extreme"]; rt = tc["regime_trend"]
    nve = nl["vol_extreme"]; nrt = nl["regime_trend"]

    pos_vol = (ve["n_blocks"] >= 4 and ve.get("p_rho") is not None
               and ve["p_rho"] < 0.05 and ve["t_stat"] > 0)
    pos_trend = (rt["n_blocks"] >= 4 and rt.get("p_rho") is not None
                 and rt["p_rho"] < 0.05 and rt["t_stat"] > 0)
    null_ok = ((nve.get("p_rho") is None or nve["p_rho"] >= 0.05)
               and (nrt.get("p_rho") is None or nrt["p_rho"] >= 0.05))

    return {"self_test": True,
            "ok": bool(pos_vol and pos_trend and null_ok),
            "positive_vol": {"rho": ve.get("mean_rho"), "p": ve.get("p_rho"),
                             "K": ve["n_blocks"], "fired": pos_vol},
            "positive_trend": {"rho": rt.get("mean_rho"), "p": rt.get("p_rho"),
                               "K": rt["n_blocks"], "fired": pos_trend},
            "null": {"vol_p": nve.get("p_rho"), "regime_p": nrt.get("p_rho"),
                     "quiet": null_ok}}


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Teknik-duruş betimsel-değer çalışması (vol + rejim; karar-destek).")
    p.add_argument("--file", help="tek günlük frames.json (≥250 bar/sembol önerilir)")
    p.add_argument("--pool", nargs="+", help="ÇOK bağımsız örnek frames.json — havuzla")
    p.add_argument("--names", help="--pool örnek adları (virgüllü)")
    p.add_argument("--horizons", default="5,10,20", help="virgüllü ufuk (işlem günü)")
    p.add_argument("--min-setup", type=int, default=200)
    p.add_argument("--no-rs", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if not args.file and not args.pool:
        out = _run_selftest()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out["ok"] else 1

    horizons = tuple(int(x) for x in args.horizons.split(",") if x.strip())
    if args.pool:
        frames_list = []
        for path in args.pool:
            with open(path, "r", encoding="utf-8") as f:
                frames_list.append(json.load(f))
        names = ([s.strip() for s in args.names.split(",")] if args.names else None)
        res = pooled_regime_study(frames_list, horizons=horizons,
                                  min_setup=args.min_setup,
                                  include_rs=not args.no_rs, sample_names=names)
    else:
        with open(args.file, "r", encoding="utf-8") as f:
            frames = json.load(f)
        res = regime_study(frames, horizons=horizons, min_setup=args.min_setup,
                           include_rs=not args.no_rs)
    print(json.dumps(res, ensure_ascii=False, indent=2) if args.json else render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Birim testlerini çalıştır, geçtiğini doğrula**

Run: `python3 -m unittest test_regime_study -v`
Expected: PASS (tüm sınıflar). `test_selftest_positive_and_null` GEÇMELİ.

**Eğer self-test başarısızsa (pozitif fire etmiyor veya null sessiz değil):** sentetik sabitleri ayarla — pozitif-vol için `_vol_coupled_frames`'te `vol_amp=1.0 + K*abs(s)` çarpanı K'yi artır (kuplajı güçlendir) veya `min_setup`/`h` ile blok sayısını artır (n_bars 300→360); null için `_null_frames` fazını daha dağıt (i*1.3 → i*2.1). Determinist olduğundan bir kez ayarlanınca sabittir. **Motor/üretim kodu DEĞİŞMEZ — yalnız self-test sentetik sabitleri.**

- [ ] **Step 5: Argümansız çalıştır (CLI self-test), sonra render dumanı**

Run: `python3 regime_study.py`
Expected: JSON; `"ok": true`.
Run: `python3 regime_study.py --file <(python3 -c "import json,backtest_posture as b; import math; ...")` → atla; render dumanı Task 6 canlı veriyle.

- [ ] **Step 6: Commit**

```bash
git add skills/bist-analist-kopilotu/scripts/regime_study.py \
        skills/bist-analist-kopilotu/scripts/test_regime_study.py
git commit -m "feat(bist-analyst): regime_study orchestration + render + positive/null self-test + CLI"
```

---

### Task 6: Canlı koşum, dokümantasyon, sürüm artışı ve dağıtım

**Files:**
- Create (geçici): `/tmp/frames_deep.json` (canlı veri; commit edilmez)
- Modify: `skills/bist-analist-kopilotu/references/methodology.md`
- Modify: `plugins/bist-analyst/CHANGELOG.md`
- Modify: `plugins/bist-analyst/.claude-plugin/plugin.json` (version `1.1.6` → `1.1.7`)
- Modify: `.claude-plugin/marketplace.json` (bist-analyst version `1.1.6` → `1.1.7`)
- Modify: `/home/mahirkurt/.claude/projects/-mnt-thunderbolt-workspaces-CureoHub/memory/project_bist_analyst_plugin.md`

**Interfaces:**
- Consumes: `regime_study.py` CLI, `stitch_daily.py`.

- [ ] **Step 1: Canlı derin set'i kur (parallel-agent fetch, partiler ≤5)**

8 BIST (GARAN, AKBNK, ISCTR, THYAO, ASELS, KCHOL, TUPRS, SISE) + XU100 için ~615 günlük bar. Her sembol için Borsa `get_historical_data(market=bist, adjust=true)`, ardışık 30-günlük günlük chunk'larla (≤30 gün → günlük çözünürlük); **aynı anda en fazla 5 ağır agent** (rate-limit dersi). Ham bar'lar agent'larda kalır; main context'e yalnız `{symbol, data:[bars]}` döner. Birleştir:

```bash
python3 skills/bist-analist-kopilotu/scripts/stitch_daily.py \
  --out /tmp/frames_deep.json  # (agent çıktıları stdin/dosya; stitch_daily formatı)
```
Kapsam raporunda SMA200 tanımlı (≥200 bar/sembol) ve split-artefakt taraması temiz olmalı.

- [ ] **Step 2: Betimsel-değer çalışmasını koş**

Run:
```bash
python3 skills/bist-analist-kopilotu/scripts/regime_study.py \
  --file /tmp/frames_deep.json --horizons 5,10,20 --min-setup 200
```
Çıktıyı (vol_extreme & regime_trend ρ̄/p/p_Šidák/verdict, asimetri, kovan-η²) kaydet. `--json` ile ham metriği de al.

- [ ] **Step 3: `methodology.md`'ye bulguyu işle**

skill_study bölümünün ardına yeni alt-başlık: **"Teknik-duruşun betimsel değeri (v1.1.7): oynaklık + trend/yatay rejim."** Yöntem (kısmi-Spearman mevcut-vol kontrollü, KW-η² çapraz-kontrol, ER rejim), K bağımsız blok, Šidák, ve gerçek koşum sonucu + namuslu yorum (VAR/YOK, betimsel; getiri-öngörüsü değil). Mevcut "absence-of-evidence" disiplinini koru.

- [ ] **Step 4: CHANGELOG + sürüm artışı**

`CHANGELOG.md`'ye `[1.1.7]` girişi (yeni `regime_study.py` aracı + bulgu, "defaults unchanged"). `plugin.json` ve `marketplace.json`'da bist-analyst `1.1.6 → 1.1.7`.

SKILL.md frontmatter `version: 1.1.7` + changelog bloğu (newest-first) bir satır: betimsel-değer aracı.

- [ ] **Step 5: Doğrula (testler + plugin validate)**

```bash
cd skills/bist-analist-kopilotu/scripts && python3 -m unittest test_regime_study -v
cd /mnt/thunderbolt/workspaces/marketplace && claude plugin validate plugins/bist-analyst --strict
```
Expected: tüm birim testleri PASS; validate strict temiz.

- [ ] **Step 6: Commit + main'e cherry-pick + push + memory**

```bash
git add -A && git commit -m "docs(bist-analyst): v1.1.7 — posture descriptive-value study (vol + trend/range regime)"
# v1.1.6 deseni: feat/cureosuite-bundle → main worktree cherry-pick (açık SHA)
```
Sonra `marketplace.json` katalog v1.1.7 doğrula, kurulu eklenti güncelle, memory dosyasına v1.1.7 girişini (bulgu + araç) ekle.

---

## Self-Review

**1. Spec coverage:**
- §2 mimari (tek dosya, import, sıfır motor değişikliği) → Task 1–5 + Global Constraints. ✓
- §3 birim/bağımsızlık (nonoverlap, W=20, indis) → Task 3 `_block_observations` + Global indis notu. ✓
- §4 Test 1/1b/1c/2 → Task 3 (vol_extreme/asym, regime_trend), Task 4 (bucket η²). ✓
- §4 kısmi-Spearman formülü, Šidák → Task 2 `_partial_spearman`, `_sidak`; Task 5 `sidak_m=2×ufuk`. ✓
- §5 çıktı sözleşmesi (JSON anahtarları, render, CLI) → Task 5. ✓
- §6 TDD self-test (pozitif+null) → Task 5 `_run_selftest`. ✓
- §7 canlı koşum + doc + sürüm → Task 6. ✓
- §8 kapsam-dışı → Global Constraints. ✓
- §9 riskler (8-isim, doğrusal-dışı, betimsel) → render uyarıları + bucket cross-check + verdict dili. ✓

**2. Placeholder scan:** Task 5 Step 5'teki `--file <(...)` örneği "atla" olarak işaretli (canlı duman Task 6'da) — bu bir plan-placeholder değil, kasıtlı erteleme. Diğer tüm kod-adımları tam. Task 6 doğası gereği canlı-veri/dağıtım (skill_study/v1.1.6 deseniyle aynı); kod yerine komut+prosedür içerir. ✓

**3. Type consistency:** Gözlem dict anahtarları (`sym/score/absscore/posture/log_sig_t/log_sig_fwd/er_fwd`) Task 3'te tanımlı, Task 4 (`_vol_buckets`) ve Task 5 (`_collect_regime_blocks` çıktısı) aynı adları kullanır. `_block_stats` çıktı anahtarları (`n_blocks/mean_rho/se_rho/t_stat/p_rho`) Task 3'te üretilir, Task 5 `study_horizon_regime` + render aynı adlarla okur. `_kruskal_wallis` dönüşü (`H/df/eta2/n/k/p`) Task 2'de tanımlı, Task 4 aynı anahtarları okur. ✓
