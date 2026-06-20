# MCP Smoke Test — Borsa MCP + fon-mcp

Süit çalışmadan önce connector sağlık-kontrolü (CONNECTORS.md §8). Her ikisi de bağlı
olmalı; biri yoksa ilgili mod degrade çalışır.

## Borsa MCP (`https://borsamcp.fastmcp.app/mcp`)
1. `Borsa get_fund_data(symbol="TI2")` → `fund.code == "TI2"`, `recent_prices[]` dolu, `price>0`.
2. `Borsa screen_funds(category="Hisse Senedi", fund_type="YAT", limit=5)` → ≥1 sonuç (ara sıra
   timeout olabilir — fallback: fon-mcp `compare_fund_costs`).
3. `Borsa get_index_data(symbol="XU100")` → benchmark serisi.
4. `Borsa get_bond_yields` → risksiz oran.

**Beklenen:** NAV/getiri/benchmark/risksiz oran alınabiliyor. Alınamıyorsa → fon-mcp
`get_fund_flows` NAV yedek omurga (getiri pencereleri/ISIN eksik kalır — caveat).

## fon-mcp (`https://fon-mcp.cureonics.workers.dev/mcp`)

### Sağlık + envanter
1. `fon_mcp_health` → bekle:
   - `tefas_reachable: true`
   - `tefas_status: 200`
   - `api: "fonBilgiGetir/fonGnlBlgSiraliGetir/dagilimSiraliGetirT (yeni resmî API)"`
   - `cache_namespace: "fon:v4"` (veya sonraki bump).
2. `tools/list` → tam **12 araç**, isimler bire-bir:
   `resolve_fund`, `get_fund_registry`, `get_fund_taxonomy`, `get_allocation_snapshot`,
   `get_allocation_history`, `get_fund_holdings`, `get_fund_costs`, `compare_fund_costs`,
   `get_fund_flows`, `get_flow_leaders`, `list_emk_funds`, `fon_mcp_health`. Eksik/fazla
   araç → süit sürümü ile fon-mcp deploy uyuşmazlığı; çalıştırma durdurulur.

### Tool-bazlı assertion (canlı kontrat)
3. `resolve_fund(query="TI2")` → `matches[].code == "TI2"`, `aum > 0`, `kap_link` mevcut.
   **Bekleme:** `founder`/`category` alanları **DÖNMEZ** (Adım 3'te `get_fund_registry`'den
   gelir).
4. `get_fund_registry(code="TI2", fund_type="YAT")` →
   `founder == "İŞ PORTFÖY"` (PYŞ kısa adı, ünvandan türetilmiş),
   `category == "Hisse Senedi Fonu"`, `aum > 0`, `category_rank ≥ 1`,
   `market_share > 0`, `last_price > 0`. **Bekleme:** `isin == null` ve `strategy == null`
   (KAP fon sayfası gerektirir). `kap_link` mevcut.
5. `get_fund_costs(code="TI2", fund_type="YAT")` →
   `management_fee_pct > 0`, **`ter_ceiling_pct > management_fee_pct`** (üst-sınır =
   yönetim ücreti + diğer giderler için tavan), `umbrella` dolu, `founder_code` dolu,
   `source == "TEFAS fonYonetimBazliBilgiGetir"`. **Bekleme:** rapor yazılırken bu
   sayı "(üst-sınır)" etiketiyle gösterilir; "gerçekleşen TER" iddiası YASAK.
6. `get_allocation_snapshot(code="TI2", fund_type="YAT")` → `allocations[]` (varlık-sınıfı
   etiketli, `code` + TR `instrument` + `weight_pct`), toplam ≈ %100.
7. `get_fund_holdings(code="TI2", fund_type="YAT")` → `level == "asset-class"`, `holdings[]`
   varlık-sınıfı düzeyi. **Bekleme:** menkul-bazlı (line-item) yok — `note` "KAP portföy
   raporu gerekir" diyor.
8. `get_fund_flows(code="TI2", start_date="<son 7 iş günü>", end_date="<bugün>",
   fund_type="YAT")` → `series[]` günlük NAV + shares_outstanding + investor_count + aum;
   `derived[]` Δshares × midNAV net giriş/çıkış. **Bekleme:** ≥3 nokta.
9. `compare_fund_costs(fund_type="YAT", limit=3)` → 3 fon, `sorted_by ==
   "ter_ceiling_pct"`, en küçük ter_ceiling_pct ilk sırada.
10. `get_flow_leaders(fund_type="YAT", limit=3)` → AUM-sıralı 3 fon.

### Degrade davranışı
fon-mcp erişilemezse:
- Holdings/allocation: Borsa `get_fund_data(include_portfolio)` (asset-class var, line-item
  yok; caveat "holdings doğrulanamadı").
- TER: yalnız KAP KIID kalır; rapor "TER üst-sınırı alınamadı" caveatıyla devam eder.
- NAV: Borsa `get_fund_data` zaten birincil; tam ters fallback için `get_fund_flows` yedek
  omurga.

## Edge-IP / auth (fon-mcp deploy sonrası)
- `curl $BASE/health` → `fon-mcp ok` (200).
- `curl -X POST $BASE/mcp` (Bearer'sız, `Accept: application/json, text/event-stream`) → 401.
- `curl $BASE/.well-known/oauth-authorization-server | jq .code_challenge_methods_supported`
  → `["S256"]`.
- Bearer = `MCP_API_KEY` (Doppler `cureohub/dev_personal` → `FON_MCP_MCP_API_KEY`).
