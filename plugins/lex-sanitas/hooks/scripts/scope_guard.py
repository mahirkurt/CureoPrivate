#!/usr/bin/env python3
"""lex-sanitas UserPromptSubmit Scope Guard — kapsam-drift erken uyarısı.

lex-sanitas YALNIZ mevzuat reformu içindir (SKILL §6). Bireysel hak-arama (SGK ödeme reddi davası,
AYM bireysel başvuru, kompasyonel kullanım, malpraktis) ve promosyonel materyal denetimi kapsam
DIŞIDIR → başka skill'lere yönlendirilir. Bu hook, prompt'ta HEM sağlık-mevzuat/hukuk bağlamı HEM
kapsam-dışı sinyal birlikte görülürse kısa bir yönlendirme hatırlatması enjekte eder; aksi halde
SESSİZ kalır (gürültü yok). Bağlam karar verir, terim değil — bu yalnız bir ERKEN UYARIDIR, asla
blok değil. Fail-open.
"""
import json
import re
import sys

# Sağlık/hukuk bağlam sinyali (en az biri) — aksi halde lex-sanitas ile ilgisiz, sessiz kal.
CONTEXT = re.compile(
    r"(mevzuat|yönetmelik|tebliğ|kanun|genelge|reform|TİTCK|titck|SGK|sağlık bakanlığı|"
    r"ilaç|tıbbi cihaz|ruhsat|SUT|geri[- ]?ödeme|regülasyon|hukuk|dava|başvuru|malpraktis|"
    r"promosyon|reçete|endikasyon)",
    re.IGNORECASE,
)

# Kapsam-dışı sinyaller → yönlendirme hedefi.
OUT_OF_SCOPE = [
    (re.compile(r"(bireysel başvuru|AYM.{0,20}başvuru|SGK.{0,20}(red|ödeme reddi|itiraz)|"
                r"ödeme reddi.{0,20}dava|kompasyon|compassionate|malpraktis|tazminat dava|"
                r"hasta.{0,10}dava|dava dilekçe)", re.IGNORECASE),
     "saglik-sigorta / onko-erisim (bireysel hak-arama / dava — reform DEĞİL)"),
    (re.compile(r"(detail aid|leave[- ]?behind|promosyon.{0,15}(materyal|denetim)|MLR|"
                r"speaker bureau|tanıtım malzeme|reklam.{0,10}uyum|CME.{0,15}uyum)", re.IGNORECASE),
     "promo-censor (promosyonel materyal / MLR denetimi — mevzuat yazımı DEĞİL)"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = str(data.get("prompt", ""))
    if not prompt or not CONTEXT.search(prompt):
        sys.exit(0)  # lex-sanitas bağlamı yok → sessiz

    hits = [target for rx, target in OUT_OF_SCOPE if rx.search(prompt)]
    if not hits:
        sys.exit(0)  # kapsam-dışı sinyal yok → sessiz

    ctx = (
        "[lex-sanitas Scope Guard] Bu talep KAPSAM-DIŞI bir sinyal taşıyor olabilir → "
        + "; ".join(hits)
        + ". lex-sanitas yalnız mevzuat REFORMU/üretimi içindir (DRAFT/AMEND/analiz/uyum/görüş/"
        "RIA/karşılaştırmalı/TBMM/ex-post). Talep gerçekten bireysel hak-arama veya promosyon "
        "denetimi ise yukarıdaki skill'e yönlendir, lex-sanitas çıktısı ÜRETME. Reform bağlamıysa "
        "(mevzuatın kendisini değiştirmek/yazmak) devam et. Bağlam karar verir — bu yalnız uyarıdır."
    )
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
