# drawdown-volatility.md — Geri Çekilme, Volatilite, Kuyruk Riski

`scripts/drawdown_var.py` + `scripts/volatility_beta.py`.

## Drawdown
- **Drawdown eğrisi:** `DD_t = P_t / max_{s≤t}P_s − 1`.
- **Max drawdown:** en derin DD + tepe/dip/toparlanma tarihleri + süre (gün). Toparlanmamışsa
  `underwater: true`.
- **Ulcer index:** `√(mean(DD_t²))` (% cinsinden) — derinlik+süre.
- **Pain index:** `mean(|DD_t|)`.

## Volatilite
- **Yıllık vol:** `std(r) · √ppy`. **Rolling vol:** pencere bazlı.
- **Downside deviation:** yalnız MAR-altı getiriler.

## Piyasa duyarlılığı
- **Beta:** `Cov(r_f,r_b)/Var(r_b)`. **Jensen alfa:** `(r̄_f − r_f^rf) − β(r̄_b − r_f^rf)`
  (yıllıklı). **R²:** `corr²`. **Up/Down beta:** benchmark-yukarı/aşağı alt-örneklemde.
- **Korelasyon matrisi:** fon × benchmark × FX(USDTRY) × akranlar (ortak tarih ekseni).

## Kuyruk riski (VaR/CVaR)
- **Historical VaR(α):** `−percentile(r, 1−α)`.
- **Parametrik VaR:** `−(μ + z_α·σ)`, z Acklam inv-normal ile.
- **Cornish-Fisher VaR:** çarpıklık+basıklık düzeltmeli z_CF.
- **CVaR:** VaR ötesi kayıpların ortalaması (expected shortfall).
- Ufuk için `√horizon` ölçeklemesi. Karar-destek; yatırım tavsiyesi değildir.
