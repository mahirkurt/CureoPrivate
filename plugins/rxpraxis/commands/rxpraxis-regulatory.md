---
description: Bir molekül/ürün için TR regülatuar snapshot — TİTCK kanonik dosya (master + holder + ATC/SNOMED + fiyat + eşdeğer grup) + üç-otorite (FDA/EMA/MHRA/PMDA) durumu. rxos Aşama 2'nin tek-skill kısayolu.
argument-hint: "[INN / barkod / ATC kodu / holder]"
---

`rxpraxis:pharmapatent` Mod 13 (TR_REGULATORY_FLOW) + `rxpraxis:pharmaintel` Regulatory çağır.

**Hedef:** $ARGUMENTS

## Yürütme

0. **Araç yükleme (tool-manifest.json — L1):** `shared/tool-manifest.json`
   `commands.rxpraxis-regulatory` bloğunu pin-yükle. `search_drugs` çakışması →
   `TİTCK:search_drugs`, ASLA AdisInsight'ınki. Pre-flight: §8 + §9.
   Boru hattı ortasında `tool_search` YAPMA.

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
4. **Mevzuat (soru gerektiriyorsa):** `Mevzuat:search_all_mevzuat` ile kanun/yönetmelik
   ve KAYSİS kurum belgelerini birlikte keşfet. Kurum/tür filtresi gerekiyorsa
   `search_kaysis_institutions` + `list_kaysis_types` → `search_kaysis`; seçilen kaydı
   `get_kaysis_detail` → sınırlı `get_kaysis_text` ile oku. mevzuat.gov.tr kaydında
   dönen no/tür/tertip ile `get_mevzuat_detail` + `get_mevzuat_content` kullan.
   İki kimlik alanını dönüştürme; kaynak başına `coverage`, kesilme ve OCR boşluklarını
   bildir (CONNECTORS.md §1.A.1). Bir kaynağın erişilememesi "mevzuat yok" demek değildir.

## Çıktı
`titck_canonical` JSON + okunabilir TR ürün kartı. Her veri noktası provenance damgalı
(`[TİTCK MCP / <tool> / <ISO>]` — provenance-standard.md §1).

## Fallback (CONNECTORS.md §6 + §9 devre-kesici)
TİTCK 5xx/timeout → cached registry → tekil barcode → web fetch (**ikinci bir TİTCK katmanı
YOK**; Worker cache 2026-08-02'de emekli). 401 = `${TITCK_MCP_API_KEY}` çözülmemiş → kullanıcıya
bildir; "No approval received" = onay verilmedi, başka adla yeniden deneme (§9). Her ham
pull **extract-then-evict** (canonical-cache §9): distille → ham hâli düşür → diske yaz;
`scan-ledger` checkpoint güncelle. Açık devreler ledger'a + Katman B İç Denetim Kaydı'na damgalanır.
