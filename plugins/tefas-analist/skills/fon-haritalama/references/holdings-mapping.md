# holdings-mapping.md — Holdings & TER Haritalama

## Holdings kaynakları (öncelik sırası)
1. `fon-mcp get_fund_holdings(code)` — line-item/asset-class ağırlıkları (birincil).
2. `fon-mcp get_allocation_snapshot/history` — varlık-sınıfı dağılımı (zaman-serili).
3. Borsa `get_fund_data(include_portfolio=true)` — asset-class düzeyi (fallback; line-item yok).

## Normalizasyon
- Ağırlıklar %/ondalık otomatik algılanır; toplam ~%100'e normalize edilir, sapma caveat'lanır.
- ISIN öncelikli eşleme; yoksa normalize-edilmiş ad (`concentration.py _norm`).

## Look-through
Hisse fonunun ağırlıklı BIST holding'leri için tekil-hisse derinliği gerekiyorsa
`bist-analyst` plugin'i çağrılabilir (composes_with). Fon-düzeyi ↔ hisse-düzeyi köprüsü.

## TER / gider ayrıştırma
- Birincil: `fon-mcp get_fund_costs(code)` → TGO/TER + yönetim ücreti.
- EMK: FİGO/FTGK (EGM kaynağı — fon-mcp gelecek alanı).
- TER eksikse caveat; `cost_analysis.py` ile net-getiri etkisi modellenir.

## Quant'a aktarım
`holdings` → `concentration.py` (HHI, top-N, overlap, drift). `allocation_history` →
stil-drift girdisi. TER → `cost_analysis.py` + `fund_quality_score.py` maliyet alt-skoru.
