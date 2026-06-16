#!/usr/bin/env python3
"""brief_lint.py — BIST analist kopilotu brifing uyumluluk/kalite denetleyicisi.

Tamamlanmış bir brifing metnini (Markdown) okuyup uyumluluk ve kalite
kontrollerini çalıştırır. Kütüphane olarak `lint(text)` ile, CLI olarak
`--file brief.md` ile kullanılır. Hiçbir koşulda çökmemelidir.

Kontroller (compliance.md ile hizalı):
  - disclaimer_present  : kanonik feragat var mı (ERROR)
  - no_imperative_advice: kişiselleştirilmiş al/sat emri yok mu (ERROR)
  - no_machine_leakage  : ham JSON / araç adı / borsa MCP sızıntısı yok mu (ERROR)
  - sources_dated       : sayı/alıntılar as-of tarihiyle anılmış mı (WARN)
  - eod_ack             : fiyat seviyesi varsa EOD/gün sonu kaydı var mı (WARN)
  - has_scenario_matrix : senaryo matrisi bölümü var mı (WARN)
  - has_confidence      : güven göstergesi var mı (WARN)

Çıktı: {passed, errors, warnings, checks}. CLI çıkış kodu 0 (geçti) / 1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

# --------------------------------------------------------------------------- #
# Yardımcılar
# --------------------------------------------------------------------------- #


def _strip_diacritics(s: str) -> str:
    """Diakritikleri kaldırır ve Türkçe özel harfleri ASCII'ye indirger."""
    if not isinstance(s, str):
        s = str(s)
    # Türkçe'ye özel önişleme (NFD bunları her zaman ayrıştırmaz)
    repl = {
        "ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
        "ç": "c", "Ç": "c", "ö": "o", "Ö": "o", "ü": "u", "Ü": "u",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _norm(s: str) -> str:
    """Küçük harf + diakritiksiz normalize edilmiş metin."""
    return _strip_diacritics(s).lower()


def _strip_code_fences(text: str) -> str:
    """Fenced kod bloklarını metinden ayırır; gövde analizinde hariç tutmak için."""
    return re.sub(r"```.*?```", " ", text, flags=re.DOTALL)


# Gövdede asla görünmemesi gereken makine/araç sızıntısı işaretleri.
_LEAKAGE_TOOL_TOKENS = [
    "get_quick_info", "get_technical_analysis", "get_news", "get_evds_data",
    "get_historical_data", "search_symbol", "scan_stocks", "screen_securities",
    "screen_funds", "get_financial_ratios", "get_sector_comparison",
    "borsa mcp", "borsa_mcp",
]

# Kişiselleştirilmiş emir kalıpları (kelime sınırlı). Yanlış pozitiflerden
# kaçınmak için "alan", "satış", "alım-satım", "alıcı" gibi türevler dışlanır.
_IMPERATIVE_PATTERNS = [
    r"\bal\b",            # "AL " tek başına emir
    r"\bsat\b",           # "SAT " tek başına emir
    r"\bsatin\s+al\b",    # "satın al"
    r"\bsatin\s+alin\b",  # "satın alın"
    r"\balin\b",          # "alın"
    r"\bsatin\b",         # "satın" (emir bağlamı)
    r"\btopla\b",         # "topla" (pozisyon topla)
    r"\bbosalt\b",        # "boşalt"
    r"\bgir\b",           # "(pozisyona) gir" tek başına
]

# Emir gibi görünse de güvenli olan ifadeler (allowlist). Bunların geçtiği
# cümleler emir sayılmaz.
_SAFE_ALLOWLIST = [
    "al/sat tavsiyesi", "al-sat", "alim-satim", "alis-satis",
    "alim satim", "yatirim danismanligi", "tavsiye niteligi",
    "alici", "satici", "alis", "satis", "satin alma gucu",
    "topladigi", "toplam", "toplanan", "veri toplama",
    "girdi", "girisi", "girilen", "giris seviyesi",
]


def _date_nearby(text: str) -> bool:
    """Metinde herhangi bir as-of tarih/dönem işareti var mı?"""
    norm = _norm(text)
    patterns = [
        r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",       # 15.06.2026
        r"\b\d{4}-\d{2}-\d{2}\b",             # 2026-06-15
        r"\b\d{1,2}\s+[a-z]+\s+\d{4}\b",      # 15 haziran 2026
        r"\bkapanis\b", r"\beod\b", r"\bgun\s*sonu\b",
        r"\bas[-\s]?of\b", r"\bitibar(?:i|iyle|iyla)\b",
    ]
    return any(re.search(p, norm) for p in patterns)


def _has_price_level(text: str) -> bool:
    """Metinde fiyat/seviye atfı var mı (TL, destek/direnç, sayısal seviye)?"""
    norm = _norm(text)
    if re.search(r"\b(destek|direnc|seviye|pivot)\b", norm):
        return True
    if re.search(r"\b\d{1,4}[.,]\d{1,2}\s*(tl|try)\b", norm):
        return True
    if re.search(r"\b(tl|try)\s*\d", norm):
        return True
    return False


# --------------------------------------------------------------------------- #
# Çekirdek lint
# --------------------------------------------------------------------------- #


def lint(text: str) -> dict:
    """Bir brifing metnini denetler ve sonuç sözlüğü döner.

    Asla istisna fırlatmaz; geçersiz girdi boş/başarısız rapora indirgenir.
    """
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            text = ""

    norm_full = _norm(text)
    body = _strip_code_fences(text)
    norm_body = _norm(body)

    # --- 1) disclaimer_present (ERROR) ------------------------------------- #
    disclaimer_ok = (
        "yatirim danismanligi" in norm_full
        and "karar-destek" in norm_full
        and "gecmis performans" in norm_full
    )
    checks["disclaimer_present"] = disclaimer_ok
    if not disclaimer_ok:
        errors.append(
            "Kanonik feragat eksik veya bozuk: 'yatırım danışmanlığı', "
            "'karar-destek' ve 'Geçmiş performans' ifadelerinin tümü "
            "bulunmalıdır."
        )

    # --- 2) no_imperative_advice (ERROR) ----------------------------------- #
    # Satır satır tara; feragat satırlarını ve allowlist içeren satırları atla.
    imperative_hits: list[str] = []
    for raw_line in body.splitlines():
        nline = _norm(raw_line)
        if not nline.strip():
            continue
        # Feragat / tavsiye-reddi satırlarını atla
        if "al/sat tavsiyesi" in nline or "tavsiye niteligi" in nline:
            continue
        # Allowlist ifadesi içeren satırı, ilgili kısmı maskeleyerek değerlendir
        masked = nline
        for safe in _SAFE_ALLOWLIST:
            masked = masked.replace(safe, " ")
        for pat in _IMPERATIVE_PATTERNS:
            if re.search(pat, masked):
                snippet = raw_line.strip()
                imperative_hits.append(snippet[:120])
                break
    imperative_ok = len(imperative_hits) == 0
    checks["no_imperative_advice"] = imperative_ok
    if not imperative_ok:
        errors.append(
            "Kişiselleştirilmiş al/sat emri tespit edildi (karar-destek "
            "çerçevesi ihlali): " + " | ".join(imperative_hits[:3])
        )

    # --- 3) no_machine_leakage (ERROR) ------------------------------------- #
    leakage_hits: list[str] = []
    if "```json" in text.lower():
        leakage_hits.append("```json kod bloğu")
    # Ham JSON nesne bloğu (gövdede, kod çitleri hariç): {"...": ...}
    if re.search(r'\{\s*"[^"]+"\s*:', body):
        leakage_hits.append("ham JSON nesne bloğu")
    for tok in _LEAKAGE_TOOL_TOKENS:
        if tok in norm_body:
            leakage_hits.append(tok)
    # "MCP" geçişi (gövdede, büyük/küçük fark etmeksizin kelime olarak)
    if re.search(r"\bmcp\b", norm_body):
        leakage_hits.append("MCP")
    leakage_ok = len(leakage_hits) == 0
    checks["no_machine_leakage"] = leakage_ok
    if not leakage_ok:
        # Tekilleştir, sırayı koru
        seen = []
        for h in leakage_hits:
            if h not in seen:
                seen.append(h)
        errors.append(
            "Makine/araç sızıntısı (kullanıcıya gösterilmemeli): "
            + ", ".join(seen[:6])
        )

    # --- 4) sources_dated (WARN) ------------------------------------------- #
    has_numbers = bool(re.search(r"\d", body))
    dated = _date_nearby(text)
    sources_dated_ok = (not has_numbers) or dated
    checks["sources_dated"] = sources_dated_ok
    if not sources_dated_ok:
        warnings.append(
            "Sayısal veri/alıntı var ancak yakınında as-of tarih/dönem "
            "(örn. 15.06.2026, 'kapanış', 'gün sonu') işareti bulunamadı."
        )

    # --- 5) eod_ack (WARN) ------------------------------------------------- #
    has_levels = _has_price_level(text)
    eod_ack = bool(re.search(r"\b(eod|gun\s*sonu|gecikmeli|kapanis)\b", norm_full))
    eod_ok = (not has_levels) or eod_ack
    checks["eod_ack"] = eod_ok
    if not eod_ok:
        warnings.append(
            "Fiyat/seviye atfı var ancak hiçbir yerde EOD / gün sonu / "
            "gecikmeli veri kaydı bulunamadı."
        )

    # --- 6) has_scenario_matrix (WARN) ------------------------------------- #
    scenario_ok = "senaryo" in norm_full
    checks["has_scenario_matrix"] = scenario_ok
    if not scenario_ok:
        warnings.append(
            "Senaryo matrisi/bölümü bulunamadı ('senaryo' ifadesi yok)."
        )

    # --- 7) has_confidence (WARN) ------------------------------------------ #
    confidence_ok = bool(re.search(r"\bguven\b|\bguven\w*", norm_full))
    checks["has_confidence"] = confidence_ok
    if not confidence_ok:
        warnings.append(
            "Güven göstergesi bulunamadı ('güven' işareti yok)."
        )

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


# --------------------------------------------------------------------------- #
# Yerleşik öz-test örnekleri
# --------------------------------------------------------------------------- #

_CANONICAL_DISCLAIMER = (
    "Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; yatırım "
    "danışmanlığı, aracılık veya al/sat tavsiyesi niteliği taşımaz. Veriler "
    "büyük ölçüde gün sonu (EOD) ve gecikmeli olabilir; gün içi emir "
    "defteri/derinlik bilgisi içermez. Yatırım kararları; kişinin kendi risk "
    "profili, bağımsız araştırması ve gerektiğinde SPK lisanslı bir yatırım "
    "danışmanına danışılarak alınmalıdır. Geçmiş performans gelecekteki "
    "getirinin garantisi değildir."
)

_SAMPLE_OK = f"""# GARAN — Karar-Destek Brifingi (as-of 15.06.2026, kapanış)

## Karar-destek özeti
Teknik görünüm nötr-yukarı; güven: orta. Veriler gün sonu (EOD) bazlıdır.

## Teknik görünüm
Destek 118,40 TL, direnç 126,00 TL (15.06.2026 kapanışına göre).

## Senaryo matrisi
Baz / Boğa / Ayı senaryoları aşağıda özetlenmiştir. Her senaryonun
geçersizlik seviyesi ve güven derecesi belirtilmiştir.

## Feragat
{_CANONICAL_DISCLAIMER}
"""

_SAMPLE_BAD = """# XYZ Hisse Notu

Bu hisseyi al, kesinlikle topla. Hedef yükseliş.

```json
{"symbol": "XYZ", "price": 10.0}
```

get_technical_analysis sonucuna göre fiyat 10 TL.
"""


def _self_test() -> int:
    """Argümansız çağrıda yerleşik örnekleri denetler, JSON basar."""
    ok_res = lint(_SAMPLE_OK)
    bad_res = lint(_SAMPLE_BAD)
    out = {
        "self_test": True,
        "compliant_sample": ok_res,
        "non_compliant_sample": bad_res,
        "compliant_passed_expected_true": ok_res["passed"],
        "non_compliant_passed_expected_false": bad_res["passed"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    # Öz-test başarısı: uyumlu örnek geçmeli, uyumsuz geçmemeli.
    return 0 if (ok_res["passed"] and not bad_res["passed"]) else 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BIST brifing uyumluluk/kalite denetleyicisi."
    )
    parser.add_argument(
        "--file", "-f", help="Denetlenecek Markdown brifing dosyası."
    )
    args = parser.parse_args(argv)

    if not args.file:
        return _self_test()

    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:  # dosya okunamazsa çökme
        print(
            json.dumps(
                {
                    "passed": False,
                    "errors": [f"Dosya okunamadı: {exc}"],
                    "warnings": [],
                    "checks": {},
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    result = lint(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # son güvenlik ağı: asla ham traceback ile çökme
        print(
            json.dumps(
                {"passed": False, "errors": [f"Beklenmeyen hata: {exc}"],
                 "warnings": [], "checks": {}},
                ensure_ascii=False,
            )
        )
        sys.exit(1)
