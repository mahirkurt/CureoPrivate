---
name: fon-haritalama
description: >-
  fon-haritalama — fon kimlik + yapı + dağılım haritalama katmanı. fon-mcp ile **varlık-sınıfı**
  düzeyi holdings, dağılım geçmişi, **TER azami sınır (üst-sınır) + yönetim ücreti**, fon akışı,
  kurucu (PYŞ kısa adı, ünvandan türetilmiş); Borsa MCP get_fund_data ile NAV/AUM/getiri/ISIN
  kimliği ve screen_funds ile kategori keşfi. fund_registry + holdings + nav_series kanonik
  artefaktlarının sahibi (Aşama 1, bir kez). USE for — fon dağılımı, portföy içeriği, TER üst-sınır
  / gider, fon büyüklüğü değişimi, kurucu PYŞ, EMK fon yapısı, fon kategorisi, fon tara, fon kimliği.
  EN — fund holdings (asset-class), allocation, TER ceiling, fund flows, founder, fund registry.
  When in doubt USE.
version: 1.3.0
last_updated: 2026-06-20
changelog:
  - "1.3.0 (2026-06-20): fon-mcp canlı tool yüzeyiyle hizalandı — get_fund_registry artık founder (PYŞ kısa adı ünvandan), category, AUM, investor_count, category_rank, market_share, last_price döner (ISIN/strateji=null → KAP). get_fund_costs gerçek management_fee_pct + ter_ceiling_pct (ÜST-SINIR, gerçekleşen DEĞİL; fonYonetimBazliBilgiGetir). get_fund_holdings varlık-sınıfı düzeyi (line-item KAP'a). compare_fund_costs sort_by destekli."
  - "1.2.0 (2026-06-16): Fon Uzmanı süiti — frontmatter sürüm/changelog beyanı (denetim D1/D10), açık Kapsam Dışı bölümü (D4), quant yüksek-CC fonksiyon refaktörü + docstring (D5). Connector'lar .mcp.json ile paketli (borsa + fon-mcp)."
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
- `fon-mcp resolve_fund(query, fund_type?)` → `code/name/aum/kap_link`. **Kurucu/kategori
  dönmez** (Adım 3'te `get_fund_registry`'den gelir).
- Belirsizse `Borsa search_symbol(market='fund')` ile çapraz-doğrula.

## Adım 2 — NAV + getiri kimliği (Borsa)
- `Borsa get_fund_data(symbol, include_performance=true, include_portfolio=true,
  start_date, end_date)` → NAV serisi (`recent_prices`/özel aralık), AUM, getiri pencereleri,
  kategori sıralaması, **ISIN**, kap_link. → **`nav_series`** artefaktı.
- Borsa erişilemezse `fon-mcp get_fund_flows(code, start, end)` NAV/shares/AUM zaman-serisini
  yedek omurga olarak sağlar (ISIN/getiri pencereleri eksik kalır → caveat).

## Adım 3 — Yapı/dağılım/maliyet/akış (fon-mcp)
- `get_fund_registry(code, fund_type?)` → `name/category/aum/investor_count/category_rank/
  category_fund_count/market_share/last_price/founder` (PYŞ kısa adı, fon ünvanından türetilmiş)
  + `kap_link`. **ISIN ve strateji `null`** (KAP fon sayfası gerekir). → **`fund_registry`**.
- `get_fund_taxonomy(fund_type, code)` → tek-fon kategorisi (sayım yok); evren-geneli
  kategori sayımı için Borsa `screen_funds`.
- `get_allocation_snapshot(code, fund_type?)` + `get_allocation_history(code, start, end,
  fund_type?)` → varlık-sınıfı dağılımı (anlık + zaman-serili; ~30 kodlu kolon → TR etiket).
- `get_fund_holdings(code, fund_type?)` → **varlık-sınıfı ağırlıkları** → **`holdings`**.
  Menkul-bazlı (line-item) holdings TEFAS public API'sinde YOK; gerekiyorsa KAP aylık
  portföy raporu PDF.
- `get_fund_costs(code, fund_type?)` → `management_fee_pct` (yıllık yönetim ücreti) + **`ter_ceiling_pct`
  (azami toplam gider oranı — ÜST SINIR; gerçekleşen TER DEĞİL)** + `umbrella` + `founder_code`
  ([fon-mcp / fonYonetimBazliBilgiGetir]). Gerçekleşen TER için KAP KIID.
- `get_fund_flows(code, start, end, fund_type?)` → net giriş/çıkış (Δshares×midNAV) +
  AUM/yatırımcı trendi.

## Adım 4 — Tarama (Mod 2)
- `Borsa screen_funds(category, fund_type, sort_by, min_return_*)` → aday evren (getiri-sıralı).
- `fon-mcp compare_fund_costs(fund_type, category?, sort_by?, limit?)` → **TER üst-sınır
  bazlı tarama** (varsayılan `sort_by=ter_ceiling_pct`); kategori filtresi opsiyonel.
- `fon-mcp get_flow_leaders(fund_type, limit?)` → AUM proxy sıralama.
- `fon-mcp list_emk_funds(founder?, limit?)` → EMK evreni (founder = ünvan substring filtresi).

## G1 Kalite Kapısı (BLOKER, 5 kontrol)
1. Her fon çözüldü (kod+ad). 2. NAV serisi ≥ horizon uzunluğu. 3. holdings toplamı ≈ %100
(değilse normalize + caveat). 4. TER üst-sınırı ve yönetim ücreti alındı (alınmadıysa caveat;
gerçekleşen TER her durumda KAP KIID gerektirir — rapor bunu açıkça etiketler). 5. Kategori atandı.

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

## Kapsam Dışı
ISIN / strateji / tam tüzel ünvan / gerçekleşen TER (KAP KIID gerekir); menkul-bazlı
(line-item) holdings — yalnız varlık-sınıfı düzeyi (KAP aylık portföy raporu PDF gerekir);
gerçek-zamanlı / gün-içi NAV; portföy yöneticisi kimliği (TEFAS yeni API'sinde yok — KAP
fon sayfası gerekir).
