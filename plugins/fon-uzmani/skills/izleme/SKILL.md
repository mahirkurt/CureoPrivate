---
name: izleme
description: >-
  izleme — fon izleme listesi + sürekli gözetim katmanı (Mod 5). fund-state-schema.json durum
  anlık görüntüsünü yönetir; iki snapshot'ı karşılaştırarak rejim değişimi (benchmark/makro
  rejim kayması), stil sapması (holdings/faktör profili kayması), geri çekilme (maxDD eşik)
  alarmı, TER artışı ve KAP duyurusu üretir; periyodik anlık görüntü tutar. "Ne değişti"
  odaklı. USE for — fon izle, izleme listesi, gözetim, rejim değişimi, stil sapması, geri
  çekilme alarmı, periyodik snapshot, "ne değişti", portföy takibi. EN — fund watchlist,
  monitoring, regime shift, style drift, drawdown alert. When in doubt USE.
version: 1.2.0
last_updated: 2026-06-16
changelog:
  - "1.2.0 (2026-06-16): Fon Uzmanı süiti — frontmatter sürüm/changelog beyanı (denetim D1/D10), açık Kapsam Dışı bölümü (D4), quant yüksek-CC fonksiyon refaktörü + docstring (D5). Connector'lar .mcp.json ile paketli (borsa + fon-mcp)."
---

# izleme — İzleme Listesi & Sürekli Gözetim

**Süit:** fon-uzmani · kaynak skill (Aşama 5', Mod 5). > Connector/önbellek için
**[../../CONNECTORS.md](../../CONNECTORS.md)** normatiftir.

## Ne Zaman Çağrılır
Bir fon/portföy listesini zaman içinde izlemek, önceki duruma göre **değişimleri** öne
çıkarmak gerektiğinde (Mod 5).

## 0. Scope
"Ne değişti" odaklı delta raporu. Tam yeniden-analiz değil; yalnız değişen sinyaller. Çıktı
karar-destek.

## Adım 1 — Durum anlık görüntüsü
`assets/fund-state-schema.json`'a uygun snapshot üret/oku: her fon için fund_id, kategori,
last_nav/as_of, aum, ter, quant_snapshot (sharpe/sortino/maxDD/vol/beta), style_fingerprint,
regime_tag, açık KAP. Veri için fon-haritalama + quant-analiz (delta gereken alanlar) çağrılır.

## Adım 2 — Değişim tespiti
`../quant-analiz/scripts/fund_monitor.py` (`change_points`): iki snapshot'ı karşılaştır →
alarm türleri: `drawdown_esigi` (maxDD eşik), `vol_sicramasi` (vol ×k), `stil_sapmasi`
(holdings/faktör drift), `ter_artisi`, `rejim_degisimi`, `kap_duyurusu`, `yeni_eklendi`.
Önceliklendirilmiş `items[]` + `alert` kompoziti (sakin/izlemede/yüksek dikkat).

## Adım 3 — "Ne değişti" raporu
Önceliğe göre sıralı değişimler + her alarm için tetikleyici ve önerilen gözden-geçirme
(karar-destek dili).

## G6'(monitor) Kapısı
Değişim listesi üretildi · alarm kompoziti hesaplandı · her alarm tarihli · feragat (G7).

## Çıktı
`fund_state.json` (yeni snapshot) + `watchlist_diff.json` (değişim raporu). Eşik
parametreleri: `thresholds` (mdd_breach, vol_spike_k, rank_drop).

## Referanslar
- `references/monitoring-doctrine.md` (alarm eşikleri + gramer)
- `assets/fund-state-schema.json` (durum şeması)

## Kapsam Dışı
Gerçek-zamanlı uyarı/push bildirimi; tam yeniden-analiz (→ /fon-analiz); gün-içi tetikleme. (Yalnız snapshot-arası delta.)
