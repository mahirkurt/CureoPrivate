---
name: piyasa-makro
description: >-
  piyasa-makro — benchmark + risksiz oran + makro rejim katmanı. Borsa MCP ile
  get_index_data (BIST/sektör benchmark serileri), get_bond_yields (risksiz oran — riske
  göre düzeltilmiş getiri paydası), get_fx_data (USDTRY/EURTRY), get_evds_data/get_macro_data
  (TCMB makro rejim: faiz, kur, enflasyon). market_context kanonik artefaktının sahibi;
  quant-analiz beta/alfa/aktif-getiri için buradan okur. USE for — benchmark karşılaştırma,
  gösterge endeks, risksiz oran, TCMB rejim, faiz/kur/enflasyon ortamı, rejim değişimi,
  makro bağlam. EN — benchmark, risk-free rate, TCMB macro regime, regime shift. When in doubt USE.
---

# piyasa-makro — Benchmark + Risksiz Oran + Makro Rejim

**Süit:** fon-uzmani · kaynak skill (Aşama 2). > Connector/önbellek için
**[../../CONNECTORS.md](../../CONNECTORS.md)** normatiftir.

## Ne Zaman Çağrılır
Fon-dışı bağlam (benchmark serisi, risksiz oran, makro rejim) gerektiğinde. Orkestratör
Aşama 2'de çağırır. **Kanonik sahip:** `market_context` (CONNECTORS.md §2).

## Adım 1 — Benchmark serisi
Fon kategorisine uygun benchmark seç (`references/benchmark-selection.md`): hisse fonu →
XU100/XUTUM; borçlanma → KYD endeksleri/tahvil; karma → karma. `Borsa get_index_data(symbol,
start, end)` → NAV penceresiyle hizalanmış seri.

## Adım 2 — Risksiz oran
`Borsa get_bond_yields` (gösterge tahvil) veya O/N politika faizi (`references/
risk-free-doctrine.md`): nakit-benzeri için O/N, daha uzun ufuk için gösterge tahvil.
Sharpe/Sortino/Treynor paydası bu orandır.

## Adım 3 — Makro rejim
`Borsa get_evds_data`/`get_macro_data` → faiz değişimi, TÜFE (YoY), kur. `get_fx_data` →
USDTRY/EURTRY. Rejim etiketi (`references/macro-regime.md`): Risk-Açık / Nötr / Risk-Kapalı
+ fon kategorisi duyarlılığı. (Hesap için `../quant-analiz/scripts/fund_monitor.py regime_tag`
kullanılabilir.)

## G2 Kalite Kapısı (4 kontrol, 1 WARN)
1. Benchmark serisi NAV penceresiyle hizalı. 2. Risksiz oran alındı (Sharpe paydası).
3. Makro rejim etiketi üretildi. 4. (WARN) FX bağlamı.

## Çıktı
`market_context.json`: {benchmark:{symbol, series}, risk_free:{annual, source}, regime:{tag,
drivers}, fx:{usdtry_change}}. Provenance: `[Borsa MCP / get_index_data / <as-of>]` vb.

## Referanslar
- `references/benchmark-selection.md` (kategori→benchmark eşlemesi)
- `references/risk-free-doctrine.md` (TCMB gösterge tahvil / O-N seçimi)
- `references/macro-regime.md` (rejim sınıflandırma + kategori duyarlılığı)
