#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_study.py — Teknik-duruş motorunun MUTLAK kesitsel öngörü gücü çalışması.

NEDEN VAR
---------
`walkforward_calibrate` PARAMETRE sorusunu yanıtlar (3/13 yenildi mi?) ve cevabı
"hayır"dı. Ama o taramada tüm Spearman ρ'lar NEGATİF çıktı — bu PARAMETRE değil,
motorun **mutlak skilline** dair ayrı bir sorudur: duruş skoru, ileri getiriyi
gerçekten (pozitif) sıralıyor mu, yoksa sinyal sıfır/ters mi? Bu betik o soruyu
istatistiksel güçle yanıtlamak için tasarlandı; üç eksiği kapatır:

  1) ÖRTÜŞMEYEN pencereler — `walkforward_calibrate --windows` örtüşen (otokorelasyonlu)
     pencereler üretir; etkin N çöker. Burada anlık-zamanlar ufuk kadar ADIMLANIR
     (t_{k+1} = t_k + horizon), böylece ardışık blokların ileri-getiri pencereleri
     ÇAKIŞMAZ → bloklar bağımsızdır.
  2) SMA200 KAPSAMI — ≥200 barlık setup'ta SMA200 tanımlıdır; motor artık
     kapsam-sınırlı değildir (aylık/kısa-günlük testlerin aksine). min_setup≥200 önerilir.
  3) ANLAMLILIK — K bağımsız blok üzerinden ρ ortalamasına t-testi (H0: ortalama=0)
     ve toplu isabet oranına binom testi (H0: 0.5). Hem iyimser (toplu) hem korumalı
     (blok-düzeyi) ölçüt raporlanır.

SIZINTISIZLIK: her blok `backtest_posture`'a delege edilir (duruş = bars[:-horizon],
getiri = kurulum→sonuç). Skorlama mantığı ÇOĞALTILMAZ.

PARAMETRE: bu bir SKILL testidir, tuning değil → sabit varsayılan (3/13).
Karar-destek; yatırım tavsiyesi DEĞİLDİR. Bağımlılık: yalnız stdlib + backtest_posture.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

try:
    from backtest_posture import backtest_posture
except ImportError:  # pragma: no cover
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from backtest_posture import backtest_posture


# --------------------------------------------------------------------------- #
# İstatistik yardımcıları (stdlib)
# --------------------------------------------------------------------------- #

def _phi(z):
    """Standart normal CDF (math.erf ile)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _two_sided_p_from_z(z):
    return 2.0 * (1.0 - _phi(abs(z)))


def _betacf(a, b, x, itmax=200, eps=3e-12):
    """Lentz sürekli-kesir (Numerical Recipes betacf) — düzenlenmiş eksik beta için."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    """Düzenlenmiş eksik beta I_x(a,b) (stdlib: lgamma + sürekli kesir)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _t_two_sided_p(t, df):
    """Student-t iki-yanlı p: P(|T|>|t|) = I_{df/(df+t^2)}(df/2, 1/2).

    Küçük K (df) rejiminde normal-yaklaşımı AŞMAZ — t-dağılımının kalın
    kuyrukları doğru hesaba katılır (skill_study'nin yaşadığı az-blok rejimi).
    """
    if df <= 0 or t is None:
        return None
    x = df / (df + t * t)
    return _betai(df / 2.0, 0.5, x)


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _std(xs):
    """Örneklem std (ddof=1) — bağımsız blok ortalamasının SE'si için."""
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def _binom_two_sided_p(k, n, p0=0.5):
    """İki-yanlı binom p (normal yaklaşım; n büyük olduğunda yeterli)."""
    if n <= 0:
        return None
    mean = n * p0
    sd = math.sqrt(n * p0 * (1 - p0))
    if sd == 0:
        return 1.0
    z = (k - mean) / sd
    return _two_sided_p_from_z(z)


# --------------------------------------------------------------------------- #
# Örtüşmeyen blok zamanları
# --------------------------------------------------------------------------- #

def nonoverlap_times(frames, horizon, min_setup):
    """Örtüşmeyen anlık-zaman indeksleri: t = min_setup, min_setup+h, ...

    Her t için: duruş = bars[:t] (sızıntısız), getiri = bars[t] → bars[t+horizon].
    `backtest_posture`'a frames'in [:t+horizon] dilimi horizon ile verilince tam
    olarak bu blok elde edilir (o, bars[:-horizon] = bars[:t] ile duruşu hesaplar).
    Ardışık t'ler horizon kadar adımlandığından ileri-getiri pencereleri çakışmaz.
    """
    symbols = frames.get("symbols", frames)
    full = min((len(b) for b in symbols.values()), default=0)
    ts = []
    t = min_setup
    while t + horizon <= full:
        ts.append(t)
        t += horizon  # ÖRTÜŞMEME: bir sonraki blok bu bloğun sonuç-penceresinden sonra başlar
    return ts


def _slice(frames, end_idx):
    symbols = frames.get("symbols", frames)
    out = {"symbols": {s: b[:end_idx] for s, b in symbols.items()}}
    idx = frames.get("index")
    if idx is not None:
        out["index"] = idx[:end_idx]
    return out


# --------------------------------------------------------------------------- #
# Tek ufuk için skill ölçümü
# --------------------------------------------------------------------------- #

def study_horizon(frames, horizon, min_setup=200, include_relative_strength=True,
                  bt_min_setup=50):
    """Bir ufuk için örtüşmeyen bloklarda skill metriklerini toplar + test eder."""
    ts = nonoverlap_times(frames, horizon, min_setup)
    block_rho = []
    block_ic = []
    block_hit = []            # blok-içi mutlak isabet oranı (cross-sectional)
    pooled_hits = 0           # tüm bloklarda (sembol,blok) pozitif-hizalama sayısı
    pooled_total = 0
    for t in ts:
        sliced = _slice(frames, t + horizon)
        res = backtest_posture(
            sliced["symbols"], horizon=horizon, index_bars=sliced.get("index"),
            include_relative_strength=include_relative_strength,
            min_setup_bars=bt_min_setup)
        m = res["metrics"]
        if m["spearman_rho"] is not None:
            block_rho.append(m["spearman_rho"])
        if m["information_coeff"] is not None:
            block_ic.append(m["information_coeff"])
        if m["hit_rate_absolute"] is not None:
            block_hit.append(m["hit_rate_absolute"])
        # Toplu isabeti satırlardan TAM say (round(hit*n) yuvarlama kaybı yok).
        for r in res["rows"]:
            if not r.get("skipped") and r.get("score_norm") is not None \
                    and r.get("realized_ret_pct") is not None:
                pooled_total += 1
                if (r["score_norm"] > 0) == (r["realized_ret_pct"] > 0):
                    pooled_hits += 1

    K = len(block_rho)
    out = {"horizon": horizon, "n_blocks": K, "min_setup": min_setup,
           "include_relative_strength": include_relative_strength}

    # --- Blok-düzeyi ρ ortalaması t-testi (H0: ortalama=0), Student-t df=K-1 ---
    if K >= 2:
        m_rho = _mean(block_rho)
        sd = _std(block_rho)
        out["mean_rho"] = round(m_rho, 4)
        out["std_rho"] = round(sd, 4) if sd is not None else None
        if sd is None or sd == 0.0:
            # Dejenere: tüm bloklar özdeş → varyans sıfır, t-testi tanımsız.
            out.update({"se_rho": 0.0, "t_stat": None, "p_rho": None,
                        "note": "sıfır varyans — t-testi tanımsız (tüm bloklar özdeş)"})
        else:
            se = sd / math.sqrt(K)
            t_stat = m_rho / se
            out["se_rho"] = round(se, 4)
            out["t_stat"] = round(t_stat, 3)
            out["p_rho"] = round(_t_two_sided_p(t_stat, K - 1), 4)  # Student-t, NOT normal
    else:
        out.update({"mean_rho": (round(block_rho[0], 4) if block_rho else None),
                    "std_rho": None, "se_rho": None, "t_stat": None, "p_rho": None,
                    "note": "yetersiz bağımsız blok (K<2)"})

    out["mean_ic"] = round(_mean(block_ic), 4) if block_ic else None
    out["mean_block_hit"] = round(_mean(block_hit), 4) if block_hit else None

    # --- Toplu isabet binom testi (İYİMSER: kesitsel korelasyonu yok sayar) ---
    if pooled_total > 0:
        out["pooled_hit_rate"] = round(pooled_hits / pooled_total, 4)
        out["pooled_n"] = pooled_total
        out["pooled_hit_p"] = round(_binom_two_sided_p(pooled_hits, pooled_total), 4)
        # Makine-okur tüketici için caveat JSON'a da taşınır (sadece render'da değil).
        out["pooled_hit_p_note"] = ("İYİMSER: blok-içi kesitsel korelasyonu yok sayar; "
                                    "etkin N≪pooled_n. Birincil ölçüt blok t-testidir.")
    else:
        out["pooled_hit_rate"] = None

    # --- Yorum: Student-t p tabanlı + küçük-K kapısı (verdict yalnız korumalı
    #     blok t-testinden türer; pooled binom ASLA verdict'i sürüklemez) ---
    p = out.get("p_rho")
    t = out.get("t_stat")
    if K < 4:
        verdict = f"yetersiz güç (K={K}<4) — sonuç çıkarılamaz"
    elif p is None or t is None:
        verdict = out.get("note", "belirsiz")
    elif p >= 0.05:
        verdict = "SIFIRDAN AYIRT EDİLEMEZ (skill kanıtı yok)"
    elif t > 0:
        verdict = "POZİTİF skill (anlamlı, p<0.05)"
    else:
        verdict = "NEGATİF/ters ilişki (anlamlı, p<0.05)"
    out["verdict"] = verdict
    return out


def skill_study(frames, horizons=(5, 10, 20), min_setup=200,
                include_relative_strength=True):
    return {
        "horizons": [study_horizon(frames, h, min_setup, include_relative_strength)
                     for h in horizons],
        "basis": "EOD günlük; örtüşmeyen bloklar; sabit varsayılan parametre (3/13)",
        "disclaimer": "karar-destek; yatırım tavsiyesi değildir",
    }


def render(result):
    lines = ["Teknik-Duruş MUTLAK SKILL Çalışması (örtüşmeyen, sızıntısız)",
             "=" * 60,
             "Sabit parametre: varsayılan (3/13) | H0: skill yok (ρ ortalaması=0)"]
    hdr = (f"{'ufuk':>5}{'blok':>6}{'ρ̄':>9}{'SE':>8}{'t':>8}{'p':>8}"
           f"{'isabet':>8}{'binom_p':>9}  yorum")
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for h in result["horizons"]:
        mr = f"{h['mean_rho']:9.3f}" if h.get('mean_rho') is not None else f"{'—':>9}"
        se = f"{h['se_rho']:8.3f}" if h.get('se_rho') is not None else f"{'—':>8}"
        ts = f"{h['t_stat']:8.2f}" if h.get('t_stat') is not None else f"{'—':>8}"
        pp = f"{h['p_rho']:8.3f}" if h.get('p_rho') is not None else f"{'—':>8}"
        hit = f"{h['pooled_hit_rate']:8.3f}" if h.get('pooled_hit_rate') is not None else f"{'—':>8}"
        bp = f"{h['pooled_hit_p']:9.3f}" if h.get('pooled_hit_p') is not None else f"{'—':>9}"
        lines.append(f"{h['horizon']:>5}{h['n_blocks']:>6}{mr}{se}{ts}{pp}{hit}{bp}  {h['verdict']}")
    lines.append("")
    lines.append("ρ̄=örtüşmeyen bloklarda ortalama Spearman; t/p=Student-t (df=K-1) "
                 "H0(ortalama=0); isabet=toplu yön-isabeti, binom_p H0(0.5).")
    lines.append("Not: p<0.05 → anlamlı (Student-t, küçük-K kalın kuyruk hesaba katılır; "
                 "K<4 → yetersiz güç). Toplu binom İYİMSER (blok-içi korelasyonu yok sayar); "
                 "birincil ölçüt korumalı blok t-testidir.")
    lines.append("Karar-destek; yatırım tavsiyesi değildir.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Self-test / CLI
# --------------------------------------------------------------------------- #

def _synthetic_frames(n_symbols=10, n_bars=320, signal=0.0):
    """Sentetik günlük frames. signal>0 → duruşun ileri getiriyi GERÇEKTEN
    öngördüğü kontrollü bir durum (testin pozitif-skill'i yakalayabildiğini doğrular)."""
    from backtest_posture import _synthetic_bars
    syms = {}
    slopes = [0.6, 0.4, 0.2, 0.0, -0.2, -0.4, 0.5, 0.1, -0.3, 0.3, -0.5, 0.25]
    for i in range(n_symbols):
        syms[f"S{i:02d}"] = _synthetic_bars(n_bars, slope=slopes[i % len(slopes)],
                                            noise_phase=i * 0.6)
    idx = _synthetic_bars(n_bars, slope=0.3, noise_phase=0.0)
    return {"symbols": syms, "index": idx}


def _run_selftest():
    frames = _synthetic_frames(10, 320)
    res = skill_study(frames, horizons=(5, 10), min_setup=200)
    ok = all(h["n_blocks"] >= 2 for h in res["horizons"])
    return {"self_test": True, "ok": ok,
            "blocks": {h["horizon"]: h["n_blocks"] for h in res["horizons"]},
            "verdicts": {h["horizon"]: h["verdict"] for h in res["horizons"]}}


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Teknik-duruş mutlak skill çalışması (karar-destek).")
    p.add_argument("--file", help="günlük frames.json (≥250 bar/sembol önerilir)")
    p.add_argument("--horizons", default="5,10,20",
                   help="virgüllü ufuk listesi (işlem günü)")
    p.add_argument("--min-setup", type=int, default=200,
                   help="ilk blok için asgari setup-barı (SMA200 için ≥200)")
    p.add_argument("--no-rs", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if not args.file:
        out = _run_selftest()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out["ok"] else 1

    with open(args.file, "r", encoding="utf-8") as f:
        frames = json.load(f)
    horizons = tuple(int(x) for x in args.horizons.split(",") if x.strip())
    res = skill_study(frames, horizons=horizons, min_setup=args.min_setup,
                      include_relative_strength=not args.no_rs)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
