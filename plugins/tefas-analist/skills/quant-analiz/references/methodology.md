# methodology.md — Kuant Motoru Metodoloji & Doktrin

## Genel ilkeler
- Tüm betikler saf-stdlib, deterministik, `--file in.json` CLI + argümansız self-test.
- Veri ÇEKİLMEZ — artefaktlardan (nav_series/holdings/market_context) okunur.
- Kısa/eksik/bozuk seride asla çökmez: `None` + `note` + `coverage/confidence`.
- Her çıktı `disclaimer: "karar-destek; yatırım tavsiyesi değildir"` taşır.

## Çekirdek (`fund_math.py`)
NAV/getiri ayrıştırma (`normalize_nav`, `simple_returns`, `log_returns`, `align_series`),
istatistik (mean/stdev/cov/corr/percentile/skew/kurt), lineer cebir (cov_matrix, Cholesky,
solve_spd, Gauss-Jordan inverse, nearest_pd, simplex_projection). Tek numerik katman.

## Yıllıklama
Tarih ekseninden çıkarılır: günlük→252, haftalık→52, aylık→12. Her metrikte `ppy`/`ppy_basis`
raporlanır (252 vs gerçek-işlem-günü kararı denetlenebilir).

## Reel getiri (TL enflasyonu birinci sınıf)
Nominal TL getiri yüksek-enflasyon döneminde şişer. EVDS TÜFE verilirse Fisher kesin ile
reel getiri paralel hesaplanır: `1+r_real = (1+r_nom)/(1+π)`.

## Determinizm
monte_carlo seed sabit; tüm diğer betikler analitik. Aynı girdi → aynı çıktı (G4 kontrolü).

## Edge-case doktrini
σ=0/n<2 → `None`; negatif/sıfır NAV → normalize'de düşürülür+işaretlenir; benchmark
örtüşmesi yok → ilgili metrik `None`+note; non-PD kovaryans → nearest_pd ridge.
