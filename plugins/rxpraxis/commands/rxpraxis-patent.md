---
description: Patent FTO + LOE + Bolar penceresi + SPC analizi. pharmapatent Mod 13→1→5→(9) zinciri + Türk Patent MCP. rxos Aşama 4'ün tek-skill kısayolu.
argument-hint: "[molekül / patent no / başvuru sahibi]"
---

`rxpraxis:pharmapatent` Mod 13→1→5→(9) zincirini çalıştır.

**Hedef:** $ARGUMENTS

## Yürütme

0. **Araç yükleme (tool-manifest.json — L1):** `shared/tool-manifest.json`
   `commands.rxpraxis-patent` bloğunu pin-yükle. Pre-flight: §8 + §9 — Türk Patent servis
   bakiyesini kontrol et; bakiye/timeout varsa devre durumunu `scan-ledger.circuit_breakers`'a
   yaz. Her ham pull **extract-then-evict** (canonical-cache §9); `scan-ledger` checkpoint güncelle.

1. **Mod 13 (TR çekirdek):** `titck_canonical` varsa **oku** (canonical-cache §3); yoksa çıkar.
   Türk Patent MCP: `search_patents` (applicant + IPC/CPC + abstract) → `get_patent_details`
   → EP→TR validation.
2. **Mod 1 FTO:** compound + formülasyon + use + polimorf/metabolite/process; Rezidüel Risk Beyanı.
3. **Mod 5 exclusivity:** FDA NCE 5y + EMA 8+2 + TR BTÜ-RM 6+2 + Bolar (SMK 6769 m.85) + LOE.
4. **Mod 9 (koşullu):** yalnız biyolojik/biyobenzer — patent duvarı + karşılaştırılabilirlik.
5. **Helper'lar:** `scripts/loe-calculator.py` · `spc-calculator.py` · T-DEATH + Bolar safety +
   injunction risk skorları.

## Çıktı
`feasibility_matrix` patent bölümü: patent timeline + 7-katman typology + verdict
(VIABLE/VIABLE_WITH_CAVEAT/NOT_VIABLE).

## Fallback (CONNECTORS.md §6 + §9 devre-kesici — bu komut için belirleyici)
Türk Patent MCP **2 ardışık başarısızlıkta OPEN** olur (§9; service balance / Capsolver /
timeout). OPEN davranışı: Espacenet → Patentscope WIPO → USPTO → Google Patents zinciri +
(ABD için) Orange/Purple Book **dokümante-public-fact**. Kritik: patent **yön-yalnız**
raporlanır ("patent-canlı / off-patent yönü"), **sayısal LOE tarihi olmadan**; verdict
`feasibility_matrix.patent_section` `VIABLE_WITH_CAVEAT`'a düşer ve
`"sayısal LOE teyidi eksik — Türk Patent + Espacenet + Orange Book ile doğrulanmalı"` caveat'ı
taşır. **Sessizce "engel yok" ya da "engel var" VARSAYMA.** Açık devre `scan-ledger` +
Katman B'ye yazılır. (Üç referans koşumunda — dapagliflozin/sevimelin/efinaconazole — bu yola
düşüldü; özellikle efinaconazole'de patent-canlı yön kararın belirleyici kapısıydı.)
