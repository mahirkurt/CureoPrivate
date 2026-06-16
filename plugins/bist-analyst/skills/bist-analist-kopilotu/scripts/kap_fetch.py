#!/usr/bin/env python3
"""kap_fetch.py — `borsa` MCP `get_news` ham çıktısını temiz açıklama kalemlerine normalize eder.

Rol: `get_news` (ve benzeri KAP/haber kaynakları) farklı şekillerde dönebilir
(düz liste, {items:[...]}, {data:[...]}, {result:[...]}). Bu modül hepsini tek tip
{date, title, summary, source, url, is_kap} kalemlerine indirger, en yeniden eskiye
sıralar ve eksik alanlara dayanıklıdır. Ağ çağrısı yapmaz; yalnızca son-işleme.

Bu çıktı KARAR-DESTEK amaçlıdır, **yatırım tavsiyesi değildir**.

CLI:
    python kap_fetch.py --file raw.json
    python kap_fetch.py --file raw.json --days 7

İçe aktarım:
    from kap_fetch import normalize, recent
"""

import argparse
import json
import re
import sys
from datetime import datetime, date

# Olası alan adı eşlemeleri (öncelik sırasıyla).
_TITLE_KEYS = ("title", "baslik", "header", "konu", "subject", "headline")
_DATE_KEYS = ("date", "tarih", "datetime", "published", "publishDate", "yayinTarihi", "time")
_SUMMARY_KEYS = ("summary", "ozet", "content", "icerik", "description", "aciklama", "body")
_SOURCE_KEYS = ("source", "kaynak", "provider", "publisher")
_URL_KEYS = ("url", "link", "href", "permalink")

# Yaygın tarih formatları.
_DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d.%m.%Y %H:%M",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
)


def _first(d, keys):
    """Sözlükte verilen anahtarlardan ilk dolu olanın değerini döndürür."""
    if not isinstance(d, dict):
        return None
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def _parse_date(value):
    """Çeşitli formatları dener; ISO 'YYYY-MM-DD' string döndürür ya da None."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        # Epoch saniye/milisaniye tahmini.
        try:
            ts = float(value)
            if ts > 1e12:  # milisaniye
                ts /= 1000.0
            return datetime.utcfromtimestamp(ts).date().isoformat()
        except (ValueError, OverflowError, OSError):
            return None
    s = str(value).strip()
    # ISO içinden sadece tarih kısmını ayıkla (zaman dilimi vb. için).
    iso_match = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    if iso_match:
        try:
            return datetime.strptime(iso_match.group(1), "%Y-%m-%d").date().isoformat()
        except ValueError:
            return None
    return None


def _looks_kap(item, source, title, summary):
    """Kalemin bir KAP açıklaması olup olmadığını sezgisel olarak belirler."""
    if isinstance(item, dict):
        for flag_key in ("is_kap", "isKap", "kap"):
            if isinstance(item.get(flag_key), bool):
                return item[flag_key]
    blob = " ".join(str(x).lower() for x in (source, title, summary) if x)
    return "kap" in blob or "kamuyu aydinlat" in blob or "kamuyu aydınlat" in blob


def _coerce_items(raw):
    """Çeşitli kapsayıcı şekilleri düz bir kalem listesine indirger."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("items", "data", "result", "results", "news", "haberler", "rows"):
            val = raw.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                # Bir kademe daha iç içe olabilir.
                nested = _coerce_items(val)
                if nested:
                    return nested
        # Tek bir kalem sözlüğü olabilir.
        if any(k in raw for k in (_TITLE_KEYS + _DATE_KEYS)):
            return [raw]
    return []


def normalize(raw):
    """Ham `get_news` çıktısını tek tip kalem listesine çevirir (en yeniden eskiye).

    Her kalem: {date, title, summary, source, url, is_kap}
    """
    items = _coerce_items(raw)
    out = []
    for it in items:
        if isinstance(it, dict):
            title = _first(it, _TITLE_KEYS)
            raw_date = _first(it, _DATE_KEYS)
            summary = _first(it, _SUMMARY_KEYS)
            source = _first(it, _SOURCE_KEYS)
            url = _first(it, _URL_KEYS)
        else:
            title = str(it)
            raw_date = summary = source = url = None

        parsed = _parse_date(raw_date)
        norm = {
            "date": parsed,
            "raw_date": str(raw_date) if raw_date not in (None, "") else None,
            "title": (str(title).strip() if title not in (None, "") else None),
            "summary": (str(summary).strip() if summary not in (None, "") else None),
            "source": (str(source).strip() if source not in (None, "") else None),
            "url": (str(url).strip() if url not in (None, "") else None),
            "is_kap": _looks_kap(it, source, title, summary),
        }
        out.append(norm)

    # En yeniden eskiye sırala; tarihi parse edilemeyenler sona.
    out.sort(key=lambda x: (x["date"] is not None, x["date"] or ""), reverse=True)
    return out


def recent(items, days=7, today=None):
    """Son N güne ait kalemleri filtreler.

    `today` enjekte edilebilir (test için). String 'YYYY-MM-DD' ya da date kabul eder.
    Parse edilemeyen tarihli kalemler korunur ama `date_unparsed=True` ile işaretlenir.
    """
    if not items:
        return []
    if today is None:
        today = date.today()
    elif isinstance(today, str):
        try:
            today = datetime.strptime(today[:10], "%Y-%m-%d").date()
        except ValueError:
            today = date.today()
    elif isinstance(today, datetime):
        today = today.date()

    try:
        days = int(days)
    except (TypeError, ValueError):
        days = 7
    if days < 0:
        days = 0

    result = []
    for it in items:
        d = it.get("date")
        if not d:
            # Tarihi belirsiz; koru ama işaretle.
            flagged = dict(it)
            flagged["date_unparsed"] = True
            result.append(flagged)
            continue
        try:
            dval = datetime.strptime(d, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            flagged = dict(it)
            flagged["date_unparsed"] = True
            result.append(flagged)
            continue
        delta = (today - dval).days
        if 0 <= delta <= days:
            result.append(it)
        # Gelecek tarihli (delta < 0) kalemleri de tut — saat dilimi kayması olabilir.
        elif delta < 0:
            result.append(it)
    return result


def _main(argv=None):
    parser = argparse.ArgumentParser(description="get_news ham çıktısını normalize eder")
    parser.add_argument("--file", help="Ham JSON dosyası")
    parser.add_argument("--days", type=int, default=None,
                        help="Belirtilirse son N güne filtrele")
    parser.add_argument("--today", default=None,
                        help="Referans bugün (YYYY-MM-DD), test için")
    args = parser.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, ValueError) as e:
            print(json.dumps({"error": str(e), "items": []}, ensure_ascii=False))
            return
        items = normalize(raw)
        if args.days is not None:
            items = recent(items, days=args.days, today=args.today)
        print(json.dumps({"count": len(items), "items": items},
                         ensure_ascii=False, indent=2))
    else:
        # Argümansız: küçük yerleşik öz-test.
        example = {"items": [
            {"baslik": "Geri alım açıklaması", "tarih": "2026-06-14",
             "ozet": "KAP üzerinden bildirim", "kaynak": "KAP"},
            {"title": "Eski haber", "date": "2026-01-01", "source": "Reuters"},
            {"header": "Tarihsiz kayıt"},
        ]}
        normalized = normalize(example)
        result = {
            "self_test_normalize": normalized,
            "self_test_recent": recent(normalized, days=7, today="2026-06-15"),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
