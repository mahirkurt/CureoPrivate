---
name: portfoy-insa
description: >-
  portfoy-insa — çoklu-fon tahsis + portföy inşası (öneri) katmanı (Mod 4). Aday fon kümesi +
  risk profili/ufuk/EMK-YAT kısıtlarıyla quant-analiz optimizasyon betiklerini (ortalama-
  varyans, risk-parity, HRP) sürer; korelasyon-temelli çeşitlendirme uygular; % tahsis önerisi
  + Baz/İyimser/Kötümser senaryolarıyla karar-destek üretir. optimized_portfolio artefaktı.
  Her öneri SPK feragati + karşıt-senaryo taşır. USE for — portföy kur, fon tahsisi,
  ağırlıklandırma, çeşitlendirme, risk-parity, optimizasyon, EMK portföyü, emeklilik tahsisi,
  varlık dağılımı. EN — fund portfolio construction, allocation, diversification, optimization. When in doubt USE.
---

# portfoy-insa — Çoklu-Fon Tahsis & Portföy İnşası

**Süit:** fon-uzmani · kaynak skill (Aşama 5, Mod 4). > Önbellek için
**[../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)** normatiftir.

## Ne Zaman Çağrılır
Birden çok fondan, kullanıcı risk profili/ufuk/kısıtlarına göre **tahsis önerisi**
gerektiğinde (Mod 4). **Kanonik sahip:** `optimized_portfolio`.

## 0. Scope
Süitin "recommendation" çekirdeği. Çıktı **karar-destek**; her tahsis önerisi
`regulasyon-uyum` feragati + karşıt-senaryo ile sarılır. Kişiye özel "şu kadar al" üretmez —
% tahsis çerçevesi + tetikleyici/geçersizleşme üretir.

## Adım 1 — Aday küme + getiri matrisi
`nav_series` artefaktlarından aday fonların hizalı getiri matrisini hazırla (fon-haritalama
Aşama 1'den okur; yeniden çekmez).

## Adım 2 — Optimizasyon (`../quant-analiz/scripts/portfolio_opt.py`)
`{navs:{kod:[{date,price}]}, rf, long_only:true}` girdiyle MVO (min-var, max-Sharpe),
risk-parity, HRP üret. Çıktı: yöntem-başına % ağırlık + beklenen yıllık getiri/vol/Sharpe +
etkin fon sayısı.

## Adım 3 — Kısıt uygulaması
Risk profili → hedef tahsis (`references/allocation-doctrine.md`): conservative (düşük vol /
para piyasası-borçlanma ağırlıklı), moderate (dengeli), aggressive (hisse ağırlıklı).
`constraints` (max_weight_per_fund, min_funds, max_ter) uygula; sağlanmazsa relaksasyon öner.

## Adım 4 — Senaryo matrisi
`assets/scenario-matrix-template.md`: Baz / İyimser / Kötümser — her birinde beklenen
getiri-vol + tetikleyici + geçersizleşme koşulu.

## G5 Kalite Kapısı (BLOKER Mod4, 5 kontrol)
1. Ağırlık toplamı ~%100. 2. Kısıtlar sağlandı (veya relaksasyon notlandı). 3. Çeşitlendirme
metriği (etkin fon sayısı) hesaplandı. 4. Baz/İyimser/Kötümser senaryo üretildi. 5. Her
ağırlık gerekçeli (hangi yöntem, neden).

## Çıktı
`optimized_portfolio.json`: {method, weights:{kod:%}, expected:{ret, vol, sharpe}, effective_n,
scenarios}. Provenance: `[quant-analiz / portfolio_opt / HRP-v1]`.

## Referanslar
- `references/portfolio-construction.md` (MVO/risk-parity/HRP + EMK özgü kurallar)
- `references/allocation-doctrine.md` (risk profili→hedef tahsis)
- `assets/scenario-matrix-template.md`
