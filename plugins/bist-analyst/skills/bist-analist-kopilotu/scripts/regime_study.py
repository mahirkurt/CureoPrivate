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


# --------------------------------------------------------------------------- #
# Orkestrasyon
# --------------------------------------------------------------------------- #

def study_horizon_regime(frames, h, min_setup=200, include_rs=True,
                         sidak_m=6, _pre=None):
    """Bir ufuk için iki birincil + iki ikincil betimsel test.

    _pre: (ve, va, rt, all_obs) önceden toplanmışsa (havuz modu) kullan.
    """
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
    """Birden fazla ufuk için vol_extreme + regime_trend betimsel çalışması.

    Döner: {horizons:[...], basis, disclaimer}
    Šidák aile boyutu m = 2 × ufuk-sayısı (iki birincil test × ufuk).
    """
    m = 2 * len(horizons)
    return {
        "horizons": [study_horizon_regime(frames, h, min_setup, include_rs, sidak_m=m)
                     for h in horizons],
        "basis": "EOD günlük; örtüşmeyen bloklar; sabit varsayılan (3/13)",
        "disclaimer": "karar-destek; yatırım tavsiyesi değildir",
    }


def pooled_regime_study(frames_list, horizons=(5, 10, 20), min_setup=200,
                        include_rs=True, sample_names=None):
    """Çok bağımsız örneği (dönem/piyasa) havuzlar — blok listeleri birleştirilir.

    Her ufuk için tüm örneklerin blokları tek listede toplanır, ardından
    study_horizon_regime çağrılır. per_sample kırılımı da döner.
    """
    m = 2 * len(horizons)
    hz = []
    last_fr = frames_list[-1] if frames_list else {}
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
        block = study_horizon_regime(last_fr, h, min_setup, include_rs, sidak_m=m,
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
    """Sonucu okunabilir metin tablosuna dönüştürür."""
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


def _vol_coupled_frames(n_bars=600):
    """Pozitif kontrol (vol): periyodik vol-patlama modeli.

    Her period=30 barda 10-barlık yüksek-vol patlaması (burst) gelir; patlama genliği
    |slope| ile orantılıdır. Dolayısıyla yüksek-|slope| semboller hem yüksek puan
    (backtest_posture) hem de mevcut-vol kontrollü yüksek ileri-vol üretir.
    sig_t=[t-21:t] patlama dışında; sig_fwd=[t-1:t+h] patlama içinde → pozitif kısmi-ρ.
    """
    slopes = [0.9, 0.7, 0.5, 0.3, 0.1, -0.2, -0.4, -0.6, -0.8, 0.6, -0.5, 0.4]
    period, burst_h, first_switch, base_amp = 30, 10, 200, 0.5
    syms = {}
    for i, s in enumerate(slopes):
        factor = 1.0 + 10.0 * abs(s)   # düşük-slope → 1.1×, yüksek-slope → 10.0× burst
        bars = []
        for j in range(n_bars):
            offset = j - first_switch
            in_burst = (offset >= 0 and (offset % period) < burst_h)
            amp = base_amp * factor if in_burst else base_amp
            c = 100.0 + j * s + amp * math.sin(j / 5.0 + i * 0.7)
            o = c - s
            bars.append({"date": f"T{j:03d}", "open": round(o, 3),
                         "high": round(max(o, c) + 0.5, 3),
                         "low": round(min(o, c) - 0.5, 3),
                         "close": round(c, 3), "volume": 1_000_000})
        syms[f"V{i:02d}"] = bars
    idx_bars = []
    for j in range(n_bars):
        c = 100.0 + j * 0.3 + 2.0 * math.sin(j / 5.0)
        idx_bars.append({"date": f"T{j:03d}", "open": round(c - 0.3, 3),
                         "high": round(c + 0.5, 3), "low": round(c - 0.5, 3),
                         "close": round(c, 3), "volume": 1_000_000})
    return {"symbols": syms, "index": idx_bars}


def _trend_coupled_frames(n_bars=300):
    """Pozitif kontrol (rejim): 24 sembol, geniş slope tayfı, vol_amp=2.0.

    Yüksek |slope| → backtest_posture puanı yüksek VE efficiency-ratio yüksek
    (trend baskın). Faz aralığı 0.1 ile ayrıştırılır; sıkı küçük genlik sayesinde
    slope-ER korelasyonu gürültüyü aşar (K≥10, p<0.05, t>0).
    """
    slopes = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.05, -0.05,
              -0.2, -0.4, -0.6, -0.8, -1.0, -1.2,
              0.9, 0.7, 0.5, 0.3, 0.1, -0.1, -0.3, -0.5, -0.7, -0.9]
    vol_amp, phase_step = 2.0, 0.1
    syms = {f"T{i:02d}": _coupled_bars(n_bars, s, i * phase_step, vol_amp=vol_amp)
            for i, s in enumerate(slopes)}
    idx = _coupled_bars(n_bars, 0.3, 0.0, vol_amp=vol_amp)
    return {"symbols": syms, "index": idx}


def _null_frames(n_bars=300):
    """Null: genlik slope'tan BAĞIMSIZ (sabit), faz ayrıktır.

    Simetrik slope çiftleri (±0.5, ±0.4, …) ile puan dağılımı dengeli;
    sabit vol_amp=3.0 ve phase_step=0.7 → ileri-vol/ER ile ilişki YOK.
    """
    slopes = [0.5, -0.5, 0.4, -0.4, 0.3, -0.3, 0.2, -0.2, 0.45, -0.45, 0.35, -0.35]
    syms = {f"N{i:02d}": _coupled_bars(n_bars, s, i * 0.7, vol_amp=3.0)
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
    """CLI giriş noktası. Argümansız çalıştırılırsa self-test yapar."""
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
