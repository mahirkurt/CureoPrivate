---
description: Mod 7 COMPARATIVE_LAW — reform için uluslararası emsal analizi (benchmark/gap/policy/case-law). Yargı bölgesi seçimi + mukayese matrisi + gap analizi + politika önerisi (4-boyut uyum + geçiş). Yabancı ülke mevzuatı: health-policy (US/CA/JP/AU/ES/IE/CN/MX) + german-law (DE/AB) + Open Law (UK+EU) + Ansvar (58-yargı) + Fedlex Swiss (CH, bağlıysa). Argüman = karşılaştırma sorusu.
argument-hint: <karşılaştırma sorusu — örn. "ATMP ruhsatlandırma: AB vs US vs Japonya">
---

# /lex-comparative — Mod 7 COMPARATIVE_LAW (karşılaştırmalı hukuk)

Talep: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 7 COMPARATIVE_LAW** olarak çalıştır. Template: [`templates/comparative-law-analysis.md`](../skills/lex-sanitas/templates/comparative-law-analysis.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` ile Mod 7 server-listesi. Load-bearing yabancı katman: **health-policy · german-law · ich-guidelines · intl-treaty · eudamed · Open_Law · Ansvar · oecd** (+ CH kapsamdaysa **Fedlex Swiss** birincil metin — Ansvar CH satırı çerçeve-teyit); TR karşı-taraf: mevzuat + Yarg (+ IP-boyut varsa **Türk Patent**).
3. **Klinik ◆ → evidentia** (§6,9,13,14,20).
4. **COMPARATIVE 8-adım:** soruyu netleştir (tip) → yargı bölgeleri seç (R12 §9) → TR-metin Tabaka tespiti → **yabancı sağlık-hukukunda önce `mcp__health-policy__semantic_search`** (serbest-metin soru → çok-dilli fan-out US/JP/AU/CN + bge-m3 rerank; ES/MX/CA/IE `excluded_sources`→fetch) ile hedefle, sonra yabancı metinleri çek (**programatik: CELLAR/legislation.gov.uk AKN/eCFR/DPD; ECLI tercih** — no-fabrication, URL'siz atma; semantik `mcp_verified:false` → fetch ile doğrula) → mukayese matrisi → gap analizi (usuli/maddi/kurumsal/şeffaflık) → politika önerisi (tip C zorunlu) → 13-bölüm rapor.
5. **Kapılar G0-G7** (+ template'in koşullu G8/G9 notu), `evidence_ledger`.
6. **sci-audit'e delege et.**
7. **Kapsam manifestosu + confidence_label** ile bitir.
