---
description: Çoklu-fon karşılaştırma (Mod 3) — 2-5 fonu kimlik/dağılım/risk-getiri/korelasyon ekseninde yan yana → karar-destek karşılaştırma raporu. SPK yatırım danışmanlığı değildir.
argument-hint: "[2-5 fon kodu — örn. 'AFA, TI2, IPB']"
---

`fon-uzmani:fon-analiz-orkestratoru` orkestratörünü **çoklu-fon karşılaştırma (Mod 3)** modunda çalıştır.

**Kullanıcı briefi:** $ARGUMENTS

## Yürütme protokolü
1. **Pre-flight:** Borsa MCP + fon-mcp canlılığı.
2. **Aşama 0 (G0):** Briefi oturt (mode=3; fund_ids[2-5]; ortak benchmark).
3. **Aşama 1-3:** Her fon için fund_registry/holdings/nav_series + market_context + quant_metrics;
   `volatility_beta` ile fon-fon korelasyon matrisi; peer_metrics ile kategori konumu.
4. **Aşama 6-7:** Yan yana karşılaştırma tablosu + korelasyon + uyum kapısı.

## Çıktı
`<RUN_ID>` (…-M3-vN): fonlar × metrik tablosu + korelasyon + `rapor.md`.

## Scope guard
Tekil hisse karşılaştırması → bist-analyst. "Hangisini alayım" → karar-destek: güçlü/zayıf yönler + senaryo.
