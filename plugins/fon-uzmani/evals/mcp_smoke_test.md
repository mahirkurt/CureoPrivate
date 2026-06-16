# MCP Smoke Test — Borsa MCP + fon-mcp

Süit çalışmadan önce connector sağlık-kontrolü (CONNECTORS.md §8). Her ikisi de bağlı
olmalı; biri yoksa ilgili mod degrade çalışır.

## Borsa MCP (mevcut)
1. `Borsa get_fund_data(symbol="TI2")` → `fund.code == "TI2"`, `recent_prices[]` dolu, `price>0`.
2. `Borsa screen_funds(category="Hisse Senedi", fund_type="YAT", limit=5)` → ≥1 sonuç (ara sıra
   timeout olabilir — fallback: fon-mcp `compare_fund_costs`).
3. `Borsa get_index_data(symbol="XU100")` → benchmark serisi.
4. `Borsa get_bond_yields` → risksiz oran.

**Beklenen:** NAV/getiri/benchmark/risksiz oran alınabiliyor. Alınamıyorsa → "canlı NAV
varsayma" degrade (rapor §Sınırlar).

## fon-mcp (yeni)
1. `fon_mcp_health` → `tefas_reachable: true`, `cache_namespace: "fon:v1"`.
2. `resolve_fund(query="TI2")` → matches[].code == "TI2".
3. `get_fund_costs(code="TI2")` → `ter_annual_pct` veya `management_fee_pct` dolu.
4. `get_allocation_snapshot(code="TI2")` → `allocations[]` (varlık-sınıfı %).

**Beklenen:** holdings/TER/dağılım alınabiliyor. Alınamıyorsa → Borsa
`get_fund_data(include_portfolio)` fallback (asset-class var, line-item yok; "holdings
doğrulanamadı").

## Edge-IP / auth (fon-mcp deploy sonrası)
- `curl $BASE/health` → `fon-mcp ok`
- `curl -X POST $BASE/mcp` (bearersiz) → 401
- `curl $BASE/.well-known/oauth-authorization-server | jq .code_challenge_methods_supported` → `["S256"]`
