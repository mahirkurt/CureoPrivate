# monte-carlo.md — Monte Carlo İleri Simülasyon

`scripts/monte_carlo.py` — TAM DETERMİNİSTİK ileri NAV simülasyonu.

## Motorlar
- **Bootstrap:** tarihsel günlük getirilerin yerine-koymalı yeniden örneklemesi. Opsiyonel
  blok-bootstrap (`block_len>1`) otokorelasyonu korur.
- **GBM:** log-getirilerden μ,σ kestir → `P_{t+1}=P_t·exp((μ−½σ²)+σZ)`, Z ~ N(0,1).

## Determinizm
Yalnız `random.Random(seed)` (varsayılan seed=20260616). Seed çıktıda raporlanır → aynı
girdi+seed bit-bit aynı sonuç. `Date.now`/global random YOK. Bu, kanonik-önbellek
determinizm garantisinin (canonical-cache §4) parçasıdır.

## Çıktı
- Yüzdebirlik konileri P5/P25/P50/P75/P95 (growth-of-1, her adım).
- Terminal dağılım (P5/P50/P95/mean).
- `prob_loss` = P(terminal < 1), `prob_target` = P(terminal ≥ 1+target).

## Girdi
`{nav, horizon_days?=252, n_paths?=2000, engine?=both, target_return?, seed?}`. n_paths
MAX 20000 ile sınırlanır; n<20 getiri → düşük güven notu.

Karar-destek; geçmiş dağılım gelecek garantisi değildir.
