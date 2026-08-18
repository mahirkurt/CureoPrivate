---
name: lex-comparative
description: "Mod 7 COMPARATIVE_LAW — reform için uluslararası emsal analizi (benchmark/gap/policy/case-law). Yargı bölgesi seçimi + mukayese matrisi + gap analizi + politika önerisi (4-boyut uyum + geçiş). Yabancı ülke mevzuatı: health-policy (US/CA/JP/AU/ES/IE/CN/MX) + german-law (DE/AB↔DE) + eurlex (G6 CELEX) + uk-legal (legislation_* + içtihat/Hansard) + fedlex (CH) + Open Law (UK çapraz/HUDOC, bağlıysa) + Ansvar (58-yargı). Argüman = karşılaştırma sorusu."
argument-hint: '<karşılaştırma sorusu — örn. "ATMP ruhsatlandırma: AB vs US vs Japonya">'
---

# /lex-comparative — Mod 7 COMPARATIVE_LAW (karşılaştırmalı hukuk)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 7 COMPARATIVE_LAW** olarak çalıştır. Template: [[`templates/comparative-law-analysis.md`](../skills/cureolex/templates/comparative-law-analysis.md)](../skills/cureolex/templates/comparative-law-analysis.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` ile Mod 7 server-listesi. Load-bearing yabancı katman: **health-policy · german-law · eurlex · uk-legal · fedlex · ich-guidelines · intl-treaty · eudamed · oecd** (+ bağlıysa Open_Law UK + Ansvar tarama); TR karşı-taraf: mevzuat + Yarg.
3. **Klinik ◆ → evidentia** (§6,9,13,14,20).
4. **COMPARATIVE 8-adım:** soruyu netleştir (tip) → yargı bölgeleri seç (R12 §9) → TR-metin Tabaka tespiti → **yabancı sağlık-hukukunda önce `mcp__health-policy__semantic_search`** (serbest-metin soru → çok-dilli fan-out US/JP/AU/CN + bge-m3 rerank; ES/MX/CA/IE `excluded_sources`→fetch) ile hedefle, sonra yabancı metinleri çek (**programatik: CELLAR/eCFR/DPD; UK `legislation_search`→`legislation_get_toc`→`legislation_get_section`; ECLI tercih** — no-fabrication, URL'siz atma; Open Law yalnız çapraz/yedek; semantik `mcp_verified:false` → fetch ile doğrula) → **Md.90/5 ateş:** `treaty_status` + `treaty_reservations` (ICESCR/ICCPR/CEDAW/CRC/CRPD) · `coe_treaty_signatories` (Oviedo 164, MEDICRIME 211; snapshot) · `intl_treaty_info` bir kez · **`uhri_search`→`uhri_fetch_document`** (`live_coe:false` beyanlı degrade; UHRI treaty yerine geçmez; onay uydurulmaz) → mukayese matrisi → gap analizi (usuli/maddi/kurumsal/şeffaflık) → politika önerisi (tip C zorunlu) → 13-bölüm rapor.
5. **Kapılar G0-G7** (+ template'in koşullu G8/G9 notu), `evidence_ledger`.
6. **sci-audit'e delege et.**
7. **Kapsam manifestosu + confidence_label** ile bitir.
