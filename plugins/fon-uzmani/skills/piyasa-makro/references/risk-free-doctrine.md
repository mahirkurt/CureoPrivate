# risk-free-doctrine.md — Risksiz Oran Doktrini (TR)

Sharpe/Sortino/Treynor paydası ve Jensen alfası için risksiz oran seçimi.

## Seçim kuralı
| Fon ufku / tipi | Risksiz oran | Borsa kaynağı |
|---|---|---|
| Nakit-benzeri, para piyasası | TCMB O/N veya politika faizi | `get_macro_data`/`get_evds_data` |
| Kısa-orta vade | Kısa gösterge tahvil getirisi | `get_bond_yields` |
| Uzun ufuk | 2y/5y gösterge tahvil | `get_bond_yields` |

## İlkeler
- Oran **yıllık ondalık** olarak normalize edilir (%45 → 0.45); günlüğe çevrim
  `(1+r_f)^(1/ppy)−1`.
- Kullanılan oran ve kaynağı raporlanır (`conventions.risk_free_source`).
- Yüksek-enflasyon ortamında nominal risksiz oran yüksektir → Sharpe negatif çıkabilir;
  bu geçerli bir sonuçtur, reel çerçeve (TÜFE) ile birlikte yorumlanır.
- Risksiz oran alınamazsa rf=0 ile hesaplanır + caveat (Sharpe/Sortino abartılı görünebilir).

`market_context.risk_free` alanına yazılır; quant-analiz buradan okur.
