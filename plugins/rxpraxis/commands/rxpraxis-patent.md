---
description: Patent FTO + LOE + Bolar penceresi + SPC analizi. pharmapatent Mod 13→1→5→(9) zinciri + Türk Patent MCP. rxos Aşama 4'ün tek-skill kısayolu.
argument-hint: "[molekül / patent no / başvuru sahibi]"
---

`rxpraxis:pharmapatent` Mod 13→1→5→(9) zincirini çalıştır.

**Hedef:** $ARGUMENTS

## Yürütme
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

## Fallback
Türk Patent MCP hata → Espacenet → Patentscope → USPTO → Google Patents (CONNECTORS.md §6).
