# benchmark-selection.md — Benchmark Seçimi

Fon kategorisine uygun benchmark seçimi (beta/alfa/aktif-getiri/IR için).

| Fon kategorisi | Önerilen benchmark | Borsa sembolü |
|---|---|---|
| Hisse Senedi Fonu | BIST 100 / BIST TÜM | XU100 / XUTUM |
| Sektör hisse fonu | İlgili sektör endeksi | XBANK, XUSIN, XUTEK… |
| Borçlanma Araçları | KYD tahvil endeksleri | KYD-OST/DT (yaklaşık) |
| Para Piyasası | KYD O/N repo / mevduat | KYD-ON |
| Karma / Değişken | Bileşik (örn. %50 XU100 + %50 KYD) | sentetik karma |
| Katılım | Katılım endeksleri | XK100 (yaklaşık) |
| Kıymetli Madenler | Altın (gram/ons) | XAU / gram altın |
| EMK alt-tipleri | Karşılık gelen YAT benchmark'ı | — |

## İlkeler
- Benchmark serisi `Borsa get_index_data(symbol, start, end)` ile NAV penceresine hizalanır.
- Uygun doğrudan endeks yoksa sentetik karma kurulur ve raporda belirtilir.
- Benchmark seçimi `market_context.benchmark`'a yazılır; quant-analiz buradan okur (çift çağrı yok).
- Yanlış benchmark beta/alfa/IR'ı bozar → kategori-benchmark tutarlılığı G2 kontrolüdür.
