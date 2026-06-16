---
description: Fon izleme / sürekli gözetim (Mod 5) — fon listesi veya önceki snapshot'tan "ne değişti" deltası (rejim/stil/drawdown/TER/KAP alarmı) üretir. SPK yatırım danışmanlığı değildir.
argument-hint: "[fon listesi / önceki snapshot — örn. 'AFA, TI2, IPB' veya bir fund_state.json]"
---

`fon-uzmani:fon-analiz-orkestratoru` orkestratörünü **izleme/gözetim (Mod 5)** modunda çalıştır.

**Kullanıcı briefi:** $ARGUMENTS

## Yürütme protokolü
1. **Pre-flight:** Borsa MCP + fon-mcp canlılığı.
2. **Aşama 0 (G0):** Briefi oturt (mode=5; fund_ids veya önceki snapshot; thresholds opsiyonel).
3. **Aşama 1+ (delta):** Her fon için güncel snapshot (`fund-state-schema.json`) — last_nav/aum/ter/
   quant_snapshot/style_fingerprint/regime_tag/open_kap. fon-haritalama + quant-analiz delta alanları.
4. **Değişim:** `fund_monitor.py change_points` → drawdown_esigi/vol_sicramasi/stil_sapmasi/
   ter_artisi/rejim_degisimi/kap_duyurusu + alarm kompoziti.
5. **Aşama 6'-7:** "Ne değişti" raporu (önceliğe göre) + uyum kapısı.

## Çıktı
`<RUN_ID>` (…-M5-vN): `fund_state.json` (yeni snapshot) + `watchlist_diff.json` + `rapor.md`.

## Scope guard
Tam yeniden-analiz isteniyorsa /fon-analiz. Kişisel al/sat → karar-destek diline çevir.
