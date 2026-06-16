# allocation-doctrine.md — Risk Profili → Hedef Tahsis

Risk profili optimizasyon kısıtlarını ve hedef tahsis bandını belirler (karar-destek bağlamı).

| Profil | Hedef yapı | Tipik vol toleransı | Optimizasyon eğilimi |
|---|---|---|---|
| **conservative** | para piyasası + borçlanma ağırlıklı; sınırlı hisse | düşük | min-variance / risk-parity |
| **moderate** | dengeli (hisse + borçlanma + karma) | orta | risk-parity / HRP |
| **aggressive** | hisse + büyüme ağırlıklı; düşük nakit | yüksek | max-Sharpe |

## Kısıt çerçevesi (brief.constraints)
- `max_weight_per_fund` — tek fonda yoğunlaşmayı sınırla.
- `min_funds` — minimum çeşitlendirme.
- `max_ter` — maliyet tavanı (cost_analysis ile filtre).
- Kısıt sağlanamazsa **relaksasyon önerisi** sun (hangi kısıt gevşetilirse uygulanabilir).

## İlkeler
- Tahsis **çerçeve**dir, emir değil: "% X-Y bandı" + tetikleyici + geçersizleşme.
- EMK için alt-tip uyumu (agresif/dengeli/muhafazakâr) profil ile eşleştirilir.
- Her tahsis Baz/İyimser/Kötümser senaryo + SPK feragati ile sunulur (scenario-matrix-template).
- Kişiselleştirilmiş kesin tutar verilmez (regulasyon-uyum).
