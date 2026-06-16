---
name: fon-haritalama
description: >-
  fon-haritalama — fon kimlik + yapı + dağılım haritalama katmanı. fon-mcp ile tam portföy
  holding'leri, dağılım geçmişi, TER/gider oranı, fon akışı, kurucu/yönetici metadata;
  Borsa MCP get_fund_data ile NAV/AUM/getiri kimliği ve screen_funds ile kategori keşfi.
  fund_registry + holdings + nav_series kanonik artefaktlarının sahibi (Aşama 1, bir kez).
  USE for — fon dağılımı, portföy içeriği, TER/gider, fon büyüklüğü değişimi, yönetici kim,
  EMK fon yapısı, fon kategorisi, fon tara, fon kimliği. EN — fund holdings, allocation,
  expense ratio, fund flows, manager, fund registry. When in doubt USE.
---

# fon-haritalama — Fon Kimlik & Yapı Katmanı

**Süit:** fon-uzmani · kaynak skill (Aşama 1). > Connector/önbellek için
**[../../CONNECTORS.md](../../CONNECTORS.md)** ve
**[../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)** normatiftir.

## Ne Zaman Çağrılır
Bir fonun kimliğini, yapısını (holdings/dağılım), maliyetini (TER) ve akışını çıkarmak
gerektiğinde. Orkestratör Aşama 1'de çağırır; tek başına da fon-haritası için kullanılabilir.

## 0. Scope
YAT+EMK. **Kanonik sahip:** `fund_registry`, `holdings`, `nav_series` (CONNECTORS.md §2).
Bu skill bu artefaktları **bir kez** üretir; diğer skiller önbellekten okur.

## Adım 1 — Kimlik çözümleme
- `fon-mcp resolve_fund(query, fund_type?)` → kod/ad/kurucu/kategori/KAP.
- Belirsizse `Borsa search_symbol(market='fund')` ile çapraz-doğrula.

## Adım 2 — NAV + getiri kimliği (Borsa)
- `Borsa get_fund_data(symbol, include_performance=true, include_portfolio=true,
  start_date, end_date)` → NAV serisi (`recent_prices`/özel aralık), AUM, getiri pencereleri,
  kategori sıralaması, ISIN, kap_link. → **`nav_series`** artefaktı.

## Adım 3 — Yapı/dağılım/maliyet/akış (fon-mcp)
- `get_fund_registry(code)` → kurucu/PYŞ/strateji/risk → **`fund_registry`**.
- `get_fund_taxonomy(fund_type, code)` → kategori/alt-kategori.
- `get_allocation_snapshot(code)` + `get_allocation_history(code, start, end)` → varlık-sınıfı
  dağılımı (anlık + zaman-serili).
- `get_fund_holdings(code)` → **varlık-sınıfı** ağırlıkları → **`holdings`** (line-item yok; KAP PDF).
- `get_fund_costs(code)` → TER/yönetim ücreti.
- `get_fund_flows(code, start, end)` → net giriş/çıkış + AUM/yatırımcı trendi.

## Adım 4 — Tarama (Mod 2)
- `Borsa screen_funds(category, fund_type, sort_by, min_return_*)` → aday evren.
- `fon-mcp compare_fund_costs(fund_type, category)` → maliyet-bazlı tarama.
- `fon-mcp list_emk_funds(...)` → EMK evreni.

## G1 Kalite Kapısı (BLOKER, 5 kontrol)
1. Her fon çözüldü (kod+ad). 2. NAV serisi ≥ horizon uzunluğu. 3. holdings toplamı ≈ %100
(değilse normalize + caveat). 4. TER alındı (yoksa caveat). 5. Kategori atandı.

## Fallback (CONNECTORS.md §6)
fon-mcp timeout → Borsa `get_fund_data(include_portfolio)` (asset-class var, line-item yok,
"holdings doğrulanamadı"). Registry → KAP web_fetch ("doğrulanmamış olabilir").

## Çıktı
`fund_registry.json` · `holdings.json` · `nav_series.json` (+ allocation/costs/flows alt-blokları).
Provenance damgaları (provenance-standard §1) her sayıya eklenir.

## Referanslar
- `references/fund-taxonomy.md` (YAT+EMK SPK kategorileri)
- `references/holdings-mapping.md` (look-through, TER ayrıştırma)
- `references/data-sources.md` (TEFAS/KAP/Borsa veri-güven merdiveni)
