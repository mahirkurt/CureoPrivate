---
description: Fon tarama (Mod 2) — kategori/kriter (düşük TER, yüksek Sharpe, getiri) ile aday fon evreni + akran kuant → kısa karar-destek listesi. SPK yatırım danışmanlığı değildir.
argument-hint: "[kategori / kriter — örn. 'düşük TER hisse YAT' veya 'son 1y en iyi para piyasası']"
---

`fon-uzmani:fon-analiz-orkestratoru` orkestratörünü **kategori/tarama (Mod 2)** modunda çalıştır.

**Kullanıcı briefi:** $ARGUMENTS

## Yürütme protokolü
1. **Pre-flight:** Borsa MCP + fon-mcp canlılığı.
2. **Aşama 0 (G0):** Briefi `brief-schema.json`'a oturt (mode=2; universe; category; sıralama kriteri).
3. **Aşama 1 (G1):** `Borsa screen_funds` + `fon-mcp compare_fund_costs`/`list_emk_funds` ile aday evren.
4. **Aşama 3 (G3):** Adaylar için toplu kuant (Sharpe/maxDD/TER yüzdebirlik) → peer_metrics.
5. **Aşama 6-7:** Kısa karşılaştırma tablosu raporu + uyum kapısı.

## Çıktı
`<RUN_ID>` (…-M2-vN): peer_metrics.json + `rapor.md` (sıralı aday tablosu + caveat).

## Scope guard
Kişiselleştirilmiş "şunu al" → karar-destek diline çevir. Serbest/kaldıraçlı fonlar varsayılan dışlanır.
