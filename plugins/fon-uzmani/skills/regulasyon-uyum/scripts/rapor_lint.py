#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rapor_lint.py — Fon Uzmanı rapor uyum denetimi (G7 zorunlu kapı).

bist-analyst brief_lint.py deseninin fon+SPK uyarlaması. Yayım-öncesi 8 kontrol:
kanonik SPK feragati (anahtar-ifade string-match), emir-kipi yok, sayılar tarihli,
makine sızıntısı yok (Katman A), EOD beyanı, üçüncü-taraf etiketi, senaryo/karşıt-senaryo,
kesinlik iddiası yok. ERROR → rapor yayımlanamaz; WARN → not.

Konvansiyon: saf stdlib; `--file rapor.md`; argümansız self-test. Çökmez.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

DISCLAIMER = "karar-destek; yatırım tavsiyesi değildir"

# Kanonik feragatin denetlenen anahtar ifadeleri (compliance.md ile senkron).
DISCLAIMER_PHRASES = [
    "karar-destek",
    "SPK yatırım danışmanlığı",
    "geçmişe dönük",
    "gün-sonu (EOD)",
]

# Render-dışı annex sentinel'leri (Katman B; bunların İÇİ makine sızıntısı sayılmaz).
SENTINEL_OPEN = "<!-- RENDER:EXCLUDE-FROM-HERE -->"
SENTINEL_CLOSE = "<!-- RENDER:EXCLUDE-TO-HERE -->"

# Emir-kipi / tavsiye dili (kelime sınırıyla).
IMPERATIVE = [r"\bal[ıi]n\b", r"\bsat[ıi]n al", r"\bsat\b", r"\bsatın\b",
              r"\bbu fonu al", r"\byatırım yapın\b", r"\balın\b"]
CERTAINTY = [r"\bkesin(likle)?\b", r"\bgaranti\b", r"\bmutlaka kazan", r"\bkesin getiri\b"]
MACHINE_LEAK = [r"\bMCP\b", r"borsa[_-]?mcp", r"fon[_-]?mcp", r"get_fund_data", r"```json",
                r"structuredContent", r"tools/call"]


def _strip_annex(text):
    """Katman B (render-dışı annex) bölümünü çıkar — makine sızıntısı denetimi Katman A üstünde."""
    if SENTINEL_OPEN in text and SENTINEL_CLOSE in text:
        out = []
        depth = 0
        i = 0
        while i < len(text):
            if text.startswith(SENTINEL_OPEN, i):
                depth += 1
                i += len(SENTINEL_OPEN)
                continue
            if text.startswith(SENTINEL_CLOSE, i):
                depth = max(0, depth - 1)
                i += len(SENTINEL_CLOSE)
                continue
            if depth == 0:
                out.append(text[i])
            i += 1
        return "".join(out)
    return text


# Kanonik feragat cümlesinin işaretleri — bu cümleler emir/kesinlik taramasından muaftır
# (feragat metni meşru olarak "al/sat tavsiyesi ... değildir" ve "garanti değildir" içerir).
_DISCLAIMER_MARKERS = ("danışman", "tavsiyesi niteliği", "tavsiye niteliği",
                       "karar-destek amaçlıdır", "garantisi değildir")


def _strip_disclaimer(text):
    """Feragat cümlelerini çıkar — emir/kesinlik denetimi yalnız analiz gövdesi üstünde."""
    out = []
    for sent in re.split(r"(?<=[.\n])", text):
        if any(m in sent.lower() for m in _DISCLAIMER_MARKERS):
            continue
        out.append(sent)
    return "".join(out)


def lint(text):
    errors, warnings = [], []
    layer_a = _strip_annex(text)
    low = layer_a.lower()
    body = _strip_disclaimer(layer_a)  # emir/kesinlik/sızıntı taraması feragatsiz gövdede

    # 1) Kanonik feragat (anahtar ifadeler)
    missing = [p for p in DISCLAIMER_PHRASES if p.lower() not in low]
    if missing:
        errors.append(f"disclaimer_missing: kanonik feragat ifadeleri eksik: {missing}")

    # 2) Emir-kipi yok
    for pat in IMPERATIVE:
        if re.search(pat, body, re.IGNORECASE):
            errors.append(f"imperative_advice: tavsiye/emir-kipi tespit edildi (~/{pat}/)")
            break

    # 3) Makine sızıntısı yok (Katman A)
    for pat in MACHINE_LEAK:
        if re.search(pat, body, re.IGNORECASE):
            errors.append(f"machine_leakage: ham makine çıktısı/araç adı (~/{pat}/)")
            break

    # 4) Kesinlik iddiası yok
    for pat in CERTAINTY:
        if re.search(pat, body, re.IGNORECASE):
            errors.append(f"certainty_claim: kesinlik/garanti dili (~/{pat}/)")
            break

    # 5) EOD beyanı (WARN)
    if "eod" not in low and "gün-sonu" not in low and "gun-sonu" not in low:
        warnings.append("eod_ack: EOD/gün-sonu beyanı bulunamadı")

    # 6) Sayı tarihliliği (WARN) — yüzde/sayı varsa as-of/tarih beklenir
    if re.search(r"%\s?\d|[0-9]+,[0-9]", layer_a) and not re.search(r"as[- ]?of|\d{4}-\d{2}-\d{2}|gün-sonu", low):
        warnings.append("sources_dated: sayısal iddia var ama as-of/tarih damgası görünmüyor")

    # 7) Senaryo/karşıt-senaryo (WARN)
    if not re.search(r"senaryo|karşıt|baz|iyimser|kötümser", low):
        warnings.append("scenario_matrix: senaryo/karşıt-senaryo bölümü görünmüyor")

    # 8) Üçüncü-taraf etiketi (WARN) — kurucu/yönetici geçiyorsa
    if re.search(r"kurucu|yönetici|portföy yönetim", low) and "değildir" not in low:
        warnings.append("third_party: üçüncü-taraf (kurucu/yönetici) bağlamı var; feragat teyit edilmeli")

    return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings,
            "disclaimer": DISCLAIMER}


def _self_test():
    good = (
        "## Yönetici Özeti\n"
        "AFA fonu 2026-06-16 itibarıyla (gün-sonu/EOD) Sharpe 1.4 göstermektedir [as-of 2026-06-16].\n"
        "Baz senaryoda ... Kötümser senaryoda ...\n"
        "Kurucu: İş Portföy.\n"
        "Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; SPK yatırım danışmanlığı, "
        "portföy yöneticiliği veya al/sat tavsiyesi niteliği taşımaz. Fon getirileri geçmişe dönük "
        "olup gelecekteki getirinin garantisi değildir; NAV verileri gün-sonu (EOD) ve gecikmeli "
        "olabilir. Yatırım kararları; kişinin kendi risk profili ile alınmalıdır.\n"
        "<!-- RENDER:EXCLUDE-FROM-HERE -->\nOPS: get_fund_data x1 MCP\n<!-- RENDER:EXCLUDE-TO-HERE -->\n"
    )
    r = lint(good)
    assert r["passed"], f"iyi rapor geçmeli: {r['errors']}"
    # annex içindeki MCP/get_fund_data sızıntı sayılmamalı
    assert not any("machine_leakage" in e for e in r["errors"]), "annex sızıntı sayılmamalı"

    bad = "Bu fonu hemen alın, kesinlikle kazandırır. get_fund_data sonucu: %50."
    rb = lint(bad)
    assert not rb["passed"], "kötü rapor düşmeli"
    assert any("imperative" in e for e in rb["errors"])
    assert any("certainty" in e for e in rb["errors"])
    assert any("machine_leakage" in e for e in rb["errors"])
    assert any("disclaimer_missing" in e for e in rb["errors"])

    print("== rapor_lint: ALL TESTS PASSED ==", file=sys.stderr)
    return {"selftest": "rapor_lint", "good_passed": r["passed"], "bad_blocked": not rb["passed"],
            "disclaimer": DISCLAIMER}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fon Uzmanı rapor uyum denetimi (G7).")
    ap.add_argument("--file", help="rapor.md dosyası")
    ap.add_argument("--indent", type=int, default=2)
    args = ap.parse_args(argv)
    if not args.file:
        print(json.dumps(_self_test(), ensure_ascii=False, indent=args.indent))
        return 0
    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(json.dumps({"error": f"Girdi okunamadı: {exc}", "disclaimer": DISCLAIMER}, ensure_ascii=False))
        return 1
    res = lint(text)
    print(json.dumps(res, ensure_ascii=False, indent=args.indent))
    return 0 if res["passed"] else 2


if __name__ == "__main__":
    sys.exit(main())
