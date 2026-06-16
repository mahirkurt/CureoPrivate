# risk-adjusted-returns.md — Riske Göre Düzeltilmiş Getiri Formülleri

Tümü `scripts/risk_adjusted.py` tarafından hesaplanır. Günlük NAV getirisi `r_t`, yıllıklama
faktörü `ppy` (252/52/12, tarih ekseninden), risksiz oran `r_f` (yıllık → günlük
`(1+r_f)^(1/ppy)-1`).

| Metrik | Formül | Not |
|---|---|---|
| **Sharpe** | `(mean(r) - r_f^d) / std(r) · √ppy` | Toplam risk başına fazla getiri |
| **Sortino** | `(mean(r) - MAR^d) / downside_dev(r,MAR) · √ppy` | Yalnız aşağı-yön cezalandırılır; MAR varsayılan = r_f |
| **Calmar** | `CAGR / |maxDD|` | Geri çekilme başına büyüme |
| **Information Ratio** | `mean(r - r_b) / TE · √ppy` | TE = std(r - r_b); aktif yönetim ölçer |
| **Tracking Error** | `std(r - r_b) · √ppy` | Benchmark'tan sapma |
| **Treynor** | `(yıllık getiri - r_f) / β` | Sistematik risk başına |
| **Omega** | `Σmax(r-τ,0) / Σmax(τ-r,0)` | Eşik üstü/altı oranı |

## Risksiz oran seçimi (TR)
- Nakit-benzeri/para piyasası fonu → TCMB O/N veya politika faizi.
- Daha uzun ufuk → gösterge tahvil getirisi (`Borsa get_bond_yields`).
- Kaynak ve değer raporlanır (`conventions.risk_free_source`).

## Yıllıklama konvansiyonu
Günlük NAV → `√252`. Haftalık → `√52`, aylık → `√12`. Faktör tarih ekseninden çıkarılır;
her çıktıda `ppy`/`ppy_basis` raporlanır. Karar-destek; yatırım tavsiyesi değildir.

## Edge-case
σ=0 → oran `null` + note. n<30 → düşük güven bayrağı. |maxDD|=0 → Calmar `null`. Benchmark
örtüşmesi yok → IR/Treynor `null`.
