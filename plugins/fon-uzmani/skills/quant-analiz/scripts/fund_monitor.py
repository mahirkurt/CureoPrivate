#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fund_monitor.py — Makro rejim etiketi + izleme listesi değişim/alarm motoru.

(1) regime_tag: EVDS makro sinyallerinden (faiz yönü, enflasyon, kur) Risk-Açık/Nötr/
Risk-Kapalı rejimi + fon kategorisi duyarlılığı. (2) change_points: iki izleme snapshot'ı
arasındaki fon-bazlı değişimler (drawdown eşiği, vol sıçraması, sıra kayması, stil
sapması, KAP duyurusu) — bist-analyst watchlist_diff desenini fona uyarlar. (3)
alert_composite: çok-sinyalli ağırlıklı "izleme duruşu" (confluence mantığı).

Girdi (mode'a göre): {macro?, category?, prev?, curr?, thresholds?}.
Konvansiyon: saf stdlib; karar-destek; çökmez. Kendi-kendine yeter (cross-plugin import yok).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fund_math as fm  # noqa: E402

DISCLAIMER = fm.DISCLAIMER

# kategori → rejim duyarlılığı (kaba; karar-destek bağlamı)
_CATEGORY_SENSITIVITY = {
    "hisse": {"risk_on": "rüzgar arkadan (tailwind)", "risk_off": "rüzgar önden (headwind)"},
    "borçlanma": {"risk_on": "nötr/hafif önden", "risk_off": "faiz inişinde arkadan"},
    "para piyasası": {"risk_on": "düşük duyarlılık", "risk_off": "savunmacı sığınak"},
    "kıymetli maden": {"risk_on": "değişken", "risk_off": "sığınak talebi"},
    "değişken": {"risk_on": "tahsise bağlı", "risk_off": "tahsise bağlı"},
    "karma": {"risk_on": "tahsise bağlı", "risk_off": "tahsise bağlı"},
}


def regime_tag(macro, category=None):
    """macro: {rate_change_bps?, inflation_yoy?, fx_change_pct?, policy_rate?}."""
    if not isinstance(macro, dict):
        return {"regime": "Belirsizlik", "note": "makro sinyal verilmedi"}
    score = 0
    drivers = []
    rc = fm.to_float(macro.get("rate_change_bps"))
    if rc is not None:
        if rc <= -25:
            score += 1
            drivers.append("faiz indirimi (gevşeme)")
        elif rc >= 25:
            score -= 1
            drivers.append("faiz artışı (sıkılaştırma)")
    infl = fm.to_float(macro.get("inflation_yoy"))
    if infl is not None:
        if infl > 50:
            score -= 1
            drivers.append("yüksek enflasyon")
        elif infl < 25:
            score += 1
            drivers.append("ılımlı enflasyon")
    fx = fm.to_float(macro.get("fx_change_pct"))
    if fx is not None and fx > 5:
        score -= 1
        drivers.append("kur baskısı")
    regime = "Risk-Açık" if score >= 1 else ("Risk-Kapalı" if score <= -1 else "Nötr")
    sens = None
    if category:
        cl = category.lower()
        for k, v in _CATEGORY_SENSITIVITY.items():
            if k in cl:
                sens = v["risk_on"] if regime == "Risk-Açık" else (v["risk_off"] if regime == "Risk-Kapalı" else "nötr")
                break
    return {"regime": regime, "score": score, "drivers": drivers,
            "category_sensitivity": sens, "disclaimer": DISCLAIMER}


def _index(snapshot):
    """snapshot {funds:[{fund_id,...}]} → {fund_id: fund}."""
    out = {}
    for f in (snapshot or {}).get("funds", []) if isinstance(snapshot, dict) else []:
        fid = f.get("fund_id") or f.get("code")
        if fid:
            out[str(fid)] = f
    return out


_PRIORITY = {"drawdown_esigi": 4, "stil_sapmasi": 3, "rejim_degisimi": 3,
             "vol_sicramasi": 2, "sira_kaymasi": 2, "ter_artisi": 1, "kap_duyurusu": 2,
             "yeni_eklendi": 1}


# Tek-tip delta dedektörleri: her biri (oq, nq, old, cur, th) → change|None.
# Bağımsız ve düşük-karmaşıklıklı; change_points üzerlerinde döner (CC düşük tutulur).
def _delta_drawdown(oq, nq, old, cur, th):
    """maxDD eşiği aşıldı mı?"""
    mdd = fm.to_float(nq.get("max_drawdown"))
    if mdd is not None and mdd <= th["mdd_breach"]:
        return {"type": "drawdown_esigi", "detail": f"maxDD {mdd} ≤ eşik {th['mdd_breach']}"}
    return None


def _delta_vol(oq, nq, old, cur, th):
    """Volatilite, eski değerin vol_spike_k katına sıçradı mı?"""
    ov, nv = fm.to_float(oq.get("volatility")), fm.to_float(nq.get("volatility"))
    if ov and nv and nv >= ov * th["vol_spike_k"]:
        return {"type": "vol_sicramasi", "detail": f"vol {ov}→{nv} (×{round(nv / ov, 2)})"}
    return None


def _delta_style(oq, nq, old, cur, th):
    """Stil/holdings parmak izi ≥0.10 kaydı mı (stil sapması)?"""
    osd, nsd = old.get("style_fingerprint"), cur.get("style_fingerprint")
    if isinstance(osd, dict) and isinstance(nsd, dict):
        keys = set(osd) | set(nsd)
        mag = 0.5 * sum(abs((fm.to_float(nsd.get(k, 0)) or 0) - (fm.to_float(osd.get(k, 0)) or 0)) for k in keys)
        if mag >= 0.10:
            return {"type": "stil_sapmasi", "detail": f"stil drift {round(mag, 3)}"}
    return None


def _delta_ter(oq, nq, old, cur, th):
    """TER (gider oranı) arttı mı?"""
    ort, nrt = fm.to_float(old.get("ter")), fm.to_float(cur.get("ter"))
    if ort and nrt and nrt > ort:
        return {"type": "ter_artisi", "detail": f"TER {ort}→{nrt}"}
    return None


def _delta_regime(oq, nq, old, cur, th):
    """Makro rejim etiketi değişti mi?"""
    org, nrg = old.get("regime_tag"), cur.get("regime_tag")
    if org and nrg and org != nrg:
        return {"type": "rejim_degisimi", "detail": f"{org}→{nrg}"}
    return None


_DELTA_DETECTORS = (_delta_drawdown, _delta_vol, _delta_style, _delta_ter, _delta_regime)


def _fund_changes(old, cur, th):
    """Tek fonun eski→yeni snapshot deltalarını (alarm listesi) döndürür."""
    if old is None:
        changes = [{"type": "yeni_eklendi", "detail": "izleme listesine yeni eklendi"}]
    else:
        oq = old.get("quant_snapshot", {}) or {}
        nq = cur.get("quant_snapshot", {}) or {}
        changes = [ch for det in _DELTA_DETECTORS if (ch := det(oq, nq, old, cur, th))]
    for k in cur.get("open_kap", []) or []:
        changes.append({"type": "kap_duyurusu", "detail": k.get("title", "duyuru")})
    return changes


def change_points(prev, curr, thresholds=None):
    """İki izleme snapshot'ını karşılaştırır; fon-bazlı öncelikli değişim raporu döndürür."""
    th = {"mdd_breach": -0.20, "vol_spike_k": 1.5, "rank_drop": 1, **(thresholds or {})}
    p, c = _index(prev), _index(curr)
    items = []
    for fid, cur in c.items():
        changes = _fund_changes(p.get(fid), cur, th)
        if changes:
            priority = max(_PRIORITY.get(ch["type"], 1) for ch in changes)
            items.append({"fund_id": fid, "priority": priority, "changes": changes})
    items.sort(key=lambda x: x["priority"], reverse=True)
    removed = [fid for fid in p if fid not in c]
    return {"items": items, "removed": removed,
            "summary": f"{len(items)} fonda değişiklik, {len(removed)} çıkarıldı",
            "disclaimer": DISCLAIMER}


def alert_composite(signals):
    """signals: [{type, severity?}] → ağırlıklı izleme duruşu."""
    if not signals:
        return {"posture": "sakin", "weighted_score": 0, "disclaimer": DISCLAIMER}
    sev_w = {"Yüksek": 3, "Orta": 2, "Düşük": 1, None: 1}
    score = sum(_PRIORITY.get(s.get("type"), 1) * sev_w.get(s.get("severity"), 1) for s in signals)
    posture = "yüksek dikkat" if score >= 8 else ("izlemede" if score >= 3 else "sakin")
    return {"posture": posture, "weighted_score": score, "signal_count": len(signals),
            "disclaimer": DISCLAIMER}


def analyze(payload):
    if not isinstance(payload, dict):
        return {"error": "geçersiz girdi", "disclaimer": DISCLAIMER}
    out = {"disclaimer": DISCLAIMER}
    if payload.get("macro") is not None:
        out["regime"] = regime_tag(payload["macro"], payload.get("category"))
    if payload.get("prev") is not None or payload.get("curr") is not None:
        out["change_report"] = change_points(payload.get("prev"), payload.get("curr"), payload.get("thresholds"))
        # change'lerden alarm kompoziti türet
        sigs = []
        for it in out["change_report"]["items"]:
            for ch in it["changes"]:
                sigs.append({"type": ch["type"]})
        out["alert"] = alert_composite(sigs)
    if "regime" not in out and "change_report" not in out:
        out["error"] = "macro veya prev/curr snapshot gerekli"
    return out


def _run_selftest():
    reg = regime_tag({"rate_change_bps": -50, "inflation_yoy": 30, "fx_change_pct": 1}, "Hisse Senedi Fonu")
    assert reg["regime"] == "Risk-Açık", reg["regime"]
    prev = {"funds": [{"fund_id": "AFA", "ter": 0.02, "quant_snapshot": {"volatility": 0.20, "max_drawdown": -0.10}}]}
    curr = {"funds": [
        {"fund_id": "AFA", "ter": 0.025, "quant_snapshot": {"volatility": 0.35, "max_drawdown": -0.25}},
        {"fund_id": "TI2", "quant_snapshot": {"volatility": 0.18}},
    ]}
    cp = change_points(prev, curr)
    afa = next(i for i in cp["items"] if i["fund_id"] == "AFA")
    types = {ch["type"] for ch in afa["changes"]}
    assert "drawdown_esigi" in types and "vol_sicramasi" in types and "ter_artisi" in types, types
    res = analyze({"macro": {"rate_change_bps": 100, "inflation_yoy": 60}, "prev": prev, "curr": curr})
    assert res["regime"]["regime"] == "Risk-Kapalı"
    assert res["alert"]["posture"] in {"sakin", "izlemede", "yüksek dikkat"}
    print("== fund_monitor: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "fund_monitor", "regime": reg["regime"],
            "alert": res["alert"]["posture"], "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rejim + izleme değişim/alarm (karar-destek).")
    ap.add_argument("--file", help="{macro?, category?, prev?, curr?, thresholds?} JSON")
    ap.add_argument("--indent", type=int, default=2)
    args = ap.parse_args(argv)
    if not args.file:
        print(json.dumps(_run_selftest(), ensure_ascii=False, indent=args.indent))
        return 0
    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"Girdi okunamadı: {exc}", "disclaimer": DISCLAIMER}, ensure_ascii=False))
        return 1
    print(json.dumps(analyze(data), ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
