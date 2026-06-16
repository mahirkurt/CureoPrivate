---
description: Tek fon derin analizi (Mod 1) — kimlik+dağılım+TER + risk/getiri (Sharpe/Sortino/maxDD/beta/VaR) + akran konumu → iki-katmanlı karar-destek raporu. SPK yatırım danışmanlığı değildir.
argument-hint: "[fon kodu / adı — örn. 'AFA' veya 'İş Portföy Hisse Fonu']"
---

`fon-uzmani:fon-analiz-orkestratoru` orkestratörünü **tek-fon derin analiz (Mod 1)** modunda çalıştır.

**Kullanıcı briefi:** $ARGUMENTS

## Yürütme protokolü
1. **Pre-flight (CONNECTORS.md §8):** Borsa MCP + fon-mcp canlılığını doğrula. fon-mcp
   erişilemezse holdings/TER degrade olacağını bildir.
2. **Aşama 0 (G0):** Briefi `brief-schema.json`'a oturt (mode=1; universe; fund_ids; benchmark).
   Fon belirsizse `resolve_fund` ile netleştir.
3. **Aşama 1-4:** fund_registry/holdings/nav_series (bir kez) → market_context → peer_metrics →
   quant_metrics (risk_adjusted/drawdown_var/volatility_beta/monte_carlo/style_analysis/
   fund_quality_score). Kanonik önbellek disiplini.
4. **Aşama 6-7 (G6/G7):** İki-katmanlı rapor + `rapor_lint.py` uyum kapısı. SPK feragati birebir.

## Çıktı
`<RUN_ID>/` (TFA-YYYYMMDD-<YAT|EMK|MIX>-M1-vN): JSON artefaktlar + `rapor.md` + `run_manifest.json`.

## Scope guard
Tekil hisse/tahvil → bist-analyst. Gün-içi → kapsam dışı (EOD). Kişisel al/sat → karar-destek diline çevir.
