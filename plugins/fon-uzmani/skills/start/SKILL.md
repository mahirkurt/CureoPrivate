---
name: start
description: >-
  Fon Uzmanı (fon-uzmani) süitine giriş, connector sağlık kontrolü (Borsa MCP +
  fon-mcp) ve doğru moda/skill'e yönlendirme. İlk kez süitle çalışırken, "Fon Uzmanı
  nedir / nereden başlamalıyım / hangi modu kullanmalıyım", connector bağlı mı, ya da
  analiz öncesi kurulum doğrulaması için kullanın. EN: orientation + connector
  health-check for the TEFAS fund-analysis suite; routes to the correct mode/skill.
  Tetikler — Fon Uzmanı başlat, fon analizi nereden başlayayım, "ne yapabilirsin",
  Borsa/fon-mcp bağlı mı, connector kontrolü, kurulum doğrulama.
version: 1.2.0
last_updated: 2026-06-16
changelog:
  - "1.2.0 (2026-06-16): Fon Uzmanı süiti — frontmatter sürüm/changelog beyanı (denetim D1/D10), açık Kapsam Dışı bölümü (D4), quant yüksek-CC fonksiyon refaktörü + docstring (D5). Connector'lar .mcp.json ile paketli (borsa + fon-mcp)."
---

# start — Fon Uzmanı oryantasyon & yönlendirme

**Süit:** fon-uzmani (capability-cluster) · **Dil:** Türkçe (çıktı), İngilizce (API).

> Bağlayıcı envanteri ve fallback için **[../../CONNECTORS.md](../../CONNECTORS.md)** normatiftir.

## Adım 1 — Karşılama
Süit Türkiye yatırım (YAT) + emeklilik (EMK) fonlarını analiz eder: tek-fon derin analiz,
kategori tarama, çoklu-fon karşılaştırma, portföy inşası (öneri) ve sürekli izleme.
Çıktı **karar-destek**; SPK yatırım danışmanlığı değildir.

## Adım 2 — Connector sağlık-kontrolü (pre-flight, CONNECTORS.md §8)
1. **Borsa MCP**: `get_fund_data(symbol="TI2")` veya `search_symbol(market='fund', query="TI2")` prob.
2. **fon-mcp**: `fon_mcp_health` → `tefas_reachable`.
- Borsa erişilemezse: NAV/getiri/benchmark degrade → kullanıcıyı uyar.
- fon-mcp erişilemezse: holdings/TER/akış degrade; Borsa `get_fund_data(include_portfolio)` fallback (sınırlı).

## Adım 3 — Skill tanıtımı
| Skill | Ne yapar |
|---|---|
| `fon-analiz-orkestratoru` | Flagship — briefi alır, 6 skili G0-G7 ile orkestre eder, konsolide rapor üretir |
| `fon-haritalama` | Kimlik+holdings+TER+akış+NAV haritalama (fund_registry/holdings/nav_series sahibi) |
| `quant-analiz` | Risk/getiri motoru (Sharpe…MonteCarlo…optimizasyon; saf-Python betikler) |
| `piyasa-makro` | Benchmark+risksiz oran+TCMB makro rejim (market_context sahibi) |
| `regulasyon-uyum` | SPK feragati + KAP duyuru + rapor lint (G7 zorunlu kapı) |
| `portfoy-insa` | Çoklu-fon tahsis/optimizasyon önerisi (Mod 4) |
| `izleme` | İzleme listesi + rejim/stil/drawdown alarmı (Mod 5) |

## Adım 4 — Komut tanıtımı
`/fon-analiz` (M1) · `/fon-tara` (M2) · `/fon-karsilastir` (M3) · `/fon-portfoy` (M4) · `/fon-izle` (M5).

## Adım 5 — Niyete göre yönlendirme + Scope Guard
| Kullanıcı niyeti | Yönlendir |
|---|---|
| "X fonunu analiz et" | /fon-analiz → orchestrator Mod 1 |
| "düşük TER hisse fonları" / "bu hafta hangi fonlar" | /fon-tara → Mod 2 |
| "X ile Y'yi karşılaştır" | /fon-karsilastir → Mod 3 |
| "portföy kur / fon tahsisi" | /fon-portfoy → Mod 4 |
| "fonlarımı izle / ne değişti" | /fon-izle → Mod 5 |

**Scope dışı:** Tekil hisse/tahvil analizi → `bist-analyst`. Mevzuat reformu → `lex-sanitas`.
Bireysel vergi/SGK → kapsam dışı. Kişiselleştirilmiş "şu kadar al" → karar-destek diline
çevir (regulasyon-uyum). Gün-içi/scalping → kapsam dışı (veri EOD).

## Kapsam Dışı
Analiz YAPMAZ (yalnız oryantasyon + connector sağlık-kontrolü + yönlendirme); connector kurulumu/anahtarı kullanıcı tarafındadır.
