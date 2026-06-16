---
description: Çoklu-fon portföy inşası ve tahsis önerisi (Mod 4) — aday fon kümesi + risk profili/ufuktan G0-G7 boru hattıyla optimize % tahsis + senaryo matrisi üretir. KARAR-DESTEK; SPK yatırım danışmanlığı değildir.
argument-hint: "[aday fonlar + risk profili/ufuk — örn. 'AFA, IPB, TTE; dengeli; 5 yıl; EMK']"
---

`tefas-analist:fon-analiz-orkestratoru` orkestratörünü **portföy inşası (Mod 4)** modunda çalıştır.

**Kullanıcı briefi:** $ARGUMENTS

## Yürütme protokolü
1. **Pre-flight (CONNECTORS.md §8):** Borsa MCP + fon-mcp canlılığını doğrula. fon-mcp
   erişilemezse holdings look-through degrade olacağını bildir.
2. **Aşama 0 (G0):** Briefi `brief-schema.json`'a oturt; **risk_profile + horizon_months +
   constraints zorunlu (Mod 4)**. Eksikse kullanıcıdan iste; uydurma.
3. **Aşama 1-4:** fund_registry/holdings/nav_series (bir kez) → market_context → peer_metrics →
   quant_metrics. Kanonik önbellek disiplini (her connector/hesap bir kez).
4. **Aşama 5 (G5):** `portfolio_opt.py` (MVO/risk-parity/HRP) → % tahsis + Baz/İyimser/Kötümser
   senaryo (`scenario-matrix-template.md`). Kısıtlar sağlanmazsa relaksasyon öner.
5. **Aşama 6-7 (G6/G7):** İki-katmanlı rapor + `rapor_lint.py` uyum kapısı. SPK feragati birebir.

## Çıktı
`<RUN_ID>` (…-M4-vN): 7 JSON artefakt + `optimized_portfolio.json` + `rapor.md` + `run_manifest.json`.

## Scope guard
Tekil hisse/tahvil tahsisi → bist-analyst. Bireysel vergi/SGK → kapsam dışı. Kişisel "şu kadar al" →
karar-destek diline çevir (% tahsis bandı + tetikleyici + geçersizleşme).
