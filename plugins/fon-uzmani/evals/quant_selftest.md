# Quant Motoru Self-Test

Tüm kuant betikleri argümansız çalıştırıldığında self-test yapar (stderr'e `ALL TESTS
PASSED`, stdout'a örnek JSON). Bağımsız ve deterministiktir.

```bash
cd skills/quant-analiz/scripts
for f in *.py; do python3 "$f" >/dev/null 2>&1 && echo "PASS $f" || echo "FAIL $f"; done
```

Beklenen: 12/12 PASS (fund_math, fund_returns, risk_adjusted, drawdown_var, volatility_beta,
monte_carlo, style_analysis, portfolio_opt, concentration, cost_analysis, fund_quality_score,
fund_monitor).

## Uyum lint
```bash
python3 skills/regulasyon-uyum/scripts/rapor_lint.py            # self-test
python3 skills/regulasyon-uyum/scripts/rapor_lint.py --file evals/golden_outputs/ti2-mod1-example.md
```
Beklenen: golden örnek `passed: true`.

## Tek-fon uçtan uca (örnek)
```bash
# nav.json: [{"date":"2025-01-01","price":1.0}, ...] hazırla, sonra:
python3 skills/quant-analiz/scripts/risk_adjusted.py --file nav_payload.json
python3 skills/quant-analiz/scripts/drawdown_var.py --file nav_payload.json
python3 skills/quant-analiz/scripts/monte_carlo.py --file nav_payload.json   # aynı seed → aynı P50
```

## Determinizm
`monte_carlo.py` aynı girdi+seed → bit-bit aynı çıktı. `portfolio_opt.py` numpy olmadan
çalışır (`engine_used: "stdlib"`).
