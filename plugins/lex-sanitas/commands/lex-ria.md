---
description: "Mod 6 RIA — reform-öncesi düzenleyici etki analizi (DEA + BEF). Etkilenen aktör haritası + yurtiçi/uluslararası benchmark + maliyet-fayda (JCA) + risk-belirsizlik senaryoları (iyimser/baz/kötümser). Klinik: ICER/BIA/MEA/SGK → evidentia. Argüman = etki analizi yapılacak reform."
argument-hint: <reform konusu — örn. "biyobenzer geri-ödeme reformu DEA">
---

# /lex-ria — Mod 6 RIA (DEA/BEF düzenleyici etki analizi)

Talep: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 6 RIA** olarak çalıştır. Metodoloji: [`references/05-dea-bef.md`](../skills/lex-sanitas/references/05-dea-bef.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` ile Mod 6 server-listesi. Load-bearing: **oecd** (nicel gösterge) + health-policy + german-law + eudamed + titck + mevzuat.
3. **Klinik ◆ → evidentia:** ICER (§14.c), BIA (§14.d), MEA (§14.e), SGK (§14.f) — zenginleştirilmiş sorgu.
4. **RIA 8-adım:** hedefleri netleştir (Md.26) → etkilenen aktörler → yurtiçi benchmark (`list_mevzuat_by_type`) → uluslararası benchmark (AB + üye devletler + US eCFR/FedReg via health-policy + HTA dörtlüsü + OECD.Stat) → içtihat+doktrin → maliyet-fayda → risk senaryoları → çıktı.
5. **Template:** [`templates/dea-template.md`](../skills/lex-sanitas/templates/dea-template.md) + [`templates/bef-template.md`](../skills/lex-sanitas/templates/bef-template.md) + [`templates/karsilastirma-uluslararasi.md`](../skills/lex-sanitas/templates/karsilastirma-uluslararasi.md).
6. **Kapılar G0-G7**, `evidence_ledger`, no-fabrication.
7. **sci-audit'e delege et** (nicel iddialar → `/check-stats`).
8. **Kapsam manifestosu + confidence_label** ile bitir.
