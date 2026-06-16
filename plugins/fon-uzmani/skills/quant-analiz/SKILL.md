---
name: quant-analiz
description: >-
  quant-analiz — deterministik risk/getiri motoru. NAV-serisi JSON girdiyle saf-Python
  betikleri çalıştırır: getiri/CAGR, Sharpe, Sortino, Calmar, Information ratio, Treynor,
  maksimum geri çekilme (maxDD), volatilite, beta/alfa, VaR/CVaR, Monte Carlo, RBSA faktör/
  stil analizi, yoğunlaşma, maliyet etkisi, kalite kompoziti, portföy optimizasyonu (MVO/
  risk-parity/HRP). Veri çekmez; nav_series + holdings + market_context artefaktlarını okur,
  quant_metrics + optimized_portfolio üretir. USE for — Sharpe oranı, Sortino, Calmar, geri
  çekilme, volatilite, beta, riske göre düzeltilmiş getiri, Monte Carlo, faktör analizi,
  stil sapması, VaR, portföy optimizasyonu, fon kalite skoru. EN — risk-adjusted returns,
  drawdown, VaR, factor/style, portfolio optimization, fund quality score. When in doubt USE.
version: 1.2.0
last_updated: 2026-06-16
changelog:
  - "1.2.0 (2026-06-16): Fon Uzmanı süiti — frontmatter sürüm/changelog beyanı (denetim D1/D10), açık Kapsam Dışı bölümü (D4), quant yüksek-CC fonksiyon refaktörü + docstring (D5). Connector'lar .mcp.json ile paketli (borsa + fon-mcp)."
---

# quant-analiz — Deterministik Risk/Getiri Motoru

**Süit:** fon-uzmani · kaynak skill (Aşama 3/4/5). > Connector/önbellek için
**[../../CONNECTORS.md](../../CONNECTORS.md)** ve
**[../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)** normatiftir.

## Ne Zaman Çağrılır
NAV serisinden niceliksel metrik gerektiğinde. **Veri ÇEKMEZ** — `nav_series`/`holdings`/
`market_context` artefaktlarını okur, `quant_metrics`/`optimized_portfolio` üretir. Risksiz
oran/benchmark `market_context`'ten (piyasa-makro); çift `get_index_data` yasak.

## 0. Scope
Tüm betikler `scripts/` altında, **saf Python 3 stdlib**, deterministik, `--file in.json`
CLI + argümansız self-test. `portfolio_opt.py` varsayılan stdlib; `--engine numpy` opsiyonel
(yoksa sessiz fallback).

## Betik Kataloğu (`scripts/`)
| Betik | Üretir | Girdi |
|---|---|---|
| `fund_math.py` | çekirdek (parse/istatistik/lineer cebir) | — (diğerleri import eder) |
| `fund_returns.py` | dönem/CAGR/TWR/reel getiri (EVDS TÜFE) | {nav, cpi?, benchmark?} |
| `risk_adjusted.py` | Sharpe/Sortino/Calmar/IR/Treynor/Omega | {nav, risk_free?, benchmark?, mar_annual?} |
| `drawdown_var.py` | maxDD anatomisi, Ulcer/Pain, VaR/CVaR, capture | {nav, benchmark?, alpha?, horizon_days?} |
| `volatility_beta.py` | vol/rolling/beta/alfa/R²/korelasyon matrisi | {nav, benchmark?, fx?, peers?, risk_free?} |
| `monte_carlo.py` | bootstrap+GBM koni/P(loss)/P(target) (seed'li) | {nav, horizon_days?, n_paths?, target_return?, seed?} |
| `style_analysis.py` | RBSA örtük stil ağırlıkları | {nav, asset_classes:{label:[...]}} |
| `portfolio_opt.py` | MVO/max-Sharpe/min-var/risk-parity/HRP | {navs|returns, rf?, long_only?} |
| `concentration.py` | HHI/etkin-N/top-N/active-share/overlap/drift | {holdings, benchmark_holdings?, allocation_history?} |
| `cost_analysis.py` | TER drag/break-even/ücret-adil Sharpe | {ter, nav?|gross_return?, cheap_alternative_ter?} |
| `fund_quality_score.py` | kategori-normalize 0-100 kompozit + quintile | {metrics, category?, peers?} |
| `fund_monitor.py` | rejim etiketi + change-points + alarm | {macro?, prev?, curr?} |

## Çağrı Deseni
Artefakttan JSON girdi hazırla → `python3 scripts/<betik>.py --file <girdi>.json` → çıktıyı
`quant_metrics`'e topla. Her betik `disclaimer`/`note`/`confidence` döner; kısa seride
çökmez (`None` + note).

## G3/G4 Kalite Kapısı
- **G3 (akran):** kategori akran kuant → `peer_metrics` (medyan/yüzdebirlik).
- **G4 (BLOKER det.):** temel metrikler hesaplandı · risksiz oran doğru paydada · beta/alfa
  üretildi · maxDD penceresi tarihli · **determinizm** (aynı girdi=aynı çıktı; monte_carlo seed).

## Referanslar
- `references/risk-adjusted-returns.md` (formüller + risksiz oran seçimi)
- `references/drawdown-volatility.md`, `references/factor-style.md`, `references/monte-carlo.md`
- `references/methodology.md` (yıllıklama, reel getiri, edge-case doktrini)
- `requirements.txt` (zero-dep; numpy yalnız portfolio_opt opsiyonel)

## Kapsam Dışı
Veri ÇEKMEZ (artefakttan okur); piyasa yönü/fiyat tahmini veya al-sat sinyali üretmez; gün-içi mikro-yapı; vergi-sonrası getiri.
