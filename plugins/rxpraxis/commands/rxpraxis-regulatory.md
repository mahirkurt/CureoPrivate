---
description: Bir molekül/ürün için TR regülatuar snapshot — TİTCK kanonik dosya (master + holder + ATC/SNOMED + fiyat + eşdeğer grup) + üç-otorite (FDA/EMA/MHRA/PMDA) durumu. rxos Aşama 2'nin tek-skill kısayolu.
argument-hint: "[INN / barkod / ATC kodu / holder]"
---

`rxpraxis:pharmapatent` Mod 13 (TR_REGULATORY_FLOW) + `rxpraxis:pharmaintel` Regulatory çağır.

**Hedef:** $ARGUMENTS

## Yürütme

0. **Araç yükleme (tool-manifest.json — L1):** `shared/tool-manifest.json`
   `commands.rxpraxis-regulatory` bloğunu pin-yükle. `search_drugs` çakışması →
   `TİTCK Cache:search_drugs` (raw fallback), ASLA AdisInsight'ınki. Pre-flight: §8 + §9
   (TİTCK Cache approval-gate → raw failover). Boru hattı ortasında `tool_search` YAPMA.

   > **AdisInsight-erken / ATC-ÇÖZ kuralı (kritik):** ATC kodunu **TAHMİN ETME**. Molekülün
   > gerçek WHO ATC'sini önce `AdisInsight:get_drug` ile çöz, sonra `get_atc_class_summary`'yi
   > **doğru** kodla çağır. (Üç koşumda ATC iki kez yanlış tahmin edildi — örn. D01AE22 TİTCK'te
   > **naftifin**, efinaconazole'ün gerçek WHO ATC'si D01AC. Yanlış kod → yanlış sınıf okuması.)

1. **TİTCK kanonik dosya (pharmapatent Mod 13):** `search_drugs` (FTS5 smart) + `get_drug`
   + `get_drug_snomed_profile` + `get_holder_portfolio` + `get_atc_class_summary`
   + `find_first_in_class` (+ derin mod `get_price_history`). `titck_canonical` artefaktı üret
   (canonical-cache-contract.md §3). **TİTCK MCP'yi bir kez** çağır.
2. **Eşdeğer/biyobenzer grup:** `find_equivalent_products_by_substance` + doygunluk skoru.
3. **Üç-otorite (pharmaintel):** FDA Drugs@FDA + EMA EPAR + MHRA + PMDA.
4. **Mevzuat (opsiyonel):** ilgili SMK/yönetmelik tam metni (Mevzuat MCP).

## Çıktı
`titck_canonical` JSON + okunabilir TR ürün kartı. Her veri noktası provenance damgalı
(`[TİTCK MCP / <tool> / <ISO>]` — provenance-standard.md §1).

## Fallback (CONNECTORS.md §6 + §9 devre-kesici)
TİTCK Cache "No approval received" / 5xx → ham `TİTCK:*` raw'a **anında failover** (§9; veri
bayt-aynı). Worker tamamen erişilemezse cached registry → tekil barcode → web fetch. Her ham
pull **extract-then-evict** (canonical-cache §9): distille → ham hâli düşür → diske yaz;
`scan-ledger` checkpoint güncelle. Açık devreler ledger'a + Katman B İç Denetim Kaydı'na damgalanır.
