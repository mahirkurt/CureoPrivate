# Changelog — TEFAS Uzmanı (tefas-analist)

Bu eklenti [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) izler.

## [1.0.0] — 2026-06-16

### Eklendi
- İlk süit. SMP v1.0 capability-cluster: `fon-analiz-orkestratoru` (8-aşamalı
  deterministik boru hattı, G0-G7 kapıları) + 6 kaynak skill (fon-haritalama,
  quant-analiz, piyasa-makro, regulasyon-uyum, portfoy-insa, izleme) + `start` router.
- Paylaşılan sözleşmeler: `CONNECTORS.md`, `shared/canonical-cache-contract.md`,
  `shared/provenance-standard.md`, `shared/run-manifest-schema.json`.
- 12-modüllük deterministik saf-Python kuant kütüphanesi (`quant-analiz/scripts/`):
  fund_math (çekirdek) + getiri, risk-ayarlı, drawdown/VaR, volatilite/beta, Monte Carlo,
  RBSA stil, portföy optimizasyonu (MVO/RP/HRP), yoğunlaşma, maliyet, kalite kompoziti,
  izleme. Her modül bağımsız CLI + self-test.
- 5 komut: `/fon-analiz` `/fon-tara` `/fon-karsilastir` `/fon-portfoy` `/fon-izle`.
- Veri omurgaları: Borsa MCP (mevcut) + **fon-mcp** (yeni TEFAS/KAP detay sunucusu —
  `mcp-servers/fon-mcp/`, 12 araç, OAuth 2.1, KV-önbellekli).

### Notlar
- Çıktılar karar-destek; SPK yatırım danışmanlığı/portföy yöneticiliği/tavsiyesi değildir.
- Fiyat/NAV gün-sonu (EOD); gün-içi kapsam dışı.
- `portfolio_opt.py` varsayılan saf-stdlib; `--engine numpy` opsiyonel (yoksa fallback).
