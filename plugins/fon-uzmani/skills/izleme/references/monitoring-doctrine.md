# monitoring-doctrine.md — İzleme Doktrini & Alarm Eşikleri

`scripts/fund_monitor.py change_points` ile iki snapshot karşılaştırılır.

## Alarm türleri & varsayılan eşikler
| Tür | Eşik (varsayılan) | Anlam |
|---|---|---|
| `drawdown_esigi` | maxDD ≤ −0.20 | derin geri çekilme |
| `vol_sicramasi` | yeni vol ≥ 1.5 × eski | volatilite sıçraması |
| `stil_sapmasi` | stil/holdings drift ≥ 0.10 | strateji kayması |
| `rejim_degisimi` | regime_tag değişti | makro/benchmark rejim kayması |
| `ter_ust_sinir_artisi` | yeni `ter_ceiling_pct` > eski (fon-mcp `get_fund_costs`) | azami gider sınırı artışı (genel kurul/tebliğ tetiklidir; gün-içi değişmez — DÜŞÜK frekanslı sinyal) |
| `yonetim_ucreti_artisi` | yeni `management_fee_pct` > eski | yönetim ücreti revize |
| `gerceklesen_ter_artisi` | KAP KIID yıllık TER > önceki yıl | KAP KIID gerekir; fon-mcp kapsam dışı |
| `kap_duyurusu` | açık duyuru | kurucu/PYŞ/içtüzük |
| `yeni_eklendi` | — | listeye yeni giren |

Eşikler `thresholds` (mdd_breach, vol_spike_k, rank_drop) ile özelleştirilebilir.

## Önceliklendirme & alarm kompoziti
Her alarm öncelik puanı taşır; `alert_composite` çok-sinyali ağırlıklı "izleme duruşu"na
indirger: **sakin / izlemede / yüksek dikkat**. Birden çok eksende yanan fon yükseltilir.

## "Ne değişti" raporu
Önceliğe göre sıralı değişimler + her alarm için tetikleyici + önerilen gözden-geçirme
(karar-destek dili; emir yok). Çıkarılan fonlar da listelenir. Her snapshot EOD/as-of taşır.

## İlke
İzleme tam yeniden-analiz değildir; yalnız **delta**. Tam analiz gerekirse /fon-analiz'e
yönlendirilir. Karar-destek; yatırım tavsiyesi değildir.
