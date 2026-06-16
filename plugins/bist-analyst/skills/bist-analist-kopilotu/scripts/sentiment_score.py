#!/usr/bin/env python3
"""sentiment_score.py — BIST haber metinleri için Türkçe finansal sözlük tabanlı duygu analizi.

Rol: `borsa` MCP'sinin `get_news` çıktısından (veya serbest metinden) deterministik,
ağ-bağımsız bir duygu (sentiment) skoru üretir. Sözlük tabanlı; LLM kullanmaz.

Bu çıktı KARAR-DESTEK amaçlıdır, **yatırım tavsiyesi değildir**. Duygu skoru bir
haber akışının tonunu özetler; fiyat hareketini garanti etmez.

CLI:
    python sentiment_score.py --text "Şirket rekor kâr açıkladı"
    python sentiment_score.py --file items.json          # JSON list (haber kalemleri)

İçe aktarım:
    from sentiment_score import score_text, score_items
"""

import argparse
import json
import re
import sys

# --- Türkçe finans sözlüğü -------------------------------------------------
# Her terim normalize edilmiş (diyakritiksiz, küçük harf) biçimde tutulur.
# Çok kelimeli ifadeler boşlukla; eşleşme normalize metin üzerinde yapılır.

POSITIVE_TERMS = {
    "rekor": 1.0,
    "guclu buyume": 1.0,
    "kar artisi": 1.0,
    "kar acikladi": 0.8,
    "net kar": 0.5,
    "sozlesme kazanimi": 1.0,
    "ihale kazandi": 1.0,
    "ihale": 0.6,
    "bedelsiz": 0.8,
    "temettu artisi": 1.0,
    "temettu": 0.6,
    "geri alim": 0.8,
    "tesvik": 0.7,
    "kapasite artisi": 0.8,
    "ihracat artisi": 0.9,
    "yatirim": 0.5,
    "anlasma": 0.7,
    "ruhsat": 0.7,
    "onay": 0.6,
    "buyume": 0.6,
    "kazanc": 0.6,
    "yukselis": 0.6,
    "artti": 0.5,
    "guclu": 0.5,
    "olumlu": 0.7,
    "basari": 0.6,
    "yeni urun": 0.6,
    "uretime basladi": 0.7,
    "kredi notu yukseltildi": 1.0,
}

NEGATIVE_TERMS = {
    "zarar": 1.0,
    "kuculme": 0.9,
    "dava": 0.8,
    "ceza": 0.8,
    "yaptirim": 0.9,
    "iflas": 1.0,
    "konkordato": 1.0,
    "uretim durdurma": 1.0,
    "uretimi durdurdu": 1.0,
    "deprem": 0.7,
    "yangin": 0.7,
    "hasar": 0.7,
    "bedelli": 0.6,
    "dilusyon": 0.7,
    "kredi notu indirimi": 1.0,
    "kredi notu dusuruldu": 1.0,
    "istifa": 0.7,
    "olumsuz gorus": 0.9,
    "sira kapatma": 0.8,
    "sira kapatildi": 0.8,
    "gecikme": 0.6,
    "dustu": 0.5,
    "dusus": 0.6,
    "azaldi": 0.5,
    "kayip": 0.6,
    "risk": 0.4,
    "soruşturma": 0.7,
    "sorusturma": 0.7,
    "el konuldu": 0.9,
    "tahsilat sorunu": 0.7,
}

# Olumsuzlama belirteçleri — bir terimin önünde/yakınında geçerse skoru ters çevirir.
NEGATIONS = {"degil", "yok", "olmadi", "artmadi", "olumsuz", "etmedi", "azalmadi"}

# Pekiştiriciler — yakındaki terimin ağırlığını artırır.
INTENSIFIERS = {"cok": 1.4, "ciddi": 1.4, "buyuk": 1.3, "rekor": 1.5, "guclu": 1.3,
                "onemli": 1.2, "sert": 1.4, "aşırı": 1.5, "asiri": 1.5}

NEUTRAL_THRESHOLD = 0.15
_NEGATION_WINDOW = 3  # kaç token geriye bakılacağı

# Diyakritik sadeleştirme tablosu (TR → ASCII).
_DIACRITICS = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "İ": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "Ö": "o", "Ş": "s", "Ü": "u", "â": "a", "î": "i", "û": "u",
})


def _normalize(text):
    """Metni küçük harfe indirger, diyakritikleri sadeleştirir, boşlukları toplar."""
    if not text:
        return ""
    low = str(text).lower().translate(_DIACRITICS)
    low = re.sub(r"[^\w\s]", " ", low, flags=re.UNICODE)
    return re.sub(r"\s+", " ", low).strip()


def _tokens(norm_text):
    return norm_text.split() if norm_text else []


def _negated(tokens, idx):
    """idx konumundaki terimden önce olumsuzlama var mı (pencere içinde)?"""
    start = max(0, idx - _NEGATION_WINDOW)
    return any(t in NEGATIONS for t in tokens[start:idx])


def _intensifier(tokens, idx):
    start = max(0, idx - 2)
    factor = 1.0
    for t in tokens[start:idx]:
        if t in INTENSIFIERS:
            factor = max(factor, INTENSIFIERS[t])
    return factor


def _find_term_positions(tokens, term):
    """Çok kelimeli `term`in tokenlar içindeki başlangıç indekslerini döndürür."""
    parts = term.split()
    n = len(parts)
    if n == 0:
        return []
    positions = []
    for i in range(len(tokens) - n + 1):
        if tokens[i:i + n] == parts:
            positions.append(i)
    return positions


def score_text(text):
    """Tek bir metni puanlar.

    Dönüş: {score: float [-1,1], label, positive_hits, negative_hits, n_tokens}
    """
    norm = _normalize(text)
    tokens = _tokens(norm)
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {"score": 0.0, "label": "nötr", "positive_hits": [],
                "negative_hits": [], "n_tokens": 0}

    pos_hits, neg_hits = [], []
    raw = 0.0

    for lexicon, sign, bucket in ((POSITIVE_TERMS, 1.0, pos_hits),
                                  (NEGATIVE_TERMS, -1.0, neg_hits)):
        for term, weight in lexicon.items():
            for idx in _find_term_positions(tokens, term):
                eff_sign = sign
                if _negated(tokens, idx):
                    eff_sign = -sign  # olumsuzlama tonu ters çevirir
                factor = _intensifier(tokens, idx)
                raw += eff_sign * weight * factor
                # Hit'i, etkin yönüne göre uygun listeye koy.
                target = bucket if eff_sign == sign else (neg_hits if bucket is pos_hits else pos_hits)
                target.append(term)

    # Normalizasyon: token sayısına göre yumuşatma + [-1,1] kırpma.
    denom = max(3.0, n_tokens ** 0.5 * 1.5)
    score = max(-1.0, min(1.0, raw / denom))

    if abs(score) < NEUTRAL_THRESHOLD:
        label = "nötr"
    elif score > 0:
        label = "pozitif"
    else:
        label = "negatif"

    return {
        "score": round(score, 4),
        "label": label,
        "positive_hits": sorted(set(pos_hits)),
        "negative_hits": sorted(set(neg_hits)),
        "n_tokens": n_tokens,
    }


def score_items(items, text_key="title"):
    """Haber kalemleri listesini toplulaştırır.

    Dönüş: ortalama skor, dağılım, en pozitif/en negatif kalem.
    """
    if not items or not isinstance(items, list):
        return {
            "mean_score": 0.0,
            "label": "nötr",
            "n_items": 0,
            "distribution": {"pozitif": 0, "negatif": 0, "nötr": 0},
            "most_positive": None,
            "most_negative": None,
            "per_item": [],
        }

    per_item = []
    dist = {"pozitif": 0, "negatif": 0, "nötr": 0}
    total = 0.0

    for it in items:
        if isinstance(it, dict):
            text = it.get(text_key) or it.get("title") or it.get("baslik") or ""
        else:
            text = str(it)
        res = score_text(text)
        dist[res["label"]] += 1
        total += res["score"]
        per_item.append({"text": text, "score": res["score"], "label": res["label"]})

    n = len(per_item)
    mean = total / n if n else 0.0

    if abs(mean) < NEUTRAL_THRESHOLD:
        agg_label = "nötr"
    elif mean > 0:
        agg_label = "pozitif"
    else:
        agg_label = "negatif"

    most_positive = max(per_item, key=lambda x: x["score"]) if per_item else None
    most_negative = min(per_item, key=lambda x: x["score"]) if per_item else None

    return {
        "mean_score": round(mean, 4),
        "label": agg_label,
        "n_items": n,
        "distribution": dist,
        "most_positive": most_positive,
        "most_negative": most_negative,
        "per_item": per_item,
        "disclaimer": "Karar-destek amaçlıdır; yatırım tavsiyesi değildir.",
    }


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Türkçe finansal haber duygu skoru")
    parser.add_argument("--text", help="Tek metin")
    parser.add_argument("--file", help="JSON liste dosyası (haber kalemleri)")
    parser.add_argument("--text-key", default="title", help="Kalem metin alanı (varsayılan: title)")
    args = parser.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            print(json.dumps({"error": str(e), "result": score_items([])}, ensure_ascii=False))
            return
        if isinstance(data, dict):
            data = data.get("items") or data.get("data") or data.get("result") or []
        result = score_items(data, text_key=args.text_key)
    elif args.text:
        result = score_text(args.text)
    else:
        # Argümansız: küçük yerleşik öz-test.
        example = [
            {"title": "Şirket rekor kâr açıkladı, ihale kazandı"},
            {"title": "Üretim durdurma kararı ve dava riski"},
            {"title": "Olağan genel kurul toplantısı yapıldı"},
        ]
        result = {"self_test": score_items(example)}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
