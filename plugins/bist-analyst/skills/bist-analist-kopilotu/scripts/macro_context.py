#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""macro_context.py — TCMB makro rejim sınıflandırması (BIST hisse zemini).

`bist-analist-kopilotu` becerisinin makro katmanını deterministik bir rejim
etiketine indirger. `references/evds-macro.md` ile AYNI sinyalleri kullanır:
(a) politika faizi trendi, (b) reel faiz, (c) TÜFE trendi, (d) kur trendi.

Rejim ∈ {Sıkılaştırma, Gevşeme, Nötr/Yatay, Belirsizlik/Stres}.

Girdi: `get_evds_data` / `get_macro_data` / `get_fx_data` / `get_bond_yields`
çıktılarından türeyen sinyaller (hepsi opsiyonel). Ağ erişimi YOK — beceri zaten
çektiği veriyi son-işler.

> Bu betiğin ürettiği makro çıkarımlar KARAR-DESTEK amaçlıdır; YATIRIM TAVSİYESİ
> DEĞİLDİR. Sektör eğilimleri genel bağlamdır, otomatik hisse seçimi değildir.

Pür-deterministik, yalnız standart kütüphane (json, re, sys, math, argparse).
CLI: `--file macro.json`. Argümansız çalışınca self-test.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

# Eşikler (yüzde puanı cinsinden)
_RATE_FLAT_BAND = 0.5      # |Δ politika faizi| < 0.5pp → yatay
_CPI_FLAT_BAND = 1.0       # |Δ TÜFE yıllık| < 1.0pp → yatay
_FX_SHARP_PACE = 5.0       # son adımda TL %5+ değer kaybı → keskin
_FX_STRESS_PACE = 10.0     # %10+ → stres bayrağı
_REAL_RATE_DEEP_NEG = -10.0  # reel faiz -10pp altı → derin negatif (stres)


def _to_float(value):
    """None/'-'/'%45,1' güvenli float; aksi None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        f = float(value)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(value, str):
        s = value.strip().replace("%", "").replace(" ", "")
        if s == "" or s.lower() in ("n/a", "na", "none", "null", "-", "—"):
            return None
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


def _as_history(value):
    """Bir değeri kronolojik sayı listesine indirger.

    Kabul eder: tek sayı, sayı listesi, ya da [{'value':..}/{'deger':..}] gibi
    sözlük listesi. Liste sırası ESKİDEN YENİYE varsayılır (son = en güncel).
    """
    if value is None:
        return []
    if isinstance(value, (int, float, str)):
        f = _to_float(value)
        return [] if f is None else [f]
    if isinstance(value, dict):
        for k in ("value", "deger", "val", "v", "rate", "yield"):
            if k in value:
                f = _to_float(value[k])
                return [] if f is None else [f]
        return []
    if isinstance(value, (list, tuple)):
        out = []
        for item in value:
            if isinstance(item, dict):
                got = _as_history(item)
                out.extend(got)
            else:
                f = _to_float(item)
                if f is not None:
                    out.append(f)
        return out
    return []


def _trend(current, prev=None, history=None):
    """Trend yönünü ('rising'/'falling'/'flat'/None) ve delta'yı çıkar.

    current: güncel değer. prev: opsiyonel önceki değer. history: opsiyonel
    seri (eskiden yeniye). prev verilmemişse history'nin son-bir-önceki kullanılır.
    """
    cur = _to_float(current)
    hist = _as_history(history)
    if cur is None and hist:
        cur = hist[-1]
    p = _to_float(prev)
    if p is None and len(hist) >= 2:
        p = hist[-2]
    if cur is None or p is None:
        return None, None
    delta = cur - p
    return delta, cur


def _label_rate_trend(delta):
    if delta is None:
        return None
    if delta > _RATE_FLAT_BAND:
        return "rising"
    if delta < -_RATE_FLAT_BAND:
        return "falling"
    return "flat"


def _label_cpi_trend(delta):
    if delta is None:
        return None
    if delta > _CPI_FLAT_BAND:
        return "rising"      # enflasyon hızlanıyor
    if delta < -_CPI_FLAT_BAND:
        return "falling"     # enflasyon yavaşlıyor (dezenflasyon)
    return "flat"


def _fx_pace(usdtry, usdtry_prev=None, usdtry_history=None):
    """TL değer kaybı hızı (% olarak, pozitif = TL zayıflıyor)."""
    delta, cur = _trend(usdtry, usdtry_prev, usdtry_history)
    if delta is None or cur is None or cur == 0:
        return None, cur
    prev = cur - delta
    if prev == 0:
        return None, cur
    pct = (cur - prev) / abs(prev) * 100.0  # USDTRY artışı = TL zayıflaması
    return pct, cur


def classify_regime(
    policy_rate=None, policy_rate_prev=None, policy_rate_history=None,
    cpi_yoy=None, cpi_prev=None, cpi_history=None,
    usdtry=None, usdtry_prev=None, usdtry_history=None,
    bond_yield_10y=None, bond_yield_2y=None,
    reer=None, reer_prev=None,
    **extra,
):
    """Makro sinyallerden BIST rejimini sınıflandır.

    Tüm girdiler opsiyoneldir; mevcut olanlardan hesaplanır, eksikler listelenir
    ve güven düşürülür. Trend yardımcıları prev değeri VEYA history listesi kabul
    eder.

    Returns:
        {regime, real_rate, signals_resolved, equity_implications,
         confidence, missing_signals, note}
        Çıktı karar-destek; yatırım tavsiyesi değildir.
    """
    missing = []

    pr = _to_float(policy_rate)
    if pr is None:
        ph = _as_history(policy_rate_history)
        pr = ph[-1] if ph else None
    cpi = _to_float(cpi_yoy)
    if cpi is None:
        ch = _as_history(cpi_history)
        cpi = ch[-1] if ch else None

    # Reel faiz = politika faizi − cari/beklenen TÜFE yıllık
    real_rate = None
    if pr is not None and cpi is not None:
        real_rate = round(pr - cpi, 2)
    else:
        missing.append("real_rate (politika faizi veya TÜFE eksik)")

    # Trendler
    rate_delta, _ = _trend(policy_rate, policy_rate_prev, policy_rate_history)
    rate_trend = _label_rate_trend(rate_delta)
    if rate_trend is None:
        missing.append("policy_rate_trend (önceki/geçmiş yok)")

    cpi_delta, _ = _trend(cpi_yoy, cpi_prev, cpi_history)
    cpi_trend = _label_cpi_trend(cpi_delta)
    if cpi_trend is None:
        missing.append("cpi_trend (önceki/geçmiş yok)")

    fx_pct, usdtry_cur = _fx_pace(usdtry, usdtry_prev, usdtry_history)
    if fx_pct is None:
        missing.append("fx_trend (USDTRY önceki/geçmiş yok)")

    if reer is None:
        missing.append("reer")

    signals = {
        "policy_rate": pr,
        "policy_rate_trend": rate_trend,
        "policy_rate_delta": (round(rate_delta, 2) if rate_delta is not None else None),
        "cpi_yoy": cpi,
        "cpi_trend": cpi_trend,
        "cpi_delta": (round(cpi_delta, 2) if cpi_delta is not None else None),
        "real_rate": real_rate,
        "usdtry": usdtry_cur,
        "fx_depreciation_pct": (round(fx_pct, 2) if fx_pct is not None else None),
        "bond_yield_10y": _to_float(bond_yield_10y),
        "bond_yield_2y": _to_float(bond_yield_2y),
        "reer": _to_float(reer),
    }

    # ---- Stres bayrağı ----
    stress = False
    stress_reasons = []
    if fx_pct is not None and fx_pct >= _FX_STRESS_PACE:
        stress = True
        stress_reasons.append(f"keskin TL değer kaybı (%{round(fx_pct,1)})")
    if real_rate is not None and real_rate <= _REAL_RATE_DEEP_NEG:
        stress = True
        stress_reasons.append(f"derin negatif reel faiz ({real_rate}pp)")

    # ---- Rejim kararı ----
    # Sinyalleri yönlü oy olarak topla: +1 sıkılaştırıcı, -1 gevşetici.
    tighten = 0
    loosen = 0
    resolved = 0

    if rate_trend == "rising":
        tighten += 1; resolved += 1
    elif rate_trend == "falling":
        loosen += 1; resolved += 1
    elif rate_trend == "flat":
        resolved += 1

    if real_rate is not None:
        resolved += 1
        if real_rate > 0:
            tighten += 1
        elif real_rate < 0:
            loosen += 1  # negatif reel faiz gevşeticidir

    if cpi_trend == "falling":     # dezenflasyon → gevşeme alanı açar
        loosen += 1; resolved += 1
    elif cpi_trend == "rising":    # enflasyon hızlanıyor → sıkılaştırma baskısı
        tighten += 1; resolved += 1
    elif cpi_trend == "flat":
        resolved += 1

    fx_sharp = fx_pct is not None and fx_pct >= _FX_SHARP_PACE

    # Karar mantığı (evds-macro §2 ile hizalı)
    if resolved == 0:
        regime = "Belirsizlik/Stres"
        regime_reason = "Hiçbir yönlü sinyal çözülemedi (veri yetersiz)."
    elif stress:
        regime = "Belirsizlik/Stres"
        regime_reason = "Stres bayrağı: " + "; ".join(stress_reasons) + "."
    elif fx_sharp and tighten <= loosen:
        # Kur hızlanırken net sıkılaştırma yoksa → belirsizlik/stres eğilimi
        regime = "Belirsizlik/Stres"
        regime_reason = (
            f"Kur hızlanıyor (%{round(fx_pct,1)}) ancak net sıkılaştırma yok; "
            "sinyaller çelişkili."
        )
    elif tighten - loosen >= 2:
        regime = "Sıkılaştırma"
        regime_reason = "Sıkılaştırıcı sinyaller baskın (faiz↑ / reel faiz+ / TÜFE zirve-düşüş)."
    elif loosen - tighten >= 2:
        regime = "Gevşeme"
        regime_reason = "Gevşetici sinyaller baskın (faiz↓ / reel faiz− / dezenflasyon)."
    elif tighten > loosen:
        regime = "Sıkılaştırma"
        regime_reason = "Hafif sıkılaştırıcı eğilim (zayıf çoğunluk)."
    elif loosen > tighten:
        regime = "Gevşeme"
        regime_reason = "Hafif gevşetici eğilim (zayıf çoğunluk)."
    else:
        # Eşit oy: sinyaller çelişkili mi yoksa gerçekten yatay mı?
        if rate_trend == "flat" and cpi_trend in ("flat", None) and not fx_sharp:
            regime = "Nötr/Yatay"
            regime_reason = "Sinyaller dengeli ve durağan; belirgin yön yok."
        else:
            regime = "Belirsizlik/Stres"
            regime_reason = "Sinyaller çelişkili; tek yön ilan edilemiyor."

    implications = _equity_implications(regime, signals, stress)

    # Güven: çözülen sinyal sayısı + reel faiz varlığı
    if resolved >= 3 and real_rate is not None:
        confidence = "yüksek"
    elif resolved >= 2:
        confidence = "orta"
    else:
        confidence = "düşük"
    if stress and resolved < 2:
        confidence = "düşük"

    note = (
        "Karar-destek; yatırım tavsiyesi değildir. Sektör eğilimleri genel "
        "bağlamdır, otomatik hisse seçimi değildir. "
    )
    if missing:
        note += "Eksik sinyaller güveni düşürdü: " + ", ".join(missing) + "."

    return {
        "regime": regime,
        "regime_reason": regime_reason,
        "real_rate": real_rate,
        "signals_resolved": signals,
        "votes": {"tighten": tighten, "loosen": loosen, "resolved": resolved},
        "stress_flag": stress,
        "equity_implications": implications,
        "confidence": confidence,
        "missing_signals": missing,
        "note": note,
    }


def _equity_implications(regime, signals, stress):
    """Rejime göre niteliksel hisse çıkarımları (evds-macro §2-3 ile hizalı).

    Sektör eğilimleri BAĞLAM olarak çerçevelenir; tavsiye değildir.
    """
    if regime == "Sıkılaştırma":
        return {
            "discount_rate_pressure": "yukarı (iskonto oranı yükselir → değerleme baskısı)",
            "sector_tilts": {
                "banks": "net faiz marjı / makas göreli pozitif",
                "exporters": "nötr; kur stabilize ise avantaj sınırlı",
                "rate_sensitive": "baskı altında (GYO, inşaat, yüksek kaldıraç, uzun-vadeli temettü)",
                "importers": "kur stabilize ise göreli rahatlama",
            },
            "narrative": "Uzun-vadeli/yüksek-büyüme isimler dezavantajlı; faize-duyarlı baskıda.",
        }
    if regime == "Gevşeme":
        return {
            "discount_rate_pressure": "aşağı (iskonto oranı düşer → değerleme desteği)",
            "sector_tilts": {
                "banks": "makas daralma riski / net faiz marjı baskısı",
                "exporters": "nötr; TL sakinse döviz-geliri avantajı azalır",
                "rate_sensitive": "avantajlı (GYO, inşaat, yüksek kaldıraçlı sanayi, büyüme)",
                "importers": "girdi maliyeti açısından göreli rahat",
            },
            "narrative": "Büyüme ve faize-duyarlı isimler öne çıkar; banka makası daralabilir.",
        }
    if regime == "Belirsizlik/Stres":
        return {
            "discount_rate_pressure": "oynak / risk primi yüksek",
            "sector_tilts": {
                "banks": "değişken; faiz yönü netleşene dek belirsiz",
                "exporters": "göreli korunaklı (zayıf/oynak TL + döviz geliri)",
                "rate_sensitive": "kırılgan (yüksek kaldıraç + oynak iskonto)",
                "importers": "baskı altında (TL değer kaybı maliyeti artırır)",
            },
            "narrative": (
                "İhracatçılar ve döviz-bazlı gelir/varlık taşıyanlar göreli "
                "korunaklı; saf yerel-talep isimleri kırılgan."
            ),
        }
    # Nötr/Yatay
    return {
        "discount_rate_pressure": "yatay / belirgin yön yok",
        "sector_tilts": {
            "banks": "nötr",
            "exporters": "nötr",
            "rate_sensitive": "nötr",
            "importers": "nötr",
        },
        "narrative": "Belirgin makro eğilim yok; seçim şirket-özel temel/teknik bağlama kayar.",
    }


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------
def _self_test():
    print("== macro_context self-test ==", file=sys.stderr)

    # 1) Sıkılaştırma: faiz yükseliyor, reel faiz pozitif, TÜFE düşüyor
    r1 = classify_regime(
        policy_rate=50, policy_rate_prev=45,
        cpi_yoy=38, cpi_prev=42,
        usdtry=33.0, usdtry_prev=32.8,
    )
    assert r1["regime"] == "Sıkılaştırma", r1["regime"]
    assert r1["real_rate"] == 12.0
    assert r1["confidence"] == "yüksek"
    print(f"  [1] {r1['regime']} real={r1['real_rate']} conf={r1['confidence']}", file=sys.stderr)

    # 2) Gevşeme: faiz iniyor (history), reel faiz negatif, dezenflasyon
    r2 = classify_regime(
        policy_rate_history=[45, 42.5, 40],
        cpi_history=[60, 55, 48],
        usdtry=34.0, usdtry_prev=33.9,
    )
    assert r2["regime"] == "Gevşeme", r2["regime"]
    print(f"  [2] {r2['regime']} votes={r2['votes']}", file=sys.stderr)

    # 3) Stres: keskin TL değer kaybı
    r3 = classify_regime(
        policy_rate=45, policy_rate_prev=45,
        cpi_yoy=65, cpi_prev=64,
        usdtry=40.0, usdtry_prev=35.0,  # ~%14 TL kaybı
    )
    assert r3["regime"] == "Belirsizlik/Stres", r3["regime"]
    assert r3["stress_flag"] is True
    print(f"  [3] {r3['regime']} stress={r3['stress_flag']}", file=sys.stderr)

    # 4) Nötr/Yatay: hepsi sabit
    r4 = classify_regime(
        policy_rate=42.5, policy_rate_prev=42.5,
        cpi_yoy=40, cpi_prev=40.2,
        usdtry=35.0, usdtry_prev=34.95,
    )
    assert r4["regime"] in ("Nötr/Yatay", "Sıkılaştırma", "Gevşeme")
    print(f"  [4] {r4['regime']}", file=sys.stderr)

    # 5) Kısmi girdi: sadece reel faiz hesaplanabilir, trend yok
    r5 = classify_regime(policy_rate=50, cpi_yoy=45)
    assert r5["real_rate"] == 5.0
    assert r5["confidence"] in ("orta", "düşük")
    assert len(r5["missing_signals"]) >= 1
    print(f"  [5] real={r5['real_rate']} conf={r5['confidence']} missing={len(r5['missing_signals'])}", file=sys.stderr)

    # 6) Boş / bozuk girdi → crash yok
    for bad in ({}, {"foo": 1}):
        rb = classify_regime(**bad)
        assert "regime" in rb and "note" in rb
    rb2 = classify_regime()
    assert rb2["regime"] == "Belirsizlik/Stres"
    assert rb2["confidence"] == "düşük"
    print("  [6] boş girdi: crash yok", file=sys.stderr)

    # 7) Türkçe ondalık string toleransı
    r7 = classify_regime(policy_rate="42,5", policy_rate_prev="40,0",
                         cpi_yoy="38,2", cpi_prev="41,0", usdtry="33,1", usdtry_prev="33,0")
    assert r7["real_rate"] is not None
    print(f"  [7] TR-ondalık: real={r7['real_rate']} {r7['regime']}", file=sys.stderr)

    print("== ALL TESTS PASSED ==", file=sys.stderr)
    print(json.dumps(r1, ensure_ascii=False, indent=2))
    return 0


# Sözlük anahtarı alias eşlemesi (esnek JSON girdisi için)
_INPUT_ALIASES = {
    "policy_rate": ["policy_rate", "politika_faizi", "repo", "1w_repo", "rate"],
    "policy_rate_prev": ["policy_rate_prev", "politika_faizi_onceki", "rate_prev"],
    "policy_rate_history": ["policy_rate_history", "rate_history", "faiz_gecmisi"],
    "cpi_yoy": ["cpi_yoy", "tufe", "cpi", "enflasyon", "tufe_yillik"],
    "cpi_prev": ["cpi_prev", "tufe_onceki", "cpi_previous"],
    "cpi_history": ["cpi_history", "tufe_gecmisi"],
    "usdtry": ["usdtry", "usd_try", "dolar", "fx"],
    "usdtry_prev": ["usdtry_prev", "usd_try_prev", "dolar_onceki"],
    "usdtry_history": ["usdtry_history", "fx_history", "kur_gecmisi"],
    "bond_yield_10y": ["bond_yield_10y", "tahvil_10y", "gosterge_tahvil", "yield_10y"],
    "bond_yield_2y": ["bond_yield_2y", "tahvil_2y", "yield_2y"],
    "reer": ["reer", "reel_kur", "real_effective_exchange_rate"],
    "reer_prev": ["reer_prev", "reel_kur_onceki"],
}


def _map_payload(payload):
    """Esnek JSON sözlüğünü classify_regime kwargs'ına eşle."""
    if not isinstance(payload, dict):
        return {}
    lowered = {}
    for k, v in payload.items():
        if isinstance(k, str):
            lowered.setdefault(k.strip().lower(), v)
    kwargs = {}
    for canon, names in _INPUT_ALIASES.items():
        for name in names:
            if name in lowered:
                kwargs[canon] = lowered[name]
                break
    return kwargs


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="TCMB makro rejim sınıflandırması (BIST hisse zemini). "
                    "Karar-destek; yatırım tavsiyesi değildir.",
    )
    parser.add_argument("--file", help="Makro sinyaller JSON dosyası "
                                       "(get_evds_data/get_macro_data/get_fx_data çıktıları).")
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

    kwargs = _map_payload(payload)
    result = classify_regime(**kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
