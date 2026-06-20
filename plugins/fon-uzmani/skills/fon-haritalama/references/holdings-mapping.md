# holdings-mapping.md — Holdings & TER Haritalama

## Holdings kaynakları (öncelik sırası)
1. `fon-mcp get_fund_holdings(code)` — **varlık-sınıfı** düzeyi ağırlıklar (birincil). Menkul-bazlı
   (line-item) holdings TEFAS public API'sinde YOK; yalnız KAP aylık portföy raporu PDF'inde.
2. `fon-mcp get_allocation_snapshot/history` — varlık-sınıfı dağılımı (anlık + zaman-serili).
3. Borsa `get_fund_data(include_portfolio=true)` — asset-class düzeyi (fallback).

## Normalizasyon
- Ağırlıklar %/ondalık otomatik algılanır; toplam ~%100'e normalize edilir, sapma caveat'lanır.
- ISIN öncelikli eşleme; yoksa normalize-edilmiş ad (`concentration.py _norm`).

## Look-through
Hisse fonunun ağırlıklı BIST holding'leri için tekil-hisse derinliği gerekiyorsa
`bist-analyst` plugin'i çağrılabilir (composes_with). Fon-düzeyi ↔ hisse-düzeyi köprüsü.

## TER / gider ayrıştırma
- Birincil: `fon-mcp get_fund_costs(code, fund_type?)` → `management_fee_pct` (yıllık yönetim ücreti)
  + **`ter_ceiling_pct` (azami toplam gider oranı — ÜST SINIR)** + `umbrella` + `founder_code`.
  Kaynak `fonYonetimBazliBilgiGetir`.
- **Üst-sınır ≠ gerçekleşen TER.** Gerçekleşen yıllık TER yalnız KAP Yatırımcı Bilgi Formu'nda
  (KIID) yayımlanır; rapor her TER sayısının yanına etiket koyar: "(üst-sınır)" veya
  "(gerçekleşen, KAP KIID)".
- EMK: FİGO/FTGK (EGM kaynağı — fon-mcp gelecek alanı; şu an yalnız üst-sınır mevcut).
- TER üst-sınır alınamazsa caveat; `cost_analysis.py` ile net-getiri etkisi her iki taban
  (üst-sınır + KIID gerçekleşen) için ayrı modellenebilir.

## Quant'a aktarım
`holdings` → `concentration.py` (HHI, top-N, overlap, drift). `allocation_history` →
stil-drift girdisi. TER → `cost_analysis.py` + `fund_quality_score.py` maliyet alt-skoru.
