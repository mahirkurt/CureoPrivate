---
name: fon-analiz-orkestratoru
description: >-
  fon-analiz-orkestratoru — fon-uzmani süitinin orkestratörü. Türkiye yatırım (YAT) +
  emeklilik (EMK) fonları için sekiz-aşamalı deterministik boru hattı (Aşama 0 brief +
  1-7 pipeline) ile altı kaynak-tipi sibling skill'i (fon-haritalama, quant-analiz,
  piyasa-makro, regulasyon-uyum, portfoy-insa, izleme) G0-G7 kalite kapılarıyla orkestre
  eder. Paylaşılan connector sözleşmesi (../../CONNECTORS.md), kanonik-artefakt önbelleği
  (../../shared/canonical-cache-contract.md) ve deterministik kuant betikleri altında çift
  sorguyu/çift-hesabı engeller. Beş mod: tek-fon derin analiz · kategori/tarama · çoklu-fon
  karşılaştırma · portföy inşası (tahsis) · izleme listesi gözetimi. Çıktı KARAR-DESTEK;
  SPK yatırım danışmanlığı DEĞİLDİR. USE for — fon analiz et, fon tara, fon karşılaştır,
  portföy kur, fon izle, AFA analiz, emeklilik fonu seç, Sharpe/Sortino/maxDD, risk-getiri,
  fon dağılımı, TER karşılaştırma, "hangi fon". EN — analyze a Turkish mutual/pension fund,
  screen funds, compare funds, build a fund portfolio, monitor a fund watchlist. When in doubt USE.
version: 1.2.0
last_updated: 2026-06-16
changelog:
  - "1.2.0 (2026-06-16): Fon Uzmanı süiti — frontmatter sürüm/changelog beyanı (denetim D1/D10), açık Kapsam Dışı bölümü (D4), quant yüksek-CC fonksiyon refaktörü + docstring (D5). Connector'lar .mcp.json ile paketli (borsa + fon-mcp)."
---

# fon-analiz-orkestratoru — TEFAS Fon Analiz Orkestratörü

**Skill tipi:** Çok-skill orkestrasyon (deterministik boru hattı) — süit flagship'i.
**Süit:** fon-uzmani · **Dil:** Türkçe (rapor), İngilizce (API sorguları).

> **Plugin entegrasyon notu.** Connector envanteri/fallback için
> **[../../CONNECTORS.md](../../CONNECTORS.md)**, kanonik önbellek + çift-sorgu disiplini
> için **[../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)**,
> provenance için **[../../shared/provenance-standard.md](../../shared/provenance-standard.md)**
> normatiftir. Bu skill connector tanımı yapmaz; oraya referans verir.

## Ne Zaman Çağrılır
TEFAS'ta listelenmiş yatırım/emeklilik fonu analiz, tarama, karşılaştırma, portföy inşası
veya izleme gerektiğinde. **Scope guard:** tekil hisse/tahvil → `bist-analyst`; mevzuat
reformu → `lex-sanitas`; bireysel vergi/SGK → kapsam dışı; gün-içi/scalping → kapsam dışı
(veri EOD); kişiselleştirilmiş "şu kadar al" → karar-destek diline çevrilir.

## 0. Scope Politikası
YAT (yatırım) + EMK (emeklilik) fonları, tüm varlık sınıfları (hisse/borçlanma/karma/para
piyasası/altın/serbest/katılım). Kanal: TEFAS dağıtımlı fonlar. Tekil menkul kıymet
kapsam dışı.

## 0.B Skill Entegrasyon Sözleşmesi (mod × skill × faz)
| Mod | Skiller | Çalışan fazlar |
|---|---|---|
| (1) Tek-fon derin analiz | fon-haritalama→piyasa-makro→quant-analiz→regulasyon-uyum | G0,G1,G2,G3,G4,G6,G7 |
| (2) Kategori/tarama | fon-haritalama(`screen_funds`)→quant-analiz | G0,G1,G3,G6,G7 |
| (3) Çoklu-fon karşılaştırma | fon-haritalama→quant-analiz→piyasa-makro | G0,G1,G2,G3,G6,G7 |
| (4) Portföy inşası (öneri) | (1+3)+portfoy-insa | G0–G7 (tümü) |
| (5) İzleme/gözetim | izleme→(delta için) fon-haritalama+quant-analiz | G0,G1,G3,G6',G7 |

`regulasyon-uyum` **her modda G7'de** çalışır (feragat + lint zorunlu kapı).

## 1. Skill Ne Yapar
Kullanıcı briefini (hangi fon(lar), evren, risk profili, ufuk) Aşama 0'da deterministik
JSON'a (`assets/brief-schema.json`) oturtur; 6 sibling skili sıralı orkestrasyona alır;
her birinden JSON-strict artefakt toplar; kanonik önbellekle çift çağrıyı engeller;
iki-katmanlı konsolide **Markdown karar-destek raporu** üretir. Skill **veri üretmez**.

## 2. Mimari — Kanonik Artefakt Akışı
```
fund_registry/holdings/nav_series : Aşama1 üretir → 2,3,5,6 tüketir   (fon-mcp+get_fund_data bir kez)
market_context                    : Aşama2 üretir → 4,6 tüketir       (Borsa benchmark/risk-free/makro)
peer_metrics                      : Aşama3 üretir → 5,6 tüketir       (kategori akran kuant)
quant_metrics                     : Aşama4 üretir → 5,6 tüketir       (kuant betikleri; fon başına bir kez)
optimized_portfolio               : Aşama5 üretir → 6 tüketir          (portfolio_opt betiği)
```

## 3. Aşama Aşama Protokol (G0–G7)

### Aşama 0 — Brief Standardizasyonu (G0, BLOKER)
Doğal dil → `assets/brief-schema.json`. Zorunlu: `mode`(1-5) · `universe`(YAT/EMK/MIX) ·
`fund_ids[]` **veya** `category` · (Mod 4) `risk_profile`+`horizon_months`+`constraints` ·
`benchmark` · `exclusion`. **G0 — 8 kontrol.** Eksik kritik alanı kullanıcıdan iste; uydurma.

### Aşama 1 — Fon Haritalama (G1, BLOKER) · fon-haritalama
fon-mcp + Borsa `get_fund_data`/`screen_funds`. Her fon: kod+ad+kurucu (PYŞ kısa adı,
fon ünvanından türetilmiş)+kategori (TEFAS) + NAV-serisi + AUM + **varlık-sınıfı holdings**
(menkul-bazlı line-item KAP gerektirir) + **TER üst-sınırı + yönetim ücreti** (gerçekleşen
TER için KAP KIID) + fon akışı (Δshares×midNAV). **Kanonik:** `fund_registry` + `holdings`
+ `nav_series` **bir kez** (canonical-cache §3). **G1 — 5 kontrol:** her fon çözüldü · NAV
uzunluğu ≥ horizon · holdings ≈ %100 (varlık-sınıfı) · TER üst-sınırı alındı (yoksa caveat
"gerçekleşen için KAP KIID") · kategori atandı.

### Aşama 2 — Piyasa/Makro Bağlam (G2) · piyasa-makro
Borsa `get_index_data` (benchmark) + `get_bond_yields` (risksiz) + `get_evds_data`/
`get_macro_data` (rejim) + `get_fx_data`. **Kanonik:** `market_context`. **G2 — 4 (3+1WARN):**
benchmark NAV penceresiyle hizalı · risksiz oran alındı · makro rejim etiketi · (WARN) FX.

### Aşama 3 — Akran/Kategori Kuant (G3) · quant-analiz + fon-haritalama
Kategori akran evreni için toplu kuant (medyan Sharpe/Sortino/maxDD/TER yüzdebirlikleri).
**Kanonik:** `peer_metrics`. **G3 — 3 kontrol:** akran evreni ≥ N · yüzdebirlik üretildi ·
TER akran-göreli konumlandı.

### Aşama 4 — Tek-Fon Risk/Getiri (G4, BLOKER det.) · quant-analiz
`nav_series` + `market_context` okur (yeniden çekmez). Betikler: `fund_returns`,
`risk_adjusted` (Sharpe/Sortino/Calmar/IR/Treynor), `drawdown_var` (maxDD/VaR/CVaR),
`volatility_beta` (vol/beta/alfa/korelasyon), `monte_carlo`, `style_analysis`,
`fund_quality_score`. **Kanonik:** `quant_metrics`. **G4 — 5 kontrol:** temel metrikler
hesaplandı · risksiz oran doğru paydada · benchmark beta/alfa üretildi · maxDD penceresi
tarihli · betik determinizmi (aynı girdi=aynı çıktı) doğrulandı.

### Aşama 5 — Portföy İnşası/Tahsis (G5, BLOKER Mod4) · portfoy-insa + quant-analiz
Aday kümeden korelasyon + `portfolio_opt` (MVO/risk-parity/HRP) + kısıt uygulaması.
**Kanonik:** `optimized_portfolio` (% ağırlık + beklenen risk/getiri + senaryo matrisi).
**G5 — 5 kontrol:** ağırlık toplamı ~%100 · kısıtlar sağlandı · çeşitlendirme metriği
(etkin fon sayısı) · Baz/İyimser/Kötümser senaryo · her ağırlık gerekçeli.

### Aşama 6 — Konsolide Rapor (G6) · orchestrator + regulasyon-uyum
Aşama 1-5 JSON'larından iki-katmanlı Markdown (provenance-standard §3). **G6 — 6 yapısal:**
≥8 `##` başlık · Yönetici Özeti · ≥1 karşılaştırma tablosu · Provenance · senaryo matrisi ·
her bulgu güven+karşıt-senaryo.

### Aşama 7 — Uyum Kapısı (G7, BLOKER) · regulasyon-uyum
`scripts/rapor_lint.py` (regulasyon-uyum). **G7 — 8 kontrol:** kanonik SPK feragati
birebir mevcut · emir-kipi yok · kaynaklar tarihli · ham makine çıktısı yok · EOD beyanı ·
üçüncü-taraf etiketi · senaryo/karşıt-senaryo · kesinlik iddiası yok. Geçmezse rapor
**yayımlanmaz**.

## 4. Quality Gate Matrisi
| Gate | Aşama | Kontrol | Tip |
|---|---|---|---|
| G0 | Brief | 8 | BLOKER |
| G1 | Fon haritalama | 5 | BLOKER |
| G2 | Piyasa/makro | 4 (3+1WARN) | WARN |
| G3 | Akran kuant | 3 | WARN |
| G4 | Risk/getiri | 5 | BLOKER (determinizm) |
| G5 | Portföy (Mod4) | 5 | BLOKER (Mod4) |
| G6 | Rapor | 6 yapısal | BLOKER |
| G7 | Uyum | 8 | BLOKER |

BLOKER başarısız → boru hattı durur (eksik kullanıcıdan istenir). WARN → rapor teslim +
not (degrade'e izin).

## 5. Orkestrasyon Kayıt Şeması
Her çalıştırma `run_manifest.json` üretir (şema: `../../shared/run-manifest-schema.json`):
`skill_invocations` + `quality_gates` + `artifacts` + `cached_artifacts` +
`connector_call_ledger` (`fon_mcp.single_shot_enforced`, `quant_engine.deterministic`).

## 6. Run ID Konvansiyonu
`TFA-YYYYMMDD-(YAT|EMK|MIX)-(M1-5)-vN` — örn. `TFA-20260616-YAT-M1-v1`.

## 7. Dosya Yapısı (run çıktısı)
```
<RUN_ID>/
├── fund_registry.json · holdings.json · nav_series.json
├── market_context.json · peer_metrics.json · quant_metrics.json · optimized_portfolio.json
├── rapor.md            # Aşama 6 iki-katmanlı konsolide
└── run_manifest.json   # + cached_artifacts + connector_call_ledger
```

## 8. MCP Fallback → ../../CONNECTORS.md §6
Tüm fallback zincirleri ve caveat etiketleri orada.

## 9. Composability
**Downstream:** carbon-html-report / carbon-pptx (rapor render). **Yan:** bist-analyst
(fonun ağırlıklı BIST hisse holding'leri için look-through — line-item KAP'tan, varlık-sınıfı
fon-mcp'den), socius-vigil (kurucu/PYŞ itibar sinyali).

## 10. Referans Dosyalar
- `assets/brief-schema.json` — Aşama 0 JSON şeması.
- Plugin-düzeyi: `../../CONNECTORS.md`, `../../shared/*`.
- Kuant betikleri: `../quant-analiz/scripts/`. Uyum: `../regulasyon-uyum/references/compliance.md`
  + `../regulasyon-uyum/scripts/rapor_lint.py`.

## Kapsam Dışı
Tekil hisse/tahvil analizi (→ bist-analyst); mevzuat reformu (→ lex-sanitas); bireysel vergi/SGK; gün-içi/scalping (veri EOD); kişiselleştirilmiş kesin al/sat tutarı/emri.
