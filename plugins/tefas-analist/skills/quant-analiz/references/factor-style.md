# factor-style.md — Faktör / Stil Analizi (RBSA)

`scripts/style_analysis.py` — Sharpe (1992) Returns-Based Style Analysis.

## Yöntem
Fon getirilerini varlık-sınıfı endeks getirilerine örtük olarak çözer:
`min Σ_t (r_f,t − Σ_k w_k r_k,t)²` s.t. `w_k ≥ 0, Σw_k = 1` (long-only simpleks; Sharpe QP).

## Saf-stdlib çözüm
Simpleks-projeksiyonlu gradyan inişi (Duchi 2008 Öklid projeksiyonu, `fund_math.simplex_projection`).
Küçük K (≤4) için kaba ızgara çapraz-doğrulaması ile teyit edilebilir. numpy/scipy GEREKMEZ.

## Girdi/çıktı
Girdi: `{nav, asset_classes:{label:[{date,price}]}}` — 3-8 varlık sınıfı endeksi (örn.
BIST100, KYD tahvil, USD/altın, para piyasası). Çıktı: `style` (sınıf→ağırlık, Σ=1),
`r_squared` (stil uyum kalitesi), `tracking_error_daily`, `converged`.

## Yorum
- Yüksek R² → fon getirisi varlık-sınıfı maruziyetiyle iyi açıklanıyor (pasif-benzeri).
- Düşük R² → aktif seçim/zamanlama veya sınıf seti eksik.
- Stil ağırlıklarının zaman içindeki kayması = **stil drift** (izleme skili kullanır).

## Edge-case
K ≥ T (gözlemden çok sınıf) → ridge + not. Kollinear sınıflar → işaretlenir. Yakınsamazsa
en iyi-bulunan + `converged:false`. Karar-destek; yatırım tavsiyesi değildir.
