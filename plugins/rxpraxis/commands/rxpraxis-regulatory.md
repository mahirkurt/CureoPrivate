---
description: Bir molekül/ürün için TR regülatuar snapshot — TİTCK kanonik dosya (master + holder + ATC/SNOMED + fiyat + eşdeğer grup) + üç-otorite (FDA/EMA/MHRA/PMDA) durumu. rxos Aşama 2'nin tek-skill kısayolu.
argument-hint: "[INN / barkod / ATC kodu / holder]"
---

`rxpraxis:pharmapatent` Mod 13 (TR_REGULATORY_FLOW) + `rxpraxis:pharmaintel` Regulatory çağır.

**Hedef:** $ARGUMENTS

## Yürütme
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

## Fallback
TİTCK MCP timeout → CONNECTORS.md §6 zinciri (cached registry → tekil barcode → web fetch),
caveat damgası.
