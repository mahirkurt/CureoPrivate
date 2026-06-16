#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""financial_quality_score.py — Sektör-normalize finansal kalite kompoziti (0-100).

`bist-analist-kopilotu` becerisinin temel-analiz katmanını deterministik bir
kalite skoruna indirger. `references/fundamental-methodology.md` ile AYNI tanımı
paylaşır: dört alt-skor (kârlılık / kaldıraç-ödeme gücü / büyüme / değerleme
makullüğü) sektör-normalize edilip ağırlıklı kompozite birleştirilir.

Girdi: `get_financial_ratios` çıktısından türetilen oran sözlüğü (+ opsiyonel
`get_sector_comparison` emsal listesi). Ağ erişimi YOK — beceri zaten çektiği
veriyi son-işler.

> Karar-destek hatırlatması: Bu skor finansal kaliteye dair GÖZLEM üretir;
> yatırım tavsiyesi veya hedef fiyat VERMEZ. Negatif/anlamsız oranlar (ör. zarar
> eden şirkette F/K) "ucuzluk" sayılmaz. Eksik veride uydurma yapılmaz; ilgili
> alt-skor boş bırakılır ve kompozit "kısmi" işaretlenir.

Pür-deterministik, yalnız standart kütüphane (json, re, sys, math, argparse).
CLI: `--file ratios.json [--sector Bankacilik]`. Argümansız çalışınca self-test.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys

# ---------------------------------------------------------------------------
# Oran anahtarı normalizasyonu (alias toleransı)
# ---------------------------------------------------------------------------
# Beceri/MCP farklı isimlerle dönebilir; hepsini kanonik anahtara eşleriz.
_ALIASES = {
    "pe_ratio": ["pe_ratio", "pe", "fk", "f_k", "price_earnings", "fiyat_kazanc"],
    "pb": ["pb", "pd_dd", "pddd", "price_to_book", "pbv", "pd_dd_orani"],
    "ev_ebitda": ["ev_ebitda", "ev_to_ebitda", "fd_favok", "fdfavok", "evebitda"],
    "roe": ["roe", "ozkaynak_karliligi", "return_on_equity"],
    "roa": ["roa", "aktif_karliligi", "return_on_assets"],
    "net_margin": ["net_margin", "net_marj", "net_profit_margin", "net_kar_marji"],
    "ebitda_margin": ["ebitda_margin", "favok_marji", "favok_margin", "operating_margin"],
    "debt_to_equity": ["debt_to_equity", "de", "kaldirac", "leverage", "borc_ozkaynak", "borc_oz_kaynak"],
    "current_ratio": ["current_ratio", "cari_oran", "cari"],
    "net_debt_to_ebitda": ["net_debt_to_ebitda", "net_borc_favok", "netdebt_ebitda", "nd_ebitda"],
    "revenue_growth": ["revenue_growth", "satis_buyumesi", "sales_growth", "revenue_yoy", "satis_yoy"],
    "earnings_growth": ["earnings_growth", "net_kar_buyumesi", "earnings_yoy", "profit_growth", "kar_yoy"],
    "dividend_yield": ["dividend_yield", "temettu_verimi", "div_yield"],
}

# Kanonik anahtar -> üyesi olduğu alt-skor (coverage hesabı için referans küme)
_PROFIT_KEYS = ["roe", "roa", "net_margin", "ebitda_margin"]
_SOLV_KEYS = ["debt_to_equity", "current_ratio", "net_debt_to_ebitda"]
_GROWTH_KEYS = ["revenue_growth", "earnings_growth"]
_VAL_KEYS = ["pe_ratio", "pb", "ev_ebitda"]
_ALL_KEYS = _PROFIT_KEYS + _SOLV_KEYS + _GROWTH_KEYS + _VAL_KEYS

# Alt-skor kompozit ağırlıkları (sektör merceğine göre yeniden ölçeklenir)
_DEFAULT_WEIGHTS = {
    "profitability": 0.32,
    "solvency": 0.26,
    "growth": 0.18,
    "valuation_reasonableness": 0.24,
}
# Banka merceği: ev_ebitda/current_ratio anlamsız → kârlılık (ROE) ve değerleme
# (PD/DD) ağırlığı artar, ödeme gücü (klasik likidite) ağırlığı düşer.
_BANK_WEIGHTS = {
    "profitability": 0.40,
    "solvency": 0.14,
    "growth": 0.16,
    "valuation_reasonableness": 0.30,
}

_BANK_PATTERNS = [
    "bank", "banka", "xbank", "xumal", "mali", "finans", "katilim",
    "leasing", "faktoring", "sigorta",
]


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def _to_float(value):
    """None/'-'/'N/A'/'%12,3' gibi değerleri güvenle float'a çevir; aksi halde None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        f = float(value)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(value, str):
        s = value.strip()
        if s == "" or s.lower() in ("n/a", "na", "none", "null", "-", "—"):
            return None
        s = s.replace("%", "").replace(" ", "")
        # Türkçe ondalık: 1.234,56 -> 1234.56  | 12,3 -> 12.3
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        try:
            f = float(s)
            return None if (math.isnan(f) or math.isinf(f)) else f
        except ValueError:
            return None
    return None


def _normalize_ratios(ratios):
    """Ham oran sözlüğünü kanonik anahtarlara indirger (alias toleranslı)."""
    if not isinstance(ratios, dict):
        return {}
    # Anahtarları küçük harf + non-alnum sadeleştir
    lowered = {}
    for k, v in ratios.items():
        if not isinstance(k, str):
            continue
        norm = re.sub(r"[^a-z0-9]", "_", k.strip().lower())
        norm = re.sub(r"_+", "_", norm).strip("_")
        lowered.setdefault(norm, v)
    out = {}
    for canon, names in _ALIASES.items():
        for name in names:
            if name in lowered:
                fv = _to_float(lowered[name])
                if fv is not None:
                    out[canon] = fv
                    break
    return out


def _is_bank(sector):
    if not sector:
        return False
    s = sector.strip().lower()
    return any(p in s for p in _BANK_PATTERNS)


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def _percent_scale(value):
    """ROE/ROA/marj gibi oranları yüzde tabanına getir (0.18 -> 18.0)."""
    if value is None:
        return None
    # 0-1 aralığındaki kesirleri yüzdeye çevir (ör. 0.22 ROE -> 22%)
    if -1.5 < value < 1.5:
        return value * 100.0
    return value


def _score_higher_better(value, low, high):
    """value low->0, high->100 arasında lineer; aralık dışı clamp."""
    if value is None:
        return None
    if high == low:
        return 50.0
    return _clamp((value - low) / (high - low) * 100.0)


def _score_lower_better(value, best, worst):
    """Düşük değer iyi: best->100, worst->0 lineer."""
    if value is None:
        return None
    if worst == best:
        return 50.0
    return _clamp((worst - value) / (worst - best) * 100.0)


def _median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    n = len(vals)
    mid = n // 2
    if n % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def _peer_median(peers, canon_key):
    """Emsal listesinden bir oranın medyanını çıkar (alias toleranslı)."""
    if not peers:
        return None
    vals = []
    for p in peers:
        norm = _normalize_ratios(p)
        if canon_key in norm:
            vals.append(norm[canon_key])
    return _median(vals)


# ---------------------------------------------------------------------------
# Alt-skorlar
# ---------------------------------------------------------------------------
def _sub_profitability(r, is_bank):
    parts = []
    roe = _percent_scale(r.get("roe"))
    roa = _percent_scale(r.get("roa"))
    nm = _percent_scale(r.get("net_margin"))
    em = _percent_scale(r.get("ebitda_margin"))
    # Bankada ROE birincil, ROA ikincil; sanayide marjlar daha bilgilendirici.
    if roe is not None:
        parts.append((_score_higher_better(roe, 0, 35), 0.45 if is_bank else 0.35))
    if roa is not None:
        # Bankada ROA tabanı düşüktür (~1-2%); ölçeği ona göre seç.
        hi = 3.0 if is_bank else 12.0
        parts.append((_score_higher_better(roa, 0, hi), 0.30 if is_bank else 0.25))
    if not is_bank:
        if nm is not None:
            parts.append((_score_higher_better(nm, 0, 25), 0.20))
        if em is not None:
            parts.append((_score_higher_better(em, 0, 35), 0.20))
    else:
        # Bankada net marj net-faiz-marjı vekili olarak okunur.
        if nm is not None:
            parts.append((_score_higher_better(nm, 0, 40), 0.25))
    return _weighted(parts)


def _sub_solvency(r, is_bank):
    parts = []
    de = r.get("debt_to_equity")
    cr = r.get("current_ratio")
    nde = r.get("net_debt_to_ebitda")
    if de is not None:
        # Düşük kaldıraç iyi: 0 -> 100, 3.0 -> 0
        parts.append((_score_lower_better(de, 0.0, 3.0), 0.45 if not is_bank else 0.70))
    if not is_bank:
        # Banka için cari oran ve net borç/FAVÖK anlamsız → atlanır.
        if cr is not None:
            # Cari oran ~1.5-2 ideal; çok yüksek atıl sermaye sayılabilir, hafif tepe.
            if cr <= 2.0:
                s = _score_higher_better(cr, 0.5, 2.0)
            else:
                s = _clamp(100.0 - (cr - 2.0) * 10.0, 60.0, 100.0)
            parts.append((s, 0.30))
        if nde is not None:
            # net borç/FAVÖK: 0 -> 100, 5 -> 0; negatif (net nakit) en iyi.
            if nde < 0:
                parts.append((100.0, 0.25))
            else:
                parts.append((_score_lower_better(nde, 0.0, 5.0), 0.25))
    return _weighted(parts)


def _sub_growth(r):
    parts = []
    rg = _percent_scale(r.get("revenue_growth"))
    eg = _percent_scale(r.get("earnings_growth"))
    if rg is not None:
        parts.append((_score_higher_better(rg, -10, 50), 0.5))
    if eg is not None:
        parts.append((_score_higher_better(eg, -20, 60), 0.5))
    return _weighted(parts)


def _val_one(value, cheap, fair_lo, fair_hi, expensive):
    """Tek değerleme çarpanı için makullük skoru.

    Aşırı-ucuz ve aşırı-pahalı UÇLAR cezalandırılır; makul bant en yüksek puan.
    cheap < fair_lo <= fair_hi < expensive bekleriz.
    """
    if value is None:
        return None
    if value <= 0:
        # Negatif/sıfır çarpan (ör. zarar) anlamlı değil → düşük, ucuzluk değil.
        return 20.0
    if fair_lo <= value <= fair_hi:
        return 100.0
    if value < fair_lo:
        # Ucuz tarafa doğru: makulden ucuza inerken hafif ceza (dayanaksız ucuz).
        if value <= cheap:
            return 45.0
        return _clamp(100.0 - (fair_lo - value) / max(fair_lo - cheap, 1e-9) * 55.0, 45.0, 100.0)
    # Pahalı taraf: makulden pahalıya çıkarken ceza.
    if value >= expensive:
        return 10.0
    return _clamp(100.0 - (value - fair_hi) / max(expensive - fair_hi, 1e-9) * 90.0, 10.0, 100.0)


def _sub_valuation(r, is_bank, peers):
    """Değerleme makullüğü. Emsal medyanı varsa ona göre normalize; yoksa
    mutlak sezgisel bantlar (BIST/sektör tipiği)."""
    parts = []
    pe = r.get("pe_ratio")
    pb = r.get("pb")
    ev = r.get("ev_ebitda")

    pe_med = _peer_median(peers, "pe_ratio")
    pb_med = _peer_median(peers, "pb")
    ev_med = _peer_median(peers, "ev_ebitda")

    def _bands_from_median(med, abs_default):
        if med and med > 0:
            return (med * 0.4, med * 0.7, med * 1.3, med * 2.2)
        return abs_default

    # F/K
    if pe is not None:
        cheap, flo, fhi, exp = _bands_from_median(pe_med, (3.0, 5.0, 12.0, 25.0))
        w = 0.25 if is_bank else 0.40  # bankada F/K daha az bilgilendirici
        parts.append((_val_one(pe, cheap, flo, fhi, exp), w))
    # PD/DD
    if pb is not None:
        if is_bank:
            cheap, flo, fhi, exp = _bands_from_median(pb_med, (0.4, 0.6, 1.2, 2.0))
            w = 0.55  # banka değerlemesinde PD/DD birincil
        else:
            cheap, flo, fhi, exp = _bands_from_median(pb_med, (0.6, 0.9, 2.5, 5.0))
            w = 0.30
        parts.append((_val_one(pb, cheap, flo, fhi, exp), w))
    # FD/FAVÖK — bankada anlamsız (finansal kuruluş), atlanır.
    if ev is not None and not is_bank:
        cheap, flo, fhi, exp = _bands_from_median(ev_med, (3.0, 4.0, 9.0, 16.0))
        parts.append((_val_one(ev, cheap, flo, fhi, exp), 0.30))
    return _weighted(parts)


def _weighted(parts):
    """parts: [(score_or_None, weight), ...] → ağırlıklı ortalama veya None."""
    num = 0.0
    den = 0.0
    for score, w in parts:
        if score is None:
            continue
        num += score * w
        den += w
    if den == 0:
        return None
    return num / den


# ---------------------------------------------------------------------------
# Ana giriş
# ---------------------------------------------------------------------------
def quality_score(ratios, sector=None, peers=None):
    """Sektör-normalize finansal kalite kompoziti.

    Args:
        ratios: get_financial_ratios çıktısından türeyen oran sözlüğü.
        sector: opsiyonel sektör etiketi (ör. 'Bankacilik', 'XUSIN').
        peers: opsiyonel emsal oran sözlüğü listesi (get_sector_comparison).

    Returns:
        {composite, band, subscores, drivers, caveats, coverage, ...}
        Çıktı karar-destek; yatırım tavsiyesi değildir.
    """
    caveats = []
    r = _normalize_ratios(ratios)
    if not isinstance(peers, list):
        peers = None
    is_bank = _is_bank(sector)

    # Coverage: beklenen tüm girdilerin ne kadarı mevcut
    present = sum(1 for k in _ALL_KEYS if k in r)
    coverage = round(present / len(_ALL_KEYS), 3)

    subscores = {
        "profitability": _sub_profitability(r, is_bank),
        "solvency": _sub_solvency(r, is_bank),
        "growth": _sub_growth(r),
        "valuation_reasonableness": _sub_valuation(r, is_bank, peers),
    }
    # Yuvarla (None koru)
    subscores = {k: (round(v, 1) if v is not None else None) for k, v in subscores.items()}

    weights = _BANK_WEIGHTS if is_bank else _DEFAULT_WEIGHTS
    if is_bank:
        caveats.append(
            "Banka/finansal kuruluş merceği uygulandı: FD/FAVÖK ve cari oran "
            "anlamsız sayıldı; ROE, PD/DD ve net-faiz-marjı vekili öne çıkarıldı."
        )

    # Kompozit: mevcut alt-skorların ağırlıklı ortalaması
    comp_parts = [(subscores[k], weights[k]) for k in weights]
    composite = _weighted(comp_parts)

    partial = any(v is None for v in subscores.values())
    if partial:
        missing_subs = [k for k, v in subscores.items() if v is None]
        caveats.append(
            "Kısmi skor: şu alt-boyut(lar) veri yetersizliğinden boş — "
            + ", ".join(missing_subs) + " (uydurma değerle doldurulmadı)."
        )

    # Büyüme nominal/TL uyarısı (enflasyon caveat)
    rg = _percent_scale(r.get("revenue_growth"))
    eg = _percent_scale(r.get("earnings_growth"))
    if (rg is not None and rg > 0) or (eg is not None and eg > 0):
        caveats.append(
            "Büyüme nominal TL bazlı olabilir; yüksek enflasyon ortamında reel "
            "büyüme abartılır. Reel/marj teyidi olmadan büyüme alt-skoru ihtiyatlı "
            "okunmalı (bkz. fundamental-methodology §5)."
        )

    # Negatif değerleme çarpanı uyarısı
    for key, label in (("pe_ratio", "F/K"), ("ev_ebitda", "FD/FAVÖK")):
        v = r.get(key)
        if v is not None and v <= 0:
            caveats.append(
                f"{label} negatif/sıfır → zarar veya anlamsız; düşük çarpan "
                f"'ucuzluk' sayılmadı."
            )

    confidence = "yüksek"
    if coverage < 0.4:
        confidence = "düşük"
        caveats.append(
            "Düşük güven: girdi kapsamı %40'ın altında; kompozit yalnızca sınırlı "
            "bir görünüm sunar."
        )
    elif coverage < 0.65 or partial:
        confidence = "orta"

    if composite is None:
        return {
            "composite": None,
            "band": None,
            "subscores": subscores,
            "drivers": [],
            "caveats": caveats + ["Hiçbir alt-skor hesaplanamadı; girdi boş/uyumsuz."],
            "coverage": coverage,
            "confidence": "yok",
            "sector": sector,
            "bank_lens": is_bank,
            "note": "Karar-destek; yatırım tavsiyesi değildir.",
        }

    composite = round(composite, 1)
    band = _band(composite)

    # Drivers: kompozite en çok katkı yapan alt-skorlar (ağırlık*skor)
    contribs = []
    for k in weights:
        s = subscores[k]
        if s is not None:
            contribs.append({
                "subscore": k,
                "value": s,
                "weight": weights[k],
                "contribution": round(s * weights[k], 2),
                "direction": "olumlu" if s >= 55 else ("nötr" if s >= 45 else "olumsuz"),
            })
    contribs.sort(key=lambda c: c["contribution"], reverse=True)

    return {
        "composite": composite,
        "band": band,
        "subscores": subscores,
        "drivers": contribs[:3],
        "all_contributions": contribs,
        "caveats": caveats,
        "coverage": coverage,
        "confidence": confidence,
        "sector": sector,
        "bank_lens": is_bank,
        "weights_used": weights,
        "note": "Karar-destek; yatırım tavsiyesi değildir.",
    }


def _band(score):
    """0-100 → Türkçe band etiketi (spec: ≥75 Yüksek, 60-74 İyi, 40-59 Orta, <40 Zayıf)."""
    if score >= 75:
        return "Yüksek"
    if score >= 60:
        return "İyi"
    if score >= 40:
        return "Orta"
    return "Zayıf"


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------
def _self_test():
    print("== financial_quality_score self-test ==", file=sys.stderr)

    # 1) Sağlam sanayi şirketi
    industrial = {
        "pe_ratio": 8.5, "pb": 1.6, "ev_ebitda": 6.2,
        "roe": 24, "roa": 9, "net_margin": 14, "ebitda_margin": 22,
        "debt_to_equity": 0.6, "current_ratio": 1.8, "net_debt_to_ebitda": 1.2,
        "revenue_growth": 35, "earnings_growth": 28, "dividend_yield": 4.5,
    }
    res = quality_score(industrial, sector="XUSIN")
    assert res["composite"] is not None
    assert res["band"] in ("Yüksek", "İyi", "Orta", "Zayıf")
    assert 0 <= res["composite"] <= 100
    assert res["coverage"] > 0.9
    assert res["bank_lens"] is False
    print(f"  [1] sanayi: composite={res['composite']} band={res['band']} cov={res['coverage']}", file=sys.stderr)

    # 2) Banka merceği (alias + Türkçe ondalık string)
    bank = {
        "fk": "4,2", "pd_dd": "0,9", "roe": "32", "roa": "2,1",
        "net_marj": "38", "kaldirac": "8,0",
    }
    resb = quality_score(bank, sector="Bankacilik")
    assert resb["bank_lens"] is True
    # Bankada ev_ebitda yoksa bile değerleme skoru PD/DD'den üretilmeli
    assert resb["subscores"]["valuation_reasonableness"] is not None
    assert resb["weights_used"]["solvency"] < _DEFAULT_WEIGHTS["solvency"]
    print(f"  [2] banka: composite={resb['composite']} band={resb['band']}", file=sys.stderr)

    # 3) Zarar eden / negatif F/K → ucuzluk sayılmamalı
    loss = {"pe_ratio": -3.0, "pb": 0.5, "roe": -15, "net_margin": -8,
            "debt_to_equity": 2.8, "revenue_growth": -12, "earnings_growth": -40}
    resl = quality_score(loss, sector="XUSIN")
    assert any("negatif" in c.lower() for c in resl["caveats"])
    assert resl["composite"] < 55  # zayıf temel
    print(f"  [3] zarar: composite={resl['composite']} band={resl['band']}", file=sys.stderr)

    # 4) Eksik veri → kısmi + düşük güven, asla crash
    sparse = {"roe": 18}
    ress = quality_score(sparse)
    assert ress["coverage"] < 0.4
    assert ress["confidence"] in ("düşük", "yok")
    assert any("güven" in c.lower() or "kısmi" in c.lower() for c in ress["caveats"])
    print(f"  [4] seyrek: composite={ress['composite']} conf={ress['confidence']}", file=sys.stderr)

    # 5) Tamamen boş / bozuk girdi → crash yok
    for bad in (None, {}, {"foo": "bar"}, [], "x"):
        rb = quality_score(bad)
        assert "note" in rb
    print("  [5] bozuk girdi: crash yok", file=sys.stderr)

    # 6) Emsal medyanı ile değerleme normalizasyonu
    peers = [
        {"pe_ratio": 7, "pb": 1.2, "ev_ebitda": 5},
        {"pe_ratio": 9, "pb": 1.4, "ev_ebitda": 6},
        {"pe_ratio": 11, "pb": 1.8, "ev_ebitda": 7},
    ]
    resp = quality_score(industrial, sector="XUSIN", peers=peers)
    assert resp["subscores"]["valuation_reasonableness"] is not None
    print(f"  [6] emsal-normalize: val={resp['subscores']['valuation_reasonableness']}", file=sys.stderr)

    print("== ALL TESTS PASSED ==", file=sys.stderr)
    # Örnek JSON çıktı
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sektör-normalize finansal kalite kompoziti (0-100). "
                    "Karar-destek; yatırım tavsiyesi değildir.",
    )
    parser.add_argument("--file", help="Oran sözlüğü JSON dosyası (get_financial_ratios çıktısı).")
    parser.add_argument("--sector", default=None, help="Sektör etiketi (ör. Bankacilik, XUSIN).")
    parser.add_argument("--peers", help="Opsiyonel emsal oranlar JSON dosyası (liste).")
    args = parser.parse_args(argv)

    if not args.file:
        return _self_test()

    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Girdi okunamadı: {exc}",
                          "note": "Karar-destek; yatırım tavsiyesi değildir."},
                         ensure_ascii=False))
        return 1

    # Esnek girdi: ya doğrudan oran sözlüğü ya da {ratios, sector, peers} zarfı
    ratios = payload
    sector = args.sector
    peers = None
    if isinstance(payload, dict) and "ratios" in payload:
        ratios = payload.get("ratios")
        sector = args.sector or payload.get("sector")
        peers = payload.get("peers")

    if args.peers:
        try:
            with open(args.peers, "r", encoding="utf-8") as fh:
                peers = json.load(fh)
        except (OSError, ValueError):
            peers = peers  # sessizce yoksay; skor emsalsiz devam eder

    result = quality_score(ratios, sector=sector, peers=peers)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
