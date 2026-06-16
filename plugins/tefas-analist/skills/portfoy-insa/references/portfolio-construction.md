# portfolio-construction.md — Portföy İnşası Yöntemleri

`scripts/portfolio_opt.py` (quant-analiz). Aday fon getiri matrisi + kovaryans üzerinden.

## Yöntemler
| Yöntem | Mantık | Ne zaman |
|---|---|---|
| **Min-variance** | `w ∝ Σ⁻¹·1`, normalize | en düşük toplam risk |
| **Max-Sharpe (tanjant)** | `w ∝ Σ⁻¹(μ − r_f·1)` | risk-getiri optimum |
| **Risk-parity** | risk katkıları eşitlenir (RC_i eşit) | dengeli risk dağıtımı |
| **HRP** | korelasyon→mesafe→hiyerarşik kümeleme→özyinelemeli bölme | tahmin hatasına dayanıklı, küçük N |

Long-only varsayılan; simpleks-projeksiyonu negatif ağırlıkları engeller.

## Sayısal sağlamlık
Non-PD kovaryans → `nearest_pd` ridge. N>T → diyagonale shrink + uyarı. Çıktıda `effective_n`
(1/Σw²) çeşitlendirme ölçer. Varsayılan motor saf-stdlib; `--engine numpy` opsiyonel.

## EMK özgü kurallar
- EMK alt-tip kısıtları (örn. agresif/dengeli/muhafazakâr) tahsis bandını belirler.
- FİGO/FTGK maliyetleri net-getiri beklentisine dahil edilir (cost_analysis).
- OKS uygunluğu kullanıcı bağlamına göre not edilir.

## Çıktı
Yöntem-başına ağırlık + beklenen yıllık getiri/vol/Sharpe + etkin fon sayısı →
`optimized_portfolio`. Her ağırlık gerekçeli; SPK feragati + senaryo ile sarılır.
