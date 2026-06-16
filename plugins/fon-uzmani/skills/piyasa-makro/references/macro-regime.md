# macro-regime.md — TCMB Makro Rejim Sınıflandırma

`scripts/fund_monitor.py regime_tag` ile hesaplanır; piyasa-makro `market_context.regime`'e yazar.

## Sinyaller (Borsa get_evds_data/get_macro_data/get_fx_data)
- **Faiz değişimi (bps):** ≤−25 gevşeme (+1) · ≥+25 sıkılaştırma (−1).
- **Enflasyon (YoY %):** >50 yüksek (−1) · <25 ılımlı (+1).
- **Kur değişimi (%):** >5 baskı (−1).

## Rejim
`skor ≥ +1` → **Risk-Açık** · `skor ≤ −1` → **Risk-Kapalı** · aksi → **Nötr**.

## Kategori duyarlılığı (karar-destek bağlamı, tahsis emri değil)
| Kategori | Risk-Açık | Risk-Kapalı |
|---|---|---|
| Hisse | rüzgar arkadan | rüzgar önden |
| Borçlanma | nötr/hafif önden | faiz inişinde arkadan |
| Para piyasası | düşük duyarlılık | savunmacı sığınak |
| Kıymetli maden | değişken | sığınak talebi |
| Karma/Değişken | tahsise bağlı | tahsise bağlı |

## İlke
Rejim **bağlam** sağlar, tahsis emri vermez. Rejim değişimi izleme skili için tetikleyicidir
(`rejim_degisimi` alarmı). Karar-destek; yatırım tavsiyesi değildir.
