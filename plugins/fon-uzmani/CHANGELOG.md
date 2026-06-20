# Changelog — Fon Uzmanı (fon-uzmani)

Bu eklenti [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) izler.

## [1.3.0] — 2026-06-20

fon-mcp canlı tool yüzeyiyle dokümantasyon-davranış hizalama sürümü. Hiçbir kuant betiği
veya orkestrasyon kapısı değişmedi; **tool çağrı doğruluğu** ve **TER raporlama disiplini**
düzeltildi.

### Değişti (CONNECTORS.md §1.A — gerçek dönüş şemaları)
- `resolve_fund` → `code/name/aum/kap_link` (önceki belge "kurucu/kategori" diyordu — bunlar
  Adım 3'te `get_fund_registry`'den geliyor).
- `get_fund_registry` → `name/category/aum/investor_count/category_rank/category_fund_count/
  market_share/last_price/founder` (PYŞ kısa adı, fon ünvanından türetilmiş) + `kap_link`.
  **ISIN/strateji yeni TEFAS API'sinde yok** → `null` + KAP fon sayfası gerekir.
- `get_fund_taxonomy` → tek-fon kategorisi VEYA SPK kategori referans listesi (sayım yok;
  evren-bazlı sayım için Borsa `screen_funds`).
- `get_fund_holdings` → **varlık-sınıfı** ağırlıkları (`dagilimSiraliGetirT`); menkul-bazlı
  line-item KAP aylık portföy raporu PDF gerektirir.
- `get_fund_costs` → `management_fee_pct` + **`ter_ceiling_pct` (azami toplam gider oranı —
  ÜST SINIR, gerçekleşen TER DEĞİL; `fonYonetimBazliBilgiGetir`)** + `umbrella` +
  `founder_code`. **Gerçekleşen TER her zaman KAP KIID gerektirir.**
- `compare_fund_costs` → `fund_type` + opsiyonel `category` + `sort_by` (varsayılan
  `ter_ceiling_pct`).

### Değişti (raporlama disiplini)
- Her TER sayısı artık "(üst-sınır)" veya "(gerçekleşen, KAP KIID)" etiketi taşır.
- izleme doktrini alarm türleri ayrıldı: `ter_ust_sinir_artisi` (DÜŞÜK frekans; genel
  kurul/tebliğ tetiklidir) + `yonetim_ucreti_artisi` + `gerceklesen_ter_artisi` (KAP KIID).
- Fallback matrisi (CONNECTORS.md §6): TER üst-sınır vs gerçekleşen ayrımı, `get_fund_flows`
  Borsa `get_fund_data` çökünce **NAV yedek omurgası** olarak eklendi.

### Değişti (hizalanan dosyalar)
- `CONNECTORS.md` (§1.A, §6, §7, §8) — sürüm 1.1.0.
- `skills/fon-haritalama/SKILL.md` (Adım 1-4, G1, Kapsam Dışı) — sürüm 1.3.0.
- `skills/fon-haritalama/references/holdings-mapping.md` — TER üst-sınır / gerçekleşen ayrımı.
- `skills/fon-haritalama/references/data-sources.md` — endpoint-bazlı kaynak haritası
  (`fonGnlBlgSiraliGetir` / `dagilimSiraliGetirT` / `fonBilgiGetir` / `fonYonetimBazliBilgiGetir`).
- `skills/fon-analiz-orkestratoru/SKILL.md` (Aşama 1, G1, §9 composability).
- `skills/izleme/references/monitoring-doctrine.md` (alarm tipleri).
- `shared/provenance-standard.md` (TER üst-sınır + KAP KIID damga grameri).
- `evals/mcp_smoke_test.md` (canlı `tools/list` + `fon_mcp_health` assertion'ları; 12 araç).
- `README.md` (omurga tanımı).
- `.claude-plugin/plugin.json` description (yönetici→kurucu, TER→TER azami sınır).

### Notlar
- fon-mcp `https://fon-mcp.cureonics.workers.dev` Worker'ı **2026-06-20'de yeniden deploy
  edildi** (Version `f1406cfe-bd30-4a3e-9fc8-a83458f04998`, CACHE_NAMESPACE `fon:v4`).
  Eski TEFAS `/api/DB/Bind*` rotaları küresel kapatıldı; yeni rotalar (`fonGnlBlgSiraliGetir`
  / `dagilimSiraliGetirT` / `fonBilgiGetir` / `fonYonetimBazliBilgiGetir`) canlı + WAF YOK.

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
