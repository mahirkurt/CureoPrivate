---
name: lex-ria
description: "Mod 6 RIA — reform-öncesi düzenleyici etki analizi (DEA + BEF). Etkilenen aktör haritası + yurtiçi/uluslararası benchmark + maliyet-fayda (JCA) + risk-belirsizlik senaryoları (iyimser/baz/kötümser). Klinik: ICER/BIA/MEA/SGK → evidentia. Argüman = etki analizi yapılacak reform."
argument-hint: <reform konusu — örn. "biyobenzer geri-ödeme reformu DEA">
---

# /lex-ria — Mod 6 RIA (DEA/BEF düzenleyici etki analizi)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 6 RIA** olarak çalıştır. Metodoloji: [`references/05-dea-bef.md`](../skills/cureolex/references/05-dea-bef.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` (S1) + `comparative-law-researcher` (S2). Load-bearing: **oecd** (**GOV_REG** + HEA) + health-policy + german-law (resolve→EU) + eudamed + titck + mevzuat (`list_mevzuat_by_type`) + **fedlex** (SR get → RIA paydaş/alternatifte Vernehmlassung: `fedlex_get_open_consultations` / `fedlex_search_consultations` / `fedlex_get_consultation`; `params` sarmalayıcı; TR DRAFT usulü değil).
3. **Klinik ◆ → evidentia:** ICER/BIA/MEA/SGK.
4. **RIA 8-adım:** hedefler → aktörler (detsis) → yurtiçi `list_mevzuat_types`→`list_mevzuat_by_type` → uluslararası + **OECD GOV_REG zorunlu** + **CH danışma manzarası (SR sonrası)** → içtihat+doktrin → maliyet-fayda → risk → çıktı.
5. **Template:** [`templates/dea-template.md`](../skills/cureolex/templates/dea-template.md) + [`templates/bef-template.md`](../skills/cureolex/templates/bef-template.md) + [`templates/karsilastirma-uluslararasi.md`](../skills/cureolex/templates/karsilastirma-uluslararasi.md).
6. **Kapılar G0-G7**, `evidence_ledger`, no-fabrication.
7. **sci-audit'e delege et** (nicel iddialar → `/check-stats`).
8. **Kapsam manifestosu + confidence_label** ile bitir.
