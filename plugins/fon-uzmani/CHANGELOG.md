# Changelog — Fon Uzmanı (fon-uzmani)

Bu eklenti [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) izler.

## [1.2.0] — 2026-06-16

Skill-denetim (FULL_AUDIT) iyileştirme sürümü — rapor: 0 CRITICAL / 0 MAJOR; 6/7 skill EXEMPLARY.

### Eklendi
- 8 skill'in tümünde frontmatter `version` + `changelog` beyanı (süit sürüm uyumu; denetim D1/D10).
- Her SKILL.md'ye açık **## Kapsam Dışı** bölümü (denetim D4 gerçek payı).

### Değişti (quant teknik-borç refaktörü — denetim D5)
- `fund_monitor.change_points` (CC≈25) → delta-dedektör fonksiyonlarına bölündü (CC≈5);
  `concentration.analyze` (CC≈16) → düzleştirildi + `_concentration_block` (CC≈8). Docstring'ler eklendi.
- **Davranış değişmedi:** 12/12 quant self-test + rapor_lint yeşil; çıktı şemaları aynı.

### Not
- §3.2 (denetçi TENTATIVE): CONNECTORS.md + shared/ + evals/ kanonik kökte MEVCUT — kırık görünüm
  yalnız düzleştirilmiş-mount artefaktıydı, defekt değil.

## [1.1.0] — 2026-06-16

### Değişti
- **Yeniden adlandırıldı: "TEFAS Uzmanı" → "Fon Uzmanı"** (slug `tefas-analist` → `fon-uzmani`).
- Connector'lar artık **`.mcp.json` ile paketlenir**: `borsa` (Borsa MCP, public) + `fon-mcp`
  (`fon-mcp.cureonics.workers.dev/mcp`, OAuth 2.1 — ilk bağlantıda MCP_API_KEY). Kurulumda
  otomatik bağlanır (önceden kullanıcı-konfigürasyonluydu).

### Eklendi (fon-mcp veri omurgası canlı)
- Gerçek TER + yönetim ücreti (`fonYonetimBazliBilgiGetir`), varlık dağılımı (anlık + tarihsel),
  fon akışı (net giriş/çıkış), kategori/sıralama, kurucu (fon ünvanından).

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
