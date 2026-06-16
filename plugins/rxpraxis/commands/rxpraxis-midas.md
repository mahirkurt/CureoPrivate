---
description: IQVIA MIDAS 36-ülke cross-country pazar boyutu, fiyat koridoru ve LOE erozyon eğrisi. ThoughtSpot Spotter (yapı) + REST searchdata (ham değer). rxos Aşama 5b'nin tek-skill kısayolu.
argument-hint: "[ürün / molekül + opsiyonel pencere]"
---

`rxpraxis:thoughtspot-roche` çağır — IQVIA MIDAS cross-country pull.

**Hedef:** $ARGUMENTS

## Yürütme (canonical-cache-contract.md §4 + §9 + CONNECTORS.md §9)

0. **Araç yükleme (tool-manifest.json — L1):** `shared/tool-manifest.json`
   `commands.rxpraxis-midas` bloğunu pin-yükle (`ThoughtSpot Spotter:check_connectivity` +
   `MIDAS:midas_health` + `midas_metadata_search` + `midas_searchdata`). Eviction olursa
   `eviction_recovery.MIDAS` sorgusuyla yeniden yükle (mid-pipeline `tool_search` yok).

1. **Pre-flight (§9 cold-start devresi):** `MIDAS:midas_health` (token tazeliği) +
   `ThoughtSpot Spotter:check_connectivity`. `{"ok":true}` / Pong gelmezse **cold-start
   ihtimali**: HALF_OPEN, 1 retry (deploy/soğuk başlangıçta araç-keşfedilemezlik genelde
   toparlar). Kalıcıysa OPEN → dur, kullanıcıya bildir, `scan-ledger.circuit_breakers.midas`
   yaz; A5b degrade.
2. **Sabit explicit pencere belirle** (örn. `between 2024-01 and 2025-12`); tüm dalgalar paylaşır.
3. **W1-W6 dalgaları:** W1 ATC1 baseline · W2 by-country (36) · W3 per-capita (istemci-tarafı)
   · W4 yapısal-akran medyanı + gap · W5 LOE ±12ay erozyon · W6 fiyat koridoru (chf/su).
4. **Ham değer (Path B — sağlamlaştırılmış):** `get_session_updates` ham hücre döndürmez →
   REST `MIDAS:midas_searchdata`. **COMPACT-önce** (varlık/şekil kontrolü), gerçek rakam için
   **FULL**. `record_size`'ı sınırla (asla `-1`); `meta` bloğunu oku
   (`returned/total/truncated/exact/sampling`): `truncated=true` ise `record_offset` ile bilinçli
   sayfala; `exact=true` gerçek-toplam güvencesidir; `sampling=1` tam-sayımdır. FULL satırlar
   **dizi-içinde-dizi** (positional) gelir — `scripts/ts_getanswer_extractor.py` ile çıkar, sonra
   **extract-then-evict** (canonical-cache §9): distille → ham satırları düşür → diske yaz.
   **G9 no-fabrication** — okunamayan/erişilemeyen rakamı uydurma.
5. **Annualize:** `annualized_chf = raw_chf × (12 / span_months)`. Ham kümülatif CHF'i
   penetrasyona sokma.

## Çıktı
`midas_extract` JSON: `by_country[36]` (raw + annualized) + per_capita + structural_peer
+ erosion_curve + price_corridor + tr_rank. Her alan MIDAS yapısal provenance + `roche_confidential: true`.

> Roche confidential — ham GUID/session rapor gövdesinde gösterilmez (provenance-standard.md §4).

## Fallback (CONNECTORS.md §6 + §9)
ThoughtSpot `$0.00` / boş → attribute swap (Product→International Brand) → country swap →
ATC4 proxy → cube swap → 36-ülke dekompozisyon. MIDAS Worker `-32602` / metadata-only (artık
çözülü; serializer + meta + gerçek-toplam sağlamlaştırması) tekrarsa → worker regresyonu,
`wrangler tail` ile init/tools-list istisnasını incele. Açık devreler `scan-ledger.circuit_breakers`
+ Katman B İç Denetim Kaydı'na; rapor `"N/36 data-redacted"` caveat'ı taşır.
