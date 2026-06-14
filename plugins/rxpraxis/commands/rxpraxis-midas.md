---
description: IQVIA MIDAS 36-ülke cross-country pazar boyutu, fiyat koridoru ve LOE erozyon eğrisi. ThoughtSpot Spotter (yapı) + REST searchdata (ham değer). rxos Aşama 5b'nin tek-skill kısayolu.
argument-hint: "[ürün / molekül + opsiyonel pencere]"
---

`rxpraxis:thoughtspot-roche` çağır — IQVIA MIDAS cross-country pull.

**Hedef:** $ARGUMENTS

## Yürütme (canonical-cache-contract.md §4)
1. **Pre-flight:** `check_connectivity` → Pong gelmezse dur, kullanıcıya bildir (MIDAS erişimi yok).
2. **Sabit explicit pencere belirle** (örn. `between 2024-01 and 2025-12`); tüm dalgalar paylaşır.
3. **W1-W6 dalgaları:** W1 ATC1 baseline · W2 by-country (36) · W3 per-capita (istemci-tarafı)
   · W4 yapısal-akran medyanı + gap · W5 LOE ±12ay erozyon · W6 fiyat koridoru (chf/su).
4. **Ham değer (Path B):** `get_session_updates` ham hücre döndürmez → REST `searchdata`
   (midas-mcp Worker) veya native export. **G9 no-fabrication** — okunamayan rakamı uydurma.
5. **Annualize:** `annualized_chf = raw_chf × (12 / span_months)`. Ham kümülatif CHF'i
   penetrasyona sokma.

## Çıktı
`midas_extract` JSON: `by_country[36]` (raw + annualized) + per_capita + structural_peer
+ erosion_curve + price_corridor + tr_rank. Her alan MIDAS yapısal provenance + `roche_confidential: true`.

> Roche confidential — ham GUID/session rapor gövdesinde gösterilmez (provenance-standard.md §4).
