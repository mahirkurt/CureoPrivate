---
name: lex-opine
description: Mod 5 OPINE — reform sürecinde resmi kurum görüşü + paydaş görüşü + bilirkişi mütalaası (TİTCK/SGK-politika/AB Başkanlığı/KVKK/TBMM Sağlık Komisyonu perspektifi; EK-1 yapılı görüş + Md.7 15-gün zımni-onay). Bireysel SGK/AYM dava savunması DEĞİL (→ saglik-sigorta/onko-erisim). Argüman = görüş verilecek taslak + görüş-veren kurum.
argument-hint: <taslak + kurum — örn. "SUT değişikliği taslağı, TİTCK görüşü">
---

# /lex-opine — Mod 5 OPINE (kurum/bilirkişi görüşü)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 5 OPINE** olarak çalıştır.

## Yürütme

1. **Scope Guard (§6).** Bireysel dava savunması → `saglik-sigorta`/`onko-erisim`. (Bu mod politika-düzeyi kurumsal görüştür.)
2. **Tam-filo (G0).** `legal-distiller` ile Mod 5 server-listesi (mevzuat + Yarg + yok-akademik + görüş-veren kurum: titck/saglikbakanligi/detsis; karşılaştırmalı + oecd + evidentia çapraz).
3. **OPINE 7-adım:** taslağı+ekleri oku → arka planda COMPLY → içtihat+doktrin filtresi → görüş-veren kurum perspektifinden değerlendir → EK-1 yapılı görüş → karşılaştırma tablosu → Md.7 15-günlük zımni-onay hatırlatması.
4. **Template:** [`templates/gorus-bildirimi.md`](../skills/cureolex/templates/gorus-bildirimi.md).
5. **Kapılar G0-G7**, `evidence_ledger`, no-fabrication.
6. **sci-audit'e delege et.**
7. **Kapsam manifestosu + confidence_label** ile bitir.
