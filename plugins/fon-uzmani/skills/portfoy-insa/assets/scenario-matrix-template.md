# Senaryo Matrisi Şablonu (portföy)

Her portföy önerisi üç senaryoyla sunulur. Karar-destek; SPK yatırım danışmanlığı değildir.

| Senaryo | Makro varsayım | Beklenen yıllık getiri | Beklenen vol | Tetikleyici | Geçersizleşme |
|---|---|---|---|---|---|
| **Baz** | Mevcut rejim sürer (faiz/enflasyon/kur stabil) | `<opt. beklenen getiri>` | `<opt. vol>` | — | — |
| **İyimser** | Risk-Açık (faiz inişi / enflasyon ılımlı) | Baz + `<delta>` | ↓ | faiz indirimi, kur stabil | enflasyon yeniden hızlanır |
| **Kötümser** | Risk-Kapalı (sıkılaştırma / kur baskısı) | Baz − `<delta>` | ↑ | faiz artışı, kur şoku | faiz inişi başlar |

## Notlar
- Getiri/vol değerleri `optimized_portfolio.expected`'ten + makro rejim duyarlılığından türetilir.
- Her senaryo, ağırlıkların hangi koşulda gözden geçirilmesi gerektiğini (tetikleyici) ve
  tezin hangi koşulda geçersizleştiğini belirtir.
- Kesin getiri vaadi yoktur; bantlar ve koşullar verilir.
- Rapor sonunda **kanonik SPK feragati** birebir bulunur (regulasyon-uyum/compliance.md).
