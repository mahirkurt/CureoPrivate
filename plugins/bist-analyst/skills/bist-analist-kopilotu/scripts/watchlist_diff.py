#!/usr/bin/env python3
"""watchlist_diff.py — İzleme listesi (Mod 4) durum farkı üretici.

İki izleme listesi anlık görüntüsü (watchlist-state-schema.json uyumlu)
arasında deterministik fark hesaplar. Sembol bazında fiyat, teknik duruş,
RSI, MACD histogramı, kritik seviyeler ve açık KAP bildirimlerini karşılaştırır;
her değişikliği sınıflandırır ve materyaliteye göre öncelik puanı verir.

Kütüphane: diff(prev, curr) -> dict
CLI: --prev a.json --curr b.json   (argümansız: yerleşik öz-test)

Hiçbir koşulda çökmemelidir.
"""
from __future__ import annotations

import argparse
import json
import sys

# Teknik duruş sıralaması (yön çevrimi tespiti için ordinal).
_POSTURE_ORDER = {
    "Güçlü Aşağı": -2,
    "Zayıf Aşağı": -1,
    "Nötr": 0,
    "Zayıf Yukarı": 1,
    "Güçlü Yukarı": 2,
}

# Materyalite katmanı puanı (yüksek = daha öncelikli).
_MATERIALITY_SCORE = {
    "yuksek": 3, "high": 3,
    "orta": 2, "medium": 2,
    "dusuk": 1, "low": 1,
}

# Değişiklik türü -> taban öncelik puanı.
_CHANGE_PRIORITY = {
    "seviye kırıldı": 5,
    "teknik duruş değişti": 4,
    "yeni KAP": 4,
    "RSI bölge değişti": 3,
    "yeni eklenen": 2,
    "çıkarıldı": 2,
    "değişiklik yok": 0,
}


def _materiality_value(tier) -> int:
    if tier is None:
        return 1
    key = str(tier).strip().lower()
    # Türkçe diakritikleri sadeleştir
    key = (key.replace("ü", "u").replace("ı", "i").replace("ş", "s")
           .replace("ö", "o").replace("ç", "c").replace("ğ", "g"))
    return _MATERIALITY_SCORE.get(key, 1)


def _posture_value(posture):
    if posture is None:
        return None
    return _POSTURE_ORDER.get(str(posture).strip())


def _rsi_zone(rsi) -> str | None:
    """RSI değerini bölgeye ayırır: aşırı satım / nötr / aşırı alım."""
    if rsi is None:
        return None
    try:
        v = float(rsi)
    except (TypeError, ValueError):
        return None
    if v < 30:
        return "aşırı satım"
    if v > 70:
        return "aşırı alım"
    return "nötr"


def _as_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _kap_keys(open_kap) -> set:
    """KAP bildirimlerini (date, title) anahtar kümesine indirger."""
    keys = set()
    if not isinstance(open_kap, list):
        return keys
    for item in open_kap:
        if isinstance(item, dict):
            keys.add((str(item.get("date", "")), str(item.get("title", ""))))
    return keys


def _level_set(levels) -> set:
    """key_levels.support / resistance listesini float kümesine indirger."""
    out = set()
    if not isinstance(levels, list):
        return out
    for lv in levels:
        f = _as_float(lv)
        if f is not None:
            out.add(round(f, 4))
    return out


def _index_symbols(snapshot) -> dict:
    """Anlık görüntüden {symbol: record} sözlüğü çıkarır."""
    out = {}
    if not isinstance(snapshot, dict):
        return out
    syms = snapshot.get("symbols")
    if not isinstance(syms, list):
        return out
    for rec in syms:
        if isinstance(rec, dict) and rec.get("symbol"):
            out[str(rec["symbol"]).upper()] = rec
    return out


def _new_high_materiality_kap(prev_kap_keys: set, curr_rec: dict) -> bool:
    """Önceki görüntüde olmayan, yüksek materyaliteli yeni KAP var mı?"""
    curr_list = curr_rec.get("open_kap") if isinstance(curr_rec, dict) else None
    if not isinstance(curr_list, list):
        return False
    for item in curr_list:
        if not isinstance(item, dict):
            continue
        key = (str(item.get("date", "")), str(item.get("title", "")))
        if key not in prev_kap_keys and _materiality_value(
            item.get("materiality_tier")
        ) >= 3:
            return True
    return False


def _compare_symbol(symbol: str, prev: dict | None, curr: dict | None) -> dict:
    """Tek sembol için değişiklik listesi ve öncelik puanı üretir."""
    changes: list[dict] = []
    priority = 0

    # Yeni eklenen / çıkarılan
    if prev is None and curr is not None:
        changes.append({"type": "yeni eklenen", "detail": "Sembol listeye eklendi."})
        priority = max(priority, _CHANGE_PRIORITY["yeni eklenen"])
        # Eklenirken yüksek materyaliteli KAP varsa öne çıkar
        if _new_high_materiality_kap(set(), curr):
            changes.append({"type": "yeni KAP", "detail": "Yüksek materyaliteli açık KAP."})
            priority = max(priority, _CHANGE_PRIORITY["yeni KAP"])
        return {"symbol": symbol, "priority": priority, "changes": changes}

    if prev is not None and curr is None:
        changes.append({"type": "çıkarıldı", "detail": "Sembol listeden çıkarıldı."})
        return {
            "symbol": symbol,
            "priority": _CHANGE_PRIORITY["çıkarıldı"],
            "changes": changes,
        }

    # Her ikisi de mevcut: alan alan karşılaştır.
    prev = prev or {}
    curr = curr or {}

    # Teknik duruş çevrimi
    pv = _posture_value(prev.get("technical_posture"))
    cv = _posture_value(curr.get("technical_posture"))
    if pv is not None and cv is not None and pv != cv:
        crossed_zero = (pv > 0 and cv < 0) or (pv < 0 and cv > 0)
        changes.append({
            "type": "teknik duruş değişti",
            "detail": f"{prev.get('technical_posture')} -> "
                      f"{curr.get('technical_posture')}",
            "yon_cevrimi": crossed_zero,
        })
        base = _CHANGE_PRIORITY["teknik duruş değişti"]
        priority = max(priority, base + (1 if crossed_zero else 0))

    # Seviye kırılması: önceki destek/direnç seti ile fiyat hareketi
    prev_close = _as_float(prev.get("last_close"))
    curr_close = _as_float(curr.get("last_close"))
    prev_levels = prev.get("key_levels") or {}
    prev_support = _level_set(prev_levels.get("support"))
    prev_resistance = _level_set(prev_levels.get("resistance"))
    if curr_close is not None and prev_close is not None:
        broken = []
        for r in sorted(prev_resistance):
            if prev_close <= r < curr_close:
                broken.append(f"direnç {r} yukarı kırıldı")
        for s in sorted(prev_support, reverse=True):
            if curr_close < s <= prev_close:
                broken.append(f"destek {s} aşağı kırıldı")
        if broken:
            changes.append({
                "type": "seviye kırıldı",
                "detail": "; ".join(broken),
            })
            priority = max(priority, _CHANGE_PRIORITY["seviye kırıldı"])

    # RSI bölge değişimi
    pz = _rsi_zone(prev.get("rsi"))
    cz = _rsi_zone(curr.get("rsi"))
    if pz is not None and cz is not None and pz != cz:
        changes.append({
            "type": "RSI bölge değişti",
            "detail": f"{pz} -> {cz}",
        })
        priority = max(priority, _CHANGE_PRIORITY["RSI bölge değişti"])

    # MACD histogram işaret değişimi (bilgi amaçlı; teknik duruşa katkı)
    ph = _as_float(prev.get("macd_hist"))
    ch = _as_float(curr.get("macd_hist"))
    if ph is not None and ch is not None and (ph >= 0) != (ch >= 0):
        changes.append({
            "type": "teknik duruş değişti",
            "detail": f"MACD histogram işaret değişti ({ph} -> {ch})",
            "yon_cevrimi": True,
        })
        priority = max(priority, _CHANGE_PRIORITY["teknik duruş değişti"])

    # Yeni KAP bildirimleri
    prev_kap = _kap_keys(prev.get("open_kap"))
    curr_kap = _kap_keys(curr.get("open_kap"))
    new_kap = curr_kap - prev_kap
    if new_kap:
        hi = _new_high_materiality_kap(prev_kap, curr)
        changes.append({
            "type": "yeni KAP",
            "detail": f"{len(new_kap)} yeni bildirim",
            "yuksek_materyalite": hi,
        })
        base = _CHANGE_PRIORITY["yeni KAP"]
        priority = max(priority, base + (1 if hi else 0))

    if not changes:
        changes.append({"type": "değişiklik yok", "detail": ""})
        priority = _CHANGE_PRIORITY["değişiklik yok"]

    return {"symbol": symbol, "priority": priority, "changes": changes}


def diff(prev: dict, curr: dict) -> dict:
    """İki izleme listesi anlık görüntüsünü karşılaştırır.

    Döner: {generated_basis, items:[{symbol, priority, changes}], summary}
    Asla istisna fırlatmaz.
    """
    if not isinstance(prev, dict):
        prev = {}
    if not isinstance(curr, dict):
        curr = {}

    prev_idx = _index_symbols(prev)
    curr_idx = _index_symbols(curr)
    all_symbols = sorted(set(prev_idx) | set(curr_idx))

    items: list[dict] = []
    for sym in all_symbols:
        items.append(_compare_symbol(sym, prev_idx.get(sym), curr_idx.get(sym)))

    # Öncelik (yüksekten düşüğe), eşitlikte sembol adına göre sırala.
    items.sort(key=lambda x: (-x["priority"], x["symbol"]))

    # Özet
    counts: dict[str, int] = {}
    high_priority: list[str] = []
    for it in items:
        for ch in it["changes"]:
            counts[ch["type"]] = counts.get(ch["type"], 0) + 1
        if it["priority"] >= 4:
            high_priority.append(it["symbol"])

    summary = {
        "total_symbols": len(all_symbols),
        "changed_symbols": sum(
            1 for it in items
            if not (len(it["changes"]) == 1
                    and it["changes"][0]["type"] == "değişiklik yok")
        ),
        "high_priority_symbols": high_priority,
        "change_counts": counts,
    }

    generated_basis = (
        f"prev={prev.get('generated_at', 'bilinmiyor')} -> "
        f"curr={curr.get('generated_at', 'bilinmiyor')}"
    )

    return {
        "generated_basis": generated_basis,
        "items": items,
        "summary": summary,
    }


# --------------------------------------------------------------------------- #
# Yerleşik öz-test anlık görüntüleri
# --------------------------------------------------------------------------- #

_SNAP_PREV = {
    "generated_at": "2026-06-12T18:30:00+03:00",
    "symbols": [
        {
            "symbol": "GARAN", "last_close": 122.0, "as_of": "2026-06-12",
            "technical_posture": "Zayıf Yukarı", "rsi": 58.0, "macd_hist": 0.4,
            "key_levels": {"support": [118.0], "resistance": [126.0]},
            "open_kap": [], "notes": "",
        },
        {
            "symbol": "THYAO", "last_close": 305.0, "as_of": "2026-06-12",
            "technical_posture": "Nötr", "rsi": 72.0, "macd_hist": 0.1,
            "key_levels": {"support": [290.0], "resistance": [320.0]},
            "open_kap": [], "notes": "",
        },
        {
            "symbol": "EREGL", "last_close": 45.0, "as_of": "2026-06-12",
            "technical_posture": "Zayıf Aşağı", "rsi": 41.0, "macd_hist": -0.2,
            "key_levels": {"support": [43.0], "resistance": [48.0]},
            "open_kap": [], "notes": "",
        },
    ],
}

_SNAP_CURR = {
    "generated_at": "2026-06-13T18:30:00+03:00",
    "symbols": [
        {
            # Direnç yukarı kırıldı + duruş güçlendi
            "symbol": "GARAN", "last_close": 127.5, "as_of": "2026-06-13",
            "technical_posture": "Güçlü Yukarı", "rsi": 64.0, "macd_hist": 0.9,
            "key_levels": {"support": [124.0], "resistance": [132.0]},
            "open_kap": [], "notes": "",
        },
        {
            # RSI aşırı alımdan nötre döndü + yüksek materyaliteli KAP
            "symbol": "THYAO", "last_close": 308.0, "as_of": "2026-06-13",
            "technical_posture": "Nötr", "rsi": 66.0, "macd_hist": 0.0,
            "key_levels": {"support": [295.0], "resistance": [320.0]},
            "open_kap": [
                {"date": "2026-06-13", "title": "Pay geri alım programı",
                 "materiality_tier": "yüksek"}
            ],
            "notes": "",
        },
        # EREGL çıkarıldı; AKBNK yeni eklendi
        {
            "symbol": "AKBNK", "last_close": 62.0, "as_of": "2026-06-13",
            "technical_posture": "Zayıf Yukarı", "rsi": 55.0, "macd_hist": 0.2,
            "key_levels": {"support": [58.0], "resistance": [66.0]},
            "open_kap": [], "notes": "",
        },
    ],
}


def _self_test() -> int:
    result = diff(_SNAP_PREV, _SNAP_CURR)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Beklenen: en az bir seviye kırıldı + yeni eklenen + çıkarıldı tespiti.
    types_seen = {ch["type"] for it in result["items"] for ch in it["changes"]}
    ok = {"seviye kırıldı", "yeni eklenen", "çıkarıldı"}.issubset(types_seen)
    return 0 if ok else 1


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="İzleme listesi (Mod 4) durum farkı üretici."
    )
    parser.add_argument("--prev", help="Önceki anlık görüntü JSON dosyası.")
    parser.add_argument("--curr", help="Güncel anlık görüntü JSON dosyası.")
    args = parser.parse_args(argv)

    if not args.prev or not args.curr:
        return _self_test()

    try:
        prev = _load_json(args.prev)
        curr = _load_json(args.curr)
    except Exception as exc:
        print(json.dumps(
            {"generated_basis": "hata", "items": [],
             "summary": {"error": f"Dosya okunamadı/ayrıştırılamadı: {exc}"}},
            ensure_ascii=False, indent=2,
        ))
        return 1

    result = diff(prev, curr)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps(
            {"generated_basis": "hata", "items": [],
             "summary": {"error": f"Beklenmeyen hata: {exc}"}},
            ensure_ascii=False,
        ))
        sys.exit(1)
