#!/usr/bin/env python3
"""kap_materiality.py — KAP (Kamuyu Aydınlatma Platformu) açıklama önemlilik sınıflandırıcısı.

Rol: `borsa` MCP'sinden gelmiş bir KAP açıklama/haber metnini taksonomiye göre
kategorize eder ve ağırlıklı bir "önemlilik (materiality)" skoru üretir. Tamamen
deterministik, ağ-bağımsız, sözlük tabanlı bir kuraldır.

Bu çıktı KARAR-DESTEK amaçlıdır, **yatırım tavsiyesi değildir**. Önemlilik skoru bir
açıklamanın fiyat/algı üzerinde potansiyel etkisini kabaca ölçer; kesin sonuç vermez.

CLI:
    python kap_materiality.py --text "Şirket geri alım programı başlattı"
    python kap_materiality.py --text "..." --size-ratio 0.4 --surprise 0.8

İçe aktarım:
    from kap_materiality import classify, materiality
"""

import argparse
import json
import re

# --- Kategori taksonomisi ---------------------------------------------------
# Her kategori: anahtar kelimeler (normalize), varsayılan tier ([0,1] öncelenmiş
# önemlilik primi) ve yönelimsel önyargı (directional_prior): +1 olumlu / -1 olumsuz / 0 nötr.

CATEGORIES = {
    "finansal_rapor": {
        "label": "Finansal Rapor / Bilanço",
        "keywords": ["finansal rapor", "bilanco", "gelir tablosu", "faaliyet sonuc",
                     "donem kari", "ceyrek", "yil sonu", "konsolide finansal"],
        "tier": 0.65, "prior": 0,
    },
    "temettu": {
        "label": "Temettü / Kâr Payı",
        "keywords": ["temettu", "kar payi", "kar dagitim", "nakit temettu"],
        "tier": 0.7, "prior": 1,
    },
    "bedelli": {
        "label": "Bedelli Sermaye Artırımı",
        "keywords": ["bedelli", "bedelli sermaye", "rüçhan", "ruchan", "yeni pay"],
        "tier": 0.6, "prior": -1,
    },
    "bedelsiz": {
        "label": "Bedelsiz Sermaye Artırımı",
        "keywords": ["bedelsiz", "ic kaynak", "bedelsiz sermaye"],
        "tier": 0.55, "prior": 1,
    },
    "geri_alim": {
        "label": "Pay Geri Alımı",
        "keywords": ["geri alim", "geri alim programi", "pay geri", "hisse geri alim"],
        "tier": 0.65, "prior": 1,
    },
    "sozlesme_ihale": {
        "label": "Sözleşme / İhale",
        "keywords": ["sozlesme", "ihale", "ihale kazan", "yeni is", "siparis",
                     "anlasma imzal", "proje aldi"],
        "tier": 0.7, "prior": 1,
    },
    "yatirim_tesvik": {
        "label": "Yatırım / Teşvik",
        "keywords": ["yatirim", "tesvik", "kapasite artis", "yeni tesis", "fabrika",
                     "yatirim tesvik belgesi"],
        "tier": 0.6, "prior": 1,
    },
    "ma_satinalma": {
        "label": "Birleşme / Satın Alma",
        "keywords": ["birlesme", "satin alma", "devralma", "hisse devri ile",
                     "iktisap", "m&a", "ortaklik kurul"],
        "tier": 0.8, "prior": 1,
    },
    "pay_devri": {
        "label": "Pay Devri / Ortaklık Yapısı",
        "keywords": ["pay devri", "ortaklik yapisi", "hisse devri", "pay sahipligi",
                     "kontrol degisik"],
        "tier": 0.65, "prior": 0,
    },
    "yonetim_degisikligi": {
        "label": "Yönetim Değişikliği",
        "keywords": ["yonetim kurulu", "genel mudur", "istifa", "atama", "gorev degisik",
                     "ceo", "cfo", "yonetim degisik"],
        "tier": 0.5, "prior": 0,
    },
    "denetim_gorusu": {
        "label": "Denetim Görüşü",
        "keywords": ["denetim gorus", "olumsuz gorus", "sartli gorus", "gorus bildirmek",
                     "bagimsiz denetim"],
        "tier": 0.75, "prior": -1,
    },
    "dava_ceza": {
        "label": "Dava / Ceza / Yaptırım",
        "keywords": ["dava", "ceza", "yaptirim", "tazminat", "icra", "el konuldu",
                     "sorusturma", "tahkim"],
        "tier": 0.7, "prior": -1,
    },
    "uretim_durdurma": {
        "label": "Üretim Durdurma / Operasyonel Kesinti",
        "keywords": ["uretim durdur", "faaliyet durdur", "uretimi durdurdu",
                     "operasyon durdur", "kapatma", "tesis kapat"],
        "tier": 0.8, "prior": -1,
    },
    "kredi_notu": {
        "label": "Kredi Notu Değişikliği",
        "keywords": ["kredi notu", "rating", "not indirim", "not yukselt",
                     "kredi derecelendirme"],
        "tier": 0.7, "prior": 0,
    },
    "yeni_urun_ruhsat": {
        "label": "Yeni Ürün / Ruhsat / Onay",
        "keywords": ["yeni urun", "ruhsat", "onay", "patent", "lisans", "izin aldi",
                     "ruhsat aldi"],
        "tier": 0.6, "prior": 1,
    },
    "faaliyet_raporu": {
        "label": "Faaliyet Raporu",
        "keywords": ["faaliyet raporu", "yillik rapor", "ara donem faaliyet"],
        "tier": 0.4, "prior": 0,
    },
    "esas_sozlesme": {
        "label": "Esas Sözleşme Değişikliği",
        "keywords": ["esas sozlesme", "ana sozlesme", "tadil", "sozlesme degisik"],
        "tier": 0.45, "prior": 0,
    },
    "sira_durdurma": {
        "label": "Sıra Kapatma / İşlem Durdurma",
        "keywords": ["sira kapatma", "sira kapat", "islem durdurma", "tedbirli pazar",
                     "islem gormekten men"],
        "tier": 0.7, "prior": -1,
    },
    "icsel_bilgi_erteleme": {
        "label": "İçsel Bilginin Ertelenmesi",
        "keywords": ["icsel bilgi", "erteleme", "bilginin ertelen", "icsel bilginin"],
        "tier": 0.6, "prior": 0,
    },
    "diger": {
        "label": "Diğer / Sınıflandırılamayan",
        "keywords": [],
        "tier": 0.35, "prior": 0,
    },
}

# Önemlilik ağırlıkları (toplam 1.0).
WEIGHTS = {
    "size_ratio": 0.30,
    "surprise": 0.25,
    "persistence": 0.20,
    "cashflow": 0.15,
    "governance": 0.10,
}

HIGH_BAND = 67
LOW_BAND = 33

_DIACRITICS = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "İ": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "Ö": "o", "Ş": "s", "Ü": "u", "â": "a", "î": "i", "û": "u",
})


def _normalize(text):
    if not text:
        return ""
    low = str(text).lower().translate(_DIACRITICS)
    low = re.sub(r"\s+", " ", low)
    return low.strip()


def classify(text):
    """Metni KAP taksonomisine göre sınıflandırır.

    Dönüş: {category_id, category_label, matched_keywords}
    En çok anahtar kelime eşleşen kategori seçilir; eşitlikte tier yüksek olan kazanır.
    """
    norm = _normalize(text)
    if not norm:
        return {"category_id": "diger", "category_label": CATEGORIES["diger"]["label"],
                "matched_keywords": []}

    best_id = "diger"
    best_hits = []
    best_score = (0, 0.0)  # (eşleşme sayısı, tier)

    for cid, spec in CATEGORIES.items():
        if cid == "diger":
            continue
        hits = [kw for kw in spec["keywords"] if kw in norm]
        if not hits:
            continue
        score = (len(hits), spec["tier"])
        if score > best_score:
            best_score = score
            best_id = cid
            best_hits = hits

    return {
        "category_id": best_id,
        "category_label": CATEGORIES[best_id]["label"],
        "matched_keywords": best_hits,
    }


def _clamp01(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, v))


def materiality(text, size_ratio=None, surprise=None, persistence=None,
                cashflow=None, governance=None):
    """Ağırlıklı 0–100 önemlilik skoru hesaplar.

    Faktörler [0,1]; None verilirse kategoriye-primli varsayılan kullanılır
    (kademeli bozulma). Hiçbiri verilmezse nötr 50 döner.
    Bant: Yüksek ≥67, Orta 34–66, Düşük ≤33.
    """
    cls = classify(text)
    cid = cls["category_id"]
    spec = CATEGORIES.get(cid, CATEGORIES["diger"])
    primed = spec["tier"]  # kategoriye özgü varsayılan faktör değeri [0,1]

    raw_inputs = {
        "size_ratio": size_ratio,
        "surprise": surprise,
        "persistence": persistence,
        "cashflow": cashflow,
        "governance": governance,
    }

    # Hiçbir faktör verilmemişse: nötr 50.
    provided = {k: _clamp01(v) for k, v in raw_inputs.items()}
    any_provided = any(v is not None for v in provided.values())

    factor_values = {}
    used_defaults = []
    for k in WEIGHTS:
        v = provided[k]
        if v is None:
            v = primed
            used_defaults.append(k)
        factor_values[k] = round(v, 4)

    if not any_provided:
        score = 50.0
        note = ("Hiçbir nicel faktör verilmedi; nötr 50 döndürüldü. "
                "Kategori önyargısı yalnızca yön (directional_prior) için kullanıldı.")
    else:
        weighted = sum(WEIGHTS[k] * factor_values[k] for k in WEIGHTS)
        score = round(weighted * 100.0, 2)
        if used_defaults:
            note = ("Eksik faktörler kategori-primli varsayılanla dolduruldu: "
                    + ", ".join(used_defaults) + ".")
        else:
            note = "Tüm faktörler sağlandı."

    if score >= HIGH_BAND:
        tier = "Yüksek"
    elif score <= LOW_BAND:
        tier = "Düşük"
    else:
        tier = "Orta"

    return {
        "score": score,
        "tier": tier,
        "category_id": cid,
        "category_label": cls["category_label"],
        "directional_prior": spec["prior"],
        "matched_keywords": cls["matched_keywords"],
        "factor_values": factor_values,
        "weights": WEIGHTS,
        "note": note,
        "disclaimer": "Karar-destek amaçlıdır; yatırım tavsiyesi değildir.",
    }


def _main(argv=None):
    parser = argparse.ArgumentParser(description="KAP açıklama önemlilik sınıflandırıcısı")
    parser.add_argument("--text", help="KAP açıklama metni")
    parser.add_argument("--size-ratio", type=float, default=None, help="Büyüklük oranı [0,1]")
    parser.add_argument("--surprise", type=float, default=None, help="Sürpriz [0,1]")
    parser.add_argument("--persistence", type=float, default=None, help="Kalıcılık [0,1]")
    parser.add_argument("--cashflow", type=float, default=None, help="Nakit akışı etkisi [0,1]")
    parser.add_argument("--governance", type=float, default=None, help="Kurumsal yönetim [0,1]")
    args = parser.parse_args(argv)

    if args.text:
        result = materiality(
            args.text,
            size_ratio=args.size_ratio,
            surprise=args.surprise,
            persistence=args.persistence,
            cashflow=args.cashflow,
            governance=args.governance,
        )
    else:
        # Argümansız: küçük yerleşik öz-test.
        result = {"self_test": [
            materiality("Şirket pay geri alım programı başlattı", size_ratio=0.4, surprise=0.7),
            classify("Bağımsız denetim olumsuz görüş bildirdi"),
            materiality("Olağan genel kurul toplantısı yapıldı"),
        ]}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
